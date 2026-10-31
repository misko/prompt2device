"""Quote derivative regressions; no vendor or engineering admission implied."""
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
import quote_files as q


def rows(blob):
    return list(csv.DictReader(io.StringIO(blob.decode())))


class QuoteFilesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = q.payloads()

    def test_per_board_quantities_and_manual_scope(self):
        for board, smt, manual, count in [('carrier', 127, 10, 5), ('pod', 28, 1, 10)]:
            full = rows(self.payload[board + '-bom.csv'])
            machine = rows(self.payload[board + '-smt-bom.csv'])
            self.assertEqual(sum(int(r['Quantity']) for r in full), smt+manual)
            self.assertEqual(sum(int(r['Quantity']) for r in machine), smt)
            for r in full:
                self.assertEqual(int(r['Quantity']), len(r['Designator'].split(',')))
            self.assertEqual(len(rows(self.payload[board + '-cpl.csv'])), smt)
        scope = rows(self.payload['scope.csv'])
        self.assertEqual(len(scope), 177)
        self.assertEqual(sum(int(r['installed_batch']) for r in scope), 1000)
        for filename, total in [('manual-assembly.csv', 60), ('user-installation.csv', 25)]:
            self.assertEqual(sum(int(r['installed_batch']) for r in rows(self.payload[filename])), total)

    def test_original_cpl_and_gerbers_byte_identical(self):
        for board in q.COUNTS:
            self.assertEqual(self.payload[board + '-cpl.csv'],
                             (q.ASSEMBLY / (board+'-consigned-cpl.csv')).read_bytes())
            self.assertEqual(self.payload[board + '-gerbers.zip'],
                             (q.RELEASE / f'fab/{board}/{board}-gerbers.zip').read_bytes())

    def test_no_manual_or_user_machine_placement(self):
        for board in q.COUNTS:
            cpl = {r['Designator'] for r in rows(self.payload[board+'-cpl.csv'])}
            smt = {ref for r in rows(self.payload[board+'-smt-bom.csv']) for ref in r['Designator'].split(',')}
            self.assertEqual(cpl, smt)
            for file in ['manual-assembly.csv', 'user-installation.csv']:
                self.assertFalse(cpl & {r['reference'] for r in rows(self.payload[file]) if r['board'] == board})

    def test_global_codes_not_misrepresented_and_suffixes_preserved(self):
        for board in q.COUNTS:
            for r in rows(self.payload[board+'-bom.csv']):
                if r['Supply route'] == 'JLC_Global_Sourcing':
                    self.assertEqual(r['JLCPCB Part #'], '')
                    self.assertIn(r['MPN'], {'PCM1864DBT', 'R-78E5.0-0.5'})
                else:
                    self.assertRegex(r['JLCPCB Part #'], r'^C[1-9][0-9]*$')
                self.assertNotEqual(r['MPN'], 'PCM1864DBTR')

    def test_roundtrip_and_overwrite_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / 'draft'
            q.build(out)
            self.assertEqual(q.verify(out)['result'], 'PASS')
            with self.assertRaisesRegex(ValueError, 'overwrite'):
                q.build(out)

    def test_tampered_quantity_angle_code_exclusion_rejected(self):
        mutations = [('carrier-bom.csv', 'Quantity', '999'),
                     ('carrier-bom.csv', 'JLCPCB Part #', 'C1'),
                     ('carrier-cpl.csv', 'Rotation', '123.000000'),
                     ('user-installation.csv', 'installed_batch', '0')]
        for filename, field, value in mutations:
            with self.subTest(filename=filename, field=field), tempfile.TemporaryDirectory() as directory:
                out = Path(directory) / 'draft'
                q.build(out)
                data = q.read_csv(out / filename)
                data[0][field] = value
                (out / filename).write_bytes(q.csv_bytes(data, list(data[0])))
                with self.assertRaisesRegex(ValueError, 'changed draft'):
                    q.verify(out)

    def test_stale_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / 'draft'
            q.build(out)
            manifest = json.loads((out/'manifest.json').read_text())
            manifest['board_quantities']['pod'] = 5
            (out/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'stale manifest'):
                q.verify(out)


if __name__ == '__main__':
    unittest.main()
