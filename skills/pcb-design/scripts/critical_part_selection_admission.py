#!/usr/bin/env python3
"""Admit an explicitly declared critical part before PCB producer spend.

Projects without 03_src/rules/critical_part_selection.yaml keep their existing
conductor behavior. A declaration binds the selected TSX component, exact
part dossier, independent suitability decision, all tagged selection findings,
and a current or pinned-initial public stock observation. It admits only the recorded selection
decision, not later electrical, physical, or PCBA qualification.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import yaml


class InputError(ValueError):
    pass


def project_path(project: Path, value: str, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{label} needs a project-relative path")
    path = (project / value).resolve()
    if project not in path.parents or not path.is_file():
        raise InputError(f"{label} missing or outside project: {value}")
    return path


def mapping(path: Path, label: str) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, yaml.YAMLError) as exc:
        raise InputError(f"{label} cannot be read: {exc}") from exc
    if not isinstance(value, dict):
        raise InputError(f"{label} must be a mapping")
    return value


def positive_int(value: object, label: str, *, zero: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < (0 if zero else 1):
        raise InputError(f"{label} must be {'nonnegative' if zero else 'positive'} integer")
    return value


def exact_source_component(source: str, ref: str, mpn: str, lcsc: str) -> bool:
    """Require all three identities on one JSX opening tag, not a comment."""
    for tag in re.findall(r"<[A-Za-z][^>]*>", source, flags=re.S):
        if (re.search(r'\bname\s*=\s*["\']' + re.escape(ref) + r'["\']', tag)
                and re.search(r'\bmanufacturerPartNumber\s*=\s*["\']'
                              + re.escape(mpn) + r'["\']', tag)
                and re.search(r'["\']' + re.escape(lcsc) + r'["\']', tag)):
            return True
    return False


def utc_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        observed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if observed.tzinfo is None:
        return None
    return observed.astimezone(timezone.utc)


def fresh_timestamp(value: object, max_age_hours: int, *, as_of: datetime | None = None) -> bool:
    observed = utc_timestamp(value)
    if observed is None:
        return False
    seconds = ((as_of or datetime.now(timezone.utc)) - observed).total_seconds()
    return -300 <= seconds <= 3600 * max_age_hours


def bound_evidence(project: Path, spec: object, label: str, findings: list[str]) -> None:
    if not isinstance(spec, dict):
        raise InputError(f"{label} needs path and sha256")
    path = project_path(project, spec.get("path"), f"{label}.path")
    digest = spec.get("sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise InputError(f"{label}.sha256 must be a SHA-256 digest")
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        findings.append(f"{label}: evidence digest changed")


def reviewed_decision(project: Path, spec: object, label: str,
                      findings: list[str], *, require_reviewer: bool = True) -> dict:
    if not isinstance(spec, dict):
        raise InputError(f"{label} needs status, decision owner, independent reviewer and evidence")
    owner, reviewer = spec.get("decision_owner"), spec.get("reviewer")
    if not isinstance(owner, str) or not owner.strip():
        raise InputError(f"{label} needs decision_owner")
    if require_reviewer or reviewer is not None:
        if (not isinstance(reviewer, str) or not reviewer.strip() or
                owner.strip() == reviewer.strip()):
            raise InputError(f"{label} needs a reviewer distinct from decision_owner")
    bound_evidence(project, spec.get("evidence"), label, findings)
    return spec


def evaluate(project: Path, declaration: Path) -> dict:
    if not declaration.exists():
        return {"status": "NOT_APPLICABLE", "coverage": "0/0", "findings": [],
                "declaration": str(declaration)}
    doc = mapping(declaration, "critical selection declaration")
    rows = doc.get("selections")
    if doc.get("schema") != 1 or not isinstance(rows, list):
        raise InputError("critical selection declaration needs schema: 1 and selections list")
    mode = doc.get("status", "selections")
    if mode == "pending":
        return {"status": "FAIL", "coverage": "0/0", "findings":
                ["critical selection applicability or selections still pending"],
                "declaration": str(declaration)}
    if mode not in ("selections", "not_applicable") or (mode == "selections" and not rows):
        raise InputError("critical selection status must be selections with rows, pending, or not_applicable")
    ledger = mapping(project_path(project, doc.get("findings"), "findings ledger"), "findings ledger")
    if ledger.get("schema") != 1 or not isinstance(ledger.get("findings"), list):
        raise InputError("findings ledger needs schema: 1 and findings list")
    by_id: dict[str, dict] = {}
    tagged: dict[str, set[str]] = {}
    for item in ledger["findings"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise InputError("malformed finding in ledger")
        if item["id"] in by_id:
            raise InputError(f"duplicate finding id {item['id']}")
        by_id[item["id"]] = item
        tag = item.get("critical_selection")
        if tag is not None:
            if (not isinstance(tag, dict) or not isinstance(tag.get("ref"), str)
                    or tag.get("due_stage") != "selection"):
                raise InputError(f"finding {item['id']} has malformed critical_selection tag")
            tagged.setdefault(tag["ref"], set()).add(item["id"])
    findings: list[str] = []
    if mode == "not_applicable":
        if rows:
            raise InputError("not_applicable requires empty selections")
        reviewed_decision(project, doc.get("applicability"), "applicability", findings)
        if tagged:
            findings.append("not_applicable conflicts with tagged selection findings")
        return {"status": "PASS" if not findings else "FAIL", "coverage": "0/0",
                "findings": findings, "declaration": str(declaration)}
    assembly = mapping(project_path(project, doc.get("assembly"), "assembly"), "assembly")
    build_quantity = positive_int(assembly.get("build_quantity"), "assembly.build_quantity")
    default_surplus = positive_int(assembly.get("public_stock_surplus"),
                                   "assembly.public_stock_surplus", zero=True)
    overrides = assembly.get("public_stock_surplus_overrides") or []
    if not isinstance(overrides, list):
        raise InputError("assembly.public_stock_surplus_overrides must be a list")
    seen_refs: set[str] = set()
    prototype_refs: list[str] = []
    for index, row in enumerate(rows):
        label = f"selections[{index}]"
        if not isinstance(row, dict):
            raise InputError(f"{label} must be a mapping")
        ref, mpn, lcsc = (row.get(key) for key in ("ref", "mpn", "lcsc"))
        if not all(isinstance(x, str) and x.strip() for x in (ref, mpn, lcsc)):
            raise InputError(f"{label} needs exact ref, mpn and lcsc")
        if ref in seen_refs:
            raise InputError(f"duplicate critical selection ref {ref}")
        seen_refs.add(ref)
        dossier = mapping(project_path(project, row.get("dossier"), f"{label}.dossier"),
                          f"{label}.dossier")
        if dossier.get("mpn") != mpn or (dossier.get("sourcing") or {}).get("lcsc") != lcsc:
            findings.append(f"{ref}: dossier MPN/LCSC differs from declared selection")
        source_spec = row.get("source")
        if not isinstance(source_spec, dict):
            raise InputError(f"{label}.source must bind a TSX path and sha256")
        source_path = project_path(project, source_spec.get("path"), f"{label}.source.path")
        source_sha = source_spec.get("sha256")
        if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", source_sha):
            raise InputError(f"{label}.source.sha256 must be a SHA-256 digest")
        source_bytes = source_path.read_bytes()
        if hashlib.sha256(source_bytes).hexdigest() != source_sha:
            findings.append(f"{ref}: authored source digest changed")
        if not exact_source_component(source_bytes.decode("utf-8"), ref, mpn, lcsc):
            findings.append(f"{ref}: exact MPN/LCSC not bound on one source component")
        suitability = row.get("suitability")
        if not isinstance(suitability, dict):
            raise InputError(f"{label}.suitability needs accepted, prototype_only or incomplete status")
        if suitability.get("status") not in ("accepted", "prototype_only", "incomplete"):
            raise InputError(f"{label}.suitability.status must be accepted, prototype_only or incomplete")
        reviewed_decision(project, suitability, f"{ref}.suitability", findings,
                          require_reviewer=suitability["status"] != "incomplete")
        if suitability["status"] == "incomplete":
            findings.append(f"{ref}: independent selection suitability is incomplete")
        deferred = suitability.get("deferred_findings")
        if suitability["status"] == "prototype_only":
            prototype_refs.append(ref)
            bound_evidence(project, suitability.get("test_plan"),
                           f"{ref}.suitability.test_plan", findings)
            if (not isinstance(deferred, list) or not deferred or
                    any(not isinstance(x, str) or not x for x in deferred) or
                    len(deferred) != len(set(deferred))):
                raise InputError(f"{label}.suitability.deferred_findings needs unique finding IDs")
            for ident in deferred:
                item = by_id.get(ident)
                if item is None:
                    findings.append(f"{ref}: deferred release finding {ident!r} absent")
                elif (item.get("state") != "open" or
                      item.get("blocks_at_or_above") != "DESIGN_CLEAN" or
                      item.get("critical_selection") is not None):
                    findings.append(f"{ref}: deferred finding {ident!r} must be open, "
                                    "DESIGN_CLEAN-blocking and outside selection")
        elif deferred is not None:
            raise InputError(f"{label}.suitability.deferred_findings is only for prototype_only")
        due = row.get("due_at_selection_findings")
        if (not isinstance(due, list) or any(not isinstance(x, str) or not x for x in due)
                or len(due) != len(set(due))):
            raise InputError(f"{label}.due_at_selection_findings needs unique finding IDs")
        for omitted in sorted(tagged.get(ref, set()) - set(due)):
            findings.append(f"{ref}: tagged selection finding {omitted!r} omitted from declaration")
        for ident in due:
            item = by_id.get(ident)
            if item is None:
                findings.append(f"{ref}: due-at-selection finding {ident!r} absent")
            elif item.get("state") != "closed":
                findings.append(f"{ref}: due-at-selection finding {ident!r} is {item.get('state')!r}")
            elif not item.get("evidence"):
                findings.append(f"{ref}: closed finding {ident!r} has no evidence")
        stock = row.get("stock")
        if not isinstance(stock, dict):
            raise InputError(f"{label}.stock must name public receipt and freshness")
        stock_path = project_path(project, stock.get("path"), f"{label}.stock.path")
        max_age = positive_int(stock.get("max_age_hours"), f"{label}.stock.max_age_hours")
        policy = stock.get("policy", "rolling")
        if policy not in ("rolling", "initial_snapshot"):
            raise InputError(f"{label}.stock.policy must be rolling or initial_snapshot")
        stock_bytes = stock_path.read_bytes()
        checked_at = None
        if policy == "initial_snapshot":
            snapshot_sha = stock.get("sha256")
            if not isinstance(snapshot_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", snapshot_sha):
                raise InputError(f"{label}.stock.sha256 must pin the initial receipt")
            if hashlib.sha256(stock_bytes).hexdigest() != snapshot_sha:
                findings.append(f"{ref}: initial public stock receipt digest changed")
            checked_at = utc_timestamp(stock.get("initial_checked_at"))
            if checked_at is None:
                raise InputError(f"{label}.stock.initial_checked_at needs UTC timestamp")
            if checked_at > datetime.now(timezone.utc):
                findings.append(f"{ref}: initial stock check is dated in the future")
        try:
            receipt = json.loads(stock_bytes)
        except (OSError, json.JSONDecodeError) as exc:
            raise InputError(f"{label}.stock receipt unreadable: {exc}") from exc
        if not isinstance(receipt, dict) or not isinstance(receipt.get("lines"), list):
            raise InputError(f"{label}.stock receipt needs lines list")
        if not fresh_timestamp(receipt.get("generated_at"), max_age, as_of=checked_at):
            findings.append(f"{ref}: public stock observation was stale or undated at check time")
        if receipt.get("verdict") != "PASS":
            findings.append(f"{ref}: public stock receipt verdict is not PASS")
        matches = [line for line in receipt["lines"] if isinstance(line, dict)
                   and line.get("lcsc") == lcsc and line.get("mpn") == mpn
                   and ref in [name.strip() for name in str(line.get("designators", "")).split(",")]]
        if len(matches) != 1:
            findings.append(f"{ref}: expected one exact public stock MPN/LCSC/ref line, found {len(matches)}")
            continue
        line = matches[0]
        selected = [x for x in overrides if isinstance(x, dict)
                    and x.get("lcsc") == lcsc and x.get("mpn") == mpn]
        if len(selected) > 1:
            raise InputError(f"{ref}: duplicate assembly stock surplus overrides")
        surplus = (positive_int(selected[0].get("surplus"), f"{ref}.surplus", zero=True)
                   if selected else default_surplus)
        qty = positive_int(line.get("qty"), f"{ref}.stock.qty")
        required = build_quantity * qty
        if (line.get("required_qty") != required or
                line.get("stock_threshold") != required + surplus or
                line.get("applied_surplus") != surplus):
            findings.append(f"{ref}: stock threshold disagrees with assembly quantity/surplus")
        observed = positive_int(line.get("stock"), f"{ref}.stock", zero=True)
        if line.get("status") != "OK" or observed < required + surplus:
            findings.append(f"{ref}: public stock {observed} below {required + surplus} or line not OK")
    for omitted_ref in sorted(set(tagged) - seen_refs):
        findings.append(f"{omitted_ref}: tagged selection findings have no critical selection declaration")
    return {"status": ("FAIL" if findings else
                        "PROTOTYPE_ONLY" if prototype_refs else "PASS"),
            "coverage": f"{len(rows)}/{len(rows)}", "findings": findings,
            "declaration": str(declaration), "prototype_refs": prototype_refs}


def release_selection_errors(project: Path) -> list[str]:
    """Reject unfinished declared selections at every release boundary.

    A missing manifest cannot hide a tagged selection obligation or an open
    DESIGN_CLEAN finding. Boards without either retain their legacy path.
    """
    project = project.resolve()
    declaration = project / "03_src/rules/critical_part_selection.yaml"
    try:
        report = evaluate(project, declaration)
        ledger_path = project / "01_docs/findings.yaml"
        ledger = mapping(ledger_path, "findings ledger") if ledger_path.is_file() else None
        rows = ledger.get("findings") if ledger is not None else []
        if not isinstance(rows, list):
            raise InputError("findings ledger needs findings list")
        errors = []
        if report["status"] == "NOT_APPLICABLE":
            if any(isinstance(row, dict) and row.get("critical_selection") is not None
                   for row in rows):
                errors.append("critical selection declaration missing for tagged findings")
        elif report["status"] != "PASS":
            errors.extend([f"critical selection {report['status']}: {item}"
                           for item in report["findings"]] or [
                               f"critical selection {report['status']} is not fully accepted"])
        for row in rows:
            if not isinstance(row, dict):
                raise InputError("malformed finding in ledger")
            if row.get("state") == "open" and row.get("blocks_at_or_above") == "DESIGN_CLEAN":
                errors.append(f"open DESIGN_CLEAN finding {row.get('id')!r} blocks release")
        return errors
    except (InputError, OSError, UnicodeError, ValueError) as exc:
        return [f"critical selection input invalid: {exc}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("project")
    parser.add_argument("--declaration", default="03_src/rules/critical_part_selection.yaml")
    parser.add_argument("--require-prototype", action="store_true",
                        help="bounded prototype producer: accept only PROTOTYPE_ONLY, never PASS or N-A")
    args = parser.parse_args()
    project = Path(args.project).resolve()
    declaration = (project / args.declaration).resolve()
    try:
        if project not in declaration.parents:
            raise InputError("declaration path escapes project")
        report = evaluate(project, declaration)
    except (InputError, UnicodeError) as exc:
        print(f"CRITICAL-SELECTION INPUT-FAIL: {exc}")
        return 2
    print(f"CRITICAL-SELECTION {report['status']}: {report['coverage']} selections; "
          f"declaration={report['declaration']}")
    for item in report["findings"]:
        print(f"  {item}")
    for ref in report.get("prototype_refs", []):
        print(f"  {ref}: prototype design continuation only; release finding remains open")
    if args.require_prototype:
        return 0 if report["status"] == "PROTOTYPE_ONLY" else 1
    return 0 if report["status"] in ("PASS", "NOT_APPLICABLE") else 1


if __name__ == "__main__":
    raise SystemExit(main())
