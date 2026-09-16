"""September 8 P-ADJ-PAIR regression: isolated footprints, never a BOARD.

The generated 003a8bff board had a 1.625 mm U_ADC.7/C_LDO_A.1 copper-box
gap despite passing its 5 mm centre-distance screen. Moving only east meets
adjacency but violates the U_ADC.6 ground-via clearance. Both properties must
hold together, with existing seed contact and body/pad clearances preserved.
These live-source tests do not replace generated placement, DRC or review.
RED-verified before the source move on September 8: five tests ran, with the
live adjacency and exact-delta tests failing; all three hostile tests passed.
"""
import copy
import math
import subprocess
import unittest

import pcbnew
import yaml
from test_route_source_contract import PROJECT, REPO, load_source
from test_digital_launch_source import native_geometry, segment_rows, pair_clearance
from test_regulator_source import via_rows, connected_reach
from placement_gates import _poly_gap_mm

BASE = '003a8bff3f7f15abfe5bcd6e92c7e801a95d80cb'
OLD_POSE = [89.8, 70.0, 180]
NEW_POSE = [89.93, 70.05, 180]


def inspect_bypass(floor, route, nets, geometry=None):
    geometry = geometry or native_geometry(floor)
    pads = {p['id']: p for p in geometry['pads']}
    cap, adc = pads['C_LDO_A.1'], pads['U_ADC.7']
    a, b = cap['shape'].BBox(), adc['shape'].BBox()
    gap = math.hypot(max(0, a.GetLeft()-b.GetRight(), b.GetLeft()-a.GetRight()),
                     max(0, a.GetTop()-b.GetBottom(), b.GetTop()-a.GetBottom()))/1e6
    dossier = yaml.safe_load((PROJECT/'02_parts/CS5308P-DN/part.yaml').read_text())
    rules = [r for r in dossier['layout']['adjacency']
             if r['refdes'] == ['U_ADC', 'C_LDO_A']]
    assert len(rules) == 1 and rules[0]['nets'] == ['LDO_A_FILT']
    assert cap['net'] == adc['net'] == 'LDO_A_FILT'
    failures = [('adjacency', 'U_ADC.7', 'C_LDO_A.1')] if gap > rules[0]['max_mm'] else []
    own_pads = [pads[f'C_LDO_A.{n}'] for n in (1, 2)]
    rows, vias = segment_rows(route), via_rows(route)
    for own in own_pads:
        for other in geometry['pads']:
            if other in own_pads:
                continue
            if pcbnew.SHAPE.Collide(own['shape'], other['shape'], 127000-2):
                failures.append(('distinct-pad', own['id'], other['id']))
        for other in rows:
            if own['net'] != other['net'] and pcbnew.SHAPE.Collide(
                    own['shape'], other['shape'],
                    round(pair_clearance(own, other, floor, nets)*1e6)-2):
                failures.append(('pad/seed', own['id'], other['id']))
        for via in vias:
            if own['net'] != via['net'] and pcbnew.SHAPE.Collide(
                    own['shape'], via['shape'], 250000-2):
                failures.append(('pad/via', own['id'], via['id']))
            if via['hole'].Collide(own['shape'], 255000-2):
                failures.append(('pad/hole', own['id'], via['id']))
    refs = sorted({p['id'].split('.')[0] for p in geometry['pads']})
    footprints = dict(zip(refs, geometry['footprints']))
    for fp in footprints.values():
        fp.BuildCourtyardCaches()
    body = footprints['C_LDO_A'].GetCourtyard(pcbnew.F_CrtYd)
    assert body.OutlineCount()
    for ref, fp in footprints.items():
        if ref == 'C_LDO_A':
            continue
        other_body = fp.GetCourtyard(pcbnew.F_CrtYd)
        if other_body.OutlineCount() and _poly_gap_mm(body, other_body, .1) < .1-1e-6:
            failures.append(('courtyard', 'C_LDO_A', ref))
        for pad in fp.Pads():
            if pad.IsOnCopperLayer() and pad.IsOnLayer(pcbnew.F_Cu) and body.Collide(
                    pad.GetEffectiveShape(pcbnew.F_Cu), 100000-2):
                failures.append(('body/foreign-pad', 'C_LDO_A', ref+'.'+pad.GetNumber()))
        if other_body.OutlineCount():
            for own in own_pads:
                if other_body.Collide(own['shape'], 100000-2):
                    failures.append(('foreign-body/pad', ref, own['id']))
    reached = set(connected_reach(route, geometry, 'U_ADC.7'))
    if reached != {'C_LDO_A.1', 'U_ADC.7'}:
        failures.append(('seed-contact', 'U_ADC.7', sorted(reached)))
    return dict(failures=failures, gap_mm=gap, limit_mm=rules[0]['max_mm'],
                center_mm=math.dist(cap['at'], adc['at']),
                census=(len(pads), len(rows), len(vias)))


class AdcBypassPlacementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor, cls.route, cls.nets, *_ = load_source()
        cls.geometry = native_geometry(cls.floor)

    def test_current_pose_meets_both_adjacency_and_coupled_clearances(self):
        result = inspect_bypass(self.floor, self.route, self.nets, self.geometry)
        self.assertEqual(result['census'][0], len(self.geometry['pads']))
        self.assertTrue(all(n > 0 for n in result['census']))
        self.assertEqual(result['limit_mm'], 1.5)  # Never relax the engineering ceiling.
        self.assertEqual(result['failures'], [])
        self.assertLessEqual(result['gap_mm'], 1.5)

    def test_adopted_pose_and_adc_local_authority_are_preserved(self):
        before = yaml.safe_load(subprocess.check_output([
            'git', 'show', BASE+':projects/crow-audio-carrier-v1/03_src/floorplan.yaml'],
            cwd=REPO, timeout=15))
        self.assertEqual(before['placement']['anchors']['C_LDO_A'], OLD_POSE)
        self.assertEqual(self.floor['placement']['anchors']['C_LDO_A'], NEW_POSE)
        self.assertEqual(self.floor['placement']['anchors']['U_ADC'],
                         before['placement']['anchors']['U_ADC'])
        accepted_route = yaml.safe_load(subprocess.check_output([
            'git', 'show', '1b725986:projects/crow-audio-carrier-v1/03_src/route.yaml'],
            cwd=REPO, timeout=15))
        def local_seed(route):
            return [b for b in route['prep']['seed_stubs']['stubs'] if b['pin'] == 'U_ADC.7']
        self.assertEqual(len(local_seed(self.route)), 1)
        self.assertEqual(local_seed(self.route), local_seed(accepted_route))

    def test_real_old_pose_fails_exact_gap_while_broad_center_test_passes(self):
        bad = copy.deepcopy(self.floor)
        bad['placement']['anchors']['C_LDO_A'] = OLD_POSE
        result = inspect_bypass(bad, self.route, self.nets)
        self.assertAlmostEqual(result['gap_mm'], 1.625, places=6)
        self.assertLess(result['center_mm'], 5)
        self.assertEqual(result['failures'], [('adjacency', 'U_ADC.7', 'C_LDO_A.1')])

    def test_blind_east_shift_meets_adjacency_but_fails_ground_via(self):
        for x in (89.925, 89.95, 90.0):
            with self.subTest(x=x):
                bad = copy.deepcopy(self.floor)
                bad['placement']['anchors']['C_LDO_A'] = [x, 70.0, 180]
                result = inspect_bypass(bad, self.route, self.nets)
                self.assertLessEqual(result['gap_mm'], 1.5)
                self.assertIn(('pad/via', 'C_LDO_A.1', 'U_ADC.6:via0'), result['failures'])

    def test_missing_filter_seed_is_not_credited_as_connected(self):
        bad = copy.deepcopy(self.route)
        bank = next(b for b in bad['prep']['seed_stubs']['stubs'] if b['pin'] == 'U_ADC.7')
        bank['segments'] = []
        failures = inspect_bypass(self.floor, bad, self.nets, self.geometry)['failures']
        self.assertTrue(any(f[0] == 'seed-contact' for f in failures))


if __name__ == '__main__':
    unittest.main()
