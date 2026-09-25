"""Fail-closed TMUX process guard for source-bound pair-only DRU rules."""
import sys
import tempfile
import unittest
from pathlib import Path

import pcbnew
import yaml

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from via_process_check import (audit_dru_constraints, pair_scoped_dru_rules,
                               controlled_pair_dru_rules)  # noqa: E402


class Box:
    def __init__(self, rect):
        self.rect = [pcbnew.FromMM(x) for x in rect]

    def GetLeft(self): return self.rect[0]
    def GetTop(self): return self.rect[1]
    def GetRight(self): return self.rect[2]
    def GetBottom(self): return self.rect[3]


class LayerSet:
    def __init__(self, layers): self.layers = layers
    def Seq(self): return self.layers


class Area:
    def __init__(self, name, rect, layers=(pcbnew.F_Cu,)):
        self.name, self.rect, self.layers = name, rect, layers
    def GetZoneName(self): return self.name
    def GetIsRuleArea(self): return True
    def GetLayerSet(self): return LayerSet(self.layers)
    def GetBoundingBox(self): return Box(self.rect)
    def GetDoNotAllowTracks(self): return False
    def GetDoNotAllowVias(self): return False
    def GetDoNotAllowPads(self): return False
    def GetDoNotAllowFootprints(self): return False
    def GetDoNotAllowZoneFills(self): return False


class Pad:
    def __init__(self, net): self.net = net
    def GetNetname(self): return self.net


class Footprint:
    def __init__(self, ref, nets): self.ref, self.nets = ref, nets
    def GetReference(self): return self.ref
    def Pads(self): return [Pad(net) for net in self.nets]


class Board:
    def __init__(self, area): self.area = area
    def Zones(self): return [self.area]
    def GetLayerName(self, layer): return "F.Cu" if layer == pcbnew.F_Cu else "B.Cu"
    def GetFootprints(self): return [Footprint("U_ISO1", ["GND", "FILTER1P", "N5V_LDO_HOLD"])]


class PairScopedTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        rules = root / "03_src/rules"
        rules.mkdir(parents=True)
        self.assembly = rules / "assembly.yaml"
        self.assembly.write_text("{}\n")
        self.nets = rules / "nets.yaml"
        self.spec = {"zone": "usb_pair_xu_launch", "nets_a": ["USB_DP"],
                     "nets_b": ["USB_DN"], "clearance": "0.100mm", "why": "exact launch"}
        self.floor = {"keepouts": [{"name": "usb_pair_xu_launch", "layers": ["F.Cu"],
                                    "deny": [], "rect": [215.3, 95.0, 217.1, 95.8]}]}
        self.board = Board(Area("usb_pair_xu_launch", [215.3, 95.0, 217.1, 95.8]))
        self.write_source()

    def tearDown(self): self.tmp.cleanup()

    def write_source(self): self.nets.write_text(yaml.safe_dump({"scoped_clearances": [self.spec]}))

    def rule(self): return pair_scoped_dru_rules(self.assembly, self.board, self.floor)[0]

    def test_exact_generated_pair_is_only_removed_rule(self):
        rule = self.rule()
        self.assertEqual(rule, """(rule "scoped_clr_usb_pair_xu_launch"
  (condition "A.insideArea('usb_pair_xu_launch') && B.insideArea('usb_pair_xu_launch') && (((A.NetName == 'USB_DP') && (B.NetName == 'USB_DN')) || ((A.NetName == 'USB_DN') && (B.NetName == 'USB_DP')))")
  (constraint clearance (min 0.1mm)))""")
        self.assertEqual(audit_dru_constraints("(version 1)\n" + rule, [], [], [rule]), [])

    def test_selector_widening_fails(self):
        self.spec["nets_b"].append("OTHER")
        self.write_source()
        with self.assertRaisesRegex(ValueError, "widens selector"):
            self.rule()

    def test_tmux_net_fails(self):
        self.spec["nets_b"] = ["GND"]
        self.write_source()
        with self.assertRaisesRegex(ValueError, "TMUX nets"):
            self.rule()

    def test_native_area_or_layer_drift_fails(self):
        self.board.area.rect[2] = 217.2
        with self.assertRaisesRegex(ValueError, "bounds drift"):
            self.rule()
        self.board.area.rect[2] = 217.1
        self.board.area.layers = (pcbnew.B_Cu,)
        with self.assertRaisesRegex(ValueError, "native pair area"):
            self.rule()

    def test_source_area_layer_drift_fails(self):
        self.floor["keepouts"][0]["layers"] = ["F.Cu", "B.Cu"]
        with self.assertRaisesRegex(ValueError, "permissive F.Cu"):
            self.rule()

    def test_source_area_bounds_or_native_name_drift_fails(self):
        self.floor["keepouts"][0]["rect"][2] = 217.2
        with self.assertRaisesRegex(ValueError, "bounds drift"):
            self.rule()
        self.floor["keepouts"][0]["rect"][2] = 217.1
        self.board.area.name = "other_area"
        with self.assertRaisesRegex(ValueError, "native pair area"):
            self.rule()

    def test_dru_selector_tamper_and_foreign_constraint_fail(self):
        rule = self.rule()
        widened = rule.replace("A.NetName == 'USB_DP'", "A.NetName == 'GND'")
        failures = audit_dru_constraints("(version 1)\n" + widened, [], [], [rule])
        self.assertTrue(any("missing or altered exact pair" in x for x in failures))
        self.assertTrue(any("foreign clearance" in x for x in failures))
        foreign = '(rule "foreign"\n  (condition "true")\n  (constraint clearance (min 0.01mm)))'
        failures = audit_dru_constraints("(version 1)\n" + rule + "\n" + foreign, [], [], [rule])
        self.assertEqual(failures, ["TMUX-DRU: foreign clearance/via/hole constraint"])


class ControlledPairTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        rules = Path(self.tmp.name) / "03_src/rules"
        rules.mkdir(parents=True)
        self.assembly = rules / "assembly.yaml"
        self.assembly.write_text("{}\n")
        self.nets = rules / "nets.yaml"
        (rules.parent / "floorplan.yaml").write_text("board:\n  layers: 4\n")
        self.board = Board(Area("unused", [0, 0, 1, 1]))
        self.spec = {"pair": "USB_DEVICE", "nets_a": ["USB_DP"],
                     "nets_b": ["USB_DN"], "layer": "F.Cu",
                     "clearance": "0.100mm", "why": "measured hypothesis"}
        self.write_source()

    def tearDown(self): self.tmp.cleanup()

    def write_source(self, specs=None):
        self.nets.write_text(yaml.safe_dump({
            "classes": {"USB_HS": {"nets": ["USB_DP", "USB_DN"],
                                    "clearance": "0.150mm", "diff_pair": {"gap": "0.100mm"}}},
            "length_match": {"USB_DEVICE": {"members": {"P": ["USB_DP"],
                                                       "N": ["USB_DN"]}, "no_vias": True}},
            "controlled_pair_clearances": [self.spec] if specs is None else specs}))

    def test_exact_rule_and_tamper(self):
        rules = controlled_pair_dru_rules(self.assembly, self.board)
        self.assertEqual(len(rules), 4)
        rule = rules[0]
        self.assertIn('(layer "F.Cu")', rule)
        self.assertEqual(audit_dru_constraints('(version 1)\n'+'\n'.join(rules), [], [], [], rules), [])
        altered = rule.replace("USB_DN", "GND")
        self.assertTrue(audit_dru_constraints('(version 1)\n'+altered+'\n'+'\n'.join(rules[1:]), [], [], [], rules))

    def test_rejects_widened_selector_layer_and_second_pair(self):
        self.spec["nets_b"] = ["USB_DN", "OTHER"]
        self.write_source()
        with self.assertRaisesRegex(ValueError, "widens selector"):
            controlled_pair_dru_rules(self.assembly, self.board)
        self.spec["nets_b"] = ["USB_DN"]
        self.spec["layer"] = "B.Cu"
        self.write_source()
        with self.assertRaisesRegex(ValueError, "widens selector"):
            controlled_pair_dru_rules(self.assembly, self.board)
        self.spec["layer"] = "F.Cu"
        self.write_source([self.spec, self.spec])
        with self.assertRaisesRegex(ValueError, "at most one"):
            controlled_pair_dru_rules(self.assembly, self.board)


if __name__ == "__main__":
    unittest.main()
