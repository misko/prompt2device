"""Regression protection for the independently identified TOP-BDF-001 omission.

These source checks preserve a cited extraction; they are not a replacement for
the independent datasheet review or realized-board P-PINMAP gate.
"""
import copy
import hashlib
from pathlib import Path
import unittest

import yaml

PROJECT = Path(__file__).resolve().parents[2]
DOSSIER = PROJECT / "02_parts/DMP6023LFG-13/part.yaml"


def validate_identity(doc):
    pins = doc["pins"]
    if set(pins) != set(range(1, 9)):
        raise ValueError("all eight manufacturer identities are required")
    for pin in range(5, 9):
        if pins[pin] != "DRAIN_COMMON":
            raise ValueError("all four fused drain functions must agree")
    aliases = doc.get("pin_aliases", {})
    for pin in (6, 7, 8):
        alias = aliases.get(pin, {})
        if alias.get("schematic") != "5" or alias.get("footprint") != "5":
            raise ValueError("every fused drain must reach artifact identity 5")
        if alias.get("fused") is not True or not alias.get("why") or not alias.get("evidence"):
            raise ValueError("fused mapping requires reason and primary evidence")


class FusedIdentityTests(unittest.TestCase):
    def setUp(self):
        self.doc = yaml.safe_load(DOSSIER.read_text())

    def test_all_eight_identities_and_explicit_aliases(self):
        validate_identity(self.doc)

    def test_original_five_pin_omission_rejected(self):
        bad = copy.deepcopy(self.doc)
        bad["pins"] = {p: v for p, v in bad["pins"].items() if p <= 5}
        with self.assertRaisesRegex(ValueError, "eight"):
            validate_identity(bad)

    def test_unexplained_collapse_rejected(self):
        bad = copy.deepcopy(self.doc)
        del bad["pin_aliases"][7]["evidence"]
        with self.assertRaisesRegex(ValueError, "evidence"):
            validate_identity(bad)

    def test_wrong_artifact_pin_rejected(self):
        bad = copy.deepcopy(self.doc)
        bad["pin_aliases"][8]["footprint"] = "4"
        with self.assertRaisesRegex(ValueError, "identity 5"):
            validate_identity(bad)

    def test_primary_bytes_remain_digest_bound(self):
        primary = DOSSIER.parent / self.doc["datasheet"]["local"]
        self.assertEqual(hashlib.sha256(primary.read_bytes()).hexdigest(),
                         self.doc["datasheet"]["sha256"])


if __name__ == "__main__":
    unittest.main()
