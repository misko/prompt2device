#!/usr/bin/env python3
"""Adversarial scope controls for the committed TDM DATA local-neck packet."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "skills/kicad-pcb/scripts"))
import pcbnew  # noqa: E402

PACKET = ROOT / "projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-timing-data-neck-fab-probe-sol"
BOARD = PACKET / "local_neck.kicad_pcb"
PROJECT = PACKET / "local_neck.kicad_pro"
RULE = PACKET / "local_neck.kicad_dru"
OUT = HERE / "control_receipt.json"


def run_control(folder, name, net):
    board = pcbnew.LoadBoard(str(BOARD))
    track = pcbnew.PCB_TRACK(board)
    track.SetLayer(pcbnew.F_Cu)
    track.SetWidth(pcbnew.FromMM(0.15))
    track.SetNet(board.FindNet(net))
    # x=198 is deliberately outside the [199.7,200.95] named local area.
    track.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(198.0), pcbnew.FromMM(97.6)))
    track.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(198.5), pcbnew.FromMM(97.6)))
    board.Add(track)
    board_path = folder / f"{name}.kicad_pcb"
    pcbnew.SaveBoard(str(board_path), board)
    shutil.copyfile(PROJECT, folder / f"{name}.kicad_pro")
    shutil.copyfile(RULE, folder / f"{name}.kicad_dru")
    report = folder / f"{name}.json"
    command = ["kicad-cli", "pcb", "drc", "--refill-zones", "--format", "json", "-o", str(report), str(board_path)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    result = json.loads(report.read_text())
    related = [v for v in result["violations"] if any(
        f"Track [{net}]" in item["description"] for item in v["items"])]
    widths = [v for v in related if v["type"] == "track_width" and "actual 0.1500 mm" in v["description"]]
    if len(widths) != 1:
        raise SystemExit(f"{name}: scoped-rule escape not rejected: {related}")
    # Do not preserve generated UUIDs in the receipt; they are intentionally
    # ephemeral because controls live only in the temporary directory.
    return {"net": net, "area": "outside", "violations": len(result["violations"]),
            "unconnected": len(result["unconnected_items"]),
            "track_items": [{"type": v["type"], "description": v["description"]} for v in related]}


def main():
    version = subprocess.run(["kicad-cli", "--version"], check=True, capture_output=True, text=True).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="crow-data-scope-control-") as temp:
        folder = Path(temp)
        controls = [run_control(folder, "same_net_outside", "TDM_DATA_1V8"),
                    run_control(folder, "other_net_outside", "TDM_BCLK_1V8")]
    result = {"kind": "local-neck-rule-scope-adversarial-control", "kicad_cli_version": version,
              "coordinates_mm": [[198.0, 97.6], [198.5, 97.6]], "controls": controls,
              "conclusion": "Both 0.15-mm controls receive the board-setup 0.20-mm track-width error; the committed width exception did not apply outside its named area."}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"version": version, "controls": len(controls)}))


if __name__ == "__main__":
    main()
