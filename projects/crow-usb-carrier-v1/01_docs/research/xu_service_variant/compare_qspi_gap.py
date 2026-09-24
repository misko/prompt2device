#!/usr/bin/env python3
"""Read-only, hash-pinned comparison of rectangle board and QSPI gap board.

python3 compare_qspi_gap.py RECT_PROJECT GAP_PROJECT > qspi_gap.json
"""
import json
from pathlib import Path
import sys

import pcbnew
import yaml
from compare_regenerated import box, board_data, envelope, inside, mm, overlap, pads, pose, sha

RECT_SOURCE_SHA = '01aa2aa9fa6b264510e568236a265fefb36494b275de081a99b62229c8be3de8'
GAP_SOURCE_SHA = 'cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925'
RECT_BOARD_SHA = 'c3b9d2885e1f475aad4744185eaa7258359a0d340e864e56418da5f61a0d3a6b'
GAP_BOARD_SHA = 'fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27'
NETLIST_SHA = 'e7ef7dbd752b9431ade0933ca77ee998963bfe3871c3caf65cddc56442f1371d'
GENERATOR_SHA = '8a5fa1d48d80138458601a097ab6260565841510a498e44cb9c5773652215b3c'
PROJECT = Path(__file__).resolve().parents[3]
NEW_REGIONS = {'xmos_core': [190, 84, 232, 110.5],
               'clock_flash_debug': [190, 118.5, 232, 136],
               'board_integration_qspi': [199.8, 110.5, 223.2, 118.5]}
QSPI_FACE = [[200, 110.5], [205, 110.5]]
DIAGNOSTIC_WINDOW = [200, 111.9, 205, 117.9]


def pin(path, want):
    got = sha(path)
    if got != want:
        raise ValueError(f'SHA-256 mismatch {path}: {got} != {want}')
    return got


def zones(board):
    return sorted([{'net': z.GetNetname(), 'layer': board.GetLayerName(z.GetLayer()),
                    'rule_area': bool(z.GetIsRuleArea()), 'bbox_mm': box(z.GetBoundingBox())}
                   for z in board.Zones()], key=lambda x: (x['net'], x['layer'], x['bbox_mm']))


def run(rect_project, gap_project):
    paths = {
        'rect_source': rect_project/'03_src/floorplan.yaml',
        'gap_source': gap_project/'03_src/floorplan.yaml',
        'rect_board': rect_project/'04_kicad/crow_carrier.kicad_pcb',
        'gap_board': gap_project/'04_kicad/crow_carrier.kicad_pcb',
        'netlist': gap_project/'06_build/netlists/crow_carrier.net',
        'generator': PROJECT.parents[1]/'skills/kicad-pcb/scripts/generate_board_generic.py',
    }
    shas = {key: pin(paths[key], want) for key, want in [
        ('rect_source', RECT_SOURCE_SHA), ('gap_source', GAP_SOURCE_SHA),
        ('rect_board', RECT_BOARD_SHA), ('gap_board', GAP_BOARD_SHA),
        ('netlist', NETLIST_SHA), ('generator', GENERATOR_SHA)]}
    old = yaml.safe_load(paths['rect_source'].read_text())
    new = yaml.safe_load(paths['gap_source'].read_text())
    for name, region in NEW_REGIONS.items():
        if new['placement']['regions'].get(name) != region:
            raise ValueError(f'region {name} differs')
        old['placement']['regions'][name] = region
    if old != new:
        raise ValueError('source mutation extends beyond the two cells and QSPI region')
    outline = new['board']['outline']
    board_box = [outline['x0'], outline['y0'], outline['x1'], outline['y1']]
    all_regions = new['placement']['regions']
    region_overlaps = [{'a': a, 'b': b, 'area_mm2': overlap(ra, rb)}
                       for a, ra in all_regions.items() for b, rb in all_regions.items()
                       if a < b and (a in NEW_REGIONS or b in NEW_REGIONS) and overlap(ra, rb)]
    region_outside = [name for name, region in NEW_REGIONS.items() if not inside(region, board_box)]
    b0, f0 = board_data(paths['rect_board'])
    b1, f1 = board_data(paths['gap_board'])
    if f0.keys() != f1.keys():
        raise ValueError('footprint refs differ')
    moved = [{'ref': ref, 'before': pose(f0[ref]), 'after': pose(f1[ref])}
             for ref in sorted(f0) if pose(f0[ref]) != pose(f1[ref])]
    identity_changes = [ref for ref in sorted(f0) if pads(f0[ref], False) != pads(f1[ref], False)]
    pad_position_changes = [ref for ref in sorted(f0) if pads(f0[ref], True) != pads(f1[ref], True)]
    req = yaml.safe_load((PROJECT/'03_src/rules/p1_corridor_requirements.yaml').read_text())
    fixed = set(req['p1_fixed_refs'])
    assigned = {ref: row['region'] for row in new['placement']['patterns']
                if row.get('region') in ('xmos_core', 'clock_flash_debug') for ref in row['match']}
    assigned_outside = [{'ref': ref, 'owner': owner, 'envelope_mm': envelope(f1[ref])}
                        for ref, owner in sorted(assigned.items())
                        if not inside(envelope(f1[ref]), NEW_REGIONS[owner])]
    corridor = NEW_REGIONS['board_integration_qspi']
    corridor_hits = [ref for ref, fp in sorted(f1.items()) if overlap(envelope(fp), corridor)]
    pad_hits = [f'{ref}.{p.GetNumber()}' for ref, fp in sorted(f1.items()) for p in fp.Pads()
                if overlap(box(p.GetBoundingBox()), corridor)]
    centerline_span = QSPI_FACE[1][0] - QSPI_FACE[0][0]
    assigned_below = [envelope(f1[ref])[3] for ref, owner in assigned.items() if owner == 'xmos_core']
    assigned_above = [envelope(f1[ref])[1] for ref, owner in assigned.items() if owner == 'clock_flash_debug']
    return {'schema': 'crow-xu-qspi-gap-regeneration-v1', 'status': 'INCOMPLETE_RESEARCH',
            'sha256': shas, 'pcbnew_version': pcbnew.Version(), 'regions_mm': NEW_REGIONS,
            'region_overlaps': region_overlaps, 'regions_outside_outline': region_outside,
            'diagnostic_window_fits_corridor': inside(DIAGNOSTIC_WINDOW, corridor),
            'qspi_face': {'segment_mm': QSPI_FACE, 'raw_width_mm': centerline_span,
                          'required_width_mm': 2.70, 'raw_margin_mm': round(centerline_span-2.70, 6),
                          'claim': 'raw vacant face only; no per-net capacity or pad-to-face proof'},
            'corridor_native_footprint_hits': corridor_hits,
            'corridor_native_pad_hits': sorted(pad_hits),
            'nearest_xu_envelope_to_corridor_mm': round(corridor[1]-max(assigned_below), 6),
            'nearest_clock_envelope_to_corridor_mm': round(min(assigned_above)-corridor[3], 6),
            'baseline': {'footprints': len(f0), 'pads': sum(len(list(f.Pads())) for f in f0.values()),
                         'zones': zones(b0)},
            'gap_variant': {'footprints': len(f1), 'pads': sum(len(list(f.Pads())) for f in f1.values()),
                            'zones': zones(b1)},
            'moved_footprints': moved, 'pad_identity_changed_refs': identity_changes,
            'pad_position_changed_refs': pad_position_changes,
            'p1_fixed_count': len(fixed),
            'p1_fixed_moved_refs': sorted(fixed & {m['ref'] for m in moved}),
            'assigned_footprint_count': len(assigned), 'assigned_outside_owner': assigned_outside,
            'rule_area_count': sum(z['rule_area'] for z in zones(b1)),
            'limits': ['region is source-declared geometry; no P1 schema-2 handoff/capacity contract or native reservation exists',
                       'F.Cu pad-to-face access and filled-reference return remain P2_REQUIRED',
                       'JTAG north continuation through usb_frontend remains unowned',
                       'zero native rule areas prevents preservation check']}


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    print(json.dumps(run(Path(sys.argv[1]), Path(sys.argv[2])), indent=2, sort_keys=True))
