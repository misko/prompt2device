"""Inventoried offline Python capsule; system KiCad/OS remain explicit prerequisites.

The capsule retains regular site-packages files, not a host-specific executable
venv. Extraction creates a fresh venv using the exact declared system Python.
This is trusted-code reproducibility, not a sandbox for third-party code.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(file):
    with Path(file).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def dump(obj):
    return json.dumps(obj, indent=2, sort_keys=True) + '\n'


def pairs(rows):
    obj = {}
    for key, value in rows:
        need(key not in obj, 'duplicate runtime JSON key')
        obj[key] = value
    return obj


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs)


def relative(name):
    need(isinstance(name, str) and name and str(Path(name)) == name and
         not Path(name).is_absolute() and '..' not in Path(name).parts,
         'unsafe runtime member path')
    return name


def host():
    import sysconfig
    return dict(system=platform.system(), machine=platform.machine(),
                implementation=platform.python_implementation(),
                python=list(sys.version_info[:3]), soabi=sysconfig.get_config_var('SOABI'),
                libc=list(platform.libc_ver()))


# Exact pixel replay can depend on the host renderer as well as Python packages.
# These are explicit runtime capabilities, never write permissions on artifacts.
RENDER_ENV = {'VTK_DEFAULT_OPENGL_WINDOW':'vtkEGLRenderWindow',
              **{n:None for n in ('DISPLAY','LIBGL_ALWAYS_SOFTWARE','EGL_PLATFORM',
                 '__EGL_VENDOR_LIBRARY_FILENAMES','MESA_LOADER_DRIVER_OVERRIDE',
                 '__GLX_VENDOR_LIBRARY_NAME','LD_LIBRARY_PATH','LD_PRELOAD')}}
RENDER_PROBE = '''def rendering_profile():
    import vtk
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1)
    window.SetMultiSamples(0);window.SetSize(64,64)
    window.AddRenderer(vtk.vtkRenderer());window.Render()
    facts={}
    for line in window.ReportCapabilities().splitlines():
        key,sep,value=line.partition(':')
        if sep and key.strip() in ('EGL version string','EGL vendor string',
            'OpenGL vendor string','OpenGL renderer string','OpenGL version string'):
            facts[key.strip()]=value.strip()
    result={'window':window.GetClassName(),'capabilities':facts}
    window.Finalize()
    if len(facts)!=5: raise ValueError('incomplete EGL renderer identity')
    return result
'''
exec(RENDER_PROBE)


def graphics_devices(rows, check_host=True):
    need(isinstance(rows,list) and rows and all(isinstance(r,dict) for r in rows),
         'explicit graphics devices required')
    names=[]
    for row in rows:
        need(set(row)=={'path','major','minor'} and isinstance(row['path'],str) and
             re.fullmatch(r'/dev/(?:nvidia(?:[0-9]+|ctl)|dri/renderD[0-9]+)',row['path']) and
             all(type(row[n]) is int and row[n]>=0 for n in ('major','minor')),
             'unsupported graphics device')
        file=Path(row['path']);names.append(str(file))
        if check_host:
            need(file.resolve()==file and not file.is_symlink(), 'linked graphics device')
            info=file.stat()
            need(stat.S_ISCHR(info.st_mode) and os.major(info.st_rdev)==row['major'] and
                 os.minor(info.st_rdev)==row['minor'], 'graphics device identity differs')
    need(names==sorted(set(names)), 'duplicate/unsorted graphics devices')
    return names


def graphics_environment(graphics):
    need(graphics['environment']==RENDER_ENV, 'unsupported graphics environment policy')
    for name,value in RENDER_ENV.items():
        need(os.environ.get(name) in (None,value), 'graphics environment differs: '+name)
    for name,value in RENDER_ENV.items():
        if value is not None:os.environ[name]=value
        else:os.environ.pop(name,None)


def bind_renderer(source, output, venv, devices):
    record=validate(source)
    need(record['version']==1 and not output.exists(), 'renderer binding requires new v1 successor capsule')
    abi,interpreter=inspect_venv(venv)
    need(abi==record['abi'] and interpreter==record['interpreter'], 'renderer interpreter differs')
    need(all(sha(venv/n)==r['sha256'] for n,r in record['files'].items()),
         'renderer probe packages differ from capsule')
    rows=[]
    for name in sorted(devices):
        file=Path(name);info=file.stat()
        rows.append(dict(path=name,major=os.major(info.st_rdev),minor=os.minor(info.st_rdev)))
    graphics_devices(rows)
    graphics=dict(environment=RENDER_ENV,devices=rows)
    graphics_environment(graphics)
    run=subprocess.run([str(venv/'bin/python'),'-I','-B','-c',
        'import json\n'+RENDER_PROBE+'\nprint(json.dumps(rendering_profile()))'],
        capture_output=True,text=True,check=True)
    graphics['profile']=json.loads(run.stdout)
    record.update(version=2,graphics=graphics,modules=sorted(set(record['modules'])|{'vtk'}))
    record['system_requirements'].append('Exact declared EGL/GL renderer and driver; enumerated GPU character-device read/write/ioctl access')
    output.mkdir(parents=True)
    shutil.copyfile(source/'site-packages.tar.gz',output/'site-packages.tar.gz')
    (output/'runtime.json').write_text(dump(record),encoding='utf-8')
    validate(output)
    return dict(manifest_sha256=sha(output/'runtime.json'),graphics=graphics)


def inspect_venv(venv):
    code = """import json,sys,sysconfig,platform
from pathlib import Path
print(json.dumps(dict(system=platform.system(),machine=platform.machine(),
 implementation=platform.python_implementation(),python=list(sys.version_info[:3]),
 soabi=sysconfig.get_config_var('SOABI'),libc=list(platform.libc_ver()),
 prefix=sys.prefix,interpreter=str(Path(sys.executable).resolve()))))
"""
    run = subprocess.run([str(venv/'bin/python'), '-I', '-B', '-c', code],
                         check=True, capture_output=True, text=True)
    obj = json.loads(run.stdout)
    need(Path(obj.pop('prefix')).resolve() == venv.resolve(), 'not the selected venv')
    interpreter = Path(obj.pop('interpreter'))
    need(interpreter.is_relative_to('/usr/bin'), 'runtime requires system /usr/bin Python')
    return obj, dict(path=str(interpreter), sha256=sha(interpreter))


def build(venv, output, modules):
    need(modules and len(modules) == len(set(modules)) and
         all(re.fullmatch(r'[A-Za-z_]\w*', n) for n in modules), 'explicit top-level runtime modules required')
    need(not output.exists(), 'refusing existing runtime capsule')
    abi, interpreter = inspect_venv(venv)
    need(abi == host(), 'runtime builder ABI differs from selected venv')
    base = 'lib/python%d.%d/site-packages' % tuple(abi['python'][:2])
    need((venv/base).is_dir(), 'missing runtime site-packages')
    files = {}
    for file in sorted((venv/base).rglob('*')):
        need(not file.is_symlink(), 'linked runtime input')
        if '__pycache__' in file.parts or file.suffix == '.pyc' or file.is_dir():
            continue
        need(file.is_file(), 'nonregular runtime input')
        name = file.relative_to(venv).as_posix()
        files[name] = dict(sha256=sha(file), size=file.stat().st_size)
    need(files, 'empty runtime payload')
    output.mkdir(parents=True)
    payload = output/'site-packages.tar.gz'
    # Stable tar/gzip headers: no source paths, owners or timestamps.
    with payload.open('xb') as raw, gzip.GzipFile(filename='', mode='wb',
            fileobj=raw, mtime=0, compresslevel=6) as compressed:
        with tarfile.open(fileobj=compressed, mode='w|') as archive:
            for name, row in files.items():
                info = tarfile.TarInfo(name); info.size = row['size']; info.mode = 0o644
                with (venv/name).open('rb') as stream:
                    archive.addfile(info, stream)
                need(sha(venv/name) == row['sha256'], 'runtime input changed during packing')
    record = dict(version=1, abi=abi, interpreter=interpreter, site_packages=base, modules=sorted(modules),
                  payload=dict(path=payload.name, sha256=sha(payload)), files=files,
                  system_requirements=['Exact declared Linux/Python/libc ABI and interpreter',
                    'KiCad/pcbnew, fonts, PDF tools and shared libraries required by accepted owner checks',
                    'Linux Landlock ABI >=3 and libseccomp for isolated replay'],
                  scope='Bound Python packages; not a complete operating-system image')
    (output/'runtime.json').write_text(dump(record), encoding='utf-8')
    validate(output)
    return dict(files=len(files), bytes=sum(r['size'] for r in files.values()),
                payload_bytes=payload.stat().st_size, manifest_sha256=sha(output/'runtime.json'))


def validate(capsule, check_host=True):
    need(capsule.is_dir() and not capsule.is_symlink(), 'missing/linked runtime capsule')
    record = read(capsule/'runtime.json')
    fields={'version','abi','interpreter','site_packages','payload','files','modules','system_requirements','scope'}
    need(record.get('version') in (1,2) and set(record)==fields|({'graphics'} if record['version']==2 else set()),
         'unsupported runtime capsule')
    if record['version']==2:
        g=record['graphics']
        need(isinstance(g,dict) and set(g)=={'environment','devices','profile'} and
             g['environment']==RENDER_ENV, 'invalid renderer declaration')
        graphics_devices(g['devices'],check_host)
        profile=g['profile']
        need(set(profile)=={'window','capabilities'} and profile['window']=='vtkEGLRenderWindow' and
             set(profile['capabilities'])=={'EGL version string','EGL vendor string','OpenGL vendor string',
                 'OpenGL renderer string','OpenGL version string'} and
             all(isinstance(s,str) and s.strip() for s in profile['capabilities'].values()) and
             'vtk' in record['modules'], 'incomplete renderer profile')
    need(record['system_requirements'] and record['scope'], 'undeclared runtime scope')
    need(isinstance(record['modules'], list) and record['modules'] and
         record['modules'] == sorted(set(record['modules'])) and
         all(isinstance(n, str) and re.fullmatch(r'[A-Za-z_]\w*', n) for n in record['modules']),
         'invalid required runtime modules')
    expected = 'lib/python%d.%d/site-packages' % tuple(record['abi']['python'][:2])
    need(record['site_packages'] == expected, 'runtime site-packages ABI differs')
    need(set(record['payload']) == {'path','sha256'} and
         record['payload']['path'] == 'site-packages.tar.gz', 'unsupported runtime payload')
    need(set(f.name for f in capsule.iterdir()) == {'runtime.json','site-packages.tar.gz'},
         'runtime capsule census differs')
    for file in capsule.iterdir():
        need(file.is_file() and not file.is_symlink(), 'linked/nonregular capsule member')
    need(sha(capsule/'site-packages.tar.gz') == record['payload']['sha256'], 'runtime payload changed')
    need(isinstance(record['files'], dict) and record['files'], 'empty runtime inventory')
    for name, row in record['files'].items():
        relative(name)
        need(name.startswith(expected+'/') and set(row) == {'size','sha256'} and
             type(row['size']) is int and row['size'] >= 0 and
             isinstance(row['sha256'], str) and len(row['sha256']) == 64,
             'invalid runtime member inventory')
    interpreter = record['interpreter']
    need(set(interpreter) == {'path','sha256'} and
         Path(interpreter['path']).is_absolute() and
         Path(interpreter['path']).resolve().is_relative_to('/usr/bin'),
         'invalid runtime system interpreter')
    if check_host:
        need(record['abi'] == host(), 'runtime host ABI differs')
        need(sha(interpreter['path']) == interpreter['sha256'], 'runtime interpreter changed')
    return record


def materialize(capsule, target):
    record = validate(capsule)
    need(not target.exists() and not target.is_symlink(), 'refusing existing runtime target')
    parent = target.parent
    while not parent.exists(): parent = parent.parent
    need(shutil.disk_usage(parent).free >= sum(r['size'] for r in record['files'].values()) + 64*1024*1024,
         'insufficient free space for runtime extraction and work margin')
    target.mkdir(parents=True)
    seen = set()
    with tarfile.open(capsule/'site-packages.tar.gz', 'r:gz') as archive:
        for member in archive:
            name = relative(member.name)
            need(member.isfile() and name in record['files'] and name not in seen,
                 'unknown/duplicate/nonregular runtime payload member')
            row = record['files'][name]
            need(member.size == row['size'], 'runtime member size differs')
            file = target/name; file.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            with archive.extractfile(member) as source, file.open('xb') as dest:
                while chunk := source.read(1024*1024):
                    digest.update(chunk); dest.write(chunk)
            need(digest.hexdigest() == row['sha256'], 'runtime member hash differs')
            seen.add(name)
    need(seen == set(record['files']), 'runtime payload omits inventoried member')
    # Only this generated symlink is allowed. Its exact system target was checked.
    (target/'bin').mkdir(); python = target/'bin/python'
    python.symlink_to(record['interpreter']['path'])
    (target/'pyvenv.cfg').write_text('home = /usr/bin\ninclude-system-site-packages = true\n',
                                   encoding='utf-8')
    return python


# Invoked by the guard only after materialization. -I disables user/PYTHONPATH
# injection; the venv still exposes declared system packages such as pcbnew.
# Required CAD modules must come from the inventoried payload, never that host.
LAUNCH = RENDER_PROBE+'''import importlib,json,runpy,sys
from pathlib import Path
prefix=Path(sys.prefix).resolve()
config=json.loads(sys.argv[1])
modules=config if isinstance(config,list) else config['modules']
for name in modules:
    module=importlib.import_module(name)
    paths=list(getattr(module,'__path__',[]))
    if getattr(module,'__file__',None): paths.append(module.__file__)
    if not paths or not all(Path(p).resolve().is_relative_to(prefix) for p in paths):
        raise ValueError('required runtime module escaped capsule: '+name)
if isinstance(config,dict) and rendering_profile()!=config['graphics']['profile']:
    raise ValueError('guarded renderer differs from declared profile; no fallback')
script=Path(sys.argv[2]);sys.argv=sys.argv[2:]
sys.path.insert(0,str(script.parent))
runpy.run_path(str(script),run_name='__main__')
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build','validate','bind-renderer'])
    parser.add_argument('--venv', type=Path); parser.add_argument('--capsule', type=Path, required=True)
    parser.add_argument('--module', action='append')
    parser.add_argument('--source-capsule',type=Path)
    parser.add_argument('--graphics-device',action='append')
    args = parser.parse_args()
    if args.action=='build':result=build(args.venv.resolve(),args.capsule.resolve(),args.module)
    elif args.action=='bind-renderer':result=bind_renderer(args.source_capsule.resolve(),args.capsule.resolve(),args.venv.resolve(),args.graphics_device or [])
    else:result=validate(args.capsule)
    print(dump(result))


if __name__ == '__main__':
    main()
