#!/usr/bin/env python3
"""Pin the smallest source-geometry repair for the Crow XMOS oscillator.

This is a read-only study of the isolated QSPI-gap board.  It does not alter
the canonical floorplan, modular interface plan, board, route, or P1 state.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pcbnew
import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / "projects/crow-usb-carrier-v1"
PACKET = HERE / "p1_qspi_packet"
BOARD = Path("/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb")
FLOORPLAN = PACKET / "floorplan_qspi_gap.yaml"
SOURCE = PACKET / "p1_source_variant.yaml"
OUT = HERE / "xtal_region_handoff_search.json"

EXPECTED = {
    "board": "fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27",
    "floorplan": "cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925",
    "source": "9a13c0999d29f17280bb5d8ffb98a5e0d59afe3ee4511eb004e436bffc13ece4",
}
ENDPOINTS = (
    ("U_XU.34", "XTAL_IN"), ("R_XTAL_DRIVE.1", "XTAL_IN"),
    ("R_XTAL_FB.1", "XTAL_IN"), ("U_XU.33", "XTAL_OUT"),
    ("C_XTAL_OUT.1", "XTAL_OUT"), ("R_XTAL_FB.2", "XTAL_OUT"),
    ("Y_XU.3", "XTAL_OUT"),
)
OSCILLATOR_REFS = {
    "U_XU", "C_XTAL_IN", "C_XTAL_OUT", "R_XTAL_DRIVE", "R_XTAL_FB", "Y_XU",
}

# The proposed narrow handoff reaches the XU's east face and stops short of
# the QSPI south-face x=219.0.  It is intentionally only a coarse P1 shape:
# pad escape, trace clearance and In1 return are P2/P3 obligations.
HANDOFF = [217.2, 105.5, 218.95, 118.5]
SHIFTED_QSPI = [219.0, 110.5, 223.2, 118.5]
XU_WEST = [190.0, 84.0, 217.2, 110.5]
XU_EAST = [217.2, 84.0, 232.0, 105.5]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box_mm(box) -> list[float]:
    return [round(v / 1_000_000, 6) for v in
            (box.GetX(), box.GetY(), box.GetRight(), box.GetBottom())]


def physical_envelope(fp) -> list[float]:
    """Native footprint body plus F/B courtyard, excluding movable text."""
    body = box_mm(fp.GetBoundingBox(False, False))
    for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        courtyard = fp.GetCourtyard(layer)
        if courtyard.OutlineCount():
            x0, y0, x1, y1 = box_mm(courtyard.BBox())
            body = [min(body[0], x0), min(body[1], y0),
                    max(body[2], x1), max(body[3], y1)]
    return body


def intersects(a: list[float], b: list[float]) -> bool:
    # Sharing an owner boundary is permitted; positive-area overlap is not.
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def main() -> None:
    paths = {"board": BOARD, "floorplan": FLOORPLAN, "source": SOURCE}
    hashes = {name: digest(path) for name, path in paths.items()}
    for name, expected in EXPECTED.items():
        if hashes[name] != expected:
            raise RuntimeError(f"{name} hash drift: {hashes[name]}")

    board = pcbnew.LoadBoard(str(BOARD))
    floorplan = yaml.safe_load(FLOORPLAN.read_text())
    source = yaml.safe_load(SOURCE.read_text())
    regions = floorplan["placement"]["regions"]
    if regions["board_integration_qspi"] != [199.8, 110.5, 223.2, 118.5]:
        raise RuntimeError("pinned QSPI region drift")

    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    pads = {f"{fp.GetReference()}.{pad.GetNumber()}": pad
            for fp in board.GetFootprints() for pad in fp.Pads()}
    endpoint_rows = []
    for ref_pad, net in ENDPOINTS:
        pad = pads.get(ref_pad)
        if pad is None or pad.GetNetname() != net:
            raise RuntimeError(f"endpoint drift: {ref_pad}")
        endpoint_rows.append({"ref_pad": ref_pad, "net": net,
                              "pad_bbox_mm": box_mm(pad.GetBoundingBox())})
    if len(endpoint_rows) != 7:
        raise RuntimeError("exact XTAL denominator drift")

    native = {ref: physical_envelope(fp) for ref, fp in footprints.items()}
    candidate_hits = sorted(ref for ref, envelope in native.items()
                            if intersects(envelope, HANDOFF))
    if candidate_hits != ["C_XU_VDDIO_35"]:
        raise RuntimeError(f"handoff obstacle denominator drift: {candidate_hits}")
    qspi_hits = sorted(ref for ref, envelope in native.items()
                       if intersects(envelope, SHIFTED_QSPI))
    if qspi_hits:
        raise RuntimeError(f"shifted QSPI region not physically empty: {qspi_hits}")
    shifted_qspi_copper = [
        {"net": item.GetNetname(), "bbox_mm": box_mm(item.GetBoundingBox())}
        for item in board.GetTracks()
        if intersects(box_mm(item.GetBoundingBox()), SHIFTED_QSPI)
    ]
    if shifted_qspi_copper:
        raise RuntimeError("shifted QSPI region has native copper")

    # The split replaces xmos_core.  The handoff and lower clock region share
    # only y=118.5; the shifted QSPI region shares no positive area with it.
    proposed = {"xmos_core_west": XU_WEST, "xmos_core_east": XU_EAST,
                "clock_oscillator_handoff": HANDOFF,
                "board_integration_qspi": SHIFTED_QSPI,
                "clock_flash_debug": regions["clock_flash_debug"]}
    names = sorted(proposed)
    overlaps = [[a, b] for i, a in enumerate(names) for b in names[i + 1:]
                if intersects(proposed[a], proposed[b])]
    if overlaps:
        raise RuntimeError(f"proposed source regions overlap: {overlaps}")

    fixed_hits = sorted(ref for ref in source["p1_fixed_refs"]
                       if ref in native and any(intersects(native[ref], box)
                                                for box in proposed.values()))
    if fixed_hits:
        raise RuntimeError(f"P1-fixed footprint in proposed repair: {fixed_hits}")

    oscillator_envelopes = {ref: native[ref] for ref in sorted(OSCILLATOR_REFS)}
    result = {
        "schema": 1,
        "kind": "crow-xtal-region-handoff-search",
        "status": "REQUIRES_REGION_SHIFT_AND_C_XU_VDDIO_35_MOVE",
        "hashes": hashes,
        "exact_endpoint_count": len(endpoint_rows),
        "exact_endpoints": endpoint_rows,
        "native_oscillator_envelopes_mm": oscillator_envelopes,
        "p1_fixed_ref_count": len(source["p1_fixed_refs"]),
        "p1_fixed_refs_intersecting_proposal": fixed_hits,
        "current_qspi_region_mm": regions["board_integration_qspi"],
        "proposed_source_regions_mm": proposed,
        "current_qspi_blocks_handoff": intersects(regions["board_integration_qspi"], HANDOFF),
        "shifted_qspi_region_native_hits": qspi_hits,
        "shifted_qspi_region_native_copper_hits": shifted_qspi_copper,
        "handoff_native_hits_before_move": candidate_hits,
        "required_component_move": {
            "ref": "C_XU_VDDIO_35",
            "current_envelope_mm": native["C_XU_VDDIO_35"],
            "reason": "its native body/courtyard blocks the two XTAL pads' east exit",
            "fixed": "C_XU_VDDIO_35 is absent from p1_fixed_refs; its replacement pose needs P2 proof",
        },
        "required_region_move": {
            "from": regions["board_integration_qspi"], "to": SHIFTED_QSPI,
            "reason": "moving the QSPI left edge to its existing x=219.0 face frees the source-owned x=217.2..218.95 oscillator handoff",
            "qspi_raw_width_mm": round(SHIFTED_QSPI[2] - SHIFTED_QSPI[0], 3),
            "qspi_declared_demand_mm": 2.7,
        },
        "remaining_debt": [
            "P2 pad escape and clearance for U_XU.33/U_XU.34 and the moved C_XU_VDDIO_35",
            "P2 placement and route of all oscillator parts; this study does not approve a pose or copper",
            "continuous filled In1.Cu GND reference beneath both XTAL lanes",
            "P3 oscillator electrical/length/guard validation and all P1 allocation review",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "component": "C_XU_VDDIO_35",
                      "qspi": SHIFTED_QSPI, "fixed_hits": fixed_hits}, indent=2))


if __name__ == "__main__":
    main()
