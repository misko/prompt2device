"""Real scene replay; engineering judgments here are explicitly synthetic."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import mating_admission as a
import test_mechanical_scene_replay as fixture


class Admission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture.Replay.setUpClass();cls.addClassCleanup(fixture.Replay.doClassCleanups)
        cls.seed=fixture.Replay.seed

    def setUp(self):
        tmp=tempfile.TemporaryDirectory(prefix='mating-admission-fixture-');self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)/'project';shutil.copytree(self.seed.root,self.root)
        self.report=a.p.read(self.root/'scene-output/scene.json')
        self.scene=a.p.read(self.root/'scene-input.json')
        assembly=a.p.read(self.root/self.scene['assembly_manifest'])
        bundle=a.p.read(self.root/assembly['package']/'native/bundle.json')
        (self.root/'placed').mkdir()
        for key,row in bundle['boards'].items():
            shutil.copyfile(self.root/assembly['package']/'native'/row['native'],self.root/'placed'/f'{key}.kicad_pcb')
        self.put('plan.json',{'boards':{key:{} for key in bundle['boards']}})
        self.placement=dict(plan='plan.json',output='placed')
        archive=self.root/'producer';files={}
        for name,digest in self.report['tools'].items():files['tools/'+name]=digest
        for name in ['skills/pcb-design/workflow/stages/assembly-verify.md',
                     'skills/pcb-design/procedures/fabrication/assembly-tooling.md']:
            files[name]=a.p.sha(a.p.ROOT/name)
        for name in files:
            target=archive/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a.p.ROOT/name,target)
        evidence='evidence/geometry.txt'
        self.requirements=dict(version=1,scope_evidence=[evidence],interfaces={
            key:dict(board=key,references=[next(iter(row['references']))],requirement='Synthetic module fit only',
                     evidence=[evidence]) for key,row in self.report['boards'].items()})
        self.put('requirements.json',self.requirements)
        self.mechanical=dict(scene_manifest='scene-input.json',scene_output='scene-output',
            toolchain='producer',toolchain_files=files,
            interfaces={key:{check:dict(verdict='PASS',rationale='Synthetic judgment, not hardware approval',
                        evidence=[evidence]) for check in a.CHECKS} for key in self.requirements['interfaces']},
            limitations={key:dict(classification='outside_mating_scope',
                rationale='Synthetic fixture qualification is not an actual product claim',evidence=[evidence])
                for key in a.limitation_inventory(self.report)})
        self.review=dict(applicability='applicable',mechanical=self.mechanical)

    def put(self,name,value):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value,indent=2)+'\n')

    def verify(self):return a.verify(self.root,'requirements.json',self.review,self.placement,{})

    def test_actual_frozen_scene_replay_and_complete_judgments(self):
        result=self.verify()
        self.assertEqual(result['interfaces'],sorted(self.requirements['interfaces']))
        self.assertIn('scene-output/scene.json',result['subjects'])
        self.assertIn('producer/tools/mechanical_scene.py',result['subjects'])
        self.assertIn('evidence/geometry.txt',result['subjects'])

    def test_missing_3d_packet_rejected(self):
        self.review.pop('mechanical')
        with self.assertRaisesRegex(ValueError,'registered mechanical'):self.verify()

    def test_omitted_interface_rejected(self):
        self.mechanical['interfaces'].pop(next(iter(self.mechanical['interfaces'])))
        with self.assertRaisesRegex(ValueError,'interface review coverage'):self.verify()

    def test_incomplete_or_failed_feature_review_rejected(self):
        key=next(iter(self.mechanical['interfaces']))
        for criterion in a.CHECKS:
            self.mechanical['interfaces'][key][criterion]['verdict']='UNRESOLVED'
            with self.assertRaisesRegex(ValueError,'unresolved interface'):self.verify()
            self.mechanical['interfaces'][key][criterion]['verdict']='PASS'

    def test_missing_limitation_disposition_rejected(self):
        self.mechanical['limitations'].pop(next(iter(self.mechanical['limitations'])))
        with self.assertRaisesRegex(ValueError,'limitation coverage'):self.verify()

    def test_unresolved_not_relabelled_qualification(self):
        row=next(iter(self.mechanical['limitations'].values()));row['classification']='unresolved'
        with self.assertRaisesRegex(ValueError,'unresolved scene'):self.verify()

    def test_interface_not_mounted_rejected(self):
        next(iter(self.requirements['interfaces'].values()))['references']=['MISSING']
        self.put('requirements.json',self.requirements)
        with self.assertRaisesRegex(ValueError,'absent from mounted'):self.verify()

    def test_not_applicable_cannot_hide_inventory(self):
        self.review['applicability']='not_applicable'
        with self.assertRaisesRegex(ValueError,'contradicts'):self.verify()

    def test_justified_no_foreign_interfaces_still_replays_scene(self):
        self.requirements['interfaces']={};self.put('requirements.json',self.requirements)
        self.review['applicability']='not_applicable';self.mechanical['interfaces']={}
        self.assertEqual(self.verify()['interfaces'],[])

    def test_stale_or_missing_export_rejected(self):
        name=next(iter(self.report['files']))
        (self.root/'scene-output'/name).write_text('wrong geometry')
        with self.assertRaisesRegex(ValueError,'stale scene artifact'):self.verify()

    def test_archive_change_rejected(self):
        path=self.root/'producer/tools/mechanical_scene.py';path.write_text(path.read_text()+'\n# changed')
        with self.assertRaisesRegex(ValueError,'producer archive changed'):self.verify()

    def test_current_placement_change_rejected(self):
        key=next(iter(self.report['boards']));path=self.root/'placed'/f'{key}.kicad_pcb'
        board=a.p.pcb.LoadBoard(str(path));fp=next(iter(board.GetFootprints()))
        fp.SetPosition(a.p.vector(25,18));a.p.pcb.SaveBoard(str(path),board)
        with self.assertRaisesRegex(ValueError,'accepted placement'):self.verify()

    def test_board_thickness_change_rejected(self):
        key=next(iter(self.report['boards']));path=self.root/'placed'/f'{key}.kicad_pcb'
        board=a.p.pcb.LoadBoard(str(path));board.GetDesignSettings().SetBoardThickness(2000000)
        a.p.pcb.SaveBoard(str(path),board)
        with self.assertRaisesRegex(ValueError,'accepted placement'):self.verify()

    def test_owning_receipt_requires_real_replay_and_independent_scope(self):
        import routing as r
        result=self.verify()
        self.put('authority.json',{'scope':'Synthetic fixture only'})
        self.put('placement-receipt.json',{'fixture':'accepted upstream mocked only in this test'})
        contract=dict(version=3,authority='authority.json',authority_sha256=a.p.sha(self.root/'authority.json'),
                      placement_receipt='placement-receipt.json',placement_receipt_sha256=a.p.sha(self.root/'placement-receipt.json'),
                      mating_requirements='requirements.json',mating_receipt='mating-receipt.json')
        self.put(r.CONTRACT,contract)
        subjects={**result['subjects'],**r.base_subjects(self.root,contract)}
        review={**self.review,'schema':1,'stage':'KICAD-MATING-IMPORT','author':'fixture author',
                'reviewer':'fixture independent reviewer','verdict':'PASS','subjects':subjects,
                'scope_evidence':['requirements.json'],'geometry_evidence':['scene-output/scene.json'],
                'checks':{key:dict(verdict='PASS',rationale='Synthetic independent judgment only',
                          evidence=['evidence/geometry.txt']) for key in r.CRITERIA['mating']}}
        name='08_reviews/2026-10-09-synthetic-mating.md';path=self.root/name;path.parent.mkdir()
        path.write_text('```json\n'+json.dumps(review)+'\n```\n')
        with patch.object(r,'upstream',return_value=(contract,self.placement,{})):
            receipt=r.receipt(self.root,name,'mating')
            self.assertEqual(receipt['role'],'mating_clearance')
            self.assertEqual(receipt['mechanical']['interfaces'],sorted(self.requirements['interfaces']))
            key=next(iter(review['mechanical']['interfaces']))
            review['mechanical']['interfaces'][key]['tolerances']['verdict']='FAIL'
            path.write_text('```json\n'+json.dumps(review)+'\n```\n')
            with self.assertRaisesRegex(ValueError,'unresolved interface'):r.receipt(self.root,name,'mating')

    def test_collision_is_not_an_engineering_waiver(self):
        row=next(iter(self.report['boards'].values()));row['clearance']['failures']=[{'collision':True}]
        self.put('scene-output/scene.json',self.report)
        with self.assertRaisesRegex(ValueError,'nominal mechanical failures'):self.verify()

    def test_extra_artifact_cannot_hide_outside_report(self):
        (self.root/'scene-output/unaccounted.txt').write_text('extra')
        with self.assertRaisesRegex(ValueError,'frozen scene replay failed'):self.verify()


if __name__=='__main__':unittest.main()
