#!/usr/bin/env python3
"""Explicit, one-attempt Codex adapter for checkpoint solving (spends tokens)."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from runner import ROOT, run_case
from schema import CaseError


def sandbox_preflight(executable="bwrap") -> dict:
    """Probe the Linux network-isolation primitive required by this CLI adapter.

    This detects the nested-host EPERM failure without a paid model request;
    it is not proof that every Codex sandbox operation will succeed.
    """
    argv = [executable, "--unshare-net", "--ro-bind", "/", "/", "--", "/usr/bin/true"]
    try:
        completed = subprocess.run(argv, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"outcome": "ERROR", "message": str(exc)}
    return {"outcome": "PASS" if completed.returncode == 0 else "ERROR",
            "returncode": completed.returncode,
            "message": (completed.stdout + completed.stderr)[-2000:]}


def command(run_dir: Path, model: str, effort: str, executable="codex") -> list[str]:
    return [executable, "-a", "never", "exec", "--ignore-user-config", "--ephemeral",
            "--json", "--color", "never", "--sandbox", "workspace-write",
            "--skip-git-repo-check", "-m", model,
            "-c", f'model_reasoning_effort="{effort}"',
            "-C", str(run_dir.resolve() / "workspace"),
            "Read .checkpoint_context/START.md and TASK.md. Resume the supplied PCB "
            "checkpoint using its current skill context. Solve the stated engineering "
            "problem within the allowed edits, run the relevant checks, and write "
            "HANDOFF.md explaining changed source, evidence and remaining limitations. "
            "Do not seek reference solutions or inspect case graders or sibling runs. "
            "Do not launch subagents, publish, use the network, or change requirements. "
            "Stop after this case's objective is satisfied or report a concrete blocker."]


def usage_from_log(path: Path) -> dict:
    """Collect provider-reported per-turn usage, without guessing missing tokens."""
    records = []
    commands = 0
    errors = []
    for line in path.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            records.append(event["usage"])
        if event.get("type") == "item.completed" and isinstance(event.get("item"), dict):
            commands += event["item"].get("type") == "command_execution"
        if event.get("type") in {"error", "turn.failed"}:
            errors.append(event.get("type"))
    keys = ("input_tokens", "cached_input_tokens", "output_tokens")
    totals = {key: sum(row[key] for row in records) if records and all(
        isinstance(row.get(key), int) and not isinstance(row[key], bool) and row[key] >= 0
        for row in records) else None for key in keys}
    complete = bool(records) and all(value is not None for value in totals.values())
    return {"status": "REPORTED" if complete else "PARTIAL" if records else "UNKNOWN", "source": "codex turn.completed",
            "completed_turns": len(records), "tokens": totals,
            "command_executions": commands, "error_events": errors, "cost": "UNKNOWN",
            "coverage": "completed turns only; interrupted-turn usage may be missing",
            "incomplete_fields": [key for key, value in totals.items() if value is None]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--model", required=True, help="Explicit provider model; no automatic escalation")
    parser.add_argument("--effort", choices=["low", "medium"], default="medium")
    parser.add_argument("--allow-agent", action="store_true", help="Required acknowledgement of model usage")
    args = parser.parse_args()
    if not args.allow_agent:
        parser.error("agent execution requires --allow-agent; deterministic tests do not need it")
    executable = shutil.which("codex")
    if executable is None:
        parser.error("codex CLI is unavailable")
    run_dir = Path(args.run_dir).resolve()
    preflight = sandbox_preflight()
    if preflight["outcome"] != "PASS":
        print(json.dumps({"schema": 1, "outcome": "ERROR", "findings": [
            {"code": "SANDBOX_UNAVAILABLE", "message": preflight["message"]}],
            "agent_launched": False, "usage": "NOT_INVOKED"}, indent=2))
        return 2
    try:
        result = run_case(args.case, run_dir, command(run_dir, args.model, args.effort, executable), repo=ROOT)
    except (CaseError, OSError, ValueError) as exc:
        result = {"schema": 1, "outcome": "ERROR", "error": str(exc)}
        if not (run_dir / "logs/agent-command.log").is_file():
            print(json.dumps(result))
            return 2
    result["agent"] = {"provider": "codex", "model": args.model, "effort": args.effort,
                       "attempts": 1, "usage": usage_from_log(run_dir / "logs/agent-command.log")}
    state_path = run_dir / "state.json"
    state = json.loads(state_path.read_text())
    state["agent"] = result["agent"]
    state_path.write_text(json.dumps(state, indent=2) + "\n")
    (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return {"PASS": 0, "FAIL": 1}.get(result.get("outcome"), 2)


if __name__ == "__main__":
    raise SystemExit(main())
