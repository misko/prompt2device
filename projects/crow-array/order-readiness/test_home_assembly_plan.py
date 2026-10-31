"""Scenario/ownership checks, not vendor production acceptance."""
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
import home_assembly_plan as h


def rows(blob):
    return list(csv.DictReader(io.StringIO(blob.decode())))


class HomeAssemblyPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = h.payloads()
        cls.parts = rows(cls.data['procurement-plan.csv'])

    def test_complete_scenario_demands(self):
        self.assertEqual(len(self.parts), 38)
        for r in self.parts:
            c, p = int(r['per_carrier']), int(r['per_pod'])
            self.assertEqual(int(r['installed_A_1c8p']), c+8*p)
            self.assertEqual(int(r['installed_B_5c8p']), 5*c+8*p)
            for unknown in ['purchase_quantity', 'price', 'usable_arrival']:
                self.assertEqual(r[unknown], '')
        for key, total, smt, home in [('installed_A_1c8p', 386, 351, 35),
                                      ('installed_B_5c8p', 938, 859, 79)]:
            self.assertEqual(sum(int(r[key]) for r in self.parts), total)
            self.assertEqual(sum(int(r[key]) for r in self.parts if r['owner']=='JLC_SMT'), smt)
            self.assertEqual(sum(int(r[key]) for r in self.parts if r['owner']=='HOME'), home)

    def test_six_home_identities_and_no_recom_global(self):
        home = {r['mpn']: r for r in rows(self.data['home-install-parts.csv'])}
        self.assertEqual(set(home), h.HOME)
        expected = {'RJHSE-5080': (16,48), 'PJ-102AH': (1,5), 'R-78E5.0-0.5': (1,5),
                    'SC0915': (1,5), 'CMA-4544PF-W': (8,8), 'CPE-203': (8,8)}
        for mpn,(a,b) in expected.items():
            self.assertEqual((int(home[mpn]['installed_A_1c8p']), int(home[mpn]['installed_B_5c8p'])), (a,b))
            self.assertEqual(home[mpn]['proposed_route'], 'external_to_home')

    def test_shortages_exact_and_stock_not_deducted_twice(self):
        short = {r['mpn']:r for r in rows(self.data['shortage-parts.csv'])}
        self.assertEqual(set(short), h.SHORT)
        self.assertEqual(short['1206L010/30WR']['installed_A_1c8p'], '16')
        self.assertEqual(short['1206L010/30WR']['installed_B_5c8p'], '48')
        self.assertEqual(short['PCM1864DBT']['installed_A_1c8p'], '2')
        self.assertNotIn('PCM1864DBTR', short)

    def test_uploads_preserved_per_board_smt_only(self):
        for board, count in [('carrier',127),('pod',28)]:
            bom = rows(self.data[f'{board}-bom.csv'])
            refs = {ref for r in bom for ref in r['Designator'].split(',')}
            cpl = rows(self.data[f'{board}-cpl.csv'])
            self.assertEqual(len(refs), count)
            self.assertEqual({r['Designator'] for r in cpl}, refs)
            self.assertFalse({r['MPN'] for r in bom} & h.HOME)
            for dst,src in [(f'{board}-bom.csv',f'{board}-smt-bom.csv'),
                            (f'{board}-cpl.csv',f'{board}-cpl.csv'),
                            (f'{board}-gerbers.zip',f'{board}-gerbers.zip')]:
                self.assertEqual(self.data[dst], (h.q.DEFAULT/src).read_bytes())

    def test_all_native_references_accounted(self):
        scope = rows(self.data['scope.csv'])
        self.assertEqual(len(scope),177)
        self.assertEqual(len({(r['board'],r['reference']) for r in scope}),177)
        self.assertEqual(sum(r['owner']=='MECHANICAL' for r in scope),8)
        self.assertFalse(any(r['owner']=='JLC_manual_requested' for r in scope))
        self.assertEqual(sum(int(r['installed_A_1c8p']) for r in scope),386)
        self.assertEqual(sum(int(r['installed_B_5c8p']) for r in scope),938)

    def test_verify_overwrite_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'r3'
            h.build(out)
            self.assertEqual(h.verify(out)['result'],'PASS')
            with self.assertRaisesRegex(ValueError,'existing revision'):
                h.build(out)
            data=json.loads((out/'scenarios.json').read_text())
            data['A_target_1c8p']['pod_assembled']=10
            (out/'scenarios.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'changed scenario artifact'):
                h.verify(out)


if __name__=='__main__':
    unittest.main()
