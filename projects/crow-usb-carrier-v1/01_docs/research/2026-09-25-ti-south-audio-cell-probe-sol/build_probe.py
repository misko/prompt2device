#!/usr/bin/env python3
"""Isolated native test of Terra's 16-mm southern audio receiving cell."""
from __future__ import annotations
import hashlib, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
try:
 import pcbnew as p
except ImportError:
 sys.path.append('/usr/lib/python3/dist-packages'); import pcbnew as p
ROOT=Path(__file__).resolve().parents[5]
PROJECT=ROOT/'projects/crow-usb-carrier-v1'
PACKET=PROJECT/'06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
BOARD=PACKET/'04_kicad/crow_carrier.kicad_pcb'
RULES=PACKET/'03_src/rules/p1_corridor_requirements.yaml'
EXPECTED='8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10'
CELL=[145,140,190,156]
ORIGINS={'Y_AUDIO':(156.481,143.361),'C_ADC_I2C_A':(170.435,140.485),'C_ADC_CLOCK_OK':(172.461,153.789)}
RELATED=[('Y_AUDIO','3','U_TDM_XLATE','11'),('Y_AUDIO','4','C_AUDIO_OSC','1'),('C_ADC_I2C_A','1','U_ADC_I2C_XLATE','3'),('C_ADC_CLOCK_OK','1','U_ADC_CLOCK_OK','5')]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def mm(v):return v/1e6
def bbox(fp):
 z=fp.GetBoundingBox(True,True);return [mm(v) for v in (z.GetLeft(),z.GetTop(),z.GetRight(),z.GetBottom())]
def hit(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def footprints(board):return {x.GetReference():x for x in board.GetFootprints()}
def pairs(board):
 fps=footprints(board); keys=sorted(fps); boxes={k:bbox(fps[k]) for k in keys}
 return {a+'|'+bb for i,a in enumerate(keys) for bb in keys[i+1:] if hit(boxes[a],boxes[bb])}
def pad_sig(board):
 return sorted((f.GetReference(),q.GetNumber(),q.GetNetname(),tuple(board.GetLayerName(l) for l in q.GetLayerSet().Seq())) for f in board.GetFootprints() for q in f.Pads())
def pose(f):return [f.GetPosition().x,f.GetPosition().y,round(f.GetOrientationDegrees(),6)]
def pad(f,n):return next(q for q in f.Pads() if q.GetNumber()==n)
def proximity(board):
 fps=footprints(board); result={}
 for a,ap,b,bp in RELATED:
  x=pad(fps[a],ap).GetPosition(); y=pad(fps[b],bp).GetPosition()
  result[f'{a}.{ap}->{b}.{bp}']=round(math.hypot(mm(x.x-y.x),mm(x.y-y.y)),6)
 return result
def drc(board_path,output):
 command=['kicad-cli','pcb','drc','--severity-all','--refill-zones','--format','json','--output',str(output),str(board_path)]
 run=subprocess.run(command,text=True,capture_output=True)
 if not output.exists():raise SystemExit(f'DRC did not emit JSON: {run.returncode} {run.stderr}')
 data=json.loads(output.read_text())
 return {'exit_code':run.returncode,'violations':len(data.get('violations',[])),'unconnected_items':len(data.get('unconnected_items',[])), 'types':sorted([v.get('type','') for v in data.get('violations',[])])}
def main():
 if sha(BOARD)!=EXPECTED:raise SystemExit('exact TI board drift')
 base=p.LoadBoard(str(BOARD)); old=footprints(base)
 fixed=yaml.safe_load(RULES.read_text())['p1_fixed_refs']
 if len(fixed)!=27:raise SystemExit('fixed set drift')
 old_fixed={r:pose(old[r]) for r in fixed}; old_pad=pad_sig(base); old_pairs=pairs(base); before=proximity(base)
 edge=[]
 for s in base.GetDrawings():
  if s.GetLayer()==p.Edge_Cuts:
   edge.append(s)
   start=s.GetStart();end=s.GetEnd()
   if start.y==140000000:s.SetStart(p.VECTOR2I(start.x,156000000))
   if end.y==140000000:s.SetEnd(p.VECTOR2I(end.x,156000000))
 if len(edge)!=4:raise SystemExit('outline primitive count drift')
 for r,(x,y) in ORIGINS.items():old[r].SetPosition(p.VECTOR2I(round(x*1e6),round(y*1e6)))
 with tempfile.TemporaryDirectory(prefix='crow-south-cell-') as tmp:
  t=Path(tmp); project=t/'project'; native=project/'04_kicad';native.mkdir(parents=True)
  (project/'03_src').symlink_to(PACKET/'03_src',target_is_directory=True)
  for fn in ('crow_carrier.kicad_pro','crow_carrier.kicad_dru','fp-lib-table'):
   shutil.copy2(PACKET/'04_kicad'/fn,native/fn)
  variant=native/'crow_carrier.kicad_pcb';p.SaveBoard(str(variant),base)
  copy=p.LoadBoard(str(variant)); new=footprints(copy); new_pairs=pairs(copy)
  if any(pose(new[r])!=old_fixed[r] for r in fixed):raise SystemExit('fixed ref moved')
  if pad_sig(copy)!=old_pad:raise SystemExit('pad/net/layer identity changed')
  if new_pairs-old_pairs:raise SystemExit('new native full-bbox collision')
  boxes={r:bbox(new[r]) for r in ORIGINS}
  if any(not (CELL[0]<=v[0] and CELL[1]<=v[1] and v[2]<=CELL[2] and v[3]<=CELL[3]) for v in boxes.values()):raise SystemExit('receiving-cell containment failed')
  portal={'adc7':[166,83.9,167.12,85],'adc8':[190.5,83.9,191.62,85],'tdm_neck':[188,94,190,99.84]}
  obstacles={k:sorted(r for r,f in new.items() if hit(bbox(f),v)) for k,v in portal.items()}
  a=drc(BOARD,t/'base-drc.json');z=drc(variant,t/'copy-drc.json')
  report={'source_board_sha256':EXPECTED,'candidate_board_sha256':sha(variant),'outline_mm':[20,20,240,156],'size_mm':[220,136],'fixed_count':len(fixed),'fixed_poses_identical':True,'pad_net_layer_identity_identical':True,'new_full_bbox_overlap_pairs':[],'baseline_overlap_pairs':len(old_pairs),'candidate_overlap_pairs':len(new_pairs),'receiving_cell_mm':CELL,'moved_full_bboxes_mm':boxes,'port_obstacles':obstacles,'related_pad_center_distances_mm':{'baseline':before,'candidate':proximity(copy)},'native_drc':{'baseline':a,'candidate':z}}
  if a['violations']!=z['violations'] or a['unconnected_items']!=z['unconnected_items'] or a['types']!=z['types']:report['native_drc']['delta_pass']=False
  else:report['native_drc']['delta_pass']=True
  print(json.dumps(report,indent=2))
if __name__=='__main__':main()
