"""Adversarial controls for the isolated AUDIO_EN owner-pocket packet."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('audio_pocket_trial', HERE / 'build_trial.py')
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)
check_spec = importlib.util.spec_from_file_location('audio_pocket_checker', trial.CHECKER)
checker = importlib.util.module_from_spec(check_spec)
check_spec.loader.exec_module(checker)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OwnerPocketReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = yaml.safe_load((HERE / 'p1_requirements.yaml').read_text())
        cls.contract = json.loads((HERE / 'coarse.json').read_text())
        cls.floor = yaml.safe_load((trial.BASE / 'floorplan.yaml').read_text())

    def evaluate(self, mutate):
        source, contract, floor = (copy.deepcopy(self.source), copy.deepcopy(self.contract),
                                    copy.deepcopy(self.floor))
        mutate(source, contract, floor)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            req, coarse, layout = root / 'source.yaml', root / 'contract.json', root / 'floor.yaml'
            req.write_text(yaml.safe_dump(source, sort_keys=False))
            if floor == self.floor:
                layout.write_bytes((trial.BASE / 'floorplan.yaml').read_bytes())
            else:
                layout.write_text(yaml.safe_dump(floor, sort_keys=False))
            if floor != self.floor:
                for pocket in source['branch_owner_pockets']:
                    pocket['floorplan_sha256'] = sha(layout)
                req.write_text(yaml.safe_dump(source, sort_keys=False))
            contract.update(source_sha256=sha(req), floorplan_sha256=sha(layout))
            coarse.write_text(json.dumps(contract))
            return checker.evaluate_coarse(
                trial.BOARD, coarse, sha(coarse), source_path=req,
                interface_path=trial.BASE / 'modular_plan.json', alias_path=trial.ALIASES,
                floorplan_path=layout, expected_source_sha256=sha(req),
                expected_interface_sha256=sha(trial.BASE / 'modular_plan.json'),
                expected_alias_sha256=sha(trial.ALIASES),
                expected_floorplan_sha256=sha(layout), diagnose_all=True)

    def test_positive_exact_denominator_no_credit(self):
        result = self.evaluate(lambda *_: None)
        self.assertEqual((result['status'], result['errors']), ('INCOMPLETE', []))
        self.assertFalse(result['p1_accepted'])
        self.assertFalse(result['routing_realized'])
        timing = next(r for r in result['allocations'] if r['id'] == 'adc_timing_xmos_bundle')
        branch = next(r for r in timing['reservations'] if r['id'] == trial.RESERVATION_ID)
        self.assertEqual(branch['status'], 'INCOMPLETE')
        self.assertIsNone(branch['capacity_slots'])
        self.assertEqual(len(branch['p2_obligations']), 11)
        self.assertEqual(branch['tree_obligation']['minimum_tree_edges'], 10)
        self.assertEqual(branch['return_obligation']['reference_layer'], 'In1.Cu')
        self.assertEqual(branch['physical_blockers'], [{
            'source_pad': 'R_AUDIO_PU.2', 'native_pad': 'R_AUDIO_PU.2',
            'block': 'quiet_power', 'foreign_regions': ['input_buck']}])

    def test_bad_pockets_and_branch_records_fail_closed(self):
        def row(source):
            return next(r for r in source['unresolved_multiterminal_branches']
                        if r['id'] == trial.BRANCH_ID)

        cases = {
            'clipped_body': (lambda s, c, f: s['branch_owner_pockets'][0].update(bbox=[22.5, 104, 24.5, 106.2]), 'native body/pad'),
            'foreign_native': (lambda s, c, f: s['branch_owner_pockets'][1].update(bbox=[21.3, 108.2, 26, 110.8]), 'foreign native body/pad'),
            'foreign_region': (lambda s, c, f: f['placement']['regions'].update(fake_foreign=[22.1, 104.1, 22.2, 104.2]), 'foreign source region'),
            'foreign_pattern': (lambda s, c, f: next(p for p in f['placement']['patterns']
                                    if 'R_AUDIO_PD' in p['match']).update(region='input_buck'),
                                'source pattern'),
            'stale_board_hash': (lambda s, c, f: s['branch_owner_pockets'][0].update(board_sha256='0'*64), 'hash drift'),
            'stale_alias_hash': (lambda s, c, f: s['branch_owner_pockets'][0].update(alias_sha256='0'*64), 'hash drift'),
            'stale_floor_hash': (lambda s, c, f: s['branch_owner_pockets'][0].update(floorplan_sha256='0'*64), 'hash drift'),
            'wrong_owner': (lambda s, c, f: s['branch_owner_pockets'][0].update(owner_block='analog_ch1'), 'owner/ref/branch'),
            'wrong_ref': (lambda s, c, f: s['branch_owner_pockets'][0].update(refs=['U_AUDIO']), 'native body/pad'),
            'wrong_endpoint_pocket': (lambda s, c, f: next(e for e in row(s)['endpoints']
                                        if e['source_pad'] == 'U_AUDIO.6').update(branch_owner_pocket_id='iso1'),
                                      'P2 pad-to-tree'),
            'duplicate_endpoint': (lambda s, c, f: row(s)['endpoints'].append(copy.deepcopy(row(s)['endpoints'][0])), 'endpoint denominator'),
            'omitted_endpoint': (lambda s, c, f: row(s)['endpoints'].pop(), 'endpoint denominator'),
            'remove_foreign_blocker': (lambda s, c, f: row(s).update(physical_blockers=[]), 'blocker inventory'),
            'capacity_claim': (lambda s, c, f: row(s).update(capacity_slots=1), 'geometry/capacity'),
            'pass_claim': (lambda s, c, f: row(s).update(status='PASS'), 'source fields'),
            'p2_access_removed': (lambda s, c, f: row(s)['p2_obligations'].pop(), 'P2 pad-to-tree'),
            'pocket_duty_removed': (lambda s, c, f: next(d for d in row(s)['p2_obligations']
                                        if d['source_pad'] == 'U_AUDIO.6').pop('branch_owner_pocket_id'),
                                    'P2 pad-to-tree'),
            'p3_tree_removed': (lambda s, c, f: row(s).update(tree_obligation={}), 'P2 return/P3 tree'),
            'return_removed': (lambda s, c, f: row(s).update(return_obligation={}), 'P2 return/P3 tree'),
            'as_physical_cell': (lambda s, c, f: s.update(physical_cells=[{
                'id': 'audio_pd', 'owner_block': 'quiet_power', 'refs': ['R_AUDIO_PD'],
                'transit': False}]), 'physical cell'),
            'reservation_pass': (lambda s, c, f: next(r for r in next(a for a in c['allocations']
                                       if a['id'] == 'adc_timing_xmos_bundle')['reservations']
                                       if r['id'] == trial.RESERVATION_ID).update(status='PASS'),
                                 'reservation fields'),
        }
        for label, (mutation, reason) in cases.items():
            with self.subTest(label=label):
                result = self.evaluate(mutation)
                self.assertEqual(result['status'], 'FAIL', result)
                self.assertTrue(result['errors'], result)
                self.assertIn(reason, json.dumps(result))
                self.assertFalse(result['p1_accepted'])


if __name__ == '__main__':
    unittest.main()
