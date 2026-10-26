"""Namespace/NC regressions; source semantics must survive native placement."""
import unittest
import xml.etree.ElementTree as ET

import placement as p
import native_identity_repair as migration
import test_routing


def tree(rows):
    root=ET.Element('export');nets=ET.SubElement(root,'nets')
    for name,members in rows:
        net=ET.SubElement(nets,'net',name=name)
        for ref,pin,kind in members:ET.SubElement(net,'node',ref=ref,pin=pin,pintype=kind)
    return ET.ElementTree(root)


class Namespace(unittest.TestCase):
    def test_native_names_and_isolated_nc_preserved(self):
        components=[dict(ref='U1',pins=[dict(number='1',net='GND'),dict(number='2',nc=True)])]
        source=tree([('/GND',[('U1','1','passive')]),
                     ('unconnected-(U1-Pad2)',[('U1','2','passive+no_connect')])])
        self.assertEqual(p.native_net_names(components,source),{'GND':'/GND'})
        self.assertEqual(p.native_pin_nets(components,source),
                         {('U1','1'):'/GND',('U1','2'):'unconnected-(U1-Pad2)'})

    def test_ambiguous_namespace_and_duplicate_pin_rejected(self):
        components=[dict(ref='U1',pins=[dict(number='1',net='N'),dict(number='2',net='N')])]
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            p.native_net_names(components,tree([('/N',[('U1','1','passive')]),('N',[('U1','2','passive')])]))
        with self.assertRaisesRegex(ValueError,'duplicate'):
            p.native_net_names(components,tree([('/N',[('U1','1','passive'),('U1','1','passive')])]))

    def test_nc_must_really_be_isolated_not_hidden_connectivity(self):
        components=[dict(ref='U1',pins=[dict(number='1',nc=True)])]
        for name,nodes in [('/GND',[('U1','1','passive')]),
                           ('unconnected-X',[('U1','1','no_connect'),('U2','1','no_connect')])]:
            with self.assertRaisesRegex(ValueError,'isolated'):
                p.native_pin_nets(components,tree([(name,nodes)]))


class Migration(test_routing.Native):
    # Only the migration cases are relevant here; the inherited fixture also runs
    # routing controls, exercising unchanged geometry behavior after the fix.
    def netlist(self,split=False):
        source=tree([('/N',[('U1','1','passive')]+([] if split else [('U2','1','passive')]))]+
                    ([('/OTHER',[('U2','1','passive')])] if split else []))
        comps=ET.SubElement(source.getroot(),'components')
        for ref in ('U1','U2'):
            c=ET.SubElement(comps,'comp',ref=ref)
            ET.SubElement(c,'value').text='Pad';ET.SubElement(c,'footprint').text='Test:Pad'
        target=self.root/'native.xml';source.write(target);return target

    def test_metadata_migration_preserves_complete_native_geometry(self):
        # Output outside input resource directory avoids copying it into itself.
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'candidate'
            report=migration.repair(self.root/'source.kicad_pcb',self.netlist(),out)
            self.assertTrue(report['complete_inverse_delta_verified'])
            self.assertEqual(report['renames'],{'N':'/N'})
            board=p.pcb.LoadBoard(str(out/'native/source.kicad_pcb'))
            self.assertEqual({pad.GetNetname() for fp in board.GetFootprints() for pad in fp.Pads()},{'/N'})
            self.assertFalse(report['acceptance'])

    def test_real_connectivity_change_cannot_be_called_namespace_repair(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'namespace'):
                migration.repair(self.root/'source.kicad_pcb',self.netlist(split=True),Path(d)/'candidate')


if __name__=='__main__':unittest.main()
