"""Regression boundaries for the quote derivative; native checks run in build/verify."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import r10_quote as r


class QuoteRepairTests(unittest.TestCase):
    def test_only_factory_jack_pose_changes(self):
        old = r.q.read_csv(r.BASE / 'carrier-cpl.csv')
        expected = copy.deepcopy(old)
        for row in expected:
            if row['Designator'] == 'J1':
                row['Rotation'] = '180.000000'
                row['Mid Y'] = '-8.200000mm'
        self.assertEqual(r.tables()['carrier-cpl.csv'], expected)
        self.assertNotIn('X1', {row['Designator'] for row in expected})

    def test_only_jack_mechanical_row_changes(self):
        old = r.q.read_csv(r.BASE / 'tht-placement-verification.csv')
        new = r.tables()['tht-placement-verification.csv']
        changed = [(a, b) for a, b in zip(old, new) if a != b]
        self.assertEqual(len(changed), 1)
        a, b = changed[0]
        self.assertEqual((b['board'], b['reference']), ('carrier', 'J1'))
        self.assertEqual(b['anchor_y'], '14.7')
        self.assertEqual(b['body_center_y'], '8.2')
        self.assertEqual(b['cpl_y'], '-8.2')
        for key in ('mpn', 'body_center_x', 'cpl_x', 'layer'):
            self.assertEqual(a[key], b[key])

    def test_population_remains_unchanged(self):
        self.assertEqual(r.base.population(r.BASE), {'JLC_SMT': 476, 'JLC_THT': 28, 'HOME': 20})

    def test_fab_normalization_does_not_hide_geometry(self):
        a = b'%TF.CreationDate,old*%\nX100Y200D01*\n'
        b = b'%TF.CreationDate,new*%\nX100Y200D01*\n'
        c = b'%TF.CreationDate,new*%\nX101Y200D01*\n'
        self.assertEqual(r.normalize_fabrication(a), r.normalize_fabrication(b))
        self.assertNotEqual(r.normalize_fabrication(a), r.normalize_fabrication(c))

    def test_review_hold_cannot_be_packaged(self):
        with patch.object(r.Path, 'read_text', return_value='{"decision":"HOLD"}'):
            with self.assertRaises(Exception):
                r.reviewed()

    def test_reviewed_board_hash_mismatch_rejected(self):
        fake = '{"decision":"PASS_FOR_PROTOTYPE_QUOTE","subjects":{},"board":"fake","board_sha256":"expected"}'
        with patch.object(r.Path, 'read_text', return_value=fake), patch.object(r.q, 'sha', return_value='wrong'):
            with self.assertRaises(Exception):
                r.reviewed()

    @unittest.skipUnless(r.OUT.exists(), 'Build reviewed package first')
    def test_restamped_wrong_placement_rejected(self):
        with tempfile.TemporaryDirectory(prefix='crow-r10-test-') as tmp:
            out = Path(tmp) / 'package'
            shutil.copytree(r.OUT, out)
            rows = r.q.read_csv(out / 'carrier-cpl.csv')
            for row in rows:
                if row['Designator'] == 'J1':
                    row['Rotation'] = '0.000000'
            (out / 'carrier-cpl.csv').write_bytes(r.q.csv_bytes(rows))
            self.restamp(out, 'carrier-cpl.csv')
            with self.assertRaisesRegex(Exception, 'Wrong derived table'):
                r.verify(out)

    @unittest.skipUnless(r.OUT.exists(), 'Build reviewed package first')
    def test_restamped_wrong_drill_rejected(self):
        with tempfile.TemporaryDirectory(prefix='crow-r10-test-') as tmp:
            out = Path(tmp) / 'package'
            shutil.copytree(r.OUT, out)
            archive = out / 'carrier-gerbers.zip'
            with zipfile.ZipFile(archive) as reader:
                files = {name: reader.read(name) for name in reader.namelist()}
            files['carrier-PTH.drl'] += b'\nX0Y0\n'
            with zipfile.ZipFile(archive, 'w') as writer:
                for name, data in files.items():
                    writer.writestr(name, data)
            self.restamp(out, 'carrier-gerbers.zip')
            with self.assertRaisesRegex(Exception, 'Fabrication does not reproduce native'):
                r.verify(out)

    def restamp(self, out, name):
        manifest = json.loads((out / 'manifest.json').read_text())
        manifest['files'][name] = r.q.sha(out / name)
        (out / 'manifest.json').write_text(json.dumps(manifest))


if __name__ == '__main__':
    unittest.main()
