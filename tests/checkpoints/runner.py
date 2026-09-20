#!/usr/bin/env python3
"""Bounded, filesystem-audited runner for local checkpoint exercises.

Filesystem receipts are after-the-fact checks, not a hermetic sandbox.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "skills/pcb-design/scripts"))
from pipeline_runtime import run_stage  # noqa: E402
try:  # Script execution and package import are both supported.
    from .schema import CaseError, load_case  # type: ignore
except ImportError:
    from schema import CaseError, load_case  # noqa: E402


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(_json(value), encoding="utf-8")
    os.replace(temporary, path)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree(root: Path) -> dict[str, str]:
    """Hash regular files, rejecting links and unusual nodes rather than copying them."""
    if root.is_symlink():
        raise CaseError(f"symlink is forbidden: {root}")
    output: dict[str, str] = {}
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        if current_path.is_symlink():
            raise CaseError(f"symlink is forbidden: {current_path}")
        for name in dirs + files:
            item = current_path / name
            if item.is_symlink():
                raise CaseError(f"symlink is forbidden: {item}")
        for name in files:
            item = current_path / name
            if not item.is_file():
                raise CaseError(f"non-regular file is forbidden: {item}")
            output[item.relative_to(root).as_posix()] = _sha(item)
    return dict(sorted(output.items()))


def _copy_tree(source: Path, destination: Path) -> None:
    _tree(source)
    shutil.copytree(source, destination, copy_function=shutil.copy2)


def _manifest(root: Path) -> dict[str, str]:
    if root.is_symlink():
        raise CaseError(f"symlink is forbidden: {root}")
    return _tree(root) if root.is_dir() else {root.name: _sha(root)}


def _trusted_manifest(repo: Path) -> dict[str, str]:
    """Bind the local runner and skill scripts the trusted grader can use."""
    roots = [HERE / "runner.py", HERE / "schema.py",
             repo / "skills/pcb-design", repo / "skills/kicad-pcb", repo / "skills/jlcpcb-fab"]
    output: dict[str, str] = {}
    for item in roots:
        label = item.relative_to(repo).as_posix() if item.is_relative_to(repo) else item.name
        if item.is_file():
            output[label] = _sha(item)
            continue
        for current, dirs, files in os.walk(item, followlinks=False):
            current_path = Path(current)
            dirs[:] = [name for name in dirs if name != "__pycache__"]
            for name in files:
                source = current_path / name
                if source.is_symlink():
                    raise CaseError(f"symlink is forbidden in trusted dependency: {source}")
                # Python bytecode is a local execution cache, not grader authority.
                if source.suffix == ".pyc":
                    continue
                relative = source.relative_to(item).as_posix()
                output[f"{label}/{relative}"] = _sha(source)
    return dict(sorted(output.items()))


def _repo_revision(repo: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def _substitute(argv: Iterable[str], *, workspace: Path, repo: Path, case: Path) -> list[str]:
    values = {"workspace": str(workspace), "repo": str(repo), "case": str(case)}
    result: list[str] = []
    for item in argv:
        tokens = re.findall(r"\{[^{}]*\}", item)
        invalid = [token for token in tokens if token[1:-1] not in values]
        if invalid:
            raise CaseError(f"unknown command substitution(s): {', '.join(invalid)}")
        expanded = item
        for name, value in values.items():
            expanded = expanded.replace("{" + name + "}", value)
        result.append(expanded)
    return result


def _run(argv: list[str], *, stage_id: str, timeout_s: float, cwd: Path, log: Path) -> dict[str, Any]:
    runtime = run_stage({"id": stage_id, "work_class": "local", "timeout_s": timeout_s}, argv,
                        log_path=log, cwd=cwd, console=None, run_id=uuid.uuid4().hex)
    return runtime.to_mapping()


def _last_json(log: Path) -> dict[str, Any]:
    raw = log.read_text(encoding="utf-8", errors="replace").strip()
    decoder = json.JSONDecoder()
    values: list[Any] = []
    for index, char in enumerate(raw):
        if char != "{":
            continue
        try:
            value, end = decoder.raw_decode(raw[index:])
        except json.JSONDecodeError:
            continue
        if raw[index + end:].strip():
            continue
        values.append(value)
    if len(values) != 1 or not isinstance(values[0], dict):
        raise CaseError("grader stdout must end in exactly one JSON object")
    return values[0]


def _grade_command(case: dict[str, Any], workspace: Path, repo: Path) -> list[str]:
    return _substitute(case["grader"], workspace=workspace, repo=repo, case=Path(case["_dir"]))


def _grade(case: dict[str, Any], run: Path, *, initial: bool = False) -> dict[str, Any]:
    workspace = run / "workspace"
    log = run / "logs" / ("initial-grader.log" if initial else f"grader-{uuid.uuid4().hex}.log")
    runtime = _run(_grade_command(case, workspace, Path(run_state(run)["repo"])), stage_id="CHECKPOINT-GRADER",
                   timeout_s=float(case["grader_timeout_s"]), cwd=workspace, log=log)
    result: dict[str, Any] = {"execution_status": runtime["status"], "elapsed_s": runtime["elapsed_s"],
                              "log_path": str(log), "usage": "UNKNOWN"}
    if runtime["status"] not in {"PASS", "FAIL"}:
        result.update(outcome="ERROR", findings=[{"code": "GRADER_EXECUTION", "message": runtime["status"]}])
        return result
    payload = _last_json(log)
    if set(payload) - {"schema", "outcome", "findings", "evidence"} or payload.get("schema") != 1 or payload.get("outcome") not in {"PASS", "FAIL", "ERROR"}:
        raise CaseError("grader JSON has an invalid schema or outcome")
    findings = payload.get("findings")
    if not isinstance(findings, list) or not all(isinstance(row, dict) and set(row) == {"code", "message"} and isinstance(row["code"], str) and isinstance(row["message"], str) for row in findings):
        raise CaseError("grader findings must be [{code,message}]")
    expected_rc = {"PASS": 0, "FAIL": 1, "ERROR": 2}[payload["outcome"]]
    if runtime["returncode"] != expected_rc:
        raise CaseError("grader exit code does not match grader outcome")
    result.update(payload)
    return result


def run_state(run_dir: Path) -> dict[str, Any]:
    source = run_dir / "state.json"
    if not source.is_file() or source.is_symlink():
        raise CaseError("run state is missing or unsafe")
    return json.loads(source.read_text(encoding="utf-8"))


def _context(case: dict[str, Any], repo: Path, destination: Path) -> dict[str, str]:
    authority = repo / "skills/pcb-design/references/skill-authority-map.json"
    stage = case["checkpoint"]["stage_id"]
    graph = json.loads(authority.read_text(encoding="utf-8"))
    wanted = {"skills/pcb-design/SKILL.md", "skills/kicad-pcb/SKILL.md", "skills/jlcpcb-fab/SKILL.md", "skills/pcb-design/references/skill-authority-map.json"}
    for row in graph["stages"]:
        if row["spec"]["id"] == stage:
            domains = set(row.get("domains", []))
            for domain in graph["domains"]:
                if domain["id"] in domains:
                    wanted.update(domain.get("references", []))
            break
    for relative in sorted(wanted):
        source = repo / relative
        if source.is_symlink() or not source.is_file():
            raise CaseError(f"skill context source is missing or unsafe: {relative}")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    spec = next(row["spec"] for row in graph["stages"] if row["spec"]["id"] == stage)
    (destination / "START.md").write_text(
        "# Checkpoint task\n\n"
        "Work only in the prepared workspace. Read `TASK.md`, then the pcb-design "
        "entrypoint and only the owning skill/reference material selected for this stage. The current "
        f"graph stage is `{stage}`. Preserve the checkpoint state and history "
        "below. Finish with a nonempty `HANDOFF.md` in the workspace.\n\n"
        f"Trusted repository (read-only reference/tools): `{repo}`\n\n"
        f"Allowed edits: {', '.join(case['editable'])}\n\n"
        f"Origin reduction: {case['origin']['reduction']}\n\n"
        f"Initial finding codes to resolve: {', '.join(case['initial_findings']) or '(none)'}\n\n"
        f"Stage prerequisites: {', '.join(spec.get('requires', [])) or '(none)'}\n\n"
        "These reduced fixture states are exercise context, not acceptance receipts for a full board.\n\n"
        "```json\n" + json.dumps(case["checkpoint"], indent=2, sort_keys=True) + "\n```\n",
        encoding="utf-8")
    return _tree(destination)


def prepare(case_dir: str | Path, run_dir: str | Path, repo: str | Path = ROOT) -> dict[str, Any]:
    repo_path, run = Path(repo).resolve(), Path(run_dir).resolve()
    if run.exists():
        raise CaseError("run_dir must not already exist (fresh run required)")
    case = load_case(case_dir, repo=repo_path)
    run.mkdir(parents=True)
    workspace = run / "workspace"
    _copy_tree(Path(case["_dir"]) / case["snapshot_dir"], workspace)
    task = Path(case["_dir"]) / case["task_file"]
    shutil.copy2(task, workspace / "TASK.md")
    context_hashes = _context(case, repo_path, workspace / ".checkpoint_context")
    tool_hashes = _trusted_manifest(repo_path)
    state = {"schema": 1, "case_dir": case["_dir"], "repo": str(repo_path), "repo_revision": _repo_revision(repo_path), "case_manifest": _manifest(Path(case["_dir"])),
             "context_manifest": context_hashes, "baseline": {}, "checkpoint": case["checkpoint"],
             "skill_revision_hashes": context_hashes, "tool_revision_hashes": tool_hashes,
             "execution": "UNKNOWN/manual", "usage": "UNKNOWN"}
    _write(run / "state.json", state)
    for index, argv in enumerate(case["prepare"]):
        runtime = _run(_substitute(argv, workspace=workspace, repo=repo_path, case=Path(case["_dir"])),
                       stage_id="CHECKPOINT-PREPARE", timeout_s=float(case["timeout_s"]), cwd=workspace,
                       log=run / "logs" / f"prepare-{index}.log")
        if runtime["status"] != "PASS" or runtime["returncode"] != 0:
            raise CaseError(f"prepare command {index} failed; see {runtime['log_path']}")
    state["baseline"] = _tree(workspace)
    _write(run / "state.json", state)
    initial = _grade(case, run, initial=True)
    codes = [row["code"] for row in initial.get("findings", [])]
    if initial.get("outcome") != "FAIL" or codes != case["initial_findings"]:
        raise CaseError("initial grader calibration must FAIL with exactly initial_findings")
    # The trusted calibration is permitted to materialize deterministic setup
    # evidence.  Its resulting tree, rather than the snapshot alone, is the
    # immutable baseline handed to the external worker.
    state["baseline"] = _tree(workspace)
    state["initial_grader"] = initial
    _write(run / "state.json", state)
    return state


def _allowed(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) or Path(path).match(pattern) for pattern in patterns)


def _identity(case: dict[str, Any], state: dict[str, Any], workspace: Path) -> None:
    if _manifest(Path(case["_dir"])) != state["case_manifest"]:
        raise CaseError("case identity changed after prepare")
    context = _tree(workspace / ".checkpoint_context")
    if context != state["context_manifest"]:
        raise CaseError("protected checkpoint context changed")
    if _trusted_manifest(Path(state["repo"])) != state["tool_revision_hashes"]:
        raise CaseError("trusted runner or skill dependency changed after prepare")


def _scope(case: dict[str, Any], state: dict[str, Any], workspace: Path) -> list[str]:
    after = _tree(workspace)
    failures: list[str] = []
    before = state["baseline"]
    for path in sorted(set(before) | set(after)):
        if before.get(path) == after.get(path):
            continue
        if path == ".checkpoint_context" or path.startswith(".checkpoint_context/") or not _allowed(path, case["editable"]):
            failures.append(f"protected or out-of-scope change: {path}")
    return failures


def grade(run_dir: str | Path) -> dict[str, Any]:
    run = Path(run_dir).resolve(); state = run_state(run)
    fatal_identity: CaseError | None = None
    try:
        case = load_case(state["case_dir"], repo=state["repo"]); workspace = run / "workspace"
        _identity(case, state, workspace)
        scope = _scope(case, state, workspace)
        handoff = workspace / "HANDOFF.md"
        if not handoff.is_file() or not handoff.read_text(encoding="utf-8", errors="replace").strip():
            scope.append("required nonempty HANDOFF.md is missing")
        elif state["baseline"].get("HANDOFF.md") == _sha(handoff):
            scope.append("required HANDOFF.md was not updated from the prepared baseline")
        if scope:
            result = {"schema": 1, "outcome": "ERROR", "execution_status": "NOT_RUN", "elapsed_s": 0.0,
                      "usage": "UNKNOWN", "findings": [{"code": "WORKSPACE_SCOPE", "message": item} for item in scope], "log_paths": []}
        else:
            result = _grade(case, run)
            if result["outcome"] == "PASS" and result["findings"]:
                raise CaseError("PASS grader result must have no findings")
            result.update(schema=1, log_paths=[result["log_path"]])
        execution = state.get("execution")
        result["engineering_outcome"] = result["outcome"]
        if isinstance(execution, dict):
            result["agent_execution"] = execution
        if "agent" in state:
            result["agent"] = state["agent"]
        if isinstance(execution, dict) and (execution.get("status") != "PASS" or execution.get("returncode") != 0):
            result["outcome"] = "ERROR"
            result.setdefault("findings", []).append({"code": "AGENT_EXECUTION",
                "message": f"agent command ended {execution.get('status')} (returncode={execution.get('returncode')})"})
    except (CaseError, OSError, json.JSONDecodeError) as exc:
        result = {"schema": 1, "outcome": "ERROR", "execution_status": "ERROR", "elapsed_s": 0.0,
                  "usage": "UNKNOWN", "findings": [{"code": "RUNNER_CONTRACT", "message": str(exc)}], "log_paths": []}
        if isinstance(exc, CaseError) and "protected checkpoint context changed" in str(exc):
            fatal_identity = exc
    result.setdefault("skill_revision_hashes", state.get("skill_revision_hashes", {}))
    result.setdefault("tool_revision_hashes", state.get("tool_revision_hashes", {}))
    _write(run / "result.json", result)
    if fatal_identity is not None:
        raise fatal_identity
    return result


def run_case(case_dir: str | Path, run_dir: str | Path, command: list[str], repo: str | Path = ROOT) -> dict[str, Any]:
    prepare(case_dir, run_dir, repo)
    run = Path(run_dir).resolve(); state = run_state(run); case = load_case(case_dir, repo=repo)
    workspace = run / "workspace"; runtime = _run(_substitute(command, workspace=workspace, repo=Path(repo).resolve(), case=Path(case["_dir"])), stage_id=case["checkpoint"]["stage_id"],
        timeout_s=float(case["timeout_s"]), cwd=workspace, log=run / "logs" / "agent-command.log")
    state["execution"] = runtime; _write(run / "state.json", state)
    result = grade(run)
    result["agent_execution"] = runtime
    _write(run / "result.json", result)
    return result


def _main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="action", required=True)
    for name in ("prepare", "run"):
        item = sub.add_parser(name); item.add_argument("--case", required=True); item.add_argument("--run-dir", required=True)
    sub.choices["run"].add_argument("command", nargs=argparse.REMAINDER)
    item = sub.add_parser("grade"); item.add_argument("--run-dir", required=True)
    item = sub.add_parser("list"); item.add_argument("--cases-dir", required=True); item.add_argument("--tag")
    args = parser.parse_args()
    try:
        if args.action == "prepare": value = prepare(args.case, args.run_dir)
        elif args.action == "grade": value = grade(args.run_dir)
        elif args.action == "run":
            command = args.command[1:] if args.command[:1] == ["--"] else args.command
            if not command: raise CaseError("run requires a command after --")
            value = run_case(args.case, args.run_dir, command)
        else:
            value = []
            for source in sorted(Path(args.cases_dir).rglob("case.json")):
                case = load_case(source.parent, repo=ROOT)
                if args.tag is None or args.tag in case["tags"]:
                    value.append({key: case[key] for key in ("id", "title", "tags", "checkpoint")})
        print(_json(value), end="")
        if args.action in {"prepare", "list"}:
            return 0
        return 0 if value.get("outcome") == "PASS" else 1
    except (CaseError, OSError, json.JSONDecodeError) as exc:
        print(_json({"schema": 1, "outcome": "ERROR", "error": str(exc)}), end="", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
