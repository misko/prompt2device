#!/usr/bin/env python3
"""Prepare and independently grade the Crow coupled-geometry checkpoint."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pcbnew

sys.dont_write_bytecode = True
from native_fixture import MIN_WIDTH_MM, NETS, PAD_LAYOUT, build_from_source


HERE = Path(__file__).resolve().parent
PROTECTED = (
    "03_src/route.yaml",
    "03_src/rules/nets.yaml",
    "03_src/rules/stackup.yaml",
    "build_native.py",
)
COPPER_CONFLICTS = {"clearance", "shorting_items", "tracks_crossing"}


def emit(outcome, findings=(), evidence=None, rc=None):
    payload = {
        "schema": 1,
        "outcome": outcome,
        "findings": [{"code": code, "message": message}
                     for code, message in findings],
    }
    if evidence is not None:
        payload["evidence"] = evidence
    print(json.dumps(payload, sort_keys=True))
    return rc if rc is not None else (0 if outcome == "PASS" else 1)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _nm(point):
    return (int(point.x), int(point.y))


def _track_row(item):
    ends = sorted((_nm(item.GetStart()), _nm(item.GetEnd())))
    width = (item.GetWidth(pcbnew.F_Cu) if item.GetClass() == "PCB_VIA"
             else item.GetWidth())
    return (str(item.GetNetname()), tuple(ends), int(width),
            int(item.GetLayer()), item.GetClass())


def _native_properties(prepared_path: Path, witness_path: Path):
    findings = []
    prepared = pcbnew.LoadBoard(str(prepared_path))
    witness = pcbnew.LoadBoard(str(witness_path))
    expected = {
        (net, ref, number,
         (pcbnew.FromMM(location[0]), pcbnew.FromMM(location[1])))
        for net in NETS for ref, number, location in PAD_LAYOUT[net]
    }
    actual = {
        (str(pad.GetNetname()), str(fp.GetReference()), str(pad.GetNumber()),
         _nm(pad.GetPosition()))
        for fp in witness.GetFootprints() for pad in fp.Pads()
        if str(pad.GetNetname()) in NETS
    }
    if actual != expected:
        expected_ids = {(n, r, p) for n, r, p, _ in expected}
        actual_ids = {(n, r, p) for n, r, p, _ in actual}
        if actual_ids != expected_ids:
            findings.append(("NET-POPULATION-CHANGED",
                             "the exact six required net terminals were not retained"))
        else:
            findings.append(("PAD-GEOMETRY-CHANGED",
                             "a fixed required pad moved from the synthetic pin field"))
    inherited = {_track_row(item) for item in prepared.GetTracks()}
    combined = {_track_row(item) for item in witness.GetTracks()}
    if not inherited <= combined:
        findings.append(("INHERITED-SEED-CHANGED",
                         "the combined witness dropped or changed prepared launch copper"))
    vias = [item for item in witness.GetTracks()
            if item.GetClass() == "PCB_VIA" and str(item.GetNetname()) in NETS]
    if vias:
        findings.append(("ZERO-VIA-CONSTRAINT",
                         f"required coupled nets contain {len(vias)} via(s)"))
    ordinary = [item for item in witness.GetTracks()
                if item.GetClass() != "PCB_VIA" and str(item.GetNetname()) in NETS]
    if any(item.GetLayer() != pcbnew.F_Cu for item in ordinary):
        findings.append(("FROZEN-LAYER-CONSTRAINT",
                         "required coupled copper must remain on F.Cu"))
    if any(item.GetWidth() < pcbnew.FromMM(MIN_WIDTH_MM) for item in ordinary):
        findings.append(("FROZEN-WIDTH-CONSTRAINT",
                         "required coupled copper is below 0.25 mm"))
    connectivity = witness.GetConnectivity()
    connectivity.Build(witness)
    for net in NETS:
        pads = [pad for fp in witness.GetFootprints() for pad in fp.Pads()
                if str(pad.GetNetname()) == net]
        if len(pads) != 3:
            continue
        connected = list(connectivity.GetConnectedItems(pads[0]))
        if any(pad not in connected for pad in pads[1:]):
            findings.append(("REQUIRED-TERMINAL-UNCONNECTED",
                             f"{net} does not connect all three required terminals"))
    return findings


def _native_drc(witness_path: Path):
    report = witness_path.with_suffix(".drc.json")
    completed = subprocess.run(
        ["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json",
         "-o", str(report), str(witness_path)],
        text=True, capture_output=True, timeout=60, check=False)
    if completed.returncode != 0 or not report.is_file():
        raise RuntimeError((completed.stdout + completed.stderr)[-3000:] or
                           f"native DRC exited {completed.returncode}")
    payload = json.loads(report.read_text())
    types = [str(row.get("type")) for row in payload.get("violations", [])]
    return payload, types


def _production_gate(repo: Path, workspace: Path, prepared: Path, witness: Path):
    output = workspace / "06_build/coupled"
    gate_workspace = output / "gate"
    receipt = output / "coupled-receipt.json"
    if gate_workspace.exists():
        shutil.rmtree(gate_workspace)
    if receipt.exists():
        receipt.unlink()
    command = [
        "/usr/bin/python3",
        str(repo / "skills/kicad-pcb/scripts/coupled_geometry_preflight.py"),
        "grade", str(workspace), "--prepared", str(prepared),
        "--witness", str(witness), "--workspace", str(gate_workspace),
        "--json", str(receipt),
    ]
    completed = subprocess.run(command, cwd=workspace, text=True,
                               capture_output=True, timeout=150, check=False)
    value = None
    if receipt.is_file():
        value = json.loads(receipt.read_text())
    return completed, receipt, value


def prepare(repo: Path, workspace: Path):
    shutil.copytree(HERE / "snapshot", workspace, dirs_exist_ok=True)
    try:
        prepared, witness = build_from_source(
            workspace, workspace / "06_build/coupled")
    except Exception as exc:
        return emit("ERROR", [("PREPARE-FAILED", str(exc))], rc=2)
    return emit("PASS", evidence={
        "prepared": str(prepared.relative_to(workspace)),
        "witness": str(witness.relative_to(workspace)),
        "scope": "synthetic native Crow-inspired neighborhood",
    })


def grade(repo: Path, workspace: Path):
    findings = []
    for relative in PROTECTED:
        expected = HERE / "snapshot" / relative
        actual = workspace / relative
        if not actual.is_file() or sha(actual) != sha(expected):
            findings.append(("FROZEN-CONSTRAINT-CHANGED",
                             f"protected fixture authority changed: {relative}"))
    output = workspace / "06_build/coupled"
    try:
        prepared, witness = build_from_source(workspace, output)
        findings.extend(_native_properties(prepared, witness))
        drc, violation_types = _native_drc(witness)
    except Exception as exc:
        return emit("ERROR", [("SOURCE-REGENERATION-FAILED", str(exc))], rc=2)
    conflicts = [kind for kind in violation_types if kind in COPPER_CONFLICTS]
    unexpected = [kind for kind in violation_types
                  if kind not in COPPER_CONFLICTS and kind != "track_width"]
    if conflicts:
        findings.append(("COMBINED-NATIVE-COLLISION",
                         f"combined witness has native conflicts: {conflicts}"))
    if unexpected:
        findings.append(("UNCLASSIFIED-NATIVE-DRC",
                         f"unexpected native violation types: {unexpected}"))
    if drc.get("unconnected_items") and not any(
            code == "REQUIRED-TERMINAL-UNCONNECTED" for code, _ in findings):
        findings.append(("REQUIRED-TERMINAL-UNCONNECTED",
                         "native DRC reports unconnected required copper"))
    gate, receipt_path, receipt = _production_gate(
        repo, workspace, prepared, witness)
    gate_valid = (
        gate.returncode == 0 and isinstance(receipt, dict) and
        receipt.get("schema") == 1 and
        receipt.get("kind") == "coupled-geometry-receipt-v1" and
        receipt.get("status") == "PASS" and
        set(receipt.get("checks") or {}) ==
        {"route_base", "candidate", "realized_policy"} and
        all(row.get("status") == "PASS"
            for row in receipt.get("checks", {}).values())
    )
    if not gate_valid:
        findings.append(("COUPLED-PREFLIGHT-FAIL",
                         f"production coupled gate exited {gate.returncode}"))
    handoff = (workspace / "HANDOFF.md").read_text(errors="replace").lower()
    if any(claim in handoff for claim in
           ("routing stage complete", "board complete", "layout sealed",
            "release ready")):
        findings.append(("HANDOFF-SCOPE-OVERCLAIM",
                         "local neighborhood evidence claims a later lifecycle stage"))
    evidence = {
        "source_regenerated": True,
        "native_violation_types": violation_types,
        "native_unconnected": len(drc.get("unconnected_items") or []),
        "pad_population": {net: len(PAD_LAYOUT[net]) for net in NETS},
        "production_gate_exit": gate.returncode,
        "production_gate_status": receipt.get("status") if receipt else None,
        "production_receipt": str(receipt_path.relative_to(workspace)),
        "production_complete": False,
    }
    if findings:
        return emit("FAIL", findings, evidence)
    return emit("PASS", evidence=evidence)


def apply_control(workspace: Path, name: str):
    source = HERE / "controls" / f"{name}.yaml"
    if not source.is_file():
        raise ValueError(f"unknown control {name}")
    shutil.copy2(source, workspace / "03_src/route_geometry.yaml")


def main(argv):
    if len(argv) < 4:
        print("usage: driver.py MODE REPO WORKSPACE [CONTROL]", file=sys.stderr)
        return 2
    mode, repo, workspace = argv[1], Path(argv[2]).resolve(), Path(argv[3]).resolve()
    if mode == "prepare":
        return prepare(repo, workspace)
    if mode == "grade":
        return grade(repo, workspace)
    if mode == "control" and len(argv) == 5:
        apply_control(workspace, argv[4])
        return emit("PASS", evidence={"control": argv[4]})
    return emit("ERROR", [("MODE", f"unknown mode {mode}")], rc=2)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
