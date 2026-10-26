import csv
import json
from pathlib import Path
import unittest

from exact_stock_recovery import product_offers, ROOT


def page(**changes):
    product = {'@type': 'Product', 'mpn': 'EXACT-7-F', 'sku': 'C123',
               'brand': {'name': 'Maker'},
               'offers': {'availability': 'https://schema.org/InStock'}}
    product.update(changes)
    return '<script type="application/ld+json">' + json.dumps(product) + '</script>'


class EvidenceTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertEqual(len(product_offers(page(), 'EXACT-7-F', 'C123')), 1)

    def test_suffix_and_code_not_normalized(self):
        self.assertEqual(product_offers(page(), 'EXACT-13-F', 'C123'), [])
        self.assertEqual(product_offers(page(), 'EXACT-7-F', 'C124'), [])

    def test_navigation_and_nonproduct_ignored(self):
        self.assertEqual(product_offers('In Stock Parts', 'EXACT-7-F'), [])
        self.assertEqual(product_offers(page(**{'@type': 'BreadcrumbList'}), 'EXACT-7-F'), [])

    def test_unknown_quantity_is_not_invented(self):
        offer = product_offers(page(), 'EXACT-7-F')[0]['offers']
        self.assertNotIn('inventoryLevel', offer)

    def test_zero_and_outofstock_preserved(self):
        offer = {'availability': 'https://schema.org/OutOfStock', 'inventoryLevel': 0}
        self.assertEqual(product_offers(page(offers=offer), 'EXACT-7-F')[0]['offers'], offer)

    def test_malformed_ignored(self):
        self.assertEqual(product_offers('<script type="application/ld+json">bad</script>', 'EXACT-7-F'), [])

    def test_retained_recovery_matches_sealed_demand(self):
        release = ROOT.parent / 'releases/crow-prototype-v3-first-run-5c10p-public-v1'
        with (release / 'fab/assembly/demand.csv').open() as f:
            demand = {r['mpn']: int(r['quantity']) for r in csv.DictReader(f)}
        records = json.loads((ROOT / 'code-stock-recovery-20261026.json').read_text())
        self.assertEqual(len(records), 6)
        for r in records:
            self.assertEqual(r['installed_need'], demand[r['mpn']])
            for p in r['supplier'].get('exact_product_offers', []):
                self.assertEqual(p['mpn'], r['mpn'])
                self.assertEqual(p['sku'], r['code'])

    def test_buerklin_offer_and_count_bind_to_same_exact_product(self):
        r = json.loads((ROOT / 'buerklin-20261026.json').read_text())
        release = ROOT.parent / 'releases/crow-prototype-v3-first-run-5c10p-public-v1'
        with (release / 'fab/assembly/demand.csv').open() as f:
            demand = {row['mpn']: int(row['quantity']) for row in csv.DictReader(f)}
        self.assertEqual(r['installed_need'], demand[r['mpn']])
        self.assertTrue(r['exact_product_offers'])
        for p in r['exact_product_offers']:
            self.assertEqual(p['mpn'], r['mpn'])
            self.assertEqual(p['sku'], r['bound_page_product']['id'])
            self.assertEqual(p['brand']['name'], r['bound_page_product']['brand'])
        self.assertIn(r['mpn'], r['bound_page_product']['name'])
        self.assertGreaterEqual(r['bound_page_product']['stock'], r['installed_need'])


if __name__ == '__main__':
    unittest.main()
