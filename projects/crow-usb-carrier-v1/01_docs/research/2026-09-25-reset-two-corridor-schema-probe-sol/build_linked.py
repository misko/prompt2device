#!/usr/bin/env /usr/bin/python3
"""One frozen-board scratch Crow linked reset candidate; no design mutation."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import yaml

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
PROJECT=ROOT/'projects/crow-usb-carrier-v1'
BASE=PROJECT/'01_docs/research/2026-09-25-ti-expanded-locked-p1-sol'
BOARD=PROJECT/'06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb'
ALIASES=PROJECT/'02_parts/USB4215-03-A/part.yaml'
CHECKER=ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
PINS={'board':'fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16',
      'source':'e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92',
      'floor':'8a805d92d4f57c3a0db00a45d1c9aef57958eb0c219d44f9ca89e5531021d8b4',
      'contract':'9faaed39333c0db45c188003d2ac6bacc69562f259f8332d0d6a79db7d25037f',
      'interfaces':'02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
      'aliases':'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
      'checker':'c6609198e3daa5fc9718436194945f4cb0f39f4e9095ec991674479f798e7b46'}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def endpoint(pad,owner):
    return {'source_pad':pad,'native_pad':pad,'net':'XU_RESET_N','block':owner}


def stage(ident,region,participants,faces,affected,axis,demand,fixed):
    return {'id':ident,'kind':'physical_corridor','owner':'board_integration',
        'region_id':region,'allocation_id':'xmos_service_escape','participants':participants,
        'faces':faces,'layer':'F.Cu','reference_layer':'In1.Cu','nets':['XU_RESET_N'],
        'reservation_id':ident+'_trunk','affected':affected,
        'p2_obligations':[{'status':'P2_REQUIRED',**e,'corridor_id':ident,
            'region_face':next(f['region_face'] for f in faces if f['block']==e['block']),
            'layer':'F.Cu','to_reservation':ident+'_trunk',
            **({'physical_cell_id':next(f['physical_cell_id'] for f in faces if f['block']==e['block'])}
               if any(f['block']==e['block'] and 'physical_cell_id' in f for f in faces) else {})}
            for e in affected],
        'return_obligation':{'status':'P2_REQUIRED','net':'GND','corridor_id':ident,
            'reference_layer':'In1.Cu','proof':'continuous_filled_reference'},
        'fixed_accesses':fixed,'axis':axis,'slot_pitch_mm':.45,'demand_slots':demand}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,
        default=Path('/tmp/crow-reset-linked-shared-single-sol'))
    out=parser.parse_args().out
    paths={'board':BOARD,'source':BASE/'p1_requirements.yaml','floor':BASE/'floorplan.yaml',
           'contract':BASE/'coarse.json','interfaces':BASE/'modular_plan.json',
           'aliases':ALIASES,'checker':CHECKER}
    assert {k:sha(v) for k,v in paths.items()}==PINS
    if out.exists(): raise SystemExit(f'{out} exists; choose a new scratch output')
    out.mkdir()
    source=yaml.safe_load(paths['source'].read_text())
    floor=yaml.safe_load(paths['floor'].read_text())
    contract=json.loads(paths['contract'].read_text())
    source['unresolved_multiterminal_branches']=[r for r in source['unresolved_multiterminal_branches']
        if r['net']!='XU_RESET_N']
    floor['placement']['regions']['board_integration_reset']=[185,100,190,110.5]
    jtag=next(r for r in source['integration_corridors'] if r['id']=='jtag_strip')
    jfixed=endpoint('J_JTAG.10','debug_connector')
    xu=endpoint('U_XU.38','xmos_core')
    power=[endpoint(p,'digital_power') for p in
           ('R_XU_RST_PU.2','U_CORE_OK.1','U_XU_3V3_OK.6')]
    first=stage('reset_jtag_stage','board_integration_jtag',
        ['debug_connector','xmos_core'],jtag['faces'],[jfixed,xu],'vertical',5,
        [{'source_pad':'J_JTAG.10','native_pad':'J_JTAG.10','net':'XU_RESET_N',
          'block':'debug_connector','face':'east','bbox':[221.175,47.89,225.09,65],
          'segments':[[221.175,47.89,225.09,48.04],
                      [221.175,48.04,221.325,65]]}])
    first['shared_with']='jtag_strip_trunk'
    second=stage('reset_power_stage','board_integration_reset',
        ['xmos_core','digital_power'],
        [{'block':'xmos_core','physical_cell_id':'xmos_core','region_face':'west',
          'bbox':[190,102,190.3,108]},
         {'block':'digital_power','region_face':'east','bbox':[184.7,102,185,108]}],
        [xu]+power,'horizontal',1,[])
    source['linked_paths'].append({'id':'reset_linked','allocation_id':'xmos_service_escape',
        'nets':['XU_RESET_N'],'owner_order':['debug_connector','xmos_core','digital_power'],
        'reservation_id':'reset_linked','layer':'F.Cu','reference_layer':'In1.Cu',
        'stages':[first,second],
        'joins':[{'from':'reset_jtag_stage','to':'reset_power_stage',
                  'owner':'xmos_core','net':'XU_RESET_N','source_pad':'U_XU.38',
                  'kind':'pad_anchored_physical_interstage'}],
        'terminal_count':5,'minimum_tree_edges':4,
        'tree_obligation':{'status':'P3_REQUIRED','net':'XU_RESET_N',
            'terminal_count':5,'minimum_tree_edges':4,
            'proof':'one_connected_native_net_without_unrelated_branches'}})
    row=next(r for r in contract['allocations'] if r['id']=='xmos_service_escape')
    row['boundary_witnesses']=[w for w in row['boundary_witnesses']
        if not (w.get('net')=='XU_RESET_N' and w.get('kind')=='unresolved_multiterminal_branch')]
    row['reservations']=[r for r in row['reservations'] if r['id']!='reset_unresolved_tree']
    row['linked_paths']=[{'id':'reset_linked','kind':'linked_path','nets':['XU_RESET_N'],
                          'status':'INCOMPLETE'}]
    source_path=out/'p1_requirements.yaml';floor_path=out/'floorplan.yaml'
    source_path.write_text(yaml.safe_dump(source,sort_keys=False))
    floor_path.write_text(yaml.safe_dump(floor,sort_keys=False))
    contract.update(source_sha256=sha(source_path),floorplan_sha256=sha(floor_path))
    contract_path=out/'coarse.json';contract_path.write_text(json.dumps(contract,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('linked_checker',CHECKER)
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    result=checker.evaluate_coarse(BOARD,contract_path,sha(contract_path),
        source_path=source_path,interface_path=paths['interfaces'],alias_path=ALIASES,
        floorplan_path=floor_path,expected_source_sha256=sha(source_path),
        expected_interface_sha256=sha(paths['interfaces']),expected_alias_sha256=sha(ALIASES),
        expected_floorplan_sha256=sha(floor_path),diagnose_all=True)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    summary={'status':result['status'],'errors':result['errors'],
             'service':next(r for r in result['allocations'] if r['id']=='xmos_service_escape'),
             'sha256':{'board':PINS['board'],'checker':PINS['checker'],
                       'source':sha(source_path),'floor':sha(floor_path),
                       'contract':sha(contract_path)}}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))


if __name__=='__main__':main()
