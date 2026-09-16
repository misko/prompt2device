"""Current shared-rail input/protection placement oracle, not PCB acceptance.

Exact native isolated footprints grade all35 retained input/bleed instances
against333 fitted instances. No generated BOARD, routed inductance or
arbitrary-waveform startup guarantee is inferred.
"""
import copy
import unittest
from collections import Counter
import pcbnew
from source_inventory import inventory
from placement_gates import _poly_gap_mm
from test_power_landing_source import load_source, native_geometry
from test_analog_keepout_source import inspect_mask

TARGETS={f'R_{tag}{n}{leg}' for tag in ('IN','B') for n in range(1,9) for leg in 'PN'} | {
    'C_OPA_BULK','R_OPA_BLEED1','R_OPA_BLEED2'}

def topology(comps,pins):
    failures=[]
    if len(comps)!=333 or len(pins)!=985 or len(set(pins.values()))!=221:failures.append('census')
    if {'FB_OPA','R_OPA_FEED','C_RAW_HOLD','C_OPA_BULK2','R_OPA_BLEED3'}&set(comps):failures.append('retired-feed')
    expected={'R_OPA_BLEED1':{'1':'3V3_ADC','2':'OPA_BLEED_A'},
      'R_OPA_BLEED2':{'1':'OPA_BLEED_A','2':'GND'},
      'C_OPA_BULK':{'1':'3V3_ADC','2':'GND'}}
    values={'R_OPA_BLEED1':'100','R_OPA_BLEED2':'100','C_OPA_BULK':'47uF'}
    for n in range(1,9):
        for leg,p in [('P','3'),('N','5')]:
            ref=f'R_IN{n}{leg}';net=f'AIN_{leg}{n}'
            expected[ref]={'1':f'BIAS_{leg}{n}','2':net};values[ref]='10k'
            wanted={(ref,'2'),(f'U_AFE{n}',p)}
            if {k for k,v in pins.items() if v==net}!=wanted:failures.append('isolated:'+net)
    for ref,row in expected.items():
        if {p:v for (r,p),v in pins.items() if r==ref}!=row:failures.append('pins:'+ref)
        if ref not in comps or comps[ref][1]!=values[ref]:failures.append('value:'+ref)
    return failures

def clearances(geometry,targets=TARGETS):
    refs=sorted({p['id'].split('.')[0] for p in geometry['pads']})
    fps=dict(zip(refs,geometry['footprints']))
    assert len(refs)==333 and len(targets)>0 and targets<=fps.keys()
    for fp in fps.values():fp.BuildCourtyardCaches()
    failures=[];checks=Counter()
    for ref in sorted(targets):
        fp=fps[ref];env=fp.GetCourtyard(pcbnew.F_CrtYd)
        assert env.OutlineCount()>0
        for other,foreign in fps.items():
            if other==ref:continue
            body=foreign.GetCourtyard(pcbnew.F_CrtYd);checks['courtyard']+=1
            if _poly_gap_mm(env,body,.1)<.1-1e-6:failures.append((ref,'courtyard',other))
            for p in foreign.Pads():
                checks['body-pad']+=1
                if env.Collide(p.GetEffectiveShape(pcbnew.F_Cu),99998):failures.append((ref,'body-pad',other))
            for p in fp.Pads():
                checks['pad-body']+=1
                if body.Collide(p.GetEffectiveShape(pcbnew.F_Cu),99998):failures.append((ref,'pad-body',other))
                for q in foreign.Pads():
                    checks['pad-pad']+=1
                    if p.GetEffectiveShape(pcbnew.F_Cu).Collide(q.GetEffectiveShape(pcbnew.F_Cu),126998):failures.append((ref,'pad-pad',other))
    return failures,dict(checks)

def copper_gap(a,b):
    lo,hi=0,20000000
    while hi-lo>1:
        mid=(lo+hi)//2
        if a.Collide(b,mid):hi=mid
        else:lo=mid
    return lo/1e6

class StartupSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor,cls.route,cls.nets,*_=load_source()
        cls.geometry=native_geometry(cls.floor)
        cls.comps,cls.pins,_=inventory()

    def test_exact_live_topology_and_hostile_each_new_connection(self):
        self.assertEqual(topology(self.comps,self.pins),[])
        refs=TARGETS-{r for r in TARGETS if r.startswith('R_B') and not r.startswith('R_OPA')}
        affected=[k for k in self.pins if k[0] in refs]
        self.assertEqual(len(affected),38)
        for key in affected:
            bad=dict(self.pins);bad[key]='GND' if bad[key]!='GND' else '5V_OPA'
            self.assertTrue(topology(self.comps,bad),key)

    def test_all_35_input_and_bleed_instances_clear_full_foreign_native_geometry(self):
        failures,checks=clearances(self.geometry)
        self.assertEqual(len(TARGETS),35)
        self.assertEqual(checks['courtyard'],35*332)
        self.assertGreater(checks['pad-pad'],60000)
        self.assertEqual(failures,[])

    def test_shared_output_and_bleed_gap_budgets_reject_distant_cap(self):
        pads={p['id']:p['shape'] for p in self.geometry['pads']}
        pairs=[('U_LDO.13','C_LDO_OUT.1',3.5),('U_LDO.14','C_OPA_BULK.1',3.5),
               ('R_OPA_BLEED1.1','C_OPA_BULK.1',10),('R_OPA_BLEED1.2','R_OPA_BLEED2.1',3)]
        for a,b,limit in pairs:self.assertLess(copper_gap(pads[a],pads[b]),limit)
        bad=copy.deepcopy(self.floor);bad['placement']['anchors']['C_OPA_BULK']=[96,70,0]
        geometry=native_geometry(bad);badpads={p['id']:p['shape'] for p in geometry['pads']}
        self.assertGreater(copper_gap(badpads['U_LDO.14'],badpads['C_OPA_BULK.1']),3.5)
        self.assertTrue(clearances(geometry,{'C_OPA_BULK'})[0])

    def test_active_signal_and_reference_masks_cannot_be_dropped(self):
        for net,group in [('AIN_P1','analog_nonadc'),('VMID1_EXT','references')]:
            bad=copy.deepcopy(self.route);bad['prep']['waves']['groups'][group].remove(net)
            self.assertIn('coverage',inspect_mask(bad,self.geometry)['failures'])
        bad=copy.deepcopy(self.route)
        next(w for w in bad['route']['waves'] if w['name']=='analog_nonadc').pop('keepout_layer')
        self.assertIn('wave-mask:analog_nonadc',inspect_mask(bad,self.geometry)['failures'])

    def test_retired_rail_and_bleed_values_are_rejected_without_census_change(self):
        bad=dict(self.pins);bad[('C_OPA_BULK','1')]='5V_OPA'
        self.assertIn('pins:C_OPA_BULK',topology(self.comps,bad))
        comps=dict(self.comps)
        comps['R_OPA_BLEED1']=(comps['R_OPA_BLEED1'][0],'300')
        self.assertIn('value:R_OPA_BLEED1',topology(comps,self.pins))

if __name__=='__main__':unittest.main()
