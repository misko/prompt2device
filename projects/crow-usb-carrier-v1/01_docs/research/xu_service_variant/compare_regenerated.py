#!/usr/bin/env python3
"""Compare the pinned current-source board with a rectangle-only regeneration.

python3 compare_regenerated.py BASE_PROJECT VARIANT_PROJECT > regeneration.json
Read-only; requires native KiCad 10 pcbnew and PyYAML.
"""
import hashlib
import json
from pathlib import Path
import sys

import pcbnew
import yaml

PROJECT = Path(__file__).resolve().parents[3]
PIN = {
    'baseline_floorplan': 'a882f87682484c37c5766a9e37c5a0d93b38a8e5a775fb1ab4425011da40a275',
    'variant_floorplan': '01aa2aa9fa6b264510e568236a265fefb36494b275de081a99b62229c8be3de8',
    'modular_plan': '7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e',
    'requirements': '9ef85e5f4918dea0378203a97fa631ce2e73a690170235902a97a6c8e30527d8',
    'netlist': 'e7ef7dbd752b9431ade0933ca77ee998963bfe3871c3caf65cddc56442f1371d',
    'generator': '8a5fa1d48d80138458601a097ab6260565841510a498e44cb9c5773652215b3c',
    'baseline_board': '60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17',
    'variant_board': 'c3b9d2885e1f475aad4744185eaa7258359a0d340e864e56418da5f61a0d3a6b',
}
CELLS = {'xmos_core': [190, 84, 232, 114], 'clock_flash_debug': [190, 114, 232, 136]}
WINDOWS = {'qspi': [200, 111.9, 205, 117.9], 'jtag_reset': [222, 82, 225, 86]}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def need(label, path):
    got = sha(path)
    if got != PIN[label]:
        raise ValueError(f'{label} SHA-256 {got} != {PIN[label]}: {path}')
    return got


def mm(n):
    return round(pcbnew.ToMM(n), 6)


def box(r):
    return [mm(x) for x in (r.GetX(), r.GetY(), r.GetRight(), r.GetBottom())]


def envelope(fp):
    b = box(fp.GetBoundingBox(False, False))
    c = fp.GetCourtyard(pcbnew.F_CrtYd)
    if c.OutlineCount():
        pts = [c.COutline(i).CPoint(k) for i in range(c.OutlineCount())
               for k in range(c.COutline(i).PointCount())]
        xs, ys = [mm(p.x) for p in pts], [mm(p.y) for p in pts]
        b = [min(b[0], min(xs)), min(b[1], min(ys)),
             max(b[2], max(xs)), max(b[3], max(ys))]
    return b


def overlap(a, b):
    return max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))


def inside(a, b):
    return a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]


def pose(fp):
    p = fp.GetPosition()
    return [mm(p.x), mm(p.y), round(fp.GetOrientationDegrees(), 6)]


def pads(fp, position):
    rows = []
    for p in fp.Pads():
        q = p.GetPosition()
        row = [p.GetNumber(), p.GetNetname(), int(p.GetShape()),
               mm(p.GetSize().x), mm(p.GetSize().y), p.GetLayerSet().FmtBin()]
        if position:
            row.extend([mm(q.x), mm(q.y)])
        rows.append(row)
    return sorted(rows)


def board_data(path):
    b = pcbnew.LoadBoard(str(path))
    if b is None:
        raise ValueError(f'cannot load {path}')
    fs = {f.GetReference(): f for f in b.GetFootprints()}
    return b, fs


def run(base, variant):
    source = {
        'baseline_floorplan': need('baseline_floorplan', PROJECT/'03_src/floorplan.yaml'),
        'variant_floorplan': need('variant_floorplan', variant/'03_src/floorplan.yaml'),
        'modular_plan': need('modular_plan', PROJECT/'03_src/modular_plan.json'),
        'requirements': need('requirements', PROJECT/'03_src/rules/p1_corridor_requirements.yaml'),
        'netlist': need('netlist', variant/'06_build/netlists/crow_carrier.net'),
        'generator': need('generator', PROJECT.parents[1]/'skills/kicad-pcb/scripts/generate_board_generic.py'),
        'baseline_board': need('baseline_board', base/'04_kicad/crow_carrier.kicad_pcb'),
        'variant_board': need('variant_board', variant/'04_kicad/crow_carrier.kicad_pcb'),
    }
    floor = yaml.safe_load((variant/'03_src/floorplan.yaml').read_text())
    orig = yaml.safe_load((PROJECT/'03_src/floorplan.yaml').read_text())
    for name, rect in CELLS.items():
        if floor['placement']['regions'][name] != rect:
            raise ValueError(f'variant region {name} differs')
    changed_source = {name: [orig['placement']['regions'][name], rect]
                      for name, rect in CELLS.items()}
    # Exact mutation scope: all source data other than the two region rows must agree.
    for name in CELLS:
        orig['placement']['regions'][name] = CELLS[name]
    if orig != floor:
        raise ValueError('variant floorplan changed data outside the two regions')
    b0, f0 = board_data(base/'04_kicad/crow_carrier.kicad_pcb')
    b1, f1 = board_data(variant/'04_kicad/crow_carrier.kicad_pcb')
    if f0.keys() != f1.keys():
        raise ValueError('footprint references differ')
    ref_names = sorted(f0)
    moved = []
    changed_identity = []
    changed_pad_positions = []
    for ref in ref_names:
        if pose(f0[ref]) != pose(f1[ref]):
            moved.append({'ref': ref, 'before': pose(f0[ref]), 'after': pose(f1[ref]),
                          'before_envelope_mm': envelope(f0[ref]),
                          'after_envelope_mm': envelope(f1[ref])})
        if pads(f0[ref], False) != pads(f1[ref], False):
            changed_identity.append(ref)
        if pads(f0[ref], True) != pads(f1[ref], True):
            changed_pad_positions.append(ref)
    patterns = floor['placement']['patterns']
    assigned = {ref: row['region'] for row in patterns if row.get('region') in CELLS
                for ref in row['match']}
    outside = [{'ref': ref, 'owner': owner, 'envelope_mm': envelope(f1[ref])}
               for ref, owner in sorted(assigned.items()) if not inside(envelope(f1[ref]), CELLS[owner])]
    source_intersections = [{'cell': name, 'with': other, 'area_mm2': overlap(rect, other_rect)}
                            for name, rect in CELLS.items()
                            for other, other_rect in floor['placement']['regions'].items()
                            if other != name and overlap(rect, other_rect)]
    window_hits = {name: sorted(ref for ref, fp in f1.items() if overlap(envelope(fp), rect))
                   for name, rect in WINDOWS.items()}
    zones = lambda b: sorted([{'net': z.GetNetname(), 'layer': b.GetLayerName(z.GetLayer()),
                               'rule_area': bool(z.GetIsRuleArea()), 'bbox_mm': box(z.GetBoundingBox())}
                              for z in b.Zones()], key=lambda x: (x['layer'], x['net'], x['bbox_mm']))
    z0, z1 = zones(b0), zones(b1)
    req = yaml.safe_load((PROJECT/'03_src/rules/p1_corridor_requirements.yaml').read_text())
    fixed = set(req['p1_fixed_refs'])
    fixed_moved = [x['ref'] for x in moved if x['ref'] in fixed]
    return {'schema': 'crow-xu-service-regeneration-v1', 'status': 'INCOMPLETE_RESEARCH',
            'source_commit': '9c73181c432b51558003a8be7e496cc8c6757d5a',
            'sha256': source, 'pcbnew_version': pcbnew.Version(),
            'changed_source_regions_mm': changed_source,
            'baseline': {'footprints': len(f0), 'pads': sum(len(list(f.Pads())) for f in f0.values()),
                         'tracks_and_vias': len(b0.GetTracks()), 'zones': z0},
            'variant': {'footprints': len(f1), 'pads': sum(len(list(f.Pads())) for f in f1.values()),
                        'tracks_and_vias': len(b1.GetTracks()), 'zones': z1},
            'moved_footprints': moved, 'changed_pad_identity_refs': changed_identity,
            'changed_pad_position_refs': changed_pad_positions,
            'p1_fixed_count': len(fixed), 'p1_fixed_moved_refs': fixed_moved,
            'assigned_cell_footprints': len(assigned), 'assigned_outside_cell': outside,
            'source_region_intersections': source_intersections,
            'diagnostic_window_footprint_hits': window_hits,
            'zone_inventory_equal': z0 == z1,
            'reservation_status': 'UNREPRESENTED: diagnostic windows are not exclusive source-owned corridors'}


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    print(json.dumps(run(Path(sys.argv[1]), Path(sys.argv[2])), indent=2, sort_keys=True))
