"""Negative controls for raw-catalog CPL replay; not a live-JLC test."""
import copy
import csv
import io
import json
import math
import unittest

import mapping as m


class MappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = m.expected()
        cls.report = json.loads(cls.outputs['measurements.json'])
        cls.rows = cls.report['connectors']

    def check_pose(self, r, pose):
        return m.errors(r['native_pins'], r['native_pegs'],
                        *m.replay(r['catalog_pins'],r['catalog_pegs'],pose))

    def test_every_connector_and_candidate(self):
        self.assertEqual({(r['board'],r['reference']) for r in self.rows},
                         {('pod','J1'),('carrier','J1')} | {('carrier',f'J{n}') for n in range(101,109)})
        for r in self.rows:
            self.assertLess(max(self.check_pose(r,r['candidate']).values()), .03)
            self.assertGreater(max(self.check_pose(r,r['before']).values()), .03)

    def test_wrong_rotation_rejected_for_every_instance(self):
        for r in self.rows:
            pose = dict(r['candidate'],Rotation=str((float(r['candidate']['Rotation'])+180)%360))
            self.assertGreater(self.check_pose(r,pose)['max_pin_mm'], 1)

    def test_body_centre_with_correct_rotation_still_fails(self):
        for r in self.rows:
            pose = dict(r['before'],Rotation=r['candidate']['Rotation'])
            self.assertGreater(self.check_pose(r,pose)['max_pin_mm'], 1)

    def test_generic_legacy_datum_is_not_a_raw_catalog_origin_for_rj(self):
        for r in self.rows:
            if r['code'] != 'C599441':
                continue
            self.assertAlmostEqual(r['legacy_catalog_datum_mm'][1],1.27)
            x,y = r['legacy_native_datum_mm']
            pose = dict(r['candidate'], **{'Mid X':str(x)+'mm','Mid Y':str(-y)+'mm'})
            self.assertGreater(self.check_pose(r,pose)['max_pin_mm'],1.2)

    def test_manufacturer_locator_pattern_independent_of_fit(self):
        for r in self.rows:
            if r['code'] != 'C599441':
                continue
            x,y = r['native_pins']['1']
            # Amphenol component-side primary inch dimensions, converted to mm.
            expected = [[x-.110*25.4,y-.100*25.4], [x+.390*25.4,y-.100*25.4]]
            for a,b in zip(sorted(expected), sorted(r['native_pegs'])):
                self.assertLess(math.dist(a,b),.006)

    def test_terminal_swap_and_missing_peg_fail(self):
        r = self.rows[0]
        pins = copy.deepcopy(r['catalog_pins'])
        pins['1'],pins['8'] = pins['8'],pins['1']
        actual = m.replay(pins,r['catalog_pegs'],r['candidate'])
        self.assertGreater(m.errors(r['native_pins'],r['native_pegs'],*actual)['max_pin_mm'],1)
        with self.assertRaises(ValueError):
            m.errors(r['native_pins'],r['native_pegs'],actual[0],actual[1][:-1])

    def test_all_quarter_turns_against_native_engine(self):
        import pcbnew
        fp = pcbnew.FOOTPRINT(None)
        pad = pcbnew.PAD(fp)
        pad.SetNumber('1');fp.Add(pad)
        pad.SetPosition(pcbnew.VECTOR2I(2300000,-1700000))
        for angle in (0,90,180,270):
            fp.SetOrientationDegrees(angle)
            actual = m.replay({'1':[2.3,-1.7]},[],
                {'Mid X':'0mm','Mid Y':'0mm','Rotation':str(angle),'Layer':'Top'})[0]['1']
            self.assertLess(math.dist(actual,[pad.GetPosition().x/1e6,pad.GetPosition().y/1e6]),1e-6)

    def test_only_authorized_rows_change(self):
        for name, blob in self.outputs.items():
            if not name.endswith('.csv'):
                continue
            board = name.split('-')[0]
            old = (m.BASE/f'{board}-cpl.csv').read_bytes()
            before = {r['Designator']:r for r in csv.DictReader(io.StringIO(old.decode()))}
            after = {r['Designator']:r for r in csv.DictReader(io.StringIO(blob.decode()))}
            self.assertEqual(set(before),set(after))
            changed = {r for r in before if before[r] != after[r]}
            wanted = {r['reference'] for r in self.rows if r['board']==board}
            if '-ONLY-' in name:
                wanted = {name.split('-')[1]}
            self.assertEqual(changed,wanted)
            for r in changed:
                self.assertEqual(before[r]['Layer'],after[r]['Layer'])
            for line in old.splitlines(keepends=True)[1:]:
                if line.split(b',',1)[0].decode() not in changed:
                    self.assertIn(line,blob.splitlines(keepends=True))

    def test_pod_candidate_matches_existing_test_c(self):
        prior = m.HERE.parent/'r10-pod-j1-origin/pod-cpl-J1-180-Y9390-TEST-ONLY.csv'
        self.assertEqual(prior.read_bytes(),self.outputs['pod-ALL-CONNECTORS-RAW-ORIGIN-TEST-ONLY.csv'])

    def test_wrong_side_nonfinite_duplicate_and_missing_refs_refused(self):
        r = self.rows[0]
        for pose in [dict(r['candidate'],Layer='Bottom'),dict(r['candidate'],Rotation='nan')]:
            with self.assertRaises(ValueError):
                self.check_pose(r,pose)
        blob = (m.BASE/'pod-cpl.csv').read_bytes()
        with self.assertRaises(ValueError):
            m.revise(blob,{'J999':r['candidate']})
        with self.assertRaises(ValueError):
            m.revise(blob+blob.splitlines(keepends=True)[1],{})


if __name__ == '__main__':
    unittest.main()
