"""Strict, deliberately small schema reader for checkpoint exercises."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping


class CaseError(ValueError):
    """A case is malformed or cannot be safely used."""


STATE_VALUES = frozenset({"pending", "accepted", "failed", "blocked", "not_applicable"})


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CaseError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _mapping(value: Any, name: str, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        missing = sorted(keys - set(value)) if isinstance(value, dict) else sorted(keys)
        extra = sorted(set(value) - keys) if isinstance(value, dict) else []
        raise CaseError(f"{name} must contain exactly {sorted(keys)} (missing={missing}, extra={extra})")
    return value


def _string(value: Any, name: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value):
        raise CaseError(f"{name} must be a{' nonempty' if nonempty else ''} string")
    return value


def _relative(value: Any, name: str) -> str:
    text = _string(value, name)
    path = Path(text)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise CaseError(f"{name} must be a relative path without traversal")
    return text


def _argv(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise CaseError(f"{name} must be a nonempty argv list of nonempty strings")
    return list(value)


def _stage_ids(repo: Path) -> set[str]:
    authority = repo / "skills/pcb-design/references/skill-authority-map.json"
    try:
        data = json.loads(authority.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicates)
        return {row["spec"]["id"] for row in data["stages"] if isinstance(row, dict)}
    except (OSError, KeyError, TypeError, json.JSONDecodeError, CaseError) as exc:
        raise CaseError(f"cannot read current skill authority map: {exc}") from exc


def load_case(case_dir: str | Path, *, repo: str | Path) -> dict[str, Any]:
    """Read and validate ``case.json`` without following a case-controlled link."""
    directory = Path(case_dir).resolve()
    if directory.is_symlink() or not directory.is_dir():
        raise CaseError("case directory must be a real directory")
    source = directory / "case.json"
    if source.is_symlink() or not source.is_file():
        raise CaseError("case.json is missing or is a symlink")
    try:
        raw = json.loads(source.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicates)
    except (OSError, json.JSONDecodeError, CaseError) as exc:
        raise CaseError(f"invalid case.json: {exc}") from exc
    case = _mapping(raw, "case", {"schema", "id", "title", "tags", "origin", "checkpoint", "task_file", "snapshot_dir", "editable", "prepare", "grader", "initial_findings", "timeout_s", "grader_timeout_s"})
    if case["schema"] != 1:
        raise CaseError("case.schema must be 1")
    _string(case["id"], "id"); _string(case["title"], "title")
    if not isinstance(case["tags"], list) or not all(isinstance(x, str) and x for x in case["tags"]):
        raise CaseError("tags must be a list of nonempty strings")
    origin = _mapping(case["origin"], "origin", {"board", "revision", "evidence", "reduction"})
    _string(origin["board"], "origin.board"); _string(origin["revision"], "origin.revision")
    _string(origin["reduction"], "origin.reduction")
    if not isinstance(origin["evidence"], list) or not all(isinstance(x, str) for x in origin["evidence"]):
        raise CaseError("origin.evidence must be a list of strings")
    checkpoint = _mapping(case["checkpoint"], "checkpoint", {"stage_id", "states", "history"})
    stage = _string(checkpoint["stage_id"], "checkpoint.stage_id")
    if stage not in _stage_ids(Path(repo).resolve()):
        raise CaseError(f"checkpoint.stage_id is not a current authority stage: {stage}")
    stages = _stage_ids(Path(repo).resolve())
    if not isinstance(checkpoint["states"], dict) or not checkpoint["states"]:
        raise CaseError("checkpoint.states must be a nonempty mapping")
    unknown_stages = sorted(set(checkpoint["states"]) - stages)
    if unknown_stages:
        raise CaseError(f"checkpoint.states has unknown current stages: {unknown_stages}")
    if stage not in checkpoint["states"]:
        raise CaseError("checkpoint.states must include checkpoint.stage_id")
    invalid_states = sorted({value for value in checkpoint["states"].values() if value not in STATE_VALUES})
    if invalid_states:
        raise CaseError("checkpoint.states values must be one of " + ", ".join(sorted(STATE_VALUES)))
    if not isinstance(checkpoint["history"], list):
        raise CaseError("checkpoint.history must be a list")
    for index, history in enumerate(checkpoint["history"]):
        # History is evidence carried from the source campaign.  Its known
        # fields are required, while additional provenance remains opaque.
        if not isinstance(history, dict) or not {"attempt", "result", "disposition", "reconsider_when"} <= set(history):
            raise CaseError(f"checkpoint.history[{index}] must include attempt, result, disposition, reconsider_when")
        if not isinstance(history["attempt"], int) or history["attempt"] < 0:
            raise CaseError(f"checkpoint.history[{index}].attempt must be a nonnegative integer")
        for key in ("result", "disposition", "reconsider_when"):
            _string(history[key], f"checkpoint.history[{index}].{key}")
    _relative(case["task_file"], "task_file"); _relative(case["snapshot_dir"], "snapshot_dir")
    if not isinstance(case["editable"], list) or not case["editable"] or not all(isinstance(x, str) and x and not Path(x).is_absolute() and ".." not in Path(x).parts for x in case["editable"]):
        raise CaseError("editable must be nonempty relative glob patterns without traversal")
    if not any(Path("HANDOFF.md").match(pattern) for pattern in case["editable"]):
        raise CaseError("editable must explicitly allow HANDOFF.md")
    if not isinstance(case["prepare"], list):
        raise CaseError("prepare must be a list of argv lists")
    case["prepare"] = [_argv(row, f"prepare[{i}]") for i, row in enumerate(case["prepare"])]
    case["grader"] = _argv(case["grader"], "grader")
    if not isinstance(case["initial_findings"], list) or not all(isinstance(x, str) and x for x in case["initial_findings"]):
        raise CaseError("initial_findings must be a list of nonempty codes")
    for key in ("timeout_s", "grader_timeout_s"):
        value = case[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise CaseError(f"{key} must be a positive finite number")
    for relative in (case["task_file"], case["snapshot_dir"]):
        item = directory / relative
        if item.is_symlink() or not item.exists():
            raise CaseError(f"case {relative} is missing or is a symlink")
    if not (directory / case["task_file"]).is_file() or not (directory / case["snapshot_dir"]).is_dir():
        raise CaseError("task_file must be a file and snapshot_dir must be a directory")
    case["_dir"] = str(directory)
    return case
