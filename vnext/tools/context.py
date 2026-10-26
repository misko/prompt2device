#!/usr/bin/env python3
"""Read-only, fail-closed instruction packet for a pinned PCB stage/task.

The baseline router remains the authority for stage selection and mandatory
legacy references. This tool only narrows the *new* local instructions.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "dependencies.json"
GRAPH = ROOT / "skills/pcb-design/workflow/graph.json"
BASE_GRAPH = Path("skills/pcb-design/workflow/graph.json")
ROUTER = Path("skills/pcb-design/scripts/skill_reference_router.py")
TASKS = frozenset({"generate", "review", "repair", "resume", "recover"})
SCHEMATIC = "KICAD-SCHEMATIC"
COMMISSION = "PCB-COMMISSION"

ENTRYPOINTS = (
    "skills/workflow-orchestrator/SKILL.md",
    "skills/pcb-design/SKILL.md",
    "skills/workflow-orchestrator/references/task-interface.md",
    "skills/workflow-orchestrator/references/dispatch.md",
    "skills/pcb-design/bindings/existing-tools.md",
)
SCHEMATIC_CONTRACT = "skills/pcb-design/workflow/stages/schematic.md"
COMMISSION_CONTRACT = "skills/pcb-design/workflow/stages/commission.md"
SCHEMATIC_PROCEDURE = {
    "generate": "skills/pcb-design/procedures/schematic/generate.md",
    "review": "skills/pcb-design/procedures/schematic/review.md",
    "repair": "skills/pcb-design/procedures/schematic/repair.md",
}
TASK_PROCEDURE = {
    "resume": "skills/workflow-orchestrator/references/resume.md",
    "recover": "skills/workflow-orchestrator/references/recover.md",
    "repair": "skills/workflow-orchestrator/references/recover.md",
}
SCHEMATIC_LEGACY_COMMON = (
    "skills/pcb-design/SKILL.md",
    "skills/pcb-design/workflow/STAGES.md",
    "skills/kicad-pcb/SKILL.md",
)
SCHEMATIC_LEGACY_TASK = {
    "generate": ("skills/pcb-design/references/commission-and-scope.md",),
    "review": ("skills/kicad-pcb/references/pin-review-protocol.md",),
    "repair": ("skills/pcb-design/references/commission-and-scope.md",
               "skills/kicad-pcb/references/pin-review-protocol.md"),
    # The next action is not a CLI input; retain both action lenses until the
    # reopened project record determines it. This is disclosure, not dispatch.
    "resume": ("skills/pcb-design/references/operator-checkpoints.md",
               "skills/pcb-design/references/commission-and-scope.md",
               "skills/kicad-pcb/references/pin-review-protocol.md"),
    "recover": ("skills/pcb-design/references/operator-checkpoints.md",
                "skills/pcb-design/references/commission-and-scope.md",
                "skills/kicad-pcb/references/pin-review-protocol.md"),
}


class ContextError(ValueError):
    """No trustworthy disclosure packet can be constructed."""


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContextError(f"cannot read {path}: {exc}") from exc


def _file(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ContextError(f"invalid instruction path: {relative!r}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ContextError(f"missing or escaping instruction: {relative!r}")
    return path


def _run(command: list[str], *, where: str) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                check=False, timeout=30,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContextError(f"{where}: {exc}") from exc
    if result.returncode:
        raise ContextError(f"{where}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def validate_baseline(root: Path, lock: Path = LOCK, graph: Path = GRAPH) -> None:
    data = _json(lock)
    if (not isinstance(data, dict) or set(data) != {"schema", "baseline"}
            or type(data["schema"]) is not int or data["schema"] != 1
            or not isinstance(data["baseline"], dict)
            or set(data["baseline"]) != {"root", "commit"}):
        raise ContextError("dependencies.json has an unsupported schema")
    baseline = data["baseline"]
    commit = baseline["commit"]
    if (not isinstance(commit, str) or len(commit) != 40
            or any(char not in "0123456789abcdef" for char in commit)):
        raise ContextError("baseline commit must be a full lowercase SHA-1")
    locked_root = baseline["root"]
    if not isinstance(locked_root, str) or not Path(locked_root).is_absolute():
        raise ContextError("baseline root must be absolute")
    if not root.is_dir():
        raise ContextError(f"baseline root is missing: {root}")
    head = _run(["git", "-C", str(root), "rev-parse", "HEAD"], where="baseline HEAD")
    if head.strip() != commit:
        raise ContextError(f"baseline HEAD {head.strip()} differs from pinned {commit}")
    dirty = _run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all", "--", "skills"], where="baseline status")
    if dirty.strip():
        raise ContextError(f"baseline skills are dirty:\n{dirty.strip()}")
    try:
        if graph.read_bytes() != _file(root, str(BASE_GRAPH)).read_bytes():
            raise ContextError("local workflow graph differs from pinned baseline")
    except OSError as exc:
        raise ContextError(f"cannot compare workflow graphs: {exc}") from exc
    catalog = _json(graph)
    try:
        references = [item for domain in catalog["domains"]
                      for item in domain["references"]]
        references.append(catalog["core_budget"]["path"])
    except (TypeError, KeyError) as exc:
        raise ContextError("workflow graph lacks instruction references") from exc
    for item in references:
        _file(root, item)
    _file(root, str(ROUTER))


def _metrics(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    try:
        words = len(data.decode("utf-8").split())
    except UnicodeError as exc:
        raise ContextError(f"instruction is not UTF-8: {path}") from exc
    return {"path": str(path), "bytes": len(data), "words": words}


def build_packet(stage: str, task: str, profile: Path, *,
                 baseline_root: Path | None = None, local_root: Path = ROOT) -> dict[str, Any]:
    if task not in TASKS:
        raise ContextError(f"unsupported task: {task}")
    lock = _json(local_root / "dependencies.json")
    try:
        locked_root = lock["baseline"]["root"]
    except (TypeError, KeyError) as exc:
        raise ContextError("dependencies.json lacks baseline root") from exc
    if not isinstance(locked_root, str) or not Path(locked_root).is_absolute():
        raise ContextError("dependencies.json baseline root must be absolute")
    root = (baseline_root or Path(locked_root)).resolve()
    validate_baseline(root, local_root / "dependencies.json",
                      local_root / "skills/pcb-design/workflow/graph.json")
    if not profile.is_file():
        raise ContextError(f"profile is missing: {profile}")
    output = _run([
        sys.executable, str(_file(root, str(ROUTER))),
        "--profile", str(profile.resolve()), "--at-stage", stage, "--json",
    ], where="baseline stage router")
    try:
        plan = json.loads(output)
    except json.JSONDecodeError as exc:
        raise ContextError(f"baseline router returned invalid JSON: {exc}") from exc
    if (plan.get("authority") != "DISCLOSURE_ONLY"
            or not isinstance(plan.get("load_now"), list)):
        raise ContextError("baseline router did not provide disclosure-only load_now")
    selected = [entry for entry in plan.get("stages", [])
                if entry.get("spec", {}).get("id") == stage]
    if len(selected) != 1 or selected[0].get("references") != plan["load_now"]:
        raise ContextError("stage is unselected or baseline reference list drifted")
    local = list(ENTRYPOINTS)
    if stage == COMMISSION:
        local.append(COMMISSION_CONTRACT)
    if stage == SCHEMATIC:
        local.append(SCHEMATIC_CONTRACT)
        if task in SCHEMATIC_PROCEDURE:
            local.append(SCHEMATIC_PROCEDURE[task])
    if task in TASK_PROCEDURE:
        local.append(TASK_PROCEDURE[task])
    local_files = [_metrics(_file(local_root, item)) for item in local]
    legacy = list(plan["load_now"])
    if stage == SCHEMATIC:
        for item in SCHEMATIC_LEGACY_COMMON + SCHEMATIC_LEGACY_TASK[task]:
            if item not in legacy:
                legacy.append(item)
    legacy_files = [_metrics(_file(root, item)) for item in legacy]
    # Baseline comparison includes the old common entrypoint and control loop,
    # not only the stage references; both counts are explicit and reproducible.
    old_core = [_metrics(_file(root, item)) for item in (
        "skills/pcb-design/SKILL.md",
        "skills/pcb-design/orchestrator/EXECUTION.md",
    ) if item not in legacy]
    sum_size = lambda rows, key: sum(row[key] for row in rows)
    return {
        "schema": 1, "disclosure_only": True, "stage": stage, "task": task,
        "profile": str(profile.resolve()), "baseline_commit": lock["baseline"]["commit"],
        "local_instructions": local_files, "mandatory_legacy_instructions": legacy_files,
        "load_now": local_files + legacy_files,
        "size": {
            "new_bytes": sum_size(local_files + legacy_files, "bytes"),
            "new_words": sum_size(local_files + legacy_files, "words"),
            "baseline_bytes": sum_size(old_core + legacy_files, "bytes"),
            "baseline_words": sum_size(old_core + legacy_files, "words"),
            "baseline_comparison_scope": "baseline PCB SKILL + EXECUTION.md + identical mandatory stage/task legacy instructions; duplicate files counted once",
            "comparison_limit": "instruction-file lower bound only; transitive instructions and project inputs are excluded from both totals",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--task", choices=sorted(TASKS), default="generate")
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path)
    args = parser.parse_args(argv)
    try:
        packet = build_packet(args.stage, args.task, args.profile,
                              baseline_root=args.baseline_root)
    except ContextError as exc:
        print(f"CONTEXT FAIL: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
