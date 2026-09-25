#!/usr/bin/env /usr/bin/python3
"""Read-only, hash-pinned USB pad and rule screen on the expanded Crow board."""

import hashlib
import json
from pathlib import Path

import pcbnew

PROJECT = Path(__file__).resolve().parents[3]
BOARD = PROJECT / "06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb"
RULES = PROJECT / "03_src/rules/nets.yaml"
D15 = PROJECT / "06_build/prototype_board_diagnostic/current-ti-4l-3313a-preflight-20260925/04_kicad/crow_carrier.kicad_dru"
D15_PRO = D15.with_suffix(".kicad_pro")
D15_BOARD = D15.with_suffix(".kicad_pcb")
EXPECTED = {
    BOARD: "fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16",
    RULES: "18033487a097b6d29abe3f9d8517879931cf80d278d8973adcf276010a5b7190",
    D15: "ddb17c62f3beb2e0a03cf18acbb1148c36f60d516937c96660cfb44d146520a3",
    D15_PRO: "2d0bf4d9c14fedee82e1ba22f06d05a4ba97e7b7fe39a66e086ec1c48b408c1a",
    D15_BOARD: "ee34cf62a436fbebcd9afbdd0f046e5b9796e6a9ab60a8283d2e297a177b1db6",
}


def mm(n):
    return round(n / 1_000_000, 6)


def record(pad):
    box = pad.GetBoundingBox()
    return {
        "net": pad.GetNetname(),
        "center": [mm(pad.GetPosition().x), mm(pad.GetPosition().y)],
        "bbox": [mm(box.GetX()), mm(box.GetY()), mm(box.GetRight()), mm(box.GetBottom())],
    }


def main():
    for path, expected in EXPECTED.items():
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
    text = RULES.read_text()
    assert "min_width: 0.410mm" in text and "diff_pair: {width: 0.410mm, gap: 0.150mm}" in text
    dr = D15.read_text()
    assert "scoped_clr_usb_pair_xu_launch" in dr and "A.insideArea('usb_pair_xu_launch') && B.insideArea('usb_pair_xu_launch')" in dr
    assert "(constraint clearance (min 0.1mm))" in dr
    classes = {c["name"]: c for c in json.loads(D15_PRO.read_text())["net_settings"]["classes"]}
    assert {k: classes["USB_HS"][k] for k in ("track_width", "clearance", "diff_pair_width", "diff_pair_gap")} == {
        "track_width": .18, "clearance": .15, "diff_pair_width": .18, "diff_pair_gap": .1
    }
    d15board = pcbnew.LoadBoard(str(D15_BOARD))
    areas = [z for z in d15board.Zones() if z.GetZoneName() == "usb_pair_xu_launch"]
    assert len(areas) == 1 and areas[0].GetLayerName() == "F.Cu"
    ab = areas[0].GetBoundingBox()
    assert [mm(v) for v in (ab.GetX(), ab.GetY(), ab.GetRight(), ab.GetBottom())] == [215.3, 95.0, 217.1, 95.8]
    board = pcbnew.LoadBoard(str(BOARD))
    refs = {f.GetReference(): f for f in board.GetFootprints()}
    selected = {
        ref: {p.GetNumber(): record(p) for p in refs[ref].Pads() if p.GetNumber() in numbers}
        for ref, numbers in {
            "U_XU": {"58", "59", "60", "61"},
            "U_USB_ESD": {"1", "2", "3"},
            "J_USB": {"A6", "A7", "B6", "B7", "A8", "B8"},
        }.items()
    }
    assert selected["U_XU"]["59"]["net"] == "USB_DN"
    assert selected["U_XU"]["60"]["net"] == "USB_DP"
    assert selected["U_USB_ESD"]["1"]["net"] == "USB_DP"
    assert selected["U_USB_ESD"]["2"]["net"] == "USB_DN"
    assert [selected["J_USB"][p]["net"] for p in ("B6", "A7", "A6", "B7")] == ["USB_DP", "USB_DN", "USB_DP", "USB_DN"]
    # A centered straight track overhangs a pad by max(0,(width-pad_width)/2).
    # Subtract this from the exact native adjacent-pad edge gap.
    x = selected["J_USB"]
    c_gap = x["B6"]["bbox"][0] - x["A8"]["bbox"][2]
    assert abs(x["A7"]["bbox"][0] - x["B6"]["bbox"][2] - c_gap) < 1e-6
    y = selected["U_XU"]
    xu_gap = y["60"]["bbox"][1] - y["61"]["bbox"][3]
    assert abs(y["59"]["bbox"][1] - y["60"]["bbox"][3] - xu_gap) < 1e-6
    assert abs(c_gap - .2) < 1e-6 and abs(xu_gap - .15) < 1e-6
    clearance = {
        "connector_foreign_union_from_centered_041": round(c_gap - (.410 - .300) / 2, 6),
        "connector_foreign_union_from_centered_018": round(c_gap, 6),
        "xu_foreign_union_from_centered_041": round(xu_gap - (.410 - .250) / 2, 6),
        "xu_foreign_union_from_centered_018": round(xu_gap, 6),
        "xu_foreign_track_only_from_centered_018": round(.400 - .180 / 2 - .250 / 2, 6),
        "xu_pair_edge_gap_at_041": round(.400 - .410, 6),
        "xu_pair_edge_gap_at_018": round(.400 - .180, 6),
    }
    result = {
        "inputs_sha256": {str(p.relative_to(PROJECT)): h for p, h in EXPECTED.items()},
        "pads_mm": selected,
        "calculated_mm": clearance,
        "board_copper_layers": board.GetCopperLayerCount(),
        "saved_gnd_zones": [{"layer": z.GetLayerName(), "filled": bool(z.IsFilled())} for z in board.Zones() if z.GetNetname() == "GND"],
        "claims": "geometry lower bound only; no native route, DRC, filled In1.Cu reference, SI or connector proof",
    }
    for path, expected in EXPECTED.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"changed during measurement: {path}"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
