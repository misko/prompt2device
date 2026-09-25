#!/usr/bin/env python3
"""Bound one hash-pinned PCB research producer; never admit engineering work.

This is an adapter over TaskAttempt, decision_progress and the existing
content-addressed experiment store.  Its receipt is diagnostic only.  The
caller supplies reviewed hashes; this module never turns a measured hash into
an expected authority hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any
import yaml

from decision_progress import evaluate as decision_evaluate, reserve_launch
from pipeline_execution import TaskEnvelope, verify_input_packet
from pipeline_identity import TypedIdentityInput, subject_identity
from pipeline_runtime import execute_attempt

REQUIRED = frozenset({"board", "netlist", "circuit", "floorplan", "p1_source",
                      "p1_contract", "interfaces", "aliases", "modular_plan",
                      "pro", "dru", "route_config", "producer", "p1_checker", "modular_checker"})
OPTIONAL = frozenset({"edge_authority"})
TOOLS = frozenset({"producer", "p1_checker", "modular_checker"})
HEX = re.compile(r"[0-9a-f]{64}\Z")
SAFE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _path(root: Path, relative: str, label: str) -> Path:
    if not isinstance(relative, str) or not relative or ".." in PurePosixPath(relative).parts:
        raise ValueError(f"{label}: project-relative path required")
    path = PurePosixPath(relative)
    if path.is_absolute() or path.as_posix() in (".", ""):
        raise ValueError(f"{label}: project-relative path required")
    target = root / path
    if target.is_symlink() or not target.resolve().is_relative_to(root):
        raise ValueError(f"{label}: symlink or project escape refused")
    return target


def _input_path(root: Path, relative: str, label: str) -> Path:
    if relative.startswith("repo:"):
        if label not in TOOLS:
            raise ValueError(f"{label}: only tool roles may use repo authority")
        repo = Path(__file__).resolve().parents[3]
        return _path(repo, relative.removeprefix("repo:"), label)
    return _path(root, relative, label)


def preflight(project: Path, spec: dict[str, Any]) -> tuple[dict[str, Path], list[dict[str, Any]], Any]:
    """Verify all authority before creating a run directory or reserving budget."""
    root = project.resolve(strict=True)
    expected_fields = {"schema", "decision_id", "experiment_id", "files", "command",
                       "timeout_s", "output_root", "next_acceptance_consumer"}
    if (not expected_fields <= set(spec) or set(spec) - expected_fields - {"expected_candidate"}
            or spec["schema"] != 1):
        raise ValueError("research specification has unknown/missing fields or schema")
    if "expected_candidate" in spec:
        expected_candidate = spec["expected_candidate"]
        if not isinstance(expected_candidate, dict) or set(expected_candidate) != {"board", "p1_source", "p1_contract"}:
            raise ValueError("expected_candidate requires exact board/source/contract digests")
        if any(not isinstance(value, str) or not HEX.fullmatch(value)
               for value in expected_candidate.values()):
            raise ValueError("expected_candidate requires independently pinned SHA-256 digests")
    if not isinstance(spec["decision_id"], str) or not spec["decision_id"]:
        raise ValueError("semantic decision_id required")
    if not SAFE.fullmatch(str(spec["experiment_id"])):
        raise ValueError("unsafe experiment_id")
    files = spec["files"]
    if not isinstance(files, dict) or not REQUIRED <= set(files) or set(files) - REQUIRED - OPTIONAL:
        raise ValueError(f"files require {sorted(REQUIRED)} and only optional {sorted(OPTIONAL)}")
    paths: dict[str, Path] = {}
    packet = []
    for role, record in sorted(files.items()):
        if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
            raise ValueError(f"{role}: exact path/sha256 required")
        expected = record["sha256"]
        if not isinstance(expected, str) or not HEX.fullmatch(expected):
            raise ValueError(f"{role}: independent expected SHA-256 required")
        path = _input_path(root, record["path"], role)
        if not path.is_file() or path.stat().st_size == 0 or _sha(path) != expected:
            raise ValueError(f"{role}: missing, empty or stale input")
        paths[role] = path
        if not record["path"].startswith("repo:"):
            packet.append({"name": role, "path": record["path"],
                           "sha256": expected, "size": path.stat().st_size})
    if paths["pro"].suffix != ".kicad_pro" or paths["dru"].suffix != ".kicad_dru":
        raise ValueError("native PRO and DRU rule files required")
    if paths["pro"].stem != paths["dru"].stem:
        raise ValueError("PRO/DRU rule set stem mismatch")
    contract = json.loads(paths["p1_contract"].read_text())
    for key, role in (("board_sha256", "board"), ("source_sha256", "p1_source"),
                      ("interfaces_sha256", "interfaces"),
                      ("floorplan_sha256", "floorplan"),
                      ("aliases_sha256", "aliases")):
        if contract.get(key) != files[role]["sha256"]:
            raise ValueError(f"P1 contract {key} does not bind candidate {role}")
    source = yaml.safe_load(paths["p1_source"].read_text())
    if isinstance(source, dict) and source.get("physical_cell_edge_attachments") and "edge_authority" not in paths:
        raise ValueError("edge authority and reviewed SHA required for edge attachments")
    command = spec["command"]
    if (not isinstance(command, list) or not command or
            any(not isinstance(token, str) or not token for token in command)):
        raise ValueError("nonempty argv command required")
    if str(paths["producer"]) not in command and files["producer"]["path"] not in command:
        raise ValueError("command must invoke pinned producer")
    timeout = spec["timeout_s"]
    if type(timeout) not in (int, float) or not 0 < timeout <= 3600:
        raise ValueError("timeout_s must be positive and at most one hour")
    output = _path(root, spec["output_root"], "output_root")
    if not output.relative_to(root).as_posix().startswith("06_build/"):
        raise ValueError("producer output_root must be below 06_build")
    if output.exists():
        raise ValueError("producer output_root already exists")
    if not isinstance(spec["next_acceptance_consumer"], str) or not spec["next_acceptance_consumer"].strip():
        raise ValueError("explicit next acceptance consumer required")
    if decision_evaluate(root, spec["decision_id"])["decision"] != "CONTINUE_BOUNDED":
        raise ValueError("investigation requires assessment or reassessment before launch")
    identity = subject_identity("pcb-integration-candidate", 1, [TypedIdentityInput(
        "pinned_inputs", "mapping", {role: row["sha256"] for role, row in files.items()},
        json.dumps(files, sort_keys=True).encode())])
    return paths, packet, identity


def _diagnostics(paths: dict[str, Path], files: dict[str, Any], board: Path | None,
                 candidate_inputs: dict[str, Any] | None,
                 expected_candidate: dict[str, str] | None,
                 root: Path) -> dict[str, Any]:
    """Collect independent existing checks; an unavailable check stays unknown."""
    result: dict[str, Any] = {}
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("bound_modular_design", paths["modular_checker"])
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        observed = module.evaluate(json.loads(paths["modular_plan"].read_text()),
                                   json.loads(paths["circuit"].read_text()))
        result["modular"] = {**observed, "engineering_acceptance": "NOT_EVALUATED"}
    except Exception as exc:
        result["modular"] = {"status": "UNEVALUATED", "reason": f"{type(exc).__name__}: {exc}"}
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("bound_p1_capacity", paths["p1_checker"])
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        kwargs = dict(source_path=paths["p1_source"], interface_path=paths["interfaces"],
                      alias_path=paths["aliases"], floorplan_path=paths["floorplan"],
                      expected_source_sha256=files["p1_source"]["sha256"],
                      expected_interface_sha256=files["interfaces"]["sha256"],
                      expected_alias_sha256=files["aliases"]["sha256"],
                      expected_floorplan_sha256=files["floorplan"]["sha256"],
                      diagnose_all=True)
        if "edge_authority" in paths:
            kwargs.update(edge_authority_path=paths["edge_authority"],
                          expected_edge_authority_sha256=files["edge_authority"]["sha256"])
        for label, checked_board in (("baseline_p1", paths["board"]),
                                     ("candidate_p1", board)):
            if checked_board is None:
                result[label] = {"status": "UNEVALUATED", "reason": "producer emitted no exact candidate board"}
                continue
            if label == "candidate_p1":
                assert candidate_inputs is not None
                contract_hash = candidate_inputs["p1_contract"]["sha256"]
                source_hash = candidate_inputs["p1_source"]["sha256"]
                if expected_candidate is not None:
                    if any(candidate_inputs[role]["sha256"] != expected_candidate[role]
                           for role in expected_candidate):
                        result[label] = {"status": "UNEVALUATED",
                                         "reason": "produced candidate differs from independently pinned replay",
                                         "board_sha256": _sha(checked_board)}
                        continue
                    candidate_contract = _path(root, candidate_inputs["p1_contract"]["path"],
                                               "candidate p1_contract")
                    candidate_source = _path(root, candidate_inputs["p1_source"]["path"],
                                             "candidate p1_source")
                    candidate_contract_data = json.loads(candidate_contract.read_text())
                    required_bindings = (("board_sha256", expected_candidate["board"]),
                                         ("source_sha256", expected_candidate["p1_source"]),
                                         ("floorplan_sha256", files["floorplan"]["sha256"]),
                                         ("interfaces_sha256", files["interfaces"]["sha256"]),
                                         ("aliases_sha256", files["aliases"]["sha256"]))
                    if any(candidate_contract_data.get(key) != expected
                           for key, expected in required_bindings):
                        result[label] = {"status": "UNEVALUATED",
                                         "reason": "candidate contract mixes board/source or fixed planning authority",
                                         "board_sha256": _sha(checked_board)}
                        continue
                    candidate_kwargs = dict(kwargs, source_path=candidate_source,
                                            expected_source_sha256=expected_candidate["p1_source"])
                    observed = module.evaluate(checked_board, candidate_contract,
                                               expected_candidate["p1_contract"], **candidate_kwargs)
                    result[label] = {**observed, "board_sha256": _sha(checked_board),
                                     "engineering_acceptance": False,
                                     "reviewed_contract_for_this_board": True,
                                     "replay_hashes_pinned": True}
                    continue
                if (contract_hash != files["p1_contract"]["sha256"] or
                        source_hash != files["p1_source"]["sha256"]):
                    result[label] = {"status": "UNEVALUATED",
                                     "reason": "candidate source/contract lacks independently reviewed expected digest",
                                     "board_sha256": _sha(checked_board)}
                    continue
                if _sha(checked_board) != files["board"]["sha256"]:
                    result[label] = {"status": "UNEVALUATED",
                                     "reason": "reviewed P1 contract is stale for produced board",
                                     "board_sha256": _sha(checked_board)}
                    continue
            observed = module.evaluate(checked_board, paths["p1_contract"],
                                       files["p1_contract"]["sha256"], **kwargs)
            result[label] = {**observed, "board_sha256": _sha(checked_board),
                             "engineering_acceptance": False,
                             "reviewed_contract_for_this_board":
                                 _sha(checked_board) == files["board"]["sha256"]}
    except Exception as exc:
        result["baseline_p1"] = {"status": "UNEVALUATED", "reason": f"{type(exc).__name__}: {exc}"}
        result["candidate_p1"] = {"status": "UNEVALUATED", "reason": f"{type(exc).__name__}: {exc}"}
    return result


def _candidate_manifest(root: Path, output_root: str) -> tuple[dict[str, Any] | None, Path | None]:
    manifest = root / output_root / "candidate_inputs.json"
    if not manifest.is_file():
        return None, None
    data = json.loads(manifest.read_text())
    if not isinstance(data, dict) or set(data) != {"board", "p1_source", "p1_contract"}:
        raise ValueError("candidate_inputs.json requires exact board/source/contract records")
    paths = {}
    for role, record in data.items():
        if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
            raise ValueError(f"candidate {role}: exact path/sha256 required")
        path = _path(root, record["path"], f"candidate {role}")
        if not isinstance(record["sha256"], str) or not HEX.fullmatch(record["sha256"]):
            raise ValueError(f"candidate {role}: malformed observed hash")
        if not path.is_file() or _sha(path) != record["sha256"]:
            raise ValueError(f"candidate {role}: stale output manifest")
        paths[role] = path
    if not paths["board"].relative_to(root).as_posix().startswith(output_root + "/"):
        raise ValueError("candidate board must be in producer output root")
    return data, paths["board"]


def run(project: Path, spec: dict[str, Any]) -> dict[str, Any]:
    root = project.resolve(strict=True)
    paths, packet, subject = preflight(root, spec)
    ident = spec["experiment_id"]
    relative_output = spec["output_root"]
    attempt_path = f"06_build/task_runs/integration-{ident}/attempt.json"
    if (root / attempt_path).exists() or (root / f"06_build/task_runs/integration-{ident}").exists():
        raise ValueError("attempt already exists")
    store = root / "06_build/integration_candidates"
    if (store / "experiments" / f"{ident}.json").exists():
        raise ValueError("terminal candidate already exists")
    now = datetime.now(timezone.utc)
    envelope = TaskEnvelope(
        task_id=f"integration-{ident}", stage_id="P1", run_id=ident,
        subject=subject, executor="subprocess", execution_class="local",
        recommended_agent_role=None, agent_role=None, role_escalation_reason=None,
        context_mode="NOT_APPLICABLE", input_handoff_id=None,
        input_packet=packet,
        deadline_at=(now + timedelta(seconds=spec["timeout_s"])).isoformat().replace("+00:00", "Z"),
        max_nonimproving_attempts=1, replacement_limit=0,
        writer_scope={"mode": "EXCLUSIVE", "paths": [relative_output]},
        output_path=attempt_path)
    valid, failures = verify_input_packet(envelope, root)
    if not valid:
        raise ValueError(f"input changed before reservation: {failures}")
    # Match pcb_flow's placement/source admission. A legacy route has no
    # decision-admission credit, exactly as in pcb_flow; it remains research.
    tool_root = Path(__file__).resolve().parents[2] / "kicad-pcb/scripts"
    sys.path.insert(0, str(tool_root))
    import pcb_flow
    context = pcb_flow.resolve_context(root)
    if context.route_path != paths["route_config"]:
        raise ValueError("route config does not match pinned source admission input")
    if pcb_flow.run_decision_admission(context, "source") != 0:
        raise ValueError("pcb_flow source admission refused research producer")
    from critical_part_selection_admission import evaluate as selection_evaluate
    selection = selection_evaluate(root, root / "03_src/rules/critical_part_selection.yaml")
    if selection["status"] not in {"PASS", "PROTOTYPE_ONLY", "NOT_APPLICABLE"}:
        raise ValueError(f"critical selection refuses research: {selection['status']}: {selection['findings']}")
    if (root / "01_docs/pause_state.json").exists():
        from pause_state import verify as verify_pause_state
        pause_valid, pause_failures = verify_pause_state(root)
        if not pause_valid:
            raise ValueError(f"stale pause state refuses research: {pause_failures}")
    valid, failures = verify_input_packet(envelope, root)
    if not valid:
        raise ValueError(f"input changed during source admission: {failures}")
    tool_before = {role: _sha(paths[role]) for role in TOOLS}
    if any(tool_before[role] != spec["files"][role]["sha256"] for role in TOOLS):
        raise ValueError("pinned tool changed during source admission")
    # This semantic finding ID is stable across workers, producer hashes and retries.
    reservation = reserve_launch(root, spec["decision_id"], subject.semantic_sha256)
    # A new parent directory would otherwise appear as an out-of-scope write
    # in the runtime's pre/post tree census. The leaf remains producer-owned.
    (root / relative_output).parent.mkdir(parents=True, exist_ok=True)
    attempt = execute_attempt(envelope, spec["command"], cwd=root, env=dict(os.environ),
                              console=None)
    tool_after = {role: _sha(paths[role]) for role in TOOLS}
    manifest_error = None
    try:
        candidate_inputs, candidate_board = _candidate_manifest(root, relative_output)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        candidate_inputs, candidate_board = None, None
        manifest_error = f"{type(exc).__name__}: {exc}"
    candidate_hash = _sha(candidate_board) if candidate_board else None
    if tool_after != tool_before:
        diagnostics = {name: {"status": "UNEVALUATED", "reason": "pinned checker or producer changed"}
                       for name in ("modular", "baseline_p1", "candidate_p1")}
    else:
        diagnostics = _diagnostics(paths, spec["files"], candidate_board if candidate_hash else None,
                                   candidate_inputs, spec.get("expected_candidate"), root)
    progress = decision_evaluate(root, spec["decision_id"])
    research_status = ("INCOMPLETE" if attempt.status == "PASS" and tool_after == tool_before
                       and candidate_inputs is not None else "REJECTED")
    receipt = {"schema": 1, "kind": "pcb-integration-research", "experiment_id": ident,
               "decision_id": spec["decision_id"], "reservation_id": reservation,
               "subject": subject.to_mapping(), "input_packet": packet,
               "external_tool_hashes": tool_after,
               "tool_identity_valid_after_attempt": tool_after == tool_before,
               "candidate_inputs": candidate_inputs,
               "candidate_manifest_error": manifest_error,
               "candidate_board": ({"path": candidate_board.relative_to(root).as_posix(),
                                    "sha256": candidate_hash} if candidate_hash else None),
               "attempt_path": attempt_path, "attempt_status": attempt.status,
               "research_status": research_status, "assessment_owed": True,
               "diagnostics": diagnostics, "decision_progress": progress,
               "selection_status": selection["status"],
               "next_acceptance_consumer": spec["next_acceptance_consumer"],
               "engineering_acceptance": False, "p1_accepted": False,
               "release_admitted": False, "order_admitted": False}
    receipt_path = root / f"06_build/task_runs/integration-{ident}/research_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    store_script = Path(__file__).resolve().parents[2] / "kicad-pcb/scripts"
    sys.path.insert(0, str(store_script))
    from route_experiment_store import record
    record(store, ident, research_status,
           subject.raw_sha256, [], receipt_path, " ".join(spec["command"]))
    receipt["candidate_store"] = f"06_build/integration_candidates/experiments/{ident}.json"
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("spec", type=Path)
    args = parser.parse_args(argv)
    try:
        receipt = run(args.project, json.loads(args.spec.read_text()))
    except Exception as exc:
        print(f"INTEGRATION RESEARCH REFUSED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["research_status"] == "INCOMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
