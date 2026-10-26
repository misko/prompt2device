"""Behavioral solid fixtures; these do not accept any real PCB or mating part."""
import math
from pathlib import Path
import tempfile
import unittest

import cadquery as cq
import mechanical_kernel as m


def box(x=2, y=2, z=2):
    return cq.Workplane('XY').box(x, y, z).val()


class MechanicalKernel(unittest.TestCase):
    def test_hollow_part_is_not_its_bounding_box(self):
        ring = cq.Workplane('XY').circle(5).circle(3).extrude(2).val()
        pin = cq.Workplane('XY').circle(1).extrude(2).val()
        result = m.measure_pair(ring, pin, 1.5)
        self.assertEqual(result['verdict'], 'PASS')
        self.assertAlmostEqual(result['distance_mm'], 2)
        self.assertEqual(result['intersection_mm3'], 0)
        self.assertEqual(m.measure_pair(ring, pin, 2.1)['verdict'], 'FAIL')

    def test_true_collision_and_vertical_clearance(self):
        a = box(); b = m.pose(box(), [1, 0, 0])
        result = m.measure_pair(a, b)
        self.assertEqual(result['verdict'], 'FAIL')
        self.assertAlmostEqual(result['intersection_mm3'], 4)
        b = m.pose(box(), [0, 0, 2.2])
        self.assertEqual(m.measure_pair(a, b, .19)['verdict'], 'PASS')
        self.assertEqual(m.measure_pair(a, b, .21)['verdict'], 'FAIL')

    def test_registration_rotation_translation_and_wrong_datum(self):
        src = [[0, 0, 0], [1, 0, 0], [0, 2, 0], [0, 0, 3]]
        dst = [[10, 20, 5], [10, 21, 5], [8, 20, 5], [10, 20, 8]]
        result = m.registration(src, dst, [10, 20, 5], [0, 0, 90], .001)
        self.assertEqual(result['verdict'], 'PASS')
        for shift, angle in [([10.1, 20, 5], [0, 0, 90]), ([10, 20, 5], [0, 0, -90])]:
            self.assertEqual(m.registration(src, dst, shift, angle, .001)['verdict'], 'FAIL')

    def test_reflection_scaling_degenerate_and_nonfinite(self):
        src = [[0, 0, 0], [1, 0, 0], [0, 2, 0], [0, 0, 3]]
        reflected = [[-x, y, z] for x, y, z in src]
        scaled = [[x*2, y*2, z*2] for x, y, z in src]
        for wrong in [reflected, scaled]:
            self.assertEqual(m.registration(src, wrong, [0, 0, 0], [0, 0, 0], .001)['verdict'], 'FAIL')
        with self.assertRaisesRegex(ValueError, 'degenerate'):
            m.registration([[0, 0, 0], [1, 0, 0], [2, 0, 0]],
                           [[0, 0, 0], [1, 0, 0], [2, 0, 0]], [0, 0, 0], [0, 0, 0], .1)
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            m.pose(box(), [math.nan, 0, 0])
        with self.assertRaisesRegex(ValueError, 'tolerance'):
            m.registration(src, src, [0, 0, 0], [0, 0, 0], math.inf)

    def test_bottom_mount_is_proper_rotation(self):
        self.assertAlmostEqual(m.point_pose([0, 1, 2], [0, 0, -1.6], [180, 0, 0])[2], -3.6)
        self.assertAlmostEqual(m.point_pose([0, 1, 2], [0, 0, -1.6], [180, 0, 0])[1], -1)

    def test_geometry_comparison_not_equal_bounds_or_volume(self):
        outer = box(10, 10, 2)
        drill = cq.Workplane('XY').circle(1).extrude(6).translate((2, 0, -3)).val()
        a = outer.cut(drill); b = outer.cut(m.pose(drill, [-4, 0, 0]))
        self.assertAlmostEqual(a.Volume(), b.Volume())
        self.assertEqual(m.bounds(a), m.bounds(b))
        self.assertEqual(m.compare_solids(a, b)['verdict'], 'FAIL')
        self.assertEqual(m.compare_solids(a, a)['verdict'], 'PASS')

    def test_step_export_reopen_population_holes_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'assembly.step'
            board = cq.Workplane('XY').box(20, 10, 1.6).faces('>Z').workplane().hole(2).val()
            parts = {'board': board, 'U1': m.pose(box(), [5, 0, 3]), 'J1': m.pose(box(), [-5, 0, 3])}
            result = m.export_step(parts, path)
            self.assertEqual(result['verdict'], 'PASS')
            self.assertEqual(result['solids_after'], 3)
            self.assertEqual(len(m.load_step(path).Solids()), 3)
            with self.assertRaisesRegex(ValueError, 'existing'): m.export_step(parts, path)
            link = Path(directory)/'linked.step'; link.symlink_to(path)
            with self.assertRaisesRegex(ValueError, 'regular'): m.load_step(link)

    def test_empty_non_solid_and_invalid_clearance(self):
        with self.assertRaisesRegex(ValueError, 'solids'):
            m.solid_check(cq.Workplane('XY').rect(2, 2).val())
        with self.assertRaisesRegex(ValueError, 'clearance'):
            m.measure_pair(box(), box(), -1)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'population'):
                m.export_step({}, Path(directory)/'empty.step')

    def test_free_vertex_and_unbounded_comparison_refused(self):
        contaminated = cq.Compound.makeCompound([box(), cq.Vertex.makeVertex(100, 0, 0)])
        with self.assertRaisesRegex(ValueError, 'non-solid'):
            m.solid_check(contaminated)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'contaminated.step'
            cq.exporters.export(contaminated, str(path))
            with self.assertRaisesRegex(ValueError, 'non-solid'): m.load_step(path)
        for tolerance in (math.inf, math.nan, -1, True):
            with self.assertRaisesRegex(ValueError, 'tolerance'):
                m.compare_solids(box(), box(3, 3, 3), tolerance, tolerance)

    def test_camera_missing_scene_does_not_produce_visual_evidence(self):
        frame = m.camera_frame([99, 99, 99, 101, 101, 101], [0, 0, 1], [0, 1, 0], 64, 64)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'blank'):
                m.render_png({'board': box()}, Path(directory)/'blank.png', frame)

    def test_common_camera_render_changes_body_not_frame(self):
        from PIL import Image, ImageChops
        board = box(20, 10, 1.6)
        parts = {'board': board, 'U1': m.pose(box(4, 4, 3), [0, 0, 2.3])}
        frame = m.camera_frame([-10, -5, -.8, 10, 5, 4], [0, 0, 1], [0, 1, 0], 320, 240)
        original = dict(frame)
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'bare.png', Path(directory)/'populated.png'
            m.render_png({'board': board}, a, frame); m.render_png(parts, b, frame)
            with Image.open(a) as bare, Image.open(b) as pop:
                self.assertEqual(bare.size, (320, 240)); self.assertEqual(pop.size, bare.size)
                self.assertIsNotNone(ImageChops.difference(bare, pop).getbbox())
                self.assertGreater(len(pop.getcolors(320*240)), 2)
        self.assertEqual(frame, original)


if __name__ == '__main__':
    unittest.main()
