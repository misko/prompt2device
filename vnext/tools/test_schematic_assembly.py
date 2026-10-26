"""Synthetic multi-board regression; not Crow electrical or stage acceptance.

Run: python3 tools/test_schematic_assembly.py
Requires real KiCad/Poppler as pinned by native_schematic. Two resistor-only
designs model one hub and eight identical nodes. Explicit expected membership
and wiring are test specifications, never derived from a candidate or export.
All generated files and deliberate corruption stay in temporary directories.
"""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import native_schematic as native
import schematic_assembly as assembly


FIXTURE = Path(__file__).parent / 'test-fixtures' / 'native-smoke.json'
MEMBERSHIP = {
    'version': 1, 'nets': ['A', 'B'], 'components': {
        'R1': {'value': '1k', 'footprint': 'Resistor_SMD:R_0603_1608Metric',
               'pins': ['1', '2']},
        'R2': {'value': '2k', 'footprint': 'Resistor_SMD:R_0603_1608Metric',
               'pins': ['1', '2']},
    },
}


def terminal(instance, pin, net):
    return {'instance': instance, 'ref': 'R1', 'pin': pin, 'net': net}


class AssemblyRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='vnext-assembly-base-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.base = Path(cls.temp.name)
        for board in ('hub', 'node'):
            source = json.loads(FIXTURE.read_text())
            source['title'] = f'Synthetic {board} - not Crow hardware'
            path = cls.base / f'{board}.json'
            path.write_text(json.dumps(source))
            (cls.base / f'{board}-members.json').write_text(json.dumps(MEMBERSHIP))
            native.build(path, cls.base / f'{board}-out')

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='vnext-assembly-case-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        shutil.copytree(self.base, self.root, dirs_exist_ok=True)
        self.manifest = {
            'version': 2,
            'boards': {b: {'source': f'{b}.json',
                           'membership': f'{b}-members.json',
                           'output': f'{b}-out'} for b in ('hub', 'node')},
            'instances': {'central': 'hub', **{f'pod{i}': 'node' for i in range(1, 9)}},
            'harness': [[terminal('central', p, n), terminal(f'pod{i}', p, n)]
                        for i in range(1, 9) for p, n in [('1', 'A'), ('2', 'B')]],
        }
        # Independent specification: eight nodes, each wired A-to-A and B-to-B.
        # This does not read self.manifest or the native exported connectivity.
        self.expected = {
            'version': 2,
            'instances': {'central': 'hub', 'pod1': 'node', 'pod2': 'node',
                          'pod3': 'node', 'pod4': 'node', 'pod5': 'node',
                          'pod6': 'node', 'pod7': 'node', 'pod8': 'node'},
            'harness': [],
        }
        for pod in ('pod1', 'pod2', 'pod3', 'pod4', 'pod5', 'pod6', 'pod7', 'pod8'):
            for pin, net in [('2', 'B'), ('1', 'A')]:
                self.expected['harness'].append([
                    {'instance': pod, 'ref': 'R1', 'pin': pin, 'net': net},
                    {'instance': 'central', 'ref': 'R1', 'pin': pin, 'net': net},
                ])

    def verify(self):
        (self.root / 'manifest.json').write_text(json.dumps(self.manifest))
        (self.root / 'expected.json').write_text(json.dumps(self.expected))
        return assembly.verify(self.root, 'manifest.json', 'expected.json')

    def test_two_designs_nine_instances_real_native_replay(self):
        result = self.verify()
        self.assertEqual(set(result['boards']), {'hub', 'node'})
        self.assertEqual(len(result['instances']), 9)
        self.assertTrue(result['harness_checked'])
        self.assertEqual(result['harness_wire_count'], 16)

    def test_missing_pod_rejected(self):
        del self.manifest['instances']['pod8']
        with self.assertRaisesRegex(ValueError, 'instance membership'):
            self.verify()

    def test_extra_pod_rejected(self):
        self.manifest['instances']['pod9'] = 'node'
        with self.assertRaisesRegex(ValueError, 'instance membership'):
            self.verify()

    def test_omitted_wire_rejected(self):
        self.manifest['harness'].pop()
        with self.assertRaisesRegex(ValueError, 'wiring differs'):
            self.verify()

    def test_valid_terminal_but_crossed_net_rejected(self):
        self.manifest['harness'][0][1] = terminal('pod1', '2', 'B')
        with self.assertRaisesRegex(ValueError, 'wiring differs'):
            self.verify()

    def test_false_local_net_rejected(self):
        self.manifest['harness'][0][1]['net'] = 'B'
        with self.assertRaisesRegex(ValueError, 'net/pin mismatch'):
            self.verify()

    def test_nonexistent_pin_rejected(self):
        self.manifest['harness'][0][1]['pin'] = '99'
        with self.assertRaisesRegex(ValueError, 'net/pin mismatch'):
            self.verify()

    def test_reversed_duplicate_wire_rejected(self):
        self.manifest['harness'].append(list(reversed(copy.deepcopy(self.manifest['harness'][0]))))
        with self.assertRaisesRegex(ValueError, 'duplicate harness wire'):
            self.verify()

    def test_self_wire_rejected(self):
        self.manifest['harness'][0][1] = copy.deepcopy(self.manifest['harness'][0][0])
        with self.assertRaisesRegex(ValueError, 'terminal to itself'):
            self.verify()

    def test_incomplete_design_membership_rejected(self):
        members = copy.deepcopy(MEMBERSHIP)
        del members['components']['R2']
        (self.root / 'node-members.json').write_text(json.dumps(members))
        with self.assertRaisesRegex(ValueError, 'complete design membership'):
            self.verify()

    def test_native_output_mutation_rejected(self):
        path = native.artifacts(self.root / 'node-out')['schematic']
        path.write_text(path.read_text() + '\n; synthetic corruption\n')
        with self.assertRaisesRegex(ValueError, 'differs from source'):
            self.verify()

    def test_version_one_explicitly_has_no_harness_coverage(self):
        for document in (self.manifest, self.expected):
            document['version'] = 1
            del document['harness']
        result = self.verify()
        self.assertFalse(result['harness_checked'])
        self.assertIsNone(result['harness_wire_count'])


if __name__ == '__main__':
    unittest.main()
