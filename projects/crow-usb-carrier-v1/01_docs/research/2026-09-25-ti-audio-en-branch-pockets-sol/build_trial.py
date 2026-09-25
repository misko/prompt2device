#!/usr/bin/env python3
"""Build a hash-bound, no-credit AUDIO_EN pocket replay from pinned research."""
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
BASE = PROJECT / '01_docs/research/2026-09-25-ti-two-terminal-timing-sol'
BOARD = PROJECT / '01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED = {
    'board': 'd0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7',
    'floorplan': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    'interfaces': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
}
POCKETS = (
    ('audio_pd', 'quiet_power', 'R_AUDIO_PD', [22.0, 104.0, 24.5, 106.2]),
    ('audio_ic', 'quiet_power', 'U_AUDIO', [21.3, 108.2, 24.1, 110.8]),
    ('iso1', 'analog_ch1', 'U_ISO1', [21.3, 65.5, 25.3, 69.7]),
)
BRANCH_ID = 'timing_audio_en_unplaced_tree'
RESERVATION_ID = 'timing_audio_en_tree'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    paths = {'board': BOARD, 'floorplan': BASE / 'floorplan.yaml',
             'interfaces': BASE / 'modular_plan.json', 'aliases': ALIASES}
    for key, path in paths.items():
        if sha(path) != EXPECTED[key]:
            raise RuntimeError(f'{key}: pinned input drift')
    spec = importlib.util.spec_from_file_location('p1_pocket_checker', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    source = yaml.safe_load((BASE / 'p1_requirements.yaml').read_text())
    contract = json.loads((BASE / 'coarse.json').read_text())
    interfaces = json.loads(paths['interfaces'].read_text())
    floor = yaml.safe_load(paths['floorplan'].read_text())
    board = pcbnew.LoadBoard(str(BOARD))
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    _, pads = checker.graph.board_index(board)
    interface = next(i for i in interfaces['interfaces'] if i['net'] == 'AUDIO_EN')
    src_allocation = next(a for a in source['allocations'] if a['id'] == 'adc_timing_xmos_bundle')
    allocation = next(a for a in contract['allocations'] if a['id'] == 'adc_timing_xmos_bundle')
    if (src_allocation['endpoints']['AUDIO_EN'] != interface['endpoints'] or
            any('AUDIO_EN' in r['nets'] for r in allocation['reservations']) or
            'branch_owner_pockets' in source):
        raise RuntimeError('base AUDIO_EN source/contract drift')
    pocket_by_ref = {ref: ident for ident, _, ref, _ in POCKETS}
    entries = sorted(({'source_pad': source_pad,
                       'native_pad': checker.graph.native_identity(source_pad, aliases),
                       'net': 'AUDIO_EN', 'block': block,
                       **({'branch_owner_pocket_id': pocket_by_ref[source_pad.rsplit('.', 1)[0]]}
                          if source_pad.rsplit('.', 1)[0] in pocket_by_ref else {})}
                      for block, names in interface['endpoints'].items() for source_pad in names),
                     key=lambda e: e['source_pad'])
    native = [fp.GetReference() + '.' + pad.GetNumber()
              for fp in board.GetFootprints() for pad in fp.Pads()
              if pad.GetNetname() == 'AUDIO_EN']
    if len(entries) != 11 or len(native) != 11 or set(native) != {e['native_pad'] for e in entries}:
        raise RuntimeError('exact AUDIO_EN 11-terminal denominator drift')
    source['branch_owner_pockets'] = [
        {'id': ident, 'owner_block': owner, 'refs': [ref], 'bbox': box,
         'branch_ids': [BRANCH_ID], 'board_sha256': EXPECTED['board'],
         'floorplan_sha256': EXPECTED['floorplan'], 'alias_sha256': EXPECTED['aliases']}
        for ident, owner, ref, box in POCKETS]
    regions = floor['placement']['regions']
    blockers = []
    for e in entries:
        pocket = next((p for p in source['branch_owner_pockets']
                       if p['id'] == e.get('branch_owner_pocket_id')), None)
        box = checker.box_mm(pads[e['native_pad']][0].GetBoundingBox())
        home = pocket['bbox'] if pocket else regions[e['block']]
        if not checker.contains(home, box):
            raise RuntimeError(f"{e['source_pad']}: location remains outside owner")
        foreign = sorted(name for name, region in regions.items()
                         if name != e['block'] and checker.intersects(box, region))
        if foreign:
            blockers.append({'source_pad': e['source_pad'], 'native_pad': e['native_pad'],
                             'block': e['block'], 'foreign_regions': foreign})
    if not any(b['source_pad'] == 'R_AUDIO_PU.2' and 'input_buck' in b['foreign_regions']
               for b in blockers):
        raise RuntimeError('R_AUDIO_PU foreign-region debt disappeared')
    duties = [{'status': 'P2_REQUIRED', **e, 'branch_id': BRANCH_ID,
               'layer': 'F.Cu', 'proof': 'native_pad_to_unplaced_tree'} for e in entries]
    source.setdefault('unresolved_multiterminal_branches', []).append({
        'id': BRANCH_ID, 'owner': 'board_integration',
        'allocation_id': 'adc_timing_xmos_bundle', 'net': 'AUDIO_EN',
        'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
        'reservation_id': RESERVATION_ID, 'endpoints': entries,
        'terminal_count': 11, 'minimum_tree_edges': 10,
        'physical_blockers': blockers, 'capacity_slots': None,
        'p2_obligations': duties,
        'tree_obligation': {'status': 'P3_REQUIRED', 'net': 'AUDIO_EN',
                            'terminal_count': 11, 'minimum_tree_edges': 10,
                            'proof': 'one_connected_native_net_without_unrelated_branches'},
        'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                              'branch_id': BRANCH_ID, 'reference_layer': 'In1.Cu',
                              'proof': 'continuous_filled_reference_under_actual_tree'}})
    rep = next(e for e in entries if e['source_pad'] == 'R_AUDIO_PD.1')
    allocation['boundary_witnesses'].append({
        'kind': 'unresolved_multiterminal_branch', 'branch_id': BRANCH_ID,
        'source': rep['source_pad'], 'native': rep['native_pad'], 'net': 'AUDIO_EN',
        'block': rep['block'], 'branch_owner_pocket_id': rep['branch_owner_pocket_id'],
        'layer': 'F.Cu', 'face': 'north',
        'boundary_bbox': list(checker.box_mm(pads[rep['native_pad']][0].GetBoundingBox())),
        'reservation_id': RESERVATION_ID,
        'p2_obligation': next(d for d in duties if d['source_pad'] == rep['source_pad'])})
    allocation['reservations'].append({'id': RESERVATION_ID,
                                       'kind': 'unresolved_multiterminal_branch',
                                       'branch_id': BRANCH_ID, 'layer': 'F.Cu',
                                       'nets': ['AUDIO_EN']})
    return source, contract, blockers


def main():
    source, contract, blockers = build()
    req, coarse = HERE / 'p1_requirements.yaml', HERE / 'coarse.json'
    floor, iface = BASE / 'floorplan.yaml', BASE / 'modular_plan.json'
    req.write_text(yaml.safe_dump(source, sort_keys=False))
    contract.update(board_sha256=sha(BOARD), source_sha256=sha(req),
                    floorplan_sha256=sha(floor))
    coarse.write_text(json.dumps(contract, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('p1_pocket_checker', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    result = checker.evaluate_coarse(BOARD, coarse, sha(coarse), source_path=req,
                                    interface_path=iface, alias_path=ALIASES,
                                    floorplan_path=floor,
                                    expected_source_sha256=sha(req),
                                    expected_interface_sha256=sha(iface),
                                    expected_alias_sha256=sha(ALIASES),
                                    expected_floorplan_sha256=sha(floor),
                                    diagnose_all=True)
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    timing = next(r for r in result['allocations'] if r['id'] == 'adc_timing_xmos_bundle')
    branch = next((r for r in timing.get('reservations', []) if r['id'] == RESERVATION_ID), None)
    if (result['p1_accepted'] or result['routing_realized'] or branch is None or
            branch['status'] != 'INCOMPLETE' or branch['capacity_slots'] is not None or
            branch['physical_blockers'] != blockers or
            len(branch['p2_obligations']) != 11 or
            branch['return_obligation']['reference_layer'] != 'In1.Cu' or
            branch['tree_obligation']['minimum_tree_edges'] != 10):
        raise RuntimeError('AUDIO_EN no-credit checker replay failed: ' + str(result['errors'][:4]))
    print(json.dumps({'status': result['status'], 'p1_accepted': False,
                      'timing_status': timing['status'], 'global_errors': len(result['errors']),
                      'physical_blockers': blockers, 'board_sha256': sha(BOARD),
                      'source_sha256': sha(req), 'contract_sha256': sha(coarse)}, indent=2))


if __name__ == '__main__':
    main()
