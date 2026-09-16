#!/usr/bin/env python3
"""Startup qualification: real native control pair, cache and failure admission."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import check, eq, main, test, tmpdir, run, must_fail
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/pcb-design/scripts'))
from pipeline_qualification import qualify, fingerprint, cached_native


@test("qualification grades exact native pad pairs and reuses only stable evidence")
def t_native():
    root = tmpdir('qualification_')
    first, path = qualify(root, audits=False)
    eq(first['native']['status'], 'PASS', str(first['failures']))
    eq(first['native']['cached'], False, 'first native run')
    eq(first['reviewer']['status'], 'UNKNOWN', 'native probe cannot certify reviewer')
    second, _ = qualify(root, audits=False)
    eq(second['native']['cached'], True, str(second['failures']))
    (root / 'unrelated-board-edit.txt').write_text('not an API dependency')
    third, _ = qualify(root, audits=False)
    eq(third['native']['cached'], True, 'unrelated board edit does not invalidate native cache')
    check(path.exists(), 'durable qualification result')


@test("qualification catches missing tools before board work", kind="known_bad")
def t_missing():
    root = tmpdir('qualification_')
    result, path = qualify(root, cli='/definitely/missing/kicad-cli')
    eq(result['status'], 'INCOMPLETE', 'missing tool cannot qualify')
    check('missing tool' in result['failures'][0], 'named remedy')
    eq(result['attempts'], [], 'no expensive probe admitted')
    check(path.exists(), 'failed qualification retained')


@test("qualification cache rejects changed binaries, probe config and evidence", kind="known_bad")
def t_cache():
    root = tmpdir('qualification_cache_')
    tool = root / 'tool'; tool.write_text('v1')
    digest, _ = fingerprint([tool], {'schema': 1})
    from pipeline_runtime import _file_sha256
    cache = root / 'cache.json'
    cache.write_text(json.dumps({'fingerprint': digest, 'status': 'PASS',
                                'evidence': {str(tool): _file_sha256(tool)}}))
    check(cached_native(cache, digest), 'control cache accepted')
    changed, _ = fingerprint([tool], {'schema': 2})
    eq(cached_native(cache, changed), None, 'changed configuration rejected')
    tool.write_text('v2')
    changed, _ = fingerprint([tool], {'schema': 1})
    check(changed != digest, 'binary/probe content participates')
    eq(cached_native(cache, digest), None, 'modified evidence rejected even with old digest')
    cache.write_text('{}')
    eq(cached_native(cache, digest), None, 'partial cache refused')


@test("qualification refuses a CLI without complete native reporting", kind="known_bad")
def t_hostile_tool():
    root = tmpdir('qualification_cli_')
    cli = root / 'kicad-cli'
    cli.write_text('#!/bin/sh\necho "unknown option --all-track-errors"\nexit 2\n')
    cli.chmod(0o755)
    result, _ = qualify(root, cli=str(cli), audits=False)
    eq(result['native']['status'], 'INCOMPLETE', 'unsupported reporting blocks native')
    check(result['failures'], 'named probe failure')
    check(not (root / '06_build/cache/native-qualification.json').exists(), 'failed run never cached')


@test("qualification library public CLI failure carries input and coverage", kind="known_bad")
def t_cli_missing():
    # Exercise the actual library through its maintained pcb_flow entry point.
    module = ROOT / "skills/pcb-design/scripts/pipeline_qualification.py"
    check(module.is_file(), "owning library exists")
    root = tmpdir("qualification_cli_failure_")
    result = run([sys.executable, str(ROOT / "skills/kicad-pcb/scripts/pcb_flow.py"),
                  "qualify", str(root), "--kicad-cli", "/missing/kicad-cli"])
    must_fail(result, "missing executable must block the public qualification entry")
    check(str(root) in result.out and "coverage=0/4" in result.out, "subject and full denominator")


@test("native probe catches class fallback after project reload", kind="known_bad")
def t_class_fallback():
    import os
    root = tmpdir("qualification_class_")
    (root / "outputs").mkdir(); (root / "scratch").mkdir()
    probe = ROOT / "skills/kicad-pcb/scripts/qualification_probe.py"
    source = probe.read_text()
    check('dict(cls, name="Probe", priority=0, clearance=.25)' in source, "single class mutation located")
    broken = root / "broken_probe.py"
    broken.write_text(source.replace('dict(cls, name="Probe", priority=0, clearance=.25)',
                                    'dict(cls, name="Unexpected", priority=0, clearance=.25)'))
    env = dict(os.environ, PCB_TASK_OUTPUT_DIR=str(root / "outputs"),
               PCB_TASK_SCRATCH_DIR=str(root / "scratch"), PCB_QUALIFY_KICAD_CLI="kicad-cli",
               PCB_TASK_SUBJECT_JSON="{}", PYTHONPATH=str(probe.parent),
               KICAD_CONFIG_HOME=str(root / "scratch/config"))
    result = run([sys.executable, str(broken), "native"], env=env)
    must_fail(result, "class fallback must fail before DRC can mask schema loss")
    check("netclass fallback after reload" in result.out, "failed on class identity")


if __name__ == '__main__':
    raise SystemExit(main())
