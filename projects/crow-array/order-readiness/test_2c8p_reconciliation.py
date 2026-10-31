"""Check quote arithmetic/boundaries, not supplier availability or acceptance."""
import csv
from decimal import Decimal
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
PACKET = ROOT / 'quote-draft/r3-1c8p-home'


def read_rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


class QuoteReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.rows = read_rows(ROOT / 'jlc-2c8p-reconciliation-20261031.csv')
        self.by_mpn = {r['mpn']: r for r in self.rows}

    def test_exact_subjects_and_native_bound_demand(self):
        source = {r['mpn']: r for r in read_rows(PACKET / 'shortage-parts.csv')}
        self.assertEqual(len(self.rows), 6)
        self.assertEqual(set(source), set(self.by_mpn))
        for r in self.rows:
            src = source[r['mpn']]
            self.assertEqual(r['manufacturer'], src['manufacturer'])
            for board, n in [('carrier', 2), ('pod', 8)]:
                per = int(r[f'per_{board}'])
                self.assertEqual(per, int(src[f'per_{board}']))
                self.assertEqual(int(r[f'installed_{board}_{n}']), n * per)
            self.assertEqual(int(r['installed_total']),
                             int(r['installed_carrier_2']) + int(r['installed_pod_8']))

    def test_gross_and_offer_counts_are_not_installed_counts(self):
        for r in self.rows:
            gross = int(r['observed_gross_carrier']) + int(r['observed_gross_pod'])
            self.assertEqual(gross, int(r['observed_gross_total']))
            self.assertGreaterEqual(gross, int(r['installed_total']))
            self.assertGreaterEqual(int(r['global_offer_quantity']), gross)
        self.assertEqual(sum(int(r['installed_total']) for r in self.rows), 54)
        self.assertEqual(sum(int(r['observed_gross_total']) for r in self.rows), 88)
        self.assertEqual(sum(int(r['global_offer_quantity']) for r in self.rows), 96)
        murata = self.by_mpn['GRM21BR71A105KA01L']
        self.assertEqual((murata['observed_gross_carrier'], murata['observed_gross_pod']), ('20', '20'))

    def test_shared_fuse_stock_never_credited_to_global_offer(self):
        fuse = self.by_mpn['1206L010/30WR']
        self.assertEqual(fuse['public_pool_seen'], '7')
        self.assertEqual(fuse['observed_gross_total'], '28')
        self.assertEqual(28 - int(fuse['public_pool_seen']), 21)
        for r in self.rows:
            self.assertEqual(r['credited_to_global_plan'], '0')

    def test_prices_and_unknowns_remain_separate(self):
        self.assertEqual(sum(Decimal(r['global_offer_usd']) for r in self.rows), Decimal('87.58'))
        self.assertEqual(sum(Decimal(r['regular_offer_usd']) for r in self.rows
                             if r['regular_offer_usd']), Decimal('36.54'))
        for r in self.rows:
            self.assertNotIn(None, r)  # Reject malformed CSV extra columns.
            for field in ['final_purchase_quantity', 'final_fees_usd', 'usable_stock_date']:
                self.assertEqual(r[field], '')
        self.assertNotIn('PCM1864DBTR', self.by_mpn)

    def test_complete_smt_and_home_scope(self):
        parts = read_rows(PACKET / 'procurement-plan.csv')
        smt = [r for r in parts if r['owner'] == 'JLC_SMT']
        home = [r for r in parts if r['owner'] == 'HOME']
        self.assertEqual(len(smt), 32)
        self.assertEqual(sum(2 * int(r['per_carrier']) + 8 * int(r['per_pod']) for r in smt), 478)
        self.assertEqual(478 - sum(int(r['installed_total']) for r in self.rows), 424)
        self.assertEqual(sum(int(r['per_carrier']) + 8 * int(r['per_pod']) for r in home), 35)


if __name__ == '__main__':
    unittest.main()
