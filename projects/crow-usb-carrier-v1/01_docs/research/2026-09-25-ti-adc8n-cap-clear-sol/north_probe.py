#!/usr/bin/env python3
"""One bounded north-of-cap ADC8N route, with explicit own-pad launch exemption."""
from __future__ import annotations
import hashlib,json,math,shutil,sys,tempfile
from pathlib import Path
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p

HERE=Path(__file__).resolve().parent
PREV=HERE.parent/'2026-09-25-ti-adc8n-local-route-sol'
sys.path.insert(0,str(PREV))
import route_probe as base
EXPECTED_PROBE='f7cd97bbf5a018e958f4b5d1132d21c38e16a997c970ec230e1ccfb2c794fc8c'
CAP=[195.205,58.305,200.795,61.795]
USB=[195.0,62.0,220.0,82.0]
COORDS=[(199.8,60.05),(199.8,58.05),(195.05,58.05),(195.05,61.6),
        (190.75,65.9),(187.9,65.9),(187.9,66.1),(187.5,66.5),(187.52,66.5)]
LAUNCH_GND_VIA=(200.4,57.8)

def rect(box):return p.SHAPE_RECT(base.pt(box[0],box[1]),base.pt(box[2],box[3]))
def distance_to_shape(track,shape):
    native=track.GetEffectiveShape(p.F_Cu)
    if native.Collide(shape,0):return 0.0
    lo,hi=0,p.FromMM(2)
    if not native.Collide(shape,hi):return 2.0
    for _ in range(22):
        mid=(lo+hi)//2
        if native.Collide(shape,mid):hi=mid
        else:lo=mid
    return base.mm(hi)

def short_south_screens(board):
    result=[]
    for y in (61.88,61.895,61.8975,61.9):
        t=p.PCB_TRACK(board);t.SetStart(base.pt(198.0,y));t.SetEnd(base.pt(194.6,y))
        t.SetWidth(p.FromMM(.20));t.SetLayer(p.F_Cu)
        result.append({'centerline_y_mm':y,
                       'hits_cap_full':t.GetEffectiveShape(p.F_Cu).Collide(rect(CAP),0),
                       'hits_usb':t.GetEffectiveShape(p.F_Cu).Collide(rect(USB),0),
                       'cap_gap_mm':round(distance_to_shape(t,rect(CAP)),6),
                       'usb_gap_mm':round(distance_to_shape(t,rect(USB)),6)})
    return result

def add_candidate(board):
    adc=board.FindNet('ADC8N');gnd=board.FindNet('GND')
    for a,b in zip(COORDS,COORDS[1:]):
        t=p.PCB_TRACK(board);t.SetStart(base.pt(*a));t.SetEnd(base.pt(*b))
        t.SetLayer(p.F_Cu);t.SetWidth(p.FromMM(.20));t.SetNet(adc);board.Add(t)
    for xy,near in [(LAUNCH_GND_VIA,(198.1,56.5)),((188.95,66.5),(188.48,66.5))]:
        via=p.PCB_VIA(board);via.SetPosition(base.pt(*xy));via.SetWidth(p.FromMM(.60))
        via.SetDrill(p.FromMM(.30));via.SetViaType(p.VIATYPE_THROUGH)
        via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(gnd);board.Add(via)
        neck=p.PCB_TRACK(board);neck.SetStart(base.pt(*xy));neck.SetEnd(base.pt(*near))
        neck.SetLayer(p.F_Cu);neck.SetWidth(p.FromMM(.20));neck.SetNet(gnd);board.Add(neck)

def cap_usb_screen(board):
    tracks=[t for t in board.GetTracks() if t.GetNetname()=='ADC8N']
    if len(tracks)!=len(COORDS)-1:raise RuntimeError('ADC8N track count drift')
    launch=[t for t in tracks if (base.mm(t.GetStart().x),base.mm(t.GetStart().y))==COORDS[0]]
    if len(launch)!=1:raise RuntimeError('named pad launch absent')
    launch=launch[0]
    if not launch.GetEffectiveShape(p.F_Cu).Collide(rect(CAP),0):
        raise RuntimeError('expected own-pad launch within native cap envelope absent')
    cap_gaps=[];usb_gaps=[]
    for t in tracks:
        shape=t.GetEffectiveShape(p.F_Cu)
        if shape.Collide(rect(USB),0):raise RuntimeError('ADC8N copper enters USB planning cell')
        usb_gaps.append(distance_to_shape(t,rect(USB)))
        if t is launch:continue
        if shape.Collide(rect(CAP),0):raise RuntimeError('post-launch copper enters cap full envelope')
        cap_gaps.append(distance_to_shape(t,rect(CAP)))
    return {'named_own_pad_launch_mm':[list(COORDS[0]),list(COORDS[1])],
            'post_launch_min_cap_full_gap_mm':round(min(cap_gaps),6),
            'full_route_min_usb_gap_mm':round(min(usb_gaps),6),
            'post_launch_cap_copper_hits':0,'usb_copper_hits':0}

def native_envelope_hits(board):
    tracks=[t for t in board.GetTracks() if t.GetNetname()=='ADC8N']
    result={}
    for fp in board.GetFootprints():
        body=fp.GetBoundingBox(False,False)
        box=[base.mm(v) for v in (body.GetLeft(),body.GetTop(),body.GetRight(),body.GetBottom())]
        for layer in (p.F_CrtYd,p.B_CrtYd):
            courtyard=fp.GetCourtyard(layer)
            if courtyard.OutlineCount():
                bb=courtyard.BBox();other=[base.mm(v) for v in
                                             (bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom())]
                box=[min(box[0],other[0]),min(box[1],other[1]),
                     max(box[2],other[2]),max(box[3],other[3])]
        shape=rect(box)
        hits=[]
        for t in tracks:
            if t.GetEffectiveShape(p.F_Cu).Collide(shape,0):
                hits.append([[base.mm(t.GetStart().x),base.mm(t.GetStart().y)],
                             [base.mm(t.GetEnd().x),base.mm(t.GetEnd().y)]])
        if hits:result[fp.GetReference()]={'full_envelope_mm':box,'segment_hits_mm':hits}
    return result

def return_screen(board):
    zones=[z for z in board.Zones() if z.GetNetname()=='GND' and p.In1_Cu in z.GetLayerSet().Seq()]
    if len(zones)!=1 or not zones[0].IsFilled():raise RuntimeError('In1 GND fill absent')
    filled=zones[0].GetFilledPolysList(p.In1_Cu)
    points=COORDS+[LAUNCH_GND_VIA,(188.95,66.5),(199.0,53.0)]
    common=set(range(filled.OutlineCount()))
    for x,y in points:
        q=base.pt(x,y)
        if not filled.Contains(q):raise RuntimeError(f'GND fill gap at {x},{y}')
        common&={i for i in range(filled.OutlineCount()) if filled.Outline(i).PointInside(q)}
    if not common:raise RuntimeError('route/stitiches lack one filled polygon')
    uncovered=[]
    for a,b in zip(COORDS,COORDS[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        nx,ny=-dy/length*.1,dx/length*.1
        ribbon=p.SHAPE_POLY_SET();ribbon.NewOutline()
        for x,y in ((a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),
                    (b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)):
            ribbon.Append(base.pt(x,y))
        ribbon.BooleanSubtract(filled)
        uncovered.append(round(ribbon.Area()/1e12,9))
    if any(uncovered):raise RuntimeError(f'In1 uncovered route ribbon: {uncovered}')
    return {'same_filled_polygon_outline_indices':sorted(common),
            'uncovered_0p20mm_ribbon_area_mm2_by_segment':uncovered}

def main():
    if hashlib.sha256((PREV/'route_probe.py').read_bytes()).hexdigest()!=EXPECTED_PROBE:
        raise RuntimeError('prior native checker wrapper drift')
    files={'board':base.SOURCE,'pro':base.PROFILE/'crow_carrier.kicad_pro',
           'dru':base.PROFILE/'crow_carrier.kicad_dru','assembly':base.ASSEMBLY,'producer':base.GEN}
    hashes={k:base.sha(v) for k,v in files.items()}
    if hashes!=base.EXPECTED:raise RuntimeError(f'input profile SHA drift: {hashes}')
    source=p.LoadBoard(str(base.SOURCE));ledger=base.footprint_ledger(source)
    if len(ledger)!=569:raise RuntimeError('footprint denominator drift')
    south=short_south_screens(source)
    add_candidate(source)
    geometry=cap_usb_screen(source)
    with tempfile.TemporaryDirectory(prefix='crow-adc8n-north-') as folder:
        temp=Path(folder);bare=temp/'candidate.kicad_pcb';p.SaveBoard(str(bare),source)
        old,old_drc,old_via,_=base.profile('baseline',base.SOURCE,temp)
        new,new_drc,new_via,new_drc_path=base.profile('candidate',bare,temp)
        board=p.LoadBoard(str(new))
        if base.footprint_ledger(board)!=ledger:raise RuntimeError('pose/pad ledger drift')
        if old_via.get('fails') or new_via.get('fails'):raise RuntimeError('V-PROCESS failed')
        old_issues=set(map(base.issue,old_drc['violations']))
        new_issues=set(map(base.issue,new_drc['violations']))
        if new_issues-old_issues:raise RuntimeError(f'new DRC violations: {new_issues-old_issues}')
        geometry=cap_usb_screen(board)
        ret=return_screen(board)
        gap=base.route_clearance(board)
        if gap['minimum_effective_shape_copper_gap_mm']<.15:
            raise RuntimeError('different-net copper gap below rule')
        board.BuildConnectivity();conn=board.GetConnectivity()
        linked={x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
                for x in conn.GetConnectedItems(base.pad(board,'C_ADC_AC8N1','2')) if isinstance(x,p.PAD)}
        if 'C_ADC_CM8N.1' not in linked:raise RuntimeError('ADC8N endpoint disconnection')
        envelope_hits=native_envelope_hits(board)
        if sorted(envelope_hits)!=['C_ADC_AC8N1','C_ADC_CM8N','U_SPOKE8']:
            raise RuntimeError(f'footprint full-envelope hit census changed: {sorted(envelope_hits)}')
        spoke=next(f for f in board.GetFootprints() if f.GetReference()=='U_SPOKE8')
        spoke_body_box=spoke.GetBoundingBox(False,False)
        spoke_body=[base.mm(v) for v in (spoke_body_box.GetLeft(),spoke_body_box.GetTop(),
                                         spoke_body_box.GetRight(),spoke_body_box.GetBottom())]
        spoke_body_hit=any(t.GetEffectiveShape(p.F_Cu).Collide(rect(spoke_body),0)
                           for t in board.GetTracks() if t.GetNetname()=='ADC8N')
        if not spoke_body_hit:raise RuntimeError('expected U_SPOKE8 body-undertrace debt changed')
        launch_gnd=[t for t in board.GetTracks() if t.GetNetname()=='GND' and
                    ((isinstance(t,p.PCB_VIA) and abs(base.mm(t.GetPosition().x)-LAUNCH_GND_VIA[0])<.001 and
                      abs(base.mm(t.GetPosition().y)-LAUNCH_GND_VIA[1])<.001) or
                     (not isinstance(t,p.PCB_VIA) and abs(base.mm(t.GetStart().x)-LAUNCH_GND_VIA[0])<.001 and
                      abs(base.mm(t.GetStart().y)-LAUNCH_GND_VIA[1])<.001))]
        if len(launch_gnd)!=2:raise RuntimeError('relocated GND stitch/neck missing')
        gnd_to_cap=[round(distance_to_shape(t,rect(CAP)),6) for t in launch_gnd]
        gnd_links=[]
        for xy,wanted in ((LAUNCH_GND_VIA,'C_FILTER8N1.2'),((188.95,66.5),'C_ADC_CM8N.2')):
            via=next(t for t in board.GetTracks() if isinstance(t,p.PCB_VIA) and
                     t.GetNetname()=='GND' and abs(base.mm(t.GetPosition().x)-xy[0])<.001 and
                     abs(base.mm(t.GetPosition().y)-xy[1])<.001)
            pads={x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
                  for x in conn.GetConnectedItems(via) if isinstance(x,p.PAD)}
            if wanted not in pads:raise RuntimeError(f'GND stitch missing named pad {wanted}')
            gnd_links.append({'via_center_mm':list(xy),'named_gnd_pad':wanted})
        shutil.copy2(new,HERE/'candidate_filled_profile.kicad_pcb')
        shutil.copy2(new_drc_path,HERE/'candidate_drc.json')
        length=sum(math.dist(a,b) for a,b in zip(COORDS,COORDS[1:]))
        result={'schema':1,'status':'LOCAL_RESEARCH_GEOMETRY_ONLY',
                'input_sha256':hashes,'prior_probe_sha256':EXPECTED_PROBE,
                'cap_full_envelope_mm':CAP,'usb_vbus_sense_mm':USB,
                'south_throat_screens':south,
                'north_route':{'vertices_mm':COORDS,'width_mm':.20,'layer':'F.Cu',
                               'length_mm':round(length,6),'segment_count':len(COORDS)-1},
                'post_launch_shape_clearances':geometry,
                'other_native_full_envelope_hits':envelope_hits,
                'u_spoke8_body_mm':spoke_body,
                'u_spoke8_body_under_adc8n_trace':spoke_body_hit,
                'minimum_native_different_net_copper_gap':gap,
                'filled_return':ret,'native_connected_adc8n_pads':sorted(linked),
                'launch_gnd_via_mm':list(LAUNCH_GND_VIA),
                'launch_gnd_via_and_neck_to_cap_full_gap_mm':sorted(gnd_to_cap),
                'gnd_stitch_connected_pads':gnd_links,
                'receiver_gnd_via_mm':[188.95,66.5],
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
        (HERE/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'south':south,'route_length':result['north_route']['length_mm'],
                          'cap_gap':geometry['post_launch_min_cap_full_gap_mm'],
                          'usb_gap':geometry['full_route_min_usb_gap_mm'],
                          'native_gap':gap['minimum_effective_shape_copper_gap_mm'],
                          'drc':[len(old_drc['violations']),len(new_drc['violations'])]},sort_keys=True))

if __name__=='__main__':main()
