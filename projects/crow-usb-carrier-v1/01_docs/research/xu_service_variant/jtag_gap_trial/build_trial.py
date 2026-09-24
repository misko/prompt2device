#!/usr/bin/env python3
"""Research-only, hash-bound trial of the four two-terminal JTAG nets."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BASE = HERE.parent / 'p1_qspi_packet'
BOARD = Path('/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb')
INTERFACES = PROJECT / '03_src/modular_plan.json'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
SOURCE = BASE / 'p1_source_variant.yaml'
FLOORPLAN = BASE / 'floorplan_qspi_gap.yaml'
CONTRACT = BASE / 'coarse_contract.json'
PINNED = {
    'board': 'fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27',
    'source': '9a13c0999d29f17280bb5d8ffb98a5e0d59afe3ee4511eb004e436bffc13ece4',
    'floorplan': 'cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925',
    'contract': 'b17a94fedafbc334bdc0721535c640fb786f4b632b1abddf487289fdb19fbda4',
    'interfaces': '7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
}
NET_PADS = {'JTAG_TCK': ('U_XU.51', 'J_JTAG.4'),
            'JTAG_TDI': ('U_XU.36', 'J_JTAG.8'),
            'JTAG_TDO': ('U_XU.37', 'J_JTAG.6'),
            'JTAG_TMS': ('U_XU.44', 'J_JTAG.2')}
STRIP = [221, 65, 226, 84]
XU_FACE = [221.1, 84, 225.9, 84.3]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> None:
    inputs = {'board': BOARD, 'source': SOURCE, 'floorplan': FLOORPLAN,
              'contract': CONTRACT, 'interfaces': INTERFACES, 'aliases': ALIASES}
    for name, path in inputs.items():
        if sha(path) != PINNED[name]:
            raise RuntimeError(f'{name} input hash drift: {sha(path)}')
    floorplan = yaml.safe_load(FLOORPLAN.read_text())
    regions = floorplan['placement']['regions']
    if regions['usb_frontend'] != [200, 35, 236, 70] or regions['xmos_core'] != [190, 84, 232, 110.5]:
        raise RuntimeError('source boundary drift')
    # The handoff has 0.3 mm depth in debug_connector.  The USB ownership
    # rectangle must end before that face or schema-2 rejects double ownership.
    regions['usb_frontend'][3] = 64.7
    regions['board_integration_jtag'] = STRIP
    floorplan_out = HERE / 'floorplan_trial.yaml'
    floorplan_out.write_text(yaml.safe_dump(floorplan, sort_keys=False))
    source = yaml.safe_load(SOURCE.read_text())
    source_alloc = next(a for a in source['allocations'] if a['id'] == 'xmos_service_escape')
    old_demand = next(d for d in source_alloc['demands'] if d['id'] == 'jtag_reset')
    if set(old_demand['nets']) != set(NET_PADS) | {'XU_RESET_N'}:
        raise RuntimeError('JTAG/reset source demand drift')
    old_demand.update(id='jtag_four', nets=list(NET_PADS), slots=4, required_width_mm=1.8)
    source_alloc['demands'].insert(source_alloc['demands'].index(old_demand) + 1, {
        'id': 'reset_branch', 'nets': ['XU_RESET_N'], 'layers': ['F.Cu'],
        'status': 'INCOMPLETE', 'reason': 'digital_power fan-in and connector branch unallocated'})
    endpoint_rows = []
    for net, (xu_pad, connector_pad) in NET_PADS.items():
        endpoint_rows.extend(({'source_pad': xu_pad, 'native_pad': xu_pad,
                               'net': net, 'block': 'xmos_core'},
                              {'source_pad': connector_pad, 'native_pad': connector_pad,
                               'net': net, 'block': 'debug_connector'}))
    faces = [{'block': 'xmos_core', 'region_face': 'north', 'bbox': XU_FACE},
             {'block': 'debug_connector', 'region_face': 'south',
              'bbox': [221.1, 64.7, 225.9, 65]}]
    face_map = {f['block']: f for f in faces}
    obligations = [{'status': 'P2_REQUIRED', **e, 'corridor_id': 'jtag_gap',
                    'region_face': face_map[e['block']]['region_face'],
                    'layer': 'F.Cu', 'to_reservation': 'jtag_gap_four'}
                   for e in endpoint_rows]
    source['integration_corridors'].append({
        'id': 'jtag_gap', 'owner': 'board_integration',
        'region_id': 'board_integration_jtag',
        'allocation_id': 'xmos_service_escape',
        'participants': ['xmos_core', 'debug_connector'], 'faces': faces,
        'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
        'nets': list(NET_PADS), 'reservation_id': 'jtag_gap_four',
        'affected': endpoint_rows, 'p2_obligations': obligations,
        'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                              'corridor_id': 'jtag_gap', 'reference_layer': 'In1.Cu',
                              'proof': 'continuous_filled_reference'}})
    source_out = HERE / 'p1_source_trial.yaml'
    source_out.write_text(yaml.safe_dump(source, sort_keys=False))
    contract = json.loads(CONTRACT.read_text())
    allocation = next(a for a in contract['allocations'] if a['id'] == 'xmos_service_escape')
    net_set = set(NET_PADS)
    allocation['boundary_witnesses'] = [w for w in allocation['boundary_witnesses']
                                        if w['net'] not in net_set]
    # Only the movable XU-side obligations can use virtual source-region faces.
    # The fixed connector pads keep native identities and require a separate
    # north-side access study; the coarse checker has no multi-reservation graph.
    for net, (xu_pad, _) in NET_PADS.items():
        obligation = next(o for o in obligations if o['source_pad'] == xu_pad)
        allocation['boundary_witnesses'].append({
            'kind': 'integration_corridor_handoff', 'corridor_id': 'jtag_gap',
            'source': xu_pad, 'native': xu_pad,
            'net': net, 'block': 'xmos_core', 'face': 'south',
            'layer': 'F.Cu', 'region_face': 'north',
            'boundary_bbox': XU_FACE, 'reservation_id': 'jtag_gap_four',
            'p2_obligation': obligation})
    # XU_RESET_N remains a separate, three-owner branch.  This deliberately
    # leaves its original nonlocal witness in place for a fail-closed verdict.
    old = next(r for r in allocation['reservations'] if r['id'] == 'jtag_north')
    old['nets'] = ['XU_RESET_N']
    old['demand_slots'] = 1
    old['bbox'] = [221, 65, 226, 91]
    allocation['reservations'].append({
        'id': 'jtag_gap_four', 'kind': 'integration_corridor',
        'corridor_id': 'jtag_gap', 'owner': 'board_integration',
        'region_id': 'board_integration_jtag', 'layer': 'F.Cu',
        'bbox': STRIP, 'nets': list(NET_PADS)})
    contract['source_sha256'] = sha(source_out)
    contract['floorplan_sha256'] = sha(floorplan_out)
    contract_out = HERE / 'coarse_trial.json'
    contract_out.write_text(json.dumps(contract, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('p1_corridor_capacity',
        ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    board = checker.pcbnew.LoadBoard(str(BOARD))
    outline = checker.pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise RuntimeError('native outline unavailable')
    refs, pads = checker.graph.board_index(board)
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    interfaces = json.loads(INTERFACES.read_text())
    coverage, terminal_nets = checker.graph.source_inventory(source, interfaces)
    if len(terminal_nets) != 59:
        raise RuntimeError('whole-source 59-net denominator drift')
    corridors = checker._integration_corridors(
        source, interfaces, board, outline, regions, list(board.Zones()),
        coverage, aliases, pads, {})
    if set(corridors) != {'qspi_gap', 'jtag_gap'}:
        raise RuntimeError('source corridor declaration drift')
    owned = {}
    for item in interfaces['interfaces']:
        for block, source_pads in item['endpoints'].items():
            owned.setdefault((item['net'], block), set()).update(source_pads)
    checked = []
    target = next(r for r in allocation['reservations'] if r['id'] == 'jtag_gap_four')
    for witness in allocation['boundary_witnesses']:
        if witness.get('reservation_id') != 'jtag_gap_four':
            continue
        exact = checker._coarse_witness(board, witness, witness['net'], owned, aliases,
                                        pads, outline, regions, set(source['p1_fixed_refs']),
                                        {}, corridors)
        if not checker._witness_touches_reservation(exact, target):
            raise RuntimeError(f'{exact["source"]}: face does not touch strip')
        checked.append(exact['source'])
    if set(checked) != {p[0] for p in NET_PADS.values()}:
        raise RuntimeError('four-net XU denominator drift')
    fixed_probe = {'kind': 'integration_corridor_handoff', 'corridor_id': 'jtag_gap',
                   'source': 'J_JTAG.4', 'native': 'J_JTAG.4', 'net': 'JTAG_TCK',
                   'block': 'debug_connector', 'face': 'north', 'layer': 'F.Cu',
                   'region_face': 'south', 'boundary_bbox': faces[1]['bbox'],
                   'reservation_id': 'jtag_gap_four',
                   'p2_obligation': next(o for o in obligations if o['source_pad'] == 'J_JTAG.4')}
    try:
        checker._coarse_witness(board, fixed_probe, 'JTAG_TCK', owned, aliases,
                                pads, outline, regions, set(source['p1_fixed_refs']),
                                {}, corridors)
    except checker.ContractError as exc:
        if str(exc) != 'J_JTAG.4: fixed P1 ref cannot use integration handoff':
            raise
        fixed_rejection = str(exc)
    else:
        raise RuntimeError('fixed connector handoff unexpectedly accepted')
    obstacles = checker.layer_obstacles(board, 'F.Cu', set())
    capacity = checker.connected_capacity(STRIP, obstacles, 'vertical', 0.45)
    if (not capacity['connected_through_lane'] or
            capacity['connected_width_mm'] != 5 or
            capacity['capacity_slots'] != 11 or
            capacity['foreign_obstacles']):
        raise RuntimeError('native strip capacity drift')
    result = checker.evaluate_coarse(BOARD, contract_out, sha(contract_out),
                                     source_path=source_out, interface_path=INTERFACES,
                                     alias_path=ALIASES, floorplan_path=floorplan_out,
                                     expected_source_sha256=sha(source_out),
                                     expected_interface_sha256=sha(INTERFACES),
                                     expected_alias_sha256=sha(ALIASES),
                                     expected_floorplan_sha256=sha(floorplan_out))
    xmos = next(a for a in result['allocations'] if a['id'] == 'xmos_service_escape')
    if result['p1_accepted'] or xmos.get('reason') != 'U_XU.38: witness bbox is a nonlocal bridge across source region':
        raise RuntimeError('fail-closed allocation result drift')
    receipt = {'status': 'INCOMPLETE_SOURCE_TRIAL', 'p1_accepted': False,
               'board_sha256': sha(BOARD), 'source_sha256': sha(source_out),
               'floorplan_sha256': sha(floorplan_out), 'contract_sha256': sha(contract_out),
               'strip_mm': STRIP, 'xu_face_mm': XU_FACE,
               'validated_xu_witnesses': checked,
               'declared_endpoint_count': len(endpoint_rows),
               'fixed_connector_handoff_rejection': fixed_rejection,
               'native_strip_capacity': capacity,
               'whole_packet_status': result['status'], 'whole_packet_errors': result['errors'],
               'xmos_allocation': xmos,
               'fixed_connector_access_proven': False,
               'multi_reservation_connectivity_proven': False,
               'filled_reference_proven': False,
               'effective_capacity_proven': False}
    (HERE / 'trial_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'raw_slots': capacity['capacity_slots'],
                      'whole_packet': result['status'], 'xmos_reason': xmos.get('reason')}, indent=2))


if __name__ == '__main__':
    run()
