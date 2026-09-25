#!/usr/bin/env python3
"""Native necessary-condition screen for a 0.60/0.30 ILIM via mouth."""
from __future__ import annotations
from collections import deque
import hashlib,importlib.util,json,sys
from pathlib import Path
import yaml
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('ilim_probe',ROOT/'2026-09-25-ti-tps26625-ilim-loop-sol/probe.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
base=prior.base
X0,Y0,STEP,NX,NY=190.5,42.0,.025,141,381
SOURCE=(191.4,48.0)
CLEAR=p.FromMM(.15)-100 # 0.0001-mm arithmetic tolerance, not a rule change
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pt(x,y):return base.pt(round(x,6),round(y,6))
def place(i,j):return (round(X0+i*STEP,6),round(Y0+j*STEP,6))
def collision_gap(a,b):
 if a.Collide(b,0):return 0.
 lo,hi=0,p.FromMM(2)
 if not a.Collide(b,hi):return None
 while hi-lo>100:
  mid=(lo+hi)//2
  if a.Collide(b,mid):hi=mid
  else:lo=mid
 return round(base.mm(hi),6)
def via(b,xy):
 v=p.PCB_VIA(b);v.SetPosition(pt(*xy));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3))
 v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet('SPOKE_ILIM8'))
 return v
def track_disc(b,xy):
 t=p.PCB_TRACK(b);t.SetStart(pt(*xy));t.SetEnd(pt(*xy));t.SetWidth(p.FromMM(.2))
 t.SetLayer(p.F_Cu);t.SetNet(b.FindNet('SPOKE_ILIM8'))
 return t
def main():
 if sha(prior.BOARD)!=prior.BOARD_SHA:raise RuntimeError('pinned board drift')
 nets_path=prior.out.trial.prior.TI/'03_src/rules/nets.yaml'
 nets=yaml.safe_load(nets_path.read_text())
 if nets['default_track_width']!='0.20mm' or nets['default_clearance']!='0.15mm':
  raise RuntimeError('default signal class drift')
 b=p.LoadBoard(str(prior.BOARD))
 if len(base.footprint_ledger(b))!=569:raise RuntimeError('footprint count drift')
 obstacles=[]
 for f in b.GetFootprints():
  for q in f.Pads():
   if not q.GetNumber() or q.GetNetname()=='SPOKE_ILIM8' or not q.IsOnLayer(p.F_Cu):continue
   z=q.GetBoundingBox()
   if base.mm(z.GetRight())<189 or base.mm(z.GetLeft())>195 or base.mm(z.GetBottom())<41 or base.mm(z.GetTop())>52:continue
   obstacles.append((f.GetReference()+'.'+q.GetNumber(),q.GetEffectiveShape(p.F_Cu)))
 for t in b.GetTracks():
  if t.GetNetname()=='SPOKE_ILIM8' or not t.IsOnLayer(p.F_Cu):continue
  z=t.GetBoundingBox()
  if base.mm(z.GetRight())<189 or base.mm(z.GetLeft())>195 or base.mm(z.GetBottom())<41 or base.mm(z.GetTop())>52:continue
  obstacles.append(('track:'+t.GetNetname(),t.GetEffectiveShape(p.F_Cu)))
 foreign_envelopes=[]
 for f in b.GetFootprints():
  if f.GetReference() in ('U_SPOKE8','R_SPOKE_ILIM8'):continue
  box=prior.out.trial.prior.full_box(f)
  if box[2]<189 or box[0]>195 or box[3]<41 or box[1]>52:continue
  foreign_envelopes.append((f.GetReference(),prior.out.trial.prior.rect(box)))
 free=set();via_clear=set()
 for i in range(NX):
  for j in range(NY):
   xy=place(i,j)
   disc=track_disc(b,xy).GetEffectiveShape(p.F_Cu)
   if all(not disc.Collide(shape,CLEAR) for _,shape in obstacles) and all(
       not disc.Collide(shape,0) for _,shape in foreign_envelopes):free.add((i,j))
   shape=via(b,xy).GetEffectiveShape(p.F_Cu)
   if all(not shape.Collide(q,CLEAR) for _,q in obstacles) and all(
       not shape.Collide(q,0) for _,q in foreign_envelopes):via_clear.add((i,j))
 start=(round((SOURCE[0]-X0)/STEP),round((SOURCE[1]-Y0)/STEP))
 if start not in free:raise RuntimeError('U7 source pad no F.Cu launch mouth')
 reached={start};todo=deque([start])
 while todo:
  i,j=todo.popleft()
  for di in (-1,0,1):
   for dj in (-1,0,1):
    if not di and not dj:continue
    k=(i+di,j+dj)
    if k in free and k not in reached:reached.add(k);todo.append(k)
 candidates=sorted(reached&via_clear)
 # Exact limiting corner of the first east-side U7 via pocket. Both GND
 # boundaries force x<=191.95, y<=47.95; U8 separation grows toward corner.
 limit=(191.95,47.95);s=via(b,limit).GetEffectiveShape(p.F_Cu)
 critical={}
 for name,q in obstacles:
  if name not in ('U_SPOKE8.8','U_SPOKE8.6','U_SPOKE8.11','track:GND'):continue
  g=collision_gap(s,q)
  if g is not None:critical[name]=min(g,critical.get(name,float('inf')))
 reachable_xy=[place(*z) for z in reached]
 reached_box=[min(x for x,y in reachable_xy),min(y for x,y in reachable_xy),
              max(x for x,y in reachable_xy),max(y for x,y in reachable_xy)]
 reached_boundary_sites=sum(i in (0,NX-1) or j in (0,NY-1) for i,j in reached)
 result={'schema':1,'status':'IMMEDIATE_MOUTH_BLOCKED_REMOTE_CENTERS_EXIST',
  'pinned_board_sha256':prior.BOARD_SHA,'nets_yaml_sha256':sha(nets_path),
  'source_default_track_width_mm':.2,'source_default_clearance_mm':.15,
  'grid_mm':{'x':[X0,round(X0+(NX-1)*STEP,3)],'y':[Y0,round(Y0+(NY-1)*STEP,3)],
             'step':STEP,'sites':NX*NY},
  'copper_obstacle_count':len(obstacles),'foreign_full_envelope_refs':[name for name,_ in foreign_envelopes],
  'launch_center_clear_sites':len(free),
  'u7_reachable_launch_center_sites_eight_neighbor_overapprox':len(reached),
  'u7_reachable_center_bbox_mm':reached_box,
  'u7_reachable_on_screen_boundary_sites':reached_boundary_sites,
  'via_center_clear_sites':len(via_clear),
  'reachable_and_via_clear_sites':len(candidates),
  'reachable_and_via_clear_coordinates_mm':[place(*z) for z in candidates[:20]],
  'first_mouth_east_box_mm':[191.7,47.5,191.95,47.95],
  'first_mouth_extreme_mm':limit,'first_mouth_extreme_gaps_mm':critical,
  'first_mouth_restrictions_mm':{'east_gnd_vertical_via_center_x_max':191.95,
      'south_gnd_horizontal_via_center_y_max':47.95,
      'u8_clearance_at_joint_max':critical['U_SPOKE8.8']},
  'scope':'F.Cu necessary condition for a 0.20-mm launch and 0.60-mm via; eight-neighbor reachability overapproximates centerline passage. Remote clear via centers require a complete multilayer route check.'}
 (HERE/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:result[k] for k in ('launch_center_clear_sites','u7_reachable_launch_center_sites_eight_neighbor_overapprox','via_center_clear_sites','reachable_and_via_clear_sites','first_mouth_extreme_gaps_mm')}))
if __name__=='__main__':main()
