"""Hash-bound isolated ADC7 portal replay on the reviewed four-part board."""
from __future__ import annotations

import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / 'skills/kicad-pcb/scripts'))
import p1_corridor_capacity as checker  # noqa: E402
import pcbnew  # noqa: E402

CROW = ROOT / 'projects/crow-usb-carrier-v1'
BASE = CROW / '01_docs/research/2026-09-25-ti-usb-linked-two-physical-sol'
THREE = CROW / '01_docs/research/2026-09-25-ti-adc7-local-osc-probe-sol/candidate.kicad_pcb'
FOUR = CROW / '01_docs/research/2026-09-25-ti-adc7-four-part-margin-sol/candidate.kicad_pcb'
ALIASES = CROW / '02_parts/USB4215-03-A/part.yaml'
EXPECTED = {
    'three_part_board': 'c9b758d69867b274f0592bd2eceb9a26d64a80dd2daafa8ab9516d23d5925502',
    'four_part_board': '046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0',
    'portal': 'f1952e27cebd1eb3fa3b1ebc4863ed7d408f4b04d603a8c76454a063eff719ae',
    'base_source': '6fa9b9aee4a1651a1e2f75c4d629d077b29504f4033b6062f6fb25187c0d3fcf',
    'interfaces': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'floorplan': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
    'merged_source': '553b062a963f139cac9a9d987635861e56849dc040fc2602f9be8891a12ea9d7',
    'four_part_contract': '409f8221f8afcbdd372b9bd46912dffdb34f8e415f56538afbf4e22ea5e7e357',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def portal_clearance(board_path, area):
    board = pcbnew.LoadBoard(str(board_path))
    candidates = []
    for fp in board.GetFootprints():
        shapes = [checker._physical_envelope(fp)] + [checker.box_mm(p.GetBoundingBox())
                                                     for p in fp.Pads()]
        for shape in shapes:
            dx = max(shape[0] - area[2], area[0] - shape[2], 0)
            dy = max(shape[1] - area[3], area[1] - shape[3], 0)
            candidates.append((round(math.hypot(dx, dy), 6), fp.GetReference()))
    gap, ref = min(candidates)
    y_audio = next(fp for fp in board.GetFootprints() if fp.GetReference() == 'Y_AUDIO')
    return {'nearest_ref': ref, 'nearest_physical_or_pad_gap_mm': gap,
            'Y_AUDIO_physical_bbox_mm': list(checker._physical_envelope(y_audio)),
            'Y_AUDIO_to_portal_y85_mm': round(checker._physical_envelope(y_audio)[1] - area[3], 6)}


def main():
    paths = {'three_part_board': THREE, 'four_part_board': FOUR,
             'portal': HERE / 'portal.yaml', 'base_source': BASE / 'p1_requirements.yaml',
             'interfaces': BASE / 'modular_plan.json', 'floorplan': BASE / 'floorplan.yaml',
             'aliases': ALIASES}
    for label, path in paths.items():
        if digest(path) != EXPECTED[label]:
            raise SystemExit(f'{label} SHA-256 drift')
    portal = yaml.safe_load(paths['portal'].read_text())
    source = yaml.safe_load(paths['base_source'].read_text())
    source.update(portal)
    contract = json.loads((BASE / 'coarse.json').read_text())
    with tempfile.TemporaryDirectory() as temp:
        source_path = Path(temp) / 'source.yaml'
        contract_path = Path(temp) / 'coarse.json'
        source_path.write_text(yaml.safe_dump(source, sort_keys=False))
        contract.update(board_sha256=digest(FOUR), source_sha256=digest(source_path))
        contract_path.write_text(json.dumps(contract, sort_keys=True))
        if digest(source_path) != EXPECTED['merged_source'] or digest(contract_path) != EXPECTED['four_part_contract']:
            raise SystemExit('merged source/contract SHA-256 drift')
        result = checker.evaluate_coarse(
            FOUR, contract_path, digest(contract_path), source_path=source_path,
            interface_path=paths['interfaces'], alias_path=ALIASES,
            floorplan_path=paths['floorplan'],
            expected_source_sha256=digest(source_path),
            expected_interface_sha256=digest(paths['interfaces']),
            expected_alias_sha256=digest(ALIASES),
            expected_floorplan_sha256=digest(paths['floorplan']))
    expected_conflict = 'adc7_local_portal: overlaps ordinary reservation analog_5_8'
    if (result['status'] != 'FAIL' or result['errors'] != [expected_conflict] or
            result['p1_accepted'] or result['routing_realized'] or
            result.get('access_only_portals')):
        raise SystemExit('four-part full contract did not fail on exact ordinary reservation overlap')
    board = pcbnew.LoadBoard(str(FOUR))
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise SystemExit('native outline missing')
    interfaces = json.loads(paths['interfaces'].read_text())
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    floorplan = yaml.safe_load(paths['floorplan'].read_text())
    coverage, _ = checker.graph.source_inventory(source, interfaces)
    _, pads = checker.graph.board_index(board)
    checked = checker._access_only_portals(
        source, interfaces, board, outline, floorplan['placement']['regions'],
        list(board.Zones()), coverage, aliases, pads)
    if (len(checked) != 1 or checked[0]['status'] != 'INCOMPLETE' or
            checked[0]['capacity_slots'] is not None or
            len(checked[0]['p2_obligations']) != 8):
        raise SystemExit('local portal geometry/endpoint debt check failed')
    native_terminals = sorted((e['net'], e['native_pad']) for e in portal['access_only_portals'][0]['affected'])
    area = checked[0]['bbox']
    receipt = {
        'hashes': {**{label: digest(path) for label, path in paths.items()},
                   'merged_source': EXPECTED['merged_source'],
                   'four_part_contract': EXPECTED['four_part_contract']},
        'status': result['status'], 'errors': result['errors'],
        'p1_accepted': result['p1_accepted'], 'routing_realized': result['routing_realized'],
        'local_portal_screen': {'id': checked[0]['id'], 'status': checked[0]['status'],
                   'bbox_mm': area, 'capacity_slots': checked[0]['capacity_slots'],
                   'p2_obligation_count': len(checked[0]['p2_obligations']),
                   'return_obligation': checked[0]['return_obligation'],
                   'exact_native_terminals': native_terminals},
        'three_part_margin': portal_clearance(THREE, area),
        'four_part_margin': portal_clearance(FOUR, area),
    }
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
