#!/usr/bin/env /usr/bin/python3
"""One scratch-only Crow reset two-corridor source/checker experiment."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[5]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BASE = PROJECT / '01_docs/research/2026-09-25-ti-expanded-locked-p1-sol'
BOARD = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
OUT = Path('/tmp/crow-reset-two-corridor-single-candidate-sol')
PINS = {'board':'fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16',
        'source':'e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92',
        'floor':'8a805d92d4f57c3a0db00a45d1c9aef57958eb0c219d44f9ca89e5531021d8b4',
        'contract':'9faaed39333c0db45c188003d2ac6bacc69562f259f8332d0d6a79db7d25037f',
        'interfaces':'02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
        'aliases':'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e'}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def member(pad, block):
    return {'source_pad':pad,'native_pad':pad,'net':'XU_RESET_N','block':block}


def obligation(endpoint, corridor, face, reservation, cell=None):
    out = {'status':'P2_REQUIRED',**endpoint,'corridor_id':corridor,
           'region_face':face,'layer':'F.Cu','to_reservation':reservation}
    if cell: out['physical_cell_id'] = cell
    return out


def witness(endpoint, corridor, face, bbox, reservation, cell=None):
    out = {'kind':'integration_corridor_handoff','corridor_id':corridor,
           'source':endpoint['source_pad'],'native':endpoint['native_pad'],
           'net':'XU_RESET_N','block':endpoint['block'],
           'face':{'north':'south','south':'north','east':'west','west':'east'}[face],
           'layer':'F.Cu','region_face':face,'boundary_bbox':bbox,
           'reservation_id':reservation,
           'p2_obligation':obligation(endpoint,corridor,face,reservation,cell)}
    if cell: out['physical_cell_id'] = cell
    return out


def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=OUT,
                        help='new empty scratch directory; candidate geometry is unchanged')
    OUT=parser.parse_args().out
    paths={'board':BOARD,'source':BASE/'p1_requirements.yaml','floor':BASE/'floorplan.yaml',
           'contract':BASE/'coarse.json','interfaces':BASE/'modular_plan.json','aliases':ALIASES}
    assert {key:sha(path) for key,path in paths.items()} == PINS
    assert OUT.exists() is False, f'{OUT} exists: preserve the one-candidate output'
    OUT.mkdir()
    source=yaml.safe_load(paths['source'].read_text())
    floor=yaml.safe_load(paths['floor'].read_text())
    contract=json.loads(paths['contract'].read_text())
    service=next(a for a in source['allocations'] if a['id']=='xmos_service_escape')
    represented={pad for owners in service['endpoints']['XU_RESET_N'].values() for pad in owners}
    assert represented=={'J_JTAG.10','R_XU_RST_PU.2','U_CORE_OK.1','U_XU_3V3_OK.6','U_XU.38'}
    old=source['unresolved_multiterminal_branches']
    assert len([x for x in old if x['net']=='XU_RESET_N'])==1
    source['unresolved_multiterminal_branches']=[x for x in old if x['net']!='XU_RESET_N']
    jtag=next(x for x in source['integration_corridors'] if x['id']=='jtag_strip')
    jtag['nets'].append('XU_RESET_N')
    jfixed=member('J_JTAG.10','debug_connector'); jxu=member('U_XU.38','xmos_core')
    jtag['affected'] += [jfixed,jxu]
    jtag['p2_obligations'] += [obligation(jfixed,'jtag_strip','south','jtag_strip_trunk'),
                               obligation(jxu,'jtag_strip','north','jtag_strip_trunk','xmos_core_east')]
    jd=next(d for d in service['demands'] if d['id']=='jtag_four')
    jd['nets'].append('XU_RESET_N');jd.update(id='jtag_plus_reset',slots=5,required_width_mm=2.25)
    floor['placement']['regions']['board_integration_reset']=[185,100,190,110.5]
    gap_endpoints=[member(p,'digital_power') for p in ('R_XU_RST_PU.2','U_CORE_OK.1','U_XU_3V3_OK.6')]+[jxu]
    new={'id':'reset_power_gap','owner':'board_integration','region_id':'board_integration_reset',
         'allocation_id':'xmos_service_escape','participants':['digital_power','xmos_core'],
         'faces':[{'block':'digital_power','region_face':'east','bbox':[184.7,100.1,185,110.3]},
                  {'block':'xmos_core','physical_cell_id':'xmos_core','region_face':'west',
                   'bbox':[190,100.1,190.3,110.3]}],
         'layer':'F.Cu','reference_layer':'In1.Cu','nets':['XU_RESET_N'],
         'reservation_id':'reset_power_trunk','affected':gap_endpoints,
         'p2_obligations':[obligation(e,'reset_power_gap',
             'east' if e['block']=='digital_power' else 'west','reset_power_trunk',
             'xmos_core' if e['block']=='xmos_core' else None) for e in gap_endpoints],
         'return_obligation':{'status':'P2_REQUIRED','net':'GND','corridor_id':'reset_power_gap',
                              'reference_layer':'In1.Cu','proof':'continuous_filled_reference'}}
    source['integration_corridors'].append(new)
    row=next(a for a in contract['allocations'] if a['id']=='xmos_service_escape')
    row['boundary_witnesses']=[w for w in row['boundary_witnesses']
                               if not (w.get('net')=='XU_RESET_N' and w.get('kind')=='unresolved_multiterminal_branch')]
    row['reservations']=[r for r in row['reservations'] if r['id']!='reset_unresolved_tree']
    next(r for r in row['reservations'] if r['id']=='jtag_strip_trunk')['nets'].append('XU_RESET_N')
    row['reservations'].append({'id':'reset_power_trunk','kind':'integration_corridor',
        'corridor_id':'reset_power_gap','owner':'board_integration','region_id':'board_integration_reset',
        'layer':'F.Cu','bbox':[185,100,190,110.5],'nets':['XU_RESET_N']})
    seg=[[221.175,47.89,225.09,48.04],[221.175,48.04,221.325,65]]
    row['reservations'].append({'id':'jtag_access_10','kind':'fixed_connector_access_segmented',
        'corridor_id':'jtag_strip','layer':'F.Cu','bbox':[221.175,47.89,225.09,65],
        'segments':seg,'nets':['XU_RESET_N']})
    row['boundary_witnesses'] += [witness(jxu,'jtag_strip','north',[221.1,84,223.9,84.3],
                                          'jtag_strip_trunk','xmos_core_east')]
    row['boundary_witnesses'].append({'kind':'fixed_connector_access_segmented',
        'corridor_id':'jtag_strip','source':'J_JTAG.10','native':'J_JTAG.10',
        'net':'XU_RESET_N','block':'debug_connector','face':'east','layer':'F.Cu',
        'region_face':'south','boundary_bbox':[225.09,46.57,225.83,49.36],
        'reservation_id':'jtag_access_10',
        'p2_obligation':obligation(jfixed,'jtag_strip','south','jtag_strip_trunk')})
    for e in gap_endpoints:
        face='east' if e['block']=='digital_power' else 'west'
        bbox=[184.7,100.1,185,110.3] if face=='east' else [190,100.1,190.3,110.3]
        row['boundary_witnesses'].append(witness(e,'reset_power_gap',face,bbox,'reset_power_trunk',
                                                  'xmos_core' if face=='west' else None))
    source_path=OUT/'p1_requirements.yaml';floor_path=OUT/'floorplan.yaml'
    source_path.write_text(yaml.safe_dump(source,sort_keys=False))
    floor_path.write_text(yaml.safe_dump(floor,sort_keys=False))
    contract.update(source_sha256=sha(source_path),floorplan_sha256=sha(floor_path))
    contract_path=OUT/'coarse.json';contract_path.write_text(json.dumps(contract,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('scratch_p1',CHECKER)
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    result=checker.evaluate_coarse(BOARD,contract_path,sha(contract_path),
        source_path=source_path,interface_path=paths['interfaces'],alias_path=ALIASES,
        floorplan_path=floor_path,expected_source_sha256=sha(source_path),
        expected_interface_sha256=sha(paths['interfaces']),expected_alias_sha256=sha(ALIASES),
        expected_floorplan_sha256=sha(floor_path),diagnose_all=True)
    (OUT/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    summary={'status':result['status'],'errors':result.get('errors',[]),
             'service':next((a for a in result['allocations'] if a['id']=='xmos_service_escape'),None),
             'diagnostics':[d for d in result.get('diagnostics',[]) if d.get('allocation')=='xmos_service_escape'],
             'sha256':{'board':PINS['board'],'source':sha(source_path),'floor':sha(floor_path),
                       'contract':sha(contract_path)}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))


if __name__=='__main__':main()
