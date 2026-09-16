from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_realized_routes.py"
SPEC = importlib.util.spec_from_file_location("crow_realized_routes", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


class Oracle:
    def __init__(self) -> None:
        self.overrides = {}
        self.bypasses = {}

    def __call__(self, start: str, end: str):
        key = (start, end)
        if key in self.overrides:
            return self.overrides[key]
        required = "F.Cu"
        return checker.PathResult(
            start, end, "N", 1.0, frozenset({1}), 0, frozenset({required})
        )

    def bypassed_prefix_edges(self, start: str, clamp: str, target: str,
                              _prefix_edges: frozenset[int]):
        return frozenset(self.bypasses.get((start, clamp, target), ()))


class RealizedRoutePolicyTests(unittest.TestCase):
    def test_exact_policy_shape_passes(self) -> None:
        receipt = checker.grade(Oracle())
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["graded"], 22)

    def test_long_cap_route_fails_even_without_via(self) -> None:
        oracle = Oracle()
        oracle.overrides[("U2.1", "C5.1")] = checker.PathResult(
            "U2.1", "C5.1", "5V_QUIET", 3.001, frozenset({7}), 0,
            frozenset({"F.Cu"}),
        )
        receipt = checker.grade(oracle)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(any("U2.1->C5.1" in item for item in receipt["findings"]))

    def test_regulator_critical_path_on_back_layer_fails(self) -> None:
        oracle = Oracle()
        oracle.overrides[("U2.8", "C2.1")] = checker.PathResult(
            "U2.8", "C2.1", "VIN_PROTECTED", 1.0, frozenset({7}), 0,
            frozenset({"B.Cu"}),
        )
        receipt = checker.grade(oracle)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(any("instead of F.Cu only" in item for item in receipt["findings"]))

    def test_via_bearing_short_path_fails(self) -> None:
        oracle = Oracle()
        oracle.overrides[("J1.4", "U3.5")] = checker.PathResult(
            "J1.4", "U3.5", "AUDIO_N", 2.0, frozenset({3, 4}), 1,
            frozenset({"F.Cu", "B.Cu"}),
        )
        receipt = checker.grade(oracle)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(any("uses 1 via" in item for item in receipt["findings"]))

    def test_audio_positive_prefix_on_back_layer_fails(self) -> None:
        oracle = Oracle()
        oracle.overrides[("J1.5", "U3.3")] = checker.PathResult(
            "J1.5", "U3.3", "AUDIO_P", 1.94, frozenset({3}), 0,
            frozenset({"B.Cu"}),
        )
        receipt = checker.grade(oracle)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(any("instead of F.Cu only" in item for item in receipt["findings"]))

    def test_audio_negative_prefix_on_back_layer_fails(self) -> None:
        oracle = Oracle()
        oracle.overrides[("J1.4", "U3.5")] = checker.PathResult(
            "J1.4", "U3.5", "AUDIO_N", 1.94, frozenset({3}), 0,
            frozenset({"B.Cu"}),
        )
        receipt = checker.grade(oracle)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(any("instead of F.Cu only" in item for item in receipt["findings"]))

    def test_audio_pad_centre_over_positive_budget_fails(self) -> None:
        oracle = Oracle()
        oracle.overrides[("J1.5", "U3.3")] = checker.PathResult(
            "J1.5", "U3.3", "AUDIO_P", 4.1, frozenset({3}), 0,
            frozenset({"F.Cu"}), 8.601,
        )
        receipt = checker.grade(oracle)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(any("pad-centre span" in item for item in receipt["findings"]))

    def test_audio_realized_copper_over_negative_budget_fails(self) -> None:
        oracle = Oracle()
        oracle.overrides[("J1.4", "U3.5")] = checker.PathResult(
            "J1.4", "U3.5", "AUDIO_N", 7.501, frozenset({3}), 0,
            frozenset({"F.Cu"}), 5.538173,
        )
        receipt = checker.grade(oracle)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(any("exceeds 7.500 mm" in item for item in receipt["findings"]))

    def test_branch_before_clamp_fails(self) -> None:
        oracle = Oracle()
        oracle.overrides[("J1.5", "U3.3")] = checker.PathResult(
            "J1.5", "U3.3", "AUDIO_P", 2.0, frozenset({10, 11}), 0,
            frozenset({"F.Cu"}),
        )
        oracle.overrides[("J1.5", "R12.2")] = checker.PathResult(
            "J1.5", "R12.2", "AUDIO_P", 3.0, frozenset({10, 99}), 0,
            frozenset({"F.Cu"}),
        )
        receipt = checker.grade(oracle)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(any("branches before U3.3" in item for item in receipt["findings"]))

    def test_longer_parallel_preclamp_bypass_fails_dominance(self) -> None:
        oracle = Oracle()
        oracle.overrides[("J1.4", "U3.5")] = checker.PathResult(
            "J1.4", "U3.5", "AUDIO_N", 2.0, frozenset({20, 21}), 0,
            frozenset({"F.Cu"}),
        )
        oracle.overrides[("J1.4", "R13.2")] = checker.PathResult(
            "J1.4", "R13.2", "AUDIO_N", 3.0, frozenset({20, 21, 22}), 0,
            frozenset({"F.Cu"}),
        )
        # The shortest downstream path contains the entire clamp prefix, but
        # a longer parallel tee still reaches R13 while bypassing edge 21.
        oracle.bypasses[("J1.4", "U3.5", "R13.2")] = {21}
        receipt = checker.grade(oracle)
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(any("parallel copper" in item for item in receipt["findings"]))


if __name__ == "__main__":
    unittest.main()
