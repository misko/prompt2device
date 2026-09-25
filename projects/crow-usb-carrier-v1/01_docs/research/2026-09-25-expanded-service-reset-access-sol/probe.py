#!/usr/bin/env /usr/bin/python3
"""Read-only same-pose F.Cu access and reset-window proposal screen."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / '2026-09-25-expanded-service-timing-capacity-sol/measure.py'
assert hashlib.sha256(BASE.read_bytes()).hexdigest() == '7812eb60ee262117f979872dee32fa4cadc2f5038dbc04d7e918b296bbfeefff'
spec = importlib.util.spec_from_file_location('capacity_base', BASE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
capacity = base.capacity


def extend(box, margin):
    return [box[0]-margin, box[1]-margin, box[2]+margin, box[3]+margin]


def collided(box, other):
    return base.hits(box, other)


def probe():
    binding = base.study()  # hash and every source/native pad identity check
    board = capacity.pcbnew.LoadBoard(str(base.FILES['board']))
    contract = json.loads(base.FILES['contract'].read_text())
    allocation = next(a for a in contract['allocations'] if a['id']=='xmos_service_escape')
    accesses = {r['id']:r['segments'] for r in allocation['reservations']
                if r['id'].startswith('jtag_access_')}
    assert set(accesses) == {'jtag_access_2','jtag_access_4','jtag_access_6','jtag_access_8'}
    obstacles = []
    endpoints = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref != 'J_JTAG' and fp.GetLayerName() == 'F.Cu':
            obstacles.append((ref+':body', capacity.box_mm(fp.GetBoundingBox(False,False))))
        for pad in fp.Pads():
            if pad.IsOnLayer(capacity.pcbnew.F_Cu):
                ident = ref+'.'+pad.GetNumber()
                box = capacity.box_mm(pad.GetEffectiveShape(capacity.pcbnew.F_Cu).BBox())
                obstacles.append((ident,box))
                if ident in {'J_JTAG.10','R_XU_RST_PU.2','U_CORE_OK.1','U_XU_3V3_OK.6','U_XU.38'}:
                    assert pad.GetNetname() == 'XU_RESET_N'
                    endpoints[ident] = {'net':pad.GetNetname(),'bbox_mm':box}
    assert len(endpoints) == 5
    rule = binding['rules']
    clearance = rule['default_clearance_mm']
    preferred = rule['default_track_mm']
    absolute = rule['absolute_min_track_mm']
    assert (preferred,absolute,clearance) == (.2,.15,.15)

    # Source paths are rectangles, not copper. A .15-mm stroke can be placed
    # only if its full rectangular envelope clears other native pads and
    # disjoint access envelopes by .15 mm. Connector body is not a copper
    # obstacle, but its other native pads always are.
    path_screen = {}
    for name,segments in accesses.items():
        own = 'J_JTAG.'+name.rsplit('_',1)[1]
        native = sorted({ident for seg in segments for ident,box in obstacles
                         if ident != own and collided(seg,extend(box,clearance))})
        other_paths = sorted({other for other,other_segments in accesses.items()
                              if other != name for seg in segments for box in other_segments
                              if collided(seg,extend(box,clearance))})
        widened = []
        for seg in segments:
            thin = min(seg[2]-seg[0],seg[3]-seg[1])
            widened.append(extend(seg,(preferred-thin)/2))
        wider_native = sorted({ident for seg in widened for ident,box in obstacles
                               if ident != own and collided(seg,extend(box,clearance))})
        wider_other = sorted({other for other,other_segments in accesses.items()
                              if other != name for seg in widened for box in other_segments
                              if collided(seg,extend(extend(box,(preferred-absolute)/2),clearance))})
        path_screen[name] = {'segment_count':len(segments),'at_015_native_hits':native,
            'at_015_other_path_hits':other_paths,'naive_020_native_hits':wider_native,
            'naive_020_other_path_hits':wider_other}
    assert all(not x['at_015_native_hits'] and not x['at_015_other_path_hits'] for x in path_screen.values())

    # Proposed connector pad-10 access: the leftmost north-row pad is given a
    # leftward 0.15-mm stroke and a separate western stem into JTAG strip.
    reset_access = [[221.175,47.89,225.09,48.04], [221.175,48.04,221.325,65.0]]
    assert reset_access[0][2] == endpoints['J_JTAG.10']['bbox_mm'][0]
    assert reset_access[-1][3] == 65.0
    reset_native_hits = sorted({ident for seg in reset_access for ident,box in obstacles
                                if ident != 'J_JTAG.10' and collided(seg,extend(box,clearance))})
    reset_path_hits = sorted({name for seg in reset_access for name,parts in accesses.items()
                              for box in parts if collided(seg,extend(box,clearance))})
    assert not reset_native_hits and not reset_path_hits

    # A one-net digital-power -> XU source-face candidate. This is an empty
    # floorplan gap, not a changed source reservation or realized route.
    gap = [185.0,100.0,190.0,110.5]
    expanded = [(ident,extend(box,clearance)) for ident,box in obstacles]
    inner = [gap[0]+clearance,gap[1]+clearance,gap[2]-clearance,gap[3]-clearance]
    physical = capacity.connected_capacity(inner,expanded,'horizontal',preferred+clearance)
    other_reservations = sorted(f"{a['id']}:{r['id']}" for a in contract['allocations']
        for r in a.get('reservations',[]) if r.get('bbox') and collided(gap,r['bbox']))
    assert not physical['foreign_obstacles'] and not other_reservations
    return {'input_hashes':binding['hashes'],'rules':rule,'reset_endpoints':endpoints,
            'jtag_authored_access':path_screen,
            'reset_fixed_access_proposal':{'segments_mm':reset_access,
                'native_clearance_hits':reset_native_hits,'other_access_clearance_hits':reset_path_hits},
            'reset_digital_gap_proposal':{'bbox_mm':gap,'axis':'horizontal',
                'cleared_aperture_mm':physical['connected_width_mm'],
                'native_obstacles':physical['foreign_obstacles'],
                'reservation_overlaps':other_reservations},
            'claim':'source proposal only; no reset tree, copper route, P1 admission or filled return'}


if __name__ == '__main__':
    print(json.dumps(probe(),indent=2,sort_keys=True))
