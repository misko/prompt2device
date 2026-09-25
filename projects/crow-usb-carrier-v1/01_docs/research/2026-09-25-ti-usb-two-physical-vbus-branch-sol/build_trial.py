#!/usr/bin/env python3
"""Merge exact VBUS tree debt into the isolated two-physical TI USB packet."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BASE = PROJECT / '01_docs/research/2026-09-25-ti-usb-linked-two-physical-sol'
BOARD = PROJECT / '06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/crow_carrier.kicad_pcb'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED = {
    'board': '8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10',
    'source': '6fa9b9aee4a1651a1e2f75c4d629d077b29504f4033b6062f6fb25187c0d3fcf',
    'floorplan': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    'interfaces': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'contract': '8a04d8e2370e90e572a0cd196e47b33642a42f879bcbb974822f9377fbd1ce1d',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run() -> None:
    inputs = {'board': BOARD, 'source': BASE / 'p1_requirements.yaml',
              'floorplan': BASE / 'floorplan.yaml', 'interfaces': BASE / 'modular_plan.json',
              'contract': BASE / 'coarse.json', 'aliases': ALIASES}
    for key, path in inputs.items():
        if sha(path) != EXPECTED[key]:
            raise RuntimeError(f'{key} input drift')
    spec = importlib.util.spec_from_file_location('vbus_merged_checker', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    source = yaml.safe_load(inputs['source'].read_text())
    contract = json.loads(inputs['contract'].read_text())
    interfaces = json.loads(inputs['interfaces'].read_text())
    alias_map = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    iface = next(row for row in interfaces['interfaces'] if row['net'] == 'VBUS_USB')
    expected_owners = {
        'usb_edge_connector': ['J_USB.10', 'J_USB.15', 'J_USB.2', 'J_USB.7'],
        'usb_frontend': ['C_USB_VBUS.1', 'R_USB_VBUS_BLEED.1', 'U_USB_VBUS_ESD.3'],
        'usb_vbus_sense': ['R_VBUS_B.1'],
    }
    if iface['endpoints'] != expected_owners:
        raise RuntimeError('eight-terminal VBUS source ownership drift')
    entries = sorted((source_pad, checker.graph.native_identity(source_pad, alias_map),
                      'VBUS_USB', owner)
                     for owner, names in iface['endpoints'].items() for source_pad in names)
    if len(entries) != 8 or dict((s, n) for s, n, _, _ in entries)['J_USB.2'] != 'J_USB.A4' or \
            dict((s, n) for s, n, _, _ in entries)['J_USB.10'] != 'J_USB.B4':
        raise RuntimeError('VBUS terminal/alias denominator drift')
    ident, reservation = 'vbus_unplaced_tree', 'vbus_tree'
    endpoints = [{'source_pad': s, 'native_pad': n, 'net': net, 'block': owner}
                 for s, n, net, owner in entries]
    obligations = [{'status': 'P2_REQUIRED', **e, 'branch_id': ident,
                    'layer': 'F.Cu', 'proof': 'native_pad_to_unplaced_tree'}
                   for e in endpoints]
    branch = {'id': ident, 'net': 'VBUS_USB', 'allocation_id': 'usb_device_pair',
              'owner': 'board_integration', 'layer': 'F.Cu',
              'reference_layer': 'In1.Cu', 'reservation_id': reservation,
              'endpoints': endpoints, 'terminal_count': 8,
              'minimum_tree_edges': 7, 'capacity_slots': None,
              'physical_blockers': [],
              'tree_obligation': {'status': 'P3_REQUIRED', 'net': 'VBUS_USB',
                                  'terminal_count': 8, 'minimum_tree_edges': 7,
                                  'proof': 'one_connected_native_net_without_unrelated_branches'},
              'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                    'branch_id': ident, 'reference_layer': 'In1.Cu',
                                    'proof': 'continuous_filled_reference_under_actual_tree'},
              'p2_obligations': obligations}
    source.setdefault('unresolved_multiterminal_branches', []).append(branch)
    alloc = next(row for row in contract['allocations'] if row['id'] == 'usb_device_pair')
    if len([w for w in alloc['boundary_witnesses'] if w['net'] == 'VBUS_USB']) != 2 or \
            len([r for r in alloc['reservations'] if 'VBUS_USB' in r['nets']]) != 2:
        raise RuntimeError('old VBUS ordinary credit denominator drift')
    alloc['boundary_witnesses'] = [w for w in alloc['boundary_witnesses']
                                   if w['net'] != 'VBUS_USB']
    alloc['reservations'] = [r for r in alloc['reservations']
                             if 'VBUS_USB' not in r['nets']]
    representative = next(e for e in endpoints if e['source_pad'] == 'J_USB.2')
    obligation = next(o for o in obligations if o['source_pad'] == 'J_USB.2')
    alloc['boundary_witnesses'].append({
        'kind': 'unresolved_multiterminal_branch', 'branch_id': ident,
        'source': representative['source_pad'], 'native': representative['native_pad'],
        'net': 'VBUS_USB', 'block': representative['block'], 'layer': 'F.Cu',
        'face': 'north', 'boundary_bbox': [232.1, 26.1, 232.7, 27.25],
        'reservation_id': reservation, 'p2_obligation': obligation})
    alloc['reservations'].append({'id': reservation, 'kind': 'unresolved_multiterminal_branch',
                                  'branch_id': ident, 'layer': 'F.Cu', 'nets': ['VBUS_USB']})
    # Retain all three VBUS_PRESENT_N endpoints and their native identities.
    # Its two old movable-pad witnesses also cannot pass as physical pad faces,
    # so keep this control net as an explicit unresolved tree with zero credit.
    presence_iface = next(row for row in interfaces['interfaces']
                          if row['net'] == 'VBUS_PRESENT_N')
    presence_id, presence_res = 'presence_unplaced_tree', 'presence_tree'
    presence_tuples = sorted((s, checker.graph.native_identity(s, alias_map),
                              'VBUS_PRESENT_N', owner)
                             for owner, names in presence_iface['endpoints'].items()
                             for s in names)
    if len(presence_tuples) != 3:
        raise RuntimeError('VBUS_PRESENT_N endpoint denominator drift')
    presence_rows = [{'source_pad': s, 'native_pad': n, 'net': net, 'block': owner}
                     for s, n, net, owner in presence_tuples]
    presence_obligations = [{'status': 'P2_REQUIRED', **e,
                             'branch_id': presence_id, 'layer': 'F.Cu',
                             'proof': 'native_pad_to_unplaced_tree'}
                            for e in presence_rows]
    source['unresolved_multiterminal_branches'].append({
        'id': presence_id, 'net': 'VBUS_PRESENT_N',
        'allocation_id': 'usb_device_pair', 'owner': 'board_integration',
        'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
        'reservation_id': presence_res, 'endpoints': presence_rows,
        'terminal_count': 3, 'minimum_tree_edges': 2,
        'capacity_slots': None, 'physical_blockers': [],
        'tree_obligation': {'status': 'P3_REQUIRED', 'net': 'VBUS_PRESENT_N',
                            'terminal_count': 3, 'minimum_tree_edges': 2,
                            'proof': 'one_connected_native_net_without_unrelated_branches'},
        'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                              'branch_id': presence_id,
                              'reference_layer': 'In1.Cu',
                              'proof': 'continuous_filled_reference_under_actual_tree'},
        'p2_obligations': presence_obligations})
    alloc['boundary_witnesses'] = [w for w in alloc['boundary_witnesses']
                                   if w['net'] != 'VBUS_PRESENT_N']
    alloc['reservations'] = [r for r in alloc['reservations']
                             if 'VBUS_PRESENT_N' not in r['nets']]
    presence_rep = next(e for e in presence_rows if e['source_pad'] == 'Q_VBUS.3')
    presence_ob = next(o for o in presence_obligations
                       if o['source_pad'] == 'Q_VBUS.3')
    alloc['boundary_witnesses'].append({
        'kind': 'unresolved_multiterminal_branch', 'branch_id': presence_id,
        'source': presence_rep['source_pad'], 'native': presence_rep['native_pad'],
        'net': 'VBUS_PRESENT_N', 'block': presence_rep['block'],
        'layer': 'F.Cu', 'face': 'north',
        'boundary_bbox': [212.2, 74.2, 213.675, 74.8],
        'reservation_id': presence_res, 'p2_obligation': presence_ob})
    alloc['reservations'].append({
        'id': presence_res, 'kind': 'unresolved_multiterminal_branch',
        'branch_id': presence_id, 'layer': 'F.Cu', 'nets': ['VBUS_PRESENT_N']})
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
    result = checker.evaluate_coarse(
        BOARD, contract_file, sha(contract_file), source_path=source_file,
        interface_path=interface_file, alias_path=ALIASES, floorplan_path=floor_file,
        expected_source_sha256=sha(source_file),
        expected_interface_sha256=sha(interface_file),
        expected_alias_sha256=sha(ALIASES), expected_floorplan_sha256=sha(floor_file),
        diagnose_all=True)
    usb = next(row for row in result['allocations'] if row['id'] == 'usb_device_pair')
    usb_diagnostics = [d for d in result.get('diagnostics', [])
                       if d.get('allocation') == 'usb_device_pair']
    if (result['p1_accepted'] or result['allocation_denominator'] != 5 or
            result['status'] != 'INCOMPLETE' or result['errors'] or
            usb['status'] != 'INCOMPLETE' or usb.get('reason') or usb_diagnostics or
            {r['id'] for r in usb['reservations']} != {reservation, presence_res} or
            any(r.get('capacity_slots') is not None for r in usb['reservations']) or
            usb['linked_paths'][0]['capacity_slots'] is not None):
        raise RuntimeError('fail-closed merged USB result drift')
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'errors': result['errors'],
                      'usb_status': usb['status'], 'usb_reason': usb.get('reason'),
                      'usb_diagnostics': usb_diagnostics,
                      'source_sha256': sha(source_file), 'contract_sha256': sha(contract_file)}, indent=2))

if __name__ == '__main__':
    run()
