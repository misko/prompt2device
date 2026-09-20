#!/usr/bin/env python3
"""Offline usage ingestion controls: attribution, dedupe, privacy and coverage."""
import copy
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import test, main, eq, check, tmpdir
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/pcb-design/scripts'
sys.path.insert(0, str(SCRIPTS))
from pipeline_usage_import import import_usage
from pipeline_issue_ledger import append_event, append_events, summarize, LedgerValidationError


def fixture():
    root = tmpdir('usage-import-')
    source = root / 'session.jsonl'
    rows = [
        {'type': 'session_meta', 'payload': {'id': 'parent'}},
        {'type': 'response_item', 'payload': {'content': 'PRIVATE_PROMPT_SENTINEL'}},
        {'type': 'turn_context', 'payload': {'turn_id': 'turn-1', 'model': 'test-model', 'effort': 'medium'}},
        {'type': 'event_msg', 'payload': {'type': 'token_count', 'total_token_usage': {'input_tokens': 900000}}},
        {'type': 'token_usage_record', 'timestamp': '2026-09-20T00:00:01Z',
         'payload': {'turn_id': 'turn-1', 'response_id': 'response-1',
                     'usage': {'input_tokens': 100, 'cached_input_tokens': 80,
                               'output_tokens': 10, 'reasoning_output_tokens': 4, 'total_tokens': 110}}},
    ]
    source.write_text(''.join(json.dumps(row)+'\n' for row in rows))
    manifest = {'schema': 1, 'provider_scope': 'test-account', 'expected_session_ids': ['parent'],
                'sources': [{'format': 'codex-rollout-v1', 'path': 'session.jsonl',
                             'assignments': {'turn-1': {'issue_id': 'ISSUE-1', 'attempt_id': 'attempt-1'}}}]}
    path = root / 'manifest.json'
    path.write_text(json.dumps(manifest))
    return root, path, root/'ledger.jsonl', manifest, rows


def reject(fn, contains):
    try:
        fn()
    except (ValueError, OSError) as exc:
        check(contains in str(exc), f'wrong refusal: {exc}')
    else:
        raise AssertionError('invalid import accepted')


@test('Codex imports only increments and preserves unknown timing and billing')
def t_codex():
    root, path, ledger, _, _ = fixture()
    report = import_usage(path, ledger, require_complete=True)
    eq(report['appended'], 1)
    eq(report['sources'][0]['ignored_cumulative_records'], 1)
    eq(report['all_descendants_verified'], False)
    stored = json.loads(ledger.read_text())
    eq(stored['schema'], 2)
    eq(stored['event_type'], 'USAGE')
    eq(stored['effort'], 'medium')
    eq(stored['elapsed_s'], None)
    summary = summarize(ledger)['issues']['ISSUE-1']
    eq(summary['usage_observation_count'], 1)
    eq(summary['completed_run_count'], 0)
    eq(summary['token_usage']['groups'][0]['totals']['total_tokens'], 110)
    eq(summary['timing_coverage']['unknown_duration_count'], 0)
    eq(summary['timing_coverage']['usage_unknown_duration_count'], 1)
    eq(summary['provider_cost_usd']['status'], 'UNKNOWN')
    check('PRIVATE_PROMPT_SENTINEL' not in ledger.read_text()+json.dumps(report), 'private content escaped')
    before = ledger.read_bytes()
    eq(import_usage(path, ledger)['already_recorded'], 1)
    eq(ledger.read_bytes(), before, 'idempotent import unchanged')


@test('parent and child repeated response is counted once with declared coverage')
def t_child_dedupe():
    root, path, ledger, manifest, rows = fixture()
    child = copy.deepcopy(rows)
    child[0]['payload']['id'] = 'child'
    child[-1]['timestamp'] = '2026-09-20T00:00:02Z'
    (root/'child.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in child))
    manifest['sources'].append({**manifest['sources'][0], 'path': 'child.jsonl'})
    manifest['expected_session_ids'].append('child')
    path.write_text(json.dumps(manifest))
    result = import_usage(path, ledger, require_complete=True)
    eq(result['unique_responses'], 1)
    eq(result['within_import_duplicates'], 1)
    eq(result['appended'], 1)
    # Reimport the second observer alone: timestamp drift cannot double bill.
    manifest['sources'] = manifest['sources'][1:]
    manifest['expected_session_ids'] = ['child']
    path.write_text(json.dumps(manifest))
    eq(import_usage(path, ledger)['already_recorded'], 1)


@test('missing child sessions and unassigned turns are explicit and can block import', kind='known_bad')
def t_partial_coverage():
    root, path, ledger, manifest, rows = fixture()
    manifest['expected_session_ids'].append('absent-child')
    unassigned = copy.deepcopy(rows[-1]); unassigned['payload']['turn_id'] = 'other-turn'
    unassigned['payload']['response_id'] = 'response-2'
    with (root/'session.jsonl').open('a') as stream:
        stream.write(json.dumps(unassigned)+'\n')
    path.write_text(json.dumps(manifest))
    result = import_usage(path, ledger, dry_run=True)
    eq(result['coverage'], 'PARTIAL')
    eq(result['missing_expected_sessions'], ['absent-child'])
    eq(result['unassigned_records'], 1)
    check(not ledger.exists(), 'dry-run wrote ledger')
    reject(lambda: import_usage(path, ledger, require_complete=True), 'coverage is partial')
    check(not ledger.exists(), 'refused import wrote ledger')


@test('unexpected session cannot satisfy complete declared coverage', kind='known_bad')
def t_unexpected_session():
    root, path, ledger, manifest, _ = fixture()
    manifest['expected_session_ids'] = []
    path.write_text(json.dumps(manifest))
    report = import_usage(path, ledger, dry_run=True)
    eq(report['unexpected_sessions'], ['parent'])
    eq(report['coverage'], 'PARTIAL')
    reject(lambda: import_usage(path, ledger, require_complete=True), 'coverage is partial')
    check(not ledger.exists(), 'unexpected session committed')


@test('conflicting attribution fails atomically instead of double counting', kind='known_bad')
def t_conflict():
    root, path, ledger, manifest, _ = fixture()
    import_usage(path, ledger)
    before = ledger.read_bytes()
    manifest['sources'][0]['assignments']['turn-1']['issue_id'] = 'OTHER-ISSUE'
    path.write_text(json.dumps(manifest))
    reject(lambda: import_usage(path, ledger), 'conflicting duplicate')
    eq(ledger.read_bytes(), before)


@test('malformed late source prevents earlier valid records from being appended', kind='known_bad')
def t_late_malformed():
    root, path, ledger, _, _ = fixture()
    with (root/'session.jsonl').open('a') as stream:
        stream.write('{"partial":')
    reject(lambda: import_usage(path, ledger), 'incomplete source JSONL')
    check(not ledger.exists(), 'partial import committed')


@test('context from another turn cannot misattribute the model')
def t_model_context():
    root, path, ledger, _, rows = fixture()
    rows[2]['payload']['turn_id'] = 'different-turn'
    (root/'session.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in rows))
    result = import_usage(path, ledger)
    eq(result['sources'][0]['missing_turn_context'], 1)
    eq(json.loads(ledger.read_text())['model'], None)


@test('USAGE records cannot fabricate execution timing', kind='known_bad')
def t_timing_boundary():
    root, path, ledger, _, _ = fixture()
    import_usage(path, ledger)
    row = json.loads(ledger.read_text())
    row['elapsed_s'] = 0
    reject(lambda: append_event(root/'bad-timing.jsonl', row), 'null execution timing')


@test('batch identity conflict cannot partially append', kind='known_bad')
def t_batch_transaction():
    root, path, ledger, _, _ = fixture()
    import_usage(path, ledger)
    original = json.loads(ledger.read_text())
    before = ledger.read_bytes()
    addition = {**original, 'event_id': 'new-event', 'run_id': 'new-run', 'response_id': 'new-response'}
    conflict = {**original, 'issue_id': 'changed-issue'}
    reject(lambda: append_events(ledger, [addition, conflict]), 'conflicting duplicate')
    eq(ledger.read_bytes(), before)


@test('OpenRouter receipts import reported cost and truncation without API calls')
def t_openrouter():
    root, path, ledger, manifest, _ = fixture()
    receipt = {'id': 'or-1', 'model': 'test-model', 'created': 1789862400,
               'choices': [{'finish_reason': 'length', 'message': {'content': 'PRIVATE_REPLY_SENTINEL'}}],
               'usage': {'prompt_tokens': 100, 'completion_tokens': 10, 'total_tokens': 110,
                         'cost': 0.125}}
    (root/'response.json').write_text(json.dumps(receipt))
    manifest['expected_session_ids'] = []
    manifest['sources'] = [{'format': 'openrouter-response-v1', 'path': 'response.json',
                            'issue_id': 'review', 'attempt_id': 'review-1'}]
    path.write_text(json.dumps(manifest))
    import_usage(path, ledger, require_complete=True)
    stored = json.loads(ledger.read_text())
    eq(stored['provider_cost_usd'], 0.125)
    eq(stored['status'], 'INCOMPLETE')
    eq(stored['elapsed_s'], None)
    check('PRIVATE_REPLY_SENTINEL' not in ledger.read_text(), 'response content escaped')


@test('CLI rejects bad input with a nonzero exit and no ledger', kind='known_bad')
def t_cli():
    root, path, ledger, manifest, _ = fixture()
    result = subprocess.run([sys.executable, str(SCRIPTS/'pipeline_usage_import.py'),
                             '--manifest', str(path), '--ledger', str(ledger), '--dry-run'],
                            capture_output=True, text=True)
    eq(result.returncode, 0, result.stderr)
    eq(json.loads(result.stdout)['dry_run'], True)
    manifest['sources'][0]['format'] = 'future-unknown-format'
    path.write_text(json.dumps(manifest))
    result = subprocess.run([sys.executable, str(SCRIPTS/'pipeline_usage_import.py'),
                             '--manifest', str(path), '--ledger', str(ledger)], capture_output=True, text=True)
    eq(result.returncode, 2)
    check(not ledger.exists(), 'CLI rejection wrote ledger')


if __name__ == '__main__':
    raise SystemExit(main())
