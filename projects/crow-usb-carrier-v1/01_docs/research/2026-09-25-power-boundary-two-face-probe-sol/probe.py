#!/usr/bin/env python3
"""Bounded native replay of two power branch owner-region boundary moves."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BASE = PROJECT / '01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol'
PRIOR = PROJECT / '01_docs/research/2026-09-25-quiet-power-functional-cells-sol'
BOARD = PROJECT / '01_docs/research/2026-09-25-ti-cin3-qpre-owner-repair-sol/candidate.kicad_pcb'
sys.path.insert(0, str(ROOT / 'skills/kicad-pcb/scripts'))
sys.path.insert(0, str(PRIOR))
import p1_corridor_capacity as checker  # noqa: E402
import replay as prior  # noqa: E402

EXPECTED = {
    BOARD: 'e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef',
    BASE / 'p1_requirements.yaml': 'f6f132891712bfcb1cec4d1df6714748337040ba5c42ae3fecd14fb9c35d1222',
    BASE / 'floorplan.yaml': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    BASE / 'modular_plan.json': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
}
NETS = prior.NETS


def partition(plan, source, floor, groups, analog_xmax, input_ymax):
    regions = floor['placement']['regions']
    regions['adc_reference'] = [90.455, 87.505, 142.275, 112.255]
    regions['analog_ch2'][2] = analog_xmax
    regions['input_buck'] = [25, 84, 58, input_ymax]
    for name, row in groups.items():
        regions[name] = row['bbox']
    group_for = {ref: name for name, row in groups.items() for ref in row['refs']}
    if len(group_for) != 69 or any(not row['refs'] for row in groups.values()):
        raise SystemExit('69-member occupied cell denominator drift')
    patterns = []
    for pattern in floor['placement']['patterns']:
        buckets = {}
        for ref in pattern['match']:
            buckets.setdefault(group_for.get(ref, pattern.get('region')), []).append(ref)
        for region, names in buckets.items():
            row = dict(pattern, match=names)
            if region is not None:
                row['region'] = region
            patterns.append(row)
    source['physical_cells'] = list(source['physical_cells']) + [
        {'id': name, 'owner_block': 'quiet_power', 'refs': row['refs'],
         'transit': False} for name, row in groups.items()]
    return regions, patterns, group_for


def main():
    for path, digest in EXPECTED.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit(f'input SHA drift: {path}')
    board = pcbnew.LoadBoard(str(BOARD))
    refs = {fp.GetReference(): fp for fp in board.GetFootprints()}
    plan = json.loads((BASE / 'modular_plan.json').read_text())
    owners = {ref: block['id'] for block in plan['blocks'] for ref in block['refs']}
    if len(refs) != 569 or set(refs) != set(owners):
        raise SystemExit('569 native owner denominator drift')
    previous = json.loads((PRIOR / 'result.json').read_text())
    groups = previous['groups']
    if not previous['physical_cells']['accepted'] or sum(len(row['refs']) for row in groups.values()) != 69:
        raise SystemExit('prior 13-cell authority drift')
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise SystemExit('native outline unavailable')
    _, pads = checker.graph.board_index(board)
    aliases = checker.graph.alias_inventory(yaml.safe_load(
        (PROJECT / '02_parts/USB4215-03-A/part.yaml').read_text()))
    attempts = {}
    for label, analog_xmax, input_ymax in (
            ('baseline_cells', 69, 100.5),
            ('analog_ch2_only', 69.25, 100.5),
            ('both_boundaries', 69.25, 100.7)):
        source = yaml.safe_load((BASE / 'p1_requirements.yaml').read_text())
        floor = yaml.safe_load((BASE / 'floorplan.yaml').read_text())
        floor['placement']['post_anchors']['Q_PRE'] = [46.0, 107.15, 0]
        regions, patterns, group_for = partition(
            plan, source, floor, groups, analog_xmax, input_ymax)
        try:
            cells = checker._physical_cells(source, plan, board, outline, regions, patterns)
        except checker.ContractError as exc:
            attempts[label] = {'physical_cells': {'accepted': False, 'reason': str(exc)},
                               'power_branches': None}
            continue
        coverage, _ = checker.graph.source_inventory(source, plan)
        branches = {}
        for net in NETS:
            row = prior.branch(net, plan, aliases, pads, regions, cells, group_for)
            if row['terminal_count'] != {'N1V8': 42, 'N3V3X': 27,
                                        'N3V3_ADC': 68, 'N5V_BUCK': 34}[net]:
                raise SystemExit(f'{net}: full terminal denominator drift')
            try:
                checker._unresolved_branches(
                    {'unresolved_multiterminal_branches': [row]}, plan, board,
                    regions, coverage, aliases, pads, cells, patterns)
            except checker.ContractError as exc:
                branches[net] = {'accepted': False, 'reason': str(exc),
                                 'terminal_count': row['terminal_count']}
            else:
                branches[net] = {'accepted': True, 'reason': None,
                                 'terminal_count': row['terminal_count']}
        attempts[label] = {'physical_cells': {'accepted': True, 'reason': None},
                           'power_branches': branches}
    if (not attempts['baseline_cells']['physical_cells']['accepted'] or
            not attempts['analog_ch2_only']['physical_cells']['accepted'] or
            attempts['both_boundaries']['physical_cells']['reason'] !=
            'quiet_buck_edge: physical cell overlaps foreign region input_buck'):
        raise SystemExit('bounded boundary conflict drift')
    input_box = [25, 84, 58, 100.7]
    edge_box = groups['quiet_buck_edge']['bbox']
    overlap = [max(input_box[0], edge_box[0]), max(input_box[1], edge_box[1]),
               min(input_box[2], edge_box[2]), min(input_box[3], edge_box[3])]
    result = {
        'status': 'INCOMPLETE', 'p1_accepted': False, 'routing_realized': False,
        'board_sha256': EXPECTED[BOARD], 'native_ref_count': 569,
        'quiet_power_ref_count': 69, 'cell_count': len(groups),
        'boundary_deltas_mm': {'analog_ch2_xmax': [69, 69.25],
                               'input_buck_ymax': [100.5, 100.7]},
        'input_buck_quiet_buck_edge_overlap_mm': overlap,
        'attempts': attempts,
    }
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
