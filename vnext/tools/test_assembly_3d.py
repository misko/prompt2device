"""Admission-contract negatives; synthetic judgments are not board acceptance."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import assembly_3d as a


class RegisteredAssembly(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);self.root=Path(tmp.name)
        self.spec={'package':'package','models':{'part':{'evidence':['maker.txt']}},
                   'boards':{'board':{'source_sha256':'pending'}}}
        self.refs={'U1':{'model':'part','position':[1,2,0]}}
        self.envelope={'boards':{'board':{'references':self.refs}}}
        self.put('maker.txt','synthetic source');self.put('assembly.json',self.spec)
        self.put('scene-manifest.json',{'assembly_manifest':'assembly.json','step_models':{}})
        self.put('package/native/board.kicad_pcb','synthetic board')
        self.spec['boards']['board']['source_sha256']=self.sha('package/native/board.kicad_pcb')
        self.put('assembly.json',self.spec)
        self.put('package/native/bundle.json',{'boards':{'board':{'native':'board.kicad_pcb'}}})
        self.put('package/fabrication.json',{});self.put('package/assembly/population.csv','synthetic')
        for tool in ('mechanical_scene.py','mechanical_kernel.py','assembly_verify.py'):
            self.put('frozen/tools/'+tool,'# synthetic producer; never executed\n')
        self.binding=dict(scene_manifest='scene-manifest.json',scene_output='scene',toolchain='frozen',
                          toolchain_files=a.mechanical.inventory(self.root/'frozen'))
        artifacts=['board/board-populated.step','board/board.step','board/native-dielectric.step']
        artifacts += ['board/twin_'+v+'.png' for v in a.VIEWS]
        artifacts += ['board/render_'+v+'_bare.png' for v in ('top','bottom')]
        for name in artifacts:self.put('scene/'+name,'synthetic artifact')
        part=dict(verdict='PASS',solids_after=1)
        self.report=dict(version=1,accepted=False,status='INCOMPLETE',manifest='scene-manifest.json',
            unresolved=['Synthetic physical qualification remains'],
            models={'part':{'limitations':['Synthetic source bound']}},
            inputs={n:self.sha(n) for n in ['assembly.json','scene-manifest.json',
                'package/native/bundle.json','package/fabrication.json','package/assembly/population.csv',
                'package/native/board.kicad_pcb']},
            tools={n:self.sha('frozen/tools/'+n) for n in ('mechanical_scene.py','mechanical_kernel.py','assembly_verify.py')},
            files={n:self.sha('scene/'+n) for n in artifacts},
            boards={'board':dict(references=self.refs,mounted_references=1,contact_failures=[],
                clearance=dict(verdict='PASS',failures=[]),access=[],
                step_roundtrip=dict(verdict='PASS',parts={'board':part,'U1':part}),
                board_datum={'bare_step_roundtrip':{'verdict':'PASS'},'limitation':'Synthetic datum'},
                frames={v:{} for v in a.VIEWS},details={})})
        self.save()

    def put(self,n,v):
        path=self.root/n;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(v if isinstance(v,str) else json.dumps(v))
    def sha(self,n):return a.p.sha(self.root/n)
    def save(self):self.put('scene/scene.json',self.report)
    def run_scene(self):
        with patch.object(a.subprocess,'run',return_value=SimpleNamespace(returncode=0,stderr='',stdout='')) as run:
            result=a.scene(self.root,self.binding,'assembly.json',self.spec,self.envelope,{})
            run.assert_called_once()
            self.assertEqual(run.call_args.kwargs['timeout'],600)
            self.assertIn('verify',run.call_args.args[0])
            return result

    def test_complete_binding_calls_replay_and_preserves_unaccepted_scope(self):
        result=self.run_scene();self.assertFalse(result['accepted'])
        self.assertEqual(result['coverage'],{'board':{'U1':'part'}})
        self.assertEqual(len(result['limitations']),3)

    def test_missing_model_body_reference_view_or_board_refused(self):
        original=copy.deepcopy(self.report)
        mutations=[lambda r:r['models'].clear(),lambda r:r['boards'].clear(),
            lambda r:r['boards']['board']['references'].clear(),
            lambda r:r['boards']['board']['frames'].pop('top'),
            lambda r:r['boards']['board']['step_roundtrip']['parts'].pop('U1')]
        for mutate in mutations:
            self.report=copy.deepcopy(original);mutate(self.report);self.save()
            with self.assertRaises(ValueError):self.run_scene()

    def test_stale_source_wrong_native_missing_artifact_and_extra_file_refused(self):
        self.put('package/native/board.kicad_pcb','changed')
        with self.assertRaisesRegex(ValueError,'stale'):self.run_scene()
        self.put('package/native/board.kicad_pcb','synthetic board')
        original=self.report['inputs'].pop('package/native/board.kicad_pcb');self.save()
        with self.assertRaisesRegex(ValueError,'native differs'):self.run_scene()
        self.report['inputs']['package/native/board.kicad_pcb']=original;self.save()
        target=self.root/'scene/board/twin_top.png';target.unlink()
        with self.assertRaisesRegex(ValueError,'census'):self.run_scene()
        self.put('scene/board/twin_top.png','synthetic artifact');self.put('scene/unexpected.txt','extra')
        with self.assertRaisesRegex(ValueError,'census'):self.run_scene()

    def test_wrong_assembly_and_missing_package_binding_refused(self):
        self.put('scene-manifest.json',{'assembly_manifest':'other.json'})
        with self.assertRaisesRegex(ValueError,'different assembly'):self.run_scene()
        self.put('scene-manifest.json',{'assembly_manifest':'assembly.json','step_models':{}})
        self.report['inputs'].pop('package/fabrication.json');self.save()
        with self.assertRaisesRegex(ValueError,'omits assembly'):self.run_scene()

    def test_faults_and_failed_replay_cannot_pass(self):
        original=copy.deepcopy(self.report)
        for field,value in [('contact_failures',['bad']),('clearance',{'verdict':'FAIL','failures':['collision']}),
                            ('access',[{'verdict':'FAIL'}])]:
            self.report=copy.deepcopy(original);self.report['boards']['board'][field]=value;self.save()
            with self.assertRaisesRegex(ValueError,'failures'):self.run_scene()
        self.report=original;self.save()
        with patch.object(a.subprocess,'run',return_value=SimpleNamespace(returncode=1,stderr='bad geometry',stdout='')):
            with self.assertRaisesRegex(ValueError,'replay failed'):a.scene(self.root,self.binding,'assembly.json',self.spec,self.envelope,{})

    def test_frozen_tool_and_linked_artifact_refused(self):
        self.put('frozen/tools/mechanical_scene.py','# changed')
        with self.assertRaisesRegex(ValueError,'producer inventory'):self.run_scene()
        self.put('frozen/tools/mechanical_scene.py','# synthetic producer; never executed\n')
        path=self.root/'scene/board/twin_top.png';path.unlink();path.symlink_to(self.root/'maker.txt')
        with self.assertRaisesRegex(ValueError,'linked'):self.run_scene()

    def test_exhaustive_independent_model_board_and_limitation_judgments(self):
        result=self.run_scene()
        def verdict(ev):return dict(verdict='PASS',rationale='Synthetic fixture only',evidence=ev)
        required=[result['scene_output']+'/'+n for n in self.report['files']]+['scene/scene.json']
        review=dict(models={'part':verdict(['maker.txt'])},boards={'board':verdict(required)},
            limitations={n:dict(classification='design_resolved',rationale='Synthetic',evidence=['maker.txt']) for n in result['limitations']})
        subjects=dict(result['subjects']);a.judgments(self.root,review,result,self.spec,subjects)
        self.assertIn('maker.txt',subjects)
        for group in ('models','boards','limitations'):
            broken=copy.deepcopy(review);broken[group].pop(next(iter(broken[group])))
            with self.assertRaisesRegex(ValueError,'coverage'):a.judgments(self.root,broken,result,self.spec,{})
        row=next(iter(review['limitations'].values()));row['classification']='outside_mating_scope'
        with self.assertRaisesRegex(ValueError,'mating-only'):a.judgments(self.root,review,result,self.spec,{})

if __name__=='__main__':unittest.main()
