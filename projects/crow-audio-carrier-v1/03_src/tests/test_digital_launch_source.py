"""Live carrier source regressions; isolated native footprints, never a BOARD.

Live source reads are intentional: these tests must fail when the recipe loses
an endpoint, duplicates a complete-net owner, or grows a thin item outside its
explicit area. Native SHAPE_SEGMENT/Collide independently screen every new
segment's full copper and widened end against all foreign pad/seed/hole shapes.
This is source geometry, not generated P-LAND, native DRC or SI acceptance.
"""
import copy
import json
import math
import sys
import unittest
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pcbnew
import yaml

PROJECT=Path(__file__).resolve().parents[2]
REPO=PROJECT.parents[1]
sys.path.insert(0,str(REPO/'skills/kicad-pcb/scripts'))
sys.path.insert(0,str(PROJECT/'03_src'))
from test_route_source_contract import load_source, shadow_inputs
from test_local_placement_source import source_builder
from source_inventory import parse_netlist
from check_power_source import source_power_maps
from check_protection_architecture import validate as validate_protection_source
from rules_audit import parse_mm
from route_ownership_preflight import audit_config
from route_and_stitch_generic import wave_nets
from board_authority import compile_source_prep_authority
from source_geometry import (point_in_polygon, polygon_edge_distance,
                             sample_polygon_starts)

DIGITAL_PINS={'U_CLK.1','U_CLK.2','U_CLK.3','U_CLK.5','U_CLK.6','U_CLK.7',
              'U_ADC.24','U_ADC.25','U_ADC.29','U_ADC.34'}
NARROW_PINS=DIGITAL_PINS
AUDIO_CONTROL_PINS={'U_AUDIO.3','U_AUDIO.5','U_AUDIO.6','U_PWR.6'}

def vec(p): return pcbnew.VECTOR2I(*(round(x*1e6) for x in p))
def rect_shape(rect):
    x0,y0,x1,y1=rect
    return pcbnew.SHAPE_RECT(vec((x0,y0)),vec((x1,y1)))
def primitive(a,b,width): return pcbnew.SHAPE_SEGMENT(vec(a),vec(b),round(width*1e6))

def native_geometry(floor):
    source=source_builder(floor)
    comps,pins,_=parse_netlist(PROJECT/floor['project']['netlist'])
    # The exact live electrical contract owns the population after ADR0025.
    # Do not stop every geometry suite at the retired325/923 census, or
    # derive acceptance from arbitrary observed counts. Validate the source
    # first; then require one realized copper pad per declared physical pin.
    population=validate_protection_source(*source_power_maps(comps,pins))
    footprints=[]; pads=[]; holes=[]
    for ref,(fpid,_) in sorted(comps.items()):
        lib,name=fpid.split(':')
        directory=PROJECT/'03_src/lib/crow_audio_carrier.pretty' if lib=='crow_audio_carrier' else Path('/usr/share/kicad/footprints')/(lib+'.pretty')
        fp=pcbnew.FootprintLoad(str(directory),name)
        assert fp is not None,(ref,fpid)
        x,y,rot,_=source.initial_pose(ref)
        fp.SetOrientationDegrees(rot);fp.SetPosition(vec((x,y)));footprints.append(fp)
        for p in fp.Pads():
            if p.IsOnCopperLayer() and p.IsOnLayer(pcbnew.F_Cu):
                poly=p.GetEffectivePolygon(pcbnew.F_Cu).Outline(0)
                pads.append(dict(id=ref+'.'+p.GetNumber(),net=pins[(ref,p.GetNumber())],
                                 shape=p.GetEffectiveShape(pcbnew.F_Cu),at=(p.GetPosition().x/1e6,p.GetPosition().y/1e6),
                                 poly=[(poly.CPoint(i).x/1e6,poly.CPoint(i).y/1e6) for i in range(poly.PointCount())]))
            if p.GetDrillSizeX()>0:
                holes.append(dict(id=ref+'.'+p.GetNumber(),net=pins.get((ref,p.GetNumber())) if p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH else None,shape=p.GetEffectiveHoleShape()))
    for i,at in enumerate(floor['board']['mounting_holes']['at']):
        # Router source keepout is stronger than the isolated mounting drill.
        holes.append(dict(id=f'mounting-head-{i+1}',shape=pcbnew.SHAPE_CIRCLE(vec(at),pcbnew.FromMM(3.2))))
    assert len(footprints)==population['components']
    assert len(pins)==population['pins'] and len(pads)==population['pins']
    return dict(footprints=footprints,pads=pads,holes=holes,pins=pins)

def overlaps(shape,area): return shape.Collide(rect_shape(area['rect']),0)

def pair_clearance(a,b,floor,nets):
    """Existing scoped-clearance item-overlap semantics, not containment."""
    required=.25
    areas={x['name']:x for x in floor['keepouts']}
    for rule in nets.get('scoped_clearances',[]):
        # This screen always grades a seed segment, never two package pads.
        if rule.get('pads_only'): continue
        area=areas[rule['zone']]
        layer=a.get('layer',b.get('layer','F.Cu'))
        if layer not in area['layers'] or not overlaps(a['shape'],area) or not overlaps(b['shape'],area): continue
        if 'nets' in rule:
            match=a['net'] in rule['nets'] or b['net'] in rule['nets']
        else:
            match=(a['net'] in rule['nets_a'] and b['net'] in rule['nets_b']) or (b['net'] in rule['nets_a'] and a['net'] in rule['nets_b'])
        if match: required=parse_mm(rule['clearance'])
    # A scoped item overlap is not a license to squeeze a widened entry.
    # Only the two exact first corner items use full width at local clearance.
    for item in (a,b):
        if item.get('id') in DIGITAL_PINS and item.get('width',0)>=.36 and not item.get('corner_entry',False):
            required=max(required,.25)
    return required

def segment_rows(route):
    rows=[]
    for stub in route['prep']['seed_stubs']['stubs']:
        for spec_index,spec in enumerate(stub['segments']):
            for index,(a,b) in enumerate(zip(spec['pts'],spec['pts'][1:])):
                rows.append(dict(id=stub['pin'],net=stub['net'],a=a,b=b,width=spec['width'],layer=spec['layer'],shape=primitive(a,b,spec['width']),
                                 corner_entry=(stub['pin']=='U_ADC.24' or
                                               (stub['pin']=='U_ADC.25' and spec_index==index==0))))
    return rows

def audio_control_errors(floor,route,nets,geometry):
    """Simultaneously grade the adjacent monitor/control escapes and drills."""
    rows=segment_rows(route)
    targets=[r for r in rows if r['id'] in AUDIO_CONTROL_PINS]
    vias=[]
    for stub in route['prep']['seed_stubs']['stubs']:
        spec=stub.get('via',route['prep']['seed_stubs']['via'])
        for i,at in enumerate(stub.get('vias',[])):
            vias.append(dict(id=f"{stub['pin']}:via{i}",pin=stub['pin'],
                             net=stub['net'],at=at,
                             shape=primitive(at,at,spec['size']),
                             hole=primitive(at,at,spec['drill']),
                             layer='F.Cu'))
    target_vias=[v for v in vias if v['pin'] in AUDIO_CONTROL_PINS]
    failures=[]
    tolerance=2
    def collide(a,b,required,kind):
        try: hit=a['shape'].Collide(b['shape'],round(required*1e6)-tolerance)
        except TypeError: hit=b['shape'].Collide(a['shape'],round(required*1e6)-tolerance)
        if hit: failures.append((kind,a['id'],b['id']))
    for a in targets:
        if a['layer']=='F.Cu':
            for b in geometry['pads']:
                if a['net']!=b['net']:
                    collide(a,b,pair_clearance(a,b,floor,nets),'segment-pad')
        for b in rows:
            if a is not b and a['net']!=b['net'] and a['layer']==b['layer']:
                collide(a,b,pair_clearance(a,b,floor,nets),'segment-segment')
        for b in vias:
            if a['net']==b['net']: continue
            collide(a,b,pair_clearance(a,b,floor,nets),'segment-via')
            collide(a,dict(id=b['id']+':hole',shape=b['hole']),.20,'segment-hole')
    for a in target_vias:
        for b in geometry['pads']:
            if a['net']!=b['net']:
                collide(a,b,pair_clearance(a,b,floor,nets),'via-pad')
                collide(dict(id=a['id']+':hole',shape=a['hole']),b,.20,'hole-pad')
            elif a['shape'].Collide(b['shape'],0):
                failures.append(('via-in-pad',a['id'],b['id']))
        for b in rows:
            if a['net']!=b['net']:
                collide(a,b,pair_clearance(a,b,floor,nets),'via-segment')
                collide(dict(id=a['id']+':hole',shape=a['hole']),b,.20,'hole-segment')
        for b in vias:
            if a['id']==b['id'] or a['net']==b['net']:continue
            collide(a,b,pair_clearance(a,b,floor,nets),'via-via')
            collide(dict(id=a['id']+':hole',shape=a['hole']),
                    dict(id=b['id']+':hole',shape=b['hole']),
                    floor['design_rules']['hole_to_hole'],'hole-hole')
    expected={'AUDIO_CT':{'U_AUDIO.5','C_AUDIO_CT1.1','C_AUDIO_CT2.1'},
              'AUDIO_EN':{'U_AUDIO.6','R_AUDIO_PU.2'},
              'PWR_EN':{'U_AUDIO.3','U_PWR.6'}}
    for net,pin_ids in expected.items():
        nodes=[dict(id=p['id'],shape=p['shape'],layer='F.Cu',kind='pad')
               for p in geometry['pads'] if p['id'] in pin_ids]
        nodes += [dict(id=f"{r['id']}:segment{i}",shape=r['shape'],
                       layer=r['layer'],kind='segment')
                  for i,r in enumerate(rows)
                  if r['id'] in AUDIO_CONTROL_PINS and r['net']==net]
        nodes += [dict(id=v['id'],shape=v['shape'],layer=None,kind='via')
                  for v in target_vias if v['net']==net]
        reached={0};todo=[0]
        while todo:
            i=todo.pop()
            for j,b in enumerate(nodes):
                if j in reached:continue
                a=nodes[i]
                if (a['kind']=='via' or b['kind']=='via' or
                    a['layer']==b['layer']) and a['shape'].Collide(b['shape'],0):
                    reached.add(j);todo.append(j)
        found={nodes[i]['id'] for i in reached} & pin_ids
        if found!=pin_ids:
            failures.append(('incomplete-local-tree',net,
                             ','.join(sorted(pin_ids-found))))
    return sorted(set(failures))

def source_extent_errors(floor,route,nets):
    errors=[];areas={x['name']:x for x in floor['keepouts']}
    for row in segment_rows(route):
        if row['id'] not in DIGITAL_PINS or row['width']>=.36-1e-9: continue
        eligible=[areas[r['zone']] for r in nets.get('scoped_floors',[]) if row['net'] in r.get('nets',[]) and parse_mm(r['min_width'])<=row['width']]
        def contained(area):
            x0,y0,x1,y1=area['rect'];r=row['width']/2
            return row['layer'] in area['layers'] and area['deny']==[] and all(x0+r-1e-9<=x<=x1-r+1e-9 and y0+r-1e-9<=y<=y1-r+1e-9 for x,y in [row['a'],row['b']])
        if not any(contained(area) for area in eligible): errors.append(row['id'])
    return errors

def source_budget_errors(route):
    """Pre-generation source check of the existing clocks output-guard limits.

    The real realized_track_width_guard must later reopen the routed board;
    invoking that board consumer is outside this source-only task.
    """
    wave=next(w for w in route['route']['waves'] if w['name']=='clocks')
    guard=wave['realized_width']; totals={}; errors=[]
    for row in segment_rows(route):
        if row['id'] not in DIGITAL_PINS: continue
        if row['width']<guard['minimum']-1e-9:errors.append((row['net'],'floor'))
        if row['width']>=guard['nominal']-1e-9: continue
        item=totals.setdefault(row['net'],[0.,0])
        item[0]+=math.dist(row['a'],row['b']);item[1]+=1
    for net,(length,count) in totals.items():
        if length>guard['max_subnominal_length_per_net']+1e-9:errors.append((net,'length'))
        if count>guard['max_subnominal_segments_per_net']:errors.append((net,'segments'))
    return errors

def bulk_endpoint_launches(floor,route,nets,geometry):
    """One full native-shape 1mm straight .36/.25 witness per other endpoint.

    Includes all adopted and new seeds, holes and relevant keepouts. Finite
    48-direction/in-pad grid search is a launch screen, never a route solve.
    """
    rows=segment_rows(route);digital=set(nets['classes']['ADC_CLOCK']['nets'])
    result=[]
    for pad in geometry['pads']:
        if pad['net'] not in digital or pad['id'] in DIGITAL_PINS:continue
        obstacles=[(p['shape'],.25) for p in geometry['pads'] if p['net']!=pad['net']]
        obstacles += [(s['shape'],.25) for s in rows if s['net']!=pad['net']]
        # A PTH pad must contact its own plated barrel. Its own drill is not
        # a foreign hole-clearance obstacle; every other physical hole remains.
        obstacles += [(h['shape'],.255) for h in geometry['holes'] if h['id']!=pad['id']]
        obstacles += [(rect_shape(k['rect']),0.) for k in floor['keepouts'] if 'F.Cu' in k['layers'] and 'tracks' in k['deny']]
        for stub in route['prep']['seed_stubs']['stubs']:
            via=stub.get('via',route['prep']['seed_stubs']['via'])
            for at in stub.get('vias',[]):
                if stub['net']!=pad['net']:obstacles.append((pcbnew.SHAPE_CIRCLE(vec(at),pcbnew.FromMM(via['size']/2)),.25))
                obstacles.append((pcbnew.SHAPE_CIRCLE(vec(at),pcbnew.FromMM(via['drill']/2)),.255))
        # Nearby source obstacles first improves rejection time; no culling.
        obstacles.sort(key=lambda item: item[0].BBox().SquaredDistance(vec(pad['at'])))
        witness=None;attempts=0
        for start in [pad['at']]+list(sample_polygon_starts(pad['poly'])):
            for i in range(48):
                angle=i*math.tau/48
                end=[start[0]+math.cos(angle),start[1]+math.sin(angle)]
                shape=primitive(start,end,.36);attempts+=1
                if any(shape.Collide(other,round(clearance*1e6)-2) for other,clearance in obstacles):continue
                o=floor['board']['outline'];r=.18+.8
                if not all(o['x0']+r<=x<=o['x1']-r and o['y0']+r<=y<=o['y1']-r for x,y in [start,end]):continue
                witness=dict(start=list(start),end=end,width_mm=.36,clearance_mm=.25,reach_mm=1.,foreign_checks=len(obstacles))
                break
            if witness:break
        result.append(dict(pin=pad['id'],net=pad['net'],attempts=attempts,witness=witness))
    return result

def completion_owner_errors(route,pins,reached):
    """Reconcile native seed reach with declarative complete-net ownership."""
    pad_counts=Counter(pins.values())
    routed={net for group in wave_nets(route,set(pins.values())).values() for net in group}
    owners=route.get('route',{}).get('ownership',{}).get('nets',{})
    errors=[]
    for stub in route['prep']['seed_stubs']['stubs']:
        if stub['pin'] not in DIGITAL_PINS:continue
        net=stub['net']
        if len(reached.get(stub['pin'],[])) != pad_counts[net]:continue
        if net in routed or owners.get(net,{}).get('owner')!='prep.seed_stubs':
            errors.append(dict(kind='complete-owner',pin=stub['pin'],net=net))
    return errors

def inspect_geometry(floor,route,nets,geometry):
    rows=segment_rows(route);digital=[r for r in rows if r['id'] in DIGITAL_PINS]
    failures=[];checks=Counter();nearest=[]
    tolerance=2  # nanometres; preserves native source quantization only
    def check(a,b,kind,required):
        checks[kind]+=1
        if a['shape'].Collide(b['shape'],round(required*1e6)-tolerance):
            failures.append(dict(kind=kind,pin=a['id'],other=b['id'],a=a['a'],b=a['b'],width=a['width'],required=required))
    for a in digital:
        assert a['layer'] in {'F.Cu','B.Cu'}
        if a['layer']=='F.Cu':
            gaps=[]
            for b in geometry['pads']:
                if a['net']==b['net']:continue
                check(a,b,'full-segment/pad',pair_clearance(a,b,floor,nets))
                d=0. if point_in_polygon(a['a'],b['poly']) or point_in_polygon(a['b'],b['poly']) else polygon_edge_distance(b['poly'],a['a'],a['b'])
                gaps.append((d-a['width']/2,b['id']))
            gap,other=min(gaps);nearest.append(dict(pin=a['id'],a=a['a'],b=a['b'],width=a['width'],other=other,gap_mm=gap))
        for b in geometry['holes']:
            if b.get('net') is not None and a['net']==b['net']: continue
            check(a,b,'full-segment/hole',floor['design_rules']['hole_to_hole'] if b['id'].startswith('mounting-head') else .255)
        for area in floor['keepouts']:
            if a['layer'] in area['layers'] and 'tracks' in area['deny']:
                check(a,dict(id=area['name'],shape=rect_shape(area['rect'])),'full-segment/keepout',0.)
        outline=floor['board']['outline'];r=a['width']/2
        checks['full-segment/edge']+=1
        if not all(outline['x0']+.8+r<=x<=outline['x1']-.8-r and outline['y0']+.8+r<=y<=outline['y1']-.8-r for x,y in [a['a'],a['b']]):failures.append(dict(kind='edge',pin=a['id']))
        for stub in route['prep']['seed_stubs']['stubs']:
            via=stub.get('via',route['prep']['seed_stubs']['via'])
            for at in stub.get('vias',[]):
                if stub['net']==a['net']:continue
                check(a,dict(id=stub['pin']+' via',shape=pcbnew.SHAPE_CIRCLE(vec(at),pcbnew.FromMM(via['size']/2))),'full-segment/seed-via',.25)
                check(a,dict(id=stub['pin']+' hole',shape=pcbnew.SHAPE_CIRCLE(vec(at),pcbnew.FromMM(via['drill']/2))),'full-segment/seed-hole',.255)
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            if (a['net']==b['net'] or a['layer']!=b['layer'] or
                    not (a['id'] in DIGITAL_PINS or b['id'] in DIGITAL_PINS)):continue
            check(a,b,'full-segment/seed',pair_clearance(a,b,floor,nets))
    reached={}
    for stub in route['prep']['seed_stubs']['stubs']:
        if stub['pin'] not in DIGITAL_PINS:continue
        own=[r for r in digital if r['id']==stub['pin']]
        hits=sorted(p['id'] for p in geometry['pads'] if p['net']==stub['net'] and any(r['shape'].Collide(p['shape'],0) for r in own))
        reached[stub['pin']]=hits
        checks['declared-pin-reached']+=1
        if stub['pin'] not in hits:failures.append(dict(kind='unreached-pin',pin=stub['pin']))
        for i in range(1,len(own)):
            if not any(own[i]['shape'].Collide(p['shape'],0) for p in own[:i]):failures.append(dict(kind='disconnected-seed',pin=stub['pin']))
    subnominal={}
    for row in digital:
        if row['width']>=.36-1e-9: continue
        d=subnominal.setdefault(row['net'],dict(length_mm=0.,segments=0))
        d['length_mm']+=math.dist(row['a'],row['b']);d['segments']+=1
    failures += [dict(kind='extent',pin=p) for p in source_extent_errors(floor,route,nets)]
    failures += completion_owner_errors(route,geometry['pins'],reached)
    return dict(kind='MEASURED native isolated source geometry; NOT generated P-LAND/DRC/SI',utc=datetime.now(timezone.utc).isoformat(),
                checks=dict(checks),check_count=sum(checks.values()),new_segments=len(digital),native_pad_count=len(geometry['pads']),native_hole_count=len(geometry['holes']),
                failures=failures,reached_endpoints=reached,nearest_pad_gaps=nearest,subnominal=subnominal)

class DigitalLaunchSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor,cls.route,cls.nets,cls.stack,cls.comps,cls.pins=load_source()
        cls.geometry=native_geometry(cls.floor)

    def test_same_net_plated_terminal_is_contact_but_foreign_hole_blocks(self):
        # RED before the hole census carried electrical identity: every complete
        # MCH tree was rejected for touching its own plated J10 terminal.
        geometry=dict(self.geometry)
        geometry['holes']=[dict(h,net=self.geometry['pins'].get(tuple(h['id'].rsplit('.',1))))
                           for h in self.geometry['holes']]
        result=inspect_geometry(self.floor,self.route,self.nets,geometry)
        own=[v for v in result['failures'] if v['kind']=='full-segment/hole'
             and v['other']=='J10.9' and v['pin']=='U_CLK.1']
        self.assertFalse(own,own)
        foreign=dict(geometry)
        foreign['holes']=[dict(h,net='FOREIGN_HOSTILE') if h['id']=='J10.9' else h
                          for h in geometry['holes']]
        result=inspect_geometry(self.floor,self.route,self.nets,foreign)
        self.assertTrue(any(v['kind']=='full-segment/hole' and v['other']=='J10.9'
                            and v['pin']=='U_CLK.1' for v in result['failures']))

    def test_audio_monitor_pin_field_is_screened_as_one_three_net_cell(self):
        self.assertEqual(audio_control_errors(
            self.floor,self.route,self.nets,self.geometry),[])
        bad=copy.deepcopy(self.route)
        enable=next(s for s in bad['prep']['seed_stubs']['stubs']
                    if s['pin']=='U_AUDIO.6')
        enable['segments']=[
            {'layer':'F.Cu','width':.2,'pts':[[33.6,60.6],[34.2,60.6]]},
            {'layer':'B.Cu','width':.2,'pts':[[34.2,60.6],[33.5,62.89]]},
            {'layer':'F.Cu','width':.2,'pts':[[33.5,62.89],[34.2,62.89]]},
        ]
        enable['via']={'size':.3,'drill':.2}
        enable['vias']=[[34.2,60.6],[33.5,62.89]]
        timer=next(s for s in bad['prep']['seed_stubs']['stubs']
                   if s['pin']=='U_AUDIO.5')
        timer['segments']=[{'layer':'F.Cu','width':.2,
                            'pts':[[33.6,61.1],[34.3,61.1]]}]
        self.assertTrue(audio_control_errors(
            self.floor,bad,self.nets,self.geometry))
        bad=copy.deepcopy(self.route)
        pwr=next(s for s in bad['prep']['seed_stubs']['stubs']
                 if s['pin']=='U_AUDIO.3')
        pwr['segments']=pwr['segments'][:1]
        self.assertTrue(audio_control_errors(
            self.floor,bad,self.nets,self.geometry))

    def test_all_ten_target_banks_exist_without_narrowing_corners(self):
        stubs=[s for s in self.route['prep']['seed_stubs']['stubs'] if s['pin'] in DIGITAL_PINS]
        self.assertEqual({s['pin'] for s in stubs},DIGITAL_PINS)
        self.assertEqual(len(stubs),10)
        narrow={s['pin'] for s in stubs if any(r['width']<.36 for r in s['segments'])}
        self.assertEqual(narrow,NARROW_PINS)
        self.assertEqual({s['pin']:s.get('vias') for s in stubs if s.get('vias')},
                         {})
        self.assertFalse(any(s.get('arcs') for s in stubs))
        self.assertEqual({r['layer'] for s in stubs for r in s['segments']},{'F.Cu'})
        for name in ('MCH_INPUT_SECTIONS','BUFFERED_DIGITAL_SECTIONS'):
            self.assertTrue(self.nets['length_match'][name]['no_vias'])

    def test_full_new_geometry_and_declared_reach(self):
        report=inspect_geometry(self.floor,self.route,self.nets,self.geometry)
        self.assertEqual(report['failures'],[])
        self.assertEqual(len(report['reached_endpoints']),10)
        self.assertEqual(report['reached_endpoints']['U_CLK.2'],['R_FSYNC.1','U_CLK.2'])
        self.assertEqual(report['reached_endpoints']['U_CLK.5'],['R_BCLK.1','U_CLK.5'])
        self.assertEqual(set(report['subnominal']),{s['net'] for s in self.route['prep']['seed_stubs']['stubs'] if s['pin'] in DIGITAL_PINS})
        self.assertEqual(source_budget_errors(self.route),[])

    def test_all_twenty_other_endpoints_have_full_width_launch_witnesses(self):
        rows=bulk_endpoint_launches(self.floor,self.route,self.nets,self.geometry)
        self.assertEqual(len(rows),20)
        self.assertTrue({'R_TDM_PD.1','U_TDM_SCH.2','U_TDM_SCH.4'} <= {r['pin'] for r in rows})
        self.assertEqual([r['pin'] for r in rows if r['witness'] is None],[])

    def test_old_clock_bulk_entries_are_rejected_by_native_shapes(self):
        lookup={p['id']:p for p in self.geometry['pads']}
        # Pose-relative hostile points retain the original wrong-neighbor
        # clearance defect when the entire buffer is relocated.
        for pin,other in [('U_CLK.3','U_CLK.4'),('U_CLK.6','U_CLK.5')]:
            at=lookup[other]['at']
            self.assertTrue(primitive(at,at,.36).Collide(lookup[other]['shape'],pcbnew.FromMM(.25)),pin)
        at=lookup['C_CLK.1']['at']
        self.assertTrue(primitive(at,at,.36).Collide(lookup['C_CLK.1']['shape'],pcbnew.FromMM(.25)))

    def test_opposite_outer_layer_crossing_passes_but_same_layer_fails(self):
        self.assertEqual(inspect_geometry(self.floor,self.route,self.nets,self.geometry)['failures'],[])
        bad=copy.deepcopy(self.route)
        row=next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin']=='U_ADC.21')
        crossing=next(s for s in row['segments'] if s['layer']=='B.Cu' and s['pts'][0]==[97.0,73.375])
        crossing['layer']='F.Cu'
        failures=inspect_geometry(self.floor,bad,self.nets,self.geometry)['failures']
        self.assertIn('full-segment/seed',{f['kind'] for f in failures})

    def test_subnominal_items_are_wholly_contained_not_merely_overlapping(self):
        self.assertEqual(source_extent_errors(self.floor,self.route,self.nets),[])
        bad=copy.deepcopy(self.route)
        seed=next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin']=='U_CLK.3')
        seed['segments'][0]['pts'][-1]=[140.,59.65]
        area=next(k for k in self.floor['keepouts'] if k['name']=='CLK_WEST_DIGITAL')
        s=seed['segments'][0]
        self.assertTrue(overlaps(primitive(s['pts'][0],s['pts'][-1],s['width']),area))
        self.assertIn('U_CLK.3',source_extent_errors(self.floor,bad,self.nets))

    def test_two_complete_buffer_outputs_have_source_owners_and_no_generic_wave(self):
        groups=wave_nets(self.route,set(self.pins.values()))
        routed={n for group in groups.values() for n in group}
        for net in {'FSYNC_BUF','BCLK_BUF'}:
            self.assertNotIn(net,routed)
            self.assertEqual(self.route['route']['ownership']['nets'][net]['owner'],'prep.seed_stubs')
        kwargs=dict(pad_counts=dict(Counter(self.pins.values())),board_nets=set(self.pins.values()),nets_cfg=self.nets)
        self.assertEqual(audit_config(self.route,**kwargs)['findings'],[])
        bad=copy.deepcopy(self.route)
        bad['prep']['waves']['exclude'].remove('FSYNC_BUF')
        bad['prep']['waves']['groups']['clocks'].append('FSYNC_BUF')
        # O-DOUBLE is explicitly limited to many-pad power by that consumer.
        # It does NOT grade this two-pad clock; retain the limitation visibly.
        self.assertEqual(audit_config(bad,**kwargs)['findings'],[])
        observed,plan=shadow_inputs(bad,self.nets,self.comps,self.pins)
        receipt=compile_source_prep_authority(stack=self.stack,observed=observed,route_plan=plan)
        self.assertEqual(receipt['verdict'],'FAIL')
        bad=copy.deepcopy(self.route)
        bad['prep']['waves']['exclude'].remove('BCLK_BUF')
        bad['prep']['waves']['groups']['clocks'].append('BCLK_BUF')
        del bad['route']['ownership']['nets']['BCLK_BUF']
        reached=inspect_geometry(self.floor,self.route,self.nets,self.geometry)['reached_endpoints']
        self.assertEqual(completion_owner_errors(bad,self.geometry['pins'],reached),
                         [dict(kind='complete-owner',pin='U_CLK.5',net='BCLK_BUF')])

    def test_bulk_class_and_partial_owner_partition_stay_exact(self):
        clock=self.nets['classes']['ADC_CLOCK']
        self.assertEqual(len(clock['nets']),13)
        self.assertEqual(parse_mm(clock['min_width']),.36)
        self.assertEqual(parse_mm(clock['clearance']),.25)
        groups=wave_nets(self.route,set(self.pins.values()))
        complete={'MCH_MCLK','MCH_BCLK','MCH_FSYNC','MCLK_BUF','FSYNC_BUF','BCLK_BUF','ADC_MCLK','ADC_BCLK','ADC_FSYNC','TDM_RAW'}
        self.assertEqual(set(groups['clocks']),set(clock['nets'])-complete)
        for net in complete:
            self.assertEqual(self.route['route']['ownership']['nets'][net]['owner'],'prep.seed_stubs')
            self.assertIn(net,self.route['prep']['waves']['exclude'])
        digital_seeds=[s for s in self.route['prep']['seed_stubs']['stubs'] if s['pin'] in DIGITAL_PINS]
        self.assertEqual({s['pin'] for s in digital_seeds},DIGITAL_PINS)

    def test_existing_output_guard_declared_and_source_budget_hostiles(self):
        wave=next(w for w in self.route['route']['waves'] if w['name']=='clocks')
        self.assertEqual(wave['layers'],['F.Cu'])
        self.assertEqual(wave['clearance'],.25)
        self.assertEqual(self.route['route']['routability']['class_layers']['ADC_CLOCK'],
                         ['F.Cu','B.Cu'])
        self.assertEqual(dict(zip(wave['power_nets'],wave['power_nets_widths'])),dict.fromkeys(self.nets['classes']['ADC_CLOCK']['nets'],.36))
        self.assertEqual(wave['track_width'],.18)
        self.assertEqual(wave['realized_width'],dict(nominal=.36,minimum=.18,max_subnominal_length_per_net=3.0,max_subnominal_segments_per_net=3))
        self.assertEqual(source_budget_errors(self.route),[])
        bad=copy.deepcopy(self.route)
        seed=next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin']=='U_CLK.3')
        seed['segments'][0]['pts'][-1]=[140.,59.65]
        self.assertIn(('MCH_BCLK','length'),source_budget_errors(bad))
        bad=copy.deepcopy(self.route)
        seed=next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin']=='U_CLK.3')
        seed['segments'][0]['pts'][1:1]=[[158.3,58.25],[158.0,58.25]]
        self.assertNotIn(('MCH_BCLK','length'),source_budget_errors(bad))
        self.assertIn(('MCH_BCLK','segments'),source_budget_errors(bad))
        seed['segments'][0]['width']=.17
        self.assertIn(('MCH_BCLK','floor'),source_budget_errors(bad))

    def test_corner_entries_and_fsync_transition_are_exactly_scoped(self):
        areas={a['name']:a for a in self.floor['keepouts']}
        for pin,name in [('U_ADC.24','ADC_FSYNC_CORNER'),('U_ADC.25','ADC_DOUT1_CORNER')]:
            seed=next(s for s in self.route['prep']['seed_stubs']['stubs'] if s['pin']==pin)
            spec=seed['segments'][0]
            self.assertEqual(spec['width'],.36)
            x0,y0,x1,y1=areas[name]['rect']
            # Ordinary-width corner copper follows the native pair-rule
            # overlap semantics; only subnominal items require containment.
            self.assertTrue(overlaps(primitive(spec['pts'][0],spec['pts'][1],.36),areas[name]))
            self.assertEqual({s['layer'] for s in seed['segments']},{'F.Cu'})
            self.assertFalse(seed.get('vias'))
        self.assertEqual(source_extent_errors(self.floor,self.route,self.nets),[])
        self.assertTrue(any(r['zone']=='ADC_FSYNC_CORNER' and r['nets']==['ADC_FSYNC'] and
                            parse_mm(r['min_width'])==.18 for r in self.nets['scoped_floors']))

    def test_whole_segment_screen_rejects_midspan_obstacle_and_lost_endpoint(self):
        # Both endpoint discs miss this foreign shape; the full copper does not.
        a,b=[140.,50.],[143.,50.]
        obstacle=pcbnew.SHAPE_CIRCLE(vec([141.5,50.]),pcbnew.FromMM(.1))
        self.assertFalse(primitive(a,a,.18).Collide(obstacle,pcbnew.FromMM(.25)))
        self.assertFalse(primitive(b,b,.18).Collide(obstacle,pcbnew.FromMM(.25)))
        self.assertTrue(primitive(a,b,.18).Collide(obstacle,pcbnew.FromMM(.25)))
        bad=copy.deepcopy(self.route)
        seed=next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin']=='U_ADC.29')
        for spec in seed['segments']:
            spec['pts']=[[x+2.,y] for x,y in spec['pts']]
        report=inspect_geometry(self.floor,bad,self.nets,self.geometry)
        self.assertIn(dict(kind='unreached-pin',pin='U_ADC.29'),report['failures'])

if __name__=='__main__': unittest.main()
