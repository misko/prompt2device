#!/usr/bin/env python3
"""Hash-pinned no-credit P1 replay of the single expanded locked board."""
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
PRIOR = PROJECT / '01_docs/research/2026-09-25-ti-six-hole-power-windows-trial-sol'
PRIVATE = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925'
BOARD = PRIVATE / '04_kicad/crow_carrier.kicad_pcb'
NATIVE_FLOOR = PRIVATE / '03_src/floorplan.yaml'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
REBINDER = ROOT / 'skills/pcb-design/scripts/integration_candidate.py'
EXPECTED = {
    'board': 'fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16',
    'native_floor': '2f7843ada9eb08d19d268f0d6671079a8cf367629b2b3331119088927415b634',
    'source': 'e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92',
    'contract': '6609dfb1a54febabf274a61353b9403078476c27b11ef67f31dd2e74ffda6ddf',
    'floor': '6a897a1db71a4aa6166a69252bfd56bc7ff40908af4b5da4de9fbfdc3bd66dc1',
    'interfaces': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
    'checker': '5c4eba1e1286c6dd69e8f553e99117ba70acdd5c45740eb9678bdf5b5a529e10',
    'rebinder': 'a0250b54ee7a8190ed01d27b8de85e30fbeb8571393be250fb1fa3043bce18c4',
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    paths = {'board': BOARD, 'native_floor': NATIVE_FLOOR,
             'source': PRIOR/'p1_requirements.yaml', 'contract': PRIOR/'coarse.json',
             'floor': PRIOR/'floorplan.yaml', 'interfaces': PRIOR/'modular_plan.json',
             'aliases': ALIASES, 'checker': CHECKER, 'rebinder': REBINDER}
    for name, path in paths.items():
        if sha(path) != EXPECTED[name]:
            raise SystemExit(f'{name}: pinned input SHA drift')
    source_file = HERE/'p1_requirements.yaml'
    interface_file = HERE/'modular_plan.json'
    source_file.write_bytes(paths['source'].read_bytes())
    interface_file.write_bytes(paths['interfaces'].read_bytes())
    floor = yaml.safe_load(paths['floor'].read_text())
    native = yaml.safe_load(NATIVE_FLOOR.read_text())
    floor['board']['outline'] = native['board']['outline']
    floor['board']['mounting_holes'] = native['board']['mounting_holes']
    floor['placement']['post_anchors'].update(native['placement']['post_anchors'])
    for key in ('analog_ch1', 'analog_ch5', 'clock_flash_debug'):
        floor['placement']['regions'][key] = native['placement']['regions'][key]
    for index, (x, y) in enumerate(native['board']['mounting_holes']['at'], 1):
        floor['placement']['anchors'][f'H{index}'] = [x, y, 0]
    floor_file = HERE/'floorplan.yaml'
    floor_file.write_text(yaml.safe_dump(floor, sort_keys=False))

    contract = json.loads(paths['contract'].read_text())
    prior_power = next(row for row in contract['allocations']
                       if row['id'] == 'power_boundary_windows')
    prior_windows = [(w['source'], w['boundary_bbox'])
                     for w in prior_power['boundary_witnesses']]
    prior_reservations = [(r['id'], r['bbox']) for r in prior_power['reservations']]
    contract.update(source_sha256=sha(source_file), floorplan_sha256=sha(floor_file))
    sys.path.insert(0, str(REBINDER.parent))
    from integration_candidate import propose_native_witnesses
    proposal = propose_native_witnesses(BOARD, contract)
    contract = proposal['proposed_contract']
    current_power = next(row for row in contract['allocations']
                         if row['id'] == 'power_boundary_windows')
    if ([(w['source'], w['boundary_bbox']) for w in current_power['boundary_witnesses']]
            != prior_windows or
            [(r['id'], r['bbox']) for r in current_power['reservations']]
            != prior_reservations):
        raise SystemExit('nine power windows changed during native rebind')
    contract_file = HERE/'coarse.json'
    contract_file.write_text(json.dumps(contract, indent=2)+'\n')
    (HERE/'native_witness_rebind.json').write_text(json.dumps(
        {k: v for k, v in proposal.items() if k != 'proposed_contract'},
        indent=2, sort_keys=True)+'\n')
    spec = importlib.util.spec_from_file_location('expanded_locked_p1', CHECKER)
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
            {row['id'] for row in result['allocations']} != expected_allocations or
            any(row['status'] != 'INCOMPLETE' for row in result['allocations'])):
        raise SystemExit('full expanded-board P1 diagnostic shape drift')
    (HERE/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    receipt = {'status': result['status'], 'p1_accepted': result['p1_accepted'],
               'routing_realized': result['routing_realized'],
               'board_sha256': sha(BOARD), 'source_sha256': sha(source_file),
               'floorplan_sha256': sha(floor_file),
               'contract_sha256': sha(contract_file),
               'power_witness_count': len(prior_windows),
               'unchanged_virtual_power_windows': sum(
                   w.get('kind') == 'virtual_block_face'
                   for w in prior_power['boundary_witnesses']),
               'errors': result.get('errors', []),
               'diagnostics': result.get('diagnostics', []),
               'allocations': {row['id']: row['status']
                               for row in result.get('allocations', [])}}
    (HERE/'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
