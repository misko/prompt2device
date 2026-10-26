"""Behavioral transition regressions. Synthetic artifacts, not PCB validation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import exploration as e
import workflow


class ExplorationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)
        self.brief=self.base/'input.md';self.brief.write_text('Eight coherent audio channels, USB,12V,8pods with buzzers.\n')
        self.root=self.base/'run'
        e.initialize(self.root,self.brief,budget=2000,width=1,rounds=2)
        self.clock=100

    def tearDown(self):self.temp.cleanup()

    def event(self,**kw):
        self.clock+=1
        # These candidate-transition fixtures explicitly supply the new milestone
        # checkpoints. test_progress exercises missing/invalid ones without this
        # convenience. No synthetic local success is declared board advancement.
        if kw['op']=='start' and not self.state()['paused']:
            self.progress_checkpoint()
        return e.apply(self.root,kw,now=self.clock)

    def progress_checkpoint(self):
        s=self.state();events=s['events'];tasks=s['tasks']
        evidence=self.root/'progress-evidence.md'
        evidence.write_text('Synthetic transition fixture; no engineering advancement.\n')
        if not any(x['op']=='milestone-checkpoint' for x in events):
            e.apply(self.root,dict(op='milestone-checkpoint',milestone='whole deliverable',tasks=[],
                    result='baseline',reason='Synthetic starting point',path=evidence.name),now=self.clock)
        s=self.state();p=e.progress.status(s['events'],s['tasks'])
        if p['pending'] and not any(t['status']=='running' for t in tasks.values()):
            e.apply(self.root,dict(op='milestone-checkpoint',milestone=p['milestone'],tasks=p['pending'],
                    result='unchanged',reason='No domain advancement in this fixture',path=evidence.name),now=self.clock)
            s=self.state();p=e.progress.status(s['events'],s['tasks'])
        if p['stalled'] and not p['decision']:
            e.apply(self.root,dict(op='reassess',action='continue' if p['stalled']<2 else 'escalate',
                    reason='Exercise candidate transitions under a bounded synthetic recovery',
                    hypothesis='Fixture controls distinguish valid transitions',
                    check='Run the named transition assertion',deadline=10000),now=self.clock)

    def state(self):return json.loads((self.root/'run.json').read_text())

    def candidate(self,cid='a',kind='draft',**kw):
        self.event(op='start',id=cid,actor='author_'+cid,seconds=100,kind=kind,**kw)
        (self.root/'candidates'/cid/'design.txt').write_text('Candidate pin map, not real CAD\n')
        self.event(op='finish',id=cid,outcome='complete')

    def compare(self,rid='review1',eligible=True,reviewer='independent',compact=False,references=None):
        self.event(op='start',id=rid,kind='review',actor=reviewer,seconds=100)
        s=self.state();cs=e.current_candidates(s)
        d=dict(reviewer=reviewer,subjects={k:v['snapshot'] for k,v in cs.items()},
               assessments={k:dict(eligible=eligible,rationale='Needs power repair') for k in cs},
               findings=[dict(id='power-transition',kind='uncertainty',statement='Shutdown ordering unresolved',
                              evidence='Synthetic Crow power-transition fixture, not a silicon verdict',
                              candidates=list(cs),blocking=True)])
        if compact:d['subjects']=e.review_subjects(self.root)
        if references is not None:d['subjects']=references
        p=self.root/'reviews'/f'{rid}.json';p.write_text(json.dumps(d))
        self.event(op='finish',id=rid,outcome='complete')
        self.event(op='review',task=rid,path=str(p.relative_to(self.root)))
        return p

    def select(self,cid='a'):return self.event(op='select',candidate=cid,rationale='Repair baseline only')

    def lessons(self,**change):
        d=dict(brief_sha256=self.state()['brief_sha256'],blockers=['power-transition'],
               blocker_evidence={'power-transition':'Synthetic Crow power-transition fixture, not a silicon verdict'},
               hypothesis='Different power ownership could remove sequencing dependence',
               learned='Prior candidate needs coupled supply ordering',unknowns='Physical rail decay unmeasured',
               failed_attempts=[],outcomes={},freedom='Replace topology and parts, preserve all requirements')
        d.update(change)
        if 'outcomes' not in change:d['outcomes']={t:'Reviewed blocker remains unresolved' for t in d['failed_attempts']}
        p=self.root/'lessons'/f"r{self.state()['round']+1}.json";p.write_text(json.dumps(d));return str(p.relative_to(self.root))

    def test_draft_without_architecture_or_stock_receipts(self):
        self.candidate();self.assertFalse((self.root/'parts_locked.json').exists())

    def test_selection_never_acceptance(self):
        self.candidate();self.compare();s=self.select()
        self.assertEqual(s['phase'],'selected')
        self.assertNotIn('schematic_reviewed',s)
        with self.assertRaises(ValueError):self.event(op='accept',candidate='a')

    def test_compact_review_selects_and_reopens_without_acceptance(self):
        self.candidate();self.compare(compact=True);before=self.select()
        self.assertIsInstance(json.loads((self.root/'reviews/review1.json').read_text())['subjects']['a'],str)
        self.candidate('fix','repair',parent='a',problem='power-transition')
        self.assertEqual(self.state()['repairs']['power-transition'],1)
        self.assertNotIn('schematic_reviewed',before)

    def test_compact_subject_export_is_read_only_and_order_independent(self):
        self.candidate();before=(self.root/'run.json').read_bytes()
        refs=e.review_subjects(self.root)
        self.assertEqual(refs['a'],e.snapshot_digest(self.state()['tasks']['a']['snapshot']))
        self.assertEqual(before,(self.root/'run.json').read_bytes())
        self.assertEqual(e.snapshot_digest({'a':'1','b':'2'}),e.snapshot_digest({'b':'2','a':'1'}))
        self.assertNotEqual(e.snapshot_digest({'a':'1'}),e.snapshot_digest({'renamed':'1'}))

    def test_compact_subject_export_rejects_unfinished_or_stale_candidate(self):
        self.event(op='start',id='a',kind='draft',actor='author',seconds=100)
        with self.assertRaisesRegex(ValueError,'unfinished'):e.review_subjects(self.root)
        (self.root/'candidates/a/design.txt').write_text('original')
        self.event(op='finish',id='a',outcome='complete')
        (self.root/'candidates/a/design.txt').write_text('changed')
        with self.assertRaisesRegex(ValueError,'stale'):e.review_subjects(self.root)

    def test_forged_compact_subject_cannot_be_adopted(self):
        self.candidate()
        with self.assertRaisesRegex(ValueError,'stale candidate'):
            self.compare(references={'a':'0'*64})
        self.assertIsNone(self.state()['review'])

    def test_compact_review_reuse_detects_modified_added_and_removed_files(self):
        self.candidate();self.compare(compact=True);self.select()
        path=self.root/'candidates/a/design.txt';original=path.read_bytes()
        for action in ('modify','add','remove'):
            with self.subTest(action=action):
                if action=='modify':path.write_text('changed')
                elif action=='add':(path.parent/'extra.txt').write_text('unexpected')
                else:path.unlink()
                with self.assertRaisesRegex(ValueError,'stale review'):e.reviewed(self.root,self.state())
                path.write_bytes(original)
                if action=='add':(path.parent/'extra.txt').unlink()

    def test_compact_references_do_not_relax_subject_coverage(self):
        self.candidate()
        with self.assertRaisesRegex(ValueError,'cover all current candidates'):
            self.compare(references={})

    def diagnosis(self):
        return self.event(op='start',id='diagnosis',kind='diagnose',actor='expert',seconds=100,
                          parent='a',problem='power-transition',question='Does a local restart inject charge?')

    def test_diagnosis_preserves_review_selection_and_attempts(self):
        self.candidate();self.compare();before=self.select();self.diagnosis()
        p=self.root/'reviews'/'diagnosis.md';p.write_text('Bounded assessment; no acceptance.\n')
        after=self.event(op='finish',id='diagnosis',outcome='complete',path='reviews/diagnosis.md')
        for key in ('phase','selected','review','repairs','round'):
            self.assertEqual(before[key],after[key])
        self.assertEqual(after['charged_s'],before['charged_s']+100)
        self.assertEqual(after['tasks']['diagnosis']['evidence']['sha256'],e.digest(p))
        self.assertNotIn('diagnosis',e.current_candidates(after))

    def test_diagnosis_requires_checkpoint_and_current_problem(self):
        with self.assertRaisesRegex(ValueError,'settled review'):self.diagnosis()
        self.candidate();self.compare();self.select()
        with self.assertRaisesRegex(ValueError,'current blocker'):
            self.event(op='start',id='bad',kind='diagnose',actor='expert',seconds=100,
                       parent='a',problem='invented',question='Unrelated?')

    def test_view_reports_live_diagnosis_without_promoting_phase(self):
        self.candidate();self.compare();self.select();self.diagnosis()
        self.event(op='bind',id='diagnosis',handle='/root/expert')
        before=(self.root/'run.json').read_bytes()
        view=workflow.render(self.root)
        self.assertIn('Live task `diagnosis` (diagnose)',view)
        self.assertIn('handle `/root/expert`',view)
        self.assertIn('phase `selected`',view)
        self.assertEqual(before,(self.root/'run.json').read_bytes())

    def test_diagnosis_cannot_close_without_evidence_or_repeat(self):
        self.candidate();self.compare();self.select();self.diagnosis()
        with self.assertRaisesRegex(ValueError,'needs evidence'):
            self.event(op='finish',id='diagnosis',outcome='complete')
        self.event(op='finish',id='diagnosis',outcome='partial')
        with self.assertRaisesRegex(ValueError,'already attempted'):
            self.event(op='start',id='new_expert',kind='diagnose',actor='other',seconds=100,
                       parent='a',problem='power-transition',question='Same underlying question')

    def test_diagnosis_detects_frozen_subject_mutation(self):
        self.candidate();self.compare();self.select();self.diagnosis()
        (self.root/'candidates/a/design.txt').write_text('Unauthorized circuit edit\n')
        with self.assertRaisesRegex(ValueError,'stale'):
            self.event(op='finish',id='diagnosis',outcome='partial')

    def test_diagnosis_respects_existing_budget(self):
        self.candidate();self.compare();self.select()
        s=self.state();s['budget_s']=s['charged_s']+99;e.save(self.root,s)
        with self.assertRaisesRegex(ValueError,'budget exhausted'):self.diagnosis()

    def test_reopened_review_requires_reason_and_retains_comparison_ceiling(self):
        self.candidate();self.compare();self.select()
        with self.assertRaisesRegex(ValueError,'new evidence reason'):
            self.event(op='start',id='r2',kind='review',actor='reviewer2',seconds=100)
        self.event(op='start',id='r2',kind='review',actor='reviewer2',seconds=100,
                   reason='Focused diagnosis supplies new operating-state evidence')
        self.event(op='finish',id='r2',outcome='partial')
        with self.assertRaisesRegex(ValueError,'comparison attempt ceiling'):
            self.event(op='start',id='r3',kind='review',actor='reviewer3',seconds=100)

    def test_expert_diagnosis_after_two_repairs_does_not_unlock_third(self):
        self.candidate();self.compare();self.select()
        for n,parent in [(1,'a'),(2,'fix1')]:
            self.candidate('fix'+str(n),'repair',parent=parent,problem='power-transition')
            self.compare('review'+str(n+1));self.select('fix'+str(n))
        self.event(op='start',id='expert',kind='diagnose',actor='expert',seconds=100,
                   parent='fix2',problem='power-transition',question='Earliest causal choice?')
        self.event(op='finish',id='expert',outcome='partial')
        with self.assertRaisesRegex(ValueError,'ceiling'):
            self.candidate('fix3','repair',parent='fix2',problem='power-transition')

    def test_self_review_rejected(self):
        self.candidate()
        with self.assertRaisesRegex(ValueError,'independent'):self.compare(reviewer='author_a')

    def test_no_clean_check_shortcut_for_ineligible_candidate(self):
        self.candidate();self.compare(eligible=False)
        with self.assertRaises(ValueError):self.select()

    def test_changed_candidate_invalidates_review(self):
        self.candidate();self.compare()
        (self.root/'candidates/a/design.txt').write_text('Changed power pin\n')
        with self.assertRaisesRegex(ValueError,'stale'):self.select()

    def test_changed_review_invalidates_selection(self):
        self.candidate();p=self.compare();p.write_text(p.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'review changed'):self.select()

    def test_pause_blocks_dispatch_and_requires_explicit_resume(self):
        self.event(op='pause',reason='User asked to stop')
        with self.assertRaisesRegex(ValueError,'paused'):self.candidate()
        with self.assertRaises(ValueError):self.event(op='resume')
        self.event(op='resume',user_authorized=True);self.candidate()

    def test_finish_after_pause_records_actual_handle_and_overrun(self):
        self.event(op='start',id='a',kind='draft',actor='author',seconds=10)
        self.event(op='bind',id='a',handle='/root/real_worker')
        self.event(op='pause',reason='User stop')
        self.clock=120;s=self.event(op='finish',id='a',outcome='failed')
        self.assertEqual(s['tasks']['a']['handle'],'/root/real_worker')
        self.assertGreater(s['charged_s'],10);self.assertTrue(s['paused'])

    def test_redesign_keeps_requirements_budget_and_repair_history(self):
        self.candidate();self.compare();self.select()
        self.candidate('fix1','repair',parent='a',problem='power-transition')
        self.compare('review2');self.select('fix1')
        before=self.state();s=self.event(op='reexplore',path=self.lessons(failed_attempts=['fix1']))
        self.assertEqual(s['charged_s'],before['charged_s'])
        self.assertEqual(s['repairs'],{'power-transition':1})
        self.assertEqual(s['brief_sha256'],before['brief_sha256'])
        self.assertEqual(s['round'],2);self.assertIsNone(s['selected'])
        self.candidate('fresh');self.compare('review3')
        with self.assertRaisesRegex(ValueError,'no further'):self.event(op='reexplore',path=self.lessons())

    def test_renamed_task_does_not_renew_same_problem(self):
        self.candidate();self.compare();self.select()
        for n,parent in [(1,'a'),(2,'fix1')]:
            self.candidate('fix'+str(n),'repair',parent=parent,problem='power-transition')
            self.compare('review'+str(n+1));self.select('fix'+str(n))
        with self.assertRaisesRegex(ValueError,'ceiling'):
            self.candidate('capacitor_research','repair',parent='fix2',problem='power-transition')

    def test_changed_requirement_or_invented_blocker_rejected(self):
        self.candidate();self.compare()
        for changes in ({'brief_sha256':'wrong'},{'blockers':['imaginary']},{'failed_attempts':['not-run']}):
            with self.assertRaises(ValueError):self.event(op='reexplore',path=self.lessons(**changes))

    def test_budget_exhaustion_not_reset_by_round(self):
        self.candidate();self.compare();self.event(op='reexplore',path=self.lessons())
        self.event(op='start',id='big',actor='other',kind='draft',seconds=100)
        self.event(op='finish',id='big',outcome='failed')
        s=self.state();s['budget_s']=s['charged_s'];e.save(self.root,s)
        with self.assertRaises(ValueError):self.event(op='start',id='r',actor='reviewer',kind='review',seconds=100)

    def test_paths_and_fresh_brief(self):
        with self.assertRaises(ValueError):self.event(op='start',id='../escape',actor='a',kind='draft',seconds=10)
        (self.root/'BRIEF.md').write_text('One channel only\n')
        with self.assertRaisesRegex(ValueError,'brief changed'):self.candidate()

    def test_all_fanout_candidates_must_be_compared(self):
        s=self.state();s['width']=3;e.save(self.root,s)
        self.candidate('a')
        with self.assertRaises(ValueError):self.compare()
        self.candidate('b');self.candidate('c');self.compare()
        self.assertEqual(len(self.state()['tasks']),4)

    def test_same_control_for_unrelated_board(self):
        # No Crow names, channel count or component choices in the adapter.
        self.brief.write_text('Design a battery-powered temperature logger.\n')
        self.root=self.base/'temperature'
        e.initialize(self.root,self.brief,budget=600,width=1,rounds=1)
        self.candidate();self.compare();self.select()
        self.assertEqual(self.state()['phase'],'selected')

    def test_empty_failed_candidate_can_be_compared_but_not_selected(self):
        self.event(op='start',id='a',kind='draft',actor='author',seconds=100)
        self.event(op='finish',id='a',outcome='failed')
        self.compare(eligible=False)
        with self.assertRaises(ValueError):self.select()

    def test_redesign_pointer_mutation_stops_dispatch(self):
        self.candidate();self.compare()
        path=self.lessons();self.event(op='reexplore',path=path)
        (self.root/path).write_text('{}')
        with self.assertRaisesRegex(ValueError,'pointers changed'):self.candidate('b')

    def test_comparison_budget_reserved_before_fanout(self):
        s=self.state();s['budget_s']=350;s['width']=3;e.save(self.root,s)
        with self.assertRaisesRegex(ValueError,'reserve'):self.candidate()

    def test_infeasible_initial_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,'reserve'):
            e.initialize(self.base/'bad',self.brief,budget=3,width=3)

    def test_redesign_cannot_drop_blocker_evidence(self):
        self.candidate();self.compare()
        with self.assertRaisesRegex(ValueError,'blocker evidence'):
            self.event(op='reexplore',path=self.lessons(blocker_evidence={}))

    def test_failed_review_cannot_publish(self):
        self.candidate();self.compare()
        s=self.state();s['phase']='review';s['review']=None
        s['tasks']['review1']['outcome']='failed';e.save(self.root,s)
        with self.assertRaisesRegex(ValueError,'did not complete'):
            self.event(op='review',task='review1',path='reviews/review1.json')

    def test_failed_comparison_has_one_bounded_retry(self):
        self.candidate()
        self.event(op='start',id='badreview',kind='review',actor='independent',seconds=100)
        self.event(op='finish',id='badreview',outcome='failed')
        self.compare('retryreview');self.select()
        self.assertEqual(self.state()['phase'],'selected')

    def test_repeated_failed_comparisons_do_not_loop(self):
        self.candidate()
        for rid in ('review1','review2'):
            self.event(op='start',id=rid,kind='review',actor='independent',seconds=100)
            self.event(op='finish',id=rid,outcome='partial')
        with self.assertRaisesRegex(ValueError,'comparison attempt ceiling'):
            self.event(op='start',id='review3',kind='review',actor='new_person',seconds=100)

    def test_redesign_cannot_omit_prior_remedy(self):
        self.candidate();self.compare();self.select()
        self.candidate('fix','repair',parent='a',problem='power-transition')
        self.compare('review2')
        with self.assertRaisesRegex(ValueError,'omitted prior'):
            self.event(op='reexplore',path=self.lessons())
        with self.assertRaisesRegex(ValueError,'outcomes'):
            self.event(op='reexplore',path=self.lessons(failed_attempts=['fix'],outcomes={}))

    def test_workflow_view_includes_exploration_without_acceptance(self):
        self.candidate();self.compare();self.select()
        before=(self.root/'run.json').read_bytes()
        view=workflow.render(self.root)
        self.assertIn('Exploration before acceptance',view)
        self.assertIn('redesign_brief',view)
        self.assertIn('phase `selected`, selected `a`',view)
        self.assertIn('No acceptance inferred',view)
        self.assertNotIn('STATUS unavailable',view)
        self.assertEqual(before,(self.root/'run.json').read_bytes())

    def test_assist_is_charged_and_parent_waits_for_it(self):
        self.candidate();self.compare();self.select()
        self.event(op='start',id='fix',kind='repair',actor='engineer',seconds=200,parent='a',problem='power-transition')
        before=self.state()['charged_s']
        self.event(op='start',id='stock',kind='assist',actor='researcher',seconds=50,parent='fix')
        self.assertEqual(self.state()['charged_s'],before+50)
        with self.assertRaisesRegex(ValueError,'child work'):
            self.event(op='finish',id='fix',outcome='complete')
        self.event(op='finish',id='stock',outcome='complete')
        self.event(op='start',id='render',kind='assist',actor='renderer',seconds=50,parent='fix')
        self.event(op='finish',id='render',outcome='complete')
        self.assertEqual(self.state()['charged_s'],before+100)
        self.event(op='finish',id='fix',outcome='partial')
        self.assertEqual(e.progress.status(self.state()['events'],self.state()['tasks'])['pending'],
                         ['fix','render','stock'])
        self.assertNotIn('stock',e.current_candidates(self.state()))

    def test_assist_cannot_outlive_parent_or_start_without_one(self):
        with self.assertRaisesRegex(ValueError,'live repair'):
            self.event(op='start',id='stock',kind='assist',actor='researcher',seconds=50,parent='none')
        self.candidate();self.compare();self.select()
        self.event(op='start',id='fix',kind='repair',actor='engineer',seconds=100,parent='a',problem='power-transition')
        with self.assertRaisesRegex(ValueError,'parent deadline'):
            self.event(op='start',id='stock',kind='assist',actor='researcher',seconds=100,parent='fix')

    def test_decision_note_neither_promotes_nor_renews_budget(self):
        before=self.state()
        after=self.event(op='note',reason='Reassess an upstream interface from manufacturer evidence')
        for key in ('phase','round','selected','charged_s','repairs'):
            self.assertEqual(before[key],after[key])

    def test_allowance_needs_reviewed_checkpoint_and_authority(self):
        with self.assertRaisesRegex(ValueError,'checkpoint'):
            self.event(op='allowance',budget_s=3000,reason='Continue',authority='User continuation')
        self.candidate();self.compare();self.select()
        with self.assertRaisesRegex(ValueError,'authority'):
            self.event(op='allowance',budget_s=3000,reason='Continue')
        with self.assertRaisesRegex(ValueError,'larger finite total'):
            self.event(op='allowance',budget_s=1000,reason='Continue',authority='User continuation')

    def test_allowance_preserves_spend_repairs_rounds_and_review(self):
        self.candidate();self.compare();self.select()
        self.candidate('fix','repair',parent='a',problem='power-transition')
        self.compare('review2');self.select('fix')
        before=self.state()
        after=self.event(op='allowance',budget_s=3000,
                         reason='Independent review identifies a finite next remedy',
                         authority='User requested further in-scope development; prior ceiling coordinator-set')
        for key in ('phase','round','selected','charged_s','repairs','tasks','review','max_rounds'):
            self.assertEqual(before[key],after[key])
        self.assertEqual(after['budget_s'],3000)
        self.assertEqual(after['events'][-1]['previous_budget_s'],2000)

    def test_canceled_dispatch_retains_charge_without_consuming_comparison(self):
        self.candidate()
        self.event(op='start',id='provider',kind='review',actor='reviewer',seconds=100)
        self.event(op='bind',id='provider',handle='/root/provider')
        self.event(op='finish',id='provider',outcome='failed')
        self.event(op='start',id='canceled',kind='review',actor='reviewer',seconds=100)
        self.event(op='finish',id='canceled',outcome='failed')
        before=self.state()
        self.compare('actual_retry')
        after=self.state()
        self.assertEqual(after['charged_s'],before['charged_s']+100)
        self.assertEqual(after['tasks']['canceled'],before['tasks']['canceled'])
        self.select()
        with self.assertRaisesRegex(ValueError,'comparison attempt ceiling'):
            self.event(op='start',id='third',kind='review',actor='reviewer',seconds=100,
                       reason='No extra executed comparison allowed')

    def test_bound_provider_failures_still_consume_two_comparison_ceiling(self):
        self.candidate()
        for rid in ('p1','p2'):
            self.event(op='start',id=rid,kind='review',actor='reviewer',seconds=100)
            self.event(op='bind',id=rid,handle='/root/'+rid)
            self.event(op='finish',id=rid,outcome='failed')
        with self.assertRaisesRegex(ValueError,'comparison attempt ceiling'):
            self.event(op='start',id='p3',kind='review',actor='reviewer',seconds=100)

    def test_failed_review_allowance_preserves_history_and_requires_terminal_failure(self):
        self.candidate()
        self.event(op='start',id='provider',kind='review',actor='reviewer',seconds=100)
        args=dict(op='allowance',budget_s=2600,failed_review='provider',
                  reason='Provider capacity independently observed restored',
                  authority='Continuing user task; previous allowance coordinator-set')
        with self.assertRaisesRegex(ValueError,'terminal failed review'):self.event(**args)
        self.event(op='finish',id='provider',outcome='failed')
        before=self.state();after=self.event(**args)
        for key in ('phase','selected','review','charged_s','tasks','repairs','round'):
            self.assertEqual(before[key],after[key])
        with self.assertRaisesRegex(ValueError,'already used'):
            self.event(**dict(args,budget_s=3200))
        self.assertNotIn('schematic_reviewed',after)

    def test_completed_review_cannot_use_failed_recovery_allowance(self):
        self.candidate();self.compare()
        with self.assertRaisesRegex(ValueError,'terminal failed review'):
            self.event(op='allowance',budget_s=2600,failed_review='review1',
                       reason='Wrong route',authority='Coordinator')


if __name__=='__main__':unittest.main(verbosity=2)
