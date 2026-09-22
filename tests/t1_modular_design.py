#!/usr/bin/env python3
"""T1: independent modular decomposition coverage and bounded child work."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import check, eq, main, test  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/pcb-design/scripts"))
from modular_design import ModularDesignError, evaluate, work_subject  # noqa: E402
from pipeline_execution import TaskEnvelope  # noqa: E402
from pipeline_runtime import execute_attempt  # noqa: E402


def circuit():
    return [
        {"type": "source_component", "source_component_id": "c_j1", "name": "J1"},
        {"type": "source_component", "source_component_id": "c_u1", "name": "U1"},
        {"type": "source_component", "source_component_id": "c_c1", "name": "C1"},
        {"type": "source_net", "source_net_id": "n_sig", "name": "SIG",
         "subcircuit_id": "s", "subcircuit_connectivity_map_key": "sig"},
        {"type": "source_net", "source_net_id": "n_gnd", "name": "GND",
         "subcircuit_id": "s", "subcircuit_connectivity_map_key": "gnd"},
        {"type": "source_port", "source_port_id": "p_j1", "source_component_id": "c_j1",
         "pin_number": 1, "subcircuit_id": "s", "subcircuit_connectivity_map_key": "sig"},
        {"type": "source_port", "source_port_id": "p_u1a", "source_component_id": "c_u1",
         "pin_number": 2, "subcircuit_id": "s", "subcircuit_connectivity_map_key": "sig"},
        {"type": "source_port", "source_port_id": "p_u1b", "source_component_id": "c_u1",
         "pin_number": 3, "subcircuit_id": "s", "subcircuit_connectivity_map_key": "gnd"},
        {"type": "source_port", "source_port_id": "p_c1", "source_component_id": "c_c1",
         "pin_number": 1, "subcircuit_id": "s", "subcircuit_connectivity_map_key": "gnd"},
        # Trace links exercise the real tscircuit connected-id representation.
        {"type": "source_trace", "connected_source_port_ids": ["p_j1"],
         "connected_source_net_ids": ["n_sig"]},
        {"type": "source_trace", "connected_source_port_ids": ["p_u1a"],
         "connected_source_net_ids": ["n_sig"]},
        {"type": "source_trace", "connected_source_port_ids": ["p_u1b", "p_c1"],
         "connected_source_net_ids": ["n_gnd"]},
    ]


def item(wid, phase, blocks, depends, back, evidence, stage="KICAD-PLACEMENT"):
    return {"id": wid, "phase": phase, "stage_id": stage, "blocks": blocks,
            "depends_on": depends, "max_attempts": 2, "backtrack_to": back,
            "evidence": evidence}


def plan():
    return {
        "schema": 1, "stage_id": "KICAD-PLACEMENT",
        "blocks": [
            {"id": "connector", "refs": ["J1"], "responsibilities": ["mechanical entry"]},
            {"id": "processing", "refs": ["C1", "U1"], "responsibilities": ["signal processing"]},
        ],
        "interfaces": [{"net": "SIG", "endpoints": {"connector": ["J1.1"], "processing": ["U1.2"]},
                        "requirements": ["preserve signal return"], "disposition": "joint corridor"}],
        "shared_responsibilities": [
            {"id": "ground_return", "owner": "board_integration", "requirements": ["continuous return plane"]}
        ],
        # P2 processing can feed P3 before the independent connector P2 task;
        # this intentionally rejects a rigid all-P2-before-any-P3 schedule.
        "work_items": [
            item("p1", "P1_FLOORPLAN", ["connector", "processing"], [], [], ["floorplan_receipt"]),
            item("p2_connector", "P2_BLOCK_PLACEMENT", ["connector"], ["p1"], ["p1"], ["connector_placement"]),
            item("p2_processing", "P2_BLOCK_PLACEMENT", ["processing"], ["p1"], ["p1"], ["processing_placement"]),
            item("p3_processing", "P3_CRITICAL_LOCAL_ROUTES", ["processing"], ["p2_processing"], ["p2_processing"], ["critical_route_receipt"]),
            item("p4_joint", "P4_JOINT_PROOF", ["connector", "processing"], ["p2_connector", "p3_processing"], ["p1", "p2_connector", "p2_processing"], ["coupled_geometry_receipt"]),
            item("p5", "P5_INTEGRATED_PLACEMENT_REVIEW", ["connector", "processing"], ["p4_joint"], ["p1", "p2_connector", "p2_processing"], ["independent_placement_review"]),
        ],
    }


def attempt(source, wid, status="PASS", evidence=(), index=0, root=None):
    root = root or Path(tempfile.mkdtemp(prefix="modular-work-"))
    attempt_path = root / "runs" / f"{wid}-{index}" / "attempt.json"
    outputs = attempt_path.parent / "outputs"; outputs.mkdir(parents=True)
    records = {}
    for name in list(evidence) + ["result.json"]:
        path = outputs / name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n" if name.endswith(".json") else "evidence\n")
        records[name] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size": path.stat().st_size}
    value = {"schema": 1, "task_id": wid, "envelope_sha256": "a" * 64,
            "attempt_index": index, "replacement_index": 0,
            "subject": work_subject(source, circuit()).to_mapping(),
            "started_at": "2026-09-21T10:00:00Z", "finished_at": "2026-09-21T10:00:01Z",
            "elapsed_s": 1.0, "status": status,
            "unresolved": [] if status == "PASS" else ["not complete"],
            "output": {"completion": {"schema": 1, "outputs": records,
                                        "checks": {"task": "PASS"}, "graded": 1, "total": 1}}}
    attempt_path.write_text(json.dumps(value))
    return root, [{"attempt_path": attempt_path.relative_to(root).as_posix()}]


def runtime_attempt(source, *, deliver: bool):
    root = Path(tempfile.mkdtemp(prefix="modular-runtime-"))
    output = "06_build/task_runs/p1-0/attempt.json"
    deadline = (datetime.now(timezone.utc) + timedelta(seconds=10)).isoformat().replace("+00:00", "Z")
    envelope = TaskEnvelope(
        schema=2, task_id="p1", stage_id="KICAD-PLACEMENT", run_id="modular-p1-0",
        subject=work_subject(source, circuit()), executor="subprocess",
        execution_class="local", recommended_agent_role=None, agent_role=None,
        role_escalation_reason=None, context_mode="NOT_APPLICABLE",
        input_handoff_id=None, input_packet=[], deadline_at=deadline,
        max_nonimproving_attempts=2, replacement_limit=0,
        writer_scope={"mode": "READ_ONLY", "paths": []}, output_path=output,
        completion={"outputs": ["floorplan_receipt"], "checks": ["probe"]}, repair=None)
    report = {"subject": envelope.subject.to_mapping(), "checks": {"probe": "PASS"}, "unresolved": []}
    code = ("import json,os; from pathlib import Path; "
            "p=Path(os.environ['PCB_TASK_OUTPUT_DIR']); "
            "(p/'floorplan_receipt').write_text('measured output'); "
            f"(p/'result.json').write_text({json.dumps(report)!r})") if deliver else "raise SystemExit(7)"
    result = execute_attempt(envelope, [sys.executable, "-c", code], cwd=root, env={}, console=None)
    return root, result, [{"attempt_path": output}]


def rejects(fn, phrase):
    try:
        fn()
    except ModularDesignError as exc:
        check(phrase in str(exc), f"{exc!s} does not contain {phrase!r}")
    else:
        raise AssertionError("malformed modular plan SHOULD HAVE FAILED")


@test("valid decomposition covers actual refs and every crossing endpoint")
def t_green():
    report = evaluate(plan(), circuit())
    eq(report["status"], "PASS", "coverage verdict")
    eq(report["coverage"]["components_singly_owned"], 3, "component denominator")
    eq(report["coverage"]["crossing_nets_exactly_declared"], 1, "crossing denominator")
    eq(report["work"]["p1"]["state"], "READY", "initial floorplan readiness")
    eq(report["work"]["p3_processing"]["state"], "BLOCKED", "local proof blocker")
    eq(report["work"]["p1"]["engineering_acceptance"], "NOT_EVALUATED", "claim limit")


@test("omitted crossing, endpoint shortcut, and duplicate ownership all fail", kind="known_bad")
def t_coverage_reds():
    omitted = plan(); omitted["interfaces"] = []
    r = evaluate(omitted, circuit())
    check(r["status"] == "FAIL" and "observed crossing omitted" in r["findings"][0], "omitted crossing passed")
    shortened = plan(); shortened["interfaces"][0]["endpoints"]["processing"] = ["U1.9"]
    r = evaluate(shortened, circuit())
    check(r["status"] == "FAIL" and "endpoint coverage differs" in r["findings"][0], "invented endpoint passed")
    duplicate = plan(); duplicate["blocks"][0]["refs"].append("U1"); duplicate["blocks"][0]["refs"].sort()
    r = evaluate(duplicate, circuit())
    check(r["status"] == "FAIL" and any("exactly one owner" in f for f in r["findings"]), "duplicate owner passed")


@test("same-phase dependency orders correctly and child PASS cannot bypass parent")
def t_dependency_shortcut():
    source = plan()
    root, observations = attempt(source, "p2_connector", evidence=["connector_placement"])
    report = evaluate(source, circuit(), observations, evidence_root=root)
    eq(report["work"]["p2_connector"]["state"], "BLOCKED", "parent dependency is mandatory")
    eq(report["work"]["p4_joint"]["state"], "BLOCKED", "same-phase join remains blocked")


@test("stale TaskAttempt subject and non-backward repair are refused", kind="known_bad")
def t_stale_and_bad_backtrack():
    source = plan(); root, stale = attempt(source, "p1", evidence=["floorplan_receipt"])
    changed = copy.deepcopy(source); changed["blocks"][0]["responsibilities"] = ["changed boundary"]
    rejects(lambda: evaluate(changed, circuit(), stale, evidence_root=root), "stale subject")
    forward = plan(); forward["work_items"][0]["backtrack_to"] = ["p2_connector"]
    rejects(lambda: evaluate(forward, circuit()), "not earlier")


@test("P5 cannot omit a local or joint proof dependency", kind="known_bad")
def t_join_all_proofs():
    source = plan(); source["work_items"][-1]["depends_on"] = ["p2_connector"]
    rejects(lambda: evaluate(source, circuit()), "every prior work item")


@test("circuit census rejects unknown and pinless traced endpoints", kind="known_bad")
def t_bad_circuit_connectivity():
    unknown = circuit(); unknown[-1]["connected_source_port_ids"].append("missing")
    rejects(lambda: evaluate(plan(), unknown), "unknown port")
    pinless = circuit();
    next(row for row in pinless if row.get("source_port_id") == "p_j1")["pin_number"] = None
    rejects(lambda: evaluate(plan(), pinless), "lacks pin_number")
    duplicate = circuit(); duplicate.append(copy.deepcopy(next(row for row in duplicate if row.get("type") == "source_net")))
    rejects(lambda: evaluate(plan(), duplicate), "duplicate source_net id")
    ambiguous = circuit()
    second = copy.deepcopy(next(row for row in ambiguous if row.get("source_net_id") == "n_sig"))
    second.update(source_net_id="n_sig2", subcircuit_connectivity_map_key="sig2")
    ambiguous.append(second)
    port = next(row for row in ambiguous if row.get("source_port_id") == "p_u1a")
    port["subcircuit_connectivity_map_key"] = "sig2"
    trace = next(row for row in ambiguous if row.get("connected_source_port_ids") == ["p_u1a"])
    trace["connected_source_net_ids"] = ["n_sig2"]
    rejects(lambda: evaluate(plan(), ambiguous), "multiple disconnected nets")
    malformed_pin = circuit()
    next(row for row in malformed_pin if row.get("source_port_id") == "p_j1")["pin_number"] = True
    rejects(lambda: evaluate(plan(), malformed_pin), "unsupported pin_number")


@test("P1, P2, and P5 scopes cover every declared block", kind="known_bad")
def t_block_work_coverage():
    missing_p1 = plan(); missing_p1["work_items"][0]["blocks"] = ["connector"]
    rejects(lambda: evaluate(missing_p1, circuit()), "P1 floorplan covering every block")
    missing_p2 = plan(); missing_p2["work_items"] = [row for row in missing_p2["work_items"] if row["id"] != "p2_connector"]
    # Repair references only to isolate the missing P2 coverage predicate.
    next(row for row in missing_p2["work_items"] if row["id"] == "p4_joint")["depends_on"] = ["p3_processing"]
    for row in missing_p2["work_items"]:
        row["backtrack_to"] = [target for target in row["backtrack_to"] if target != "p2_connector"]
    rejects(lambda: evaluate(missing_p2, circuit()), "P2 placement work must cover every block")
    missing_p5 = plan(); missing_p5["work_items"][-1]["blocks"] = ["processing"]
    rejects(lambda: evaluate(missing_p5, circuit()), "P5 integrated placement review covering every block")


@test("attempt chronology is sorted and duplicate receipts are rejected", kind="known_bad")
def t_attempt_chronology():
    source = plan()
    root, old = attempt(source, "p1", evidence=["floorplan_receipt"], index=0)
    _, new = attempt(source, "p1", status="FAIL", evidence=["floorplan_receipt"], index=1, root=root)
    report = evaluate(source, circuit(), new + old, evidence_root=root)
    check(report["work"]["p1"]["state"] != "WORK_RECORDED", "older PASS overrode newer FAIL")
    rejects(lambda: evaluate(source, circuit(), old + old, evidence_root=root), "duplicate attempt identity")


@test("deleted completed output cannot unlock dependent work", kind="known_bad")
def t_deleted_output():
    source = plan(); root, observations = attempt(source, "p1", evidence=["floorplan_receipt"])
    (root / "runs/p1-0/outputs/floorplan_receipt").unlink()
    rejects(lambda: evaluate(source, circuit(), observations, evidence_root=root), "missing path")


@test("real runtime failure counts without completion and real delivery unlocks work")
def t_real_runtime_attempts():
    source = plan()
    failed_root, failed, failed_index = runtime_attempt(source, deliver=False)
    check(failed.status != "PASS" and failed.output["completion"] is None,
          "runtime fixture did not exercise absent completion")
    failed_report = evaluate(source, circuit(), failed_index, evidence_root=failed_root)
    eq(failed_report["work"]["p1"]["attempts"], 1, "failed runtime attempt count")
    check(failed_report["work"]["p1"]["state"] != "WORK_RECORDED",
          "failed runtime attempt unlocked child work")
    passed_root, passed, passed_index = runtime_attempt(source, deliver=True)
    eq(passed.status, "PASS", "real delivered runtime status")
    passed_report = evaluate(source, circuit(), passed_index, evidence_root=passed_root)
    eq(passed_report["work"]["p1"]["state"], "WORK_RECORDED", "real completion state")
    eq(passed_report["work"]["p2_connector"]["state"], "READY", "dependent readiness")


if __name__ == "__main__":
    main()
