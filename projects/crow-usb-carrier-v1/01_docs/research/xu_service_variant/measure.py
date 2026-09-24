#!/usr/bin/env python3
"""Read-only XU/clock rectangle and service-face diagnostic, native KiCad 10.

python3 measure.py BOARD.kicad_pcb > measurement.json
"""
import hashlib
import json
from pathlib import Path
import sys

import pcbnew
import yaml

PROJECT = Path(__file__).resolve().parents[3]
EXPECTED = {
    '03_src/floorplan.yaml': 'a882f87682484c37c5766a9e37c5a0d93b38a8e5a775fb1ab4425011da40a275',
    '03_src/modular_plan.json': '7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e',
    '03_src/rules/p1_corridor_requirements.yaml': '9ef85e5f4918dea0378203a97fa631ce2e73a690170235902a97a6c8e30527d8',
}
BOARD_SHA = '60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17'
# Rectangles are [x0,y0,x1,y1], mm. Touching edges have zero overlap.
CELLS = {'xmos_core': [190, 84, 232, 114],
         'clock_flash_debug': [190, 114, 232, 136]}
FACES = {
    'qspi': {'owners': ['xmos_core', 'clock_flash_debug'],
             'segment': [[200, 114], [205, 114]], 'required_width_mm': 2.70,
             'reservation': [200, 111.9, 205, 117.9]},
    'jtag_reset': {'owners': ['xmos_core', 'board_integration'],
                   'segment': [[222, 84], [225, 84]], 'required_width_mm': 2.25,
                   'reservation': [222, 82, 225, 86]},
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def overlap(a, b):
    return max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))


def contained(a, b):
    return all((a[0] >= b[0], a[1] >= b[1], a[2] <= b[2], a[3] <= b[3]))


def rect(r):
    return [round(pcbnew.ToMM(v), 6) for v in (r.GetX(), r.GetY(), r.GetRight(), r.GetBottom())]


def native_envelope(fp):
    """Union full native footprint bounds with F.CrtYd, if present."""
    box = rect(fp.GetBoundingBox(False, False))
    courtyard = fp.GetCourtyard(pcbnew.F_CrtYd)
    if courtyard.OutlineCount():
        pts = [courtyard.COutline(i).CPoint(k)
               for i in range(courtyard.OutlineCount())
               for k in range(courtyard.COutline(i).PointCount())]
        xs = [round(pcbnew.ToMM(p.x), 6) for p in pts]
        ys = [round(pcbnew.ToMM(p.y), 6) for p in pts]
        box = [min(box[0], min(xs)), min(box[1], min(ys)),
               max(box[2], max(xs)), max(box[3], max(ys))]
    return box


def crosses_segment(box, line):
    (x0, y0), (x1, y1) = line
    if y0 == y1:
        return box[1] < y0 < box[3] and max(box[0], min(x0, x1)) < min(box[2], max(x0, x1))
    if x0 == x1:
        return box[0] < x0 < box[2] and max(box[1], min(y0, y1)) < min(box[3], max(y0, y1))
    raise ValueError('only orthogonal boundary segments supported')


def pos(p):
    return [round(pcbnew.ToMM(p.x), 6), round(pcbnew.ToMM(p.y), 6)]


def run(board_path):
    actual = {name: digest(PROJECT / name) for name in EXPECTED}
    if actual != EXPECTED:
        raise ValueError(f'source hash mismatch: {actual}')
    if digest(board_path) != BOARD_SHA:
        raise ValueError('native board SHA mismatch')
    floor = yaml.safe_load((PROJECT / '03_src/floorplan.yaml').read_text())
    req = yaml.safe_load((PROJECT / '03_src/rules/p1_corridor_requirements.yaml').read_text())
    board = pcbnew.LoadBoard(str(board_path))
    if board is None:
        raise ValueError('native board failed to load')
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    source_keepouts = {x['name']: x['rect'] for x in floor.get('keepouts', [])}
    native_rule_areas = [z for z in board.Zones() if z.GetIsRuleArea()]
    outline = floor['board']['outline']
    outer = [outline['x0'], outline['y0'], outline['x1'], outline['y1']]
    regions = dict(floor['placement']['regions'])
    other = {name: box for name, box in regions.items() if name not in CELLS}
    cell_intersections = []
    for name, box in CELLS.items():
        if not contained(box, outer):
            cell_intersections.append({'cell': name, 'with': 'outline'})
        for other_name, other_box in other.items():
            if overlap(box, other_box):
                cell_intersections.append({'cell': name, 'with': other_name,
                                           'area_mm2': round(overlap(box, other_box), 6)})
    if overlap(*CELLS.values()):
        cell_intersections.append({'cell': 'xmos_core', 'with': 'clock_flash_debug'})
    boundaries = {
        'xmos_north': [[190, 84], [232, 84]],
        'xmos_west': [[190, 84], [190, 114]],
        'xmos_clock': [[190, 114], [232, 114]],
        'clock_west': [[190, 114], [190, 136]],
        'clock_south': [[190, 136], [232, 136]],
    }
    boundary_hits = {}
    for name, line in boundaries.items():
        body_hits = []
        pad_hits = []
        for ref, fp in fps.items():
            if crosses_segment(native_envelope(fp), line):
                body_hits.append(ref)
            for pad in fp.Pads():
                if crosses_segment(rect(pad.GetBoundingBox()), line):
                    pad_hits.append(f'{ref}.{pad.GetNumber()}')
        boundary_hits[name] = {'segment': line, 'native_footprint_hits': sorted(body_hits),
                               'native_pad_hits': sorted(pad_hits),
                               'source_keepout_hits': sorted(name for name, box in source_keepouts.items()
                                                             if crosses_segment(box, line))}
    assigned = {}
    for group in floor['placement']['patterns']:
        name = group.get('region')
        if name in CELLS:
            for ref in group['match']:
                if ref in assigned:
                    raise ValueError(f'duplicate assignment {ref}')
                assigned[ref] = name
    footprints = []
    for ref in sorted(assigned):
        fp = fps.get(ref)
        if fp is None:
            footprints.append({'ref': ref, 'owner': assigned[ref], 'missing': True})
            continue
        box = native_envelope(fp)
        footprints.append({'ref': ref, 'owner': assigned[ref], 'bbox_mm': box,
                           'inside_owner': contained(box, CELLS[assigned[ref]]),
                           'crosses_boundary_y114': box[1] < 114 < box[3]})
    face_results = {}
    for name, spec in FACES.items():
        box = spec['reservation']
        hits = []
        pad_hits = []
        for ref, fp in fps.items():
            if overlap(native_envelope(fp), box):
                hits.append(ref)
            for pad in fp.Pads():
                if overlap(rect(pad.GetBoundingBox()), box):
                    pad_hits.append(f'{ref}.{pad.GetNumber()}')
        foreign = [region for region, region_box in other.items() if overlap(box, region_box)]
        zone_hits = []
        for z in native_rule_areas:
            if overlap(rect(z.GetBoundingBox()), box):
                zone_hits.append(z.GetZoneName())
        s = spec['segment']
        length = ((s[1][0]-s[0][0])**2 + (s[1][1]-s[0][1])**2)**0.5
        face_results[name] = {**spec, 'measured_width_mm': length,
                              'width_margin_mm': round(length-spec['required_width_mm'], 6),
                              'inside_outline': contained(box, outer),
                              'native_footprint_hits': sorted(set(hits)),
                              'native_pad_hits': sorted(set(pad_hits)),
                              'foreign_source_region_hits': sorted(foreign),
                              'source_keepout_hits': sorted(name for name, keepout in source_keepouts.items()
                                                            if overlap(keepout, box)),
                              'native_rule_area_hits': sorted(zone_hits)}
    alloc = next(x for x in req['allocations'] if x['id'] == 'xmos_service_escape')
    fixed = set(req['p1_fixed_refs'])
    net_class = {n: d['id'] for d in alloc['demands'] for n in d['nets']}
    endpoints = []
    for net, owners in alloc['endpoints'].items():
        for owner, names in owners.items():
            for name in names:
                ref, number = name.rsplit('.', 1)
                fp = fps.get(ref)
                pads = [p for p in fp.Pads() if p.GetNumber() == number] if fp else []
                endpoints.append({'net': net, 'source_owner': owner, 'ref_pad': name,
                                  'native_pads': [{'net': p.GetNetname(), 'center_mm': pos(p.GetPosition())}
                                                  for p in pads],
                                  'fixed_p1': ref in fixed,
                                  'p2_pad_to_face': 'P2_REQUIRED' if ref not in fixed else 'fixed endpoint',
                                  'p2_local_return': 'P2_REQUIRED' if ref not in fixed else 'fixed endpoint',
                                  'proposed_face': net_class.get(net, 'crystal unmeasured')})
    fixed_native = {ref: native_envelope(fps[ref]) for ref in sorted(fixed) if ref in fps}
    fixed_missing = sorted(fixed - fixed_native.keys())
    fixed_hits = {name: sorted(ref for ref, box in fixed_native.items()
                               if overlap(box, spec['reservation'])) for name, spec in FACES.items()}
    return {'schema': 'crow-xu-service-ownership-variant-v1',
            'status': 'INCOMPLETE_RESEARCH', 'source_commit': '9c73181c432b51558003a8be7e496cc8c6757d5a',
            'source_sha256': actual, 'board_sha256': BOARD_SHA, 'pcbnew_version': pcbnew.Version(),
            'variant': 'two disjoint rectangles with exclusive measured faces',
            'outline_mm': outer, 'cells_mm': CELLS, 'cell_intersections': cell_intersections,
            'source_keepouts_mm': source_keepouts,
            'native_rule_area_count': len(native_rule_areas),
            'boundaries': boundary_hits,
            'assigned_native_footprints': footprints, 'faces': face_results,
            'p1_fixed_ref_count': len(fixed), 'p1_fixed_native_missing': fixed_missing,
            'p1_fixed_reservation_hits': fixed_hits, 'endpoints': endpoints,
            'limits': ['native board is source-derived evidence, not a fresh variant regeneration',
                       'reservations are diagnostic windows, not source-owned floorplan regions',
                       'current source and generated board contain no rule areas; preservation under a later rule-area addition is unproven',
                       'pad-to-face routes, return continuity and local crystal window remain P2_REQUIRED',
                       'north JTAG continuation crosses unallocated/USB frontend territory and is not proved']}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    print(json.dumps(run(Path(sys.argv[1])), indent=2, sort_keys=True))
