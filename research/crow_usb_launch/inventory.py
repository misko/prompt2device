#!/usr/bin/env python3
"""Pin and inventory the exact Crow XU USB launch from a KiCad board.

Usage: python3 inventory.py BOARD.kicad_pcb > geometry.json
Requires the native KiCad 10 pcbnew Python module. All dimensions are mm.
"""
import hashlib
import json
import math
import pathlib
import re
import sys

import pcbnew

EXPECTED_SHA = 'a822e3ddb355113cb8708ffdd3e3990aacc9b53bf214355d88d04a7e5a3bb435'
ROI = (215.5, 93.8, 220.8, 97.4)  # XU launch, neighbor pads and first 0.410-mm tracks
NETS = {'USB_DP', 'USB_DN'}
SHAPES = {getattr(pcbnew, n): n.removeprefix('PAD_SHAPE_') for n in dir(pcbnew)
          if n.startswith('PAD_SHAPE_') and isinstance(getattr(pcbnew, n), int)}


def mm(i):
    return round(pcbnew.ToMM(i), 9)


def point(p):
    return [mm(p.x), mm(p.y)]


def bbox(b):
    return [mm(b.GetX()), mm(b.GetY()), mm(b.GetRight()), mm(b.GetBottom())]


def intersects(a, b):
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def polyset(s):
    result = []
    for i in range(s.OutlineCount()):
        o = s.COutline(i)
        result.append({'outline': [point(o.CPoint(k)) for k in range(o.PointCount())],
                       'holes': [[point(s.CHole(i, h).CPoint(k))
                                  for k in range(s.CHole(i, h).PointCount())]
                                 for h in range(s.HoleCount(i))]})
    return result


def extract_stack(raw):
    start = raw.index('(stackup', raw.index('(setup'))
    depth = 0
    quoted = False
    escaped = False
    for i in range(start, len(raw)):
        c = raw[i]
        if quoted:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return raw[start:i+1]
    raise ValueError('unterminated board stackup')


def run(path):
    data = pathlib.Path(path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA:
        raise ValueError(f'board SHA256 {digest} differs from pinned {EXPECTED_SHA}')
    board = pcbnew.LoadBoard(str(path))
    if board is None:
        raise ValueError('pcbnew failed to load board')
    tracks = []
    for t in board.GetTracks():
        if t.GetNetname() not in NETS:
            continue
        a, b = point(t.GetStart()), point(t.GetEnd())
        width = mm(t.GetWidth())
        if type(t).__name__ != 'PCB_TRACK':
            raise ValueError(f'unsupported track type {type(t).__name__}')
        tracks.append({'uuid': t.m_Uuid.AsString(), 'net': t.GetNetname(),
                       'layer': board.GetLayerName(t.GetLayer()), 'start': a, 'end': b,
                       'width_mm': width, 'length_mm': round(math.dist(a, b), 9),
                       'effective_shape': 'closed capsule: segment Minkowski sum disk radius width_mm/2',
                       'bbox_mm': [round(min(a[0], b[0])-width/2, 9),
                                   round(min(a[1], b[1])-width/2, 9),
                                   round(max(a[0], b[0])+width/2, 9),
                                   round(max(a[1], b[1])+width/2, 9)]})
    tracks.sort(key=lambda t: (t['net'], t['uuid']))
    neck = [t for t in tracks if t['layer'] == 'F.Cu' and t['width_mm'] < 0.410]
    if len(neck) != 6 or sorted(t['width_mm'] for t in neck) != [0.15]*4 + [0.25]*2:
        raise ValueError('expected exactly four 0.15-mm and two 0.25-mm XU neck segments')
    pads = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            bb = bbox(p.GetBoundingBox())
            if not intersects(bb, ROI) or not p.IsOnLayer(pcbnew.F_Cu):
                continue
            item = {'ref': fp.GetReference(), 'number': p.GetNumber(),
                    'uuid': p.m_Uuid.AsString(), 'net': p.GetNetname(),
                    'center_mm': point(p.GetPosition()), 'size_local_mm': point(p.GetSize()),
                    'orientation_degrees': p.GetOrientationDegrees(),
                    'shape': SHAPES.get(p.GetShape(), str(p.GetShape())),
                    'bbox_mm': bb,
                    'f_mask_opening': bool(p.IsOnLayer(pcbnew.F_Mask)),
                    'f_mask_expansion_mm': mm(p.GetSolderMaskExpansion(pcbnew.F_Mask))
                    if p.IsOnLayer(pcbnew.F_Mask) else None}
            if p.GetShape() == pcbnew.PAD_SHAPE_ROUNDRECT:
                item['roundrect_corner_radius_mm'] = mm(p.GetRoundRectCornerRadius())
            pads.append(item)
    pads.sort(key=lambda p: (p['ref'], p['number']))
    zones = []
    for z in board.Zones():
        layer = board.GetLayerName(z.GetLayer())
        item = {'uuid': z.m_Uuid.AsString(), 'net': z.GetNetname(), 'layer': layer,
                'rule_area': bool(z.GetIsRuleArea()), 'filled': bool(z.IsFilled()),
                'bbox_mm': bbox(z.GetBoundingBox()), 'outline': polyset(z.Outline())}
        if z.GetIsRuleArea():
            item['rule_area_name'] = z.GetZoneName()
            item['prohibitions'] = {kind: bool(getattr(z, 'GetDoNotAllow' + method)())
                                    for kind, method in [('tracks', 'Tracks'), ('pads', 'Pads'),
                                                         ('vias', 'Vias'), ('zone_fills', 'ZoneFills'),
                                                         ('footprints', 'Footprints')]}
        if z.IsFilled() and z.HasFilledPolysForLayer(z.GetLayer()):
            item['filled_polygons'] = polyset(z.GetFilledPolysList(z.GetLayer()))
        zones.append(item)
    zones.sort(key=lambda z: (z['layer'], z['net']))
    stack = extract_stack(data.decode('utf-8'))
    if not any(z['net'] == 'GND' and z['layer'] == 'In1.Cu' and z['filled'] for z in zones):
        raise ValueError('In1.Cu GND fill missing')
    if not any(z['rule_area'] and z['layer'] == 'F.Cu' for z in zones):
        raise ValueError('F.Cu launch zone rule area missing')
    return {'schema': 'crow-xu-usb-launch-geometry-v1', 'source_sha256': digest,
            'pcbnew_version': pcbnew.Version(), 'units': 'mm', 'roi_mm': ROI,
            'stackup_kicad_sexpr': stack, 'mask_settings': {
                'pad_to_mask_clearance_mm': 0, 'allow_soldermask_bridges_in_footprints': False,
                'source': 'board (setup) adjacent to stackup'},
            'tracks_usb_pair_all': tracks, 'neck_track_uuids': [t['uuid'] for t in neck],
            'pads_fcu_intersecting_roi': pads, 'zones_all': zones,
            'model_status': 'geometry inventory only; no impedance or S-parameter result'}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    print(json.dumps(run(pathlib.Path(sys.argv[1])), indent=2, sort_keys=True))
