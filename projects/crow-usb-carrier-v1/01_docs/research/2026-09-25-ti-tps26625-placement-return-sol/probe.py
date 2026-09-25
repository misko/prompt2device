#!/usr/bin/env python3
"""One source-generated six-member pose/return recut with a local ILIM mouth."""
from __future__ import annotations
import hashlib,importlib.util,json,math,sys,tempfile
from pathlib import Path
import yaml
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('output_probe',ROOT/'2026-09-25-ti-tps26625-output-loop-sol/probe.py')
out=importlib.util.module_from_spec(spec);spec.loader.exec_module(out)
base=out.base;trial=out.trial
PINNED=ROOT/'2026-09-25-ti-tps26625-output-loop-sol/candidate_filled_profile.kicad_pcb'
PINNED_SHA='28412ec5054d3b322ea03e37516aa969551beb1e2083b2fa0d2662863969dff4'
DVDT_POSE=[193.9,49.5,180]
GND_CIN=[(190.7,44.0),(192.0,43.8)]
GND_OUT=[(191.4,48.5),(192.7,48.5),(195.55,48.5),(195.55,46.7)]
RTN_ILIM=trial.LOCAL_RETURN_PATHS['rtn_rilim_to_ep11'][1]
RTN_DVDT=[(193.42,49.5),(190.0,49.5),(190.0,47.5)]
RTN_U3=trial.LOCAL_RETURN_PATHS['rtn_u3_to_ep11'][1]
RTN_U5=trial.LOCAL_RETURN_PATHS['rtn_u5_to_ep11'][1]
OUT=[(191.4,46.3),(193.65,46.3),(193.65,46.7)]
ILIM=[(191.4,48.0),(192.1,47.9),(191.825,50.2),(191.825,51.0)]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def track(b,net,a,c,width,layer=p.F_Cu):
 t=p.PCB_TRACK(b);t.SetStart(base.pt(*a));t.SetEnd(base.pt(*c));t.SetWidth(p.FromMM(width))
 t.SetLayer(layer);t.SetNet(b.FindNet(net));b.Add(t);return t
def path(b,net,vertices,width,layer=p.F_Cu):
 return [track(b,net,a,c,width,layer) for a,c in zip(vertices,vertices[1:])]
def via(b,net,xy):
 v=p.PCB_VIA(b);v.SetPosition(base.pt(*xy));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3))
 v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet(net));b.Add(v);return v
def gap(a,b):
 if a.Collide(b,0):return 0.
 lo,hi=0,p.FromMM(2)
 if not a.Collide(b,hi):return None
 while hi-lo>100:
  m=(lo+hi)//2
  if a.Collide(b,m):hi=m
  else:lo=m
 return round(base.mm(hi),6)
def area(points):return round(abs(sum(a[0]*c[1]-c[0]*a[1] for a,c in zip(points,points[1:]+points[:1])))/2,6)
def main():
 if sha(PINNED)!=PINNED_SHA:raise RuntimeError('pinned board drift')
 if sha(base.PROFILE/'crow_carrier.kicad_pro')!=out.PROFILE_SHA:raise RuntimeError('profile drift')
 baseline=p.LoadBoard(str(PINNED));old=base.footprint_ledger(baseline)
 with tempfile.TemporaryDirectory(prefix='crow-spoke8-place-') as tmp:
  root=Path(tmp)
  saved=trial.GROUP['C_SPOKE_DVDT8'];trial.GROUP['C_SPOKE_DVDT8']=DVDT_POSE
  try:source,inputs=trial.generate(root/'source')
  finally:trial.GROUP['C_SPOKE_DVDT8']=saved
  b=p.LoadBoard(str(source));trial.prior.add_candidate(b)
  old_adc8n=[q for q in out.inp.tracks(baseline) if q[0]=='ADC8N']
  new_adc8n=[q for q in out.inp.tracks(b) if q[0]=='ADC8N']
  if old_adc8n!=new_adc8n:raise RuntimeError('ADC8N witness copper drift')
  ledger=base.footprint_ledger(b)
  if len(ledger)!=569 or set(ledger)!=set(old):raise RuntimeError('569 footprint denominator drift')
  changed=sorted(r for r in old if old[r]!=ledger[r])
  if changed!=['C_SPOKE_DVDT8']:raise RuntimeError(f'pose/pad change set {changed}')
  if ledger['C_SPOKE_DVDT8']['pose']!=DVDT_POSE:raise RuntimeError('DVDT source pose drift')
  for a,c in zip(old['C_SPOKE_DVDT8']['pads'],ledger['C_SPOKE_DVDT8']['pads']):
   if a[:4]!=c[:4] or abs(a[4]-c[4])>1e-6 or abs(a[5]+.2-c[5])>1e-6:
    raise RuntimeError('DVDT native pad identity/translation drift')
  fixed=yaml.safe_load((trial.PROJECT/'03_src/rules/p1_corridor_requirements.yaml').read_text())['p1_fixed_refs']
  if len(fixed)!=27 or any(old[r]!=ledger[r] for r in fixed):raise RuntimeError('fixed ref drift')
  source_cfg=yaml.safe_load(trial.prior.SOURCE.read_text())
  owner=source_cfg['placement']['regions']['analog_ch8']
  fs={f.GetReference():f for f in b.GetFootprints()}
  boxes={r:trial.prior.full_box(f) for r,f in fs.items()}
  group=set(trial.GROUP)
  pose_hits={r:sorted(q for q,box in boxes.items() if q!=r and trial.prior.box_gap(boxes[r],box)<1e-6) for r in group}
  if any(pose_hits.values()):raise RuntimeError(f'group full-envelope collision {pose_hits}')
  if any(boxes[r][0]<owner[0] or boxes[r][1]<owner[1] or boxes[r][2]>owner[2] or boxes[r][3]>owner[3] for r in group):
   raise RuntimeError('group source owner escape')
  contacts={name:trial.copper_gap(base.pad(b,'U_SPOKE8',upin),base.pad(b,ref,pin))
            for name,(upin,ref,pin,net) in trial.PAIRS.items()}
  old_contacts={name:trial.copper_gap(base.pad(baseline,'U_SPOKE8',upin),base.pad(baseline,ref,pin))
                for name,(upin,ref,pin,net) in trial.PAIRS.items()}
  if contacts['IN_to_CIN']>2.5 or contacts['ILIM_to_RILIM']>2.5:
   raise RuntimeError(f'project IN/ILIM contact ceilings failed {contacts}')
  # Pose screen passed. Recut only local GND and DVDT RTN paths; the other
  # six-member RTN support paths and the ADC8N link remain source-generated.
  added=[]
  for net,verts in [('GND',GND_CIN),('GND',GND_OUT),('SPOKE_RTN8',RTN_ILIM),
                    ('SPOKE_RTN8',RTN_DVDT),('SPOKE_RTN8',RTN_U3),('SPOKE_RTN8',RTN_U5)]:
   added+=path(b,net,verts,.2)
  added += [via(b,'GND',GND_CIN[-1]),via(b,'GND',GND_OUT[1])]
  added+=path(b,'N12V_PROTECTED',[(188.35,46.025),(188.35,44.0)],1.2)
  added+=path(b,'N12V_POD8',OUT,.5)
  added+=path(b,'SPOKE_ILIM8',ILIM[:2],.2)
  added.append(via(b,'SPOKE_ILIM8',ILIM[1]))
  added+=path(b,'SPOKE_ILIM8',ILIM[1:3],.2,p.In2_Cu)
  added.append(via(b,'SPOKE_ILIM8',ILIM[2]))
  added+=path(b,'SPOKE_ILIM8',ILIM[2:],.2)
  copper_boxes=[]
  for q in added:
   z=q.GetBoundingBox();copper_boxes.append([base.mm(v) for v in
    (z.GetLeft(),z.GetTop(),z.GetRight(),z.GetBottom())])
  if any(c[0]<owner[0] or c[1]<owner[1] or c[2]>owner[2] or c[3]>owner[3] for c in copper_boxes):
   raise RuntimeError('new copper outside analog_ch8 source owner')
  # Native effective-shape mouth screen before invoking the costly profile.
  mouth=next(q for q in added if isinstance(q,p.PCB_VIA) and q.GetNetname()=='SPOKE_ILIM8' and abs(base.mm(q.GetPosition().y)-ILIM[1][1])<1e-6)
  shape=mouth.GetEffectiveShape(p.F_Cu)
  mouth_gaps={f'U_SPOKE8.{n}':gap(shape,base.pad(b,'U_SPOKE8',n).GetEffectiveShape(p.F_Cu))
              for n in ('6','8','11')}
  mouth_gaps['GND_return']=min(g for q in added if q.GetNetname()=='GND' and q.IsOnLayer(p.F_Cu)
                                 if (g:=gap(shape,q.GetEffectiveShape(p.F_Cu))) is not None)
  mouth_gaps['POD8_output']=min(g for q in added if q.GetNetname()=='N12V_POD8' and q.IsOnLayer(p.F_Cu)
                                  if (g:=gap(shape,q.GetEffectiveShape(p.F_Cu))) is not None)
  pre={'schema':1,'status':'POSE_AND_MOUTH_SCREEN','source_input_sha256':inputs,
       'pinned_board_sha256':PINNED_SHA,'moved_ref':'C_SPOKE_DVDT8',
       'old_pose_mm':old['C_SPOKE_DVDT8']['pose'],'new_pose_mm':DVDT_POSE,
       'group_full_boxes_mm':{r:boxes[r] for r in group},'group_envelope_collisions':pose_hits,
       'direct_native_pad_copper_gaps_mm':contacts,
       'baseline_direct_native_pad_copper_gaps_mm':old_contacts,
       'project_in_ilim_gap_ceilings_mm':[2.5,2.5],
       'adc8n_copper_preserved':True,
       'fixed_27_preserved':True,'pad_identity_preserved':True,'owner_region_mm':owner,
       'ilim_first_via_mm':ILIM[1],'ilim_first_via_effective_shape_gaps_mm':mouth_gaps}
  (HERE/'pose_screen.json').write_text(json.dumps(pre,indent=2,sort_keys=True)+'\n')
  if min(mouth_gaps['U_SPOKE8.6'],mouth_gaps['U_SPOKE8.8'],mouth_gaps['U_SPOKE8.11'],mouth_gaps['GND_return'])<.15-1e-6 or mouth_gaps['POD8_output']<.2-1e-6:
   raise RuntimeError(f'ILIM first-via mouth failed: {mouth_gaps}')
  unfilled=root/'candidate.kicad_pcb';p.SaveBoard(str(unfilled),b)
  prof=root/'profile';prof.mkdir()
  _,d0,v0,_=base.profile('before',PINNED,prof)
  native,d1,v1,_=base.profile('candidate',unfilled,prof)
  n=p.LoadBoard(str(native));n.BuildConnectivity();conn=n.GetConnectivity()
  if base.footprint_ledger(n)!=ledger:raise RuntimeError('native pad/pose drift')
  def links(ref,pin):return sorted(q.GetParentFootprint().GetReference()+'.'+q.GetNumber()
    for q in conn.GetConnectedItems(base.pad(n,ref,pin)) if isinstance(q,p.PAD))
  connected={'in':'C_SPOKE_IN8.1' in links('U_SPOKE8','1'),
   'out':'C_SPOKE_OUT8.1' in links('U_SPOKE8','10'),
   'ilim':'R_SPOKE_ILIM8.1' in links('U_SPOKE8','7'),
   'cin_gnd':'C_SPOKE_IN8.2' in links('U_SPOKE8','6'),
   'cout_gnd':'C_SPOKE_OUT8.2' in links('U_SPOKE8','6'),
   'ilim_rtn':'R_SPOKE_ILIM8.2' in links('U_SPOKE8','11'),
   'dvdt_rtn':'C_SPOKE_DVDT8.2' in links('U_SPOKE8','11'),
   'u3_ovp_rtn':'U_SPOKE8.3' in links('U_SPOKE8','11'),
   'u5_rtn':'U_SPOKE8.5' in links('U_SPOKE8','11')}
  if not all(connected.values()):raise RuntimeError(f'native local link missing {connected}')
  if set(links('U_SPOKE8','6'))&set(links('U_SPOKE8','11')):raise RuntimeError('GND/RTN bridge')
  zones=[z for z in n.Zones() if z.GetNetname()=='GND' and p.In1_Cu in z.GetLayerSet().Seq()]
  if len(zones)!=1 or not zones[0].IsFilled():raise RuntimeError('In1 GND fill absent')
  fill=zones[0].GetFilledPolysList(p.In1_Cu);common=set(range(fill.OutlineCount()))
  for xy in [*GND_CIN,*GND_OUT]:
   q=base.pt(*xy)
   if not fill.Contains(q):raise RuntimeError(f'GND path not over fill {xy}')
   common&={i for i in range(fill.OutlineCount()) if fill.Outline(i).PointInside(q)}
  if not common:raise RuntimeError('GND returns over disconnected fill outlines')
  stitch_centers=[GND_CIN[-1],GND_OUT[1]]
  native_stitches=[q for q in n.GetTracks() if isinstance(q,p.PCB_VIA) and q.GetNetname()=='GND' and
                   (base.mm(q.GetPosition().x),base.mm(q.GetPosition().y)) in stitch_centers]
  if len(native_stitches)!=2:raise RuntimeError('off-pad GND stitch denominator/identity drift')
  old_issues=set(map(base.issue,d0['violations']));new_issues=set(map(base.issue,d1['violations']))
  output_polygon=[(191.4,46.5)]+OUT+[(195.55,46.7),(195.55,48.5),(192.7,48.5),(191.4,48.5)]
  input_polygon=[(188.6,46.5),(188.35,46.025),(188.35,44.0),(188.8,44.0),
                 (190.7,44.0),GND_CIN[-1],GND_OUT[1],(191.4,48.5)]
  ilim_polygon=ILIM+[(190.175,51.0),(190.175,49.8),(190.0,49.625),(190.0,47.5),(189.0,48.5),(188.6,48.5)]
  result={**pre,'status':'NATIVE_LOCAL_ROUTE_WITNESS' if not(new_issues-old_issues or old_issues-new_issues or v1.get('fails')) else 'REJECT_NATIVE_ROUTE',
   'gnd_return_same_filled_in1_outline_ids':sorted(common),'named_connectivity':connected,
   'gnd_stitch_centers_mm':stitch_centers,'gnd_stitches_contact_one_filled_in1_polygon':True,
   'ordinary_via_centers_mm':{'GND':stitch_centers,'SPOKE_ILIM8':[ILIM[1],ILIM[2]],'N12V_POD8':[]},
   'gnd_rtn_separate':True,'new_copper_boxes_mm':copper_boxes,
   'output_signal_centerline_length_mm':round(sum(math.dist(a,c) for a,c in zip(OUT,OUT[1:])),6),
   'ilim_signal_centerline_length_mm':round(sum(math.dist(a,c) for a,c in zip(ILIM,ILIM[1:])),6),
   'gnd_cin_fcu_length_mm':round(math.dist(*GND_CIN),6),
   'gnd_cout_fcu_length_mm':round(sum(math.dist(a,c) for a,c in zip(GND_OUT,GND_OUT[1:])),6),
   'diagnostic_projected_loop_area_mm2':{'input_with_straight_in1_stitch_chord':area(input_polygon),
      'output':area(output_polygon),'ilim_rtn':area(ilim_polygon)},
   'input_projection_uses_straight_in1_via_to_via_chord_not_measured_return_path':True,
   'native_profile':{'violations':[len(d0['violations']),len(d1['violations'])],
      'unconnected':[len(d0['unconnected_items']),len(d1['unconnected_items'])],
      'added_issue_identities':len(new_issues-old_issues),'removed_issue_identities':len(old_issues-new_issues),
      'added_issue_summaries':sorted((z[0],z[1]) for z in new_issues-old_issues),
      'via_process_fails':[v0.get('fails'),v1.get('fails')]}}
  (HERE/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
  print(json.dumps({'status':result['status'],'mouth':mouth_gaps,'profile':result['native_profile']}))
if __name__=='__main__':main()
