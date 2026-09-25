#!/usr/bin/env python3
"""Bounded ADC8N local reroute avoiding the current USB VBUS planning cell."""
from __future__ import annotations
import hashlib, json, math, shutil, sys, tempfile
from pathlib import Path
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p

HERE=Path(__file__).resolve().parent
PREV=HERE.parent/'2026-09-25-ti-adc8n-local-route-sol'
sys.path.insert(0,str(PREV))
import route_probe as base

PREV_SCRIPT_SHA='f7cd97bbf5a018e958f4b5d1132d21c38e16a997c970ec230e1ccfb2c794fc8c'
COORDS=[(199.8,60.05),(199.8,60.0),(198.0,61.8),(194.6,61.8),
        (190.5,65.9),(187.9,65.9),(187.9,66.1),(187.5,66.5),(187.52,66.5)]
USB_RECT=[195.0,62.0,220.0,82.0]

def usb_screen(board):
    rect=p.SHAPE_RECT(base.pt(USB_RECT[0],USB_RECT[1]),base.pt(USB_RECT[2],USB_RECT[3]))
    gaps=[]
    for track in (t for t in board.GetTracks() if t.GetNetname()=='ADC8N'):
        shape=track.GetEffectiveShape(p.F_Cu)
        if shape.Collide(rect,0):raise RuntimeError('ADC8N F.Cu copper enters usb_vbus_sense')
        lo,hi=0,p.FromMM(2)
        if not shape.Collide(rect,hi):continue
        for _ in range(22):
            middle=(lo+hi)//2
            if shape.Collide(rect,middle):hi=middle
            else:lo=middle
        gaps.append((base.mm(hi),[[base.mm(track.GetStart().x),base.mm(track.GetStart().y)],
                                    [base.mm(track.GetEnd().x),base.mm(track.GetEnd().y)]]))
    gap,segment=min(gaps)
    return {'usb_vbus_sense_bbox_mm':USB_RECT,'minimum_copper_to_planning_rect_gap_mm':round(gap,6),
            'limiting_segment_mm':segment,'any_copper_intersection':False}

def main():
    if hashlib.sha256((PREV/'route_probe.py').read_bytes()).hexdigest()!=PREV_SCRIPT_SHA:
        raise RuntimeError('prior proven probe implementation drift')
    paths={'board':base.SOURCE,'pro':base.PROFILE/'crow_carrier.kicad_pro',
           'dru':base.PROFILE/'crow_carrier.kicad_dru','assembly':base.ASSEMBLY,
           'producer':base.GEN}
    hashes={key:base.sha(path) for key,path in paths.items()}
    if hashes!=base.EXPECTED:raise RuntimeError(f'input SHA drift: {hashes}')
    original=p.LoadBoard(str(base.SOURCE));ledger=base.footprint_ledger(original)
    if len(ledger)!=569:raise RuntimeError('569 footprint denominator drift')
    if base.pad(original,'C_ADC_AC8N1','2').GetNetname()!='ADC8N' or \
       base.pad(original,'C_ADC_CM8N','1').GetNetname()!='ADC8N':
        raise RuntimeError('exact ADC8N endpoint net drift')
    prior=json.loads((PREV/'receipt.json').read_text())
    if prior['route']['length_mm']!=15.179545:raise RuntimeError('prior route receipt drift')
    previous_board=PREV/'candidate_filled_profile.kicad_pcb'
    if base.sha(previous_board)!=prior['filled_board_sha256_observation']:
        raise RuntimeError('prior filled route artifact drift')
    previous=p.LoadBoard(str(previous_board))
    rect=p.SHAPE_RECT(base.pt(USB_RECT[0],USB_RECT[1]),base.pt(USB_RECT[2],USB_RECT[3]))
    previous_usb_hits=sum(t.GetEffectiveShape(p.F_Cu).Collide(rect,0)
                          for t in previous.GetTracks() if t.GetNetname()=='ADC8N')
    if not previous_usb_hits:raise RuntimeError('prior route USB-region red control absent')
    base.add_route(original,COORDS)  # Same two native-clean ordinary GND stitches.
    usb_screen(original)
    with tempfile.TemporaryDirectory(prefix='crow-adc8n-usb-avoid-') as folder:
        temp=Path(folder)
        bare=temp/'rerouted.kicad_pcb';p.SaveBoard(str(bare),original)
        baseline,old_drc,old_via,_=base.profile('baseline',base.SOURCE,temp)
        candidate,new_drc,new_via,new_drc_path=base.profile('candidate',bare,temp)
        native=p.LoadBoard(str(candidate))
        if base.footprint_ledger(native)!=ledger:raise RuntimeError('pose/pad identity drift')
        old_issues=set(map(base.issue,old_drc['violations']))
        new_issues=set(map(base.issue,new_drc['violations']))
        if new_issues-old_issues or old_via.get('fails') or new_via.get('fails'):
            raise RuntimeError(f'new native/profile finding: {new_issues-old_issues}')
        native.BuildConnectivity();conn=native.GetConnectivity()
        linked={x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
                for x in conn.GetConnectedItems(base.pad(native,'C_ADC_AC8N1','2'))
                if isinstance(x,p.PAD)}
        if 'C_ADC_CM8N.1' not in linked:raise RuntimeError('exact ADC8N pads disconnected')
        area=usb_screen(native)
        ret=base.return_coverage(native,COORDS)
        gap=base.route_clearance(native)
        if gap['minimum_effective_shape_copper_gap_mm']<.15:
            raise RuntimeError('minimum native copper gap below rule')
        length=sum(math.dist(a,b) for a,b in zip(COORDS,COORDS[1:]))
        shutil.copy2(candidate,HERE/'candidate_filled_profile.kicad_pcb')
        shutil.copy2(new_drc_path,HERE/'candidate_drc.json')
        receipt={'schema':1,'status':'LOCAL_GEOMETRY_ONLY_RESEARCH',
                 'input_sha256':hashes,'prior_probe_sha256':PREV_SCRIPT_SHA,
                 'route':{'vertices_mm':COORDS,'layer':'F.Cu','width_mm':.20,
                          'length_mm':round(length,6),'segments':len(COORDS)-1},
                 'prior_route_length_mm':prior['route']['length_mm'],
                 'prior_filled_route_sha256':base.sha(previous_board),
                 'prior_route_copper_usb_region_hits':previous_usb_hits,
                 'length_delta_mm':round(length-prior['route']['length_mm'],6),
                 'usb_planning_region':area,
                 'minimum_native_effective_shape_clearance':gap,
                 'return_polygon':ret,'native_connected_adc8n_pads':sorted(linked),
                 'full_profile':{'baseline_violations':len(old_drc['violations']),
                                 'candidate_violations':len(new_drc['violations']),
                                 'added_violation_identities':len(new_issues-old_issues),
                                 'removed_violation_identities':len(old_issues-new_issues),
                                 'baseline_unconnected':len(old_drc['unconnected_items']),
                                 'candidate_unconnected':len(new_drc['unconnected_items']),
                                 'baseline_v_process_fails':old_via.get('fails'),
                                 'candidate_v_process_fails':new_via.get('fails')},
                 'all_569_footprint_pose_pad_ledgers_preserved':True,
                 'candidate_filled_board_sha256_observation':base.sha(HERE/'candidate_filled_profile.kicad_pcb')}
        (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'length':receipt['route']['length_mm'],'usb_gap':area['minimum_copper_to_planning_rect_gap_mm'],
                          'copper_gap':gap['minimum_effective_shape_copper_gap_mm'],
                          'drc':[len(old_drc['violations']),len(new_drc['violations'])],
                          'opens':[len(old_drc['unconnected_items']),len(new_drc['unconnected_items'])]},sort_keys=True))

if __name__=='__main__':main()
