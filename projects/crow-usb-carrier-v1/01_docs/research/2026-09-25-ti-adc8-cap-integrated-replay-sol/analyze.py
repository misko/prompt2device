#!/usr/bin/env python3
"""Full-board geometry/authority receipt for the source-generated ADC8 cap shift."""
from __future__ import annotations
import hashlib, importlib.util, json, math, sys, tempfile
from pathlib import Path
import yaml
try:
    import pcbnew as p
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages'); import pcbnew as p

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
P=ROOT/'projects/crow-usb-carrier-v1'
RESEARCH=P/'01_docs/research'
OLD=RESEARCH/'2026-09-25-ti-integrated-placement-sol/candidate.kicad_pcb'
NEW=HERE/'candidate.kicad_pcb'
PROFILE=HERE/'profile_receipt.json'
SOURCE=P/'06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/03_src/floorplan.yaml'
FIXED=P/'03_src/rules/p1_corridor_requirements.yaml'
PREV=RESEARCH/'2026-09-25-ti-integrated-placement-sol/analyze.py'
HELPER=ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED={'old':'20373950748ac51113b115b2d12d169160c24024a2a000572bb70c67b0f60919',
          'new':'0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93',
          'source':'0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hit(a,b):return max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3])
def gap(a,b):return round(math.hypot(max(b[0]-a[2],a[0]-b[2],0),max(b[1]-a[3],a[1]-b[3],0)),6)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def main():
    if {'old':sha(OLD),'new':sha(NEW),'source':sha(SOURCE)}!=EXPECTED:
        raise SystemExit('board/source SHA drift')
    profile=json.loads(PROFILE.read_text())
    if profile['input_sha256']['baseline']!=EXPECTED['old'] or \
       profile['input_sha256']['candidate']!=EXPECTED['new'] or \
       profile['status']!='FULL_PROFILE_DRC_DELTA_CLEAN_RESEARCH_ONLY' or \
       profile['issue_identity_delta']!={'added':0,'removed':0}:
        raise SystemExit('full-profile DRC receipt drift')
    old=p.LoadBoard(str(OLD));new=p.LoadBoard(str(NEW))
    f0={f.GetReference():f for f in old.GetFootprints()}
    f1={f.GetReference():f for f in new.GetFootprints()}
    if len(f0)!=569 or set(f0)!=set(f1):raise SystemExit('569-ref denominator drift')
    prev=load(PREV,'integrated_checks')
    helper=load(HELPER,'corridor_helper')
    fixed=yaml.safe_load(FIXED.read_text())['p1_fixed_refs']
    if len(fixed)!=27 or any(prev.pose(f0[r])!=prev.pose(f1[r]) for r in fixed):
        raise SystemExit('27 fixed poses drift')
    if any(prev.sig(old,f0[r])!=prev.sig(new,f1[r]) for r in f0):
        raise SystemExit('pad/net/layer/shape/local-geometry drift')
    pose_delta={r:{'old':prev.pose(f0[r]),'new':prev.pose(f1[r])}
                for r in f0 if prev.pose(f0[r])!=prev.pose(f1[r])}
    if pose_delta!={'C_ADC_AC8N1':{'old':[198.2,60.25,0.0],'new':[198.0,60.05,0.0]}}:
        raise SystemExit(f'unexpected pose delta: {pose_delta}')
    floor=yaml.safe_load(SOURCE.read_text())
    regions=floor['placement']['regions']
    boxes={r:helper._physical_envelope(fp) for r,fp in f1.items()}
    cap=boxes['C_ADC_AC8N1']
    owner=regions['analog_ch8'];usb=regions['usb_vbus_sense']
    margins={'owner_east_mm':round(owner[2]-cap[2],6),'usb_north_mm':round(usb[1]-cap[3],6)}
    if margins!={'owner_east_mm':.205,'usb_north_mm':.205}:
        raise SystemExit(f'ADC8/USB margin drift: {margins}')
    if not helper.contains(owner,cap) or hit(cap,usb):raise SystemExit('ADC8 owner/USB containment failure')
    full_hits=sorted(r for r,b in boxes.items() if r!='C_ADC_AC8N1' and hit(cap,b))
    if full_hits:raise SystemExit(f'new cap full-envelope intersection: {full_hits}')
    old_cap_pads=[helper.box_mm(q.GetBoundingBox()) for q in f0['C_ADC_AC8N1'].Pads()]
    new_cap_pads=[helper.box_mm(q.GetBoundingBox()) for q in f1['C_ADC_AC8N1'].Pads()]
    def pad_hits(cap_pads,board_fps):
        return sorted(f'{r}.{q.GetNumber()}' for r,fp in board_fps.items() if r!='C_ADC_AC8N1'
                      for q in fp.Pads() if any(hit(a,helper.box_mm(q.GetBoundingBox())) for a in cap_pads))
    if pad_hits(new_cap_pads,f1) or set(pad_hits(new_cap_pads,f1))-set(pad_hits(old_cap_pads,f0)):
        raise SystemExit('new cap pad collision')
    related=[('C_ADC_AC8N1','1','U_ISO8','6'),('C_ADC_AC8N1','2','C_ADC_CM8N','1')]
    distances=[{'pads':[f'{a}.{an}',f'{b}.{bn}'],'old_mm':prev.distance(f0,a,an,b,bn),
                'new_mm':prev.distance(f1,a,an,b,bn)} for a,an,b,bn in related]
    if any(d['new_mm']>d['old_mm'] for d in distances):raise SystemExit('ADC8 related-pad locality worsened')
    nearest=sorted((gap(cap,b),r) for r,b in boxes.items() if r!='C_ADC_AC8N1')[:8]
    with tempfile.TemporaryDirectory(prefix='crow-cap-census-') as d:
        root=Path(d)
        before=prev.census(OLD,root/'old');after=prev.census(NEW,root/'new')
    oldc=before['counts'];newc=after['counts']
    if before['cross_owner_native_interactions'] or after['cross_owner_native_interactions'] or oldc!=newc:
        raise SystemExit('global owner/native census delta')
    timing=json.loads((RESEARCH/'2026-09-25-ti-timing-coupled-placement-sol/result.json').read_text())
    fab_refs=sorted(set(timing['moves'])|{'U_ADC_I2C_XLATE'})
    fab_fields=[r for r in fab_refs if f1[r].Reference().GetLayer()==p.F_Fab]
    gnd_zones=[{'layers':[new.GetLayerName(i) for i in z.GetLayerSet().Seq()],
                'filled':bool(z.IsFilled())} for z in new.Zones() if z.GetNetname()=='GND' and not z.GetIsRuleArea()]
    if fab_fields or any(z['filled'] for z in gnd_zones):raise SystemExit('label/return state drift')
    result={'schema':1,'status':'GEOMETRY_IMPROVED_RESEARCH_ONLY','p1_accepted':False,'p2_accepted':False,
            'board_sha256':{'baseline':EXPECTED['old'],'trial':EXPECTED['new']},
            'profile_receipt_sha256':sha(PROFILE),'fixed_ref_count':27,'footprint_count':569,
            'pad_identity_preserved':True,'pose_delta':pose_delta,
            'cap_envelope_mm':cap,'cap_owner_usb_margins_mm':margins,
            'cap_full_envelope_hits':full_hits,'cap_pad_hits':pad_hits(new_cap_pads,f1),
            'cap_nearest_envelope_gaps_mm':nearest,'related_pad_distances':distances,
            'global_census_counts':newc,'global_cross_owner_native_pairs':after['cross_owner_native_interactions'],
            'full_profile_drc':{'baseline':profile['boards']['baseline']['drc'],
                                'trial':profile['boards']['candidate']['drc'],
                                'issue_identity_delta':profile['issue_identity_delta']},
            'timing_probe_fab_reference_fields_expected':len(fab_refs),
            'source_regenerated_fab_reference_fields':fab_fields,
            'gnd_zones':gnd_zones,
            'unresolved':['0.205 mm is source rectangle margin only, not routing/assembly tolerance',
                          'ADC8 signal/return escape and nearby support gaps need route proof',
                          '28 timing label placements on F.Fab are not source encoded',
                          'GND zone remains unfilled and 499 opens remain',
                          'conditional B2 POFV and USB ESD shape/vendor acceptance remain separate']}
    (HERE/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'trial_sha':EXPECTED['new'],'margins':margins,'nearest':nearest[:3],
                      'census_cross_owner':newc['cross_owner_native_interaction_pairs'],
                      'drc_delta':profile['issue_identity_delta']},sort_keys=True))

if __name__=='__main__':main()
