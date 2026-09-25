#!/usr/bin/env python3
"""Tests for staged manufacturing-readiness composition."""
import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import manufacturing_readiness as mr  # noqa: E402


class ManufacturingReadinessTest(unittest.TestCase):
    def test_selection_precedes_jlc_prelayout_receipt(self):
        """Part/value freeze must be reachable before a JLC request exists."""
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            circuit = project / "03_tscircuit/build/circuit.json"
            circuit.parent.mkdir(parents=True)
            circuit.write_text(json.dumps([]), encoding="utf-8")
            assembly = project / "03_src/rules/assembly.yaml"
            assembly.parent.mkdir(parents=True)
            assembly.write_text("build_quantity: 5\n", encoding="utf-8")
            (project / "02_parts").mkdir()

            with patch.object(mr, "_run", return_value={
                    "status": "PASS", "detail": "test", "output": ""}), \
                 patch.object(mr, "_pcba_check") as pcba_check:
                result = mr.grade(project, phase="selection")

            self.assertEqual(result["verdict"], "ACCEPTED")
            self.assertEqual(result["coverage"], {"passing": 2, "total": 2})
            self.assertNotIn("jlc_pcba_availability", result["checks"])
            self.assertNotIn("procurement_exposure", result["checks"])
            pcba_check.assert_not_called()

    def test_pinned_initial_full_catalog_stays_pre_layout_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            request_path = project / "request.json"
            evidence_path = project / "stock.json"
            decision_path = project / "decision.md"
            decision_path.write_text("public-catalog pre-layout DO-NOT-ORDER")
            request_rows = []
            stock_rows = []
            exact_rows = []
            for index in range(88):
                code, ref, mpn = f"C{1000 + index}", f"U{index + 1}", f"PART-{index}"
                request_rows.append(dict(requested_lcsc=code, designators=[ref],
                                         per_board_qty=1, required_qty=5))
                stock_rows.append(dict(lcsc=code, mpn=mpn, designators=ref, qty=1,
                                       required_qty=5, stock_threshold=155,
                                       absolute_surplus=195, stock=200, status="OK"))
                exact_rows.append(dict(ref=ref, mpn=mpn, jlc_codes=[code]))
            request = dict(schema=2, phase="prelayout", build_quantity=5,
                           rows=request_rows)
            evidence = dict(tool="jlc_stock_check.py",
                            stock_source="lcsc_catalog_stockCount",
                            generated_at="2026-01-01T12:00:00Z",
                            min_stock_per_board=5, min_absolute_surplus=150,
                            public_stock_surplus_overrides=[], verdict="PASS",
                            predicts_jlc_assembly_allocation=False,
                            graded_lines=88, total_lines=88, failures=0,
                            uncoded_lines=0, lines=stock_rows)
            request_path.write_text(json.dumps(request))
            evidence_path.write_text(json.dumps(evidence))
            snapshot = dict(path="stock.json",
                            sha256=hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
                            initial_checked_at="2026-01-01T13:00:00Z",
                            max_age_hours=24)

            def grade(*, pinned=True):
                return mr._catalog_prelayout_check(
                    request_path, evidence_path, decision_path,
                    expected_min_surplus=150, exact_rows=exact_rows,
                    selection_snapshot=snapshot if pinned else None, project=project)

            self.assertEqual("PASS", grade()["status"])
            self.assertIn("pinned initial", grade()["detail"])
            self.assertEqual("FAIL", grade(pinned=False)["status"])
            circuit = project / "03_tscircuit/build/circuit.json"
            circuit.parent.mkdir(parents=True)
            circuit.write_text("[]")
            assembly = project / "03_src/rules/assembly.yaml"
            assembly.parent.mkdir(parents=True)
            assembly.write_text("build_quantity: 5\npublic_stock_surplus: 150\n"
                                "sourcing_authority: public-observations\n"
                                "public_stock_selection_snapshot:\n"
                                f"  path: stock.json\n  sha256: {snapshot['sha256']}\n"
                                "  initial_checked_at: 2026-01-01T13:00:00Z\n"
                                "  max_age_hours: 24\n")
            with patch.object(mr, "exact_code_check", return_value=(
                    {"status": "PASS", "rows": exact_rows}, [])), \
                 patch.object(mr, "_run", return_value={
                     "status": "PASS", "detail": "test", "output": ""}):
                composed = mr.grade(project, phase="prelayout",
                                    catalog_request=request_path,
                                    catalog_evidence=evidence_path,
                                    catalog_decision=decision_path)
            self.assertEqual("ACCEPTED", composed["verdict"])
            self.assertIn("pinned initial",
                          composed["checks"]["public_catalog_prelayout"]["detail"])
            request_rows[0]["required_qty"] = 10
            request_path.write_text(json.dumps(request))
            self.assertEqual("FAIL", grade()["status"])
            request_rows[0]["required_qty"] = 5
            request_path.write_text(json.dumps(request))
            evidence["lines"][0]["stock"] = 201
            evidence_path.write_text(json.dumps(evidence))
            self.assertIn("catalog initial snapshot digest changed", grade()["detail"])
            evidence["lines"][0]["stock"] = 200
            evidence_path.write_text(json.dumps(evidence))
            snapshot["initial_checked_at"] = "2026-01-04T13:00:00Z"
            self.assertEqual("FAIL", grade()["status"])


if __name__ == "__main__":
    unittest.main()
