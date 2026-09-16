#!/usr/bin/env python3
"""Focused tests for pre-route owner and corridor decisions."""
import sys
import tempfile
import contextlib
import io
import json
from unittest.mock import patch

import yaml
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from route_ownership_preflight import audit_config  # noqa: E402
import route_ownership_preflight as ownership
import route_and_stitch_generic as driver


def base_cfg():
    return {
        "prep": {"waves": {"groups": {"pwr": ["P5V"],
                                         "xtal": ["XTAL1", "XTAL2"],
                                         "sig": ["SCL"]}}},
        "route": {
            "common": {"layers": ["F.Cu", "B.Cu"]},
            "waves": [
                {"name": "xtal", "group": "xtal", "layers": ["F.Cu"]},
                {"name": "sig", "group": "sig"},
                {"name": "pwr", "group": "pwr"},
            ],
        },
    }


NETS = {"classes": {"POWER": {"nets": ["P5V"],
                                "routing": "pour_or_wide_track"}}}
PAD_COUNTS = {"P5V": 22, "XTAL1": 2, "XTAL2": 2, "SCL": 2}
BOARD_NETS = set(PAD_COUNTS)


class RouteOwnershipPreflightTest(unittest.TestCase):
    def test_many_pad_power_without_owner_fails(self):
        result = audit_config(base_cfg(), pad_counts=PAD_COUNTS,
                              board_nets=BOARD_NETS, nets_cfg=NETS)
        self.assertEqual(result["verdict"], "FAIL")
        self.assertIn("O-PWR", {row["code"] for row in result["findings"]})

    def test_deterministic_owner_cannot_also_be_generic_wave(self):
        cfg = base_cfg()
        cfg["route"]["ownership"] = {"nets": {"P5V": {
            "topology": "wide_trunk", "owner": "prep.seed_stubs",
            "why": "reviewed 3 A trunk",
        }}}
        result = audit_config(cfg, pad_counts=PAD_COUNTS,
                              board_nets=BOARD_NETS, nets_cfg=NETS)
        self.assertIn("O-DOUBLE", {row["code"] for row in result["findings"]})

    def test_owned_power_excluded_from_wave_passes(self):
        cfg = base_cfg()
        cfg["route"]["waves"] = cfg["route"]["waves"][:2]
        cfg["route"]["ownership"] = {"nets": {"P5V": {
            "topology": "wide_trunk", "owner": "prep.seed_stubs",
            "why": "reviewed 3 A trunk",
        }}}
        result = audit_config(cfg, pad_counts=PAD_COUNTS,
                              board_nets=BOARD_NETS, nets_cfg=NETS)
        self.assertEqual(result["verdict"], "PASS")

    def test_constrained_corridor_must_claim_first(self):
        cfg = base_cfg()
        cfg["route"]["waves"][:2] = list(reversed(cfg["route"]["waves"][:2]))
        cfg["route"]["ownership"] = {
            "corridors": {"hub_top": {
                "claim_order": ["sig", "xtal"],
                "why": "shared hub top escape",
            }}
        }
        result = audit_config(cfg, pad_counts={"SCL": 2, "XTAL1": 2,
                                               "XTAL2": 2},
                              board_nets={"SCL", "XTAL1", "XTAL2"},
                              nets_cfg={})
        self.assertIn("O-FLEX", {row["code"] for row in result["findings"]})



class ProjectRootTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ownership-root-")
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "project"
        (self.project / "03_src/rules").mkdir(parents=True)
        (self.project / "04_kicad").mkdir()
        (self.project / "06_build/probe").mkdir(parents=True)
        self.board = self.project / "04_kicad/board.kicad_pcb"
        self.board.write_text("board reader is mocked for path/authority tests")
        self.cfg = base_cfg()
        self.cfg["project"] = {"board": "04_kicad/board.kicad_pcb"}
        self.cfg["route"]["ownership"] = {"nets": {"P5V": {
            "topology": "wide_trunk", "owner": "route.wave",
            "allow_generic_router": True, "why": "explicit fixture trunk"}}}
        self.canonical = self.project / "03_src/route.yaml"
        self.diagnostic = self.project / "06_build/probe/route.yaml"
        for path in (self.canonical, self.diagnostic):
            path.write_text(yaml.safe_dump(self.cfg))
        (self.project / "03_src/rules/nets.yaml").write_text(yaml.safe_dump(NETS))

    def grade(self, config, root=None, board=None):
        out = Path(self.tmp.name) / "receipt.json"
        out.unlink(missing_ok=True)
        args = [str(config), "--json", str(out)]
        if root is not None:
            args += ["--root", str(root)]
        if board is not None:
            args += ["--board", str(board)]
        with patch.object(ownership, "_load_board_facts", return_value=(BOARD_NETS, PAD_COUNTS)) as native:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = ownership.main(args)
        return rc, json.loads(out.read_text()) if out.exists() else None, native

    def test_canonical_without_explicit_root_remains_supported(self):
        rc, result, native = self.grade(self.canonical)
        self.assertEqual(rc, 0)
        self.assertEqual(result["verdict"], "PASS")
        native.assert_called_once_with(self.board)

    def test_canonical_with_root_retains_board_local_rules(self):
        nested = self.project / "03_src/board_a"
        (nested / "rules").mkdir(parents=True)
        route = nested / "route.yaml"
        route.write_text(self.canonical.read_text())
        rules = nested / "rules/nets.yaml"
        rules.write_text(yaml.safe_dump(NETS))
        rc, result, native = self.grade(route, self.project)
        self.assertEqual(rc, 0)
        self.assertEqual(result["inputs"]["nets"], str(rules))
        native.assert_called_once_with(self.board)

    def test_diagnostic_with_root_uses_current_project_rules(self):
        rc, result, native = self.grade(self.diagnostic, self.project)
        self.assertEqual(rc, 0)
        self.assertEqual(result["inputs"]["nets"], str(self.project / "03_src/rules/nets.yaml"))
        native.assert_called_once_with(self.board)

    def test_diagnostic_without_root_is_refused(self):
        rc, result, native = self.grade(self.diagnostic)
        self.assertEqual(rc, 2)
        self.assertIsNone(result)
        native.assert_not_called()

    def test_mismatched_root_is_refused_before_board_read(self):
        other = Path(self.tmp.name) / "other"
        (other / "03_src").mkdir(parents=True)
        for config in (self.canonical, self.diagnostic):
            with self.subTest(config=config):
                rc, result, native = self.grade(config, other)
                self.assertEqual(rc, 2)
                self.assertIsNone(result)
                native.assert_not_called()

    def test_diagnostic_cannot_shadow_source_power_rules(self):
        self.cfg["route"].pop("ownership")
        self.diagnostic.write_text(yaml.safe_dump(self.cfg))
        (self.diagnostic.parent / "rules").mkdir()
        (self.diagnostic.parent / "rules/nets.yaml").write_text("{}")
        rc, result, _ = self.grade(self.diagnostic, self.project)
        self.assertEqual(rc, 1)
        self.assertIn("O-PWR", {x["code"] for x in result["findings"]})

    def test_config_symlink_outside_project_is_refused(self):
        external = Path(self.tmp.name) / "external.yaml"
        external.write_text(self.diagnostic.read_text())
        self.diagnostic.unlink()
        self.diagnostic.symlink_to(external)
        rc, _, native = self.grade(self.diagnostic, self.project)
        self.assertEqual(rc, 2)
        native.assert_not_called()

    def test_explicit_root_cannot_grade_external_board(self):
        external = Path(self.tmp.name) / "external.kicad_pcb"
        external.write_text("external")
        rc, _, native = self.grade(self.diagnostic, self.project, external)
        self.assertEqual(rc, 2)
        native.assert_not_called()

    def test_build_directory_symlink_cannot_escape_root(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        copied = outside / "route.yaml"
        copied.write_text(self.canonical.read_text())
        alias = self.project / "06_build/external"
        alias.symlink_to(outside, target_is_directory=True)
        rc, _, native = self.grade(alias / "route.yaml", self.project)
        self.assertEqual(rc, 2)
        native.assert_not_called()

    def test_build_config_requires_canonical_source_rules(self):
        (self.project / "03_src/rules/nets.yaml").unlink()
        rc, result, _ = self.grade(self.diagnostic, self.project)
        self.assertEqual(rc, 2)
        self.assertIsNone(result)

    def test_build_rules_cannot_resolve_outside_project(self):
        rules = self.project / "03_src/rules/nets.yaml"
        outside = Path(self.tmp.name) / "external-rules.yaml"
        outside.write_text(rules.read_text())
        rules.unlink()
        rules.symlink_to(outside)
        rc, result, _ = self.grade(self.diagnostic, self.project)
        self.assertEqual(rc, 2)
        self.assertIsNone(result)

    def test_driver_passes_its_resolved_root(self):
        cfg = dict(self.cfg, _root=self.project, _path=self.diagnostic)
        cfg["route"]["ownership_preflight"] = {"mode": "enforce"}
        with patch.object(driver, "run_bounded") as run:
            run.return_value.returncode = 0
            with contextlib.redirect_stdout(io.StringIO()):
                driver._route_ownership_gate(cfg, self.project / "06_build")
        argv = run.call_args.args[0]
        self.assertIn("--root", argv)
        self.assertEqual(argv[argv.index("--root") + 1], str(self.project))


if __name__ == "__main__":
    unittest.main()
