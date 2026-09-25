#!/usr/bin/env python3
"""One source-generated TPS26625 output-bypass signal-leg trial."""
from __future__ import annotations
import hashlib,importlib.util,json,math,shutil,sys,tempfile
from pathlib import Path
import yaml
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('pinned_input_loop',ROOT/'2026-09-25-ti-tps26625-input-loop-sol/loop_probe.py')
inp=importlib.util.module_from_spec(spec);spec.loader.exec_module(inp)
spec2=importlib.util.spec_from_file_location('pinned_u1_screen',ROOT/'2026-09-25-ti-tps26625-input-pad-launch-sol/screen.py')
geom=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(geom)
base=inp.base;trial=inp.trial
START=(191.4,46.3);VIA_A=(191.4,45.8);VIA_B=(193.65,45.8);END=(193.65,46.7);WIDTH=.5
GND_PATH=trial.LOCAL_RETURN_PATHS['gnd_cout_to_join'][1][:-1]+trial.LOCAL_RETURN_PATHS['gnd_cin_to_u6'][1][2:]
PROFILE_SHA='7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def add_track(board,net,start,end,width,layer=p.F_Cu):
 t=p.PCB_TRACK(board);t.SetStart(base.pt(*start));t.SetEnd(base.pt(*end))
 t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(board.FindNet(net));board.Add(t)
 return t
def add_via(board,net,point):
 t=p.PCB_VIA(board);t.SetPosition(base.pt(*point));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3))
 t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(board.FindNet(net));board.Add(t)
 return t
def area(v):return round(abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(v,v[1:]+v[:1])))/2,6)
def nearby_gaps(board,track):
 s=track.GetEffectiveShape(p.F_Cu);out=[]
 for f in board.GetFootprints():
  for q in f.Pads():
   if not q.IsOnLayer(p.F_Cu) or q.GetNetname()=='N12V_POD8':continue
   g=inp.copper_gap(s,q.GetEffectiveShape(p.F_Cu))
   if g is not None:out.append((g,f.GetReference()+'.'+q.GetNumber()))
 for q in board.GetTracks():
  if q is track or q.GetNetname()=='N12V_POD8' or not q.IsOnLayer(p.F_Cu):continue
  g=inp.copper_gap(s,q.GetEffectiveShape(p.F_Cu))
  if g is not None:out.append((g,'track:'+q.GetNetname()))
 return sorted(out)[:8]

def main():
 if sha(base.PROFILE/'crow_carrier.kicad_pro')!=PROFILE_SHA:raise RuntimeError('profile drift')
 if sha(inp.PREV/'candidate_filled_profile.kicad_pcb')!=inp.PINNED_PREV_BOARD_SHA:
  raise RuntimeError('partial-return baseline drift')
 nets=yaml.safe_load((trial.prior.TI/'03_src/rules/nets.yaml').read_text())['classes']['POD_POWER']
 if nets['min_width']!='0.5mm' or nets['clearance']!='0.2mm' or 'N12V_POD8' not in nets['nets']:
  raise RuntimeError('POD_POWER source rule drift')
 with tempfile.TemporaryDirectory(prefix='crow-tps26625-out-') as tmp:
  root=Path(tmp);source,inputs=trial.generate(root/'source')
  b=p.LoadBoard(str(source));trial.prior.add_candidate(b);trial.add_local_returns(b)
  prev=p.LoadBoard(str(inp.PREV/'candidate_filled_profile.kicad_pcb'))
  if base.footprint_ledger(b)!=base.footprint_ledger(prev) or inp.tracks(b)!=inp.tracks(prev):
   raise RuntimeError('source-generated partial-return baseline drift')
  u1=add_track(b,'N12V_PROTECTED',(188.35,46.025),(188.35,44.0),1.2)
  before=root/'before.kicad_pcb';p.SaveBoard(str(before),b)
  out=add_track(b,'N12V_POD8',START,VIA_A,WIDTH)
  add_via(b,'N12V_POD8',VIA_A)
  add_track(b,'N12V_POD8',VIA_A,VIA_B,WIDTH,p.B_Cu)
  add_via(b,'N12V_POD8',VIA_B)
  add_track(b,'N12V_POD8',VIA_B,END,WIDTH)
  gaps=nearby_gaps(b,out)
  after=root/'after.kicad_pcb';p.SaveBoard(str(after),b)
  prof=root/'profile';prof.mkdir()
  _,d0,v0,_=base.profile('before',before,prof)
  filled,d1,v1,_=base.profile('after',after,prof)
  i0=set(map(base.issue,d0['violations']));i1=set(map(base.issue,d1['violations']))
  n=p.LoadBoard(str(filled));n.BuildConnectivity();conn=n.GetConnectivity()
  if base.footprint_ledger(n)!=base.footprint_ledger(prev):raise RuntimeError('pad/pose drift')
  def links(ref,pin):
   return sorted(x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
       for x in conn.GetConnectedItems(base.pad(n,ref,pin)) if isinstance(x,p.PAD))
  supply=links('U_SPOKE8','10');gnd=links('U_SPOKE8','6');rtn=links('U_SPOKE8','11')
  if 'C_SPOKE_OUT8.1' not in supply or 'C_SPOKE_OUT8.2' not in gnd or 'U_SPOKE8.11' in gnd or 'U_SPOKE8.6' in rtn:
   raise RuntimeError('OUT/GND/RTN connectivity failure')
  z=[q for q in n.Zones() if q.GetNetname()=='GND' and p.In1_Cu in q.GetLayerSet().Seq()]
  if len(z)!=1 or not z[0].IsFilled():raise RuntimeError('filled In1 GND absent')
  fill=z[0].GetFilledPolysList(p.In1_Cu);common=set(range(fill.OutlineCount()))
  for xy in GND_PATH:
   point=base.pt(*xy)
   if not fill.Contains(point):raise RuntimeError(f'GND path outside fill {xy}')
   common&={i for i in range(fill.OutlineCount()) if fill.Outline(i).PointInside(point)}
  if not common:raise RuntimeError('GND path not on one filled polygon')
  t=next(q for q in n.GetTracks() if q.GetNetname()=='N12V_POD8' and q.GetLayer()==p.F_Cu and abs(base.mm(q.GetStart().x)-START[0])<1e-6 and abs(base.mm(q.GetStart().y)-START[1])<1e-6)
  t2=next(q for q in n.GetTracks() if q.GetNetname()=='N12V_POD8' and q.GetLayer()==p.F_Cu and abs(base.mm(q.GetEnd().x)-END[0])<1e-6 and abs(base.mm(q.GetEnd().y)-END[1])<1e-6)
  land=base.pad(n,'U_SPOKE8','10');cap=base.pad(n,'C_SPOKE_OUT8','1')
  points=[(191.4,46.5),START,VIA_A,VIA_B,END,(195.55,46.7)]+GND_PATH[1:]
  if points[-1]!=(191.4,48.5):raise RuntimeError('GND path end drift')
  receipt={'schema':1,'status':'RESEARCH_OUTPUT_BYPASS_SIGNAL_LEG',
    'source_input_sha256':inputs,'prior_partial_return_sha256':inp.PINNED_PREV_BOARD_SHA,
    'native_footprints':len(base.footprint_ledger(n)),'fixed_27_and_pad_identities_preserved':True,
    'input_u1_track':{'start_mm':[188.35,46.025],'end_mm':[188.35,44.0],'width_mm':1.2},
    'output_track':{'net':'N12V_POD8','layer_path':['F.Cu','B.Cu','F.Cu'],
      'vertices_mm':[START,VIA_A,VIA_B,END],'vias_mm':[VIA_A,VIA_B],
      'via_outer_diameter_mm':.6,'via_drill_mm':.3,'width_mm':WIDTH,
      'centerline_length_mm':round(math.dist(START,VIA_A)+math.dist(VIA_A,VIA_B)+math.dist(VIA_B,END),6),
      'first_leg_nearest_foreign_copper_gaps_mm':gaps,
      'u10_center_contained':bool(t.GetEffectiveShape(p.F_Cu).Collide(land.GetPosition(),0)),
      'u10_overlap_area_mm2':geom.overlap(t,land),
      'cout1_center_contained':bool(t2.GetEffectiveShape(p.F_Cu).Collide(cap.GetPosition(),0)),
      'cout1_overlap_area_mm2':geom.overlap(t2,cap)},
    'output_loop':{'polygon_vertices_mm':points,'projected_centerline_area_mm2':area(points),
      'gnd_return_path_length_mm':round(sum(math.dist(a,b) for a,b in zip(GND_PATH,GND_PATH[1:])),6),
      'output_pad_center_path_surrogate_mm':round(math.dist((191.4,46.5),START)+math.dist(START,VIA_A)+math.dist(VIA_A,VIA_B)+math.dist(VIA_B,END),6),
      'gnd_same_filled_in1_outline_ids':sorted(common),
      'closure_chords':['C_SPOKE_OUT8.1→.2 internal capacitor','U_SPOKE8.6→.10 internal device']},
    'native_connected_output_pads':supply,'native_connected_gnd_pads':gnd,'native_connected_rtn_pads':rtn,
    'profile':{'violations':[len(d0['violations']),len(d1['violations'])],
      'unconnected':[len(d0['unconnected_items']),len(d1['unconnected_items'])],
      'added_issue_identities':len(i1-i0),'removed_issue_identities':len(i0-i1),
      'added_issue_types':sorted({x[0] for x in i1-i0}),
      'via_process_fails':[v0.get('fails'),v1.get('fails')]},
    'filled_board_sha256_observation':sha(filled)}
  shutil.copy2(filled,HERE/'candidate_filled_profile.kicad_pcb')
  (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
  print(json.dumps({'profile':receipt['profile'],'output':receipt['output_track'],'area':receipt['output_loop']['projected_centerline_area_mm2']}))
if __name__=='__main__':main()
