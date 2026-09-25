#!/usr/bin/env python3
"""One coupled output-crossover/ILIM route trial on the pinned TI witness."""
from __future__ import annotations
import hashlib,importlib.util,json,math,subprocess,sys,tempfile
from pathlib import Path
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('mouth_probe',ROOT/'2026-09-25-ti-tps26625-ilim-mouth-sol/route.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
base=old.base
BOARD=old.prior.BOARD;BOARD_SHA=old.prior.BOARD_SHA
OUT=[(191.4,46.3),(191.4,46.1),(193.65,46.1),(193.65,46.7)]
ILIM=[(191.4,48.0),(192.05,48.0),(192.05,45.15),(191.95,45.15),
      (192.1,45.5),(192.1,46.7),(191.825,50.2),(191.825,51.0)]
ILIM_LAYERS=[p.F_Cu,p.F_Cu,p.F_Cu,p.In2_Cu,p.In2_Cu,p.In2_Cu,p.F_Cu]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def track(b,net,a,c,width,layer):
 t=p.PCB_TRACK(b);t.SetStart(base.pt(*a));t.SetEnd(base.pt(*c));t.SetWidth(p.FromMM(width))
 t.SetLayer(layer);t.SetNet(b.FindNet(net));b.Add(t);return t
def via(b,net,xy):
 v=p.PCB_VIA(b);v.SetPosition(base.pt(*xy));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3))
 v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet(net));b.Add(v);return v
def area(points):
 return round(abs(sum(a[0]*c[1]-c[0]*a[1] for a,c in zip(points,points[1:]+points[:1])))/2,6)
def main():
 if sha(BOARD)!=BOARD_SHA:raise RuntimeError('pinned output board drift')
 b=p.LoadBoard(str(BOARD));ledger=base.footprint_ledger(b)
 original=old.prior.out.inp.tracks(b)
 removed=[q for q in b.GetTracks() if q.GetNetname()=='N12V_POD8']
 if len(removed)!=5:raise RuntimeError(f'output crossover denominator {len(removed)}')
 for q in removed:b.Remove(q)
 revised=[]
 revised.append(track(b,'N12V_POD8',OUT[0],OUT[1],.5,p.F_Cu))
 revised.append(via(b,'N12V_POD8',OUT[1]))
 revised.append(track(b,'N12V_POD8',OUT[1],OUT[2],.5,p.B_Cu))
 revised.append(via(b,'N12V_POD8',OUT[2]))
 revised.append(track(b,'N12V_POD8',OUT[2],OUT[3],.5,p.F_Cu))
 added=[]
 for k,(a,c) in enumerate(zip(ILIM,ILIM[1:])):
  if a==ILIM[3]:added.append(via(b,'SPOKE_ILIM8',a))
  if a==ILIM[6]:added.append(via(b,'SPOKE_ILIM8',a))
  added.append(track(b,'SPOKE_ILIM8',a,c,.2,ILIM_LAYERS[k]))
 boxes=[]
 for q in revised+added:
  z=q.GetBoundingBox();boxes.append([base.mm(v) for v in
   (z.GetLeft(),z.GetTop(),z.GetRight(),z.GetBottom())])
 if any(q[0]<179 or q[1]<42 or q[2]>201 or q[3]>84 for q in boxes):
  raise RuntimeError('source analog_ch8 owner violation')
 hits=sorted(f.GetReference() for f in b.GetFootprints() if any(
  old.prior.out.trial.prior.box_gap(old.prior.out.trial.prior.full_box(f),box)<1e-6 for box in boxes))
 if hits!=['C_SPOKE_OUT8','R_SPOKE_ILIM8','U_SPOKE8']:
  raise RuntimeError(f'foreign full-envelope intersection {hits}')
 with tempfile.TemporaryDirectory(prefix='crow-coupled-copper-') as tmp:
  root=Path(tmp);before=root/'before.kicad_pcb';after=root/'after.kicad_pcb'
  p.SaveBoard(str(before),p.LoadBoard(str(BOARD)));p.SaveBoard(str(after),b)
  prof=root/'profile';prof.mkdir()
  _,d0,v0,_=base.profile('before',before,prof)
  via_failure=None
  try:
   filled,d1,v1,_=base.profile('after',after,prof)
  except RuntimeError as e:
   # The full profile stops at V-VIP before invoking native DRC. Continue the
   # DRC command on that exact generated .pro/.dru/POFV board for a bounded
   # diagnostic delta; the V-PROCESS failure remains rejecting.
   via_failure=next((line.strip() for line in str(e).splitlines() if 'FAIL V-VIP' in line),str(e)[-500:])
   filled=prof/'after/crow_carrier.kicad_pcb'
   drc_path=prof/'after/drc.json'
   q=subprocess.run(['kicad-cli','pcb','drc','--format','json','--refill-zones',
       '--save-board','--output',str(drc_path),str(filled)],capture_output=True,text=True)
   if not drc_path.exists():raise RuntimeError(f'native DRC output missing: {q.stderr[-500:]}')
   d1=json.loads(drc_path.read_text());v1={'fails':[via_failure]}
  n=p.LoadBoard(str(filled));n.BuildConnectivity();conn=n.GetConnectivity()
  if base.footprint_ledger(n)!=ledger:raise RuntimeError('pad/pose drift')
  # All old non-output tracks remain; only the five output primitives changed.
  old_other=[x for x in original if x[0]!='N12V_POD8']
  if not set(old_other).issubset(set(old.prior.out.inp.tracks(n))):
   raise RuntimeError('non-output witness copper drift')
  def linked(ref,pin):return sorted(q.GetParentFootprint().GetReference()+'.'+q.GetNumber()
   for q in conn.GetConnectedItems(base.pad(n,ref,pin)) if isinstance(q,p.PAD))
  links={'input':linked('U_SPOKE8','1'),'output':linked('U_SPOKE8','10'),
         'ilim':linked('U_SPOKE8','7'),'gnd':linked('U_SPOKE8','6'),
         'rtn':linked('U_SPOKE8','11')}
  if not all(('C_SPOKE_IN8.1' in links['input'],'C_SPOKE_OUT8.1' in links['output'],
      'R_SPOKE_ILIM8.1' in links['ilim'],'C_SPOKE_IN8.2' in links['gnd'],
      'C_SPOKE_OUT8.2' in links['gnd'],'R_SPOKE_ILIM8.2' in links['rtn'])):
   raise RuntimeError('named local connectivity failure')
  if set(links['gnd'])&set(links['rtn']):raise RuntimeError('GND/RTN bridge')
  zone=[z for z in n.Zones() if z.GetNetname()=='GND' and p.In1_Cu in z.GetLayerSet().Seq()]
  if len(zone)!=1 or not zone[0].IsFilled():raise RuntimeError('filled In1 GND absent')
  fill=zone[0].GetFilledPolysList(p.In1_Cu);common=set(range(fill.OutlineCount()))
  for net,verts in old.prior.out.trial.LOCAL_RETURN_PATHS.values():
   if net!='GND':continue
   for xy in verts:
    q=base.pt(*xy)
    if not fill.Contains(q):raise RuntimeError(f'GND path outside fill {xy}')
    common&={i for i in range(fill.OutlineCount()) if fill.Outline(i).PointInside(q)}
  if not common:raise RuntimeError('GND return split by vias')
  issues0=set(map(base.issue,d0['violations']));issues1=set(map(base.issue,d1['violations']))
  new=[{'type':z['type'],'description':z['description'],
        'items':[{'description':q['description'],'pos':q['pos']} for q in z['items']]}
       for z in d1['violations'] if base.issue(z) in issues1-issues0]
  output_points=[(191.4,46.5)]+OUT+[(195.55,46.7),(195.55,48.5),(192.5,48.5),(191.4,48.5)]
  ilim_points=ILIM+[(190.175,51.0),(190.175,49.8),(190.0,49.625),(190.0,47.5),
                    (189.0,48.5),(188.6,48.5)]
  output_return=[(195.55,46.7),(195.55,48.5),(192.5,48.5),(191.4,48.5)]
  ilim_return=[(190.175,51.0),(190.175,49.8),(190.0,49.625),(190.0,47.5),
               (189.0,48.5),(188.6,48.5)]
  valid=not(issues1-issues0 or issues0-issues1 or v0.get('fails') or v1.get('fails'))
  receipt={'schema':1,'status':'RULE_CLEAN_LOCAL_LOOP_WITNESS' if valid else 'REJECT_COUPLED_COPPER_TRIAL',
   'pinned_board_sha256':BOARD_SHA,'profile_sha256':old.prior.out.PROFILE_SHA,
   'native_footprints':len(ledger),'pad_poses_27_fixed_preserved':True,
   'removed_output_primitives':len(removed),'revised_output_vertices_mm':OUT,
   'revised_output_width_mm':.5,'revised_output_via_outer_drill_mm':[.6,.3],
   'revised_output_centerline_length_mm':round(sum(math.dist(a,c) for a,c in zip(OUT,OUT[1:])),6),
   'ilim_vertices_mm':ILIM,'ilim_width_mm':.2,'ilim_via_outer_drill_mm':[.6,.3],
   'ilim_centerline_length_mm':round(sum(math.dist(a,c) for a,c in zip(ILIM,ILIM[1:])),6),
   'gnd_output_return_centerline_length_mm':round(sum(math.dist(a,c) for a,c in zip(output_return,output_return[1:])),6),
   'rtn_ilim_return_centerline_length_mm':round(sum(math.dist(a,c) for a,c in zip(ilim_return,ilim_return[1:])),6),
   'changed_copper_boxes_mm':boxes,'full_envelope_hits':hits,
   'gnd_return_same_filled_in1_outline_ids':sorted(common),
   'named_connectivity':{k:v for k,v in links.items() if k!='gnd'},
   'gnd_rtn_distinct':True,
   'diagnostic_projected_centerline_area_mm2':{
       'input_existing':15.315625,'output':area(output_points),'ilim_rtn':area(ilim_points)},
   'admitted_new_loop_area_mm2':{'output':area(output_points) if valid else None,
                                 'ilim_rtn':area(ilim_points) if valid else None},
   'loop_projected_vertices_mm':{'output':output_points,'ilim_rtn':ilim_points},
   'native_profile':{'violations':[len(d0['violations']),len(d1['violations'])],
     'unconnected':[len(d0['unconnected_items']),len(d1['unconnected_items'])],
     'added_issue_identities':len(issues1-issues0),'removed_issue_identities':len(issues0-issues1),
     'added_issue_details':new,'via_process_fails':[v0.get('fails'),v1.get('fails')],
     'via_process_failure':via_failure}}
  (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
  print(json.dumps({'status':receipt['status'],'profile':receipt['native_profile'],
    'areas':receipt['diagnostic_projected_centerline_area_mm2']}))
if __name__=='__main__':main()
