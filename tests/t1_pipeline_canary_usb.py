#!/usr/bin/env python3
"""T1: USB Hub v4 deterministic-reuse shadow catalog canary.

Catalog tests parse declarations and exact legacy bytes without execution.
Bounded source-rules and rules-artifact pilots additionally execute selected
hash-pinned shell steps and catalog commands on disposable input copies only.
They neither run the whole driver nor change its authority.
"""
from __future__ import annotations

import copy
import hashlib
import shutil
import tempfile
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import KPY, SCRIPTS, check, contains, eq, main, must_fail, must_pass, run, test, tmpdir  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "archived_projects" / "usb-hub-3s-v4"
CATALOG_PATH = PROJECT / "03_src" / "pipeline_shadow_reuse.json"
DRIVER_PATH = PROJECT / "03_src" / "rebuild_reuse.sh"
ROUTE_PATH = PROJECT / "03_src" / "route.yaml"

sys.path.insert(0, str(ROOT / "skills" / "pcb-design" / "scripts"))
from pipeline_catalog import CatalogValidationError, LegacyPipelineCatalog  # noqa: E402
from pipeline_xtrace import parse_xtrace  # noqa: E402


EXPECTED_DRIVER_SHA256 = (
    "b5a29d9ba23817a376f7589b0c400493de219d9818b2683f9883fe7b58a573b1"
)
EXPECTED_STAGE_IDS = (
    "USBV4-R-MODULE-FIRST-VALID",
    "USBV4-R-DESIGN-SCHEMA-VALID",
    "USBV4-R-SOURCE-RULES-VALID",
    "USBV4-R-PINNED-SUBJECT-RESOLVED",
    "USBV4-R-BUILD-ROUTE-MARKER-INVALIDATED",
    "USBV4-R-NETLIST-PRODUCED",
    "USBV4-R-SCHEMATIC-REVIEWS-ADMISSIBLE",
    "USBV4-R-BOARD-PRODUCED",
    "USBV4-R-PARITY-SCHEMATIC-COPIED",
    "USBV4-R-PIN-MAP-VALID",
    "USBV4-R-BOARD-AUDIT-DISPOSITION",
    "USBV4-R-PLACEMENT-GATES-VALID",
    "USBV4-R-PAD-SEPARATION-VALID",
    "USBV4-R-CRITICAL-PAIR-MAP-VALID",
    "USBV4-R-PLACEMENT-POLICY-VALID",
    "USBV4-R-RULES-PRE-PLACEMENT-DRC",
    "USBV4-R-PLACEMENT-DRC-REPORT",
    "USBV4-R-PLACEMENT-DRC-CLEAN",
    "USBV4-R-RULES-PRE-ROUTE-PREP",
    "USBV4-R-PAD-ESCAPE-VALID",
    "USBV4-R-TIER-PREFLIGHT-VALID",
    "USBV4-R-ROUTE-PREP-PRODUCED",
    "USBV4-R-PLACEMENT-REVIEW-BOUNDARY-PREPARED",
    "USBV4-R-PLACEMENT-REVIEWS-ADMISSIBLE",
    "USBV4-R-PROMOTED-ROUTE-IMPORTED",
    "USBV4-R-ROUTE-TAPS-PRODUCED",
    "USBV4-R-STITCH-PRODUCED",
    "USBV4-R-CRITICAL-ROUTES-CONNECTED",
    "USBV4-R-RULES-POST-STITCH",
    "USBV4-R-REALIZED-RULES-VALID",
    "USBV4-R-VIA-AMPACITY-VALID",
    "USBV4-R-LAYOUT-DRC-REPORT",
    "USBV4-R-LAYOUT-DRC-CLEAN",
)

# Exact source-line dispositions for the hash-pinned driver.  Repeated lines
# within one shell stage collapse only while consecutive; the three rules
# invocations therefore remain three distinct observed stages.
TRACE_STAGE_LINES = {
    48: EXPECTED_STAGE_IDS[0], 50: EXPECTED_STAGE_IDS[1],
    52: EXPECTED_STAGE_IDS[2], 62: EXPECTED_STAGE_IDS[3],
    63: EXPECTED_STAGE_IDS[3], 64: EXPECTED_STAGE_IDS[3],
    65: EXPECTED_STAGE_IDS[3], 67: EXPECTED_STAGE_IDS[4],
    71: EXPECTED_STAGE_IDS[5], 74: EXPECTED_STAGE_IDS[6],
    79: EXPECTED_STAGE_IDS[7], 82: EXPECTED_STAGE_IDS[8],
    86: EXPECTED_STAGE_IDS[9], 91: EXPECTED_STAGE_IDS[10],
    92: EXPECTED_STAGE_IDS[11], 93: EXPECTED_STAGE_IDS[12],
    95: EXPECTED_STAGE_IDS[13], 100: EXPECTED_STAGE_IDS[14],
    103: EXPECTED_STAGE_IDS[15], 104: EXPECTED_STAGE_IDS[16],
    106: EXPECTED_STAGE_IDS[17], 112: EXPECTED_STAGE_IDS[18],
    116: EXPECTED_STAGE_IDS[19], 119: EXPECTED_STAGE_IDS[20],
    121: EXPECTED_STAGE_IDS[21], 128: EXPECTED_STAGE_IDS[22],
    131: EXPECTED_STAGE_IDS[23], 136: EXPECTED_STAGE_IDS[24],
    138: EXPECTED_STAGE_IDS[25], 141: EXPECTED_STAGE_IDS[26],
    142: EXPECTED_STAGE_IDS[27], 146: EXPECTED_STAGE_IDS[28],
    147: EXPECTED_STAGE_IDS[29], 149: EXPECTED_STAGE_IDS[30],
    156: EXPECTED_STAGE_IDS[31], 158: EXPECTED_STAGE_IDS[32],
}
TRACE_FAILURE_LINES = {
    49: EXPECTED_STAGE_IDS[0], 51: EXPECTED_STAGE_IDS[1],
    53: EXPECTED_STAGE_IDS[2], 76: EXPECTED_STAGE_IDS[6],
    88: EXPECTED_STAGE_IDS[9], 94: EXPECTED_STAGE_IDS[12],
    96: EXPECTED_STAGE_IDS[13], 101: EXPECTED_STAGE_IDS[14],
    107: EXPECTED_STAGE_IDS[17], 117: EXPECTED_STAGE_IDS[19],
    120: EXPECTED_STAGE_IDS[20], 133: EXPECTED_STAGE_IDS[23],
    143: EXPECTED_STAGE_IDS[27], 148: EXPECTED_STAGE_IDS[29],
    151: EXPECTED_STAGE_IDS[30],
}
TRACE_IGNORED_LINES = (37, 38, 40, 42, 43, 44, 70, 155, 166)


def source_mapping():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def catalog():
    return LegacyPipelineCatalog.from_json(
        CATALOG_PATH.read_text(encoding="utf-8"))


def by_key(value, key):
    return next(row for row in value.bindings if row.legacy_key == key)


def trace_key(line):
    return ("project/03_src/rebuild_reuse.sh", line)


@test("USB reuse catalog binds the exact declaration and current driver bytes")
def t_exact_files_and_driver():
    value = catalog()
    eq(value.project_slug, "usb-hub-3s-v4", "project identity")
    eq(value.driver_relative_path, "03_src/rebuild_reuse.sh", "driver path")
    eq(value.driver_sha256, EXPECTED_DRIVER_SHA256, "catalog driver digest")
    driver = DRIVER_PATH.read_bytes()
    check(value.driver_matches(driver), "current rebuild_reuse.sh bytes drifted")
    check(not value.driver_matches(driver + b"\n"),
          "mutated driver bytes matched the catalog")


@test("USB reuse catalog preserves all 33 observed stages in exact order")
def t_order_and_denominator():
    value = catalog()
    eq(len(value.bindings), 33, "catalog denominator")
    eq(value.observed_stage_ids(), EXPECTED_STAGE_IDS, "legacy order")
    plan = value.stage_registry().resolve(
        available=("usbv4_reuse_source_tree",))
    eq(tuple(stage.id for stage in plan), EXPECTED_STAGE_IDS,
       "strict one-fact dependency order")
    for prior, current in zip(value.bindings, value.bindings[1:]):
        eq(current.dependencies, (prior.spec.id,),
           f"{current.legacy_key} direct dependency")
        eq(tuple(current.spec.requires), tuple(prior.spec.produces),
           f"{current.legacy_key} semantic handoff")


@test("USB reuse commands remain portable inert argv data")
def t_portable_nonexecuting_commands():
    value = catalog()
    check(not hasattr(value, "execute"), "catalog unexpectedly exposes execution")
    for row in value.bindings:
        eq(row.cwd, ".", f"{row.legacy_key} cwd")
        if row.argv is not None:
            joined = "\0".join(row.argv)
            check("/home/" not in joined, f"{row.legacy_key} captured a host path")
            check("$(" not in joined and ";" not in joined,
                  f"{row.legacy_key} argv became shell syntax")
        for path in row.accepted_output_paths:
            check(not path.startswith("/") and ".." not in Path(path).parts,
                  f"{row.legacy_key} output path is not normalized: {path}")
    python_rows = [row for row in value.bindings
                   if row.argv and row.argv[0] == "/usr/bin/python3"]
    check(python_rows, "no Python command evidence was cataloged")
    check(all("{repo}/" in row.argv[1] for row in python_rows),
          "Python tool paths are not portable {repo} literals")


@test("USB reuse keeps all three rule rewrites as distinct stages")
def t_repeated_rules_distinct():
    value = catalog()
    rows = tuple(by_key(value, key) for key in (
        "rules-pre-placement-drc", "rules-pre-route-prep", "rules-post-stitch"))
    eq(tuple(row.sequence for row in rows), (16, 19, 29), "rule positions")
    eq(tuple(row.spec.id for row in rows), (
        "USBV4-R-RULES-PRE-PLACEMENT-DRC",
        "USBV4-R-RULES-PRE-ROUTE-PREP",
        "USBV4-R-RULES-POST-STITCH",
    ), "distinct rule stage identities")
    check(rows[0].argv == rows[1].argv == rows[2].argv,
          "repeated rule producer argv drifted")
    check(len({tuple(row.spec.produces) for row in rows}) == 3,
          "repeated rules reused one semantic output")


@test("USB reuse records the current generic-board audit as explicit N/A")
def t_board_audit_na():
    value = catalog()
    row = by_key(value, "board-audit-na")
    eq(row.sequence, 11, "N/A position")
    eq(row.applicability, "NOT_APPLICABLE", "N/A applicability")
    eq(row.applicability_reason,
       "generic-backend board has no 03_src/audit_board.py", "N/A reason")
    eq(row.shell_builtin, "not_applicable", "N/A command token")
    eq(row.accepted_output_symbols, (), "N/A accepted symbols")
    eq(row.accepted_output_paths, (), "N/A accepted paths")
    check(not (PROJECT / "03_src" / "audit_board.py").exists(),
          "catalog says N/A but audit_board.py now exists")


@test("USB reuse import evidence agrees with promoted-route configuration")
def t_promoted_import():
    value = catalog()
    route = yaml.safe_load(ROUTE_PATH.read_text(encoding="utf-8"))
    eq(route["route"]["import_source"], "promoted", "route import policy")
    eq(route["route"]["final"], "03_src/route/r8.kicad_pcb",
       "promoted route subject")
    row = by_key(value, "route-import")
    eq(row.sequence, 25, "route import position")
    eq(row.argv, (
        "/usr/bin/python3",
        "{repo}/skills/kicad-pcb/scripts/route_and_stitch_generic.py",
        "import",
        "03_src/route.yaml",
    ), "reuse import argv")
    check("--route-source" not in row.argv,
          "catalog invented a flag absent from rebuild_reuse.sh")
    marker = by_key(value, "route-marker-reset")
    eq((marker.authority, marker.authority_binding),
       ("ignored_until", "route-import"), "ignored marker-reset authority")


@test("USB reuse producer reports retain their later postcheck authority")
def t_postcheck_authority():
    value = catalog()
    placement = by_key(value, "placement-drc-report")
    layout = by_key(value, "layout-drc-report")
    eq((placement.authority, placement.authority_binding),
       ("postcheck", "placement-drc-verdict"), "placement DRC authority")
    eq((layout.authority, layout.authority_binding),
       ("postcheck", "layout-drc-verdict"), "layout DRC authority")


@test("USB reuse xtrace line map covers the exact catalog without executing it")
def t_xtrace_map():
    source_lines = DRIVER_PATH.read_text(encoding="utf-8").splitlines()
    all_declared = (set(TRACE_STAGE_LINES) | set(TRACE_FAILURE_LINES) |
                    set(TRACE_IGNORED_LINES))
    check(max(all_declared) <= len(source_lines), "trace line exceeds driver")
    for line in all_declared:
        text = source_lines[line - 1].strip()
        check(text and not text.startswith("#"),
              f"trace line {line} no longer names executable shell text")

    records = [
        f"+PIPELINE_TRACE:{DRIVER_PATH}:{line}: opaque line {line}"
        for line in sorted(TRACE_STAGE_LINES)
    ]
    observed = parse_xtrace(
        "\n".join(records) + "\n",
        {trace_key(line): stage for line, stage in TRACE_STAGE_LINES.items()},
        project_root=PROJECT, repo_root=ROOT,
        expected_driver_sha256=EXPECTED_DRIVER_SHA256,
        trace_driver_sha256=EXPECTED_DRIVER_SHA256, trace_complete=True)
    eq(observed.observed_stage_ids, EXPECTED_STAGE_IDS,
       "source-line observation order")
    check(observed.fully_mapped, "declared USB trace retained unmapped commands")


@test("USB reuse catalog REFUSES a severed semantic chain",
      kind="known_bad")
def t_mutated_catalog_refused():
    clean = source_mapping()
    LegacyPipelineCatalog.from_mapping(copy.deepcopy(clean))
    broken = copy.deepcopy(clean)
    broken["bindings"][18]["dependencies"] = []
    try:
        LegacyPipelineCatalog.from_mapping(broken)
    except CatalogValidationError as exc:
        check("missing from dependencies" in str(exc),
              f"severed-chain diagnosis: {exc}")
    else:
        raise AssertionError("catalog with a severed dependency SHOULD HAVE FAILED")


@test("USB source-rules stage matches legacy shell catalog and accounted execution",
      kind="known_bad")
def t_source_rules_stage_pilot():
    value = catalog()
    driver = DRIVER_PATH.read_bytes()
    check(value.driver_matches(driver), 'pilot refuses driver/catalog drift')
    binding = by_key(value, 'source-rules')
    eq(binding.authority, 'exit', 'owning verdict remains exit status')
    eq(binding.accepted_output_paths, (), 'source checker publishes no artifact')
    # The existing hash-pinned trace map assigns these exact two lines to
    # source-rules and its failure handler. Never execute the remaining driver.
    eq(TRACE_STAGE_LINES[52], binding.spec.id, 'legacy invocation owner')
    eq(TRACE_FAILURE_LINES[53], binding.spec.id, 'legacy failure owner')
    snippet = '\n'.join(driver.decode().splitlines()[51:53])
    contains(snippet, '"$S/rules_audit.py" . --phase source', 'literal legacy command')
    stage_ids = list(value.observed_stage_ids())
    impact = value.stage_registry().change_impact(changed_stage_ids=(binding.spec.id,))
    eq(impact['affected'], stage_ids[2:], 'actual catalog conservative downstream closure')
    eq(impact['unaffected'], stage_ids[:2], 'upstream stages outside declared method change')
    eq(impact['authority'], 'DIAGNOSTIC_ONLY', 'graph remains diagnostic')
    eq(impact['reuse_authorized'], False, 'no upstream cache grant')
    root = tmpdir('usb_source_stage_')
    (root/'03_src/rules').mkdir(parents=True)
    # Copy the actual flow configuration unchanged; no generated board needed.
    shutil.copy2(ROUTE_PATH, root/'03_src/route.yaml')
    shutil.copy2(PROJECT/'03_src/floorplan.yaml', root/'03_src/floorplan.yaml')
    # Accounting requires nonvacuous part-card inputs even though this
    # source-only checker reads nets.yaml alone. Copy cards, not large PDFs.
    for card in (PROJECT/'02_parts').glob('*/part.yaml'):
        target = root/card.relative_to(PROJECT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(card, target)
    (root/'03_tscircuit').mkdir()
    nets = root/'03_src/rules/nets.yaml'
    original = (PROJECT/'03_src/rules/nets.yaml').read_bytes()
    ledger = root/'01_docs/issue_usage.jsonl'
    command = [arg.replace('{repo}', str(ROOT)).replace('{project}', str(root))
               for arg in binding.argv]
    eq(binding.cwd, '.', 'same project-root cwd')
    def diagnostics(result):
        return [line.strip() for line in result.out.splitlines()
                if line.strip().startswith(('ok ', 'FAIL ', 'coverage ', 'RULES SOURCE AUDIT:'))]
    for bad in (False, True, False):
        if bad:
            changed = yaml.safe_load(original)
            changed['classes']['VIN_TRUNK']['nets'] = []
            nets.write_text(yaml.safe_dump(changed))
        else:
            nets.write_bytes(original)
        before = nets.read_bytes()
        # Execute the exact source-stage shell and original failure handler,
        # not a Python approximation of the driver's shell semantics.
        legacy = run(['bash', '-c', 'set -euo pipefail\nPY="$1"; S="$2"\n'+snippet,
                      'source-stage-pilot', KPY, SCRIPTS], cwd=root)
        direct = run(command, cwd=root)
        wrapped = run([KPY, SCRIPTS/'pcb_flow.py', 'run', root,
                       '--stage', binding.spec.id, '--timeout-s', str(binding.spec.timeout_s),
                       '--issue', 'usb-source-rules', '--usage-ledger', ledger,
                       '--', *command], cwd=root)
        for result in (legacy, direct, wrapped):
            if bad:
                must_fail(result, 'empty class membership must reject', 'A-SOURCE')
            else:
                must_pass(result, 'real source-rule baseline')
            eq(result.rc, 1 if bad else 0, 'owning shell/checker verdict')
        eq(diagnostics(direct), diagnostics(legacy), 'catalog preserves legacy domain findings')
        eq(diagnostics(wrapped), diagnostics(legacy), 'runner preserves legacy domain findings')
        check(diagnostics(legacy), 'nonempty diagnostic census')
        eq(nets.read_bytes(), before, 'read-only stage preserves source')
    events = [json.loads(line) for line in ledger.read_text().splitlines()]
    starts = [row for row in events if row['event_type']=='START']
    ends = [row for row in events if row['event_type']=='TERMINAL']
    eq(len(starts),3,'exact stage execution count')
    check(all(row['stage_id']==binding.spec.id and row['issue_id']=='usb-source-rules'
              for row in events), 'exact catalog stage and stable issue attribution')
    eq([row['status'] for row in ends], ['PASS','FAIL','PASS'], 'failed stage retained')
    eq(len({row['attempt_id'] for row in starts}),3,'distinct accounted attempts')
    expected_command_hash = hashlib.sha256(json.dumps(command).encode()).hexdigest()
    check(all(row['provenance']['command_sha256']==expected_command_hash for row in starts),
          'accounting binds the expanded catalog argv')
    hashes = [row['provenance']['source_sha256'] for row in starts]
    eq(hashes[0],hashes[2],'restored real source identity')
    check(hashes[0]!=hashes[1],'invalid source changes attribution identity')
    check(all(row['token_usage'] is None for row in ends), 'no invented model tokens')
    eq((PROJECT/'03_src/rules/nets.yaml').read_bytes(), original, 'archived source untouched')
    check(not (root/'04_kicad').exists(), 'source stage needs no board artifacts')
    check(not (root/'07_releases').exists(), 'stage comparison cannot release')


@test("USB rules artifact pilot validates both outputs and preserves acceptance on failure",
      kind="known_bad")
def t_rules_artifact_pilot():
    from pipeline_artifacts import (ArtifactBundleTransaction, OutputSpec,
                                    ArtifactProducerError, ArtifactValidationError)
    value = catalog()
    check(value.driver_matches(DRIVER_PATH.read_bytes()), 'exact legacy producer binding')
    binding = by_key(value, 'rules-pre-placement-drc')
    eq(TRACE_STAGE_LINES[103], binding.spec.id, 'exact producer source line')
    snippet = DRIVER_PATH.read_text().splitlines()[102]
    contains(snippet, '"$S/generate_rules_generic.py" .', 'literal legacy producer')
    eq(binding.authority, 'exit', 'legacy producer authority unchanged')
    pro_name = '04_kicad/usb_hub_3s_v4.kicad_pro'
    dru_name = '04_kicad/usb_hub_3s_v4.kicad_dru'
    eq(set(binding.accepted_output_paths), {pro_name, dru_name}, 'exact output pair')
    root = tmpdir('usb_rule_artifact_')
    seed = root/'seed'; seed.mkdir()
    inputs = {}
    for rel in ('03_src/rules/nets.yaml', '03_src/floorplan.yaml', '03_src/route.yaml',
                pro_name, dru_name, '04_kicad/usb_hub_3s_v4.kicad_pcb'):
        target=seed/rel; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT/rel,target); inputs[rel]=target
    for card in (PROJECT/'02_parts').glob('*/part.yaml'):
        rel=card.relative_to(PROJECT); target=seed/rel
        target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(card,target)
        inputs[rel.as_posix()]=target
    (seed/'03_tscircuit').mkdir()
    inputs['driver.sh']=DRIVER_PATH
    for name in ('generate_rules_generic.py','dru_subject.py','fab_tier_util.py','rules_audit.py'):
        inputs['tools/'+name]=SCRIPTS/name
    nets=seed/'03_src/rules/nets.yaml'; original=nets.read_bytes()
    accepted=root/'accepted'; ledger=root/'usage.jsonl'
    audit_count=[]
    def reopen(staging, opened):
        eq(set(opened),{pro_name,dru_name},'durably reopened exact output pair')
        result=run([KPY,SCRIPTS/'rules_audit.py','--nets',nets,
                    '--pro',staging/pro_name,'--dru',staging/dru_name,
                    '--board',seed/'04_kicad/usb_hub_3s_v4.kicad_pcb'])
        audit_count.append(result.rc)
        if result.rc:
            raise ArtifactValidationError('independent rules audit rejected: '+result.out)
        contains(result.out,'RULES AUDIT: PASS','independent postcheck ran')
    def attempt(mode, fault=None):
        # Conservative raw subject; no semantic cache/reuse claim is made.
        digest=hashlib.sha256(json.dumps({k:hashlib.sha256(v.read_bytes()).hexdigest()
                                         for k,v in sorted(inputs.items())},sort_keys=True).encode()).hexdigest()
        tx=ArtifactBundleTransaction(accepted,producer=binding.spec.id,
            producer_version=hashlib.sha256((SCRIPTS/'generate_rules_generic.py').read_bytes()).hexdigest(),
            subject={'semantic_sha256':digest,'raw_sha256':digest},inputs=inputs,
            outputs={pro_name:OutputSpec(parser=lambda p:json.loads(p.read_text())),
                     dru_name:OutputSpec(parser=lambda p:p.read_text())})
        def produce(staging):
            if fault=='missing': return 0  # stale accepted pair must not count
            with tempfile.TemporaryDirectory(prefix='workspace-',dir=root) as temporary:
                workspace=Path(temporary)/'project'; shutil.copytree(seed,workspace)
                command=[arg.replace('{repo}',str(ROOT)).replace('{project}',str(workspace))
                         for arg in binding.argv]
                if mode=='legacy':
                    argv=['bash','-c','set -euo pipefail\nPY="$1"; S="$2"\n'+snippet,
                          'artifact-pilot',KPY,SCRIPTS]
                elif mode=='accounted':
                    argv=[KPY,SCRIPTS/'pcb_flow.py','run',workspace,'--stage',binding.spec.id,
                          '--timeout-s',str(binding.spec.timeout_s),'--issue','usb-rule-artifacts',
                          '--usage-ledger',ledger,'--',*command]
                else: argv=command
                result=run(argv,cwd=workspace)
                if result.rc: return result.rc
                for name in (pro_name,dru_name):
                    target=staging/name;target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(workspace/name,target)
                    if fault=='partial': return 1
                if fault=='corrupt':
                    doc=json.loads((staging/pro_name).read_text())
                    next(c for c in doc['net_settings']['classes'] if c['name']=='VIN_TRUNK')['track_width']=.1
                    (staging/pro_name).write_text(json.dumps(doc))
                return 0
        return tx.publish(produce,reopen_validator=reopen)
    def snapshot():
        return {p.relative_to(accepted).as_posix():p.read_bytes()
                for p in accepted.rglob('*') if p.is_file()}
    baseline=None
    for mode in ('legacy','catalog','accounted'):
        attempt(mode)
        settings=json.loads((accepted/pro_name).read_text())['net_settings']
        if baseline is None: baseline=settings
        eq(settings,baseline,'same generated netclass semantics across execution paths')
        manifest=json.loads((accepted/'bundle.json').read_text())
        eq(set(manifest['outputs']),{pro_name,dru_name},'both outputs admitted together')
        for name in (pro_name,dru_name):
            eq(manifest['outputs'][name]['sha256'],hashlib.sha256((accepted/name).read_bytes()).hexdigest(),
               'accepted output binding')
    eq(audit_count,[0,0,0],'each clean path independently audited')
    previous=snapshot()
    bad=yaml.safe_load(original);bad['classes']['VIN_TRUNK']['min_width']='0.001mm'
    nets.write_text(yaml.safe_dump(bad))
    for mode in ('legacy','catalog','accounted'):
        try: attempt(mode)
        except ArtifactProducerError: pass
        else: raise AssertionError('invalid source admitted an artifact pair')
        eq(snapshot(),previous,'failed generation preserves previous accepted pair')
    nets.write_bytes(original)
    for fault, error in (('missing',ArtifactValidationError),('partial',ArtifactProducerError),
                         ('corrupt',ArtifactValidationError)):
        try: attempt('accounted',fault)
        except error: pass
        else: raise AssertionError(f'{fault} outputs admitted')
        eq(snapshot(),previous,'failed output admission preserves previous bundle')
        eq(list(root.glob('.accepted.txn-*')),[],'failed staging cleaned')
        eq(list(root.glob('workspace-*')),[],'disposable producer workspace cleaned')
    check(audit_count[-1]!=0,'corruption reached independent rules checker')
    events=[json.loads(line) for line in ledger.read_text().splitlines()]
    ends=[row for row in events if row['event_type']=='TERMINAL']
    eq([row['status'] for row in ends],['PASS','FAIL','PASS','PASS'],
       'producer success remains separate from failed artifact admission')
    check(all(row['stage_id']==binding.spec.id for row in events),'exact stage attribution')
    eq((PROJECT/'03_src/rules/nets.yaml').read_bytes(),original,'archive unchanged')
    check(not (root/'07_releases').exists(),'artifact bundle is not a release')


if __name__ == "__main__":
    raise SystemExit(main())
