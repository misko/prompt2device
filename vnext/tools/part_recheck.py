#!/usr/bin/env python3
"""Read-only design-availability evaluation of supplied exact-part facts."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import sys
from urllib.parse import urlparse


IDENTITY = ("manufacturer", "mpn", "package")
QUANTITY = ("quantity_per_assembly", "assembly_count")


def subject_key(subject: dict) -> tuple:
    for field in IDENTITY:
        if not isinstance(subject.get(field), str) or not subject[field].strip():
            raise ValueError(f"missing exact {field}")
    for field in QUANTITY:
        if type(subject.get(field)) is not int or subject[field] <= 0:
            raise ValueError(f"{field} must be a positive integer")
    return tuple(subject[field] for field in (*IDENTITY, *QUANTITY))


def affected_dependencies(part_id: str, dependencies: dict) -> list[str]:
    """Transitive consumers only; dependency discovery remains the caller's job."""
    affected = {part_id}
    while True:
        added = {name for name, inputs in dependencies.items()
                 if any(item in affected for item in inputs)} - affected
        if not added:
            return sorted(affected - {part_id})
        affected.update(added)


def adequate_offer(offer: dict, subject: dict, need: int) -> bool:
    # Legacy supplied-fact inputs remain supported; explicit weak evidence cannot pass.
    if any(offer.get(key) in {"aggregate_snapshot", "search_snippet"}
           for key in ("evidence_kind", "source_kind")):
        return False
    if offer.get("availability_verified") is False:
        return False
    if offer.get("lookup_state") in {"lookup_failed", "stale", "no_exact_match", "no_exact_evidence", "inventory_unverified"}:
        return False
    if any(offer.get(key) != subject[key] for key in IDENTITY):
        return False
    url = urlparse(offer.get("supplier_url", ""))
    if url.scheme not in {"https", "http"} or not url.netloc:
        return False
    try:
        date.fromisoformat(offer.get("checked_on", ""))
    except (TypeError, ValueError):
        return False
    count = offer.get("stock_count")
    return (offer.get("in_stock") is True
            and (count is None or (type(count) is int and count >= need)))


def evaluate(facts: dict) -> dict:
    subject = facts["subject"]
    current = subject_key(subject)
    need = subject["quantity_per_assembly"] * subject["assembly_count"]
    result = {
        "authority": "SUPPLIED_FACTS_ONLY",
        "state": "provisional",
        "next_action": "check_exact_part",
        "build_need": need,
        "affected_dependencies": affected_dependencies(
            facts["part_id"], facts.get("dependencies", {})),
        "reason": "missing_check",
    }
    check = facts.get("check")
    if not check:
        return result
    if subject_key(check["subject"]) != current:
        result["reason"] = "stale_subject"
        return result
    if check.get("jlc_checked") is not True:
        result["reason"] = "jlc_check_missing"
        return result
    if any(adequate_offer(offer, subject, need) for offer in check.get("offers", [])):
        result.update(state="checked", next_action="sourcing_guard_clear",
                      reason="adequate_exact_offer")
    elif check.get("lookup_issue") in {"lookup_failed", "stale", "no_exact_match", "inventory_unverified"}:
        result.update(next_action="resolve_lookup_evidence", reason=check["lookup_issue"])
    elif check.get("western_search_complete") is True:
        result.update(state="needs_user_decision", next_action="ask_user",
                      reason="short_search_without_adequate_offer")
    else:
        result.update(next_action="brief_western_search", reason="no_adequate_offer_yet")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("facts", type=Path)
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.facts.read_text()))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"part recheck input error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["state"] == "checked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
