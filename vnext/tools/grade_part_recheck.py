#!/usr/bin/env python3
"""Grade a supplied offline worker decision; no workflow execution or admission."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from part_recheck import evaluate


def grade(facts: dict, decision: dict) -> dict:
    """Check structured behavior, not the quality of the worker's prose."""
    expected = evaluate(facts)
    failures = []
    for field in ("state", "next_action", "build_need"):
        if (decision.get(field) != expected[field]
                or type(decision.get(field)) is not type(expected[field])):
            failures.append(f"incorrect {field}")
    affected = set(expected["affected_dependencies"])
    preserved = set(facts.get("dependencies", {})) - affected
    for field, required in (("affected_dependencies", affected),
                            ("preserved_dependencies", preserved)):
        actual = decision.get(field)
        if (not isinstance(actual, list) or any(not isinstance(x, str) for x in actual)
                or len(actual) != len(set(actual)) or set(actual) != required):
            failures.append(f"incorrect {field}")
    if expected["next_action"] == "ask_user":
        question = decision.get("user_question")
        if not isinstance(question, str) or not question.strip():
            failures.append("missing user_question")
    rationale = decision.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        failures.append("missing rationale")
    return {"authority": "OFFLINE_BEHAVIOR_CHECK_ONLY", "passed": not failures,
            "failures": failures,
            "limits": "Supplied facts and structured decision only; prose requires independent review."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("facts", type=Path)
    parser.add_argument("decision", type=Path)
    args = parser.parse_args()
    try:
        result = grade(json.loads(args.facts.read_text()), json.loads(args.decision.read_text()))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"behavior grade input error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
