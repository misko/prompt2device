"""Source-native peripheral power branches, never a BOARD or route admission.

Finite full-width entry witnesses grade local connected copper groups, not
global routing, ground return, safe ampacity, fault duration or thermal rise.
ADC-feed regressions require actual entries for the formerly unresolved groups.
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
from test_digital_launch_source import native_geometry, segment_rows, primitive, rect_shape, vec
from test_regulator_source import via_rows, contained, connected_reach
from source_geometry import sample_polygon_starts
from rules_audit import parse_mm

PINS = {f'U_ISO{n}.8' for n in range(1,9)} | {f'U_AFE{n}.8' for n in range(1,9)} | {
    'U_PWR.3','U_PWR.4','U_AUDIO.4','R_PWR_PU.1','Q_PRE.3','R_PWR_TOP.1',
    'C_DUMP_LOGIC.1','U_CLK.8','U_RST2.2','U_RST2.8',
    'C_FILT1_10U.1','C_FILT2_10U.1'}
LANDING_PINS = {'U_PWR.4','U_AUDIO.4','R_PWR_PU.1','Q_PRE.3','R_PWR_TOP.1',
                'C_FILT1_10U.1','C_FILT2_10U.1'}
ADDED_BUDGETS = {'5V_LDO_HOLD': (28.36947434857499,28), '3V3_ADC': (20.27658426095509,13),
                 '5V_BUCK': (.8,1), 'FILT1P': (1.55,1), 'FILT2P': (1.55,1)}
WHOLE_BUDGETS = {'5V_LDO_HOLD': (41.81191723866479,36), '3V3_ADC': (78.0819281355697,63),
                 'BUCK_SW': (3.4000799987200394,2), '5V_BUCK': (.8,1),
                 'FILT1P': (6.050464884544218,4), 'FILT2P': (6.050464884544218,4)}


def copper_groups(net, geometry, route):
    nodes=[dict(p,kind='pad') for p in geometry['pads'] if p['net']==net]
    nodes += [dict(r,id='seed-'+str(i),pin=r['id'],kind='seed') for i,r in enumerate(segment_rows(route)) if r['net']==net and r['layer']=='F.Cu']
    nodes += [dict(v,kind='via') for v in via_rows(route) if v['net']==net]
    remaining=set(range(len(nodes)));groups=[]
    while remaining:
        first=min(remaining);remaining.remove(first);group={first};todo=[first]
        while todo:
            i=todo.pop()
            for j in sorted(remaining):
                if pcbnew.SHAPE.Collide(nodes[i]['shape'],nodes[j]['shape'],0):
                    remaining.remove(j);group.add(j);todo.append(j)
        groups.append([nodes[i] for i in sorted(group)])
    return groups


def obstacles(net, geometry, route, floor):
    result=[dict(id=p['id'],kind='pad',shape=p['shape'],gap=.25) for p in geometry['pads'] if p['net']!=net]
    result += [dict(id=r['id'],kind='seed',shape=r['shape'],gap=.25) for r in segment_rows(route) if r['net']!=net and r['layer']=='F.Cu']
    result += [dict(id=h['id'],kind='hole',shape=h['shape'],gap=.255) for h in geometry['holes']]
    for via in via_rows(route):
        if via['net']!=net:
            result.append(dict(id=via['id'],kind='via',shape=via['shape'],gap=.25))
            result.append(dict(id=via['id'],kind='via-hole',shape=via['hole'],gap=.255))
    result += [dict(id=a['name'],kind='keepout',shape=rect_shape(a['rect']),gap=0.) for a in floor['keepouts'] if 'F.Cu' in a['layers'] and 'tracks' in a['deny']]
    return result


def group_starts(group):
    result=[]
    for item in group:
        if item['kind']=='pad':
            result += [(list(item['at']),item['id'])] + [(list(p),item['id']) for p in sample_polygon_starts(item['poly'])]
        elif item['kind']=='seed':
            steps=max(1,math.ceil(math.dist(item['a'],item['b'])/.2))
            result += [([item['a'][j]+(item['b'][j]-item['a'][j])*i/steps for j in range(2)],item['id']) for i in range(steps+1)]
        else:result.append((item['at'],item['id']))
    unique={}
    for point,owner in result:unique.setdefault(tuple(round(x,6) for x in point),owner)
    return [(list(point),owner) for point,owner in unique.items()]


def _entry_screen(net, group, geometry, route, floor, width=1.2, *, layer="F.Cu", obs=None, points=None):
    if obs is None:obs=obstacles(net,geometry,route,floor)
    if points is None:points=group_starts(group)
    checks=0;attempts=0;rejections=Counter();outline=floor['board']['outline'];radius=width/2+.8
    # Only a contacted PTH component's own plated barrel is not a foreign hole.
    own_holes={p['id'] for p in group if p['kind']=='pad'}
    obs=[item for item in obs if not (item['kind']=='hole' and item['id'] in own_holes)]
    for start,owner in points:
        # Sorting accelerates rejection without dropping any obstacle.
        obs.sort(key=lambda item:item['shape'].BBox().SquaredDistance(vec(start)))
        for i in range(48):
            angle=i*math.tau/48;end=[start[0]+math.cos(angle),start[1]+math.sin(angle)]
            shape=primitive(start,end,width);attempts+=1
            if not all(outline['x0']+radius<=x<=outline['x1']-radius and outline['y0']+radius<=y<=outline['y1']-radius for x,y in [start,end]):
                rejections['edge']+=1;continue
            for item in obs:
                checks+=1
                if pcbnew.SHAPE.Collide(shape,item['shape'],round(item['gap']*1e6)-2):
                    rejections[item['kind']+':'+item['id']]+=1;break
            else:
                return dict(witness=dict(start=start,end=end,owner=owner,layer=layer,width_mm=width,clearance_mm=.25,reach_mm=1.,foreign_obstacles=len(obs)),attempts=attempts,checks=checks)
    return dict(witness=None,attempts=attempts,checks=checks,rejections=dict(rejections))


def entry_screen(net, group, geometry, route, floor, width=1.2):
    front=_entry_screen(net,group,geometry,route,floor,width)
    if front['witness'] is not None:return front
    wave=next((w for w in route['route']['waves'] if net in w.get('nets',[])),{})
    layers=wave.get('layers',route['route'].get('common',{}).get('layers',[]))
    if 'B.Cu' not in layers:return front
    live={v['id']:v for v in via_rows(route) if v['net']==net}
    transfers=[v for v in group if v['kind']=='via' and v['id'] in live and v['at']==live[v['id']]['at']]
    if not transfers:return front
    obs=[]
    refs=sorted({ref for ref,pin in geometry['pins']})
    for ref,fp in zip(refs,geometry['footprints']):
        for pad in fp.Pads():
            if pad.IsOnCopperLayer() and pad.IsOnLayer(pcbnew.B_Cu) and geometry['pins'].get((ref,pad.GetNumber()))!=net:
                obs.append(dict(id=ref+'.'+pad.GetNumber(),kind='back-pad',shape=pad.GetEffectiveShape(pcbnew.B_Cu),gap=.25))
    obs += [dict(id=r['id'],kind='back-seed',shape=r['shape'],gap=.25) for r in segment_rows(route) if r['net']!=net and r['layer']=='B.Cu']
    obs += [dict(id=h['id'],kind='hole',shape=h['shape'],gap=.255) for h in geometry['holes']]
    for v in via_rows(route):
        if v['net']!=net:
            obs += [dict(id=v['id'],kind='via',shape=v['shape'],gap=.25),dict(id=v['id'],kind='via-hole',shape=v['hole'],gap=.255)]
    obs += [dict(id=a['name'],kind='keepout',shape=rect_shape(a['rect']),gap=0.) for a in floor['keepouts'] if 'B.Cu' in a['layers'] and 'tracks' in a['deny']]
    back=_entry_screen(net,group,geometry,route,floor,width,layer='B.Cu',obs=obs,points=[(v['at'],v['id']) for v in transfers])
    back['checks']+=front['checks'];back['attempts']+=front['attempts']
    return back


def inspect(floor, route, nets, geometry):
    rows=segment_rows(route);new=[r for r in rows if r['id'] in LANDING_PINS]
    failures=[];checks=Counter();extent_errors=[];areas={a['name']:a for a in floor['keepouts']}
    for row in new:
        for item in (obstacles(row['net'],geometry,route,floor)
                     if row['layer']=='F.Cu' else []):
            checks[item['kind']]+=1
            if pcbnew.SHAPE.Collide(row['shape'],item['shape'],round(item['gap']*1e6)-2):
                failures.append(dict(pin=row['id'],a=row['a'],b=row['b'],width=row['width'],kind=item['kind'],other=item['id'],required_mm=item['gap']))
        outline=floor['board']['outline'];radius=row['width']/2+.8;checks['edge']+=1
        if not all(outline['x0']+radius<=x<=outline['x1']-radius and outline['y0']+radius<=y<=outline['y1']-radius for x,y in [row['a'],row['b']]):failures.append(dict(pin=row['id'],kind='edge'))
        if row['layer'] not in {'F.Cu','B.Cu'}:extent_errors.append('layer:'+row['id'])
        if row['layer']=='F.Cu' and row['width']<1.2:
            eligible=[areas[r['zone']] for r in nets['scoped_floors'] if row['net'] in r.get('nets',[]) and parse_mm(r['min_width'])<=row['width']]
            if not any(a['deny']==[] and contained(row,a) for a in eligible):extent_errors.append(row['id'])
    contacts={pin:any(r['id']==pin and r['shape'].Collide(next(p['shape'] for p in geometry['pads'] if p['id']==pin),0) for r in new) for pin in LANDING_PINS}
    budgets={};added={}
    for row in rows:
        if row['width']>=1.2 or row['net'] not in WHOLE_BUDGETS:continue
        length=math.dist(row['a'],row['b']);total=budgets.setdefault(row['net'],[0.,0]);total[0]+=length;total[1]+=1
        if row['id'] in PINS:
            total=added.setdefault(row['net'],[0.,0]);total[0]+=length;total[1]+=1
    return dict(utc=datetime.now(timezone.utc).isoformat(),kind='Native source peripheral branches; NOT PCB DRC/current/return/thermal acceptance',primitives=len(new),checks=dict(checks),check_count=sum(checks.values()),failures=failures,contacts=contacts,extent_errors=extent_errors,whole_budgets=budgets,added_budgets=added)


def landing_report(floor, route, geometry):
    rows=[]
    nets=[net for wave in route['route']['waves'] if wave['name'].startswith('power_')
          for net in wave.get('nets',[])]
    for net in nets:
        for group in copper_groups(net,geometry,route):
            rows.append(dict(net=net,pads=sorted(p['id'] for p in group if p['kind']=='pad'),**entry_screen(net,group,geometry,route,floor)))
    return dict(utc=datetime.now(timezone.utc).isoformat(),kind='Finite1.20/.25mm1mm source entry witnesses; not global routing or impossibility proof',components=len(rows),witnesses=sum(r['witness'] is not None for r in rows),rows=rows)


class PowerLandingSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor,cls.route,cls.nets,*_=load_source();cls.geometry=native_geometry(cls.floor)
        cls.report=inspect(cls.floor,cls.route,cls.nets,cls.geometry)
        cls.landings=landing_report(cls.floor,cls.route,cls.geometry)

    def test_all_new_native_copper_and_contacts(self):
        self.assertEqual(self.report['primitives'],21);self.assertGreater(self.report['check_count'],16000)
        self.assertEqual(self.report['failures'],[]);self.assertEqual(self.report['extent_errors'],[])
        self.assertEqual(len(self.report['contacts']),7);self.assertTrue(all(self.report['contacts'].values()))
        added=[b for b in self.route['prep']['seed_stubs']['stubs'] if b['pin'] in PINS]
        self.assertEqual(len(added),28)
        self.assertEqual({b['pin']:b['vias'] for b in added if b.get('vias')},
                         {'U_PWR.4':[[34.843223,57.626777]],
                          'U_AUDIO.4':[[35.403,60.524]],
                          'Q_PRE.3':[[44.0825,58.1]],
                          'R_PWR_TOP.1':[[30.825,55.7]],
                          'C_FILT1_10U.1':[[95.8,61.0]],
                          'C_FILT2_10U.1':[[95.8,79.0]]})

    def test_finite_entries_cover_every_power_group(self):
        self.assertGreater(self.landings['components'],0)
        self.assertEqual(self.landings['components'],self.landings['witnesses'])
        missing={(r['net'],tuple(r['pads'])) for r in self.landings['rows'] if r['witness'] is None}
        self.assertEqual(missing,set())
        observed=[pin for r in self.landings['rows'] for pin in r['pads']]
        selected=[net for wave in self.route['route']['waves'] if wave['name'].startswith('power_')
                  for net in wave.get('nets',[])]
        self.assertEqual(set(selected),{'5V_BUCK','5V_LDO_FEED','5V_LDO_HOLD','3V3_ADC','FILT1P','FILT2P','ADC_DUMP','BUCK_SW'})
        expected=[p['id'] for p in self.geometry['pads'] if p['net'] in selected]
        self.assertCountEqual(observed,expected);self.assertEqual(len(observed),116)
        self.assertTrue({'R_OPA_BLEED1.1','C_OPA_BULK.1','C_LDO_OUT.1'} <= set(observed))
        self.assertTrue({f'U_AFE{n}.8' for n in range(1,9)} <= set(observed))
        self.assertTrue({'U_TDM_SCH.5','C_TDM_SCH.1'} <= set(observed))

    def test_exact_new_and_whole_net_budgets(self):
        for key,expected in [('added_budgets',ADDED_BUDGETS),('whole_budgets',WHOLE_BUDGETS)]:
            self.assertEqual(set(self.report[key]),set(expected))
            for net,(length,count) in expected.items():
                self.assertAlmostEqual(self.report[key][net][0],length,places=8)
                self.assertEqual(self.report[key][net][1],count)
        banks=self.route['prep']['seed_stubs']['stubs']
        buck=next(b for b in banks if b['pin']=='R_PWR_TOP.1')
        self.assertEqual(buck, {'net':'5V_BUCK','pin':'R_PWR_TOP.1',
            'segments':[
                {'layer':'F.Cu','width':.3,'pts':[[30.825,54.9],[30.825,55.7]]},
                {'layer':'B.Cu','width':1.2,'pts':[[30.825,55.7],[30.71,55.815],[30.71,60.385],[30.825,60.5]]}],
            'via':{'size':.5,'drill':.2},'vias':[[30.825,55.7]]})
        for bank, y0, y1, y2 in [('C_FILT1_10U.1',62.55,61.0,59.0),
                                 ('C_FILT2_10U.1',77.45,79.0,81.0)]:
            row=next(b for b in banks if b['pin']==bank)
            self.assertEqual(row, {'net':'FILT1P' if '1_' in bank else 'FILT2P',
                'pin':bank,
                'segments':[{'layer':'F.Cu','width':.35,'pts':[[95.8,y0],[95.8,y1]]},
                            {'layer':'B.Cu','width':1.2,'pts':[[95.8,y1],[95.8,y2]]}],
                'via':{'size':.5,'drill':.2},'vias':[[95.8,y1]]})
        wave=next(w for w in self.route['route']['waves']
                  if w['name']=='power_5v_ldo_hold')
        self.assertEqual(wave['layers'],['F.Cu','B.Cu'])
        self.assertEqual(wave['power_nets'],['5V_LDO_HOLD'])
        self.assertEqual(wave['power_nets_widths'],[1.2])
        self.assertIs(wave['no_power_tap_neckdown'],True)

    def test_exact_supply_pins_reach_their_own_capacitors(self):
        pairs=[(f'U_ISO{n}.8',f'C_ISO{n}.1') for n in range(1,9)]
        pairs += [(f'U_AFE{n}.8',f'C_OPA{n}.1') for n in range(1,9)]
        pairs += [('U_PWR.4','C_PWR.1'),('U_AUDIO.4','C_AUDIO.1'),('U_CLK.8','C_CLK.1'),('U_RST2.8','C_RST2.1')]
        for pin,cap in pairs:self.assertIn(cap,connected_reach(self.route,self.geometry,pin))
        self.assertIn('U_PWR.4',connected_reach(self.route,self.geometry,'U_PWR.3'))
        self.assertNotIn('U_RST2.8',connected_reach(self.route,self.geometry,'U_RST2.2'))
        self.assertNotIn('U_DUMP.5',connected_reach(self.route,self.geometry,'C_DUMP_LOGIC.1'))

    def test_readmitted_and_unchanged_supply_branches_preserve_reviewed_source(self):
        project=Path(__file__).resolve().parents[2];root=project.parents[1]
        def frozen(name):
            return yaml.safe_load(subprocess.check_output(
                ['git','show','ccd83774:projects/crow-audio-carrier-v1/03_src/'+name],
                cwd=root,timeout=15))
        prior={s['pin']:s for s in frozen('route.yaml')['prep']['seed_stubs']['stubs']}
        current={s['pin']:s for s in self.route['prep']['seed_stubs']['stubs']}
        # U_ADC.5/.9 now use independently exact-screened exterior FILT branches.
        readmitted={'U_ADC.31','C_VDDIO.1','U_ADC.38',
                    'U_CLK.8','U_RST2.2','U_RST2.8'}
        retained=PINS-{f'U_AFE{n}.8' for n in range(1,9)}-LANDING_PINS
        self.assertEqual(len(readmitted|retained),16)
        # Three co-designed supply trees are graded by exact contact,
        # full native geometry and whole-capsule tests, not the old pose.
        for pin in (readmitted|retained)-{'U_ADC.31','C_VDDIO.1','U_CLK.8'}:
            self.assertEqual(current[pin],prior[pin],pin)
        # U_AUDIO moved0.30mm; preserve the rest of its original supply tree.
        prior['U_AUDIO.4']['segments'][0]['pts'][0]=[33.9,61.64]
        for pin in {'U_PWR.4','U_AUDIO.4'}:
            self.assertEqual(current[pin]['segments'][:-2],prior[pin]['segments'],pin)
        before=frozen('floorplan.yaml')
        before['board']['outline']['x1']=172.0  # authorized east-side growth; all other physical authority retained
        for key in ('board','design_rules','zones'):
            self.assertEqual(self.floor[key],before[key],key)
        # All new LT and amplifier geometry remains covered by independent
        # native screens; no projection reinstates a removed TPS/OPA rail.

    def test_hostile_extent_and_layer_are_rejected(self):
        bad=copy.deepcopy(self.route)
        bank=next(b for b in bad['prep']['seed_stubs']['stubs'] if b['pin']=='R_PWR_PU.1')
        bank['segments'][0]['pts'][-1]=[34.,55.316]
        bank['segments'][1]['layer']='In1.Cu'
        errors=inspect(self.floor,bad,self.nets,self.geometry)['extent_errors']
        self.assertIn('R_PWR_PU.1',errors);self.assertIn('layer:R_PWR_PU.1',errors)

    def test_hostile_full_width_at_small_pad_is_rejected(self):
        bad=copy.deepcopy(self.route)
        bank=next(b for b in bad['prep']['seed_stubs']['stubs'] if b['pin']=='R_PWR_PU.1')
        bank['segments'][0]['width']=1.2
        failures=inspect(self.floor,bad,self.nets,self.geometry)['failures']
        self.assertTrue(any(r['pin']=='R_PWR_PU.1' for r in failures))


class LayerEntryWitnessTests(unittest.TestCase):
    def test_back_entry_requires_real_transfer_and_rejects_back_wall(self):
        floor={'keepouts':[],'board':{'outline':{'x0':0,'y0':0,'x1':20,'y1':20}}}
        route={'prep':{'seed_stubs':{'via':{'size':.5,'drill':.2},'stubs':[
            {'pin':'R.1','net':'P','segments':[],'vias':[[10,10]]}]}},
            'route':{'waves':[{'name':'power_p','nets':['P'],'layers':['F.Cu','B.Cu']}]}}
        for i,pts in enumerate([[[9.2,9.2],[10.8,9.2]],[[10.8,9.2],[10.8,10.8]],
                                [[10.8,10.8],[9.2,10.8]],[[9.2,10.8],[9.2,9.2]]]):
            route['prep']['seed_stubs']['stubs'].append({'pin':f'W.{i}','net':'Q','segments':[{'layer':'F.Cu','width':.1,'pts':pts}]})
        geometry={'pads':[],'holes':[],'footprints':[],'pins':{}}
        group=[dict(via_rows(route)[0],kind='via')]
        result=entry_screen('P',group,geometry,route,floor)
        self.assertIsNotNone(result['witness'])
        self.assertEqual(result['witness']['layer'],'B.Cu')
        bad=copy.deepcopy(route);bad['route']['waves'][0]['layers']=['F.Cu']
        self.assertIsNone(entry_screen('P',group,geometry,bad,floor)['witness'])
        self.assertIsNone(entry_screen('P',[],geometry,route,floor)['witness'])
        bad=copy.deepcopy(route);bad['prep']['seed_stubs']['stubs'][0]['vias']=[]
        self.assertIsNone(entry_screen('P',group,geometry,bad,floor)['witness'])
        bad=copy.deepcopy(route)
        for bank in bad['prep']['seed_stubs']['stubs'][1:]:bank['segments'][0]['layer']='B.Cu'
        # Retain the front wall while adding the hostile back wall.
        bad['prep']['seed_stubs']['stubs']+=copy.deepcopy(route['prep']['seed_stubs']['stubs'][1:])
        self.assertIsNone(entry_screen('P',group,geometry,bad,floor)['witness'])

if __name__=='__main__':unittest.main()
