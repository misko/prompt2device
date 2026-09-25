#!/usr/bin/env python3
"""One farther-north ILIM via route after the finite mouth screen."""
from __future__ import annotations
import hashlib,importlib.util,json,math,sys,tempfile
from pathlib import Path
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('ilim_probe',ROOT/'2026-09-25-ti-tps26625-ilim-loop-sol/probe.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
base=prior.base
VIA1=(191.95,45.15);VIA2=(191.825,50.2)
PATH=[(191.4,48.0),(192.0,48.0),(192.0,45.15),VIA1,VIA2,(191.825,51.0)]
LAYERS=[p.F_Cu,p.F_Cu,p.F_Cu,p.In2_Cu,p.F_Cu]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def add_track(b,a,c,layer):
 t=p.PCB_TRACK(b);t.SetStart(base.pt(*a));t.SetEnd(base.pt(*c));t.SetWidth(p.FromMM(.2))
 t.SetLayer(layer);t.SetNet(b.FindNet('SPOKE_ILIM8'));b.Add(t);return t
def add_via(b,xy):
 v=p.PCB_VIA(b);v.SetPosition(base.pt(*xy));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3))
 v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet('SPOKE_ILIM8'));b.Add(v);return v
def main():
 if sha(prior.BOARD)!=prior.BOARD_SHA:raise RuntimeError('pinned board drift')
 b=p.LoadBoard(str(prior.BOARD));ledger=base.footprint_ledger(b)
 before_tracks=prior.out.inp.tracks(b)
 added=[]
 for k,(a,c) in enumerate(zip(PATH,PATH[1:])):
  if a==VIA1:added.append(add_via(b,VIA1))
  if a==VIA2:added.append(add_via(b,VIA2))
  added.append(add_track(b,a,c,LAYERS[k]))
 boxes=[]
 for q in added:
  z=q.GetBoundingBox();boxes.append([base.mm(v) for v in
   (z.GetLeft(),z.GetTop(),z.GetRight(),z.GetBottom())])
 hits=sorted(f.GetReference() for f in b.GetFootprints() if any(
  prior.out.trial.prior.box_gap(prior.out.trial.prior.full_box(f),box)<1e-6 for box in boxes))
 if hits!=['R_SPOKE_ILIM8','U_SPOKE8']:raise RuntimeError(f'foreign body/courtyard hit {hits}')
 if any(q[0]<179 or q[1]<42 or q[2]>201 or q[3]>84 for q in boxes):
  raise RuntimeError('source analog_ch8 owner violation')
 with tempfile.TemporaryDirectory(prefix='crow-ilim-mouth-') as tmp:
  root=Path(tmp);before=root/'before.kicad_pcb';after=root/'after.kicad_pcb'
  p.SaveBoard(str(before),p.LoadBoard(str(prior.BOARD)));p.SaveBoard(str(after),b)
  prof=root/'profile';prof.mkdir()
  _,d0,v0,_=base.profile('before',before,prof)
  filled,d1,v1,_=base.profile('after',after,prof)
  n=p.LoadBoard(str(filled));n.BuildConnectivity();conn=n.GetConnectivity()
  if base.footprint_ledger(n)!=ledger:raise RuntimeError('pad/pose drift')
  if not set(before_tracks).issubset(set(prior.out.inp.tracks(n))):
   raise RuntimeError('prior copper drift')
  def linked(ref,pin):return sorted(x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
   for x in conn.GetConnectedItems(base.pad(n,ref,pin)) if isinstance(x,p.PAD))
  ilim=linked('U_SPOKE8','7');gnd=linked('U_SPOKE8','6');rtn=linked('U_SPOKE8','11')
  zones=[z for z in n.Zones() if z.GetNetname()=='GND' and p.In1_Cu in z.GetLayerSet().Seq()]
  if len(zones)!=1 or not zones[0].IsFilled():raise RuntimeError('filled In1 GND absent')
  fill=zones[0].GetFilledPolysList(p.In1_Cu)
  common=set(range(fill.OutlineCount()))
  for net,vertices in prior.out.trial.LOCAL_RETURN_PATHS.values():
   if net!='GND':continue
   for xy in vertices:
    point=base.pt(*xy)
    if not fill.Contains(point):raise RuntimeError(f'GND path outside fill {xy}')
    common&={i for i in range(fill.OutlineCount()) if fill.Outline(i).PointInside(point)}
  if not common:raise RuntimeError('GND return not over one In1 fill polygon')
  old=set(map(base.issue,d0['violations']));new=set(map(base.issue,d1['violations']))
  added_details=[{'type':v['type'],'description':v['description'],
      'items':[{'description':q['description'],'pos':q['pos']} for q in v['items']]}
      for v in d1['violations'] if base.issue(v) in new-old]
  result={'schema':1,'status':'ILIM_NORTH_VIA_NATIVE_TRIAL',
   'pinned_board_sha256':prior.BOARD_SHA,'profile_sha256':prior.out.PROFILE_SHA,
   'path_vertices_mm':PATH,'layers':['F.Cu','F.Cu','F.Cu','In2.Cu','F.Cu'],
   'width_mm':.2,'via_outer_drill_mm':[.6,.3],
   'signal_centerline_length_mm':round(sum(math.dist(a,c) for a,c in zip(PATH,PATH[1:])),6),
   'new_copper_boxes_mm':boxes,'full_envelope_hits':hits,
   'native_ilim_pads_connected':'R_SPOKE_ILIM8.1' in ilim,
   'prior_input_output_gnd_witnesses_connected':all([
       'C_SPOKE_IN8.1' in linked('U_SPOKE8','1'),
       'C_SPOKE_OUT8.1' in linked('U_SPOKE8','10'),
       'C_SPOKE_OUT8.2' in gnd]),
   'gnd_rtn_distinct':not(set(gnd)&set(rtn)),
   'gnd_return_same_filled_in1_outline_ids':sorted(common),
   'native_profile':{'violations':[len(d0['violations']),len(d1['violations'])],
      'unconnected':[len(d0['unconnected_items']),len(d1['unconnected_items'])],
      'added_issue_identities':len(new-old),'removed_issue_identities':len(old-new),
      'added_issue_summaries':sorted((x[0],x[1]) for x in new-old),
      'added_issue_details':added_details,
      'removed_issue_summaries':sorted((x[0],x[1]) for x in old-new),
      'via_process_fails':[v0.get('fails'),v1.get('fails')]},
   'qualified_ilim_loop_area_mm2':None}
  (HERE/'route_receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
  print(json.dumps({'profile':result['native_profile'],'ilim':result['native_ilim_pads_connected'],'length':result['signal_centerline_length_mm']}))
if __name__=='__main__':main()
