# SPDX-License-Identifier: MIT
"""New ownership and known-bad tests: no fabricated THT placement acceptance."""
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
import jlc_tht_quote as t


def rows(blob):
    return list(csv.DictReader(io.StringIO(blob.decode())))


class ThtQuoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = t.payloads()

    def test_full_counts_and_partition(self):
        scope = rows(self.data['scope.csv'])
        totals = {who: sum(int(r['installed_batch']) for r in scope if r['owner'] == who)
                  for who in ('JLC_SMT', 'JLC_THT', 'HOME')}
        self.assertEqual(totals, {'JLC_SMT': 478, 'JLC_THT': 28, 'HOME': 18})
        self.assertEqual(sum(totals.values()), 524)

    def test_home_and_factory_identities(self):
        home = rows(self.data['home-install-parts.csv'])
        self.assertEqual({r['mpn']: int(r['installed_2c8p']) for r in home},
                         {'SC0915': 2, 'CMA-4544PF-W': 8, 'CPE-203': 8})
        tht = rows(self.data['jlc-tht-parts.csv'])
        self.assertEqual({r['mpn']: int(r['installed_2c8p']) for r in tht},
                         {'RJHSE-5080': 24, 'PJ-102AH': 2, 'R-78E5.0-0.5': 2})
        self.assertEqual(next(r for r in tht if r['mpn'] == 'R-78E5.0-0.5')['proposed_route'],
                         'JLC_Global_Sourcing_or_consignment_candidate')

    def test_bom_per_board_no_home_and_no_global_code_credit(self):
        for board, count in [('carrier', 137), ('pod', 29)]:
            bom = rows(self.data[board + '-bom.csv'])
            self.assertEqual(sum(int(r['Quantity']) for r in bom), count)
            self.assertFalse({r['MPN'] for r in bom} & t.HOME)
            for r in bom:
                if r['MPN'] in ('PCM1864DBT', 'R-78E5.0-0.5'):
                    self.assertEqual(r['JLCPCB Part #'], '')

    def test_preserved_smt_and_gerbers(self):
        for board in t.COUNTS:
            self.assertEqual(self.data[board + '-cpl-SMT-ONLY-INCOMPLETE.csv'],
                             (t.q.DEFAULT / (board + '-cpl.csv')).read_bytes())
            self.assertEqual(self.data[board + '-gerbers.zip'],
                             (t.q.DEFAULT / (board + '-gerbers.zip')).read_bytes())
            self.assertNotIn(board + '-cpl.csv', self.data)

    def test_no_guessed_tht_coordinates(self):
        for board, count in [('carrier', 10), ('pod', 1)]:
            template = rows(self.data[board + '-cpl-THT-NOT-UPLOAD.csv'])
            self.assertEqual(len(template), count)
            self.assertTrue(all(r[k] == '' for r in template for k in ('Mid X', 'Mid Y', 'Rotation')))

    def test_build_verify_and_upload_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'r4'
            t.build(output)
            self.assertEqual(t.verify(output)['result'], 'PASS')
            with self.assertRaisesRegex(ValueError, 'NOT UPLOAD-READY'):
                t.verify(output, require_upload_ready=True)
            with self.assertRaisesRegex(ValueError, 'overwrite'):
                t.build(output)

    def test_tampered_bom_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'r4'
            t.build(output)
            path = output / 'carrier-bom.csv'
            path.write_text(path.read_text().replace('RJHSE-5080', 'RJHSE-5081'))
            with self.assertRaisesRegex(ValueError, 'Changed quote artifact'):
                t.verify(output)

    def test_tampered_authority_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'r4'
            t.build(output)
            path = output / 'manifest.json'
            record = json.loads(path.read_text())
            record['upload_ready'] = True
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, 'manifest'):
                t.verify(output)


if __name__ == '__main__':
    unittest.main()
