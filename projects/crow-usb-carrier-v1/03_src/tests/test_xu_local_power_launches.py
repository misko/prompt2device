"""Portable native-board tests for the inactive XU launch helper."""
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pcbnew as p
import yaml

SCRIPT = Path(__file__).parents[1] / "diagnostics/xu_local_power_launches.py"
SOURCE_CONFIG = Path(__file__).parents[1] / "rules/xu_local_power_launches.yaml"
spec = importlib.util.spec_from_file_location("xu_local_power_launches", SCRIPT)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)

CONFIG = {
    "status": "placement_review_required",
    "width_mm": 0.15,
    "ordinary_width_mm": 0.60,
    "layer": "F.Cu",
    "launches": [
        {"id": "XU_VDD14_LOCAL", "ref": "U_XU", "pad": "14", "net": "N0V9",
         "target": {"ref": "C_XU_VDD_14", "pad": "1"},
         "window": [207.25, 107.4, 207.75, 109.05],
         "flare": [207.5, 108.95], "max_window_area_mm2": 0.90},
        {"id": "XU_VDDIO17_LOCAL", "ref": "U_XU", "pad": "17", "net": "N1V8",
         "target": {"ref": "C_XU_VDDIO_17", "pad": "1"},
         "window": [208.45, 107.4, 208.95, 109.05],
         "flare": [208.7, 108.95], "max_window_area_mm2": 0.90},
    ],
}
ORDINARY = ('(version 1)\n'
            '(rule "DIGITAL_POWER_width"\n'
            '  (condition "A.NetClass == \'DIGITAL_POWER\'")\n'
            '  (constraint track_width (min 0.6mm)))\n'
            '(rule "SENTINEL" (constraint clearance (min 0.15mm)))\n')


def fixture():
    """Build only the native pads needed by this exact-pin contract."""
    board = p.BOARD()
    nets = {}
    for name in ("N0V9", "N1V8", "GND"):
        net = p.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net

    def add_pad(ref, number, net, point, size):
        foot = board.FindFootprintByReference(ref)
        if foot is None:
            foot = p.FOOTPRINT(board)
            foot.SetReference(ref)
            foot.SetPosition(p.VECTOR2I_MM(*point))
            board.Add(foot)
        pad = p.PAD(foot)
        pad.SetNumber(number)
        pad.SetAttribute(p.PAD_ATTRIB_SMD)
        pad.SetShape(p.PAD_SHAPE_RECT)
        pad.SetSize(p.VECTOR2I_MM(*size))
        pad.SetPosition(p.VECTOR2I_MM(*point))
        layers = p.LSET()
        layers.AddLayer(p.F_Cu)
        pad.SetLayerSet(layers)
        pad.SetNet(nets[net])
        foot.Add(pad)

    add_pad("U_XU", "14", "N0V9", (207.5, 107.6625), (0.25, 1.475))
    add_pad("U_XU", "17", "N1V8", (208.7, 107.6625), (0.25, 1.475))
    add_pad("C_XU_VDD_14", "1", "N0V9", (208.02, 112.4), (0.56, 0.62))
    add_pad("C_XU_VDDIO_17", "1", "N1V8", (208.7, 109.32), (0.56, 0.62))
    return board


def track(board, net, start, end, width=0.15, layer=p.F_Cu):
    item = p.PCB_TRACK(board)
    item.SetStart(p.VECTOR2I_MM(*start))
    item.SetEnd(p.VECTOR2I_MM(*end))
    item.SetWidth(p.FromMM(width))
    item.SetLayer(layer)
    item.SetNet(board.FindNet(net))
    board.Add(item)
    return item


def positive(board):
    track(board, "N0V9", (207.5, 107.6625), (207.5, 108.95))
    track(board, "N0V9", (207.5, 108.95), (207.5, 109.2), 0.60)
    track(board, "N1V8", (208.7, 107.6625), (208.7, 108.95))
    track(board, "N1V8", (208.7, 108.95), (208.7, 109.32), 0.60)


class LaunchTests(unittest.TestCase):
    def setUp(self):
        self.board = fixture()
        self.config = copy.deepcopy(CONFIG)

    def test_native_fixture_and_contiguous_launch(self):
        positive(self.board)
        helper.audit(self.board, self.config)

    def test_source_declaration_remains_inactive(self):
        declaration = helper.load(SOURCE_CONFIG)
        self.assertEqual({entry["id"] for entry in declaration["launches"]},
                         set(helper.REQUIRED))
        with self.assertRaisesRegex(ValueError, "invalid window"):
            helper.validate(self.board, declaration)

    def test_exact_two_identities(self):
        for change in (lambda c: c["launches"].pop(),
                       lambda c: c["launches"][0].update(net="N1V8"),
                       lambda c: c["launches"][1].update(pad="14"),
                       lambda c: c["launches"][0]["target"].update(ref="C_XU_VDDIO_17"),
                       lambda c: c["launches"][0].update(id="XU_VDDIO17_LOCAL")):
            candidate = copy.deepcopy(self.config)
            change(candidate)
            with self.assertRaises(ValueError):
                helper.validate(self.board, candidate)

    def test_declared_area_cap_cannot_authorize_wider_window(self):
        candidate = copy.deepcopy(self.config)
        candidate["launches"][0]["max_window_area_mm2"] = 10.0
        with self.assertRaisesRegex(ValueError, "widened or unbounded"):
            helper.validate(self.board, candidate)
        candidate = copy.deepcopy(self.config)
        candidate["status"] = "approved"
        with self.assertRaisesRegex(ValueError, "placement_review_required"):
            helper.validate(self.board, candidate)

    def test_missing_gap_and_missing_flare(self):
        with self.assertRaisesRegex(ValueError, "missing narrow launch"):
            helper.audit(self.board, self.config)
        track(self.board, "N0V9", (207.5, 107.6625), (207.5, 108.0))
        track(self.board, "N0V9", (207.5, 108.1), (207.5, 108.95))
        track(self.board, "N0V9", (207.5, 108.95), (207.5, 109.2), 0.60)
        positive17 = fixture()
        positive(positive17)
        # Both full paths are needed, including the ordinary continuation.
        with self.assertRaises(ValueError):
            helper.audit(self.board, self.config)
        for item in positive17.GetTracks():
            if item.GetNetname() == "N1V8" and p.ToMM(item.GetWidth()) >= 0.60:
                item.SetWidth(p.FromMM(0.15))
        with self.assertRaises(ValueError):
            helper.audit(positive17, self.config)

    def test_full_copper_containment_and_offsite(self):
        positive(self.board)
        track(self.board, "N1V8", (180, 115), (181, 115))
        with self.assertRaisesRegex(ValueError, "offsite"):
            helper.audit(self.board, self.config)
        self.board = fixture()
        positive(self.board)
        # Centreline is inside, but 0.15-mm copper extends 0.005 mm past x0.
        track(self.board, "N0V9", (207.32, 108.2), (207.32, 108.4))
        with self.assertRaisesRegex(ValueError, "partial"):
            helper.audit(self.board, self.config)
        self.board = fixture()
        positive(self.board)
        track(self.board, "N0V9", (207.5, 108.5), (207.5, 109.3))
        with self.assertRaisesRegex(ValueError, "partial"):
            helper.audit(self.board, self.config)

    def test_foreign_via_branch_and_wrong_layer(self):
        positive(self.board)
        track(self.board, "GND", (207.5, 108.0), (207.5, 108.2))
        with self.assertRaisesRegex(ValueError, "foreign-net"):
            helper.audit(self.board, self.config)
        self.board = fixture()
        positive(self.board)
        via = p.PCB_VIA(self.board)
        via.SetPosition(p.VECTOR2I_MM(207.5, 108.2))
        via.SetNet(self.board.FindNet("N0V9"))
        self.board.Add(via)
        with self.assertRaisesRegex(ValueError, "via in"):
            helper.audit(self.board, self.config)
        self.board = fixture()
        positive(self.board)
        via = p.PCB_VIA(self.board)
        via.SetPosition(p.VECTOR2I_MM(207.93, 108.2))
        via.SetWidth(p.FromMM(0.60))
        via.SetDrill(p.FromMM(0.30))
        via.SetNet(self.board.FindNet("N0V9"))
        self.board.Add(via)
        with self.assertRaisesRegex(ValueError, "via in"):
            helper.audit(self.board, self.config)
        self.board = fixture()
        positive(self.board)
        track(self.board, "N0V9", (207.5, 108.2), (207.4, 108.3))
        with self.assertRaises(ValueError):
            helper.audit(self.board, self.config)
        self.board = fixture()
        positive(self.board)
        track(self.board, "N0V9", (207.5, 108.2), (207.5, 108.3), layer=p.B_Cu)
        with self.assertRaisesRegex(ValueError, "offsite"):
            helper.audit(self.board, self.config)

    def test_emit_preserves_ordinary_rules_and_is_idempotent(self):
        positive(self.board)
        helper.audit(self.board, self.config)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.kicad_dru"
            path.write_text(ORDINARY)
            for _ in range(2):
                helper.emit(self.board, self.config, path)
            text = path.read_text()
            self.assertEqual(text.count('rule "DIGITAL_POWER_width"'), 1)
            self.assertIn('(rule "SENTINEL"', text)
            self.assertEqual(text.count('rule "xu_launch_xu_vdd14_local_width"'), 1)
            self.assertEqual(text.count('rule "xu_launch_xu_vddio17_local_width"'), 1)
            self.assertEqual(len([z for z in self.board.Zones() if z.GetZoneName().startswith("xu_launch_")]), 2)
            self.assertIn('(layer "F.Cu")', text)
            self.assertNotIn('(max 0.15mm)', text)
            path.write_text('(version 1)\n')
            with self.assertRaisesRegex(ValueError, "ordinary DIGITAL_POWER"):
                helper.emit(self.board, self.config, path)

    def test_cli_saved_native_fixture(self):
        positive(self.board)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            board = root / "fixture.kicad_pcb"
            saved = root / "saved.kicad_pcb"
            config = root / "launches.yaml"
            dru = root / "fixture.kicad_dru"
            p.SaveBoard(str(board), self.board)
            config.write_text(yaml.safe_dump(self.config))
            dru.write_text(ORDINARY)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(board), str(config),
                 "--emit-dru", str(dru), "--save", str(saved)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            reloaded = p.LoadBoard(str(saved))
            helper.audit(reloaded, self.config)
            self.assertEqual(len([z for z in reloaded.Zones() if z.GetIsRuleArea()]), 2)
            helper.emit(reloaded, self.config, dru)
            self.assertEqual(len([z for z in reloaded.Zones() if z.GetIsRuleArea()]), 2)

    def test_native_drc_local_width_and_offsite_negative(self):
        cli = shutil.which("kicad-cli")
        if cli is None:
            self.skipTest("kicad-cli unavailable")
        positive(self.board)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            board = root / "fixture.kicad_pcb"
            dru = root / "fixture.kicad_dru"
            pro = root / "fixture.kicad_pro"
            dru.write_text(ORDINARY)
            helper.audit(self.board, self.config)
            helper.emit(self.board, self.config, dru)
            p.SaveBoard(str(board), self.board)
            default = dict(name="Default", clearance=.15, track_width=.2,
                           via_diameter=.6, via_drill=.3, microvia_diameter=.3,
                           microvia_drill=.1, diff_pair_gap=.25, diff_pair_width=.2,
                           diff_pair_via_gap=.25, wire_width=6, bus_width=12,
                           line_style=0, pcb_color="rgba(0, 0, 0, 0.000)",
                           schematic_color="rgba(0, 0, 0, 0.000)",
                           priority=2147483647, tuning_profile="")
            power = dict(default, name="DIGITAL_POWER", priority=0,
                         track_width=.6)
            project = {
                "board": {"design_settings": {"rules": {"min_clearance": .15}}},
                "net_settings": {
                    "classes": [default, power], "netclass_assignments": {},
                    "netclass_patterns": [
                        {"netclass": "DIGITAL_POWER", "pattern": name}
                        for name in ("N0V9", "N1V8")],
                },
            }
            pro.write_text(json.dumps(project))

            def drc(name):
                report = root / name
                result = subprocess.run(
                    [cli, "pcb", "drc", "--severity-all", "--format", "json",
                     "--output", str(report), str(board)],
                    capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(report.read_text())

            local = drc("local.json")
            self.assertFalse([v for v in local["violations"]
                              if v["type"] == "track_width"], local["violations"])
            reloaded = p.LoadBoard(str(board))
            track(reloaded, "N1V8", (214, 114), (215, 114))
            p.SaveBoard(str(board), reloaded)
            pro.write_text(json.dumps(project))
            offsite = drc("offsite.json")
            width = [v for v in offsite["violations"]
                     if v["type"] == "track_width"]
            self.assertEqual(len(width), 1, offsite["violations"])
            self.assertIn("DIGITAL_POWER_width", width[0]["description"])


if __name__ == "__main__":
    unittest.main()
