#!/usr/bin/env python3
"""Fail-closed native receipt for the isolated TI placement union."""
from __future__ import annotations
import hashlib, importlib.util, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
try:
    import pcbnew as p
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages'); import pcbnew as p

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
P=ROOT/'projects/crow-usb-carrier-v1'
TI=P/'06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/crow_carrier.kicad_pcb'
BASE=HERE/'baseline.kicad_pcb'
TRIAL=HERE/'candidate.kicad_pcb'
POSES=HERE/'expected_poses.json'
SOURCE=P/'03_src/rules/p1_corridor_requirements.yaml'
RESEARCH=P/'01_docs/research'
TERRA=RESEARCH/'2026-09-25-ti-global-owner-census-terra/census.py'
SCREEN=RESEARCH/'2026-09-25-ti-timing-mouth-screen-sol/build_screen.py'
EXPECTED={'ti':'8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10',
          'base':'3c3893e65100d51078e5f915e473585e4f38e3d6d34ef607992dcf6f2fc54cc8',
          'trial':'20373950748ac51113b115b2d12d169160c24024a2a000572bb70c67b0f60919'}
RELATED=[('Y_AUDIO','3','U_TDM_XLATE','11'),('Y_AUDIO','4','C_AUDIO_OSC','1'),
         ('C_ADC_I2C_A','1','U_ADC_I2C_XLATE','3'),('C_ADC_I2C_B','1','U_ADC_I2C_XLATE','7'),
         ('C_ADC_CLOCK_OK','1','U_ADC_CLOCK_OK','5'),
         ('C_ADC_AC8N1','1','U_ISO8','6'),('C_ADC_AC8N1','2','C_ADC_CM8N','1'),
         ('C_A8P','2','R_B8P','1'),('C_FILTER8N1','1','U_ISO8','9'),
         ('C_FILTER8P2','1','U_ISO8','7'),('C_FILTER8N2','1','R_X8N','2'),
         ('C_SPOKE_IN8','1','U_SPOKE8','1')]
RELATED += [(f'R_B{i}P','1',f'C_A{i}P','2') for i in range(1,8)]
MOUTHS={'translator_west_four':([172.5,94.2,174.305,96.8],'horizontal',4),
        'xu_west_data':([197.5,97.1,199.805,98.5],'horizontal',1),
        'xu_south_three':([209.5,108.5,212.5,109.7],'vertical',3)}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def pose(fp):
    z=fp.GetPosition(); return [p.ToMM(z.x),p.ToMM(z.y),fp.GetOrientationDegrees()]
def xy(item):
    z=item.GetPosition();return p.ToMM(z.x),p.ToMM(z.y)
def pad(fp,num):return next(q for q in fp.Pads() if q.GetNumber()==num)
def sig(board,fp):
    x,y=xy(fp)
    angle=math.radians(fp.GetOrientationDegrees())
    co,si=math.cos(angle),math.sin(angle)
    def local(q):
        dx,dy=xy(q)[0]-x,xy(q)[1]-y
        return round(dx*co-dy*si,6),round(dx*si+dy*co,6)
    return sorted((q.GetNumber(),q.GetNetname(),tuple(board.GetLayerName(i) for i in q.GetLayerSet().Seq()),
                   q.GetShape(),q.GetAttribute(),tuple(q.GetSize()),tuple(q.GetDrillSize()),
                   *local(q)) for q in fp.Pads())
def distance(fps,a,an,b,bn):return round(math.dist(xy(pad(fps[a],an)),xy(pad(fps[b],bn))),6)
def drc(path,out):
    run=subprocess.run(['kicad-cli','pcb','drc','--format','json','--output',str(out),str(path)],capture_output=True,text=True)
    if not out.exists():raise SystemExit(f'DRC JSON absent: {run.stderr}')
    return json.loads(out.read_text())
def issues(report):
    return {(v['type'],v['description'],tuple(sorted(i['uuid'] for i in v['items']))) for v in report['violations']}
def census(path,output):
    output.mkdir()
    spec=importlib.util.spec_from_file_location('full_census',TERRA)
    c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    c.BOARD=path;c.EXPECTED_BOARD_SHA256=sha(path);c.HERE=output;c.main()
    return json.loads((output/'receipt.json').read_text())

def main():
    for key,path in [('ti',TI),('base',BASE),('trial',TRIAL)]:
        if sha(path)!=EXPECTED[key]:raise SystemExit(f'{key} board SHA drift')
    expected=json.loads(POSES.read_text())
    if expected['candidate_sha256']!=EXPECTED['trial'] or len(expected['move_union'])!=45:
        raise SystemExit('expected pose union drift')
    boards={name:p.LoadBoard(str(path)) for name,path in [('ti',TI),('base',BASE),('trial',TRIAL)]}
    fps={name:{f.GetReference():f for f in board.GetFootprints()} for name,board in boards.items()}
    refs=set(fps['ti'])
    if len(refs)!=569 or any(set(fps[name])!=refs for name in fps):raise SystemExit('569-ref denominator drift')
    fixed=yaml.safe_load(SOURCE.read_text())['p1_fixed_refs']
    if len(fixed)!=27 or any(pose(fps[name][ref])!=pose(fps['ti'][ref]) for ref in fixed for name in ('base','trial')):
        raise SystemExit('fixed pose drift')
    if any(sig(boards['ti'],fps['ti'][ref])!=sig(boards[name],fps[name][ref])
           for ref in refs for name in ('base','trial')):raise SystemExit('pad number/net/layer/shape/relative position drift')
    base_changed={ref for ref in refs if pose(fps['base'][ref])!=pose(fps['ti'][ref])}
    trial_changed={ref for ref in refs if pose(fps['trial'][ref])!=pose(fps['ti'][ref])}
    if base_changed!={'Q_PRE'} or trial_changed!=set(expected['move_union'])|{'Q_PRE'}:
        raise SystemExit(f'pose union drift: {len(trial_changed)} refs')
    if any(pose(fps['trial'][ref])!=list(target) for ref,target in expected['move_union'].items()):
        raise SystemExit('research target pose drift')
    if pose(fps['trial']['Q_PRE'])!=[46.0,107.15,0.0]:raise SystemExit('Q_PRE target drift')
    sys.path.insert(0,str(SCREEN.parent));import build_screen as screen
    obs=[]
    for ref,fp in fps['trial'].items():
        c=fp.GetCourtyard(p.F_CrtYd)
        obs.append((ref+':native',screen.bbox(c.BBox() if c.OutlineCount() else fp.GetBoundingBox(False,False))))
        for q in fp.Pads():
            if q.IsOnLayer(p.F_Cu):obs.append((ref+':pad'+q.GetNumber(),screen.bbox(q.GetBoundingBox())))
    portal=[166,83.9,167.12,85]
    portal_hits=[name for name,box in obs if screen.intersects(portal,box)]
    if portal_hits:raise SystemExit(f'ADC7 portal physical hit: {portal_hits}')
    mouths={name:{'bbox_mm':box,'demand_slots':demand,**screen.mouth_screen(box,axis,obs)}
            for name,(box,axis,demand) in MOUTHS.items()}
    if any(v['raw_slots']<v['demand_slots'] for v in mouths.values()):raise SystemExit('timing mouth deficit')
    related=[{'pads':[f'{a}.{an}',f'{b}.{bn}'],'ti_mm':distance(fps['ti'],a,an,b,bn),
              'trial_mm':distance(fps['trial'],a,an,b,bn)} for a,an,b,bn in RELATED]
    timing=json.loads((RESEARCH/'2026-09-25-ti-timing-coupled-placement-sol/result.json').read_text())
    bypass=[]
    for ref in timing['moves']:
        if ref.startswith(('C_XU_VDD_','C_XU_VDDIO_')):
            pin=ref.rsplit('_',1)[-1]
            before=distance(fps['ti'],ref,'1','U_XU',pin)
            after=distance(fps['trial'],ref,'1','U_XU',pin)
            bypass.append({'ref':ref,'xu_pin':pin,'ti_mm':before,'trial_mm':after})
            if after>before+1e-5:raise SystemExit(f'bypass owner distance worsened: {ref}')
    fab_group=sorted(set(timing['moves'])|{'U_ADC_I2C_XLATE'})
    fab_rows=[ref for ref in fab_group if fps['trial'][ref].Reference().GetLayer()==p.F_Fab]
    with tempfile.TemporaryDirectory(prefix='crow-integrated-audit-') as d:
        temp=Path(d)
        old_board=temp/'old.kicad_pcb';new_board=temp/'new.kicad_pcb'
        shutil.copy2(BASE,old_board);shutil.copy2(TRIAL,new_board)
        old=drc(old_board,temp/'old.json');new=drc(new_board,temp/'new.json')
        before=census(BASE,temp/'before');after=census(TRIAL,temp/'after')
    old_issues=issues(old);new_issues=issues(new)
    new_non_silk=sorted(v for v in new_issues-old_issues if v[0] not in ('silk_overlap','silk_over_copper'))
    new_issue_rows=[v for v in new['violations'] if (v['type'],v['description'],
                    tuple(sorted(i['uuid'] for i in v['items']))) in new_issues-old_issues]
    if len(new['unconnected_items'])!=499:raise SystemExit('opens denominator drift')
    bc=before['counts'];ac=after['counts']
    if after['cross_owner_native_interactions'] or ac['cross_owner_native_interaction_pairs']!=0:
        raise SystemExit('cross-owner native collision')
    removed_issue_rows=[v for v in old['violations'] if (v['type'],v['description'],
                        tuple(sorted(i['uuid'] for i in v['items']))) in old_issues-new_issues]
    old_clearance=[v for v in removed_issue_rows if v['type']=='clearance']
    new_clearance=[v for v in new_issue_rows if v['type']=='clearance']
    if len(old_clearance)!=1 or len(new_clearance)!=1 or \
       'actual 0.1000 mm' not in old_clearance[0]['description'] or \
       old_clearance[0]['description']!=new_clearance[0]['description']:
        raise SystemExit('persistent ISO8 clearance identity/magnitude drift')
    receipt={'schema':1,'status':'REJECTED_PERSISTENT_NATIVE_CLEARANCE','p1_accepted':False,'p2_accepted':False,
             'route_credit':False,'return_credit':False,
             'board_sha256':EXPECTED,'fixed_ref_count':27,'footprint_count':569,
             'pose_union_count_excluding_qpre':len(expected['move_union']),
             'pose_union_count_including_qpre':len(trial_changed),
             'pad_identity_and_relative_geometry_preserved':True,
             'cross_owner_census':{'baseline':bc,'trial':ac,
                                   'baseline_pairs':before['cross_owner_native_interactions'],
                                   'trial_pairs':after['cross_owner_native_interactions']},
             'adc7_portal':{'bbox_mm':portal,'native_obstacles':portal_hits},
             'timing_mouths':mouths,'related_distances':related,'xu_bypass_distances':bypass,
             'native_drc':{'baseline_violations':len(old['violations']),'trial_violations':len(new['violations']),
                           'baseline_unconnected':len(old['unconnected_items']),
                           'trial_unconnected':len(new['unconnected_items']),
                           'new_non_silk_issues':len(new_non_silk),
                           'new_silk_issues':len(new_issues-old_issues)-len(new_non_silk),
                           'removed_issues':len(old_issues-new_issues),
                           'new_issue_rows':new_issue_rows,'removed_issue_rows':removed_issue_rows,
                           'clearance_interpretation':'The same 0.100 mm actual versus 0.200 mm required via/pad deficit persists; identity moves from U_ISO8.2 AUDIO_EN to U_ISO8.4 ISO8P.'},
             'timing_native_probe_fab_label_count':len(fab_group),
             'source_regenerated_timing_fab_reference_fields':fab_rows,
             'debts':['Pre-existing 0.100 mm versus 0.200 mm ISO8 GND-via clearance deficit persists at U_ISO8.4 ISO8P after moving from U_ISO8.2 AUDIO_EN',
                      'five source-generated reference text-height DRC warnings change identity; total unchanged',
                      'ADC8 coupling-cap owner/USB margin is only 0.005 mm in the 15-part component study',
                      '28 timing-probe reference fields placed on F.Fab are not source-encoded here',
                      'In1.Cu GND zone is unfilled; no continuous return or traces are proved',
                      'Frozen TI roundrect USB ESD pads differ from the rect style in the current ordinary netlist; governed TSX status requires shape-sensitive rebaseline before promotion']}
    (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'board':EXPECTED['trial'],'poses':len(trial_changed),'cross_owner':ac['cross_owner_native_interaction_pairs'],
                      'mouth_slots':{n:v['raw_slots'] for n,v in mouths.items()},'drc':receipt['native_drc']},sort_keys=True))

if __name__=='__main__':main()
