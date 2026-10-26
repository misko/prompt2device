"""Runtime packaging/isolation behavior, not PCB or mechanical acceptance."""
import copy
import gzip
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

import release_runtime as r


class Runtime(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='runtime-fixture-')
        self.addCleanup(tmp.cleanup); self.root = Path(tmp.name)
        self.venv = self.root/'venv'; (self.venv/'bin').mkdir(parents=True)
        (self.venv/'bin/python').symlink_to(Path(sys.executable).resolve())
        (self.venv/'pyvenv.cfg').write_text('home = /usr/bin\ninclude-system-site-packages = true\n')
        self.base = 'lib/python%d.%d/site-packages' % sys.version_info[:2]
        module = self.venv/self.base/'fixture_runtime.py'; module.parent.mkdir(parents=True)
        module.write_text('value = 42\n')
        self.capsule = self.root/'capsule'
        r.build(self.venv, self.capsule, ['fixture_runtime'])

    def save(self, record):
        (self.capsule/'runtime.json').write_text(r.dump(record))

    def test_relocatable_deterministic_payload(self):
        other = self.root/'second'; r.build(self.venv, other, ['fixture_runtime'])
        self.assertEqual(r.sha(other/'runtime.json'), r.sha(self.capsule/'runtime.json'))
        python = r.materialize(other, self.root/'restored')
        result = subprocess.run([str(python), '-I', '-B', '-c',
                                 'import fixture_runtime;print(fixture_runtime.value)'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '42')

    def test_inventory_host_and_payload_failures(self):
        original = r.read(self.capsule/'runtime.json')
        for mutation in (lambda x:x['abi'].update(machine='other'),
                         lambda x:x['interpreter'].update(sha256='0'*64),
                         lambda x:x['payload'].update(sha256='0'*64),
                         lambda x:x.update(files={}),
                         lambda x:x.update(modules=[]),
                         lambda x:x['files'].update({'../escape':dict(size=1,sha256='0'*64)})):
            record = copy.deepcopy(original); mutation(record); self.save(record)
            with self.assertRaises(ValueError): r.validate(self.capsule)
        self.save(original)
        (self.capsule/'extra').write_text('unlisted')
        with self.assertRaisesRegex(ValueError, 'census'): r.validate(self.capsule)

    def test_missing_wrong_hash_and_unknown_tar_members(self):
        original = r.read(self.capsule/'runtime.json')
        for index, kind in enumerate(('missing','wrong-hash','unknown','symlink','duplicate','traversal')):
            record = copy.deepcopy(original); payload = self.capsule/'site-packages.tar.gz'
            with tarfile.open(payload, 'w:gz') as archive:
                if kind != 'missing':
                    name = next(iter(record['files']))
                    if kind == 'unknown': name += '.extra'
                    if kind == 'traversal': name = '../escape'
                    info = tarfile.TarInfo(name); data = b'value = 43\n'; info.size = len(data)
                    if kind == 'symlink': info.type = tarfile.SYMTYPE; info.linkname = '/etc/passwd'
                    archive.addfile(info, io.BytesIO(data))
                    if kind == 'duplicate':
                        # First copy must pass its hash before the second is rejected.
                        record['files'][name]['sha256'] = __import__('hashlib').sha256(data).hexdigest()
                        archive.addfile(info, io.BytesIO(data))
            record['payload']['sha256'] = r.sha(payload); self.save(record)
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                r.materialize(self.capsule, self.root/('bad'+str(index)))
        self.assertFalse((self.root/'escape').exists())

    def test_guarded_reexec_uses_capsule_and_preserves_denials(self):
        scratch = self.root/'scratch'; archive = scratch/'archive'; archive.mkdir(parents=True)
        capsule = archive/'runtime'; shutil.copytree(self.capsule, capsule)
        outside = self.root/'outside'; outside.write_text('inaccessible')
        script = archive/'probe.py'
        script.write_text('''import socket,sys
from pathlib import Path
import fixture_runtime
assert fixture_runtime.value == 42
assert Path(fixture_runtime.__file__).is_relative_to(Path(sys.prefix))
for target in (Path(sys.argv[1]), Path(__file__)):
    try:
        if target == Path(__file__): target.write_text('mutated')
        else: target.read_text()
    except PermissionError: pass
    else: raise AssertionError('filesystem guard lost')
try: socket.socket()
except PermissionError: pass
else: raise AssertionError('network guard lost')
try: socket.socketpair()
except PermissionError: pass
else: raise AssertionError('socketpair guard lost')
Path('result.json').write_text(__import__('json').dumps({'python':sys.executable,'value':fixture_runtime.value}))
''')
        before = r.sha(script)
        result = subprocess.run([sys.executable, '-B', str(Path(r.__file__).with_name('offline_replay.py')),
            '--scratch', str(scratch), '--readonly-archive', '--runtime', str(capsule),
            str(script), str(outside)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(r.sha(script), before)
        output = json.loads((scratch/'work/result.json').read_text())
        self.assertTrue(Path(output['python']).is_relative_to(scratch/'work/runtime'))

    def test_runtime_location_must_be_readonly_scratch(self):
        scratch=self.root/'scratch';archive=scratch/'archive';archive.mkdir(parents=True)
        work=scratch/'work';work.mkdir()
        script=archive/'probe.py';script.write_text('raise AssertionError("must not run")')
        shutil.copytree(self.capsule,work/'capsule')
        for capsule in (self.capsule,work/'capsule'):
            result=subprocess.run([sys.executable,'-B',str(Path(r.__file__).with_name('offline_replay.py')),
                '--scratch',str(scratch),'--readonly-archive','--runtime',str(capsule),str(script)],
                capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('runtime capsule must be in read-only scratch archive',result.stderr)

    def test_required_module_cannot_fall_back_to_system(self):
        python = r.materialize(self.capsule, self.root/'restored')
        script = self.root/'never.py'; script.write_text('raise AssertionError("ran target")')
        result = subprocess.run([str(python), '-I', '-B', '-c', r.LAUNCH,
                                 '["json"]', str(script)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('escaped capsule', result.stderr)
        self.assertNotIn('ran target', result.stderr)

    def graphics_record(self):
        record=r.read(self.capsule/'runtime.json')
        record.update(version=2,modules=['fixture_runtime','vtk'],graphics=dict(
            environment=dict(r.RENDER_ENV),devices=[dict(path='/dev/nvidia0',major=195,minor=0)],
            profile=dict(window='vtkEGLRenderWindow',capabilities={k:'fixture' for k in
                ('EGL version string','EGL vendor string','OpenGL vendor string',
                 'OpenGL renderer string','OpenGL version string')})))
        return record

    def test_graphics_declaration_fails_closed(self):
        original=self.graphics_record();self.save(original)
        r.validate(self.capsule,check_host=False)
        mutations=[lambda x:x.pop('graphics'),
            lambda x:x['graphics'].update(extra=True),
            lambda x:x['graphics']['devices'][0].update(path='/dev/mem'),
            lambda x:x['graphics']['devices'][0].update(path='/dev/dri/card0'),
            lambda x:x['graphics']['devices'][0].update(path='/dev/nvidia0/../mem'),
            lambda x:x['graphics']['devices'].append(dict(path='/dev/null',major=1,minor=3)),
            lambda x:x['graphics']['devices'].append(dict(x['graphics']['devices'][0])),
            lambda x:x['graphics'].update(devices=[]),
            lambda x:x['graphics']['environment'].update(LIBGL_ALWAYS_SOFTWARE='1'),
            lambda x:x['graphics']['profile'].update(window='vtkXOpenGLRenderWindow'),
            lambda x:x['graphics']['profile']['capabilities'].pop('OpenGL version string'),
            lambda x:x.update(modules=['fixture_runtime'])]
        for mutate in mutations:
            changed=copy.deepcopy(original);mutate(changed);self.save(changed)
            with self.assertRaises(ValueError):r.validate(self.capsule,check_host=False)

    def test_graphics_devices_require_actual_exact_character_nodes(self):
        row=dict(path='/dev/nvidia0',major=195,minor=0)
        with mock.patch.object(Path,'stat',side_effect=FileNotFoundError):
            with self.assertRaises((ValueError,OSError)):r.graphics_devices([row])
        with mock.patch.object(Path,'resolve',return_value=Path('/dev/null')):
            with self.assertRaisesRegex(ValueError,'linked'):r.graphics_devices([row])
        import stat
        from types import SimpleNamespace
        for info in (SimpleNamespace(st_mode=stat.S_IFREG,st_rdev=0),
                     SimpleNamespace(st_mode=stat.S_IFCHR,st_rdev=0)):
            with mock.patch.object(Path,'resolve',return_value=Path('/dev/nvidia0')),\
                 mock.patch.object(Path,'is_symlink',return_value=False),\
                 mock.patch.object(Path,'stat',return_value=info):
                with self.assertRaisesRegex(ValueError,'identity'):r.graphics_devices([row])

    def test_graphics_environment_rejects_conflicting_selection(self):
        import os
        g=self.graphics_record()['graphics']
        with mock.patch.dict(os.environ,{},clear=True):
            r.graphics_environment(g)
            self.assertEqual(os.environ['VTK_DEFAULT_OPENGL_WINDOW'],'vtkEGLRenderWindow')
        for name,value in [('LIBGL_ALWAYS_SOFTWARE','1'),('LD_PRELOAD','unexpected.so'),
                           ('DISPLAY',':99'),('VTK_DEFAULT_OPENGL_WINDOW','vtkOSOpenGLRenderWindow')]:
            with mock.patch.dict(os.environ,{name:value},clear=True),\
                 self.assertRaisesRegex(ValueError,'environment differs'):
                r.graphics_environment(g)

    def test_renderer_substitution_cannot_run_target(self):
        fake=self.venv/self.base/'vtk.py'
        fake.write_text('''class vtkRenderer: pass
class vtkRenderWindow:
 def SetOffScreenRendering(self,x): pass
 def SetMultiSamples(self,x): pass
 def SetSize(self,x,y): pass
 def AddRenderer(self,x): pass
 def Render(self): pass
 def Finalize(self): pass
 def GetClassName(self): return 'vtkEGLRenderWindow'
 def ReportCapabilities(self): return "EGL version string: fixture\\nEGL vendor string: fixture\\nOpenGL vendor string: fixture\\nOpenGL renderer string: llvmpipe\\nOpenGL version string: fixture"
''')
        capsule=self.root/'graphics-payload';r.build(self.venv,capsule,['fixture_runtime','vtk'])
        python=r.materialize(capsule,self.root/'graphics-runtime')
        script=self.root/'never.py';script.write_text('raise AssertionError("ran target")')
        config=dict(modules=['fixture_runtime','vtk'],graphics=self.graphics_record()['graphics'])
        result=subprocess.run([str(python),'-I','-B','-c',r.LAUNCH,json.dumps(config),str(script)],
                              capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('no fallback',result.stderr)
        self.assertNotIn('ran target',result.stderr)


if __name__ == '__main__':
    unittest.main()
