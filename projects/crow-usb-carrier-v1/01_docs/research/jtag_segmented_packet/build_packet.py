#!/usr/bin/env python3
"""Build an isolated, hash-bound fixed-pose Crow JTAG source declaration."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BASE = HERE.parent / 'xu_service_variant/p1_qspi_packet'
BOARD = Path('/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb')
INTERFACES = PROJECT / '03_src/modular_plan.json'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
PINS = [('JTAG_TMS', 'J_JTAG.2', 'U_XU.44'),
        ('JTAG_TCK', 'J_JTAG.4', 'U_XU.51'),
        ('JTAG_TDO', 'J_JTAG.6', 'U_XU.37'),
        ('JTAG_TDI', 'J_JTAG.8', 'U_XU.36')]
STRIP = [221, 65, 226, 84]
FACES = [{'block': 'debug_connector', 'region_face': 'south',
          'bbox': [221.1, 64.7, 225.9, 65]},
         {'block': 'xmos_core', 'region_face': 'north',
          'bbox': [221.1, 84, 225.9, 84.3]}]
PINNED = {
    'board': 'fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27',
    'source': '9a13c0999d29f17280bb5d8ffb98a5e0d59afe3ee4511eb004e436bffc13ece4',
    'floorplan': 'cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925',
    'contract': 'b17a94fedafbc334bdc0721535c640fb786f4b632b1abddf487289fdb19fbda4',
    'interfaces': '7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e',
    'aliases': 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
    'checker': '4060a59cd67936bcf7193114b786859f5a31aa8eeff2c49ab5f7713d970139e1',
}
# Edge-joined 0.15-mm strips follow Terra's four simultaneous native Manhattan
# centrelines (5ad7dd9b). Butt joints avoid positive-area self-overlap.
SEGMENTS = {
    'JTAG_TMS': [[230.91,47.89,231.21,48.04], [231.06,48.04,231.21,54.725],
                 [225.325,54.725,231.21,54.875], [225.325,54.875,225.475,65]],
    'JTAG_TCK': [[229.195,49.36,229.345,50.125], [224.775,50.125,229.345,50.275],
                 [224.775,50.275,224.925,54.125], [222.525,54.125,224.925,54.275],
                 [222.525,54.275,222.675,65]],
    'JTAG_TDO': [[227.925,49.36,228.075,49.825], [224.475,49.825,228.075,49.975],
                 [224.475,49.975,224.625,53.825], [221.925,53.825,224.625,53.975],
                 [221.925,53.975,222.075,65]],
    'JTAG_TDI': [[226.655,49.36,226.805,49.525], [224.175,49.525,226.805,49.675],
                 [224.175,49.675,224.325,53.525], [221.625,53.525,224.325,53.675],
                 [221.625,53.675,221.775,65]],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(name, path):
    got = sha(path)
    if got != PINNED[name]:
        raise RuntimeError(f'{name} hash drift: {got}')


def envelope(shapes):
    return [min(s[0] for s in shapes), min(s[1] for s in shapes),
            max(s[2] for s in shapes), max(s[3] for s in shapes)]


def main():
    inputs = {'board': BOARD, 'source': BASE/'p1_source_variant.yaml',
              'floorplan': BASE/'floorplan_qspi_gap.yaml',
              'contract': BASE/'coarse_contract.json',
              'interfaces': INTERFACES, 'aliases': ALIASES, 'checker': CHECKER}
    for name, path in inputs.items():
        pin(name, path)
    spec = importlib.util.spec_from_file_location('p1_corridor_capacity', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    board = checker.pcbnew.LoadBoard(str(BOARD))
    outline = checker.pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise RuntimeError('native outline unavailable')
    pads = {f'{fp.GetReference()}.{p.GetNumber()}': checker.box_mm(p.GetBoundingBox())
            for fp in board.GetFootprints() for p in fp.Pads()}
    header = board.FindFootprintByReference('J_JTAG')
    if (header.GetPosition().x/1e6, header.GetPosition().y/1e6,
            header.GetOrientationDegrees()) != (228,50,90):
        raise RuntimeError('fixed header pose drift')
    source = yaml.safe_load(inputs['source'].read_text())
    floorplan = yaml.safe_load(inputs['floorplan'].read_text())
    contract = json.loads(inputs['contract'].read_text())
    interfaces = json.loads(INTERFACES.read_text())
    regions = floorplan['placement']['regions']
    if (regions['usb_frontend'] != [200,35,236,70] or
            regions['debug_connector'] != [218,35,238,65] or
            regions['xmos_core'] != [190,84,232,110.5]):
        raise RuntimeError('source region drift')
    regions['usb_frontend'] = [200,35,238.5,40]
    regions['debug_connector'] = [221,40,238,65]
    regions['board_integration_jtag'] = STRIP
    allocation_source = next(a for a in source['allocations'] if a['id']=='xmos_service_escape')
    demand = next(d for d in allocation_source['demands'] if d['id']=='jtag_reset')
    if set(demand['nets']) != {n for n,_,_ in PINS} | {'XU_RESET_N'}:
        raise RuntimeError('JTAG/reset demand drift')
    demand.update(id='jtag_four', nets=[n for n,_,_ in PINS], slots=4, required_width_mm=1.8)
    allocation_source['demands'].insert(allocation_source['demands'].index(demand)+1,
        {'id':'reset_branch','nets':['XU_RESET_N'],'layers':['F.Cu'],
         'status':'INCOMPLETE','reason':'three-owner reset fan-in and connector branch unallocated'})
    endpoints = [{'source_pad': pad,'native_pad':pad,'net':net,'block':block}
                 for net,fixed,xu in PINS for block,pad in
                 [('debug_connector',fixed),('xmos_core',xu)]]
    face_map = {f['block']:f for f in FACES}
    def obligation(e):
        return {'status':'P2_REQUIRED',**e,'corridor_id':'jtag_strip',
                'region_face':face_map[e['block']]['region_face'],
                'layer':'F.Cu','to_reservation':'jtag_strip_trunk'}
    corridor = {'id':'jtag_strip','owner':'board_integration',
        'region_id':'board_integration_jtag','allocation_id':'xmos_service_escape',
        'participants':['debug_connector','xmos_core'],'faces':FACES,
        'layer':'F.Cu','reference_layer':'In1.Cu','nets':[n for n,_,_ in PINS],
        'reservation_id':'jtag_strip_trunk','affected':endpoints,
        'p2_obligations':[obligation(e) for e in endpoints],
        'return_obligation':{'status':'P2_REQUIRED','net':'GND',
            'corridor_id':'jtag_strip','reference_layer':'In1.Cu',
            'proof':'continuous_filled_reference'}}
    source['integration_corridors'].append(corridor)
    allocation = next(a for a in contract['allocations'] if a['id']=='xmos_service_escape')
    allocation['boundary_witnesses'] = [w for w in allocation['boundary_witnesses']
        if w['net'] not in {n for n,_,_ in PINS}]
    allocation['reservations'] = [r for r in allocation['reservations'] if r['id']!='jtag_north']
    allocation['reservations'].insert(0, {'id':'jtag_strip_trunk','kind':'integration_corridor',
        'corridor_id':'jtag_strip','owner':'board_integration','region_id':'board_integration_jtag',
        'layer':'F.Cu','bbox':STRIP,'nets':[n for n,_,_ in PINS]})
    allocation['reservations'].append({'id':'reset_unresolved','kind':'signal','layer':'F.Cu',
        'bbox':[221,84,226,91],'nets':['XU_RESET_N'],'axis':'vertical',
        'demand_slots':1,'slot_pitch_mm':.45})
    for e in endpoints:
        if e['block']=='xmos_core':
            allocation['boundary_witnesses'].append({'kind':'integration_corridor_handoff',
                'corridor_id':'jtag_strip','source':e['source_pad'],'native':e['native_pad'],
                'net':e['net'],'block':'xmos_core','face':'south','layer':'F.Cu',
                'region_face':'north','boundary_bbox':FACES[1]['bbox'],
                'reservation_id':'jtag_strip_trunk','p2_obligation':obligation(e)})
    declarations = []
    for net,fixed,xu in PINS:
        seg = SEGMENTS[net]
        e = next(e for e in endpoints if e['source_pad']==fixed)
        rid = 'jtag_access_'+fixed.rsplit('.',1)[1]
        witness = {'kind':'fixed_connector_access_segmented','corridor_id':'jtag_strip',
            'source':fixed,'native':fixed,'net':net,'block':'debug_connector',
            'face':'west' if net=='JTAG_TMS' else 'north','layer':'F.Cu',
            'region_face':'south','boundary_bbox':list(pads[fixed]),
            'reservation_id':rid,'p2_obligation':obligation(e)}
        reservation = {'id':rid,'kind':'fixed_connector_access_segmented',
            'corridor_id':'jtag_strip','layer':'F.Cu','bbox':envelope(seg),
            'segments':seg,'nets':[net]}
        allocation['boundary_witnesses'].append(witness)
        allocation['reservations'].append(reservation)
        declarations.append((witness,reservation))
    # Put the exact eight JTAG witnesses first. A whole-allocation failure at
    # the retained reset witness then cannot hide an earlier access rejection.
    allocation['boundary_witnesses'].sort(
        key=lambda w: 0 if w.get('corridor_id')=='jtag_strip' else 1)
    source_path = HERE/'p1_source_jtag.yaml'
    floor_path = HERE/'floorplan_jtag.yaml'
    contract_path = HERE/'coarse_jtag.json'
    source_path.write_text(yaml.safe_dump(source,sort_keys=False))
    floor_path.write_text(yaml.safe_dump(floorplan,sort_keys=False))
    contract.update(board_sha256=sha(BOARD),source_sha256=sha(source_path),
        floorplan_sha256=sha(floor_path),interfaces_sha256=sha(INTERFACES),
        aliases_sha256=sha(ALIASES))
    contract_path.write_text(json.dumps(contract,indent=2)+'\n')
    _, native_pads = checker.graph.board_index(board)
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    coverage, terminal_nets = checker.graph.source_inventory(source,interfaces)
    if len(terminal_nets)!=59 or len(coverage['xmos_service_escape'])!=13:
        raise RuntimeError('whole-source 59-net / XMOS-service 13-net denominator drift')
    if set(coverage) != set(checker.CROW_COVERAGE) or any(
            coverage[name] != expected for name,expected in checker.CROW_COVERAGE.items()):
        raise RuntimeError('full 59-net Crow allocation membership drift')
    corridors = checker._integration_corridors(source,interfaces,board,outline,
        regions,list(board.Zones()),coverage,aliases,native_pads,{})
    if set(corridors)!={'qspi_gap','jtag_strip'}:
        raise RuntimeError('corridor denominator drift')
    owned = {}
    for interface in interfaces['interfaces']:
        for block,items in interface['endpoints'].items():
            owned.setdefault((interface['net'],block),set()).update(items)
    fixed_refs = set(source['p1_fixed_refs'])
    xu_handoffs = []
    trunk = next(r for r in allocation['reservations'] if r['id']=='jtag_strip_trunk')
    for witness in allocation['boundary_witnesses']:
        if witness.get('kind')!='integration_corridor_handoff' or witness.get('corridor_id')!='jtag_strip':
            continue
        checked = checker._coarse_witness(board,witness,witness['net'],owned,aliases,
            native_pads,outline,regions,fixed_refs,{},corridors)
        if not checker._witness_touches_reservation(checked,trunk):
            raise RuntimeError(f"{witness['source']}: XU face misses integration strip")
        xu_handoffs.append(witness['source'])
    if set(xu_handoffs)!={x for _,_,x in PINS} or len(xu_handoffs)!=4:
        raise RuntimeError('four exact XU handoffs not checked')
    checks = []
    for witness,reservation in declarations:
        net = witness['net']
        checked = checker._coarse_witness(board,witness,net,owned,aliases,native_pads,
            outline,regions,fixed_refs,{},corridors)
        shapes = checker._fixed_access_shapes(reservation,checked,corridors['jtag_strip']['bbox'],
            checker.rectangle(regions['debug_connector'],'debug connector source region'))
        if not checker.intersects(shapes[-1],FACES[0]['bbox']):
            raise RuntimeError(f'{net}: source face missed')
        hits=[]
        for fp in board.GetFootprints():
            ref=fp.GetReference()
            if ref!='J_JTAG' and fp.GetLayerName()=='F.Cu' and any(
                    checker.intersects(s,checker._physical_envelope(fp)) for s in shapes):
                hits.append('body:'+ref)
            for pad in fp.Pads():
                name=f'{ref}.{pad.GetNumber()}'
                if name!=witness['native'] and pad.IsOnLayer(board.GetLayerID('F.Cu')) and any(
                        checker.intersects(s,checker.box_mm(pad.GetBoundingBox())) for s in shapes):
                    hits.append('pad:'+name)
        if any(item.IsOnLayer(board.GetLayerID('F.Cu')) and any(
                checker.intersects(s,checker.box_mm(item.GetBoundingBox())) for s in shapes)
                for item in board.GetTracks()):
            hits.append('existing track')
        if any(zone.GetIsRuleArea() and 'F.Cu' in {
                board.GetLayerName(i) for i in zone.GetLayerSet().Seq()} and any(
                checker.intersects(s,checker.box_mm(zone.GetBoundingBox())) for s in shapes)
                for zone in board.Zones()):
            hits.append('rule area')
        if any(not zone.GetIsRuleArea() and checker._filled_zone_intersects(
                zone,board.GetLayerID('F.Cu'),s)
                for zone in board.Zones() for s in shapes):
            hits.append('saved filled copper')
        if any(other is not reservation and other.get('layer')=='F.Cu' and
               other.get('id')!='jtag_strip_trunk' and any(
               checker.intersects(s,checker.rectangle(t,'other reservation'))
               for s in shapes for t in other.get('segments',[other['bbox']]))
               for other in allocation['reservations']):
            hits.append('other reservation')
        if hits:
            raise RuntimeError(f'{net}: native obstacle {hits}')
        checks.append({'net':net,'fixed_pad':witness['source'],'xu_pad':next(x for n,f,x in PINS if n==net),
            'physical_pad_bbox':witness['boundary_bbox'],'reservation_id':reservation['id'],
            'segments':shapes,'segment_envelope':reservation['bbox'],
            'native_obstacle_hits':hits,'status':'INCOMPLETE'})
    minimum_spacing = {}
    for index,left in enumerate(checks):
        for right in checks[index+1:]:
            spacing = min(math.hypot(max(a[0]-b[2],b[0]-a[2],0),
                                     max(a[1]-b[3],b[1]-a[3],0))
                          for a in left['segments'] for b in right['segments'])
            if spacing < .15-1e-6:
                raise RuntimeError(f"{left['net']}/{right['net']}: mutual clearance {spacing}")
            minimum_spacing[left['net']+'/'+right['net']] = round(spacing,6)
    result = checker.evaluate_coarse(BOARD,contract_path,sha(contract_path),
        source_path=source_path,interface_path=INTERFACES,alias_path=ALIASES,
        floorplan_path=floor_path,expected_source_sha256=sha(source_path),
        expected_interface_sha256=sha(INTERFACES),expected_alias_sha256=sha(ALIASES),
        expected_floorplan_sha256=sha(floor_path))
    service=next(a for a in result['allocations'] if a['id']=='xmos_service_escape')
    expected_errors = ['qspi_gap: integration affected endpoint/layer denominator mismatch',
                       'jtag_strip: integration affected endpoint/layer denominator mismatch']
    if (result['status']!='FAIL' or result['p1_accepted'] or result['routing_realized'] or
            len(result['allocations'])!=5 or service['status']!='FAIL' or
            service.get('reason')!='U_XU.38: witness bbox is a nonlocal bridge across source region' or
            result['errors']!=expected_errors):
        raise RuntimeError('whole allocation checker outcome drift')
    report={'status':'STANDALONE_JTAG_DECLARATION_INCOMPLETE','scope':'RESEARCH_ONLY',
        'p1_accepted':False,'p2_proven':False,'board_sha256':sha(BOARD),
        'checker_git_commit':'851a2efe','checker_sha256':sha(CHECKER),
        'source_sha256':sha(source_path),'floorplan_sha256':sha(floor_path),
        'contract_sha256':sha(contract_path),'full_net_denominator':len(terminal_nets),
        'allocation_net_denominator':len(coverage['xmos_service_escape']),
        'jtag_net_count':len(PINS),'jtag_endpoint_count':len(endpoints),
        'validated_xu_handoffs':xu_handoffs,
        'strip_bbox_mm':STRIP,'fixed_pose_deg':90,'fixed_access':checks,
        'pairwise_segment_spacing_mm':minimum_spacing,
        'p2_pad_to_face_obligation_count':len(corridor['p2_obligations']),
        'return_obligation':corridor['return_obligation'],
        'whole_allocation_status':result['status'],'whole_allocation':service,
        'whole_packet_errors':result['errors'],'routing_realized':result['routing_realized']}
    (HERE/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'standalone':report['status'],'whole':result['status'],
                      'service_reason':service.get('reason'),'errors':result['errors']},indent=2))


if __name__=='__main__':
    main()
