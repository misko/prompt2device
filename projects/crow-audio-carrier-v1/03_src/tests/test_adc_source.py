"""ADC source geometry only: isolated native footprints, never a BOARD.

These tests do not certify filled return paths, via ampacity, native PCB DRC,
manufactured impedance, noise/THD, assembly, or safe power-up.
"""
import copy
import json
import math
import subprocess
import unittest
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pcbnew
import yaml
from test_route_source_contract import load_source
from test_digital_launch_source import native_geometry, segment_rows, primitive, rect_shape, pair_clearance
from test_regulator_source import via_rows, contained, connected_reach
from placement_gates import _poly_gap_mm
from rules_audit import parse_mm

CELL_PINS = {f'U_ADC.{i}' for i in [1,2,3,4,5,8,9,10,11,12,17,18,23,30,31,32,33,35,36,37,38,43,44]} | {
    'C_VDDIO.1','C_VDDIO.2','C_LDO_D.2','C_FILT1_1U.2','C_FILT2_1U.2'}
COMPLETE = {'LDO_D_FILT': {'U_ADC.32','U_ADC.33','C_LDO_D.1'},
            'VMID1': {'U_ADC.1','C_VMID1_470N.1','C_VMID1_4U7.1'},
            'VMID2': {'U_ADC.12','C_VMID2_470N.1','C_VMID2_4U7.1'}}
EXPECTED_BUDGETS = {'3V3_ADC': (78.0819281355697,63), 'FILT1P': (6.050464884544218,4),
    'FILT2P': (6.050464884544218,4), 'CFG1': (2.732988327739914,3), 'CFG5': (2.732988327739914,3),
    'CFG2': (1.9997137551367592,3), 'CFG4': (1.9997137551367592,3)}


def extent_errors(floor, route, nets):
    areas={a['name']:a for a in floor['keepouts']}
    widths={net:parse_mm(c['min_width']) for c in nets['classes'].values() for net in c['nets']}
    errors=[]
    for row in segment_rows(route):
        if row['id'] not in CELL_PINS:continue
        if row['width']>=widths[row['net']]-1e-9:continue
        if row['layer']!='F.Cu':errors.append('unexpected-layer:'+row['id'])
        eligible=[areas[r['zone']] for r in nets['scoped_floors'] if row['net'] in r.get('nets',[]) and parse_mm(r['min_width'])<=row['width']]
        if not any(a['deny']==[] and contained(row,a) for a in eligible):errors.append(row['id'])
    return errors


def budgets(route, nets):
    widths={net:parse_mm(c['min_width']) for c in nets['classes'].values() for net in c['nets']}
    result={}
    for row in segment_rows(route):
        if row['net'] not in EXPECTED_BUDGETS or row['width']>=widths[row['net']]:continue
        d=result.setdefault(row['net'],[0.,0]);d[0]+=math.dist(row['a'],row['b']);d[1]+=1
    return result


def placement_screen(floor, geometry):
    refs=sorted({p['id'].split('.')[0] for p in geometry['pads']})
    fps=dict(zip(refs,geometry['footprints']));findings=[];counts=Counter()
    for fp in fps.values():fp.BuildCourtyardCaches()
    for moved_ref in ['C_LDO_D','C_VDDIO']:
        moved=fps[moved_ref];body=moved.GetCourtyard(pcbnew.F_CrtYd)
        for ref,fp in fps.items():
            if ref==moved_ref:continue
            foreign=fp.GetCourtyard(pcbnew.F_CrtYd)
            if foreign.OutlineCount():
                counts['courtyard-pair']+=1
                if _poly_gap_mm(body,foreign,.1)<.1-1e-6:findings.append((moved_ref,ref,'courtyard'))
            for p in fp.Pads():
                if not p.IsOnCopperLayer() or not p.IsOnLayer(pcbnew.F_Cu):continue
                counts['moved-body/foreign-pad']+=1
                if body.Collide(p.GetEffectiveShape(pcbnew.F_Cu),100000-2):findings.append((moved_ref,ref,'body-pad'))
                for own in moved.Pads():
                    if not own.IsOnCopperLayer():continue
                    counts['distinct-pad']+=1
                    if own.GetEffectiveShape(pcbnew.F_Cu).Collide(p.GetEffectiveShape(pcbnew.F_Cu),127000-2):findings.append((moved_ref,ref,'distinct-pad'))
            if foreign.OutlineCount():
                for p in moved.Pads():
                    if not p.IsOnCopperLayer():continue
                    counts['foreign-body/moved-pad']+=1
                    if foreign.Collide(p.GetEffectiveShape(pcbnew.F_Cu),100000-2):findings.append((moved_ref,ref,'reverse-body-pad'))
    lookup={p['id']:p for p in geometry['pads']};spans={};gaps={}
    for cap,pins,limit in [('C_LDO_D.1',['U_ADC.32','U_ADC.33'],2.),('C_VDDIO.1',['U_ADC.31'],2.5)]:
        cb=lookup[cap]['shape'].BBox()
        for pin in pins:
            pb=lookup[pin]['shape'].BBox();key=cap+'/'+pin
            spans[key]=math.dist(lookup[cap]['at'],lookup[pin]['at'])
            dx=max(0,cb.GetLeft()-pb.GetRight(),pb.GetLeft()-cb.GetRight())/1e6
            dy=max(0,cb.GetTop()-pb.GetBottom(),pb.GetTop()-cb.GetBottom())/1e6
            gaps[key]=math.hypot(dx,dy);counts['exact-adjacency/span']+=1
            if spans[key]>5. or gaps[key]>limit:findings.append((cap,pin,'adjacency/span'))
    return dict(findings=findings,checks=dict(counts),pin_spans_mm=spans,copper_bbox_gaps_mm=gaps)


def area_shape(area):
    if 'rect' in area:return rect_shape(area['rect'])
    poly=pcbnew.SHAPE_POLY_SET();chain=pcbnew.SHAPE_LINE_CHAIN()
    for x,y in area['points']:chain.Append(pcbnew.VECTOR2I(round(x*1e6),round(y*1e6)))
    chain.SetClosed(True);poly.AddOutline(chain);return poly


def inspect(floor, route, nets, geometry):
    rows=segment_rows(route);new=[r for r in rows if r['id'] in CELL_PINS]
    vias=via_rows(route);newvias=[v for v in vias if v['pin'] in CELL_PINS]
    counts=Counter();failures=[]
    def check(a,b,kind,clearance):
        counts[kind]+=1
        if pcbnew.SHAPE.Collide(a['shape'],b['shape'],max(0,round(clearance*1e6)-2)):
            failures.append(dict(kind=kind,item=a['id'],other=b['id'],required_mm=clearance))
    def clearance(a,b):
        required=pair_clearance(a,b,floor,nets)
        if any(x.get('id') in {'U_ADC.5','U_ADC.9'} and x.get('width',0)>=.6 for x in [a,b]):required=max(.25,required)
        return required
    def hole_clearance(a,b):
        required=.255
        areas={x['name']:x for x in floor['keepouts']}
        for rule in nets.get('scoped_clearances',[]):
            if 'hole_clearance' not in rule:continue
            area=areas[rule['zone']]
            layer=a.get('layer',b.get('layer','F.Cu'))
            if layer not in area['layers']:continue
            if not (area_shape(area).Collide(a['shape'],0) and area_shape(area).Collide(b['shape'],0)):continue
            if a['net'] in rule.get('nets',[]) or b['net'] in rule.get('nets',[]):
                required=parse_mm(rule['hole_clearance'])
        return required
    for row in new:
        counts['source-layer']+=1
        if row['layer'] not in {'F.Cu','B.Cu'}:failures.append(dict(kind='source-layer',item=row['id']))
        outline=floor['board']['outline'];radius=row['width']/2
        counts['source-edge']+=1
        if not all(outline['x0']+.8+radius<=x<=outline['x1']-.8-radius and outline['y0']+.8+radius<=y<=outline['y1']-.8-radius for x,y in [row['a'],row['b']]):failures.append(dict(kind='source-edge',item=row['id']))
        if row['layer']=='F.Cu':
            for pad in geometry['pads']:
                if row['net']!=pad['net']:check(row,pad,'segment-pad',clearance(row,pad))
        for hole in geometry['holes']:check(row,hole,'segment-hole',.255)
        for area in floor['keepouts']:
            if 'F.Cu' in area['layers'] and 'tracks' in area['deny']:check(row,dict(id=area['name'],shape=area_shape(area)),'segment-keepout',0.)
        for via in vias:
            if row['net']==via['net']:continue
            check(row,via,'segment-via',clearance(row,via))
            check(row,dict(id=via['id'],net=via['net'],shape=via['hole'],layer=row['layer']),
                  'segment-via-hole',hole_clearance(row,via))
    for i,row in enumerate(rows):
        for other in rows[i+1:]:
            if row['id'] not in CELL_PINS and other['id'] not in CELL_PINS:continue
            if row['layer']==other['layer'] and row['net']!=other['net']:check(row,other,'segment-pair',clearance(row,other))
    for via in newvias:
        counts['via-geometry']+=1
        if (via['size'],via['drill'])!=(.5,.2):failures.append(dict(kind='via-geometry',item=via['id']))
        for fp in geometry['footprints']:
            for pad in fp.Pads():
                for layer in [pcbnew.F_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu,pcbnew.B_Cu]:
                    if not pad.IsOnCopperLayer() or not pad.IsOnLayer(layer):continue
                    counts['via-hole/physical-layer-pad']+=1
                    if pcbnew.SHAPE.Collide(via['hole'],pad.GetEffectiveShape(layer),255000-2):failures.append(dict(kind='via-hole/physical-layer-pad',item=via['id'],other=pad.GetNumber(),layer=int(layer)))
        for pad in geometry['pads']:
            if via['net']!=pad['net']:check(via,pad,'via-pad',.25)
        for hole in geometry['holes']:check(dict(id=via['id'],shape=via['hole']),hole,'via-hole-pair',.5)
        for area in floor['keepouts']:
            if any(layer in area['layers'] for layer in ['F.Cu','In1.Cu','In2.Cu','B.Cu']) and 'vias' in area['deny']:
                check(via,dict(id=area['name'],shape=area_shape(area)),'via-keepout',0.)
        for row in rows:
            if via['net']!=row['net']:
                check(via,row,'via-segment',clearance(via,row))
                check(dict(id=via['id'],net=via['net'],shape=via['hole'],layer=row['layer']),
                      row,'via-hole-segment',hole_clearance(via,row))
    for i,via in enumerate(vias):
        for other in vias[i+1:]:
            if via['pin'] not in CELL_PINS and other['pin'] not in CELL_PINS:continue
            check(dict(id=via['id'],shape=via['hole']),dict(id=other['id'],shape=other['hole']),'via-hole-via',.5)
            if via['net']!=other['net']:check(via,other,'via-copper-via',.25)
    pads={p['id']:p for p in geometry['pads']}
    reached={pin:any(r['id']==pin and r['net']==pads[pin]['net'] and r['shape'].Collide(pads[pin]['shape'],0) for r in new) for pin in CELL_PINS}
    return dict(utc=datetime.now(timezone.utc).isoformat(),kind='Source-native ADC screen; NOT PCB DRC/filled return/ampacity/thermal PASS',
        segments=len(new),vias=len(newvias),check_count=sum(counts.values()),checks=dict(counts),failures=failures,reached=reached,
        extent_errors=extent_errors(floor,route,nets),budgets=budgets(route,nets),placement=placement_screen(floor,geometry))


class AdcSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor,cls.route,cls.nets,cls.stack,cls.comps,cls.pins=load_source()
        cls.geometry=native_geometry(cls.floor);cls.report=inspect(cls.floor,cls.route,cls.nets,cls.geometry)

    def test_native_complete_candidate(self):
        self.assertGreater(self.report['check_count'],80000)
        self.assertEqual(self.report['failures'],[])
        self.assertEqual(len(self.report['reached']),28);self.assertTrue(all(self.report['reached'].values()))
        self.assertEqual(self.report['placement']['findings'],[])

    def test_whole_capsule_extents_and_hostile_long_leaf(self):
        self.assertEqual(self.report['extent_errors'],[])
        bad=copy.deepcopy(self.route)
        next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin']=='U_ADC.2')['segments'][0]['pts'][-1]=[85.,65.]
        self.assertIn('U_ADC.2',extent_errors(self.floor,bad,self.nets))
        bad=copy.deepcopy(self.route)
        next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin']=='U_ADC.31')['segments'][0]['layer']='B.Cu'
        self.assertIn('unexpected-layer:U_ADC.31',extent_errors(self.floor,bad,self.nets))

    def test_exact_per_net_budgets_and_wave_ceiling(self):
        self.assertEqual(set(self.report['budgets']),set(EXPECTED_BUDGETS))
        for net,(length,count) in EXPECTED_BUDGETS.items():
            self.assertAlmostEqual(self.report['budgets'][net][0],length,places=8)
            self.assertEqual(self.report['budgets'][net][1],count)
        guard=next(w for w in self.route['route']['waves'] if w['name']=='residual_control')['realized_width']
        self.assertEqual(guard,dict(nominal=.2,minimum=.18,max_subnominal_length_per_net=2.733,max_subnominal_segments_per_net=3))

    def test_complete_three_pad_owners_are_native_contact_graphs(self):
        for net,expected in COMPLETE.items():
            actual={p['id'] for p in self.geometry['pads'] if p['net']==net}
            self.assertEqual(actual,expected)
            reached=set(connected_reach(self.route,self.geometry,sorted(expected)[0]))
            self.assertTrue(expected<=reached,(net,reached))
            self.assertIn(net,self.route['prep']['waves']['exclude'])
            self.assertEqual(self.route['route']['ownership']['nets'][net]['owner'],'prep.seed_stubs')
        bad=copy.deepcopy(self.route)
        # Remove the real interlayer link; moving the old endpoint no longer
        # disconnects the separately connected pin33 branch.
        next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin']=='U_ADC.32')['segments'].pop(1)
        self.assertNotIn('C_LDO_D.1',connected_reach(bad,self.geometry,'U_ADC.32'))

    def test_partial_controls_and_filter_feeds_remain_generic(self):
        from route_and_stitch_generic import wave_nets
        groups=wave_nets(self.route,set(self.pins.values()))
        self.assertIn('ADC_RESET_N',groups['pwr_en'])
        for net in ['CFG1','CFG2']:self.assertIn(net,groups['timers'])
        for net in ['CFG4','CFG5']:self.assertIn(net,groups['adc'])
        for bank,pin in [(1,'43'),(2,'18')]:
            net=f'FILT{bank}P'
            wave=next(w for w in self.route['route']['waves'] if w['name']==f'power_filt{bank}p')
            self.assertEqual(wave['nets'],[net])
            reached=set(connected_reach(self.route,self.geometry,'U_ADC.'+pin))
            self.assertTrue({f'C_FILT{bank}_1U.1',f'C_FILT{bank}_10U.1'}<=reached)
            self.assertNotIn(f'C_FILT{bank}_470U.1',reached)
            self.assertEqual(len([p for p in self.geometry['pads'] if p['net']==net]),5)

    def test_own_ground_drops_do_not_invent_a_plane_edge(self):
        for pin in ['30','17','44']:
            reached=connected_reach(self.route,self.geometry,'U_ADC.'+pin)
            self.assertNotIn('U_ADC.49',reached)
            self.assertIn('U_ADC.'+pin+':via0',reached)
        self.assertIn('U_ADC.49',connected_reach(self.route,self.geometry,'U_ADC.4'))
        masks={a['name']:a for a in self.floor['keepouts']}
        for name in ['ADC_GD_PADDLE_GAP','ADC_FILT1N_PADDLE_GAP','ADC_FILT2N_PADDLE_GAP']:
            self.assertEqual(masks[name]['layers'],['F.Cu']);self.assertEqual(set(masks[name]['deny']),{'tracks','vias','pours'})

    def test_adc_local_seeds_and_anchors_preserved_across_regulator_change(self):
        project=Path(__file__).resolve().parents[2];root=project.parents[1]
        def frozen(name):
            return yaml.safe_load(subprocess.check_output(['git','show','1b725986:projects/crow-audio-carrier-v1/03_src/'+name],cwd=root,timeout=15))
        before=frozen('route.yaml')['prep']['seed_stubs']['stubs']
        same=[b for b in before if b['pin'] in CELL_PINS]
        next(b for b in same if b['pin']=='U_ADC.3')['segments'].append(
            dict(layer='B.Cu',width=.2,pts=[[91.6,67.65],[90.7,67.65]]))
        live={b['pin']:b for b in self.route['prep']['seed_stubs']['stubs']}
        self.assertEqual(len(same),28)
        changed={'U_ADC.5','U_ADC.9','U_ADC.23'}
        # These cells were explicitly co-designed after the regulator change.
        # Native collision, exact adjacency, contact and extent tests above
        # own their acceptance; the historical snapshot owns other cells.
        redesigned={'U_ADC.23','U_ADC.30','U_ADC.31','U_ADC.32','U_ADC.33','C_LDO_D.2','C_VDDIO.1','C_VDDIO.2'}
        for bank in same:
            if bank['pin'] in redesigned:continue
            if bank['pin'] in changed:
                self.assertEqual(live[bank['pin']]['segments'][:len(bank['segments'])],bank['segments'])
            else:
                self.assertEqual(live[bank['pin']],bank)
        placement=frozen('floorplan.yaml')['placement']
        for ref in ['U_ADC','C_FILT1_1U','C_FILT2_1U']:
            self.assertEqual(self.floor['placement']['anchors'][ref],placement['anchors'][ref],ref)


if __name__=='__main__':unittest.main()
