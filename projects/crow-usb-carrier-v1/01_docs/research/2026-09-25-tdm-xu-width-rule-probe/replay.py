#!/usr/bin/python3
"""Isolated KiCad 10 predicate controls for one TDM pad; no source edits."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
BOARD = HERE.parent / "2026-09-25-ti-timing-coupled-placement-sol/candidate.kicad_pcb"
BOARD_SHA = "53e6fb7809910946c36053e7ceeb77e7fc866456ff77775ed4c59b3e49278555"
AREA = "tdm_xu_107_launch"
PAD_PT = (200.8375, 97.6)
END_PT = (199.805, 97.6)
RECT = (199.7, 97.49, 200.95, 97.71)


def point(x, y):
    return pcbnew.VECTOR2I(round(x * 1e6), round(y * 1e6))


def make_board(case, destination):
    board = pcbnew.LoadBoard(str(BOARD))
    pad = [p for fp in board.GetFootprints() if fp.GetReference() == "U_XU"
           for p in fp.Pads() if p.GetNumber() == "107"]
    assert len(pad) == 1 and pad[0].GetNetname() == "TDM_DATA_1V8"
    assert pad[0].GetPosition() == point(*PAD_PT)
    if case != "no_area":
        x0, y0, x1, y1 = RECT
        zone = pcbnew.ZONE(board)
        zone.SetIsRuleArea(True)
        zone.SetLayer(pcbnew.F_Cu)
        zone.SetZoneName(AREA)
        for setter in (zone.SetDoNotAllowTracks, zone.SetDoNotAllowVias,
                       zone.SetDoNotAllowPads, zone.SetDoNotAllowZoneFills,
                       zone.SetDoNotAllowFootprints):
            setter(False)
        zone.Outline().NewOutline()
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            zone.Outline().Append(round(x * 1e6), round(y * 1e6))
        board.Add(zone)
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(point(*PAD_PT))
    track.SetEnd(point(199.5, 97.6) if case == "too_long" else point(*END_PT))
    track.SetWidth(150000)
    track.SetLayer(pcbnew.F_Cu)
    track.SetNet(board.FindNet("TDM_DATA_1V8"))
    board.Add(track)
    if case == "usb_hs":
        usb = pcbnew.PCB_TRACK(board)
        usb.SetStart(point(250, 150))
        usb.SetEnd(point(251, 150))
        usb.SetWidth(150000)
        usb.SetLayer(pcbnew.F_Cu)
        usb.SetNet(board.FindNet("USB_DP"))
        board.Add(usb)
    pcbnew.SaveBoard(str(destination), board)


def rules(case):
    net = "N0V9" if case == "wrong_net" else "TDM_DATA_1V8"
    return f'''(version 1)
(rule "general_track_width_020"
  (constraint track_width (min 0.20mm)))
(rule "USB_HS_width"
  (condition "A.NetName == 'USB_DP' || A.NetName == 'USB_DN'")
  (constraint track_width (min 0.41mm)))
(rule "tdm_xu_107_launch_width"
  (layer F.Cu)
  (condition "A.NetName == '{net}' && A.enclosedByArea('{AREA}')")
  (constraint track_width (min 0.15mm)))
'''


def target_findings(report, net):
    out = []
    for item in report["violations"]:
        if item["type"] not in {"track_width", "clearance", "items_not_allowed"}:
            continue
        if any(f"Track [{net}]" in x["description"] for x in item["items"]):
            out.append((item["type"], item["description"]))
    return out


def main():
    if hashlib.sha256(BOARD.read_bytes()).hexdigest() != BOARD_SHA:
        raise SystemExit("candidate board hash changed; refusing stale replay")
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/crow-tdm-rule-replay-sol")
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for case in ("positive", "wrong_net", "too_long", "no_area", "usb_hs"):
        stem = out / case
        board_path = stem.with_suffix(".kicad_pcb")
        make_board(case, board_path)
        shutil.copyfile(HERE / "probe.kicad_pro", stem.with_suffix(".kicad_pro"))
        stem.with_suffix(".kicad_dru").write_text(rules(case))
        report_path = stem.with_suffix(".json")
        subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all",
                        "--all-track-errors", "--format", "json", "-o",
                        str(report_path), str(board_path)], check=True,
                       capture_output=True, text=True)
        report = json.loads(report_path.read_text())
        data = target_findings(report, "TDM_DATA_1V8")
        usb = target_findings(report, "USB_DP")
        widths = [description for kind, description in data if kind == "track_width"]
        if case in ("positive", "usb_hs"):
            assert not data, (case, data)
        else:
            assert len(widths) == 1 and "general_track_width_020" in widths[0], (case, data)
        if case == "usb_hs":
            assert len(usb) == 1 and usb[0][0] == "track_width" and "USB_HS_width" in usb[0][1], usb
        results[case] = {"violations_total": len(report["violations"]),
                         "unconnected_total": len(report["unconnected_items"]),
                         "tdm_findings": data, "usb_findings": usb}
    (out / "summary.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
