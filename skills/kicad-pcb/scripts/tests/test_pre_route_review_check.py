#!/usr/bin/env python3
"""Regression tests for stable, electrically exact PR-REVIEW netlist hashes."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "pre_route_review_check.py"
SPEC = importlib.util.spec_from_file_location("pre_route_review_check", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def netlist(date: str, tstamp: str, net: str = "VBUS") -> str:
    return f'''(export
  (version "E")
  (design
    (source "board.kicad_sch")
    (date "{date}")
    (sheet (title_block (date "2026-08-01"))))
  (components
    (comp (ref "U1")
      (value "IC")
      (footprint "Package:QFN")
      (tstamps "{tstamp}")))
  (nets
    (net (code "1") (name "{net}")
      (node (ref "U1") (pin "1") (pinfunction "VIN")))))
'''


class NetlistDigestTest(unittest.TestCase):
    def digest(self, content: str) -> str:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "board.net"
            path.write_text(content)
            return MODULE.netlist_digest(path)

    def test_export_clock_and_instance_uuid_are_ignored(self) -> None:
        first = self.digest(netlist(
            "2026-08-01T01:02:03", "11111111-1111-1111-1111-111111111111"))
        second = self.digest(netlist(
            "2026-08-02T09:08:07", "22222222-2222-2222-2222-222222222222"))
        self.assertEqual(first, second)

    def test_electrical_change_invalidates_review(self) -> None:
        first = self.digest(netlist(
            "2026-08-01T01:02:03", "11111111-1111-1111-1111-111111111111", "VBUS"))
        changed = self.digest(netlist(
            "2026-08-02T09:08:07", "22222222-2222-2222-2222-222222222222", "GND"))
        self.assertNotEqual(first, changed)


class DesignRulesDigestTest(unittest.TestCase):
    def project(self, route: str) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        project = Path(temporary.name)
        rules = project / "03_src" / "rules"
        rules.mkdir(parents=True)
        (rules / "requirements.yaml").write_text("schema: 1\n")
        (project / "03_src" / "route.yaml").write_text(route)
        return temporary, project

    def test_search_controls_are_nonsemantic_but_width_remains_semantic(self) -> None:
        base = '''route:
  waves:
  - name: clocks
    group: clocks
    layers: [F.Cu]
    track_width: 0.36
    clearance: 0.25
'''
        with_grid = base.replace(
            "    track_width",
            "    grid_step: 0.05\n    ordering: original\n"
            "    via_cost: 1000\n    via_proximity_cost: 0\n"
            "    track_width")
        narrower = base.replace("track_width: 0.36", "track_width: 0.20")
        fixtures = [self.project(text) for text in (base, with_grid, narrower)]
        try:
            digests = [MODULE.design_rules_digest(project) for _, project in fixtures]
        finally:
            for temporary, _ in fixtures:
                temporary.cleanup()
        self.assertEqual(digests[0], digests[1])
        self.assertNotEqual(digests[0], digests[2])


if __name__ == "__main__":
    unittest.main()
