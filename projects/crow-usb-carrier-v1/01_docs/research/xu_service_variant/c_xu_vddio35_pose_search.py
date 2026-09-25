#!/usr/bin/env python3
"""Read-only pose search for the C_XU_VDDIO_35 oscillator-handoff repair."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pcbnew
import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PACKET = HERE / "p1_qspi_packet"
BOARD = Path("/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb")
FLOORPLAN = PACKET / "floorplan_qspi_gap.yaml"
SOURCE = PACKET / "p1_source_variant.yaml"
OUT = HERE / "c_xu_vddio35_pose_search.json"
EXPECTED = {
    "board": "fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27",
    "floorplan": "cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925",
    "source": "9a13c0999d29f17280bb5d8ffb98a5e0d59afe3ee4511eb004e436bffc13ece4",
}

# The source-owned repair proposed in xtal_region_handoff_search.py.  The cap
# must remain in the east XMOS slice, above the oscillator-handoff entry.
XU_EAST = [217.2, 84.0, 232.0, 105.5]
HANDOFF = [217.2, 105.5, 218.95, 118.5]
CLEARANCE = 0.15  # pinned floorplan's design_rules.min_clearance
GRID = 0.05


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox_mm(box) -> list[float]:
    return [round(v / 1_000_000, 6) for v in
            (box.GetX(), box.GetY(), box.GetRight(), box.GetBottom())]


def physical_envelope(fp) -> list[float]:
    """Native body + F/B courtyards; deliberately excludes movable text."""
    body = bbox_mm(fp.GetBoundingBox(False, False))
    for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        courtyard = fp.GetCourtyard(layer)
        if courtyard.OutlineCount():
            x0, y0, x1, y1 = bbox_mm(courtyard.BBox())
            body = [min(body[0], x0), min(body[1], y0),
                    max(body[2], x1), max(body[3], y1)]
    return body


def intersects(a: list[float], b: list[float]) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def inflate(box: list[float], amount: float) -> list[float]:
    return [box[0] - amount, box[1] - amount, box[2] + amount, box[3] + amount]


def inside(box: list[float], region: list[float]) -> bool:
    return (box[0] >= region[0] and box[1] >= region[1]
            and box[2] <= region[2] and box[3] <= region[3])


def center_mm(pad) -> list[float]:
    point = pad.GetPosition()
    return [round(point.x / 1_000_000, 6), round(point.y / 1_000_000, 6)]


def distance(a: list[float], b: list[float]) -> float:
    return round(math.hypot(a[0] - b[0], a[1] - b[1]), 6)


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
    cap = board.FindFootprintByReference("C_XU_VDDIO_35")
    xu = board.FindFootprintByReference("U_XU")
    if cap is None or xu is None:
        raise RuntimeError("native cap or XU missing")
    xu35 = next((pad for pad in xu.Pads() if pad.GetNumber() == "35"), None)
    if xu35 is None or xu35.GetNetname() != "N1V8":
        raise RuntimeError("U_XU.35 net drift")

    original_envelope = physical_envelope(cap)
    original_pads = {pad.GetNumber(): pad for pad in cap.Pads()}
    if {name: pad.GetNetname() for name, pad in original_pads.items()} != {"1": "N1V8", "2": "GND"}:
        raise RuntimeError("C_XU_VDDIO_35 pad/net drift")
    original_n1v8 = center_mm(original_pads["1"])
    xu35_center = center_mm(xu35)

    # Store immutable obstacles before moving the in-memory cap.  Courtyards
    # and bodies are expanded by the declared clearance; a later DRC remains
    # necessary because this is a rectangle-level placement screen.
    obstacles = [(fp.GetReference(), physical_envelope(fp))
                 for fp in board.GetFootprints()
                 if fp.GetReference() != cap.GetReference()]
    inflated = [(ref, inflate(box, CLEARANCE)) for ref, box in obstacles]
    fixed = set(source["p1_fixed_refs"])
    fixed_envelopes = {ref: box for ref, box in obstacles if ref in fixed}

    candidates = []
    for rotation in (0, 90, 180, 270):
        for xi in range(round(XU_EAST[0] / GRID), round(XU_EAST[2] / GRID) + 1):
            for yi in range(round(XU_EAST[1] / GRID), round(XU_EAST[3] / GRID) + 1):
                cap.SetOrientationDegrees(rotation)
                cap.SetPosition(pcbnew.VECTOR2I(round(xi * GRID * 1_000_000),
                                                 round(yi * GRID * 1_000_000)))
                envelope = physical_envelope(cap)
                if not inside(envelope, XU_EAST):
                    continue
                if intersects(envelope, HANDOFF):
                    continue
                if any(intersects(envelope, box) for _, box in inflated):
                    continue
                pads = {pad.GetNumber(): pad for pad in cap.Pads()}
                n1v8 = center_mm(pads["1"])
                gnd = center_mm(pads["2"])
                candidates.append({
                    "at_mm": [round(xi * GRID, 3), round(yi * GRID, 3)],
                    "rotation_deg": rotation,
                    "envelope_mm": envelope,
                    "n1v8_pad_center_mm": n1v8,
                    "gnd_pad_center_mm": gnd,
                    "u_xu_35_to_n1v8_pad_mm": distance(xu35_center, n1v8),
                })
    if not candidates:
        raise RuntimeError("no clearance-aware candidate in source region")
    candidates.sort(key=lambda row: (row["u_xu_35_to_n1v8_pad_mm"],
                                     row["rotation_deg"], row["at_mm"]))
    best = candidates[0]

    # Reapply the chosen in-memory pose and explicitly enumerate envelope and
    # pad collisions.  This does not write the loaded board.
    cap.SetOrientationDegrees(best["rotation_deg"])
    cap.SetPosition(pcbnew.VECTOR2I(round(best["at_mm"][0] * 1_000_000),
                                     round(best["at_mm"][1] * 1_000_000)))
    selected_pads = {pad.GetNumber(): pad for pad in cap.Pads()}
    selected_pad_boxes = {name: bbox_mm(pad.GetBoundingBox())
                          for name, pad in selected_pads.items()}
    body_hits = sorted(ref for ref, box in obstacles
                       if intersects(physical_envelope(cap), box))
    pad_hits = sorted(f"{fp.GetReference()}.{pad.GetNumber()}"
                      for fp in board.GetFootprints()
                      if fp.GetReference() != cap.GetReference()
                      for pad in fp.Pads()
                      if any(intersects(box, bbox_mm(pad.GetBoundingBox()))
                             for box in selected_pad_boxes.values()))
    fixed_hits = sorted(ref for ref, box in fixed_envelopes.items()
                       if intersects(physical_envelope(cap), box))
    if body_hits or pad_hits or fixed_hits:
        raise RuntimeError("selected pose collision denominator drift")

    # The pinned board has no local GND via at the original or selected cap.
    # Record that fact rather than crediting a hypothetical In1 return.
    gnd_vias = []
    for item in board.GetTracks():
        if item.GetClass() == "PCB_VIA" and item.GetNetname() == "GND":
            point = item.GetPosition()
            gnd_vias.append([point.x / 1_000_000, point.y / 1_000_000])
    nearest_via = min((distance(best["gnd_pad_center_mm"], point) for point in gnd_vias),
                      default=None)
    if nearest_via is None:
        raise RuntimeError("no native GND via denominator drift")

    result = {
        "schema": 1,
        "kind": "crow-c-xu-vddio35-in-memory-pose-search",
        "status": "NO_SHORT_RETURN-PROVEN_POSE",
        "hashes": hashes,
        "search": {"region_mm": XU_EAST, "handoff_exclusion_mm": HANDOFF,
                   "grid_mm": GRID, "clearance_mm": CLEARANCE,
                   "candidate_count": len(candidates)},
        "original": {
            "at_mm": [218.0, 105.8], "rotation_deg": 90,
            "envelope_mm": original_envelope,
            "u_xu_35_center_mm": xu35_center,
            "n1v8_pad_center_mm": original_n1v8,
            "u_xu_35_to_n1v8_pad_mm": distance(xu35_center, original_n1v8),
        },
        "nearest_clearance_aware_pose": {
            **best, "pad_bboxes_mm": selected_pad_boxes,
            "native_body_courtyard_hits": body_hits,
            "native_pad_hits": pad_hits,
            "p1_fixed_ref_hits": fixed_hits,
            "distance_increase_mm": round(best["u_xu_35_to_n1v8_pad_mm"]
                                             - distance(xu35_center, original_n1v8), 6),
        },
        "direct_gnd_return": {
            "nearest_existing_gnd_via_mm": nearest_via,
            "finding": "No local native GND via exists; a new adjacent via and filled In1.Cu proof are P2 debt.",
        },
        "conclusion": (
            "The nearest clearance-aware in-region pose is materially farther from U_XU.35 than the pinned pose and has no existing adjacent GND via. "
            "It is a collision-free geometric fallback only, not evidence that the required short local N1V8 connection or direct GND return is preserved."),
        "not_claimed": ["P2 placement approval", "routing", "In1 filled return", "DRC", "P1 acceptance"],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "best": best,
                      "nearest_gnd_via_mm": nearest_via}, indent=2))


if __name__ == "__main__":
    main()
