#!/usr/bin/env python3
"""Read-only native object and hash audit for the single D15 private build."""
import hashlib
import json
from pathlib import Path

import pcbnew as pcb

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
BASE = PROJECT / "06_build/prototype_board_diagnostic"
OLD = BASE / "current-ti-mounting-expanded-locked-20260925"
NEW = BASE / "current-ti-4l-3313a-preflight-20260925"
MANIFEST = json.loads((PROJECT / "01_docs/research/2026-09-25-d15-preflight-sol/preflight_manifest.json").read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox(item):
    b = item.GetBoundingBox()
    return (b.GetX(), b.GetY(), b.GetRight(), b.GetBottom())


def inventory(path):
    board = pcb.LoadBoard(str(path))
    fps = {}
    for fp in board.GetFootprints():
        pads = sorted((p.GetNumber(), p.GetNetname(), tuple(p.GetPosition()), tuple(p.GetSize()),
                       p.GetShape(), p.GetLayerSet().FmtBin(), bbox(p)) for p in fp.Pads())
        fps[fp.GetReference()] = (tuple(fp.GetPosition()), fp.GetOrientationDegrees(),
                                  fp.GetLayerName(), fp.GetFPIDAsString(), pads)
    tracks = sorted((type(t).__name__, t.GetNetname(), t.GetLayerName(),
                     tuple(t.GetPosition()), t.GetWidth(pcb.F_Cu),
                     t.GetDrillValue() if isinstance(t, pcb.PCB_VIA) else 0) for t in board.GetTracks())
    zones = {}
    for z in board.Zones():
        key = z.GetZoneName() or "GND"
        zones[key] = (z.GetNetname(), z.GetLayerName(), bool(z.GetIsRuleArea()), bbox(z), bool(z.IsFilled()))
    edges = sorted((type(d).__name__, d.GetLayerName(), bbox(d)) for d in board.GetDrawings()
                   if d.GetLayerName() == "Edge.Cuts")
    return {"footprints": fps, "tracks": tracks, "zones": zones, "edges": edges}


a = inventory(OLD / "04_kicad/crow_carrier.kicad_pcb")
b = inventory(NEW / "04_kicad/crow_carrier.kicad_pcb")
pose_delta = sorted(k for k in a["footprints"] if a["footprints"].get(k) != b["footprints"].get(k))
old_zones = {k: v for k, v in b["zones"].items() if k != "usb_pair_xu_launch"}
launch = b["zones"].get("usb_pair_xu_launch")
expected_bbox = tuple(round(x * 1e6) for x in MANIFEST["allowed_area_bbox_mm"])
findings = []
if a["footprints"].keys() != b["footprints"].keys() or pose_delta:
    findings.append("footprint/pad geometry or identity drift")
if a["tracks"] != b["tracks"]:
    findings.append("saved tracks/vias drift")
if a["edges"] != b["edges"]:
    findings.append("outline edge geometry drift")
if a["zones"] != old_zones:
    findings.append("existing zone or rule-area drift")
if launch != ("", "F.Cu", True, expected_bbox, False):
    findings.append(f"launch area differs: {launch}")
if len(a["footprints"]) != 575 or len([k for k in a["footprints"] if not k.startswith("H")]) != 569:
    findings.append("baseline footprint denominator")
if len(b["tracks"]) != 14 or any(t[0] != "PCB_VIA" or t[1] != "GND" for t in b["tracks"]):
    findings.append("saved copper class")
physical_pads = sum(len(fp[-1]) for ref, fp in b["footprints"].items() if not ref.startswith("H"))
if physical_pads != sum(len(fp[-1]) for ref, fp in a["footprints"].items() if not ref.startswith("H")):
    findings.append("native non-hole pad denominator changed")
if len([z for z in b["zones"].values() if z[2]]) != 9 or len([z for z in b["zones"].values() if not z[2]]) != 1:
    findings.append("zone/area denominator")
if any(z[-1] for z in b["zones"].values()):
    findings.append("saved zone fill")
files = {}
for rel in ("03_src/floorplan.yaml", "03_src/rules/nets.yaml", "03_src/rules/rf.yaml",
            "03_src/rules/route_fab_overrides.txt", "03_tscircuit/build/circuit.json",
            "06_build/netlists/crow_carrier.net", "04_kicad/crow_carrier.kicad_pcb",
            "04_kicad/crow_carrier.kicad_pro", "04_kicad/crow_carrier.kicad_dru",
            "04_kicad/fp-lib-table"):
    files[rel] = {"reference": sha(OLD / rel), "candidate": sha(NEW / rel)}
for rel, expected in MANIFEST["prepared_files_sha256"].items():
    if rel.startswith("04_kicad/"):
        continue
    if sha(NEW / rel) != expected:
        findings.append("prepared source drift " + rel)
result = {"status": "FAILED_RESEARCH", "object_gate_findings": findings,
          "object_gate_pass": not findings, "footprint_or_pad_delta_refs": pose_delta,
          "footprints_total": len(b["footprints"]), "electrical_footprints": 569,
          "native_non_hole_pads": physical_pads, "saved_tracks": len(b["tracks"]),
          "saved_zone_count": len(b["zones"]), "saved_zone_fills": 0,
          "allowed_new_rule_area": "usb_pair_xu_launch", "file_sha256": files,
          "p1_credit": False, "route_credit": False, "fab_credit": False,
          "release_credit": False, "order_credit": False}
print(json.dumps(result, indent=2, sort_keys=True))
if findings:
    raise SystemExit(1)
