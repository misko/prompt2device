#!/usr/bin/env python3
"""Rebuild a no-credit Crow P1 diagnostic against the current three-pose board."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
RESEARCH = PROJECT / '01_docs/research'
BASE = RESEARCH / '2026-09-25-ti-usb-two-physical-vbus-branch-sol'
BOARD = PROJECT / '06_build/prototype_board_diagnostic/current-ti-audio-en-three-pose-20260925/project/04_kicad/crow_carrier.kicad_pcb'
CURRENT_FLOOR = PROJECT / '06_build/prototype_board_diagnostic/current-ti-audio-en-three-pose-20260925/project/03_src/floorplan.yaml'
PORTAL = RESEARCH / '2026-09-25-ti-adc7-access-only-portal-sol/portal.yaml'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED = {
    'board': '0bd3ac8dd8c80177958c009a0644f0bc723bcee7ad7085c2fb76c09c5df958f5',
    'source': 'be824e24fc0b0e165cd9ca2d1623dddaac40ce72ce2dc9775b675c498ad1e385',
    'contract': '69d4f615a845f5eb1f4ad765614a7c6b1c8fbe98f172cb925cdbbca06ff179ca',
    'floorplan': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    'current_floor': '5d705a162c5ad4c8ee797dfeb3921b230b16126e603341b43fffbc21de602bcb',
    'interfaces': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'portal': 'f1952e27cebd1eb3fa3b1ebc4863ed7d408f4b04d603a8c76454a063eff719ae',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
    'checker': '5c4eba1e1286c6dd69e8f553e99117ba70acdd5c45740eb9678bdf5b5a529e10',
}
FAMILIES = {
    'adc_analog_boundary': tuple([f'ADC{i}{p}' for i in range(1, 9)
                                  for p in ('N', 'P')] + ['VMID1_EXT', 'VMID2_EXT']),
    'adc_timing_xmos_bundle': ('ADC_BCLK', 'ADC_FSYNC', 'ADC_DOUT1',
                               'AUDIO_MCLK_1V8', 'TDM_BCLK_1V8', 'TDM_DATA_1V8',
                               'TDM_FSYNC_1V8', 'ADC_I2C_SCL', 'ADC_I2C_SDA',
                               'ADC_READY', 'AUDIO_EN', 'XU_I2C_SCL_1V8',
                               'XU_I2C_SDA_1V8', 'ADC_DIGITAL_BAD'),
}
COUNTS = {'adc_analog_boundary': 88, 'adc_timing_xmos_bundle': 54}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branch_for(family, item):
    net, entries = item['net'], item['endpoints']
    prefix = 'analog' if family == 'adc_analog_boundary' else 'timing'
    two_terminal = len(entries) == 2
    ident = f'{prefix}_{net.lower()}_{"unplaced_crossing" if two_terminal else "unplaced_tree"}'
    reservation = f'{prefix}_{net.lower()}_{"crossing" if two_terminal else "tree"}'
    obligations = [{'status': 'P2_REQUIRED', **entry, 'branch_id': ident,
                    'layer': 'F.Cu', 'proof': 'native_pad_to_unplaced_tree'}
                   for entry in entries]
    branch = {'id': ident, 'owner': 'board_integration', 'allocation_id': family,
              'net': net, 'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
              'reservation_id': reservation, 'endpoints': entries,
              'terminal_count': len(entries), 'minimum_tree_edges': len(entries)-1,
              'physical_blockers': item['foreign_regions'], 'capacity_slots': None,
              'p2_obligations': obligations,
              'tree_obligation': {'status': 'P3_REQUIRED', 'net': net,
                                  'terminal_count': len(entries),
                                  'minimum_tree_edges': len(entries)-1,
                                  'proof': 'one_connected_native_net_without_unrelated_branches'},
              'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                    'branch_id': ident, 'reference_layer': 'In1.Cu',
                                    'proof': 'continuous_filled_reference_under_actual_tree'}}
    return branch, obligations


def main():
    inputs = {'board': BOARD, 'source': BASE/'p1_requirements.yaml',
              'contract': BASE/'coarse.json', 'floorplan': BASE/'floorplan.yaml',
              'current_floor': CURRENT_FLOOR, 'interfaces': BASE/'modular_plan.json', 'portal': PORTAL,
              'aliases': ALIASES, 'checker': CHECKER}
    for name, path in inputs.items():
        if sha(path) != EXPECTED[name]:
            raise SystemExit(f'{name}: input SHA drift')
    spec = importlib.util.spec_from_file_location('unified_p1_checker', CHECKER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = yaml.safe_load(inputs['source'].read_text())
    source.update(yaml.safe_load(PORTAL.read_text()))
    contract = json.loads(inputs['contract'].read_text())
    floor = yaml.safe_load(inputs['floorplan'].read_text())
    current_floor = yaml.safe_load(CURRENT_FLOOR.read_text())
    # Keep the diagnostic integration regions/corridors while rebinding the
    # source-owned current poses, including the three AUDIO_EN moves.
    floor['placement']['post_anchors'].update(current_floor['placement']['post_anchors'])
    interfaces = json.loads(inputs['interfaces'].read_text())
    alias_map = helper.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    board = pcbnew.LoadBoard(str(BOARD))
    _, pads = helper.graph.board_index(board)
    regions = floor['placement']['regions']
    by_net = {row['net']: row for row in interfaces['interfaces']}
    ledger = {}
    for family, nets in FAMILIES.items():
        src = next(row for row in source['allocations'] if row['id'] == family)
        alloc = next(row for row in contract['allocations'] if row['id'] == family)
        if (tuple(src['coverage_nets']) != nets or tuple(alloc['coverage_nets']) != nets or
                len(alloc['boundary_witnesses']) != len(nets)):
            raise SystemExit(f'{family}: source/contract net denominator drift')
        alloc['boundary_witnesses'] = []
        alloc['reservations'] = []
        ledger[family] = []
        for net in nets:
            if src['endpoints'][net] != by_net[net]['endpoints']:
                raise SystemExit(f'{net}: exact modular/source endpoint drift')
            members = sorted((s, helper.graph.native_identity(s, alias_map), owner)
                             for owner, names in by_net[net]['endpoints'].items()
                             for s in names)
            entries, outside, foreign = [], [], []
            for source_pad, native_pad, owner in members:
                found = pads.get(native_pad, [])
                if (len(found) != 1 or found[0].GetNetname() != net or
                        not found[0].IsOnLayer(pcbnew.F_Cu)):
                    raise SystemExit(f'{source_pad}: exact native F.Cu pad/net mismatch')
                box = helper.box_mm(found[0].GetBoundingBox())
                entries.append({'source_pad': source_pad, 'native_pad': native_pad,
                                'net': net, 'block': owner})
                if not helper.contains(regions[owner], box):
                    outside.append({'source_pad': source_pad, 'native_pad': native_pad,
                                    'owner': owner, 'pad_bbox_mm': box})
                neighbors = sorted(name for name, region in regions.items()
                                   if name != owner and helper.intersects(box, region))
                if neighbors:
                    foreign.append({'source_pad': source_pad, 'native_pad': native_pad,
                                    'block': owner, 'foreign_regions': neighbors})
            native = [fp.GetReference()+'.'+pad.GetNumber()
                      for fp in board.GetFootprints() for pad in fp.Pads()
                      if pad.GetNetname() == net]
            if len(native) != len(entries) or set(native) != {e['native_pad'] for e in entries}:
                raise SystemExit(f'{net}: undeclared/duplicate native terminal')
            category = ('owner_containment' if outside else
                        'two_terminal_crossing' if len(entries) == 2 else 'schema_branch')
            item = {'net': net, 'terminal_count': len(entries), 'endpoints': entries,
                    'outside_owner': outside, 'foreign_regions': foreign,
                    'category': category, 'capacity_slots': None,
                    'p2_debt': 'native_pad_to_tree_and_continuous_filled_In1_Cu_return',
                    'p3_debt': 'one_connected_native_net_without_unrelated_branches'}
            ledger[family].append(item)
            if category == 'owner_containment':
                continue
            branch, obligations = branch_for(family, item)
            kind = ('unresolved_two_terminal_crossing' if len(entries) == 2
                    else 'unresolved_multiterminal_branch')
            source.setdefault('unresolved_two_terminal_crossings' if len(entries) == 2
                              else 'unresolved_multiterminal_branches', []).append(branch)
            rep = entries[0]
            box = helper.box_mm(pads[rep['native_pad']][0].GetBoundingBox())
            alloc['boundary_witnesses'].append({
                'kind': kind, 'branch_id': branch['id'],
                'source': rep['source_pad'], 'native': rep['native_pad'],
                'net': net, 'block': rep['block'], 'layer': 'F.Cu', 'face': 'north',
                'boundary_bbox': list(box), 'reservation_id': branch['reservation_id'],
                'p2_obligation': obligations[0]})
            alloc['reservations'].append({
                'id': branch['reservation_id'], 'kind': kind,
                'branch_id': branch['id'], 'layer': 'F.Cu', 'nets': [net]})
        if sum(x['terminal_count'] for x in ledger[family]) != COUNTS[family]:
            raise SystemExit(f'{family}: exact endpoint count drift')
    source_file = HERE/'p1_requirements.yaml'
    floor_file = HERE/'floorplan.yaml'
    interfaces_file = HERE/'modular_plan.json'
    contract_file = HERE/'coarse.json'
    source_file.write_text(yaml.safe_dump(source, sort_keys=False))
    floor_file.write_text(yaml.safe_dump(floor, sort_keys=False))
    interfaces_file.write_bytes(inputs['interfaces'].read_bytes())
    contract.update(board_sha256=sha(BOARD), source_sha256=sha(source_file),
                    floorplan_sha256=sha(floor_file))
    # Use the shared read-only native rebind for every unresolved witness,
    # including reset U_XU.38 whose pad bbox moved with this board.
    sys.path.insert(0, str(ROOT / 'skills/pcb-design/scripts'))
    from integration_candidate import propose_native_witnesses
    proposal = propose_native_witnesses(BOARD, contract)
    contract = proposal['proposed_contract']
    contract['source_sha256'] = sha(source_file)
    contract['floorplan_sha256'] = sha(floor_file)
    contract_file.write_text(json.dumps(contract, indent=2)+'\n')
    (HERE/'native_witness_rebind.json').write_text(json.dumps(
        {key: value for key, value in proposal.items() if key != 'proposed_contract'},
        indent=2, sort_keys=True)+'\n')
    coverage, _ = helper.graph.source_inventory(source, interfaces)
    accepted = helper._unresolved_branches(source, interfaces, board, regions,
                                           coverage, alias_map, pads)
    for family, items in ledger.items():
        for item in items:
            if item['category'] in ('schema_branch', 'two_terminal_crossing'):
                branch, _ = branch_for(family, item)
                if branch['id'] not in accepted:
                    raise SystemExit(f"{item['net']}: exact branch not accepted")
    result = helper.evaluate_coarse(
        BOARD, contract_file, sha(contract_file), source_path=source_file,
        interface_path=interfaces_file, alias_path=ALIASES, floorplan_path=floor_file,
        expected_source_sha256=sha(source_file),
        expected_interface_sha256=sha(interfaces_file),
        expected_alias_sha256=sha(ALIASES), expected_floorplan_sha256=sha(floor_file),
        diagnose_all=True)
    if result['p1_accepted'] or result['status'] != 'INCOMPLETE':
        raise SystemExit('unexpected P1 acceptance/status')
    allocation_status = {row['id']: row for row in result['allocations']}
    expected_states = {'usb_device_pair': 'INCOMPLETE',
                       'xmos_service_escape': 'INCOMPLETE',
                       'adc_timing_xmos_bundle': 'INCOMPLETE',
                       'adc_analog_boundary': 'INCOMPLETE',
                       'power_boundary_windows': 'INCOMPLETE'}
    if (result['routing_realized'] or
            {key: row['status'] for key, row in allocation_status.items()} != expected_states or
            len(source['linked_paths']) != 1 or
            source['linked_paths'][0]['id'] != 'usb_data_series' or
            len(result.get('access_only_portals', [])) != 1 or
            result['access_only_portals'][0]['capacity_slots'] is not None or
            result['errors'] or len(result['diagnostics']) != 9 or
            any(row.get('allocation') != 'power_boundary_windows'
                for row in result['diagnostics'])):
        raise SystemExit('full fail-closed diagnostic shape drift')
    summary = {family: {kind: sum(x['category'] == kind for x in items)
                        for kind in sorted({x['category'] for x in items})}
               for family, items in ledger.items()}
    (HERE/'endpoint_ledger.json').write_text(json.dumps({
        'status': 'INCOMPLETE', 'p1_accepted': False, 'board_sha256': sha(BOARD),
        'source_sha256': sha(source_file), 'contract_sha256': sha(contract_file),
        'summary': summary, 'families': ledger}, indent=2, sort_keys=True)+'\n')
    (HERE/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    issues = {
        'status': 'INCOMPLETE', 'p1_accepted': False, 'routing_realized': False,
        'board_sha256': sha(BOARD), 'source_sha256': sha(source_file),
        'contract_sha256': sha(contract_file),
        'allocation_status': expected_states,
        'exact_accounting': {
            'usb': {'linked_dp_dn_paths': 1, 'vbus_tree_terminals': 8,
                    'presence_tree_terminals': 3},
            'analog': {'nets': 18, 'terminals': 88, 'exact_unplaced_branches': 18},
            'adc7_portal': {'nets': 2, 'terminals': 8, 'capacity_slots': None},
            'timing': {'nets': 14, 'terminals': 54, 'exact_unplaced_branches': 14,
                       'two_terminal_crossings': 4,
                       'two_terminal_nets': [x['net'] for x in
                                             ledger['adc_timing_xmos_bundle']
                                             if x['category'] == 'two_terminal_crossing']}},
        'remaining_issues': {
            'timing_owner_containment': [x for x in
                                         ledger['adc_timing_xmos_bundle']
                                         if x['category'] == 'owner_containment'],
            'power_witness_diagnostics': result['diagnostics'],
            'global_denominator_errors': result['errors'],
            'allocation_reasons': {key: row.get('reason')
                                   for key, row in allocation_status.items()},
            'p2_p3_debt': 'No native routes, local pad access, filled return, or connected-net proof'},
    }
    (HERE/'issues.json').write_text(json.dumps(issues, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': result['status'], 'summary': summary,
                      'errors': len(result['errors']),
                      'diagnostics': len(result['diagnostics']),
                      'portal': result.get('access_only_portals'),
                      'source_sha256': sha(source_file),
                      'contract_sha256': sha(contract_file)}, indent=2))


if __name__ == '__main__':
    main()
