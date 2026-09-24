#!/usr/bin/env python3
"""Contract tests for critical-pair naming and independent inventory."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import critical_route_check as checker  # noqa: E402


class Board:
    def __init__(self, nets):
        self.nets = nets

    def GetNetsByName(self):
        return {net: None for net in self.nets}


class CriticalRoutePairNamingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="critical-pairs-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.route_path = self.root / "route.yaml"
        self.nets_path = self.root / "nets.yaml"
        self.board_path = self.root / "board.kicad_pcb"
        self.pairs = [("USB_DP", "USB_DN"), ("LINK_P", "LINK_N"),
                      ("LEGACY+", "LEGACY-")]

    def grade(self, declarations=None, required=None):
        declarations = self.pairs if declarations is None else declarations
        required = self.pairs if required is None else required
        all_nets = {net for pair in self.pairs + declarations + required
                    for net in pair}
        cfg = {
            "prep": {"waves": {"groups": {"differential": sorted(all_nets)}}},
            "route": {
                "preflight_critical_pairs": [
                    {"name": f"pair_{i}", "p": p, "n": n,
                     "wave": "differential", "allowed_layers": ["F.Cu"],
                     "no_vias": True}
                    for i, (p, n) in enumerate(declarations)],
                "no_critical_routes": "fixture has none" if not declarations else None,
                "waves": [{"name": "differential", "group": "differential",
                           "engine": "diff",
                           "layers": ["F.Cu"],
                           "length_match_group": list(pair)}
                          for pair in declarations],
            },
        }
        # Each declaration has its own wave so membership cannot hide a bad
        # pairing; names and suffixes are graded before wave lookup.
        for i, (declaration, wave) in enumerate(zip(
                cfg["route"]["preflight_critical_pairs"],
                cfg["route"]["waves"])):
            wave["name"] = f"differential_{i}"
            declaration["wave"] = wave["name"]
        self.route_path.write_text(yaml.safe_dump(cfg))
        self.nets_path.write_text(yaml.safe_dump({
            "length_match": {f"required_{i}": {"members": {"P": [p], "N": [n]}}
                             for i, (p, n) in enumerate(required)}}))
        with patch.object(checker.pcbnew, "LoadBoard", return_value=Board(all_nets)):
            return checker.check(self.root, self.board_path,
                                 route_path=self.route_path,
                                 nets_path=self.nets_path)

    def test_three_conventional_forms_are_discovered_and_declared(self):
        self.assertEqual(checker.length_contract_pairs(
            self.root, self._write_required()), set(self.pairs))
        self.assertEqual(len(self.grade()), 3)

    def _write_required(self):
        self.nets_path.write_text(yaml.safe_dump({
            "length_match": {f"pair_{i}": {"members": {"P": [p], "N": [n]}}
                             for i, (p, n) in enumerate(self.pairs)}}))
        return self.nets_path

    def test_usb_pair_omission_is_found_from_independent_rules(self):
        with self.assertRaisesRegex(checker.RouteContractError,
                                    "omits length_match pair.*USB_DP/USB_DN"):
            self.grade(declarations=self.pairs[1:])

    def test_no_critical_routes_reason_cannot_hide_required_usb_pair(self):
        with self.assertRaisesRegex(checker.RouteContractError,
                                    "omits length_match pair.*USB_DP/USB_DN"):
            self.grade(declarations=[], required=[self.pairs[0]])
        self.assertEqual(self.grade(declarations=[], required=[]),
                         ["no critical routes: fixture has none"])

    def test_reversed_wrong_stem_and_mixed_style_are_rejected(self):
        for pair in (("USB_DN", "USB_DP"), ("USB_DP", "OTHER_DN"),
                     ("USB_DP", "USB_N"), ("LINK_P", "OTHER_N"),
                     ("LEGACY+", "OTHER-")):
            with self.subTest(pair=pair):
                with self.assertRaisesRegex(checker.RouteContractError,
                                            "polarity requires matching"):
                    self.grade(declarations=[pair], required=[])

    def test_duplicate_declaration_is_ambiguous(self):
        with self.assertRaisesRegex(checker.RouteContractError,
                                    "duplicate critical-pair declaration"):
            self.grade(declarations=[self.pairs[0], self.pairs[0]], required=[])

    def _native_with_vias(self, counts):
        pcb = checker.pcbnew
        board = pcb.BOARD()
        for name, count in counts.items():
            net = pcb.NETINFO_ITEM(board, name)
            board.Add(net)
            segment = pcb.PCB_TRACK(board)
            segment.SetStart(pcb.VECTOR2I(pcb.FromMM(1), pcb.FromMM(1)))
            segment.SetEnd(pcb.VECTOR2I(pcb.FromMM(2), pcb.FromMM(1)))
            segment.SetWidth(pcb.FromMM(0.2))
            segment.SetLayer(pcb.F_Cu)
            segment.SetNet(net)
            board.Add(segment)
            for i in range(count):
                via = pcb.PCB_VIA(board)
                via.SetPosition(pcb.VECTOR2I(pcb.FromMM(3 + i), pcb.FromMM(1)))
                via.SetWidth(pcb.FromMM(0.6))
                via.SetDrill(pcb.FromMM(0.3))
                via.SetLayerPair(pcb.F_Cu, pcb.B_Cu)
                via.SetNet(net)
                board.Add(via)
        return board

    def _grade_via_policy(self, route_cap, group_cap, counts, *, no_vias=False):
        pair = self.pairs[0]
        self.grade(declarations=[pair], required=[pair])
        route = yaml.safe_load(self.route_path.read_text())
        item = route['route']['preflight_critical_pairs'][0]
        item['no_vias'] = no_vias
        if route_cap is not None:
            item['max_vias_per_net'] = route_cap
        self.route_path.write_text(yaml.safe_dump(route))
        nets = yaml.safe_load(self.nets_path.read_text())
        if group_cap is not None:
            nets['length_match']['required_0']['max_vias_per_net'] = group_cap
        self.nets_path.write_text(yaml.safe_dump(nets))
        board = self._native_with_vias(counts)
        with patch.object(checker.pcbnew, 'LoadBoard', return_value=board), \
                patch.object(checker, 'connected', return_value=(True, 'all pads connected')):
            return checker.check(self.root, self.board_path, require_connected=True,
                                 route_path=self.route_path, nets_path=self.nets_path)

    def test_optional_via_cap_counts_each_net_and_accepts_the_boundary(self):
        notes = self._grade_via_policy(1, 1, {'USB_DP': 1, 'USB_DN': 0})
        self.assertIn('max_vias_per_net=1', notes[0])
        with self.assertRaisesRegex(checker.RouteContractError,
                                    'USB_DP: 2 via\\(s\\) exceed max_vias_per_net 1'):
            self._grade_via_policy(1, 1, {'USB_DP': 2, 'USB_DN': 0})

    def test_group_cap_applies_when_route_cap_is_omitted(self):
        with self.assertRaisesRegex(checker.RouteContractError,
                                    'USB_DN: 1 via\\(s\\) exceed max_vias_per_net 0'):
            self._grade_via_policy(None, 0, {'USB_DP': 0, 'USB_DN': 1})

    def test_malformed_conflicting_and_no_vias_caps_reject(self):
        for bad in (-1, True, 1.5, '2'):
            with self.subTest(bad=bad), self.assertRaisesRegex(
                    checker.RouteContractError, 'max_vias_per_net must be a nonnegative integer'):
                self._grade_via_policy(bad, None, {'USB_DP': 0, 'USB_DN': 0})
        with self.assertRaisesRegex(checker.RouteContractError,
                                    'disagrees with length_match cap'):
            self._grade_via_policy(1, 2, {'USB_DP': 0, 'USB_DN': 0})
        with self.assertRaisesRegex(checker.RouteContractError,
                                    'no_vias conflicts with max_vias_per_net'):
            self._grade_via_policy(1, None, {'USB_DP': 0, 'USB_DN': 0}, no_vias=True)
        with self.assertRaisesRegex(checker.RouteContractError,
                                    'max_vias_per_net must be a nonnegative integer'):
            self._grade_via_policy(None, True, {'USB_DP': 0, 'USB_DN': 0})
        with self.assertRaisesRegex(checker.RouteContractError,
                                    'expected zero'):
            self._grade_via_policy(0, 0, {'USB_DP': 1, 'USB_DN': 0}, no_vias=True)
        with self.assertRaisesRegex(checker.RouteContractError,
                                    'expected zero'):
            self._grade_via_policy(None, None, {'USB_DP': 1, 'USB_DN': 0}, no_vias=True)


if __name__ == "__main__":
    unittest.main()
