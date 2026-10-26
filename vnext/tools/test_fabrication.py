"""Isolated fabrication-stage regressions, never Crow or manufacturer acceptance.

The package is built from real KiCad native/schematic replay. Supplied stock,
geometry, process and review evidence below are explicitly synthetic.
"""
import copy
import csv
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import fabrication as fab
import test_fab_replay as replay_fixture


class Fabrication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = replay_fixture.Native()
        cls.seed.setUp()
        cls.addClassCleanup(cls.seed.doCleanups)
        root = cls.seed.root
        cls.root_fixture = root

        # The routing fixture has one connected net and strict KiCad settings.
        # Add exact ordering fields to its PCB, then author the matching flat
        # schematic and intent from one trusted local producer.
        cls.fields = {
            'U1': {'Manufacturer': 'FixtureMaker', 'MPN': 'Fixture-1',
                   'Assembly': 'SMT', 'Supplier': 'C123'},
            'U2': {'Manufacturer': 'FixtureMaker', 'MPN': 'Fixture-2',
                   'Assembly': 'SMT', 'Supplier': 'C456'},
        }
        native = root/'source.kicad_pcb'
        settings = native.with_suffix('.kicad_pro').read_bytes()
        board = fab.p.pcb.LoadBoard(str(native))
        board.FindNet('N').SetNetname('/N')  # Native local-label namespace.
        for fp in board.GetFootprints():
            for key, value in cls.fields[fp.GetReference()].items():
                field = fab.p.pcb.PCB_FIELD(fp, fab.p.pcb.FIELD_T_USER, key)
                field.SetText(value)
                field.SetVisible(False)
                fp.Add(field)
        fab.p.pcb.SaveBoard(str(native), board)
        # KiCad materializes defaults for added user fields on the next load.
        fab.p.pcb.SaveBoard(str(native), fab.p.pcb.LoadBoard(str(native)))
        native.with_suffix('.kicad_pro').write_bytes(settings)

        model = dict(version=1, title='Synthetic fabrication replay', nets=['N'],
                     components=[dict(ref=ref, value='Pad', footprint='Test:Pad',
                        expected_pins=['1'], at=[x,25.4],
                        pins=[dict(number='1', name='P', type='passive',
                                   at=[0,0], direction=180, net='N')])
                        for ref,x in [('U1',25.4),('U2',50.8)]],
                     wire_paths=[dict(net='N', points=[[25.4,25.4],[50.8,25.4]])])
        cls.seed.write('circuit/model.json', json.dumps(model))
        cls.seed.write('circuit/fields.json', json.dumps(cls.fields))
        shutil.copyfile(Path(fab.replay.imported.native.__file__), root/'circuit/core.py')
        cls.seed.write('circuit/author.py', '''from pathlib import Path
import json
import core
here=Path(__file__).parent
model=json.loads((here/'model.json').read_text())
fields=json.loads((here/'fields.json').read_text())
core.check(model)
lines=core.render(model,'test').splitlines()
rendered=[]
for line in lines:
    rendered.append(line)
    if line.startswith('(symbol (lib_id '):
        ref=line.split('"')[1].split(':')[1]
        for name,value in fields[ref].items():
            rendered.append('(property '+json.dumps(name)+' '+json.dumps(value)+
                ' (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
(here/'test.kicad_sch').write_text('\\n'.join(rendered)+'\\n')
(here/'test.kicad_pro').write_text('{}\\n')
intent=dict(version=1,nets=model['nets'],components=[
    dict(ref=c['ref'],value=c['value'],footprint=c['footprint'],physical=True,
         fields=fields[c['ref']],pins=[{k:v for k,v in pin.items()
             if k not in ('at','direction')} for pin in c['pins']])
    for c in model['components']])
(here/'intent.json').write_text(json.dumps(intent,sort_keys=True)+'\\n')
''')
        fab.p.command(['/usr/bin/python3', str(root/'circuit/author.py')])
        declaration = dict(version=1, producer=dict(entrypoint='circuit/author.py',
            inputs=['circuit/author.py','circuit/core.py','circuit/model.json','circuit/fields.json']),
            intent='circuit/intent.json', schematic='circuit/test.kicad_sch',
            context=['circuit/test.kicad_pro'])
        cls.seed.write('import.json', json.dumps(declaration))
        membership = dict(version=1, nets=['N'], components={ref:dict(
            value='Pad', footprint='Test:Pad', physical=True, pins=['1'])
            for ref in cls.fields})
        cls.seed.write('membership.json', json.dumps(membership))
        cls.seed.write('assembly.json', json.dumps(dict(version=1,
            instances={'carrier1':'carrier','pod1':'pod'}, boards={key:dict(
                producer='imported', source='import.json', membership='membership.json',
                output='exports/'+key) for key in ('carrier','pod')})))
        cls.seed.write('expected.json', json.dumps(dict(version=1,
            instances={'carrier1':'carrier','pod1':'pod'})))
        cls.schematics = {'manifest':'assembly.json','expected':'expected.json'}
        cls.boards = {key:copy.deepcopy(cls.seed.boards['test'])
                      for key in ('carrier','pod')}

        for name, content in {
            'evidence/geometry.txt':'SYNTHETIC centroid and orientation declaration; not validated manufacturer geometry.',
            'evidence/population.txt':'SYNTHETIC per-reference placement and manual/DNP policy.',
            'evidence/manual.txt':'SYNTHETIC manual placement, polarity check and inspection instruction.',
            'evidence/process.txt':'SYNTHETIC process selections; actual uploader confirmation remains a hold.',
            'evidence/mechanical.txt':'SYNTHETIC 2D mechanical view and dimension check.',
            'evidence/handoff.txt':'SYNTHETIC handoff and independent review to follow.',
            'evidence/stock.txt':'SYNTHETIC exact offer observation; not live stock or allocation.',
        }.items(): cls.seed.write(name, content)
        cls.source_sha = fab.p.sha(native)
        pop = cls.population_manifest()
        cls.seed.write('population.json', json.dumps(pop))
        facts = cls.stock_facts(pop)
        cls.seed.write('stock.json', json.dumps(facts))
        cls.seed.write('fabrication-manifest.json', json.dumps(cls.fabrication_manifest()))
        cls.record = fab.produce(root, cls.boards, cls.schematics,
                                 'fabrication-manifest.json', root/'fabrication-package')

    @classmethod
    def population_manifest(cls):
        rows = {}
        for key, quantity in [('carrier',5),('pod',40)]:
            modes = {'U1':'factory','U2':'manual' if key == 'carrier' else 'consigned'}
            rows[key] = dict(source='source.kicad_pcb', intent='circuit/intent.json',
                quantity=quantity, population={ref:dict(mode=mode,
                    reason='Synthetic disposition only',
                    evidence=['evidence/manual.txt' if mode == 'manual' else 'evidence/population.txt'])
                    for ref,mode in modes.items()})
        mapping = {}
        for key, row in rows.items():
            placements = {}
            for ref, policy in row['population'].items():
                if policy['mode'] not in ('factory','consigned'): continue
                fields = cls.fields[ref]
                placements[ref] = dict(manufacturer=fields['Manufacturer'], mpn=fields['MPN'],
                    footprint='Test:Pad', supplier_code=fields['Supplier'],
                    centroid_offset_mm=[0.1,-0.2], rotation_deg=15 if ref=='U1' else 195,
                    evidence=['evidence/geometry.txt'])
            mapping[key] = dict(source_sha256=cls.source_sha, placements=placements)
        return dict(version=1, boards=rows, assembly=dict(version=1,boards=mapping))

    @classmethod
    def stock_facts(cls, pop, *, counts=None):
        counts = counts or {'Fixture-1':45,'Fixture-2':45}
        return dict(version=1, as_of='2026-10-06', parts=[dict(
            manufacturer='FixtureMaker', mpn=mpn, package='Test:Pad',
            quantity=45, contributors=[{'board':key,'reference':ref}
                for key,row in pop['boards'].items() for ref,policy in row['population'].items()
                if cls.fields[ref]['MPN']==mpn and policy['mode']!='dnp'],
            jlc_evidence=['evidence/stock.txt'], offers=[dict(
                manufacturer='FixtureMaker',mpn=mpn,package='Test:Pad',
                supplier_url='https://example.invalid/'+mpn, checked_on='2026-10-06',
                in_stock=True,stock_count=counts[mpn],evidence=['evidence/stock.txt'])])
            for mpn in ('Fixture-1','Fixture-2')])

    @classmethod
    def fabrication_manifest(cls):
        board = fab.p.pcb.LoadBoard(str(cls.root_fixture/'source.kicad_pcb'))
        process = dict(copper_layers=board.GetCopperLayerCount(),
            thickness_mm=board.GetDesignSettings().GetBoardThickness()/1e6,
            selections={'finish':'synthetic HASL','mask':'synthetic green'},
            evidence=['evidence/process.txt'])
        return dict(version=1,population='population.json',sourcing='stock.json',
            boards={key:dict(source_sha256=cls.source_sha,process=process,
                mechanical_views=['evidence/mechanical.txt'],
                instructions=['evidence/manual.txt']) for key in ('carrier','pod')},
            handoff=['evidence/handoff.txt'],order_holds=[dict(id='uploader',
                reason='Actual uploader choices unconfirmed', evidence=['evidence/process.txt'])])

    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='vnext-fabrication-case-')
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)/'package'
        shutil.copytree(self.root_fixture/'fabrication-package',self.root)

    def rehash(self):
        record=json.loads((self.root/'fabrication.json').read_text())
        record['files']=fab.inventory(self.root)
        (self.root/'fabrication.json').write_text(json.dumps(record))

    def test_complete_portable_replay_and_exact_mixed_quantities(self):
        run=subprocess.run(['/usr/bin/python3',str(self.root/'tools/fabrication.py'),
            'replay','--package',str(self.root)],cwd='/tmp',text=True,capture_output=True,timeout=180)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        result=json.loads(run.stdout)
        self.assertEqual(result['boards'],['carrier','pod'])
        self.assertFalse(result['accepted']);self.assertEqual(result['order_status'],'DO-NOT-ORDER')
        demand={row['mpn']:row['quantity'] for row in result['sourcing']['demand']}
        self.assertEqual(demand,{'Fixture-1':45,'Fixture-2':45})
        self.assertEqual(self.record['order_holds'][-1]['id'],'uploader')
        assembly=self.root/'assembly'
        self.assertTrue((assembly/'carrier-factory-bom.csv').is_file())
        self.assertTrue((assembly/'pod-consigned-cpl.csv').is_file())
        with (assembly/'carrier-factory-bom.csv').open(newline='') as f:
            self.assertEqual(list(csv.DictReader(f))[0]['Quantity'],'1')
        with (assembly/'pod-consigned-cpl.csv').open(newline='') as f:
            self.assertEqual(list(csv.DictReader(f))[0]['Designator'],'U2')
        self.assertIn('U2,manual', (assembly/'population.csv').read_text())

    def test_missing_corrupt_linked_and_rehashed_native_fail(self):
        path=self.root/'inputs/evidence/manual.txt';path.unlink()
        with self.assertRaises(ValueError):fab.verify_package(self.root)
        shutil.copyfile(self.root_fixture/'fabrication-package/inputs/evidence/manual.txt',path)
        native=self.root/'native/source/carrier/carrier.kicad_pcb'
        native.write_bytes(native.read_bytes()+b'\n')
        self.rehash()
        with self.assertRaises(ValueError):fab.verify_package(self.root)
        native.unlink();native.symlink_to(self.root_fixture/'source.kicad_pcb')
        with self.assertRaisesRegex(ValueError,'linked'):fab.verify_package(self.root)

    def test_stale_source_mapping_and_policy_are_refused(self):
        inputs=self.root/'inputs';pop=json.loads((inputs/'population.json').read_text())
        pop['assembly']['boards']['pod']['source_sha256']='0'*64
        (inputs/'population.json').write_text(json.dumps(pop))
        self.rehash()
        with self.assertRaisesRegex(ValueError,'stale assembly source'):fab.verify_package(self.root)

    def test_rehashed_native_intent_and_derivative_corruption_fail(self):
        intent=self.root/'inputs/circuit/intent.json'
        data=json.loads(intent.read_text());data['components'][0]['fields']['MPN']='Wrong'
        intent.write_text(json.dumps(data));self.rehash()
        with self.assertRaisesRegex(ValueError,'native/intent'):fab.verify_package(self.root)
        shutil.copyfile(self.root_fixture/'fabrication-package/inputs/circuit/intent.json',intent)
        pdf=self.root/'native/fab/carrier/pdf/assembly-top.pdf'
        pdf.write_bytes(pdf.read_bytes()+b'\n');self.rehash()
        with self.assertRaises(ValueError):fab.verify_package(self.root)
        shutil.copyfile(self.root_fixture/'fabrication-package/native/fab/carrier/pdf/assembly-top.pdf',pdf)
        csv_path=self.root/'assembly/carrier-factory-cpl.csv'
        csv_path.write_text(csv_path.read_text().replace('15.000000','16.000000'))
        self.rehash()
        with self.assertRaises(ValueError):fab.verify_package(self.root)

    def test_missing_producer_extra_root_and_stale_context_fail(self):
        producer=self.root/'native/design/circuit/author.py';producer.unlink();self.rehash()
        with self.assertRaises(ValueError):fab.verify_package(self.root)
        shutil.copyfile(self.root_fixture/'fabrication-package/native/design/circuit/author.py',producer)
        (self.root/'unexpected.txt').write_text('unclaimed')
        self.rehash()
        with self.assertRaisesRegex(ValueError,'root census'):fab.verify_package(self.root)
        (self.root/'unexpected.txt').unlink()
        record=json.loads((self.root/'fabrication.json').read_text())
        record['context']={'fabrication-contract.json':'0'*64}
        (self.root/'fabrication.json').write_text(json.dumps(record))
        with self.assertRaises(ValueError):fab.verify_package(self.root)

    def test_manual_and_dnp_policy_is_accounted_not_machine_placed(self):
        pop=self.population_manifest()
        pop['boards']['pod']['population']['U2']['mode']='dnp'
        del pop['assembly']['boards']['pod']['placements']['U2']
        result=fab.population.data(self.root_fixture,pop)
        self.assertEqual({x['mpn']:x['quantity'] for x in result['demand']},
                         {'Fixture-1':45,'Fixture-2':5})
        files=fab.population.assembly_files(self.root_fixture,pop,result)
        self.assertEqual(len(files['pod-consigned-cpl.csv'].splitlines()),1)
        self.assertEqual(len(files['pod-consigned-bom.csv'].splitlines()),1)
        self.assertFalse(any(x['reference']=='U2' and x['board']=='pod'
                             for x in result['positions']))

    def test_stock_adequate_insufficient_unknown_and_contributors(self):
        pop=self.population_manifest()
        rows=fab.population.data(self.root_fixture,pop)['population']
        facts=self.stock_facts(pop)
        # Do not mutate the shared fixture: stock() reads package-copied files.
        case=self.root/'inputs/stock.json'
        subjects={}
        self.assertEqual({x['mpn']:x['quantity'] for x in fab.stock(
            self.root/'inputs','stock.json',rows,subjects)['demand']},
            {'Fixture-1':45,'Fixture-2':45})
        facts['parts'][0]['offers'][0]['stock_count']=44
        case.write_text(json.dumps(facts))
        with self.assertRaisesRegex(ValueError,'no adequate exact offer'):fab.stock(
            self.root/'inputs','stock.json',rows,{})
        facts['parts'][0]['offers'][0]['stock_count']=None
        case.write_text(json.dumps(facts))
        self.assertEqual(len(fab.stock(self.root/'inputs','stock.json',rows,{})['demand']),2)
        facts['parts'][0]['offers'][0]['in_stock']=False
        case.write_text(json.dumps(facts))
        with self.assertRaisesRegex(ValueError,'no adequate exact offer'):fab.stock(
            self.root/'inputs','stock.json',rows,{})
        facts=self.stock_facts(pop);facts['parts'][0]['contributors']=[]
        case.write_text(json.dumps(facts))
        with self.assertRaisesRegex(ValueError,'contributors differ'):fab.stock(
            self.root/'inputs','stock.json',rows,{})
        facts=self.stock_facts(pop);facts['parts'][0]['quantity']=44
        case.write_text(json.dumps(facts))
        with self.assertRaisesRegex(ValueError,'quantity differs'):fab.stock(
            self.root/'inputs','stock.json',rows,{})
        facts=self.stock_facts(pop);facts['as_of']='2999-01-01'
        case.write_text(json.dumps(facts))
        with self.assertRaisesRegex(ValueError,'future'):fab.stock(
            self.root/'inputs','stock.json',rows,{})
        for key,value,error in (
            ('availability_verified',False,'no adequate exact offer'),
            ('availability_verified','false','must be boolean'),
            ('lookup_state','unverified','no adequate exact offer'),
            ('lookup_state','unknown','unknown stock lookup state'),
            ('lookup_state','exact_matches','no adequate exact offer'),
            ('evidence_kind','search_snippet','no adequate exact offer')):
            facts=self.stock_facts(pop)
            facts['parts'][0]['offers'][0][key]=value
            case.write_text(json.dumps(facts))
            with self.assertRaisesRegex(ValueError,error):fab.stock(
                self.root/'inputs','stock.json',rows,{})
        facts=self.stock_facts(pop)
        facts['parts'][0]['offers'][0].update(
            availability_verified=True,lookup_state='verified',source_kind='supplier_page')
        case.write_text(json.dumps(facts))
        self.assertEqual(len(fab.stock(self.root/'inputs','stock.json',rows,{})['demand']),2)

    def test_policy_missing_manual_process_and_mechanical_evidence_fail(self):
        inputs=self.root/'inputs';manifest=json.loads((inputs/'fabrication-manifest.json').read_text())
        manifest['boards']['carrier']['process']['copper_layers']=4
        with self.assertRaisesRegex(ValueError,'copper layer'):fab.policy(inputs,manifest)
        manifest=self.fabrication_manifest()
        manifest['boards']['pod']['mechanical_views']=[]
        with self.assertRaisesRegex(ValueError,'evidence list'):fab.policy(inputs,manifest)
        manifest=self.fabrication_manifest()
        manifest['boards']['pod']['instructions']=[]
        with self.assertRaisesRegex(ValueError,'evidence list'):fab.policy(inputs,manifest)
        pop=json.loads((inputs/'population.json').read_text())
        pop['boards']['carrier']['population']['U2']['evidence']=[]
        (inputs/'population.json').write_text(json.dumps(pop))
        with self.assertRaisesRegex(ValueError,'population evidence'):fab.policy(inputs,manifest)

    def test_upstream_owner_check_is_invoked_isolated_sentinel(self):
        # This patches the owner to throw, never to simulate an accepted layout.
        project=self.root
        authority=project/'authority.txt';authority.write_text('synthetic authority only')
        receipt=project/fab.seal.RECEIPT
        receipt.parent.mkdir(parents=True);receipt.write_text('synthetic, not accepted')
        contract=project/fab.CONTRACT;contract.parent.mkdir(parents=True,exist_ok=True)
        contract.write_text(json.dumps(dict(version=1,authority='authority.txt',
            authority_sha256=fab.p.sha(authority),layout_receipt_sha256=fab.p.sha(receipt),
            board_quantities={'carrier':5,'pod':40})))
        authority.write_text('changed synthetic authority')
        with self.assertRaisesRegex(ValueError,'authority changed'):fab.upstream(project)
        authority.write_text('synthetic authority only')
        receipt.write_text('changed synthetic receipt')
        with self.assertRaisesRegex(ValueError,'layout receipt changed'):fab.upstream(project)
        receipt.write_text('synthetic, not accepted')
        with patch.object(fab.seal,'check',side_effect=ValueError('owner-check-sentinel')) as owner:
            with self.assertRaisesRegex(ValueError,'owner-check-sentinel'):
                fab.build(project,'fabrication-manifest.json','never-publish')
            owner.assert_called_once_with(project)
        self.assertFalse((project/'never-publish').exists())

    def test_definition_only_graph_refuses_receipt_even_with_review(self):
        original_read=fab.p.read
        def definition_only(path):
            value=original_read(path)
            if Path(path)==fab.p.ROOT/'skills/pcb-design/workflow/graph.json':
                value=copy.deepcopy(value)
                stage=next(s for s in value['stages']
                           if s['spec']['id']=='JLC-FABRICATION')
                stage.pop('local_execution',None)
                stage['local_definition']={'contract':fab.STAGE,'status':'definition_only'}
            return value
        with patch.object(fab.p,'read',side_effect=definition_only):
            with self.assertRaisesRegex(ValueError,'not adopted'):
                fab.certificate(self.root_fixture,'synthetic-review.json')

    def test_review_helper_isolated_not_a_stage_receipt(self):
        manifest=self.fabrication_manifest()
        required={'evidence/process.txt':fab.p.sha(self.root_fixture/'evidence/process.txt')}
        review=dict(schema=1,stage='JLC-FABRICATION',verdict='PASS',author='author',
            reviewer='author',subjects=required,checks={})
        with self.assertRaisesRegex(ValueError,'independent reviewer'):
            fab.validate_review(self.root_fixture,review,required,manifest)
        review['reviewer']='independent';review['checks']={name:dict(verdict='PASS',
            rationale='Synthetic unit case',evidence=['evidence/process.txt'])
            for name in fab.CRITERIA}
        with self.assertRaisesRegex(ValueError,'omits'):
            fab.validate_review(self.root_fixture,review,required,manifest)

    def test_isolated_certificate_issue_check_and_exclusive_receipt(self):
        # Only this unit test substitutes the upstream verify verdict. All
        # subject files are synthetic; this cannot certify Crow or production.
        project=self.root.parent/'synthetic-project'
        shutil.copytree(self.root_fixture,project)
        output='fabrication-package'
        citations={
            'source':[f'{output}/fabrication.json',f'{output}/native/bundle.json']+[
                f'{output}/native/design/exports/{key}/{name}'
                for key in ('carrier','pod') for name in ('native.pdf','receipt.json')]+[
                f'{output}/native/fab/{key}/{key}-gerbers.zip'
                for key in ('carrier','pod')]+[
                f'{output}/native/fab/{key}/pdf/{name}'
                for key in ('carrier','pod') for name in fab.replay.PDF_NAMES],
            'population':[f'{output}/assembly/{n}' for n in sorted(
                x.name for x in (project/output/'assembly').iterdir() if x.suffix=='.csv')]
                +['evidence/population.txt','evidence/manual.txt','evidence/geometry.txt'],
            'sourcing':['stock.json','evidence/stock.txt'],
            'process':['evidence/process.txt'],
            'mechanical':['evidence/mechanical.txt'],
            'instructions':['evidence/manual.txt','evidence/population.txt'],
            'handoff':['evidence/handoff.txt','evidence/process.txt'],
        }
        names={name for group in citations.values() for name in group}
        subjects={name:fab.p.sha(project/name) for name in names}
        review=dict(schema=1,stage='JLC-FABRICATION',verdict='PASS',
            author='synthetic author',reviewer='synthetic reviewer',
            manifest='fabrication-manifest.json',output=output,subjects=subjects,
            checks={key:dict(verdict='PASS',rationale='Synthetic unit disposition only',
                             evidence=values) for key,values in citations.items()})
        (project/'synthetic-review.json').write_text(json.dumps(review))
        # The graph may still be definition-only during parallel integration;
        # substitute its binding here solely to exercise receipt mechanics.
        original_read=fab.p.read
        def synthetic_graph_read(path):
            value=original_read(path)
            if Path(path)==fab.p.ROOT/'skills/pcb-design/workflow/graph.json':
                value=copy.deepcopy(value)
                stage=next(s for s in value['stages']
                           if s['spec']['id']=='JLC-FABRICATION')
                stage.pop('local_definition',None)
                stage['local_execution']=dict(tool='tools/fabrication.py',
                    contract=fab.STAGE,status='pilot_under_validation')
            return value
        with patch.object(fab,'verify',return_value={'subjects':subjects}) as isolated, \
             patch.object(fab.seal.r,'review_json',return_value=review), \
             patch.object(fab.p,'read',side_effect=synthetic_graph_read):
            result=fab.certificate(project,'synthetic-review.json')
            isolated.assert_called_once_with(project,'fabrication-manifest.json',output)
            self.assertEqual(result['role'],'fabrication_staged')
            self.assertEqual(result['order_status'],'DO-NOT-ORDER')
            receipt=project/fab.RECEIPT
            with patch.object(fab,'certificate',return_value=result), \
                 patch.object(sys,'argv',['fabrication.py','issue','--project',str(project),
                     '--review','synthetic-review.json']), \
                 redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(fab.main(),0)
                self.assertEqual(fab.main(),1)
            self.assertEqual(json.loads(receipt.read_text()),result)
            with patch.object(fab,'certificate',return_value=result):
                self.assertEqual(fab.check(project),result)
            altered=copy.deepcopy(result);altered['order_status']='WRONG'
            with patch.object(fab,'certificate',return_value=altered):
                with self.assertRaisesRegex(ValueError,'stale fabrication receipt'):
                    fab.check(project)

    def test_joined_public_path_with_only_layout_owner_mocked(self):
        # Root-added integration coverage after SOL's interrupted pass. Every new
        # fabrication predicate is real; ONLY the established layout owner verdict
        # is synthetic. This is explicitly not an accepted board or live run.
        project=self.root.parent/'public-fixture'
        shutil.copytree(self.root_fixture,project)
        write=lambda name,value: (project/name).write_text(json.dumps(value))
        output='public-package';pop=self.population_manifest()
        for key,row in self.boards.items():
            base=project/'layout-output'/key/'native';base.mkdir(parents=True)
            shutil.copyfile(project/row['source'],base/(key+'.kicad_pcb'))
            shutil.copyfile(project/row['project'],base/(key+'.kicad_pro'))
            for name,source in row['resources'].items():
                target=base/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(project/source,target)
            pop['boards'][key]['source']=f'layout-output/{key}/native/{key}.kicad_pcb'
        write('population.json',pop)
        write('layout-manifest.json',{'boards':self.boards})
        (project/'08_reviews').mkdir(exist_ok=True)
        layout_review='08_reviews/2026-10-06-layout.md'
        (project/layout_review).write_text('```json\n'+json.dumps(
            {'manifest':'layout-manifest.json','output':'layout-output'})+'\n```\n')
        (project/'authority.txt').write_text('SYNTHETIC local staging authority; no real acceptance.')
        seal_receipt=project/fab.seal.RECEIPT
        seal_receipt.parent.mkdir(parents=True,exist_ok=True)
        write(fab.seal.RECEIPT,{'review':layout_review})
        (project/'01_docs').mkdir(exist_ok=True)
        write(fab.CONTRACT,dict(version=1,authority='authority.txt',
            authority_sha256=fab.p.sha(project/'authority.txt'),
            layout_receipt_sha256=fab.p.sha(seal_receipt),board_quantities={'carrier':5,'pod':40}))
        write('01_docs/schematic-contract.json',self.schematics)
        with patch.object(fab.seal,'check',return_value={'review':layout_review}) as owner:
            fab.build(project,'fabrication-manifest.json',output)
            result=fab.verify(project,'fabrication-manifest.json',output)
            self.assertFalse(result['accepted'])
            # Synthetic review deliberately cites every graded subject; unlike the
            # older receipt unit test, the complete subject census comes from the
            # actual new verifier, not a mocked verification result.
            names=sorted(result['subjects'])
            review=dict(schema=1,stage='JLC-FABRICATION',verdict='PASS',
                author='synthetic author',reviewer='synthetic reviewer',
                manifest='fabrication-manifest.json',output=output,subjects=result['subjects'],
                checks={k:dict(verdict='PASS',rationale='Synthetic integration coverage only',
                                evidence=names) for k in fab.CRITERIA})
            review_name='08_reviews/2026-10-06-fabrication.md'
            (project/review_name).write_text('```json\n'+json.dumps(review)+'\n```\n')
            argv=['fabrication.py','issue','--project',str(project),'--review',review_name]
            with patch.object(sys,'argv',argv),redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                self.assertEqual(fab.main(),0)
            receipt=fab.check(project)
            self.assertEqual(receipt['role'],'fabrication_staged')
            self.assertEqual(receipt['order_status'],'DO-NOT-ORDER')
            self.assertGreaterEqual(owner.call_count,4)
            # Changes to source policy cannot be hidden behind a previously issued
            # stage receipt, even when the upstream owner boundary is unchanged.
            (project/'evidence/manual.txt').write_text('Changed after review')
            with self.assertRaisesRegex(ValueError,'stale fabrication inputs'):
                fab.check(project)

    def test_population_policy_uses_project_board_names_and_quantities(self):
        # Generic policy regression: neither a two-board topology nor any
        # particular product names/build counts are prerequisites.
        inputs=self.root/'inputs'
        for declared in ({'power':3}, {'controller':2,'io':7}):
            with self.subTest(boards=declared):
                template=self.population_manifest();pop=copy.deepcopy(template)
                pop['boards']={};pop['assembly']['boards']={}
                manifest=self.fabrication_manifest();manifest['boards']={}
                for key,quantity in declared.items():
                    pop['boards'][key]=copy.deepcopy(template['boards']['carrier'])
                    pop['boards'][key]['quantity']=quantity
                    pop['assembly']['boards'][key]=copy.deepcopy(template['assembly']['boards']['carrier'])
                    manifest['boards'][key]=copy.deepcopy(self.fabrication_manifest()['boards']['carrier'])
                facts=self.stock_facts(pop)
                for part in facts['parts']:
                    part['quantity']=sum(declared.values())
                    part['offers'][0]['stock_count']=part['quantity']
                (inputs/'population.json').write_text(json.dumps(pop))
                (inputs/'stock.json').write_text(json.dumps(facts))
                _,_,graded=fab.policy(inputs,manifest)
                self.assertEqual({r['quantity'] for r in graded['demand']},{sum(declared.values())})
                for part in graded['demand']:
                    self.assertEqual({c['board'] for c in part['contributors']},set(declared))

    def test_public_build_refuses_missing_layout_seal(self):
        # Use an unadopted fixture: a regression must not require the real Crow
        # project to remain unfinished forever.
        crow=self.root.parent/'unadopted-project';crow.mkdir()
        run=subprocess.run(['/usr/bin/python3',str(Path(fab.__file__)),'build',
            '--project',str(crow),'--manifest','01_docs/nonexistent-fabrication.json',
            '--output','06_build/recovery/ls9-fabrication/test/never-publish'],
            text=True,capture_output=True,timeout=30)
        self.assertNotEqual(run.returncode,0)
        self.assertFalse((crow/'06_build/recovery/ls9-fabrication/test/never-publish').exists())
        self.assertIn('missing input: 01_docs/fabrication-contract.json',run.stderr)
        seal=subprocess.run(['/usr/bin/python3',str(Path(fab.seal.__file__)),
            'check','--project',str(crow)],text=True,capture_output=True,timeout=30)
        self.assertNotEqual(seal.returncode,0)
        self.assertIn('missing input: 06_build/checkpoints/layout_sealed.json',seal.stderr)


if __name__=='__main__': unittest.main()
