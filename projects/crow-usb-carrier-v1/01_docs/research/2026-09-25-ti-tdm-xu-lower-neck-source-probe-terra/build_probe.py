#!/usr/bin/env python3
"""Build and reject a source-owned lower TDM/XU neck on the exact TI board."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
PACKET = PROJECT / '06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
BOARD = PACKET / '04_kicad/crow_carrier.kicad_pcb'
RULES = PACKET / '03_src/rules/p1_corridor_requirements.yaml'
FLOOR = PACKET / '03_src/floorplan.yaml'
INTERFACES = PACKET / '03_src/modular_plan.json'
ALIASES = PACKET / '02_parts/USB4215-03-A/part.yaml'
BASE = PROJECT / '01_docs/research/2026-09-25-ti-adc-transition-probe/tdm-widen/candidate.json'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
BOARD_SHA = '8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10'
NETS = ['AUDIO_MCLK_1V8', 'TDM_BCLK_1V8', 'TDM_DATA_1V8', 'TDM_FSYNC_1V8']
REGION = 'board_integration_tdm_xu_lower_neck'
CORRIDOR = 'tdm_xu_lower_neck'
RESERVATION = 'tdm_xu_lower_neck_reservation'
LANE = [188.0, 94.0, 190.0, 99.84]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def endpoint_rows(interfaces):
    rows = []
    for net in NETS:
        interface = next(row for row in interfaces['interfaces'] if row['net'] == net)
        for block in ('audio_clock_tdm', 'xmos_core'):
            for pad in interface['endpoints'][block]:
                rows.append({'source_pad': pad, 'native_pad': pad, 'net': net, 'block': block})
    return rows


def face(block):
    row = {'block': block, 'region_face': 'east' if block == 'audio_clock_tdm' else 'west',
            'bbox': [187.9, 94.1, 188.0, 99.7] if block == 'audio_clock_tdm'
            else [190.0, 94.1, 190.1, 99.7]}
    if block == 'xmos_core':
        row['physical_cell_id'] = 'xmos_core'
    return row


def write_yaml(path, value):
    path.write_text(yaml.safe_dump(value, sort_keys=False))


def main():
    if sha(BOARD) != BOARD_SHA:
        raise SystemExit('exact TI board hash mismatch')
    source, floor = yaml.safe_load(RULES.read_text()), yaml.safe_load(FLOOR.read_text())
    interfaces, contract = json.loads(INTERFACES.read_text()), json.loads(BASE.read_text())
    floor['placement']['regions']['audio_clock_tdm'][2] = 188.0
    floor['placement']['regions'][REGION] = LANE
    affected = endpoint_rows(interfaces)
    expected = {(net, block) for net in NETS for block in ('audio_clock_tdm', 'xmos_core')}
    if {(row['net'], row['block']) for row in affected} != expected or len(affected) != 8:
        raise SystemExit('TDM/XU endpoint denominator drift')
    p2 = [{'status': 'P2_REQUIRED', **row, 'corridor_id': CORRIDOR,
           'region_face': 'east' if row['block'] == 'audio_clock_tdm' else 'west',
           'layer': 'F.Cu', 'to_reservation': RESERVATION,
           **({'physical_cell_id': 'xmos_core'} if row['block'] == 'xmos_core' else {})}
          for row in affected]
    source['integration_corridors'] = [{
        'id': CORRIDOR, 'owner': 'board_integration', 'region_id': REGION,
        'allocation_id': 'adc_timing_xmos_bundle',
        'participants': ['audio_clock_tdm', 'xmos_core'],
        'faces': [face('audio_clock_tdm'), face('xmos_core')],
        'layer': 'F.Cu', 'reference_layer': 'In1.Cu', 'nets': NETS,
        'reservation_id': RESERVATION, 'affected': affected,
        'p2_obligations': p2,
        'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                              'corridor_id': CORRIDOR, 'reference_layer': 'In1.Cu',
                              'proof': 'continuous_filled_reference'},
    }]
    allocation = next(row for row in contract['allocations'] if row['id'] == 'adc_timing_xmos_bundle')
    # This packet deliberately tests only the four-net lower-neck slice.  The
    # remaining timing nets retain no alternative credit here.
    allocation['boundary_witnesses'] = []
    allocation['reservations'] = []
    for row in affected:
        block = row['block']
        witness = {'source': row['source_pad'], 'native': row['native_pad'], 'net': row['net'],
                   'block': block, 'face': 'west' if block == 'audio_clock_tdm' else 'east',
                   'layer': 'F.Cu', 'boundary_bbox': face(block)['bbox'],
                   'region_face': 'east' if block == 'audio_clock_tdm' else 'west',
                   'reservation_id': RESERVATION, 'kind': 'integration_corridor_handoff',
                   'corridor_id': CORRIDOR,
                   **({'physical_cell_id': 'xmos_core'} if block == 'xmos_core' else {}),
                   'p2_obligation': next(p for p in p2 if p['source_pad'] == row['source_pad'])}
        allocation['boundary_witnesses'].append(witness)
    allocation['reservations'].append({'id': RESERVATION, 'kind': 'integration_corridor',
                                       'corridor_id': CORRIDOR, 'owner': 'board_integration',
                                       'region_id': REGION, 'layer': 'F.Cu', 'bbox': LANE,
                                       'nets': NETS})
    source_path, floor_path = HERE / 'p1_requirements.yaml', HERE / 'floorplan.yaml'
    contract_path = HERE / 'coarse.json'
    write_yaml(source_path, source); write_yaml(floor_path, floor)
    contract.update({'board_sha256': sha(BOARD), 'source_sha256': sha(source_path),
                     'interfaces_sha256': sha(INTERFACES), 'aliases_sha256': sha(ALIASES),
                     'floorplan_sha256': sha(floor_path)})
    contract_path.write_text(json.dumps(contract, indent=2) + '\n')
    command = ['python3', str(CHECKER), str(BOARD), str(contract_path), str(HERE / 'result.json'),
               '--expected-contract-sha256', sha(contract_path), '--source-requirements', str(source_path),
               '--interfaces', str(INTERFACES), '--aliases', str(ALIASES), '--floorplan', str(floor_path),
               '--expected-source-sha256', sha(source_path), '--expected-interface-sha256', sha(INTERFACES),
               '--expected-alias-sha256', sha(ALIASES), '--expected-floorplan-sha256', sha(floor_path)]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    result = json.loads((HERE / 'result.json').read_text())
    errors = result.get('errors', [])
    # The complete schema-2 denominator correctly rejects this deliberately
    # isolated four-net slice before it can credit the other ten timing nets.
    expected_error = 'adc_timing_xmos_bundle: missing per-net boundary witness'
    timing = next(row for row in result['allocations'] if row['id'] == 'adc_timing_xmos_bundle')
    if completed.returncode != 1 or expected_error not in timing.get('reason', ''):
        raise SystemExit(f'lower-neck fail-closed predicate drift: {completed.returncode} {errors} {timing}')
    receipt = {'board_sha256': sha(BOARD), 'p1_fixed_ref_count': len(source['p1_fixed_refs']),
               'lane_mm': LANE, 'endpoint_denominator': affected,
               'p2_obligations': p2, 'return_obligation': source['integration_corridors'][0]['return_obligation'],
               'source_cell_validation': 'integration corridor has no body/courtyard error; its '
                                         'four-net exact endpoint and P2 denominator was accepted',
               'complete_allocation_rejection': expected_error, 'checker_returncode': completed.returncode,
               'strict_full_bbox_blockers': {
                   'C_XU_VDD_105': [188.579999, 96.5384, 198.934524, 99.10825],
                   'C_XU_VDDIO_109': [187.222857, 98.7384, 198.934524, 101.30825],
               },
               'p1_accepted': False}
    (HERE / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
