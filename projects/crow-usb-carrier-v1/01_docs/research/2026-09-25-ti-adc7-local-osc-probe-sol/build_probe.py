#!/usr/bin/env python3
"""Isolated, local channel-7 physical-port placement probe on exact TI board."""
from __future__ import annotations
import hashlib, importlib.util, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
try:
 import pcbnew as p
except ImportError:
 sys.path.append('/usr/lib/python3/dist-packages'); import pcbnew as p
ROOT=Path(__file__).resolve().parents[5]
PROJECT=ROOT/'projects/crow-usb-carrier-v1'
HERE=Path(__file__).resolve().parent
PACKET=PROJECT/'06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
BOARD=PACKET/'04_kicad/crow_carrier.kicad_pcb'
RULES=PACKET/'03_src/rules/p1_corridor_requirements.yaml'
CHECKER=ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
BOARD_SHA='8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10'
REGION=[145,72,190,99.84]
PORTS={'adc7':[166,83.9,167.12,85],'adc8':[190.5,83.9,191.62,85],'tdm_neck':[188,94,190,99.84]}
RELATED=[('Y_AUDIO','3','U_TDM_XLATE','11'),('Y_AUDIO','4','C_AUDIO_OSC','1'),('C_ADC_I2C_A','1','U_ADC_I2C_XLATE','3'),('C_ADC_CLOCK_OK','1','U_ADC_CLOCK_OK','5')]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def mm(v):return v/1e6
def box(z):return tuple(mm(v) for v in (z.GetLeft(),z.GetTop(),z.GetRight(),z.GetBottom()))
def hit(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def contains(a,b):return a[0]<=b[0] and a[1]<=b[1] and b[2]<=a[2] and b[3]<=a[3]
def fps(board):return {f.GetReference():f for f in board.GetFootprints()}
def pad_sig(board):return sorted((f.GetReference(),q.GetNumber(),q.GetNetname(),tuple(board.GetLayerName(l) for l in q.GetLayerSet().Seq())) for f in board.GetFootprints() for q in f.Pads())
def pose(f):return (f.GetPosition().x,f.GetPosition().y,round(f.GetOrientationDegrees(),6))
def pad(f,n):return next(q for q in f.Pads() if q.GetNumber()==n)
def proximity(board):
 ff=fps(board); result={}
 for a,ap,b,bp in RELATED:
  x=pad(ff[a],ap).GetPosition();y=pad(ff[b],bp).GetPosition()
  result[f'{a}.{ap}->{b}.{bp}']=round(math.hypot(mm(x.x-y.x),mm(x.y-y.y)),6)
 return result
def physical(fp,helper):return tuple(helper._physical_envelope(fp))
def physical_pairs(board,helper):
 ff=fps(board);names=sorted(ff);bb={r:physical(ff[r],helper) for r in names}
 return {a+'|'+b for i,a in enumerate(names) for b in names[i+1:] if hit(bb[a],bb[b])}
def portal_rows(board,helper):
 ff=fps(board);rows={}
 for name,area in PORTS.items():
  rows[name]={'physical':sorted(r for r,f in ff.items() if hit(area,physical(f,helper)) or any(hit(area,box(q.GetBoundingBox())) for q in f.Pads())),
              'full_text_inclusive':sorted(r for r,f in ff.items() if hit(area,box(f.GetBoundingBox(True,True))))}
 return rows
def drc(board_path,output):
 cmd=['kicad-cli','pcb','drc','--severity-all','--refill-zones','--format','json','--output',str(output),str(board_path)]
 run=subprocess.run(cmd,text=True,capture_output=True)
 if not output.exists():raise SystemExit(f'DRC JSON absent: {run.returncode} {run.stderr}')
 data=json.loads(output.read_text())
 return {'exit_code':run.returncode,'violation_count':len(data.get('violations',[])),'unconnected_count':len(data.get('unconnected_items',[])),'types':sorted(v.get('type','') for v in data.get('violations',[]))}
def main():
 if sha(BOARD)!=BOARD_SHA:raise SystemExit('exact TI board drift')
 spec=importlib.util.spec_from_file_location('corridor',CHECKER);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 base=p.LoadBoard(str(BOARD));old=fps(base);fixed=yaml.safe_load(RULES.read_text())['p1_fixed_refs']
 if len(fixed)!=27:raise SystemExit('fixed-reference count drift')
 fixed_poses={r:pose(old[r]) for r in fixed};signatures=pad_sig(base);before=proximity(base);old_pairs=physical_pairs(base,helper)
 old['Y_AUDIO'].SetPosition(p.VECTOR2I(167500000,87200000))
 old['C_ADC_I2C_A'].SetPosition(p.VECTOR2I(168000000,97600000))
 old['C_ADC_CLOCK_OK'].SetPosition(p.VECTOR2I(164600000,76200000))
 with tempfile.TemporaryDirectory(prefix='crow-adc7-local-') as tmp:
  t=Path(tmp);project=t/'project';native=project/'04_kicad';native.mkdir(parents=True)
  (project/'03_src').symlink_to(PACKET/'03_src',target_is_directory=True)
  for fn in ('crow_carrier.kicad_pro','crow_carrier.kicad_dru','fp-lib-table'):shutil.copy2(PACKET/'04_kicad'/fn,native/fn)
  candidate=HERE/'candidate.kicad_pcb';p.SaveBoard(str(candidate),base)
  copy_path=native/'crow_carrier.kicad_pcb';shutil.copy2(candidate,copy_path)
  board=p.LoadBoard(str(copy_path));new=fps(board);new_pairs=physical_pairs(board,helper)
  if any(pose(new[r])!=fixed_poses[r] for r in fixed):raise SystemExit('fixed pose drift')
  if pad_sig(board)!=signatures:raise SystemExit('pad/net/layer drift')
  if new_pairs-old_pairs:raise SystemExit('new physical collision')
  if not all(contains(REGION,physical(new[r],helper)) and all(contains(REGION,box(q.GetBoundingBox())) for q in new[r].Pads()) for r in ('Y_AUDIO','C_ADC_I2C_A','C_ADC_CLOCK_OK')):raise SystemExit('audio physical-cell containment drift')
  portals=portal_rows(board,helper)
  if portals['adc7']['physical'] or portals['adc8']['physical']:raise SystemExit('ADC physical portal blocked')
  a=drc(BOARD,t/'base.json');b=drc(copy_path,t/'copy.json')
  warnings=json.loads((t/'copy.json').read_text()).get('violations',[])
  if a['unconnected_count']!=b['unconnected_count'] or any(v.get('type') not in ('silk_overlap','silk_over_copper') for v in warnings):raise SystemExit('non-silk DRC delta or unconnected count drift')
  after=proximity(board)
  if any(after[k]>before[k]+1e-6 for k in before):raise SystemExit('related-pad proximity worsened')
  report={'source_board_sha256':BOARD_SHA,'candidate_board_sha256':sha(candidate),'outline_unchanged_mm':[20,20,240,140],'moved_origin_mm':{'Y_AUDIO':[167.5,87.2],'C_ADC_I2C_A':[168.0,97.6],'C_ADC_CLOCK_OK':[164.6,76.2]},'fixed_count':len(fixed),'fixed_poses_identical':True,'pad_net_layer_identity_identical':True,'new_physical_overlap_pairs':[],'baseline_physical_overlap_pairs':len(old_pairs),'candidate_physical_overlap_pairs':len(new_pairs),'audio_region_mm':REGION,'physical_and_pad_containment':True,'portal_obstacles':portals,'Y_AUDIO_physical_bbox_mm':physical(new['Y_AUDIO'],helper),'Y_AUDIO_full_bbox_mm':box(new['Y_AUDIO'].GetBoundingBox(True,True)),'related_pad_center_distances_mm':{'baseline':before,'candidate':after},'native_drc':{'baseline':a,'candidate':b,'delta_pass':False,'new_silk_warning_inventory':warnings},'p1_accepted':False}
  print(json.dumps(report,indent=2))
if __name__=='__main__':main()
