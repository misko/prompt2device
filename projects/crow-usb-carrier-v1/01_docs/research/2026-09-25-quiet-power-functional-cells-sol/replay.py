#!/usr/bin/env python3
"""Disposable all-member quiet-power physical-cell partition probe."""
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
BOARD = PROJECT / '01_docs/research/2026-09-25-ti-cin3-qpre-owner-repair-sol/candidate.kicad_pcb'
sys.path.insert(0, str(ROOT / 'skills/kicad-pcb/scripts'))
import p1_corridor_capacity as checker  # noqa: E402

EXPECTED = {
    BOARD: 'e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef',
    BASE / 'p1_requirements.yaml': 'f6f132891712bfcb1cec4d1df6714748337040ba5c42ae3fecd14fb9c35d1222',
    BASE / 'floorplan.yaml': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    BASE / 'modular_plan.json': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
}
NETS = ('N1V8', 'N3V3X', 'N3V3_ADC', 'N5V_BUCK')
REMOTE_XU = {'C_XU_VDDIO_35.1', 'C_XU_VDDIO_56.1', 'C_XU_USB33.1'}
PWR = {'U_PWR', 'R_PWR_TOP', 'R_PWR_BOT', 'R_PWR_PU', 'C_PWR', 'C_PWR_CT'}
LDO = {'U_LDO', 'C_LDO_OUT_1', 'C_LDO_OUT_2', 'C_LDO_IN', 'C_LDO_NR4',
       'C_LDO_NR5', 'R_LDO_ILIM', 'R_LDO_PG_TOP', 'R_LDO_SET'}
PRE_SWITCH = {'Q_PRE'}
PRE_RESISTOR = {'R_PRE'}
PRE_GATE = {'R_PRE_G'}
PRE_DRIVER = {'Q_PRE_EN', 'Q_DUMP'}
HOLD_SWITCH = {'D_HOLD', 'R_DUMP'}
BUCK_EDGE = {'C_PWR_CT2', 'R_DUMP_PD'}


def hull(boxes):
    boxes = list(boxes)
    return [min(box[0] for box in boxes), min(box[1] for box in boxes),
            max(box[2] for box in boxes), max(box[3] for box in boxes)]


def branch(net, interfaces, aliases, pads, regions, cells, group_for):
    item = next(row for row in interfaces['interfaces'] if row['net'] == net)
    endpoint_rows = sorted((source_pad, checker.graph.native_identity(source_pad, aliases),
                            net, block)
                           for block, names in item['endpoints'].items()
                           for source_pad in names)
    ident = f'power_{net.lower()}_unplaced_tree'
    entries = []
    blockers = []
    for source_pad, native_pad, _, block in endpoint_rows:
        entry = {'source_pad': source_pad, 'native_pad': native_pad,
                 'net': net, 'block': block}
        if native_pad in REMOTE_XU:
            entry['physical_cell_id'] = 'xmos_core_east'
        if block == 'quiet_power' and group_for[entry['native_pad'].rsplit('.', 1)[0]] != 'quiet_power':
            entry['physical_cell_id'] = group_for[entry['native_pad'].rsplit('.', 1)[0]]
        entries.append(entry)
        cell_id = entry.get('physical_cell_id')
        foreign = sorted(name for name, area in regions.items()
                         if name not in (block, cell_id) and
                         not (name in cells and cells[name]['owner_block'] == block) and
                         checker.intersects(checker.box_mm(pads[native_pad][0].GetBoundingBox()), area))
        if foreign:
            blockers.append({'source_pad': source_pad, 'native_pad': native_pad,
                             'block': block, 'foreign_regions': foreign})
    p2 = [{'status': 'P2_REQUIRED', 'source_pad': s, 'native_pad': n,
           'net': net, 'block': block, 'branch_id': ident, 'layer': 'F.Cu',
           'proof': 'native_pad_to_unplaced_tree'} for s, n, _, block in endpoint_rows]
    return {'id': ident, 'owner': 'board_integration',
            'allocation_id': 'power_boundary_windows', 'net': net,
            'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
            'reservation_id': f'power_{net.lower()}_unresolved_tree',
            'endpoints': entries, 'terminal_count': len(entries),
            'minimum_tree_edges': len(entries) - 1,
            'physical_blockers': blockers, 'p2_obligations': p2,
            'tree_obligation': {'status': 'P3_REQUIRED', 'net': net,
                                'terminal_count': len(entries),
                                'minimum_tree_edges': len(entries) - 1,
                                'proof': 'one_connected_native_net_without_unrelated_branches'},
            'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                  'branch_id': ident, 'reference_layer': 'In1.Cu',
                                  'proof': 'continuous_filled_reference_under_actual_tree'}}


def main():
    for path, digest in EXPECTED.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit(f'input drift: {path}')
    board = pcbnew.LoadBoard(str(BOARD))
    refs = {fp.GetReference(): fp for fp in board.GetFootprints()}
    plan = json.loads((BASE / 'modular_plan.json').read_text())
    owners = {ref: block['id'] for block in plan['blocks'] for ref in block['refs']}
    if len(refs) != 569 or set(refs) != set(owners):
        raise SystemExit('569 native owner denominator drift')
    source = yaml.safe_load((BASE / 'p1_requirements.yaml').read_text())
    floor = yaml.safe_load((BASE / 'floorplan.yaml').read_text())
    floor['placement']['post_anchors']['Q_PRE'] = [46.0, 107.15, 0]
    regions = floor['placement']['regions']
    envelopes = {ref: checker._physical_envelope(fp) for ref, fp in refs.items()}
    quiet = {ref for ref, owner in owners.items() if owner == 'quiet_power'}
    if len(quiet) != 69:
        raise SystemExit('69 quiet-power owner denominator drift')
    fixed_groups = [PWR, LDO, PRE_SWITCH, PRE_RESISTOR, PRE_GATE,
                    PRE_DRIVER, HOLD_SWITCH, BUCK_EDGE]
    if any(not group <= quiet for group in fixed_groups) or len(set.union(*fixed_groups)) != sum(map(len, fixed_groups)):
        raise SystemExit('named functional group ownership/uniqueness drift')
    groups = {'quiet_power': set(PWR), 'quiet_ldo': set(LDO),
              'quiet_pre_switch': set(PRE_SWITCH),
              'quiet_pre_resistor': set(PRE_RESISTOR),
              'quiet_pre_gate': set(PRE_GATE),
              'quiet_pre_driver': set(PRE_DRIVER),
              'quiet_hold_switch': set(HOLD_SWITCH),
              'quiet_buck_edge': set(BUCK_EDGE),
              'hold_bank_left': {f'C_HOLD{i}' for i in range(1, 9)} | {'C_PWR_CT3', 'R_OPA_BLEED1'},
              'hold_bank_right': {f'C_HOLD{i}' for i in range(9, 17)}}
    assigned = set.union(*groups.values())
    remainder = quiet - assigned
    for ref in sorted(remainder):
        box = envelopes[ref]
        if box[2] < 38:
            name = 'quiet_audio_control'
        elif box[0] < 58:
            name = 'quiet_pre_support'
        elif box[1] < 100:
            name = 'quiet_dump_timing'
        else:
            name = 'quiet_mid_control'
        groups.setdefault(name, set()).add(ref)
    if set.union(*groups.values()) != quiet or sum(len(group) for group in groups.values()) != 69:
        raise SystemExit('functional partition is not exact 69/69')
    regions['adc_reference'] = hull(envelopes[ref] for ref, owner in owners.items()
                                    if owner == 'adc_reference')
    # This deliberately narrows the broad input region to a plausible local
    # footprint area.  Branch validation below exposes endpoints it excludes.
    regions['input_buck'] = [25, 84, 58, 100.5]
    for name, members in groups.items():
        regions[name] = hull(envelopes[ref] for ref in members)
    # Preserve every non-quiet pattern and each quiet model override, while
    # binding each quiet footprint to its proposed physical cell.
    group_for = {ref: name for name, members in groups.items() for ref in members}
    patterns = []
    for pattern in floor['placement']['patterns']:
        buckets = {}
        for ref in pattern['match']:
            buckets.setdefault(group_for.get(ref, pattern.get('region')), []).append(ref)
        for name, names in buckets.items():
            row = dict(pattern, match=names)
            if name is not None:
                row['region'] = name
            patterns.append(row)
    floor['placement']['patterns'] = patterns
    rows = list(source['physical_cells']) + [
        {'id': name, 'owner_block': 'quiet_power', 'refs': sorted(members),
         'transit': False} for name, members in groups.items()]
    source['physical_cells'] = rows
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise SystemExit('native outline unavailable')
    try:
        candidate_cells = checker._physical_cells(source, plan, board, outline, regions, patterns)
    except checker.ContractError as exc:
        physical_result = {'accepted': False, 'reason': str(exc)}
    else:
        physical_result = {'accepted': True, 'reason': None}
    # Use the proposed cells only if _physical_cells admitted the complete
    # partition; otherwise retain the six previously validated baseline cells.
    baseline_regions = yaml.safe_load((BASE / 'floorplan.yaml').read_text())['placement']['regions']
    baseline_cells = checker._physical_cells(
        yaml.safe_load((BASE / 'p1_requirements.yaml').read_text()), plan,
        board, outline, baseline_regions,
        yaml.safe_load((BASE / 'floorplan.yaml').read_text())['placement']['patterns'])
    branch_cells = candidate_cells if physical_result['accepted'] else baseline_cells
    _, pads = checker.graph.board_index(board)
    aliases = checker.graph.alias_inventory(yaml.safe_load(
        (PROJECT / '02_parts/USB4215-03-A/part.yaml').read_text()))
    coverage, _ = checker.graph.source_inventory(source, plan)
    power = {}
    untagged_quiet_endpoints = []
    tagged_quiet_endpoints = []
    for net in NETS:
        row = branch(net, plan, aliases, pads, regions, branch_cells, group_for)
        for entry in row['endpoints']:
            if entry['block'] == 'quiet_power' and 'physical_cell_id' not in entry:
                untagged_quiet_endpoints.append({'net': net, 'native_pad': entry['native_pad']})
            if entry['block'] == 'quiet_power' and 'physical_cell_id' in entry:
                tagged_quiet_endpoints.append({'net': net, 'native_pad': entry['native_pad'],
                                               'physical_cell_id': entry['physical_cell_id']})
        try:
            checker._unresolved_branches(
                {'unresolved_multiterminal_branches': [row]}, plan, board,
                regions, coverage, aliases, pads, branch_cells, patterns)
        except checker.ContractError as exc:
            power[net] = {'accepted': False, 'reason': str(exc),
                          'terminal_count': row['terminal_count']}
        else:
            power[net] = {'accepted': True, 'reason': None,
                          'terminal_count': row['terminal_count']}
    q_box, i_box = envelopes['Q_PRE'], envelopes['C_IN3']
    if checker.intersects(q_box, i_box):
        raise SystemExit('reviewed Q_PRE move lost native envelope clearance')
    qpre_gap = round(q_box[1] - i_box[3], 6)
    primary_hull = hull(checker.box_mm(pads[entry['native_pad']][0].GetBoundingBox())
                        for entry in untagged_quiet_endpoints)
    primary_foreign = sorted(ref for ref, box in envelopes.items()
                             if owners[ref] != 'quiet_power' and
                             checker.intersects(primary_hull, box))
    if len(untagged_quiet_endpoints) != 1 or len(tagged_quiet_endpoints) != 10:
        raise SystemExit('complete quiet-power branch tagging drift')
    result = {
        'status': 'FAIL', 'p1_accepted': False, 'board_sha256': EXPECTED[BOARD],
        'native_ref_count': 569, 'quiet_power_ref_count': 69,
        'groups': {name: {'refs': sorted(members), 'bbox': regions[name]}
                   for name, members in groups.items()},
        'physical_cells': physical_result,
        'complete_quiet_power_branch_tags': {
            'tagged': sorted(tagged_quiet_endpoints,
                             key=lambda entry: (entry['net'], entry['native_pad'])),
            'untagged_quiet_power_endpoints': sorted(
                untagged_quiet_endpoints, key=lambda entry: (entry['net'], entry['native_pad'])),
            'minimum_primary_pad_hull_mm': primary_hull,
            'foreign_native_envelope_refs': primary_foreign,
            'foreign_native_envelope_count': len(primary_foreign)},
        'reviewed_qpre_cin3_clearance': {
            'quiet_ref': 'Q_PRE', 'quiet_bbox': list(q_box),
            'input_ref': 'C_IN3', 'input_bbox': list(i_box),
            'y_gap_mm': qpre_gap},
        'power_branches': power,
    }
    if (not physical_result['accepted'] or
            any(not power[net]['accepted'] for net in ('N1V8', 'N3V3X')) or
            power['N3V3_ADC']['reason'] != 'U_AFE2.8: branch pad outside source owner region' or
            power['N5V_BUCK']['reason'] != 'U_BUCK.10: branch pad outside source owner region'):
        raise SystemExit('refined partition/branch outcome drift')
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'physical_cells': physical_result, 'power_branches': power,
                      'complete_quiet_power_branch_tags': result['complete_quiet_power_branch_tags'],
                      'qpre_cin3_clearance': result['reviewed_qpre_cin3_clearance']}, indent=2))


if __name__ == '__main__':
    main()
