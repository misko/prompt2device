"""Protect the exact two-ref first-match correction; never generate a PCB."""
import copy
import sys
import unittest
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO / 'skills/kicad-pcb/scripts'))
from generate_board_generic import BoardBuilder

REGULATOR_REFS = {'C_LDO_IN', 'C_LDO_OUT', 'C_LDO_NR4', 'C_LDO_NR5', 'C_LDO_EN'}


def builder(config):
    # Deliberately avoid __init__: initial_pose/patterns_for only need declarative
    # placement state. No board creation, footprint loading, or output writes.
    obj = object.__new__(BoardBuilder)
    obj.place_cfg = copy.deepcopy(config['placement'])
    obj.silk_cfg = copy.deepcopy(config['silk'])
    obj.say = lambda message: None
    obj.expand_repeats()
    outline = config['board']['outline']
    obj.X0, obj.Y0, obj.X1, obj.Y1 = (outline[k] for k in ('x0', 'y0', 'x1', 'y1'))
    return obj


def snapshot(config, refs):
    obj = builder(config)
    return {ref: {'pose': obj.initial_pose(ref),
                  'first_region': next((p['region'] for p in obj.patterns_for(ref)
                                        if 'region' in p), None)} for ref in refs}


class LdoRegionSelectionTests(unittest.TestCase):
    def test_whole_333_ref_first_match_delta(self):
        current = yaml.safe_load((PROJECT / '03_src/floorplan.yaml').read_text())
        refs = yaml.safe_load((PROJECT / '03_tscircuit/manifest.yaml').read_text())['components']
        self.assertEqual(len(refs), 333)
        self.assertEqual(len(set(refs)), 333)
        self.assertEqual({r for r in refs if r.startswith('C_LDO')},
                         REGULATOR_REFS | {'C_LDO_A', 'C_LDO_D'})
        power = next(p for p in current['placement']['patterns']
                     if 'F_IN' in p.get('match', []) and p.get('region') == 'power')
        self.assertEqual({r for r in power['match'] if r.startswith('C_LDO')}, REGULATOR_REFS)
        self.assertNotIn('C_LDO*', power['match'])
        # The local-placement correction now pins these two capacitors at their
        # physical ADC pin groups. Remove only those pins from this historical
        # fallback fixture so the original first-match regression stays live;
        # the separate local-placement tests enforce the new exact anchors.
        for ref in ('C_LDO_A', 'C_LDO_D'):
            current['placement']['anchors'].pop(ref)
        previous = copy.deepcopy(current)
        prior_power = next(p for p in previous['placement']['patterns'] if p == power)
        prior_power['match'] = [r for r in power['match'] if r not in REGULATOR_REFS] + ['C_LDO*']
        before, after = snapshot(previous, refs), snapshot(current, refs)
        self.assertEqual({r for r in refs if before[r] != after[r]}, {'C_LDO_A', 'C_LDO_D'})
        for ref in ('C_LDO_A', 'C_LDO_D'):
            self.assertEqual(before[ref], {'pose': (47.5, 69.0, 0.0, False), 'first_region': 'power'})
            self.assertEqual(after[ref], {'pose': (94.5, 70.0, 0.0, False), 'first_region': 'adc'})
        for ref in REGULATOR_REFS:
            self.assertEqual(after[ref]['first_region'], 'power')


if __name__ == '__main__':
    unittest.main()
