#!/usr/bin/env python3
"""Replay one expanded-board C105 placement hypothesis into a fresh directory."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pcbnew
import yaml

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
ROOT = HERE.parents[4]
BASE = PROJECT / "06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb"
PACKET = HERE.parent / "2026-09-25-ti-expanded-locked-p1-sol"
ALIASES = PROJECT / "02_parts/USB4215-03-A/part.yaml"
CHECKER = ROOT / "skills/kicad-pcb/scripts/p1_corridor_capacity.py"
REBINDER = ROOT / "skills/pcb-design/scripts/integration_candidate.py"
MOUTH = HERE.parent / "2026-09-25-ti-timing-mouth-screen-sol/build_screen.py"
EXPECTED = {
    "board": "fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16",
    "native_floor": "2f7843ada9eb08d19d268f0d6671079a8cf367629b2b3331119088927415b634",
    "p1": "e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92",
    "floor": "8a805d92d4f57c3a0db00a45d1c9aef57958eb0c219d44f9ca89e5531021d8b4",
    "coarse": "9faaed39333c0db45c188003d2ac6bacc69562f259f8332d0d6a79db7d25037f",
    "project": "7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094",
    "rules": "00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a",
    "fp_lib_table": "f7d3e5557b95cf52fb52294c497f6cf2680f0c750acc550b1b9d808973dc8b55",
    "interfaces": "02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8",
    "aliases": "a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e",
    "checker": "c6609198e3daa5fc9718436194945f4cb0f39f4e9095ec991674479f798e7b46",
    "rebinder": "48102e1322cbb3a0cbae297909a35fe6c4adcf7b7a37c4a269a35048eef5e905",
    "mouth_helper": "d6281ffae7273c956aefaf3a394cf1f782aaf6b1f3493449999af52bc254bad6",
}
NEW_POSE = (198.25, 97.05, 180.0)
NECK = [188, 94, 190, 99.84]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pose(fp):
    point = fp.GetPosition()
    return [round(pcbnew.ToMM(point.x), 4), round(pcbnew.ToMM(point.y), 4),
            round(fp.GetOrientationDegrees(), 4)]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def drc(board: Path):
    report = board.with_suffix(".drc.json")
    subprocess.run(["kicad-cli", "pcb", "drc", "--refill-zones", "--format", "json",
                    "-o", str(report), str(board)], check=True, capture_output=True, text=True)
    data = json.loads(report.read_text())
    return {"violations": dict(sorted(Counter(item["type"] for item in data["violations"]).items())),
            "unconnected": len(data["unconnected_items"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir", type=Path, help="new scratch directory; existing paths are refused")
    args = parser.parse_args()
    if args.out_dir.exists():
        raise SystemExit(f"refusing existing output: {args.out_dir}")
    paths = {"board": BASE,
             "native_floor": BASE.parents[1] / "03_src/floorplan.yaml",
             "p1": PACKET / "p1_requirements.yaml",
             "floor": PACKET / "floorplan.yaml",
             "coarse": PACKET / "coarse.json",
             "project": BASE.with_suffix(".kicad_pro"),
             "rules": BASE.with_suffix(".kicad_dru"),
             "fp_lib_table": BASE.parent / "fp-lib-table",
             "interfaces": PACKET / "modular_plan.json",
             "aliases": ALIASES, "checker": CHECKER,
             "rebinder": REBINDER, "mouth_helper": MOUTH}
    actual = {name: sha(path) for name, path in paths.items()}
    if actual != EXPECTED:
        raise SystemExit(f"frozen input drift: {actual}")
    fixed = yaml.safe_load(paths["p1"].read_text())["p1_fixed_refs"]
    if len(fixed) != 33 or "C_XU_VDD_105" in fixed:
        raise SystemExit("P1-fixed denominator drift")
    board = pcbnew.LoadBoard(str(BASE))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    before = {ref: pose(fp) for ref, fp in fps.items()}
    if before["C_XU_VDD_105"] != [196.5, 96.3, 180.0]:
        raise SystemExit("C105 baseline pose drift")
    cap = fps["C_XU_VDD_105"]
    pad = next(p for p in cap.Pads() if p.GetNumber() == "1")
    xu = next(p for p in fps["U_XU"].Pads() if p.GetNumber() == "105")
    def distance():
        a, b = pad.GetPosition(), xu.GetPosition()
        return round(math.hypot(pcbnew.ToMM(a.x-b.x), pcbnew.ToMM(a.y-b.y)), 4)
    old_distance = distance()
    screen = load_module("timing_mouth", MOUTH)
    def envelope(fp):
        c = fp.GetCourtyard(pcbnew.F_CrtYd)
        return screen.bbox(c.BBox() if c.OutlineCount() else fp.GetBoundingBox(False, False))
    def neck():
        obstacles = [(ref, screen.bbox(fp.GetBoundingBox(True, True)))
                     for ref, fp in fps.items() if ref not in {"U_XU", "U_TDM_XLATE"}]
        return screen.mouth_screen(NECK, "horizontal", obstacles)
    old_neck = neck()
    old_env = envelope(cap)
    old_collisions = {ref for ref, fp in fps.items() if ref != "C_XU_VDD_105"
                      and screen.intersects(old_env, envelope(fp))}
    cap.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(NEW_POSE[0]), pcbnew.FromMM(NEW_POSE[1])))
    if pose(cap) != list(NEW_POSE):
        raise SystemExit("candidate native pose drift")
    if any(pose(fps[ref]) != before[ref] for ref in fixed):
        raise SystemExit("P1-fixed pose moved")
    changed = [ref for ref, fp in fps.items() if pose(fp) != before[ref]]
    if changed != ["C_XU_VDD_105"]:
        raise SystemExit(f"unexpected placement delta: {changed}")
    new_env = envelope(cap)
    new_collisions = {ref for ref, fp in fps.items() if ref != "C_XU_VDD_105"
                      and screen.intersects(new_env, envelope(fp))}
    if new_collisions - old_collisions:
        raise SystemExit(f"new courtyard intersections: {new_collisions-old_collisions}")
    core = yaml.safe_load(paths["floor"].read_text())["placement"]["regions"]["xmos_core"]
    if (new_env[0] < core[0] or new_env[1] < core[1]
            or new_env[2] > core[2] or new_env[3] > core[3]):
        raise SystemExit(f"C105 courtyard leaves xmos_core: {new_env}")
    new_neck = neck()
    if new_neck["connected_width_mm"] <= old_neck["connected_width_mm"]:
        raise SystemExit("alternate neck did not improve")

    args.out_dir.mkdir(parents=True)
    out = args.out_dir
    native = out / "04_kicad"
    native.mkdir()
    (out / "03_src").mkdir()
    os.symlink(BASE.parents[1] / "03_src/lib", out / "03_src/lib", target_is_directory=True)
    shutil.copyfile(BASE.parent / "fp-lib-table", native / "fp-lib-table")
    candidate = native / "candidate.kicad_pcb"
    pcbnew.SaveBoard(str(candidate), board)
    shutil.copyfile(BASE, native / "baseline.kicad_pcb")
    for name in ("baseline", "candidate"):
        for ext in ("kicad_pro", "kicad_dru"):
            shutil.copyfile(BASE.with_suffix("."+ext), native / (name+"."+ext))
    for name in ("p1_requirements.yaml", "modular_plan.json"):
        shutil.copyfile(PACKET / name, out / name)
    floor = yaml.safe_load(paths["floor"].read_text())
    floor["placement"]["post_anchors"]["C_XU_VDD_105"] = list(NEW_POSE)
    floor_path = out / "floorplan.yaml"
    floor_path.write_text(yaml.safe_dump(floor, sort_keys=False))
    coarse = json.loads(paths["coarse"].read_text())
    coarse["source_sha256"] = sha(out / "p1_requirements.yaml")
    coarse["floorplan_sha256"] = sha(floor_path)
    sys.path.insert(0, str(REBINDER.parent))
    from integration_candidate import propose_native_witnesses
    proposal = propose_native_witnesses(candidate, coarse)
    contract = out / "coarse.json"
    contract.write_text(json.dumps(proposal["proposed_contract"], indent=2)+"\n")
    checker = load_module("timing_p1_checker", CHECKER)
    result = checker.evaluate_coarse(
        candidate, contract, sha(contract), source_path=out/"p1_requirements.yaml",
        interface_path=out/"modular_plan.json", alias_path=ALIASES,
        floorplan_path=floor_path, expected_source_sha256=sha(out/"p1_requirements.yaml"),
        expected_interface_sha256=sha(out/"modular_plan.json"),
        expected_alias_sha256=sha(ALIASES), expected_floorplan_sha256=sha(floor_path),
        diagnose_all=True)
    (out/"checker_result.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    timing = next(a for a in result["allocations"] if a["id"] == "adc_timing_xmos_bundle")
    if (result["status"] != "INCOMPLETE" or result["errors"] or result["diagnostics"]
            or result["p1_accepted"] or result["routing_realized"]
            or len(timing["reservations"]) != 14
            or sum(len(r.get("p2_obligations", [])) for r in timing["reservations"]) != 54):
        raise SystemExit("no-credit 14-net/54-duty checker shape drift")
    before_drc, after_drc = drc(native/"baseline.kicad_pcb"), drc(candidate)
    if after_drc != before_drc:
        raise SystemExit(f"native DRC delta: {before_drc} -> {after_drc}")
    receipt = {"kind": "expanded-tdm-c105-p2-placement-probe", "status": "INCOMPLETE",
               "inputs": actual, "candidate_board_sha256": sha(candidate),
               "source_floorplan_sha256": sha(floor_path),
               "move": {"ref": "C_XU_VDD_105", "from": before["C_XU_VDD_105"],
                        "to": pose(cap), "owner_pad_distance_mm": [old_distance, distance()]},
               "fixed_refs_unchanged": 33, "timing_nets": 14, "timing_p2_duties": 54,
               "neck_bbox_mm": NECK,
               "neck_connected_width_mm": [old_neck["connected_width_mm"], new_neck["connected_width_mm"]],
               "rough_slots": [old_neck["raw_slots"], new_neck["raw_slots"]],
               "new_courtyard_intersections": [], "drc": {"baseline": before_drc, "candidate": after_drc},
               "p1_accepted": False, "p2_accepted": False, "routing_realized": False,
               "proof_debt": ["canonical 03_src C105 anchor is (196.5,97.1,0), unlike the frozen private board; generation and parity required before adoption",
                              "no source-generated production board or P2 placement review",
                              "rough slots do not prove four exact pad entrances or continuous path",
                              "filled In1.Cu return along a connected route unproved",
                              "no timing, SI, XU local-power return, or final silk proof"]}
    (out/"receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"scratch": str(out), "candidate_sha256": sha(candidate),
                      "neck_connected_width_mm": receipt["neck_connected_width_mm"],
                      "timing_nets": 14, "timing_p2_duties": 54, "status": "INCOMPLETE"}, sort_keys=True))


if __name__ == "__main__":
    main()
