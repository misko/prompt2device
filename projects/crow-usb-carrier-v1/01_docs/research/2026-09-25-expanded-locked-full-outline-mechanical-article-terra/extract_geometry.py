#!/usr/bin/env python3
"""Extract a no-fabrication mechanical-screen manifest from the pinned board."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
import sys

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
PRIVATE = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925'
BOARD = PRIVATE / '04_kicad/crow_carrier.kicad_pcb'
EXPECTED_SHA = 'fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16'
CONNECTORS = {
    **{f'J{i}': ('crow_usb_analog', 'Wurth_615008160221_RJ45', 50 + 22 * (i - 1), 26.86, 0)
       for i in range(1, 9)},
    'J_PWR': ('crow_usb_power_aux', 'Molex_43650-0200', 30, 29.42, 0),
    'J_USB': ('crow_usb_carrier_v1', 'GCT_USB4215_03_A', 230, 22.995, 180),
    'J_JTAG': ('crow_usb_digital', 'Samtec_FTSH_105_01_L_DV_K', 228, 50, 90),
}
HOLES = {'H1': (30, 40), 'H2': (130, 40), 'H3': (211.5, 45),
         'H4': (18, 82), 'H5': (130, 142), 'H6': (230, 130)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mm(v: int) -> float:
    return round(pcbnew.ToMM(v), 6)


def courtyard_bbox(fp: pcbnew.FOOTPRINT) -> list[float] | None:
    items = [g for g in fp.GraphicalItems() if g.GetLayer() == pcbnew.F_CrtYd]
    if not items:
        return None
    boxes = [g.GetBoundingBox() for g in items]
    return [mm(min(b.GetLeft() for b in boxes)), mm(min(b.GetTop() for b in boxes)),
            mm(max(b.GetRight() for b in boxes)), mm(max(b.GetBottom() for b in boxes))]


def rect_distance(point: tuple[float, float], box: list[float]) -> float:
    x, y = point
    dx = max(box[0] - x, 0, x - box[2])
    dy = max(box[1] - y, 0, y - box[3])
    return math.hypot(dx, dy)


def main() -> None:
    if sha(BOARD) != EXPECTED_SHA:
        raise SystemExit('private board SHA drift')
    board = pcbnew.LoadBoard(str(BOARD))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    if set(CONNECTORS) - set(fps) or set(HOLES) - set(fps):
        raise SystemExit('connector or mounting-hole reference absent')
    if board.GetCopperLayerCount() != 4:
        raise SystemExit('not a four-copper board')
    text = BOARD.read_text()
    thickness = re.search(r'\(general\s+\(thickness\s+([0-9.]+)\)', text)
    if not thickness or float(thickness.group(1)) != 1.63:
        raise SystemExit('1.63-mm board target drift')
    edge = []
    for d in board.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts:
            edge.extend(((mm(d.GetStart().x), mm(d.GetStart().y)),
                         (mm(d.GetEnd().x), mm(d.GetEnd().y))))
    xs, ys = sorted({p[0] for p in edge}), sorted({p[1] for p in edge})
    if xs != [10.0, 240.0] or ys != [20.0, 150.0] or len(edge) != 8:
        raise SystemExit(f'outline drift: {xs=}, {ys=}, {len(edge)=}')

    rows = []
    connector_refs = set(CONNECTORS)
    for ref in sorted(CONNECTORS):
        fp = fps[ref]
        nick, item = str(fp.GetFPID().GetLibNickname()), str(fp.GetFPID().GetLibItemName())
        x, y = mm(fp.GetPosition().x), mm(fp.GetPosition().y)
        rot = round(fp.GetOrientationDegrees(), 6)
        expected = CONNECTORS[ref]
        if (nick, item, x, y, rot) != expected:
            raise SystemExit(f'{ref}: native identity or pose drift')
        near = []
        for other_ref, other in fps.items():
            if other_ref == ref or other_ref in connector_refs or other_ref.startswith('H'):
                continue
            bbox = courtyard_bbox(other)
            if bbox:
                near.append((rect_distance((x, y), bbox), other_ref, bbox))
        near.sort(key=lambda r: (r[0], r[1]))
        rows.append({'ref': ref, 'footprint': f'{nick}:{item}', 'pose_mm_deg': [x, y, rot],
                     'courtyard_bbox_mm': courtyard_bbox(fp),
                     'nearest_nominal_nonconnector_courtyards': [
                         {'ref': r, 'center_to_bbox_mm': round(d, 6), 'bbox_mm': b}
                         for d, r, b in near[:3]
                     ]})
    holes = []
    for ref in sorted(HOLES):
        fp = fps[ref]
        x, y = mm(fp.GetPosition().x), mm(fp.GetPosition().y)
        if (x, y) != HOLES[ref] or str(fp.GetFPID().GetLibItemName()) != 'MountingHole_3.2mm_M3':
            raise SystemExit(f'{ref}: mounting geometry drift')
        holes.append({'ref': ref, 'footprint': 'MountingHole:MountingHole_3.2mm_M3',
                      'pose_mm_deg': [x, y, round(fp.GetOrientationDegrees(), 6)],
                      'courtyard_bbox_mm': courtyard_bbox(fp)})
    result = {
        'status': 'RESEARCH_MECHANICAL_ARTICLE_CANDIDATE_NO_FAB',
        'source_board': str(BOARD.relative_to(PROJECT)),
        'source_board_sha256': EXPECTED_SHA,
        'board_target': {'outline_mm': [10, 20, 240, 150], 'size_mm': [230, 130],
                         'copper_layers': 4, 'nominal_thickness_mm': 1.63},
        'connectors': rows, 'mounting_holes': holes,
        'screen_limit': ('Courtyard bounding boxes screen only nominal placed-neighbor proximity; '
                         'they are not assembled body, mate, cable, fixture, force, tolerance, or enclosure evidence.'),
        'fabrication_payload': False, 'connector_full_credit': False,
    }
    (HERE / 'native_geometry.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'board_sha256': EXPECTED_SHA, 'connectors': len(rows),
                      'holes': len(holes), 'outline_mm': result['board_target']['size_mm']}, indent=2))


if __name__ == '__main__':
    main()
