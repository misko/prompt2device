import json
import unittest

from stock_lookup import discover, lookup, public_evidence
from part_recheck import evaluate


class StockLookupTests(unittest.TestCase):
    def test_exact_suffix_and_quantity(self):
        result = discover({"components": [
            {"mfr": "TPS3700DDCR2", "stock": 999},
            {"mfr": "TPS3700DDCR", "stock": 40, "package": "SOT-23-6"},
        ]}, "TPS3700DDCR", 40)
        self.assertEqual(len(result["matches"]), 1)
        self.assertEqual(result["matches"][0]["status"], "reported_sufficient")
        self.assertIsNone(result["matches"][0]["manufacturer"])

    def test_empty_is_not_zero_stock(self):
        self.assertEqual(discover({"components": []}, "X", 5)["lookup_state"], "no_exact_match")

    def test_live_failure_replay_unrelated_component(self):
        payload = {"components": [{"mfr": "BZX55C43V", "stock": 3500}]}
        self.assertEqual(discover(payload, "TPSM82822ASILR", 5)["matches"], [])

    def test_stock_outcomes(self):
        for count, status in [(0, "reported_out_of_stock"), (3, "reported_insufficient"),
                              (None, "stock_unknown"), (True, "stock_unknown"),
                              (-1, "stock_unknown"), ("50", "stock_unknown")]:
            with self.subTest(count=count):
                self.assertEqual(discover({"components": [{"mfr": "X", "stock": count}]},
                                          "X", 5)["matches"][0]["status"], status)

    def test_timeout_is_lookup_failure(self):
        def failed(_):
            raise TimeoutError("offline")
        result = lookup("X", 5, getter=failed)
        self.assertEqual(result["lookup_state"], "lookup_failed")
        self.assertEqual(result["sourcing_guard"], "provisional")

    def test_malformed_response(self):
        for body in ["<html>error</html>", '{}', '{"components":[null]}']:
            result = lookup("X", 5, getter=lambda _: (body, {}))
            self.assertEqual(result["lookup_state"], "lookup_failed")

    def test_snapshot_never_automatically_admits(self):
        result = lookup("X", 5, getter=lambda _: ('{"components":[{"mfr":"X","stock":50}]}', {}))
        self.assertEqual(result["sourcing_guard"], "provisional")
        self.assertIsNone(result["inventory_updated_at"])

    def test_public_page_ignores_recommendations_and_generic_stock(self):
        payload = '1:{"componentInfo":{"componentModelEn":"X2","stockCount":99}}'
        html = 'In Stock' + '<script>self.__next_f.push(' + json.dumps([1, payload]) + ')</script>'
        self.assertEqual(public_evidence(html, "X")["lookup_state"], "no_exact_evidence")

    def test_public_page_preserves_inventory_pool_not_admission(self):
        payload = '1:{"componentInfo":{"componentModelEn":"X","overseasStockCount":500}}'
        html = '<script>self.__next_f.push(' + json.dumps([1, payload]) + ')</script>'
        result = public_evidence(html, "X")
        self.assertFalse(result["availability_verified"])
        self.assertEqual(result["observations"][0]["overseasStockCount"], 500)
        self.assertNotIn("stockCount", result["observations"][0])

    def test_public_page_code_mismatch_rejected(self):
        payload = '1:{"componentInfo":{"componentModelEn":"X","componentCode":"C2","stockCount":500}}'
        html = '<script>self.__next_f.push(' + json.dumps([1, payload]) + ')</script>'
        self.assertEqual(public_evidence(html, "X", "C1")["lookup_state"], "no_exact_evidence")

    def test_untrusted_public_url_rejected(self):
        with self.assertRaises(ValueError):
            lookup("X", 5, "https://example.com/partdetail/X", getter=lambda _: ('{"components":[]}', {}))


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.subject = dict(manufacturer="TI", mpn="X", package="P", quantity_per_assembly=1, assembly_count=5)
        self.offer = dict(manufacturer="TI", mpn="X", package="P", supplier_url="https://jlcpcb.com/partdetail/X",
                          checked_on="2026-10-02", in_stock=True, stock_count=None)

    def check(self, offers, **extra):
        return evaluate(dict(part_id="x", subject=self.subject, check=dict(subject=self.subject,
            jlc_checked=True, western_search_complete=True, offers=offers, **extra)))

    def test_explicit_in_stock_unknown_count_still_passes(self):
        self.assertEqual(self.check([self.offer])["state"], "checked")

    def test_insufficient_known_count_overrides_badge(self):
        self.assertEqual(self.check([{**self.offer, "stock_count": 3}])["state"], "needs_user_decision")

    def test_weak_offer_never_passes(self):
        for kind in ["aggregate_snapshot", "search_snippet"]:
            self.assertNotEqual(self.check([{**self.offer, "evidence_kind": kind}])["state"], "checked")
            self.assertNotEqual(self.check([{**self.offer, "source_kind": kind}])["state"], "checked")

    def test_failed_or_stale_search_is_not_shortage(self):
        for issue in ["lookup_failed", "stale", "no_exact_match", "inventory_unverified"]:
            result = self.check([], lookup_issue=issue)
            self.assertEqual(result["state"], "provisional")
            self.assertEqual(result["next_action"], "resolve_lookup_evidence")
            self.assertNotEqual(self.check([{**self.offer, "lookup_state": issue}])["state"], "checked")

    def test_good_independent_offer_resolves_lookup_failure(self):
        self.assertEqual(self.check([self.offer], lookup_issue="lookup_failed")["state"], "checked")

    def test_explicit_unverified_public_evidence_cannot_pass(self):
        for fields in [{"availability_verified": False}, {"lookup_state": "no_exact_evidence"}]:
            self.assertNotEqual(self.check([{**self.offer, **fields}])["state"], "checked")


if __name__ == "__main__":
    unittest.main()
