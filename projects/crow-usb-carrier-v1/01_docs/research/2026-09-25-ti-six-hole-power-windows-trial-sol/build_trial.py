#!/usr/bin/env python3
"""Rebuild the no-credit six-hole power-window contract diagnostic."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
PRIOR = PROJECT / '01_docs/research/2026-09-25-ti-current-three-pose-p1-diagnostic-sol'
TRIAL = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-six-20260925/project'
BOARD = TRIAL / '04_kicad/crow_carrier.kicad_pcb'
TRIAL_FLOOR = TRIAL / '03_src/floorplan.yaml'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
REBINDER = ROOT / 'skills/pcb-design/scripts/integration_candidate.py'
EXPECTED = {
    'board': '009ecf6383f07129653758fdc0855c793d8915e4ae5b0980278e7a5fa4fc47c7',
    'source': '8bb5f71b36f6723005bf2a346ddba8acb00d530fd5cd5787128e0c27ca297749',
    'contract': 'cdf20223e49b6e491eec76ca3b95182bcc6b4b4fa67727af20e5ef1971e216cc',
    'floor': '747745f88af6b1f1db939ad650327c64ace3cce2d4ddeceebe114b70678e6e6b',
    'trial_floor': '770ef46d377cf35cd4c7432d46ca7c17ffa5bfc42278bade7ea6ae9cc4482630',
    'interfaces': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
    'checker': '5c4eba1e1286c6dd69e8f553e99117ba70acdd5c45740eb9678bdf5b5a529e10',
    'rebinder': 'a0250b54ee7a8190ed01d27b8de85e30fbeb8571393be250fb1fa3043bce18c4',
}

# All proposed windows are short local faces in unowned planning space. They
# carry P2 pad-to-face debt and are not assertions that a power route fits.
WINDOWS = {
    'GND': ('west', [75, 90, 75.5, 92], [70, 90, 75, 92]),
    'N0V9': ('south', [150, 133.5, 154, 134], [150, 134, 154, 136]),
    'N12V_PROTECTED': ('south', [36, 83.5, 38, 84], [36, 84, 38, 85]),
    'N1V8': ('south', [134, 133.5, 136, 134], [134, 134, 136, 136]),
    'N3V3X': ('south', [138, 133.5, 140, 134], [138, 134, 140, 136]),
    'N3V3_ADC': ('west', [75, 98, 75.5, 100], [70, 98, 75, 100]),
    'N5V_BUCK': ('south', [160, 133.5, 164, 134], [160, 134, 164, 136]),
    'N5V_LDO_HOLD': ('south', [40, 83.5, 42, 84], [40, 84, 42, 85]),
    'PWR_EN': ('west', [75, 94, 75.5, 96], [70, 94, 75, 96]),
}
OPPOSITE = {'west': 'east', 'east': 'west', 'north': 'south', 'south': 'north'}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    paths = {'board': BOARD, 'source': PRIOR/'p1_requirements.yaml',
             'contract': PRIOR/'coarse.json', 'floor': PRIOR/'floorplan.yaml',
             'trial_floor': TRIAL_FLOOR, 'interfaces': PRIOR/'modular_plan.json',
             'aliases': ALIASES, 'checker': CHECKER, 'rebinder': REBINDER}
    for name, path in paths.items():
        if sha(path) != EXPECTED[name]:
            raise SystemExit(f'{name}: pinned input SHA drift')
    source = yaml.safe_load(paths['source'].read_text())
    contract = json.loads(paths['contract'].read_text())
    floor = yaml.safe_load(paths['floor'].read_text())
    trial_floor = yaml.safe_load(TRIAL_FLOOR.read_text())
    floor['board']['mounting_holes'] = trial_floor['board']['mounting_holes']
    floor['placement']['post_anchors'].update(trial_floor['placement']['post_anchors'])
    # H6's native courtyard begins at x=226.525. The clock cell's declared
    # members end at x=215.675, so trim only its unused east planning margin.
    if floor['placement']['regions']['clock_flash_debug'] != [190, 119.2, 232, 136]:
        raise SystemExit('clock cell source-region drift')
    floor['placement']['regions']['clock_flash_debug'] = [190, 119.2, 225, 136]
    for ref, (x, y) in zip(('H1', 'H2', 'H3', 'H4', 'H5', 'H6'),
                           trial_floor['board']['mounting_holes']['at']):
        floor['placement']['anchors'][ref] = [x, y, 0]
        source['p1_fixed_refs'].append(ref)
    if len(set(source['p1_fixed_refs'])) != len(source['p1_fixed_refs']):
        raise SystemExit('mounting fixed-ref duplicate')

    allocation = next(x for x in contract['allocations']
                      if x['id'] == 'power_boundary_windows')
    reservations = {x['id']: x for x in allocation['reservations']}
    touched = set()
    for witness in allocation['boundary_witnesses']:
        net = witness['net']
        if net not in WINDOWS:
            continue
        face, boundary, reserve = WINDOWS[net]
        witness['kind'] = 'virtual_block_face'
        witness['region_id'] = witness['block']
        witness['region_face'] = face
        witness['face'] = OPPOSITE[face]
        witness['boundary_bbox'] = boundary
        witness['p2_obligation'] = {
            'status': 'P2_REQUIRED', 'source_pad': witness['source'],
            'native_pad': witness['native'], 'net': net, 'block': witness['block'],
            'region_face': face, 'layer': witness['layer'],
            'to_reservation': witness['reservation_id']}
        reservations[witness['reservation_id']]['bbox'] = reserve
        touched.add(net)
    if touched != set(WINDOWS):
        raise SystemExit(f'power denominator drift: {sorted(set(WINDOWS)-touched)}')

    source_file, floor_file = HERE/'p1_requirements.yaml', HERE/'floorplan.yaml'
    contract_file, interface_file = HERE/'coarse.json', HERE/'modular_plan.json'
    source_file.write_text(yaml.safe_dump(source, sort_keys=False))
    floor_file.write_text(yaml.safe_dump(floor, sort_keys=False))
    interface_file.write_bytes(paths['interfaces'].read_bytes())
    contract.update(source_sha256=sha(source_file), floorplan_sha256=sha(floor_file))
    sys.path.insert(0, str(REBINDER.parent))
    from integration_candidate import propose_native_witnesses
    proposal = propose_native_witnesses(BOARD, contract)
    contract = proposal['proposed_contract']
    contract_file.write_text(json.dumps(contract, indent=2)+'\n')
    (HERE/'native_witness_rebind.json').write_text(json.dumps(
        {k: v for k, v in proposal.items() if k != 'proposed_contract'},
        indent=2, sort_keys=True)+'\n')

    spec = importlib.util.spec_from_file_location('six_hole_p1', CHECKER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    result = helper.evaluate_coarse(
        BOARD, contract_file, sha(contract_file), source_path=source_file,
        interface_path=interface_file, alias_path=ALIASES, floorplan_path=floor_file,
        expected_source_sha256=sha(source_file),
        expected_interface_sha256=sha(interface_file),
        expected_alias_sha256=sha(ALIASES),
        expected_floorplan_sha256=sha(floor_file), diagnose_all=True)
    expected_allocations = {'usb_device_pair', 'xmos_service_escape',
                            'adc_timing_xmos_bundle', 'adc_analog_boundary',
                            'power_boundary_windows'}
    if (result['status'] != 'INCOMPLETE' or result['p1_accepted'] or
            result['routing_realized'] or result.get('errors') or
            result.get('diagnostics') or
            {x['id'] for x in result['allocations']} != expected_allocations or
            any(x['status'] != 'INCOMPLETE' for x in result['allocations']) or
            len(next(x for x in result['allocations']
                     if x['id'] == 'power_boundary_windows')['reservations']) != 10):
        raise SystemExit('six-hole full P1 diagnostic shape drift')
    (HERE/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    summary = {'board_sha256': sha(BOARD), 'source_sha256': sha(source_file),
               'contract_sha256': sha(contract_file), 'status': result['status'],
               'p1_accepted': result['p1_accepted'],
               'routing_realized': result['routing_realized'],
               'errors': result.get('errors', []),
               'diagnostics': result.get('diagnostics', []),
               'allocations': {x['id']: {'status': x['status'],
                                         'reason': x.get('reason')}
                               for x in result.get('allocations', [])},
               'proposed_windows': WINDOWS}
    (HERE/'issues.json').write_text(json.dumps(summary, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': result['status'], 'errors': result.get('errors', []),
                      'diagnostics': result.get('diagnostics', []),
                      'allocations': summary['allocations']}, indent=2))


if __name__ == '__main__':
    main()
