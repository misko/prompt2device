"""The pinned connector geometry screen must regenerate byte for byte."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "projects/crow-usb-carrier-v1/01_docs/research"
SCRIPT = RESEARCH / "connector_fit_prototype.py"
BOARD = RESEARCH / "connector_fit_prototype.kicad_pcb"
REPORT = RESEARCH / "connector_fit_prototype.json"


class ConnectorFitPrototypeTest(unittest.TestCase):
    def test_regeneration_is_byte_stable_and_has_no_sidecars(self):
        before = (BOARD.read_bytes(), REPORT.read_bytes())
        for _ in range(2):
            subprocess.run(["/usr/bin/python3", str(SCRIPT)], cwd=ROOT,
                           check=True, capture_output=True, text=True)
            self.assertEqual((BOARD.read_bytes(), REPORT.read_bytes()), before)
            self.assertFalse((RESEARCH / "connector_fit_prototype.kicad_pro").exists())
            self.assertFalse((RESEARCH / "connector_fit_prototype.kicad_prl").exists())
        report = json.loads(before[1])
        self.assertEqual(report["board_sha256"], hashlib.sha256(before[0]).hexdigest())
        self.assertEqual(report["status"], "NONQUALIFYING_GEOMETRY_SCREEN_ONLY")
        self.assertFalse(report["gerbers_emitted"])


if __name__ == "__main__":
    unittest.main()
