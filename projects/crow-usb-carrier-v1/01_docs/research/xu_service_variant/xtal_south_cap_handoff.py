#!/usr/bin/env python3
"""Read-only 0.15/0.15 dogleg screen that preserves C_XU_VDDIO_35's pose."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pcbnew
import yaml

HERE = Path(__file__).resolve().parent
PACKET = HERE / "p1_qspi_packet"
BOARD = Path("/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb")
FLOORPLAN = PACKET / "floorplan_qspi_gap.yaml"
SOURCE = PACKET / "p1_source_variant.yaml"
OUT = HERE / "xtal_south_cap_handoff.json"
EXPECTED = {
    "board": "fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27",
    "floorplan": "cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925",
    "source": "9a13c0999d29f17280bb5d8ffb98a5e0d59afe3ee4511eb004e436bffc13ece4",
}
WIDTH, CLEARANCE = 0.15, 0.15
OBSTACLE_RADIUS = WIDTH / 2 + CLEARANCE
PAIR_RADIUS = WIDTH / 2 + CLEARANCE / 2
HANDOFF = [217.2, 107.0, 218.95, 118.5]
SHIFTED_QSPI = [219.2, 110.5, 223.2, 118.5]
SHIFTED_QSPI_FACE = [219.2, 110.2, 222.8, 110.5]
PROPOSED_REGIONS = {
    "xmos_core_west": [190.0, 84.0, 217.2, 110.5],
    "xmos_core_east": [217.2, 84.0, 232.0, 107.0],
    "clock_oscillator_handoff": HANDOFF,
    "board_integration_qspi": SHIFTED_QSPI,
    "clock_flash_debug": [190.0, 118.5, 232.0, 136.0],
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox_mm(box) -> list[float]:
    return [round(v / 1_000_000, 6) for v in
            (box.GetX(), box.GetY(), box.GetRight(), box.GetBottom())]


def envelope(fp) -> list[float]:
    """Physical body plus F/B courtyards, excluding movable reference text."""
    result = bbox_mm(fp.GetBoundingBox(False, False))
    for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        courtyard = fp.GetCourtyard(layer)
        if courtyard.OutlineCount():
            x0, y0, x1, y1 = bbox_mm(courtyard.BBox())
            result = [min(result[0], x0), min(result[1], y0),
                      max(result[2], x1), max(result[3], y1)]
    return result


def intersects(a: list[float], b: list[float]) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def sweep(a: list[float], b: list[float], radius: float) -> list[float]:
    return [min(a[0], b[0]) - radius, min(a[1], b[1]) - radius,
            max(a[0], b[0]) + radius, max(a[1], b[1]) + radius]


def point(pad) -> list[float]:
    position = pad.GetPosition()
    return [round(position.x / 1_000_000, 6), round(position.y / 1_000_000, 6)]


def main() -> None:
    paths = {"board": BOARD, "floorplan": FLOORPLAN, "source": SOURCE}
    hashes = {name: digest(path) for name, path in paths.items()}
    for name, expected in EXPECTED.items():
        if hashes[name] != expected:
            raise RuntimeError(f"{name} hash drift: {hashes[name]}")
    floorplan = yaml.safe_load(FLOORPLAN.read_text())
    source = yaml.safe_load(SOURCE.read_text())
    if floorplan["design_rules"]["min_clearance"] != CLEARANCE:
        raise RuntimeError("clearance authority drift")

    board = pcbnew.LoadBoard(str(BOARD))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    xu, cap = fps["U_XU"], fps["C_XU_VDDIO_35"]
    xu_pads = {pad.GetNumber(): pad for pad in xu.Pads()}
    for number, net in (("33", "XTAL_OUT"), ("34", "XTAL_IN"), ("35", "N1V8")):
        if xu_pads[number].GetNetname() != net:
            raise RuntimeError(f"U_XU.{number} net drift")
    cap_pads = {pad.GetNumber(): pad for pad in cap.Pads()}
    if cap_pads["1"].GetNetname() != "N1V8" or cap_pads["2"].GetNetname() != "GND":
        raise RuntimeError("C_XU_VDDIO_35 pad/net drift")
    cap_envelope = envelope(cap)
    if cap_envelope[3] + CLEARANCE > HANDOFF[1]:
        raise RuntimeError("handoff starts inside stroked cap courtyard")
    if not (PROPOSED_REGIONS["xmos_core_east"][0] <= cap_envelope[0]
            and cap_envelope[2] <= PROPOSED_REGIONS["xmos_core_east"][2]
            and cap_envelope[3] <= PROPOSED_REGIONS["xmos_core_east"][3]):
        raise RuntimeError("current cap not contained by local XU east region")

    routes = {
        "XTAL_IN": [point(xu_pads["34"]), [217.2, 105.8], [217.2, 104.59],
                    [218.8, 104.59], [218.8, 107.1]],
        "XTAL_OUT": [point(xu_pads["33"]), [217.2, 106.2], [217.2, 107.1]],
    }
    sweeps = {net: [sweep(a, b, OBSTACLE_RADIUS) for a, b in zip(path, path[1:])]
              for net, path in routes.items()}
    pair_sweeps = {net: [sweep(a, b, PAIR_RADIUS) for a, b in zip(path, path[1:])]
                   for net, path in routes.items()}
    footprint_hits = {net: [] for net in routes}
    fixed_hits = {net: [] for net in routes}
    own_other_pad_hits = {net: [] for net in routes}
    track_hits = {net: [] for net in routes}
    fixed = set(source["p1_fixed_refs"])
    for net, boxes in sweeps.items():
        for ref, fp in fps.items():
            if ref != "U_XU" and any(intersects(box, envelope(fp)) for box in boxes):
                footprint_hits[net].append(ref)
            if ref in fixed and any(intersects(box, envelope(fp)) for box in boxes):
                fixed_hits[net].append(ref)
        own_other_pad_hits[net] = [pad.GetNumber() for pad in xu.Pads()
                                    if pad.GetNumber() not in {"33", "34"}
                                    and any(intersects(box, bbox_mm(pad.GetBoundingBox())) for box in boxes)]
        track_hits[net] = [{"net": item.GetNetname(), "bbox_mm": bbox_mm(item.GetBoundingBox())}
                           for item in board.GetTracks()
                           if any(intersects(box, bbox_mm(item.GetBoundingBox())) for box in boxes)]
    if any(footprint_hits.values()) or any(fixed_hits.values()) or any(own_other_pad_hits.values()) or any(track_hits.values()):
        raise RuntimeError("dogleg native-obstacle denominator drift")
    pair_hits = [[i, j] for i, a in enumerate(pair_sweeps["XTAL_IN"])
                 for j, b in enumerate(pair_sweeps["XTAL_OUT"])
                 if intersects(a, b)]
    if pair_hits:
        raise RuntimeError(f"XTAL doglegs fail 0.15/0.15 separation: {pair_hits}")

    qspi_native_hits = [ref for ref, fp in fps.items()
                        if intersects(SHIFTED_QSPI, envelope(fp))
                        or intersects(SHIFTED_QSPI_FACE, envelope(fp))]
    qspi_track_hits = [{"net": item.GetNetname(), "bbox_mm": bbox_mm(item.GetBoundingBox())}
                       for item in board.GetTracks()
                       if intersects(SHIFTED_QSPI, bbox_mm(item.GetBoundingBox()))
                       or intersects(SHIFTED_QSPI_FACE, bbox_mm(item.GetBoundingBox()))]
    if qspi_native_hits or qspi_track_hits:
        raise RuntimeError("shifted QSPI face/region has native obstacle")
    if SHIFTED_QSPI_FACE[2] - SHIFTED_QSPI_FACE[0] < 2.7:
        raise RuntimeError("shifted QSPI face below declared six-lane demand")
    names = sorted(PROPOSED_REGIONS)
    overlaps = [[a, b] for i, a in enumerate(names) for b in names[i + 1:]
                if intersects(PROPOSED_REGIONS[a], PROPOSED_REGIONS[b])]
    if overlaps:
        raise RuntimeError(f"proposed source regions overlap: {overlaps}")

    result = {
        "schema": 1, "kind": "crow-xtal-south-cap-handoff-screen",
        "status": "GEOMETRIC_DOGLEG_FEASIBLE_P2_REQUIRED", "hashes": hashes,
        "trace_contract": {"layer": "F.Cu", "width_mm": WIDTH,
                           "clearance_mm": CLEARANCE, "pair_clearance_mm": CLEARANCE},
        "retained_cap": {"ref": "C_XU_VDDIO_35", "envelope_mm": cap_envelope,
                         "pads": {number: {"net": pad.GetNetname(), "bbox_mm": bbox_mm(pad.GetBoundingBox())}
                                  for number, pad in cap_pads.items()}},
        "routes": routes, "obstacle_radius_mm": OBSTACLE_RADIUS,
        "native_footprint_courtyard_hits": footprint_hits,
        "native_fixed_ref_hits": fixed_hits,
        "native_other_u_xu_pad_hits": own_other_pad_hits,
        "native_track_hits": track_hits, "pair_0p15_clearance_hits": pair_hits,
        "proposed_regions_mm": PROPOSED_REGIONS,
        "shifted_qspi": {"region_mm": SHIFTED_QSPI, "xmos_face_mm": SHIFTED_QSPI_FACE,
                         "raw_owner_gap_to_handoff_mm": round(SHIFTED_QSPI[0] - HANDOFF[2], 3),
                         "face_raw_width_mm": round(SHIFTED_QSPI_FACE[2] - SHIFTED_QSPI_FACE[0], 3),
                         "declared_qspi_demand_mm": 2.7,
                         "native_obstacle_hits": qspi_native_hits,
                         "native_track_hits": qspi_track_hits},
        "debt": ["This is a swept-envelope screen, not routed board or DRC.",
                 "The 0.25 mm source-region gap to QSPI is ownership geometry, not electrical clearance proof.",
                 "P2 must prove XTAL pad escapes, actual copper, DRC, and continuous filled In1.Cu GND reference.",
                 "P3 oscillator electrical/length/guard checks and P1 review remain open."],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "qspi": result["shifted_qspi"], "cap": cap_envelope}, indent=2))


if __name__ == "__main__":
    main()
