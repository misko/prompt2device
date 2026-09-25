#!/usr/bin/env python3
"""Focused current-Crow graph/attempt boundary regression."""
import json
import unittest

import audit


class CurrentCrowGraphTest(unittest.TestCase):
    def test_unspent_root_and_one_failure_backtrack(self):
        receipt = audit.audit()
        self.assertEqual(receipt['coverage']['components_singly_owned'], 569)
        self.assertEqual(receipt['coverage']['crossing_nets_exactly_declared'], 59)
        self.assertEqual(receipt['p1_root']['state'], 'READY')
        self.assertEqual(receipt['p1_root']['attempts'], 0)
        self.assertEqual(receipt['p1_root']['max_attempts'], 1)
        self.assertEqual(receipt['counterfactual_only']['one_failed_current_subject_attempt'],
                         'BACKTRACK_REQUIRED')
        self.assertEqual(receipt['recording_decision'], 'NO_TASK_ATTEMPT_WRITTEN_OR_OBSERVED')

    def test_archived_failure_cannot_be_observed_as_current_root(self):
        plan = json.loads(audit.PLAN.read_text())
        circuit = json.loads(audit.CIRCUIT.read_text())
        attempt = audit.ARCHIVED[-1].relative_to(audit.PROJECT).as_posix()
        with self.assertRaisesRegex(audit.graph.ModularDesignError, 'unknown work item'):
            audit.graph.evaluate(plan, circuit, [{'attempt_path':attempt}],
                                 evidence_root=audit.PROJECT)


if __name__ == '__main__':
    unittest.main()
