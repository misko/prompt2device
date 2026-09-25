#!/usr/bin/env python3
"""Final bounded Crow oscillator placement/route experiment; never promotes source."""
from __future__ import annotations

import argparse
import collections
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pcbnew

from run_xtal_escape import (BOARD, EXPECTED_BOARD_SHA256, PINNED, ROOT,
                             RULE_GENERATOR, copy_input, footprint_poses,
                             pad_positions, point, sha)


MOVES = {
    "Y_XU": (216.6, 112.5, 0),
    "R_XTAL_FB": (216.6, 115.4, 180),
    "C_XTAL_OUT": (215.8, 117.0, 0),
    "R_XTAL_DRIVE": (218.0, 117.0, 180),
    "C_XTAL_IN": (218.0, 118.6, 0),
}
WIDTH_MM = 0.20
ROUTES = {
    "XTAL_IN": [
        [(216.1625, 105.8), (217.2, 105.8), (217.2, 104.59),
         (218.8, 104.59), (218.8, 107.1), (218.8, 115.4), (217.11, 115.4)],
        [(218.8, 115.4), (218.8, 117.0), (218.51, 117.0)],
    ],
    "XTAL_OUT": [
        [(216.1625, 106.2), (217.2, 106.2), (217.2, 110.2),
         (217.7, 110.7), (217.7, 111.65), (216.6, 111.65),
         (216.6, 114.89), (216.09, 115.4), (216.09, 116.2),
         (215.32, 116.97), (215.32, 117.0)],
    ],
    "XTAL_IN_R": [
        [(215.5, 113.35), (214.6, 113.35), (214.6, 118.0),
         (217.49, 118.0), (217.49, 117.0)],
        [(217.49, 118.0), (217.52, 118.6)],
    ],
}
EXPECTED_PADS = {
    "U_XU.34": (216.1625, 105.8, "XTAL_IN"),
    "U_XU.33": (216.1625, 106.2, "XTAL_OUT"),
    "R_XTAL_FB.1": (217.11, 115.4, "XTAL_IN"),
    "R_XTAL_FB.2": (216.09, 115.4, "XTAL_OUT"),
    "R_XTAL_DRIVE.1": (218.51, 117.0, "XTAL_IN"),
    "R_XTAL_DRIVE.2": (217.49, 117.0, "XTAL_IN_R"),
    "Y_XU.1": (215.5, 113.35, "XTAL_IN_R"),
    "Y_XU.3": (217.7, 111.65, "XTAL_OUT"),
    "C_XTAL_IN.1": (217.52, 118.6, "XTAL_IN_R"),
    "C_XTAL_OUT.1": (215.32, 117.0, "XTAL_OUT"),
}
OSCILLATOR_NETS = ("XTAL_IN", "XTAL_OUT", "XTAL_IN_R")


def mm_box(box) -> tuple[float, float, float, float]:
    return tuple(v / 1_000_000 for v in
                 (box.GetX(), box.GetY(), box.GetRight(), box.GetBottom()))


def courtyard_box(fp) -> tuple[float, float, float, float]:
    return mm_box(fp.GetCourtyard(pcbnew.F_CrtYd).BBox())


def overlap(a, b) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def draw_compact(prepared: Path, candidate: Path) -> dict:
    board = pcbnew.LoadBoard(str(prepared))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    original_poses = footprint_poses(board)
    original_pads = pad_positions(board)
    if len(fps) != 569 or len(fps) != len(original_poses):
        raise RuntimeError("pinned footprint denominator drift")
    initial_tracks = len(list(board.GetTracks()))
    for ref, (x, y, angle) in MOVES.items():
        fp = fps[ref]
        fp.SetOrientationDegrees(angle)
        fp.SetPosition(point((x, y)))
    changed = {ref for ref, pose in footprint_poses(board).items()
               if pose != original_poses[ref]}
    if changed != set(MOVES):
        raise RuntimeError(f"unexpected footprint pose changes: {sorted(changed)}")
    pads = pad_positions(board)
    if any((ref not in MOVES and pads[key] != prior)
           for key, prior in original_pads.items() for ref in [key.rsplit('.', 1)[0]]):
        raise RuntimeError("fixed/unmoved pad identity changed")
    for refpad, (x, y, net) in EXPECTED_PADS.items():
        target = point((x, y))
        if pads.get(refpad) != (target.x, target.y, net):
            raise RuntimeError(f"oscillator ref/pad/net pose drift: {refpad}: {pads.get(refpad)}")
    boxes = {ref: courtyard_box(fp) for ref, fp in fps.items()}
    overlaps = sorted((ref, other) for ref in MOVES for other in fps
                      if other != ref and (other not in MOVES or ref < other)
                      and overlap(boxes[ref], boxes[other]))
    if overlaps:
        raise RuntimeError(f"compact oscillator courtyard collisions: {overlaps}")
    for net, chains in ROUTES.items():
        native_net = board.FindNet(net)
        if native_net is None:
            raise RuntimeError(f"missing native net {net}")
        for vertices in chains:
            for a, b in zip(vertices, vertices[1:]):
                segment = pcbnew.PCB_TRACK(board)
                segment.SetStart(point(a))
                segment.SetEnd(point(b))
                segment.SetLayer(pcbnew.F_Cu)
                segment.SetWidth(round(WIDTH_MM * 1_000_000))
                segment.SetNet(native_net)
                board.Add(segment)
    pcbnew.SaveBoard(str(candidate), board)
    saved = pcbnew.LoadBoard(str(candidate))
    if footprint_poses(saved) != footprint_poses(board) or pad_positions(saved) != pads:
        raise RuntimeError("saved candidate pose/pad identity drift")
    added = sum(len(vertices) - 1 for chains in ROUTES.values() for vertices in chains)
    if len(list(saved.GetTracks())) != initial_tracks + added:
        raise RuntimeError("saved candidate copper inventory drift")
    zones = [(z.GetNetname(), [saved.GetLayerName(layer)
                              for layer in z.GetLayerSet().Seq()])
             for z in saved.Zones()]
    return {"moved_refs": MOVES, "changed_pose_count": len(changed),
            "fixed_and_other_pose_count": len(fps) - len(changed),
            "courtyard_overlaps": overlaps, "added_FCu_segments": added,
            "route_chains": ROUTES, "width_mm": WIDTH_MM,
            "native_zone_inventory": zones,
            "in1_GND_zone_present": any(net == "GND" and "In1.Cu" in layers
                                        for net, layers in zones)}


def native_drc(board: Path, report: Path) -> dict:
    command = ["kicad-cli", "pcb", "drc", "--severity-all", "--refill-zones",
               "--save-board", "--schematic-parity", "--format", "json",
               "-o", str(report), str(board)]
    try:
        run = subprocess.run(command, capture_output=True, text=True, timeout=360, check=False)
    except subprocess.TimeoutExpired as exc:
        return {"status": "INCOMPLETE", "reason": f"native DRC timeout: {exc}", "command": command}
    if not report.is_file():
        return {"status": "INCOMPLETE", "exit": run.returncode,
                "reason": "native DRC wrote no report", "stderr_tail": run.stderr[-1000:],
                "command": command}
    try:
        data = json.loads(report.read_text(encoding="utf-8-sig"))
        counts = {key: len(data[key]) for key in
                  ("violations", "unconnected_items", "schematic_parity")}
        types = dict(sorted(collections.Counter(row.get("type", "UNKNOWN")
                                                for row in data["violations"]).items()))
        oscillator_opens = {net: 0 for net in OSCILLATOR_NETS}
        oscillator_related = 0
        for row in data["unconnected_items"]:
            descriptions = [item.get("description", "") for item in row.get("items", [])]
            row_nets = {match for description in descriptions
                        for match in re.findall(r"\[([^]]+)\]", description)}
            if any("XTAL" in description or "Y_XU" in description
                   for description in descriptions):
                oscillator_related += 1
            for net in OSCILLATOR_NETS:
                if net in row_nets:
                    oscillator_opens[net] += 1
        return {"status": "MEASURED" if run.returncode in (0, 1) else "INCOMPLETE",
                "exit": run.returncode, "report_sha256": sha(report),
                "saved_board_sha256": sha(board), "counts": counts,
                "violation_types": types, "oscillator_unconnected_items": oscillator_opens,
                "oscillator_related_unconnected_items": oscillator_related,
                "stderr_tail": run.stderr[-1000:], "command": command}
    except (ValueError, KeyError, TypeError) as exc:
        return {"status": "INCOMPLETE", "exit": run.returncode,
                "reason": f"invalid native DRC JSON: {exc}",
                "report_sha256": sha(report), "command": command}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"experiment directory already exists: {output}")
    if sha(BOARD) != EXPECTED_BOARD_SHA256:
        raise SystemExit("pinned QSPI-gap board SHA-256 drift")
    output.mkdir(parents=True)
    inputs = ["04_kicad/crow_carrier.kicad_pcb", "04_kicad/crow_carrier.kicad_pro",
              "04_kicad/crow_carrier.kicad_sch", "03_src/rules/nets.yaml",
              "03_src/rules/assembly.yaml", "03_src/floorplan.yaml",
              "02_parts/TMUX4827YBHR/part.yaml",
              "02_parts/TMUX4827YBHR/qualification/coupon.kicad_pcb",
              "03_src/lib/crow_usb_analog.pretty/TI_YBH0009_C02_TMUX4827.kicad_mod"]
    hashes = {relative: sha(copy_input(relative, output)) for relative in inputs}
    prepared = output / "04_kicad/crow_carrier.kicad_pcb"
    generated = subprocess.run([sys.executable, str(RULE_GENERATOR), str(output)],
                               capture_output=True, text=True, timeout=120, check=False)
    (output / "rule_generation.log").write_text(generated.stdout + generated.stderr)
    if generated.returncode != 0:
        raise RuntimeError(f"prepared rule generation failed: {generated.stderr[-1000:]}")
    pro, dru = prepared.with_suffix(".kicad_pro"), prepared.with_suffix(".kicad_dru")
    if not pro.is_file() or not dru.is_file():
        raise RuntimeError("prepared PRO/DRU incomplete")
    candidate = output / "04_kicad/xtal_compact_candidate.kicad_pcb"
    geometry = draw_compact(prepared, candidate)
    for suffix in (".kicad_pro", ".kicad_dru", ".kicad_sch"):
        shutil.copy2(prepared.with_suffix(suffix), candidate.with_suffix(suffix))
    baseline = native_drc(prepared, output / "baseline_drc.json")
    subject = native_drc(candidate, output / "candidate_drc.json")
    result = {
        "schema": 1, "kind": "crow-xtal-compact-native-experiment",
        "status": "DIAGNOSTIC_ONLY", "input_sha256": hashes,
        "rule_generation_command": [sys.executable, str(RULE_GENERATOR), str(output)],
        "prepared_pro_sha256": sha(pro), "prepared_dru_sha256": sha(dru),
        "candidate_pro_sha256": sha(candidate.with_suffix(".kicad_pro")),
        "candidate_dru_sha256": sha(candidate.with_suffix(".kicad_dru")),
        "geometry": geometry, "baseline_drc": baseline, "candidate_drc": subject,
        "claim_limit": "Provisional compact P2 experiment; P1 cell/redrawn ownership, crystal loading and loop, actual return, and engineering acceptance remain open.",
    }
    (output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "geometry": geometry,
                      "baseline_drc": baseline, "candidate_drc": subject}, indent=2))
    return 0 if baseline["status"] == subject["status"] == "MEASURED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
