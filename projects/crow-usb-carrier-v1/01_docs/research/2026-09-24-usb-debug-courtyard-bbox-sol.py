#!/usr/bin/env python3
"""Reproduce the stroke-expanded F.CrtYd boxes in the USB/debug split note.

Usage: python3 this_script.py /path/to/crow_carrier.kicad_pcb
Requires KiCad's pcbnew Python module. Refuses boards other than the pinned
QSPI-gap regeneration, so the printed geometry cannot silently drift.
"""

import hashlib
import json
import sys
from pathlib import Path

import pcbnew


BOARD_SHA256 = "fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27"
USB_REFS = (
    "J_USB", "C_USB_VBUS", "R_USB_CC1", "R_USB_CC2",
    "R_USB_VBUS_BLEED", "U_USB_CC_ESD", "U_USB_ESD", "U_USB_VBUS_ESD",
)
OTHER_REFS = ("J_JTAG", "J8")
USB_REGION = (200, 35, 238.5, 40)
JTAG_STRIP = (221, 65, 226, 84)


def box_mm(box):
    return tuple(round(n / 1_000_000, 6) for n in
                 (box.GetX(), box.GetY(), box.GetRight(), box.GetBottom()))


def overlap(a, b):
    return (max(a[0], b[0]) < min(a[2], b[2]) and
            max(a[1], b[1]) < min(a[3], b[3]))


def contains(outer, inner):
    return (outer[0] <= inner[0] and outer[1] <= inner[1] and
            inner[2] <= outer[2] and inner[3] <= outer[3])


def union(boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def main(board_path):
    digest = hashlib.sha256(board_path.read_bytes()).hexdigest()
    if digest != BOARD_SHA256:
        raise SystemExit(f"board SHA-256 mismatch: {digest}")
    board = pcbnew.LoadBoard(str(board_path))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    boxes = {}
    for ref in USB_REFS + OTHER_REFS:
        fp = fps[ref]
        courtyard = fp.GetCourtyard(pcbnew.F_CrtYd)
        if courtyard.IsEmpty():
            raise SystemExit(f"missing F.CrtYd: {ref}")
        boxes[ref] = box_mm(courtyard.BBox(0))
    support_union = union([boxes[ref] for ref in USB_REFS if ref != "J_USB"])
    j8 = boxes["J8"]
    j8_intersection = (
        round(max(0, min(support_union[2], j8[2]) -
                  max(support_union[0], j8[0])), 6),
        round(max(0, min(support_union[3], j8[3]) -
                  max(support_union[1], j8[1])), 6),
    )
    strip_hits = []
    for fp in fps.values():
        shapes = [box_mm(fp.GetBoundingBox(False, False))]
        shapes.extend(box_mm(pad.GetBoundingBox()) for pad in fp.Pads())
        courtyard = fp.GetCourtyard(pcbnew.F_CrtYd)
        if not courtyard.IsEmpty():
            shapes.append(box_mm(courtyard.BBox(0)))
        if any(overlap(JTAG_STRIP, shape) for shape in shapes):
            strip_hits.append(fp.GetReference())
    print(json.dumps({
        "board_sha256": digest,
        "footprints": len(fps),
        "courtyard_method": "FOOTPRINT.GetCourtyard(F_CrtYd).BBox(0), including stroke",
        "courtyard_boxes_mm": boxes,
        "usb_support_union_excluding_J_USB_mm": support_union,
        "usb_region_fully_contains_refs": [ref for ref in USB_REFS
                                           if contains(USB_REGION, boxes[ref])],
        "support_union_intersection_with_J8_mm": j8_intersection,
        "jtag_strip_body_pad_courtyard_hits": sorted(strip_hits),
    }, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: script.py /path/to/crow_carrier.kicad_pcb")
    main(Path(sys.argv[1]))
