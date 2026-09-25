"""Native KiCad fixtures for the strict five-terminal tree contract."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import critical_tree_check as check  # noqa: E402
import route_acceptance_gate as gate  # noqa: E402


def pt(x,y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))


def add_pad(board,ref,xy,net='TREE'):
    fp=pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue('test')
    fp.SetLayer(pcbnew.F_Cu)
    fp.SetPosition(pt(*xy))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    p=pcbnew.PAD(fp)
    p.SetNumber('1')
    p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p.SetShape(pcbnew.PAD_SHAPE_RECT)
    p.SetSize(pt(.4,.4))
    p.SetPosition(pt(*xy))
    p.SetLayerSet(pcbnew.LSET.FrontMask())
    p.SetNet(board.FindNet(net))
    fp.Add(p)
    board.Add(fp)


def add_track(board,a,b,layer=pcbnew.F_Cu):
    item=pcbnew.PCB_TRACK(board)
    item.SetStart(pt(*a))
    item.SetEnd(pt(*b))
    item.SetWidth(pcbnew.FromMM(.2))
    item.SetLayer(layer)
    item.SetNet(board.FindNet('TREE'))
    board.Add(item)
    return item


def add_ground_anchor(board):
    fp=pcbnew.FOOTPRINT(board)
    fp.SetReference('GND_ANCHOR')
    fp.SetValue('test')
    fp.SetPosition(pt(1.5,1.5))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    p=pcbnew.PAD(fp)
    p.SetNumber('1')
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(pt(.6,.6))
    p.SetDrillSize(pt(.3,.3))
    p.SetPosition(pt(1.5,1.5))
    p.SetLayerSet(pcbnew.LSET.AllCuMask())
    p.SetNet(board.FindNet('GND'))
    fp.Add(p)
    board.Add(fp)


def poly(points):
    p=pcbnew.SHAPE_POLY_SET()
    index=p.NewOutline()
    for xy in points:
        p.Append(pt(*xy),index)
    return p


class CriticalTreeTest(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/'board.kicad_pcb'
        self.board=pcbnew.BOARD()
        self.board.SetCopperLayerCount(4)
        for net in ('TREE','GND'):
            self.board.Add(pcbnew.NETINFO_ITEM(self.board,net))
        add_ground_anchor(self.board)
        self.positions={'A':(2,5),'B':(5,2),'C':(5,8),'D':(7,2),'E':(9,5)}
        for ref,xy in self.positions.items():
            add_pad(self.board,ref,xy)
        t1,t2=(5,5),(7,5)
        for a,b in [(self.positions['A'],t1),(self.positions['B'],t1),
                    (self.positions['C'],t1),(t1,t2),
                    (self.positions['D'],t2),(self.positions['E'],t2)]:
            add_track(self.board,a,b)
        self.fill=[(1,1),(10,1),(10,9),(1,9)]
        self.declaration={'net':'TREE','pads':[f'{ref}.1' for ref in self.positions],
            'signal_layer':'F.Cu','reference_layer':'In1.Cu','reference_net':'GND',
            'reference_anchor':'GND_ANCHOR.1',
            'max_vias':0,'tees':[
                {'at':[5,5],'layer':'F.Cu','degree':4,'why':'first fanout'},
                {'at':[7,5],'layer':'F.Cu','degree':3,'why':'second fanout'}]}

    def save(self,filled=True):
        zone=pcbnew.ZONE(self.board)
        zone.SetLayer(pcbnew.In1_Cu)
        zone.SetNet(self.board.FindNet('GND'))
        shape=poly(self.fill)
        zone.Outline().Append(shape)
        if filled:
            zone.SetFilledPolysList(pcbnew.In1_Cu,shape)
            zone.SetIsFilled(True)
        self.board.Add(zone)
        pcbnew.SaveBoard(str(self.path),self.board)
        return check.inspect(self.path,[self.declaration])

    def assert_failed(self,needle,filled=True):
        result=self.save(filled)
        self.assertEqual(result['status'],'FAIL',result)
        self.assertIn(needle,result['trees'][0]['reason'])

    def test_exact_five_terminal_tree_and_filled_reference(self):
        result=self.save()
        self.assertEqual(result['status'],'PASS',result)
        self.assertEqual(result['trees'][0]['pad_count'],5)
        self.assertEqual(result['trees'][0]['tee_count'],2)
        required=gate._required_checks('quick',[],
            {'route':{'critical_trees':[self.declaration]}},None)
        self.assertIn('critical_trees',required)
        self.assertNotIn('critical_trees',gate._required_checks('quick',[],{'route':{}},None))
        self.assertEqual(gate._admission({'critical_trees':{'status':'FAIL'}},
                                         ['critical_trees'])[0],'REJECTED')

    def test_extra_same_net_pad_rejected(self):
        add_pad(self.board,'EXTRA',(3,8))
        self.assert_failed('exact native pad set mismatch')

    def test_duplicate_native_pad_identity_rejected(self):
        fp=next(f for f in self.board.GetFootprints() if f.GetReference()=='A')
        extra=pcbnew.PAD(fp)
        extra.SetNumber('1')
        extra.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        extra.SetShape(pcbnew.PAD_SHAPE_RECT)
        extra.SetSize(pt(.4,.4))
        extra.SetPosition(pt(2,5.8))
        extra.SetLayerSet(pcbnew.LSET.FrontMask())
        extra.SetNet(self.board.FindNet('TREE'))
        fp.Add(extra)
        self.assert_failed('exact native pad set mismatch')

    def test_undeclared_tee_and_cycle_rejected(self):
        self.declaration['tees'].pop()
        self.assert_failed('declared tee inventory')

    def test_unfilled_and_partial_reference_rejected(self):
        self.assert_failed('no saved filled reference',filled=False)

    def test_partial_reference_rejected(self):
        self.fill=[(1,1),(6,1),(6,9),(1,9)]
        self.assert_failed('lacks continuous saved filled reference')

    def test_disconnected_reference_island_rejected(self):
        island=pcbnew.ZONE(self.board)
        island.SetLayer(pcbnew.In1_Cu)
        island.SetNet(self.board.FindNet('GND'))
        shape=poly([(11,1),(12,1),(12,2),(11,2)])
        island.Outline().Append(shape)
        island.SetFilledPolysList(pcbnew.In1_Cu,shape)
        island.SetIsFilled(True)
        self.board.Add(island)
        self.assert_failed('disconnected islands')

    def test_reference_anchor_required(self):
        self.declaration['reference_anchor']='MISSING.1'
        self.assert_failed('reference anchor')

    def test_via_or_unsupported_via_budget_rejected(self):
        self.declaration['max_vias']=1
        self.assert_failed('requires zero vias')

    def test_realized_via_rejected(self):
        via=pcbnew.PCB_VIA(self.board)
        via.SetPosition(pt(6,5))
        via.SetWidth(pcbnew.FromMM(.6))
        via.SetDrill(pcbnew.FromMM(.3))
        via.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu)
        via.SetNet(self.board.FindNet('TREE'))
        self.board.Add(via)
        self.assert_failed('via exceeds zero-via limit')

    def test_cycle_rejected(self):
        add_track(self.board,(5,5),(6,4))
        add_track(self.board,(6,4),(7,5))
        self.assert_failed('cycle')

    def test_spur_rejected(self):
        add_track(self.board,(7,5),(8,8))
        self.assert_failed('declared tee inventory')

    def test_hidden_midsegment_tee_rejected(self):
        add_track(self.board,(6,5),(6,7))
        self.assert_failed('undeclared copper contact')


if __name__=='__main__':
    unittest.main()
