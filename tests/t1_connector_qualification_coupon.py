#!/usr/bin/env python3
"""T1: source-bound connector coupon production and physical receipt grading."""
from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path

import pcbnew
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import ROOT, check, contains, eq, main, test, tmpdir  # noqa: E402

PCB_SCRIPTS = ROOT / "skills/pcb-design/scripts"
sys.path.insert(0, str(PCB_SCRIPTS))
import connector_qualification_coupon as coupon  # noqa: E402

SOURCE = ROOT / "projects/crow-audio-carrier-v1"
CONFIG = Path("03_src/connector_qualification_coupon.yaml")
OUTPUT = Path("06_build/connector_qualification_coupon/current")


def fixture() -> Path:
    project = tmpdir("connector-coupon-")
    contract_path = Path("03_src/rules/connector_assemblies.yaml")
    contract = yaml.safe_load((SOURCE / contract_path).read_text(encoding="utf-8"))
    files = {
        contract_path,
        Path("03_src/rules/connector_assembly_phases.yaml"),
        CONFIG,
        Path("03_src/floorplan.yaml"),
        Path("03_src/rules/spoke_interface.yaml"),
        Path("04_kicad/crow_audio_carrier_v1.kicad_pcb"),
        Path("04_kicad/crow_audio_carrier_v1.kicad_pro"),
    }
    files.update(Path(row["path"]) for row in contract["evidence_sources"])
    for relative in sorted(files):
        destination = project / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / relative, destination)
    shutil.copytree(
        SOURCE / "03_src/lib/crow_audio_carrier.pretty",
        project / "03_src/lib/crow_audio_carrier.pretty")
    # The live carrier now records plug/boot variation as two additional physical
    # unknowns. Supply explicit fixture-only measurement plans for both; never
    # erase those unknowns to make the qualification census smaller.
    config = yaml.safe_load((project / CONFIG).read_text(encoding="utf-8"))
    for target_id in ("installed-plug-boot-axial", "installed-plug-boot-radial"):
        config["qualification"]["targets"].append({
            "assembly_id": "factory-rj45-spoke-bank",
            "target_kind": "tolerance", "target_id": target_id,
            "required_measurements": [
                {"name": "realized-minus", "unit": "mm", "minimum": 0.0, "maximum": None},
                {"name": "realized-plus", "unit": "mm", "minimum": 0.0, "maximum": None},
                {"name": "worst-case-clearance", "unit": "mm", "minimum": 0.5, "maximum": None}],
            "required_evidence_kinds": ["photo", "measurement_sheet"]})
    (project / CONFIG).write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    receipt = coupon.base.load_and_compile(project, contract_path)
    eq(receipt["status"], "INCOMPLETE", "physical fixture base status")
    receipt_path = project / "06_build/verification/connector_assembly_contract.json"
    receipt_path.parent.mkdir(parents=True)
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return project


def prepare_fixture() -> tuple[Path, Path, dict]:
    project = fixture()
    output = coupon.prepare(project, CONFIG, OUTPUT)
    request = json.loads((output / "request.json").read_text(encoding="utf-8"))
    return project, output, request


def evidence_rows(kinds: list[str] | set[str]) -> list[dict[str, str]]:
    return [{"kind": kind, "path": f"evidence/{kind}.txt"}
            for kind in sorted(kinds)]


def populate_evidence(project: Path) -> None:
    root = project / "evidence"
    root.mkdir()
    for kind in sorted(coupon._EVIDENCE_KINDS):  # noqa: SLF001
        (root / f"{kind}.txt").write_text(
            f"fixture-only {kind} record for receipt tests\n", encoding="utf-8")


def pass_response(project: Path, output: Path, request: dict) -> Path:
    populate_evidence(project)
    qual = request["qualification"]
    samples = []
    for assembly_id, count in qual["minimum_samples"].items():
        for index in range(count):
            samples.append({
                "sample_id": f"{assembly_id}-sample-{index + 1}",
                "assembly_id": assembly_id,
                "receptacle_lot": f"receptacle-lot-{index + 1}",
                "mate_lot": f"mate-lot-{index + 1}",
                "cable_lot": f"cable-lot-{index + 1}",
                "evidence": evidence_rows(
                    qual["required_sample_evidence_kinds"]),
            })
    hardware = []
    for required in qual["target_hardware"]:
        hardware.append({
            **required,
            "model": "MCHStreamer fixture model",
            "revision": "fixture revision A",
            "serial": "fixture serial 001",
            "evidence": evidence_rows(["photo", "lot_label"]),
        })
    observations = []
    for target in qual["targets"]:
        measurements = []
        for spec in target["required_measurements"]:
            minimum, maximum = spec["minimum"], spec["maximum"]
            if minimum is not None and maximum is not None:
                value = (minimum + maximum) / 2
            elif minimum is not None:
                value = minimum
            elif maximum is not None:
                value = maximum
            else:
                value = 1.0
            measurements.append({
                "name": spec["name"],
                "unit": spec["unit"],
                "values": [{"ref": ref, "value": value}
                           for ref in target["required_refs"]],
            })
        observations.append({
            "assembly_id": target["assembly_id"],
            "target_kind": target["target_kind"],
            "target_id": target["target_id"],
            "result": "PASS",
            "tested_refs": target["required_refs"],
            "measurements": measurements,
            "evidence": evidence_rows(target["required_evidence_kinds"]),
            "notes": "Observed on the exact governed coupon with required neighbors populated.",
        })
    response = {
        "schema": coupon.RESPONSE_SCHEMA,
        "kind": coupon.RESPONSE_KIND,
        "request_sha256": coupon._digest(  # noqa: SLF001
            (output / "request.json").read_bytes()),
        "coupon_id": request["coupon_id"],
        "target_hardware": hardware,
        "samples": samples,
        "instruments": [{
            "instrument_id": "fixture-bench-set",
            "roles": qual["required_instrument_roles"],
            "maker": "Fixture Instruments",
            "model": "Bench Set A",
            "serial": "fixture instrument serial 001",
            "resolution": "0.01 mm; 0.1 N; continuity audible",
            "calibration_date": "2026-09-07",
            "evidence": evidence_rows(["calibration_record"]),
        }],
        "observations": observations,
    }
    path = output / "physical-response.yaml"
    path.write_text(yaml.safe_dump(response, sort_keys=False), encoding="utf-8")
    return path


@test("exact full-outline connector coupon prepares and a complete response regrades PASS")
def t_prepare_and_grade_pass():
    project, output, request = prepare_fixture()
    eq(request["status"], "READY_FOR_FABRICATION", "request status")
    eq(request["summary"]["connector_count"], 11, "connector census")
    eq(request["summary"]["physical_target_count"], 23, "target census")
    eq(request["board"]["source_geometry_sha256"],
       request["board"]["coupon_geometry_sha256"], "geometry identity")
    check(not list(output.glob("*.kicad_prl")),
          "portable coupon retained KiCad per-user process state")
    board = pcbnew.LoadBoard(str(project / request["board"]["coupon"]["path"]))
    eq(sorted(fp.GetReference() for fp in board.GetFootprints()),
       ["FID1", "FID2", "FID3", "H1", "H2", "H3", "H4",
        "J1", "J10", "J11", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "J9"],
       "coupon footprint census")
    check(all(pad.GetNetCode() == 0 for fp in board.GetFootprints() for pad in fp.Pads()),
          "coupon contains functional connectivity")
    with zipfile.ZipFile(next(output.glob("*_gerbers.zip"))) as bundle:
        check(bundle.testzip() is None, "fabrication archive did not reopen cleanly")
    response = pass_response(project, output, request)
    receipt_path, receipt = coupon.grade(
        project, OUTPUT / "request.json", response.relative_to(project),
        OUTPUT / "qualification-receipt.json")
    eq(receipt["status"], "PASS", "complete physical response")
    eq(receipt["summary"]["pass_target_count"], 23, "PASS target denominator")
    eq(receipt["summary"]["sample_count"], 11, "sample denominator")
    reopened = coupon.verify(
        project, OUTPUT / "request.json", response.relative_to(project),
        receipt_path.relative_to(project))
    eq(reopened, receipt, "reopened grade receipt")


@test("unfilled response stays typed INCOMPLETE rather than laundering unknowns")
def t_unfilled_response_incomplete():
    project, output, _request = prepare_fixture()
    receipt = coupon.compile_grade(
        project, OUTPUT / "request.json", OUTPUT / "physical-response.yaml")
    eq(receipt["status"], "INCOMPLETE", "unfilled response status")
    eq(receipt["summary"]["unobserved_target_count"], 23,
       "unobserved target denominator")
    eq(receipt["summary"]["finding_count"], 28, "incomplete finding census")


@test("coupon geometry drift fails even when an attacker refreshes byte bindings",
      kind="known_bad")
def t_coupon_geometry_drift_rejected():
    project, output, request = prepare_fixture()
    relative = Path(request["board"]["coupon"]["path"])
    board_path = project / relative
    board = pcbnew.LoadBoard(str(board_path))
    j1 = next(fp for fp in board.GetFootprints() if fp.GetReference() == "J1")
    j1.SetPosition(j1.GetPosition() + pcbnew.VECTOR2I(pcbnew.FromMM(1.0), 0))
    board.Save(str(board_path))
    binding = coupon._binding_bytes(board_path, relative.as_posix())  # noqa: SLF001
    request["board"]["coupon"] = binding
    for index, artifact in enumerate(request["artifacts"]):
        if artifact["path"] == relative.as_posix():
            request["artifacts"][index] = binding
    (output / "request.json").write_text(
        json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        coupon.compile_grade(
            project, OUTPUT / "request.json", OUTPUT / "physical-response.yaml")
    except coupon.ContractError as exc:
        contains(str(exc), "geometry is stale", "geometry-drift verdict")
    else:
        raise AssertionError("moved connector SHOULD HAVE invalidated the coupon")


if __name__ == "__main__":
    sys.exit(main())
