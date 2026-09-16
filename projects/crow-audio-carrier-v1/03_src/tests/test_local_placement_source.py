"""Declaration/ownership regressions only; never construct or save a PCB.

Realized copper, ground returns, body/courtyard and routes remain owning gates.
The hostile distance example calls the existing policy consumer, not a second
production proximity implementation.
"""
import copy
import math
import sys
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import yaml

PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO / 'skills/kicad-pcb/scripts'))
from generate_board_generic import BoardBuilder
from source_inventory import parse_netlist
from policy_audit import physical_pin_keep_short_spans

DATUMS = {**{f'J{i+1}': [38.0+32*i, 25.86, 0] for i in range(4)},
          **{f'J{i+5}': [43.0+32*i, 114.14, 180] for i in range(4)},
          'J9': [28.0, 69.0, 90], 'J10': [158.0, 49.0, 90], 'J11': [158.0, 80.0, 90]}


def source_builder(config):
    obj = object.__new__(BoardBuilder)
    obj.cfg = copy.deepcopy(config)
    obj.place_cfg = obj.cfg['placement']
    obj.silk_cfg = obj.cfg['silk']
    obj.log = []
    obj.say = lambda message: obj.log.append(message)
    outline = obj.cfg['board']['outline']
    obj.X0, obj.Y0, obj.X1, obj.Y1 = (outline[k] for k in ('x0', 'y0', 'x1', 'y1'))
    obj.expand_repeats()
    return obj


class LocalPlacementSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load((PROJECT / '03_src/floorplan.yaml').read_text())
        cls.comps, cls.pin_nets, _ = parse_netlist(PROJECT / cls.config['project']['netlist'])
        cls.parts = {d['mpn']: d for path in (PROJECT / '02_parts').glob('*/part.yaml')
                     for d in [yaml.safe_load(path.read_text())]}
        cls.adj = [row for part in cls.parts.values() for row in part.get('layout', {}).get('adjacency', [])]

    def test_all_333_fitted_refs_are_uniquely_pinned(self):
        b = source_builder(self.config)
        self.assertEqual(len(self.comps), 333)
        self.assertTrue(b.place_cfg['require_anchor'])
        self.assertEqual(set(b.place_cfg['anchors']), set(self.comps))
        self.assertTrue(all(b.initial_pose(ref)[3] for ref in self.comps))
        self.assertEqual(len(self.config['placement']['anchors']), 141)

    def test_rj45_datums_and_board_outline(self):
        self.assertEqual({r: self.config['placement']['anchors'][r] for r in DATUMS}, DATUMS)
        self.assertEqual(self.config['board']['outline'], {'x0':16., 'y0':20., 'x1':172., 'y1':120.})
        self.assertEqual(self.config['board']['mounting_holes']['at'], [[21.,25.],[165.,25.],[21.,115.],[165.,115.]])
        self.assertEqual(self.config['board']['fiducials']['at'], [[25.,33.],[161.,29.],[29.,111.]])
        self.assertEqual(self.config['board']['layers'], 4)

    def test_two_repeat_banks_are_exact_mirrors(self):
        north, south = self.config['placement']['repeat']
        self.assertEqual((north['count'], south['count']), (4, 4))
        self.assertEqual((north['index_from'], south['index_from']), (1, 5))
        self.assertEqual(north['pitch'], south['pitch'])
        self.assertEqual(len(north['members']), 24)
        self.assertEqual(set(north['members']), set(south['members']))
        for ref, pose in north['members'].items():
            other = south['members'][ref]
            self.assertEqual(other['at'], [-v for v in pose['at']], ref)
            self.assertEqual(other['rot'], (pose['rot']+180) % 360, ref)
        self.assertFalse(any('ADC_CM' in r for r in north['members']))
        self.assertEqual(north['members']['C_A{i}P']['rot'], 270)
        self.assertEqual(north['members']['C_A{i}N']['rot'], 270)

    def test_all_146_caps_and_nonconnector_roles_are_covered(self):
        covered = {ref for row in self.adj for ref in row['refdes']}
        caps = {r for r in self.comps if r.startswith('C_')}
        self.assertEqual(len(caps), 146)
        self.assertFalse(caps-covered)
        self.assertEqual(set(self.comps)-covered, {'J10', 'J11'})
        self.assertEqual(len(self.adj), 353)

    def test_each_pair_names_real_shared_nonpoured_nets(self):
        for row in self.adj:
            a, b = row['refdes']
            self.assertIn(a, self.comps)
            self.assertIn(b, self.comps)
            self.assertNotEqual(a, b)
            self.assertGreater(row['max_mm'], 0)
            self.assertTrue(row['nets'])
            self.assertNotIn('GND', row['nets'])
            shared = {n for (r,p),n in self.pin_nets.items() if r==a} & {n for (r,p),n in self.pin_nets.items() if r==b}
            self.assertFalse(set(row['nets'])-shared, row)

    def test_repeated_bypasses_bind_exact_owner_not_nearest_family(self):
        for prefix, cap, rail, count in [('U_AFE','C_OPA','3V3_ADC',8), ('U_ISO','C_ISO','5V_LDO_HOLD',8)]:
            for i in range(1,count+1):
                matches = [r for r in self.adj if r['refdes']==[f'{prefix}{i}',f'{cap}{i}']]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0]['nets'], [rail])
                self.assertLessEqual(matches[0]['max_mm'], 2.5)
        for mpn in ('OPA2320AIDR', 'TMUX2821DSGR', 'TPS389001DSER', '74LVC1G14GV,125'):
            self.assertFalse(self.parts[mpn]['layout'].get('keep_short'))

    def test_adc_capacitors_bind_each_physical_pin(self):
        rows = self.parts['CS5308P-DN']['layout']['keep_short']
        expected = {'C_LDO_A':{'7'}, 'C_LDO_D':{'32','33'}, 'C_VDDIO':{'31'},
                    'C_VDDA1_10N':{'5'}, 'C_VDDA1_4U7':{'5'}, 'C_VDDA2_10N':{'9'}, 'C_VDDA2_4U7':{'9'},
                    'C_VMID1_470N':{'1'}, 'C_VMID1_4U7':{'1'}, 'C_VMID2_470N':{'12'}, 'C_VMID2_4U7':{'12'}}
        for i,pin in [(1,'43'),(2,'18')]:
            for suffix in ['1U','10U']: expected[f'C_FILT{i}_{suffix}']={pin}
        for i in range(1,9):
            for leg in 'PN':
                net=f'ADC{i}{leg}'
                expected[f'C_ADC_CM{i}{leg}']={p for (r,p),n in self.pin_nets.items() if r=='U_ADC' and n==net}
        for cap,pins in expected.items():
            rr=[r for r in rows if r['partner_refs']==[cap]]
            self.assertEqual(len(rr),1,cap)
            self.assertEqual(set(map(str,rr[0]['anchor_pins'])),pins,cap)
            self.assertEqual(rr[0]['max_span_mm'],5,cap)

    def test_pin_specific_owner_footprints_are_unique(self):
        counts=Counter(fpid for fpid,value in self.comps.values())
        for part in self.parts.values():
            for row in part.get('layout',{}).get('keep_short',[]):
                self.assertEqual(counts[part['footprint']],1,part['mpn'])
                if part['mpn']!='XGL4020-332MEC':
                    self.assertEqual(len(row['partner_refs']),1)
                    self.assertTrue(row['anchor_pins'])

    def test_existing_consumer_rejects_distant_intended_cap_even_with_close_rail_neighbor(self):
        def pad(number,x):
            return SimpleNamespace(GetNumber=lambda:number, GetPosition=lambda:SimpleNamespace(x=x,y=0))
        def fp(ref): return SimpleNamespace(GetReference=lambda:ref)
        u=fp('U_ADC'); intended=fp('C_VDDA1_10N'); wrong=fp('C_VDDA2_10N')
        anchor=pad('5',0); far=pad('1',20_000_000); near=pad('1',1_000_000)
        rows=self.parts['CS5308P-DN']['layout']['keep_short']
        rule=next(r for r in rows if r['partner_refs']==['C_VDDA1_10N'])
        points=[(anchor,u),(far,intended),(near,wrong)]
        span=lambda a,b: math.hypot(a.GetPosition().x-b.GetPosition().x,a.GetPosition().y-b.GetPosition().y)/1e6
        got=physical_pin_keep_short_spans([(anchor,u)],points,span,set(rule['partner_refs']))
        self.assertEqual(len(got),1)
        self.assertGreater(got[0][0],rule['max_span_mm'])
        # The unconstrained nearest-rail calculation would falsely look local.
        self.assertLess(physical_pin_keep_short_spans([(anchor,u)],points,span)[0][0],rule['max_span_mm'])

    def assert_fuse_caption_owners(self, b):
        # Actual reference and fitted side, under the unchanged 3mm budget.
        # The old P# selector is RED on the source's F# PTC captions.
        captions=b.silk_cfg['captions']
        for i in range(1,9):
            ref=f'F{i}'
            self.assertEqual(b.place_cfg['sides'].get(ref,'top'), 'top')
            rows=[r for r in captions if isinstance(r,dict) and r.get('text')==f'{ref} PTC']
            self.assertEqual(len(rows),1,ref)
            x,y,_,_=b.initial_pose(ref)
            self.assertLess(math.hypot(rows[0]['at'][0]-x,rows[0]['at'][1]-y),3,ref)
            self.assertFalse(any(isinstance(r,list) and r[0] in (f'P{i}',f'{ref} PTC') for r in captions),ref)
            self.assertFalse(any(isinstance(r,dict) and r.get('text')==f'P{i}' for r in captions),ref)

    def test_fuse_captions_have_one_local_owner(self):
        b=source_builder(self.config)
        self.assert_fuse_caption_owners(b)
        main=[r for r in b.silk_cfg['captions'] if isinstance(r,dict) and r.get('text')=='MAIN']
        self.assertEqual(main,[{'text':'MAIN','at':[32.5,73.3],'size':.5,'nudge':False}])

    def test_fuse_caption_consumer_rejects_missing_duplicate_distant_wrong_owner(self):
        # All mutants call the same ownership consumer as the positive case.
        for kind in ('missing','duplicate','distant','wrong-owner','wrong-side'):
            with self.subTest(kind=kind):
                b=source_builder(self.config)
                captions=b.silk_cfg['captions']
                row=next(r for r in captions if isinstance(r,dict) and r.get('text')=='F1 PTC')
                if kind=='missing': captions.remove(row)
                elif kind=='duplicate': captions.append(copy.deepcopy(row))
                elif kind=='distant':
                    x,y,_,_=b.initial_pose('F1')
                    row['at']=[x+3.01,y]
                elif kind=='wrong-owner':
                    other=next(r for r in captions if isinstance(r,dict) and r.get('text')=='F2 PTC')
                    row['at'],other['at']=other['at'],row['at']
                else: b.place_cfg['sides']['F1']='bottom'
                with self.assertRaises(AssertionError): self.assert_fuse_caption_owners(b)

    def test_exact_eight_clamp_pad4_ground_override(self):
        refs={f'U_ESD{i}' for i in range(1,9)}
        rows=[r for r in self.config['placement']['patterns']
              if 'pad_overrides' in r and refs.intersection(r['match'])]
        self.assertEqual(len(rows),1)
        self.assertEqual(set(rows[0]),{'match','pad_overrides'})
        self.assertEqual(set(rows[0]['match']),refs)
        self.assertEqual(len(rows[0]['match']),8)
        self.assertEqual(rows[0]['pad_overrides'],[{'pads':['4'],'on_net':'GND','zone_connection':'full'}])
        self.assertTrue(all(self.pin_nets[(ref,'4')]=='GND' for ref in refs))

    def test_model_overrides_remain_exact_and_after_region_patterns(self):
        # GroundConnectionTests reject any model/region fields in the later
        # eight-pad connection patterns; those do not reorder model authority.
        patterns=self.config['placement']['patterns']
        overrides=[p for p in patterns if 'model_override' in p]
        regions=[p for p in patterns if 'region' in p]
        self.assertEqual(len(overrides),3)
        self.assertTrue(regions)
        self.assertLess(max(map(patterns.index,regions)),min(map(patterns.index,overrides)))
        self.assertEqual(set(overrides[0]['match']),{f'C_A{i}{s}' for i in range(1,9) for s in 'PN'})
        self.assertEqual(set(overrides[1]['match']),{f'F{i}' for i in range(1,9)})
        self.assertEqual(overrides[2]['match'],'F_IN')
        self.assertEqual([p['model_override'] for p in overrides],[
            '${KIPRJMOD}/../03_src/lib/3dmodels/kicad/C_Rect_L7.2mm_W5.0mm_P5.00mm.step',
            '${KIPRJMOD}/../03_src/lib/3dmodels/derived/Littelfuse_1812L035_60_max-envelope.wrl',
            '${KIPRJMOD}/../03_src/lib/3dmodels/derived/Littelfuse_2920L260_33_max-envelope.wrl'])


if __name__=='__main__': unittest.main()
