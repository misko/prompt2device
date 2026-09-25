#!/usr/bin/env python3
"""One isolated native XU crystal pad-escape experiment on the pinned QSPI board.

This recipe draws only the two screened F.Cu doglegs. It does not promote P1/P2,
move oscillator parts, complete XTAL nets, or claim oscillator performance.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[5]
PINNED = Path("/tmp/crow-xu-qspi-gap-sol/project")
BOARD = PINNED / "04_kicad/crow_carrier.kicad_pcb"
EXPECTED_BOARD_SHA256 = "fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27"
RULE_GENERATOR = ROOT / "skills/kicad-pcb/scripts/generate_rules_generic.py"
ROUTES = {
    "XTAL_IN": [(216.1625, 105.8), (217.2, 105.8), (217.2, 104.59),
                (218.8, 104.59), (218.8, 107.1)],
    "XTAL_OUT": [(216.1625, 106.2), (217.2, 106.2), (217.2, 107.1)],
}
WIDTH_MM = 0.20  # pinned nets.yaml Default track width; not a rule relaxation


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_input(relative: str, output: Path) -> Path:
    source = PINNED / relative
    target = output / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def point(xy: tuple[float, float]) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(round(xy[0] * 1_000_000), round(xy[1] * 1_000_000))


def pad_positions(board: pcbnew.BOARD) -> dict[str, tuple[int, int, str]]:
    return {f"{fp.GetReference()}.{pad.GetNumber()}":
            (pad.GetPosition().x, pad.GetPosition().y, pad.GetNetname())
            for fp in board.GetFootprints() for pad in fp.Pads()}


def footprint_poses(board: pcbnew.BOARD) -> dict[str, tuple[int, int, float]]:
    return {fp.GetReference(): (fp.GetPosition().x, fp.GetPosition().y,
                                fp.GetOrientationDegrees())
            for fp in board.GetFootprints()}


def draw_escape(prepared: Path, candidate: Path) -> dict[str, object]:
    board = pcbnew.LoadBoard(str(prepared))
    before_pads = pad_positions(board)
    before_poses = footprint_poses(board)
    if len(before_poses) != 569 or len(before_poses) != len(list(board.GetFootprints())):
        raise RuntimeError("pinned footprint denominator drift")
    for net, number in (("XTAL_IN", "34"), ("XTAL_OUT", "33")):
        expected = point(ROUTES[net][0])
        if before_pads[f"U_XU.{number}"] != (expected.x, expected.y, net):
            raise RuntimeError(f"U_XU.{number} source pad/net drift")
    initial_tracks = len(list(board.GetTracks()))
    for net, vertices in ROUTES.items():
        netinfo = board.FindNet(net)
        if netinfo is None:
            raise RuntimeError(f"missing native net {net}")
        for a, b in zip(vertices, vertices[1:]):
            segment = pcbnew.PCB_TRACK(board)
            segment.SetStart(point(a))
            segment.SetEnd(point(b))
            segment.SetLayer(pcbnew.F_Cu)
            segment.SetWidth(round(WIDTH_MM * 1_000_000))
            segment.SetNet(netinfo)
            board.Add(segment)
    pcbnew.SaveBoard(str(candidate), board)
    saved = pcbnew.LoadBoard(str(candidate))
    if footprint_poses(saved) != before_poses or pad_positions(saved) != before_pads:
        raise RuntimeError("candidate altered footprint pose or pad/net identity")
    if len(list(saved.GetTracks())) != initial_tracks + sum(len(v) - 1 for v in ROUTES.values()):
        raise RuntimeError("candidate track inventory differs from the recipe")
    return {"footprints_unchanged": len(before_poses), "initial_tracks": initial_tracks,
            "added_tracks": sum(len(v) - 1 for v in ROUTES.values()),
            "routes": ROUTES, "width_mm": WIDTH_MM, "layer": "F.Cu"}


def drc(prepared: Path, output: Path) -> dict[str, object]:
    command = ["kicad-cli", "pcb", "drc", "--severity-all", "--refill-zones",
               "--schematic-parity", "--format", "json", "-o", str(output), str(prepared)]
    try:
        run = subprocess.run(command, capture_output=True, text=True, timeout=360, check=False)
    except subprocess.TimeoutExpired as exc:
        return {"status": "INCOMPLETE", "reason": f"native DRC timeout: {exc}", "command": command}
    if not output.is_file():
        return {"status": "INCOMPLETE", "reason": "native DRC wrote no JSON", "exit": run.returncode,
                "stderr_tail": run.stderr[-1000:], "command": command}
    try:
        payload = json.loads(output.read_text(encoding="utf-8-sig"))
        counts = {key: len(payload[key]) for key in
                  ("violations", "unconnected_items", "schematic_parity")}
        types = dict(sorted(collections.Counter(row.get("type", "UNKNOWN")
                                                for row in payload["violations"]).items()))
        xtal_open = [row for row in payload["unconnected_items"]
                     if "XTAL_IN" in json.dumps(row) or "XTAL_OUT" in json.dumps(row)]
        return {"status": "MEASURED" if run.returncode in (0, 1) else "INCOMPLETE",
                "exit": run.returncode, "report_sha256": sha(output), "counts": counts,
                "violation_types": types, "xtal_unconnected_items": len(xtal_open),
                "stderr_tail": run.stderr[-1000:], "command": command}
    except (ValueError, KeyError, TypeError) as exc:
        return {"status": "INCOMPLETE", "reason": f"invalid native DRC JSON: {exc}",
                "exit": run.returncode, "report_sha256": sha(output), "command": command}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="Previously absent, isolated experiment directory")
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
    pro = prepared.with_suffix(".kicad_pro")
    dru = prepared.with_suffix(".kicad_dru")
    if not pro.is_file() or not dru.is_file():
        raise RuntimeError("prepared PRO/DRU incomplete")
    candidate = output / "04_kicad/xtal_escape_candidate.kicad_pcb"
    geometry = draw_escape(prepared, candidate)
    for suffix in (".kicad_pro", ".kicad_dru", ".kicad_sch"):
        shutil.copy2(prepared.with_suffix(suffix), candidate.with_suffix(suffix))
    baseline_drc = drc(prepared, output / "baseline_drc.json")
    candidate_drc = drc(candidate, output / "candidate_drc.json")
    result = {
        "kind": "crow-xtal-native-escape-experiment", "schema": 1,
        "status": "DIAGNOSTIC_ONLY", "source_board_sha256": hashes["04_kicad/crow_carrier.kicad_pcb"],
        "input_sha256": hashes, "prepared_pro_sha256": sha(pro), "prepared_dru_sha256": sha(dru),
        "candidate_pro_sha256": sha(candidate.with_suffix(".kicad_pro")),
        "candidate_dru_sha256": sha(candidate.with_suffix(".kicad_dru")),
        "prepared_board_sha256": sha(prepared), "candidate_board_sha256": sha(candidate),
        "rule_generation_command": [sys.executable, str(RULE_GENERATOR), str(output)],
        "geometry": geometry, "baseline_drc": baseline_drc, "candidate_drc": candidate_drc,
        "claim_limit": "Local F.Cu pad escapes only; crystal endpoints, loading, loop, return, and P1/P2 acceptance remain open.",
    }
    (output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "geometry": geometry,
                      "baseline_drc": baseline_drc, "candidate_drc": candidate_drc}, indent=2))
    return 0 if baseline_drc["status"] == candidate_drc["status"] == "MEASURED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
