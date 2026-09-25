#!/usr/bin/env python3
"""Strict 20-ref input_buck partition attempt on disposable moved-edge board."""
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
BOUNDARY = PROJECT / '01_docs/research/2026-09-25-power-boundary-two-face-probe-sol'
sys.path.insert(0, str(ROOT / 'skills/kicad-pcb/scripts'))
sys.path.insert(0, str(BOUNDARY))
import p1_corridor_capacity as checker  # noqa: E402
import probe as boundary  # noqa: E402

INPUT_GROUPS = {
    'input_buck': {'C_IN1', 'C_IN2', 'C_IN_HF', 'C_OUT1', 'C_OUT3',
                   'C_VCC', 'C_VLDO', 'R_AGND_JOIN', 'R_BUCK_FB_BOTTOM',
                   'R_BUCK_FB_TOP', 'R_RT', 'U_BUCK'},
    'input_buck_jpwr': {'J_PWR'},
    'input_buck_front': {'D_IN', 'F_IN', 'Q_IN', 'R_QIN_G'},
    'input_buck_gate': {'D_QIN_GS'},
    'input_buck_cin3': {'C_IN3'},
    'input_buck_out2': {'C_OUT2'},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hull(boxes):
    boxes = list(boxes)
    return [min(box[0] for box in boxes), min(box[1] for box in boxes),
            max(box[2] for box in boxes), max(box[3] for box in boxes)]


def main():
    for path, expected in boundary.EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f'governed input drift: {path}')
    board = pcbnew.LoadBoard(str(boundary.BOARD))
    native = {fp.GetReference(): fp for fp in board.GetFootprints()}
    plan = json.loads((BASE / 'modular_plan.json').read_text())
    owners = {ref: block['id'] for block in plan['blocks'] for ref in block['refs']}
    if len(native) != 569 or set(native) != set(owners):
        raise SystemExit('569 owner denominator drift')
    all_input = {ref for ref, owner in owners.items() if owner == 'input_buck'}
    assigned = {ref for group in INPUT_GROUPS.values() for ref in group}
    if len(all_input) != 20 or assigned != all_input or sum(map(len, INPUT_GROUPS.values())) != 20:
        raise SystemExit('complete input_buck partition drift')
    counts = {net: sum(len(v) for v in iface['endpoints'].values())
              for iface in plan['interfaces'] for net in [iface['net']]
              if net in boundary.NETS}
    if counts != {'N1V8': 42, 'N3V3X': 27, 'N3V3_ADC': 68, 'N5V_BUCK': 34}:
        raise SystemExit('171 full power terminal denominator drift')

    # Disposable board mutation and matching source pose; original file untouched.
    ct = native['C_PWR_CT2']
    pos = ct.GetPosition()
    ct.SetPosition(pcbnew.VECTOR2I(pos.x, pos.y + pcbnew.FromMM(1.13)))
    floor = yaml.safe_load((BASE / 'floorplan.yaml').read_text())
    floor['placement']['post_anchors']['Q_PRE'] = [46, 107.15, 0]
    floor['placement']['post_anchors']['C_PWR_CT2'] = [53.2, 102.43, 0]
    groups = json.loads((PRIOR / 'result.json').read_text())['groups']
    groups['quiet_buck_edge']['bbox'] = [51.675, 101.655, 54.975, 104.515]
    source = yaml.safe_load((BASE / 'p1_requirements.yaml').read_text())
    regions, patterns, _ = boundary.partition(plan, source, floor, groups, 69, 100.5)
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise SystemExit('native outline unavailable')
    baseline_cells = checker._physical_cells(source, plan, board, outline, regions, patterns)
    if len(baseline_cells) != 19:
        raise SystemExit('13 quiet plus six established cells drift')
    envelopes = {ref: checker._physical_envelope(fp) for ref, fp in native.items()}
    group_for = {ref: name for name, refs in INPUT_GROUPS.items() for ref in refs}
    for name, refs in INPUT_GROUPS.items():
        regions[name] = hull(envelopes[ref] for ref in refs)
        source['physical_cells'].append({'id': name, 'owner_block': 'input_buck',
                                         'refs': sorted(refs), 'transit': False})
    split_patterns = []
    for pattern in patterns:
        buckets = {}
        for ref in pattern['match']:
            buckets.setdefault(group_for.get(ref, pattern.get('region')), []).append(ref)
        for name, refs in buckets.items():
            split_patterns.append(dict(pattern, match=refs, region=name))
    jpwr_box = regions['input_buck_jpwr']
    outline_box = list(checker.box_mm(outline.BBox()))
    if checker.lane_inside_outline(outline, jpwr_box):
        raise SystemExit('J_PWR complete native envelope unexpectedly on board')
    try:
        checker._physical_cells(source, plan, board, outline, regions, split_patterns)
    except checker.ContractError as exc:
        rejection = str(exc)
    else:
        raise SystemExit('complete partition unexpectedly passed')
    if rejection != 'input_buck_jpwr: physical cell off board outline':
        raise SystemExit(f'unexpected first structural conflict: {rejection}')
    result = {
        'status': 'INCOMPLETE', 'p1_accepted': False, 'routing_realized': False,
        'board_sha256': sha(boundary.BOARD),
        'checker_sha256': sha(ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'),
        'native_ref_count': len(native), 'quiet_power_ref_count': 69,
        'accepted_preexisting_cell_count_after_in_memory_move': len(baseline_cells),
        'full_power_terminal_counts': counts,
        'input_buck_partition_ref_count': len(assigned),
        'input_buck_groups': {name: {'refs': sorted(refs), 'bbox_mm': regions[name]}
                              for name, refs in INPUT_GROUPS.items()},
        'board_outline_bbox_mm': outline_box,
        'jpwr_full_native_envelope_mm': list(envelopes['J_PWR']),
        'jpwr_north_overhang_mm': round(outline_box[1] - jpwr_box[1], 6),
        'physical_cells_rejection': rejection,
        'branch_checks_run': False,
    }
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
