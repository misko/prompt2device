#!/usr/bin/env python3
"""Measure the stale P1 native-pad witnesses on the exact current TI trial."""
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
PROJECT = HERE.parents[2]
REPO = PROJECT.parents[1]
OLD = HERE.parent / '2026-09-25-ti-unified-p1-diagnostic-sol'
TRIAL = PROJECT / '06_build/prototype_board_diagnostic/current-ti-coupled-replay-20260925/project'
BOARD = TRIAL / '04_kicad/crow_carrier.kicad_pcb'
CHECKER = REPO / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
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
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    inputs = {'board': BOARD, 'source': OLD / 'p1_requirements.yaml',
              'contract': OLD / 'coarse.json',
              'old_floor': OLD / 'floorplan.yaml',
              'interfaces': OLD / 'modular_plan.json', 'aliases': ALIASES,
              'trial_floor': TRIAL / '03_src/floorplan.yaml', 'checker': CHECKER}
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
    board = pcbnew.LoadBoard(str(BOARD))
    _, pads = helper.graph.board_index(board)
    cases = {}
    for name, repaired in (('before', False), ('native_pad_rebound', True)):
        contract = json.loads(json.dumps(original))
        changed = []
        if repaired:
            for allocation in contract['allocations']:
                for witness in allocation.get('boundary_witnesses', []):
                    if witness.get('kind') != 'unresolved_multiterminal_branch':
                        continue
                    found = pads.get(witness['native'], [])
                    if len(found) != 1 or found[0].GetNetname() != witness['net']:
                        raise RuntimeError(f"native pad mismatch: {witness['native']}")
                    actual = list(helper.box_mm(found[0].GetBoundingBox()))
                    if witness['boundary_bbox'] != actual:
                        changed.append({'source': witness['source'], 'native': witness['native'],
                                        'from': witness['boundary_bbox'], 'to': actual})
                        witness['boundary_bbox'] = actual
        contract.update(board_sha256=sha(BOARD), source_sha256=sha(source),
                        floorplan_sha256=sha(floor_path),
                        interface_sha256=sha(interfaces), alias_sha256=sha(ALIASES))
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
        cases[name] = {'contract_sha256': sha(path), 'changed_native_witnesses': changed,
                       'status': result['status'], 'p1_accepted': result['p1_accepted'],
                       'allocation_status': {row['id']: row['status'] for row in result['allocations']},
                       'allocation_reasons': {row['id']: row.get('reason') for row in result['allocations']},
                       'errors': result['errors'], 'diagnostics': result['diagnostics']}
    summary = {'board_sha256': sha(BOARD), 'source_sha256': sha(source),
               'checker_sha256': sha(CHECKER),
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
