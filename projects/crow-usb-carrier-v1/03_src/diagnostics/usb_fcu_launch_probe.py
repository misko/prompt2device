#!/usr/bin/python3
"""Replay an isolated, deliberately incomplete XU316 USB F.Cu launch probe.

This builds a scratch project with its own board, schematic, netlist, footprint
libraries, .kicad_pro and .kicad_dru. It never writes a canonical board or
imports a route. The two open copper ends are diagnostic, not P3 route proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zlib

import pcbnew


PROJECT = Path(__file__).resolve().parents[2]
REPO = next(p for p in PROJECT.parents if (p / "skills/kicad-pcb/scripts/generate_board_generic.py").is_file())
SCRIPTS = REPO / "skills/kicad-pcb/scripts"
ROUTE = (
    ("USB_DN", 216.900, 95.800, 217.325, 95.800, 0.150),
    ("USB_DN", 217.325, 95.800, 217.425, 95.800, 0.250),
    ("USB_DN", 217.425, 95.800, 230.000, 95.800, 0.410),
    ("USB_DP", 216.900, 95.400, 217.125, 95.400, 0.150),
    ("USB_DP", 217.125, 95.400, 217.125, 95.240, 0.150),
    ("USB_DP", 217.125, 95.240, 217.325, 95.240, 0.150),
    ("USB_DP", 217.325, 95.240, 217.425, 95.240, 0.250),
    ("USB_DP", 217.425, 95.240, 230.000, 95.240, 0.410),
)
SAMPLE_POINTS = (
    (217.0, 95.24), (217.5, 95.24), (218.0, 95.24), (222.0, 95.24),
    (230.0, 95.24), (217.0, 95.8), (222.0, 95.8), (230.0, 95.8),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cwd: Path, *argv: object) -> None:
    command = [str(a) for a in argv]
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def replace_once(path: Path, before: str, after: str) -> None:
    content = path.read_text()
    if content.count(before) != 1:
        raise ValueError(f"expected one insertion point in {path}: {before!r}")
    path.write_text(content.replace(before, after))


def build(root: Path, board: Path) -> None:
    run(root, "/usr/bin/python3", SCRIPTS / "generate_board_generic.py",
        root / "03_src/floorplan.yaml", "-o", board)
    run(root, "/usr/bin/python3", SCRIPTS / "generate_rules_generic.py", root)


def drc(root: Path, board: Path, output: Path) -> dict:
    run(root, "kicad-cli", "pcb", "drc", "--severity-all",
        "--all-track-errors", "--refill-zones", "--save-board",
        "--schematic-parity", "--format", "json", "-o", output, board)
    return json.loads(output.read_text())


def categories(report: dict) -> dict[str, int]:
    return dict(sorted(Counter(v["type"] for v in report["violations"]).items()))


def pad_check(board: pcbnew.BOARD) -> None:
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    if len(fps) != 569 or len(list(board.GetTracks())) != 14:
        raise ValueError("unexpected source footprint or thermal-via census")
    xu = fps["U_XU"]
    expected = {"59": ("USB_DN", 95.8), "60": ("USB_DP", 95.4)}
    for pad in xu.Pads():
        number = pad.GetNumber()
        if number not in expected:
            continue
        net, y = expected.pop(number)
        box = pad.GetBoundingBox()
        if pad.GetNetname() != net or abs(pcbnew.ToMM(pad.GetPosition().y) - y) > 0.001 \
                or abs(pcbnew.ToMM(box.GetRight()) - 216.9) > 0.001:
            raise ValueError(f"unexpected U_XU.{number} launch pad")
    if expected:
        raise ValueError(f"missing launch pads: {expected}")
    cap = fps["C_XU_VDD_54"].GetPosition()
    if (round(pcbnew.ToMM(cap.x), 3), round(pcbnew.ToMM(cap.y), 3)) != (219.14, 96.94):
        raise ValueError("C_XU_VDD_54 source anchor differs from probe")


def add_tracks(board: pcbnew.BOARD) -> None:
    nets = {n.GetNetname(): n for n in board.GetNetInfo().NetsByNetcode().values()}
    pcbnew.KIID.SeedGenerator(zlib.crc32(b"crow-usb-fcu-launch-diagnostic-v1"))
    for net, x1, y1, x2, y2, width in ROUTE:
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I_MM(x1, y1))
        track.SetEnd(pcbnew.VECTOR2I_MM(x2, y2))
        track.SetWidth(pcbnew.FromMM(width))
        track.SetLayer(pcbnew.F_Cu)
        track.SetNet(nets[net])
        board.Add(track)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new empty output directory outside the project")
    args = parser.parse_args()
    out = args.output.resolve()
    if out == PROJECT or PROJECT in out.parents or out.exists():
        parser.error("output must be a new directory outside the canonical project")
    root = out / "project"
    (root / "04_kicad").mkdir(parents=True)
    (root / "06_build/netlists").mkdir(parents=True)
    for subdir in ("02_parts", "03_src"):
        shutil.copytree(PROJECT / subdir, root / subdir)
    for relative in ("04_kicad/crow_carrier.kicad_sch",
                     "06_build/netlists/crow_carrier.net"):
        shutil.copy2(PROJECT / relative, root / relative)
    board = root / "04_kicad/crow_carrier.kicad_pcb"
    build(root, board)
    baseline_pre_drc = sha(board)
    baseline = drc(root, board, out / "baseline_drc.json")
    baseline_board = sha(board)
    pad_check(pcbnew.LoadBoard(str(board)))

    floorplan = root / "03_src/floorplan.yaml"
    nets = root / "03_src/rules/nets.yaml"
    replace_once(floorplan, "design_rules:\n", """keepouts:
  - name: usb_xu_launch_neck
    layers: [F.Cu]
    deny: []
    rect: [216.85, 94.95, 217.44, 96.10]
design_rules:
""")
    replace_once(nets, "length_match:\n", """scoped_floors:
  - zone: usb_xu_launch_neck
    nets: [USB_DP, USB_DN]
    min_width: 0.15mm
    why: "Diagnostic XU316 pad pitch neck; SI, decoupling and full route unqualified."
length_match:
""")
    build(root, board)
    candidate = pcbnew.LoadBoard(str(board))
    pad_check(candidate)
    add_tracks(candidate)
    pcbnew.SaveBoard(str(board), candidate)
    run(root, "/usr/bin/python3", SCRIPTS / "generate_rules_generic.py", root)
    candidate_pre_drc = sha(board)
    result = drc(root, board, out / "candidate_drc.json")
    saved = pcbnew.LoadBoard(str(board))
    zone = next(z for z in saved.Zones() if z.GetNetname() == "GND" and not z.GetIsRuleArea())
    samples = [{"x": x, "y": y,
                "in1_gnd_filled": bool(zone.HitTestFilledArea(
                    pcbnew.In1_Cu, pcbnew.VECTOR2I_MM(x, y)))}
               for x, y in SAMPLE_POINTS]
    usb_findings = [v for v in result["violations"] if any(
        "[USB_DP]" in i.get("description", "") or "[USB_DN]" in i.get("description", "")
        for i in v.get("items", []))]
    if sorted(v["type"] for v in usb_findings) != ["track_dangling", "track_dangling"]:
        raise ValueError(f"unexpected USB native DRC findings: {usb_findings}")
    lengths = {net: round(sum(abs(x2-x1) + abs(y2-y1) for n,x1,y1,x2,y2,_ in ROUTE if n == net), 3)
               for net in ("USB_DP", "USB_DN")}
    summary = {
        "status": "DIAGNOSTIC_ONLY_INCOMPLETE",
        "source_floorplan_sha256": sha(PROJECT / "03_src/floorplan.yaml"),
        "source_nets_sha256": sha(PROJECT / "03_src/rules/nets.yaml"),
        "source_netlist_sha256": sha(PROJECT / "06_build/netlists/crow_carrier.net"),
        "source_schematic_sha256": sha(PROJECT / "04_kicad/crow_carrier.kicad_sch"),
        "baseline_pre_drc_board_sha256": baseline_pre_drc,
        "baseline_saved_board_sha256": baseline_board,
        "candidate_pre_drc_board_sha256": candidate_pre_drc,
        "candidate_saved_board_sha256": sha(board),
        "candidate_pro_sha256": sha(board.with_suffix(".kicad_pro")),
        "candidate_dru_sha256": sha(board.with_suffix(".kicad_dru")),
        "candidate_fp_lib_table_sha256": sha(board.parent / "fp-lib-table"),
        "baseline_drc_json_sha256": sha(out / "baseline_drc.json"),
        "candidate_drc_json_sha256": sha(out / "candidate_drc.json"),
        "baseline_violations": categories(baseline),
        "candidate_violations": categories(result),
        "baseline_unconnected": len(baseline["unconnected_items"]),
        "candidate_unconnected": len(result["unconnected_items"]),
        "baseline_schematic_parity": len(baseline["schematic_parity"]),
        "candidate_schematic_parity": len(result["schematic_parity"]),
        "usb_findings": usb_findings,
        "track_lengths_mm": lengths,
        "skew_mm": round(abs(lengths["USB_DP"] - lengths["USB_DN"]), 3),
        "added_tracks": len(ROUTE), "added_vias": 0,
        "in1_gnd_samples": samples,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"summary": str(out / "summary.json"),
                      "status": summary["status"], "violations": summary["candidate_violations"]}))


if __name__ == "__main__":
    main()
