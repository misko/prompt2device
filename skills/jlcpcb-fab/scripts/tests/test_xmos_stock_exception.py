"""D10 applies to one placed XMOS identity and preserves all other reserves."""
import json
import io
import runpy
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manufacturing_readiness as mr
import release_freshness_check as fresh
from stock_surplus_policy import parse_policy, surplus_for


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "projects/crow-usb-carrier-v1"
XMOS = "XU316-1024-TQ128-C24"
CODE = "C6362698"
ENTRY = {"lcsc": CODE, "mpn": XMOS, "surplus": 0, "directive": "D10"}


class XmosStockException(unittest.TestCase):
    def test_stock_generator_records_exact_applied_surplus(self):
        with tempfile.TemporaryDirectory() as folder:
            bom = Path(folder) / "bom.csv"
            output = Path(folder) / "stock.json"
            bom.write_text("Comment,Designator,Footprint,LCSC\n"
                           f"{XMOS},U_XU,TQFP-128,{CODE}\n"
                           "10k,R1,R_0402,C123\n")
            components = {
                CODE: dict(componentCode=CODE, componentModelEn=XMOS,
                           stockCount=46),
                "C123": dict(componentCode="C123", componentModelEn="OTHER",
                             stockCount=156),
            }

            def answer(request, timeout):
                code = json.loads(request.data)["keyword"]
                payload = {"data": {"componentPageInfo": {"list": [components[code]]}}}
                return io.BytesIO(json.dumps(payload).encode())

            script = Path(__file__).resolve().parents[1] / "jlc_stock_check.py"
            argv = [str(script), str(bom), "--assembly",
                    str(PROJECT / "03_src/rules/assembly.yaml"),
                    "--json", str(output)]
            with patch.object(sys, "argv", argv), patch("urllib.request.urlopen", answer), \
                    patch("time.sleep", return_value=None), \
                    self.assertRaises(SystemExit) as result:
                runpy.run_path(str(script), run_name="__main__")
            self.assertEqual(0, result.exception.code)
            doc = json.loads(output.read_text())
            self.assertEqual("PASS", doc["verdict"])
            self.assertEqual([5, 155], [row["stock_threshold"] for row in doc["lines"]])
            self.assertEqual([0, 150], [row["applied_surplus"] for row in doc["lines"]])

    def test_policy_is_exact_and_authorized(self):
        policy = {"public_stock_surplus": 150,
                  "public_stock_surplus_overrides": [ENTRY]}
        default, overrides = parse_policy(policy, PROJECT)
        self.assertEqual((150, 0), (default, surplus_for(default, overrides, CODE, XMOS, ["U_XU"])))
        self.assertEqual(150, surplus_for(default, overrides, "C123", "OTHER", ["U2"]))
        for bad in (
            dict(ENTRY, lcsc="C123"), dict(ENTRY, mpn="OTHER"),
            dict(ENTRY, surplus=1), dict(ENTRY, surplus=False),
            dict(ENTRY, directive="D7")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse_policy(dict(policy, public_stock_surplus_overrides=[bad]), PROJECT)
        with self.assertRaises(ValueError):
            parse_policy(dict(policy, public_stock_surplus_overrides=[ENTRY, ENTRY]), PROJECT)
        with self.assertRaises(ValueError):
            parse_policy(policy, Path(tempfile.gettempdir()) / "other-project")
        with self.assertRaisesRegex(ValueError, "D7"):
            parse_policy(dict(policy, public_stock_surplus=0), PROJECT)
        with self.assertRaisesRegex(ValueError, "MPN"):
            surplus_for(default, overrides, CODE, "OTHER", ["U_XU"])
        with self.assertRaisesRegex(ValueError, "U_XU"):
            surplus_for(default, overrides, CODE, XMOS, ["U2"])

    def test_catalog_binds_one_override_and_keeps_other_line_at_150(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            request = root / "request.json"
            evidence = root / "stock.json"
            decision = root / "decision.md"
            decision.write_text("public-catalog pre-layout DO-NOT-ORDER")
            rows = [dict(requested_lcsc=CODE, designators=["U_XU"],
                         per_board_qty=1, required_qty=5),
                    dict(requested_lcsc="C123", designators=["R1"],
                         per_board_qty=1, required_qty=5)]
            request.write_text(json.dumps(dict(schema=2, phase="prelayout",
                                               build_quantity=5, rows=rows)))
            observations = [dict(lcsc=CODE, designators="U_XU", qty=1,
                                 required_qty=5, stock_threshold=5,
                                 applied_surplus=0, absolute_surplus=41,
                                 stock=46, mpn=XMOS, status="OK"),
                            dict(lcsc="C123", designators="R1", qty=1,
                                 required_qty=5, stock_threshold=155,
                                 applied_surplus=150, absolute_surplus=151,
                                 stock=156, mpn="OTHER", status="OK")]
            doc = dict(tool="jlc_stock_check.py", stock_source="lcsc_catalog_stockCount",
                       generated_at=datetime.now(timezone.utc).isoformat(),
                       min_stock_per_board=5, min_absolute_surplus=150,
                       public_stock_surplus_overrides=[ENTRY], verdict="PASS",
                       predicts_jlc_assembly_allocation=False, graded_lines=2,
                       total_lines=2, failures=0, uncoded_lines=0, lines=observations)
            exact = [dict(ref="U_XU", mpn=XMOS, jlc_codes=[CODE]),
                     dict(ref="R1", mpn="OTHER", jlc_codes=["C123"])]

            def grade():
                evidence.write_text(json.dumps(doc))
                return mr._catalog_prelayout_check(
                    request, evidence, decision, expected_min_surplus=150,
                    expected_overrides={CODE: {"mpn": XMOS, "surplus": 0,
                                               "directive": "D10"}},
                    exact_rows=exact)

            self.assertEqual("PASS", grade()["status"])
            doc["lines"][1]["stock_threshold"] = 5
            self.assertEqual("FAIL", grade()["status"])
            doc["lines"][1]["stock_threshold"] = 155
            doc["lines"][0]["mpn"] = "OTHER"
            self.assertEqual("FAIL", grade()["status"])
            doc["lines"][0]["mpn"] = XMOS
            doc["public_stock_surplus_overrides"] = []
            self.assertEqual("FAIL", grade()["status"])

    def test_release_checks_placed_refs_and_shipped_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / "crow-usb-carrier-v1"
            decision = project / "01_docs/decisions"
            decision.mkdir(parents=True)
            (project / "01_docs/BRIEF.md").write_bytes(
                (PROJECT / "01_docs/BRIEF.md").read_bytes())
            (decision / "0009-xmos-public-stock-reserve-exception.md").write_bytes(
                (PROJECT / "01_docs/decisions/0009-xmos-public-stock-reserve-exception.md").read_bytes())
            rel = project / "07_releases/v1.0"
            (rel / "fab").mkdir(parents=True)
            (rel / "verification").mkdir()
            (rel / "fab/bom.csv").write_text(
                "Comment,Designator,Footprint,LCSC\n"
                f"{XMOS},U_XU,Package_QFP:TQFP-128,{CODE}\n"
                "10k,R1,Resistor_SMD:R_0402,C123\n")
            (rel / "fab/cpl.csv").write_text(
                "Designator,Val,Package,Mid X,Mid Y,Layer,Rotation\n"
                "U_XU,XMOS,TQFP-128,1,1,top,0\nR1,10k,R_0402,2,2,top,0\n")
            doc = dict(verdict="PASS", min_absolute_surplus=150,
                       public_stock_surplus_overrides=[ENTRY],
                       lines=[dict(lcsc=CODE, designators="U_XU", status="OK",
                                   stock=46, mpn=XMOS, required_qty=5,
                                   stock_threshold=5, applied_surplus=0,
                                   absolute_surplus=41),
                              dict(lcsc="C123", designators="R1", status="OK",
                                   stock=156, mpn="OTHER", required_qty=5,
                                   stock_threshold=155, applied_surplus=150,
                                   absolute_surplus=151)])
            assembly = dict(public_stock_surplus=150,
                            public_stock_surplus_overrides=[ENTRY], build_quantity=5)

            def grade():
                (rel / "verification/stock_check.json").write_text(json.dumps(doc))
                return fresh.check_stock(rel, assembly)[0]

            self.assertEqual([], grade())
            doc["lines"][0]["mpn"] = "OTHER"
            self.assertTrue(any("IDENTITY" in item for item in grade()))
            doc["lines"][0]["mpn"] = XMOS
            (rel / "fab/bom.csv").write_text(
                "Comment,Designator,Footprint,LCSC\n"
                f"{XMOS},U2,Package_QFP:TQFP-128,{CODE}\n"
                "10k,R1,Resistor_SMD:R_0402,C123\n")
            (rel / "fab/cpl.csv").write_text(
                "Designator,Val,Package,Mid X,Mid Y,Layer,Rotation\n"
                "U2,XMOS,TQFP-128,1,1,top,0\nR1,10k,R_0402,2,2,top,0\n")
            self.assertTrue(any("IDENTITY" in item for item in grade()))


if __name__ == "__main__":
    unittest.main()
