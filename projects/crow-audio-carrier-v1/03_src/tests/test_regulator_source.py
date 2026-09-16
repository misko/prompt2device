"""LT3041 source-native regression; isolated footprints, never a BOARD.

ADR0025 replaces TPS pin identities and EP-referenced feedback with actual
LT3041 OUTS/SET capacitor-terminal Kelvin connections. Source geometry does not
certify filled-plane returns, ampacity, stability, thermal resistance or DRC.
"""
import copy
import math
import unittest
from collections import Counter
import pcbnew
from test_digital_launch_source import native_geometry, segment_rows, primitive, rect_shape
from test_route_source_contract import load_source
from rules_audit import parse_mm

POWER_PINS = {'U_LDO.1', 'U_LDO.2', 'U_LDO.3', 'U_LDO.13', 'U_LDO.14', 'U_BUCK.5'}
QUIET_PINS = {'C_LDO_NR4.2', 'C_LDO_NR5.2', 'R_LDO_SET.2'}
CELL_PINS = POWER_PINS | QUIET_PINS | {
    'U_LDO.5', 'U_LDO.7', 'U_LDO.8', 'U_LDO.9', 'U_LDO.10',
    'U_LDO.11', 'U_LDO.12', 'C_LDO_IN.1', 'C_LDO_IN.2',
    'C_LDO_OUT.1', 'C_LDO_OUT.2', 'C_OPA_BULK.1', 'C_OPA_BULK.2',
    'C_LDO_NR4.1', 'C_LDO_NR5.1'}

def via_rows(route):
    result=[]
    for stub in route['prep']['seed_stubs']['stubs']:
        via=stub.get('via',route['prep']['seed_stubs']['via'])
        for i,at in enumerate(stub.get('vias',[])):
            # Native zero-length capsule is an exact circle; unlike the
            # SHAPE_CIRCLE SWIG overload it accepts arbitrary native shapes.
            result.append(dict(id=stub['pin']+':via'+str(i),pin=stub['pin'],net=stub['net'],at=at,size=via['size'],drill=via['drill'],shape=primitive(at,at,via['size']),hole=primitive(at,at,via['drill'])))
    return result

def contained(row,area,margin=0.):
    """True when the complete round-capped source segment is in a rule area."""
    r=row['width']/2+margin
    if area['layers'] != ['F.Cu']:
        return False
    if 'rect' in area:
        x0,y0,x1,y1=area['rect']
        return all(x0+r-1e-9<=x<=x1-r+1e-9 and
                   y0+r-1e-9<=y<=y1-r+1e-9
                   for x,y in [row['a'],row['b']])
    pts=area.get('points',[])
    if len(pts) < 3:
        return False
    area2=sum(x*y2-x2*y for (x,y),(x2,y2) in
              zip(pts,pts[1:]+pts[:1]))
    orient=1 if area2 > 0 else -1
    # These source permission polygons are convex. Requiring every endpoint
    # to sit at least one copper radius inside every edge proves the entire
    # straight capsule is contained; refuse concave polygons here.
    turns=[]
    for a,b,c in zip(pts,pts[1:]+pts[:1],pts[2:]+pts[:2]):
        turns.append((b[0]-a[0])*(c[1]-b[1])-
                     (b[1]-a[1])*(c[0]-b[0]))
    if any(orient*t < -1e-9 for t in turns):
        return False
    for x,y in [row['a'],row['b']]:
        for (x1,y1),(x2,y2) in zip(pts,pts[1:]+pts[:1]):
            length=math.hypot(x2-x1,y2-y1)
            inward=orient*((x2-x1)*(y-y1)-(y2-y1)*(x-x1))/length
            if inward < r-1e-6:
                return False
    return True

def connected_reach(route,geometry,start):
    """Native layer-aware contact graph; only physical barrels transfer layers."""
    net=next(p['net'] for p in geometry['pads'] if p['id']==start)
    plated={h['id'] for h in geometry.get('holes',[]) if h.get('net')==net}
    nodes=[dict(p,layers={'F.Cu','B.Cu'} if p['id'] in plated else {'F.Cu'}) for p in geometry['pads'] if p['net']==net]
    nodes += [dict(r,id='segment:'+str(i),layers={r['layer']}) for i,r in enumerate(segment_rows(route)) if r['net']==net]
    nodes += [dict(v,layers={'F.Cu','B.Cu'}) for v in via_rows(route) if v['net']==net]
    reached={i for i,n in enumerate(nodes) if n['id']==start};todo=list(reached)
    while todo:
        i=todo.pop()
        for j,node in enumerate(nodes):
            if j not in reached and nodes[i]['layers'] & node['layers'] and pcbnew.SHAPE.Collide(nodes[i]['shape'],node['shape'],0):reached.add(j);todo.append(j)
    return sorted(nodes[i]['id'] for i in reached if not nodes[i]['id'].startswith('segment:'))


def extent_errors(floor, route, nets):
    areas = {a['name']: a for a in floor['keepouts']}
    errors = []
    floors = {net: parse_mm(cls['min_width'])
              for cls in nets['classes'].values() for net in cls['nets']}
    for row in segment_rows(route):
        if row['id'] not in CELL_PINS:
            continue
        minimum = floors[row['net']]
        if row['width'] >= minimum - 1e-9:
            continue
        eligible = [areas[r['zone']] for r in nets['scoped_floors']
                    if row['net'] in r.get('nets', [])
                    and parse_mm(r['min_width']) <= row['width']]
        if not any(a['deny'] == [] and contained(row, a) for a in eligible):
            errors.append(row['id'])
    return sorted(set(errors))


def cut_reach(route, geometry, start, junction):
    """Remove a capacitor land: distinct sense/load branches must disconnect."""
    g = {**geometry, 'pads': [p for p in geometry['pads'] if p['id'] != junction]}
    return set(connected_reach(route, g, start))


def quiet_errors(floor, route, geometry):
    errors = []
    pads = {p['id']: p for p in geometry['pads']}
    mask = [a for a in floor['keepouts'] if a['name'].startswith('LT3041_QUIET_')
            and a['layers'] == ['F.Cu'] and set(a['deny']) == {'vias', 'pours'}]
    if len(mask) != 3:
        errors.append('missing-quiet-pour-reservation')
    for pin in QUIET_PINS:
        b = pads[pin]['shape'].BBox()
        box = [b.GetLeft()/1e6, b.GetTop()/1e6, b.GetRight()/1e6, b.GetBottom()/1e6]
        if not any(a['rect'][0]+.05 <= box[0] and a['rect'][1]+.05 <= box[1]
                   and a['rect'][2]-.05 >= box[2] and a['rect'][3]-.05 >= box[3]
                   for a in mask):
            errors.append('unmasked-pad:'+pin)
        reached = cut_reach(route, geometry, pin, 'C_LDO_OUT.2')
        if reached - QUIET_PINS:
            errors.append('pre-cap-ground-touch:'+pin+':'+str(sorted(reached-QUIET_PINS)))
    for row in segment_rows(route):
        if row['id'] not in QUIET_PINS:
            continue
        steps = max(1, math.ceil(math.dist(row['a'], row['b'])/.005))
        for i in range(steps+1):
            at = [row['a'][j]+(row['b'][j]-row['a'][j])*i/steps for j in range(2)]
            radius = row['width']/2+.05
            if not any(a['rect'][0]+radius <= at[0] <= a['rect'][2]-radius
                       and a['rect'][1]+radius <= at[1] <= a['rect'][3]-radius for a in mask):
                errors.append('unmasked-trace:'+row['id'])
                break
    return sorted(set(errors))


def inspect(floor, route, nets, geometry):
    from test_thermal_source import thermal_rows
    # Existing ADC source-test reader handles exact concave polygon keepouts.
    # Import here because that module imports our via/extent helpers.
    from test_adc_source import area_shape
    rows = segment_rows(route)
    selected = [r for r in rows if r['id'] in CELL_PINS]
    ordinary = via_rows(route)
    thermal = thermal_rows(floor, geometry)
    vias = ordinary + thermal
    failures = []
    counts = Counter()
    pads = {p['id']: p for p in geometry['pads']}
    def check(a, b, kind, gap):
        counts[kind] += 1
        if a['shape'].Collide(b['shape'], round(gap*1e6)-2 if gap else 0):
            failures.append((kind, a['id'], b['id']))
    for pin in CELL_PINS:
        own = [r for r in selected if r['id'] == pin]
        if not own or any(r['net'] != pads[pin]['net'] for r in own):
            failures.append(('pin-net-or-coverage', pin))
        elif not any(r['shape'].Collide(pads[pin]['shape'], 0) for r in own):
            failures.append(('unreached-pin', pin))
    for row in selected:
        if row['layer'] not in {'F.Cu','B.Cu'}:
            failures.append(('unreviewed-layer', row['id']))
        bounds = floor['board']['outline']; radius = row['width']/2
        if not all(bounds['x0']+.8+radius <= x <= bounds['x1']-.8-radius
                   and bounds['y0']+.8+radius <= y <= bounds['y1']-.8-radius
                   for x, y in (row['a'], row['b'])):
            failures.append(('edge', row['id']))
        if row['layer']=='F.Cu':
            for pad in pads.values():
                if row['net'] != pad['net']:
                    check(row, pad, 'segment/native-pad', .25)
        for hole in geometry['holes']:
            check(row, hole, 'segment/native-hole', .255)
        for area in floor['keepouts']:
            if 'F.Cu' in area['layers'] and 'tracks' in area['deny']:
                check(row, dict(id=area['name'], shape=area_shape(area)), 'segment/keepout', 0)
        for via in vias:
            if row['net'] != via['net']:
                check(row, via, 'segment/via', .25)
            # Only each ordinary via's own authored connection is intentional.
            # No thermal-hole shortcut or blanket same-GND drill exemption.
            if via['pin'] != row['id'] or via in thermal:
                check(row, dict(id=via['id'], shape=via['hole']), 'segment/via-hole', .255)
    for i, row in enumerate(rows):
        for other in rows[i+1:]:
            if (row['id'] in CELL_PINS or other['id'] in CELL_PINS) and row['net'] != other['net'] and row['layer']==other['layer']:
                check(row, other, 'segment/segment', .25)
    for via in [v for v in ordinary if v['pin'] in CELL_PINS]:
        for fp in geometry['footprints']:
            for pad in fp.Pads():
                for layer in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
                    if pad.IsOnCopperLayer() and pad.IsOnLayer(layer):
                        check(dict(id=via['id'], shape=via['hole']),
                              dict(id=fp.GetReference()+'.'+pad.GetNumber(), shape=pad.GetEffectiveShape(layer)),
                              'via/no-pad-drill', .255)
        for pad in pads.values():
            if pad['net'] != via['net']:
                check(via, pad, 'via/native-pad', .25)
        for hole in geometry['holes']:
            check(dict(id=via['id'], shape=via['hole']), hole, 'via/native-hole', .5)
        for area in floor['keepouts']:
            if 'F.Cu' in area['layers'] and 'vias' in area['deny']:
                check(via, dict(id=area['name'], shape=area_shape(area)), 'via/keepout', 0)
        for other in vias:
            if other['id'] == via['id']:
                continue
            check(dict(id=via['id'], shape=via['hole']),
                  dict(id=other['id'], shape=other['hole']), 'via/hole-pair', .5)
            if other['net'] != via['net']:
                check(via, other, 'via/copper-pair', .25)
        for row in rows:
            if row['net'] != via['net']:
                check(via, row, 'via/segment', .25)
    failures += [('extent', p) for p in extent_errors(floor, route, nets)]
    return dict(failures=failures, checks=dict(counts), segments=len(selected),
                vias=sum(v['pin'] in CELL_PINS for v in ordinary))


class RegulatorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor, cls.route, cls.nets, *_ = load_source()
        cls.geometry = native_geometry(cls.floor)

    def test_all_target_pins_and_simultaneous_native_geometry(self):
        report = inspect(self.floor, self.route, self.nets, self.geometry)
        self.assertEqual(report['failures'], [])
        self.assertEqual(report['vias'], 6)
        self.assertGreater(report['checks']['segment/native-pad'], 25000)
        self.assertEqual(len(CELL_PINS), 24)

    def test_each_exact_pin_reaches_its_real_destination(self):
        goals = {**{f'U_LDO.{p}':'C_LDO_IN.1' for p in (1, 2, 3, 8)},
                 **{f'U_LDO.{p}':'C_LDO_OUT.1' for p in (12, 13, 14)},
                 **{f'U_LDO.{p}':'U_LDO.15' for p in (7, 10, 11)},
                 **{p:'C_LDO_OUT.2' for p in QUIET_PINS},
                 'U_LDO.9':'R_LDO_SET.1', 'C_LDO_NR4.1':'C_LDO_NR5.1',
                 'C_OPA_BULK.1':'C_LDO_OUT.1', 'U_BUCK.5':'L_BUCK.1'}
        for start, end in goals.items():
            self.assertIn(end, connected_reach(self.route, self.geometry, start), (start, end))
        for pin, count in [('C_LDO_IN.2', 1), ('C_LDO_OUT.2', 2), ('C_OPA_BULK.2', 1)]:
            reached = connected_reach(self.route, self.geometry, pin)
            self.assertEqual(len([p for p in reached if p.startswith(pin+':via')]), count)
        # A source graph must not pretend unfilled reference-plane connections.
        self.assertNotIn('C_LDO_IN.2', connected_reach(self.route, self.geometry, 'C_LDO_OUT.2'))

    def test_outs_sense_has_no_pre_cap_load_contact(self):
        self.assertEqual(cut_reach(self.route, self.geometry, 'U_LDO.12', 'C_LDO_OUT.1'), {'U_LDO.12'})
        bad = copy.deepcopy(self.route)
        stub = next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin'] == 'U_LDO.12')
        stub['segments'].append(dict(layer='F.Cu', width=.2, pts=[[65.95, 69.5], [65.95, 69.0]]))
        self.assertIn('U_LDO.13', cut_reach(bad, self.geometry, 'U_LDO.12', 'C_LDO_OUT.1'))

    def test_quiet_return_mask_and_single_cap_terminal(self):
        self.assertEqual(quiet_errors(self.floor, self.route, self.geometry), [])
        bad = copy.deepcopy(self.floor)
        bad['keepouts'] = [a for a in bad['keepouts'] if not a['name'].startswith('LT3041_QUIET_')]
        self.assertIn('missing-quiet-pour-reservation', quiet_errors(bad, self.route, self.geometry))
        badroute = copy.deepcopy(self.route)
        stub = next(s for s in badroute['prep']['seed_stubs']['stubs'] if s['pin'] == 'C_LDO_NR4.2')
        stub['vias'] = [[69.28, 72.0]]
        self.assertTrue(any(e.startswith('pre-cap-ground-touch:') for e in quiet_errors(self.floor, badroute, self.geometry)))

    def test_full_width_pin_necks_fail_clearance(self):
        bad = copy.deepcopy(self.route)
        for s in bad['prep']['seed_stubs']['stubs']:
            if s['pin'] in {'U_LDO.3', 'U_LDO.13', 'U_BUCK.5'}:
                s['segments'][0]['width'] = 1.2
        failures = inspect(self.floor, bad, self.nets, self.geometry)['failures']
        for pin in ('U_LDO.3', 'U_LDO.13', 'U_BUCK.5'):
            self.assertTrue(any(f[0] == 'segment/native-pad' and f[1] == pin for f in failures), pin)

    def test_wrong_pin_net_and_missing_branch_fail(self):
        for pin in ('U_LDO.1', 'U_LDO.7', 'U_LDO.12', 'U_LDO.14'):
            bad = copy.deepcopy(self.route)
            bad['prep']['seed_stubs']['stubs'] = [s for s in bad['prep']['seed_stubs']['stubs'] if s['pin'] != pin]
            self.assertIn(('pin-net-or-coverage', pin), inspect(self.floor, bad, self.nets, self.geometry)['failures'])
        bad = copy.deepcopy(self.route)
        next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin'] == 'U_LDO.1')['net'] = '3V3_ADC'
        self.assertIn(('pin-net-or-coverage', 'U_LDO.1'), inspect(self.floor, bad, self.nets, self.geometry)['failures'])

    def test_extended_neck_or_removed_scope_cannot_pass(self):
        bad = copy.deepcopy(self.route)
        next(s for s in bad['prep']['seed_stubs']['stubs'] if s['pin'] == 'U_LDO.3')['segments'][0]['pts'][-1] = [60, 69.5]
        self.assertIn('U_LDO.3', extent_errors(self.floor, bad, self.nets))
        nets = copy.deepcopy(self.nets)
        nets['scoped_floors'] = [r for r in nets['scoped_floors'] if r['zone'] != 'LT3041_OUTPUT_NECKS']
        self.assertIn('U_LDO.13', extent_errors(self.floor, self.route, nets))

    def test_buck_bootstrap_return_is_source_owned_and_power_stays_generic(self):
        from route_and_stitch_generic import wave_nets
        groups = wave_nets(self.route, set(self.geometry['pins'].values()))
        power={net for wave in self.route['route']['waves']
               if wave['name'].startswith('power_') for net in wave['nets']}
        self.assertTrue({'BUCK_SW', '3V3_ADC', '5V_LDO_HOLD'} <= power)
        self.assertNotIn('BUCK_SW', {net for values in groups.values() for net in values})
        self.assertIn('C_BUCK_BST.2', connected_reach(self.route, self.geometry, 'U_BUCK.5'))
        branch = next(s for s in self.route['prep']['seed_stubs']['stubs']
                      if s['pin'] == 'C_BUCK_BST.2')
        self.assertEqual(branch, {'net':'BUCK_SW','pin':'C_BUCK_BST.2',
            'segments':[{'layer':'F.Cu','width':.2,
                         'pts':[[44.48,62.95],[44.5,65.45]]}]})


    def test_polygon_via_keepout_uses_actual_shape_and_scope(self):
        # Before this repair, valid current via-only polygons raised KeyError
        # in inspect before any classification. This is a real consumer error,
        # not an import/setup failure or a false-PASS regression claim.
        # A concave L has the via inside its bbox but outside actual copper;
        # the enclosing triangle must be detected. Native board DRC stays owed.
        via = next(v for v in via_rows(self.route) if v['pin'] in CELL_PINS)
        x, y = via['at']
        self.assertLess(via['size'] / 2, 1.)
        outlines = {
            'concave': [(-2., -2.), (2., -2.), (2., -1.),
                        (-1., -1.), (-1., 2.), (-2., 2.)],
            'enclosing': [(-1., -1.), (1., -1.), (0., 1.)],
        }
        for shape, layers, deny, expected in [
            ('concave', ['F.Cu'], ['vias'], False),
            ('enclosing', ['F.Cu'], ['vias'], True),
            ('enclosing', ['In1.Cu'], ['vias'], False),
            ('enclosing', ['F.Cu'], ['tracks'], False),
        ]:
            with self.subTest(shape=shape, layers=layers, deny=deny):
                floor = copy.deepcopy(self.floor)
                area = dict(name='REGULATOR_POLYGON_CONTROL', layers=layers,
                            deny=deny, points=[[x+dx, y+dy]
                                              for dx, dy in outlines[shape]])
                floor['keepouts'].append(area)
                report = inspect(floor, self.route, self.nets, self.geometry)
                finding = ('via/keepout', via['id'], area['name'])
                self.assertEqual(finding in report['failures'], expected)



class LayerContactTests(unittest.TestCase):
    def test_same_net_projection_requires_an_actual_layer_transfer(self):
        geometry={'pads':[{'id':'R.1','net':'P','shape':primitive([0,0],[0,0],.5)},
                           {'id':'R.2','net':'P','shape':primitive([2,0],[2,0],.5)}]}
        route={'prep':{'seed_stubs':{'via':{'size':.5,'drill':.2},'stubs':[
            {'pin':'R.1','net':'P','segments':[{'layer':'F.Cu','width':.2,'pts':[[0,0],[1,0]]}]},
            {'pin':'R.2','net':'P','segments':[{'layer':'B.Cu','width':.2,'pts':[[1,0],[2,0]]}],
             'vias':[[2,0]]}]}}}
        self.assertNotIn('R.2',connected_reach(route,geometry,'R.1'))
        route['prep']['seed_stubs']['stubs'][0]['vias']=[[1,0]]
        self.assertIn('R.2',connected_reach(route,geometry,'R.1'))
        route['prep']['seed_stubs']['stubs'][0]['vias']=[[1,1]]
        self.assertNotIn('R.2',connected_reach(route,geometry,'R.1'))

if __name__ == '__main__':
    unittest.main()
