#!/usr/bin/env python3
"""Exact source-to-native Q_PRE move, related-pad, collision, and DRC receipt."""
from __future__ import annotations
import hashlib, importlib.util, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages');import pcbnew

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
P=ROOT/'projects/crow-usb-carrier-v1'
EXACT=P/'01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb'
BASE=Path('/tmp/crow-qpre-source-baseline.kicad_pcb')
TRIAL=HERE/'candidate.kicad_pcb'
FLOOR=P/'01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol/floorplan.yaml'
SOURCE=P/'01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol/p1_requirements.yaml'
HELPER=ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
SHA={'exact':'d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7',
     'baseline':'612d319fdafd5b9eaa085f64c7752f94a0953a659f9b883cd5008b6504eeab71',
     'trial':'e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef',
     'floorplan':'7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0'}
RELATED=[('Q_PRE','1','R_PRE_G','1'),('Q_PRE','2','D_HOLD','1'),
         ('Q_PRE','2','R_PRE_G','2'),('Q_PRE','3','R_PRE','2'),
         ('C_IN3','1','C_IN2','1'),('C_IN3','2','C_IN2','2')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xy(item):
    p=item.GetPosition();return pcbnew.ToMM(p.x),pcbnew.ToMM(p.y)
def intersects(a,b):return max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3])
def gap(a,b):return math.hypot(max(b[0]-a[2],a[0]-b[2],0),max(b[1]-a[3],a[1]-b[3],0))
def pad_key(fp,board):
    x,y=xy(fp)
    return sorted((p.GetNumber(),p.GetNetname(),tuple(board.GetLayerName(i) for i in p.GetLayerSet().Seq()),
                   p.GetShape(),p.GetAttribute(),tuple(p.GetSize()),tuple(p.GetDrillSize()),
                   round(xy(p)[0]-x,6),round(xy(p)[1]-y,6)) for p in fp.Pads())
def pd(fps,a,ap,b,bp):
    q=next(p for p in fps[a].Pads() if p.GetNumber()==ap)
    r=next(p for p in fps[b].Pads() if p.GetNumber()==bp)
    if q.GetNetname()!=r.GetNetname():raise SystemExit(f'not same net: {a}.{ap}/{b}.{bp}')
    return round(math.dist(xy(q),xy(r)),6)
def drc(path,output):
    subprocess.run(['kicad-cli','pcb','drc','--format','json','--output',str(output),str(path)],
                   check=True,stdout=subprocess.DEVNULL)
    return json.loads(output.read_text())
def issue_key(v):return(v['type'],v['description'],tuple(sorted(i['uuid'] for i in v['items'])))

def main():
    for name,path in [('exact',EXACT),('baseline',BASE),('trial',TRIAL),('floorplan',FLOOR)]:
        if sha(path)!=SHA[name]:raise SystemExit(f'{name} SHA drift')
    spec=importlib.util.spec_from_file_location('p1helper',HELPER)
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    boards={name:pcbnew.LoadBoard(str(path)) for name,path in
            [('exact',EXACT),('baseline',BASE),('trial',TRIAL)]}
    fps={name:{f.GetReference():f for f in board.GetFootprints()} for name,board in boards.items()}
    if len(fps['exact'])!=569 or any(set(fps[name])!=set(fps['exact']) for name in fps):
        raise SystemExit('569-footprint denominator drift')
    fixed=yaml.safe_load(SOURCE.read_text())['p1_fixed_refs']
    if len(fixed)!=27:raise SystemExit('fixed-set drift')
    identity=all(pad_key(fps['exact'][ref],boards['exact'])==pad_key(fps[name][ref],boards[name])
                 for ref in fps['exact'] for name in ('baseline','trial'))
    pose_diff={name:sorted(ref for ref in fps['exact'] if
                    xy(fps[name][ref])!=xy(fps['exact'][ref]) or
                    fps[name][ref].GetOrientationDegrees()!=fps['exact'][ref].GetOrientationDegrees())
               for name in ('baseline','trial')}
    if not identity or pose_diff['baseline'] or pose_diff['trial']!=['Q_PRE'] or 'Q_PRE' in fixed:
        raise SystemExit('pose/pad parity drift')
    envelopes={name:{ref:h._physical_envelope(fp) for ref,fp in fps[name].items()}
               for name in ('baseline','trial')}
    if any(envelopes['baseline'][ref]!=h._physical_envelope(fps['exact'][ref]) for ref in fps['exact']):
        raise SystemExit('baseline full-envelope mismatch against exact board')
    def full_pairs(name):
        boxes=envelopes[name];refs=sorted(boxes)
        return {tuple((left,right)) for i,left in enumerate(refs) for right in refs[i+1:]
                if intersects(boxes[left],boxes[right])}
    before_pairs=full_pairs('baseline');after_pairs=full_pairs('trial')
    if after_pairs-before_pairs or before_pairs-after_pairs!={('C_IN3','Q_PRE')}:
        raise SystemExit('unexpected full-envelope collision delta')
    def pad_pairs(name):
        q=fps[name]['Q_PRE'];others=[(fp.GetReference(),p) for fp in boards[name].GetFootprints()
                                    if fp.GetReference()!='Q_PRE' for p in fp.Pads()]
        return sorted((f'Q_PRE.{p.GetNumber()}',f'{ref}.{other.GetNumber()}')
                      for p in q.Pads() for ref,other in others
                      if intersects(h.box_mm(p.GetBoundingBox()),h.box_mm(other.GetBoundingBox())))
    old_pad_pairs=pad_pairs('baseline');new_pad_pairs=pad_pairs('trial')
    if set(new_pad_pairs)-set(old_pad_pairs):raise SystemExit('new inter-footprint pad overlap')
    regions=yaml.safe_load(FLOOR.read_text())['placement']['regions']
    qbox=envelopes['trial']['Q_PRE']
    owner=regions['quiet_power']
    q_own=h.contains(owner,qbox)
    q_foreign=sorted(name for name,reg in regions.items() if name!='quiet_power' and intersects(qbox,reg))
    q_near=sorted((round(gap(qbox,box),6),ref) for ref,box in envelopes['trial'].items() if ref!='Q_PRE')[:7]
    related=[{'pads':[f'{a}.{ap}',f'{b}.{bp}'],
              'before_mm':pd(fps['baseline'],a,ap,b,bp),
              'after_mm':pd(fps['trial'],a,ap,b,bp)} for a,ap,b,bp in RELATED]
    with tempfile.TemporaryDirectory(prefix='crow-qpre-drc-') as d:
        t=Path(d);copy=t/'trial.kicad_pcb';shutil.copy2(TRIAL,copy)
        old=drc(BASE,t/'before.json');new=drc(copy,t/'after.json')
    old_issues={issue_key(v) for v in old['violations']}
    new_issues={issue_key(v) for v in new['violations']}
    if old_issues!=new_issues or len(old['unconnected_items'])!=len(new['unconnected_items']):
        raise SystemExit('new or removed native DRC issue')
    result={'schema':1,'kind':'source-controlled-qpre-cin3-courtyard-repair',
            'status':'GEOMETRY_SCREEN_ONLY','p1_accepted':False,'p2_accepted':False,
            'route_credit':False,'return_credit':False,
            'sha256':{'exact':sha(EXACT),'baseline':sha(BASE),'trial':sha(TRIAL),
                      'floorplan':sha(FLOOR),'source':sha(SOURCE),'helper':sha(HELPER)},
            'footprint_count':len(fps['exact']),'fixed_ref_count':len(fixed),
            'pad_net_layer_shape_relative_pose_identical':identity,
            'baseline_pose_diff_from_exact':pose_diff['baseline'],
            'trial_pose_diff_from_exact':pose_diff['trial'],
            'Q_PRE':{'old_origin_mm':xy(fps['baseline']['Q_PRE']),
                     'trial_origin_mm':xy(fps['trial']['Q_PRE']),
                     'old_envelope_mm':envelopes['baseline']['Q_PRE'],
                     'trial_envelope_mm':qbox,'owner_contained':q_own,
                     'foreign_planning_regions':q_foreign,
                     'nearest_envelopes_mm':q_near},
            'removed_full_envelope_pairs':sorted([list(p) for p in before_pairs-after_pairs]),
            'added_full_envelope_pairs':sorted([list(p) for p in after_pairs-before_pairs]),
            'old_Q_PRE_pad_overlap_pairs':old_pad_pairs,
            'trial_Q_PRE_pad_overlap_pairs':new_pad_pairs,
            'related_pad_center_distances':related,
            'native_drc':{'baseline_violations':len(old['violations']),
                          'trial_violations':len(new['violations']),
                          'baseline_unconnected':len(old['unconnected_items']),
                          'trial_unconnected':len(new['unconnected_items']),
                          'violation_identity_sets_equal':old_issues==new_issues},
            'limitation':'0.26 mm is a measured native envelope gap, not assembly or routing proof. '
                         'Planning regions remain overlapping and GND return is unproved.'}
    if not q_own or q_near[0][0]<.25 or q_foreign!=['input_buck']:
        raise SystemExit('Q_PRE owner/gap/foreign shape drift')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
