"""Read-only forward binding checks for the retained ls37 registered scene.

This is evidence-route coverage only: it deliberately does not make an
engineering judgment for the nominal candidate and never issues a receipt.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import assembly_3d as scene  # noqa: E402
import assembly_verify as assembly  # noqa: E402


class RegisteredAssemblyForward(unittest.TestCase):
    project = ROOT / 'crow-sol6/recovery4'

    def binding(self):
        contract = assembly.contract(self.project)
        self.assertEqual(contract['version'], 2)
        return contract['mechanical']

    def structural_scene(self):
        binding = self.binding()
        scene_spec = assembly.p.read(self.project / binding['scene_manifest'])
        manifest = scene_spec['assembly_manifest']
        spec = assembly.p.read(self.project / manifest)
        _, envelope, subjects = assembly.payload(self.project, manifest, spec['package'], {})
        with patch.object(scene.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='', stderr='')):
            return scene.scene(self.project, binding, manifest, spec, envelope, subjects), spec

    def test_exact_population_scene_and_frozen_producer_bind_without_admission(self):
        result, spec = self.structural_scene()
        self.assertFalse(result['accepted'])
        self.assertEqual(set(result['coverage']), set(spec['boards']))
        self.assertEqual({key: len(refs) for key, refs in result['coverage'].items()},
                         {'carrier': 138, 'pod': 31})
        self.assertEqual(set(result['coverage']['carrier'].values()) | set(result['coverage']['pod'].values()),
                         set(spec['models']))
        self.assertEqual(result['replay_exit_code'], 0)

    def test_incomplete_judgments_and_changed_frozen_inventory_are_refused(self):
        result, spec = self.structural_scene()
        with self.assertRaisesRegex(ValueError, 'independent registered assembly judgments required'):
            scene.judgments(self.project, None, result, spec, {})
        broken = self.binding()
        broken['toolchain_files'] = dict(broken['toolchain_files'], **{'unexpected': '0' * 64})
        binding = self.binding()
        manifest = assembly.p.read(self.project / binding['scene_manifest'])['assembly_manifest']
        _, envelope, subjects = assembly.payload(self.project, manifest, spec['package'], {})
        with patch.object(scene.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='', stderr='')):
            with self.assertRaisesRegex(ValueError, 'producer inventory differs'):
                scene.scene(self.project, broken, manifest, spec, envelope, subjects)

    def test_historical_v1_contract_has_no_registered_scene_binding(self):
        """Historical compatibility assertion; it must not pin live adoption state."""
        with tempfile.TemporaryDirectory(prefix='assembly-v1-contract-') as tmp:
            project = Path(tmp)
            authority = project / 'authority.txt'
            authority.write_text('Synthetic historical assembly authority.\n')
            receipt = project / assembly.fab.RECEIPT
            receipt.parent.mkdir(parents=True)
            receipt.write_text('{}\n')
            contract = {
                'version': 1,
                'authority': 'authority.txt',
                'authority_sha256': assembly.p.sha(authority),
                'fabrication_receipt_sha256': assembly.p.sha(receipt),
            }
            path = project / assembly.CONTRACT
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(contract))
            observed = assembly.contract(project)
        self.assertEqual(observed['version'], 1)
        self.assertNotIn('mechanical', observed)


if __name__ == '__main__':
    unittest.main()
