"""Unmocked native board/STEP/image replay; synthetic engineering inputs only."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from PIL import Image
import mechanical_scene as m
import test_assembly_verify as fixture


class Replay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture.Assembly.setUpClass()
        cls.addClassCleanup(fixture.Assembly.doClassCleanups)
        cls.seed = fixture.Assembly(); cls.seed.setUp()
        cls.addClassCleanup(cls.seed.doCleanups)
        cls.scene = 'scene-input.json'
        (cls.seed.root/cls.scene).write_text(json.dumps(dict(
            version=1, assembly_manifest=cls.seed.name, step_models={},
            unresolved=['Synthetic model/dimensions, no actual assembly acceptance.'])))
        native = cls.seed.root/cls.seed.package/'native/source'
        before = {f.relative_to(native).as_posix(): m.sha(f) for f in native.rglob('*') if f.is_file()}
        m.build(cls.seed.root, cls.scene, cls.seed.root/'scene-output')
        after = {f.relative_to(native).as_posix(): m.sha(f) for f in native.rglob('*') if f.is_file()}
        if before != after: raise AssertionError('scene build modified native source census/bytes')

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='scene-replay-fixture-'); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)/'relocated-project'
        shutil.copytree(self.seed.root, self.root)
        self.out = self.root/'scene-output'

    def verify(self): return m.verify(self.root, self.scene, self.out)

    def rehash(self, name):
        record = m.p.read(self.out/'scene.json'); record['files'][name] = m.sha(self.out/name)
        m.write_json(self.out/'scene.json', record)

    def test_relocated_real_native_scene_replays_without_acceptance(self):
        result = self.verify()
        self.assertFalse(result['accepted']); self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertEqual(len(result['replayed_boards']), 2)

    def test_wrong_image_not_hidden_by_updated_hash(self):
        file = next(self.out.glob('*/twin_top.png'))
        Image.new('RGB', (1200, 800), 'white').save(file)
        self.rehash(file.relative_to(self.out).as_posix())
        with self.assertRaisesRegex(ValueError, 'render pixels differ'): self.verify()

    def test_missing_population_not_hidden_by_updated_step_hash(self):
        file = next(self.out.glob('*/*-populated.step'))
        shutil.copyfile(file.parent/'board.step', file)
        self.rehash(file.relative_to(self.out).as_posix())
        with self.assertRaisesRegex(ValueError, 'STEP'): self.verify()

    def test_stale_input_and_unaccounted_artifact_fail(self):
        evidence = self.root/'evidence/geometry.txt'; saved = evidence.read_bytes()
        evidence.write_text('changed source')
        with self.assertRaisesRegex(ValueError, 'stale scene input'): self.verify()
        evidence.write_bytes(saved)
        (self.out/'unexpected.txt').write_text('not part of scene')
        with self.assertRaisesRegex(ValueError, 'inventory'): self.verify()

    def test_population_omission_fails_before_solid_checks(self):
        path = self.root/self.seed.name; spec = m.p.read(path)
        key = next(iter(spec['boards']))
        spec['boards'][key]['references'].pop('U1'); m.write_json(path, spec)
        with self.assertRaisesRegex(ValueError, 'reference coverage'):
            m.inputs(self.root, self.scene)


if __name__ == '__main__': unittest.main()
