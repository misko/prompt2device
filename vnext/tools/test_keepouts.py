"""Portable native ownership regressions; synthetic geometry is not board approval."""
from pathlib import Path
import tempfile
import unittest

import placement as p
import routing as r


class Keepouts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='vnext-keepouts-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'Area.kicad_mod').write_text('''(footprint "Area"
 (version 20260206) (generator "pcbnew") (layer "F.Cu")
 (zone (layers "F.Cu" "B.Cu")
  (uuid "00000000-0000-4000-8000-000000000001")
  (name "Curved restriction") (hatch edge 0.5)
  (connect_pads (clearance 0)) (min_thickness 0.25)
  (keepout (tracks not_allowed) (vias not_allowed) (pads not_allowed)
   (copperpour not_allowed) (footprints allowed))
  (fill (thermal_gap 0.5) (thermal_bridge_width 0.5))
  (polygon (pts (xy 0 0) (xy 2 0)
   (arc (start 2 0) (mid 3 1) (end 2 2)) (xy 0 2))))
 (group "original" (uuid "00000000-0000-4000-8000-000000000002")
  (members "00000000-0000-4000-8000-000000000001")))''')

    def fixture(self, angle=0, serialized=True):
        board = p.pcb.BOARD()
        f = p.pcb.FootprintLoad(str(self.root), 'Area')
        f.SetReference('U1'); f.SetPosition(p.vector(21.234567, 17.891011))
        f.SetOrientationDegrees(angle); board.Add(f)
        if not serialized: return board, f
        source = self.root/'original.kicad_pcb'; p.pcb.SaveBoard(str(source), board)
        board = p.pcb.LoadBoard(str(source))
        return board, board.FindFootprintByReference('U1')

    def signature(self, zone):
        q = zone.Outline()
        return (zone.GetLayerSet().FmtBin(), zone.GetIsRuleArea(), q.ArcCount(),
                tuple((q.CVertex(i).x, q.CVertex(i).y) for i in range(q.TotalVertices())),
                tuple((k, getattr(zone, k)()) for k in dir(zone) if k.startswith('GetDoNotAllow')))

    def test_curves_layers_flags_and_group_survive_all_supported_rotations(self):
        for angle in (0, 90, 180, 270):
            board, f = self.fixture(angle)
            before = self.signature(next(iter(f.Zones())))
            p.board_keepouts(board, ['U1'])
            target = self.root/'moved.kicad_pcb'; p.pcb.SaveBoard(str(target), board)
            fresh = p.pcb.LoadBoard(str(target))
            self.assertEqual(before, self.signature(next(iter(fresh.Zones()))))
            groups = list(fresh.Groups()); self.assertEqual(len(groups), 1)
            items = list(groups[0].GetItems()); self.assertEqual(len(items), 2)
            self.assertEqual({x.m_Uuid.AsString() for x in items},
                             {fresh.FindFootprintByReference('U1').m_Uuid.AsString(),
                              next(iter(fresh.Zones())).m_Uuid.AsString()})
            self.assertTrue(all(not list(g.GetItems()) for g in fresh.FindFootprintByReference('U1').Groups()))

    def test_routing_binds_keepout_and_group_but_allows_copper(self):
        board, _ = self.fixture(); p.board_keepouts(board, ['U1'])
        base = self.root/'base.kicad_pcb'; p.pcb.SaveBoard(str(base), board)
        expected = r.identity(base)
        for mutation in ('remove', 'weaken', 'move', 'layer', 'ungroup', 'detach', 'copper'):
            b = p.pcb.LoadBoard(str(base)); z = next(iter(b.Zones()))
            if mutation == 'remove':
                next(iter(b.Groups())).RemoveItem(z); b.Remove(z)
            elif mutation == 'weaken': z.SetDoNotAllowTracks(False)
            elif mutation == 'move': z.Move(p.vector(.1, 0))
            elif mutation == 'layer': z.SetLayer(p.pcb.F_Cu)
            elif mutation == 'ungroup':
                group = next(iter(b.Groups()))
                for item in list(group.GetItems()): group.RemoveItem(item)
                b.Remove(group)
            elif mutation == 'detach': next(iter(b.Groups())).RemoveItem(z)
            else:
                t = p.pcb.PCB_TRACK(b); t.SetStart(p.vector(1, 1)); t.SetEnd(p.vector(2, 1))
                t.SetLayer(p.pcb.F_Cu); t.SetWidth(200000); b.Add(t)
            target = self.root/(mutation+'.kicad_pcb'); p.pcb.SaveBoard(str(target), b)
            if mutation == 'copper': self.assertEqual(expected, r.identity(target))
            else: self.assertNotEqual(expected, r.identity(target), mutation)

    def test_missing_owner_and_non_rule_area_fail(self):
        board, f = self.fixture()
        with self.assertRaisesRegex(ValueError, 'missing keepout owner'):
            p.board_keepouts(board, ['UNKNOWN'])
        next(iter(f.Zones())).SetIsRuleArea(False)
        with self.assertRaisesRegex(ValueError, 'owner needs rule areas'):
            p.board_keepouts(board, ['U1'])

    def test_producer_first_save_preserves_native_world_geometry(self):
        for angle in (0, 90, 180, 270):
            original, f = self.fixture(angle)
            expected = self.signature(next(iter(f.Zones())))
            candidate, _ = self.fixture(angle, serialized=False)
            p.board_keepouts(candidate, ['U1'])
            target = self.root/'first-save.kicad_pcb'; p.pcb.SaveBoard(str(target), candidate)
            reloaded = p.pcb.LoadBoard(str(target))
            self.assertEqual(expected, self.signature(next(iter(reloaded.Zones()))))

    def test_malformed_declarations_rejected(self):
        data = {'boards':{'b':{'_components':[{'ref':'U1'}]}}}
        board = dict(outline=[30,30], layers=2, layer_plan='ground reference',
                     placements={'U1':[10,10,0]}, mounts=[], notes='fixture',
                     blocks=[{'id':'one','members':['U1']}])
        for value in ('U1', ['UNKNOWN'], ['U1','U1'], [None], {}):
            with self.assertRaisesRegex(ValueError, 'invalid board keepout owners'):
                p.validate_plan(data, {'version':1, 'boards':{'b':dict(board, board_keepouts=value)}})


if __name__ == '__main__': unittest.main()
