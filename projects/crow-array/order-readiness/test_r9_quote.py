"""Regression tests for the authorized home-clock assembly split."""
import json
import shutil
import tempfile
import unittest
import r9_quote as r


class HomeClock(unittest.TestCase):
    def test_valid_package(self):
        result = r.verify(r.OUT)
        self.assertEqual(result['installed'], {'JLC_SMT':476,'JLC_THT':28,'HOME':20,'total':524})

    def test_only_clock_changes_owner(self):
        a = r.q.read_csv(r.BASE/'scope.csv')
        b = r.q.read_csv(r.OUT/'scope.csv')
        changed = [(x,y) for x,y in zip(a,b) if x != y]
        self.assertEqual(len(changed), 1)
        old,new = changed[0]
        self.assertEqual((new['board'],new['reference'],new['owner']), ('carrier','X1','HOME'))
        self.assertEqual({**old,'owner':'HOME'}, new)
        self.assertEqual(len(a),len(b))

    def test_c4_remains_factory(self):
        rows = r.q.read_csv(r.OUT/'carrier-bom.csv')
        self.assertFalse(any(x['Designator'] == 'X1' for x in rows))
        self.assertEqual(next(x for x in rows if x['Designator']=='C4')['MPN'], 'CL21B105KBFNNNE')
        plan = r.q.read_csv(r.OUT/'procurement-plan.csv')
        self.assertEqual(next(x for x in plan if x['mpn']=='CL21B105KBFNNNE')['installed_2c8p'], '14')

    def test_rehashed_unauthorized_omission_rejected(self):
        with tempfile.TemporaryDirectory(prefix='crow-r9-test-') as tmp:
            target = r.Path(tmp)/'package'
            shutil.copytree(r.OUT,target)
            path = target/'carrier-bom.csv'
            rows = [x for x in r.q.read_csv(path) if x['Designator'] != 'C4']
            path.write_bytes(r.q.csv_bytes(rows))
            manifest = target/'manifest.json'
            m = json.loads(manifest.read_text())
            m['files']['carrier-bom.csv'] = r.q.sha(path)
            manifest.write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError, 'Wrong derived table'):
                r.verify(target)

    def test_rehashed_board_change_rejected(self):
        with tempfile.TemporaryDirectory(prefix='crow-r9-test-') as tmp:
            target = r.Path(tmp)/'package'
            shutil.copytree(r.OUT,target)
            relative = 'native/pcb/carrier/carrier.kicad_pcb'
            path = target/relative
            path.write_bytes(path.read_bytes()+b'\n')
            manifest = target/'manifest.json'
            m = json.loads(manifest.read_text())
            m['files'][relative] = r.q.sha(path)
            manifest.write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError, 'Changed protected payload'):
                r.verify(target)


if __name__ == '__main__':
    unittest.main(verbosity=2)
