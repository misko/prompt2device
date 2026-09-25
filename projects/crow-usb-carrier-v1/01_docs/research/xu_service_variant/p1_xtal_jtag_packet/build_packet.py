#!/usr/bin/env python3
"""Combine pinned physical-cell XTAL/QSPI with reviewed fixed JTAG access."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
XTAL = HERE.parent / 'p1_xtal_packet'
JTAG = PROJECT / '01_docs/research/jtag_segmented_packet'
BOARD = Path('/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb')
PLAN = PROJECT / '03_src/modular_plan.json'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
PINNED = {
    BOARD: 'fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27',
    XTAL / 'p1_source_xtal.yaml': 'a159d4ac25f8c13a81ea79e76ad5eac023349a169119feadf7ff04d8e7c15c36',
    XTAL / 'floorplan_xtal.yaml': '41632157eda6c65721d33d8aa04c6295569f1a8d8d926de25c8cf95b465e890e',
    XTAL / 'coarse_contract_xtal.json': '99bb672774e24cc0e1fbc443a9de727304b812ba3168dcdfbce00e4959d2702c',
    JTAG / 'p1_source_jtag.yaml': 'b6ed302ba2ee2462dbc39de5ac1e851c528e9897478325aee0657e2e68d87799',
    JTAG / 'floorplan_jtag.yaml': '1a05e7247604519d3c69b0d311ac607b7c63ba959973c2672ae43763974ce569',
    JTAG / 'coarse_jtag.json': '03e91be3e2c77a91d7ce8268d35681f52e5db44be550dd9f75643f298d688416',
    PLAN: '7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e',
    ALIASES: 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
    CHECKER: '7e08888948c237690a889e1e62d8b2b02f1e8d2a03549c02593b3a715bf5ed0d',
}
JTAG_NETS = {'JTAG_TMS', 'JTAG_TCK', 'JTAG_TDO', 'JTAG_TDI'}
XU_FACE = [221.1, 84, 223.9, 84.3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for path, expected in PINNED.items():
        if sha(path) != expected:
            raise RuntimeError(f'pinned parent drift: {path}')
    source = yaml.safe_load((XTAL / 'p1_source_xtal.yaml').read_text())
    floor = yaml.safe_load((XTAL / 'floorplan_xtal.yaml').read_text())
    contract = json.loads((XTAL / 'coarse_contract_xtal.json').read_text())
    j_source = yaml.safe_load((JTAG / 'p1_source_jtag.yaml').read_text())
    j_floor = yaml.safe_load((JTAG / 'floorplan_jtag.yaml').read_text())
    j_contract = json.loads((JTAG / 'coarse_jtag.json').read_text())
    regions = floor['placement']['regions']
    for key in ('usb_frontend', 'debug_connector', 'board_integration_jtag'):
        regions[key] = j_floor['placement']['regions'][key]
    if regions['board_integration_jtag'] != [221, 65, 226, 84]:
        raise RuntimeError('JTAG strip geometry drift')
    source_demand = next(a for a in source['allocations'] if a['id'] == 'xmos_service_escape')['demands']
    old = next(d for d in source_demand if d['id'] == 'jtag_reset')
    j_demand = next(a for a in j_source['allocations'] if a['id'] == 'xmos_service_escape')['demands']
    source_demand[source_demand.index(old):source_demand.index(old) + 1] = [
        next(d for d in j_demand if d['id'] == 'jtag_four'),
        next(d for d in j_demand if d['id'] == 'reset_branch')]
    corridor = next(c for c in j_source['integration_corridors'] if c['id'] == 'jtag_strip')
    xu_face = next(f for f in corridor['faces'] if f['block'] == 'xmos_core')
    xu_face['bbox'] = XU_FACE
    xu_face['physical_cell_id'] = 'xmos_core_east'
    for obligation in corridor['p2_obligations']:
        if obligation['block'] == 'xmos_core':
            obligation['physical_cell_id'] = 'xmos_core_east'
    source['integration_corridors'].append(corridor)
    allocation = next(a for a in contract['allocations'] if a['id'] == 'xmos_service_escape')
    j_allocation = next(a for a in j_contract['allocations'] if a['id'] == 'xmos_service_escape')
    allocation['boundary_witnesses'] = [w for w in allocation['boundary_witnesses']
                                        if w['net'] not in JTAG_NETS]
    j_witnesses = [w for w in j_allocation['boundary_witnesses']
                   if w.get('corridor_id') == 'jtag_strip']
    if len(j_witnesses) != 8:
        raise RuntimeError('reviewed JTAG witness denominator drift')
    for witness in j_witnesses:
        if witness['block'] == 'xmos_core':
            witness['physical_cell_id'] = 'xmos_core_east'
            witness['boundary_bbox'] = XU_FACE
            witness['p2_obligation']['physical_cell_id'] = 'xmos_core_east'
    allocation['boundary_witnesses'] = j_witnesses + allocation['boundary_witnesses']
    for witness in allocation['boundary_witnesses']:
        if witness['net'] == 'XU_RESET_N' and witness['block'] == 'xmos_core':
            witness['reservation_id'] = 'reset_unresolved'
    allocation['reservations'] = [r for r in allocation['reservations'] if r['id'] != 'jtag_north']
    j_reservations = [r for r in j_allocation['reservations']
                      if r.get('corridor_id') == 'jtag_strip']
    if len(j_reservations) != 5:
        raise RuntimeError('reviewed JTAG reservation denominator drift')
    allocation['reservations'] = j_reservations + allocation['reservations']
    allocation['reservations'].append({
        'id': 'reset_unresolved', 'kind': 'signal', 'layer': 'F.Cu',
        'bbox': [221, 84, 226, 91], 'nets': ['XU_RESET_N'],
        'axis': 'vertical', 'demand_slots': 1, 'slot_pitch_mm': 0.45})
    source_out = HERE / 'p1_source_xtal_jtag.yaml'
    floor_out = HERE / 'floorplan_xtal_jtag.yaml'
    contract_out = HERE / 'coarse_xtal_jtag.json'
    source_out.write_text(yaml.safe_dump(source, sort_keys=False))
    floor_out.write_text(yaml.safe_dump(floor, sort_keys=False))
    hashes = {'board': sha(BOARD), 'source': sha(source_out),
              'floorplan': sha(floor_out), 'interfaces': sha(PLAN),
              'aliases': sha(ALIASES)}
    for label, value in hashes.items():
        contract[label + '_sha256'] = value
    contract_out.write_text(json.dumps(contract, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location(
        'checker', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    board = checker.pcbnew.LoadBoard(str(BOARD))
    header = board.FindFootprintByReference('J_JTAG')
    position = header.GetPosition()
    if (checker.pcbnew.ToMM(position.x), checker.pcbnew.ToMM(position.y),
            header.GetOrientationDegrees()) != (228, 50, 90):
        raise RuntimeError('fixed JTAG header pose drift')
    outline = checker.pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise RuntimeError('native outline unavailable')
    plan = json.loads(PLAN.read_text())
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    _, pads = checker.graph.board_index(board)
    coverage, terminals = checker.graph.source_inventory(source, plan)
    if len(terminals) != 59 or coverage != checker.CROW_COVERAGE:
        raise RuntimeError('59-net source allocation drift')
    cells = checker._physical_cells(source, plan, board, outline, regions,
                                    floor['placement']['patterns'])
    corridors = checker._integration_corridors(
        source, plan, board, outline, regions, list(board.Zones()),
        coverage, aliases, pads, {}, cells)
    if set(corridors) != {'qspi_gap', 'xtal_south_cap', 'jtag_strip'}:
        raise RuntimeError('three-corridor source denominator drift')
    owned = {}
    for interface in plan['interfaces']:
        for block, names in interface['endpoints'].items():
            owned.setdefault((interface['net'], block), set()).update(names)
    fixed = set(source['p1_fixed_refs'])
    checked = []
    reservations = {r['id']: r for r in allocation['reservations']}
    for witness in j_witnesses:
        exact = checker._coarse_witness(
            board, witness, witness['net'], owned, aliases, pads,
            outline, regions, fixed, {}, corridors, physical_cells=cells)
        target = reservations[witness['reservation_id']]
        if witness['kind'] == 'fixed_connector_access_segmented':
            checker._fixed_access_shapes(target, exact, corridors['jtag_strip']['bbox'],
                checker.rectangle(regions['debug_connector'], 'debug source region'))
        elif not checker._witness_touches_reservation(exact, target):
            raise RuntimeError(f'{exact["source"]}: JTAG face misses reservation')
        checked.append((exact['source'], exact['native'], exact['net'], exact['block']))
    expected = {(e['source_pad'], e['native_pad'], e['net'], e['block'])
                for e in corridor['affected']}
    fixed_pads = {e['source_pad'] for e in corridor['affected']
                  if e['block'] == 'debug_connector'}
    if (len(checked) != 8 or set(checked) != expected or
            len(corridor['p2_obligations']) != 8 or
            fixed_pads != {'J_JTAG.2', 'J_JTAG.4', 'J_JTAG.6', 'J_JTAG.8'} or
            'J_JTAG' not in fixed):
        raise RuntimeError('fixed JTAG pads or P2 obligation denominator drift')
    result = checker.evaluate_coarse(
        BOARD, contract_out, sha(contract_out), source_path=source_out,
        interface_path=PLAN, alias_path=ALIASES, floorplan_path=floor_out,
        expected_source_sha256=hashes['source'],
        expected_interface_sha256=hashes['interfaces'],
        expected_alias_sha256=hashes['aliases'],
        expected_floorplan_sha256=hashes['floorplan'])
    allocation_results = {a['id']: a for a in result['allocations']}
    expected_errors = [
        'qspi_gap: integration affected endpoint/layer denominator mismatch',
        'xtal_south_cap: integration affected endpoint/layer denominator mismatch',
        'jtag_strip: integration affected endpoint/layer denominator mismatch']
    if (result['status'] != 'FAIL' or result['p1_accepted'] or
            result['errors'] != expected_errors or
            allocation_results['xmos_service_escape']['reason'] !=
            'U_XU.38: witness bbox is a nonlocal bridge across source region' or
            allocation_results['usb_device_pair']['reason'] !=
            'J_USB.4: witness bbox is a nonlocal bridge across source region'):
        raise RuntimeError(f'whole native failure outcome drift: {result}')
    receipt = {'kind': 'crow-xtal-qspi-jtag-source-probe', 'schema': 1,
               'inputs': {str(path): value for path, value in PINNED.items()},
               'outputs': {'source': sha(source_out), 'floorplan': sha(floor_out),
                           'contract': sha(contract_out)},
               'board_sha256': hashes['board'], 'coverage_net_count': len(terminals),
               'fixed_jtag_pads': sorted(e['source_pad'] for e in corridor['affected']
                                         if e['block'] == 'debug_connector'),
               'jtag_p2_obligation_count': len(corridor['p2_obligations']),
               'native_jtag_witness_count': len(checked),
               'declaration_corridors': sorted(corridors),
               'whole_status': result['status'], 'p1_accepted': result['p1_accepted'],
               'whole_errors': result['errors'],
               'allocations': [{'id': a['id'], 'status': a['status'],
                                'reason': a.get('reason')} for a in result['allocations']]}
    (HERE / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'declaration_corridors': receipt['declaration_corridors'],
                      'native_jtag_witness_count': len(checked),
                      'whole_status': result['status'],
                      'xmos_service': next(a for a in receipt['allocations']
                                           if a['id'] == 'xmos_service_escape'),
                      'errors': result['errors']}, indent=2))


if __name__ == '__main__':
    main()
