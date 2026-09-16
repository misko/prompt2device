"""ADC/LT3041 thermal intent, independently screened with native footprints.

Never construct/load a BOARD. This source screen is not V-PROCESS, filled
connectivity, thermal resistance, stencil approval, DRC or release acceptance.
Known-bad fixtures exercise missing drops, foreign copper, drill spacing,
unprotected in-pad holes and ambiguous fabrication selectors.
"""
import copy
import math
import subprocess
import unittest
from collections import Counter
from pathlib import Path

import pcbnew
import yaml
from test_adc_source import load_source, native_geometry
from test_digital_launch_source import primitive, rect_shape, segment_rows, vec
from test_adc_source import area_shape
from test_regulator_source import via_rows

PROJECT=Path(__file__).resolve().parents[2]
REPO=PROJECT.parents[1]
BASE='1b725986'
LAYERS={'F.Cu':pcbnew.F_Cu,'In1.Cu':pcbnew.In1_Cu,
        'In2.Cu':pcbnew.In2_Cu,'B.Cu':pcbnew.B_Cu}


def assembly_source():
    return yaml.safe_load((PROJECT/'03_src/rules/assembly.yaml').read_text())


def thermal_rows(floor,geometry):
    """Decode authored fields independently, without calling the producer."""
    fps=dict(zip(sorted({p['id'].split('.')[0] for p in geometry['pads']}),geometry['footprints']))
    rows=[]
    for field in floor.get('thermal_vias',{}).get('fields',[]):
        for ref in field.get('refs',[field.get('ref')]):
            fp=fps[ref];angle=math.radians(fp.GetOrientationDegrees())
            x,y=fp.GetPosition().x/1e6,fp.GetPosition().y/1e6
            pin=ref+'.'+str(field['pad'])
            for i,(dx,dy) in enumerate(field['at']):
                at=[x+dx*math.cos(angle)+dy*math.sin(angle),
                    y-dx*math.sin(angle)+dy*math.cos(angle)]
                rows.append(dict(id=pin+f':thermal{i}',pin=pin,
                    net=geometry['pins'][(ref,str(field['pad']))],at=at,
                    size=field['size'],drill=field['drill'],
                    protection=field.get('protection',floor['thermal_vias'].get('protection',{})),
                    shape=primitive(at,at,field['size']),hole=primitive(at,at,field['drill'])))
    return rows


def inspect_thermal(floor,route,assembly,geometry):
    """Full-shape, all physical copper layers; exactly one intentional host."""
    rows=thermal_rows(floor,geometry);ordinary=via_rows(route)
    counts=Counter();failures=[];hits=[]
    def fail(kind,item,other=''):failures.append(dict(kind=kind,item=item,other=other))
    def clear(a,b,kind,gap):
        counts[kind]+=1
        if pcbnew.SHAPE.Collide(a['shape'],b['shape'],max(0,round(gap*1e6)-2)):
            fail(kind,a['id'],b['id'])
    expected_hosts = {'U_ADC.49': 9, 'U_LDO.15': 2}
    if Counter(row['pin'] for row in rows)!=Counter(expected_hosts):
        fail('coverage','ADC49/LT15',str(Counter(row['pin'] for row in rows)))
    pads=[]
    refs=sorted({p['id'].split('.')[0] for p in geometry['pads']})
    for ref,fp in zip(refs,geometry['footprints']):
        for pad in fp.Pads():
            if pad.IsOnCopperLayer():pads.append((ref+'.'+pad.GetNumber(),ref,pad))
            if pad.GetDrillSizeX()>0:
                counts['component-drill-selector']+=1
                if abs(pad.GetDrillSizeX()/1e6-.3)<.0015:
                    fail('component-drill-selector',ref+'.'+pad.GetNumber())
    for row in rows:
        if row['pin'] not in expected_hosts or row['net']!='GND':fail('host-identity',row['id'])
        if row['protection']!={'capping':True,'filling':True}:fail('protection',row['id'])
        if (row['size'],row['drill'])!=(.6,.3):fail('geometry',row['id'])
        x,y=row['at'];radius=row['size']/2
        outline=floor['board']['outline']
        if not (outline['x0']+.8+radius<=x<=outline['x1']-.8-radius and
                outline['y0']+.8+radius<=y<=outline['y1']-.8-radius):fail('edge',row['id'])
        own=[]
        for pin,ref,pad in pads:
            for name,layer in LAYERS.items():
                if not pad.IsOnLayer(layer):continue
                shape=pad.GetEffectiveShape(layer)
                if pin==row['pin']:
                    # Exact host is an unrotated native rectangle, not a bbox
                    # approximation of arbitrary pads or a blanket GND waiver.
                    if (pad.GetShape()!=pcbnew.PAD_SHAPE_RECT or
                        pad.GetOrientationDegrees()%180!=0):fail('host-shape',row['id'])
                    px,py=pad.GetPosition().x/1e6,pad.GetPosition().y/1e6
                    sx,sy=pad.GetSize().x/1e6,pad.GetSize().y/1e6
                    if abs(x-px)+radius>sx/2+1e-9 or abs(y-py)+radius>sy/2+1e-9:
                        fail('host-containment',row['id'])
                    counts['intentional-host']+=1
                else:
                    other=dict(id=pin+':'+name,shape=shape)
                    net=geometry['pins'][(ref,pad.GetNumber())]
                    if net!=row['net']:clear(row,other,'via/foreign-pad',.25)
                    clear(dict(id=row['id'],shape=row['hole']),other,'drill/physical-pad',.255)
                if name=='F.Cu' and not pad.GetDrillSizeX() and pad.HitTest(vec(row['at']),0,layer):own.append(pin)
        hits.append(dict(id=row['id'],pads=own))
        if own!=[row['pin']]:fail('in-pad-host',row['id'],str(own))
        for seed in segment_rows(route):
            if seed['net']!=row['net']:clear(row,seed,'via/foreign-seed',.25)
            clear(dict(id=row['id'],shape=row['hole']),seed,'drill/seed',.255)
        for other in ordinary:
            if other['net']!=row['net']:clear(row,other,'via/foreign-via',.25)
            clear(row,dict(id=other['id'],shape=other['hole']),'via/old-drill',.255)
            clear(dict(id=row['id'],shape=row['hole']),other,'drill/old-via',.255)
            clear(dict(id=row['id'],shape=row['hole']),dict(id=other['id'],shape=other['hole']),'drill/old-drill',.5)
        for hole in geometry['holes']:
            clear(row,hole,'via/physical-hole',.255)
            clear(dict(id=row['id'],shape=row['hole']),hole,'drill/physical-hole',.5)
        for area in floor['keepouts']:
            if set(area['layers'])&set(LAYERS) and 'vias' in area['deny']:
                clear(row,dict(id=area['name'],shape=area_shape(area)),'via/keepout',0)
    for i,row in enumerate(rows):
        for other in rows[i+1:]:
            clear(dict(id=row['id'],shape=row['hole']),dict(id=other['id'],shape=other['hole']),'thermal-hole-pair',.5)
    process=assembly.get('via_process',{})
    if process.get('protected_geometry')!={'via_diameter_mm':.6,'drill_mm':.3}:fail('process-geometry','assembly')
    selector=process.get('fabricator_selector',{})
    if selector!={'kind':'drill_family','protected_drill_mm':.3,'ordinary_drill_mm':[.2]}:fail('process-selector','assembly')
    if process.get('uploader_confirmation_required') is not True:fail('process-confirmation','assembly')
    remark=process.get('order_remark','').lower()
    if not all(s in remark for s in ['fill','cap','0.30','0.20']):fail('process-remark','assembly')
    if not all(s in remark for s in [
        'u_adc exposed pad 49', 'u_ldo exposed pad 15',
        'c_adc_cm6p pad 2',
    ]):
        fail('process-hosts','assembly')
    if not route['route'].get('forbid_new_via_in_pad'):fail('router-vip-guard','route')
    for row in ordinary:
        if row['drill']!=.2:fail('ordinary-drill-family',row['id'])
        for pin,ref,pad in pads:
            if pad.IsOnLayer(pcbnew.F_Cu) and not pad.GetDrillSizeX():
                counts['ordinary-vip-census']+=1
                if pad.HitTest(vec(row['at']),0,pcbnew.F_Cu):fail('ordinary-vip',row['id'],pin)
    return dict(checks=dict(counts),failures=failures,thermal_vias=len(rows),ordinary_vias=len(ordinary),in_pad_hits=hits)


class ThermalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor,cls.route,*_=load_source();cls.assembly=assembly_source()
        cls.geometry=native_geometry(cls.floor)

    def check(self,floor=None,route=None,assembly=None):
        return inspect_thermal(floor or self.floor,route or self.route,assembly or self.assembly,self.geometry)

    def test_full_native_geometry_and_exact_denominators(self):
        result=self.check();self.assertEqual(result['failures'],[])
        self.assertEqual((result['thermal_vias'],result['ordinary_vias']),(11,121))
        self.assertEqual(result['checks']['intentional-host'],11)
        self.assertEqual(result['checks']['thermal-hole-pair'],55)

    def test_new_regulator_thermal_host_and_process_cannot_be_omitted(self):
        bad=copy.deepcopy(self.floor)
        bad['thermal_vias']['fields']=[f for f in bad['thermal_vias']['fields'] if f['ref']!='U_LDO']
        self.assertIn('coverage',{f['kind'] for f in self.check(floor=bad)['failures']})
        assembly=copy.deepcopy(self.assembly)
        assembly['via_process']['order_remark']=assembly['via_process']['order_remark'].replace('C_ADC_CM6P pad 2','C_ADC_CM6P pad X')
        self.assertIn('process-hosts',{f['kind'] for f in self.check(assembly=assembly)['failures']})

    def test_regulator_via_on_input_land_is_rejected(self):
        bad=copy.deepcopy(self.floor)
        next(f for f in bad['thermal_vias']['fields'] if f['ref']=='U_LDO')['at'][0]=[-1.45,-1.5]
        kinds={f['kind'] for f in self.check(floor=bad)['failures']}
        self.assertTrue({'host-containment','via/foreign-pad','in-pad-host'}<=kinds)

    def test_absent_field_fails_actual_coverage(self):
        bad=copy.deepcopy(self.floor);bad.pop('thermal_vias',None)
        self.assertIn('coverage',{f['kind'] for f in self.check(floor=bad)['failures']})

    def test_foreign_pad_site_fails_native_clearance_and_host(self):
        bad=copy.deepcopy(self.floor);bad['thermal_vias']['fields'][0]['at'][0]=[-2.95,-.6]
        kinds={f['kind'] for f in self.check(floor=bad)['failures']}
        self.assertTrue({'host-containment','via/foreign-pad','drill/physical-pad'}<=kinds)

    def test_close_holes_fail_without_foreign_net(self):
        bad=copy.deepcopy(self.floor);field=bad['thermal_vias']['fields'][0]
        field['at'][1]=[-1,-.5]
        self.assertIn('thermal-hole-pair',{f['kind'] for f in self.check(floor=bad)['failures']})

    def test_unfilled_and_overlapping_processes_fail(self):
        bad=copy.deepcopy(self.floor);bad['thermal_vias']['fields'][0]['protection']['filling']=False
        self.assertEqual(sum(f['kind']=='protection' for f in self.check(floor=bad)['failures']),9)
        assembly=copy.deepcopy(self.assembly)
        assembly['via_process']['fabricator_selector']['ordinary_drill_mm']=[.2,.3]
        self.assertIn('process-selector',{f['kind'] for f in self.check(assembly=assembly)['failures']})

    def test_existing_thermal_stack_and_process_authority_is_preserved(self):
        # This suite owns thermal/process invariants, not a reverse migration
        # through deleted TPS and VMID-buffer circuits. Their replacements are
        # covered by current topology, placement and local-copper suites.
        def frozen(name):
            return yaml.safe_load(subprocess.check_output(
                ['git', 'show', BASE+':projects/crow-audio-carrier-v1/03_src/'+name],
                cwd=REPO, timeout=15))
        old = frozen('floorplan.yaml')
        # Exact ADR0030 mechanical changes; thermal/stack authority is unchanged.
        old['board']['outline']['x0']=16.0
        old['board']['outline']['x1']=172.0  # authorized2mm east-side growth
        old['board']['mounting_holes']['at']=[[21.,25.],[165.,25.],[21.,115.],[165.,115.]]
        old['board']['fiducials']['at']=[[25.,33.],[161.,29.],[29.,111.]]
        for key in ('board', 'design_rules', 'zones'):
            self.assertEqual(self.floor[key], old[key], key)
        adc = lambda floor: [r for r in floor['thermal_vias']['fields'] if r['ref']=='U_ADC']
        self.assertEqual(adc(self.floor), adc(old))
        self.assertEqual(len(adc(self.floor)), 1)
        before = frozen('rules/assembly.yaml')['via_process']
        after = self.assembly['via_process']
        self.assertEqual(set(before), set(after))
        for key in before:
            if key != 'order_remark':
                self.assertEqual(after[key], before[key], key)
        self.assertTrue(self.route['route']['forbid_new_via_in_pad'])

    def test_host_paste_and_nominal_geometry(self):
        refs=sorted({p['id'].split('.')[0] for p in self.geometry['pads']})
        fp=dict(zip(refs,self.geometry['footprints']))['U_ADC']
        host=next(p for p in fp.Pads() if p.GetNumber()=='49')
        self.assertEqual((host.GetSizeX()/1e6,host.GetSizeY()/1e6),(4.6,4.6))
        self.assertEqual(host.GetLocalZoneConnection(),pcbnew.ZONE_CONNECTION_FULL)
        paste=[p for p in fp.Pads() if not p.GetNumber() and p.IsOnLayer(pcbnew.F_Paste)]
        self.assertEqual(len(paste),9);self.assertFalse(host.IsOnLayer(pcbnew.F_Paste))
        self.assertAlmostEqual((.6-.3)/2,.15);self.assertAlmostEqual(1-.3,.7)
        self.assertAlmostEqual(self.floor['board']['stackup']['nominal_thickness_mm']/.3,16/3)


if __name__=='__main__':unittest.main()
