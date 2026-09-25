#!/usr/bin/env python3
"""Isolated native four-part ADC7 margin-placement screen."""
from __future__ import annotations
import hashlib, importlib.util, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
try:
 import pcbnew as p
except ImportError:
 sys.path.append('/usr/lib/python3/dist-packages');import pcbnew as p
ROOT=Path(__file__).resolve().parents[5]
PROJECT=ROOT/'projects/crow-usb-carrier-v1'
PACKET=PROJECT/'06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
HERE=Path(__file__).resolve().parent
SOURCE=PROJECT/'01_docs/research/2026-09-25-ti-adc7-local-osc-probe-sol/candidate.kicad_pcb'
SOURCE_SHA='c9b758d69867b274f0592bd2eceb9a26d64a80dd2daafa8ab9516d23d5925502'
CHECKER=ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
PORTS={'adc7':[166,83.9,167.12,85],'adc8':[190.5,83.9,191.62,85],'tdm_neck':[188,94,190,99.84]}
REGION=[145,72,190,99.84]
RELATED=[('Y_AUDIO','3','U_TDM_XLATE','11'),('Y_AUDIO','4','C_AUDIO_OSC','1'),('C_ADC_I2C_A','1','U_ADC_I2C_XLATE','3'),('C_ADC_I2C_B','1','U_ADC_I2C_XLATE','7'),('C_ADC_CLOCK_OK','1','U_ADC_CLOCK_OK','5')]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def mm(v):return v/1e6
def box(z):return tuple(mm(v) for v in (z.GetLeft(),z.GetTop(),z.GetRight(),z.GetBottom()))
def hit(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def contains(a,b):return a[0]<=b[0] and a[1]<=b[1] and b[2]<=a[2] and b[3]<=a[3]
def fps(b):return {f.GetReference():f for f in b.GetFootprints()}
def pose(f):return (f.GetPosition().x,f.GetPosition().y,round(f.GetOrientationDegrees(),6))
def padsig(b):return sorted((f.GetReference(),q.GetNumber(),q.GetNetname(),tuple(b.GetLayerName(l) for l in q.GetLayerSet().Seq())) for f in b.GetFootprints() for q in f.Pads())
def pad(f,n):return next(q for q in f.Pads() if q.GetNumber()==n)
def prox(b):
 ff=fps(b);o={}
 for a,ap,z,zp in RELATED:
  x=pad(ff[a],ap).GetPosition();y=pad(ff[z],zp).GetPosition();o[f'{a}.{ap}->{z}.{zp}']=round(math.hypot(mm(x.x-y.x),mm(x.y-y.y)),6)
 return o
def physical(f,h):return tuple(h._physical_envelope(f))
def pairs(b,h):
 ff=fps(b);names=sorted(ff);z={r:physical(ff[r],h) for r in names}
 return {a+'|'+c for i,a in enumerate(names) for c in names[i+1:] if hit(z[a],z[c])}
def physical_and_pad_pairs(b,h):
 ff=fps(b);names=sorted(ff)
 shapes={r:[physical(ff[r],h)]+[box(q.GetBoundingBox()) for q in ff[r].Pads()] for r in names}
 return {a+'|'+c for i,a in enumerate(names) for c in names[i+1:]
         if any(hit(x,y) for x in shapes[a] for y in shapes[c])}
def portals(b,h):
 ff=fps(b);return {name:{'physical':sorted(r for r,f in ff.items() if hit(area,physical(f,h)) or any(hit(area,box(q.GetBoundingBox())) for q in f.Pads())),
                        'full_text_inclusive':sorted(r for r,f in ff.items() if hit(area,box(f.GetBoundingBox(True,True))))} for name,area in PORTS.items()}
def drc(board,report):
 run=subprocess.run(['kicad-cli','pcb','drc','--severity-all','--refill-zones','--format','json','--output',str(report),str(board)],text=True,capture_output=True)
 if not report.exists():raise SystemExit(f'DRC JSON absent: {run.stderr}')
 d=json.loads(report.read_text());return {'exit_code':run.returncode,'violations':d.get('violations',[]),'unconnected_items':len(d.get('unconnected_items',[]))}
def main():
 if sha(SOURCE)!=SOURCE_SHA:raise SystemExit('exact local candidate drift')
 spec=importlib.util.spec_from_file_location('p1_corridor_capacity',CHECKER);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
 b=p.LoadBoard(str(SOURCE));old=fps(b);fixed=yaml.safe_load((PACKET/'03_src/rules/p1_corridor_requirements.yaml').read_text())['p1_fixed_refs']
 assert len(fixed)==27
 fixed_poses={r:pose(old[r]) for r in fixed};signature=padsig(b);old_pairs=pairs(b,h);old_shape_pairs=physical_and_pad_pairs(b,h);before=prox(b)
 old['Y_AUDIO'].SetPosition(p.VECTOR2I(167500000,87350000))
 old['C_ADC_I2C_B'].SetPosition(p.VECTOR2I(172800000,95000000))
 with tempfile.TemporaryDirectory(prefix='crow-adc7-four-') as tmp:
  t=Path(tmp);project=t/'project';native=project/'04_kicad';native.mkdir(parents=True)
  (project/'03_src').symlink_to(PACKET/'03_src',target_is_directory=True)
  for n in ('crow_carrier.kicad_pro','crow_carrier.kicad_dru','fp-lib-table'):shutil.copy2(PACKET/'04_kicad'/n,native/n)
  target=native/'crow_carrier.kicad_pcb';shutil.copy2(SOURCE,target);db=drc(target,t/'before.json')
  variant=t/'variant.kicad_pcb';p.SaveBoard(str(variant),b);shutil.copy2(variant,target)
  copy=p.LoadBoard(str(target));new=fps(copy);new_pairs=pairs(copy,h);new_shape_pairs=physical_and_pad_pairs(copy,h);da=drc(target,t/'after.json')
  if any(pose(new[r])!=fixed_poses[r] for r in fixed) or padsig(copy)!=signature:raise SystemExit('fixed or pad identity drift')
  if new_pairs-old_pairs:raise SystemExit(f'new physical pairs: {sorted(new_pairs-old_pairs)}')
  if new_shape_pairs-old_shape_pairs:raise SystemExit(f'new physical/pad pairs: {sorted(new_shape_pairs-old_shape_pairs)}')
  if any(not (contains(REGION,physical(new[r],h)) and all(contains(REGION,box(q.GetBoundingBox())) for q in new[r].Pads())) for r in ('Y_AUDIO','C_ADC_I2C_A','C_ADC_I2C_B','C_ADC_CLOCK_OK')):raise SystemExit('audio region containment')
  pp=portals(copy,h)
  if pp['adc7']['physical'] or pp['adc8']['physical']:raise SystemExit('ADC physical portal blocked')
  after=prox(copy)
  if any(after[k]>before[k]+1e-6 for k in before):raise SystemExit('related pad distance increased')
  if da['unconnected_items']!=db['unconnected_items']:raise SystemExit('unconnected denominator drift')
  if any(v.get('type') not in ('silk_overlap','silk_over_copper') for v in da['violations']):raise SystemExit('non-silk DRC finding')
  candidate=HERE/'candidate.kicad_pcb';shutil.copy2(target,candidate)
  def summary(d):return {'violation_count':len(d['violations']),'types':sorted(v['type'] for v in d['violations']),'unconnected_items':d['unconnected_items']}
  def warning_key(v):return (v['type'],tuple(sorted(item.get('uuid','') for item in v['items'])))
  previous={warning_key(v) for v in db['violations']}
  added=[v for v in da['violations'] if warning_key(v) not in previous]
  report={'source_candidate_sha256':SOURCE_SHA,'four_part_candidate_sha256':sha(candidate),'outline_mm':[20,20,240,140],
          'moved_poses_mm':{'Y_AUDIO':[167.5,87.35],'C_ADC_I2C_B':[172.8,95.0]},
          'held_cap_poses_mm':{'C_ADC_I2C_A':[168.0,97.6],'C_ADC_CLOCK_OK':[164.6,76.2]},
          'fixed_count':len(fixed),'fixed_poses_identical':True,'pad_net_layer_identity_identical':True,
          'new_physical_overlap_pairs':[],'new_physical_or_pad_overlap_pairs':[],
          'baseline_physical_overlap_pairs':len(old_pairs),'candidate_physical_overlap_pairs':len(new_pairs),
          'baseline_physical_or_pad_overlap_pairs':len(old_shape_pairs),'candidate_physical_or_pad_overlap_pairs':len(new_shape_pairs),
          'physical_and_pad_audio_cell_containment':True,'port_obstacles':pp,
          'Y_AUDIO_physical_bbox_mm':physical(new['Y_AUDIO'],h),'C_ADC_I2C_B_physical_bbox_mm':physical(new['C_ADC_I2C_B'],h),
          'adc7_portal_to_Y_courtyard_margin_mm':round(physical(new['Y_AUDIO'],h)[1]-85,6),
          'related_pad_center_distances_mm':{'baseline':before,'candidate':after},
          'native_drc':{'baseline':summary(db),'candidate':summary(da),'silk_warning_delta':len(da['violations'])-len(db['violations']),
                        'new_warning_inventory':added},'p1_accepted':False}
  print(json.dumps(report,indent=2))
if __name__=='__main__':main()
