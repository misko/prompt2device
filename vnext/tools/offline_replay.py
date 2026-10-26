"""Linux offline replay guard: no networking or access to the original workspace.

Runs trusted, hash-checked archive tooling in disposable scratch. Not an
untrusted-code sandbox: /etc and system runtime files remain readable.
"""
import argparse
import ctypes as c
import errno
import os
from pathlib import Path
import runpy
import sys


def restrict(scratch, readonly_archive=False, graphics_devices=()):
    libc = c.CDLL(None, use_errno=True)
    def call(number, *args):
        result = libc.syscall(number, *args)
        if result < 0: raise OSError(c.get_errno(), os.strerror(c.get_errno()))
        return result
    # Landlock syscall numbers on supported Linux x86_64/aarch64.
    if os.uname().machine not in ('x86_64', 'aarch64'):
        raise RuntimeError('offline guard requires Linux x86_64/aarch64')
    abi = call(444, 0, 0, 1)
    if abi < 3: raise RuntimeError('Landlock ABI >=3 required; no silent fallback')
    rights = (1 << 15) - 1  # through TRUNCATE; REFER needs ABI2.
    class Ruleset(c.Structure): _fields_ = [('handled_access_fs', c.c_uint64)]
    class PathRule(c.Structure):
        _pack_ = 1
        _fields_ = [('allowed_access', c.c_uint64), ('parent_fd', c.c_int32)]
    rule = Ruleset(rights); fd = call(444, c.byref(rule), c.sizeof(rule), 0)
    try:
        local_rules=[(scratch,13),(scratch/'work',rights)] if readonly_archive else [(scratch,rights)]
        if graphics_devices:
            if not readonly_archive:raise ValueError('graphics grant requires read-only archive')
            import release_runtime
            local_rules.extend((Path(n),6) for n in release_runtime.graphics_devices(graphics_devices))
        for path, access in [*local_rules, *[(Path(n), 13) for n in
                             ('/usr', '/lib', '/lib64', '/bin', '/etc', '/proc', '/dev')]]:
            if not path.exists(): continue
            pfd = os.open(path, os.O_PATH | os.O_CLOEXEC)
            try:
                item = PathRule(access, pfd); call(445, fd, 1, c.byref(item), 0)
            finally: os.close(pfd)
        if libc.prctl(38, 1, 0, 0, 0): raise OSError(c.get_errno(), 'no_new_privs failed')
        call(446, fd, 0)
    finally: os.close(fd)
    # The filter is inherited by all subprocesses, including KiCad and producers.
    sec = c.CDLL('libseccomp.so.2', use_errno=True)
    sec.seccomp_init.argtypes = [c.c_uint32]; sec.seccomp_init.restype = c.c_void_p
    sec.seccomp_syscall_resolve_name.argtypes = [c.c_char_p]
    sec.seccomp_rule_add.argtypes = [c.c_void_p,c.c_uint32,c.c_int,c.c_uint]
    sec.seccomp_load.argtypes = [c.c_void_p]; sec.seccomp_release.argtypes = [c.c_void_p]
    ctx = sec.seccomp_init(0x7fff0000)
    if not ctx: raise RuntimeError('seccomp initialization failed')
    try:
        for name in (b'socket', b'socketpair'):
            number = sec.seccomp_syscall_resolve_name(name)
            if number < 0 or sec.seccomp_rule_add(ctx, 0x50000 | errno.EPERM, number, 0):
                raise RuntimeError('network filter creation failed')
        if sec.seccomp_load(ctx): raise RuntimeError('network filter load failed')
    finally: sec.seccomp_release(ctx)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch', required=True, type=Path)
    parser.add_argument('--readonly-archive', action='store_true')
    parser.add_argument('--runtime', type=Path,
                        help='Inventoried capsule within the read-only archive; v2 only')
    parser.add_argument('script', type=Path); parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args(); scratch = args.scratch.resolve(); script = args.script.resolve()
    if not script.is_relative_to(scratch): raise ValueError('script outside scratch')
    work=scratch/'work' if args.readonly_archive else scratch
    work.mkdir(exist_ok=True)
    if args.readonly_archive and script.is_relative_to(work):
        raise ValueError('archive script must be outside writable work directory')
    runtime = None
    if args.runtime:
        import release_runtime
        runtime = args.runtime.resolve()
        if not args.readonly_archive or not runtime.is_relative_to(scratch) or runtime.is_relative_to(work):
            raise ValueError('runtime capsule must be in read-only scratch archive')
        record = release_runtime.validate(runtime)
    os.chdir(work); os.environ['TMPDIR'] = str(work)
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'; sys.dont_write_bytecode = True
    graphics=record.get('graphics') if runtime else None
    if graphics:release_runtime.graphics_environment(graphics)
    restrict(scratch,args.readonly_archive,graphics['devices'] if graphics else ())
    if runtime:
        python = release_runtime.materialize(runtime, work/'runtime')
        # Existing assembly/mating owners use sys.executable when their original
        # workspace venv is absent. Keep those accepted tools byte-identical.
        import json
        os.execv(str(python), [str(python), '-I', '-B', '-c', release_runtime.LAUNCH,
                              json.dumps(dict(modules=record['modules'],graphics=graphics) if graphics else record['modules']), str(script), *args.args])
    sys.path.insert(0, str(script.parent)); sys.argv = [str(script), *args.args]
    runpy.run_path(str(script), run_name='__main__')


if __name__ == '__main__': main()
