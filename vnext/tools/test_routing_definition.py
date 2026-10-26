"""Routing metadata regressions; not router or engineering acceptance tests."""
import json
from pathlib import Path
import tempfile
import unittest

import coverage
import task


class RoutingDefinition(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        self.graph = json.loads((source / coverage.GRAPH).read_text())
        self.inventory = json.loads((source / coverage.COVERAGE).read_text())
        for row in self.inventory['stages']:
            if row['backing'] == 'local_procedure':
                self.write(row['procedure'], 'Fixture procedure, not acceptance.')
        self.write('skills/workflow-orchestrator/references/recover.md', 'Fixture recovery.')
        self.route = next(s for s in self.graph['stages'] if s['spec']['id'] == 'KICAD-ROUTING')
        # Retain a definition-only fixture even after the live adapter is ported.
        self.route.pop('local_execution', None)
        self.route['local_definition'] = {
            'contract': 'skills/pcb-design/workflow/stages/routing.md',
            'status': 'definition_only', 'missing': ['fixture implementation']}

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)

    def load(self):
        self.write(coverage.GRAPH, json.dumps(self.graph))
        self.write(coverage.COVERAGE, json.dumps(self.inventory))
        return coverage.load(self.root)

    def test_definition_is_not_executable_or_dispatchable(self):
        self.load()
        self.assertIn('definition only; execution unavailable', coverage.render(self.root))
        with self.assertRaisesRegex(task.PacketError, 'unsupported task'):
            task.build_packet(self.root, self.root, [], 'routing')

    def test_definition_cannot_masquerade_as_execution(self):
        self.route['local_execution'] = {'tool': 'invented.py'}
        with self.assertRaisesRegex(coverage.CoverageError, 'definition-only'):
            self.load()

    def test_missing_implementation_cannot_disappear(self):
        self.route['local_definition']['missing'] = []
        with self.assertRaisesRegex(coverage.CoverageError, 'definition-only'):
            self.load()

    def test_backtrack_destinations_are_actual_stages(self):
        self.route['recovery']['destinations']['placement_geometry'] = 'MISSING-STAGE'
        with self.assertRaisesRegex(coverage.CoverageError, 'recovery'):
            self.load()

    def test_recovery_does_not_claim_automatic_execution(self):
        self.route['recovery']['mode'] = 'automatic_dispatch'
        with self.assertRaisesRegex(coverage.CoverageError, 'recovery'):
            self.load()

    def test_routing_preserves_upstream_and_mating_prerequisites(self):
        self.load()
        self.assertEqual(set(self.route['spec']['requires']),
                         {'placement_reviewed', 'mating_clearance'})
        destinations = self.route['recovery']['destinations']
        self.assertEqual(destinations['placement_geometry'], 'KICAD-PLACEMENT')
        self.assertEqual(destinations['circuit_contradiction'], 'KICAD-SCHEMATIC')
        self.assertEqual(destinations['system_choice'], 'PCB-ARCHITECTURE')


if __name__ == '__main__':
    unittest.main()
