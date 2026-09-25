from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml


SCRIPTS = Path(__file__).resolve().parents[1]
REPO = SCRIPTS.parents[2]
sys.path.insert(0, str(SCRIPTS))
from critical_part_selection_admission import evaluate  # noqa: E402


class CriticalSelectionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        source = self.write("03_tscircuit/src/usb.tsx", '''<chip name="U_ESD"
  manufacturerPartNumber="PART-5V" supplierPartNumbers={{jlcpcb:["C123"]}}
  connections={pins} />\n''')
        self.write_yaml("02_parts/PART-5V/part.yaml", {
            "mpn": "PART-5V", "sourcing": {"lcsc": "C123"},
            "pins": {"1": "DP", "2": "DN", "3": "GND"},
        })
        self.write_yaml("03_src/rules/assembly.yaml", {
            "build_quantity": 5, "public_stock_surplus": 2,
        })
        self.write_yaml("01_docs/findings.yaml", {
            "schema": 1, "findings": [{"id": "ESD-DC", "state": "closed",
                                      "critical_selection": {"ref": "U_ESD", "due_stage": "selection"},
                                      "evidence": ["01_docs/selection-review.md"]}],
        })
        review = self.write("01_docs/selection-review.md", "Independent electrical selection review\n")
        self.write_json("06_build/sourcing/selection-stock.json", {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "verdict": "PASS", "lines": [{
                "lcsc": "C123", "mpn": "PART-5V", "designators": "U_ESD",
                "qty": 1, "required_qty": 5, "stock_threshold": 7,
                "applied_surplus": 2, "stock": 10, "status": "OK",
            }],
        })
        self.declaration = self.write_yaml("03_src/rules/critical_part_selection.yaml", {
            "schema": 1,
            "assembly": "03_src/rules/assembly.yaml",
            "findings": "01_docs/findings.yaml",
            "selections": [{
                "ref": "U_ESD", "mpn": "PART-5V", "lcsc": "C123",
                "dossier": "02_parts/PART-5V/part.yaml",
                "source": {"path": "03_tscircuit/src/usb.tsx",
                           "sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
                "stock": {"path": "06_build/sourcing/selection-stock.json",
                          "max_age_hours": 24},
                "suitability": {"status": "accepted", "decision_owner": "electrical-lead",
                                "reviewer": "independent-reviewer",
                                "evidence": {"path": "01_docs/selection-review.md",
                                             "sha256": hashlib.sha256(review.read_bytes()).hexdigest()}},
                "due_at_selection_findings": ["ESD-DC"],
            }],
        })

    def write(self, name, value):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
        return path

    def write_yaml(self, name, value):
        return self.write(name, yaml.safe_dump(value, sort_keys=False))

    def write_json(self, name, value):
        return self.write(name, json.dumps(value))

    def grade(self):
        return evaluate(self.project, self.declaration)

    def test_exact_selection_passes(self):
        report = self.grade()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["coverage"], "1/1")
        self.assertEqual(report["findings"], [])

    def test_exact_part_stock_failure_blocks(self):
        path = self.project / "06_build/sourcing/selection-stock.json"
        stock = json.loads(path.read_text())
        stock["verdict"] = "FAIL"
        stock["lines"][0].update(stock=6, status="LOW")
        path.write_text(json.dumps(stock))
        report = self.grade()
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("public stock 6 below 7" in f for f in report["findings"]))

    def set_initial_snapshot(self, stock):
        stock_path = self.project / "06_build/sourcing/selection-stock.json"
        stock_path.write_text(json.dumps(stock))
        manifest = yaml.safe_load(self.declaration.read_text())
        manifest["selections"][0]["stock"].update({
            "policy": "initial_snapshot",
            "sha256": hashlib.sha256(stock_path.read_bytes()).hexdigest(),
            "initial_checked_at": "2026-01-01T13:00:00Z",
        })
        self.declaration.write_text(yaml.safe_dump(manifest))

    def test_initial_snapshot_stays_valid_after_inventory_age_expires(self):
        stock_path = self.project / "06_build/sourcing/selection-stock.json"
        stock = json.loads(stock_path.read_text())
        stock["generated_at"] = "2026-01-01T12:00:00Z"
        self.set_initial_snapshot(stock)
        self.assertEqual(self.grade()["status"], "PASS")
        manifest = yaml.safe_load(self.declaration.read_text())
        manifest["selections"][0]["stock"]["policy"] = "rolling"
        self.declaration.write_text(yaml.safe_dump(manifest))
        self.assertEqual(self.grade()["status"], "FAIL")

    def test_initial_snapshot_refuses_mutated_receipt_or_changed_threshold(self):
        stock_path = self.project / "06_build/sourcing/selection-stock.json"
        stock = json.loads(stock_path.read_text())
        stock["generated_at"] = "2026-01-01T12:00:00Z"
        self.set_initial_snapshot(stock)
        stock["lines"][0]["stock"] = 99
        stock_path.write_text(json.dumps(stock))
        self.assertIn("U_ESD: initial public stock receipt digest changed",
                      self.grade()["findings"])
        self.set_initial_snapshot(stock)
        self.write_yaml("03_src/rules/assembly.yaml", {
            "build_quantity": 5, "public_stock_surplus": 150,
        })
        self.assertTrue(any("stock threshold disagrees" in item
                            for item in self.grade()["findings"]))

    def test_initial_snapshot_must_have_been_fresh_at_initial_check(self):
        stock = json.loads((self.project / "06_build/sourcing/selection-stock.json").read_text())
        stock["generated_at"] = "2025-12-28T12:00:00Z"
        self.set_initial_snapshot(stock)
        self.assertTrue(any("stale or undated at check time" in item
                            for item in self.grade()["findings"]))

    def test_unresolved_due_at_selection_electrical_finding_blocks(self):
        self.write_yaml("01_docs/findings.yaml", {
            "schema": 1, "findings": [{"id": "ESD-DC", "state": "open",
                                      "critical_selection": {"ref": "U_ESD", "due_stage": "selection"},
                                      "owner": "electrical",
                                      "finding": "transient coordination unresolved"}],
        })
        report = self.grade()
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("U_ESD: due-at-selection finding 'ESD-DC' is 'open'",
                      report["findings"])

    def test_unlisted_open_selection_finding_blocks(self):
        self.write_yaml("01_docs/findings.yaml", {
            "schema": 1, "findings": [
                {"id": "ESD-DC", "state": "closed", "evidence": ["review"]},
                {"id": "ESD-UV-MARGIN", "state": "open",
                 "critical_selection": {"ref": "U_ESD", "due_stage": "selection"}},
            ],
        })
        report = self.grade()
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("U_ESD: tagged selection finding 'ESD-UV-MARGIN' omitted from declaration",
                      report["findings"])

    def test_incomplete_suitability_blocks_even_with_stock_and_closed_findings(self):
        manifest = yaml.safe_load(self.declaration.read_text())
        manifest["selections"][0]["suitability"]["status"] = "incomplete"
        del manifest["selections"][0]["suitability"]["reviewer"]
        self.declaration.write_text(yaml.safe_dump(manifest))
        report = self.grade()
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("U_ESD: independent selection suitability is incomplete",
                      report["findings"])

    def test_accepted_suitability_requires_independent_reviewer(self):
        manifest = yaml.safe_load(self.declaration.read_text())
        del manifest["selections"][0]["suitability"]["reviewer"]
        self.declaration.write_text(yaml.safe_dump(manifest))
        with self.assertRaisesRegex(ValueError, "reviewer distinct from decision_owner"):
            self.grade()

    def test_absent_declaration_preserves_existing_behavior(self):
        self.declaration.unlink()
        self.assertEqual(self.grade()["status"], "NOT_APPLICABLE")

    def test_pending_scaffold_blocks_without_other_inputs(self):
        self.declaration.write_text("schema: 1\nstatus: pending\nselections: []\n")
        self.assertEqual(self.grade()["status"], "FAIL")

    def test_reviewed_not_applicable_passes_only_without_tagged_obligations(self):
        review = self.project / "01_docs/selection-review.md"
        manifest = {
            "schema": 1, "status": "not_applicable", "selections": [],
            "findings": "01_docs/findings.yaml",
            "applicability": {
                "decision_owner": "electrical-lead", "reviewer": "independent-reviewer",
                "evidence": {"path": "01_docs/selection-review.md",
                             "sha256": hashlib.sha256(review.read_bytes()).hexdigest()},
            },
        }
        self.declaration.write_text(yaml.safe_dump(manifest))
        self.assertEqual(self.grade()["status"], "FAIL")
        self.write_yaml("01_docs/findings.yaml", {"schema": 1, "findings": []})
        self.assertEqual(self.grade()["status"], "PASS")

    def test_full_and_reuse_conductors_stop_before_producer(self):
        stock = self.project / "06_build/sourcing/selection-stock.json"
        value = json.loads(stock.read_text())
        value["verdict"] = "FAIL"
        value["lines"][0].update(stock=6, status="LOW")
        stock.write_text(json.dumps(value))
        templates = REPO / "skills/pcb-design/templates/03_src"
        for name in ("rebuild_all.sh", "rebuild_reuse.sh"):
            with self.subTest(conductor=name):
                target = self.project / "03_src" / name
                shutil.copyfile(templates / name, target)
                env = {**os.environ, "CIRCUITS_ROOT": str(REPO)}
                run = subprocess.run(["bash", str(target)], cwd=self.project,
                                     env=env, capture_output=True, text=True,
                                     timeout=20)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("CRITICAL-SELECTION FAIL", run.stdout)
                self.assertIn("GATE INCOMPLETE", run.stderr)
                self.assertFalse((self.project / "03_tscircuit/dist").exists())
                self.assertFalse((self.project / "03_tscircuit/build/circuit.json").exists())

    def test_pending_scaffold_stops_both_conductors_before_producer(self):
        self.declaration.write_text("schema: 1\nstatus: pending\nselections: []\n")
        templates = REPO / "skills/pcb-design/templates/03_src"
        for name in ("rebuild_all.sh", "rebuild_reuse.sh"):
            with self.subTest(conductor=name):
                target = self.project / "03_src" / name
                shutil.copyfile(templates / name, target)
                run = subprocess.run(["bash", str(target)], cwd=self.project,
                                     env={**os.environ, "CIRCUITS_ROOT": str(REPO)},
                                     capture_output=True, text=True, timeout=20)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("CRITICAL-SELECTION FAIL", run.stdout)
                self.assertFalse((self.project / "03_tscircuit/dist").exists())

    def test_crow_usb_esd_historical_selection_replay(self):
        """Offline decision replay; quantities are retained Crow public snapshots, not live stock."""
        cases = (
            # Original TI catalog line fell below Crow's five-board +150 buffer.
            ("TPD2EUSB30ADRTR", "C94934", 29, "accepted", "closed", "stock"),
            # UV stock was ample, but 3.3-V standoff suitability was unresolved.
            ("PESD2USB3UV-TR", "C3704436", 110907, "incomplete", "open", "suitability"),
            # 5UX stock was ample; powered/unpowered transient coordination stayed open.
            ("PESD2USB5UX-TR", "C3709087", 17369, "incomplete", "open", "suitability"),
        )
        for mpn, lcsc, observed, suitability, finding_state, expected in cases:
            with self.subTest(mpn=mpn):
                source = self.write("03_tscircuit/src/usb.tsx",
                                    f'<chip name="U_ESD" manufacturerPartNumber="{mpn}" '
                                    f'supplierPartNumbers={{{{jlcpcb:["{lcsc}"]}}}} />\n')
                dossier = f"02_parts/{mpn}/part.yaml"
                self.write_yaml(dossier, {"mpn": mpn, "sourcing": {"lcsc": lcsc}})
                manifest = yaml.safe_load(self.declaration.read_text())
                row = manifest["selections"][0]
                row.update(mpn=mpn, lcsc=lcsc, dossier=dossier)
                row["source"]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
                row["suitability"]["status"] = suitability
                if suitability == "incomplete":
                    row["suitability"].pop("reviewer", None)
                self.declaration.write_text(yaml.safe_dump(manifest))
                self.write_yaml("01_docs/findings.yaml", {
                    "schema": 1, "findings": [{
                        "id": "ESD-DC", "state": finding_state,
                        "critical_selection": {"ref": "U_ESD", "due_stage": "selection"},
                        "evidence": ["01_docs/selection-review.md"],
                    }],
                })
                stock = {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "verdict": "PASS" if observed >= 155 else "FAIL",
                    "lines": [{"lcsc": lcsc, "mpn": mpn, "designators": "U_ESD",
                               "qty": 1, "required_qty": 5, "stock_threshold": 155,
                               "applied_surplus": 150, "stock": observed,
                               "status": "OK" if observed >= 155 else "LOW"}],
                }
                self.write_yaml("03_src/rules/assembly.yaml", {
                    "build_quantity": 5, "public_stock_surplus": 150,
                })
                self.write_json("06_build/sourcing/selection-stock.json", stock)
                report = self.grade()
                self.assertEqual(report["status"], "FAIL")
                self.assertTrue(any(expected in item for item in report["findings"]),
                                report["findings"])


if __name__ == "__main__":
    unittest.main()
