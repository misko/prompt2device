#!/usr/bin/env python3
"""Rebuild the exact no-credit unified P1 packet on the AUDIO_EN trial board."""
from __future__ import annotations
import importlib.util, json, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
P = ROOT / 'projects/crow-usb-carrier-v1'
UPSTREAM = P / '01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol'
BOARD = HERE / 'candidate.kicad_pcb'

def main():
    spec = importlib.util.spec_from_file_location('unified_builder', UPSTREAM/'build_trial.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    with tempfile.TemporaryDirectory(prefix='crow-audio-unified-') as d:
        base = Path(d)
        for name in ('p1_requirements.yaml','coarse.json','modular_plan.json'):
            (base/name).symlink_to(builder.BASE/name)
        (base/'floorplan.yaml').write_bytes((HERE/'source_floorplan.yaml').read_bytes())
        builder.HERE = HERE
        builder.BASE = base
        builder.BOARD = BOARD
        builder.EXPECTED['board'] = 'f1f491c22b20c853fc9d208265237364cbcec3992e4818759281eaa32fc69eac'
        builder.EXPECTED['floorplan'] = '1c7149d9a104ea954b5df9ac98dd4249329efd24481c36af6cdbf39fb02d09f5'
        builder.EXPECTED['checker'] = 'b4ece816b23bcc1f213a6e66253d4aa2dfe1a1358a5a74aaaea40fd8a36bab95'
        try:
            builder.main()
        except SystemExit as exc:
            if str(exc) != 'full fail-closed diagnostic shape drift':
                raise
        sys.path.insert(0,str(ROOT/'skills/kicad-pcb/scripts'))
        import p1_corridor_capacity as checker
        paths = {name: HERE/name for name in ('coarse.json','p1_requirements.yaml',
                                               'modular_plan.json','floorplan.yaml')}
        aliases = P/'02_parts/USB4215-03-A/part.yaml'
        result = checker.evaluate_coarse(
            BOARD,paths['coarse.json'],builder.sha(paths['coarse.json']),
            source_path=paths['p1_requirements.yaml'],interface_path=paths['modular_plan.json'],
            alias_path=aliases,floorplan_path=paths['floorplan.yaml'],
            expected_source_sha256=builder.sha(paths['p1_requirements.yaml']),
            expected_interface_sha256=builder.sha(paths['modular_plan.json']),
            expected_alias_sha256=builder.sha(aliases),
            expected_floorplan_sha256=builder.sha(paths['floorplan.yaml']),diagnose_all=True)
        if (result['status']!='FAIL' or result['p1_accepted'] or result['routing_realized'] or
                len(result['errors'])!=10 or len(result['diagnostics'])!=9 or
                not any('timing_audio_en_unplaced_tree' in s for s in result['errors'])):
            raise SystemExit('unexpected unified no-credit diagnostic shape')
        (HERE/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'status':result['status'],'errors':len(result['errors']),
                          'diagnostics':len(result['diagnostics']),
                          'board_sha256':builder.sha(BOARD),
                          'source_sha256':builder.sha(paths['p1_requirements.yaml']),
                          'contract_sha256':builder.sha(paths['coarse.json'])},indent=2))

if __name__=='__main__':main()
