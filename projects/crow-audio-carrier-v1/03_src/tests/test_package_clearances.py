"""Exact source package-gap scopes; saved native DRC is separate evidence.

Positive coverage is run RED on 06d3bd3e's actual source before adding scopes.
This checks native library lands independently of the text rule emitter.
It does not claim generated-board, assembly, or route acceptance.
"""
import copy
from pathlib import Path
import subprocess
import unittest

import pcbnew
import yaml
from test_digital_launch_source import native_geometry, overlaps
from test_route_source_contract import load_source

SRC = Path(__file__).resolve().parents[1]
ROOT = SRC.parents[2]
BASE = '06d3bd3e679e22381e4be88cbcaa6c24b2c1bb30'
PREFIX = 'PKG_PAD_'
TARGETS = {f'{PREFIX}ESD{i}_2_3': (f'U_ESD{i}.2', f'U_ESD{i}.3', .15)
           for i in range(1, 9)}
TARGETS.update({f'{PREFIX}CLK_{a}_{b}': (f'U_CLK.{a}', f'U_CLK.{b}', .15)
                for a, b in [(1, 2), (2, 3), (3, 4), (5, 6), (6, 7), (7, 8)]})
TARGETS[f'{PREFIX}QIN_3_4'] = ('Q_IN.3', 'Q_IN.4', .23)


def frozen(name, revision=BASE):
    return yaml.safe_load(subprocess.check_output(
        ['git', 'show', f'{revision}:{(SRC/name).relative_to(ROOT)}'],
        cwd=ROOT, text=True, timeout=15))


def gap_mm(a, b):
    lo, hi = 0, 1_000_000
    assert not pcbnew.SHAPE.Collide(a, b, lo), 'copper touches'
    assert pcbnew.SHAPE.Collide(a, b, hi), 'unexpected distant pair'
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if pcbnew.SHAPE.Collide(a, b, mid): hi = mid
        else: lo = mid
    return lo / 1e6


def inspect(floor, nets, geometry):
    errors = []; measured = []
    rules = [r for r in nets['scoped_clearances'] if r['zone'].startswith(PREFIX)]
    areas = {r['name']: r for r in floor['keepouts'] if r['name'].startswith(PREFIX)}
    if {r['zone'] for r in rules} != set(TARGETS) or len(rules) != 15:
        errors.append('rule-coverage')
    if set(areas) != set(TARGETS): errors.append('area-coverage')
    pads = {p['id']: p for p in geometry['pads']}
    for rule in rules:
        name = rule['zone']
        if name not in TARGETS or name not in areas: continue
        pa, pb, required = TARGETS[name]; area = areas[name]
        if set(rule) != {'zone', 'nets_a', 'nets_b', 'clearance', 'pads_only', 'why'}:
            errors.append('rule-fields')
        if rule.get('pads_only') is not True: errors.append('not-pad-only')
        if rule.get('nets_a') != [pads[pa]['net']] or rule.get('nets_b') != [pads[pb]['net']]:
            errors.append('wrong-net-pair')
        if rule.get('clearance') != f'{required:.2f}mm': errors.append('wrong-gap')
        if 'ADR0020' not in rule.get('why', ''): errors.append('missing-evidence')
        if set(area) != {'name', 'layers', 'deny', 'rect'} or area['layers'] != ['F.Cu'] or area['deny']:
            errors.append('area-kind')
        members = [p['id'] for p in geometry['pads'] if overlaps(p['shape'], area)]
        if set(members) != {pa, pb}: errors.append('foreign-or-missing-pad')
        boxes = [pads[p]['shape'].BBox() for p in (pa, pb)]
        bound = [min(b.GetLeft() for b in boxes)/1e6, min(b.GetTop() for b in boxes)/1e6,
                 max(b.GetRight() for b in boxes)/1e6, max(b.GetBottom() for b in boxes)/1e6]
        if any(abs(x-y) > .011 for x,y in zip(bound, area['rect'])):
            errors.append('unbounded-area')
        gap = gap_mm(pads[pa]['shape'], pads[pb]['shape'])
        if abs(gap-required) > .000002: errors.append('native-gap-changed')
        if gap < floor['design_rules']['min_clearance']: errors.append('below-fab-floor')
        measured.append(dict(zone=name, pads=[pa,pb], gap_mm=gap, members=members))
    return errors, measured


class PackageClearanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor, cls.route, cls.nets, *_ = load_source()
        cls.geometry = native_geometry(cls.floor)

    def test_all_fifteen_exact_pad_pairs_are_bounded(self):
        errors, rows = inspect(self.floor, self.nets, self.geometry)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 15)

    def test_actual_old_source_is_rejected(self):
        self.assertIn('rule-coverage', inspect(frozen('floorplan.yaml'),
            frozen('rules/nets.yaml'), self.geometry)[0])

    def test_hostile_widened_rules_are_rejected(self):
        for field, value, expected in [('pads_only', False, 'not-pad-only'),
                ('nets_a', ['GND'], 'wrong-net-pair'),
                ('clearance', '0.12mm', 'wrong-gap'), ('why', '', 'missing-evidence')]:
            bad = copy.deepcopy(self.nets)
            rule = next(r for r in bad['scoped_clearances'] if r['zone'].startswith(PREFIX))
            rule[field] = value
            self.assertIn(expected, inspect(self.floor, bad, self.geometry)[0])

    def test_hostile_foreign_pad_area_is_rejected(self):
        bad = copy.deepcopy(self.floor)
        area = next(a for a in bad['keepouts'] if a['name'].startswith(PREFIX))
        area['rect'] = [20, 20, 170, 120]
        errors, _ = inspect(bad, self.nets, self.geometry)
        self.assertIn('foreign-or-missing-pad', errors)
        self.assertIn('unbounded-area', errors)

    def test_package_scopes_and_fabrication_floors_are_preserved(self):
        accepted_floor = frozen('floorplan.yaml', '1b725986')
        accepted_nets = frozen('rules/nets.yaml', '1b725986')
        areas = lambda floor: [a for a in floor['keepouts'] if a['name'].startswith(PREFIX)]
        rules = lambda nets: [r for r in nets['scoped_clearances'] if r['zone'].startswith(PREFIX)]
        self.assertEqual(len(areas(self.floor)), 15)
        self.assertEqual([a for a in areas(self.floor) if 'ESD' not in a['name'] and 'CLK' not in a['name']],
                         [a for a in areas(accepted_floor) if 'ESD' not in a['name'] and 'CLK' not in a['name']])
        # ESD and relocated clock regions follow their current native pads. The independent
        # native-pad coverage test above grades each exact pair and bounding slack.
        for i in range(1,9):
            area=next(a for a in areas(self.floor) if a['name']==f'PKG_PAD_ESD{i}_2_3')
            x=40.865+32*(i-1) if i<5 else 39.440+32*(i-5); y=34.070 if i<5 else 105.070
            self.assertEqual(area['layers'],['F.Cu'])
            self.assertEqual(area['rect'],[round(x,3),y,round(x+.695,3),round(y+.860,3)])
        self.assertEqual(rules(self.nets), rules(accepted_nets))
        self.assertEqual(self.floor['design_rules'], accepted_floor['design_rules'])


if __name__ == '__main__': unittest.main(verbosity=2)
