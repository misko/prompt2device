#!/usr/bin/env python3
"""Bound engineering investigations; never grade or promote a PCB.

Reads optional findings[].investigation in the existing findings ledger.
History is durable authored assessment, not fabricated TaskAttempt telemetry.
The CLI is read-only: default enforcement exits 1 on reassessment, 2 on invalid
evidence; --shadow observes the same decision without enforcing reassessment.

Evidence hashes establish identity, not the truth of a coordinator's assessment.
Milestones are finite, credited once, and never override the total-attempt cap.
No result from this tool supplies engineering, maturity, or release admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid

import yaml

CATALOG = Path(__file__).resolve().parents[1] / 'references/skill-authority-map.json'


class UniqueLoader(yaml.SafeLoader):
    """Duplicate keys must not silently erase cumulative history."""

    _merge_key = object()  # a merge directive is not the literal string "<<"

    def flatten_mapping(self, node):
        # Check authored keys before merging: an explicit override of an
        # inherited default is valid YAML, not an erased duplicate history.
        # A merge source may be flattened again when its anchor is constructed.
        if not getattr(node, '_explicit_keys_checked', False):
            node._explicit_keys_checked = True
            seen = set()
            for key_node, _ in node.value:
                key = (self._merge_key if key_node.tag == 'tag:yaml.org,2002:merge'
                       else key_node.value if key_node.tag == 'tag:yaml.org,2002:value'
                       else self.construct_object(key_node, deep=False))
                if key in seen:
                    raise ValueError(f'duplicate YAML key: {key_node.value}')
                seen.add(key)
        super().flatten_mapping(node)


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label}: nonempty string required')
    return value


def _fields(value, fields, label):
    if not isinstance(value, dict) or set(value) != set(fields.split()):
        raise ValueError(f'{label}: expected exactly {fields}')


def _strings(value, label, *, empty=False):
    if not isinstance(value, list) or (not value and not empty):
        raise ValueError(f'{label}: nonempty list required')
    for item in value:
        _text(item, label)
    if len(set(value)) != len(value):
        raise ValueError(f'{label}: duplicates')
    return value


def _positive(value, label):
    if type(value) is not int or value < 1:
        raise ValueError(f'{label}: positive integer required')
    return value


def _digest(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ValueError(f'{label}: SHA256 required')
    return value


def _evidence(project, ref, *, requirement=False):
    fields = 'path sha256 locator' if requirement else 'path sha256'
    _fields(ref, fields, 'evidence')
    name = _text(ref['path'], 'evidence.path')
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('evidence path must be project-relative without traversal')
    path = (project / relative).resolve()
    if not path.is_relative_to(project) or not path.is_file():
        raise ValueError(f'evidence missing or outside project: {name}')
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != _digest(ref['sha256'], 'evidence.sha256'):
        raise ValueError(f'stale evidence: {name}')
    if requirement:
        _text(ref['locator'], 'requirement.locator')


def assess(project: Path, finding: dict) -> dict:
    """Recompute cumulative progress from the whole history, never a cache."""
    project = project.resolve()
    ident = _text(finding.get('id'), 'finding.id')
    for name in ('owner', 'closes_when', 'blocks_at_or_above'):
        _text(finding.get(name), f'{ident}.{name}')
    if finding.get('state') not in ('open', 'closed', 'waived'):
        raise ValueError(f'{ident}: invalid finding state')
    inv = finding['investigation']
    _fields(inv, 'schema requirement due_stage operating_states question milestones '
            'max_nonimproving_attempts max_attempts launches history next', ident)
    if type(inv['schema']) is not int or inv['schema'] != 1:
        raise ValueError(f'{ident}: investigation schema must be 1')
    _evidence(project, inv['requirement'], requirement=True)
    stage_ids = {row['spec']['id'] for row in json.loads(CATALOG.read_bytes())['stages']}
    if inv['due_stage'] not in stage_ids:
        raise ValueError(f'{ident}: unknown due_stage')
    _strings(inv['operating_states'], 'operating_states')
    _text(inv['question'], 'question')
    milestones = inv['milestones']
    if not isinstance(milestones, dict) or not milestones:
        raise ValueError('milestones: nonempty id-to-closure-condition mapping required')
    for key, value in milestones.items():
        _text(key, 'milestone.id')
        _text(value, 'milestone.closure')
    plateau = _positive(inv['max_nonimproving_attempts'], 'max_nonimproving_attempts')
    cap = _positive(inv['max_attempts'], 'max_attempts')
    if cap < plateau:
        raise ValueError('max_attempts must cover max_nonimproving_attempts')
    history = inv['history']
    if not isinstance(history, list):
        raise ValueError('history: list required')
    launches = inv['launches']
    if not isinstance(launches, list):
        raise ValueError('launches: list required')
    reserved = {}
    for launch in launches:
        _fields(launch, 'id subject_sha256', 'launch')
        lid = _text(launch['id'], 'launch.id')
        if lid in reserved:
            raise ValueError('duplicate launch reservation')
        reserved[lid] = _digest(launch['subject_sha256'], 'launch.subject_sha256')
    seen, credited = set(), set()
    nonimproving = 0
    observations = []
    for obs in history:
        _fields(obs, 'id subject_sha256 origin hypothesis result model_domain progress evidence',
                'observation')
        oid = _text(obs['id'], 'observation.id')
        if oid in seen:
            raise ValueError(f'duplicate observation: {oid}')
        seen.add(oid)
        _digest(obs['subject_sha256'], 'subject_sha256')
        if oid in reserved and (reserved[oid] != obs['subject_sha256'] or obs['origin'] != 'executed'):
            raise ValueError('assessment does not bind its reserved launch subject/origin')
        if obs['origin'] not in ('executed', 'historical_assessment'):
            raise ValueError('origin must distinguish execution from historical assessment')
        for key in ('hypothesis', 'result'):
            _text(obs[key], key)
        if obs['model_domain'] not in ('within', 'outside', 'unknown', 'not_applicable'):
            raise ValueError('invalid model_domain')
        progress = set(_strings(obs['progress'], 'progress', empty=True))
        if not progress <= milestones.keys():
            raise ValueError('progress names undeclared milestones')
        if not isinstance(obs['evidence'], list) or not obs['evidence']:
            raise ValueError('observation requires evidence')
        for ref in obs['evidence']:
            _evidence(project, ref)
        new = progress - credited if obs['model_domain'] in ('within', 'not_applicable') else set()
        nonimproving = 0 if new else nonimproving + 1
        credited.update(new)
        observations.append({'id': oid, 'credited': sorted(new),
                             'learning_only': not bool(new),
                             'model_domain': obs['model_domain']})
    plan = inv['next']
    _fields(plan, 'action hypothesis on_support on_reject uncertainty', 'next')
    if plan['action'] not in ('investigate', 'reassess'):
        raise ValueError('next.action must be investigate or reassess')
    for key in ('hypothesis', 'on_support', 'on_reject'):
        _text(plan[key], 'next.' + key)
    if plan['on_support'].strip() == plan['on_reject'].strip():
        raise ValueError('investigation must distinguish two decision outcomes')
    if plan['uncertainty'] not in ('bounded', 'decision_limiting'):
        raise ValueError('next.uncertainty must be bounded or decision_limiting')

    reasons = []
    attempts = len(seen | reserved.keys())
    pending = sorted(reserved.keys() - seen)
    if attempts >= cap:
        reasons.append('total investigation budget exhausted')
    if nonimproving >= plateau:
        reasons.append('consecutive attempts without new decision-relevant milestone')
    if plan['uncertainty'] == 'decision_limiting':
        reasons.append('uncertainty prevents the proposed experiment deciding the choice')
    if plan['action'] == 'reassess':
        reasons.append('coordinator requests architecture/model reassessment')
    active = finding['state'] == 'open'
    decision = ('REASSESS' if reasons else 'ASSESS_PENDING' if pending else
                'CONTINUE_BOUNDED') if active else 'INACTIVE'
    if pending:
        reasons.append('reserved launch needs an evidence-bound coordinator assessment')
    return {
        'finding_id': ident, 'decision': decision, 'stop_local_refinement': active and bool(reasons),
        'owner': finding['owner'], 'due_stage': inv['due_stage'],
        'blocks_at_or_above': finding['blocks_at_or_above'],
        'question': inv['question'], 'closes_when': finding['closes_when'],
        'attempts': attempts, 'max_attempts': cap, 'pending_launches': pending,
        'nonimproving_attempts': nonimproving, 'max_nonimproving_attempts': plateau,
        'credited_milestones': sorted(credited), 'observations': observations,
        'reasons': reasons, 'next': plan, 'engineering_admitted': False,
    }


def evaluate(project: Path, finding_id: str | None = None) -> dict:
    project = project.resolve()
    ledger = project / '01_docs/findings.yaml'
    if not ledger.exists():
        if finding_id:
            raise ValueError('requested investigation has no findings ledger')
        return {'schema': 1, 'decision': 'NOT_APPLICABLE', 'investigations': [],
                'engineering_admitted': False, 'ledger_sha256': None}
    raw = ledger.read_bytes()
    data = yaml.load(raw, Loader=UniqueLoader)
    if not isinstance(data, dict) or type(data.get('schema')) is not int or data['schema'] != 1:
        raise ValueError('findings ledger schema must be 1')
    findings = data.get('findings', [])
    if not isinstance(findings, list):
        raise ValueError('findings must be a list')
    ids = [_text(f.get('id'), 'finding.id') for f in findings if isinstance(f, dict)]
    if len(ids) != len(findings) or len(ids) != len(set(ids)):
        raise ValueError('malformed or duplicate findings')
    selected = [f for f in findings if 'investigation' in f and
                (finding_id is None or f['id'] == finding_id)]
    if finding_id and not selected:
        raise ValueError(f'unknown investigation: {finding_id}')
    rows = [assess(project, f) for f in selected]
    reassess = any(r['decision'] == 'REASSESS' for r in rows)
    pending = any(r['decision'] == 'ASSESS_PENDING' for r in rows)
    return {'schema': 1, 'decision': 'REASSESS' if reassess else 'ASSESS_PENDING' if pending else
            ('CONTINUE_BOUNDED' if any(r['decision'] != 'INACTIVE' for r in rows)
             else 'NOT_APPLICABLE'),
            'ledger_sha256': hashlib.sha256(raw).hexdigest(),
            'catalog_sha256': hashlib.sha256(CATALOG.read_bytes()).hexdigest(),
            'investigations': rows, 'engineering_admitted': False}


def reserve_launch(project: Path, finding_id: str, subject_sha256: str) -> str:
    """Reserve before dispatch, even if dispatch fails. No completed-run claim.

    This explicit mutating seam is used only by pcb_flow's named investigation
    launch. It uses a nonblocking Linux advisory lock plus a byte-change check;
    ordinary arbitrary writers are still governed by the one-writer rule.
    """
    import fcntl
    project = project.resolve()
    _digest(subject_sha256, 'launch.subject_sha256')
    lock_dir = project / '06_build/tmp'
    lock_dir.mkdir(parents=True, exist_ok=True)
    with (lock_dir / 'decision_progress.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = evaluate(project, finding_id)
        if result['decision'] != 'CONTINUE_BOUNDED':
            raise ValueError(f"{result['decision']}: assess or reassess before another launch")
        ledger = project / '01_docs/findings.yaml'
        original = ledger.read_bytes()
        if hashlib.sha256(original).hexdigest() != result['ledger_sha256']:
            raise ValueError('ledger changed before launch reservation')
        data = yaml.load(original, Loader=UniqueLoader)
        finding = next(f for f in data['findings'] if f['id'] == finding_id)
        ident = 'launch-' + uuid.uuid4().hex
        finding['investigation']['launches'].append(
            {'id': ident, 'subject_sha256': subject_sha256})
        # The reservation counts immediately. The later human assessment uses
        # this same ID and source hash; union accounting cannot double count it.
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                    prefix='.decision-', suffix='.tmp', dir=ledger.parent,
                    delete=False) as stream:
                temporary = Path(stream.name)
                yaml.safe_dump(data, stream, sort_keys=False)
                stream.flush()
                os.fsync(stream.fileno())
            if ledger.read_bytes() != original:
                raise ValueError('concurrent ledger change; launch reservation refused')
            os.replace(temporary, ledger)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        return ident


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('project', type=Path)
    parser.add_argument('--finding')
    parser.add_argument('--shadow', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = evaluate(args.project, args.finding)
        result['mode'] = 'shadow' if args.shadow else 'enforce'
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1 if result['decision'] in ('REASSESS', 'ASSESS_PENDING') and not args.shadow else 0
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(json.dumps({'decision': 'INVALID', 'error': str(exc),
                          'engineering_admitted': False}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
