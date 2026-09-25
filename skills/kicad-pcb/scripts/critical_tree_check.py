#!/usr/bin/env python3
"""Strict native proof for declared, single-layer, zero-via signal trees.

This intentionally narrow contract rejects copper shapes it cannot model.
It validates straight tracks with explicit endpoint junctions, rectangular SMD
terminal pads with exactly one track endpoint at each pad centre, exact tee
inventory, and saved filled reference copper.
It does not infer a route from a source bbox or an unfilled zone outline.

Optional ``route.yaml`` declaration::

    route:
      critical_trees:
        - net: RESET_N
          pads: [J_RESET.1, U_CTRL.7, U_OK.1]
          signal_layer: F.Cu
          reference_layer: In1.Cu
          reference_net: GND
          reference_anchor: J_GND.1   # PTH pad inside the saved fill
          max_vias: 0
          tees:
            - {at: [25.0, 42.0], layer: F.Cu, degree: 3, why: reset fanout}

Version 1 deliberately supports exactly one signal layer and zero vias. A
nonzero via budget, pad tee, signal zone, arc, hidden copper contact, detached
reference island, or unfilled reference fails instead of receiving credit.
"""
from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import math

import pcbnew


class TreeError(ValueError):
    pass


def _mm(point):
    return [point.x / 1e6, point.y / 1e6]


def _segment_distance(a, b, c, d):
    def point_segment(p, x, y):
        vx, vy = y[0]-x[0], y[1]-x[1]
        length2 = vx*vx+vy*vy
        t = 0 if length2 == 0 else max(0, min(1, ((p[0]-x[0])*vx+(p[1]-x[1])*vy)/length2))
        return math.hypot(p[0]-x[0]-t*vx, p[1]-x[1]-t*vy)
    den = (b[0]-a[0])*(d[1]-c[1])-(b[1]-a[1])*(d[0]-c[0])
    if abs(den)>1e-12:
        t = ((c[0]-a[0])*(d[1]-c[1])-(c[1]-a[1])*(d[0]-c[0]))/den
        u = ((c[0]-a[0])*(b[1]-a[1])-(c[1]-a[1])*(b[0]-a[0]))/den
        if 0<=t<=1 and 0<=u<=1:
            return 0
    return min(point_segment(a,c,d),point_segment(b,c,d),
               point_segment(c,a,b),point_segment(d,a,b))


def _line_hits_box(a, b, box, margin):
    """Conservative axis-aligned bbox intersection, including track width."""
    x0,y0,x1,y1 = (box.GetLeft()-margin,box.GetTop()-margin,
                    box.GetRight()+margin,box.GetBottom()+margin)
    t0,t1 = 0.0,1.0
    dx,dy = b.x-a.x,b.y-a.y
    for p,q in ((-dx,a.x-x0),(dx,x1-a.x),(-dy,a.y-y0),(dy,y1-a.y)):
        if p==0:
            if q<0:return False
        else:
            t=q/p
            if p<0:t0=max(t0,t)
            else:t1=min(t1,t)
            if t0>t1:return False
    return True


def _poly_for_track(track, layer_id):
    poly = pcbnew.SHAPE_POLY_SET()
    track.TransformShapeToPolygon(poly, layer_id, 0, pcbnew.FromMM(.005),
                                  pcbnew.ERROR_OUTSIDE)
    if poly.IsEmpty():
        raise TreeError('track polygon unavailable')
    return poly


def _reference_fill(board, layer_id, net, anchor_name):
    union = pcbnew.SHAPE_POLY_SET()
    count = 0
    for zone in board.Zones():
        if (zone.GetIsRuleArea() or zone.GetNetname()!=net or
                not zone.IsOnLayer(layer_id) or not zone.IsFilled() or
                not zone.HasFilledPolysForLayer(layer_id)):
            continue
        polys = zone.GetFilledPolysList(layer_id)
        if polys is None or polys.IsEmpty():
            continue
        union.BooleanAdd(polys)
        count += 1
    if not count or union.IsEmpty():
        raise TreeError('no saved filled reference copper')
    if union.OutlineCount()!=1:
        raise TreeError('saved reference fill has disconnected islands')
    anchor=[pad for fp in board.GetFootprints() for pad in fp.Pads()
            if f'{fp.GetReference()}.{pad.GetNumber()}'==anchor_name]
    if (len(anchor)!=1 or anchor[0].GetNetname()!=net or
            anchor[0].GetAttribute()!=pcbnew.PAD_ATTRIB_PTH or
            not anchor[0].IsOnLayer(layer_id) or
            not union.PointInside(anchor[0].GetPosition())):
        raise TreeError('reference anchor is not a grounded PTH pad in filled copper')
    return union,count


def _one(board, row):
    if not isinstance(row,dict):
        raise TreeError('critical tree declaration must be a mapping')
    net = row.get('net')
    pads_decl = row.get('pads')
    layer = row.get('signal_layer')
    reference_layer = row.get('reference_layer')
    reference_net = row.get('reference_net')
    reference_anchor = row.get('reference_anchor')
    tees = row.get('tees')
    if (not isinstance(net,str) or not net or
            not isinstance(pads_decl,list) or len(pads_decl)<3 or
            any(not isinstance(p,str) or '.' not in p for p in pads_decl) or
            len(pads_decl)!=len(set(pads_decl)) or
            not isinstance(tees,list) or
            not isinstance(layer,str) or not isinstance(reference_layer,str) or
            not isinstance(reference_net,str) or not reference_net or
            not isinstance(reference_anchor,str) or '.' not in reference_anchor or
            layer==reference_layer or
            row.get('max_vias')!=0 or type(row.get('max_vias')) is not int or
            set(row) != {'net','pads','signal_layer','reference_layer',
                         'reference_net','reference_anchor','tees','max_vias'}):
        raise TreeError('critical tree declaration incomplete or unsupported; v1 requires zero vias')
    enabled = {board.GetLayerName(i):i for i in board.GetEnabledLayers().Seq()
               if pcbnew.IsCopperLayer(i)}
    if layer not in enabled or reference_layer not in enabled:
        raise TreeError('critical tree signal/reference layer unavailable')
    lid,rid = enabled[layer],enabled[reference_layer]
    physical_pads = [(f'{fp.GetReference()}.{pad.GetNumber()}',pad)
                     for fp in board.GetFootprints() for pad in fp.Pads()
                     if pad.GetNetname()==net]
    pads = dict(physical_pads)
    if (len(physical_pads)!=len(pads_decl) or len(pads)!=len(physical_pads) or
            set(pads)!=set(pads_decl)):
        raise TreeError(f'{net}: exact native pad set mismatch')
    for name,pad in pads.items():
        if (pad.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD or
                pad.GetShape()!=pcbnew.PAD_SHAPE_RECT or
                not pad.IsOnLayer(lid)):
            raise TreeError(f'{name}: terminal must be rectangular SMD on {layer}')
    items = [item for item in board.GetTracks() if item.GetNetname()==net]
    if not items:
        raise TreeError(f'{net}: no realized tracks')
    if any(isinstance(item,pcbnew.PCB_VIA) for item in items):
        raise TreeError(f'{net}: via exceeds zero-via limit')
    if any(item.GetClass()!='PCB_TRACK' or item.GetLayer()!=lid or
           item.GetStart()==item.GetEnd() or item.GetWidth()<=0 for item in items):
        raise TreeError(f'{net}: unsupported track shape/layer/width')
    if any(zone.GetNetname()==net and zone.IsFilled() for zone in board.Zones()):
        raise TreeError(f'{net}: signal zone makes a tree graph ambiguous')
    vertices=defaultdict(set)
    endpoints=[]
    for index,item in enumerate(items):
        a=(item.GetStart().x,item.GetStart().y)
        b=(item.GetEnd().x,item.GetEnd().y)
        if a==b:raise TreeError(f'{net}: zero-length track')
        vertices[a].add(index)
        vertices[b].add(index)
        endpoints.append((a,b))
    if len(endpoints)!=len(set(tuple(sorted(pair)) for pair in endpoints)):
        raise TreeError(f'{net}: duplicate copper edge')
    for index,left in enumerate(items):
        a,b=endpoints[index]
        for j,right in enumerate(items[index+1:],start=index+1):
            c,d=endpoints[j]
            common={a,b}&{c,d}
            if common:
                if len(common)!=1:
                    raise TreeError(f'{net}: duplicated copper edge')
                shared=next(iter(common))
                x=b if a==shared else a
                y=d if c==shared else c
                cross=(x[0]-shared[0])*(y[1]-shared[1])-(x[1]-shared[1])*(y[0]-shared[0])
                dot=(x[0]-shared[0])*(y[0]-shared[0])+(x[1]-shared[1])*(y[1]-shared[1])
                if cross==0 and dot>0:
                    raise TreeError(f'{net}: overlapping collinear tracks')
                continue
            distance=_segment_distance(_mm(left.GetStart()),_mm(left.GetEnd()),
                                       _mm(right.GetStart()),_mm(right.GetEnd()))
            if distance <= (left.GetWidth()+right.GetWidth())/2e6 + 1e-6:
                raise TreeError(f'{net}: undeclared copper contact or near-contact')
    pad_vertices={}
    for name,pad in pads.items():
        center=(pad.GetPosition().x,pad.GetPosition().y)
        if len(vertices.get(center,set()))!=1:
            raise TreeError(f'{name}: terminal must have exactly one center landing')
        pad_vertices[name]=center
        for index,item in enumerate(items):
            if index not in vertices[center] and _line_hits_box(
                    item.GetStart(),item.GetEnd(),pad.GetBoundingBox(),item.GetWidth()//2):
                raise TreeError(f'{name}: another track enters terminal pad')
    adjacency=defaultdict(set)
    for a,b in endpoints:
        adjacency[a].add(b)
        adjacency[b].add(a)
    start=next(iter(adjacency))
    seen={start}
    queue=deque([start])
    while queue:
        for neighbor in adjacency[queue.popleft()]:
            if neighbor not in seen:
                seen.add(neighbor);queue.append(neighbor)
    if len(seen)!=len(adjacency):
        raise TreeError(f'{net}: disconnected track graph')
    if len(endpoints)!=len(adjacency)-1:
        raise TreeError(f'{net}: copper graph contains a cycle')
    if any(len(adjacency[xy])!=1 for xy in pad_vertices.values()):
        raise TreeError(f'{net}: terminal pad has an undeclared branch')
    actual={(xy[0],xy[1],len(neighbors)) for xy,neighbors in adjacency.items()
            if len(neighbors)>=3}
    declared=set()
    for tee in tees:
        if (not isinstance(tee,dict) or set(tee)!={'at','layer','degree','why'} or
                tee.get('layer')!=layer or type(tee.get('degree')) is not int or
                tee['degree']<3 or not isinstance(tee.get('why'),str) or
                not tee['why'].strip() or not isinstance(tee.get('at'),list) or
                len(tee['at'])!=2 or any(type(v) not in (int,float) or
                    not math.isfinite(v) for v in tee['at'])):
            raise TreeError(f'{net}: malformed tee declaration')
        declared.add((pcbnew.FromMM(tee['at'][0]),pcbnew.FromMM(tee['at'][1]),tee['degree']))
    if len(declared)!=len(tees) or declared!=actual:
        raise TreeError(f'{net}: declared tee inventory differs from native graph')
    conn=board.GetConnectivity()
    conn.Build(board)
    anchor=pads[pads_decl[0]]
    connected=list(conn.GetConnectedItems(anchor))
    if any(pad not in connected and pad is not anchor for pad in pads.values()):
        raise TreeError(f'{net}: native pad connectivity incomplete')
    fill,zone_count=_reference_fill(board,rid,reference_net,reference_anchor)
    for item in items:
        remainder=_poly_for_track(item,lid)
        remainder.BooleanSubtract(fill)
        if not remainder.IsEmpty() and abs(remainder.Area())>1:
            raise TreeError(f'{net}: track lacks continuous saved filled reference')
    for name,pad in pads.items():
        remainder=pcbnew.SHAPE_POLY_SET()
        pad.TransformShapeToPolygon(remainder,lid,0,pcbnew.FromMM(.005),
                                    pcbnew.ERROR_OUTSIDE)
        if remainder.IsEmpty():
            raise TreeError(f'{name}: pad projection unavailable')
        remainder.BooleanSubtract(fill)
        if not remainder.IsEmpty() and abs(remainder.Area())>1:
            raise TreeError(f'{name}: pad lacks continuous saved filled reference')
    return {'net':net,'status':'PASS','pad_count':len(pads),
            'track_count':len(items),'via_count':0,'tee_count':len(actual),
            'reference_zone_count':zone_count,
            'reference_layer':reference_layer,'reference_net':reference_net,
            'reference_anchor':reference_anchor}


def inspect(board_path: Path, declarations):
    if declarations is None:
        return {'status':'N-A','detail':'critical_trees not declared','trees':[]}
    if not isinstance(declarations,list) or not declarations:
        return {'status':'FAIL','detail':'critical_trees must be a non-empty list','trees':[]}
    board=pcbnew.LoadBoard(str(board_path))
    if board is None:
        return {'status':'INCOMPLETE','detail':'native board unavailable','trees':[]}
    rows=[]
    seen=set()
    for row in declarations:
        net=row.get('net') if isinstance(row,dict) else None
        if net in seen:
            return {'status':'FAIL','detail':f'duplicate critical tree net {net}','trees':rows}
        seen.add(net)
        try:
            rows.append(_one(board,row))
        except (TreeError,ValueError,TypeError,AttributeError) as exc:
            rows.append({'net':net,'status':'FAIL','reason':str(exc)})
    return {'status':'FAIL' if any(r['status']!='PASS' for r in rows) else 'PASS',
            'detail':f'{len(rows)} critical tree(s) graded','trees':rows}
