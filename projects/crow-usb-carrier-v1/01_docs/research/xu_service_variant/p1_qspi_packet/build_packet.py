#!/usr/bin/env python3
"""Build and evaluate an exact-source, research-only QSPI corridor packet."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BOARD = Path('/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb')
GAP_FLOORPLAN = Path('/tmp/crow-xu-qspi-gap-sol/project/03_src/floorplan.yaml')
PINNED = {
    'board': 'fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27',
    'floorplan': 'cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925',
    'source': '9ef85e5f4918dea0378203a97fa631ce2e73a690170235902a97a6c8e30527d8',
    'interfaces': '7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
}
SOURCE = PROJECT / '03_src/rules/p1_corridor_requirements.yaml'
INTERFACES = PROJECT / '03_src/modular_plan.json'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CANDIDATE = PROJECT / '01_docs/research/2026-09-24-p1-unified-coarse-candidate-sol.json'
NETS = ['QSPI_CLK', 'QSPI_CS_N', 'QSPI_D0', 'QSPI_D1', 'QSPI_D2', 'QSPI_D3']
REGION = [199.8, 110.5, 223.2, 118.5]
FACES = [
    {'block': 'xmos_core', 'region_face': 'south', 'bbox': [219.0, 110.2, 222.8, 110.5]},
    {'block': 'clock_flash_debug', 'region_face': 'north', 'bbox': [219.0, 118.5, 222.8, 118.8]},
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def demand(path: Path, expected: str) -> None:
    actual = sha(path)
    if actual != expected:
        raise RuntimeError(f'{path}: expected {expected}, got {actual}')


def run() -> None:
    inputs = {'board': BOARD, 'floorplan': GAP_FLOORPLAN, 'source': SOURCE,
              'interfaces': INTERFACES, 'aliases': ALIASES}
    for name, path in inputs.items():
        demand(path, PINNED[name])
    floorplan = yaml.safe_load(GAP_FLOORPLAN.read_text())
    if floorplan['placement']['regions']['board_integration_qspi'] != REGION:
        raise RuntimeError('gap corridor region drift')
    source = yaml.safe_load(SOURCE.read_text())
    interfaces = json.loads(INTERFACES.read_text())
    endpoint_rows = []
    for net in NETS:
        interface = next(item for item in interfaces['interfaces'] if item['net'] == net)
        for block in ('xmos_core', 'clock_flash_debug'):
            for source_pad in interface['endpoints'][block]:
                endpoint_rows.append({'source_pad': source_pad, 'native_pad': source_pad,
                                      'net': net, 'block': block})
    if len(endpoint_rows) != 13 or len({e['source_pad'] for e in endpoint_rows}) != 13:
        raise RuntimeError('QSPI endpoint denominator drift')
    faces = {face['block']: face for face in FACES}
    def obligation(endpoint):
        return {'status': 'P2_REQUIRED', **endpoint, 'corridor_id': 'qspi_gap',
                'region_face': faces[endpoint['block']]['region_face'],
                'layer': 'F.Cu', 'to_reservation': 'qspi_gap_trunk'}
    corridor = {'id': 'qspi_gap', 'owner': 'board_integration',
                'region_id': 'board_integration_qspi', 'allocation_id': 'xmos_service_escape',
                'participants': ['xmos_core', 'clock_flash_debug'],
                'faces': FACES, 'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
                'nets': NETS, 'reservation_id': 'qspi_gap_trunk',
                'affected': endpoint_rows,
                'p2_obligations': [obligation(e) for e in endpoint_rows],
                'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                      'corridor_id': 'qspi_gap', 'reference_layer': 'In1.Cu',
                                      'proof': 'continuous_filled_reference'}}
    source['integration_corridors'] = [corridor]
    candidate = json.loads(CANDIDATE.read_text())
    allocation = next(item for item in candidate['allocations']
                      if item['id'] == 'xmos_service_escape')
    allocation['boundary_witnesses'] = [w for w in allocation['boundary_witnesses']
                                        if w['net'] not in NETS]
    for endpoint in endpoint_rows:
        block = endpoint['block']
        region_face = faces[block]['region_face']
        allocation['boundary_witnesses'].append({
            'kind': 'integration_corridor_handoff', 'corridor_id': 'qspi_gap',
            'source': endpoint['source_pad'], 'native': endpoint['native_pad'],
            'net': endpoint['net'], 'block': block, 'layer': 'F.Cu',
            'region_face': region_face,
            'face': 'north' if region_face == 'south' else 'south',
            'boundary_bbox': faces[block]['bbox'],
            'reservation_id': 'qspi_gap_trunk',
            'p2_obligation': obligation(endpoint)})
    allocation['reservations'] = [r for r in allocation['reservations']
                                  if r['id'] != 'qspi_cross_cell']
    allocation['reservations'].insert(0, {
        'id': 'qspi_gap_trunk', 'kind': 'integration_corridor', 'corridor_id': 'qspi_gap',
        'owner': 'board_integration', 'region_id': 'board_integration_qspi',
        'layer': 'F.Cu', 'bbox': REGION, 'nets': NETS})
    # The old crystal diagnostic enters the new exclusive corridor by 0.7 mm.
    # Trim it to the clock-cell edge; this does not make its old witness valid.
    crystal = next(r for r in allocation['reservations'] if r['id'] == 'crystal_clock_cell')
    crystal['bbox'][1] = REGION[3]
    for witness in allocation['boundary_witnesses']:
        if witness['reservation_id'] == 'crystal_clock_cell':
            witness['boundary_bbox'][3] = REGION[3]
    source_out = HERE / 'p1_source_variant.yaml'
    floorplan_out = HERE / 'floorplan_qspi_gap.yaml'
    contract_out = HERE / 'coarse_contract.json'
    source_out.write_text(yaml.safe_dump(source, sort_keys=False))
    shutil.copyfile(GAP_FLOORPLAN, floorplan_out)
    hashes = {'board': sha(BOARD), 'source': sha(source_out),
              'interfaces': sha(INTERFACES), 'aliases': sha(ALIASES),
              'floorplan': sha(floorplan_out)}
    for name, value in hashes.items():
        candidate[name + '_sha256'] = value
    candidate.pop('status', None)
    candidate.pop('p1_accepted', None)
    candidate.pop('routing_realized', None)
    contract_out.write_text(json.dumps(candidate, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('p1_corridor_capacity',
        ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    board = checker.pcbnew.LoadBoard(str(BOARD))
    outline = checker.pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise RuntimeError('native outline unavailable')
    _, native_pads = checker.graph.board_index(board)
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    coverage, _ = checker.graph.source_inventory(source, interfaces)
    corridors = checker._integration_corridors(
        source, interfaces, board, outline, floorplan['placement']['regions'],
        list(board.Zones()), coverage, aliases, native_pads, {})
    if set(corridors) != {'qspi_gap'}:
        raise RuntimeError('exact corridor source validation drift')
    owned_pads = {}
    for item in interfaces['interfaces']:
        for block, source_pads in item['endpoints'].items():
            owned_pads.setdefault((item['net'], block), set()).update(source_pads)
    target = next(r for r in allocation['reservations'] if r['id'] == 'qspi_gap_trunk')
    checked = []
    for witness in allocation['boundary_witnesses']:
        if witness.get('kind') != 'integration_corridor_handoff':
            continue
        exact = checker._coarse_witness(
            board, witness, witness['net'], owned_pads, aliases, native_pads,
            outline, floorplan['placement']['regions'], set(source['p1_fixed_refs']),
            {}, corridors)
        if not checker._witness_touches_reservation(exact, target):
            raise RuntimeError(f'{exact["source"]}: integration face does not touch reservation')
        checked.append((exact['source'], exact['native'], exact['net'], exact['block']))
    if len(checked) != 13 or set(checked) != {
            (e['source_pad'], e['native_pad'], e['net'], e['block']) for e in endpoint_rows}:
        raise RuntimeError('exact QSPI witness denominator drift')
    (HERE / 'qspi_declaration_validation.json').write_text(json.dumps({
        'status': 'INCOMPLETE_SOURCE_GEOMETRY', 'board_sha256': hashes['board'],
        'source_sha256': hashes['source'], 'corridor_id': 'qspi_gap',
        'validated_native_endpoint_count': len(checked), 'net_count': len(NETS),
        'p2_pad_to_face_obligation_count': len(corridor['p2_obligations']),
        'filled_gnd_return_proven': False, 'effective_capacity_proven': False,
        'whole_allocation_validated': False}, indent=2) + '\n')
    result = checker.evaluate_coarse(
        BOARD, contract_out, sha(contract_out), source_path=source_out,
        interface_path=INTERFACES, alias_path=ALIASES, floorplan_path=floorplan_out,
        expected_source_sha256=hashes['source'],
        expected_interface_sha256=hashes['interfaces'],
        expected_alias_sha256=hashes['aliases'],
        expected_floorplan_sha256=hashes['floorplan'])
    if (result['status'] != 'FAIL' or result['p1_accepted'] or
            result['errors'] != ['qspi_gap: integration affected endpoint/layer denominator mismatch'] or
            len(result['allocations']) != 5 or
            next(a for a in result['allocations'] if a['id'] == 'xmos_service_escape')['reason'] !=
            'U_XU.51: witness bbox is a nonlocal bridge across source region'):
        raise RuntimeError('exact Crow rejection outcome drift')
    (HERE / 'evaluation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'errors': result['errors'],
                      'xmos_service_escape': next((a for a in result['allocations']
                                                  if a['id'] == 'xmos_service_escape'), None),
                      'hashes': hashes}, indent=2))


if __name__ == '__main__':
    run()
