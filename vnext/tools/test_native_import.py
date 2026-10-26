"""Real B8 import/replay and adversarial controls; not engineering acceptance.

The base uses actual Crow artifacts with explicitly labelled test-projection
membership. Mutations only affect temporary copies. Upstream receipts remain
mandatory; no frozen candidate or real review is modified by these tests.
"""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

import native_import as imported
import schematic_assembly as assembly
import schematic_admission as admission

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'development/adoption1'


@unittest.skipUnless((FIXTURE/'carrier-import.json').exists(),'Crow import fixture absent')
class ImportedNative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='vnext-import-tests-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.base=Path(cls.temp.name)/'base'
        shutil.copytree(FIXTURE,cls.base,ignore=shutil.ignore_patterns('build','build-*','__pycache__'))
        for board in ('carrier','pod'):
            imported.build(cls.base,cls.base/f'{board}-import.json',cls.base/'build'/board)

    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='vnext-import-case-')
        self.addCleanup(temp.cleanup);self.root=Path(temp.name)/'case'
        shutil.copytree(self.base,self.root)
        self.path=self.root/'carrier-import.json';self.out=self.root/'build/carrier'

    def verify(self):
        return imported.verify(self.root,self.path,self.out,self.root/'carrier-members-fixture.json')

    def write(self,path,value):
        path.write_text(json.dumps(value))

    def test_both_native_drawings_are_unchanged_from_frozen_b8(self):
        for b in ('carrier','pod'):
            self.assertEqual((self.root/f'circuit/{b}/{b}.kicad_sch').read_bytes(),
                             (ROOT/f'development/candidates/b8/{b}/{b}.kicad_sch').read_bytes())
        self.assertTrue(self.verify())

    def test_actual_nine_instances_and_64_wires(self):
        r=assembly.verify(self.root,'assembly-fixture.json','expected-fixture.json')
        self.assertEqual(len(r['instances']),9)
        self.assertEqual(r['harness_wire_count'],64)
        self.assertTrue(r['harness_checked'])

    def test_missing_pod_and_swapped_audio_wire(self):
        p=self.root/'assembly-fixture.json';good=imported.read(p)
        bad=copy.deepcopy(good);del bad['instances']['pod8'];self.write(p,bad)
        with self.assertRaisesRegex(ValueError,'instance membership'):
            assembly.verify(self.root,p.name,'expected-fixture.json')
        bad=copy.deepcopy(good)
        bad['harness'][0][1].update(pin='2',net='LINEM');self.write(p,bad)
        with self.assertRaisesRegex(ValueError,'wiring differs'):
            assembly.verify(self.root,p.name,'expected-fixture.json')

    def test_empty_or_duplicate_intent_rejected(self):
        s=imported.read(self.root/'circuit/carrier/intent.json')
        bad=copy.deepcopy(s);bad['components']=[]
        with self.assertRaises(ValueError):imported.check_intent(bad)
        bad=copy.deepcopy(s);bad['components'].append(bad['components'][0])
        with self.assertRaises(ValueError):imported.check_intent(bad)
        bad=copy.deepcopy(s);bad['components'][0]['pins'][0]['net']='MISSING'
        with self.assertRaises(ValueError):imported.check_intent(bad)

    def test_missing_membership_and_wrong_virtual_status(self):
        p=self.root/'carrier-members-fixture.json';m=imported.read(p)
        del m['components']['J8'];self.write(p,m)
        with self.assertRaisesRegex(ValueError,'membership mismatch'):self.verify()
        s=imported.read(self.root/'circuit/carrier/intent.json')
        s['components'][0]['physical']=False
        with self.assertRaisesRegex(ValueError,'physical part'):imported.check_intent(s)

    def test_native_and_library_or_source_changes_stale_receipt(self):
        for name in ('circuit/carrier/carrier.kicad_sch','circuit/selected_parts.json',
                     'circuit/libraries/Crow.pretty/Infineon_IM70A135_PG_TLGA_5_5_NSMD.kicad_mod'):
            p=self.root/name;original=p.read_bytes();p.write_bytes(original+b'\n')
            with self.assertRaisesRegex(ValueError,'stale import'):self.verify()
            p.write_bytes(original)

    def test_forged_receipt_cannot_hide_native_edit(self):
        p=self.root/'circuit/carrier/carrier.kicad_sch';p.write_text(p.read_text()+'\n')
        self.write(self.out/'receipt.json',imported.record(self.root,self.path,self.out))
        with self.assertRaisesRegex(ValueError,'producer replay differs'):self.verify()

    def test_wrong_pdf_rejected_even_with_refreshed_hashes(self):
        shutil.copyfile(self.root/'build/pod/native.pdf',self.out/'native.pdf')
        self.write(self.out/'receipt.json',imported.record(self.root,self.path,self.out))
        with self.assertRaisesRegex(ValueError,'PDF replay differs'):self.verify()

    def test_erc_scope_and_details_not_only_counts_are_replayed(self):
        for key in ('native-erc.json','native-erc-all.json'):
            p=self.out/key;original=p.read_bytes();obj=imported.read(p)
            obj['source']='wrong-source.kicad_sch';self.write(p,obj)
            self.write(self.out/'receipt.json',imported.record(self.root,self.path,self.out))
            with self.assertRaisesRegex(ValueError,'ERC replay differs'):self.verify()
            p.write_bytes(original)
        p=self.out/'native-erc-all.json';obj=imported.read(p)
        obj['ignored_checks']=[];self.write(p,obj)
        self.write(self.out/'receipt.json',imported.record(self.root,self.path,self.out))
        with self.assertRaisesRegex(ValueError,'ERC replay differs'):self.verify()

    def test_pin_type_and_ordering_identity_not_just_net_counts(self):
        s=imported.read(self.root/'circuit/carrier/intent.json')
        xml=self.out/'native.xml';original=xml.read_bytes()
        tree=ET.parse(xml);pin=tree.find('./libparts/libpart/pins/pin')
        pin.set('type','output' if pin.get('type')!='output' else 'input');tree.write(xml)
        with self.assertRaisesRegex(ValueError,'pin function/type'):imported.parity(s,xml)
        xml.write_bytes(original);tree=ET.parse(xml)
        field=tree.find('./components/comp/fields/field[@name="MPN"]')
        self.assertIsNotNone(field);field.text='WRONG';tree.write(xml)
        with self.assertRaisesRegex(ValueError,'ordering/custom'):imported.parity(s,xml)

    def test_unknown_producer_and_escaping_paths_fail(self):
        with self.assertRaisesRegex(ValueError,'unsupported schematic producer'):
            assembly.producer({'source':'x','membership':'y','output':'z','producer':'trust-me'})
        d=imported.read(self.path);d['producer']['inputs'][0]='../outside.py';self.write(self.path,d)
        with self.assertRaisesRegex(ValueError,'invalid import path'):self.verify()

    def test_noop_producer_cannot_copy_native_as_input(self):
        d=imported.read(self.path);d['producer']['inputs'].append(d['schematic']);self.write(self.path,d)
        with self.assertRaisesRegex(ValueError,'must be produced'):self.verify()

    def test_receipt_and_membership_cannot_follow_outside_symlinks(self):
        with tempfile.TemporaryDirectory(prefix='vnext-outside-') as tmp:
            for name in ('build/carrier/receipt.json','carrier-members-fixture.json'):
                p=self.root/name;original=p.read_bytes();outside=Path(tmp)/p.name
                outside.write_bytes(original);p.unlink();p.symlink_to(outside)
                with self.assertRaisesRegex(ValueError,'escapes root'):self.verify()
                p.unlink();p.write_bytes(original)

    def test_erc_suppression_is_not_admitted(self):
        s=imported.read(self.root/'circuit/carrier/intent.json')
        p=self.root/'circuit/carrier/carrier.kicad_pro';self.write(p,{'erc':{'erc_exclusions':['hidden']}})
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'suppressed ERC'):
                imported.export(p.with_suffix('.kicad_sch'),Path(tmp),s)

    def test_real_erc_conflict_prevents_build_receipt(self):
        p=self.root/'circuit/generate.py'
        old='("1","+12V","passive","VIN12")'
        new='("1","+12V","power_out","VIN12")'
        self.assertIn(old,p.read_text());p.write_text(p.read_text().replace(old,new))
        subprocess.run([sys.executable,str(self.root/'circuit/import_source.py')],
                       check=True,capture_output=True)
        out=self.root/'build/conflict'
        with self.assertRaisesRegex(ValueError,'kicad-cli failed|ERC'):
            imported.build(self.root,self.path,out)
        self.assertFalse((out/'receipt.json').exists())

    def test_flat_only_not_hierarchy_by_omission(self):
        s=imported.read(self.root/'circuit/carrier/intent.json');p=self.out/'native.xml'
        tree=ET.parse(p);ET.SubElement(tree.find('design'),'sheet',{'number':'2'});tree.write(p)
        with self.assertRaisesRegex(ValueError,'flat schematic'):imported.parity(s,p)

    def test_missing_upstream_receipt_prevents_admission(self):
        with self.assertRaises((ValueError,OSError)):
            admission.prerequisites(self.root,ROOT)

    def synthetic_admission(self, version=2):
        """Exercise the real receipt chain, NEVER supply a real engineering verdict.

        All upstream facts and review identities below are deliberately synthetic;
        only the copied Crow producer/native artifacts are real. The directory is
        disposable and no result may be promoted to the development project.
        """
        upstream=admission.upstream
        def put(name, text):
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        contract={'version':version,'manifest':'assembly-fixture.json',
                  'expected':'expected-fixture.json','rf':False}
        if version==2:contract['producers']=['imported']
        put(admission.CONTRACT,json.dumps(contract))
        put(admission.CAPABILITY,json.dumps({'rf':False,'signal_integrity':'high_speed_digital'}))
        prompt='Synthetic admission contract exercise; not a board approval.'
        put('01_docs/BRIEF.md',f'status: in-progress\nprompt_sha256: {upstream.digest(prompt.encode())}\n'
            f'<!-- prompt-verbatim-begin -->\n{prompt}\n<!-- prompt-verbatim-end -->\n')
        for name in ('requirements','power_tree','integration'):
            put(f'03_src/rules/{name}.yaml','synthetic_test_only: true\n')
        for name in ('ARCHITECTURE','DETAIL_DESIGN'):
            put(f'01_docs/{name}.md','Synthetic upstream input; no engineering verdict.\n')
        put('01_docs/sourcing/exact-parts.csv','MPN,Dossier\nSYNTHETIC,02_parts/test/part.yaml\n')
        put('02_parts/test/part.yaml','mpn: SYNTHETIC\n')
        put('02_parts/test/datasheet.pdf','Synthetic nonempty evidence fixture, NOT a manufacturer PDF.\n')
        put('01_docs/decisions/sourcing.md','Synthetic sourcing policy for receipt testing only.\n')
        def review(stage, names, criteria, name):
            obj={'schema':1,'stage':stage,'author':'synthetic-author','reviewer':'synthetic-reviewer',
                 'verdict':'PASS','subjects':{n:upstream.digest((self.root/n).read_bytes()) for n in names},
                 'checks':{c:{'verdict':'PASS','evidence':sorted(names),
                              'rationale':'Synthetic structural test, not engineering acceptance.'}
                           for c in criteria}}
            put(name,'# Synthetic test only\n```json\n'+json.dumps(obj)+'\n```\n')
            return obj
        for stage in ('PCB-COMMISSION','PCB-ARCHITECTURE','PCB-SOURCING'):
            names=set(upstream.REQUIRED[stage])
            if stage=='PCB-ARCHITECTURE':
                names.update(f'03_src/rules/{n}.yaml' for n in ('requirements','power_tree','integration'))
            if stage=='PCB-SOURCING':
                names.update((admission.CONTRACT,'contracts.md','02_parts/test/part.yaml',
                              '02_parts/test/datasheet.pdf','01_docs/decisions/sourcing.md'))
            role=upstream.ROLES[stage];name=f'08_reviews/2026-10-04-synthetic-{role}.md'
            review(stage,names,upstream.CRITERIA[stage],name)
            put(f'06_build/checkpoints/{role}.json',json.dumps(upstream.certificate(self.root,name,ROOT)))
        names={admission.CONTRACT,admission.CAPABILITY,'contracts.md',admission.PARTS,
               'assembly-fixture.json','expected-fixture.json'}
        for board in ('carrier','pod'):
            names.add(f'{board}-members-fixture.json')
            names.update(p.relative_to(self.root).as_posix() for p in imported.subjects(
                self.root,self.root/f'{board}-import.json',self.root/'build'/board))
        name='08_reviews/2026-10-04-synthetic-schematic.md'
        return name,review('KICAD-SCHEMATIC',names,admission.CHECKS,name)

    def save_review(self,name,obj):
        (self.root/name).write_text('# Synthetic test only\n```json\n'+json.dumps(obj)+'\n```\n')

    def test_opted_in_import_admission_reopens_real_chain_and_native(self):
        name,_=self.synthetic_admission()
        cert=admission.certificate(self.root,name,ROOT)
        self.assertEqual(cert['role'],'schematic_reviewed')
        self.assertEqual(cert['assembly']['harness_wire_count'],64)
        self.write(self.root/admission.RECEIPT,cert)
        self.assertEqual(admission.validate(self.root,ROOT),cert)
        (self.root/'03_src/rules/power_tree.yaml').write_text('changed: true\n')
        with self.assertRaisesRegex(ValueError,'stale subject'):
            admission.validate(self.root,ROOT)

    def test_legacy_contract_does_not_silently_adopt_imported_producer(self):
        name,_=self.synthetic_admission(version=1)
        with self.assertRaisesRegex(ValueError,'producer not adopted'):
            admission.certificate(self.root,name,ROOT)

    def test_import_requires_review_of_each_producer_input(self):
        name,obj=self.synthetic_admission()
        obj['checks']['completeness']['evidence'].remove('circuit/generate.py')
        self.save_review(name,obj)
        with self.assertRaisesRegex(ValueError,'completeness lacks'):
            admission.certificate(self.root,name,ROOT)

    def test_import_cannot_bypass_review_independence_or_criteria(self):
        name,obj=self.synthetic_admission()
        obj['reviewer']=obj['author'];self.save_review(name,obj)
        with self.assertRaisesRegex(ValueError,'author and reviewer must differ'):
            admission.certificate(self.root,name,ROOT)
        obj['reviewer']='synthetic-reviewer';del obj['checks']['electrical'];self.save_review(name,obj)
        with self.assertRaisesRegex(ValueError,'schematic checks'):
            admission.certificate(self.root,name,ROOT)


if __name__=='__main__':unittest.main()
