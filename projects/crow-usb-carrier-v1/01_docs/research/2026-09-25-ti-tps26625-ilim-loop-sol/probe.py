#!/usr/bin/env python3
"""One bounded ILIM via-pair route on the pinned source-generated TI witness."""
from __future__ import annotations
import hashlib,importlib.util,json,math,sys,tempfile
from pathlib import Path
import yaml
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('output_probe',ROOT/'2026-09-25-ti-tps26625-output-loop-sol/probe.py')
out=importlib.util.module_from_spec(spec);spec.loader.exec_module(out)
base=out.base
BOARD=ROOT/'2026-09-25-ti-tps26625-output-loop-sol/candidate_filled_profile.kicad_pcb'
BOARD_SHA='28412ec5054d3b322ea03e37516aa969551beb1e2083b2fa0d2662863969dff4'
ROUTE=[(191.4,48.0),(191.95,47.95),(191.825,50.2),(191.825,51.0)]
WIDTH=.20;VIA_D=.60;DRILL=.30
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def gap(a,b):
 if a.Collide(b,0):return 0.
 lo,hi=0,p.FromMM(2)
 if not a.Collide(b,hi):return None
 while hi-lo>100:
  m=(lo+hi)//2
  if a.Collide(b,m):hi=m
  else:lo=m
 return round(base.mm(hi),6)
def add_track(b,start,end,layer):
 t=p.PCB_TRACK(b);t.SetStart(base.pt(*start));t.SetEnd(base.pt(*end));t.SetWidth(p.FromMM(WIDTH))
 t.SetLayer(layer);t.SetNet(b.FindNet('SPOKE_ILIM8'));b.Add(t);return t
def add_via(b,xy):
 v=p.PCB_VIA(b);v.SetPosition(base.pt(*xy));v.SetWidth(p.FromMM(VIA_D));v.SetDrill(p.FromMM(DRILL))
 v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet('SPOKE_ILIM8'));b.Add(v);return v
def main():
 if sha(BOARD)!=BOARD_SHA:raise RuntimeError('pinned output witness drift')
 if sha(base.PROFILE/'crow_carrier.kicad_pro')!=out.PROFILE_SHA:raise RuntimeError('profile drift')
 b=p.LoadBoard(str(BOARD));ledger=base.footprint_ledger(b)
 if len(ledger)!=569 or base.pad(b,'U_SPOKE8','7').GetNetname()!='SPOKE_ILIM8' or base.pad(b,'R_SPOKE_ILIM8','1').GetNetname()!='SPOKE_ILIM8':
  raise RuntimeError('source net/pad identity drift')
 # Existing copper and return are identical to the pinned board; only this leg is added.
 t1=add_track(b,ROUTE[0],ROUTE[1],p.F_Cu)
 v1=add_via(b,ROUTE[1]);middle=add_track(b,ROUTE[1],ROUTE[2],p.B_Cu)
 v2=add_via(b,ROUTE[2]);t2=add_track(b,ROUTE[2],ROUTE[3],p.F_Cu)
 copper_boxes=[]
 for obj in (t1,v1,middle,v2,t2):
  bb=obj.GetBoundingBox()
  copper_boxes.append([base.mm(z) for z in (bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom())])
 owner=yaml.safe_load(out.trial.prior.SOURCE.read_text())['placement']['regions']['analog_ch8']
 if any(x[0]<owner[0] or x[1]<owner[1] or x[2]>owner[2] or x[3]>owner[3] for x in copper_boxes):
  raise RuntimeError('ILIM path exceeds analog_ch8 owner region')
 envelope_hits=sorted(f.GetReference() for f in b.GetFootprints() if any(
  out.trial.prior.box_gap(out.trial.prior.full_box(f),box)<1e-6 for box in copper_boxes))
 if envelope_hits!=['R_SPOKE_ILIM8','U_SPOKE8']:
  raise RuntimeError(f'foreign footprint full-envelope hit {envelope_hits}')
 first=v1.GetEffectiveShape(p.F_Cu)
 neighbors=[]
 for f in b.GetFootprints():
  for q in f.Pads():
   if q.GetNumber() and q.GetNetname()!='SPOKE_ILIM8' and q.IsOnLayer(p.F_Cu):
    g=gap(first,q.GetEffectiveShape(p.F_Cu))
    if g is not None:neighbors.append((g,f.GetReference()+'.'+q.GetNumber()))
 for t in b.GetTracks():
  if t.GetNetname()!='SPOKE_ILIM8' and t.IsOnLayer(p.F_Cu):
   g=gap(first,t.GetEffectiveShape(p.F_Cu))
   if g is not None:neighbors.append((g,'track:'+t.GetNetname()))
 neighbors.sort()
 with tempfile.TemporaryDirectory(prefix='crow-ilim-') as tmp:
  root=Path(tmp);before=root/'before.kicad_pcb';after=root/'after.kicad_pcb'
  p.SaveBoard(str(after),b)
  original=p.LoadBoard(str(BOARD));p.SaveBoard(str(before),original)
  prof=root/'profile';prof.mkdir()
  _,d0,via0,_=base.profile('before',before,prof)
  result,d1,via1,_=base.profile('after',after,prof)
  n=p.LoadBoard(str(result));n.BuildConnectivity();conn=n.GetConnectivity()
  if base.footprint_ledger(n)!=ledger:raise RuntimeError('footprint/pad pose drift')
  linked=sorted(x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
    for x in conn.GetConnectedItems(base.pad(n,'U_SPOKE8','7')) if isinstance(x,p.PAD))
  rtn=sorted(x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
    for x in conn.GetConnectedItems(base.pad(n,'U_SPOKE8','11')) if isinstance(x,p.PAD))
  gnd=sorted(x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
    for x in conn.GetConnectedItems(base.pad(n,'U_SPOKE8','6')) if isinstance(x,p.PAD))
  i0=set(map(base.issue,d0['violations']));i1=set(map(base.issue,d1['violations']))
  added=sorted((z[0],z[1]) for z in i1-i0)
  removed=sorted((z[0],z[1]) for z in i0-i1)
  receipt={'schema':1,'status':'REJECT_ILIM_ROUTE_NATIVE_CLEARANCE',
    'pinned_board_sha256':BOARD_SHA,'profile_sha256':out.PROFILE_SHA,
    'source_width_mm':WIDTH,'source_default_clearance_mm':.15,
    'route_vertices_mm':ROUTE,'route_layers':['F.Cu','B.Cu','F.Cu'],
    'route_copper_boxes_mm':copper_boxes,'analog_ch8_owner_mm':owner,
    'full_envelope_hits_endpoint_refs_only':envelope_hits,
    'via_outer_drill_mm':[VIA_D,DRILL],
    'signal_centerline_length_mm':round(sum(math.dist(a,c) for a,c in zip(ROUTE,ROUTE[1:])),6),
    'first_via_nearest_foreign_copper_gaps_mm':neighbors[:8],
    'u7_to_resistor_pad_native_connected':'R_SPOKE_ILIM8.1' in linked,
    'gnd_rtn_separate':not(set(gnd)&set(rtn)),
    'fixed_27_and_footprint_pad_poses_unchanged':True,
    'native_profile':{'violations':[len(d0['violations']),len(d1['violations'])],
      'unconnected':[len(d0['unconnected_items']),len(d1['unconnected_items'])],
      'added_issue_identities':len(i1-i0),'removed_issue_identities':len(i0-i1),
      'added_issue_summaries':added,'removed_issue_summaries':removed,
      'via_process_fails':[via0.get('fails'),via1.get('fails')]},
    'closed_qualified_ilim_loop_area_mm2':None}
  (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
  print(json.dumps({'nearest':neighbors[:4],'profile':receipt['native_profile'],'connected':receipt['u7_to_resistor_pad_native_connected']}))
if __name__=='__main__':main()
