"""Self-contained joined source/schematic/PCB replay, not engineering acceptance."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import fab_replay as f
import test_fab_replay as fixture


class Design(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed=fixture.Native();cls.seed.setUp()
        cls.addClassCleanup(cls.seed.doCleanups)
        root=cls.seed.root
        circuit=dict(version=1,title='Synthetic replay test',nets=['N'],components=[
            dict(ref=ref,value='Pad',footprint='Test:Pad',expected_pins=['1'],at=[x,25.4],
                 pins=[dict(number='1',name='P',type='passive',at=[0,0],direction=180,net='N')])
            for ref,x in [('U1',25.4),('U2',50.8)]],
            wire_paths=[dict(net='N',points=[[25.4,25.4],[50.8,25.4]])])
        cls.seed.write('circuit/model.json',json.dumps(circuit))
        shutil.copyfile(Path(f.imported.native.__file__),root/'circuit/core.py')
        cls.seed.write('circuit/author.py','''from pathlib import Path
import json
import core
here=Path(__file__).parent
model=json.loads((here/'model.json').read_text())
core.check(model)
(here/'test.kicad_sch').write_text(core.render(model,'test'))
(here/'test.kicad_pro').write_text('{}\\n')
intent=dict(version=1,nets=model['nets'],components=[
    dict(ref=c['ref'],value=c['value'],footprint=c['footprint'],physical=True,fields={},
         pins=[{k:v for k,v in p.items() if k not in ('at','direction')} for p in c['pins']])
    for c in model['components']])
(here/'intent.json').write_text(json.dumps(intent,sort_keys=True)+'\\n')
''')
        f.p.command(['/usr/bin/python3',str(root/'circuit/author.py')])
        declaration=dict(version=1,producer=dict(entrypoint='circuit/author.py',
            inputs=['circuit/author.py','circuit/core.py','circuit/model.json']),
            intent='circuit/intent.json',schematic='circuit/test.kicad_sch',context=['circuit/test.kicad_pro'])
        cls.seed.write('import.json',json.dumps(declaration))
        member=dict(version=1,nets=['N'],components={c['ref']:dict(value=c['value'],
            footprint=c['footprint'],physical=True,pins=['1']) for c in circuit['components']})
        cls.seed.write('membership.json',json.dumps(member))
        cls.seed.write('assembly.json',json.dumps(dict(version=1,instances={'unit':'test'},boards={
            'test':dict(producer='imported',source='import.json',membership='membership.json',output='exports/test')})))
        cls.seed.write('expected.json',json.dumps(dict(version=1,instances={'unit':'test'})))
        cls.spec=dict(manifest='assembly.json',expected='expected.json')
        # Local schematic labels are /N in the native netlist; preserve that
        # exact namespace rather than comparing against the short intent alias.
        board=f.p.pcb.LoadBoard(str(root/'source.kicad_pcb'))
        board.FindNet('N').SetNetname('/N')
        settings=(root/'source.kicad_pro').read_bytes()
        f.p.pcb.SaveBoard(str(root/'source.kicad_pcb'),board)
        (root/'source.kicad_pro').write_bytes(settings)
        f.produce(root,cls.seed.boards,root/'package',schematics=cls.spec)

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='vnext-design-case-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'relocated'
        shutil.copytree(self.seed.root/'package',self.root)

    def rehash(self):
        record=f.p.read(self.root/'bundle.json');record['files']=f.inventory(self.root)
        (self.root/'bundle.json').write_text(json.dumps(record))

    def test_copied_tool_replays_circuit_and_pcb(self):
        before=f.inventory(self.root)
        run=subprocess.run(['/usr/bin/python3',str(self.root/'tools/fab_replay.py'),
            'verify','--package',str(self.root)],cwd='/tmp',text=True,capture_output=True,timeout=120)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertEqual(before,f.inventory(self.root));self.assertIn('DO-NOT-ORDER',run.stdout)

    def test_missing_producer_and_unclaimed_design_fail(self):
        source=self.root/'design/circuit/author.py';saved=source.read_bytes();source.unlink()
        self.rehash()
        with self.assertRaises((ValueError,OSError)):f.verify(self.root)
        source.write_bytes(saved);self.rehash()
        record=f.p.read(self.root/'bundle.json');record['schematics']=None
        (self.root/'bundle.json').write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError,'unclaimed'):f.verify(self.root)

    def test_wrong_board_pdf_not_hidden_by_inventory(self):
        pdf=self.root/'fab/test/pdf'
        shutil.copyfile(pdf/'assembly-bottom.pdf',pdf/'assembly-top.pdf');self.rehash()
        with self.assertRaisesRegex(ValueError,'PDF rendered pages differ'):f.verify(self.root)

    def test_native_source_edit_not_hidden_by_rebuilt_receipt(self):
        design=self.root/'design';sch=design/'circuit/test.kicad_sch'
        sch.write_text(sch.read_text()+'\n')
        receipt=f.imported.record(design,design/'import.json',design/'exports/test')
        (design/'exports/test/receipt.json').write_text(json.dumps(receipt));self.rehash()
        with self.assertRaisesRegex(ValueError,'producer replay differs'):f.verify(self.root)

    def test_wrong_schematic_pdf_not_hidden_by_rebuilt_receipt(self):
        design=self.root/'design';out=design/'exports/test'
        shutil.copyfile(self.root/'fab/test/pdf/pcb.pdf',out/'native.pdf')
        (out/'receipt.json').write_text(json.dumps(f.imported.record(design,design/'import.json',out)))
        self.rehash()
        with self.assertRaisesRegex(ValueError,'PDF replay differs'):f.verify(self.root)

    def test_missing_instance_and_extra_design_files_fail(self):
        design=self.root/'design';manifest=f.p.read(design/'assembly.json')
        manifest['instances']={};(design/'assembly.json').write_text(json.dumps(manifest));self.rehash()
        with self.assertRaises(ValueError):f.verify(self.root)
        shutil.copyfile(self.seed.root/'package/design/assembly.json',design/'assembly.json')
        (design/'extra.txt').write_text('not declared');self.rehash()
        with self.assertRaisesRegex(ValueError,'file census'):f.verify(self.root)

    def test_cross_artifact_pin_and_part_identity(self):
        # Exercise the joined predicate directly, before plot/DRC would also fail.
        record=f.p.read(self.root/'bundle.json');native=self.root/record['boards']['test']['native']
        original=native.read_bytes()
        for kind in ('value','pin'):
            native.write_bytes(original);board=f.p.pcb.LoadBoard(str(native))
            fp=board.FindFootprintByReference('U1')
            if kind=='value':fp.SetValue('other')
            else:next(iter(fp.Pads())).SetNetCode(0)
            f.p.pcb.SaveBoard(str(native),board)
            with self.assertRaisesRegex(ValueError,'PCB/schematic'):
                f.pcb_schematic_parity(self.root,record['boards'],self.spec)

    def test_raw_native_parity_executed_and_bound(self):
        path=self.root/'fab/test/drc-execution.json';record=f.p.read(path)
        self.assertIn('--schematic-parity',record['command'])
        self.assertIn('--exit-code-violations',record['command'])
        self.assertEqual(record['schematic_sha256'],f.p.sha(self.root/'design/circuit/test.kicad_sch'))
        record['command'].remove('--schematic-parity');path.write_text(json.dumps(record));self.rehash()
        with self.assertRaisesRegex(ValueError,'execution differs'):f.verify(self.root)

    def test_shortened_namespace_is_not_equivalent(self):
        record=f.p.read(self.root/'bundle.json');native=self.root/record['boards']['test']['native']
        board=f.p.pcb.LoadBoard(str(native));board.FindNet('/N').SetNetname('N')
        f.p.pcb.SaveBoard(str(native),board)
        with self.assertRaisesRegex(ValueError,'pin nets differ'):
            f.pcb_schematic_parity(self.root,record['boards'],self.spec)

    def test_native_mismatch_not_covered_by_custom_pin_comparison(self):
        record=f.p.read(self.root/'bundle.json');entry=record['boards']['test']
        native=self.root/entry['native'];settings=native.with_suffix('.kicad_pro').read_bytes()
        board=f.p.pcb.LoadBoard(str(native));fp=board.FindFootprintByReference('U1')
        fp.SetAttributes(fp.GetAttributes() | f.p.pcb.FP_DNP)
        f.p.pcb.SaveBoard(str(native),board);native.with_suffix('.kicad_pro').write_bytes(settings)
        native.with_suffix('.kicad_prl').unlink(missing_ok=True)  # Test-only SaveBoard side effect.
        f.pcb_schematic_parity(self.root,record['boards'],self.spec)
        with self.assertRaisesRegex(ValueError,'DRC failed'):
            f.regenerate(self.root,'test',entry,self.root/'bad-export',
                         self.root/'design/circuit/test.kicad_sch')

    def test_schematic_component_cannot_be_marked_board_only(self):
        record=f.p.read(self.root/'bundle.json');entry=record['boards']['test']
        native=self.root/entry['native'];board=f.p.pcb.LoadBoard(str(native))
        fp=board.FindFootprintByReference('U1')
        fp.SetAttributes(fp.GetAttributes() | f.p.pcb.FP_BOARD_ONLY)
        f.p.pcb.SaveBoard(str(native),board)
        with self.assertRaisesRegex(ValueError,'incorrectly marked board-only'):
            f.pcb_schematic_parity(self.root,record['boards'],self.spec)

    def test_complete_claim_cannot_survive_schematic_downgrade(self):
        record=f.p.read(self.root/'bundle.json')
        record['schematics']=None
        shutil.rmtree(self.root/'design')  # Disposable fixture only.
        record['files']=f.inventory(self.root)
        (self.root/'bundle.json').write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError,'scope/limitations'):
            f.verify(self.root)


if __name__=='__main__':unittest.main()
