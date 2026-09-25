#!/usr/bin/env python3
"""Reject-first ADC8 cap margin and two-cell recut screen; no board mutation."""
from __future__ import annotations
import hashlib, importlib.util, json, math, sys
from pathlib import Path
import yaml
try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
P = ROOT / 'projects/crow-usb-carrier-v1'
PATHS = {
    'board': P/'01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb',
    'floorplan': P/'01_docs/research/2026-09-25-ti-adc-analog-88-accounting-sol/floorplan.yaml',
    'modular_plan': P/'01_docs/research/2026-09-25-ti-adc-analog-88-accounting-sol/modular_plan.json',
    'source': P/'01_docs/research/2026-09-25-ti-adc-analog-88-accounting-sol/p1_requirements.yaml',
    'helper': ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py',
}
EXPECTED = {
    'board': 'd0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7',
    'floorplan': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    'modular_plan': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'source': '60b7062e53bfd930ee7e9e2a8694b87098b1a5625d4a48c06eddb2f8bd8b5be7',
    'helper': '0827824c749206fc11194f27daa6e732a3253b348054a6d93218e960fe138a93',
}
MARGIN = .56  # Exploratory full-envelope entry/return screen, not a design rule.
GAP = .15
RATIO = 1.5  # Exploratory related-pad locality bound, not a design rule.
DIVIDER = 202.105  # Terra 0e5ef9fa's divider interval; 0.56 mm east of U_AFE8.

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def xy(item):
    p = item.GetPosition()
    return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
def gap(a,b):
    return math.hypot(max(b[0]-a[2],a[0]-b[2],0), max(b[1]-a[3],a[1]-b[3],0))
def pad(fps,ref,pin):
    return next(p for p in fps[ref].Pads() if p.GetNumber()==pin)

def main():
    for name, expected in EXPECTED.items():
        if sha(PATHS[name]) != expected: raise SystemExit(f'{name} SHA drift')
    spec=importlib.util.spec_from_file_location('capacity',PATHS['helper'])
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    b=pcbnew.LoadBoard(str(PATHS['board']))
    fps={fp.GetReference():fp for fp in b.GetFootprints()}
    floor=yaml.safe_load(PATHS['floorplan'].read_text())['placement']['regions']
    modular=json.loads(PATHS['modular_plan'].read_text())
    fixed=yaml.safe_load(PATHS['source'].read_text())['p1_fixed_refs']
    if len(fixed)!=27 or not all(ref in fps for ref in fixed): raise SystemExit('fixed set mismatch')
    ref='C_ADC_AC8N1'; c=fps[ref]; old=xy(c); body=h._physical_envelope(c)
    owner=floor['analog_ch8'];usb=floor['usb_vbus_sense']
    stat={k:h._physical_envelope(v) for k,v in fps.items() if k!=ref}
    partners=(xy(pad(fps,'U_ISO8','6')),xy(pad(fps,'C_ADC_CM8N','1')))
    baseline=(9.141663,11.810521)
    counts={'owner_and_usb_margin':0,'body_clear':0,'related_1_5x':0,
            'related_1_5x_and_0_56_body_mouth':0,'within_6mm':0}
    legal=[]
    # Complete 0.1-mm grid of cap origins within the original analog-ch8 rectangle.
    for xi in range(1818,1980):
        x=xi/10
        for yi in range(438,823):
            y=yi/10
            bb=(x-2.795,y-1.745,x+2.795,y+1.745)
            if not h.contains(owner,bb) or owner[2]-bb[2]<MARGIN-1e-6 or gap(bb,usb)<MARGIN-1e-6:continue
            counts['owner_and_usb_margin']+=1
            nearest=min((gap(bb,v),name) for name,v in stat.items())
            if nearest[0]<GAP-1e-6:continue
            counts['body_clear']+=1
            ds=(math.dist((x-1.8,y),partners[0]),math.dist((x+1.8,y),partners[1]))
            ratio=max(ds[i]/baseline[i] for i in range(2))
            if ratio>RATIO+1e-6:continue
            counts['related_1_5x']+=1
            if nearest[0]>=MARGIN-1e-6:counts['related_1_5x_and_0_56_body_mouth']+=1
            move=math.dist((x,y),old)
            if move<=6+1e-6:counts['within_6mm']+=1
            legal.append((move,x,y,nearest[0],nearest[1],ratio,*ds))
    if counts['within_6mm']!=0:raise SystemExit('compact cap pose unexpectedly exists')
    trial=(197.6,59.6)
    tb=(trial[0]-2.795,trial[1]-1.745,trial[0]+2.795,trial[1]+1.745)
    trial_blockers=sorted((round(gap(tb,v),6),name) for name,v in stat.items())[:6]
    # Test only the analog/USB x divider. All other source rectangles are unchanged.
    recut=dict(floor)
    recut['analog_ch8']=[179,42,DIVIDER,84]
    recut['usb_vbus_sense']=[DIVIDER,62,215,82]
    failures=[];block_sizes={}
    for block in modular['blocks']:
        if block['id'] not in ('analog_ch8','usb_vbus_sense'):continue
        name=block['id'];block_sizes[name]=len(block['refs'])
        for member in block['refs']:
            if member not in fps:raise SystemExit(f'missing modular member {member}')
            bb=h._physical_envelope(fps[member])
            foreign=[key for key,region in recut.items() if key!=name and h.intersects(bb,region)]
            if not h.contains(recut[name],bb) or foreign:
                failures.append({'ref':member,'owner':name,
                                 'physical_bbox_mm':[round(v,6) for v in bb],
                                 'contained':h.contains(recut[name],bb),
                                 'foreign_regions':foreign})
    if len(failures)!=7:raise SystemExit(f'two-cell failure inventory drift: {len(failures)}')
    return {'schema':1,'kind':'adc8-cap-positive-mouth-and-two-cell-recut-bound',
            'status':'REJECTED_BOUNDED_REPAIR','p1_accepted':False,'p2_accepted':False,
            'routing_realized':False,'return_credit':False,
            'sha256':{key:sha(value) for key,value in PATHS.items()},
            'board_unchanged':True,'fixed_ref_count':len(fixed),
            'illustrative_margin_mm':MARGIN,'minimum_body_gap_mm':GAP,
            'illustrative_max_related_distance_ratio':RATIO,
            'cap_origin_mm':old,'cap_physical_bbox_mm':body,
            'current_owner_mm':owner,'current_usb_mm':usb,
            'cap_grid_step_mm':.1,'cap_grid_counts':counts,
            'nearest_grid_pose_1_5x':dict(zip(('move_mm','x_mm','y_mm','nearest_gap_mm','nearest_ref',
                                              'worst_related_ratio','iso6_mm','cm8n1_mm'),
                                             (round(v,6) if isinstance(v,float) else v for v in sorted(legal)[0]))),
            'compact_trial':{'cap_origin_mm':trial,'cap_bbox_mm':tb,
                             'east_owner_margin_mm':round(owner[2]-tb[2],6),
                             'usb_separation_mm':round(gap(tb,usb),6),
                             'nearest_static_envelopes_mm':trial_blockers},
            'two_cell_recut':{'divider_x_mm':DIVIDER,'analog_ch8_mm':recut['analog_ch8'],
                              'usb_vbus_sense_mm':recut['usb_vbus_sense'],
                              'block_member_counts':block_sizes,
                              'owner_or_foreign_failures':failures},
            'limitations':'Grid keeps 14 other candidate moves fixed; 0.56-mm margin and 1.5x locality are exploratory. '
                          'Two-cell recut leaves all other source regions unchanged. No trace/return/zone fill is proved.'}
if __name__=='__main__':print(json.dumps(main(),indent=2,sort_keys=True))
