#!/usr/bin/env python3
"""Read-only native-envelope screen for two quiet_power branch endpoints."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import pcbnew
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BOARD = PROJECT / '01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb'
FLOOR = PROJECT / '01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol/floorplan.yaml'
EXPECTED_BOARD = 'd0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7'
EXPECTED_FLOOR = '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0'
sys.path.insert(0, str(ROOT / 'skills/kicad-pcb/scripts'))
from p1_corridor_capacity import _physical_envelope  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xy(point):
    return [pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)]


def pad(fp, number):
    hits = [p for p in fp.Pads() if p.GetNumber() == number]
    if len(hits) != 1:
        raise ValueError(f'{fp.GetReference()}.{number}: expected one native pad')
    p = hits[0]
    return {'center': xy(p.GetPosition()), 'net': p.GetNetname()}


def gap(a, b):
    return round(math.hypot(max(a[0]-b[2], b[0]-a[2], 0),
                            max(a[1]-b[3], b[1]-a[3], 0)), 3)


def overlap(a, b):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    return [x0, y0, x1, y1] if x1 > x0 and y1 > y0 else None


def main():
    if sha(BOARD) != EXPECTED_BOARD or sha(FLOOR) != EXPECTED_FLOOR:
        raise SystemExit('exact TI board/floorplan hash drift')
    board = pcbnew.LoadBoard(str(BOARD))
    floor = yaml.safe_load(FLOOR.read_text())
    quiet = floor['placement']['regions']['quiet_power']
    adc = floor['placement']['regions']['adc_reference']
    assert quiet == [25, 105, 75, 134] and adc == [75, 85, 145, 134]
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    envelopes = {ref: _physical_envelope(fp) for ref, fp in fps.items()}
    related = {
        'C_LDO_OUT_1': ['U_LDO', 'C_LDO_IN', 'C_LDO_OUT_2', 'R_LDO_PG_TOP', 'C_LDO_NR4'],
        'R_PWR_TOP': ['R_PWR_BOT', 'U_PWR', 'C_PWR', 'R_PWR_PU', 'C_PWR_CT'],
    }
    related_pads = {
        'C_LDO_OUT_1': [('1', 'U_LDO', '9'), ('1', 'U_LDO', '10'),
                        ('1', 'C_LDO_OUT_2', '1'), ('2', 'U_LDO', '11')],
        'R_PWR_TOP': [('2', 'U_PWR', '1'), ('2', 'R_PWR_BOT', '1')],
    }
    targets = {}
    for ref, neighbors in related.items():
        box = envelopes[ref]
        targets[ref] = {
            'native_envelope_mm': box,
            'foreign_adc_reference_overlap_mm': overlap(box, adc),
            'native_pads': {p.GetNumber(): pad(fps[ref], p.GetNumber()) for p in fps[ref].Pads()},
            'nearby_envelope_gaps_mm': {n: gap(box, envelopes[n]) for n in neighbors},
            'related_pad_distances_mm': [
                {'from': f'{ref}.{own}', 'to': f'{other}.{pin}',
                 'from_net': pad(fps[ref], own)['net'],
                 'to_net': pad(fps[other], pin)['net'],
                 'center_distance_mm': round(math.dist(pad(fps[ref], own)['center'],
                                                       pad(fps[other], pin)['center']), 3)}
                for own, other, pin in related_pads[ref]
            ],
            'minimum_axis_shift_to_contain_in_quiet_power_mm': [
                round(quiet[0]-box[0] if box[0] < quiet[0] else quiet[2]-box[2] if box[2] > quiet[2] else 0, 3),
                round(quiet[1]-box[1] if box[1] < quiet[1] else quiet[3]-box[3] if box[3] > quiet[3] else 0, 3),
            ],
        }
    # Only test the smallest axis-aligned C_LDO_OUT_1 relocation. Stop at its first hard conflict.
    dx, dy = targets['C_LDO_OUT_1']['minimum_axis_shift_to_contain_in_quiet_power_mm']
    box = envelopes['C_LDO_OUT_1']
    moved = [round(box[0]+dx, 3), round(box[1]+dy, 3),
             round(box[2]+dx, 3), round(box[3]+dy, 3)]
    conflicts = [(ref, overlap(moved, env)) for ref, env in sorted(envelopes.items())
                 if ref != 'C_LDO_OUT_1' and overlap(moved, env)]
    if not conflicts:
        raise SystemExit('expected first hard native-envelope conflict absent')
    result = {
        'status': 'HARD_CONFLICT_RESEARCH_ONLY',
        'board_sha256': sha(BOARD), 'floorplan_sha256': sha(FLOOR),
        'native_ref_count': len(fps), 'quiet_power_region_mm': quiet,
        'adc_reference_region_mm': adc, 'targets': targets,
        'first_minimum_move': {'ref': 'C_LDO_OUT_1', 'shift_mm': [dx, dy],
                               'projected_envelope_mm': moved,
                               'first_native_conflict': {'ref': conflicts[0][0],
                                                         'intersection_mm': conflicts[0][1]}},
        'p1_accepted': False, 'placement_modified': False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
