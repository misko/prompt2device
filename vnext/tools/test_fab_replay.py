"""Real native portability tests; fixture acceptance is not a board release."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest
import zipfile
from unittest.mock import patch

import fab_replay as f
import test_routing as fixture


class Native(unittest.TestCase):
    write=fixture.Native.write
    def setUp(self):
        fixture.Native.setUp(self)
        self.write('fp-lib-table','(fp_lib_table (lib (name "Test") (type "KiCad") '
                   '(uri "${KIPRJMOD}/Test.pretty") (options "")))')
        self.boards={'test':{'source':'source.kicad_pcb','project':'source.kicad_pro',
                            'resources':{'fp-lib-table':'fp-lib-table','Test.pretty/Pad.kicad_mod':'lib/Pad.kicad_mod'}}}
        source=self.root/'source.kicad_pcb'; settings=source.with_suffix('.kicad_pro').read_bytes()
        board=f.p.pcb.LoadBoard(str(source))
        for fp in board.GetFootprints():fp.Reference().SetTextSize(f.p.vector(1,1))
        f.p.pcb.SaveBoard(str(source),board);source.with_suffix('.kicad_pro').write_bytes(settings)

    def build(self):return f.produce(self.root,self.boards,self.root/'package')

    def test_relocated_copied_tool_replays_without_original_project(self):
        result=self.build(); target=self.root/'relocated'; (self.root/'package').rename(target)
        (self.root/'source.kicad_pcb').unlink(); shutil.rmtree(self.root/'lib')
        command=['/usr/bin/python3',str(target/'tools/fab_replay.py'),'verify','--package',str(target)]
        run=subprocess.run(command,capture_output=True,text=True,timeout=90,cwd='/tmp')
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertFalse(result['accepted']); self.assertIn('2D',result['scope'])
        self.assertEqual(f.inventory(target),result['files'])

    def test_relocated_bundle_contains_critical_gate_dependencies(self):
        self.build();target=self.root/'package'
        run=subprocess.run(['/usr/bin/python3','-B','-c',
            'import critical_routes,json; print(json.dumps(critical_routes.tool_identities()))'],
            cwd=target/'tools',capture_output=True,text=True,timeout=30)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        actual=json.loads(run.stdout)
        self.assertEqual(set(actual),{'critical_routes.py','routing.py','routing_geometry.py'})
        for name,digest in actual.items():self.assertEqual(digest,f.p.sha(target/'tools'/name))

    def test_missing_and_extra_archive_files_fail(self):
        self.build(); root=self.root/'package'; file=root/'source/test/Test.pretty/Pad.kicad_mod'
        saved=file.read_bytes(); file.unlink()
        with self.assertRaisesRegex(ValueError,'inventory'):f.verify(root)
        file.write_bytes(saved); (root/'extra').write_text('unreviewed')
        with self.assertRaisesRegex(ValueError,'inventory'):f.verify(root)

    def test_gerber_tamper_not_hidden_by_refreshed_hash(self):
        self.build(); root=self.root/'package'; path=root/'fab/test/plots/test-F_Cu.gbr'
        path.write_text(path.read_text().replace('D01*','D02*'))
        record=json.loads((root/'bundle.json').read_text());record['files']=f.inventory(root)
        (root/'bundle.json').write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError,'archive/plot bytes differ'):f.verify(root)

    def test_replot_catches_matching_modified_plot_zip_and_hash(self):
        self.build(); root=self.root/'package'; path=root/'fab/test/plots/test-F_Cu.gbr'
        original=path.read_text(); changed=original.replace('D01*','D02*')
        self.assertNotEqual(original,changed); path.write_text(changed)
        zip_path=root/'fab/test/test-gerbers.zip'
        with zipfile.ZipFile(zip_path) as z: members=[(info,z.read(info.filename)) for info in z.infolist()]
        with zipfile.ZipFile(zip_path,'w') as z:
            for info, content in members:z.writestr(info,path.read_bytes() if info.filename == path.name else content)
        record=json.loads((root/'bundle.json').read_text());record['files']=f.inventory(root)
        (root/'bundle.json').write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError,'offline source/plot geometry differs'):f.verify(root)

    def test_timestamp_prefix_cannot_hide_gerber_commands(self):
        a=self.root/'normal.gbr';b=self.root/'forged.gbr'
        a.write_text('G04 Created by KiCad date*\n%TF.CreationDate,old*%\nM02*\n')
        for prefix in ('G04 Created by KiCad date*','%TF.CreationDate,new*%'):
            b.write_text(a.read_text().replace('M02*',prefix+'D10*X100Y100D01*\nM02*'))
            self.assertNotEqual(f.fab.canonical_plot(a),f.fab.canonical_plot(b))

    def test_zip_symlink_metadata_cannot_be_hidden_by_rehash(self):
        self.build();root=self.root/'package';zip_path=root/'fab/test/test-gerbers.zip'
        with zipfile.ZipFile(zip_path) as z: members=[(info,z.read(info.filename)) for info in z.infolist()]
        members[0][0].external_attr=0o120777 << 16
        with zipfile.ZipFile(zip_path,'w') as z:
            for info,content in members:z.writestr(info,content)
        record=json.loads((root/'bundle.json').read_text());record['files']=f.inventory(root)
        (root/'bundle.json').write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError,'archive member metadata'):f.verify(root)

    def test_omitted_board_entry_cannot_reduce_replay_scope(self):
        self.boards['second']=self.boards['test'].copy(); self.build(); root=self.root/'package'
        record=json.loads((root/'bundle.json').read_text()); del record['boards']['second']
        (root/'bundle.json').write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError,'board directory census'):f.verify(root)

    def test_linked_member_and_directory_rejected(self):
        self.build(); root=self.root/'package'; linked=self.root/'linked'
        linked.symlink_to(root,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'linked'):f.verify(linked)
        file=root/'source/test/Test.pretty/Pad.kicad_mod'; saved=self.root/'saved'
        file.rename(saved);file.symlink_to(saved)
        with self.assertRaisesRegex(ValueError,'linked'):f.verify(root)

    def test_existing_target_preserved_and_live_gate_required(self):
        self.build()
        with self.assertRaisesRegex(ValueError,'existing'):self.build()
        with patch.object(f.s,'check',side_effect=ValueError('layout seal required')):
            with self.assertRaisesRegex(ValueError,'seal required'):f.export(self.root,'live')
        self.assertFalse((self.root/'live').exists())

    def test_rehashed_missing_or_changed_copied_tools_fail(self):
        self.build();root=self.root/'package';tool=root/'tools/native_import.py'
        original=tool.read_bytes()
        for change in ('missing','changed'):
            if change=='missing':tool.unlink()
            else:tool.write_bytes(original+b'\n# unreviewed change\n')
            record=json.loads((root/'bundle.json').read_text());record['files']=f.inventory(root)
            (root/'bundle.json').write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError,'tool census|verifying toolchain'):f.verify(root)

    def test_missing_library_and_real_short_do_not_publish(self):
        mapping=self.boards['test']['resources'];del mapping['Test.pretty/Pad.kicad_mod']
        with self.assertRaises(ValueError):self.build()
        self.assertFalse((self.root/'package').exists())
        mapping['Test.pretty/Pad.kicad_mod']='lib/Pad.kicad_mod'
        source=self.root/'source.kicad_pcb';settings=source.with_suffix('.kicad_pro').read_bytes()
        b=f.p.pcb.LoadBoard(str(source))
        net=f.p.pcb.NETINFO_ITEM(b,'OTHER');b.Add(net)
        t=f.p.pcb.PCB_TRACK(b);t.SetStart(f.p.vector(10,3));t.SetEnd(f.p.vector(10,7))
        t.SetWidth(250000);t.SetNetCode(net.GetNetCode());t.SetLayer(f.p.pcb.F_Cu);b.Add(t)
        f.p.pcb.SaveBoard(str(source),b)
        source.with_suffix('.kicad_pro').write_bytes(settings)
        with self.assertRaisesRegex(ValueError,'DRC failed'):self.build()
        self.assertFalse((self.root/'package').exists())


if __name__=='__main__':unittest.main()
