"""Native exporter components, not fabrication or release acceptance."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import fab_payload as f
import test_routing as fixture


class Native(unittest.TestCase):
    write=fixture.Native.write
    def setUp(self):fixture.Native.setUp(self)

    def test_native_layer_drill_zip_census_and_replot(self):
        one=f.native_payload(self.root/'source.kicad_pcb',self.root/'one')
        two=f.native_payload(self.root/'source.kicad_pcb',self.root/'two')
        self.assertEqual(len(one['members']),11)
        self.assertEqual(one['members'],two['members'])
        for n in one['members']:
            self.assertEqual(f.canonical_plot(self.root/'one/plots'/n),
                             f.canonical_plot(self.root/'two/plots'/n))
        with zipfile.ZipFile(self.root/'one/source-gerbers.zip') as z:
            self.assertEqual(z.namelist(),one['members'])
            self.assertFalse(any(n.endswith('.csv') for n in z.namelist()))
        self.write('one/plots/stale.g2','old copper')
        with self.assertRaisesRegex(ValueError,'census'):
            f.census(self.root/'one/plots','source',one['layers'])

    def test_existing_output_preserved(self):
        (self.root/'out').mkdir();self.write('out/keep','x')
        with self.assertRaisesRegex(ValueError,'existing'):
            f.native_payload(self.root/'source.kicad_pcb',self.root/'out')
        self.assertEqual((self.root/'out/keep').read_text(),'x')

    def test_layer_swap_and_drill_stub_rejected(self):
        result=f.native_payload(self.root/'source.kicad_pcb',self.root/'out')
        plots=self.root/'out/plots'
        front=plots/'source-F_Cu.gbr';back=plots/'source-B_Cu.gbr'
        saved=front.read_bytes();front.write_bytes(back.read_bytes())
        with self.assertRaisesRegex(ValueError,'Gerber function'):f.census(plots,'source',result['layers'])
        front.write_bytes(saved)
        self.write('out/plots/source-PTH.drl','M48\nM30\n')
        with self.assertRaisesRegex(ValueError,'incomplete drill'):f.census(plots,'source',result['layers'])

    def test_current_seal_is_mandatory(self):
        with patch.object(f.seal,'check',side_effect=ValueError('layout seal missing')):
            with self.assertRaisesRegex(ValueError,'seal missing'):f.export(self.root,'out')
        self.assertFalse((self.root/'out').exists())

    def test_four_layer_role_order_and_missing_drill_hit(self):
        board=f.p.pcb.LoadBoard(str(self.root/'source.kicad_pcb'));board.SetCopperLayerCount(4)
        via=f.p.pcb.PCB_VIA(board);via.SetPosition(f.p.vector(10,5))
        via.SetWidth(600000);via.SetDrill(300000);via.SetLayerPair(f.p.pcb.F_Cu,f.p.pcb.B_Cu)
        via.SetNetCode(board.FindNet('N').GetNetCode());board.Add(via)
        f.p.pcb.SaveBoard(str(self.root/'four.kicad_pcb'),board)
        result=f.native_payload(self.root/'four.kicad_pcb',self.root/'out')
        self.assertEqual(result['layers'][:4],['F.Cu','In1.Cu','In2.Cu','B.Cu'])
        self.assertEqual(result['drill_counts'],{'PTH':1,'NPTH':0})
        drill=self.root/'out/plots/four-PTH.drl'
        drill.write_text('\n'.join(line for line in drill.read_text().splitlines() if not line.startswith('X'))+'\n')
        with self.assertRaisesRegex(ValueError,'drill hit census'):
            f.census(self.root/'out/plots','four',result['layers'],result['drill_counts'])

    def test_failed_export_does_not_promote(self):
        receipt={'review':'review'};review={'manifest':'m.json','output':'sealed'}
        self.write('m.json',json.dumps({'boards':{'test':{}}}))
        self.write('sealed/test/native/test.kicad_pcb',(self.root/'source.kicad_pcb').read_text())
        self.write(f.seal.RECEIPT,'fixture receipt, not acceptance')
        with patch.object(f.seal,'check',return_value=receipt), \
             patch.object(f.seal.r,'review_json',return_value=review), \
             patch.object(f,'native_payload',side_effect=ValueError('producer interrupted')):
            with self.assertRaisesRegex(ValueError,'producer interrupted'):f.export(self.root,'out')
        self.assertFalse((self.root/'out').exists())

    def test_geometry_not_normalized_away(self):
        self.write('a.gbr','%TF.CreationDate,old*%\nX100Y200D01*\nM02*\n')
        self.write('b.gbr','%TF.CreationDate,new*%\nX100Y201D01*\nM02*\n')
        self.assertNotEqual(f.canonical_plot(self.root/'a.gbr'),f.canonical_plot(self.root/'b.gbr'))


if __name__=='__main__':unittest.main()
