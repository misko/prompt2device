"""Small two-board v2 recipient fixtures; no engineering acceptance is mocked as real."""
import copy
import csv
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import release_evidence as e
import release_review as r
import release_runtime as runtime
import release_seal as seal


class Recipient(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory(prefix='release-v2-');self.addCleanup(tmp.cleanup)
        self.project=Path(tmp.name)/'project';self.project.mkdir()
        self.boards={'main':dict(version='a',quantity=2),'sensor':dict(version='b',quantity=6)}
        self.spec=dict(version=2,release_id='generic-v2',boards=self.boards,runtime='runtime',
                       calculations={b:['math/'+b+'.md'] for b in self.boards},mechanical_basis='Synthetic fixture',
                       handoff='handoff.md',order_policy='policy.json',evidence=['math/main.md'])
        self.package='package';self.views='views'
        self.put('handoff.md','Synthetic only')
        self.policy=dict(holds=[dict(id='physical',reason='Unqualified fixture',closure='Do not manufacture',evidence=['handoff.md'])])
        self.put('policy.json',self.policy)
        models={b+'-model':{} for b in self.boards}
        references={b:{'U1':dict(model=b+'-model')} for b in self.boards}
        self.geometry=dict(boards={b:dict(references=refs) for b,refs in references.items()})
        self.put('views/geometry.json',self.geometry)
        self.put('assembly-spec.json',dict(models=models,boards={b:{} for b in self.boards}))
        self.put('views/assembly.json',dict(version=2,package='package',manifest='assembly-spec.json'))
        self.put('scene-spec.json',{})
        scene=dict(models=models,boards={},files={})
        for board,refs in references.items():
            scene['boards'][board]=dict(references=refs,mounted_references=1,frames={v:{} for v in e.VIEWS},details={})
            names=[board+'-populated.step','board.step','native-dielectric.step']
            names+=['twin_'+v+'.png' for v in e.VIEWS]+['render_'+v+'_bare.png' for v in ('top','bottom')]
            for name in names:
                path='scene/'+board+'/'+name;self.put(path,'fixture artifact '+name)
                scene['files'][board+'/'+name]=r.p.sha(self.project/path)
        self.put('scene/scene.json',scene)
        mechanical=dict(scene_output='scene',scene_manifest='scene-spec.json',subjects={},
                        coverage={b:{'U1':b+'-model'} for b in self.boards},limitations=['fixture-limitation'])
        self.put('views/mechanical.json',mechanical)
        bundle=dict(boards={},files={},schematics=dict(manifest='manifest.json'))
        schemas=dict(boards={});population=[];mapping={}
        for b in self.boards:
            files={b+'/'+b+'.kicad_pcb':'pcb',b+'/'+b+'.kicad_pro':'project',
                   b+'/fp-lib-table':'resources','design/'+b+'.kicad_sch':'schematic',
                   'design/'+b+'/native.xml':'netlist','design/'+b+'.kicad_sym':'symbols'}
            bundle['boards'][b]=dict(native=b+'/'+b+'.kicad_pcb',project=b+'/'+b+'.kicad_pro',resources=['fp-lib-table'])
            schemas['boards'][b]=dict(producer='imported',source=b+'.json',output=b)
            self.put('package/native/design/'+b+'.json',dict(schematic=b+'.kicad_sch',context=[b+'.kicad_sym']))
            for n,text in files.items():
                self.put('package/native/'+n,text);bundle['files'][n]=r.p.sha(self.project/'package/native'/n)
            self.put('math/'+b+'.md','V = I R; fixture calculation only.')
            row=dict(board=b,reference='U1',mode='consigned',manufacturer='Maker, Inc.',mpn='M-1',
                     value='10 µF, 25 V',footprint='Package:Example')
            population.append(row);mapping[b]=dict(placements={'U1':dict(supplier_code='')})
            for mode in ('factory','consigned'):
                bom=[];cpl=[]
                if mode=='consigned':
                    bom=[dict(zip(e.assembly.fab.population.BOM_COLUMNS,
                                  [row['value'],'U1',row['footprint'],'',row['manufacturer'],row['mpn'],1]))]
                    cpl=[dict(zip(e.assembly.fab.population.CPL_COLUMNS,['U1','1mm','-1mm','0','Top']))]
                self.csv('package/assembly/'+b+'-'+mode+'-bom.csv',e.assembly.fab.population.BOM_COLUMNS,bom)
                self.csv('package/assembly/'+b+'-'+mode+'-cpl.csv',e.assembly.fab.population.CPL_COLUMNS,cpl)
        self.csv('package/assembly/population.csv',list(population[0]),population)
        self.put('population-spec.json',dict(assembly=dict(boards=mapping),
                 boards={b:dict(population={'U1':dict(mode='consigned')}) for b in self.boards}))
        self.put('instructions.md','Synthetic manufacturing instructions')
        self.put('package/inputs/instructions.md','Synthetic manufacturing instructions')
        self.put('fab-spec.json',dict(population='population-spec.json',boards={b:dict(
            instructions=['instructions.md'],mechanical_views=['instructions.md'],
            process=dict(evidence=['instructions.md'])) for b in self.boards}))
        self.put('package/fabrication.json',dict(manifest='fab-spec.json',
                 files={'inputs/instructions.md':r.p.sha(self.project/'instructions.md')}))
        self.put('package/native/bundle.json',bundle);self.put('package/native/design/manifest.json',schemas)
        subjects={p.relative_to(self.project).as_posix():r.p.sha(p) for p in self.project.rglob('*') if p.is_file()}
        self.put(r.assembly.RECEIPT,dict(subjects=subjects))
        venv=self.project.parent/'venv';(venv/'bin').mkdir(parents=True)
        (venv/'bin/python').symlink_to(Path(sys.executable).resolve())
        (venv/'pyvenv.cfg').write_text('home = /usr/bin\ninclude-system-site-packages = true\n')
        base=venv/('lib/python%d.%d/site-packages' % sys.version_info[:2]);base.mkdir(parents=True)
        modules=['cadquery','OCP','vtkmodules','numpy']
        for name in modules:(base/(name+'.py')).write_text('# synthetic fixture only\n')
        runtime.build(venv,self.project/'runtime',modules)

    def put(self,name,obj):
        file=self.project/name;file.parent.mkdir(parents=True,exist_ok=True)
        file.write_text(r.dump(obj) if isinstance(obj,dict) else obj)

    def csv(self,name,headers,rows):
        text=io.StringIO(newline='');writer=csv.DictWriter(text,fieldnames=headers)
        writer.writeheader();writer.writerows(rows);self.put(name,text.getvalue())

    def describe(self):return e.describe(self.project,self.spec,self.package,self.views)

    def test_actual_roles_derive_from_small_two_board_fixture(self):
        result=self.describe()
        self.assertEqual(result['models'],['main-model','sensor-model'])
        self.assertEqual(len(result['artifacts']),22)
        self.assertEqual(result['bom']['main-factory']['references'],[])
        self.assertEqual(result['bom']['main-consigned']['references'],['U1'])
        self.assertIn('schematic',result['native']['sensor']['roles'])

    def test_each_mechanical_artifact_is_required(self):
        report=r.p.read(self.project/'scene/scene.json')
        for name in report['files']:
            file=self.project/'scene'/name;data=file.read_bytes();file.unlink()
            with self.subTest(name=name),self.assertRaises(ValueError):self.describe()
            file.write_bytes(data)
        report['files'].pop('main/twin_top.png');self.put('scene/scene.json',report)
        with self.assertRaisesRegex(ValueError,'roles missing'):self.describe()

    def test_model_reference_and_scene_identity_fail_closed(self):
        original=r.p.read(self.project/'scene/scene.json')
        for change in (lambda d:d['models'].pop('main-model'),
                       lambda d:d['boards']['sensor']['references'].clear(),
                       lambda d:d['boards']['main'].update(mounted_references=0),
                       lambda d:d['boards']['main']['frames'].pop('top')):
            report=copy.deepcopy(original);change(report);self.put('scene/scene.json',report)
            with self.assertRaises(ValueError):self.describe()
        self.put('scene/scene.json',original);mechanical=r.p.read(self.project/'views/mechanical.json')
        mechanical['coverage']['main']['U1']='sensor-model';self.put('views/mechanical.json',mechanical)
        with self.assertRaises(ValueError):self.describe()

    def test_native_math_and_runtime_omissions(self):
        for name in ('package/native/main/main.kicad_pcb','package/native/design/sensor.kicad_sch',
                     'math/main.md','runtime/runtime.json','runtime/site-packages.tar.gz'):
            file=self.project/name;data=file.read_bytes();file.unlink()
            with self.subTest(name=name),self.assertRaises((ValueError,OSError)):self.describe()
            file.write_bytes(data)
        self.spec['calculations']['main']=[]
        with self.assertRaisesRegex(ValueError,'calculations required'):self.describe()

    def test_csv_bytes_quoting_identity_supplier_and_population(self):
        file=self.project/'package/assembly/main-consigned-bom.csv';original=file.read_bytes()
        for data in (b'\xff',b'bad,header\n',original.replace(b'M-1',b'WRONG'),
                     original.replace(b'"Maker, Inc."',b'"Maker, Inc.'),
                     original.replace(b'U1',b'U2'),original.replace(b'Example,,',b'Example,C123,')):
            file.write_bytes(data)
            with self.subTest(data=data[:20]),self.assertRaises((ValueError,UnicodeError,csv.Error)):self.describe()
        file.write_bytes(original);self.assertEqual(self.describe()['bom']['main-consigned']['bom_rows'],1)

    def test_population_cannot_hide_unknown_or_phantom_excluded_refs(self):
        file=self.project/'package/assembly/population.csv';original=file.read_text()
        for mode in ('unrecognized-mode','mechanical','dnp'):
            rows=e.csv_rows(file)
            rows.append(dict(rows[0],reference='PHANTOM',mode=mode))
            self.csv('package/assembly/population.csv',list(rows[0]),rows)
            with self.subTest(mode=mode),self.assertRaisesRegex(ValueError,'policy/reference'):self.describe()
            file.write_text(original)

    def archive(self):
        recipient=self.describe();aliases=recipient['aliases']|{'HANDOFF.md':'source/project/handoff.md'}
        origins={'source/project/'+p.relative_to(self.project).as_posix():dict(origin='project',
                 path=p.relative_to(self.project).as_posix(),sha256=r.p.sha(p))
                 for p in self.project.rglob('*') if p.is_file()}
        with patch.object(r,'inputs',return_value=(self.spec,self.policy,origins,self.package,self.views)),\
             patch.object(r,'presentation',return_value=aliases):
            r.build(self.project,'manifest.json','output')
        return self.project/'output'

    def test_candidate_status_and_inventory(self):
        archive=self.archive();record=r.inventory_check(archive)
        self.assertEqual(record['version'],2);self.assertEqual(record['design_status'],'UNREVIEWED')
        index=archive/'INDEX.md';index.write_text(index.read_text().replace('UNREVIEWED','SOUND'))
        record['files']=r.census(archive,{'release.json'});(archive/'release.json').write_text(r.dump(record))
        with self.assertRaisesRegex(ValueError,'status/index'):r.inventory_check(archive)

    def test_v2_focused_lenses_have_independent_owners(self):
        review=dict(author='author',lenses={name:dict(reviewer=name,checks=sorted(checks))
                                          for name,checks in e.LENSES.items()})
        e.lenses(review);review['lenses']['integrated']['reviewer']='author'
        with self.assertRaises(ValueError):e.lenses(review)
        review['lenses']['integrated']['reviewer']='layout_power'
        with self.assertRaises(ValueError):e.lenses(review)

    def test_v2_admission_requires_each_derived_scope_and_independent_lens(self):
        archive=self.archive();record=r.p.read(archive/'release.json')
        self.put('output/mechanical/geometry.json',self.geometry)
        # verify is mocked ONLY to exercise admission validation, not owner checks.
        subjects={'output/'+n:d for n,d in r.census(archive).items()}
        units=dict(pin_identity=['main/U1','sensor/U1'],readability=sorted(self.boards),
                   electrical=sorted(self.boards),layout_power=sorted(self.boards),
                   completeness=e.completeness(record),order_readiness=['physical'],**e.units(record))
        review=dict(schema=1,stage='PCB-RELEASE-REVIEW',author='author',reviewer='integrated',
                    manifest='manifest.json',output='output',design_verdict='SOUND',order_verdict='DO-NOT-ORDER',
                    subjects=subjects,lenses={n:dict(reviewer=n,checks=sorted(c)) for n,c in e.LENSES.items()},
                    checks={k:dict(verdict='PASS',rationale='Synthetic scope only',evidence=['output/release.json'],
                                   coverage=dict(required=u,reviewed=u,findings=[])) for k,u in units.items()})
        def certificate(obj):
            name='08_reviews/2026-10-10-test.md'
            self.put(name,'```json\n'+r.dump(obj)+'```\n')
            with patch.object(r,'verify',return_value=dict(subjects=subjects)):
                return r.certificate(self.project,name)
        self.assertIn('release_runtime.py',certificate(review)['tools'])
        for key in ('mechanical','bom_identity','completeness'):
            changed=copy.deepcopy(review);changed['checks'][key]['coverage']['reviewed'].pop()
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'ungraded'):certificate(changed)
        changed=copy.deepcopy(review);changed['lenses'].pop('visual_mechanical')
        with self.assertRaisesRegex(ValueError,'lenses missing'):certificate(changed)

    def test_seal_reconstruction_has_one_current_status_and_preserves_candidate(self):
        archive=self.archive();record=r.p.read(archive/'release.json')
        repo=self.project.parent/'repo';repo.mkdir()
        for name in record['origins']:
            target=repo/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(archive/name,target)
        (repo/'inputs').mkdir()
        for src,dest in [('release.json','archive-record.json'),('INDEX.md','archive-index.md'),
                         ('ORDER-INSTRUCTIONS.md','order-instructions.md')]:shutil.copyfile(archive/src,repo/'inputs'/dest)
        receipt=dict(design_verdict='SOUND',order_verdict='DO-NOT-ORDER')
        (repo/'inputs/release_reviewed.json').write_text(r.dump(receipt))
        (repo/'inputs/release-review.md').write_text('Synthetic receipt; owner mocked only in this unit test')
        dest=self.project.parent/'sealed'
        with patch.object(seal,'archive_check'):
            seal.construct(repo,dest)
        status=seal.read(dest/'CURRENT-STATUS.json')
        self.assertEqual(status['design_verdict'],'SOUND')
        self.assertEqual(status['candidate_sha256'],seal.sha(dest/'archive/release.json'))
        self.assertEqual(seal.read(dest/'archive/release.json')['design_status'],'UNREVIEWED')
        self.assertEqual(r.census(archive),r.census(dest/'archive'))
        self.assertIn('archive/source/project/package/native/main/main.kicad_pcb',(dest/'INDEX.md').read_text())


if __name__=='__main__':unittest.main()
