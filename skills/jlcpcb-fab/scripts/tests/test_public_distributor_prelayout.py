"""Design-only public distributor admission; never an allocation receipt."""
import copy
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manufacturing_readiness as mr


class DistributorPrelayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.directive = 'Continue design using exact distributor stock; no purchases.'
        (self.project / 'brief.md').write_text(self.directive)
        (self.project / 'decision.md').write_text(
            self.directive + '\npublic-catalog pre-layout DO-NOT-ORDER')
        self.policy = self.project / 'policy.yaml'
        self.quotes = self.project / 'quotes.yaml'
        self.dossier = self.project / 'part.yaml'
        self.dossier.write_text(yaml.safe_dump({
            'mpn': 'EXACT#TR', 'manufacturer': 'Maker', 'footprint': 'Lib:DFN'}))
        self.row = dict(lcsc='C123', mpn='EXACT#TR', manufacturer='Maker',
                        footprint='Lib:DFN', designators=['U1'], distributor='digikey',
                        url='https://www.digikey.com/en/products/detail/maker/exact/123',
                        packaging='Cut Tape')
        self.p = dict(schema=1, scope='prelayout-only', order_authorized=False,
                      directive=self.directive, brief='brief.md', decision='decision.md',
                      rows=[copy.deepcopy(self.row)])
        self.q = dict(quotes=[dict(mpn='EXACT#TR', manufacturer='Maker',
            distributor='digikey', url=self.row['url'], packaging='Cut Tape',
            dpn='EXACTCT-ND', source='product_page', lifecycle='Active', stock=20,
            min=1, mult=1, checked_at=datetime.now(timezone.utc).isoformat())])
        self.request = dict(rows=[dict(requested_lcsc='C123', designators=['U1'],
                                      per_board_qty=1, required_qty=5)])
        self.exact = [dict(ref='U1', mpn='EXACT#TR', jlc_codes=['C123'],
                           footprint='Lib:DFN', dossier=str(self.dossier))]

    def grade(self, *, allow_blocked_sourcing=False):
        self.policy.write_text(yaml.safe_dump(self.p))
        self.quotes.write_text(yaml.safe_dump(self.q))
        return mr._distributor_prelayout_rows(
            self.project, self.request, self.policy, self.quotes, self.exact,
            allow_blocked_sourcing=allow_blocked_sourcing)

    def test_fresh_zero_stock_is_only_admitted_by_explicit_blocked_sourcing(self):
        self.q['quotes'][0]['stock'] = 0
        with self.assertRaisesRegex(ValueError, 'below actual'):
            self.grade()
        self.policy.write_text(yaml.safe_dump(self.p))
        self.quotes.write_text(yaml.safe_dump(self.q))
        rows, _ = mr._distributor_prelayout_rows(
            self.project, self.request, self.policy, self.quotes, self.exact,
            allow_blocked_sourcing=True)
        self.assertEqual('BLOCKED-SOURCING', rows['C123']['sourcing_state'])

        request = self.project / 'request.json'
        evidence = self.project / 'catalog.json'
        request.write_text(json.dumps(dict(self.request, schema=2, phase='prelayout', build_quantity=5)))
        evidence.write_text(json.dumps(dict(
            tool='jlc_stock_check.py', stock_source='lcsc_catalog_stockCount',
            generated_at=datetime.now(timezone.utc).isoformat(), min_stock_per_board=5,
            verdict='FAIL', predicts_jlc_assembly_allocation=False,
            graded_lines=1, total_lines=1, failures=1, uncoded_lines=0,
            lines=[dict(lcsc='C123', designators='U1', qty=1, required_qty=5,
                        stock_threshold=5, absolute_surplus=-5, stock=0,
                        status='LOW_STOCK(0)')])))
        result = mr._catalog_prelayout_check(
            request, evidence, self.project / 'decision.md', distributors=rows,
            allow_blocked_sourcing=True)
        self.assertEqual('PASS', result['status'])
        self.assertEqual('BLOCKED-SOURCING', result['sourcing_state'])
        catalog_only = mr._catalog_prelayout_check(
            request, evidence, self.project / 'decision.md', distributors={},
            allow_blocked_sourcing=True)
        self.assertEqual('PASS', catalog_only['status'])
        self.assertEqual('BLOCKED-SOURCING', catalog_only['sourcing_state'])
        hostile = json.loads(evidence.read_text())
        hostile['lines'][0]['status'] = 'QUERY_FAILED'
        evidence.write_text(json.dumps(hostile))
        self.assertEqual('FAIL', mr._catalog_prelayout_check(
            request, evidence, self.project / 'decision.md', distributors={},
            allow_blocked_sourcing=True)['status'])
        with self.assertRaisesRegex(ValueError, 'public prelayout'):
            mr.grade(self.project, phase='selection',
                     distributor_policy=self.policy,
                     distributor_quotes=self.quotes,
                     allow_blocked_sourcing=True)

    def test_exact_public_observation_is_design_only(self):
        # Measured RED before introducing the explicit distributor path.
        rows, inputs = self.grade()
        self.assertEqual({'C123'}, set(rows))
        self.assertEqual(20, rows['C123']['stock'])
        self.assertIn('distributor_policy', inputs)
        self.assertIn('distributor_quotes', inputs)
        self.assertIn('distributor_decision', inputs)

    def test_exact_mouser_product_page_is_admitted_and_lookalikes_fail(self):
        url = 'https://www.mouser.com/en/ProductDetail/Maker/EXACTTR'
        self.p['rows'][0].update(distributor='mouser', url=url)
        self.q['quotes'][0].update(distributor='mouser', url=url, dpn='123-EXACTTR')
        rows, _ = self.grade()
        self.assertEqual({'C123'}, set(rows))
        for hostile in (
                'http://www.mouser.com/en/ProductDetail/Maker/EXACTTR',
                'https://mouser.com/en/ProductDetail/Maker/EXACTTR',
                'https://www.mouser.com/en/ProductDetail/',
                'https://www.mouser.com/en/ProductDetail/Maker/EXACTTR?claim=1',
                'https://www.mouser.com/en/products/detail/Maker/EXACTTR'):
            self.p['rows'][0]['url'] = hostile
            self.q['quotes'][0]['url'] = hostile
            with self.subTest(url=hostile), self.assertRaisesRegex(ValueError, 'unsupported'):
                self.grade()

    def test_cli_paths_are_cwd_relative_but_policy_references_are_project_relative(self):
        expected = self.grade()
        with patch('os.getcwd', return_value=str(self.project.parent)):
            actual = mr._distributor_prelayout_rows(
                self.project, self.request,
                Path(self.project.name) / 'policy.yaml',
                Path(self.project.name) / 'quotes.yaml', self.exact)
        self.assertEqual(expected, actual)

    def test_unapproved_wrong_stale_or_insufficient_observations_fail(self):
        good_p, good_q, good_exact = copy.deepcopy((self.p, self.q, self.exact))
        mutations = [
            lambda: self.p.update(order_authorized=True),
            lambda: self.p.update(scope='order'),
            lambda: self.p.update(directive='unapproved instruction'),
            lambda: self.p.update(rows=[]),
            lambda: self.p['rows'].append(copy.deepcopy(self.row)),
            lambda: self.p['rows'][0].update(designators=['U2']),
            lambda: self.p['rows'][0].update(mpn='NEAR#TR'),
            lambda: self.p['rows'][0].update(footprint='Lib:OTHER'),
            lambda: self.p['rows'][0].update(manufacturer='Other Maker'),
            lambda: self.q['quotes'][0].update(stock=4),
            lambda: self.q['quotes'][0].update(stock=True),
            lambda: self.q['quotes'][0].update(stock=20.5),
            lambda: self.q['quotes'][0].update(min=2500),
            lambda: self.q['quotes'][0].update(mult=0),
            lambda: self.q['quotes'][0].update(checked_at='2020-01-01T00:00:00Z'),
            lambda: self.q['quotes'][0].update(checked_at='2099-01-01T00:00:00Z'),
            lambda: self.q['quotes'][0].update(checked_at='2026-09-10'),
            lambda: self.q['quotes'][0].update(source='search_snippet'),
            lambda: self.q['quotes'][0].update(lifecycle='Obsolete'),
            lambda: self.q['quotes'][0].update(packaging='Full Reel'),
            lambda: self.q['quotes'][0].update(url='https://example.com/claim'),
            lambda: self.q['quotes'][0].update(mpn='EXACT#PBF'),
            lambda: self.q['quotes'].append(copy.deepcopy(self.q['quotes'][0])),
            lambda: self.exact[0].update(mpn='WRONG'),
            lambda: self.exact[0].update(footprint='Lib:OTHER'),
        ]
        for mutate in mutations:
            self.p, self.q, self.exact = copy.deepcopy((good_p, good_q, good_exact))
            mutate()
            with self.subTest(policy=self.p, quote=self.q):
                with self.assertRaises(ValueError):
                    self.grade()

    def test_public_path_cannot_be_used_for_order_or_selection(self):
        self.grade()
        for phase in ('selection', 'order'):
            with self.subTest(phase=phase), self.assertRaisesRegex(ValueError, 'prelayout'):
                mr.grade(self.project, phase=phase, distributor_policy=self.policy,
                         distributor_quotes=self.quotes)

    def test_composition_keeps_original_jlc_failure_and_rejects_other_failures(self):
        distributors, _ = self.grade()
        request = self.project / 'request.json'
        evidence = self.project / 'catalog.json'
        request.write_text(json.dumps(dict(self.request, schema=2, phase='prelayout', build_quantity=5)))
        raw = dict(tool='jlc_stock_check.py', stock_source='lcsc_catalog_stockCount',
                   generated_at=datetime.now(timezone.utc).isoformat(),
                   min_stock_per_board=5, verdict='FAIL', predicts_jlc_assembly_allocation=False,
                   graded_lines=1, total_lines=1, failures=1, uncoded_lines=0,
                   lines=[dict(lcsc='C123', designators='U1', qty=1, required_qty=5,
                               stock_threshold=5, absolute_surplus=-5, stock=0,
                               status='LOW_STOCK(0)')])
        def check(payload, supplements=distributors):
            evidence.write_text(json.dumps(payload))
            before = evidence.read_bytes()
            result = mr._catalog_prelayout_check(request, evidence, self.project / 'decision.md',
                                                 distributors=supplements)
            self.assertEqual(before, evidence.read_bytes())
            return result
        self.assertEqual('FAIL', check(raw, {})['status'])
        result = check(raw)
        self.assertEqual('PASS', result['status'])
        self.assertEqual({'C123'}, set(result['distributor_rows']))
        bad_rows = [dict(status='QUERY_FAILED'), dict(status='NOT_FOUND'),
                    dict(designators='U2'), dict(required_qty=4), dict(qty=2),
                    dict(stock_threshold=0), dict(absolute_surplus=0),
                    dict(stock=20), dict(status='LOW_STOCK(5)')]
        for mutation in bad_rows:
            hostile = copy.deepcopy(raw)
            hostile['lines'][0].update(mutation)
            with self.subTest(mutation=mutation):
                self.assertEqual('FAIL', check(hostile)['status'])
        for mutation in (dict(verdict='PASS'), dict(failures=0), dict(graded_lines=0),
                         dict(predicts_jlc_assembly_allocation=True), dict(lines=[])):
            hostile = dict(raw, **mutation)
            with self.subTest(mutation=mutation):
                self.assertEqual('FAIL', check(hostile)['status'])
        healthy = copy.deepcopy(raw)
        healthy.update(verdict='PASS', failures=0)
        healthy['lines'][0].update(stock=20, absolute_surplus=15, status='OK')
        self.assertEqual('PASS', check(healthy, {})['status'])


if __name__ == '__main__':
    unittest.main()
