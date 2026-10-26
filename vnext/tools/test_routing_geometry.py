"""Native assembly-geometry controls independent of any particular board."""
from pathlib import Path
import tempfile
import unittest
import pcbnew as p
from routing_geometry import screen


def layers(*values):
    result=p.LSET()
    for value in values: result.AddLayer(value)
    return result


class NativeAssemblyGeometry(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='vnext-via-pad-')
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'board.kicad_pcb'
        self.board = p.BOARD()
        self.board.SetCopperLayerCount(4)
        self.net = p.NETINFO_ITEM(self.board, 'GND')
        self.board.Add(self.net)
        foot = p.FOOTPRINT(self.board)
        foot.SetReference('C1')
        self.pad = p.PAD(foot)
        self.pad.SetNumber('1')
        self.pad.SetAttribute(p.PAD_ATTRIB_SMD)
        self.pad.SetShape(p.PAD_SHAPE_RECT)
        self.pad.SetSize(p.VECTOR2I(1000000,1000000))
        self.pad.SetPosition(p.VECTOR2I(10000000,10000000))
        self.pad.SetLayerSet(layers(p.F_Cu,p.F_Mask,p.F_Paste))
        self.pad.SetNet(self.net)
        foot.Add(self.pad)
        self.board.Add(foot)
        self.via = p.PCB_VIA(self.board)
        self.via.SetPosition(p.VECTOR2I(10000000,10000000))
        self.via.SetWidth(600000)
        self.via.SetDrill(300000)
        self.via.SetViaType(p.VIATYPE_THROUGH)
        self.via.SetLayerPair(p.F_Cu,p.B_Cu)
        self.via.SetNet(self.net)
        self.board.Add(self.via)

    def run_screen(self, gap=0):
        p.SaveBoard(str(self.path),self.board)
        return screen(self.path,gap)

    def test_same_net_drill_intersection_is_detected(self):
        result = self.run_screen()
        self.assertEqual(len(result['via_drill_smd_overlaps']),1)
        self.assertEqual(result['via_drill_smd_overlaps'][0]['ref'],'C1')
        self.assertEqual(len(result['tool_sha256']),64)

    def test_different_net_does_not_hide_assembly_geometry(self):
        other = p.NETINFO_ITEM(self.board,'OTHER'); self.board.Add(other)
        self.via.SetNet(other)
        self.assertEqual(len(self.run_screen()['via_drill_smd_overlaps']),1)

    def test_clearance_is_an_explicit_allocation(self):
        self.via.SetPosition(p.VECTOR2I(10900000,10000000))
        self.assertFalse(self.run_screen()['via_annulus_smd_gap_findings'])
        self.assertEqual(len(self.run_screen(.15)['via_annulus_smd_gap_findings']),1)
        self.assertFalse(self.run_screen(.15)['via_drill_smd_overlaps'])

    def test_repair_clears_hole_and_declared_annulus_gap(self):
        self.via.SetPosition(p.VECTOR2I(11100000,10000000))
        result = self.run_screen(.15)
        self.assertFalse(result['via_drill_smd_overlaps'])
        self.assertFalse(result['via_annulus_smd_gap_findings'])

    def test_effective_shape_not_rotated_pad_bounding_box(self):
        self.pad.SetSize(p.VECTOR2I(3000000,300000))
        self.pad.SetOrientation(p.EDA_ANGLE(45,p.DEGREES_T))
        self.via.SetPosition(p.VECTOR2I(10900000,10900000))
        result = self.run_screen()
        self.assertFalse(result['via_drill_smd_overlaps'])
        self.assertFalse(result['via_annulus_smd_gap_findings'])

    def test_blind_via_does_not_intersect_opposite_face_pad(self):
        self.pad.SetLayerSet(layers(p.B_Cu,p.B_Mask,p.B_Paste))
        self.via.SetViaType(p.VIATYPE_BLIND)
        self.via.SetLayerPair(p.F_Cu,p.In1_Cu)
        result = self.run_screen()
        self.assertFalse(result['via_drill_smd_overlaps'])
        self.assertFalse(result['via_annulus_smd_gap_findings'])

    def test_invalid_clearance_rejected(self):
        for gap in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError): screen(self.path,gap)


if __name__ == '__main__': unittest.main()
