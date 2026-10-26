"""Real-solid scene regressions; no production board is accepted by fixtures."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import mechanical_scene as m


class Scene(unittest.TestCase):
    def test_finished_board_envelope_preserves_holes_not_dielectric_height(self):
        raw = m.cq.Workplane('XY').box(20, 10, 1.4842).faces('>Z').workplane().hole(2).val()
        result = m.finished_board_envelope(raw, 1.6)
        self.assertAlmostEqual(m.k.bounds(result)[2], -1.6)
        self.assertAlmostEqual(m.k.bounds(result)[5], 0)
        self.assertAlmostEqual(result.Volume(), (200-3.141592653589793)*1.6, places=5)
        pin = m.cq.Workplane('XY').circle(.5).extrude(-1.6).val()
        self.assertEqual(m.k.measure_pair(result, pin)['verdict'], 'PASS')
        with self.assertRaisesRegex(ValueError, 'thickness'):
            m.finished_board_envelope(raw, float('inf'))

    def test_native_to_right_handed_cardinal_transform(self):
        body = dict(shape='box', bounds=[1, 2, 3, 4], z=[0, 1])
        solid = m.k.pose(m.envelope(body), [10, -20, 0], [0, 0, 90])
        expected = [12, -19, 0, 14, -17, 1]
        for a, b in zip(m.k.bounds(solid), expected): self.assertAlmostEqual(a, b)

    def test_pairs_use_solids_not_overlapping_boxes(self):
        ring = m.cq.Workplane('XY').circle(5).circle(3).extrude(2).val()
        pin = m.cq.Workplane('XY').circle(1).extrude(2).val()
        far = pin.translate((30, 0, 0))
        result = m.pair_checks({'ring': ring, 'pin': pin, 'far': far}, 1.5)
        self.assertEqual(result['verdict'], 'PASS')
        self.assertEqual(result['total_pairs'], 3)
        self.assertEqual(result['separated_by_bounds_lower_limit'], 2)
        self.assertEqual(len(result['kernel_pairs']), 1)
        self.assertAlmostEqual(result['kernel_pairs'][0]['distance_mm'], 2)
        self.assertEqual(m.pair_checks({'ring': ring, 'pin': pin}, 2.1)['verdict'], 'FAIL')

    def test_no_component_collision_exemption(self):
        a = m.cq.Workplane('XY').box(2, 2, 2).val()
        result = m.pair_checks({'board': a, 'U1': a.translate((.5, 0, 0))})
        self.assertEqual(result['verdict'], 'FAIL')
        self.assertGreater(result['failures'][0]['intersection_mm3'], 0)
        with self.assertRaisesRegex(ValueError, 'reserved'):
            m.assemble_parts(a, {'board': a})

    def test_access_checks_the_owner_as_well_as_neighbors(self):
        a = m.cq.Workplane('XY').box(2, 2, 2).val()
        declaration = [dict(id='socket', ref='J1', bounds=[-.5, -.5, .5, .5], z=[0, 1])]
        result = m.access_checks({'J1': a}, declaration)
        self.assertEqual(result[0]['verdict'], 'FAIL')
        self.assertEqual(result[0]['measurements'][0]['reference'], 'J1')

    def test_3d_witness_rejects_coplanar_and_mirrored_landmarks(self):
        with self.assertRaisesRegex(ValueError, 'coplanar'):
            m.noncoplanar([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])
        src = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
        m.noncoplanar(src)
        self.assertEqual(m.k.registration(src, [[-x, y, z] for x, y, z in src],
                                          [0, 0, 0], [0, 0, 0], .001)['verdict'], 'FAIL')

    def test_step_retained_evidence_pose_and_stale_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            m.k.export_step({'test': m.cq.Workplane('XY').box(2, 2, 2).val()}, root/'test.step')
            (root/'maker.txt').write_text('synthetic independent dimensions')
            points = [[1, 1, 1], [-1, 1, 1], [1, -1, 1], [1, 1, -1]]
            row = dict(path='test.step', translation=[0, 0, 0], rotation=[0, 0, 0],
                       local_landmarks=points, expected_landmarks=points, tolerance_mm=.001,
                       landmark_features=[dict(kind='surface') for _ in points],
                       evidence=['maker.txt'], limitations=['Synthetic fixture, not maker evidence'])
            subjects = {}; shape, report = m.step_model(root, row, subjects)
            self.assertEqual(report['registration']['verdict'], 'PASS')
            self.assertEqual(set(subjects), {'test.step', 'maker.txt'})
            m.k.export_step({'wrong': m.cq.Workplane('XY').box(20, 20, 20).val()}, root/'wrong.step')
            wrong = copy.deepcopy(row); wrong['path'] = 'wrong.step'
            with self.assertRaisesRegex(ValueError, 'STEP feature'):
                m.step_model(root, wrong, {})
            wrong = copy.deepcopy(row); wrong['translation'][2] = .2
            with self.assertRaisesRegex(ValueError, 'registration failed'):
                m.step_model(root, wrong, {})

            wrong = copy.deepcopy(row); wrong['evidence'] = []
            with self.assertRaisesRegex(ValueError, 'evidence required'):
                m.step_model(root, wrong, {})
            wrong = copy.deepcopy(row); wrong['evidence'] = ['test.step']
            with self.assertRaisesRegex(ValueError, 'only the STEP'):
                m.step_model(root, wrong, {})
            (root/'linked.step').symlink_to(root/'test.step'); wrong = copy.deepcopy(row)
            wrong['path'] = 'linked.step'
            with self.assertRaisesRegex(ValueError, 'linked'):
                m.step_model(root, wrong, {})

    def test_circle_witness_binds_radius_and_center(self):
        ring = m.cq.Workplane('XY').circle(5).circle(3).extrude(2).val()
        point = [[0, 0, 0]]
        self.assertEqual(len(m.bind_features(ring, point, [dict(kind='circle_center', radius_mm=3)])), 1)
        for point, radius in [([[0, 0, 0]], 2), ([[1, 0, 0]], 3)]:
            with self.assertRaisesRegex(ValueError, 'STEP feature'):
                m.bind_features(ring, point, [dict(kind='circle_center', radius_mm=radius)])


if __name__ == '__main__': unittest.main()
