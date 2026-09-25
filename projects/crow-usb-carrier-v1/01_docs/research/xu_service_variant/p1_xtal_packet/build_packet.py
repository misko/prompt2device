#!/usr/bin/env python3
"""Research-only XTAL physical-cell source probe; never promotes P1."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
PARENT = HERE.parent / 'p1_qspi_packet'
BOARD = Path('/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb')
INTERFACES = PROJECT / '03_src/modular_plan.json'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
INPUTS = {
    BOARD: 'fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27',
    PARENT / 'p1_source_variant.yaml': '9a13c0999d29f17280bb5d8ffb98a5e0d59afe3ee4511eb004e436bffc13ece4',
    PARENT / 'floorplan_qspi_gap.yaml': 'cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925',
    PARENT / 'coarse_contract.json': 'b17a94fedafbc334bdc0721535c640fb786f4b632b1abddf487289fdb19fbda4',
    INTERFACES: '7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e',
    ALIASES: 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
}
REGION = [217.2, 107.0, 218.95, 118.5]
FACES = [
    {'block': 'xmos_core', 'region_face': 'east', 'bbox': [217.196, 107.2, 217.2, 108.7]},
    {'block': 'clock_flash_debug', 'region_face': 'north', 'bbox': [217.35, 118.5, 218.8, 118.8]},
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    for path, expected in INPUTS.items():
        if sha(path) != expected:
            raise RuntimeError(f'pinned input drift: {path}')
    floor = yaml.safe_load((PARENT / 'floorplan_qspi_gap.yaml').read_text())
    regions = floor['placement']['regions']
    regions['xmos_core'] = [190, 84, 217.2, 110.5]
    regions['xmos_core_east'] = [217.2, 84, 221.0, 107.0]
    regions['xmos_core_qspi_south'] = [218.95, 107.0, 232.0, 110.5]
    regions['clock_oscillator_handoff'] = REGION
    regions['board_integration_qspi'] = [219.2, 110.5, 223.2, 118.5]
    east_refs = {'C_XU_VDD_54', 'C_XU_VDD_50', 'C_XU_USB33', 'C_XU_VDD_45',
                 'C_XU_VDDIO_56', 'C_PLL_1U', 'C_PLL_100N',
                 'C_XU_VDD_39', 'C_XU_VDDIO_35'}
    found = set()
    for pattern in floor['placement']['patterns']:
        for ref in east_refs & set(pattern['match']):
            pattern['match'].remove(ref)
            found.add(ref)
    if found != east_refs:
        raise RuntimeError('east-cell pattern denominator drift')
    floor['placement']['patterns'].append({'match': sorted(east_refs), 'region': 'xmos_core_east'})
    # The source's modular owner remains xmos_core; only its physical cell is split.
    source = yaml.safe_load((PARENT / 'p1_source_variant.yaml').read_text())
    plan = json.loads(INTERFACES.read_text())
    xmos_refs = next(b['refs'] for b in plan['blocks'] if b['id'] == 'xmos_core')
    if not east_refs <= set(xmos_refs):
        raise RuntimeError('east physical cell is not entirely xmos_core-owned')
    rows = []
    for net in ('XTAL_IN', 'XTAL_OUT'):
        interface = next(i for i in plan['interfaces'] if i['net'] == net)
        for block in ('xmos_core', 'clock_flash_debug'):
            for pad in interface['endpoints'][block]:
                rows.append({'source_pad': pad, 'native_pad': pad, 'net': net, 'block': block})
    if len(rows) != 7 or len({r['source_pad'] for r in rows}) != 7:
        raise RuntimeError('XTAL endpoint denominator drift')
    by_block = {f['block']: f for f in FACES}
    def obligation(e):
        return {'status': 'P2_REQUIRED', **e, 'corridor_id': 'xtal_south_cap',
                'region_face': by_block[e['block']]['region_face'], 'layer': 'F.Cu',
                'to_reservation': 'xtal_handoff'}
    xtal = {'id': 'xtal_south_cap', 'owner': 'board_integration',
            'region_id': 'clock_oscillator_handoff',
            'allocation_id': 'xmos_service_escape',
            'participants': ['xmos_core', 'clock_flash_debug'],
            'faces': FACES, 'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
            'nets': ['XTAL_IN', 'XTAL_OUT'], 'reservation_id': 'xtal_handoff',
            'affected': rows, 'p2_obligations': [obligation(e) for e in rows],
            'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                  'corridor_id': 'xtal_south_cap',
                                  'reference_layer': 'In1.Cu',
                                  'proof': 'continuous_filled_reference'}}
    source['integration_corridors'].append(xtal)
    qspi = source['integration_corridors'][0]
    qspi['faces'][0]['bbox'] = [219.2, 110.2, 222.8, 110.5]
    contract = json.loads((PARENT / 'coarse_contract.json').read_text())
    allocation = next(a for a in contract['allocations'] if a['id'] == 'xmos_service_escape')
    allocation['boundary_witnesses'] = [w for w in allocation['boundary_witnesses']
                                        if w['net'] not in ('XTAL_IN', 'XTAL_OUT')]
    for e in rows:
        direction = by_block[e['block']]['region_face']
        allocation['boundary_witnesses'].append({
            'kind': 'integration_corridor_handoff', 'corridor_id': 'xtal_south_cap',
            'source': e['source_pad'], 'native': e['native_pad'], 'net': e['net'],
            'block': e['block'], 'layer': 'F.Cu', 'region_face': direction,
            'face': {'east': 'west', 'north': 'south'}[direction],
            'boundary_bbox': by_block[e['block']]['bbox'],
            'reservation_id': 'xtal_handoff', 'p2_obligation': obligation(e)})
    allocation['reservations'] = [r for r in allocation['reservations']
                                  if r['id'] != 'crystal_clock_cell']
    allocation['reservations'].append({
        'id': 'xtal_handoff', 'kind': 'integration_corridor',
        'corridor_id': 'xtal_south_cap', 'owner': 'board_integration',
        'region_id': 'clock_oscillator_handoff', 'layer': 'F.Cu',
        'bbox': REGION, 'nets': ['XTAL_IN', 'XTAL_OUT']})
    for w in allocation['boundary_witnesses']:
        if w.get('corridor_id') == 'qspi_gap' and w['block'] == 'xmos_core':
            w['boundary_bbox'] = qspi['faces'][0]['bbox']
    for r in allocation['reservations']:
        if r['id'] == 'qspi_gap_trunk':
            r['bbox'] = regions['board_integration_qspi']
    out = {'source': HERE / 'p1_source_xtal.yaml',
           'floorplan': HERE / 'floorplan_xtal.yaml',
           'contract': HERE / 'coarse_contract_xtal.json'}
    out['source'].write_text(yaml.safe_dump(source, sort_keys=False))
    out['floorplan'].write_text(yaml.safe_dump(floor, sort_keys=False))
    hashes = {'board': sha(BOARD), 'source': sha(out['source']),
              'floorplan': sha(out['floorplan']), 'interfaces': sha(INTERFACES),
              'aliases': sha(ALIASES)}
    for key, value in hashes.items():
        contract[key + '_sha256'] = value
    out['contract'].write_text(json.dumps(contract, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('checker', ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    board = checker.pcbnew.LoadBoard(str(BOARD))
    native_refs = {fp.GetReference(): fp for fp in board.GetFootprints()}
    for ref in east_refs:
        if not checker.contains(regions['xmos_core_east'],
                                checker._physical_envelope(native_refs[ref])):
            raise RuntimeError(f'{ref}: native envelope leaves east physical cell')
    outline = checker.pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise RuntimeError('native outline unavailable')
    _, pads = checker.graph.board_index(board)
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    coverage, _ = checker.graph.source_inventory(source, plan)
    failures = {}
    # Isolate the XTAL declaration to separate its native validation from QSPI.
    only_xtal = {**source, 'integration_corridors': [xtal]}
    try:
        checked = checker._integration_corridors(
            only_xtal, plan, board, outline, regions, list(board.Zones()),
            coverage, aliases, pads, {})
        owned = {}
        for item in plan['interfaces']:
            for block, source_pads in item['endpoints'].items():
                owned.setdefault((item['net'], block), set()).update(source_pads)
        reservation = next(r for r in allocation['reservations'] if r['id'] == 'xtal_handoff')
        verified = []
        for witness in allocation['boundary_witnesses']:
            if witness.get('corridor_id') != 'xtal_south_cap':
                continue
            exact = checker._coarse_witness(
                board, witness, witness['net'], owned, aliases, pads,
                outline, regions, set(source['p1_fixed_refs']), {}, checked)
            if not checker._witness_touches_reservation(exact, reservation):
                raise checker.ContractError(f'{exact["source"]}: XTAL face misses reservation')
            verified.append((exact['source'], exact['native'], exact['net'], exact['block']))
        if set(verified) != {(e['source_pad'], e['native_pad'], e['net'], e['block'])
                             for e in rows}:
            raise checker.ContractError('XTAL exact witness denominator mismatch')
        failures['xtal_only'] = {'status': 'VALID_DECLARATION',
                                 'endpoint_count': len(verified),
                                 'native_witnesses': [list(v) for v in verified]}
    except checker.ContractError as exc:
        failures['xtal_only'] = {'status': 'FAIL', 'reason': str(exc)}
    try:
        checker._integration_corridors(source, plan, board, outline, regions,
                                      list(board.Zones()), coverage, aliases, pads, {})
        failures['combined'] = {'status': 'VALID_DECLARATION'}
    except checker.ContractError as exc:
        failures['combined'] = {'status': 'FAIL', 'reason': str(exc)}
    result = checker.evaluate_coarse(
        BOARD, out['contract'], sha(out['contract']),
        source_path=out['source'], interface_path=INTERFACES,
        alias_path=ALIASES, floorplan_path=out['floorplan'],
        expected_source_sha256=hashes['source'],
        expected_interface_sha256=hashes['interfaces'],
        expected_alias_sha256=hashes['aliases'],
        expected_floorplan_sha256=hashes['floorplan'])
    if (failures['xtal_only']['status'] != 'VALID_DECLARATION' or
            failures['xtal_only']['endpoint_count'] != 7 or
            failures['combined'] != {'status': 'FAIL',
                                     'reason': 'qspi_gap: integration face lacks positive non-corner shared edge'} or
            result['status'] != 'FAIL' or result['p1_accepted'] or
            result['errors'] != [failures['combined']['reason']]):
        raise RuntimeError('XTAL schema-probe native outcome drift')
    receipt = {'kind': 'crow-xtal-source-model-schema-probe', 'schema': 1,
               'inputs': {str(k): v for k, v in INPUTS.items()},
               'outputs': {k: sha(v) for k, v in out.items()},
               'hashes': hashes, 'native_declarations': failures,
               'whole_allocation': {'status': result['status'],
                                    'errors': result['errors'],
                                    'xmos_service': next((a for a in result['allocations']
                                                         if a['id'] == 'xmos_service_escape'), None)},
               'p1_accepted': result['p1_accepted']}
    (HERE / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'native_declarations': failures,
                      'whole_status': result['status'],
                      'xmos_service': receipt['whole_allocation']['xmos_service']}, indent=2))


if __name__ == '__main__':
    run()
