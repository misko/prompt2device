"""Source declarations only: no BOARD construction/load/save or route producer.

These tests deliberately accept a NOT ROUTE-READY source correction. They
grade exact membership and consumer agreement, not physical feasibility.
"""
import copy
import fnmatch
import json
import math
import sys
import unittest
from collections import Counter
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO/'skills/kicad-pcb/scripts'))
from source_inventory import parse_netlist
from route_and_stitch_generic import wave_nets, check_wave_widths, net_class_floors, RouteConfigError
from route_ownership_preflight import audit_config
from rules_audit import parse_mm, parse_amps, required_width_mm
from board_authority import compile_source_prep_authority, verify_authority
from copper_length_audit import load_groups
from test_local_placement_source import source_builder
from source_geometry import point_in_polygon, polygon_edge_distance, segment_distance
from placement_gates import _poly_gap_mm
import pcbnew


def load_source():
    floor = yaml.safe_load((PROJECT/'03_src/floorplan.yaml').read_text())
    route = yaml.safe_load((PROJECT/'03_src/route.yaml').read_text())
    route['_root'] = PROJECT
    nets = yaml.safe_load((PROJECT/'03_src/rules/nets.yaml').read_text())
    stack = yaml.safe_load((PROJECT/'03_src/rules/stackup.yaml').read_text())
    comps, pins, _ = parse_netlist(PROJECT/floor['project']['netlist'])
    return floor, route, nets, stack, comps, pins


def shadow_inputs(route, nets, comps, pins):
    membership = {n: name for name, c in nets['classes'].items() for n in c['nets']}
    groups = wave_nets(route, sorted(set(pins.values())))
    plan_groups = copy.deepcopy(groups)
    waves = []
    for wave in route['route']['waves']:
        members = wave.get('nets', groups.get(wave.get('group', wave['name']), []))
        group = wave.get('group',wave['name'])
        if 'nets' in wave: plan_groups[group] = list(members)
        by_class = {}
        for net in members:
            by_class.setdefault(membership[net], []).append(net)
        # A physical wave may deliberately co-route more than one policy class
        # to solve a shared pin field.  The authority shadow remains class-pure
        # by representing each class as a separate logical ownership row.
        for routing_class in sorted(by_class):
            name = wave['name'] if len(by_class) == 1 else f"{wave['name']}__{routing_class.lower()}"
            row = dict(name=name, routing_class=routing_class)
            if len(by_class) == 1:
                row['group'] = group
            else:
                row['nets'] = by_class[routing_class]
            waves.append(row)
    plan = dict(schema='route-plan-v1', groups=plan_groups, waves=waves,
                exclusions=[dict(pattern='GND', owner='reference-plane', why='Existing common GND pours; local egress remains unproved'),
                            dict(pattern='unconnected-*', owner='intentional-nc', why='Explicit source intentional unused pins; preserve identities')],
                deterministic_owners=[dict(net=net, owner='prep.seed_stubs', why='Complete native local source connection, independently contact-graded and excluded from generic routing')
                                      for net, owner in route['route']['ownership']['nets'].items() if owner['owner']=='prep.seed_stubs'])
    parts = [yaml.safe_load(path.read_text()) for path in (PROJECT/'02_parts').glob('*/part.yaml')]
    observed = dict(schema='observed-source-facts-v1', refs=sorted(comps),
                    nets=sorted(set(pins.values())), mpns=sorted({p['mpn'] for p in parts}))
    return observed, plan


def via_rows(route):
    rows = []
    def walk(value, path):
        if isinstance(value, dict):
            if 'via_size' in value or 'via_drill' in value:
                rows.append((path, value.get('via_size'), value.get('via_drill')))
            if 'size' in value and 'drill' in value:
                rows.append((path, value['size'], value['drill']))
            for key, child in value.items(): walk(child, path+'.'+str(key))
        elif isinstance(value, list):
            for i, child in enumerate(value): walk(child, path+f'[{i}]')
    walk(route, 'route.yaml')
    return rows


def paired_vias_legal(route, floor):
    override_path = REPO/route['route']['common']['fab_overrides']
    overrides = {}
    for raw in override_path.read_text().splitlines():
        line = raw.split('#',1)[0].strip()
        if '=' in line:
            key,value = line.split('=',1)
            overrides[key.strip()] = float(value.strip())
    min_size = overrides['via_diameter']
    min_drill = overrides['via_drill']
    min_annulus = (min_size-min_drill)/2
    for path, size, drill in via_rows(route):
        if size is None or drill is None: return False
        if size < min_size or drill < min_drill: return False
        if (size-drill)/2 + 1e-9 < min_annulus: return False
        if floor['board']['stackup']['nominal_thickness_mm']/drill > 10: return False
    return True


# Exact reviewed source identities; spec/primitive indices are zero based.
# These expectations are independent of the observed population, so deletion,
# substitution or changing a bank to an ordinary width cannot erase a failure.
NARROW_GND_SPECS = {
    ('U_ISO4.4', 0): (.25, [(135.55,54.85),(135.35,55.15)]),
    ('U_LDO.7', 0): (.20, [(63.05,71.5),(63.75,71.5)]),
    ('U_LDO.10', 0): (.20, [(65.95,70.5),(65.15,70.5)]),
    ('U_LDO.11', 0): (.20, [(65.95,70),(65.15,70)]),
    ('U_ADC.6', 0): (.18, [(93.05,69.8),(92.15,69.8),(91.6,69.5)]),
    ('U_ADC.8', 0): (.18, [(93.05,70.6),(92.15,70.6),(91.6,70.68),(90.55,71)]),
    ('C_VMID1_470N.2', 1): (.18, [(89.45,68.7),(89.45,69.17),(91.2,69.17),(91.6,69.5)]),
    ('U_ADC.30', 0): (.18, [(98.95,70.2),(100.0,70.2),(100.5,70.4)]),
    ('U_ADC.44', 0): (.18, [(95.4,67.05),(95.4,65.85),(95.1,65.45)]),
    ('U_ADC.17', 0): (.18, [(95.4,72.95),(95.4,74.15),(95.1,74.55)]),
    ('U_ADC.4', 0): (.18, [(93.05,69),(93.85,69)]),
}
NARROW_GND_SCOPES = {
    'ISO4_GROUND_RETURN_LOCAL': (['GND'], .25),
    'LT3041_GROUND_NECKS': (['GND'], .20),
    'ADC_WEST_LOCAL': (['3V3_ADC','LDO_A_FILT','GND'], .18),
    'ADC_EAST_SUPPLY_LOCAL': (['3V3_ADC','GND'], .18),
    'ADC_FILT_NORTH_LOCAL': (['FILT1P','GND'], .18),
    'ADC_FILT_SOUTH_LOCAL': (['FILT2P','GND'], .18),
    'ADC_CFG3_GND_LOCAL': (['GND'], .18),
}

GROUND_RETURN_SPECS = {
    'C_AUDIO_CT2.2': ((29.225, 61.1), (28.83, 61.5)),
    'U_ISO4.4': ((135.55, 54.85), (135.35, 55.15)),
    'C_ADC_CM4N.2': ((102.83, 65.3), (103.23, 64.9)),
    'R_CFG1.2': ((86.89, 63.9), (86.49, 63.5)),
    'R_AUDIO_PD.2': ((37.17, 59.14), (36.77, 58.74)),
    'C_ISO1.2': ((43.63, 53.3), (43.43, 54.3)),
    'C_ISO2.2': ((75.63, 53.3), (76.03, 52.9)),
}


def narrow_ground_source(floor, route, nets, pins):
    """Complete declared point census and exact rectangle capsule containment.

    Walk the whole route document to detect non-seed point geometry or arcs.
    Future generated fallback copper is not present source geometry; its
    declared GND width floors remain mandatory. No native area-overlap test is
    used: an axis-aligned rectangle contains a straight round capsule exactly
    when both endpoint extrema plus the full radius fit all four bounds.
    """
    errors=[]; point_specs=[]; rows=[]
    def walk(value, path=()):
        if isinstance(value, dict):
            if 'pts' in value:
                point_specs.append((path,value))
            if any(value.get(k) for k in ('arc','arcs')):
                errors.append(('unsupported-arc',path))
            for key, child in value.items(): walk(child,path+(key,))
        elif isinstance(value,list):
            for i,child in enumerate(value): walk(child,path+(i,))
    walk(route)
    banks=route.get('prep',{}).get('seed_stubs',{}).get('stubs',[])
    for path,spec in point_specs:
        if (len(path)!=6 or path[:3] not in {('prep','seed_stubs','stubs'),('stitch','seed_stubs','stubs')}
                or path[4]!='segments' or not isinstance(path[3],int)
                or not isinstance(path[5],int)):
            errors.append(('unsupported-point-source',path)); continue
        bank=route[path[0]]['seed_stubs']['stubs'][path[3]]; owner=bank['pin']; net=bank['net']
        if pins.get(tuple(owner.rsplit('.',1)))!=net:
            errors.append(('pin-net',owner))
        pts=spec['pts']
        if len(pts)<2:
            errors.append(('empty-point-spec',owner,path[5])); continue
        for i,(a,b) in enumerate(zip(pts,pts[1:])):
            rows.append((owner,path[5],i,net,spec['layer'],spec['width'],tuple(a),tuple(b)))
    if (len(banks),len(point_specs),len(rows))!=(230,529,862):
        errors.append(('complete-source-census',len(banks),len(point_specs),len(rows)))
    ground=[r for r in rows if r[3]=='GND']
    if (len({r[0] for r in ground}),len(ground))!=(98,153):
        errors.append(('ground-census',len({r[0] for r in ground}),len(ground)))
    for pin, (start, end) in GROUND_RETURN_SPECS.items():
        matched = [b for b in banks if b.get('pin') == pin]
        expected = {'net': 'GND', 'pin': pin,
                    'via': {'size': .5, 'drill': .2},
                    'segments': [{'layer': 'F.Cu',
                                  'width': .25 if pin == 'U_ISO4.4' else .3,
                                  'pts': [list(start), list(end)]}],
                    'vias': [list(end)]}
        if matched != [expected]:
            errors.append(('ground-return-identity', pin))
    narrow=[r for r in ground if r[5]<.30]
    expected=[(pin,index,i,'GND','F.Cu',width,a,b)
              for (pin,index),(width,pts) in NARROW_GND_SPECS.items()
              for i,(a,b) in enumerate(zip(pts,pts[1:]))]
    if Counter(narrow)!=Counter(expected): errors.append(('narrow-identity',))
    if parse_mm(nets['classes']['GROUND']['min_width'])!=.30:
        errors.append(('ordinary-ground-floor',))
    for name,key in [('pad_rescue','stub_width'),('stub_fallback','width'),('astar_fallback','width')]:
        fallback=route.get('stitch',{}).get(name,{})
        if fallback.get(key)!=.30: errors.append(('fallback-floor',name))
    areas={a['name']:a for a in floor['keepouts']}
    scopes=[s for s in nets['scoped_floors'] if 'GND' in s['nets']]
    actual={s['zone']:(s['nets'],parse_mm(s['min_width'])) for s in scopes}
    if actual!=NARROW_GND_SCOPES or len(scopes)!=len(NARROW_GND_SCOPES):
        errors.append(('ground-scope-authority',))
    coverage=[]
    for row in narrow:
        owner,index,i,net,layer,width,a,b=row; radius=width/2
        bbox=(min(a[0],b[0])-radius,min(a[1],b[1])-radius,
              max(a[0],b[0])+radius,max(a[1],b[1])+radius)
        covered=[]
        for scope in scopes:
            area=areas.get(scope['zone'],{})
            if (net not in scope['nets'] or layer not in area.get('layers',[])
                    or area.get('deny')!=[] or parse_mm(scope['min_width'])>width): continue
            # All six owning scopes are rectangles; reject unproved shapes.
            rect=area.get('rect')
            if not rect or any(key in area for key in ('points','region','ref','polygon')): continue
            if (rect[0]<=bbox[0]+1e-9 and rect[1]<=bbox[1]+1e-9 and
                    bbox[2]<=rect[2]+1e-9 and bbox[3]<=rect[3]+1e-9):
                covered.append(scope['zone'])
        coverage.append(dict(identity=row,bbox=bbox,covering_scopes=covered))
        if not covered: errors.append(('capsule-scope',owner,index,i))
    return dict(errors=errors,point_spec_count=len(point_specs),primitive_count=len(rows),
                narrow=narrow,coverage=coverage)


class RouteSourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor, cls.route, cls.nets, cls.stack, cls.comps, cls.pins = load_source()
        cls.native = set(cls.pins.values())
        cls.groups = wave_nets(cls.route, sorted(cls.native))

    def test_source_census_includes_lt3041_shared_rail_and_explicit_nc(self):
        self.assertEqual(len(self.comps), 333)
        self.assertEqual(len(self.pins), 985)
        self.assertEqual(len(self.native), 221)
        self.assertEqual(sum(n.startswith('unconnected-') for n in self.native), 42)
        self.assertEqual(len(self.native-{'GND'}-{n for n in self.native if n.startswith('unconnected-')}), 178)

    def test_every_connected_net_has_one_exact_class(self):
        members = [n for c in self.nets['classes'].values() for n in c['nets']]
        self.assertFalse(any(any(ch in n for ch in '*?[') for n in members))
        self.assertEqual(set(members), {n for n in self.native if not n.startswith('unconnected-')})
        self.assertEqual(set(Counter(members).values()), {1})
        self.assertEqual({name:len(c['nets']) for name,c in self.nets['classes'].items()},
                         dict(CHASSIS_SHIELD=1, POD_POWER=12, POWER_TRANSIENT=8, POWER_CONTROL=25, BOOTSTRAP=1,
                              QUIET_POWER=6, ANALOG_AUDIO=112, ADC_CLOCK=13, GROUND=1))

    def test_every_generic_net_has_one_exact_wave(self):
        members = []
        for wave in self.route['route']['waves']:
            members.extend(wave.get('nets', self.groups.get(wave.get('group', wave['name']), [])))
        excluded={'GND','LDO_A_FILT','FSYNC_BUF','BCLK_BUF','MCLK_BUF','LDO_D_FILT','VMID1','VMID2','AUDIO_CT',
                  'MCH_MCLK','MCH_BCLK','MCH_FSYNC','ADC_MCLK','ADC_BCLK','ADC_FSYNC','TDM_RAW'}
        self.assertEqual(len(members),163)
        self.assertEqual(set(Counter(members).values()),{1})
        self.assertEqual(set(members),{n for n in self.native if n not in excluded and not n.startswith('unconnected-')})
        self.assertEqual(set(self.route['prep']['waves']['exclude']),excluded|{'unconnected-*'})

    def test_existing_consumer_rejects_ghost_and_glob_groups(self):
        for bad_name in ['FILT1N', 'FILT2N', 'AUDIO_*', 'ADC?P']:
            bad = copy.deepcopy(self.route)
            bad['prep']['waves']['groups']['analog_nonadc'].append(bad_name)
            with self.assertRaises(RouteConfigError): wave_nets(bad, self.native)

    def test_existing_width_consumer_reaches_all_current_wave_nets(self):
        floors = net_class_floors(self.route)
        self.assertEqual(set(floors), {n for n in self.native if not n.startswith('unconnected-')})
        check_wave_widths(self.route, self.groups)

    def test_existing_width_consumer_rejects_underfloor_power(self):
        bad = copy.deepcopy(self.route)
        wave = next(w for w in bad['route']['waves'] if w['name']=='power_3v3_adc')
        wave['power_nets_widths'] = [.60]
        with self.assertRaises(RouteConfigError): check_wave_widths(bad, self.groups)

    def test_declared_current_bound_is_not_lowered_to_fit(self):
        c = self.nets['classes']['POWER_TRANSIENT']
        self.assertEqual(parse_amps(c['current']), (2.5, 'number'))
        required = required_width_mm(2.5)
        self.assertAlmostEqual(required, 1.0630368549, places=8)
        self.assertGreaterEqual(parse_mm(c['min_width']), required)
        self.assertLess(.8, required)  # known-bad historical nominal floor
        self.assertNotIn('pour_fed', c)

    def test_transient_bulk_layers_and_hold_preference_are_explicit(self):
        names = ['power_filt1p','power_filt2p','power_3v3_adc',
                 'power_5v_ldo_hold','power_5v_buck','power_5v_ldo_feed',
                 'power_buck_sw','power_adc_dump']
        waves = [next(w for w in self.route['route']['waves'] if w['name']==name)
                 for name in names]
        self.assertEqual([w['nets'][0] for w in waves],
                         ['FILT1P','FILT2P','3V3_ADC','5V_LDO_HOLD','5V_BUCK',
                          '5V_LDO_FEED','BUCK_SW','ADC_DUMP'])
        for wave in waves:
            self.assertEqual(wave['track_width'], .20)
            expected_clearance = {
                'power_3v3_adc': .25,
                'power_5v_ldo_hold': .25,
                # A 0.20 mm raster request can realize 0.246 mm against a
                # native 0.25 mm foreign-net rule. Keep an explicit margin.
                'power_5v_buck': .21,
            }.get(wave['name'], .20)
            self.assertEqual(wave['clearance'], expected_clearance)
            self.assertEqual(wave['power_nets_widths'], [1.20])
            self.assertEqual(wave['max_ripup'], 0)
        self.assertEqual(next(w for w in waves if w['name']=='power_5v_buck')['layers'],
                         ['F.Cu','B.Cu'])
        self.assertEqual(next(w for w in waves if w['name']=='power_5v_ldo_hold')['layers'],
                         ['F.Cu','B.Cu'])
        self.assertEqual(next(w for w in waves if w['name']=='power_5v_ldo_hold')['layer_costs'],
                         [10.,1.])
        self.assertTrue(all(w['layers']==['F.Cu'] for w in waves
                            if w['name'] not in {'power_filt1p','power_filt2p',
                                                 'power_5v_buck','power_5v_ldo_hold','power_3v3_adc'}))
        for name in ('power_filt1p','power_filt2p','power_3v3_adc'):
            self.assertEqual(next(w for w in waves if w['name']==name)['layers'],
                             ['F.Cu','B.Cu'])
        self.assertEqual(next(w for w in self.route['route']['waves'] if w['name']=='adc')['clearance'], .25)
        self.assertFalse(self.route.get('taps', {}).get('connections'))
        self.assertEqual(self.route['route']['routability']['class_layers']['POWER_TRANSIENT'],
                         ['F.Cu','B.Cu'])
        # This is source intent only. Reopened copper must independently prove it.

    def test_hold_via_ampacity_contract_covers_exact_realized_transfers(self):
        a = self.route['via_ampacity']
        self.assertEqual(a['temperature_rise_c'], 10)
        self.assertEqual(a['capacity_by_finished_hole_mm'], {0.20: 0.55})
        rows = a['transfers']
        self.assertEqual(len(rows), 54)
        self.assertEqual(len({r['name'] for r in rows}), 54)
        self.assertEqual(Counter(r['net'] for r in rows),
                         Counter({'5V_LDO_HOLD':20,'5V_BUCK':4,
                                  'FILT1P':2,'FILT2P':2,'3V3_ADC':18,
                                  '12V_PROTECTED':4,'12V_BUCK_IN':3,'12V_IN':1}))
        leaves=[r for r in rows if r['net']!='12V_IN']
        self.assertTrue(all(r['minimum_vias']==1 and
                            r['required_continuous_a']==.30 for r in leaves))
        self.assertTrue(all(abs((r['rect'][2]-r['rect'][0])-.12)<1e-9 and
                            abs((r['rect'][3]-r['rect'][1])-.12)<1e-9
                            for r in leaves))
        trunk=next(r for r in rows if r['net']=='12V_IN')
        self.assertEqual(trunk['minimum_vias'],2)
        self.assertEqual(trunk['required_continuous_a'],1.0)
        self.assertEqual(trunk['rect'],[27.94,71.84,28.56,72.46])
        self.assertGreaterEqual(2*a['capacity_by_finished_hole_mm'][.20],1.0)

    def test_existing_owner_consumer_and_known_bad_double_owner(self):
        kw = dict(pad_counts=dict(Counter(self.pins.values())), board_nets=self.native, nets_cfg=self.nets)
        self.assertEqual(audit_config(self.route, **kw)['findings'], [])
        bad = copy.deepcopy(self.route)
        bad['route']['ownership']['nets']['3V3_ADC']['owner'] = 'taps.connections'
        self.assertIn('O-DOUBLE', {r['code'] for r in audit_config(bad, **kw)['findings']})
        bad = copy.deepcopy(self.route)
        del bad['route']['ownership']['nets']['3V3_ADC']
        self.assertIn('O-PWR', {r['code'] for r in audit_config(bad, **kw)['findings']})

    def test_audio_monitor_controls_have_exact_codesigned_local_trees(self):
        row=next(x for x in self.route['prep']['seed_stubs']['stubs']
                 if x['pin']=='U_AUDIO.6')
        self.assertEqual(row, {
            'net':'AUDIO_EN', 'pin':'U_AUDIO.6',
            'segments':[
                {'layer':'F.Cu','width':.2,'pts':[[33.6,60.6],[34.4,60.6]]},
                {'layer':'B.Cu','width':.2,'pts':[[34.4,60.6],[33.5,62.89]]},
                {'layer':'F.Cu','width':.2,'pts':[[33.5,62.89],[34.2,62.89]]},
            ],
            'via':{'size':.3,'drill':.2},
            'vias':[[34.4,60.6],[33.5,62.89]],
        })
        timer=next(x for x in self.route['prep']['seed_stubs']['stubs']
                   if x['pin']=='U_AUDIO.5')
        self.assertEqual(timer, {
            'net':'AUDIO_CT', 'pin':'U_AUDIO.5',
            'segments':[{'layer':'F.Cu','width':.15,'pts':[
                [33.9,61.1],[33.425,61.325],[33.325,61.475],[33.35,62.05],
                [33.225,62.25],[33.025,62.35],[32.8,62.325],
                [30.775,61.1],[30.775,59.3],
            ]}],
        })
        self.assertEqual(self.route['route']['ownership']['nets']['AUDIO_CT']['owner'],
                         'prep.seed_stubs')
        self.assertNotIn('AUDIO_CT', self.groups['timers'])
        pwr=next(x for x in self.route['prep']['seed_stubs']['stubs']
                 if x['pin']=='U_AUDIO.3')
        self.assertEqual(pwr['segments'][1], {
            'layer':'B.Cu','width':.2,'pts':[
                [32.96,61.96],[33.2,59.8],[33.2,55.8],[33.6,55.4],
            ]})

    def test_via_pair_not_independent_size_and_drill_floors(self):
        self.assertEqual(len(via_rows(self.route)), 214)
        # Includes prep/stitch banks, typed relocation source/target geometries,
        # the late exact-geometry restoration source/target, and defaults;
        # every declared pair is independently checked below.
        overrides = {s['pin'] for s in self.route['prep']['seed_stubs']['stubs'] if 'via' in s}
        self.assertEqual(len(overrides), 80)
        self.assertIn('R_PRE.2', overrides)
        self.assertTrue(paired_vias_legal(self.route, self.floor))
        bad = copy.deepcopy(self.route)
        bad['route']['common']['via_size'] = .24
        self.assertFalse(paired_vias_legal(bad, self.floor))
        # Known-bad integration: low-current status cannot exempt 10:1 aspect.
        bad = copy.deepcopy(self.route)
        reset = next(e for e in bad['stitch']['relocate_exact_vias']['edits']
                     if e['net']=='ADC_RESET_N')
        reset['to'].update(size=.25, drill=.15)
        self.assertFalse(paired_vias_legal(bad, self.floor))
        via = self.route['stitch']['via']
        self.assertGreaterEqual(via['spacing']-via['drill'], self.floor['design_rules']['hole_to_hole'])
        self.assertGreaterEqual(via['spacing']-via['size'], self.route['stitch']['clearance'])
        self.assertEqual(self.route['stitch']['hole_to_hole']['mode'], 'nudge')
        self.assertNotIn('normalize_vias', self.route['stitch']['passes'])

    def test_stack_public_dimensions_reconcile_both_source_consumers(self):
        physical = self.floor['board']['stackup']
        self.assertEqual(physical['copper_thickness_mm'], [.035,.0152,.0152,.035])
        self.assertEqual([d['thickness_mm'] for d in physical['dielectrics']], [.2104,1.065,.2104])
        self.assertEqual([d['epsilon_r'] for d in physical['dielectrics']], [4.4,4.6,4.4])
        self.assertAlmostEqual(sum(physical['copper_thickness_mm'])+sum(d['thickness_mm'] for d in physical['dielectrics']), 1.5862)
        self.assertEqual([d['thickness_um']/1000 for d in self.stack['copper']], physical['copper_thickness_mm'])
        for d in physical['dielectrics']:
            self.assertTrue({'type','thickness_mm','material','epsilon_r','loss_tangent'} <= set(d))
            self.assertIn('assumed', d['material'])

    def test_shadow_compile_and_hostile_ownership_and_plane_rejection(self):
        observed, plan = shadow_inputs(self.route, self.nets, self.comps, self.pins)
        kwargs = dict(stack=self.stack, observed=observed, route_plan=plan, migration=None)
        receipt = compile_source_prep_authority(**kwargs)
        self.assertEqual(receipt['verdict'], 'PASS')
        self.assertEqual(receipt['coverage']['owned_live_nets'], 221)
        self.assertEqual(verify_authority(receipt, **kwargs), (True, []))
        duplicate = copy.deepcopy(plan)
        duplicate['deterministic_owners'].append(dict(net='ADC_MCLK', owner='prep.seed_stubs', why='Hostile duplicate whole-net owner'))
        self.assertEqual(compile_source_prep_authority(stack=self.stack, observed=observed, route_plan=duplicate)['verdict'], 'FAIL')
        wrong = copy.deepcopy(self.stack)
        wrong['copper'][1]['role'] = 'mixed'
        del wrong['copper'][1]['plane_net']
        self.assertEqual(compile_source_prep_authority(stack=wrong, observed=observed, route_plan=plan)['verdict'], 'FAIL')

    def test_chassis_shadow_matches_exact_outer_layer_shell_owner(self):
        # RED against the pre-fix shadow: the accepted chassis wave named an
        # absent routing class. Adjacency metadata is not a DC ground bond.
        from board_authority import resolve_routing_classes
        self.assertIn('CHASSIS_SHIELD', self.stack['routing_classes'])
        spec = self.stack['routing_classes']['CHASSIS_SHIELD']
        self.assertEqual(spec, dict(allowed_layers=['F.Cu','B.Cu'],
                                    references={}, reference_required=False))
        self.assertEqual(spec['allowed_layers'],
                         self.route['route']['routability']['class_layers']['CHASSIS_SHIELD'])
        self.assertEqual(self.nets['classes']['CHASSIS_SHIELD']['nets'], ['CHASSIS'])
        self.assertNotIn('chassis', self.groups)
        self.assertEqual(self.groups['pod_power'][-1], 'CHASSIS')
        self.assertEqual({pin for pin,net in self.pins.items() if net=='CHASSIS'},
                         {(f'J{i}',str(pin)) for i in range(1,9) for pin in (9,10)})
        self.assertEqual(parse_mm(self.nets['classes']['CHASSIS_SHIELD']['min_width']), .60)
        self.assertEqual(parse_mm(self.nets['classes']['CHASSIS_SHIELD']['clearance']), .25)
        resolved = resolve_routing_classes(self.stack)['classes']['CHASSIS_SHIELD']
        self.assertEqual(resolved['references'], {
            'F.Cu': dict(layer='In1.Cu', net='GND', source='adjacent-role'),
            'B.Cu': dict(layer='In2.Cu', net='GND', source='adjacent-role')})
        observed, plan = shadow_inputs(self.route, self.nets, self.comps, self.pins)
        missing = copy.deepcopy(self.stack)
        del missing['routing_classes']['CHASSIS_SHIELD']
        receipt = compile_source_prep_authority(stack=missing, observed=observed, route_plan=plan)
        self.assertIn('W-CLASS-UNKNOWN', {f['code'] for f in receipt['findings']})
        wrong = copy.deepcopy(self.stack)
        wrong['routing_classes']['CHASSIS_SHIELD']['allowed_layers'].append('In1.Cu')
        receipt = compile_source_prep_authority(stack=wrong, observed=observed, route_plan=plan)
        self.assertIn('S-ROLE-CONFLICT', {f['code'] for f in receipt['findings']})

    def test_adc_clock_layers_match_required_adjacent_ground_references(self):
        from board_authority import resolve_routing_classes
        spec = self.stack['routing_classes']['ADC_CLOCK']
        self.assertEqual(spec, dict(
            allowed_layers=['F.Cu','B.Cu'],
            references={'F.Cu':'In1.Cu','B.Cu':'In2.Cu'},
            reference_required=True))
        self.assertEqual(spec['allowed_layers'],
                         self.route['route']['routability']['class_layers']['ADC_CLOCK'])
        wave=next(w for w in self.route['route']['waves'] if w['name']=='clocks')
        self.assertEqual(wave.get('layers'), ['F.Cu'])
        governed = set(self.nets['classes']['ADC_CLOCK']['nets'])
        for bank in self.route['prep']['seed_stubs']['stubs']:
            if bank['net'] in governed:
                self.assertNotIn('vias', bank)
                self.assertEqual({segment['layer'] for segment in bank['segments']},
                                 {'F.Cu'})
        resolved=resolve_routing_classes(self.stack)['classes']['ADC_CLOCK']
        self.assertEqual(resolved['references'], {
            'F.Cu':dict(layer='In1.Cu',net='GND',source='declared'),
            'B.Cu':dict(layer='In2.Cu',net='GND',source='declared')})
        bad=copy.deepcopy(self.stack)
        del bad['routing_classes']['ADC_CLOCK']['references']['B.Cu']
        inferred=resolve_routing_classes(bad)['classes']['ADC_CLOCK']['references']['B.Cu']
        self.assertEqual(inferred,
                         dict(layer='In2.Cu',net='GND',source='adjacent-role'))
        self.assertNotEqual(inferred['source'],'declared')

        def projection_contract(nets):
            checks=nets['reference_plane_checks']
            actual={(row['signal_layer'],row['reference_layer'],row['reference_net'])
                    for row in checks.values()}
            expected={('F.Cu','In1.Cu','GND')}
            for name in ('MCH_INPUT_SECTIONS','BUFFERED_DIGITAL_SECTIONS'):
                self.assertTrue(nets['length_match'][name]['no_vias'])
            self.assertEqual(actual,expected)
            clock_nets=set(self.nets['classes']['ADC_CLOCK']['nets'])
            for row in checks.values():
                self.assertEqual(set(row['signal_nets']),clock_nets)
                self.assertEqual(row['min_track_clearance_mm'],.25)
                self.assertEqual(row['min_via_clearance_mm'],.50)
        projection_contract(self.nets)
        hostile=copy.deepcopy(self.nets)
        del hostile['reference_plane_checks']['ADC_DIGITAL_RETURN']
        with self.assertRaises(AssertionError):
            projection_contract(hostile)
        hostile=copy.deepcopy(self.nets)
        hostile['reference_plane_checks']['ADC_DIGITAL_RETURN']['signal_nets'].pop()
        with self.assertRaises(AssertionError):
            projection_contract(hostile)
        hostile=copy.deepcopy(self.nets)
        hostile['length_match']['MCH_INPUT_SECTIONS']['no_vias']=False
        with self.assertRaises(AssertionError):
            projection_contract(hostile)

    def test_sense_control_preserves_clearance_and_bootstrap_is_not_quiet(self):
        clock = self.nets['classes']['ADC_CLOCK']['nets']
        control = self.nets['classes']['POWER_CONTROL']
        for net in ['MCH_3V3_SENSE','TDM_SENSE_G','TDM_OE_N']:
            self.assertNotIn(net, clock)
            self.assertIn(net, control['nets'])
        self.assertGreaterEqual(parse_mm(control['clearance']), .25)
        self.assertEqual(self.nets['classes']['BOOTSTRAP']['nets'], ['BUCK_BST'])
        self.assertNotIn('BUCK_BST', control['nets'])

    def test_common_planes_and_only_explicit_bounded_launch_exceptions(self):
        self.assertEqual({z['net'] for z in self.floor['zones']}, {'GND'})
        self.assertEqual(set(self.floor['zones'][0]['layers']), {'F.Cu','In1.Cu','In2.Cu','B.Cu'})
        self.assertEqual(len(self.nets['scoped_floors']), 60)
        # PackageClearanceTests grade 15 additional pad-only, not route, scopes.
        self.assertEqual(len([r for r in self.nets['scoped_clearances'] if not r['zone'].startswith('PKG_PAD_')]), 29)
        self.assertEqual(self.route['route']['ownership']['nets']['LDO_A_FILT']['owner'], 'prep.seed_stubs')
        self.assertFalse(any('NOT ROUTE-READY' in text for text in self.route['flow']['blockers']))
        self.assertTrue(any('FIRST-ARTICLE-ONLY / DO-NOT-ORDER' in text
                            for text in self.route['flow']['blockers']))

    def test_timer_and_isolator_crossover_exceptions_are_exactly_bounded(self):
        areas = {a['name']: a for a in self.floor['keepouts']}
        for index in range(1, 9):
            name = f'ISO{index}_SUPPLY_LOCAL'
            area = areas[name]
            x0 = 41.25 + 32 * (index - 1) if index <= 4 else 38.0 + 32 * (index - 5)
            expected = ([x0, 52.2, x0 + 1.75, 54.05] if index <= 4
                        else [x0, 85.95, x0 + 1.75, 87.8])
            self.assertEqual(area, dict(name=name, layers=['F.Cu'], deny=[],
                                        rect=expected))
            scope = next(s for s in self.nets['scoped_clearances']
                         if s['zone'] == name)
            self.assertEqual(scope['nets'], ['5V_LDO_HOLD', 'AUDIO_EN'])
            self.assertEqual(parse_mm(scope['clearance']), .20)
        self.assertEqual(areas['R_PRE_CROSSOVER_LOCAL'], dict(
            name='R_PRE_CROSSOVER_LOCAL', layers=['F.Cu'], deny=[],
            rect=[49.15, 61.55, 49.5, 62.85]))
        rpre = next(s for s in self.nets['scoped_floors']
                    if s['zone'] == 'R_PRE_CROSSOVER_LOCAL')
        self.assertEqual(rpre['nets'], ['5V_LDO_HOLD'])
        self.assertEqual(parse_mm(rpre['min_width']), .20)

    def test_power_waves_cannot_fallback_below_their_declared_width(self):
        power = [w for w in self.route['route']['waves']
                 if w['name'].startswith('power_')]
        self.assertEqual(len(power), 8)
        for wave in power:
            self.assertIs(wave.get('no_power_tap_neckdown'), True, wave['name'])
            self.assertEqual(len(wave['power_nets']),
                             len(wave['power_nets_widths']), wave['name'])
            self.assertTrue(all(width == 1.2
                                for width in wave['power_nets_widths']))

    def test_three_strict_3v3_attachment_escapes_are_exact_and_bounded(self):
        areas = {a['name']: a for a in self.floor['keepouts']}
        expected = {
            'ADC_FEED_NORTH_TRUNK_ESCAPE': [86.2, 59.5, 91.6, 61.6],
            'ADC_FEED_SOUTH_TRUNK_ESCAPE': [86.2, 78.4, 91.6, 80.5],
            'VMID1_TOP_TRUNK_ESCAPE': [71.7, 75.1, 76.3, 76.7],
        }
        for name, rect in expected.items():
            self.assertEqual(areas[name], dict(
                name=name, layers=['F.Cu'], deny=[], rect=rect))
            scope = next(s for s in self.nets['scoped_floors']
                         if s['zone'] == name)
            self.assertEqual(scope['nets'], ['3V3_ADC'])
            self.assertEqual(parse_mm(scope['min_width']), .60)
        self.assertFalse(any(name.endswith(('_ESCAPE_ENTRY', '_TRANSFER'))
                             for name in areas))
        banks = {b['pin']: b for b in self.route['prep']['seed_stubs']['stubs']}
        self.assertEqual(banks['U_ADC.5']['segments'][-1], dict(
            layer='F.Cu', width=.6,
            pts=[[91.3,60.5],[91.3,59.8],[87.65,59.8],
                 [87.65,61.3],[86.55,61.3]]))
        self.assertEqual(banks['U_ADC.9']['segments'][-1], dict(
            layer='F.Cu', width=.6,
            pts=[[91.3,79.5],[91.3,80.2],[87.65,80.2],
                 [87.65,78.7],[86.55,78.7]]))
        self.assertEqual(banks['R_VMID1_TOP.1']['segments'], [dict(
            layer='F.Cu', width=.6,
            pts=[[72.0,75.425],[72.0,75.4],[73.0,76.4],[74.25,76.4],
                 [74.3,76.35],[74.45,76.35],[75.1,75.7],[76.0,75.7]])])

    def test_four_strict_5v_attachment_escapes_are_exact_and_bounded(self):
        areas = {a['name']: a for a in self.floor['keepouts']}
        expected = {
            'POWER_MONITOR_PULLUP_TRUNK_ESCAPE': ([30.63,53.07,32.7,54.75],.60),
            'POWER_MONITOR_SUPPLY_TRUNK_ESCAPE': ([34.54,56.9,35.32,57.93],.30),
            'AUDIO_MONITOR_SUPPLY_TRUNK_ESCAPE': ([34.72,59.3,35.71,60.83],.30),
            'PRECHARGE_TRUNK_ESCAPE': ([42.78,57.8,44.39,58.4],.60),
        }
        for name, (rect, floor) in expected.items():
            self.assertEqual(areas[name], dict(
                name=name, layers=['F.Cu'], deny=[], rect=rect))
            scope = next(s for s in self.nets['scoped_floors']
                         if s['zone'] == name)
            self.assertEqual(scope['nets'], ['5V_LDO_HOLD'])
            self.assertEqual(parse_mm(scope['min_width']), floor)
        banks = {b['pin']: b for b in self.route['prep']['seed_stubs']['stubs']}
        self.assertEqual(banks['U_PWR.4']['segments'][-1], dict(
            layer='B.Cu', width=1.2,
            pts=[[34.843223,57.626777],[35.403,60.524]]))
        self.assertEqual(banks['U_PWR.4']['via'],dict(size=.5,drill=.2))
        self.assertEqual(banks['U_PWR.4']['vias'],[[34.843223,57.626777]])
        self.assertEqual(banks['U_AUDIO.4']['segments'][-2], dict(
            layer='F.Cu', width=.6, pts=[[35.02,59.6],[35.403,60.524]]))
        self.assertEqual(banks['U_AUDIO.4']['segments'][-1], dict(
            layer='B.Cu', width=1.2,
            pts=[[35.403,60.524],[46.028125,56.6225]]))
        self.assertEqual(banks['U_AUDIO.4']['via'],dict(size=.5,drill=.2))
        self.assertEqual(banks['U_AUDIO.4']['vias'],[[35.403,60.524]])
        self.assertEqual(banks['R_PWR_PU.1']['segments'][0], dict(
            layer='F.Cu', width=.6,
            pts=[[32.4,54.45],[31.130449609397438,53.836346684507085],
                 [30.939107893214896,53.374406918251445]]))
        self.assertEqual(banks['R_PWR_PU.1']['segments'][1], dict(
            layer='F.Cu', width=1.2,
            pts=[[31.002888,53.528387],[30.002888,53.528387]]))
        self.assertEqual(banks['Q_PRE.3']['segments'], [
            dict(layer='F.Cu', width=.6, pts=[[43.0825,58.1],[44.0825,58.1]]),
            dict(layer='B.Cu', width=1.2,
                 pts=[[44.0825,58.1],[43.83559328264077,57.42758817498872]])])
        self.assertEqual(banks['Q_PRE.3']['via'],dict(size=.5,drill=.2))
        self.assertEqual(banks['Q_PRE.3']['vias'],[[44.0825,58.1]])

    def test_native_filter_negative_and_ground_pin_identities(self):
        for pin in ['6','8','17','30','44','49']:
            self.assertEqual(self.pins[('U_ADC',pin)], 'GND')
        self.assertNotIn('FILT1N', self.native)
        self.assertNotIn('FILT2N', self.native)

    def test_rf_stays_disabled_without_denying_digital_impedance_intent(self):
        rf = yaml.safe_load((PROJECT/'03_src/rules/rf.yaml').read_text())['rf']
        self.assertIs(rf['enabled'], False)
        self.assertIn('50 ohm', rf['rationale'])
        self.assertIn('high_speed_digital', rf['rationale'])

    def test_existing_length_consumer_accepts_exact_complete_digital_paths(self):
        groups, _ = load_groups(PROJECT)
        # ADR0019 owns the additional analog groups; retain exact digital tests.
        groups = {k: groups[k] for k in ['MCH_INPUT_SECTIONS', 'BUFFERED_DIGITAL_SECTIONS']}
        covered = set()
        endpoints = set()
        self.assertEqual(len(groups), 2)
        for group in groups.values():
            self.assertTrue(group['no_vias'])
            self.assertEqual(group['stackup_mm'], [.2104, 1.065, .2104])
            self.assertEqual(group['max_spread_mm'], 'report')
            self.assertFalse(group['congruent_pads'])
            for paths in group['paths'].values():
                for path in paths:
                    for segment in path['segments']:
                        covered.add(segment['net'])
                        for kind in ['from', 'to']:
                            ref, pin = segment[kind].rsplit('.', 1)
                            self.assertEqual(self.pins[(ref,pin)], segment['net'])
                            endpoints.add((ref,pin))
        self.assertEqual(covered, set(self.nets['classes']['ADC_CLOCK']['nets']))
        self.assertEqual(endpoints, {pin for pin,net in self.pins.items() if net in covered})

    def test_exact_seed_identity_scope_extent_and_no_high_current_vias(self):
        all_seed = self.route['prep']['seed_stubs']['stubs']
        # ADR0030 adds eight five-bank RJ45 cells, eight fuse exits, and
        # the separately owned north bypass return to the existing 105 banks.
        overlay_pins = ({f'J{i}.{pin}' for i in range(1,9) for pin in (4,5)} |
                        {f'U_ESD{i}.{pin}' for i in range(1,9) for pin in (3,4,5)} |
                        {f'F{i}.2' for i in range(1,9)} | {'C_VDDA1_10N.2'})
        bank_pins = [s['pin'] for s in all_seed]
        self.assertEqual({k:v for k,v in Counter(bank_pins).items() if v>1}, {})
        self.assertEqual(set(bank_pins) & overlay_pins, overlay_pins)
        for bank in all_seed:
            ref, pin = bank['pin'].rsplit('.', 1)
            self.assertEqual(self.pins[(ref, pin)], bank['net'], bank['pin'])
        vmid_escape=next(s for s in all_seed if s['pin']=='R_B1P.2')
        self.assertEqual(vmid_escape, {
            'net':'VMID1_EXT', 'pin':'R_B1P.2',
            'via':{'size':.5,'drill':.2},
            'segments':[
                {'layer':'F.Cu','width':.35,'pts':[[32.79,49.5],[31.8,49.5]]},
                {'layer':'B.Cu','width':.35,'pts':[[31.8,49.5],[31.0,48.7]]},
            ],
            'vias':[[31.8,49.5]],
        })
        # Preserve the adopted west-ADC engineering checks. Digital geometry is
        # independently covered by test_digital_launch_source, not exempted here.
        seed = [s for s in all_seed if s['pin'].startswith(('U_ADC.5','U_ADC.6','U_ADC.7','U_ADC.8','U_ADC.9','C_VMID'))]
        self.assertEqual(len(seed), 9)
        self.assertEqual({s['pin'] for s in seed}, {'U_ADC.5','U_ADC.6','U_ADC.7','U_ADC.8','U_ADC.9',
                         'C_VMID1_470N.2','C_VMID1_4U7.2','C_VMID2_470N.2','C_VMID2_4U7.2'})
        area = next(k for k in self.floor['keepouts'] if k['name']=='ADC_WEST_LOCAL')
        self.assertEqual(area['layers'], ['F.Cu'])
        self.assertEqual(area['deny'], [])
        x0,y0,x1,y1 = area['rect']
        length = 0.; count = 0
        for stub in seed:
            ref,pin = stub['pin'].rsplit('.',1)
            self.assertEqual(self.pins[(ref,pin)], stub['net'])
            if stub.get('vias'): self.assertEqual(stub['net'], 'GND')
            for spec_index,segment in enumerate(stub['segments']):
                self.assertEqual(segment['layer'], 'F.Cu')
                if stub['net']=='3V3_ADC' and spec_index>0:
                    # Full new feed capsules have independent native/extent
                    # and exact length/count coverage in test_adc_feed_source.
                    continue
                if segment['width'] < .30 or stub['net']=='3V3_ADC':
                    radius = segment['width']/2
                    for x,y in segment['pts']:
                        with self.subTest(pin=stub['pin'], spec=spec_index, point=(x,y)):
                            self.assertTrue(x0+radius <= x <= x1-radius and y0+radius <= y <= y1-radius,
                                            f'full {segment["width"]}mm capsule outside ADC_WEST_LOCAL {area["rect"]}')
                if stub['net']=='3V3_ADC':
                    length += sum(math.dist(a,b) for a,b in zip(segment['pts'],segment['pts'][1:]))
                    count += len(segment['pts'])-1
        self.assertAlmostEqual(length, 3.69825107277109)
        self.assertEqual(count, 4)
        power = [w for w in self.route['route']['waves'] if w['name'].startswith('power_')]
        self.assertEqual(len(power), 8)
        self.assertTrue(all(w['max_ripup']==0 for w in power))

    def test_power_dependency_schedule_and_only_proven_hold_crossover(self):
        names = [w['name'] for w in self.route['route']['waves']]
        prefix = ['clocks','timers','power_filt1p','power_filt2p','power_5v_ldo_hold',
                  'power_3v3_adc','power_5v_buck','power_5v_ldo_feed',
                  'power_buck_sw','power_adc_dump']
        self.assertEqual(names[:len(prefix)], prefix)
        self.assertEqual(self.groups['pwr_en'],
                         ['PWR_EN','ADC_RESET_N'])
        self.assertEqual(self.groups['timers'], ['PWR_CT','CFG1','CFG2'])
        self.assertTrue({'CFG1','ADC_RESET_N'}.isdisjoint(
                        self.groups['residual_control']))
        residual = next(w for w in self.route['route']['waves']
                        if w['name'] == 'residual_control')
        self.assertEqual(residual['realized_width'], {
            'nominal': .2,
            'minimum': .18,
            'max_subnominal_length_per_net': 2.733,
            'max_subnominal_segments_per_net': 3,
        })
        banks = self.route['prep']['seed_stubs']['stubs']
        self.assertFalse(any(b['net']=='5V_BUCK' and b['pin']=='D_HOLD.2'
                             for b in banks))
        buck = next(b for b in banks if b['net']=='5V_BUCK' and
                    b['pin']=='R_PWR_TOP.1')
        self.assertEqual(buck['vias'], [[30.825,55.7]])
        self.assertEqual([(x['layer'],x['width']) for x in buck['segments']],
                         [('F.Cu',.3),('B.Cu',1.2)])
        bridge = next(b for b in banks if b['net']=='5V_LDO_HOLD' and b['pin']=='R_PRE.2')
        self.assertEqual(bridge['via'], {'size':.5,'drill':.2})
        self.assertEqual(bridge['vias'], [[49.3625,62.7],[43.3,51.65]])
        self.assertEqual([(s['layer'],s['width'],s['pts']) for s in bridge['segments']], [
            ('F.Cu',.2,[[49.3625,61.7],[49.3625,62.7]]),
            ('B.Cu',1.2,[[49.3625,62.7],[43.3,51.65]])])
        self.assertNotIn([54.85,73], bridge['vias'])
        self.assertEqual(self.route['prep']['seed_stubs']['clearance'], .2)
        for net,pin,end in [('PWR_CT','U_PWR.5',[34.5,56.7])]:
            bank = next(b for b in banks if b['pin']==pin)
            self.assertEqual(bank, {'net':net,'pin':pin,'segments':[
                {'layer':'F.Cu','width':.2,'pts':[[33.6,end[1]],end]}]})

    def test_isolated_adopted_seed_geometry_and_three_pose_screen(self):
        # Isolated library footprints only: no BOARD constructor/load/save.
        source = source_builder(self.floor)
        pads=[]; footprints={}
        for ref,(fpid,_) in self.comps.items():
            lib,name=fpid.split(':')
            directory=PROJECT/'03_src/lib/crow_audio_carrier.pretty' if lib=='crow_audio_carrier' else Path('/usr/share/kicad/footprints')/(lib+'.pretty')
            fp=pcbnew.FootprintLoad(str(directory),name)
            self.assertIsNotNone(fp)
            x,y,rot,_=source.initial_pose(ref)
            fp.SetOrientationDegrees(rot)
            fp.SetPosition(pcbnew.VECTOR2I(round(x*1e6),round(y*1e6)))
            fp.BuildCourtyardCaches(); footprints[ref]=fp
            for p in fp.Pads():
                if not p.IsOnCopperLayer() or not p.IsOnLayer(pcbnew.F_Cu): continue
                poly=p.GetEffectivePolygon(pcbnew.F_Cu).Outline(0)
                points=[(poly.CPoint(i).x/1e6,poly.CPoint(i).y/1e6) for i in range(poly.PointCount())]
                pads.append((ref+'.'+p.GetNumber(),self.pins[(ref,p.GetNumber())],points))
        def distance(poly,a,b):
            return 0. if point_in_polygon(a,poly) or point_in_polygon(b,poly) else polygon_edge_distance(poly,a,b)
        segments=[]
        from test_regulator_source import CELL_PINS as REGULATOR_PINS
        original_west={'U_ADC.5','U_ADC.6','U_ADC.7','U_ADC.8','U_ADC.9',
                      'C_VMID1_470N.2','C_VMID1_4U7.2','C_VMID2_470N.2','C_VMID2_4U7.2'}
        for stub in self.route['prep']['seed_stubs']['stubs']:
            # Preserve this older ordinary-clearance screen for its original
            # west/regulator subjects. ADC additions have an independent native
            # all-pad/all-seed/all-layer-via screen in test_adc_source, including
            # cross-interactions here, and exact named0.20mm pin-pitch rules.
            if stub['pin'] not in original_west|REGULATOR_PINS:continue
            for s in stub['segments']:
                if s['layer'] != 'F.Cu':
                    continue
                for a,b in zip(s['pts'],s['pts'][1:]):
                    segments.append((stub['net'],a,b,s['width']))
                    gap=min(distance(poly,a,b)-s['width']/2 for _,net,poly in pads if net!=stub['net'])
                    self.assertGreaterEqual(gap+1e-6,.25 if s['width']>=.30 else .20, stub['pin'])
        for i,(net,a,b,w) in enumerate(segments):
            for net2,c,d,w2 in segments[i+1:]:
                if net==net2: continue
                self.assertGreaterEqual(segment_distance(a,b,c,d)-(w+w2)/2+1e-6,.25 if max(w,w2)>=.30 else .20)
        moves={'C_LDO_A':[89.93,70.05,180], 'C_VDDA1_4U7':[87.45,68.4,180], 'C_VDDA2_4U7':[87.45,71.6,180]}
        for ref,pose in moves.items():
            self.assertEqual(self.floor['placement']['anchors'][ref],pose)
            env=footprints[ref].GetCourtyard(pcbnew.F_CrtYd)
            for other,fp in footprints.items():
                if other==ref: continue
                poly=fp.GetCourtyard(pcbnew.F_CrtYd)
                if poly.OutlineCount(): self.assertGreaterEqual(_poly_gap_mm(env,poly,.10)+1e-6,.10,(ref,other))
                for p in fp.Pads():
                    if p.IsOnCopperLayer() and p.IsOnLayer(pcbnew.F_Cu):
                        self.assertFalse(env.Collide(p.GetEffectiveShape(pcbnew.F_Cu),pcbnew.FromMM(.10)),(ref,other,p.GetNumber()))
                if poly.OutlineCount():
                    for p in footprints[ref].Pads():
                        if p.IsOnCopperLayer() and p.IsOnLayer(pcbnew.F_Cu):
                            self.assertFalse(poly.Collide(p.GetEffectiveShape(pcbnew.F_Cu),pcbnew.FromMM(.10)),(other,ref,p.GetNumber()))
        # Hostile historical single-cap west shift without companion shifts.
        bad=footprints['C_VDDA1_4U7']
        bad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(87.35),pcbnew.FromMM(68.7)))
        bad.BuildCourtyardCaches()
        self.assertLess(_poly_gap_mm(footprints['C_LDO_A'].GetCourtyard(pcbnew.F_CrtYd),bad.GetCourtyard(pcbnew.F_CrtYd),.10),.10)


    def test_complete_narrow_ground_source_capsules(self):
        # Actual RED with the exact prior floorplan: two VMID1 capsules escape
        # xmin89.5. GREEN requires the reviewed89.35 boundary and all identities.
        result=narrow_ground_source(self.floor,self.route,self.nets,self.pins)
        self.assertEqual(result['errors'],[])
        self.assertEqual(len(result['narrow']),19)
        self.assertEqual(Counter(r[5] for r in result['narrow']),{.18:15,.20:3,.25:1})
        self.assertAlmostEqual(sum(math.dist(r[6],r[7]) for r in result['narrow']),15.267592598637211,places=10)
        area=next(a for a in self.floor['keepouts'] if a['name']=='ADC_WEST_LOCAL')
        self.assertEqual(area,dict(name='ADC_WEST_LOCAL',layers=['F.Cu'],deny=[],rect=[89.35,67.7,93.6,72.35]))
        for key,value_key,value in [('scoped_floors','min_width',.18),('scoped_clearances','clearance',.20)]:
            scope=next(s for s in self.nets[key] if s['zone']=='ADC_WEST_LOCAL')
            self.assertEqual(scope['nets'],['3V3_ADC','LDO_A_FILT','GND'])
            self.assertEqual(parse_mm(scope[value_key]),value)
        for name in NARROW_GND_SCOPES:
            area=next(a for a in self.floor['keepouts'] if a['name']==name)
            self.assertEqual(area['layers'],['F.Cu']);self.assertEqual(area['deny'],[])

    def test_narrow_ground_scope_hostile_controls(self):
        def check(floor=None,route=None,nets=None):
            return narrow_ground_source(self.floor if floor is None else floor,
                self.route if route is None else route,self.nets if nets is None else nets,self.pins)['errors']
        def west(floor):return next(a for a in floor['keepouts'] if a['name']=='ADC_WEST_LOCAL')
        old=copy.deepcopy(self.floor);west(old)['rect'][0]=89.5
        self.assertEqual([e for e in check(floor=old) if e[0]=='capsule-scope'],
            [('capsule-scope','C_VMID1_470N.2',1,0),('capsule-scope','C_VMID1_470N.2',1,1)])
        # Centers fit with xmin89.4, but the complete89.36 round end does not.
        escaped=copy.deepcopy(self.floor);west(escaped)['rect'][0]=89.4
        self.assertEqual(len([e for e in check(floor=escaped) if e[0]=='capsule-scope']),2)
        for change in [dict(layers=['B.Cu']),dict(deny=['tracks'])]:
            bad=copy.deepcopy(self.floor);west(bad).update(change)
            self.assertTrue(any(e[0]=='capsule-scope' for e in check(floor=bad)))
        for change in [dict(nets=['3V3_ADC','LDO_A_FILT']),dict(min_width='0.20mm')]:
            bad=copy.deepcopy(self.nets)
            next(s for s in bad['scoped_floors'] if s['zone']=='ADC_WEST_LOCAL').update(change)
            self.assertTrue(any(e[0]=='capsule-scope' for e in check(nets=bad)))
        # The native consumer gives points/region precedence over rect.
        # Mixed geometry must not be graded using the convenient rectangle.
        for key,value in [('points',[[0,0],[1,0],[1,1],[0,1]]),
                          ('region','another-area'),('ref','U_ADC'),
                          ('polygon',[[0,0],[1,0],[1,1]])]:
            bad=copy.deepcopy(self.floor);west(bad)[key]=value
            self.assertTrue(any(e[0]=='capsule-scope' for e in check(floor=bad)),key)
        # A nonwest narrow owner must also be checked by full radius.
        bad=copy.deepcopy(self.route)
        next(b for b in bad['prep']['seed_stubs']['stubs'] if b['pin']=='U_ADC.30')['segments'][0]['pts'][-1][0]=107.0
        self.assertIn(('capsule-scope','U_ADC.30',0,1),check(route=bad))

    def test_narrow_ground_population_and_nonseed_hostile_controls(self):
        def errors(route):return narrow_ground_source(self.floor,route,self.nets,self.pins)['errors']
        for (pin,index) in NARROW_GND_SPECS:
            bad=copy.deepcopy(self.route)
            bank=next(b for b in bad['prep']['seed_stubs']['stubs'] if b['pin']==pin)
            bank['segments'][index]['pts'].pop()
            self.assertIn(('narrow-identity',),errors(bad),pin)
        for mutation in ['empty','missing','wrong-net','wrong-layer','ordinary-width','unrelated-owner']:
            bad=copy.deepcopy(self.route);banks=bad['prep']['seed_stubs']['stubs']
            bank=next(b for b in banks if b['pin']=='U_ADC.30')
            if mutation=='empty':banks.clear()
            elif mutation=='missing':banks.remove(bank)
            elif mutation=='wrong-net':bank['net']='3V3_ADC'
            elif mutation=='wrong-layer':bank['segments'][0]['layer']='B.Cu'
            elif mutation=='ordinary-width':bank['segments'][0]['width']=.30
            else:bank['pin']='U_ADC.31'
            self.assertIn(('narrow-identity',),errors(bad),mutation)
        bad=copy.deepcopy(self.route)
        bad['taps']={'connections':[dict(net='GND',layer='F.Cu',width=.18,pts=[[0,0],[1,0]])]}
        self.assertTrue(any(e[0]=='unsupported-point-source' for e in errors(bad)))
        bad=copy.deepcopy(self.route)
        ground=next(b for b in bad['stitch']['seed_stubs']['stubs'] if b['net']=='GND')
        ground['segments'][0]['width']=.18
        self.assertIn(('narrow-identity',),errors(bad))
        bad=copy.deepcopy(self.route);bad['stitch']['arcs']=[dict(net='GND',width=.18)]
        self.assertTrue(any(e[0]=='unsupported-arc' for e in errors(bad)))
        for name,key in [('pad_rescue','stub_width'),('stub_fallback','width'),('astar_fallback','width')]:
            bad=copy.deepcopy(self.route);bad['stitch'][name][key]=.18
            self.assertIn(('fallback-floor',name),errors(bad))


if __name__ == '__main__': unittest.main()
