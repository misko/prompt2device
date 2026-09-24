#!/usr/bin/env python3
"""Geometry-only native JTAG escape probe for the pinned QSPI-gap board.

This deliberately does not edit the board.  It buffers candidate F.Cu
centre-lines by half the trace width and native foreign copper/body boxes by
the requested clearance, then reports every positive-area intersection.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pcbnew

BOARD = Path('/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb')
EXPECTED = 'fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27'
OUT = Path(__file__).with_name('jtag_native_dogleg_probe_terra.json')
WIDTH = CLEARANCE = 0.15
STRIP = [221.0, 65.0, 226.0, 84.0]


def box(item):
    b = item.GetBoundingBox()
    return [b.GetLeft() / 1e6, b.GetTop() / 1e6, b.GetRight() / 1e6, b.GetBottom() / 1e6]


def courtyard(fp):
    b = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    return [b.GetLeft() / 1e6, b.GetTop() / 1e6, b.GetRight() / 1e6, b.GetBottom() / 1e6]


def inflate(b, n=CLEARANCE):
    return [b[0] - n, b[1] - n, b[2] + n, b[3] + n]


def overlap(a, b):
    """Strict-positive-area intersection, with its overlap bbox if present."""
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    return ([x0, y0, x1, y1] if x1 > x0 + 1e-9 and y1 > y0 + 1e-9 else None)


def segment_box(a, b):
    h = WIDTH / 2
    return [min(a[0], b[0]) - h, min(a[1], b[1]) - h,
            max(a[0], b[0]) + h, max(a[1], b[1]) + h]


def route_boxes(points):
    if any(a[0] != b[0] and a[1] != b[1] for a, b in zip(points, points[1:])):
        raise ValueError('only Manhattan segments are admissible')
    return [segment_box(a, b) for a, b in zip(points, points[1:])]


def transformed_pad_box(b):
    """180-degree transform about the fixed (228, 50) connector centre."""
    return [456 - b[2], 100 - b[3], 456 - b[0], 100 - b[1]]


def screen(name, routes, source_pads, pad_boxes, body_boxes, courtyard_boxes, track_boxes, rule_boxes):
    rows, all_segments = [], []
    for net, points in routes.items():
        segments = route_boxes(points)
        all_segments.extend((net, s) for s in segments)
        hits = {'foreign_pads': [], 'foreign_bodies': [], 'foreign_courtyards': [],
                'existing_f_copper': [], 'rule_areas': []}
        for seg_i, s in enumerate(segments):
            for label, b in pad_boxes.items():
                if label != source_pads[net] and overlap(s, inflate(b)):
                    hits['foreign_pads'].append({'segment': seg_i, 'object': label,
                                                  'overlap_mm': overlap(s, inflate(b))})
            for label, b in body_boxes.items():
                if label != 'J_JTAG' and overlap(s, inflate(b)):
                    hits['foreign_bodies'].append({'segment': seg_i, 'object': label,
                                                    'overlap_mm': overlap(s, inflate(b))})
            for label, b in courtyard_boxes.items():
                if label != 'J_JTAG' and overlap(s, inflate(b)):
                    hits['foreign_courtyards'].append({'segment': seg_i, 'object': label,
                                                        'overlap_mm': overlap(s, inflate(b))})
            for label, b in track_boxes.items():
                if overlap(s, inflate(b)):
                    hits['existing_f_copper'].append({'segment': seg_i, 'object': label,
                                                       'overlap_mm': overlap(s, inflate(b))})
            for label, b in rule_boxes.items():
                if overlap(s, inflate(b)):
                    hits['rule_areas'].append({'segment': seg_i, 'object': label,
                                               'overlap_mm': overlap(s, inflate(b))})
        rows.append({'net': net, 'source_pad': source_pads[net], 'points_mm': points,
                     'segment_envelopes_mm': segments, 'hits': hits,
                     'clear_of_foreign_native_geometry': not any(hits.values())})
    # Different nets must have trace-edge clearance >= CLEARANCE.  Consecutive
    # segments on one net are intentionally allowed to overlap at their joint.
    pair_hits = []
    for i, (net_a, a) in enumerate(all_segments):
        for net_b, b in all_segments[i + 1:]:
            if net_a == net_b:
                continue
            hit = overlap(a, inflate(b))
            if hit:
                pair_hits.append({'a': net_a, 'b': net_b, 'overlap_mm': hit})
    return {'name': name, 'routes': rows, 'simultaneous_interroute_clear': not pair_hits,
            'interroute_hits': pair_hits,
            'all_routes_clear': not pair_hits and all(r['clear_of_foreign_native_geometry'] for r in rows)}


def main():
    if hashlib.sha256(BOARD.read_bytes()).hexdigest() != EXPECTED:
        raise SystemExit('pinned board hash mismatch')
    board = pcbnew.LoadBoard(str(BOARD))
    jtag = next(fp for fp in board.GetFootprints() if fp.GetReference() == 'J_JTAG')
    pads = {f'{fp.GetReference()}.{p.GetNumber()}': box(p)
            for fp in board.GetFootprints() for p in fp.Pads()
            if p.IsOnLayer(board.GetLayerID('F.Cu'))}
    bodies = {fp.GetReference(): box(fp) for fp in board.GetFootprints()
              if fp.GetLayerName() == 'F.Cu'}
    courtyards = {}
    for fp in board.GetFootprints():
        try:
            c = courtyard(fp)
        except Exception:
            continue
        if c[2] > c[0] and c[3] > c[1]:
            courtyards[fp.GetReference()] = c
    tracks = {f'track_{i}': box(t) for i, t in enumerate(board.GetTracks())
              if t.IsOnLayer(board.GetLayerID('F.Cu'))}
    rules = {f'rule_area_{i}': box(z) for i, z in enumerate(board.Zones())
             if z.GetIsRuleArea() and z.GetLayerSet().Contains(board.GetLayerID('F.Cu'))}

    # Current 90-degree pose: TMS leaves directly to the east.  TDI, TDO and
    # TCK use three 0.30-mm-pitch lanes in the 1.28-mm inter-row gap, then
    # escape around either end of the header before entering the source strip.
    current = {
        'JTAG_TMS': [(230.91, 47.965), (231.135, 47.965), (231.135, 54.80), (225.40, 54.80), (225.40, 65.0)],
        'JTAG_TCK': [(229.27, 49.36), (229.27, 50.20), (224.85, 50.20), (224.85, 54.20), (222.60, 54.20), (222.60, 65.0)],
        'JTAG_TDO': [(228.00, 49.36), (228.00, 49.90), (224.55, 49.90), (224.55, 53.90), (222.00, 53.90), (222.00, 65.0)],
        'JTAG_TDI': [(226.73, 49.36), (226.73, 49.60), (224.25, 49.60), (224.25, 53.60), (221.70, 53.60), (221.70, 65.0)],
    }
    current_sources = {'JTAG_TMS': 'J_JTAG.2', 'JTAG_TCK': 'J_JTAG.4',
                       'JTAG_TDO': 'J_JTAG.6', 'JTAG_TDI': 'J_JTAG.8'}

    # Proposed fixed-pose backtrack: 90 -> 270 degrees at the same centre.
    # Rotate the native pad geometry and use the given even-pad signal mapping.
    rotated_pads = dict(pads)
    for n in range(1, 11):
        rotated_pads[f'J_JTAG.{n}'] = transformed_pad_box(pads[f'J_JTAG.{n}'])
    variant_sources = {'JTAG_TMS': 'J_JTAG.2', 'JTAG_TCK': 'J_JTAG.4',
                       'JTAG_TDO': 'J_JTAG.6', 'JTAG_TDI': 'J_JTAG.8'}
    variant = {net: [((rotated_pads[pad][0] + rotated_pads[pad][2]) / 2, rotated_pads[pad][3]),
                     ((rotated_pads[pad][0] + rotated_pads[pad][2]) / 2, 65.0)]
               for net, pad in variant_sources.items()}

    report = {
        'status': 'GEOMETRY_PASS_WITH_ORIGIN_COURTYARD_ESCAPE_EXCEPTION',
        'scope': 'RESEARCH_ONLY_NO_PCB_EDIT_NO_P1_OR_P2_CLAIM',
        'board_sha256': EXPECTED, 'trace_width_mm': WIDTH, 'clearance_mm': CLEARANCE,
        'source_owned_strip_mm': STRIP, 'fixed_pose_current_deg': 90,
        'origin_jtag_courtyard_mm': courtyard(jtag),
        'origin_courtyard_note': 'Every pad starts inside this courtyard; a literal no-origin-courtyard-crossing rule makes any surface escape impossible. Foreign courtyards are screened normally.',
        'current_pose_doglegs': screen('current_pose_90deg', current, current_sources, pads, bodies, courtyards, tracks, rules),
        'rotated_pose_directs': screen('candidate_pose_270deg', variant, variant_sources, rotated_pads, bodies, courtyards, tracks, rules),
        'rotated_pose': {'centre_mm': [228.0, 50.0], 'orientation_deg': 270,
                         'strip_required_for_direct_routes_mm': [221.0, 65.0, 231.0, 84.0],
                         'even_signal_pad_boxes_mm': {p: rotated_pads[p] for p in ['J_JTAG.2', 'J_JTAG.4', 'J_JTAG.6', 'J_JTAG.8']}},
        'limits': ['bbox clearance screen; it does not run KiCad DRC', 'no connector mating/service/assembly result',
                   'no filled-reference, impedance, return, source-ownership, P2 or P1 acceptance result',
                   'rotation is a virtual coordinate transform; the pinned board itself remains at 90 degrees'],
    }
    if not report['current_pose_doglegs']['all_routes_clear']:
        raise SystemExit('current dogleg witness unexpectedly collides')
    if not report['rotated_pose_directs']['all_routes_clear']:
        raise SystemExit('rotated direct witness unexpectedly collides')
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k]['all_routes_clear'] for k in ('current_pose_doglegs', 'rotated_pose_directs')}, indent=2))


if __name__ == '__main__':
    main()
