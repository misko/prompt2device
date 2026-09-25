#!/usr/bin/env python3
"""Exact-board negative integration tests for two-terminal crossing credit."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import build_trial
import yaml


class ExactTimingPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('two_terminal_packet_checker',
                                                       build_trial.CHECKER)
        cls.checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.checker)
        cls.base = json.loads((build_trial.HERE/'coarse.json').read_text())

    def evaluate(self, contract):
        with tempfile.TemporaryDirectory(prefix='crow-two-term-test-') as tmp:
            path = Path(tmp)/'coarse.json'
            path.write_text(json.dumps(contract, indent=2)+'\n')
            return self.checker.evaluate_coarse(
                build_trial.BOARD, path, build_trial.sha(path),
                source_path=build_trial.HERE/'p1_requirements.yaml',
                interface_path=build_trial.HERE/'modular_plan.json',
                alias_path=build_trial.ALIASES,
                floorplan_path=build_trial.HERE/'floorplan.yaml',
                expected_source_sha256=build_trial.sha(build_trial.HERE/'p1_requirements.yaml'),
                expected_interface_sha256=build_trial.sha(build_trial.HERE/'modular_plan.json'),
                expected_alias_sha256=build_trial.sha(build_trial.ALIASES),
                expected_floorplan_sha256=build_trial.sha(build_trial.HERE/'floorplan.yaml'),
                diagnose_all=True)

    def test_exact_four_crossings_have_no_item_diagnostics_or_credit(self):
        result = self.evaluate(self.base)
        self.assertEqual(result['status'], 'FAIL')
        self.assertFalse(result['p1_accepted'])
        self.assertFalse(result['routing_realized'])
        self.assertFalse([d for d in result['diagnostics']
                          if d['allocation'] == 'adc_timing_xmos_bundle'])

    def test_wrong_witness_kind_or_bogus_capacity_is_rejected(self):
        changed = copy.deepcopy(self.base)
        allocation = next(a for a in changed['allocations']
                          if a['id'] == 'adc_timing_xmos_bundle')
        witness = next(w for w in allocation['boundary_witnesses']
                       if w['net'] == 'AUDIO_MCLK_1V8')
        witness['kind'] = 'unresolved_multiterminal_branch'
        result = self.evaluate(changed)
        self.assertTrue(any(d['allocation'] == 'adc_timing_xmos_bundle' and
                            'identity mismatch' in d['reason'] for d in result['diagnostics']))
        changed = copy.deepcopy(self.base)
        allocation = next(a for a in changed['allocations']
                          if a['id'] == 'adc_timing_xmos_bundle')
        reserve = next(r for r in allocation['reservations']
                       if r['nets'] == ['AUDIO_MCLK_1V8'])
        reserve['capacity_slots'] = 1
        row = next(r for r in yaml.safe_load((build_trial.HERE/'p1_requirements.yaml').read_text())
                   ['unresolved_two_terminal_crossings']
                   if r['net'] == 'AUDIO_MCLK_1V8')
        normalized = {row['id']:{**row, '_kind':'unresolved_two_terminal_crossing'}}
        with self.assertRaisesRegex(self.checker.ContractError,
                                    'cannot reserve geometry/capacity'):
            self.checker._is_geometry_free_branch_reservation(reserve, normalized)


if __name__ == '__main__':
    unittest.main()
