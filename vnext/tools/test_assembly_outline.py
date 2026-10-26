"""Native outline display is not a surrogate solid-fit acceptance."""
import unittest
import assembly_verify as a

class Outline(unittest.TestCase):
    def board(self,open_edge=False):
        b=a.p.pcb.BOARD()
        points=[(0,0),(12,0),(12,2),(18,2),(18,0),(30,0),(30,20),(0,20),(0,0)]
        for start,end in zip(points,points[1:]):
            if open_edge and start==(0,20):continue
            edge=a.p.pcb.PCB_SHAPE(b);edge.SetShape(a.p.pcb.S_SEGMENT)
            edge.SetLayer(a.p.pcb.Edge_Cuts);edge.SetStart(a.p.vector(*start));edge.SetEnd(a.p.vector(*end));b.Add(edge)
        return b

    def test_recess_is_retained_not_replaced_with_bounding_box(self):
        b=self.board();points=a.outline_contour(b)
        self.assertIn([12,2],points);self.assertIn([18,2],points)
        self.assertEqual(a.outline(b),[0,0,30,20])
        data=dict(outline=a.outline(b),outline_contour=points,references={},access=[],native_pads=[])
        for mounted in (False,True):
            view=a.svg('synthetic',data,mounted)
            self.assertIn('<polygon points=',view)
            self.assertIn('registered STEP owns clearance',view)

    def test_open_native_outline_rejected(self):
        with self.assertRaisesRegex(ValueError,'open/disjoint'):a.outline(self.board(True))

    def test_closed_disjoint_outline_rejected(self):
        b=self.board()
        e=a.p.pcb.PCB_SHAPE(b);e.SetShape(a.p.pcb.S_RECT);e.SetLayer(a.p.pcb.Edge_Cuts)
        e.SetStart(a.p.vector(40,0));e.SetEnd(a.p.vector(50,10));b.Add(e)
        with self.assertRaisesRegex(ValueError,'open/disjoint'):a.outline_contour(b)

    def test_internal_cutout_rejected(self):
        b=self.board()
        e=a.p.pcb.PCB_SHAPE(b);e.SetShape(a.p.pcb.S_RECT);e.SetLayer(a.p.pcb.Edge_Cuts)
        e.SetStart(a.p.vector(2,5));e.SetEnd(a.p.vector(4,8));b.Add(e)
        with self.assertRaisesRegex(ValueError,'internal-cutout'):a.outline(b)

    def test_four_sided_nonrectangle_is_not_rectangularized(self):
        b=a.p.pcb.BOARD();points=[(5,0),(20,5),(5,20),(0,5),(5,0)]
        for start,end in zip(points,points[1:]):
            e=a.p.pcb.PCB_SHAPE(b);e.SetShape(a.p.pcb.S_SEGMENT);e.SetLayer(a.p.pcb.Edge_Cuts)
            e.SetStart(a.p.vector(*start));e.SetEnd(a.p.vector(*end));b.Add(e)
        self.assertEqual(a.outline(b),[0,0,20,20])
        contour=a.outline_contour(b)
        self.assertEqual(set(map(tuple,contour)),set(points))
        data=dict(outline=a.outline(b),outline_contour=contour,references={},access=[],native_pads=[])
        self.assertIn('<polygon points=',a.svg('synthetic',data,True))

if __name__=='__main__':unittest.main()
