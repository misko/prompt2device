import contextlib
import csv
import io
import tempfile
import unittest
from pathlib import Path

from catalog_mapping import ROOT, build, disposition, stock_state


class CatalogMappingTests(unittest.TestCase):
    def test_insufficient_count_overrides_instock(self):
        self.assertEqual(stock_state({'availability': 'https://schema.org/InStock',
                                      'inventoryLevel': 13}, 50), 'insufficient')

    def test_unknown_quantity_stays_unknown(self):
        self.assertEqual(stock_state({'availability': 'http://schema.org/InStock'}, 50),
                         'in_stock_quantity_unknown')

    def test_inventory_pool_fields_not_added(self):
        self.assertEqual(stock_state({'overseasStockCount': 100, 'canPresaleNumber': 100}, 5), 'unknown')

    def test_conflicting_badge_is_not_positive(self):
        self.assertEqual(stock_state({'availability': 'http://schema.org/OutOfStock',
                                      'inventoryLevel': 100}, 5), 'conflicting')

    def test_same_mpn_wrong_manufacturer_rejected(self):
        subject = dict(manufacturer='RECOM Power', mpn='R-78E5.0-0.5', quantity=5)
        obs = dict(code='C1', supplier=dict(exact_product_offers=[dict(
            mpn=subject['mpn'], sku='C1', brand={'name': 'EVISUN'},
            offers={'availability': 'https://schema.org/InStock'})]))
        self.assertEqual(disposition(subject, obs)[0], 'identity_or_lookup_pending')
        obs['supplier']['exact_product_offers'][0]['brand']['name'] = 'Recom Power'
        self.assertEqual(disposition(subject, obs)[0], 'exact_maker_mpn_code')
        obs['supplier']['exact_product_offers'][0]['mpn'] += '-ALT'
        self.assertEqual(disposition(subject, obs)[0], 'identity_or_lookup_pending')

    def test_project_coverage_manual_separation_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='crow-map-test-') as d:
            output = Path(d) / 'map.csv'
            with contextlib.redirect_stdout(io.StringIO()):
                build(ROOT / 'catalog-observations-20261026.json', output)
            with output.open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 38)
            self.assertEqual(sum(int(r['installed_need']) for r in rows), 1000)
            manual = [r for r in rows if r['population_mode'] == 'manual']
            self.assertEqual(sum(int(r['installed_need']) for r in manual), 85)
            expected = {'user_pico_installation': 5, 'user_acoustic_hand_solder': 20,
                        'jlc_manual_requested_pending_acceptance': 60}
            self.assertEqual({r['proposed_route'] for r in manual}, set(expected))
            for route, count in expected.items():
                self.assertEqual(sum(int(r['installed_need']) for r in manual
                                     if r['proposed_route'] == route), count)
            self.assertTrue(all(r['population_mode'] == 'manual' for r in rows
                                if r['proposed_route'] in expected))
            self.assertIn('buerklin.com', next(r for r in rows if r['mpn']=='C3216X7R1V106K160AC')['fallback_url'])
            with self.assertRaises(ValueError):
                build(ROOT / 'catalog-observations-20261026.json', output)


if __name__ == '__main__':
    unittest.main()
