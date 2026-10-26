"""Offline parent/helper workflow replay; never dispatch workers or CAD.

VNEXT_CROW_HISTORY optionally supplies the retained work directory. Its journals
and bound evidence are copied to disposable runs; historical times are replayed
without changing events, budgets or deadlines in the source journal.
"""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

import exploration as e
import progress


class LifecycleChecks:
    def state(self):
        return json.loads((self.run/'run.json').read_text())

    def event(self, **event):
        return e.apply(self.run, event, now=self.now)

    def reject(self, message, **event):
        before=(self.run/'run.json').read_bytes()
        with self.assertRaisesRegex(ValueError, message):
            self.event(**event)
        self.assertEqual(before, (self.run/'run.json').read_bytes())

    def helper(self, name):
        return dict(op='start', id=name, kind='assist', parent=self.parent,
                    actor='synthetic-helper', seconds=10)

    def finish_helper(self, name, outcome='complete'):
        self.event(**self.helper(name))
        self.event(op='bind', id=name, handle='synthetic-offline-handle')
        self.now+=1
        self.event(op='finish', id=name, outcome=outcome)

    def assessment(self, tasks, **overrides):
        return dict(dict(op='milestone-checkpoint', milestone=self.milestone,
                         tasks=sorted(tasks), result='unchanged', path='test-assessment.md',
                         reason='Offline lifecycle simulation; no engineering result'), **overrides)

    def test_complete_parent_gate_tool_final_review_checkpoint_pause(self):
        before=self.state();start=progress.status(before['events'],before['tasks'])
        self.finish_helper('test-gate')
        current=self.state();status=progress.status(current['events'],current['tasks'])
        self.assertEqual(status['pending'], ['test-gate'])
        self.assertEqual(status['stalled'], start['stalled'])
        self.assertEqual(status['recovery_deadline'], start['recovery_deadline'])
        # Tool execution belongs to the parent. This note simulates its return;
        # no routing engine, native import, agent or engineering verdict runs.
        self.now+=5
        self.event(op='note', reason='SYNTHETIC tool return inside parent; no CAD executed')
        self.finish_helper('test-final-review')
        self.event(op='finish', id=self.parent, outcome='partial')
        self.reject('checkpoint required', **self.helper('test-too-early'))
        owed=sorted([self.parent,'test-gate','test-final-review'])
        self.reject('every newly finished task', **self.assessment([self.parent]))
        self.reject('every newly finished task', **self.assessment(owed+['test-gate']))
        self.event(**self.assessment(owed))
        settled=self.state();status=progress.status(settled['events'],settled['tasks'])
        self.assertEqual(status['pending'], [])
        self.assertEqual(status['stalled'], start['stalled']+1)
        self.assertEqual(settled['charged_s'], before['charged_s']+20)
        for key in ('budget_s','repairs','round','max_rounds','phase','selected','review'):
            self.assertEqual(settled[key], before[key], key)
        self.assertEqual(settled['events'][:len(before['events'])], before['events'])
        for key,value in before['tasks'].items():
            if key!=self.parent:self.assertEqual(settled['tasks'][key],value)
        self.reject('every newly finished task', **self.assessment(owed))
        self.reject('reassessment required', **self.helper('test-after-checkpoint'))
        self.event(op='reassess', action='pause', reason='Offline test complete',
                   hypothesis='Lifecycle evaluated', check='Keep actual board paused')
        self.assertTrue(self.state()['paused'])
        self.assertTrue(all(t['status']=='finished' for t in self.state()['tasks'].values()))

    def test_parent_waits_for_helpers_and_early_checkpoint_is_forbidden(self):
        self.event(**self.helper('test-live'))
        self.reject('finish child work', op='finish', id=self.parent, outcome='complete')
        self.now+=1;self.event(op='finish', id='test-live', outcome='complete')
        self.reject('settle work', **self.assessment(['test-live'], result='advanced',
                    closed=['helper passed'], verifier='synthetic', regressions=False))

    def test_pending_helper_only_allows_helpers_of_its_live_parent(self):
        self.finish_helper('test-gate')
        for kind,parent in [('draft',self.parent),('recovery',self.parent),
                            ('review',self.parent),('assist','missing-parent'),
                            ('assist',self.old_parent)]:
            with self.subTest(kind=kind,parent=parent):
                event=self.helper('test-wrong');event.update(kind=kind,parent=parent)
                self.reject('checkpoint required', **event)

    def test_helper_deadlines_and_budget_still_apply(self):
        self.finish_helper('test-gate')
        self.now=self.state()['tasks'][self.parent]['deadline']-5
        self.reject('parent deadline', **self.helper('test-over-parent'))
        self.now=progress.status(self.state()['events'],self.state()['tasks'])['recovery_deadline']-5
        self.reject('recovery deadline exhausted', **self.helper('test-over-recovery'))
        self.now=self.state()['tasks'][self.parent]['started']+2
        state=self.state();state['budget_s']=state['charged_s']+5;e.save(self.run,state)
        self.reject('total run budget exhausted', **self.helper('test-over-budget'))

    def test_pause_blocks_even_same_parent_helpers(self):
        self.finish_helper('test-gate')
        self.event(op='pause', reason='Synthetic user pause')
        self.reject('run paused', **self.helper('test-paused'))
        self.event(op='finish', id=self.parent, outcome='partial')
        self.assertTrue(self.state()['paused'])

    def test_failed_helper_is_retained_and_does_not_unlock_unrelated_work(self):
        self.finish_helper('test-failed', outcome='failed')
        self.finish_helper('test-diagnosis')
        self.assertEqual(self.state()['tasks']['test-failed']['outcome'], 'failed')
        event=self.helper('test-unrelated');event.update(kind='draft')
        self.reject('checkpoint required', **event)


class ParentLifecycleTests(LifecycleChecks, unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        base=Path(temp.name);brief=base/'brief.md';brief.write_text('Synthetic logger\n')
        self.run=base/'run';e.initialize(self.run,brief,budget=10000)
        (self.run/'test-assessment.md').write_text('Synthetic evidence; not acceptance.\n')
        self.now=100;self.milestone='Complete logger';self.parent='test-parent';self.old_parent='old-a'
        self.event(**self.assessment([],result='baseline'))
        for name in ('old-a','old-b'):
            self.event(op='start',id=name,kind='draft',actor=name,seconds=10)
            self.event(op='finish',id=name,outcome='partial')
            self.event(**self.assessment([name]))
            if name=='old-a':
                self.event(op='reassess',action='continue',reason='Synthetic second attempt',
                           hypothesis='One correction',check='Verify deliverable')
        self.event(op='reassess',action='change',reason='Synthetic changed method',
                   hypothesis='Different mechanism',check='Verify deliverable',deadline=2000)
        self.event(op='start',id=self.parent,kind='recovery',actor='synthetic-parent',seconds=1500,
                   objective='Gate, tool, review and settlement',writes=['test-output'])


@unittest.skipUnless(os.environ.get('VNEXT_CROW_HISTORY'), 'optional retained Crow journal')
class CrowParentLifecycleTests(LifecycleChecks, unittest.TestCase):
    def setUp(self):
        self.source=Path(os.environ['VNEXT_CROW_HISTORY'])/'project'
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.run=Path(temp.name)
        self.source_bytes={};self.addCleanup(self.assert_sources_unchanged)

        def copy(relative, destination=None):
            src=e.inside(self.source,relative);raw=src.read_bytes();self.source_bytes[src]=raw
            dest=e.inside(self.run,destination or relative);dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(raw)

        copy('run.json','test-live-journal.json')
        live=json.loads(self.source_bytes[self.source/'run.json'])
        self.assertTrue(live['paused'])
        self.assertTrue(all(t['status']=='finished' for t in live['tasks'].values()))
        copy('recovery-c62-trial/run.before.json','run.json');copy('BRIEF.md')
        initial=self.state()
        for event in live['events']:
            if event.get('op') in ('milestone-checkpoint','progress-migration'):copy(event['path'])
        for redesign in live['redesigns']:copy(redesign['path'])
        self.assertEqual(live['events'][:len(initial['events'])], initial['events'])
        self.parent='c62trial-recovery';self.old_parent='c62v2-recovery'
        # Replay the actual prelaunch transitions with their original timestamps.
        # Resume here applies ONLY to this disposable historical simulation.
        for event in live['events'][len(initial['events']):]:
            self.now=event['time'];self.event(**{k:v for k,v in event.items() if k!='time'})
            if event.get('op')=='bind' and event.get('id')==self.parent:break
        self.assertEqual(self.state()['tasks'][self.parent]['status'],'running')
        self.now+=1
        self.milestone=progress.status(self.state()['events'],self.state()['tasks'])['milestone']
        (self.run/'test-assessment.md').write_text('SYNTHETIC lifecycle result; no board work.\n')

    def assert_sources_unchanged(self):
        for path,raw in self.source_bytes.items():self.assertEqual(path.read_bytes(),raw,str(path))

    def test_current_journal_remains_paused_and_deadline_cannot_be_renewed(self):
        shutil.copyfile(self.run/'test-live-journal.json',self.run/'run.json')
        self.now=progress.status(self.state()['events'],self.state()['tasks'])['recovery_deadline']+1
        self.reject('run paused', **self.helper('test-no-resume'))
        self.event(op='resume',user_authorized=True,reason='SYNTHETIC negative test only')
        self.reject('cannot be renewed',op='reassess',action='change',reason='Synthetic attempt',
                    hypothesis='Must not renew historical deadline',check='Reject',deadline=self.now+100)


if __name__=='__main__':unittest.main(verbosity=2)
