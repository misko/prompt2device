#!/usr/bin/env python3
"""Decision-control behavior, not simulated electrical acceptance.

The handoff integration test was run against the original pcb_flow.py before
the integration change: it fails because the ledger is absent from the saved
handoff. New evaluator predicates have executed hostile-input controls.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import ROOT, KPY, SCRIPTS, eq, main, must_fail, must_pass, run, test, tmpdir

DESIGN = ROOT / 'skills/pcb-design/scripts'
sys.path.insert(0, str(DESIGN))
sys.path.insert(0, str(SCRIPTS))
import decision_progress as guard
import pcb_flow
import project_state


def fixture():
    root = tmpdir('decision-progress-')
    (root / '01_docs').mkdir()
    (root / '03_src').mkdir()
    (root / '02_parts').mkdir()
    (root / '02_parts/X').mkdir()
    (root / '02_parts/X/part.yaml').write_text('mpn: X\n')
    (root / '03_tscircuit').mkdir()
    (root / '04_kicad').mkdir()
    (root / '01_docs/BRIEF.md').write_text('G1: safe cold startup.\n')
    (root / '01_docs/result.md').write_text('Bounded source test evidence.\n')
    (root / '03_src/route.yaml').write_text(yaml.safe_dump({
        'project': {'board': '04_kicad/test.kicad_pcb'},
        'flow': {'owner': {'stage': 'schematic', 'files': []}}}))
    (root / '04_kicad/test.kicad_pcb').write_text('(kicad_pcb)\n')
    ref = lambda p: {'path': p, 'sha256': hashlib.sha256((root / p).read_bytes()).hexdigest()}
    f = {'id': 'startup', 'state': 'open', 'owner': 'electrical',
         'blocks_at_or_above': 'DESIGN_CLEAN', 'finding': 'Protection unresolved',
         'closes_when': 'Exact source protection tests and independent review pass',
         'investigation': {
             'schema': 1, 'requirement': {**ref('01_docs/BRIEF.md'), 'locator': 'G1'},
             'due_stage': 'KICAD-SCHEMATIC', 'operating_states': ['cold_start'],
             'question': 'Which protection topology meets G1?',
             'milestones': {'eliminate_A': 'A cannot meet the input-current limit',
                            'select_B': 'B has defensible margin across the admitted states'},
             'max_nonimproving_attempts': 3, 'max_attempts': 6, 'launches': [], 'history': [],
             'next': {'action': 'investigate', 'hypothesis': 'B limits the startup current',
                      'on_support': 'Implement B for source review',
                      'on_reject': 'Reject B and compare C', 'uncertainty': 'bounded'}}}
    data = {'schema': 1, 'target': 'DRAFT', 'gates': [
        {'id': 'source-review', 'required_for': 'DESIGN_CLEAN', 'state': 'pending',
         'owner': 'electrical', 'closes_when': 'Independent source review passes'}], 'findings': [f]}
    return root, data, ref('01_docs/result.md')


def observation(index, evidence, progress=(), domain='within'):
    return {'id': f'run-{index}', 'subject_sha256': f'{index:064x}',
            'origin': 'historical_assessment', 'hypothesis': f'Candidate experiment {index}',
            'result': 'Coordinator-assessed result; not a board verdict',
            'model_domain': domain, 'progress': list(progress), 'evidence': [evidence]}


def save(root, data):
    (root / '01_docs/findings.yaml').write_text(yaml.safe_dump(data, sort_keys=False))


def cli(root, *args):
    return run([KPY, DESIGN / 'decision_progress.py', root, *args])


@test('decision guard allows a bounded first experiment without granting engineering acceptance')
def t_first():
    root, data, _ = fixture(); save(root, data)
    result = json.loads(must_pass(cli(root), 'first experiment').out)
    eq(result['decision'], 'CONTINUE_BOUNDED')
    eq(result['engineering_admitted'], False)
    eq(project_state.derive(root, root / '01_docs/findings.yaml')['derived_maturity'], 'DRAFT')


@test('decision guard stops report/model/subject churn across handoffs', kind='known_bad')
def t_plateau():
    root, data, ref = fixture()
    inv = data['findings'][0]['investigation']
    inv['history'] = [observation(i, ref) for i in range(1, 4)]
    save(root, data)
    before = (root / '01_docs/findings.yaml').read_bytes()
    r = must_fail(cli(root), 'three non-improving attempts', 'REASSESS')
    eq(r.rc, 1)
    eq(json.loads(r.out)['investigations'][0]['attempts'], 3)
    eq((root / '01_docs/findings.yaml').read_bytes(), before)
    eq(json.loads(must_pass(cli(root, '--shadow'), 'shadow').out)['decision'], 'REASSESS')


@test('decision guard credits a finite milestone once, not repeatedly', kind='known_bad')
def t_repeat_credit():
    root, data, ref = fixture()
    inv = data['findings'][0]['investigation']
    inv['history'] = [observation(i, ref, ['eliminate_A']) for i in range(1, 5)]
    save(root, data)
    r = json.loads(must_fail(cli(root), 'repeated milestone', 'REASSESS').out)
    eq(r['investigations'][0]['credited_milestones'], ['eliminate_A'])
    eq(r['investigations'][0]['nonimproving_attempts'], 3)


@test('decision guard recognizes candidate elimination and preserves total budget', kind='known_bad')
def t_progress_and_cap():
    root, data, ref = fixture()
    inv = data['findings'][0]['investigation']
    inv['history'] = [observation(1, ref), observation(2, ref),
                      observation(3, ref, ['eliminate_A'])]
    save(root, data)
    eq(json.loads(must_pass(cli(root), 'candidate eliminated').out)
       ['investigations'][0]['nonimproving_attempts'], 0)
    inv['history'] += [observation(4, ref), observation(5, ref),
                       observation(6, ref, ['select_B'])]
    save(root, data)
    r = json.loads(must_fail(cli(root), 'finite total budget', 'REASSESS').out)
    eq(r['investigations'][0]['nonimproving_attempts'], 0)
    eq(r['engineering_admitted'], False)


@test('decision guard never credits out-of-domain or unknown model predictions', kind='known_bad')
def t_domain():
    for domain in ('outside', 'unknown'):
        root, data, ref = fixture()
        inv = data['findings'][0]['investigation']
        inv['history'] = [observation(i, ref, ['select_B'], domain) for i in range(1, 4)]
        save(root, data)
        r = json.loads(must_fail(cli(root), 'invalid model credit', 'REASSESS').out)
        eq(r['investigations'][0]['credited_milestones'], [])
        eq(r['engineering_admitted'], False)


@test('decision-limiting uncertainty stops refinement without calling hardware defective', kind='known_bad')
def t_uncertainty():
    root, data, _ = fixture()
    data['findings'][0]['investigation']['next']['uncertainty'] = 'decision_limiting'
    save(root, data)
    r = json.loads(must_fail(cli(root), 'non-decisive experiment', 'REASSESS').out)
    eq(r['investigations'][0]['attempts'], 0)
    eq(data['findings'][0]['state'], 'open')


@test('decision guard rejects malformed, stale, missing and escaped evidence', kind='known_bad')
def t_bad_inputs():
    mutations = [
        lambda i: i.update(schema=True),
        lambda i: i.update(max_attempts=0),
        lambda i: i.update(max_nonimproving_attempts=True),
        lambda i: i.update(due_stage='new-invented-stage'),
        lambda i: i['requirement'].update(path='../outside'),
        lambda i: i['requirement'].update(path='/tmp/absolute'),
        lambda i: i['requirement'].update(sha256='f'*64),
        lambda i: i['requirement'].update(path='01_docs/missing.md'),
        lambda i: i['next'].update(on_reject=i['next']['on_support']),
        lambda i: i.update(undeclared_policy=True),
        lambda i: i.update(operating_states=[]),
    ]
    for mutate in mutations:
        root, data, _ = fixture(); mutate(data['findings'][0]['investigation']); save(root, data)
        eq(must_fail(cli(root, '--shadow'), 'invalid evidence even in shadow', 'INVALID').rc, 2)


@test('decision history rejects duplicate events and unplanned progress', kind='known_bad')
def t_bad_history():
    for duplicate in (True, False):
        root, data, ref = fixture()
        obs = observation(1, ref)
        data['findings'][0]['investigation']['history'] = [obs, copy.deepcopy(obs)] if duplicate else [
            {**obs, 'progress': ['invented-win']}]
        save(root, data)
        must_fail(cli(root), 'invalid history', 'INVALID')


@test('ordinary boards and deferred bench work retain their existing maturity')
def t_compatibility():
    root, data, _ = fixture()
    del data['findings'][0]['investigation']
    data['findings'][0]['blocks_at_or_above'] = 'FIRST_ARTICLE_TESTED'
    data['gates'][0].update(state='pass', evidence=['01_docs/result.md'])
    data['target'] = 'DESIGN_CLEAN'; save(root, data)
    before = project_state.derive(root, root / '01_docs/findings.yaml')
    eq(json.loads(must_pass(cli(root), 'no opted-in investigation').out)['decision'], 'NOT_APPLICABLE')
    eq(before, project_state.derive(root, root / '01_docs/findings.yaml'))
    eq(before['derived_maturity'], 'DESIGN_CLEAN')


@test('pcb flow handoff binds decision history and rejects a stale next action', kind='known_bad')
def t_handoff():
    root, data, ref = fixture()
    data['findings'][0]['investigation']['history'] = [observation(i, ref) for i in range(1, 4)]
    save(root, data)
    ctx = pcb_flow.resolve_context(root)
    pcb_flow.write_handoff(ctx, 'schematic', [])
    doc = yaml.safe_load(ctx.handoff.read_text())
    eq(doc['decision_progress']['decision'], 'REASSESS')
    eq(pcb_flow.validate_handoff(ctx), 0)
    data['findings'][0]['investigation']['next']['hypothesis'] = 'A different experiment'
    save(root, data)
    eq(pcb_flow.validate_handoff(ctx), pcb_flow.EXIT_STALE)


@test('pcb flow refuses a blocked named investigation before its child starts', kind='known_bad')
def t_launch():
    root, data, _ = fixture()
    data['findings'][0]['investigation']['next']['uncertainty'] = 'decision_limiting'
    save(root, data)
    r = run([KPY, SCRIPTS / 'pcb_flow.py', 'run', root, '--stage', 'schematic',
             '--investigation', 'startup', '--', KPY, '-c', 'print("CHILD_EXECUTED")'])
    must_fail(r, 'guarded child launch', 'REASSESS')
    assert 'CHILD_EXECUTED' not in r.out


@test('duplicate YAML cannot erase exhausted history', kind='known_bad')
def t_duplicate_yaml():
    root, data, ref = fixture()
    data['findings'][0]['investigation']['history'] = [observation(i, ref) for i in range(1, 4)]
    save(root, data)
    ledger = root / '01_docs/findings.yaml'
    # This duplicate previously replaced the real history with an empty list.
    raw = ledger.read_text().replace('    next:', '    history: []\n    next:')
    assert raw != ledger.read_text()
    ledger.write_text(raw)
    eq(must_fail(cli(root), 'duplicate history', 'duplicate YAML key').rc, 2)


@test('ordinary YAML merge defaults remain compatible while explicit duplicates fail', kind='known_bad')
def t_yaml_merge():
    root, _, _ = fixture()
    ledger = root / '01_docs/findings.yaml'
    raw = ('schema: 1\nfindings:\n  - &base\n    id: F\n    state: open\n'
           '    owner: electrical\n    closes_when: Reviewed\n'
           '    blocks_at_or_above: DESIGN_CLEAN\n  - <<: *base\n    id: G\n')
    ledger.write_text(raw)
    eq(json.loads(must_pass(cli(root), 'ordinary merge override').out)['decision'], 'NOT_APPLICABLE')
    eq(yaml.load(raw, Loader=guard.UniqueLoader), yaml.safe_load(raw))
    distinct = 'base: &b {x: 1}\nrow: {<<: *b, "<<": ordinary-data}\n'
    eq(yaml.load(distinct, Loader=guard.UniqueLoader), yaml.safe_load(distinct))
    # Explicit duplicates inside inherited defaults must still fail closed.
    ledger.write_text(raw.replace('    state: open', '    state: open\n    state: closed'))
    eq(must_fail(cli(root), 'duplicate in inherited mapping', 'duplicate YAML key').rc, 2)


@test('guarded dispatch reserves spend and prevents unreported repeat launches', kind='known_bad')
def t_reservation():
    root, data, ref = fixture(); save(root, data)
    args = [KPY, SCRIPTS / 'pcb_flow.py', 'run', root, '--stage', 'schematic',
            '--investigation', 'startup', '--', KPY, '-c', 'print("CHILD_EXECUTED")']
    first = must_pass(run(args), 'first guarded dispatch')
    assert 'CHILD_EXECUTED' in first.out
    pending = guard.evaluate(root)['investigations'][0]
    eq(pending['attempts'], 1)
    eq(len(pending['pending_launches']), 1)
    second = must_fail(run(args), 'unreported second dispatch', 'ASSESS_PENDING')
    assert 'CHILD_EXECUTED' not in second.out
    data = yaml.safe_load((root / '01_docs/findings.yaml').read_text())
    inv = data['findings'][0]['investigation']
    launch = inv['launches'][0]
    inv['history'].append({**observation(1, ref, ['eliminate_A']), **launch, 'origin': 'executed'})
    save(root, data)
    row = guard.evaluate(root)['investigations'][0]
    eq(row['attempts'], 1)  # assessment does not charge a second slot
    eq(row['pending_launches'], [])
    must_pass(run(args), 'next bounded experiment after assessment')
    eq(guard.evaluate(root)['investigations'][0]['attempts'], 2)


@test('issue accounting reuses guarded reservation without granting a second launch', kind='known_bad')
def t_accounted_reservation():
    root, data, ref = fixture(); save(root, data)
    ledger = root / '01_docs/issue_usage.jsonl'
    args = [KPY, SCRIPTS / 'pcb_flow.py', 'run', root, '--stage', 'schematic',
            '--investigation', 'startup', '--usage-ledger', ledger,
            '--', KPY, '-c', 'print("CHILD_EXECUTED")']
    must_pass(run(args), 'accounted guarded dispatch')
    data = yaml.safe_load((root / '01_docs/findings.yaml').read_text())
    reservation = data['findings'][0]['investigation']['launches'][0]['id']
    events = [json.loads(line) for line in ledger.read_text().splitlines()]
    eq(len(events), 2, 'one start and terminal')
    for event in events:
        eq(event['issue_id'], 'startup', 'existing finding identity')
        eq(event['attempt_id'], reservation, 'same budget reservation')
    must_fail(run(args), 'no automatic retry', 'ASSESS_PENDING')
    eq(len(ledger.read_text().splitlines()), 2, 'blocked retry emitted no new run')


def schema_fixture():
    """Exercise populated history/reservations, not only the empty-list case."""
    import schema_reader_audit as schema
    root, data, ref = fixture()
    inv = data['findings'][0]['investigation']
    obs = {**observation(1, ref, ['eliminate_A']), 'origin': 'executed'}
    inv['history'] = [obs]
    inv['launches'] = [{key: obs[key] for key in ('id', 'subject_sha256')}]
    save(root, data)
    rows = schema.load_declarations(ROOT)['01_docs/findings.yaml']
    return schema, root, data, rows


@test('populated decision ledger has complete executable shared-schema declarations')
def t_schema_coverage():
    schema, root, data, rows = schema_fixture()
    eq(guard.evaluate(root)['engineering_admitted'], False)
    counted, orphans, _ = schema.observe(
        '01_docs/findings.yaml', root/'01_docs/findings.yaml',
        schema.Trie.build(rows), '01_docs/findings.yaml')
    eq(orphans, [], 'every actual nested source field has a declared reader')
    declared = [row for row in rows if row.key.startswith('findings[].investigation')]
    assert declared and counted
    cache = schema.ReaderCache(ROOT)
    for row in declared:
        verdict, detail = schema.prove(row, cache)
        eq(verdict, 'PROVEN', f'{row.key}: {detail}')


@test('decision schema rejects an omitted evidence hash and an undeclared nested control', kind='known_bad')
def t_schema_nested_rejection():
    schema, root, data, rows = schema_fixture()
    evidence_key = 'findings[].investigation.history[].evidence[].sha256'
    truncated = [row for row in rows if row.key != evidence_key]
    assert len(truncated) == len(rows) - 1, 'real evidence hash declaration required'
    _, orphans, _ = schema.observe('01_docs/findings.yaml', root/'01_docs/findings.yaml',
                                  schema.Trie.build(truncated), '01_docs/findings.yaml')
    assert evidence_key in orphans, orphans
    data['findings'][0]['investigation']['next']['silent_bypass'] = True
    save(root, data)
    _, orphans, _ = schema.observe('01_docs/findings.yaml', root/'01_docs/findings.yaml',
                                  schema.Trie.build(rows), '01_docs/findings.yaml')
    assert 'findings[].investigation.next.silent_bypass' in orphans, orphans
    eq(must_fail(cli(root), 'undeclared nested control', 'INVALID').rc, 2)


@test('decision schema does not accept a combined prose reader as an executable name', kind='known_bad')
def t_schema_reader_identity():
    schema, _, _, rows = schema_fixture()
    row = copy.deepcopy(next(row for row in rows
                             if row.key == 'findings[].investigation.launches'))
    row.readers = ['decision_progress.py / pcb_flow.py']
    verdict, _ = schema.prove(row, schema.ReaderCache(ROOT))
    eq(verdict, 'UNPROVABLE')


if __name__ == '__main__':
    sys.exit(main())
