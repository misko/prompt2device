#!/usr/bin/env python3
"""Bounded effective-shape screen for a 1.20mm TPS26625 IN-pad launch."""
from __future__ import annotations
import hashlib,json,math,sys
from pathlib import Path
import yaml
sys.path.append('/usr/lib/python3/dist-packages');import pcbnew as p
HERE=Path(__file__).resolve().parent
PREV=HERE.parent/'2026-09-25-ti-tps26625-return-trial-sol'
BOARD=PREV/'candidate_filled_profile.kicad_pcb'
EXPECTED_SHA='9f5a3b11a5c6cf42e9979bc5f4d74eb202af4f79fbe6f0bc9dd85e576d0b9ede'
EXPECTED_NETS_SHA='18033487a097b6d29abe3f9d8517879931cf80d278d8973adcf276010a5b7190'
FROZEN=Path('/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project')
PAD=(188.3,46.38,188.9,46.62)
CANDIDATES=[(round(187.9+i*.05,3),round(45.85+j*.025,3)) for i in range(13) for j in range(15)]
def mm(n):return n/1e6
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pad(board,ref,num):
    return next(q for f in board.GetFootprints() if f.GetReference()==ref
                for q in f.Pads() if q.GetNumber()==num)
def gap(a,b):
    if a.Collide(b,0):return 0.0
    lo,hi=0,p.FromMM(3)
    if not a.Collide(b,hi):return None
    while hi-lo>100:
      mid=(lo+hi)//2
      if a.Collide(b,mid):hi=mid
      else:lo=mid
    return round(mm(hi),6)
def poly(item):
    out=p.SHAPE_POLY_SET()
    item.TransformShapeToPolygon(out,p.F_Cu,0,5000,p.ERROR_INSIDE)
    return out
def overlap(track,land):
    intersection=poly(track)
    intersection.BooleanIntersection(poly(land))
    return round(abs(float(intersection.Area()))/1e12,8)
def make_track(board,x,yb,width=1.2):
    t=p.PCB_TRACK(board);t.SetStart(pt(x,44.0));t.SetEnd(pt(x,yb))
    t.SetWidth(p.FromMM(width));t.SetLayer(p.F_Cu);t.SetNet(board.FindNet('N12V_PROTECTED'))
    return t

def main():
  if sha(BOARD)!=EXPECTED_SHA:raise RuntimeError('prior native board SHA drift')
  nets_path=FROZEN/'03_src/rules/nets.yaml'
  if sha(nets_path)!=EXPECTED_NETS_SHA:raise RuntimeError('frozen nets.yaml SHA drift')
  source=yaml.safe_load(nets_path.read_text())
  cls=source['classes']['INPUT_TRUNK']
  if 'N12V_PROTECTED' not in cls['nets'] or cls['min_width']!='1.2mm' or cls['clearance']!='0.2mm':
    raise RuntimeError('INPUT_TRUNK authority drift')
  b=p.LoadBoard(str(BOARD))
  u_pad=pad(b,'U_SPOKE8','1')
  if u_pad.GetShape()!=p.PAD_SHAPE_ROUNDRECT:raise RuntimeError('U.1 pad shape drift')
  pad_area=abs(float(poly(u_pad).Area()))/1e12
  u=u_pad.GetEffectiveShape(p.F_Cu)
  cap=pad(b,'C_SPOKE_IN8','1').GetEffectiveShape(p.F_Cu)
  bb=u.BBox();actual=tuple(mm(v) for v in (bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom()))
  if actual!=PAD:raise RuntimeError(f'U.1 pad box drift {actual}')
  foreign=[]
  for f in b.GetFootprints():
    for q in f.Pads():
      if q.GetNetname()=='N12V_PROTECTED' or not q.IsOnLayer(p.F_Cu):continue
      s=q.GetEffectiveShape(p.F_Cu);z=s.BBox()
      if mm(z.GetRight())<185 or mm(z.GetLeft())>192 or mm(z.GetBottom())<42 or mm(z.GetTop())>49:continue
      foreign.append((f.GetReference()+'.'+q.GetNumber(),s))
  for t in b.GetTracks():
    if t.GetNetname()=='N12V_PROTECTED' or not t.IsOnLayer(p.F_Cu):continue
    s=t.GetEffectiveShape(p.F_Cu);z=s.BBox()
    if mm(z.GetRight())<185 or mm(z.GetLeft())>192 or mm(z.GetBottom())<42 or mm(z.GetTop())>49:continue
    foreign.append((t.GetNetname()+':existing_track',s))
  results=[]
  for x,y in CANDIDATES:
    t=make_track(b,x,y);s=t.GetEffectiveShape(p.F_Cu)
    if not s.Collide(u,0) or not s.Collide(cap,0):continue
    gaps=sorted((gap(s,o),name) for name,o in foreign if gap(s,o) is not None)
    nearest=gaps[0]
    if nearest[0]<.2-1e-6:continue
    area=overlap(t,u_pad)
    results.append({'x_mm':x,'end_y_mm':y,'u1_overlap_area_mm2':area,
                    'u1_pad_fraction':round(area/pad_area,6),
                    'u1_center_contained':bool(s.Collide(u_pad.GetPosition(),0)),
                    'nearest_foreign':{'name':nearest[1],'gap_mm':nearest[0]},
                    'powerpad_gap_mm':gap(s,pad(b,'U_SPOKE8','11').GetEffectiveShape(p.F_Cu)),
                    'uvlo_pad_gap_mm':gap(s,pad(b,'U_SPOKE8','2').GetEffectiveShape(p.F_Cu))})
  results.sort(key=lambda z:(-z['u1_overlap_area_mm2'],z['x_mm'],z['end_y_mm']))
  current=next(v for v in results if v['x_mm']==188.3 and v['end_y_mm']==45.9)
  margin_frontier={str(need):next((v for v in results
      if v['nearest_foreign']['gap_mm']>=need),None)
      for need in (.2,.25,.3,.35,.4)}
  center_frontier={str(need):next((v for v in results
      if v['u1_center_contained'] and v['nearest_foreign']['gap_mm']>=need),None)
      for need in (.2,.25,.3,.35,.4)}
  out={'schema':1,'status':'BOUNDED_NATIVE_GEOMETRY_SCREEN','prior_board_sha256':EXPECTED_SHA,
       'frozen_nets_yaml_sha256':EXPECTED_NETS_SHA,
       'source_class':{'name':'INPUT_TRUNK','min_width_mm':1.2,'clearance_mm':.2,
                       'allocated_current':cls['current']},
       'pad_u1_box_mm':PAD,'pad_u1_native_roundrect_area_mm2':round(pad_area,8),
       'candidate_grid':{'x_mm':[187.9,188.5,.05],
             'endpoint_y_mm':[45.85,46.2,.025],'fixed_cap_endpoint_y_mm':44.0,
             'width_mm':1.2},
       'screened':len(CANDIDATES),'passing_contact_and_0p2_clearance':len(results),
       'current_route':current,'best_in_grid':results[0],
       'best_by_min_foreign_gap_mm':margin_frontier,
       'center_contained_best_by_min_foreign_gap_mm':center_frontier,
       'top_five':results[:5],
       'overlap_method':'KiCad TransformShapeToPolygon on native roundrect pad and 1.20mm track at 0.005mm inside error, BooleanIntersection area',
       'geometry_only':True}
  (HERE/'receipt.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
  print(json.dumps({'passing':len(results),'current':current,'best':results[0]},sort_keys=True))
if __name__=='__main__':main()
