"""Offline user-directed recovery replay; actual Crow remains read-only."""
import json
import os
from pathlib import Path
import tempfile
import time
import unittest

import exploration as e
import progress
import test_parent_lifecycle as lifecycle


class ResumeChecks:
    state = lifecycle.LifecycleChecks.state
    event = lifecycle.LifecycleChecks.event
    reject = lifecycle.LifecycleChecks.reject

    def prepare(self):
        self.original = self.state()
        self.now = time.time()
        self.old = progress.status(self.original['events'], self.original['tasks'])
        self.assertLess(self.old['recovery_deadline'], self.now)
        (self.run/'test-user-authority.md').write_text(
            'SYNTHETIC offline user direction: resume one bounded experiment. Not live authority.\n')
        (self.run/'test-window-result.md').write_text('SYNTHETIC unchanged result; no engineering acceptance.\n')
        self.window = dict(op='resume', user_authorized=True, deadline=self.now+600,
                           reason='Synthetic new user direction only', path='test-user-authority.md')

    def reassess(self, deadline=None):
        return self.event(op='reassess', action='change', reason='Synthetic new method',
                          hypothesis='A different method may close the blocker',
                          check='Verify the unchanged deliverable contract',
                          deadline=self.window['deadline'] if deadline is None else deadline)

    def start(self):
        return self.event(op='start', id='new-window-parent', kind='recovery', actor='synthetic',
                          seconds=300, objective='Offline gate/tool/review lifecycle', writes=['test-output'])

    def test_new_window_parent_gate_tool_final_review_checkpoint_pause(self):
        resumed=self.event(**self.window)
        self.assertEqual(resumed['events'][:-1], self.original['events'])
        for key in self.original:
            if key not in ('events','paused'):self.assertEqual(resumed[key],self.original[key],key)
        status=progress.status(resumed['events'],resumed['tasks'])
        self.assertEqual(status['stalled'],self.old['stalled'])
        self.assertEqual(status['recovery_deadline'],self.window['deadline'])
        self.assertIsNone(status['decision'])
        with self.assertRaisesRegex(ValueError,'reassessment required'):self.start()
        self.reassess();self.start()
        self.event(op='bind',id='new-window-parent',handle='synthetic-parent-handle')
        for name in ('new-window-gate','new-window-final-review'):
            self.event(op='start',id=name,kind='assist',parent='new-window-parent',actor=name,seconds=10)
            self.event(op='bind',id=name,handle='synthetic-helper-handle')
            self.now+=1;self.event(op='finish',id=name,outcome='complete')
            if name.endswith('gate'):
                self.event(op='note',reason='SYNTHETIC simulated tool return; no CAD executed')
        self.event(op='finish',id='new-window-parent',outcome='partial')
        owed=['new-window-final-review','new-window-gate','new-window-parent']
        settled=self.event(op='milestone-checkpoint',milestone=self.old['milestone'],tasks=owed,
                           result='unchanged',reason='Offline unchanged deliverable',path='test-window-result.md')
        self.assertEqual(settled['events'][:len(self.original['events'])],self.original['events'])
        for name,task in self.original['tasks'].items():self.assertEqual(settled['tasks'][name],task)
        for key in ('budget_s','repairs','round','max_rounds','phase','selected','review'):
            self.assertEqual(settled[key],self.original[key],key)
        self.assertEqual(settled['charged_s'],self.original['charged_s']+320)
        status=progress.status(settled['events'],settled['tasks'])
        self.assertEqual(status['stalled'],self.old['stalled']+1)
        self.assertEqual(status['pending'],[])
        self.event(op='reassess',action='pause',reason='Offline simulation complete',
                   hypothesis='No real engineering executed',check='Actual source remains unchanged')
        self.assertTrue(self.state()['paused'])

    def test_plain_resume_and_reassessment_cannot_renew(self):
        self.event(op='resume',user_authorized=True)
        self.assertEqual(progress.status(self.state()['events'],self.state()['tasks'])['recovery_deadline'],
                         self.old['recovery_deadline'])
        with self.assertRaisesRegex(ValueError,'cannot be renewed'):self.reassess()
        with self.assertRaises(ValueError):self.start()

    def test_window_requires_paused_user_authorized_settled_assessed(self):
        for changes in ({'paused':False},{'live':True},{'pending':True}):
            with self.subTest(changes=changes):
                state=json.loads(json.dumps(self.original))
                if 'paused' in changes:state['paused']=False
                else:
                    state['tasks']['synthetic-unsettled']=dict(kind='recovery',
                        status='running' if 'live' in changes else 'finished')
                e.save(self.run,state)
                self.reject('explicit user resume|settle and assess',**self.window)
        e.save(self.run,self.original)
        for authority in (False,None,'true',1):
            self.reject('explicit user resume',**dict(self.window,user_authorized=authority))

    def test_window_requires_finite_future_deadline_reason_and_evidence(self):
        for deadline in (None,True,self.now,float('inf'),float('nan')):
            self.reject('finite future deadline',**dict(self.window,deadline=deadline))
        for reason in ('',None,'   '):
            self.reject('user-directed reason',**dict(self.window,reason=reason))
        for path in ('',None,'../outside'):
            self.reject('authority evidence|path must be local',**dict(self.window,path=path))

    def test_changed_authority_evidence_refuses_further_transitions(self):
        self.event(**self.window)
        (self.run/'test-user-authority.md').write_text('Changed authority.\n')
        self.reject('authority evidence changed',op='note',reason='Must fail closed')

    def test_authority_evidence_authorizes_only_one_window_even_when_renamed(self):
        self.event(**self.window)
        self.event(op='pause',reason='Synthetic window stopped')
        self.now=self.window['deadline']+1
        renewal=dict(self.window,deadline=self.now+600)
        self.reject('authority evidence already used',**renewal)
        (self.run/'test-copied-authority.md').write_bytes((self.run/self.window['path']).read_bytes())
        self.reject('authority evidence already used',**dict(renewal,path='test-copied-authority.md'))
        (self.run/'test-next-user-authority.md').write_text(
            'SYNTHETIC distinct subsequent user direction; not live authority.\n')
        before=self.state()
        resumed=self.event(**dict(renewal,path='test-next-user-authority.md'))
        self.assertEqual(resumed['events'][:-1],before['events'])
        for key in before:
            if key not in ('events','paused'):self.assertEqual(resumed[key],before[key],key)
        status=progress.status(resumed['events'],resumed['tasks'])
        self.assertEqual(status['recovery_deadline'],renewal['deadline'])
        self.assertEqual(status['stalled'],self.old['stalled'])
        self.assertIsNone(status['decision'])

    def test_new_window_still_caps_reassessment_and_dispatch(self):
        self.event(**self.window)
        with self.assertRaisesRegex(ValueError,'cannot be renewed'):
            self.reassess(self.window['deadline']+1)
        self.reassess()
        self.now=self.window['deadline']-299
        with self.assertRaisesRegex(ValueError,'deadline exhausted'):self.start()


class ResumeWindowTests(ResumeChecks, unittest.TestCase):
    # Reuse only fixture helpers; do not inherit its live-parent test methods.
    assessment = lifecycle.LifecycleChecks.assessment

    def setUp(self):
        lifecycle.ParentLifecycleTests.setUp(self)
        self.event(op='finish',id=self.parent,outcome='partial')
        self.event(**self.assessment([self.parent]))
        self.event(op='pause',reason='Synthetic user pause')
        self.prepare()


@unittest.skipUnless(os.environ.get('VNEXT_CROW_HISTORY'),'optional retained Crow journal')
class CrowResumeWindowTests(ResumeChecks, unittest.TestCase):
    def setUp(self):
        self.source=Path(os.environ['VNEXT_CROW_HISTORY'])/'project'
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.run=Path(temp.name);self.source_bytes={}
        self.addCleanup(self.assert_sources_unchanged)

        def copy(relative):
            src=e.inside(self.source,relative);raw=src.read_bytes();self.source_bytes[src]=raw
            dest=e.inside(self.run,relative);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)

        copy('run.json');copy('BRIEF.md')
        state=self.state()
        self.assertTrue(state['paused'])
        self.assertTrue(all(t['status']=='finished' for t in state['tasks'].values()))
        for event in state['events']:
            if event.get('op') in ('milestone-checkpoint','progress-migration') or (
                    event.get('op')=='resume' and 'deadline' in event):copy(event['path'])
        for redesign in state['redesigns']:copy(redesign['path'])
        self.prepare()

    def assert_sources_unchanged(self):
        for path,raw in self.source_bytes.items():self.assertEqual(path.read_bytes(),raw,str(path))


if __name__=='__main__':unittest.main(verbosity=2)
