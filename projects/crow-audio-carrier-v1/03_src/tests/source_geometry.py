"""Pure geometry helpers for pre-board source regression tests.

These helpers sample authored source geometry only. They do not implement or
stand in for the native P-LAND gate, whose authority remains
``land_witness.BoardContext`` over a complete generated board/project/ruleset.
"""
import math


SOURCE_START_STEP_MM = 0.03
MAX_SOURCE_START_POINTS = 25


def _segment_point_distance(a, b, point):
    """Euclidean distance from ``point`` to closed segment ``a``-``b``."""
    ax, ay = a
    bx, by = b
    px, py = point
    dx, dy = bx - ax, by - ay
    length_squared = dx * dx + dy * dy
    projection = (0.0 if length_squared == 0 else
                  ((px - ax) * dx + (py - ay) * dy) / length_squared)
    projection = max(0.0, min(1.0, projection))
    return math.hypot(px - ax - projection * dx,
                      py - ay - projection * dy)


def segment_distance(a, b, c, d):
    """Distance between closed segments ``a``-``b`` and ``c``-``d``."""
    ax, ay = a
    bx, by = b
    cx, cy = c
    dx, dy = d
    abx, aby = bx - ax, by - ay
    cdx, cdy = dx - cx, dy - cy
    denominator = abx * cdy - aby * cdx
    if denominator != 0:
        ab_fraction = ((cx - ax) * cdy - (cy - ay) * cdx) / denominator
        cd_fraction = ((cx - ax) * aby - (cy - ay) * abx) / denominator
        if 0.0 <= ab_fraction <= 1.0 and 0.0 <= cd_fraction <= 1.0:
            return 0.0
    return min(_segment_point_distance(a, b, c),
               _segment_point_distance(a, b, d),
               _segment_point_distance(c, d, a),
               _segment_point_distance(c, d, b))


def polygon_edge_distance(poly, a, b):
    """Distance from polygon edges to segment; callers handle containment."""
    return min(segment_distance(poly[i], poly[(i + 1) % len(poly)], a, b)
               for i in range(len(poly)))


def point_in_polygon(point, poly):
    """Even-odd polygon test; boundary distance is a separate operation."""
    x, y = point
    inside = False
    for i, (x1, y1) in enumerate(poly):
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y):
            edge_x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < edge_x:
                inside = not inside
    return inside


def sample_polygon_starts(poly, step=SOURCE_START_STEP_MM,
                          max_points=MAX_SOURCE_START_POINTS):
    """Return the legacy bounded in-polygon grid used by source ray probes."""
    xs = [point[0] for point in poly]
    ys = [point[1] for point in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    nx = max(1, min(int(round((x1 - x0) / step)),
                    int(max_points ** 0.5)))
    ny = max(1, min(int(round((y1 - y0) / step)),
                    int(max_points ** 0.5)))
    epsilon = 1e-6
    points = []
    if point_in_polygon((cx, cy), poly):
        points.append((cx, cy))
    for i in range(nx + 1):
        for j in range(ny + 1):
            point = (x0 + (x1 - x0) * i / nx,
                     y0 + (y1 - y0) * j / ny)
            point = (min(max(point[0], x0 + epsilon), x1 - epsilon),
                     min(max(point[1], y0 + epsilon), y1 - epsilon))
            if point_in_polygon(point, poly):
                points.append(point)
    return points
