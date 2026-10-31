"""Bind the returned browser transcription to its immutable task inputs."""
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


class BrowserEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((ROOT / 'JLC-BROWSER-20261030.json').read_text())
        cls.rows = cls.record['observations']
        with (ROOT / cls.record['worksheet']).open(newline='') as stream:
            cls.worksheet = list(csv.DictReader(stream))

    def test_exact_input_hash(self):
        self.assertEqual(hashlib.sha256((ROOT / self.record['worksheet']).read_bytes()).hexdigest(),
                         self.record['worksheet_sha256'])

    def test_complete_unique_subject_and_reference_binding(self):
        expected = {(r['manufacturer'], r['mpn']): r for r in self.worksheet
                    if not r['proposed_route'].startswith('user_')}
        actual = {(r['requested_manufacturer'], r['requested_mpn']): r for r in self.rows}
        self.assertEqual(len(self.rows), 35)
        self.assertEqual(len(actual), len(self.rows))
        self.assertEqual(set(actual), set(expected))
        for key, row in actual.items():
            source = expected[key]
            self.assertEqual(row['installed_need'], int(source['installed_need']))
            for field in ('carrier_refs', 'pod_refs', 'population_mode', 'native_footprints'):
                self.assertEqual(row[field], source[field])
        self.assertEqual(sum(r['installed_need'] for r in self.rows), 975)

    def test_classifications_and_separate_pool_arithmetic(self):
        self.assertEqual(Counter(r['result'] for r in self.rows), {
            'jlc_orderable_sufficient': 26, 'jlc_insufficient_or_zero': 7,
            'identity_review_stock_sufficient': 2})
        for row in self.rows:
            if row['result'] == 'jlc_insufficient_or_zero':
                self.assertLess(row['in_stock_count'], row['installed_need'])
            else:
                self.assertGreaterEqual(row['available_order_quantity'], row['installed_need'])
            if row['result'] == 'jlc_orderable_sufficient':
                self.assertEqual(row['requested_mpn'], row['catalog_mpn'])

    def test_manual_ownership_and_unknown_lead_times_preserved(self):
        manual = [r for r in self.rows if r['population_mode'] == 'manual']
        self.assertEqual({r['requested_mpn'] for r in manual},
                         {'RJHSE-5080', 'PJ-102AH', 'R-78E5.0-0.5'})
        self.assertEqual(sum(r['installed_need'] for r in manual), 60)
        self.assertTrue(all(r['lead_time'] is None for r in self.rows))


if __name__ == '__main__':
    unittest.main()
