"""Portable domain work after verified recovery advancement; no CAD or agents."""
import unittest

import exploration as e
import progress
import test_parent_lifecycle as lifecycle


class WorkLifecycleTests(lifecycle.LifecycleChecks, unittest.TestCase):
    def setUp(self):
        lifecycle.ParentLifecycleTests.setUp(self)
        recovered=self.parent
        self.event(op='finish',id=recovered,outcome='complete')
        before=self.state()
        self.event(**self.assessment([recovered],result='advanced',closed=['Synthetic verified condition'],
                                    verifier='synthetic domain verifier',regressions=False))
        status=progress.status(self.state()['events'],self.state()['tasks'])
        self.assertEqual(status['stalled'],0)
        self.assertIsNone(status['recovery_deadline'])
        self.reject('explicit plateau decision',op='start',id='not-recovery',kind='recovery',
                    actor='synthetic',seconds=10,objective='Normal next task',writes=['test-output'])
        self.parent='ordinary-work'
        started=self.event(op='start',id=self.parent,kind='work',actor='synthetic',seconds=3000,
                           objective='Next bounded domain task after advancement',writes=['test-output'])
        for key in ('phase','selected','review','repairs','round','budget_s'):
            self.assertEqual(started[key],before[key],key)
        self.assertEqual(started['charged_s'],before['charged_s']+3000)
        self.assertEqual(started['tasks'][recovered],before['tasks'][recovered])

    def test_helper_deadlines_and_budget_still_apply(self):
        self.finish_helper('test-gate')
        self.now=self.state()['tasks'][self.parent]['deadline']-5
        self.reject('parent deadline',**self.helper('test-over-parent'))
        self.now=self.state()['tasks'][self.parent]['started']+2
        state=self.state();state['budget_s']=state['charged_s']+5;e.save(self.run,state)
        self.reject('total run budget exhausted',**self.helper('test-over-budget'))

    def test_live_work_blocks_unrelated_dispatch_before_any_helper_returns(self):
        for kind in ('draft','work','recovery','review'):
            with self.subTest(kind=kind):
                self.reject('live work parent',op='start',id='unrelated',kind=kind,actor='synthetic',
                            seconds=10,objective='Unrelated',writes=['other-output'])
        self.reject('live work parent',op='start',id='wrong-helper',kind='assist',parent=self.old_parent,
                    actor='synthetic',seconds=10)

    def test_work_parent_cannot_finish_with_live_child_or_assess_early(self):
        self.event(**self.helper('test-live'))
        self.reject('finish child work',op='finish',id=self.parent,outcome='complete')
        self.reject('settle work',**self.assessment([self.parent]))

    def test_work_still_needs_reassessment_and_fits_active_recovery_window(self):
        self.event(op='finish',id=self.parent,outcome='partial')
        self.event(**self.assessment([self.parent]))
        attempt=dict(op='start',id='next-work',kind='work',actor='synthetic',seconds=30,
                     objective='Discriminating next attempt',writes=['test-output'])
        self.reject('reassessment required',**attempt)
        self.event(op='reassess',action='continue',reason='One further discriminating check',
                   hypothesis='Specific correction closes condition',check='Verify unchanged contract',
                   deadline=self.now+20)
        self.reject('recovery deadline exhausted',**attempt)
        self.event(**dict(attempt,seconds=10))
        self.reject('ordinary segment',op='start',id='long-worker',kind='assist',parent='next-work',
                    actor='synthetic',seconds=1201)

    def test_work_requires_bounded_objective_local_writes_and_available_budget(self):
        self.event(op='finish',id=self.parent,outcome='complete')
        self.event(**self.assessment([self.parent],result='advanced',closed=['Synthetic next condition'],
                                    verifier='synthetic domain verifier',regressions=False))
        attempt=dict(op='start',id='next-work',kind='work',actor='synthetic',seconds=10,
                     objective='Next bounded domain task',writes=['test-output'])
        for changes in ({'seconds':0},{'seconds':True},{'seconds':-1},{'objective':''},
                        {'writes':[]},{'writes':['../outside']}):
            with self.subTest(changes=changes):
                self.reject('ordinary segment|objective and bounded writes|path must be local',
                            **dict(attempt,**changes))
        state=self.state();state['budget_s']=state['charged_s']+5;e.save(self.run,state)
        self.reject('total run budget exhausted',**attempt)


if __name__=='__main__':unittest.main(verbosity=2)
