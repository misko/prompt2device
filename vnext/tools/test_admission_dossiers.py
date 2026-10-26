"""Part identity/path regressions; these do not grade engineering evidence."""
import csv
import tempfile
import unittest
from pathlib import Path

import admission


class DossierPaths(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.table = self.root / '01_docs/sourcing/exact-parts.csv'
        self.table.parent.mkdir(parents=True)
        self.folder = self.root / '02_parts/ss14'
        self.folder.mkdir(parents=True)
        (self.folder / 'part.yaml').write_text('mpn: SS14-E3/61T\n')
        (self.folder / 'datasheet.pdf').write_bytes(b'Synthetic PDF evidence, not a datasheet')
        self.subjects = {
            '02_parts/ss14/part.yaml': 'test hash',
            '02_parts/ss14/datasheet.pdf': 'test hash',
            '01_docs/decisions/sourcing.md': 'test hash',
        }

    def tearDown(self):
        self.temp.cleanup()

    def write_table(self, mpn='SS14-E3/61T', dossier='02_parts/ss14/part.yaml'):
        with self.table.open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['MPN'] if dossier is None else ['MPN', 'Dossier'])
            writer.writerow([mpn] if dossier is None else [mpn, dossier])

    def test_exact_slash_mpn_with_explicit_dossier(self):
        self.write_table()
        admission.check_sourcing(self.root, self.subjects)
        self.assertIn('SS14-E3/61T', self.table.read_text())

    def test_legacy_safe_name_still_works(self):
        self.write_table(mpn='ss14', dossier=None)
        admission.check_sourcing(self.root, self.subjects)

    def test_slash_without_mapping_is_not_interpreted_as_path(self):
        self.write_table(dossier=None)
        with self.assertRaisesRegex(admission.AdmissionError, 'explicit Dossier'):
            admission.check_sourcing(self.root, self.subjects)

    def test_missing_dossier_or_datasheet_remains_rejected(self):
        self.write_table()
        for path in ('02_parts/ss14/part.yaml', '02_parts/ss14/datasheet.pdf'):
            subjects = dict(self.subjects)
            del subjects[path]
            with self.assertRaises(admission.AdmissionError):
                admission.check_sourcing(self.root, subjects)

    def test_blank_escaping_or_nonparts_dossier_rejected(self):
        for path in ('', '../02_parts/ss14/part.yaml', '/tmp/part.yaml',
                     '02_parts/../02_parts/ss14/part.yaml', '01_docs/part.yaml',
                     '02_parts/ss14\\part.yaml'):
            with self.subTest(path=path):
                self.write_table(dossier=path)
                with self.assertRaises(admission.AdmissionError):
                    admission.check_sourcing(self.root, self.subjects)

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            outside = Path(elsewhere) / 'part.yaml'
            outside.write_text('outside project\n')
            (self.root / '02_parts/escape').symlink_to(Path(elsewhere), target_is_directory=True)
            self.write_table(dossier='02_parts/escape/part.yaml')
            with self.assertRaises(admission.AdmissionError):
                admission.check_sourcing(self.root, self.subjects)


if __name__ == '__main__':
    unittest.main()
