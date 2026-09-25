#!/usr/bin/env python3
"""Read-only Crow graph audit; synthetic failure is confined to a temporary dir."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT/'projects/crow-usb-carrier-v1'
sys.path.insert(0, str(ROOT/'skills/pcb-design/scripts'))
import modular_design as graph  # noqa: E402
from pipeline_execution import TaskAttempt  # noqa: E402

PLAN = PROJECT/'03_src/modular_plan.json'
CIRCUIT = PROJECT/'03_tscircuit/build/circuit.json'
UNIFIED = PROJECT/'01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol/result.json'
ROUTE = PROJECT/'01_docs/research/2026-09-25-ti-adc8n-south-shift-route-sol/README.md'
ROOT_ID = 'p1_floorplan_569_after_native_evidence_abort'
ARCHIVED = (
    PROJECT/'01_docs/research/2026-09-24-p1-launch-abort-evidence/attempt.json',
    PROJECT/'01_docs/research/2026-09-24-p1-relative-path-failure-evidence/attempt.json',
    PROJECT/'01_docs/research/2026-09-24-p1-native-evidence-failure-evidence/attempt.json',
)
EXPECTED = {
    'plan': '75c3a517cea50dd6b5745fae96b051d334debd48aac143becaca3d5fe3fc35dc',
    'circuit': '580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d',
    'unified_result': 'e4915c32115f3cc500fc58ef0646be2c9f7c3f0a9b9dcb9944f314dcfe8c5332',
    'adc8n_route_note': 'a5cc0c860c5f1c7ba572fabc7cddb3cbeded176f877ab4e0524db39042447ffb',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    paths = {'plan':PLAN, 'circuit':CIRCUIT, 'unified_result':UNIFIED,
             'adc8n_route_note':ROUTE}
    for name, path in paths.items():
        if sha(path) != EXPECTED[name]:
            raise RuntimeError(f'{name}: exact research/graph input drift')
    plan, circuit = json.loads(PLAN.read_text()), json.loads(CIRCUIT.read_text())
    subject = graph.work_subject(plan, circuit).to_mapping()
    report = graph.evaluate(plan, circuit)
    root = report['work'][ROOT_ID]
    if (report['status'] != 'PASS' or report['coverage']['components_observed'] != 569 or
            report['coverage']['components_singly_owned'] != 569 or
            report['coverage']['crossing_nets_observed'] != 59 or
            report['coverage']['crossing_nets_exactly_declared'] != 59 or
            root['state'] != 'READY' or root['attempts'] != 0 or
            root['max_attempts'] != 1 or len(root['missing_evidence']) != 1 or
            (PROJECT/root['missing_evidence'][0]).exists()):
        raise RuntimeError('current graph/attempt state drift')
    research = json.loads(UNIFIED.read_text())
    if research['status'] != 'FAIL' or research['p1_accepted']:
        raise RuntimeError('TI research outcome drift')
    history = []
    for path in ARCHIVED:
        attempt = TaskAttempt.from_mapping(json.loads(path.read_text()))
        history.append({'path':path.relative_to(PROJECT).as_posix(),
                        'sha256':sha(path), 'task_id':attempt.task_id,
                        'status':attempt.status,
                        'subject_matches_current':attempt.subject.to_mapping() == subject,
                        'is_current_root':attempt.task_id == ROOT_ID})
    if any(row['is_current_root'] or row['subject_matches_current'] for row in history):
        raise RuntimeError('archived attempt unexpectedly belongs to current root/subject')
    # Model the budget with the real graph evaluator, without saving or
    # representing this edited historical receipt as an actual task run.
    hypothetical = json.loads(ARCHIVED[-1].read_text())
    hypothetical['task_id'] = ROOT_ID
    hypothetical['subject'] = subject
    with tempfile.TemporaryDirectory(prefix='crow-graph-audit-') as tmp:
        trial = Path(tmp)/'attempt.json'
        trial.write_text(json.dumps(hypothetical))
        simulated = graph.evaluate(plan, circuit, [{'attempt_path':'attempt.json'}],
                                   evidence_root=Path(tmp))
    simulated_root = simulated['work'][ROOT_ID]
    if (simulated_root['attempts'] != 1 or simulated_root['max_attempts'] != 1 or
            simulated_root['state'] != 'BACKTRACK_REQUIRED' or
            any(row['state'] == 'WORK_RECORDED' for row in simulated['work'].values())):
        raise RuntimeError('counterfactual P1 budget/backtrack state drift')
    return {'kind':'crow-ti-graph-attempt-audit', 'status':'RESEARCH_ONLY',
            'inputs':EXPECTED, 'current_subject':subject,
            'graph_status':report['status'], 'coverage':report['coverage'],
            'p1_root':root, 'historical_attempts':history,
            'ti_research_status':research['status'],
            'ti_research_p1_accepted':research['p1_accepted'],
            'counterfactual_only':{'one_failed_current_subject_attempt':simulated_root['state'],
                                   'attempts':simulated_root['attempts'],
                                   'max_attempts':simulated_root['max_attempts']},
            'recording_decision':'NO_TASK_ATTEMPT_WRITTEN_OR_OBSERVED'}


if __name__ == '__main__':
    receipt = audit()
    (HERE/'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
