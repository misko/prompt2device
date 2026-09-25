#!/usr/bin/env python3
"""Rerun Terra's full 569-ref census on the isolated Q_PRE source board."""
from __future__ import annotations
import importlib.util, json, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
TERRA=ROOT/'projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-global-owner-census-terra'
BOARD=HERE/'candidate.kicad_pcb'
BOARD_SHA='e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef'

def main():
    spec=importlib.util.spec_from_file_location('global_census',TERRA/'census.py')
    census=importlib.util.module_from_spec(spec);spec.loader.exec_module(census)
    census.BOARD=BOARD;census.EXPECTED_BOARD_SHA256=BOARD_SHA
    with tempfile.TemporaryDirectory(prefix='crow-qpre-census-') as output_dir:
        census.HERE=Path(output_dir)
        census.main()
        candidate=json.loads((Path(output_dir)/'receipt.json').read_text())
    baseline=json.loads((TERRA/'receipt.json').read_text())
    if (baseline['counts']['cross_owner_native_interaction_pairs']!=1 or
            candidate['counts']['cross_owner_native_interaction_pairs']!=0 or
            candidate['cross_owner_native_interactions'] or
            any(candidate['counts'][k]!=baseline['counts'][k] for k in baseline['counts']
                if k!='cross_owner_native_interaction_pairs')):
        raise SystemExit('unexpected census delta')
    candidate['exclusive_rectangular_physical_cell_result']={
        'cross_owner_native_interaction_cleared':True,
        'current_rectangles_exclusive':False,
        'source_only_feasibility':'UNPROVED',
        'reason':'The single courtyard-corner collision is gone; 115 refs remain outside their primary owner rectangles and 139 refs still enter foreign planning regions. Fixed connector/pocket and other source authority debt remains.'}
    (HERE/'census_result.json').write_text(json.dumps(candidate,indent=2,sort_keys=True)+'\n')
    delta={'schema':1,'kind':'global-native-owner-census-delta',
           'board_sha256':BOARD_SHA,
           'baseline_cross_owner_pairs':1,'candidate_cross_owner_pairs':0,
           'baseline_cross_owner_body_pairs':0,'candidate_cross_owner_body_pairs':0,
           'baseline_cross_owner_pad_pairs':0,'candidate_cross_owner_pad_pairs':0,
           'other_counts_unchanged':True,
           'remaining_outside_owner_refs':candidate['counts']['outside_owner'],
           'remaining_foreign_planning_refs':candidate['counts']['foreign_planning_refs']}
    (HERE/'census_delta.json').write_text(json.dumps(delta,indent=2,sort_keys=True)+'\n')
    print(json.dumps(delta,indent=2,sort_keys=True))

if __name__=='__main__':main()
