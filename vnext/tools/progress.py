"""Domain-neutral dispatch gate over the existing run journal, not a verifier.

The coordinator supplies domain-verified progress and an evidence reference.
This module enforces recording, plateau recovery and its fixed deadline; it
cannot judge engineering truth or whether a proposed strategy is genuinely new.
"""
import math


def require(value, message):
    if not value:
        raise ValueError(message)


def status(events, tasks):
    checkpoints = [(i, e) for i, e in enumerate(events) if e.get('op') in ('milestone-checkpoint', 'progress-migration')]
    require(checkpoints, 'milestone baseline required before dispatch')
    assessed, stalled, last_advance = set(), 0, checkpoints[0][0]
    for i, event in checkpoints:
        assessed.update(event['tasks'])
        if event['op'] == 'progress-migration':
            stalled = event['prior_stalled']
        elif event['result'] == 'advanced':
            stalled, last_advance = 0, i
        elif any(tasks[t]['kind'] not in ('review', 'assist') for t in event['tasks']):
            stalled += 1
    # Only a separately authorized, evidence-bound resume opens a new window.
    # Keep old deadlines and all milestone/attempt history in the journal.
    windows = [i for i, e in enumerate(events) if i > last_advance
               and e.get('op') == 'resume' and 'deadline' in e]
    window = windows[-1] if windows else last_advance
    recovery = [e['deadline'] for i, e in enumerate(events)
                if i >= window and e.get('op') in ('reassess', 'resume') and 'deadline' in e]
    last_index, last = checkpoints[-1]
    decisions = [e for i, e in enumerate(events)
                 if i > max(last_index, window) and e.get('op') == 'reassess']
    return dict(milestone=last['milestone'], stalled=stalled,
                pending=sorted(t for t, v in tasks.items()
                               if v['status'] == 'finished' and t not in assessed),
                decision=decisions[-1] if decisions else None,
                recovery_deadline=min(recovery) if recovery else None)


def checkpoint(events, tasks, event):
    """Validate one settled checkpoint; evidence bytes are bound by the adapter."""
    require(not any(t['status'] == 'running' for t in tasks.values()),
            'settle work before assessing milestone progress')
    require(event.get('milestone') and event.get('reason'), 'milestone and reason required')
    require(event.get('result') in ('baseline', 'advanced', 'prerequisite', 'unchanged'),
            'invalid progress result')
    if not any(e.get('op') in ('milestone-checkpoint', 'progress-migration') for e in events):
        require(not tasks and event['result'] == 'baseline' and event.get('tasks') == [],
                'existing history needs reviewed migration, not a fresh baseline')
        return
    current = status(events, tasks)
    require(event['milestone'] == current['milestone'], 'milestone cannot be renamed to reset history')
    require(event['result'] != 'baseline', 'baseline cannot reset history')
    require(current['pending'] and event.get('tasks') == current['pending'],
            'checkpoint must cover every newly finished task exactly once')
    if event['result'] == 'advanced':
        require(event.get('closed') and isinstance(event['closed'], list)
                and all(isinstance(c, str) and c.strip() for c in event['closed'])
                and event.get('verifier') and event.get('regressions') is False,
                'advance needs verified milestone conditions closed without regressions')
    else:
        require(not event.get('closed'), 'prerequisite/local success is not milestone advancement')


def migrate(events, tasks, event):
    """Adopt reviewed historical outcomes without clearing attempts or spend."""
    require(not any(e.get('op') in ('milestone-checkpoint', 'progress-migration') for e in events),
            'milestone history already adopted')
    require(not any(t['status'] == 'running' for t in tasks.values()), 'settle work before migration')
    require(event.get('tasks') == sorted(tasks), 'migration must cover every retained task')
    require(event.get('milestone') and event.get('reason') and event.get('reviewer'),
            'reviewed migration needs milestone, reason and reviewer')
    require(type(event.get('prior_stalled')) is int and event['prior_stalled'] >= 2,
            'stalled history migration must retain the plateau')


def reassess(events, tasks, event, now):
    current = status(events, tasks)
    require(not current['pending'] and not any(t['status'] == 'running' for t in tasks.values()),
            'assess all settled results before recovery')
    action = event.get('action')
    require(action in ('continue', 'change', 'backtrack', 'escalate', 'pause'), 'invalid recovery action')
    require(event.get('reason') and event.get('hypothesis') and event.get('check'),
            'reassessment needs reason, causal hypothesis and discriminating check')
    if 'deadline' in event:
        deadline = event.get('deadline')
        require(type(deadline) in (int, float) and math.isfinite(deadline) and deadline > now,
                'recovery needs a finite future deadline')
        prior = current['recovery_deadline']
        require(prior is None or deadline <= prior, 'recovery deadline cannot be renewed')
    if current['stalled'] >= 2 and action != 'pause':
        require(action != 'continue', 'plateau forbids routine continuation')
        require('deadline' in event, 'recovery needs a finite future deadline')


def resume_window(events, tasks, event, now):
    """Validate a new user-directed window; adapter checks pause and evidence."""
    current = status(events, tasks)
    require(not current['pending'] and not any(t['status'] == 'running' for t in tasks.values()),
            'settle and assess all results before a new recovery window')
    require(current['recovery_deadline'] is not None, 'no recovery window to replace')
    deadline = event['deadline']
    require(type(deadline) in (int, float) and math.isfinite(deadline) and deadline > now,
            'recovery needs a finite future deadline')
    require(isinstance(event.get('reason'), str) and event['reason'].strip(),
            'new recovery window needs user-directed reason')


def before_dispatch(events, tasks, now, seconds, *, kind=None, parent=None):
    current = status(events, tasks)
    pending = current['pending']
    owner = tasks.get(parent, {}) if kind == 'assist' else {}
    if owner.get('kind') in ('repair', 'recovery', 'work') and owner.get('status') == 'running':
        # Sibling helpers continue one live attempt. Keep their results pending
        # for its eventual checkpoint; do not assess or reset progress here.
        pending = [t for t in pending if tasks[t]['kind'] != 'assist'
                   or tasks[t].get('parent') != parent]
    require(not pending, 'milestone checkpoint required before dispatch')
    decision = current['decision']
    require(not current['stalled'] or decision, 'milestone reassessment required before dispatch')
    if decision:
        require(decision['action'] != 'pause', 'milestone paused')
        require(current['stalled'] < 2 or decision['action'] != 'continue',
                'plateau requires change, backtrack, escalation or pause')
    deadline = current['recovery_deadline']
    require(deadline is None or now + seconds <= deadline,
            'fixed milestone recovery deadline exhausted; pause and reconsider scope/authority')
    return current
