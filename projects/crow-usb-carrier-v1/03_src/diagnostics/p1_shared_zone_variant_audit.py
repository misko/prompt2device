#!/usr/bin/env python3
"""Measure an isolated shared-zone floorplan proposal against native bounds.

This is a research auditor.  It intentionally does not call the P1 checker or
create a P1 receipt: schema-2 currently accepts rectangular reservations and
direct endpoint owners only, while a board_integration shared-zone needs a
union/polygon authority model.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox(item):
    box = item.GetBoundingBox(True, True)
    return tuple(round(pcbnew.ToMM(v), 6)
                 for v in (box.GetLeft(), box.GetTop(), box.GetRight(), box.GetBottom()))


def intersects(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def crossing(ref_box, edge):
    axis, value, lo, hi = edge
    if axis == 'x':
        return ref_box[0] < value < ref_box[2] and ref_box[1] < hi and ref_box[3] > lo
    return ref_box[1] < value < ref_box[3] and ref_box[0] < hi and ref_box[2] > lo


def outer_edges(rectangles):
    """Return union exterior edges by subtracting coincident internal sides.

    The source variant presently has a stepped rectilinear union.  Splitting
    at all vertices makes this conservative for arbitrary rectangle unions.
    """
    xs = sorted({x for r in rectangles for x in (r[0], r[2])})
    ys = sorted({y for r in rectangles for y in (r[1], r[3])})
    edges = []
    for x in xs:
        for y0, y1 in zip(ys, ys[1:]):
            left = any(r[0] < x and r[1] <= (y0+y1)/2 <= r[3] for r in rectangles)
            right = any(r[2] > x and r[1] <= (y0+y1)/2 <= r[3] for r in rectangles)
            # The tests above also see rectangles that span x.  Check side
            # occupancy locally instead, using tiny offsets.
            eps = 1e-5
            left = any(r[0] <= x-eps <= r[2] and r[1] <= (y0+y1)/2 <= r[3] for r in rectangles)
            right = any(r[0] <= x+eps <= r[2] and r[1] <= (y0+y1)/2 <= r[3] for r in rectangles)
            if left != right:
                edges.append(('x', x, y0, y1))
    for y in ys:
        for x0, x1 in zip(xs, xs[1:]):
            eps = 1e-5
            below = any(r[0] <= (x0+x1)/2 <= r[2] and r[1] <= y-eps <= r[3] for r in rectangles)
            above = any(r[0] <= (x0+x1)/2 <= r[2] and r[1] <= y+eps <= r[3] for r in rectangles)
            if below != above:
                edges.append(('y', y, x0, x1))
    return edges


def main(argv):
    if len(argv) != 4:
        raise SystemExit(f'usage: {argv[0]} VARIANT.yaml MODULAR_PLAN.json OUT.json')
    variant_path, plan_path, out_path = map(Path, argv[1:])
    variant = yaml.safe_load(variant_path.read_text())
    plan = json.loads(plan_path.read_text())
    root = variant_path.parents[2]
    board_path = (variant_path.parent / variant['base']['board']).resolve()
    board = pcbnew.LoadBoard(str(board_path))
    rectangles = [tuple(map(float, r)) for r in variant['shared_zone']['geometry']['rectangles']]
    member_blocks = set(variant['shared_zone']['members'])
    owners = {ref: block['id'] for block in plan['blocks'] for ref in block.get('refs', [])}
    fps = [{'ref': fp.GetReference(), 'owner': owners.get(fp.GetReference(), 'UNOWNED'),
            'bbox': bbox(fp)} for fp in board.GetFootprints()]
    zone_hits = [fp for fp in fps if any(intersects(fp['bbox'], r) for r in rectangles)]
    edge_hits = []
    for edge in outer_edges(rectangles):
        refs = sorted(fp['ref'] for fp in fps if crossing(fp['bbox'], edge))
        if refs:
            edge_hits.append({'axis': edge[0], 'value_mm': edge[1], 'span_mm': list(edge[2:]), 'refs': refs})
    fixed = variant['fixed_refs']
    expected_fixed = yaml.safe_load((root / '03_src/rules/p1_corridor_requirements.yaml').read_text())['p1_fixed_refs']
    report = {
        'schema': 1, 'kind': 'crow-p1-shared-zone-variant-audit',
        'status': 'REJECTED', 'p1_accepted': False, 'routing_realized': False,
        'hashes': {'variant': digest(variant_path), 'board': digest(board_path),
                   'modular_plan': digest(plan_path)},
        'fixed_refs': {'count': len(fixed), 'exact_current_authority': fixed == expected_fixed,
                       'zone_intersections': sorted(ref for ref in fixed
                                                    if any(fp['ref'] == ref for fp in zone_hits))},
        'zone': {'owner': variant['shared_zone']['owner'], 'member_blocks': sorted(member_blocks),
                 'rectangles': rectangles, 'outer_edge_count': len(outer_edges(rectangles)),
                 'full_footprint_intersections': len(zone_hits),
                 'owners': dict(sorted(Counter(fp['owner'] for fp in zone_hits).items())),
                 'member_owners': dict(sorted(Counter(fp['owner'] for fp in zone_hits
                                                       if fp['owner'] in member_blocks).items())),
                 'foreign_footprints': sorted(fp['ref'] for fp in zone_hits if fp['owner'] not in member_blocks),
                 'boundary_intersections': edge_hits},
        'checker_gap': 'schema-2 accepts rectangle-only direct-owner virtual witnesses; this source-owned union needs explicit board_integration shared-zone authority',
        'reason': 'outer shared-zone boundary intersects full native footprint envelopes; no virtual face, reservation, capacity, return, or P1 claim is valid',
    }
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main(sys.argv)
