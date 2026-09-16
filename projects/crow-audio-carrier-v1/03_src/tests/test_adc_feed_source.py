"""Live ADC-feed source regression; isolated footprints, never a BOARD.

Native contact and full-shape clearance prove only the local authored source.
They cannot prove global routability, filled return, thermal/fault withstand,
assembly, safe power-up, or release readiness. Known-bad mutations reconstruct
the rejected cap-gap rule, old ground drop, disconnected feed and runaway leaf.
"""
import copy
import math
import subprocess
import unittest
from pathlib import Path

import pcbnew
import yaml
from test_adc_source import load_source, native_geometry, inspect, extent_errors
from test_digital_launch_source import segment_rows
from test_regulator_source import connected_reach, contained, via_rows
from test_power_landing_source import copper_groups

PROJECT=Path(__file__).resolve().parents[2]
REPO=PROJECT.parents[1]
REOPENED={f'U_ADC.{n}' for n in [2,3,5,8,9,10,11]}


def frozen(name, revision='549a4e793ba7f42cd971e25d96cdbbdd36f708ea'):
    return yaml.safe_load(subprocess.check_output(['git','show',
        revision+':projects/crow-audio-carrier-v1/03_src/'+name],cwd=REPO,timeout=15))


def native_gap_mm(a,b):
    """Independent native-shape clearance bisection, one-nanometre interval."""
    lo,hi=0,1000000
    while hi-lo>1:
        mid=(lo+hi)//2
        if pcbnew.SHAPE.Collide(a,b,mid):hi=mid
        else:lo=mid
    return lo/1e6


def has_connected_full_entry(route,geometry,pin):
    groups=copper_groups('3V3_ADC',geometry,route)
    own=[g for g in groups if any(p['kind']=='pad' and p['id']==pin for p in g)]
    return len(own)==1 and any(p['kind']=='seed' and p['width']>=1.2 for p in own[0])


class AdcFeedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor,cls.route,cls.nets,*_=load_source()
        cls.geometry=native_geometry(cls.floor)
        cls.rows=segment_rows(cls.route)
        cls.banks={b['pin']:b for b in cls.route['prep']['seed_stubs']['stubs']}

    def test_seven_adc_banks_and_physical_authority_survive_regulator_change(self):
        accepted=frozen('route.yaml','1b725986')['prep']['seed_stubs']['stubs']
        expected={b['pin']:b for b in accepted if b['pin'] in REOPENED}
        self.assertEqual(len(expected),7)
        expected['U_ADC.3']['segments'].append(dict(layer='B.Cu',width=.2,pts=[[91.6,67.65],[90.7,67.65]]))
        for pin in REOPENED-{'U_ADC.5','U_ADC.9'}:
            self.assertEqual(self.banks[pin],expected[pin])
        for pin in {'U_ADC.5','U_ADC.9'}:
            self.assertEqual(self.banks[pin]['segments'][:len(expected[pin]['segments'])],
                             expected[pin]['segments'])
        before=frozen('floorplan.yaml','1b725986')
        refs={'U_ADC','C_VDDA1_10N','C_VDDA2_10N','C_VMID1_470N',
              'C_VMID1_4U7','C_VMID2_470N','C_VMID2_4U7'}
        for ref in refs:
            self.assertEqual(self.floor['placement']['anchors'][ref],
                             before['placement']['anchors'][ref],ref)
        # ADR0030 changes only these explicit mechanical fields; retain all other board settings.
        before['board']['outline']['x0']=16.0
        before['board']['outline']['x1']=172.0  # authorized2mm east-side growth
        before['board']['mounting_holes']['at']=[[21.,25.],[165.,25.],[21.,115.],[165.,115.]]
        before['board']['fiducials']['at']=[[25.,33.],[161.,29.],[29.,111.]]
        for key in ['board','design_rules','zones']:
            self.assertEqual(self.floor[key],before[key])
        old_nets=frozen('rules/nets.yaml','1b725986')
        select=lambda ns:[r for r in ns['scoped_clearances'] if r['zone'].startswith('ADC_FEED_CAP_GAP_')]
        self.assertEqual(len(select(self.nets)),2)
        self.assertEqual(select(self.nets),select(old_nets))

    def test_full_feeds_are_connected_to_real_adc_and_bypass_pads(self):
        for n,cap in [(5,'C_VDDA1_10N.1'),(9,'C_VDDA2_10N.1')]:
            pin=f'U_ADC.{n}';bank=self.banks[pin]
            self.assertFalse(bank.get('vias'))
            self.assertTrue(has_connected_full_entry(self.route,self.geometry,pin))
            self.assertEqual([s['width'] for s in bank['segments']],[.18,.18,1.2,.6])
            self.assertIn(cap,connected_reach(self.route,self.geometry,pin))
        bad=copy.deepcopy(self.route)
        next(b for b in bad['prep']['seed_stubs']['stubs'] if b['pin']=='U_ADC.5')['segments'].pop(1)
        self.assertFalse(has_connected_full_entry(bad,self.geometry,'U_ADC.5'))
        self.assertTrue(has_connected_full_entry(bad,self.geometry,'U_ADC.9'))

    def test_native_pad_gaps_and_trace_clearance_are_measured_not_assumed(self):
        pads={p['id']:p for p in self.geometry['pads']}
        checks=0
        for side,pin in [(1,'U_ADC.5'),(2,'U_ADC.9')]:
            for value in ['470N','4U7']:
                pair=[pads[f'C_VMID{side}_{value}.{n}'] for n in [1,2]]
                self.assertAlmostEqual(native_gap_mm(pair[0]['shape'],pair[1]['shape']),.65,places=6)
                y=pair[0]['at'][1]
                crossing=[r for r in self.rows if r['id']==pin and r['a'][0]==r['b'][0]
                          and min(r['a'][1],r['b'][1])<y<max(r['a'][1],r['b'][1])]
                self.assertEqual(len(crossing),1)
                for pad in pair:
                    self.assertAlmostEqual(native_gap_mm(crossing[0]['shape'],pad['shape']),.235,places=6);checks+=1
        self.assertEqual(checks,8)

    def test_explicit_local_clearance_is_necessary_and_not_global(self):
        rules=[r for r in self.nets['scoped_clearances'] if r['zone'].startswith('ADC_FEED_CAP_GAP_')]
        self.assertEqual(len(rules),2)
        areas={a['name']:a for a in self.floor['keepouts']}
        for rule in rules:
            self.assertEqual(rule['nets'],['3V3_ADC']);self.assertEqual(rule['clearance'],'0.23mm')
            self.assertEqual(areas[rule['zone']]['layers'],['F.Cu']);self.assertEqual(areas[rule['zone']]['deny'],[])
        bad=copy.deepcopy(self.nets)
        for r in bad['scoped_clearances']:
            if r['zone'].startswith('ADC_FEED_CAP_GAP_'):r['clearance']='0.24mm'
        failures=inspect(self.floor,self.route,bad,self.geometry)['failures']
        self.assertEqual(len([r for r in failures if r['kind']=='segment-pad' and r['other'].startswith('C_VMID')]),8)

    def test_whole_feed_capsules_and_exact_additive_length(self):
        areas={a['name']:a for a in self.floor['keepouts']}
        lengths=[]
        for n,suffix in [(5,'NORTH'),(9,'SOUTH')]:
            pin=f'U_ADC.{n}';spec=self.banks[pin]['segments'][1]
            rows=[r for r in self.rows if r['id']==pin and r['a'] in spec['pts'][:-1] and r['b'] in spec['pts'][1:]]
            self.assertEqual(len(rows),6)
            self.assertTrue(all(contained(r,areas['ADC_FEED_'+suffix]) for r in rows))
            length=sum(math.dist(r['a'],r['b']) for r in rows)
            self.assertAlmostEqual(length,6.938221893892777,places=8);lengths.append(length)
        self.assertAlmostEqual(sum(lengths),13.876443787785554,places=8)
        bad=copy.deepcopy(self.route)
        next(b for b in bad['prep']['seed_stubs']['stubs'] if b['pin']=='U_ADC.5')['segments'][1]['pts'][-1]=[91.3,55.]
        self.assertIn('U_ADC.5',extent_errors(self.floor,bad,self.nets))

    def test_ground_return_reaches_its_own_drop_and_rejects_old_site(self):
        reached=set(connected_reach(self.route,self.geometry,'U_ADC.8'))
        self.assertTrue({'C_VMID2_470N.2','C_VMID2_4U7.2','U_ADC.8:via0'}<=reached)
        self.assertFalse({'U_ADC.6','U_ADC.49'}&reached)
        own=next(v for v in via_rows(self.route) if v['pin']=='U_ADC.8')
        for pad in self.geometry['pads']:
            self.assertFalse(own['hole'].Collide(pad['shape'],255000-2),pad['id'])
        self.assertEqual(self.banks['U_ADC.8']['vias'],[[89.8,71.5]])
        self.assertEqual(self.banks['U_ADC.8']['via'],dict(size=.5,drill=.2))
        bad=copy.deepcopy(self.route)
        next(b for b in bad['prep']['seed_stubs']['stubs'] if b['pin']=='U_ADC.8')['vias']=[[90.55,71.0]]
        failures=inspect(self.floor,bad,self.nets,self.geometry)['failures']
        self.assertTrue(any(r['kind']=='via-hole/physical-layer-pad' and r['item']=='U_ADC.8:via0' for r in failures))

    def test_shared_rail_nonwest_power_copper_has_exact_current_subtotal(self):
        rows=[r for r in self.rows if r['net']=='3V3_ADC' and r['width']<1.2 and r['id'] not in {'U_ADC.5','U_ADC.9'}]
        self.assertEqual(len(rows),39)
        self.assertAlmostEqual(sum(math.dist(r['a'],r['b']) for r in rows),46.607233275013044,places=8)


# ADR0015: immutable pre-correction protected region, in millimetres. This
# historical geometry is the coverage obligation, not a golden native board.
VMID2_PROTECTED_POINTS = [[92.53, 70.39],
 [92.15, 70.39],
 [92.11977, 70.39219],
 [91.56977, 70.47219],
 [91.53878, 70.47912],
 [90.64333, 70.75202],
 [90.60295, 70.73524],
 [90.4976, 70.73513],
 [90.40023, 70.77535],
 [89.85947, 71.13586],
 [89.8, 71.13],
 [89.72782, 71.13711],
 [89.65841, 71.15816],
 [89.59444, 71.19236],
 [89.53837, 71.23837],
 [89.49236, 71.29444],
 [89.45816, 71.35841],
 [89.43711, 71.42782],
 [89.43, 71.5],
 [89.43711, 71.57218],
 [89.45816, 71.64159],
 [89.49236, 71.70556],
 [89.53, 71.75143],
 [89.53, 73.705],
 [89.255, 73.705],
 [89.255, 74.895],
 [89.53, 74.895],
 [89.53, 75.505],
 [89.355, 75.505],
 [89.355, 76.695],
 [90.495, 76.695],
 [90.495, 75.505],
 [90.07, 75.505],
 [90.07, 74.895],
 [90.395, 74.895],
 [90.395, 73.705],
 [90.07, 73.705],
 [90.07, 71.75143],
 [90.10764, 71.70556],
 [90.14184, 71.64159],
 [90.15894, 71.58521],
 [90.69977, 71.22465],
 [90.773, 71.15157],
 [91.64599, 70.88552],
 [92.16519, 70.81],
 [92.53, 70.81],
 [92.53, 70.82],
 [93.57, 70.82],
 [93.57, 70.38],
 [92.53, 70.38]]
VMID2_RETURN_BANKS = {'C_VMID2_470N.2': {'net': 'GND',
                    'pin': 'C_VMID2_470N.2',
                    'segments': [{'layer': 'F.Cu',
                                  'pts': [[89.825, 74.3],
                                          [89.8, 74.3],
                                          [89.8, 71.5],
                                          [90.55, 71.0]],
                                  'width': 0.3}]},
 'C_VMID2_4U7.2': {'net': 'GND',
                   'pin': 'C_VMID2_4U7.2',
                   'segments': [{'layer': 'F.Cu',
                                 'pts': [[89.925, 76.1],
                                         [89.8, 76.1],
                                         [89.8, 74.3],
                                         [89.825, 74.3]],
                                 'width': 0.3}]},
 'U_ADC.8': {'net': 'GND',
             'pin': 'U_ADC.8',
             'segments': [{'layer': 'F.Cu',
                           'pts': [[93.05, 70.6], [92.15, 70.6], [91.6, 70.68], [90.55, 71.0]],
                           'width': 0.18}],
             'via': {'drill': 0.2, 'size': 0.5},
             'vias': [[89.8, 71.5]]}}


def adc2_reservation_errors(floor, route, geometry):
    """Grade native-integer polygon coverage and exact explicit return owners.

    This only reserves F.Cu pours. It neither excludes tracks/vias nor proves
    a filled return graph or KiCad's resolved thermal-spoke predicate.
    """
    from test_adc_source import area_shape
    areas = [a for a in floor['keepouts'] if a['name'] == 'ADC_VMID2_RETURN_POUR']
    if len(areas) != 1:
        return ['reservation-owner']
    area = areas[0]
    errors = []
    if set(area) != {'name', 'layers', 'deny', 'points'} or area['layers'] != ['F.Cu'] or area['deny'] != ['pours']:
        errors.append('pour-only-semantics')
    current = area_shape(area)
    if current.OutlineCount() != 1 or current.HoleCount(0) or current.IsSelfIntersecting():
        return errors + ['simple-polygon']
    old = area_shape(dict(points=VMID2_PROTECTED_POINTS))
    target = next(p for p in geometry['pads'] if p['id'] == 'C_VDDA2_10N.2')
    box = target['shape'].BBox()
    zones = [z for z in floor['zones'] if z['net'] == 'GND' and 'F.Cu' in z['layers']]
    if len(zones) != 1 or zones[0]['clearance'] != .25:
        return errors + ['zone-clearance-floor']
    margin = round(zones[0]['clearance'] * 1e6)
    x0, y0, x1, y1 = (box.GetLeft()-margin, box.GetTop()-margin,
                       box.GetRight()+margin, box.GetBottom()+margin)
    envelope = area_shape(dict(points=[(x/1e6,y/1e6) for x,y in
        [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]))
    def missing(a, b):
        delta = pcbnew.SHAPE_POLY_SET()
        delta.BooleanSubtract(a, b)
        return delta.OutlineCount() != 0
    if missing(old, current):
        errors.append('protected-return-coverage')
    if missing(envelope, current):
        errors.append('full-pad-clearance-coverage')
    expected = pcbnew.SHAPE_POLY_SET()
    expected.BooleanAdd(old, envelope)
    if missing(current, expected):
        errors.append('reservation-scope')
    banks = route['prep']['seed_stubs']['stubs']
    selected = [b for b in banks if b['pin'] in VMID2_RETURN_BANKS]
    if len(selected) != 3 or {b['pin']: b for b in selected} != VMID2_RETURN_BANKS:
        errors.append('seed-drop-ownership')
    drop = pcbnew.VECTOR2I(89800000, 71500000)
    # The existing via-only reservations must keep the designated opening.
    for other in floor['keepouts']:
        if 'F.Cu' not in other['layers'] or 'vias' not in other['deny']:
            continue
        if 'rect' in other:
            x0, y0, x1, y1 = other['rect']
            other = dict(points=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)])
        if area_shape(other).Collide(drop):
            errors.append('designated-drop-excluded')
    return errors


class Adc2ReservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor, cls.route, *_ = load_source()
        cls.geometry = native_geometry(cls.floor)

    def test_full_pad_clearance_and_original_return_coverage(self):
        self.assertEqual(adc2_reservation_errors(self.floor, self.route, self.geometry), [])

    def test_partial_pad_and_lost_return_reservations_are_rejected(self):
        bad = copy.deepcopy(self.floor)
        area = next(a for a in bad['keepouts'] if a['name'] == 'ADC_VMID2_RETURN_POUR')
        area['points'] = VMID2_PROTECTED_POINTS
        self.assertIn('full-pad-clearance-coverage', adc2_reservation_errors(bad, self.route, self.geometry))
        area['points'] = [[89.99,70.94],[91.05,70.94],[91.05,72.06],[89.99,72.06]]
        self.assertIn('protected-return-coverage', adc2_reservation_errors(bad, self.route, self.geometry))

    def test_wrong_layer_or_pour_semantics_are_rejected(self):
        for change in [dict(layers=['B.Cu']), dict(layers=['F.Cu','B.Cu']),
                       dict(deny=[]), dict(deny=['pours','tracks']), dict(deny=['pours','vias'])]:
            bad = copy.deepcopy(self.floor)
            next(a for a in bad['keepouts'] if a['name'] == 'ADC_VMID2_RETURN_POUR').update(change)
            self.assertIn('pour-only-semantics', adc2_reservation_errors(bad, self.route, self.geometry))

    def test_missing_modified_seed_or_excluded_drop_is_rejected(self):
        for pin in VMID2_RETURN_BANKS:
            bad = copy.deepcopy(self.route)
            bad['prep']['seed_stubs']['stubs'] = [b for b in bad['prep']['seed_stubs']['stubs'] if b['pin'] != pin]
            self.assertIn('seed-drop-ownership', adc2_reservation_errors(self.floor, bad, self.geometry))
            bad = copy.deepcopy(self.route)
            next(b for b in bad['prep']['seed_stubs']['stubs'] if b['pin'] == pin)['segments'][0]['width'] += .01
            self.assertIn('seed-drop-ownership', adc2_reservation_errors(self.floor, bad, self.geometry))
        for change in [dict(vias=[[90.55,71.0]]), dict(via=dict(size=.6,drill=.2))]:
            bad = copy.deepcopy(self.route)
            next(b for b in bad['prep']['seed_stubs']['stubs'] if b['pin'] == 'U_ADC.8').update(change)
            self.assertIn('seed-drop-ownership', adc2_reservation_errors(self.floor, bad, self.geometry))
        bad = copy.deepcopy(self.floor)
        bad['keepouts'].append(dict(name='BAD_DROP_EXCLUSION', layers=['F.Cu'],
            deny=['vias'], rect=[89.7,71.4,89.9,71.6]))
        self.assertIn('designated-drop-excluded', adc2_reservation_errors(bad, self.route, self.geometry))


if __name__=='__main__':unittest.main()
