#!/usr/bin/env python3
"""T1: additive connector source/full phase admission over the base receipt."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import (KPY, ROOT, check, contains, eq, main, must_fail,  # noqa: E402
                     must_pass, run, test, tmpdir)

PCB_SCRIPTS = ROOT / "skills/pcb-design/scripts"
sys.path.insert(0, str(PCB_SCRIPTS))
import connector_assembly_contract as base  # noqa: E402
import connector_assembly_phase_gate as phase_gate  # noqa: E402

PHASE_GATE = PCB_SCRIPTS / "connector_assembly_phase_gate.py"
PROTOTYPE_GATE = (ROOT / "projects/crow-audio-carrier-v1/03_src"
                  / "check_connector_prototype.sh")


def prototype(project: Path):
    decision = project / "01_docs/decisions/0007-prototype-before-physical-qualification.md"
    decision.parent.mkdir(parents=True, exist_ok=True)
    decision.write_text("Fixture: explicitly commissioned unqualified prototype.\n")
    return run(["bash", PROTOTYPE_GATE, KPY, PCB_SCRIPTS, "[test]"], cwd=project)


def evidence(grade: str = "exact", source_ids: list[str] | None = None) -> dict:
    return {
        "grade": grade,
        "source_ids": ["fixture-record"] if source_ids is None else source_ids,
        "rationale": "Fixture fact or explicitly planned physical qualification.",
    }


def physical_unknown(source_ids: list[str] | None = None) -> dict:
    return evidence("unknown", ["fixture-record"] if source_ids is None else source_ids)


def contract() -> dict:
    known = evidence()
    return {
        "schema": 1,
        "contract_id": "phase-fixture-connectors",
        "evidence_sources": [
            {"id": "fixture-record", "kind": "manufacturer-drawing-record",
             "path": "02_parts/fixture/record.txt"},
            {"id": "fixture-placement", "kind": "placement-contract",
             "path": "03_src/floorplan.yaml"},
        ],
        "assemblies": [{
            "id": "fixture-bank",
            "instances": [
                {"ref": "J1", "mating_axis_board": [0.0, -1.0, 0.0],
                 "simultaneous_group_ids": ["all-fixture-connected"]},
                {"ref": "J2", "mating_axis_board": [0.0, -1.0, 0.0],
                 "simultaneous_group_ids": ["all-fixture-connected"]},
            ],
            "receptacle": {
                "manufacturer": "Fixture", "mpn": "FIX-HEADER",
                "mounting_method": "right-angle-through-hole",
                "model_source_id": None,
                "body_envelope_mm": {"x": 8.0, "y": 9.0, "z": 7.0},
                "evidence": copy.deepcopy(known),
            },
            "mate": {
                "manufacturer": "Fixture", "mpn": "FIX-MATE",
                "part_kind": "latched-cable-housing", "model_source_id": None,
                "body_envelope_mm": {"x": 12.0, "y": 9.0, "z": 7.0},
                "evidence": copy.deepcopy(known),
            },
            "interface": {
                "mating_plane_offset_mm": None,
                "minimum_exposure_mm": None,
                "exposure_setback_allowance_mm": None,
                "minimum_service_clearance_mm": None,
                "orientation_source_id": "fixture-placement",
                "evidence": physical_unknown(
                    ["fixture-record", "fixture-placement"]),
            },
            "grip": {
                "kind": "latch-housing", "across_flats_mm": 9.0,
                "outer_diameter_mm": None, "axial_length_mm": 10.0,
                "evidence": copy.deepcopy(known),
            },
            "fastening": {
                "method": "integral-latch", "thread_designation": None,
                "final_tightening": "latch-click-and-pull-check",
                "evidence": copy.deepcopy(known),
            },
            "tool": {
                "kind": "none", "identifier": None, "model_source_id": None,
                "head_envelope_mm": None, "approach": "none",
                "effective_sweep_radius_mm": None,
                "counter_tool_required": False,
                "evidence": copy.deepcopy(known),
            },
            "torque": {
                "required": False, "minimum_nm": None, "maximum_nm": None,
                "evidence": copy.deepcopy(known),
            },
            "reaction": {
                "method": "support-board-while-latching",
                "load_path": "housing-to-board-mounts",
                "evidence": physical_unknown(),
            },
            "cable": {
                "kind": "two-conductor", "manufacturer": "Fixture",
                "mpn": "FIX-CABLE", "outer_diameter_mm": 4.0,
                "straight_run_mm": 20.0, "minimum_bend_radius_mm": 20.0,
                "exit": "along_mating_axis", "evidence": copy.deepcopy(known),
            },
            "operations": [{
                "id": "mate", "sequence": 1, "kind": "mate",
                "required": True, "with_neighbors_populated": True,
                "start_state": "unmated", "end_state": "mated",
                "evidence": physical_unknown(),
            }],
            "tolerances": [
                {"id": "drawing-stack", "applies_to": "drawing_body",
                 "effect": "exposure_setback", "minus_mm": 0.1,
                 "plus_mm": 0.1, "evidence": copy.deepcopy(known)},
                {"id": "installed-stack", "applies_to": "installed_fixture_cell",
                 "effect": "exposure_setback", "minus_mm": None,
                 "plus_mm": None, "evidence": physical_unknown()},
            ],
        }],
        "simultaneous_groups": [{
            "id": "all-fixture-connected", "members": ["J1", "J2"],
            "required_state": "all_connected",
            "serviceable_member_refs": ["J1", "J2"],
        }],
    }


def policy() -> dict:
    return {
        "schema": 1,
        "phase_policy_id": "phase-fixture-physical-qualification",
        "source_deferrals": [
            {"assembly_id": "fixture-bank", "target_kind": "interface",
             "target_id": "interface",
             "unknown_class": "realized-interface-fit",
             "plan_source_ids": ["fixture-record", "fixture-placement"],
             "rationale": "Realized seating and exposure are measured later."},
            {"assembly_id": "fixture-bank", "target_kind": "reaction",
             "target_id": "reaction",
             "unknown_class": "reaction-qualification",
             "plan_source_ids": ["fixture-record"],
             "rationale": "Exercise the selected reaction path."},
            {"assembly_id": "fixture-bank", "target_kind": "operation",
             "target_id": "mate",
             "unknown_class": "simultaneous-operation-qualification",
             "plan_source_ids": ["fixture-record"],
             "rationale": "Exercise both populated connector instances."},
            {"assembly_id": "fixture-bank", "target_kind": "tolerance",
             "target_id": "installed-stack",
             "unknown_class": "installed-tolerance-qualification",
             "plan_source_ids": ["fixture-record"],
             "rationale": "Measure the installed process stack."},
        ],
    }


def fixture(value: dict | None = None, phase_policy: dict | None = None) -> Path:
    project = tmpdir("connector-phase-")
    (project / "03_src/rules").mkdir(parents=True)
    (project / "02_parts/fixture").mkdir(parents=True)
    (project / "02_parts/fixture/record.txt").write_text(
        "fixture drawing and qualification plan revision A\n")
    (project / "03_src/floorplan.yaml").write_text(
        "fixture_axes:\n  J1: [0, -1, 0]\n  J2: [0, -1, 0]\n")
    (project / base.DEFAULT_CONTRACT).write_text(yaml.safe_dump(
        contract() if value is None else value,
        sort_keys=False, allow_unicode=True))
    (project / phase_gate.DEFAULT_POLICY).write_text(yaml.safe_dump(
        policy() if phase_policy is None else phase_policy,
        sort_keys=False, allow_unicode=True))
    write_base(project)
    return project


def write_base(project: Path) -> dict:
    receipt = base.load_and_compile(project)
    output = project / phase_gate.DEFAULT_BASE_RECEIPT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(
        receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return receipt


def invoke(project: Path, phase: str, *extra: str):
    return run([
        KPY, "-B", PHASE_GATE, "--project", project, "--phase", phase,
        *extra,
    ], cwd=ROOT)


def close_physical(project: Path) -> None:
    path = project / base.DEFAULT_CONTRACT
    value = yaml.safe_load(path.read_text())
    assembly = value["assemblies"][0]
    assembly["interface"].update({
        "mating_plane_offset_mm": 8.0,
        "minimum_exposure_mm": 1.0,
        "exposure_setback_allowance_mm": 0.3,
        "minimum_service_clearance_mm": 0.5,
        "evidence": evidence(source_ids=["fixture-record", "fixture-placement"]),
    })
    assembly["reaction"]["evidence"] = evidence()
    assembly["operations"][0]["evidence"] = evidence()
    assembly["tolerances"][1].update({
        "minus_mm": 0.2, "plus_mm": 0.2, "evidence": evidence(),
    })
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True))
    write_base(project)


@test("source phase admits only explicitly typed physical unknowns")
def t_source_typed_unknowns_pass():
    project = fixture()
    result = must_pass(invoke(project, "source"), "typed source phase")
    contains(result.out, "CONNECTOR-PHASE SOURCE PASS", "source verdict")
    receipt = json.loads((project / phase_gate.DEFAULT_SOURCE_OUTPUT).read_text())
    eq(receipt["census"]["refs"], ["J1", "J2"], "closed connector census")
    eq(receipt["summary"]["base_unknown_count"], 4, "base unknown denominator")
    eq(receipt["summary"]["source_admitted_unknown_count"], 4,
       "typed physical admission denominator")
    check(phase_gate.validate_phase_gate(
        receipt, project, expected_phase="source") == (True, []),
        "fresh source receipt did not reopen exactly")


@test("full phase retains base PASS and zero-unknown requirement",
      kind="known_bad")
def t_full_rejects_any_unknown():
    project = fixture()
    result = must_fail(invoke(project, "full"), "full phase with unknowns",
                       expect="CONNECTOR-PHASE FULL INCOMPLETE")
    contains(result.out, "base_unknown=4", "full unknown denominator")


@test("full phase passes only after the unchanged base receipt passes")
def t_full_passes_closed_base():
    project = fixture()
    close_physical(project)
    base_receipt = json.loads(
        (project / phase_gate.DEFAULT_BASE_RECEIPT).read_text())
    eq(base_receipt["status"], "PASS", "closed base status")
    result = must_pass(invoke(project, "full"), "closed full phase")
    contains(result.out, "CONNECTOR-PHASE FULL PASS", "full verdict")


@test("source admits selected reversible cable exits while installed route is unknown")
def t_source_reversible_cable_route_deferral():
    value = contract()
    cable = value["assemblies"][0]["cable"]
    cable["exit"] = "board_axes"
    cable["exit_axes_board"] = [[0.0, -1.0, 0.0], [0.0, 1.0, 0.0]]
    cable["evidence"] = physical_unknown()
    phase_policy = policy()
    phase_policy["source_deferrals"].append({
        "assembly_id": "fixture-bank", "target_kind": "cable",
        "target_id": "cable",
        "unknown_class": "installed-cable-route-qualification",
        "plan_source_ids": ["fixture-record"],
        "rationale": "Installed cable end and route remain to be qualified.",
    })
    project = fixture(value, phase_policy=phase_policy)
    must_pass(invoke(project, "source"), "reversible cable source phase")
    must_fail(invoke(project, "full"), "reversible cable full phase",
              expect="CONNECTOR-PHASE FULL INCOMPLETE")


@test("full phase refuses an exact cable with no installed signed exit", kind="known_bad")
def t_full_requires_single_installed_cable_exit():
    value = contract()
    cable = value["assemblies"][0]["cable"]
    cable["exit"] = "board_axes"
    cable["exit_axes_board"] = [[0.0, -1.0, 0.0], [0.0, 1.0, 0.0]]
    project = fixture(value)
    close_physical(project)
    base_receipt = json.loads(
        (project / phase_gate.DEFAULT_BASE_RECEIPT).read_text())
    eq(base_receipt["status"], "PASS", "two-axis base physical status")
    result = must_fail(
        invoke(project, "full"), "ambiguous exact cable exit",
        expect="CONNECTOR-PHASE FULL INCOMPLETE")
    receipt = json.loads(
        (project / phase_gate.DEFAULT_FULL_OUTPUT).read_text())
    check(any(row["code"] == "FULL-CABLE-EXIT-SELECTION"
              for row in receipt["findings"]),
          "full phase did not name ambiguous installed cable exit")


@test("full phase accepts one exact installed signed cable exit")
def t_full_accepts_single_installed_cable_exit():
    value = contract()
    cable = value["assemblies"][0]["cable"]
    cable["exit"] = "board_axes"
    cable["exit_axes_board"] = [[0.0, 1.0, 0.0]]
    project = fixture(value)
    close_physical(project)
    must_pass(invoke(project, "full"), "selected signed cable exit")


@test("source phase rejects a missing receptacle identity", kind="known_bad")
def t_missing_identity_rejected():
    value = contract()
    receptacle = value["assemblies"][0]["receptacle"]
    receptacle.update({
        "manufacturer": None, "mpn": None, "mounting_method": None,
        "body_envelope_mm": None, "evidence": physical_unknown(),
    })
    project = fixture(value)
    result = must_fail(invoke(project, "source"), "missing identity",
                       expect="CONNECTOR-PHASE SOURCE INCOMPLETE")
    receipt = json.loads((project / phase_gate.DEFAULT_SOURCE_OUTPUT).read_text())
    check(any(row["code"] == "SOURCE-IDENTITY" for row in receipt["findings"]),
          "missing identity was not named")


@test("source phase rejects an unknown tool even when a policy exists elsewhere",
      kind="known_bad")
def t_disallowed_source_unknown_rejected():
    value = contract()
    value["assemblies"][0]["tool"]["evidence"] = physical_unknown()
    project = fixture(value)
    result = must_fail(invoke(project, "source"), "unknown tool",
                       expect="CONNECTOR-PHASE SOURCE INCOMPLETE")
    receipt = json.loads((project / phase_gate.DEFAULT_SOURCE_OUTPUT).read_text())
    check(any(row["target_kind"] == "tool" and not row["source_allowed"]
              for row in receipt["unknowns"]),
          "unknown tool was admitted by source")


@test("phase and status tampering cannot replay a source receipt",
      kind="known_bad")
def t_phase_and_status_tamper_rejected():
    project = fixture()
    must_pass(invoke(project, "source"), "source fixture")
    receipt = json.loads((project / phase_gate.DEFAULT_SOURCE_OUTPUT).read_text())
    phase_tamper = copy.deepcopy(receipt)
    phase_tamper["phase"] = "full"
    valid, findings = phase_gate.validate_phase_gate(
        phase_tamper, project, expected_phase="source")
    check(not valid and any("caller-required" in row for row in findings),
          "phase tamper replayed")
    status_tamper = copy.deepcopy(receipt)
    status_tamper["status"] = "INCOMPLETE"
    valid, findings = phase_gate.validate_phase_gate(
        status_tamper, project, expected_phase="source")
    check(not valid and any("status" in row for row in findings),
          "status tamper replayed")


@test("phase policy class/path mismatches fail rather than broaden source",
      kind="known_bad")
def t_policy_class_path_mismatch_rejected():
    broken = policy()
    broken["source_deferrals"][0]["unknown_class"] = \
        "reaction-qualification"
    project = fixture(phase_policy=broken)
    result = must_fail(invoke(project, "source"), "class/path mismatch",
                       expect="class/path mismatch")
    check(not (project / phase_gate.DEFAULT_SOURCE_OUTPUT).exists(),
          "malformed policy emitted a source receipt")


@test("empty plan evidence cannot authorize a physical deferral",
      kind="known_bad")
def t_empty_plan_evidence_rejected():
    broken = policy()
    broken["source_deferrals"][0]["plan_source_ids"] = []
    project = fixture(phase_policy=broken)
    result = must_fail(invoke(project, "source"), "empty plan evidence",
                       expect="expected non-empty unique string list")
    check(not (project / phase_gate.DEFAULT_SOURCE_OUTPUT).exists(),
          "empty-evidence policy emitted a source receipt")


@test("a stale base receipt invalidates its phase wrapper", kind="known_bad")
def t_stale_base_receipt_rejected():
    project = fixture()
    must_pass(invoke(project, "source"), "source fixture")
    receipt = json.loads((project / phase_gate.DEFAULT_SOURCE_OUTPUT).read_text())
    base_path = project / phase_gate.DEFAULT_BASE_RECEIPT
    stale = json.loads(base_path.read_text())
    stale["status"] = "PASS"
    base_path.write_text(json.dumps(stale, indent=2, sort_keys=True) + "\n")
    valid, findings = phase_gate.validate_phase_gate(
        receipt, project, expected_phase="source")
    check(not valid and any("base receipt" in row for row in findings),
          "stale base receipt did not invalidate phase receipt")


@test("evidence-byte drift invalidates both base and phase receipts",
      kind="known_bad")
def t_evidence_drift_rejected():
    project = fixture()
    must_pass(invoke(project, "source"), "source fixture")
    receipt = json.loads((project / phase_gate.DEFAULT_SOURCE_OUTPUT).read_text())
    (project / "02_parts/fixture/record.txt").write_text(
        "fixture drawing and qualification plan revision B\n")
    valid, findings = phase_gate.validate_phase_gate(
        receipt, project, expected_phase="source")
    check(not valid and any("stale or invalid" in row for row in findings),
          "evidence drift did not invalidate phase receipt")


@test("source receipt cannot be consumed as full", kind="known_bad")
def t_source_as_full_rejected():
    project = fixture()
    must_pass(invoke(project, "source"), "source fixture")
    receipt = json.loads((project / phase_gate.DEFAULT_SOURCE_OUTPUT).read_text())
    valid, findings = phase_gate.validate_phase_gate(
        receipt, project, expected_phase="full")
    check(not valid and any("caller-required" in row for row in findings),
          "source phase receipt replayed as full")


@test("carrier prototype admits classified physical unknowns without changing FULL")
def t_prototype_retains_unknowns():
    project = fixture()
    original = (project / phase_gate.DEFAULT_BASE_RECEIPT).read_bytes()
    result = must_pass(prototype(project), "prototype design admission")
    contains(result.out, "DO-NOT-ORDER", "separate order boundary")
    eq((project / phase_gate.DEFAULT_BASE_RECEIPT).read_bytes(), original,
       "base evidence must not be rewritten")
    receipt = json.loads((project / phase_gate.DEFAULT_FULL_OUTPUT).read_text())
    eq(receipt["status"], "INCOMPLETE", "physical qualification remains incomplete")
    must_fail(invoke(project, "full"), "prototype is not physical qualification")


@test("carrier prototype rejects unknown connector identity", kind="known_bad")
def t_prototype_unknown_identity():
    value = contract()
    value["assemblies"][0]["mate"]["evidence"] = physical_unknown()
    must_fail(prototype(fixture(value)), "unknown mating identity")


@test("carrier prototype rejects stale base evidence", kind="known_bad")
def t_prototype_stale_evidence():
    project = fixture()
    (project / "02_parts/fixture/record.txt").write_text("changed after compilation\n")
    must_fail(prototype(project), "stale connector authority")


@test("carrier prototype rejects omitted physical deferral", kind="known_bad")
def t_prototype_unclassified_unknown():
    value = policy()
    value["source_deferrals"].pop()
    must_fail(prototype(fixture(phase_policy=value)), "unclassified unknown")



def shared_prototype(project, decision='0005-first-article-only-release.md', create_decision=True):
    adr=project/'01_docs/decisions'/decision
    if create_decision:
        adr.parent.mkdir(parents=True,exist_ok=True)
        adr.write_text('Fixture of an already accepted project prototype decision.\n')
    return run(['bash',PCB_SCRIPTS/'connector_prototype_admission.sh',KPY,PCB_SCRIPTS,
                '[test]','01_docs/decisions/'+decision,'--compile-base'],cwd=project)

@test('shared admission compiles base under each existing project decision and retains FULL unknowns')
def t_shared_admission_compiles():
    for decision in ['0005-first-article-only-release.md','0007-prototype-before-physical-qualification.md']:
        p=fixture();(p/phase_gate.DEFAULT_BASE_RECEIPT).unlink()
        r=must_pass(shared_prototype(p,decision),'authorized prototype with physical debt')
        contains(r.out,'FIRST-ARTICLE-ONLY / DO-NOT-ORDER','prototype boundary')
        receipt=json.loads((p/phase_gate.DEFAULT_FULL_OUTPUT).read_text())
        eq(receipt['status'],'INCOMPLETE','physical unknowns are unchanged')
        ok,errors=phase_gate.validate_phase_gate(receipt,p,expected_phase='full')
        check(ok,str(errors))
        source=json.loads((p/phase_gate.DEFAULT_SOURCE_OUTPUT).read_text())
        eq(source['status'],'PASS','SOURCE must pass')

@test('shared prototype admission rejects missing or indirect decision',kind='known_bad')
def t_shared_missing_decision():
    p=fixture();must_fail(shared_prototype(p,create_decision=False),'missing prototype authority',expect='Missing')
    adr=p/'01_docs/decisions/0005-first-article-only-release.md';adr.parent.mkdir(parents=True,exist_ok=True)
    adr.symlink_to(p/'02_parts/fixture/record.txt')
    must_fail(shared_prototype(p,create_decision=False),'symlink prototype authority',expect='nonregular')

@test('shared prototype admission cannot admit fresh unknown identity',kind='known_bad')
def t_shared_unknown_identity():
    value=contract();value['assemblies'][0]['mate']['mpn']=None
    value['assemblies'][0]['mate']['evidence']=physical_unknown()
    must_fail(shared_prototype(fixture(value)),'unqualified source identity',expect='SOURCE INCOMPLETE')

@test('shared prototype admission rejects invalid base before continuation',kind='known_bad')
def t_shared_invalid_base():
    p=fixture();(p/base.DEFAULT_CONTRACT).write_text('schema: broken\n')
    must_fail(shared_prototype(p),'invalid connector base',expect='invalid connector base authority')

if __name__ == "__main__":
    sys.exit(main())
