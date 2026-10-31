"""Evidence/quantity accounting for a proposal; never purchasing admission."""
import csv
import json
from decimal import Decimal
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


class ProcurementProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def rows(name):
            with (ROOT / name).open(newline='') as stream:
                return list(csv.DictReader(stream))
        cls.rows = rows('procurement-proposal-20261030.csv')
        cls.source = {r['mpn']: r for r in rows('procurement-map-20261026-v3.csv')}
        cls.pricing = {r['mpn']: r for r in json.loads(
            (ROOT / 'JLC-PRICING-20261030.json').read_text())['rows']}
        cls.browser = {r['requested_mpn']: r for r in json.loads(
            (ROOT / 'JLC-BROWSER-20261030.json').read_text())['observations']}

    def test_all_exact_identities_and_board_quantities(self):
        self.assertEqual(len(self.rows), 38)
        self.assertEqual({r['mpn'] for r in self.rows}, set(self.source))
        for r in self.rows:
            s = self.source[r['mpn']]
            self.assertEqual(r['manufacturer'], s['manufacturer'])
            for board, count in [('carrier', 5), ('pod', 10)]:
                refs = s[board + '_refs']
                self.assertEqual(r[board + '_refs'], refs)
                self.assertEqual(int(r[board + '_batch_need']),
                                 count * (len(refs.split(';')) if refs else 0))
            self.assertEqual(int(r['installed_need']),
                             int(r['carrier_batch_need']) + int(r['pod_batch_need']))
            self.assertEqual(r['installed_need'], s['installed_need'])
        self.assertEqual(sum(int(r['installed_need']) for r in self.rows), 1000)

    def test_route_and_installation_ownership(self):
        expected = {'JLC_catalog': (28, 865), 'JLC_regular_replenishment': (5, 95),
                    'JLC_Global_Sourcing': (2, 15), 'external_for_user_installation': (3, 25)}
        for route, (identities, units) in expected.items():
            selected = [r for r in self.rows if r['proposed_supply_route'] == route]
            self.assertEqual(len(selected), identities)
            self.assertEqual(sum(int(r['installed_need']) for r in selected), units)
        for owner, units in [('JLC_SMT_requested', 915), ('JLC_manual_requested', 60), ('user', 25)]:
            self.assertEqual(sum(int(r['installed_need']) for r in self.rows
                                 if r['assembly_owner'] == owner), units)
        self.assertEqual({r['mpn'] for r in self.rows if r['assembly_owner'] == 'user'},
                         {'SC0915', 'CMA-4544PF-W', 'CPE-203'})

    def test_observed_pricing_not_unavailable_catalog_price(self):
        priced = [r for r in self.rows if r['indicative_line_usd']]
        self.assertEqual({r['mpn'] for r in priced}, set(self.pricing))
        for r in priced:
            p = self.pricing[r['mpn']]
            self.assertEqual(int(r['installed_need']), p['installed_need'])
            self.assertEqual(r['catalog_code'], p['code'])
            if r['proposed_supply_route'] == 'JLC_regular_replenishment':
                self.assertEqual(r['indicative_line_usd'], p['regular_extended_usd'].removeprefix('$'))
                self.assertEqual(int(r['provisional_purchase_quantity']), p['illustrative_quantity'])
            else:
                self.assertIn('Unavailable', p['regular_extended_usd'])
                self.assertIn('10 at $' + r['indicative_line_usd'], p['global_observation'])
                self.assertEqual(r['provisional_purchase_quantity'], '10')
        self.assertEqual(sum(Decimal(r['indicative_line_usd']) for r in priced), Decimal('227.71'))
        self.assertEqual(sum(int(r['provisional_purchase_quantity']) for r in priced), 558)
        self.assertEqual({r['mpn'] for r in priced if r['proposed_supply_route'] == 'JLC_Global_Sourcing'},
                         {'R-78E5.0-0.5', 'PCM1864DBT'})

    def test_unknowns_and_source_binding_not_order_approval(self):
        for r in self.rows:
            self.assertEqual(r['authority'], 'PROPOSAL_ONLY_NO_PURCHASE')
            self.assertEqual(r['usable_JLC_arrival'], 'unknown')
            if r['mpn'] not in self.pricing:
                self.assertEqual(r['indicative_line_usd'], '')
                self.assertEqual(r['provisional_purchase_quantity'], '')
            if r['mpn'] in self.browser:
                self.assertEqual(r['catalog_code'], self.browser[r['mpn']]['catalog_code'])
            if r['proposed_supply_route'] == 'JLC_Global_Sourcing':
                self.assertIn('endpoint unconfirmed', r['displayed_lead_time'])


if __name__ == '__main__':
    unittest.main()
