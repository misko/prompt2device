"""Native edge recesses must preserve electronics and fail closed on omissions."""
import copy
import json
import math
import unittest
from unittest.mock import patch
import placement as p
import test_placement as fixtures
from test_placement import fp


def notch(edge='north'):
    return dict(edge=edge,start_mm=18,end_mm=26,depth_mm=3,radius_mm=.5,
                overhang_refs=[],reason='Synthetic service opening',evidence=['notch.md'])


class Notches(unittest.TestCase):
    def setUp(self):
        fixtures.NativeReplay.setUp(self)
        self.put('notch.md','Synthetic engineering evidence; not actual acceptance.')
        self.plan=p.read(self.root/'plan.json');self.b=self.plan['boards']['board']
        self.b['edge_notches']=[notch()]

    def save(self):self.put('notched.json',json.dumps(self.plan))

    def test_four_edges_have_closed_native_outlines_with_expected_area(self):
        for edge in ('north','east','south','west'):
            with self.subTest(edge=edge):
                self.b['edge_notches']=[notch(edge)];self.save()
                p.build(self.root,'inputs.json','notched.json','out-'+edge)
                board=p.pcb.LoadBoard(str(self.root/('out-'+edge) / 'board.kicad_pcb'))
                outline=p.pcb.SHAPE_POLY_SET()
                self.assertTrue(board.GetBoardPolygonOutlines(outline,False))
                self.assertAlmostEqual(outline.Area()/1e12,900-24+2*(.25-math.pi*.25/4),delta=.002)
                self.assertEqual(sum(x.GetShape()==p.pcb.SHAPE_T_ARC for x in board.GetDrawings()),2)

    def test_build_replay_preserves_pads_and_binds_evidence(self):
        self.save();p.build(self.root,'inputs.json','notched.json','candidate')
        a=p.observe(self.root/'out/board.kicad_pcb');b=p.observe(self.root/'candidate/board.kicad_pcb')
        self.assertEqual(a,b)
        with patch.object(p,'upstream',return_value={}):
            result=p.verify(self.root,'inputs.json','notched.json','candidate')
        self.assertEqual(result['checks']['board']['verdict'],'PASS')
        self.assertEqual(result['subjects']['notch.md'],p.sha(self.root/'notch.md'))

    def test_changed_shape_rejects_existing_output(self):
        self.save();p.build(self.root,'inputs.json','notched.json','candidate')
        self.b['edge_notches'][0]['depth_mm']=3.5;self.save()
        with patch.object(p,'upstream',return_value={}):
            with self.assertRaisesRegex(ValueError,'native placement replay differs'):
                p.verify(self.root,'inputs.json','notched.json','candidate')

    def test_invalid_recesses_rejected(self):
        for key,value in [('edge','diagonal'),('start_mm',0),('end_mm',30),
                          ('radius_mm',0),('radius_mm',3),('depth_mm',30),
                          ('depth_mm',float('nan')),('depth_mm',3.000000001),
                          ('overhang_refs',['MISSING']),('overhang_refs',['U1','U1']),
                          ('evidence',[])]:
            with self.subTest(key=key,value=value):
                self.b['edge_notches']=[{**notch(),key:value}]
                with self.assertRaises(ValueError):p.edge_notches(self.b)

    def test_overlapping_recesses_rejected(self):
        self.b['edge_notches']=[notch(),{**notch(), 'start_mm':20}]
        with self.assertRaisesRegex(ValueError,'overlapping'):p.edge_notches(self.b)

    def test_missing_evidence_rejected(self):
        self.b['edge_notches'][0]['evidence']=['missing.md'];self.save()
        with self.assertRaisesRegex(ValueError,'missing input'):p.load(self.root,'inputs.json','notched.json')

    def test_body_overhang_does_not_waive_electrical_pads(self):
        parts={'U1':fp(20,1)};spec={'_components':[{'ref':'U1'}]}
        self.b['edge_notches'][0]['overhang_refs']=['U1']
        failures=p.geometry(spec,self.b,parts)['failures']
        self.assertIn('notch-pad:U1',failures);self.assertNotIn('notch-body:U1',failures)
        self.b['edge_notches'][0]['overhang_refs']=[]
        self.assertIn('notch-body:U1',p.geometry(spec,self.b,parts)['failures'])

    def test_mount_and_reservation_cannot_be_waived(self):
        spec={'_components':[]};parts={'MH1':fp(20,1)}
        self.assertIn('notch-pad:MH1',p.geometry(spec,self.b,parts)['failures'])
        self.b['reservations']=[dict(id='escape',rect=[20,1,22,2],layer='F.Cu',owner_refs=[])]
        self.assertIn('reservation-notch:escape',p.geometry(spec,self.b,{})['failures'])


if __name__=='__main__':unittest.main()
