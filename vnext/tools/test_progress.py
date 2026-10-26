"""Offline dispatch regressions; no CAD, agents, network or live run writes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import exploration as e
import progress


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.events=[]
        self.tasks={}
        self.now=100
        self.record(result='baseline',tasks=[])

    def record(self, result='unchanged', tasks=None, **extra):
        event=dict(op='milestone-checkpoint',milestone='verified deliverable',result=result,
                   tasks=tasks if tasks is not None else progress.status(self.events,self.tasks)['pending'],
                   reason='Domain assessment of exact evidence',**extra)
        progress.checkpoint(self.events,self.tasks,event)
        self.events.append(event)

    def finish(self, name, result='unchanged', kind='repair', **extra):
        self.tasks[name]=dict(kind=kind,status='finished',actor=name)
        self.record(result,**extra)

    def reassess(self, action='change', **extra):
        event=dict(op='reassess',action=action,reason='Evidence refutes current approach',
                   hypothesis='Different authoring strategy removes the observed obstacle',
                   check='Verify one complete function without regression',**extra)
        progress.reassess(self.events,self.tasks,event,self.now)
        self.events.append(event)

    def dispatch(self):
        return progress.before_dispatch(self.events,self.tasks,self.now,10)

    def test_initial_dispatch_and_first_nonprogress_reassessment(self):
        self.dispatch();self.finish('a')
        with self.assertRaisesRegex(ValueError,'reassessment required'):self.dispatch()
        self.reassess('continue');self.dispatch()

    def test_two_successful_prerequisites_still_close_routine_dispatch(self):
        self.finish('new_worker','prerequisite');self.reassess('continue')
        self.finish('renamed_tool_task','prerequisite')
        with self.assertRaisesRegex(ValueError,'reassessment required'):self.dispatch()
        with self.assertRaisesRegex(ValueError,'routine continuation'):self.reassess('continue')
        self.assertEqual(progress.status(self.events,self.tasks)['stalled'],2)

    def test_renamed_milestone_duplicate_or_omitted_tasks_cannot_reset(self):
        self.finish('a')
        for change in ({'milestone':'renamed'}, {'tasks':[]}, {'result':'baseline'}):
            event=dict(self.events[-1],**change)
            with self.assertRaises(ValueError):progress.checkpoint(self.events,self.tasks,event)
        self.tasks['b']=dict(kind='repair',status='finished')
        event=dict(self.events[-1],tasks=['b','invented'])
        with self.assertRaises(ValueError):progress.checkpoint(self.events,self.tasks,event)

    def test_pending_results_block_dispatch_even_after_prior_reassessment(self):
        self.finish('a');self.reassess('continue')
        self.tasks['b']=dict(kind='diagnose',status='finished')
        with self.assertRaisesRegex(ValueError,'checkpoint required'):self.dispatch()

    def test_live_parent_does_not_hide_other_pending_results(self):
        self.tasks['parent']=dict(kind='recovery',status='running')
        self.tasks['other']=dict(kind='recovery',status='running')
        self.tasks['own-helper']=dict(kind='assist',status='finished',parent='parent')
        for kind,parent in [('assist','other'),('diagnose','parent'),('review','parent')]:
            with self.subTest(kind=kind,parent=parent):
                self.tasks['unrelated']=dict(kind=kind,status='finished',parent=parent)
                with self.assertRaisesRegex(ValueError,'checkpoint required'):
                    progress.before_dispatch(self.events,self.tasks,100,10,kind='assist',parent='parent')

    def test_review_and_assist_do_not_double_count_author_attempt(self):
        self.finish('author');self.reassess('continue')
        self.finish('independent_review',kind='review')
        self.finish('helper',kind='assist')
        self.assertEqual(progress.status(self.events,self.tasks)['stalled'],1)
        with self.assertRaisesRegex(ValueError,'reassessment required'):self.dispatch()

    def test_progress_requires_closed_conditions_verifier_and_no_regression(self):
        self.tasks['a']=dict(kind='repair',status='finished')
        for extra in ({}, {'closed':['fewer opens'],'verifier':'review','regressions':True},
                      {'closed':[],'verifier':'review','regressions':False}):
            with self.assertRaises(ValueError):self.record('advanced',**extra)
        self.record('advanced',closed=['complete function verified'],verifier='domain review',regressions=False)
        self.assertEqual(self.dispatch()['stalled'],0)

    def test_fixed_recovery_deadline_cannot_be_renewed_or_ignored(self):
        self.finish('a');self.finish('b')
        self.reassess(deadline=150);self.dispatch()
        self.finish('bounded_diagnosis','prerequisite',kind='diagnose')
        with self.assertRaisesRegex(ValueError,'cannot be renewed'):self.reassess(deadline=200)
        self.reassess(deadline=150)
        self.now=141
        with self.assertRaisesRegex(ValueError,'deadline exhausted'):self.dispatch()

    def test_recovery_requires_finite_future_deadline(self):
        self.finish('a');self.finish('b')
        for deadline in (None,True,99,float('inf'),float('nan')):
            with self.assertRaises(ValueError):self.reassess(deadline=deadline)

    def test_reviewed_advancement_resets_plateau_not_task_history(self):
        self.finish('a');self.finish('b');self.reassess(deadline=150)
        self.finish('verified_review','advanced',kind='review',closed=['required interface closed'],
                    verifier='independent domain verifier',regressions=False)
        self.now=200
        self.assertEqual(self.dispatch()['stalled'],0)
        self.assertEqual(len(self.tasks),3)

    def test_pause_is_not_a_recovery_permission(self):
        self.finish('a');self.finish('b');self.reassess('pause')
        with self.assertRaisesRegex(ValueError,'paused'):self.dispatch()

    def test_crow_history_blocks_before_c51_without_explicit_recovery(self):
        fixture=json.loads((Path(__file__).parent/'test-fixtures/crow-progress.json').read_text())
        first,second=fixture['checkpoints'][:2]
        self.finish(first['id'],first['result']);self.reassess('continue')
        self.finish(second['id'],second['result'])
        with self.assertRaisesRegex(ValueError,'reassessment required'):self.dispatch()
        # These are retrospective observations, not a claim that C51 never ran.
        self.assertEqual(fixture['checkpoints'][2]['id'],'C51')
        for row in fixture['checkpoints'][2:]:
            self.finish(row['id'],row['result'])
        self.assertEqual(progress.status(self.events,self.tasks)['stalled'],13)

    def test_crow_reassessment_notes_cannot_renew_recovery_indefinitely(self):
        fixture=json.loads((Path(__file__).parent/'test-fixtures/crow-progress.json').read_text())
        for row in fixture['checkpoints'][:2]:self.finish(row['id'],row['result'])
        # A changed whole-board strategy may legitimately be authorized. The
        # illustrative deadline is test policy, NOT a historical Crow allowance.
        self.reassess(deadline=150)
        self.finish('C51',fixture['checkpoints'][2]['result'])
        with self.assertRaisesRegex(ValueError,'cannot be renewed'):self.reassess(deadline=250)
        self.now=151
        with self.assertRaises(ValueError):self.reassess(deadline=150)

    @unittest.skipUnless(os.environ.get('VNEXT_CROW_HISTORY'), 'retained history is optional; fixture replay is portable')
    def test_crow_fixture_binds_original_immutable_handoffs(self):
        fixture=json.loads((Path(__file__).parent/'test-fixtures/crow-progress.json').read_text())
        root=Path(os.environ['VNEXT_CROW_HISTORY'])
        for row in fixture['checkpoints']:
            source=root/fixture['source_path_pattern'].format(number=int(row['id'][1:]))
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),row['source_sha256'],row['id'])

    @unittest.skipUnless(os.environ.get('VNEXT_CROW_HISTORY'), 'retained journal is optional; portable fixtures cover the same interface')
    def test_actual_retained_journal_migration_is_read_only_and_preserves_plateau(self):
        source=Path(os.environ['VNEXT_CROW_HISTORY'])/'project/recovery-c62/run.before-c62.json'
        raw=source.read_bytes();state=json.loads(raw)
        event=dict(op='progress-migration',milestone='retained routing deliverable',tasks=sorted(state['tasks']),
                   prior_stalled=13,reason='Historical review',reviewer='test only',path='not-written.json')
        progress.migrate(state['events'],state['tasks'],event)
        result=progress.status([*state['events'],event],state['tasks'])
        self.assertEqual(result['stalled'],13);self.assertEqual(result['pending'],[])
        with self.assertRaisesRegex(ValueError,'reassessment required'):
            progress.before_dispatch([*state['events'],event],state['tasks'],100,10)
        self.assertEqual(raw,source.read_bytes())


class RunnerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);brief=self.base/'brief.md';brief.write_text('A temperature logger.\n')
        self.run=self.base/'run';e.initialize(self.run,brief,budget=3000,width=3)
        self.now=100
        (self.run/'evidence.md').write_text('Synthetic domain assessment; not engineering acceptance.\n')

    def event(self, **event):
        return e.apply(self.run,event,now=self.now)

    def baseline(self, milestone='complete logger design'):
        self.event(op='milestone-checkpoint',milestone=milestone,tasks=[],result='baseline',
                   reason='Verified starting point',path='evidence.md')

    def start(self, name):
        return self.event(op='start',id=name,kind='draft',actor=name,seconds=10)

    def checkpoint(self, name):
        self.event(op='finish',id=name,outcome='complete')
        return self.event(op='milestone-checkpoint',milestone='complete logger design',tasks=[name],
                          result='prerequisite',reason='Local tests pass; deliverable unchanged',path='evidence.md')

    def test_actual_runner_refuses_dispatch_without_assessment(self):
        before=(self.run/'run.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'baseline required'):self.start('a')
        self.assertEqual(before,(self.run/'run.json').read_bytes())
        self.baseline();self.start('a');self.checkpoint('a')
        with self.assertRaisesRegex(ValueError,'reassessment required'):self.start('b')
        self.event(op='reassess',action='continue',reason='One discriminating test remains',
                   hypothesis='The test identifies the interface error',check='Verify that interface')
        self.start('b');self.checkpoint('b')
        self.event(op='note',reason='New model, new prerequisite, bigger budget, another worker')
        before=(self.run/'run.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'reassessment required'):self.start('c')
        self.assertEqual(before,(self.run/'run.json').read_bytes())
        self.event(op='reassess',action='change',reason='Two tests did not close the interface',
                   hypothesis='Replace the interface strategy',check='Verify end-to-end behavior',deadline=150)
        self.now=141
        with self.assertRaisesRegex(ValueError,'deadline exhausted'):self.start('c')

    def test_evidence_tampering_is_not_a_progress_reset(self):
        self.baseline();(self.run/'evidence.md').write_text('Different assessment')
        with self.assertRaisesRegex(ValueError,'evidence changed'):self.start('a')

    def test_legacy_tasks_cannot_be_reinitialized_to_hide_history(self):
        s=json.loads((self.run/'run.json').read_text())
        s['tasks']['legacy']=dict(kind='repair',status='finished');e.save(self.run,s)
        with self.assertRaisesRegex(ValueError,'reviewed migration'):self.baseline()

    def test_user_pause_survives_recovery_resume_and_gate(self):
        self.baseline();self.event(op='pause',reason='User requested a timeout')
        with self.assertRaisesRegex(ValueError,'paused'):self.start('a')
        with self.assertRaisesRegex(ValueError,'paused'):
            self.event(op='reassess',action='change',reason='Not authority to resume')
        self.assertTrue(json.loads((self.run/'run.json').read_text())['paused'])

    def test_reviewed_migration_preserves_old_state_and_gates_recovery(self):
        state=json.loads((self.run/'run.json').read_text())
        state['tasks']['old']=dict(kind='repair',status='finished')
        state['charged_s']=230;state['repairs']={'old-problem':2};e.save(self.run,state)
        migration=dict(op='progress-migration',milestone='complete logger design',tasks=['old'],
                       prior_stalled=13,reason='Review of unchanged historical deliverable',
                       reviewer='history reviewer',path='evidence.md')
        adopted=self.event(**migration)
        for key in ('tasks','repairs','charged_s','budget_s','round','selected','phase'):
            self.assertEqual(state[key],adopted[key])
        self.assertEqual(progress.status(adopted['events'],adopted['tasks'])['stalled'],13)
        with self.assertRaises(ValueError):self.event(**migration)
        with self.assertRaisesRegex(ValueError,'reassessment required'):self.start('a')
        self.event(op='reassess',action='change',reason='User selected a different preparation',
                   hypothesis='Simpler conservative constraints permit routing',
                   check='Save and verify better native copper',deadline=500)
        before=json.loads((self.run/'run.json').read_text())
        self.event(op='start',id='recovery',kind='recovery',actor='author',seconds=100,
                   objective='One bounded recovery experiment',writes=['candidate-recovery'])
        self.event(op='finish',id='recovery',outcome='partial')
        after=json.loads((self.run/'run.json').read_text())
        for key in ('repairs','round','selected','phase'):
            self.assertEqual(before[key],after[key])
        self.assertEqual(after['charged_s'],before['charged_s']+100)
        with self.assertRaisesRegex(ValueError,'checkpoint required'):self.start('b')

    def test_historical_domain_checkpoint_is_not_a_milestone_event(self):
        state=json.loads((self.run/'run.json').read_text())
        historical=dict(op='checkpoint',continuation='C40',accepted_project='old-source',
                        accepted_roles={'schematic_reviewed':'historical-hash'},native_geometry_both_PASS=True)
        state['events'].extend([historical,{'historical_note':'no op field'}]);e.save(self.run,state)
        self.baseline();self.start('a')
        self.assertEqual(json.loads((self.run/'run.json').read_text())['events'][:2],state['events'])

    def test_recovery_parent_can_cover_long_tool_without_renewing_deadline(self):
        state=json.loads((self.run/'run.json').read_text())
        state['tasks']['old']=dict(kind='repair',status='finished');e.save(self.run,state)
        self.event(op='progress-migration',milestone='complete logger design',tasks=['old'],prior_stalled=13,
                   reason='Historical reviewed plateau',reviewer='history reviewer',path='evidence.md')
        self.event(op='reassess',action='change',reason='Different authoring method',hypothesis='Simpler constraints',
                   check='Native functional improvement',deadline=2000)
        self.event(op='start',id='parent',kind='recovery',actor='coordinator',seconds=1500,
                   objective='Bounded parent for tool and review',writes=['recovery-output'])
        self.assertEqual(json.loads((self.run/'run.json').read_text())['tasks']['parent']['deadline'],1600)

    def test_crow_checkpoint_replay_blocks_actual_cli_before_c51(self):
        fixture=json.loads((Path(__file__).parent/'test-fixtures/crow-progress.json').read_text())
        self.baseline(fixture['milestone'])
        for row in fixture['checkpoints'][:2]:
            self.start(row['id']);self.event(op='finish',id=row['id'],outcome='complete')
            path=self.run/f"{row['id']}-observation.json";path.write_text(json.dumps(row))
            self.event(op='milestone-checkpoint',milestone=fixture['milestone'],tasks=[row['id']],
                       result=row['result'],reason=row['observation'],path=path.name)
            if row['id']=='C49':
                self.event(op='reassess',action='continue',reason='One coherent owner correction',
                           hypothesis='Complete the coupled replacement',check='Compare functional continuity')
        request=self.run/'next.json'
        request.write_text(json.dumps(dict(op='start',id='C51',kind='draft',actor='new_model',seconds=10)))
        before=(self.run/'run.json').read_bytes()
        result=subprocess.run([sys.executable,str(Path(e.__file__).resolve()),'event',str(self.run),str(request)],
                              cwd=self.base,capture_output=True,text=True,timeout=10)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('milestone reassessment required',result.stderr)
        self.assertEqual(before,(self.run/'run.json').read_bytes())


if __name__=='__main__':unittest.main(verbosity=2)
