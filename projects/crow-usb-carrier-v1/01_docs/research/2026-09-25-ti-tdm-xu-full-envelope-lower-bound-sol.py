#!/usr/bin/env python3
"""Bounded full-footprint TDM/XU corridor lower bound; research only."""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
PACKET = PROJECT / '06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
BOARD = PACKET / '04_kicad/crow_carrier.kicad_pcb'
RULES = PACKET / '03_src/rules/p1_corridor_requirements.yaml'
FLOOR = PACKET / '03_src/floorplan.yaml'
EXPECTED_BOARD = '8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10'
EXPECTED_RULES = '191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3'
EXPECTED_FLOOR = '0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868'
LANES = ([182.475, 94, 199.825, 100], [182.475, 93.6, 199.825, 100])
ENDPOINT_FOOTPRINTS = {'U_TDM_XLATE', 'U_XU'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for path, expected in ((BOARD, EXPECTED_BOARD), (RULES, EXPECTED_RULES),
                           (FLOOR, EXPECTED_FLOOR)):
        if sha(path) != expected:
            raise SystemExit(f'exact TI packet mismatch: {path}')
    source = yaml.safe_load(RULES.read_text())
    fixed = set(source['p1_fixed_refs'])
    if len(fixed) != 27:
        raise SystemExit('P1 fixed-ref denominator changed')
    regions = yaml.safe_load(FLOOR.read_text())['placement']['regions']
    for name in ('analog_ch7', 'analog_ch8'):
        if regions[name][3] != 84:
            raise SystemExit('analog 7/8 north boundary changed')
    script = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
    spec = importlib.util.spec_from_file_location('p1_capacity', script)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    board = pcbnew.LoadBoard(str(BOARD))
    poses = {fp.GetReference(): [round(pcbnew.ToMM(fp.GetPosition().x), 6),
                                 round(pcbnew.ToMM(fp.GetPosition().y), 6),
                                 round(fp.GetOrientationDegrees(), 6)]
             for fp in board.GetFootprints()}
    if not fixed <= set(poses):
        raise SystemExit('fixed ref missing on board')
    # Native full footprint includes body, pads, silkscreen and ref/value text.
    # Endpoint footprints are exempt only in this trunk: pad-access pockets
    # require their own proof, and are not credited here.
    obstacles = [(fp.GetReference(), helper.box_mm(fp.GetBoundingBox(True, True)))
                 for fp in board.GetFootprints()
                 if fp.GetLayerName() == 'F.Cu' and fp.GetReference() not in ENDPOINT_FOOTPRINTS]
    cases = []
    for lane in LANES:
        if lane[1] <= regions['analog_ch7'][3] or lane[1] <= regions['analog_ch8'][3]:
            raise SystemExit('lane touches ch7/8 analog region')
        relevant = sorted({ref for ref, bbox in obstacles if helper.intersects(lane, bbox)})
        relevant_boxes = {ref: bbox for ref, bbox in obstacles if ref in relevant}
        removable = sorted(set(relevant) - fixed)
        base = helper.connected_capacity(lane, obstacles, 'horizontal', .45)
        by_count = []
        first_witnesses = []
        for count in range(len(removable) + 1):
            passes = []
            for combo in itertools.combinations(removable, count):
                removed = set(combo)
                measured = helper.connected_capacity(
                    lane, [(ref, bbox) for ref, bbox in obstacles if ref not in removed],
                    'horizontal', .45)
                if measured['capacity_slots'] >= 4:
                    passes.append({'refs': list(combo),
                                   'connected_width_mm': measured['connected_width_mm'],
                                   'slots': measured['capacity_slots']})
            by_count.append({'removed_count': count, 'tested': len(list(itertools.combinations(removable, count))),
                             'four_slot_combinations': len(passes)})
            if passes:
                first_witnesses = passes
                break
        cases.append({'lane_mm': lane, 'pitch_mm': .45, 'demand_slots': 4,
                      'baseline_connected_width_mm': base['connected_width_mm'],
                      'baseline_slots': base['capacity_slots'],
                      'relevant_full_footprints': relevant,
                      'relevant_full_bboxes_mm': relevant_boxes,
                      'optimistic_removal_sweep': by_count,
                      'minimum_removed_count': by_count[-1]['removed_count'],
                      'first_relaxed_witnesses': first_witnesses})
    if any(row['minimum_removed_count'] != 3 for row in cases):
        raise SystemExit('expected bounded three-ref lower bound changed')
    report = {'schema': 1, 'kind': 'ti-tdm-xu-full-envelope-lower-bound',
              'status': 'INCOMPLETE', 'p1_accepted': False, 'routing_realized': False,
              'hashes': {'board': sha(BOARD), 'rules': sha(RULES),
                         'floorplan': sha(FLOOR), 'capacity_helper': sha(script)},
              'fixed_ref_count': len(fixed),
              'fixed_ref_poses': {ref: poses[ref] for ref in sorted(fixed)},
              'endpoint_trunk_exemptions': sorted(ENDPOINT_FOOTPRINTS),
              'analog_exclusion_regions': {key: regions[key] for key in ('analog_ch7', 'analog_ch8')},
              'cases': cases,
              'limitation': 'Footprint removal is an optimistic relaxation, not a legal relocation. '
                            'This proves only that zero, one or two moved non-endpoint refs cannot '
                            'open either specified full-envelope rectangle while other poses stay fixed.'}
    output = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(output)
    else:
        print(output, end='')


if __name__ == '__main__':
    main()
