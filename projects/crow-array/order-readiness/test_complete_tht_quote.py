# SPDX-License-Identifier: MIT
"""Quote completeness and bad-pose regressions, not independent engineering acceptance."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import complete_tht_quote as c


class CompleteQuoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = c.payloads()
        cls.tht = c.placements()

    def test_per_board_and_batch_coverage(self):
        for board, count in [('carrier', 137), ('pod', 29)]:
            bom, cpl = (c.rows(self.data[f'{board}-{k}.csv']) for k in ('bom', 'cpl'))
            self.assertEqual(sum(int(r['Quantity']) for r in bom), count)
            self.assertEqual(len(cpl), count)
            c.check_cpl(board, cpl, bom, self.tht)
            self.assertFalse({r['MPN'] for r in bom} & c.t.HOME)
        self.assertEqual(137 * 2 + 29 * 8, 506)

    def test_original_smt_bom_and_gerber_bytes(self):
        for board in c.t.COUNTS:
            self.assertTrue(self.data[f'{board}-cpl.csv'].startswith(
                (c.q.DEFAULT / f'{board}-cpl.csv').read_bytes()))
            for kind in ('bom.csv', 'gerbers.zip'):
                self.assertEqual(self.data[f'{board}-{kind}'], (c.q.DEFAULT / f'{board}-{kind}').read_bytes())

    def test_body_centers_are_not_pad_one(self):
        poses = {(r['board'], r['reference']): (r['cpl_x'], r['cpl_y']) for r in self.tht}
        self.assertEqual(poses['carrier', 'J1'], (188, -8.7))
        self.assertEqual(poses['carrier', 'U10'], (184.59, -35.75))
        self.assertEqual(poses['carrier', 'J101'], (11.556, -8.373))
        self.assertEqual(poses['carrier', 'J108'], (142.456, -8.373))
        self.assertEqual(poses['pod', 'J1'], (10.556, -8.373))

    def test_actual_rounded_rj_geometry(self):
        pads = {str(i+1): (i*1.016, 1.78*(i % 2)) for i in range(8)}
        c.check_geometry('RJHSE-5080', pads, [(-2.79, -2.54), (9.91, -2.54)])

    def test_labeled_contacts_reject_mirror_and_pin_swap(self):
        for mpn, fact in c.FACTS.items():
            pads = {n: (-x, -y) for n, (x, y) in fact['pads'].items()}
            with self.assertRaisesRegex(ValueError, 'pin pose'):
                c.check_geometry(mpn, pads, fact['pegs'])
            pads = copy.deepcopy(fact['pads'])
            pads['1'], pads['2'] = pads['2'], pads['1']
            with self.assertRaisesRegex(ValueError, 'pin pose'):
                c.check_geometry(mpn, pads, fact['pegs'])

    def test_missing_peg_rejected(self):
        with self.assertRaisesRegex(ValueError, 'peg count'):
            c.check_geometry('RJHSE-5080', c.FACTS['RJHSE-5080']['pads'], [])

    def test_bad_cpl_side_angle_and_y_rejected(self):
        bom = c.rows(self.data['carrier-bom.csv'])
        for field, bad in [('Mid Y', '8.373000mm'), ('Rotation', '180.000000'), ('Layer', 'Bottom')]:
            cpl = c.rows(self.data['carrier-cpl.csv'])
            next(r for r in cpl if r['Designator'] == 'J101')[field] = bad
            with self.assertRaisesRegex(ValueError, 'coordinate/side/orientation'):
                c.check_cpl('carrier', cpl, bom, self.tht)

    def test_missing_duplicate_and_home_reference_rejected(self):
        bom = c.rows(self.data['carrier-bom.csv'])
        original = c.rows(self.data['carrier-cpl.csv'])
        for cpl in [original[:-1], original + [original[-1]], original + [dict(original[-1], Designator='U3')]]:
            with self.assertRaisesRegex(ValueError, 'reference coverage'):
                c.check_cpl('carrier', cpl, bom, self.tht)

    def test_portable_verification_and_authority_boundary(self):
        result = c.verify(c.DEFAULT)
        self.assertTrue(result['quote_upload_ready'])
        self.assertFalse(result['production_ready'])
        manifest = json.loads((c.DEFAULT / 'manifest.json').read_text())
        self.assertFalse(manifest['vendor_preview_approved'])
        self.assertFalse(manifest['purchase_authorized'])
        self.assertFalse(manifest['submitted'])

    def test_package_tamper_rejected(self):
        for filename in ['carrier-cpl.csv', 'native-audit.json', 'manifest.json', 'README.md']:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / 'r5'
                shutil.copytree(c.DEFAULT, output)
                path = output / filename
                if filename == 'manifest.json':
                    record = json.loads(path.read_text())
                    record['production_ready'] = True
                    path.write_text(json.dumps(record))
                elif filename == 'native-audit.json':
                    record = json.loads(path.read_text())
                    record['tht'].pop()
                    path.write_text(json.dumps(record))
                else:
                    path.write_bytes(path.read_bytes() + b'changed\n')
                with self.assertRaises(ValueError):
                    c.verify(output)

    def test_rebuild_refuses_existing_directory(self):
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            c.build(c.DEFAULT)


if __name__ == '__main__':
    unittest.main()
