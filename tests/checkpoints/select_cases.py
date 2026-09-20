#!/usr/bin/env python3
"""Conservative, deterministic case selection; never invokes an agent."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def select(suite="smoke", *, tags=(), changed=(), root=HERE):
    root = Path(root)
    catalog = json.loads((root / "suites.json").read_text())
    if catalog.get("schema") != 1 or suite not in catalog["suites"]:
        raise ValueError(f"unknown suite: {suite}")
    names = catalog["suites"][suite]
    if not names or len(names) != len(set(names)):
        raise ValueError("suite must contain distinct cases")
    selected = []
    for name in names:
        if Path(name).name != name or name in {".", ".."}:
            raise ValueError("unsafe case name")
        case = root / "cases" / name
        manifest = json.loads((case / "case.json").read_text())
        if tags and not set(tags).intersection(manifest["tags"]):
            continue
        selected.append(case)
    # A changed-file hint is deliberately conservative. Case-only edits can
    # select their own cases; any shared/unknown path retains the whole suite.
    hints = set()
    for value in changed:
        parts = Path(value).parts
        if len(parts) > 3 and parts[:3] == ("tests", "checkpoints", "cases") and parts[3] in names:
            hints.add(parts[3])
        else:
            hints.clear()
            break
    if hints:
        selected = [p for p in selected if p.name in hints]
    if not selected:
        raise ValueError("selection is empty; no tests ran")
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", default="smoke")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--changed", action="append", default=[])
    args = parser.parse_args()
    try:
        selected = select(args.suite, tags=args.tag, changed=args.changed)
    except (ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps({"schema": 1, "cases": [str(p) for p in selected]}, indent=2))


if __name__ == "__main__":
    main()
