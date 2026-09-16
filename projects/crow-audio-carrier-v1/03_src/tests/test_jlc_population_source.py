import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


class JlcPopulationSourceTests(unittest.TestCase):
    def test_every_required_jlc_smd_is_position_exportable(self):
        floorplan = yaml.safe_load((ROOT / "03_src/floorplan.yaml").read_text())
        excluded = set()
        for pattern in floorplan["placement"]["patterns"]:
            if "exclude_from_pos_files" in (pattern.get("attrs") or []):
                excluded.update(pattern.get("match") or [])

        required = {
            "U_ADC", "F_IN", "C_FILT1_470U", "C_FILT2_470U",
            "C_HOLD1", "C_HOLD2",
        }
        self.assertTrue(required.isdisjoint(excluded),
                        f"JLC-required SMD still excluded from CPL: {sorted(required & excluded)}")

    def test_position_exclusions_match_declared_manual_population(self):
        floorplan = yaml.safe_load((ROOT / "03_src/floorplan.yaml").read_text())
        assembly = yaml.safe_load((ROOT / "03_src/rules/assembly.yaml").read_text())
        excluded = set()
        for pattern in floorplan["placement"]["patterns"]:
            if "exclude_from_pos_files" in (pattern.get("attrs") or []):
                excluded.update(pattern.get("match") or [])
        manual = {ref for row in assembly["not_assembled"] for ref in row["refs"]}
        self.assertEqual(excluded, manual)


if __name__ == "__main__":
    unittest.main()
