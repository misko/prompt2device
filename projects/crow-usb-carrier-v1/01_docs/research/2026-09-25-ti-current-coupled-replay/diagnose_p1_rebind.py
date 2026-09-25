#!/usr/bin/env python3
"""Measure the stale P1 native-pad witnesses on the exact current TI trial."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import yaml

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO / 'skills/pcb-design/scripts'))
from integration_candidate import propose_native_witnesses, summarize_p1_findings
OLD = HERE.parent / '2026-09-25-ti-unified-p1-diagnostic-sol'
TRIAL = PROJECT / '06_build/prototype_board_diagnostic/current-ti-coupled-replay-20260925/project'
BOARD = TRIAL / '04_kicad/crow_carrier.kicad_pcb'
CHECKER = REPO / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
AUDIO_BOARD = PROJECT / '06_build/prototype_board_diagnostic/current-ti-audio-en-three-pose-20260925/project/04_kicad/crow_carrier.kicad_pcb'
OUT = PROJECT / '06_build/prototype_board_diagnostic/current-ti-p1-rebind-scratch-20260925'
EXPECTED = {
    'board': 'bdd5bccb2617d7bbe1de9cd27cda1a0e2f68467bedd169704473a010286a948b',
    'source': 'f6f132891712bfcb1cec4d1df6714748337040ba5c42ae3fecd14fb9c35d1222',
    'contract': '18936dc3f3dd6e01637182b2dab57cb472a31bfa2eb345a20bd4f7867708777f',
    'old_floor': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    'interfaces': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
    'trial_floor': 'c773e0703b79b7c37350e54da34ecf39da8148e2476996b6d1990126db55efa0',
    'checker': '5c4eba1e1286c6dd69e8f553e99117ba70acdd5c45740eb9678bdf5b5a529e10',
    'audio_board': '0bd3ac8dd8c80177958c009a0644f0bc723bcee7ad7085c2fb76c09c5df958f5',
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    inputs = {'board': BOARD, 'source': OLD / 'p1_requirements.yaml',
              'contract': OLD / 'coarse.json',
              'old_floor': OLD / 'floorplan.yaml',
              'interfaces': OLD / 'modular_plan.json', 'aliases': ALIASES,
              'trial_floor': TRIAL / '03_src/floorplan.yaml', 'checker': CHECKER,
              'audio_board': AUDIO_BOARD}
    observed = {name: sha(path) for name, path in inputs.items()}
    if observed != EXPECTED:
        raise RuntimeError(f'input drift: {observed}')
    OUT.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('p1_rebind_checker', CHECKER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = OLD / 'p1_requirements.yaml'
    interfaces = OLD / 'modular_plan.json'
    floor = yaml.safe_load((OLD / 'floorplan.yaml').read_text())
    current_floor = yaml.safe_load((TRIAL / '03_src/floorplan.yaml').read_text())
    # Retain the old diagnostic's source regions; only native poses are rebound.
    floor['placement']['post_anchors'] = current_floor['placement']['post_anchors']
    floor_path = OUT / 'floorplan.yaml'
    floor_path.write_text(yaml.safe_dump(floor, sort_keys=False))
    original = json.loads((OLD / 'coarse.json').read_text())
    proposal = propose_native_witnesses(BOARD, original)
    cases = {}
    for name, repaired in (('before', False), ('native_pad_rebound', True)):
        contract = json.loads(json.dumps(original))
        changed = []
        if repaired:
            contract = proposal['proposed_contract']
            changed = [{'source': row['source'], 'native': row['native'],
                        'from': row['old_bbox'], 'to': row['proposed_bbox']}
                       for row in proposal['geometry_changes']]
        contract.update(board_sha256=sha(BOARD), source_sha256=sha(source),
                        floorplan_sha256=sha(floor_path),
                        interfaces_sha256=sha(interfaces), aliases_sha256=sha(ALIASES))
        path = OUT / f'{name}.json'
        path.write_text(json.dumps(contract, indent=2) + '\n')
        result = helper.evaluate_coarse(
            BOARD, path, sha(path), source_path=source, interface_path=interfaces,
            alias_path=ALIASES, floorplan_path=floor_path,
            expected_source_sha256=sha(source),
            expected_interface_sha256=sha(interfaces),
            expected_alias_sha256=sha(ALIASES),
            expected_floorplan_sha256=sha(floor_path), diagnose_all=True)
        if result['p1_accepted'] or result['status'] != 'FAIL':
            raise RuntimeError(f'{name}: unexpected P1 outcome')
        groups = summarize_p1_findings(result, contract)
        # The summary already keeps full raw errors and item diagnostics below.
        # Avoid copying the entire P1 allocation tree into the research packet.
        concise_groups = {key: groups[key] for key in
                          ('primary_missing_per_net_witnesses',
                           'consequent_branch_errors', 'other_findings')}
        cases[name] = {'contract_sha256': sha(path), 'changed_native_witnesses': changed,
                       'status': result['status'], 'p1_accepted': result['p1_accepted'],
                       'allocation_status': {row['id']: row['status'] for row in result['allocations']},
                       'allocation_reasons': {row['id']: row.get('reason') for row in result['allocations']},
                       'finding_groups': concise_groups,
                       'errors': result['errors'], 'diagnostics': result['diagnostics']}
    # Validate the same read-only proposal boundary on the three-pose trial,
    # and measure the known owner-containment improvement independently.
    audio_proposal = propose_native_witnesses(AUDIO_BOARD, original)
    if audio_proposal['p1_accepted'] or not audio_proposal['independent_review_required']:
        raise RuntimeError('native proposal manufactured approval')
    iface = json.loads(interfaces.read_text())
    audio_net = next(row for row in iface['interfaces'] if row['net'] == 'AUDIO_EN')
    membership = {name: owner for owner, names in audio_net['endpoints'].items() for name in names}
    audio_cases = {}
    for label, board_path in (('before', BOARD), ('three_pose', AUDIO_BOARD)):
        board = helper.pcbnew.LoadBoard(str(board_path))
        _, pads = helper.graph.board_index(board)
        actual = [fp.GetReference() + '.' + pad.GetNumber()
                  for fp in board.GetFootprints() for pad in fp.Pads()
                  if pad.GetNetname() == 'AUDIO_EN']
        if len(actual) != 11 or set(actual) != set(membership):
            raise RuntimeError('AUDIO_EN exact terminal inventory drift')
        outside = [name for name, owner in membership.items()
                   if len(pads[name]) != 1 or not helper.contains(
                       floor['placement']['regions'][owner],
                       helper.box_mm(pads[name][0].GetBoundingBox()))]
        audio_cases[label] = {'board_sha256': sha(board_path), 'terminal_count': 11,
                              'outside_owner': sorted(outside)}
    if [len(audio_cases[key]['outside_owner']) for key in ('before', 'three_pose')] != [3, 0]:
        raise RuntimeError('AUDIO_EN owner geometry improvement drift')
    grouped = cases['native_pad_rebound']['finding_groups']
    if (len(grouped['primary_missing_per_net_witnesses']),
        len(grouped['consequent_branch_errors']), len(grouped['other_findings'])) != (5, 9, 9):
        raise RuntimeError('primary/consequential diagnostic grouping drift')
    if {name: sha(path) for name, path in inputs.items()} != EXPECTED:
        raise RuntimeError('diagnostic changed an input')
    summary = {'board_sha256': sha(BOARD), 'source_sha256': sha(source),
               'checker_sha256': sha(CHECKER),
               'adapter_sha256': sha(REPO / 'skills/pcb-design/scripts/integration_candidate.py'),
               'invalidated_reviews': proposal['invalidated_reviews'],
               'audio_en_owner_probe': audio_cases,
               'expected_hashes_self_derived': True,
               'engineering_acceptance': False, 'p1_accepted': False,
               'cases': cases}
    if ([(len(cases[name]['errors']), len(cases[name]['diagnostics']))
         for name in ('before', 'native_pad_rebound')] != [(13, 10), (9, 9)] or
            [row['native'] for row in cases['native_pad_rebound']['changed_native_witnesses']]
            != ['U_XU.38']):
        raise RuntimeError('diagnostic finding set drift')
    (HERE / 'p1_rebind_comparison.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'changed': len(cases['native_pad_rebound']['changed_native_witnesses']),
                      'before': [len(cases['before'][key]) for key in ('errors', 'diagnostics')],
                      'after': [len(cases['native_pad_rebound'][key]) for key in ('errors', 'diagnostics')]},
                     indent=2))


if __name__ == '__main__':
    main()
