#!/usr/bin/env python3
"""Fail-closed controls for Crow's private native geometry producer."""
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "rebuild_prototype_board_diagnostic.py"
SPEC = importlib.util.spec_from_file_location("crow_private_board", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PrototypeBoardDiagnosticTests(unittest.TestCase):
    def test_seed_tamper_and_foreign_rule_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pro = root / "seed.kicad_pro"
            dru = root / "seed.kicad_dru"
            pro.write_text("{}")
            dru.write_text('(version 1)\n(rule "known" (constraint track_width (min 0.2mm)))\n')
            with self.assertRaisesRegex(RuntimeError, "unreviewed KiCad rule seed"):
                MODULE.check_rule_seed(pro, dru)
            effective = root / "effective.kicad_dru"
            effective.write_text(dru.read_text() + '(rule "foreign" (constraint clearance (min 0mm)))\n')
            with self.assertRaisesRegex(RuntimeError, "unexpected effective DRU rules"):
                MODULE.check_effective_dru(dru, effective)

    def test_canonical_output_path_is_refused_before_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            forbidden = root / "04_kicad/crow_carrier.kicad_pcb"
            with self.assertRaisesRegex(RuntimeError, "output must be below private"):
                MODULE.build(root, root, forbidden)
            self.assertFalse(forbidden.exists())

    def test_ordinary_conductors_still_require_accepted_selection(self):
        project = SCRIPT.parents[1]
        for name in ("rebuild_all.sh", "rebuild_reuse.sh"):
            source = (project / "03_src" / name).read_text()
            self.assertIn("critical_part_selection_admission.py", source)
            self.assertIn("PROTOTYPE_ONLY", source.upper())


if __name__ == "__main__":
    unittest.main()
