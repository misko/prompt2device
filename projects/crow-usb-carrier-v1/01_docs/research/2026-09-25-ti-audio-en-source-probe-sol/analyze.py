#!/usr/bin/env python3
"""Measure exact generated AUDIO_EN placement and DRC delta; reject first."""
from __future__ import annotations
import hashlib, importlib.util, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages'); import pcbnew

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
P=ROOT/'projects/crow-usb-carrier-v1'
EXACT=P/'01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb'
BASE=Path('/tmp/crow-audio-source-baseline.kicad_pcb')
TRIAL=HERE/'candidate.kicad_pcb'
FLOOR=HERE/'source_floorplan.yaml'
HELPER=ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
SHA={'exact':'d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7',
     'baseline':'612d319fdafd5b9eaa085f64c7752f94a0953a659f9b883cd5008b6504eeab71',
     'trial':'f1f491c22b20c853fc9d208265237364cbcec3992e4818759281eaa32fc69eac',
     'floorplan':'1c7149d9a104ea954b5df9ac98dd4249329efd24481c36af6cdbf39fb02d09f5'}
MOVED=('R_AUDIO_PD','U_AUDIO','U_ISO1')
PARTNERS=[('U_AUDIO','4','C_AUDIO','1'),('U_AUDIO','5','C_AUDIO_CT1','1'),
          ('U_AUDIO','5','C_AUDIO_CT2','1'),('U_ISO1','8','C_ISO1','1'),
          ('U_ISO1','7','C_FILTER1P1','1'),('U_ISO1','9','C_FILTER1N1','1'),
          ('R_AUDIO_PD','1','R_AUDIO_PU','2')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xy(item):
    p=item.GetPosition();return (pcbnew.ToMM(p.x),pcbnew.ToMM(p.y))
def gap(a,b):return math.hypot(max(b[0]-a[2],a[0]-b[2],0),max(b[1]-a[3],a[1]-b[3],0))
def pad_key(fp,board):
    x,y=xy(fp)
    return sorted((p.GetNumber(),p.GetNetname(),tuple(board.GetLayerName(i) for i in p.GetLayerSet().Seq()),
                   p.GetShape(),p.GetAttribute(),tuple(p.GetSize()),tuple(p.GetDrillSize()),
                   round(xy(p)[0]-x,6),round(xy(p)[1]-y,6)) for p in fp.Pads())
def distance(fps,a,ap,b,bp):
    q=next(p for p in fps[a].Pads() if p.GetNumber()==ap)
    r=next(p for p in fps[b].Pads() if p.GetNumber()==bp)
    if q.GetNetname()!=r.GetNetname():raise SystemExit(f'not same-net: {a}.{ap}/{b}.{bp}')
    return round(math.dist(xy(q),xy(r)),6)
def drc(path,report):
    subprocess.run(['kicad-cli','pcb','drc','--format','json','--output',str(report),str(path)],
                   check=True,stdout=subprocess.DEVNULL)
    return json.loads(report.read_text())
def key(v):return(v['type'],v['description'],tuple(sorted(i['uuid'] for i in v['items'])))

def main():
    for name,path in [('exact',EXACT),('baseline',BASE),('trial',TRIAL),('floorplan',FLOOR)]:
        if sha(path)!=SHA[name]:raise SystemExit(f'{name} SHA drift')
    spec=importlib.util.spec_from_file_location('p1helper',HELPER)
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    boards={name:pcbnew.LoadBoard(str(path)) for name,path in
            [('exact',EXACT),('baseline',BASE),('trial',TRIAL)]}
    fps={name:{f.GetReference():f for f in b.GetFootprints()} for name,b in boards.items()}
    if len(fps['exact'])!=569 or any(set(fps[n])!=set(fps['exact']) for n in fps):
        raise SystemExit('footprint denominator drift')
    fixed=yaml.safe_load((P/'01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol/p1_requirements.yaml').read_text())['p1_fixed_refs']
    if len(fixed)!=27:raise SystemExit('fixed ref count drift')
    pad_equal=all(pad_key(fps['exact'][r],boards['exact'])==pad_key(fps[n][r],boards[n])
                  for r in fps['exact'] for n in ('baseline','trial'))
    pose_diff={n:sorted(r for r in fps['exact'] if xy(fps[n][r])!=xy(fps['exact'][r]) or
                        fps[n][r].GetOrientationDegrees()!=fps['exact'][r].GetOrientationDegrees())
               for n in ('baseline','trial')}
    if (not pad_equal or pose_diff['baseline'] or pose_diff['trial']!=sorted(MOVED) or
            any(r in fixed for r in pose_diff['trial'])):
        raise SystemExit('source-to-board pose/pad parity drift')
    regions=yaml.safe_load(FLOOR.read_text())['placement']['regions']
    boxes={r:h._physical_envelope(f) for r,f in fps['trial'].items()}
    moved=[]
    for r in MOVED:
        fp=fps['trial'][r]; bb=boxes[r];owner='analog_ch1' if r=='U_ISO1' else 'quiet_power'
        pads=[]
        for p in fp.Pads():
            b=h.box_mm(p.GetBoundingBox())
            pads.append({'pad':r+'.'+p.GetNumber(),'net':p.GetNetname(),
                         'owner_contained':h.contains(regions[owner],b),
                         'foreign_regions':sorted(name for name,reg in regions.items()
                                                  if name!=owner and h.intersects(b,reg))})
        moved.append({'ref':r,'from_mm':xy(fps['baseline'][r]),'to_mm':xy(fp),
                      'physical_bbox_mm':bb,'owner':owner,
                      'owner_contained':h.contains(regions[owner],bb),
                      'foreign_regions':sorted(name for name,reg in regions.items()
                                               if name!=owner and h.intersects(bb,reg)),
                      'nearest_envelopes_mm':sorted((round(gap(bb,v),6),name)
                                                    for name,v in boxes.items() if name!=r)[:5],
                      'pads':pads})
    related=[{'pads':[f'{a}.{ap}',f'{b}.{bp}'],
              'before_mm':distance(fps['baseline'],a,ap,b,bp),
              'after_mm':distance(fps['trial'],a,ap,b,bp)} for a,ap,b,bp in PARTNERS]
    with tempfile.TemporaryDirectory(prefix='crow-audio-drc-') as d:
        t=Path(d); trialcopy=t/'trial.kicad_pcb';shutil.copy2(TRIAL,trialcopy)
        before=drc(BASE,t/'before.json');after=drc(trialcopy,t/'after.json')
    old={key(v):v for v in before['violations']};new={key(v):v for v in after['violations']}
    def changed(rows,d):
        return [{'type':k[0],'severity':d[k]['severity'],
                 'description':k[1], 'items':[x['description'] for x in d[k]['items']]}
                for k in sorted(rows)]
    added=changed(new.keys()-old.keys(),new);removed=changed(old.keys()-new.keys(),old)
    result={'schema':1,'kind':'isolated-source-audio-en-owner-trial','status':'REJECTED_LOCALITY_DRC_FOREIGN',
            'p1_accepted':False,'p2_accepted':False,'route_credit':False,'return_credit':False,
            'sha256':{'exact':sha(EXACT),'baseline':sha(BASE),'trial':sha(TRIAL),
                      'floorplan':sha(FLOOR),'helper':sha(HELPER)},
            'source_to_pad_identity_equal':pad_equal,'fixed_ref_count':len(fixed),
            'baseline_pose_diff_from_exact':pose_diff['baseline'],
            'trial_pose_diff_from_exact':pose_diff['trial'],'moved':moved,
            'related_pad_center_distances':related,
            'native_drc':{'baseline_violations':len(before['violations']),
                          'trial_violations':len(after['violations']),
                          'baseline_unconnected':len(before['unconnected_items']),
                          'trial_unconnected':len(after['unconnected_items']),
                          'added':added,'removed':removed},
            'gnd_reference':[{'net':z.GetNetname(),'filled':z.IsFilled()} for z in boards['trial'].Zones()
                             if z.GetNetname()=='GND']}
    if (len([v for v in added if v['severity']=='error'])!=2 or
            not any(x['foreign_regions'] for x in moved) or
            not all(any(p['net']=='AUDIO_EN' and p['owner_contained'] for p in x['pads']) for x in moved)):
        raise SystemExit('expected rejection/owner-branch shape drift')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
