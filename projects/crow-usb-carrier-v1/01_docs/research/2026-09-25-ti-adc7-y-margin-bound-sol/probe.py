#!/usr/bin/env python3
"""Reproduce exact Y_AUDIO y-margin bound on isolated local TI candidate."""
from __future__ import annotations
import hashlib, importlib.util, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path
try:
 import pcbnew as p
except ImportError:
 sys.path.append('/usr/lib/python3/dist-packages'); import pcbnew as p
ROOT=Path(__file__).resolve().parents[5]
PROJECT=ROOT/'projects/crow-usb-carrier-v1'
PACKET=PROJECT/'06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
CANDIDATE=PROJECT/'01_docs/research/2026-09-25-ti-adc7-local-osc-probe-sol/candidate.kicad_pcb'
CHECKER=ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
SHA='c9b758d69867b274f0592bd2eceb9a26d64a80dd2daafa8ab9516d23d5925502'
PORT=[166,83.9,167.12,85]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def mm(v):return v/1e6
def hit(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
def load_helper():
 spec=importlib.util.spec_from_file_location('p1_corridor_capacity',CHECKER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def fps(board):return {f.GetReference():f for f in board.GetFootprints()}
def pad(f,n):return next(q for q in f.Pads() if q.GetNumber()==n)
def physical(fp,h):return tuple(h._physical_envelope(fp))
def dist(a,b):
 x=a.GetPosition();y=b.GetPosition();return math.hypot(mm(x.x-y.x),mm(x.y-y.y))
def drc(board,report):
 run=subprocess.run(['kicad-cli','pcb','drc','--severity-all','--refill-zones','--format','json','--output',str(report),str(board)],text=True,capture_output=True)
 if not report.exists():raise SystemExit(f'no DRC JSON: {run.stderr}')
 data=json.loads(report.read_text());return {'violations':data.get('violations',[]),'unconnected_count':len(data.get('unconnected_items',[])),'exit_code':run.returncode}
def main():
 if sha(CANDIDATE)!=SHA:raise SystemExit('bound candidate board drift')
 h=load_helper();b=p.LoadBoard(str(CANDIDATE));f=fps(b)
 assert tuple(round(mm(v),3) for v in (f['Y_AUDIO'].GetPosition().x,f['Y_AUDIO'].GetPosition().y))==(167.5,87.2)
 assert tuple(round(mm(v),3) for v in (f['C_ADC_I2C_A'].GetPosition().x,f['C_ADC_I2C_A'].GetPosition().y))==(168.0,97.6)
 assert tuple(round(mm(v),3) for v in (f['C_ADC_CLOCK_OK'].GetPosition().x,f['C_ADC_CLOCK_OK'].GetPosition().y))==(164.6,76.2)
 y=f['Y_AUDIO'];base=physical(y,h);other={r:physical(q,h) for r,q in f.items() if r!='Y_AUDIO'};old={r for r,v in other.items() if hit(base,v)}
 clock=pad(f['U_TDM_XLATE'],'11');support=pad(f['C_AUDIO_OSC'],'1')
 positions=[]
 for yi in range(8720,8851):
  yy=yi/100;dy=yy-87.2;box=(base[0],base[1]+dy,base[2],base[3]+dy)
  collisions=sorted(r for r,v in other.items() if r not in old and hit(box,v))
  # Exact translated pad-center distances without changing the loaded candidate.
  p3=pad(y,'3').GetPosition();p4=pad(y,'4').GetPosition();q3=clock.GetPosition();q4=support.GetPosition()
  d3=math.hypot(mm(p3.x-q3.x),mm(p3.y-q3.y)+dy)
  d4=math.hypot(mm(p4.x-q4.x),mm(p4.y-q4.y)+dy)
  positions.append({'y_mm':yy,'portal_margin_mm':round(box[1]-85,6),'colliders':collisions,'clock_distance_mm':round(d3,6),'support_distance_mm':round(d4,6)})
 good=[q for q in positions if not q['colliders'] and q['clock_distance_mm']<=16.565826 and q['support_distance_mm']<=6.875536]
 best=max(good,key=lambda q:q['portal_margin_mm'])
 # At y=87.21 the western bypass blocks an upward north-edge margin.
 first=next(q for q in positions if q['y_mm']>best['y_mm'])
 z=other['C_ADC_I2C_B'];osc=other['C_AUDIO_OSC']
 # For 87.20<y<=88.50 Y intersects these parts in y. Their x projections
 # require Y origin >=168.950 to avoid C_ADC_I2C_B and <=167.950 to avoid
 # C_AUDIO_OSC, an impossible interval for a Y-only sideways adjustment.
 x_bounds={'avoid_C_ADC_I2C_B_min_origin_mm':round(167.5+(z[2]-base[0]),6),
           'avoid_C_AUDIO_OSC_max_origin_mm':round(167.5+(osc[0]-base[2]),6)}
 with tempfile.TemporaryDirectory(prefix='crow-y-bound-') as tmp:
  t=Path(tmp);project=t/'project';native=project/'04_kicad';native.mkdir(parents=True)
  (project/'03_src').symlink_to(PACKET/'03_src',target_is_directory=True)
  for name in ('crow_carrier.kicad_pro','crow_carrier.kicad_dru','fp-lib-table'):shutil.copy2(PACKET/'04_kicad'/name,native/name)
  current=native/'crow_carrier.kicad_pcb';shutil.copy2(CANDIDATE,current)
  before=drc(current,t/'before.json')
  y.SetPosition(p.VECTOR2I(167500000,87210000));variant=t/'variant.kicad_pcb';p.SaveBoard(str(variant),b);shutil.copy2(variant,current)
  after=drc(current,t/'after.json')
  def summary(result):
   return {'violations':len(result['violations']),'types':sorted(v['type'] for v in result['violations']),'unconnected_count':result['unconnected_count']}
  report={'candidate_board_sha256':SHA,'tested_y_range_mm':[87.2,88.5],'step_mm':0.01,
          'fixed_two_cap_origins_mm':{'C_ADC_I2C_A':[168.0,97.6],'C_ADC_CLOCK_OK':[164.6,76.2]},
          'best_y_only':best,'first_failed_step':first,'physical_boxes_mm':{'Y_AUDIO_at_best':base,'C_ADC_I2C_B':z,'C_AUDIO_OSC':osc},
          'sideways_bounds_at_y_above_87_2':x_bounds,
          'Y_pad_vertical_gap_at_best_mm':0.4,
          'native_drc_best':summary(before),'native_drc_first_failed_step':summary(after),
          'drc_warning_count_delta':len(after['violations'])-len(before['violations']),
          'p1_accepted':False}
  print(json.dumps(report,indent=2))
if __name__=='__main__':main()
