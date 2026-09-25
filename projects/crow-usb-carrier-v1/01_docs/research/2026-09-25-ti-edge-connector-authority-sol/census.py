#!/usr/bin/env python3
"""Read-only north-edge connector authority census on exact TI board."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pcbnew

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BOARD = PROJECT / '01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb'
DOCS = {
    'J_PWR': PROJECT / '02_parts/43650-0200/Molex_436501000_SD_revD8.pdf',
    'J1_to_J8': PROJECT / '02_parts/615008160221/Wurth_615008160221_rev001003.pdf',
    'J_USB': PROJECT / '02_parts/USB4215-03-A/GCT_USB4215_A.pdf',
}
EXPECTED_BOARD = 'd0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7'
REFS = ('J_PWR', *(f'J{n}' for n in range(1, 9)), 'J_USB', 'J_JTAG')
sys.path.insert(0, str(ROOT / 'skills/kicad-pcb/scripts'))
from p1_corridor_capacity import _physical_envelope, box_mm  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def union(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)] if boxes else None


def main():
    if sha(BOARD) != EXPECTED_BOARD:
        raise SystemExit('exact TI board hash drift')
    board = pcbnew.LoadBoard(str(BOARD))
    fp = {f.GetReference(): f for f in board.GetFootprints()}
    edges = [box_mm(x.GetBoundingBox()) for x in board.GetDrawings()
             if x.GetLayer() == pcbnew.Edge_Cuts]
    edge_bbox = union(edges)
    if edge_bbox != [19.95, 19.95, 240.05, 140.05]:
        raise SystemExit('native Edge.Cuts stroke envelope drift')
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise SystemExit('native closed outline unavailable')
    outline_bbox = box_mm(outline.BBox())
    if outline_bbox != (20.0, 20.0, 240.0, 140.0):
        raise SystemExit('native Edge.Cuts centerline outline drift')
    # The 0.1-mm Edge.Cuts line is centered on the nominal y=20 north edge.
    north_center = 20.0
    rows = {}
    for ref in REFS:
        f = fp[ref]
        fab_shapes, fab_text, silk = [], [], []
        for item in f.GraphicalItems():
            box = box_mm(item.GetBoundingBox())
            if item.GetLayer() == pcbnew.F_Fab:
                (fab_text if item.GetClass() == 'PCB_TEXT' else fab_shapes).append(box)
            elif item.GetLayer() == pcbnew.F_SilkS:
                silk.append(box)
        courtyard = f.GetCourtyard(pcbnew.F_CrtYd)
        pads = [box_mm(p.GetBoundingBox()) for p in f.Pads()]
        body = box_mm(f.GetBoundingBox(False, False))
        row = {
            'pose_mm': [pcbnew.ToMM(f.GetPosition().x), pcbnew.ToMM(f.GetPosition().y),
                        f.GetOrientationDegrees()],
            'courtyard_outer_bbox_mm': box_mm(courtyard.BBox()) if courtyard.OutlineCount() else None,
            'generic_graphics_bbox_mm': body,
            'fab_shapes_bbox_mm': union(fab_shapes),
            'fab_text_bbox_mm': union(fab_text),
            'silk_bbox_mm': union(silk),
            'pads_bbox_mm': union(pads),
            'checker_physical_envelope_mm': _physical_envelope(f),
            'pad_count': len(pads),
        }
        for key in ('courtyard_outer_bbox_mm', 'generic_graphics_bbox_mm',
                    'fab_shapes_bbox_mm', 'pads_bbox_mm'):
            row[key.replace('_bbox_mm', '_north_projection_mm')] = round(
                max(0, north_center - row[key][1]), 6) if row[key] else None
        rows[ref] = row
    for ref in ('J_PWR', *(f'J{n}' for n in range(1, 9))):
        row = rows[ref]
        if (row['courtyard_outer_north_projection_mm'] != 0.045 or
                row['fab_shapes_north_projection_mm'] != 0 or
                row['pads_north_projection_mm'] != 0):
            raise SystemExit(f'{ref}: edge classification drift')
    report = {'board_sha256': sha(BOARD), 'native_ref_count': len(fp),
              'edge_cuts_stroke_bbox_mm': edge_bbox,
              'edge_cuts_centerline_outline_bbox_mm': outline_bbox,
              'north_edge_centerline_y_mm': north_center,
              'manufacturer_pdf_sha256': {k: sha(p) for k, p in DOCS.items()},
              'connectors': rows, 'status': 'NOMINAL_COURTYARD_ONLY_OVERHANG_RESEARCH',
              'placement_modified': False, 'p1_accepted': False,
              'connector_full_accepted': False}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
