#!/usr/bin/env python3
"""Build a source-only unresolved five-terminal Crow reset branch."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BASE = HERE.parent / 'jtag_segmented_packet'
BOARD = Path('/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb')
INTERFACES = PROJECT / '03_src/modular_plan.json'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
PINS = {'debug_connector':['J_JTAG.10'],
        'digital_power':['R_XU_RST_PU.2','U_CORE_OK.1','U_XU_3V3_OK.6'],
        'xmos_core':['U_XU.38']}
PINNED = {
    'board':'fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27',
    'source':'b6ed302ba2ee2462dbc39de5ac1e851c528e9897478325aee0657e2e68d87799',
    'floorplan':'1a05e7247604519d3c69b0d311ac607b7c63ba959973c2672ae43763974ce569',
    'contract':'03e91be3e2c77a91d7ce8268d35681f52e5db44be550dd9f75643f298d688416',
    'interfaces':'7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e',
    'aliases':'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
    'checker':'2aa98dea8a963d20a32213461bcaab2a81044f688685830f54cda08aa3eca044',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    paths = {'board':BOARD,'source':BASE/'p1_source_jtag.yaml',
             'floorplan':BASE/'floorplan_jtag.yaml','contract':BASE/'coarse_jtag.json',
             'interfaces':INTERFACES,'aliases':ALIASES,'checker':CHECKER}
    for key,path in paths.items():
        if sha(path)!=PINNED[key]:
            raise RuntimeError(f'{key} input hash drift')
    source = yaml.safe_load(paths['source'].read_text())
    floorplan = yaml.safe_load(paths['floorplan'].read_text())
    contract = json.loads(paths['contract'].read_text())
    interfaces = json.loads(INTERFACES.read_text())
    record = next(x for x in interfaces['interfaces'] if x['net']=='XU_RESET_N')
    if record['endpoints']!=PINS:
        raise RuntimeError('five exact reset endpoints / owners drift')
    endpoints = [{'source_pad':p,'native_pad':p,'net':'XU_RESET_N','block':block}
                 for block,pins in PINS.items() for p in pins]
    endpoints.sort(key=lambda e:e['source_pad'])
    branch_id = 'xu_reset_five_terminal'
    reservation_id = 'reset_unresolved_tree'
    obligations = [{'status':'P2_REQUIRED',**e,'branch_id':branch_id,
                    'layer':'F.Cu','proof':'native_pad_to_unplaced_tree'} for e in endpoints]
    blockers = [
        {'source_pad':'R_XU_RST_PU.2','native_pad':'R_XU_RST_PU.2',
         'block':'digital_power','foreign_regions':['audio_clock_tdm']},
        {'source_pad':'U_XU_3V3_OK.6','native_pad':'U_XU_3V3_OK.6',
         'block':'digital_power','foreign_regions':['audio_clock_tdm']},
    ]
    branch = {'id':branch_id,'owner':'board_integration',
              'allocation_id':'xmos_service_escape','net':'XU_RESET_N',
              'layer':'F.Cu','reference_layer':'In1.Cu',
              'reservation_id':reservation_id,'terminal_count':5,
              'minimum_tree_edges':4,'endpoints':endpoints,
              'physical_blockers':blockers,'p2_obligations':obligations,
              'tree_obligation':{'status':'P3_REQUIRED','net':'XU_RESET_N',
                  'terminal_count':5,'minimum_tree_edges':4,
                  'proof':'one_connected_native_net_without_unrelated_branches'},
              'return_obligation':{'status':'P2_REQUIRED','net':'GND',
                  'branch_id':branch_id,'reference_layer':'In1.Cu',
                  'proof':'continuous_filled_reference_under_actual_tree'}}
    source['unresolved_multiterminal_branches'] = [branch]
    allocation = next(a for a in contract['allocations'] if a['id']=='xmos_service_escape')
    old = [w for w in allocation['boundary_witnesses'] if w['net']=='XU_RESET_N']
    if len(old)!=1 or old[0]['source']!='U_XU.38':
        raise RuntimeError('legacy reset witness drift')
    allocation['boundary_witnesses'] = [w for w in allocation['boundary_witnesses']
                                        if w['net']!='XU_RESET_N']
    old_res = [r for r in allocation['reservations'] if 'XU_RESET_N' in r['nets']]
    if len(old_res)!=1 or old_res[0]['id']!='reset_unresolved':
        raise RuntimeError('legacy reset reservation drift')
    allocation['reservations'] = [r for r in allocation['reservations']
                                  if r['id']!='reset_unresolved']
    spec = importlib.util.spec_from_file_location('p1_corridor_capacity',CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    board = checker.pcbnew.LoadBoard(str(BOARD))
    native = next(p for fp in board.GetFootprints() if fp.GetReference()=='U_XU'
                  for p in fp.Pads() if p.GetNumber()=='38')
    witness = {'kind':'unresolved_multiterminal_branch','branch_id':branch_id,
               'source':'U_XU.38','native':'U_XU.38','net':'XU_RESET_N',
               'block':'xmos_core','face':'north','layer':'F.Cu',
               'boundary_bbox':list(checker.box_mm(native.GetBoundingBox())),
               'reservation_id':reservation_id,
               'p2_obligation':next(o for o in obligations if o['source_pad']=='U_XU.38')}
    allocation['boundary_witnesses'].insert(8,witness)
    allocation['reservations'].append({'id':reservation_id,
        'kind':'unresolved_multiterminal_branch','branch_id':branch_id,
        'layer':'F.Cu','nets':['XU_RESET_N']})
    source_path = HERE/'p1_source_reset.yaml'
    floor_path = HERE/'floorplan_reset.yaml'
    contract_path = HERE/'coarse_reset.json'
    source_path.write_text(yaml.safe_dump(source,sort_keys=False))
    floor_path.write_text(yaml.safe_dump(floorplan,sort_keys=False))
    contract.update(source_sha256=sha(source_path),floorplan_sha256=sha(floor_path))
    contract_path.write_text(json.dumps(contract,indent=2)+'\n')
    _, native_pads = checker.graph.board_index(board)
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    coverage,networks = checker.graph.source_inventory(source,interfaces)
    if len(networks)!=59 or coverage!=checker.CROW_COVERAGE:
        raise RuntimeError('full 59-net denominator drift')
    branches = checker._unresolved_branches(source,interfaces,board,
        floorplan['placement']['regions'],coverage,aliases,native_pads)
    if set(branches)!={branch_id}:
        raise RuntimeError('branch source validation drift')
    result = checker.evaluate_coarse(BOARD,contract_path,sha(contract_path),
        source_path=source_path,interface_path=INTERFACES,alias_path=ALIASES,
        floorplan_path=floor_path,expected_source_sha256=sha(source_path),
        expected_interface_sha256=sha(INTERFACES),expected_alias_sha256=sha(ALIASES),
        expected_floorplan_sha256=sha(floor_path))
    service = next(a for a in result['allocations'] if a['id']=='xmos_service_escape')
    expected_errors = ['qspi_gap: integration affected endpoint/layer denominator mismatch',
                       'jtag_strip: integration affected endpoint/layer denominator mismatch',
                       'xu_reset_five_terminal: unresolved branch representative witness denominator mismatch']
    if (result['status']!='FAIL' or result['p1_accepted'] or result['routing_realized'] or
            service.get('reason')!='U_XU.34: witness bbox is a nonlocal bridge across source region' or
            result['errors']!=expected_errors):
        raise RuntimeError('whole packet rejection outcome drift')
    receipt = {'status':'UNRESOLVED_MULTITERMINAL_BRANCH_INCOMPLETE',
        'p1_accepted':False,'p2_proven':False,'p3_proven':False,
        'board_sha256':sha(BOARD),'source_sha256':sha(source_path),
        'floorplan_sha256':sha(floor_path),'contract_sha256':sha(contract_path),
        'checker_sha256':sha(CHECKER),'full_net_denominator':len(networks),
        'branch':branch,'native_pad_bbox':witness['boundary_bbox'],
        'whole_packet_status':result['status'],'whole_service_allocation':service,
        'whole_packet_errors':result['errors'],'routing_realized':result['routing_realized']}
    (HERE/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'branch':receipt['status'],'whole':result['status'],
        'service':service,'errors':result['errors']},indent=2))


if __name__=='__main__':
    main()
