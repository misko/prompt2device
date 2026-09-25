#!/usr/bin/env python3
"""One bounded source-region and buck-edge move study; no canonical writes."""
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

CORE = {'C_IN1', 'C_IN2', 'C_IN_HF', 'C_OUT1', 'C_OUT3', 'C_VCC',
        'C_VLDO', 'R_AGND_JOIN', 'R_BUCK_FB_BOTTOM', 'R_BUCK_FB_TOP',
        'R_RT', 'U_BUCK'}
MOVE_Y_MM = 1.13  # 0.01 mm above the exact rectangular touch at +1.12 mm


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox(pad):
    return list(checker.box_mm(pad.GetBoundingBox()))


def main():
    for path, expected in boundary.EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f'input SHA drift: {path}')
    plan = json.loads((BASE / 'modular_plan.json').read_text())
    owner = {ref: block['id'] for block in plan['blocks'] for ref in block['refs']}
    board = pcbnew.LoadBoard(str(boundary.BOARD))
    refs = {fp.GetReference(): fp for fp in board.GetFootprints()}
    if len(refs) != 569 or set(refs) != set(owner):
        raise SystemExit('569 native owner denominator drift')
    floor = yaml.safe_load((BASE / 'floorplan.yaml').read_text())
    floor['placement']['post_anchors']['Q_PRE'] = [46, 107.15, 0]
    source = yaml.safe_load((BASE / 'p1_requirements.yaml').read_text())
    groups = json.loads((PRIOR / 'result.json').read_text())['groups']
    regions, patterns, _ = boundary.partition(plan, source, floor, groups, 69, 100.5)
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise SystemExit('native outline unavailable')
    if len(checker._physical_cells(source, plan, board, outline, regions, patterns)) != 19:
        raise SystemExit('13 quiet plus six established cells drift')

    # Full U_AFE2/3 bodies plus courtyards dictate x=69.545 and 91.545.
    envelope = {ref: checker._physical_envelope(fp) for ref, fp in refs.items()}
    region_deltas = {'analog_ch2': ('right', envelope['U_AFE2'][2]),
                     'analog_ch3': ('left_right', (envelope['U_AFE2'][2], envelope['U_AFE3'][2])),
                     'analog_ch4': ('left', envelope['U_AFE3'][2])}
    recut = {name: list(box) for name, box in regions.items()}
    recut['analog_ch2'][2] = envelope['U_AFE2'][2]
    recut['analog_ch3'][0], recut['analog_ch3'][2] = envelope['U_AFE2'][2], envelope['U_AFE3'][2]
    recut['analog_ch4'][0] = envelope['U_AFE3'][2]
    pad_audit = {}
    for name in ('analog_ch3', 'analog_ch4'):
        all_pads = sorted((
            {'native_pad': ref + '.' + pad.GetNumber(), 'bbox_mm': bbox(pad)}
            for ref, fp in refs.items() if owner[ref] == name for pad in fp.Pads()
            if pad.GetNumber()),
            key=lambda row: row['native_pad'])
        left_crossers = [row for row in all_pads
                        if row['bbox_mm'][0] < recut[name][0]
                        and row['bbox_mm'][2] > regions[name][0]
                        and row['bbox_mm'][1] < recut[name][3]
                        and row['bbox_mm'][3] > recut[name][1]]
        lost_overlap = [row['native_pad'] for row in left_crossers
                        if checker.intersects(regions[name], row['bbox_mm'])
                        and not checker.intersects(recut[name], row['bbox_mm'])]
        existing = [row for row in all_pads
                    if not checker.contains(regions[name], row['bbox_mm'])]
        pad_audit[name] = {'left_edge_crossers': left_crossers,
                           'lost_region_overlap': lost_overlap,
                           'preexisting_outside_count': len(existing),
                           'preexisting_outside_pads': [row['native_pad'] for row in existing]}
        if not left_crossers or not lost_overlap:
            raise SystemExit(f'{name}: expected recut edge conflict drift')

    # Test the smallest y-only buck-edge relocation in a disposable in-memory
    # board. The native netlist and all other footprint poses stay untouched.
    c = refs['C_PWR_CT2']
    pos = c.GetPosition()
    c.SetPosition(pcbnew.VECTOR2I(pos.x, pos.y + pcbnew.FromMM(MOVE_Y_MM)))
    floor['placement']['post_anchors']['C_PWR_CT2'] = [53.2, 102.43, 0]
    moved_envelope = checker._physical_envelope(c)
    if moved_envelope[1] <= 101.645:
        raise SystemExit('buck-edge move did not clear core hull')
    groups['quiet_buck_edge']['bbox'] = [51.675, moved_envelope[1], 54.975, 104.515]
    shifted_source = yaml.safe_load((BASE / 'p1_requirements.yaml').read_text())
    shifted_regions, shifted_patterns, _ = boundary.partition(
        plan, shifted_source, floor, groups, 69, 100.5)
    shifted_cells = checker._physical_cells(
        shifted_source, plan, board, outline, shifted_regions, shifted_patterns)
    if len(shifted_cells) != 19:
        raise SystemExit('relocated 13-cell quiet partition drift')
    core_box = [40.155, 84.205, 53.795, 101.645]
    foreign = sorted(ref for ref, fp in refs.items() if ref not in CORE and
                     (checker.intersects(core_box, checker._physical_envelope(fp)) or
                      any(checker.intersects(core_box, bbox(p)) for p in fp.Pads())))
    if foreign:
        raise SystemExit(f'input_buck_core intersects foreign native refs: {foreign}')
    shifted_source['physical_cells'].append(
        {'id': 'input_buck_core', 'owner_block': 'input_buck',
         'refs': sorted(CORE), 'transit': False})
    shifted_regions['input_buck_core'] = core_box
    core_patterns = []
    for pattern in shifted_patterns:
        inside = [ref for ref in pattern['match'] if ref in CORE]
        outside = [ref for ref in pattern['match'] if ref not in CORE]
        if inside:
            core_patterns.append(dict(pattern, match=inside, region='input_buck_core'))
        if outside:
            core_patterns.append(dict(pattern, match=outside))
    try:
        checker._physical_cells(shifted_source, plan, board, outline,
                                shifted_regions, core_patterns)
    except checker.ContractError as exc:
        core_failure = str(exc)
    else:
        raise SystemExit('partial input_buck cell unexpectedly accepted')
    if core_failure != 'input_buck: physical cell ref denominator incomplete':
        raise SystemExit(f'unexpected next structural conflict: {core_failure}')
    remaining = sorted(ref for ref, native_owner in owner.items()
                       if native_owner == 'input_buck' and ref not in CORE)
    if len(remaining) != 8:
        raise SystemExit('input_buck remainder denominator drift')
    counts = {net: sum(len(v) for v in iface['endpoints'].values())
              for iface in plan['interfaces'] for net in [iface['net']]
              if net in boundary.NETS}
    if counts != {'N1V8': 42, 'N3V3X': 27, 'N3V3_ADC': 68, 'N5V_BUCK': 34}:
        raise SystemExit('171-terminal denominator drift')
    result = {
        'status': 'INCOMPLETE', 'p1_accepted': False, 'routing_realized': False,
        'board_sha256': sha(boundary.BOARD),
        'checker_sha256': sha(ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'),
        'full_power_terminal_counts': counts,
        'channel_recut_mm': {k: {'old': regions[k], 'proposed': recut[k]}
                             for k in region_deltas},
        'channel_pad_audit': pad_audit,
        'buck_move': {'ref': 'C_PWR_CT2', 'delta_mm': [0, MOVE_Y_MM],
                      'new_envelope_mm': list(moved_envelope),
                      'quiet_cells_accepted': len(shifted_cells),
                      'candidate_core_refs': sorted(CORE),
                      'candidate_core_bbox_mm': core_box,
                      'core_foreign_native_intersections': foreign,
                      'input_buck_unassigned_refs': remaining,
                      'core_checker_failure': core_failure}}
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
