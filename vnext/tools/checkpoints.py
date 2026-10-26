#!/usr/bin/env python3
"""Prepare and grade vNext packets with the pinned legacy checkpoint runner.

The runner remains responsible for calibration, hashing, write scope, and grading.
Only its context copier and trusted manifest are extended in this process.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import context


ROOT = Path(__file__).resolve().parents[1]
PROFILE = Path("capability-profile.json")


def baseline_root(local_root: Path = ROOT) -> Path:
    """Resolve the locked checkout, refusing an absent or invalid pin."""
    lock = local_root / "dependencies.json"
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
        root = data["baseline"]["root"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise context.ContextError(f"cannot read baseline pin: {exc}") from exc
    if not isinstance(root, str) or not Path(root).is_absolute():
        raise context.ContextError("baseline root must be absolute")
    path = Path(root).resolve()
    context.validate_baseline(path, lock, local_root / "skills/pcb-design/workflow/graph.json")
    receipt = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain", "--untracked-files=all",
         "--", "tests/checkpoints"],
        capture_output=True, text=True, check=False,
    )
    if receipt.returncode or receipt.stdout.strip():
        raise context.ContextError("pinned checkpoint harness is dirty or unreadable")
    return path


def _runner(root: Path):
    # The pinned implementation, not a copied or reimplemented checkpoint engine.
    module_name = "vnext_pinned_checkpoint_runner"
    if module_name in sys.modules:
        runner = sys.modules[module_name]
        if Path(runner.__file__).resolve() != (root / "tests/checkpoints/runner.py").resolve():
            raise context.ContextError("loaded checkpoint runner differs from baseline pin")
    else:
        sys.path.insert(0, str(root / "tests/checkpoints"))
        source = root / "tests/checkpoints/runner.py"
        spec = importlib.util.spec_from_file_location(module_name, source)
        if spec is None or spec.loader is None:
            raise context.ContextError(f"cannot load pinned runner: {source}")
        runner = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = runner
        spec.loader.exec_module(runner)

    original_context = getattr(runner, "_vnext_original_context", runner._context)
    original_manifest = getattr(runner, "_vnext_original_manifest", runner._trusted_manifest)
    runner._vnext_original_context = original_context
    runner._vnext_original_manifest = original_manifest

    def supplied_context(case: dict, repo: Path, destination: Path) -> dict[str, str]:
        original_context(case, repo, destination)
        stage = case["checkpoint"]["stage_id"]
        task = supplied_context.task
        # The profile is part of the restored, hashed snapshot; a generic
        # fallback could silently omit conditional owner references.
        packet = context.build_packet(stage, task, destination.parent / PROFILE,
                                      baseline_root=repo,
                                      local_root=ROOT)
        # Copy the small candidate package, including graph and linked sibling
        # procedures, so selected instructions can disclose files on demand.
        # The packet below still names only what this stage/task must read now.
        candidate = destination / "candidate"
        runner._copy_tree(ROOT / "skills", candidate / "skills")
        shutil.copy2(ROOT / "dependencies.json", candidate / "dependencies.json")
        (candidate / "tools").mkdir()
        shutil.copy2(ROOT / "tools/context.py", candidate / "tools/context.py")
        # Keep mandatory baseline instructions separate: both packages have a
        # pcb-design/SKILL.md and neither may overwrite the other.
        for row in packet["mandatory_legacy_instructions"]:
            source = Path(row["path"])
            target = destination / "baseline" / source.relative_to(repo)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        selected = [str(Path(row["path"]).relative_to(ROOT))
                    for row in packet["local_instructions"]]
        start = destination / "START.md"
        start.write_text(
            start.read_text(encoding="utf-8") +
            "\n## vNext instruction route\n\n"
            "This is a candidate-skill trial. Read `.checkpoint_context/candidate/skills/"
            "workflow-orchestrator/SKILL.md` and `.checkpoint_context/candidate/skills/"
            "pcb-design/SKILL.md` first. Follow only the selected candidate task "
            "references listed below; other copied candidate files are available "
            "for on-demand linked reading, not a preload instruction. Retain the mandatory pinned owner "
            "instructions under `.checkpoint_context/baseline/`. The original runner's "
            "legacy context under `.checkpoint_context/skills/` is retained for audit, "
            "not as the vNext entrypoint. The trusted baseline repository above "
            "holds any transitive owner references not copied into this packet. "
            "Do not edit any checkpoint context.\n\n"
            f"Selected stage: `{stage}`. Selected task: `{task}`.\n\n"
            "Selected candidate files:\n" +
            "".join(f"- `.checkpoint_context/candidate/{path}`\n" for path in selected),
            encoding="utf-8",
        )
        return runner._tree(destination)

    supplied_context.task = "resume"

    def trusted_manifest(repo: Path) -> dict[str, str]:
        result = original_manifest(repo)
        # Bind the candidate source used by the packet, the pin, and this seam
        # across prepare/grade. The legacy manifest still binds its own tools.
        for relative in ("dependencies.json", "tools/context.py", "tools/checkpoints.py"):
            result[f"candidate/{relative}"] = runner._sha(ROOT / relative)
        for relative, digest in runner._tree(ROOT / "skills").items():
            result[f"candidate/skills/{relative}"] = digest
        return dict(sorted(result.items()))

    runner._context = supplied_context
    runner._trusted_manifest = trusted_manifest
    return runner, supplied_context


def prepare(case: str | Path, run_dir: str | Path, *, task: str = "resume") -> dict:
    if task not in context.TASKS:
        raise context.ContextError(f"unsupported task: {task}")
    root = baseline_root()
    runner, seam = _runner(root)
    seam.task = task
    return runner.prepare(case, run_dir, root)


def grade(run_dir: str | Path) -> dict:
    root = baseline_root()
    runner, _ = _runner(root)
    state = runner.run_state(Path(run_dir).resolve())
    if Path(state.get("repo", "")).resolve() != root:
        raise context.ContextError("run state baseline differs from current pin")
    return runner.grade(run_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    item = actions.add_parser("prepare")
    item.add_argument("--case", type=Path, required=True)
    item.add_argument("--run-dir", type=Path, required=True)
    item.add_argument("--task", choices=sorted(context.TASKS), default="resume")
    item = actions.add_parser("grade")
    item.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        value = (prepare(args.case, args.run_dir, task=args.task)
                 if args.action == "prepare" else grade(args.run_dir))
    except (context.ContextError, OSError, ValueError) as exc:
        print(json.dumps({"schema": 1, "outcome": "ERROR", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0 if args.action == "prepare" or value.get("outcome") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
