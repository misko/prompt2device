#!/usr/bin/env python3
"""Fail-closed 36-member analog_ch8 physical-cell lower-bound screen."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'skills/kicad-pcb/scripts'))
import p1_corridor_capacity as checker

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
P=ROOT/'projects/crow-usb-carrier-v1'
BOARD=P/'01_docs/research/2026-09-25-ti-adc8-cap-integrated-replay-sol/candidate.kicad_pcb'
FLOOR=P/'03_src/floorplan.yaml'
MODULAR=P/'03_src/modular_plan.json'
SOURCE=P/'03_src/rules/p1_corridor_requirements.yaml'
CHECKER=ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED={
 'board':'0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93',
 'floorplan':'c2a6562c1a012e692109b852158af2ef73a432f712a62ae87cbd8e49c4c4ecd6',
 'modular':'75c3a517cea50dd6b5745fae96b051d334debd48aac143becaca3d5fe3fc35dc',
 'p1_source':'191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3',
 'checker':'e060924188e4e68d1e7a4f7416b3eb7c92dba29b14b8de1c929f2f70f82a0eb6',
}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def min_box(fp):
    shapes=[checker._physical_envelope(fp)]+[checker.box_mm(p.GetBoundingBox()) for p in fp.Pads()]
    return [round(min(z[0] for z in shapes),6),round(min(z[1] for z in shapes),6),
            round(max(z[2] for z in shapes),6),round(max(z[3] for z in shapes),6)]

def main():
    paths={'board':BOARD,'floorplan':FLOOR,'modular':MODULAR,'p1_source':SOURCE,'checker':CHECKER}
    hashes={name:sha(path) for name,path in paths.items()}
    if hashes!=EXPECTED:raise SystemExit(f'input SHA drift: {hashes}')
    board=checker.pcbnew.LoadBoard(str(BOARD))
    fps={fp.GetReference():fp for fp in board.GetFootprints()}
    if len(fps)!=569:raise SystemExit('569-ref board drift')
    modular=json.loads(MODULAR.read_text())
    members=next(block['refs'] for block in modular['blocks'] if block['id']=='analog_ch8')
    if len(members)!=36 or len(set(members))!=36 or not set(members)<=set(fps):
        raise SystemExit('analog_ch8 denominator drift')
    fixed=yaml.safe_load(SOURCE.read_text())['p1_fixed_refs']
    if len(fixed)!=27 or 'J8' not in fixed:raise SystemExit('fixed-set drift')
    floor=yaml.safe_load(FLOOR.read_text())
    native_regions=floor['placement']['regions']
    outline=checker.pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline,False) or outline.OutlineCount()!=1:
        raise SystemExit('native outline unavailable')
    outline_box=checker.box_mm(outline.BBox())
    # One full native envelope/pad per typed cell is the smallest rectangular
    # complete-denominator proposal. Larger cells cannot repair an off-board
    # required bound or a foreign-region hit at that footprint.
    order=['C_ADC_AC8N1','J8']+sorted(set(members)-{'C_ADC_AC8N1','J8'})
    ids={ref:('analog_ch8' if ref=='C_ADC_AC8N1' else 'analog_ch8_'+ref.lower()) for ref in order}
    boxes={ref:min_box(fps[ref]) for ref in order}
    rows=[{'id':ids[ref],'owner_block':'analog_ch8','refs':[ref],'transit':False} for ref in order]
    if {ref for row in rows for ref in row['refs']}!=set(members):raise SystemExit('typed cell ref denominator incomplete')
    regions=dict(native_regions)
    regions['analog_ch8']=boxes['C_ADC_AC8N1']
    regions.update({ids[ref]:boxes[ref] for ref in order if ref!='C_ADC_AC8N1'})
    patterns=[p for p in floor['placement']['patterns'] if not set(p.get('match',[]))&set(members)]
    patterns.extend({'match':[ref],'region':ids[ref]} for ref in order)
    source={'physical_cells':rows}
    def check(current_regions):
        try:
            checker._physical_cells(source,modular,board,outline,current_regions,patterns)
        except checker.ContractError as exc:
            return str(exc)
        return 'UNEXPECTED_PASS'
    exact_error=check(regions)
    clipped=dict(regions)
    clipped[ids['J8']]=[boxes['J8'][0],outline_box[1],boxes['J8'][2],boxes['J8'][3]]
    clipped_error=check(clipped)
    if exact_error!=f"{ids['J8']}: physical cell off board outline" or \
       clipped_error!=f"J8: native footprint/pad leaves physical cell {ids['J8']}":
        raise SystemExit(f'edge contradiction changed: {exact_error}; {clipped_error}')
    full_j8=checker._physical_envelope(fps['J8'])
    body_j8=checker.box_mm(fps['J8'].GetBoundingBox(False,False))
    pad_boxes=[checker.box_mm(p.GetBoundingBox()) for p in fps['J8'].Pads()]
    foreign={ref:sorted(name for name,box in native_regions.items()
                        if name!='analog_ch8' and checker.intersects(boxes[ref],box)) for ref in order}
    foreign={ref:names for ref,names in foreign.items() if names}
    native_hits={ref:sorted(other for other,fp in fps.items() if other!=ref and
                           checker.intersects(boxes[ref],checker._physical_envelope(fp))) for ref in order}
    native_hits={ref:names for ref,names in native_hits.items() if names}
    outboard=sorted(ref for ref in order if not checker.lane_inside_outline(outline,boxes[ref]))
    result={'schema':1,'status':'UNSAT_CURRENT_PHYSICAL_CELL_SCHEMA','p1_accepted':False,'p2_accepted':False,
            'input_sha256':hashes,'board_footprints':len(fps),'fixed_ref_count':len(fixed),
            'functional_owner':'analog_ch8','member_count':len(members),
            'native_outline_bbox_mm':outline_box,
            'primary_cell_cap_bbox_mm':boxes['C_ADC_AC8N1'],
            'j8':{'fixed':True,'full_envelope_mm':full_j8,'body_mm':body_j8,
                  'pad_count':len(pad_boxes),
                  'minimum_pad_y_mm':min(box[1] for box in pad_boxes),
                  'minimum_cell_bbox_mm':boxes['J8'],
                  'outboard_full_envelope_mm':round(outline_box[1]-full_j8[1],6),
                  'outboard_body_mm':round(outline_box[1]-body_j8[1],6)},
            'checker_exact_minimum_cell_error':exact_error,
            'checker_outline_clipped_cell_error':clipped_error,
            'outboard_minimum_cells':outboard,
            'current_foreign_region_hits':foreign,
            'minimum_cell_native_footprint_hits':native_hits,
            'current_regions':{k:native_regions[k] for k in
                               ('analog_ch7','analog_ch8','audio_clock_tdm','usb_vbus_sense','usb_frontend')},
            'full_member_ref_ids':{ref:ids[ref] for ref in order},
            'debts':['A current-schema physical cell cannot both contain fixed J8 full native envelope and stay in the outline',
                     'Eleven analog_ch8 refs intersect current foreign planning regions, requiring coupled source recuts or placement repair',
                     'Cells exactly equal to native bounds reserve no route/return margin and grant no capacity',
                     'ADC8N/P/VMID2/AUDIO_EN endpoint-to-cell and filled return obligations remain unproved']}
    (HERE/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (HERE/'typed_cells.json').write_text(json.dumps({'schema':1,'kind':'minimum-bound-typed-cell-proposal',
        'status':'REJECTED_UNDER_CURRENT_CHECKER','region_rectangles_mm':{ids[r]:boxes[r] for r in order},
        'physical_cells':rows,'placement_pattern_replacements':[{'match':[r],'region':ids[r]} for r in order]},
        indent=2,sort_keys=True)+'\n')
    print(json.dumps({'member_count':len(members),'edge_errors':[exact_error,clipped_error],
                      'outboard':outboard,'foreign_refs':len(foreign),'native_overlap_refs':len(native_hits)},sort_keys=True))

if __name__=='__main__':main()
