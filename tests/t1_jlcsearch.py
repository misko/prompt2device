"""Report-only jlcsearch adapter regressions; all network responses are mocked."""
import importlib.util
import json
import tempfile
import unittest
import urllib.error
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import main, test
SCRIPT = ROOT / "skills/jlcpcb-fab/scripts/jlcsearch.py"
spec = importlib.util.spec_from_file_location("jlcsearch_adapter", SCRIPT)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class Response:
    status = 200

    def __init__(self, data):
        self.data = json.dumps(data).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, limit):
        return self.data[:limit]


class JlcsearchReportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.request = self.base / "request.json"
        self.circuit = self.base / "circuit.json"
        self.request.write_text(json.dumps({"kind": "jlc-pcba-availability-request-v2", "build_quantity": 5,
            "rows": [{"requested_lcsc": "C123", "designators": ["R1"],
                      "per_board_qty": 1, "required_qty": 5},
                     {"requested_lcsc": "C456", "designators": ["R2"],
                      "per_board_qty": 1, "required_qty": 5}]}))
        self.circuit.write_text(json.dumps([
            {"type": "source_component", "name": "R1", "manufacturer_part_number": "EXACT-A",
             "supplier_part_numbers": {"jlcpcb": ["C123"]}},
            {"type": "source_component", "name": "R2", "manufacturer_part_number": "EXACT-B",
             "supplier_part_numbers": {"jlcpcb": ["C456"]}}]))

    def client(self, budget=10):
        return adapter.Client(self.base / "cache", budget, 1)

    def test_exact_identity_and_missing_search_result_keep_denominator(self):
        calls = iter([Response({"components": [
            {"lcsc": 999, "mfr": "EXACT-A", "stock": 1000},
            {"lcsc": 123, "mfr": "WRONG", "stock": 1000}]}),
            Response({"components": []})])
        with patch.object(adapter.urllib.request, "urlopen", side_effect=lambda *_a, **_k: next(calls)):
            report = adapter.screen(self.request, self.circuit, self.client())
        self.assertEqual(report["coverage"], {"total": 2, "catalog_observed": 0, "unknown": 2})
        self.assertTrue(all(r["status"] == "UNKNOWN" for r in report["rows"]))
        self.assertIn("MPN mismatch", report["rows"][0]["reason"])
        self.assertIn("absent from search index", report["rows"][1]["reason"])

    def test_403_stops_further_network_and_reports_unknown(self):
        failure = urllib.error.HTTPError("url", 403, "Forbidden", {}, None)
        with patch.object(adapter.urllib.request, "urlopen", side_effect=failure) as fetch:
            report = adapter.screen(self.request, self.circuit, self.client())
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(report["network_requests"], 1)
        self.assertEqual(report["coverage"]["unknown"], 2)
        self.assertTrue(all(r["observed_stock"] is None for r in report["rows"]))

    def test_valid_exact_record_cache_and_provenance(self):
        client = self.client()
        response = Response({"components": [{"lcsc": 123, "mfr": "EXACT-A", "stock": 9}]})
        with patch.object(adapter.urllib.request, "urlopen", return_value=response) as fetch:
            first = adapter.screen(self.request, self.circuit, client)
            second = adapter.screen(self.request, self.circuit, client)
        self.assertEqual(fetch.call_count, 2)  # C123 and C456, second pass cached
        row = first["rows"][0]
        self.assertEqual(row["status"], "CATALOG_OBSERVED")
        self.assertEqual(row["observed_stock"], 9)
        self.assertEqual(row["evidence"]["raw_response_sha256"], adapter.sha(response.data))
        self.assertIsNone(row["evidence"]["upstream_stock_timestamp"])
        self.assertTrue(second["rows"][0]["evidence"]["cache_hit"])
        self.assertEqual(second["rows"][0]["evidence"]["fetched_at"], row["evidence"]["fetched_at"])

    def test_missing_or_ambiguous_source_mpn_never_queries(self):
        self.circuit.write_text(json.dumps([
            {"type": "source_component", "name": "R1", "manufacturer_part_number": "A",
             "supplier_part_numbers": {"jlcpcb": ["C123"]}},
            {"type": "source_component", "name": "R1", "manufacturer_part_number": "B",
             "supplier_part_numbers": {"jlcpcb": ["C123"]}}]))
        with patch.object(adapter.urllib.request, "urlopen") as fetch:
            report = adapter.screen(self.request, self.circuit, self.client())
        fetch.assert_not_called()
        self.assertEqual(report["coverage"]["unknown"], 2)

    def test_schema_failure_and_budget_are_unknown(self):
        with patch.object(adapter.urllib.request, "urlopen", return_value=Response({"wrong": []})):
            report = adapter.screen(self.request, self.circuit, self.client(budget=1))
        self.assertEqual(report["coverage"]["unknown"], 2)
        self.assertEqual(report["network_requests"], 1)

    def test_cache_wrong_url_and_future_timestamp_are_not_replayed(self):
        client = self.client()
        response = Response({"components": [{"lcsc": 123, "mfr": "EXACT-A", "stock": 9}]})
        with patch.object(adapter.urllib.request, "urlopen", return_value=response):
            client.get("C123")
        cache_file = next((self.base / "cache").glob("*.json"))
        saved = json.loads(cache_file.read_text())
        saved["url"] = "https://example.invalid/swapped"
        cache_file.write_text(json.dumps(saved))
        with patch.object(adapter.urllib.request, "urlopen", return_value=response) as fetch:
            client.get("C123")
        self.assertEqual(fetch.call_count, 1)
        saved = json.loads(cache_file.read_text())
        saved["fetched_at"] = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        cache_file.write_text(json.dumps(saved))
        with patch.object(adapter.urllib.request, "urlopen", return_value=response) as fetch:
            client.get("C123")
        self.assertEqual(fetch.call_count, 1)

    def test_quantity_mismatch_and_duplicate_code_stay_unknown(self):
        request = json.loads(self.request.read_text())
        request["rows"][0]["required_qty"] = 4
        request["rows"][1]["requested_lcsc"] = "C123"
        self.request.write_text(json.dumps(request))
        with patch.object(adapter.urllib.request, "urlopen") as fetch:
            report = adapter.screen(self.request, self.circuit, self.client())
        fetch.assert_not_called()
        self.assertEqual(report["coverage"], {"total": 2, "catalog_observed": 0, "unknown": 2})

    def test_duplicate_exact_or_invalid_stock_is_unknown(self):
        for parts in ([{"lcsc": 123, "mfr": "EXACT-A", "stock": 9}] * 2,
                      [{"lcsc": 123, "mfr": "EXACT-A", "stock": True}],
                      [{"lcsc": 123, "mfr": "EXACT-A", "stock": -1}],
                      [{"lcsc": 123, "mfr": "EXACT-A", "stock": 9.5}]):
            with self.subTest(parts=parts):
                with patch.object(adapter.urllib.request, "urlopen",
                                  return_value=Response({"components": parts})):
                    report = adapter.screen(self.request, self.circuit,
                                            adapter.Client(self.base / ("cache" + str(id(parts))), 1, 1))
                self.assertEqual(report["rows"][0]["status"], "UNKNOWN")

    def test_discovery_empty_is_not_observed(self):
        with patch.object(adapter.urllib.request, "urlopen", return_value=Response({"components": []})):
            report = adapter.discover("nonexistent", self.client())
        self.assertEqual(report["status"], "NOT_OBSERVED")

    def test_duplicate_valid_rows_both_unknown(self):
        request = json.loads(self.request.read_text())
        request["rows"].append(dict(request["rows"][0]))
        self.request.write_text(json.dumps(request))
        with patch.object(adapter.urllib.request, "urlopen", return_value=Response({"components": []})):
            report = adapter.screen(self.request, self.circuit, self.client())
        self.assertEqual(report["coverage"]["total"], 3)
        self.assertEqual(report["rows"][0]["status"], "UNKNOWN")
        self.assertEqual(report["rows"][2]["status"], "UNKNOWN")

    def test_bool_quantities_and_unhashable_refs_are_unknown(self):
        request = json.loads(self.request.read_text())
        request["build_quantity"] = True
        request["rows"][0]["per_board_qty"] = True
        request["rows"][1]["designators"] = [["R2"]]
        self.request.write_text(json.dumps(request))
        with patch.object(adapter.urllib.request, "urlopen") as fetch:
            report = adapter.screen(self.request, self.circuit, self.client())
        fetch.assert_not_called()
        self.assertEqual(report["coverage"]["unknown"], 2)

    def test_conflicting_same_code_catalog_rows_are_unknown(self):
        parts = [{"lcsc": 123, "mfr": "EXACT-A", "stock": 9},
                 {"lcsc": 123, "mfr": "OTHER", "stock": 99}]
        with patch.object(adapter.urllib.request, "urlopen",
                          return_value=Response({"components": parts})):
            report = adapter.screen(self.request, self.circuit, self.client(budget=1))
        self.assertEqual(report["rows"][0]["status"], "UNKNOWN")


for method_name in sorted(name for name in dir(JlcsearchReportTest) if name.startswith("test_")):
    def run_case(name=method_name):
        case = JlcsearchReportTest(name)
        case.setUp()
        try:
            getattr(case, name)()
        finally:
            case.doCleanups()

    test("jlcsearch " + method_name.replace("test_", "").replace("_", " "),
         kind="known_bad" if any(term in method_name for term in (
             "403", "missing", "schema", "duplicate", "invalid",
             "quantity", "conflicting", "cache_wrong")) else "clean")(run_case)


if __name__ == "__main__":
    sys.exit(main())
