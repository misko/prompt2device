#!/usr/bin/env python3
"""Read-only, evidence-bound view of stage guidance and validation coverage."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = "skills/pcb-design/workflow/graph.json"
COVERAGE = "skills/pcb-design/workflow/coverage.json"
TYPES = {"checkpoint", "from_brief"}
# Diagnostic inventory metadata is not an instructional candidate dependency.
# Excluding it avoids making a receipt stale merely by adding that receipt here.
DIAGNOSTIC_INPUTS = {COVERAGE, "COVERAGE.md"}


class CoverageError(ValueError):
    pass


def file_at(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise CoverageError(f"invalid relative path: {relative!r}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise CoverageError(f"path escapes repository: {relative}")
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(root: Path) -> tuple[list[dict], dict[str, dict]]:
    graph = json.loads(file_at(root, GRAPH).read_text(encoding="utf-8"))
    sidecar = json.loads(file_at(root, COVERAGE).read_text(encoding="utf-8"))
    if sidecar.get("schema") != 1:
        raise CoverageError("unsupported coverage schema")
    ids = [item["spec"]["id"] for item in graph["stages"]]
    rows = sidecar["stages"]
    actual = [row["stage_id"] for row in rows]
    if len(ids) != len(set(ids)) or len(actual) != len(set(actual)):
        raise CoverageError("duplicate graph or coverage stage ID")
    if set(ids) != set(actual):
        raise CoverageError(f"stage IDs differ: missing={sorted(set(ids)-set(actual))}, "
                            f"unknown={sorted(set(actual)-set(ids))}")
    entries = sidecar["validations"]
    refs = [entry["id"] for entry in entries]
    if len(refs) != len(set(refs)):
        raise CoverageError("duplicate validation ID")
    validations = {entry["id"]: entry for entry in entries}
    for entry in entries:
        if entry.get("type") not in TYPES or not entry.get("scope"):
            raise CoverageError(f"validation {entry['id']} needs type and scope")
        file_at(root, entry["evidence"])
    for row in rows:
        backing = row.get("backing")
        if backing == "local_procedure":
            path = file_at(root, row.get("procedure"))
            if not path.is_file():
                raise CoverageError(f"missing local procedure: {path}")
        elif backing != "legacy" or "procedure" in row:
            raise CoverageError(f"invalid backing for {row['stage_id']}")
        listed = row.get("validations")
        if not isinstance(listed, list) or len(listed) != len(set(listed)):
            raise CoverageError(f"invalid validation refs for {row['stage_id']}")
        if set(listed) - validations.keys():
            raise CoverageError(f"unknown validation ref for {row['stage_id']}")
    by_id = {row['stage_id']: row for row in rows}
    for stage in graph['stages']:
        definition = stage.get('local_definition')
        if definition is not None:
            row = by_id[stage['spec']['id']]
            if (definition.get('status') != 'definition_only' or
                    'local_execution' in stage or 'tool' in definition or
                    not definition.get('missing') or
                    row.get('backing') != 'local_procedure' or
                    row.get('procedure') != definition.get('contract')):
                raise CoverageError('definition-only stage conflicts with execution/coverage')
        recovery = stage.get('recovery')
        if recovery is not None:
            if (recovery.get('owner') != 'workflow-orchestrator' or
                    recovery.get('mode') != 'coordinator_decision_not_automatic_dispatch' or
                    not file_at(root, recovery['procedure']).is_file() or
                    not recovery.get('destinations') or
                    not set(recovery['destinations'].values()) <= set(ids)):
                raise CoverageError('invalid recovery owner, procedure or destination')
    return [next(row for row in rows if row["stage_id"] == id_) for id_ in ids], validations


def evidence_status(root: Path, entry: dict) -> str:
    """STALE on a known mismatch, UNVERIFIED when the binding cannot be checked."""
    path = file_at(root, entry["evidence"])
    if not path.is_file():
        return "UNVERIFIED"
    try:
        evidence = json.loads(path.read_text(encoding="utf-8"))
        candidate = evidence["candidate_hashes"]
        manifest = evidence["case_manifest"]
        case = evidence["trial"]["case"]
        baseline = evidence["baseline_commit"]
        pin = json.loads(file_at(root, "dependencies.json").read_text())["baseline"]["commit"]
        if not isinstance(candidate, dict) or not candidate or not isinstance(manifest, dict) or not manifest:
            return "UNVERIFIED"
        if not isinstance(case, str) or "/" in case or case in (".", ".."):
            return "UNVERIFIED"
        mismatched = baseline != pin
        missing = False
        for name, expected in candidate.items():
            if not name.startswith("candidate/") or len(expected) != 64:
                return "UNVERIFIED"
            relative = name[len("candidate/"):]
            if relative in DIAGNOSTIC_INPUTS:
                continue
            target = file_at(root, relative)
            if not target.is_file():
                missing = True
            elif digest(target) != expected:
                mismatched = True
        case_root = f"tests/checkpoints/cases/{case}/"
        for name, expected in manifest.items():
            if len(expected) != 64:
                return "UNVERIFIED"
            target = file_at(root, case_root + name)
            if not target.is_file():
                missing = True
            elif digest(target) != expected:
                mismatched = True
        # A receipt must cover the *current* instructional inventory, not just
        # verify whichever old subset happened to be recorded.
        required = {"dependencies.json", "tools/context.py", "tools/checkpoints.py"}
        required.update(p.relative_to(root).as_posix() for p in (root / "skills").rglob("*")
                        if p.is_file() and p.relative_to(root).as_posix() not in DIAGNOSTIC_INPUTS)
        if any("candidate/" + name not in candidate for name in required):
            missing = True
        case_dir = file_at(root, case_root)
        if not case_dir.is_dir():
            missing = True
        elif any(p.relative_to(case_dir).as_posix() not in manifest
                 for p in case_dir.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
            missing = True
        return "STALE" if mismatched else "UNVERIFIED" if missing else "CURRENT"
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, CoverageError):
        return "UNVERIFIED"


def render(root: Path = ROOT) -> str:
    rows, validations = load(root)
    definitions = {s['spec']['id'] for s in json.loads(file_at(root, GRAPH).read_text())['stages']
                   if 'local_definition' in s}
    lines = ["# PCB workflow coverage", "",
             "Guidance/validation inventory only. This is not project progress, stage acceptance, or board verification.",
             "Historical legacy backing is migration metadata, not permission to execute it. Use the stage's explicit local_execution adapter where declared; otherwise standalone task support is defined by `tools/task.py`.",
             "`CURRENT` means recorded inputs still match; it does not mean an engineering gate passed.", "",
             "| Stage | Guidance | Evidence |", "| --- | --- | --- |"]
    for row in rows:
        guidance = (f"Local: `{row['procedure']}`" if row["backing"] == "local_procedure"
                    else "Legacy-backed")
        if row['stage_id'] in definitions:
            guidance += ' — definition only; execution unavailable'
        labels = [f"{validations[ref]['type']} {evidence_status(root, validations[ref])}: "
                  f"{validations[ref]['scope']}" for ref in row["validations"]]
        lines.append(f"| `{row['stage_id']}` | {guidance} | {'; '.join(labels) if labels else 'No recorded validation'} |")
    lines += ["", "Evidence freshness is derived from the recorded instructional candidate hashes, case manifest, and baseline pin. "
              "Diagnostic `coverage.json` and this generated view are excluded: adding evidence to the inventory cannot invalidate that same evidence. "
              "Missing or uncheckable bindings are `UNVERIFIED`; changed inputs are `STALE`.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        sys.stdout.write(render(args.root))
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, CoverageError) as exc:
        print(f"coverage: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
