"""Synthetic structural regressions. These are not electrical acceptance tests."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import admission
import schematic_admission
import source_snapshot
import task


class Handoffs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('contracts.md', 'Synthetic project contract')
        self.write('01_docs/capability-profile.json', {'rf': False})
        self.contract = dict(version=2, manifest='03_src/assembly.json',
                             expected='03_src/expected.json', rf=False,
                             producers=['imported'])
        self.write('01_docs/schematic-contract.json', self.contract)
        self.write('01_docs/sourcing/exact-parts.csv', 'MPN,Dossier\nEXACT,02_parts/exact/part.yaml\n')
        self.write('02_parts/exact/part.yaml', 'Synthetic dossier')
        self.write('02_parts/exact/data.pdf', 'Synthetic PDF; not primary evidence')
        self.write('01_docs/decisions/sourcing.md', 'Synthetic policy')
        subjects = {p.relative_to(self.root).as_posix(): admission.digest(p.read_bytes())
                    for p in self.root.rglob('*') if p.is_file()}
        self.review = dict(schema=1, stage='PCB-SOURCING', author='author', reviewer='reviewer',
                           verdict='PASS', subjects=subjects,
                           checks={k: dict(verdict='PASS', evidence=list(subjects),
                                           rationale='Synthetic structural evidence only')
                                   for k in admission.CRITERIA['PCB-SOURCING']})

    def write(self, name, value):
        path = self.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value, (dict, list)) else value)

    def check(self):
        name = '08_reviews/2026-10-05-synthetic.md'
        self.write(name, '```json\n'+json.dumps(self.review)+'\n```\n')
        return admission.review_data(self.root, name)

    def test_producer_gate_accepts_complete_contract(self):
        self.check()

    def test_producer_gate_rejects_missing_contract_subject(self):
        del self.review['subjects']['contracts.md']
        for c in self.review['checks'].values(): c['evidence'].remove('contracts.md')
        with self.assertRaisesRegex(admission.AdmissionError, 'required subjects'): self.check()

    def test_producer_gate_rejects_missing_assembly_citation(self):
        self.review['checks']['assembly']['evidence'].remove('01_docs/schematic-contract.json')
        with self.assertRaisesRegex(admission.AdmissionError, 'assembly review'): self.check()

    def test_producer_gate_rejects_unsupported_contract(self):
        self.contract['producers'] = ['invented']
        path = '01_docs/schematic-contract.json'
        self.write(path, self.contract)
        self.review['subjects'][path] = admission.digest((self.root/path).read_bytes())
        with self.assertRaisesRegex(admission.AdmissionError, 'supported producers'): self.check()

    def test_consumer_calls_same_guard(self):
        with patch.object(admission, 'validate_certificate', return_value={'role':'parts_locked','review':'review'}), \
             patch.object(admission, 'review_data', return_value=(self.review,b'')), \
             patch.object(admission, 'sourcing_contract', wraps=admission.sourcing_contract) as guard:
            _, contract = schematic_admission.prerequisites(self.root, self.root)
            guard.assert_called_once_with(self.root, self.review)
            self.assertEqual(contract, self.contract)

    def test_recursive_snapshot_includes_nested_and_binary_refs(self):
        self.write('03_src/rules/top.json', {'link': {'path':'03_src/intent/a.json'}})
        self.write('03_src/intent/a.json', {'link': {'path':'03_src/intent/b.yaml'}})
        self.write('03_src/intent/b.yaml', {'back': {'path':'03_src/intent/a.json'},
                                           'program': {'path':'03_src/generate.py'}})
        self.write('03_src/generate.py', 'print("synthetic producer")\n')
        snapshot = source_snapshot.collect(self.root)
        self.assertEqual(len(snapshot), 4)
        self.assertEqual(set(source_snapshot.validate(self.root, snapshot)), set(snapshot))
        self.write('03_src/generate.py', 'print("changed")\n')
        with self.assertRaisesRegex(source_snapshot.SnapshotError, 'stale'):
            source_snapshot.validate(self.root, snapshot)

    def test_nested_snapshot_pointer_and_hash_rules(self):
        self.write('03_src/rules/top.json', {'link': {'path':'03_src/intent/a.json'}})
        self.write('03_src/intent/a.json', {'link': {'path':'03_src/intent/b.json', 'pointer':'/missing'}})
        self.write('03_src/intent/b.json', {'value': 1})
        with self.assertRaisesRegex(source_snapshot.SnapshotError, 'pointer'):
            source_snapshot.validate(self.root, source_snapshot.collect(self.root))
        self.write('03_src/intent/a.json', {'link': {'path':'03_src/intent/b.json', 'sha256':'bad'}})
        with self.assertRaisesRegex(source_snapshot.SnapshotError, 'embedded'):
            source_snapshot.validate(self.root, source_snapshot.collect(self.root))

    def test_only_adopted_producer_manual_is_loaded(self):
        for producers in (['native'], ['imported'], ['native','imported']):
            instructions = task.schematic_instructions({'version':2,'producers':producers})
            for producer in ('native','imported'):
                path = f'skills/pcb-design/procedures/schematic/{producer}-tooling.md'
                self.assertEqual(path in instructions, producer in producers)
            self.assertFalse(any(p.startswith('tools/') for p in instructions))
        self.assertIn('skills/pcb-design/procedures/schematic/native-tooling.md',
                      task.schematic_instructions({'version':1}))

    def test_checkpoint_is_parseable_but_not_dispatchable(self):
        for name in task.REQUIRED_INPUTS: self.write(name, 'synthetic')
        status = '\n'.join(f'{k}: {v}' for k,v in dict(stage='schematic', step='reflection',
            measure='accepted', state='checkpoint', next='user reflection', op_pid='', updated='2026-10-05').items())
        self.write('01_docs/STATUS.md', status)
        self.assertEqual(task._status_fields(status)['state'], 'checkpoint')
        with self.assertRaisesRegex(task.PacketError, 'user checkpoint'):
            task.build_packet(self.root, self.root, [], 'schematic-design')


if __name__ == '__main__': unittest.main()
