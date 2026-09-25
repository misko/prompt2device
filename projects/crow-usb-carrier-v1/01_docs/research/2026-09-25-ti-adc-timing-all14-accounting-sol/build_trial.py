#!/usr/bin/env python3
"""Exact TI ADC timing source-denominator trial; research only."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import copy
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    import sys
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BASE = PROJECT / '01_docs/research/2026-09-25-ti-usb-two-physical-vbus-branch-sol'
BOARD = PROJECT / '06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/crow_carrier.kicad_pcb'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED = {
    'board': '8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10',
    'source': 'be824e24fc0b0e165cd9ca2d1623dddaac40ce72ce2dc9775b675c498ad1e385',
    'contract': '69d4f615a845f5eb1f4ad765614a7c6b1c8fbe98f172cb925cdbbca06ff179ca',
    'floorplan': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    'interfaces': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
    'checker': '2cdd5a2dc58680409391f89f8619a564c2de0b591aa27618d665dfe9a1797e8e',
}
NETS = ('ADC_BCLK', 'ADC_FSYNC', 'ADC_DOUT1', 'AUDIO_MCLK_1V8',
        'TDM_BCLK_1V8', 'TDM_DATA_1V8', 'TDM_FSYNC_1V8', 'ADC_I2C_SCL',
        'ADC_I2C_SDA', 'ADC_READY', 'AUDIO_EN', 'XU_I2C_SCL_1V8',
        'XU_I2C_SDA_1V8', 'ADC_DIGITAL_BAD')
TWO_TERMINAL = {'AUDIO_MCLK_1V8', 'TDM_BCLK_1V8', 'TDM_DATA_1V8', 'TDM_FSYNC_1V8'}
OUTSIDE_OWNER = {'AUDIO_EN'}
BRANCH_NETS = set(NETS) - TWO_TERMINAL - OUTSIDE_OWNER


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branch_for(item):
    net = item['net']
    ident = 'timing_' + net.lower() + '_unplaced_tree'
    reservation = 'timing_' + net.lower() + '_tree'
    entries = item['endpoints']
    obligations = [{'status': 'P2_REQUIRED', **entry, 'branch_id': ident,
                    'layer': 'F.Cu', 'proof': 'native_pad_to_unplaced_tree'}
                   for entry in entries]
    branch = {'id': ident, 'owner': 'board_integration',
              'allocation_id': 'adc_timing_xmos_bundle', 'net': net,
              'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
              'reservation_id': reservation, 'endpoints': entries,
              'terminal_count': len(entries),
              'minimum_tree_edges': len(entries) - 1,
              'physical_blockers': item['foreign_regions'],
              'capacity_slots': None, 'p2_obligations': obligations,
              'tree_obligation': {'status': 'P3_REQUIRED', 'net': net,
                                  'terminal_count': len(entries),
                                  'minimum_tree_edges': len(entries) - 1,
                                  'proof': 'one_connected_native_net_without_unrelated_branches'},
              'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                    'branch_id': ident, 'reference_layer': 'In1.Cu',
                                    'proof': 'continuous_filled_reference_under_actual_tree'}}
    return ident, reservation, branch, obligations


def main():
    inputs = {'board': BOARD, 'source': BASE / 'p1_requirements.yaml',
              'contract': BASE / 'coarse.json', 'floorplan': BASE / 'floorplan.yaml',
              'interfaces': BASE / 'modular_plan.json', 'aliases': ALIASES,
              'checker': CHECKER}
    for name, path in inputs.items():
        if sha(path) != EXPECTED[name]:
            raise SystemExit(f'{name} input SHA drift')
    spec = importlib.util.spec_from_file_location('ti_timing_checker', CHECKER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = yaml.safe_load(inputs['source'].read_text())
    contract = json.loads(inputs['contract'].read_text())
    floor = yaml.safe_load(inputs['floorplan'].read_text())
    interfaces = json.loads(inputs['interfaces'].read_text())
    alias_map = helper.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    board = pcbnew.LoadBoard(str(BOARD))
    _, pads = helper.graph.board_index(board)
    regions = floor['placement']['regions']
    alloc_src = next(row for row in source['allocations']
                     if row['id'] == 'adc_timing_xmos_bundle')
    alloc = next(row for row in contract['allocations']
                 if row['id'] == 'adc_timing_xmos_bundle')
    if alloc_src['coverage_nets'] != list(NETS) or alloc['coverage_nets'] != list(NETS):
        raise SystemExit('14-net order/coverage drift')
    by_net = {row['net']: row for row in interfaces['interfaces'] if row['net'] in NETS}
    if set(by_net) != set(NETS):
        raise SystemExit('interface net denominator drift')
    ledger = []
    total = 0
    for net in NETS:
        if alloc_src['endpoints'][net] != by_net[net]['endpoints']:
            raise SystemExit(f'{net}: source interface owner/member drift')
        entries = sorted((s, helper.graph.native_identity(s, alias_map), net, owner)
                         for owner, names in by_net[net]['endpoints'].items() for s in names)
        native = []
        outside = []
        foreign = []
        for source_pad, native_pad, _, owner in entries:
            found = pads.get(native_pad, [])
            if len(found) != 1 or found[0].GetNetname() != net or not found[0].IsOnLayer(pcbnew.F_Cu):
                raise SystemExit(f'{source_pad}: exact F.Cu pad/net mismatch')
            box = helper.box_mm(found[0].GetBoundingBox())
            native.append(native_pad)
            if not helper.contains(regions[owner], box):
                outside.append({'source_pad': source_pad, 'native_pad': native_pad,
                                'owner': owner, 'pad_bbox_mm': box,
                                'owner_region_mm': regions[owner]})
            neighbors = sorted(name for name, value in regions.items()
                               if name != owner and helper.intersects(box, value))
            if neighbors:
                foreign.append({'source_pad': source_pad, 'native_pad': native_pad,
                                'block': owner, 'foreign_regions': neighbors})
        native_on_net = [fp.GetReference() + '.' + pad.GetNumber()
                         for fp in board.GetFootprints() for pad in fp.Pads()
                         if pad.GetNetname() == net]
        if len(native_on_net) != len(native) or set(native_on_net) != set(native):
            raise SystemExit(f'{net}: undeclared native endpoint')
        total += len(entries)
        ledger.append({'net': net, 'terminal_count': len(entries),
                       'endpoints': [{'source_pad': s, 'native_pad': n,
                                      'net': net, 'block': owner}
                                     for s, n, _, owner in entries],
                       'outside_owner': outside, 'foreign_regions': foreign,
                       'accounting': 'schema_branch' if net in BRANCH_NETS else
                                     'schema_gap_outside_owner' if net in OUTSIDE_OWNER else
                                     'schema_gap_two_terminal',
                       'capacity_slots': None,
                       'p2_debt': 'native_pad_to_unplaced_tree_and_filled_In1_Cu_return',
                       'p3_debt': 'one_connected_native_net_without_unrelated_branches'})
    if total != 54 or sum(row['terminal_count'] for row in ledger if row['net'] in BRANCH_NETS) != 35:
        raise SystemExit('54/35 endpoint denominator drift')
    # Remove all 14 old ordinary geometry/capacity claims. Nine nets receive
    # exact branch rows below; the other five stay explicitly unrepresentable
    # under this schema rather than receiving false scalar capacity credit.
    old_witnesses = alloc['boundary_witnesses']
    if len(old_witnesses) != 14 or {row['net'] for row in old_witnesses} != set(NETS):
        raise SystemExit('legacy timing witness denominator drift')
    alloc['boundary_witnesses'] = []
    alloc['reservations'] = []
    branch_ids = []
    for item in ledger:
        net = item['net']
        if net not in BRANCH_NETS:
            continue
        ident, reservation, branch, obligations = branch_for(item)
        entries = item['endpoints']
        source['unresolved_multiterminal_branches'].append(branch)
        rep = entries[0]
        box = helper.box_mm(pads[rep['native_pad']][0].GetBoundingBox())
        alloc['boundary_witnesses'].append({
            'kind': 'unresolved_multiterminal_branch', 'branch_id': ident,
            'source': rep['source_pad'], 'native': rep['native_pad'],
            'net': net, 'block': rep['block'], 'layer': 'F.Cu',
            'face': 'north', 'boundary_bbox': list(box),
            'reservation_id': reservation, 'p2_obligation': obligations[0]})
        alloc['reservations'].append({'id': reservation,
                                      'kind': 'unresolved_multiterminal_branch',
                                      'branch_id': ident, 'layer': 'F.Cu',
                                      'nets': [net]})
        branch_ids.append(ident)
    source_file = HERE / 'p1_requirements.yaml'
    floor_file = HERE / 'floorplan.yaml'
    interface_file = HERE / 'modular_plan.json'
    contract_file = HERE / 'coarse.json'
    source_file.write_text(yaml.safe_dump(source, sort_keys=False))
    floor_file.write_bytes(inputs['floorplan'].read_bytes())
    interface_file.write_bytes(inputs['interfaces'].read_bytes())
    contract['source_sha256'] = sha(source_file)
    contract['floorplan_sha256'] = sha(floor_file)
    contract_file.write_text(json.dumps(contract, indent=2) + '\n')
    # Validate exact nine branch rows independently; full packet may still
    # fail because the other five nets lack an honest source schema.
    coverage, _ = helper.graph.source_inventory(source, interfaces)
    branches = helper._unresolved_branches(source, interfaces, board, regions,
                                           coverage, alias_map, pads)
    if not set(branch_ids) <= set(branches):
        raise SystemExit('nine exact timing branches not accepted')
    red_checks = {}
    for item in ledger:
        if item['net'] in BRANCH_NETS:
            continue
        damaged = copy.deepcopy(source)
        damaged['unresolved_multiterminal_branches'].append(branch_for(item)[2])
        try:
            helper._unresolved_branches(damaged, interfaces, board, regions,
                                        coverage, alias_map, pads)
        except helper.ContractError as exc:
            red_checks[item['net']] = str(exc)
        else:
            raise SystemExit(f"{item['net']}: unsupported branch was accepted")
    if len(red_checks) != 5 or any('exact branch endpoint denominator mismatch' not in red_checks[n]
                                   for n in TWO_TERMINAL) or \
            'branch pad outside source owner region' not in red_checks['AUDIO_EN']:
        raise SystemExit('five schema-gap red checks changed')
    (HERE / 'endpoint_ledger.json').write_text(json.dumps({
        'schema': 1, 'status': 'INCOMPLETE', 'p1_accepted': False,
        'board_sha256': sha(BOARD), 'net_count': 14, 'endpoint_count': 54,
        'branchable_net_count': 9, 'branchable_endpoint_count': 35,
        'schema_gap_red_checks': red_checks,
        'nets': ledger}, indent=2, sort_keys=True) + '\n')
    result = helper.evaluate_coarse(
        BOARD, contract_file, sha(contract_file), source_path=source_file,
        interface_path=interface_file, alias_path=ALIASES, floorplan_path=floor_file,
        expected_source_sha256=sha(source_file),
        expected_interface_sha256=sha(interface_file),
        expected_alias_sha256=sha(ALIASES), expected_floorplan_sha256=sha(floor_file),
        diagnose_all=True)
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    timing = [row for row in result['diagnostics']
              if row.get('allocation') == 'adc_timing_xmos_bundle']
    usb = [row for row in result['diagnostics']
           if row.get('allocation') == 'usb_device_pair']
    timing_allocation = next(row for row in result['allocations']
                             if row['id'] == 'adc_timing_xmos_bundle')
    if (result['status'] != 'FAIL' or result['p1_accepted'] or timing or usb or
            timing_allocation.get('reason') !=
            'adc_timing_xmos_bundle: missing per-net boundary witness' or
            len(result['errors']) != 9 or
            any('unresolved branch representative witness denominator mismatch' not in error
                for error in result['errors']) or
            len(alloc['reservations']) != 9 or
            any(row['kind'] != 'unresolved_multiterminal_branch' or 'bbox' in row
                for row in alloc['reservations'])):
        raise SystemExit('expected fail-closed all-14 schema boundary drift')
    print(json.dumps({'status': result['status'], 'errors': result['errors'],
                      'timing_diagnostics': timing,
                      'timing_reason': timing_allocation.get('reason'),
                      'accepted_branch_count': len(branch_ids),
                      'source_sha256': sha(source_file),
                      'contract_sha256': sha(contract_file)}, indent=2))


if __name__ == '__main__':
    main()
