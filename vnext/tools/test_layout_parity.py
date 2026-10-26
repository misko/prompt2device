"""Focused native-parity admission regressions; no mocked engineering acceptance."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import layout_seal as s
import test_routing as fixture


class Sources(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write('01_docs/schematic-contract.json', dict(version=2, rf=False, manifest='assembly.json', expected='expected.json'))
        self.write('assembly.json', dict(boards={'test': dict(producer='imported', source='import.json', membership='membership.json', output='out')}))
        self.write('import.json', dict(version=1, producer=dict(entrypoint='generate.py', inputs=['generate.py']),
                                     intent='intent.json', schematic='test.kicad_sch', context=['test.kicad_pro']))
        for name in ['generate.py', 'test.kicad_sch', 'test.kicad_pro', 'intent.json', 'expected.json', 'membership.json']:
            (self.root/name).write_text('{}')

    def write(self, name, value):
        target = self.root/name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value))

    def test_exact_upstream_selection_and_sources(self):
        selected, names = s.schematic_sources(self.root, {'test'})
        self.assertEqual(selected, {'test': 'test.kicad_sch'})
        self.assertTrue({'generate.py', 'intent.json', 'membership.json', 'test.kicad_pro'} <= names)

    def test_wrong_board_coverage_fails(self):
        with self.assertRaisesRegex(ValueError, 'coverage differs'):
            s.schematic_sources(self.root, {'other'})

    def test_missing_native_fails(self):
        (self.root/'test.kicad_sch').unlink()
        with self.assertRaises(ValueError): s.schematic_sources(self.root, {'test'})

    def test_unsupported_producer_fails(self):
        self.write('assembly.json', dict(boards={'test': dict(producer='native', source='import.json', membership='membership.json', output='out')}))
        with self.assertRaisesRegex(ValueError, 'producer unsupported'):
            s.schematic_sources(self.root, {'test'})

    def test_new_certificate_rejects_historical_contract(self):
        self.write(s.CONTRACT, dict(version=1, obligations=[]))
        with patch.object(s.r, 'review_json', return_value={'manifest': 'm', 'output': 'o'}), \
             patch.object(s, 'verify', return_value={'boards': {'test': {'layout_clean': True}},
                                                    'engineering_closed': True}):
            with self.assertRaisesRegex(ValueError, 'version2 native parity'):
                s.certificate(self.root, 'review')

    def test_v2_inputs_reject_missing_or_substituted_schematic_mapping(self):
        contract = dict(version=2, authority='authority', obligations=[])
        baseline = dict(boards={'test': {}})
        for mapping in (None, {'test': 'another.kicad_sch'}, {}):
            data = dict(version=1, boards={'test': {}}, closure={})
            if mapping is not None: data['schematics'] = mapping
            self.write('candidate.json', data)
            with self.subTest(mapping=mapping), patch.object(s, 'upstream', return_value=(contract, baseline)):
                with self.assertRaisesRegex(ValueError, 'missing or wrong accepted native schematics'):
                    s.inputs(self.root, 'candidate.json')


class Native(unittest.TestCase):
    write = fixture.Native.write
    setUp = fixture.Native.setUp

    def test_real_parity_executes_and_missing_schematic_components_fail_grade(self):
        # Valid empty native schematic deliberately mismatches the two-pad PCB.
        self.write('empty.kicad_sch', '(kicad_sch (version 20250114) (generator "eeschema") '
                   '(uuid "10101010-1010-4010-8010-101010101010") (paper "A4") '
                   '(lib_symbols) (embedded_fonts no))')
        self.data['boards']['test']['resources'] = {}
        self.data['schematics'] = {'test': 'empty.kicad_sch'}
        result = s.produce(self.root, self.data, self.root/'out')
        execution = s.p.read(self.root/'out/test/native/drc-execution.json')
        self.assertIn('--schematic-parity', execution['command'])
        self.assertEqual(execution['schematic_sha256'], s.p.sha(self.root/'empty.kicad_sch'))
        report = s.p.read(self.root/'out/test/native/test-drc.json')
        self.assertTrue(report['schematic_parity'])
        self.assertFalse(result['test']['layout_clean'])
        contract = {'obligations': [{'id': 'stack'}]}
        self.data['closure'] = {'stack': dict(status='open', rationale='fixture', evidence=[])}
        with patch.object(s, 'inputs', return_value=(contract, self.data, {})):
            replay = s.verify(self.root, 'manifest', 'out')
            self.assertFalse(replay['boards']['test']['layout_clean'])
            execution['command'].remove('--schematic-parity')
            self.write('out/test/native/drc-execution.json', json.dumps(execution))
            with self.assertRaisesRegex(ValueError, 'stale layout artifact'):
                s.verify(self.root, 'manifest', 'out')


if __name__ == '__main__': unittest.main()
