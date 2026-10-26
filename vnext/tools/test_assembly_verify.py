"""Synthetic native assembly fixtures; no real manufacturer or board acceptance."""
import copy
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import assembly_verify as a
import test_fabrication as fixture


class Assembly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture.Fabrication.setUpClass()
        cls.addClassCleanup(fixture.Fabrication.doClassCleanups)

    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='assembly-fixture-');self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)/'project';shutil.copytree(fixture.Fabrication.root_fixture,self.root)
        self.package='fabrication-package';self.name='assembly-models.json';self.out='assembly-output'
        models={ref:dict(manufacturer='FixtureMaker',mpn='Fixture-'+str(i),footprint='Test:Pad',
                   evidence=['evidence/geometry.txt'],basis='Synthetic 1-mm circular body only',
                   polarity='Synthetic single numbered contact 1',
                   bodies=[dict(shape='circle',center=[0,0],radius=.5,z=[0,1])],
                   contacts={'1':dict(xy=[0,0],tolerance_mm=0)}) for i,ref in enumerate(('U1','U2'),1)}
        bundle=a.p.read(self.root/self.package/'native/bundle.json')
        self.spec=dict(version=1,package=self.package,models=models,
             boards={key:dict(source_sha256=a.p.sha(self.root/self.package/'native'/row['native']),
                              references={'U1':'U1','U2':'U2'},access=[])
                     for key,row in bundle['boards'].items()},
             instructions=['evidence/manual.txt'],handoff=['evidence/handoff.txt'])
        self.save()
        self.subjects={str(f.relative_to(self.root)):a.p.sha(f)
                       for f in (self.root/self.package).rglob('*') if f.is_file()}

    @property
    def owner(self):
        # Nested review helpers need distinct context managers; re-entering one
        # unittest patch object leaks the substituted owner into later tests.
        return patch.object(a,'upstream',return_value=(self.package,self.subjects))

    def save(self): (self.root/self.name).write_text(json.dumps(self.spec))

    def build(self):
        with self.owner:return a.build(self.root,self.name,self.out)

    def verify(self):
        with self.owner:return a.verify(self.root,self.name,self.out)

    def test_complete_native_registration_replay_and_no_input_mutation(self):
        before=dict(self.subjects);report=self.build();result=self.verify()
        self.assertFalse(report['accepted']);self.assertEqual(report['order_status'],'DO-NOT-ORDER')
        for b in report['boards'].values():
            self.assertEqual(b['verdict'],'PASS');self.assertEqual(len(b['references']),2)
        for name,digest in before.items():self.assertEqual(a.p.sha(self.root/name),digest)
        self.assertEqual({str(f.relative_to(self.root)) for f in (self.root/self.package).rglob('*') if f.is_file()},set(before))
        self.assertIn(self.out+'/geometry.json',result['subjects'])
        for key in self.spec['boards']:
            bare=(self.root/self.out/(key+'-bare.svg')).read_text()
            pop=(self.root/self.out/(key+'-populated.svg')).read_text()
            self.assertEqual(bare.split('viewBox=')[1].split('>')[0],pop.split('viewBox=')[1].split('>')[0])
        with self.assertRaisesRegex(ValueError,'existing'):self.build()

    def test_missing_reference_board_model_contacts_and_wrong_identity_refused(self):
        original=copy.deepcopy(self.spec)
        mutations=[lambda s:s['boards'].pop('pod'),
                   lambda s:s['boards']['carrier']['references'].pop('U1'),
                   lambda s:s['models'].pop('U1'),
                   lambda s:s['models']['U1']['contacts'].update({'99':dict(xy=[0,0],tolerance_mm=0)}),
                   lambda s:s['models']['U1'].update(mpn='WRONG')]
        for mutate in mutations:
            self.spec=copy.deepcopy(original);mutate(self.spec);self.save()
            with self.assertRaises(ValueError):self.build()

    def test_collision_and_contact_failure_cannot_be_promoted(self):
        self.spec['models']['U1']['bodies']=[dict(shape='box',bounds=[-40,-2,40,2],z=[0,1])]
        self.spec['models']['U1']['contacts']['1']['xy']=[3,0];self.save()
        report=self.build()
        for b in report['boards'].values():
            self.assertEqual(b['verdict'],'FAIL')
            self.assertTrue(any(n.startswith('body:') for n in b['failures']))
            self.assertIn('contact:U1:1',b['failures'])
        with self.assertRaisesRegex(ValueError,'findings'):self.verify()

    def test_changed_source_evidence_output_and_extra_files_refused(self):
        self.build();e=self.root/'evidence/geometry.txt';saved=e.read_bytes();e.write_text('changed')
        with self.assertRaisesRegex(ValueError,'stale'):self.verify()
        e.write_bytes(saved);record=self.root/self.out/'geometry.json';content=record.read_bytes();record.write_text('{}')
        with self.assertRaisesRegex(ValueError,'stale'):self.verify()
        record.write_bytes(content);extra=self.root/self.out/'extra.pyc';extra.write_bytes(b'untracked')
        with self.assertRaisesRegex(ValueError,'census'):self.verify()
        extra.unlink();self.spec['boards']['carrier']['source_sha256']='0'*64;self.save()
        with self.assertRaisesRegex(ValueError,'stale assembly geometry'):self.verify()

    def test_linked_evidence_rejected(self):
        original=self.root/'evidence/geometry.txt';copy_path=self.root/'geometry-saved';original.rename(copy_path)
        original.symlink_to(copy_path)
        with self.assertRaisesRegex(ValueError,'linked'):self.build()

    def test_shapes_heights_and_native_cardinal_transform(self):
        circle=a.volume(dict(shape='circle',center=[0,0],radius=1,z=[0,1]),[0,0,0])
        diagonal=a.volume(dict(shape='box',bounds=[.9,.9,2,2],z=[0,1]),[0,0,0])
        self.assertFalse(a.collision(circle,diagonal))
        overlap=a.volume(dict(shape='box',bounds=[.5,.5,2,2],z=[0,1]),[0,0,0])
        self.assertTrue(a.collision(circle,overlap));overlap['z']=[1,2]
        self.assertFalse(a.collision(circle,overlap))
        turned=a.volume(dict(shape='box',bounds=[1,2,3,4],z=[0,1]),[10,20,90])
        for actual,expected in zip(turned['bounds'],[12,17,14,19]):self.assertAlmostEqual(actual,expected)
        with self.assertRaisesRegex(ValueError,'height'):a.volume(dict(shape='box',bounds=[0,0,1,1],z=[1,0]),[0,0,0])

    def test_access_obstruction_detected(self):
        self.spec['boards']['carrier']['access']=[dict(id='plug',ref='U1',bounds=[14,4,16,6],z=[0,2],
                                                       evidence=['evidence/mechanical.txt'])];self.save()
        r=self.build();self.assertIn('access:plug:U2',r['boards']['carrier']['failures'])
        with self.assertRaisesRegex(ValueError,'findings'):self.verify()

    def test_bare_view_retains_dnp_and_unnumbered_mechanical_drills(self):
        board=a.p.pcb.LoadBoard(str(self.root/'source.kicad_pcb'))
        fp=a.p.pcb.FOOTPRINT(board);fp.SetReference('MH1');board.Add(fp)
        pad=a.p.pcb.PAD(fp);pad.SetNumber('');pad.SetPosition(a.p.vector(10,15))
        pad.SetAttribute(a.p.pcb.PAD_ATTRIB_NPTH);pad.SetSize(a.p.vector(3,3))
        pad.SetDrillSize(a.p.vector(3,3));fp.Add(pad)
        rows=[dict(reference=ref,mode=mode,manufacturer='FixtureMaker',mpn='Fixture-'+str(i),footprint='Test:Pad')
              for i,(ref,mode) in enumerate([('U1','factory'),('U2','dnp')],1)]
        rows.append(dict(reference='MH1',mode='mechanical'))
        spec=copy.deepcopy(self.spec['boards']['carrier']);spec['references'].pop('U2')
        result=a.board_geometry(board,spec,self.spec['models'],rows)
        self.assertEqual(set(result['references']),{'U1'})
        self.assertEqual({r['reference'] for r in result['native_pads']},{'U1','U2','MH1'})
        hole=next(r for r in result['native_pads'] if r['reference']=='MH1')
        self.assertEqual(hole['drill'],[3,3]);self.assertEqual(hole['number'],'')
        for populated in (False,True):self.assertIn('<ellipse',a.svg('fixture',result,populated))

    def test_upstream_check_cannot_be_bypassed(self):
        authority=self.root/'assembly-authority.txt';authority.write_text('Synthetic scope')
        receipt=self.root/a.fab.RECEIPT;receipt.parent.mkdir(parents=True,exist_ok=True);receipt.write_text('{}')
        c=dict(version=1,authority='assembly-authority.txt',authority_sha256=a.p.sha(authority),
               fabrication_receipt_sha256=a.p.sha(receipt))
        (self.root/a.CONTRACT).parent.mkdir(parents=True,exist_ok=True)
        (self.root/a.CONTRACT).write_text(json.dumps(c))
        with patch.object(a.fab,'check',side_effect=ValueError('fabrication sentinel')) as owner:
            with self.assertRaisesRegex(ValueError,'sentinel'):a.build(self.root,self.name,self.out)
            owner.assert_called_once_with(self.root)
        authority.write_text('changed')
        with self.assertRaisesRegex(ValueError,'authority changed'):a.upstream(self.root)

    def review(self):
        result=self.verify();out=self.out;spec=self.spec
        geometry=[out+'/geometry.json',out+'/assembly.json']+[
            out+'/'+key+'-'+view+'.svg' for key in spec['boards'] for view in ('bare','populated')]
        population_files=[self.package+'/assembly/'+f.name
                          for f in (self.root/self.package/'assembly').iterdir() if f.suffix=='.csv']
        citations={'population':population_files+[out+'/geometry.json'],
                   'geometry':geometry+['evidence/geometry.txt'],
                   'polarity':['evidence/geometry.txt',out+'/geometry.json'],'access':geometry,
                   'instructions':spec['instructions'],'handoff':spec['handoff']+[self.package+'/fabrication.json']}
        return dict(schema=1,stage='JLC-ASSEMBLY-VERIFY',author='fixture author',reviewer='fixture reviewer',
                    manifest=self.name,output=out,verdict='PASS',subjects=result['subjects'],
                    checks={k:dict(verdict='PASS',rationale='Synthetic test, not an engineering verdict',evidence=v)
                            for k,v in citations.items()})

    def adopted(self):
        old=a.p.read
        def read(path):
            obj=old(path)
            if path==a.p.ROOT/'skills/pcb-design/workflow/graph.json':
                obj=copy.deepcopy(obj);s=next(s for s in obj['stages'] if s['spec']['id']=='JLC-ASSEMBLY-VERIFY')
                s.pop('local_definition',None);s['local_execution']=dict(tool='tools/assembly_verify.py',contract=a.STAGE,status='pilot_under_validation')
            return obj
        return patch.object(a.p,'read',side_effect=read)

    def test_independent_receipt_and_stale_coverage_controls(self):
        (self.root/a.CONTRACT).parent.mkdir(parents=True,exist_ok=True)
        (self.root/a.CONTRACT).write_text(json.dumps({'version':1}))
        self.build();review=self.review();name='08_reviews/2026-10-08-synthetic.md';path=self.root/name
        path.parent.mkdir(parents=True,exist_ok=True)
        def save():path.write_text('```json\n'+json.dumps(review)+'\n```\n')
        save()
        with self.owner,self.adopted():
            cert=a.certificate(self.root,name,historical=True);self.assertEqual(cert['role'],'assembly_verified')
            target=self.root/a.RECEIPT
            with patch.object(sys,'argv',['assembly_verify.py','issue','--project',str(self.root),'--review',name]), \
                 redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                self.assertEqual(a.main(),1)
                self.assertFalse(target.exists())
            # Synthetic historical receipt only: new CLI issuance above is blocked.
            target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(cert))
            self.assertEqual(a.check(self.root),cert)
            review['reviewer']=review['author'];save()
            with self.assertRaisesRegex(ValueError,'independent'):a.certificate(self.root,name,historical=True)
            review['reviewer']='other';review['checks']['geometry']['evidence']=[];save()
            with self.assertRaisesRegex(ValueError,'omits geometry'):a.certificate(self.root,name,historical=True)
            review=self.review();save();review['subjects'].pop(self.out+'/geometry.json');save()
            with self.assertRaisesRegex(ValueError,'subject coverage'):a.certificate(self.root,name,historical=True)
            review=self.review();review['checks']['handoff']['rationale']='Revised synthetic rationale';save()
            with self.assertRaisesRegex(ValueError,'stale assembly receipt'):a.check(self.root)

    def test_definition_only_graph_cannot_issue(self):
        read=a.p.read
        def definition(path):
            obj=read(path)
            if path==a.p.ROOT/'skills/pcb-design/workflow/graph.json':
                obj=copy.deepcopy(obj);s=next(s for s in obj['stages'] if s['spec']['id']=='JLC-ASSEMBLY-VERIFY')
                s.pop('local_execution',None);s['local_definition']={}
            return obj
        with patch.object(a.p,'read',side_effect=definition):
            with self.assertRaisesRegex(ValueError,'not adopted'):a.certificate(self.root,'absent.md')

    def test_version2_owner_admits_only_complete_independent_judgments(self):
        # Owner integration fixture. Only the expensive scene component and
        # upstream fabrication owner are mocked; judgment/subject/CLI gates run.
        import assembly_3d
        authority=self.root/'authority.txt';authority.write_text('Synthetic v2 scope')
        receipt=self.root/a.fab.RECEIPT;receipt.parent.mkdir(parents=True,exist_ok=True)
        receipt.write_text('{}')
        (self.root/'scene-source.json').write_text(json.dumps({'step_models':{}}))
        scene_dir=self.root/'registered-scene';scene_dir.mkdir()
        (scene_dir/'scene.json').write_text(json.dumps({'files':{}}))
        c=dict(version=2,authority='authority.txt',authority_sha256=a.p.sha(authority),
               fabrication_receipt_sha256=a.p.sha(receipt),mechanical={})
        (self.root/a.CONTRACT).parent.mkdir(parents=True,exist_ok=True)
        (self.root/a.CONTRACT).write_text(json.dumps(c))
        def registered(project,binding,name,spec,report,subjects):
            subjects=dict(subjects)
            a.evidence(project,['scene-source.json','registered-scene/scene.json'],subjects)
            return dict(version=1,scene_manifest='scene-source.json',scene_output='registered-scene',
                        subjects=subjects,limitations={'fixture-limit':'not hardware'},accepted=False)
        def judgment(evidence):
            return dict(verdict='PASS',rationale='Synthetic owner route, not board acceptance',evidence=evidence)
        name='08_reviews/2026-10-10-version2-fixture.md';path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True)
        with patch.object(assembly_3d,'scene',side_effect=registered) as component, self.owner,self.adopted():
            self.build();review=self.review()
            self.assertEqual(a.p.read(self.root/self.out/'assembly.json')['version'],2)
            self.assertIn(self.out+'/mechanical.json',review['subjects'])
            review['mechanical']=dict(
                models={key:judgment(model['evidence']) for key,model in self.spec['models'].items()},
                boards={key:judgment(['registered-scene/scene.json']) for key in self.spec['boards']},
                limitations={'fixture-limit':dict(classification='physical_qualification',
                    rationale='Synthetic fixture only',evidence=['evidence/geometry.txt'])})
            def save():path.write_text('```json\n'+json.dumps(review)+'\n```\n')
            save();cert=a.certificate(self.root,name)
            self.assertIn('assembly_3d.py',cert['toolchain'])
            self.assertIn(assembly_3d.GUIDANCE,cert['guidance'])
            original=copy.deepcopy(review)
            for mutate in (lambda r:r.pop('mechanical'),
                           lambda r:r['mechanical']['models'].pop('U1'),
                           lambda r:r['mechanical']['boards'].pop('pod'),
                           lambda r:r['mechanical']['limitations']['fixture-limit'].update(classification='outside_mating_scope'),
                           lambda r:r['subjects'].pop(self.out+'/mechanical.json')):
                review=copy.deepcopy(original);mutate(review);save()
                with self.assertRaises(ValueError):a.certificate(self.root,name)
                self.assertFalse((self.root/a.RECEIPT).exists())
            review=original;save()
            with patch.object(sys,'argv',['assembly_verify.py','issue','--project',str(self.root),'--review',name]), \
                 redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                self.assertEqual(a.main(),0)
            self.assertEqual(a.check(self.root),cert)
            self.assertGreater(component.call_count,1)
            (scene_dir/'scene.json').write_text(json.dumps({'files':{},'changed':True}))
            with self.assertRaisesRegex(ValueError,'stale assembly output'):a.check(self.root)


if __name__=='__main__':unittest.main()
