"""Positive and hostile controls for source-only geometry helpers."""
import unittest

from source_geometry import (point_in_polygon, polygon_edge_distance,
                             sample_polygon_starts, segment_distance)


class SourceGeometryTests(unittest.TestCase):
    def test_segment_distance_crossing_separated_and_degenerate(self):
        self.assertEqual(segment_distance((0, 0), (2, 0), (1, -1), (1, 1)), 0)
        self.assertEqual(segment_distance((0, 0), (2, 0), (0, 1), (2, 1)), 1)
        self.assertEqual(segment_distance((0, 0), (0, 0), (3, 4), (3, 4)), 5)

    def test_polygon_queries_keep_containment_explicit(self):
        square = [(0, 0), (2, 0), (2, 2), (0, 2)]
        self.assertTrue(point_in_polygon((1, 1), square))
        self.assertFalse(point_in_polygon((3, 1), square))
        self.assertEqual(polygon_edge_distance(square, (-1, 1), (3, 1)), 0)
        self.assertEqual(polygon_edge_distance(square, (0.5, 1), (1.5, 1)), 0.5)

    def test_source_start_sampler_excludes_a_concave_notch(self):
        concave = [(0, 0), (2, 0), (2, 2), (1, 1), (0, 2)]
        starts = sample_polygon_starts(concave, step=0.5, max_points=25)
        self.assertTrue(starts)
        self.assertTrue(all(point_in_polygon(point, concave) for point in starts))
        self.assertNotIn((1.0, 1.5), starts)


if __name__ == '__main__':
    unittest.main()
