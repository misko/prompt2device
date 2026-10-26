"""Archive integrity/admission and actual isolation tests; not board acceptance."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import release_review as r


class Release(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory(prefix='release-fixture-');self.addCleanup(t.cleanup)
        self.root=Path(t.name);self.project=self.root/'project';self.project.mkdir()
        self.archive=self.project/'output';self.archive.mkdir()
        self.write('source/project/circuit.txt','synthetic circuit')
        self.write('fab/board.txt','synthetic circuit')
        self.write('mechanical/geometry.json',r.dump({'boards':{'board':{'references':{'U1':{}}}}}))
        self.record=dict(version=1,sealed=False,design_status='UNREVIEWED',order_status='DO-NOT-ORDER',
            release_id='fixture-v1',boards={'board':dict(version='v1',quantity=1)},
            assembly_receipt_sha256='a'*64,origins={'source/project/circuit.txt':dict(origin='project',
                path='circuit.txt',sha256=r.p.sha(self.archive/'source/project/circuit.txt'))},
            aliases={'fab/board.txt':'source/project/circuit.txt'},
            order_policy={'holds':[{'id':'HOLD'}]})
        self.save()

    def write(self,name,text):
        file=self.archive/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text)

    def save(self):
        self.record['files']=r.census(self.archive,{'release.json'})
        self.write('release.json',r.dump(self.record))

    def review(self):
        units={'pin_identity':['board/U1'],'readability':['board'],'electrical':['board'],
               'layout_power':['board'],'completeness':sorted('board/'+s for s in
                   ('source','schematic','fab','assembly','mechanical')),'order_readiness':['HOLD']}
        subjects={'output/'+n:d for n,d in r.census(self.archive).items()}
        return dict(schema=1,stage='PCB-RELEASE-REVIEW',author='Author',reviewer='Independent',
                    manifest='manifest.json',output='output',design_verdict='SOUND',order_verdict='DO-NOT-ORDER',
                    subjects=subjects,checks={k:dict(verdict='PASS',rationale='Synthetic scoped judgment',
                        evidence=['output/release.json'],coverage=dict(required=u,reviewed=u,findings=[]))
                        for k,u in units.items()})

    def certificate(self,obj):
        name='08_reviews/2026-10-08-test.md';(self.project/name).parent.mkdir(exist_ok=True)
        (self.project/name).write_text('```json\n'+r.dump(obj)+'```\n')
        with patch.object(r,'verify',return_value={'subjects':self.review()['subjects']}):
            return r.certificate(self.project,name)

    def test_inventory_and_alias_positive(self):
        self.assertEqual(r.inventory_check(self.archive),self.record)

    def test_deleted_changed_extra_and_symlink_fail(self):
        f=self.archive/'fab/board.txt';data=f.read_bytes();f.unlink()
        with self.assertRaises(ValueError):r.inventory_check(self.archive)
        f.write_bytes(data+b'x')
        with self.assertRaises(ValueError):r.inventory_check(self.archive)
        f.write_bytes(data);extra=self.archive/'extra.pyc';extra.write_bytes(b'cache')
        with self.assertRaises(ValueError):r.inventory_check(self.archive)
        extra.unlink();f.unlink();f.symlink_to(self.archive/'source/project/circuit.txt')
        with self.assertRaises(ValueError):r.inventory_check(self.archive)

    def test_self_rehashed_payload_cannot_disagree_with_source(self):
        self.write('fab/board.txt','other');self.save()
        with self.assertRaisesRegex(ValueError,'presentation'):r.inventory_check(self.archive)

    def test_self_rehashed_source_cannot_disagree_with_origin(self):
        self.write('source/project/circuit.txt','other');self.save()
        with self.assertRaisesRegex(ValueError,'source inventory'):r.inventory_check(self.archive)

    def test_independent_review_exact_scope_and_design_order_verdicts(self):
        obj=self.review();cert=self.certificate(obj);self.assertEqual(cert['role'],'release_reviewed')
        mutations=[lambda d:d.update(reviewer='Author'),lambda d:d.update(design_verdict='INCOMPLETE'),
                   lambda d:d.update(order_verdict='READY'),lambda d:d['subjects'].pop('output/release.json'),
                   lambda d:d['checks'].pop('electrical'),
                   lambda d:d['checks']['electrical']['coverage'].update(required=[],reviewed=[]),
                   lambda d:d['checks']['pin_identity']['coverage'].update(required=['board/U2'],reviewed=['board/U2']),
                   lambda d:d['checks']['electrical']['coverage'].update(findings=['unresolved']),
                   lambda d:d['checks']['electrical'].update(evidence=['missing'])]
        for mutation in mutations:
            changed=copy.deepcopy(obj);mutation(changed)
            with self.assertRaises(ValueError):self.certificate(changed)

    def test_definition_only_cannot_issue(self):
        graph={'stages':[dict(spec={'id':'PCB-RELEASE-REVIEW','requires':['assembly_verified','rf_fab_clearance'],
                                  'produces':['release_reviewed']},local_definition={})]}
        original=r.p.read
        with patch.object(r.p,'read',side_effect=lambda path:graph if path.name=='graph.json' else original(path)):
            with self.assertRaisesRegex(ValueError,'not adopted'):self.certificate(self.review())

    def test_replay_rejects_untrusted_tool_before_execution(self):
        with patch.object(subprocess,'run',side_effect=AssertionError('must not execute')):
            with self.assertRaises(ValueError):r.replay(self.archive)

    def test_duplicate_stage_binding_cannot_issue(self):
        graph=r.p.read(r.p.ROOT/'skills/pcb-design/workflow/graph.json')
        stage=next(s for s in graph['stages'] if s['spec']['id']=='PCB-RELEASE-REVIEW')
        graph['stages'].append(copy.deepcopy(stage));original=r.p.read
        with patch.object(r.p,'read',side_effect=lambda path:graph if path.name=='graph.json' else original(path)):
            with self.assertRaisesRegex(ValueError,'stage identity'):self.certificate(self.review())

    def test_live_adoption_comparison_rejects_missing_boards_versions_and_extra_files(self):
        hold=dict(id='HOLD',reason='unqualified process',closure='assembly owner confirms',evidence=['fact'])
        policy={'holds':[hold]};spec=dict(release_id='fixture-v1',boards=self.record['boards'],mechanical_basis='boxes')
        self.write('source/project/g.json',(self.archive/'mechanical/geometry.json').read_text())
        self.record['origins']['source/project/g.json']=dict(origin='project',path='g.json',
            sha256=r.p.sha(self.archive/'source/project/g.json'))
        self.record['aliases']['mechanical/geometry.json']='source/project/g.json'
        f=self.project/r.assembly.RECEIPT;f.parent.mkdir(parents=True);f.write_text('{}')
        self.record.update(manifest='manifest.json',order_policy=policy,mechanical_basis='boxes',
                           assembly_receipt_sha256=r.p.sha(f))
        self.write('ORDER-INSTRUCTIONS.md',r.order_text(spec,policy));self.save()
        original=copy.deepcopy(self.record)
        def check():
            with (patch.object(r,'inputs',return_value=(spec,policy,original['origins'],'package','views')),
                  patch.object(r,'presentation',return_value=original['aliases'])):
                return r.compare(self.project,'manifest.json',self.archive)
        self.assertEqual(check(),self.record)
        for change in (lambda d:d['boards'].clear(),lambda d:d['boards']['board'].update(version='v2'),
                       lambda d:d['boards']['board'].update(quantity=8),lambda d:d.update(release_id='different')):
            self.record=copy.deepcopy(original);change(self.record);self.save()
            with self.assertRaises(ValueError):check()
        self.record=copy.deepcopy(original);self.write('extra.txt','unaccounted');self.save()
        with self.assertRaisesRegex(ValueError,'unaccounted'):check()

    def test_upstream_owning_check_mandatory(self):
        for name,body in [('authority.md','scope'),(r.assembly.RECEIPT,'{}')]:
            f=self.project/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(body)
        contract=dict(version=1,authority='authority.md',authority_sha256=r.p.sha(self.project/'authority.md'),
                      assembly_receipt_sha256=r.p.sha(self.project/r.assembly.RECEIPT))
        (self.project/r.CONTRACT).parent.mkdir(exist_ok=True)
        (self.project/r.CONTRACT).write_text(r.dump(contract))
        with patch.object(r.assembly,'check',side_effect=ValueError('owner failed')) as owner:
            with self.assertRaisesRegex(ValueError,'owner failed'):r.inputs(self.project,'missing.json')
            owner.assert_called_once_with(self.project)

    def test_dependency_closure_retains_fenced_review_and_json_transitive_files(self):
        (self.project/'data').mkdir()
        (self.project/'data/a.json').write_text(r.dump({'file':'data/b.txt','rationale':'word'*80+'/not-a-path'}))
        (self.project/'data/b.txt').write_text('evidence')
        (self.project/'review.md').write_text('```json\n{"subjects":{"data/a.json":"hash"}}\n```')
        found=r.closure(self.project,['review.md'])
        self.assertEqual(set(found),{'review.md','data/a.json','data/b.txt'})

    def test_actual_offline_guard_denies_network_original_files_and_allows_scratch(self):
        scratch=self.root/'scratch';scratch.mkdir();outside=self.root/'outside';outside.write_text('not accessible')
        script=scratch/'probe.py';script.write_text('''import socket,sys
from pathlib import Path
try: Path(sys.argv[1]).read_text()
except PermissionError: pass
else: raise AssertionError('original path readable')
try: socket.socket()
except PermissionError: pass
else: raise AssertionError('network allowed')
Path('result').write_text('isolated')
''')
        result=subprocess.run([sys.executable,'-B',str(Path(r.__file__).with_name('offline_replay.py')),
                               '--scratch',str(scratch),str(script),str(outside)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((scratch/'result').read_text(),'isolated')

    def test_actual_guard_archive_is_readonly_but_regeneration_is_allowed(self):
        scratch=self.root/'scratch';scratch.mkdir();archive=scratch/'archive';archive.mkdir()
        script=archive/'probe.py';script.write_text('''from pathlib import Path
import tempfile
try: Path(__file__).with_name('unexpected.kicad_prl').write_text('mutation')
except PermissionError: pass
else: raise AssertionError('archive writable')
with tempfile.TemporaryDirectory() as tmp:
    Path(tmp,'new.txt').write_text('regenerated')
Path('result').write_text('read-only archive')
''')
        before=r.census(archive)
        result=subprocess.run([sys.executable,'-B',str(Path(r.__file__).with_name('offline_replay.py')),
            '--scratch',str(scratch),'--readonly-archive',str(script)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(r.census(archive),before)
        self.assertEqual((scratch/'work/result').read_text(),'read-only archive')


if __name__=='__main__':unittest.main()
