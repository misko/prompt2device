"""User.3 source-mask regression, not routing/EMI/placement acceptance.

Reopen isolated native copper shapes, not a BOARD or the keepout producer.
Known-bad controls use the actual pre-fix mask and a blanket-delete repair.
Neither requires changing live source. The tests grade endpoint accessibility
and the chosen switching-copper halo, not coexistence of completed routes.
"""
import copy
import subprocess
import unittest
from pathlib import Path

import pcbnew
import yaml
import re
from test_adc_source import load_source, native_geometry
from test_digital_launch_source import rect_shape, segment_rows

PROJECT=Path(__file__).resolve().parents[2]
REPO=PROJECT.parents[1]
BASE='7415aed46374628a5866acaf0bf94ea8f03bd380'


def baseline_route():
    return yaml.safe_load(subprocess.check_output(
        ['git','show',BASE+':projects/crow-audio-carrier-v1/03_src/route.yaml'],
        cwd=REPO,timeout=15))


def inspect_mask(route,geometry):
    """Full copper/mask intersections and bounding-box containment margins."""
    groups=route['prep']['waves']['groups']
    waves=[w for w in route['route']['waves']
           if w['name'] in {'bias_p1','analog_outputs','analog_nonadc','references'}]
    selected=set();failures=[]
    for wave in waves:
        if wave.get('keepout_layer')!='User.3':failures.append('wave-mask:'+wave['name'])
        selected.update(groups[wave['group']])
    masks=[r for r in route['prep']['keepouts']['rects'] if r['layer']=='User.3']
    pads=[p for p in geometry['pads'] if p['net'] in selected]
    expected={p['net'] for p in geometry['pads'] if re.fullmatch(r'(?:AUDIO|BIAS|AIN|OPA|FB)_[PN][1-8]|(?:FILTER|ADC)[1-8][PN]|VMID[12]_EXT',p['net'])}
    expected-=set(groups['adc'])
    if len(waves)!=4 or selected!=expected or len(expected)!=98 or not pads:failures.append('coverage')
    if not masks:failures.append('missing-mask')
    hits=[]
    for pad in pads:
        if any(pcbnew.SHAPE.Collide(pad['shape'],rect_shape(
            [r[k] for k in ('x0','y0','x1','y1')]),0) for r in masks):
            hits.append(pad['id'])
    hot=[p for p in geometry['pads'] if p['net'] in {'BUCK_SW','BUCK_BST'}]
    hot += [s for s in segment_rows(route) if s['net'] in {'BUCK_SW','BUCK_BST'}]
    if len(hot)!=8:failures.append('hot-coverage')
    margins=[]
    for item in hot:
        box=item['shape'].BBox()
        # Each complete hot primitive must fit in one mask, with the explicit
        # 3 mm engineering halo; this does not estimate emitted noise.
        best=max((min(box.GetLeft()/1e6-r['x0'],box.GetTop()/1e6-r['y0'],
                      r['x1']-box.GetRight()/1e6,r['y1']-box.GetBottom()/1e6)
                  for r in masks),default=float('-inf'))
        margins.append(best)
        if best<3.-1e-6:failures.append('hot-halo:'+item['id'])
    return dict(failures=failures,hits=sorted(hits),nets=len(selected),
                pads=len(pads),hot_items=len(hot),margins_mm=margins)


class AnalogKeepoutSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor,cls.route,*_=load_source()
        cls.geometry=native_geometry(cls.floor)

    def test_live_mask_frees_endpoints_and_retains_switching_exclusion(self):
        result=inspect_mask(self.route,self.geometry)
        self.assertEqual(result['failures'],[])
        self.assertEqual(result['hits'],[])
        self.assertEqual(result['nets'],98)
        self.assertGreater(result['pads'],320)
        self.assertEqual(result['hot_items'],8)
        self.assertGreaterEqual(min(result['margins_mm']),3.)

    def test_actual_pre_fix_rect_blocks_exact_eight_endpoints(self):
        bad=copy.deepcopy(self.route)
        bad['prep']['keepouts']['rects']=baseline_route()['prep']['keepouts']['rects']
        result=inspect_mask(bad,self.geometry)
        self.assertEqual(result['hits'],sorted([
            'U_ISO1.1','U_ISO1.5','C_FILTER1P2.1','C_FILTER1N2.1']))
        self.assertEqual(result['failures'],[])

    def test_blanket_delete_cannot_pass_on_empty_endpoint_hits(self):
        bad=copy.deepcopy(self.route);bad['prep']['keepouts']['rects']=[]
        result=inspect_mask(bad,self.geometry)
        self.assertEqual(result['hits'],[])
        self.assertIn('missing-mask',result['failures'])
        self.assertEqual(sum(f.startswith('hot-halo:') for f in result['failures']),8)

    def test_each_active_wave_must_apply_the_switching_mask(self):
        for name in ('bias_p1','analog_outputs','analog_nonadc','references'):
            bad=copy.deepcopy(self.route)
            next(w for w in bad['route']['waves'] if w['name']==name).pop('keepout_layer')
            self.assertIn('wave-mask:'+name,inspect_mask(bad,self.geometry)['failures'])

    def test_too_small_switching_halo_fails(self):
        bad=copy.deepcopy(self.route)
        bad['prep']['keepouts']['rects'][0]['y0']=62.
        self.assertTrue(any(f.startswith('hot-halo:')
                            for f in inspect_mask(bad,self.geometry)['failures']))

    def test_switching_source_primitives_and_physical_planes_are_preserved(self):
        before=yaml.safe_load(subprocess.check_output(
            ['git','show','1b725986:projects/crow-audio-carrier-v1/03_src/route.yaml'],
            cwd=REPO,timeout=15))
        hot=lambda route:[s for s in route['prep']['seed_stubs']['stubs'] if s['net'] in {'BUCK_SW','BUCK_BST'}]
        old=hot(before); current=hot(self.route)
        self.assertEqual([s for s in current if s['pin']!='C_BUCK_BST.2'],old)
        self.assertEqual([s for s in current if s['pin']=='C_BUCK_BST.2'],
            [{'net':'BUCK_SW','pin':'C_BUCK_BST.2','segments':[
                {'layer':'F.Cu','width':.2,
                 'pts':[[44.48,62.95],[44.5,65.45]]}]}])
        masks=[r for r in self.route['prep']['keepouts']['rects'] if r['layer']=='User.3']
        self.assertEqual(len(masks),3)
        self.assertEqual(self.floor['zones'],[{'net':'GND','layers':['F.Cu','In1.Cu','In2.Cu','B.Cu'],
            'priority':0,'min_thickness':.25,'clearance':.25,'connect':'thermal'}])


if __name__=='__main__':unittest.main()
