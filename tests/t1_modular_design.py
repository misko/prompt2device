#!/usr/bin/env python3
"""T1: independent modular decomposition coverage and bounded child work."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import types
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


def item(wid, phase, blocks, depends, back, evidence, stage="KICAD-PLACEMENT", external=()):
    return {"id": wid, "phase": phase, "stage_id": stage, "blocks": blocks,
            "depends_on": depends, "max_attempts": 2, "backtrack_to": back,
            "external_prerequisites": list(external),
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
        "external_prerequisites": [
            {"id": "connector_full", "kind": "connector_full",
             "phase_receipt": "verification/connector_full.json",
             "binding_receipt": "verification/connector_full_binding.json",
             "board_path": "candidate.kicad_pcb"}
        ],
        # P2 processing can feed P3 before the independent connector P2 task;
        # this intentionally rejects a rigid all-P2-before-any-P3 schedule.
        "work_items": [
            item("p1", "P1_FLOORPLAN", ["connector", "processing"], [], [], ["floorplan_receipt"]),
            item("p2_connector", "P2_BLOCK_PLACEMENT", ["connector"], ["p1"], ["p1"], ["connector_placement"]),
            item("p2_processing", "P2_BLOCK_PLACEMENT", ["processing"], ["p1"], ["p1"], ["processing_placement"]),
            item("p3_processing", "P3_CRITICAL_LOCAL_ROUTES", ["processing"], ["p2_processing"], ["p2_processing"], ["critical_route_receipt"], external=("connector_full",)),
            item("p4_joint", "P4_JOINT_PROOF", ["connector", "processing"], ["p2_connector", "p3_processing"], ["p1", "p2_connector", "p2_processing"], ["coupled_geometry_receipt"]),
            item("p5", "P5_INTEGRATED_PLACEMENT_REVIEW", ["connector", "processing"], ["p4_joint"], ["p1", "p2_connector", "p2_processing"], ["independent_placement_review"], external=("connector_full",)),
        ],
    }


def scoped_plan():
    source = plan()
    source["external_prerequisites"][0]["p3_scope"] = {
        "affected_work_items": ["p3_connector"],
        "independent_work_items": [{"id": "p3_processing",
                                    "rationale": "Processing local routes stay clear of connector assembly geometry."}],
    }
    connector_route = item("p3_connector", "P3_CRITICAL_LOCAL_ROUTES", ["connector"],
                           ["p2_connector"], ["p2_connector"], ["connector_route_receipt"],
                           external=("connector_full",))
    source["work_items"].insert(-2, connector_route)
    next(row for row in source["work_items"] if row["id"] == "p3_processing")["external_prerequisites"] = []
    joint = next(row for row in source["work_items"] if row["id"] == "p4_joint")
    joint["depends_on"] = sorted(joint["depends_on"] + ["p3_connector"])
    return source


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


def file_binding(root, relative):
    path = root / relative
    return {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size": path.stat().st_size}


def connector_full_fixture(root, source):
    phase = root / "verification/connector_full.json"; phase.parent.mkdir(parents=True, exist_ok=True)
    phase.write_text(json.dumps({"status": "PASS", "authority": {"base_status": "PASS"},
                                 "summary": {"base_unknown_count": 0}}))
    board = root / "candidate.kicad_pcb"; board.write_text("native candidate\n")
    binding = {"schema": 1, "kind": "connector-full-p3-binding",
               "full_receipt": file_binding(root, "verification/connector_full.json"),
               "task_subject": work_subject(source, circuit()).to_mapping(),
               "subject": {"kind": "native_board", "artifact": file_binding(root, "candidate.kicad_pcb")}}
    (root / "verification/connector_full_binding.json").write_text(json.dumps(binding))


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


@test("P3 and P5 require a freshly regraded, exactly bound connector FULL receipt")
def t_connector_full_external_prerequisite():
    source = plan(); root, p1 = attempt(source, "p1", evidence=["floorplan_receipt"])
    _, p2 = attempt(source, "p2_processing", evidence=["processing_placement"], root=root)
    _, p3 = attempt(source, "p3_processing", evidence=["critical_route_receipt"], root=root)
    connector_full_fixture(root, source)
    old = sys.modules.get("connector_assembly_phase_gate")
    sys.modules["connector_assembly_phase_gate"] = types.SimpleNamespace(
        regrade_phase_gate=lambda path, project, expected_phase: (expected_phase == "full", []))
    try:
        report = evaluate(source, circuit(), p1 + p2 + p3, evidence_root=root)
        eq(report["work"]["p3_processing"]["state"], "WORK_RECORDED", "bound FULL unlocks P3")
        (root / "candidate.kicad_pcb").write_text("changed native candidate\n")
        stale = evaluate(source, circuit(), p1 + p2 + p3, evidence_root=root)
        eq(stale["work"]["p3_processing"]["state"], "BLOCKED", "stale bound board blocks P3")
        check(stale["work"]["p3_processing"]["external_findings"], "stale binding has finding")
    finally:
        if old is None:
            del sys.modules["connector_assembly_phase_gate"]
        else:
            sys.modules["connector_assembly_phase_gate"] = old


@test("connector FULL cannot use an unrelated board or stale task subject", kind="known_bad")
def t_connector_full_rejects_unrelated_board_or_subject():
    source = plan(); root, p1 = attempt(source, "p1", evidence=["floorplan_receipt"])
    _, p2 = attempt(source, "p2_processing", evidence=["processing_placement"], root=root)
    _, p3 = attempt(source, "p3_processing", evidence=["critical_route_receipt"], root=root)
    connector_full_fixture(root, source)
    old = sys.modules.get("connector_assembly_phase_gate")
    sys.modules["connector_assembly_phase_gate"] = types.SimpleNamespace(
        regrade_phase_gate=lambda path, project, expected_phase: (expected_phase == "full", []))
    try:
        binding_path = root / "verification/connector_full_binding.json"
        binding = json.loads(binding_path.read_text())
        other = root / "other.kicad_pcb"; other.write_text("unrelated board\n")
        binding["subject"]["artifact"] = file_binding(root, "other.kicad_pcb")
        binding_path.write_text(json.dumps(binding))
        report = evaluate(source, circuit(), p1 + p2 + p3, evidence_root=root)
        eq(report["work"]["p3_processing"]["state"], "BLOCKED", "unrelated board blocks P3")
        connector_full_fixture(root, source)
        binding = json.loads(binding_path.read_text())
        binding["task_subject"] = {"semantic_sha256": "0" * 64, "raw_sha256": "0" * 64}
        binding_path.write_text(json.dumps(binding))
        report = evaluate(source, circuit(), p1 + p2 + p3, evidence_root=root)
        eq(report["work"]["p3_processing"]["state"], "BLOCKED", "stale task subject blocks P3")
    finally:
        if old is None:
            del sys.modules["connector_assembly_phase_gate"]
        else:
            sys.modules["connector_assembly_phase_gate"] = old


@test("connector FULL coupon binding names the exact plan board", kind="known_bad")
def t_connector_full_coupon_rejects_unrelated_plan_board():
    source = plan(); root, p1 = attempt(source, "p1", evidence=["floorplan_receipt"])
    _, p2 = attempt(source, "p2_processing", evidence=["processing_placement"], root=root)
    _, p3 = attempt(source, "p3_processing", evidence=["critical_route_receipt"], root=root)
    connector_full_fixture(root, source)
    coupon_board = root / "coupon.kicad_pcb"; coupon_board.write_text("coupon board\n")
    coupon_receipt = root / "verification/coupon.json"
    coupon_receipt.write_text(json.dumps({"kind": "connector-qualification-coupon-receipt", "status": "PASS",
                                          "inputs": {"coupon_board": file_binding(root, "coupon.kicad_pcb")}}))
    binding_path = root / "verification/connector_full_binding.json"
    binding = json.loads(binding_path.read_text())
    binding["subject"] = {"kind": "governed_coupon", "artifact": file_binding(root, "coupon.kicad_pcb"),
                          "coupon_receipt": file_binding(root, "verification/coupon.json"),
                          "target_board": file_binding(root, "candidate.kicad_pcb")}
    binding_path.write_text(json.dumps(binding))
    old = sys.modules.get("connector_assembly_phase_gate")
    sys.modules["connector_assembly_phase_gate"] = types.SimpleNamespace(
        regrade_phase_gate=lambda path, project, expected_phase: (expected_phase == "full", []))
    try:
        report = evaluate(source, circuit(), p1 + p2 + p3, evidence_root=root)
        eq(report["work"]["p3_processing"]["state"], "WORK_RECORDED", "bound coupon unlocks P3")
        other = root / "other.kicad_pcb"; other.write_text("unrelated plan board\n")
        binding["subject"]["target_board"] = file_binding(root, "other.kicad_pcb")
        binding_path.write_text(json.dumps(binding))
        report = evaluate(source, circuit(), p1 + p2 + p3, evidence_root=root)
        eq(report["work"]["p3_processing"]["state"], "BLOCKED", "unrelated coupon target blocks P3")
    finally:
        if old is None:
            del sys.modules["connector_assembly_phase_gate"]
        else:
            sys.modules["connector_assembly_phase_gate"] = old


@test("legacy schema-1 plans retain their pre-prerequisite P3/P5 behavior")
def t_legacy_plan_without_external_prerequisites():
    source = plan()
    source.pop("external_prerequisites")
    for row in source["work_items"]:
        row.pop("external_prerequisites")
    root, p1 = attempt(source, "p1", evidence=["floorplan_receipt"])
    _, p2 = attempt(source, "p2_processing", evidence=["processing_placement"], root=root)
    report = evaluate(source, circuit(), p1 + p2, evidence_root=root)
    eq(report["status"], "PASS", "legacy coverage verdict")
    eq(report["work"]["p3_processing"]["state"], "READY",
       "absent connector extension does not create a new legacy blocker")


@test("connector prerequisite extension rejects an unprotected P3", kind="known_bad")
def t_connector_extension_requires_every_p3():
    source = plan()
    next(row for row in source["work_items"] if row["id"] == "p3_processing")["external_prerequisites"] = []
    rejects(lambda: evaluate(source, circuit()), "every P3 task requires exactly connector_full")


@test("scoped independent P3 work can proceed while affected P3 and P5 await connector FULL")
def t_scoped_connector_prerequisite():
    source = scoped_plan()
    root, p1 = attempt(source, "p1", evidence=["floorplan_receipt"])
    _, p2_connector = attempt(source, "p2_connector", evidence=["connector_placement"], root=root)
    _, p2_processing = attempt(source, "p2_processing", evidence=["processing_placement"], root=root)
    observations = p1 + p2_connector + p2_processing
    report = evaluate(source, circuit(), observations, evidence_root=root)
    eq(report["work"]["p3_processing"]["state"], "READY", "independent P3 readiness")
    eq(report["work"]["p3_processing"]["blocked_by_external"], [], "independent scope")
    eq(report["work"]["p3_connector"]["state"], "BLOCKED", "affected P3 waits for FULL")
    eq(report["work"]["p5"]["blocked_by_external"], ["connector_full"], "P5 remains gated")
    eq(report["work"]["p3_processing"]["engineering_acceptance"], "NOT_EVALUATED", "claim limit")
    _, p3_processing = attempt(source, "p3_processing", evidence=["critical_route_receipt"], root=root)
    progressed = evaluate(source, circuit(), observations + p3_processing, evidence_root=root)
    eq(progressed["work"]["p3_processing"]["state"], "WORK_RECORDED", "independent work record")
    eq(progressed["work"]["p3_processing"]["engineering_acceptance"], "NOT_EVALUATED", "no acceptance shortcut")


@test("scoped affected P3 and P5 still require exact current connector FULL")
def t_scoped_connector_full_binding():
    source = scoped_plan()
    root, p1 = attempt(source, "p1", evidence=["floorplan_receipt"])
    _, p2_connector = attempt(source, "p2_connector", evidence=["connector_placement"], root=root)
    _, p2_processing = attempt(source, "p2_processing", evidence=["processing_placement"], root=root)
    _, p3_connector = attempt(source, "p3_connector", evidence=["connector_route_receipt"], root=root)
    _, p3_processing = attempt(source, "p3_processing", evidence=["critical_route_receipt"], root=root)
    _, p4 = attempt(source, "p4_joint", evidence=["coupled_geometry_receipt"], root=root)
    _, p5 = attempt(source, "p5", evidence=["independent_placement_review"], root=root)
    observations = p1 + p2_connector + p2_processing + p3_connector + p3_processing + p4 + p5
    connector_full_fixture(root, source)
    old = sys.modules.get("connector_assembly_phase_gate")
    sys.modules["connector_assembly_phase_gate"] = types.SimpleNamespace(
        regrade_phase_gate=lambda path, project, expected_phase: (expected_phase == "full", []))
    try:
        report = evaluate(source, circuit(), observations, evidence_root=root)
        eq(report["work"]["p3_connector"]["state"], "WORK_RECORDED", "affected P3 with FULL")
        eq(report["work"]["p5"]["state"], "WORK_RECORDED", "integrated review with FULL")
        (root / "candidate.kicad_pcb").write_text("changed native candidate\n")
        stale = evaluate(source, circuit(), observations, evidence_root=root)
        eq(stale["work"]["p3_connector"]["state"], "BLOCKED", "stale FULL blocks affected P3")
        eq(stale["work"]["p5"]["state"], "BLOCKED", "stale FULL blocks P5")
        eq(stale["work"]["p3_processing"]["state"], "WORK_RECORDED", "independent P3 remains recorded")
    finally:
        if old is None:
            del sys.modules["connector_assembly_phase_gate"]
        else:
            sys.modules["connector_assembly_phase_gate"] = old


@test("P3 scope must completely and consistently classify every local route", kind="known_bad")
def t_scoped_connector_rejects_omissions_and_conflicts():
    source = scoped_plan()
    scope = source["external_prerequisites"][0]["p3_scope"]
    scope["independent_work_items"] = []
    rejects(lambda: evaluate(source, circuit()), "partition every P3 task")

    source = scoped_plan()
    scope = source["external_prerequisites"][0]["p3_scope"]
    scope["independent_work_items"][0]["id"] = "p3_connector"
    rejects(lambda: evaluate(source, circuit()), "partition every P3 task")

    source = scoped_plan()
    scope = source["external_prerequisites"][0]["p3_scope"]
    scope["affected_work_items"] = ["p3_connector", "p3_processing"]
    rejects(lambda: evaluate(source, circuit()), "partition every P3 task")

    source = scoped_plan()
    scope = source["external_prerequisites"][0]["p3_scope"]
    scope["independent_work_items"][0]["rationale"] = " "
    rejects(lambda: evaluate(source, circuit()), "expected non-empty trimmed text")

    source = scoped_plan()
    next(row for row in source["work_items"] if row["id"] == "p3_connector")["external_prerequisites"] = []
    rejects(lambda: evaluate(source, circuit()), "differs from its P3 scope")

    source = scoped_plan()
    next(row for row in source["work_items"] if row["id"] == "p3_processing")["external_prerequisites"] = ["connector_full"]
    rejects(lambda: evaluate(source, circuit()), "differs from its P3 scope")


@test("all-independent P3 scope is explicit and a scope edit invalidates old attempts")
def t_scoped_connector_empty_affected_and_subject_identity():
    source = plan()
    source["external_prerequisites"][0]["p3_scope"] = {
        "affected_work_items": [],
        "independent_work_items": [{"id": "p3_processing", "rationale": "Local processing route is clear of connector geometry."}],
    }
    next(row for row in source["work_items"] if row["id"] == "p3_processing")["external_prerequisites"] = []
    root, p1 = attempt(source, "p1", evidence=["floorplan_receipt"])
    _, p2 = attempt(source, "p2_processing", evidence=["processing_placement"], root=root)
    report = evaluate(source, circuit(), p1 + p2, evidence_root=root)
    eq(report["work"]["p3_processing"]["state"], "READY", "all-independent scope")
    eq(report["work"]["p5"]["blocked_by_external"], ["connector_full"], "P5 remains gated")
    changed = copy.deepcopy(source)
    changed["external_prerequisites"][0]["p3_scope"]["independent_work_items"][0]["rationale"] += " Reviewed again."
    rejects(lambda: evaluate(changed, circuit(), p1 + p2, evidence_root=root), "stale subject")


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
