#!/usr/bin/env python3
"""Focused contract tests for immutable prepared-workspace DRC authority."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import route_and_stitch_generic as driver  # noqa: E402


class Result:
    returncode = 0


class PreparedDrcAuthorityTest(unittest.TestCase):
    def fixture(self, root):
        krt = root / 'krt'
        py = krt / '.venv/bin/python'
        fixer = krt / 'fix_kicad_drc_settings.py'
        py.parent.mkdir(parents=True)
        py.write_text('')
        fixer.write_text('')
        overrides = root / 'fab.txt'
        overrides.write_text('via_diameter=.25\nvia_drill=.15\n')
        board = root / 'r0.kicad_pcb'
        board.write_text('')
        project = {
            'board': {
                'drc_severities': {'clearance': 'error'},
                'design_settings': {'rules': {'min_hole_clearance': .25}},
            },
            'net_settings': {
                'classes': [{'name': 'POWER', 'track_width': 1.2}],
                'netclass_patterns': [{'netclass': 'POWER', 'pattern': '5V'}],
            },
        }
        board.with_suffix('.kicad_pro').write_text(json.dumps(project))
        cfg = {
            '_root': root,
            'project': {'build_dir': 'build'},
            'route': {'krt': str(krt), 'common': {
                'fab_tier': 'advanced', 'fab_overrides': str(overrides)}},
        }
        return cfg, board

    def test_command_preserves_spec_authorities(self):
        with tempfile.TemporaryDirectory() as td:
            cfg, board = self.fixture(Path(td))
            cmd = driver._prepared_drc_authority_command(cfg, board)
            self.assertEqual(cmd[:3], [str(Path(td)/'krt/.venv/bin/python'),
                                      str(Path(td)/'krt/fix_kicad_drc_settings.py'),
                                      str(board)])
            self.assertIn('--fab-tier', cmd)
            self.assertIn('--fab-overrides', cmd)
            self.assertEqual(cmd[cmd.index('--hole-clearance') + 1], '0.25')
            for flag in ('--no-clamp-netclasses', '--keep-courtyards',
                         '--keep-mask', '--keep-footprint', '--keep-thermal'):
                self.assertIn(flag, cmd)

    def test_tier_only_preserves_conservative_source_floors(self):
        # A capability selector must not lower source floors at prep/import.
        # The control models the actual fixer mutation that broke pod sealing.
        for tier in ('standard', 'advanced'):
            with self.subTest(tier=tier), tempfile.TemporaryDirectory() as td:
                cfg, board = self.fixture(Path(td))
                cfg['route']['common'] = {'fab_tier': tier}
                pro = board.with_suffix('.kicad_pro')
                data = json.loads(pro.read_text())
                data['board']['design_settings'] = {'rules': {
                    'min_hole_clearance': .25, 'min_hole_to_hole': .5,
                    'min_via_diameter': .6, 'min_through_hole_diameter': .3}}
                data['net_settings']['classes'].append({
                    'name': 'Default', 'clearance': .25,
                    'via_diameter': .6, 'via_drill': .3})
                pro.write_text(json.dumps(data))
                before = pro.read_bytes()

                def lower_floors(*args, **kwargs):
                    changed = json.loads(pro.read_text())
                    changed['board']['design_settings']['rules'].update(
                        min_hole_clearance=.15, min_hole_to_hole=.2,
                        min_via_diameter=.25, min_through_hole_diameter=.15)
                    changed['net_settings']['classes'][-1].update(
                        clearance=.15, via_diameter=.25, via_drill=.15)
                    pro.write_text(json.dumps(changed))
                    return Result()

                with patch.object(driver, 'run_bounded',
                                  side_effect=lower_floors) as runner:
                    driver._sync_prepared_drc_authority(cfg, board)
                self.assertEqual(pro.read_bytes(), before,
                                 'tier-only sync lowered authoritative floors')
                runner.assert_not_called()

    def test_explicit_override_still_synchronizes_floors(self):
        with tempfile.TemporaryDirectory() as td:
            cfg, board = self.fixture(Path(td))
            pro = board.with_suffix('.kicad_pro')

            def apply_override(*args, **kwargs):
                changed = json.loads(pro.read_text())
                changed['board']['design_settings'] = {'rules': {
                    'min_hole_clearance': .25,
                    'min_via_diameter': .3, 'min_through_hole_diameter': .2}}
                pro.write_text(json.dumps(changed))
                return Result()

            with patch.object(driver, 'run_bounded',
                              side_effect=apply_override) as runner:
                driver._sync_prepared_drc_authority(cfg, board)
            runner.assert_called_once()
            rules = json.loads(pro.read_text())['board']['design_settings']['rules']
            self.assertEqual(rules['min_hole_clearance'], .25)
            self.assertEqual(rules['min_via_diameter'], .3)
            self.assertEqual(rules['min_through_hole_diameter'], .2)

    def test_sync_rejects_named_netclass_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            cfg, board = self.fixture(Path(td))

            def mutate(*args, **kwargs):
                pro = board.with_suffix('.kicad_pro')
                data = json.loads(pro.read_text())
                data['net_settings']['classes'][0]['track_width'] = .2
                pro.write_text(json.dumps(data))
                return Result()

            with patch.object(driver, 'run_bounded', side_effect=mutate):
                with self.assertRaisesRegex(driver.RouteConfigError,
                                            'changed named netclasses'):
                    driver._sync_prepared_drc_authority(cfg, board)


if __name__ == '__main__':
    unittest.main()
