#!/usr/bin/env python3
"""Research-only AUDIO_EN pull-up/input_buck region recut replay."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pcbnew
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BASE = PROJECT / '01_docs/research/2026-09-25-ti-audio-en-branch-pockets-sol'
BOARD = PROJECT / '01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb'
INTERFACES = PROJECT / '01_docs/research/2026-09-25-ti-two-terminal-timing-sol/modular_plan.json'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED = {
    'board': 'd0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7',
    'interfaces': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sha(BOARD) != EXPECTED['board'] or sha(INTERFACES) != EXPECTED['interfaces']:
        raise SystemExit('board/modular owner hash drift')
    spec = importlib.util.spec_from_file_location('audio_pocket_base', BASE / 'build_trial.py')
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    source, contract, old_blockers = base.build()
    if old_blockers != [{'source_pad': 'R_AUDIO_PU.2', 'native_pad': 'R_AUDIO_PU.2',
                         'block': 'quiet_power', 'foreign_regions': ['input_buck']}]:
        raise SystemExit('baseline AUDIO_EN blocker drift')
    floor = yaml.safe_load((base.BASE / 'floorplan.yaml').read_text())
    regions = floor['placement']['regions']
    if regions['input_buck'] != [25, 85, 70, 110]:
        raise SystemExit('input_buck source rectangle drift')
    regions['input_buck'] = [27, 85, 70, 110]
    board = pcbnew.LoadBoard(str(BOARD))
    native = {fp.GetReference(): fp for fp in board.GetFootprints()}
    interfaces = json.loads(INTERFACES.read_text())
    owner = next(b for b in interfaces['blocks'] if b['id'] == 'input_buck')
    # Every native pad already inside input_buck must remain inside the recut.
    removed_own_pads = []
    for ref in owner['refs']:
        for pad in native[ref].Pads():
            box = [pcbnew.ToMM(pad.GetBoundingBox().GetLeft()),
                   pcbnew.ToMM(pad.GetBoundingBox().GetTop()),
                   pcbnew.ToMM(pad.GetBoundingBox().GetRight()),
                   pcbnew.ToMM(pad.GetBoundingBox().GetBottom())]
            if box[0] < 27 and box[2] > 25 and box[1] < 110 and box[3] > 85:
                removed_own_pads.append(f'{ref}.{pad.GetNumber()}')
    if removed_own_pads:
        raise SystemExit('input_buck owner pads in removed strip: ' + str(removed_own_pads))
    floor_path = HERE / 'floorplan.yaml'
    floor_path.write_text(yaml.safe_dump(floor, sort_keys=False))
    for pocket in source['branch_owner_pockets']:
        pocket['floorplan_sha256'] = sha(floor_path)
    branch = next(r for r in source['unresolved_multiterminal_branches']
                  if r['id'] == base.BRANCH_ID)
    branch['physical_blockers'] = []
    source_path = HERE / 'p1_requirements.yaml'
    source_path.write_text(yaml.safe_dump(source, sort_keys=False))
    contract['floorplan_sha256'] = sha(floor_path)
    contract['source_sha256'] = sha(source_path)
    coarse_path = HERE / 'coarse.json'
    coarse_path.write_text(json.dumps(contract, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('audio_region_checker', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    removed_own_envelopes = []
    for ref in owner['refs']:
        box = checker._physical_envelope(native[ref])
        if checker.intersects(box, [25, 85, 27, 110]):
            removed_own_envelopes.append(ref)
    if removed_own_envelopes:
        raise SystemExit('input_buck owner envelopes in removed strip: ' + str(removed_own_envelopes))
    pullup = checker._physical_envelope(native['R_AUDIO_PU'])
    if checker.intersects(pullup, regions['input_buck']):
        raise SystemExit('R_AUDIO_PU full native envelope remains in input_buck')
    neighboring = [(ref, checker._physical_envelope(fp)) for ref, fp in native.items()
                   if ref != 'R_AUDIO_PU']
    collided = [ref for ref, box in neighboring if checker.intersects(pullup, box)]
    if collided:
        raise SystemExit('R_AUDIO_PU native envelope collision: ' + str(collided))
    result = checker.evaluate_coarse(BOARD, coarse_path, sha(coarse_path),
                                     source_path=source_path, interface_path=INTERFACES,
                                     alias_path=ALIASES, floorplan_path=floor_path,
                                     expected_source_sha256=sha(source_path),
                                     expected_interface_sha256=sha(INTERFACES),
                                     expected_alias_sha256=sha(ALIASES),
                                     expected_floorplan_sha256=sha(floor_path),
                                     diagnose_all=True)
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    timing = next(a for a in result['allocations'] if a['id'] == 'adc_timing_xmos_bundle')
    reservation = next(r for r in timing['reservations'] if r['id'] == base.RESERVATION_ID)
    if (result['status'] != 'INCOMPLETE' or result['errors'] or result['p1_accepted'] or
            result['routing_realized'] or reservation['status'] != 'INCOMPLETE' or
            reservation['physical_blockers'] or reservation['capacity_slots'] is not None or
            len(reservation['p2_obligations']) != 11 or
            reservation['tree_obligation']['terminal_count'] != 11 or
            reservation['tree_obligation']['minimum_tree_edges'] != 10 or
            reservation['return_obligation']['reference_layer'] != 'In1.Cu'):
        raise SystemExit('no-credit AUDIO_EN checker replay drift: ' + str(result['errors'][:4]))
    receipt = {
        'board_sha256': sha(BOARD), 'floorplan_sha256': sha(floor_path),
        'source_sha256': sha(source_path), 'coarse_sha256': sha(coarse_path),
        'interface_sha256': sha(INTERFACES), 'checker_sha256': sha(CHECKER),
        'native_refs': len(native), 'input_buck_removed_owner_pads': removed_own_pads,
        'input_buck_removed_owner_envelopes': removed_own_envelopes,
        'r_audio_pu_envelope_mm': pullup,
        'r_audio_pu_to_recut_input_buck_gap_mm': round(27 - pullup[2], 3),
        'r_audio_pu_native_envelope_collisions': collided,
        'changed_region': {'before': [25, 85, 70, 110], 'after': [27, 85, 70, 110]},
        'status': result['status'], 'global_errors': result['errors'],
        'timing_status': timing['status'], 'audio_reservation_status': reservation['status'],
        'audio_physical_blockers': reservation['physical_blockers'],
        'audio_terminal_count': reservation['tree_obligation']['terminal_count'],
        'p1_accepted': result['p1_accepted'], 'routing_realized': result['routing_realized'],
    }
    (HERE / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
