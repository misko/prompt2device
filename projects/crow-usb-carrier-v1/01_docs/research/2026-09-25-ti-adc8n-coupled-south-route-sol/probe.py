#!/usr/bin/env python3
"""One source-generated coupled ADC8 cap/spoke/VMID resistor placement and local route."""
from __future__ import annotations
import hashlib,json,math,shutil,subprocess,sys,tempfile
from pathlib import Path
import yaml
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
PROJECT=ROOT/'projects/crow-usb-carrier-v1'
PREV=HERE.parent/'2026-09-25-ti-adc8n-local-route-sol'
NORTH=HERE.parent/'2026-09-25-ti-adc8n-cap-clear-sol'
sys.path.insert(0,str(PREV));import route_probe as base
sys.path.insert(0,str(NORTH));import north_probe as north
TI=Path('/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project')
POSES=PROJECT/'01_docs/research/2026-09-25-ti-integrated-placement-sol/expected_poses.json'
GEN=ROOT/'skills/kicad-pcb/scripts/generate_board_generic.py'
SOURCE=TI/'03_src/floorplan.yaml'
NETLIST=TI/'06_build/netlists/crow_carrier.net'
EXPECTED={'source':'0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868',
          'netlist':'a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd',
          'poses':'76ba7ace1275fe1a8d6bc69d452037672519d70a21b8b02fff67f8c7d8a647bb',
          'southwest_board':'0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93',
          'generic_generator':'8a5fa1d48d80138458601a097ab6260565841510a498e44cb9c5773652215b3c'}
CAP=[195.205,57.905,200.795,61.395]
USB=[195.0,62.0,220.0,82.0]
COORDS=[(199.8,59.65),(197.75,61.7),(194.7,61.7),(194.7,62.8),
        (191.7,65.8),(187.9,65.8),(187.9,66.1),(187.5,66.5),(187.52,66.5)]
LAUNCH_GND=(199.8,57.2)
RECEIVE_GND=(188.95,66.5)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rect(box):return p.SHAPE_RECT(base.pt(box[0],box[1]),base.pt(box[2],box[3]))
def full_box(fp):
    body=fp.GetBoundingBox(False,False)
    box=[base.mm(v) for v in (body.GetLeft(),body.GetTop(),body.GetRight(),body.GetBottom())]
    for layer in (p.F_CrtYd,p.B_CrtYd):
        courtyard=fp.GetCourtyard(layer)
        if courtyard.OutlineCount():
            bb=courtyard.BBox();other=[base.mm(v) for v in
                                         (bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom())]
            box=[min(box[0],other[0]),min(box[1],other[1]),
                 max(box[2],other[2]),max(box[3],other[3])]
    return box
def box_gap(a,b):
    return math.hypot(max(a[0]-b[2],b[0]-a[2],0),max(a[1]-b[3],b[1]-a[3],0))

def generate(root):
    root.mkdir(parents=True)
    found={'source':sha(SOURCE),'netlist':sha(NETLIST),'poses':sha(POSES),
           'southwest_board':sha(base.SOURCE),'generic_generator':sha(GEN)}
    for name,want in EXPECTED.items():
        if want is not None and found[name]!=want:raise RuntimeError(f'{name} SHA drift: {found[name]}')
    cfg=yaml.safe_load(SOURCE.read_text())
    expected=json.loads(POSES.read_text())
    if len(expected['move_union'])!=45 or expected['move_union']['C_ADC_AC8N1']!=[198.2,60.25,0.0]:
        raise RuntimeError('integrated placement denominator drift')
    if cfg['placement']['post_anchors']['Q_PRE']!=[46.0,106.85,0]:
        raise RuntimeError('frozen TI Q_PRE anchor drift')
    cfg['placement']['post_anchors']['Q_PRE']=[46.0,107.15,0]
    cfg['placement']['post_anchors'].update(expected['move_union'])
    cfg['placement']['post_anchors'].update({
        'C_ADC_AC8N1':[198.0,59.65,0],
        'U_SPOKE8':[189.6,63.0,0],
        'R_B8P':[193.75,60.8,0],
    })
    (root/'03_src').mkdir();(root/'04_kicad').mkdir();(root/'06_build').mkdir()
    (root/'02_parts').symlink_to(TI/'02_parts',target_is_directory=True)
    (root/'03_src/lib').symlink_to(TI/'03_src/lib',target_is_directory=True)
    (root/'03_src/rules').symlink_to(TI/'03_src/rules',target_is_directory=True)
    (root/'06_build/netlists').symlink_to(TI/'06_build/netlists',target_is_directory=True)
    config=root/'03_src/floorplan.yaml';config.write_text(yaml.safe_dump(cfg,sort_keys=False))
    board=root/'04_kicad/crow_carrier.kicad_pcb'
    q=subprocess.run(['python3',str(GEN),str(config),'-o',str(board)],text=True,capture_output=True)
    if q.returncode:raise RuntimeError(f'governed native producer failed: {q.stdout[-800:]} {q.stderr[-800:]}')
    return board,found

def add_candidate(board):
    adc=board.FindNet('ADC8N');gnd=board.FindNet('GND')
    if adc is None or gnd is None:raise RuntimeError('native nets missing')
    for a,b in zip(COORDS,COORDS[1:]):
        t=p.PCB_TRACK(board);t.SetStart(base.pt(*a));t.SetEnd(base.pt(*b))
        t.SetLayer(p.F_Cu);t.SetWidth(p.FromMM(.20));t.SetNet(adc);board.Add(t)
    for xy,end in ((LAUNCH_GND,(198.1,56.5)),(RECEIVE_GND,(188.48,66.5))):
        v=p.PCB_VIA(board);v.SetPosition(base.pt(*xy));v.SetWidth(p.FromMM(.60))
        v.SetDrill(p.FromMM(.30));v.SetViaType(p.VIATYPE_THROUGH)
        v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(gnd);board.Add(v)
        t=p.PCB_TRACK(board);t.SetStart(base.pt(*xy));t.SetEnd(base.pt(*end))
        t.SetLayer(p.F_Cu);t.SetWidth(p.FromMM(.20));t.SetNet(gnd);board.Add(t)

def shape_screen(board):
    tracks=[t for t in board.GetTracks() if t.GetNetname()=='ADC8N']
    if len(tracks)!=len(COORDS)-1:raise RuntimeError('ADC8N route segment denominator drift')
    cap=rect(CAP);usb=rect(USB)
    launch=[t for t in tracks if (base.mm(t.GetStart().x),base.mm(t.GetStart().y))==COORDS[0]]
    if len(launch)!=1 or not launch[0].GetEffectiveShape(p.F_Cu).Collide(cap,0):
        raise RuntimeError('named own-pad launch absent')
    cap_gaps=[];usb_gaps=[]
    for t in tracks:
        if t.GetEffectiveShape(p.F_Cu).Collide(usb,0):raise RuntimeError('signal copper enters USB region')
        usb_gaps.append(north.distance_to_shape(t,usb))
        if t is launch[0]:continue
        if t.GetEffectiveShape(p.F_Cu).Collide(cap,0):raise RuntimeError('post-launch signal copper enters cap')
        cap_gaps.append(north.distance_to_shape(t,cap))
    hits=north.native_envelope_hits(board)
    if sorted(hits)!=['C_ADC_AC8N1','C_ADC_CM8N']:
        raise RuntimeError(f'other native body/courtyard crossing: {sorted(hits)}')
    nearest=sorted((min(north.distance_to_shape(t,rect(full_box(fp))) for t in tracks),
                    fp.GetReference()) for fp in board.GetFootprints()
                   if fp.GetReference() not in ('C_ADC_AC8N1','C_ADC_CM8N'))[:5]
    if nearest[0][0]<.20-1e-6:raise RuntimeError(f'other full-envelope margin <0.20: {nearest[0]}')
    if min(usb_gaps)<.20-1e-6:raise RuntimeError(f'USB region margin <0.20: {min(usb_gaps)}')
    return {'post_launch_cap_full_gap_mm':round(min(cap_gaps),6),
            'whole_route_usb_region_gap_mm':round(min(usb_gaps),6),
            'full_footprint_envelope_hits':hits,
            'nearest_other_full_envelope_gaps_mm':[
                {'ref':ref,'gap_mm':round(gap,6)} for gap,ref in nearest]}

def return_screen(board):
    zones=[z for z in board.Zones() if z.GetNetname()=='GND' and p.In1_Cu in z.GetLayerSet().Seq()]
    if len(zones)!=1 or not zones[0].IsFilled():raise RuntimeError('filled In1 GND zone absent')
    filled=zones[0].GetFilledPolysList(p.In1_Cu)
    common=set(range(filled.OutlineCount()))
    for x,y in COORDS+[LAUNCH_GND,RECEIVE_GND,(199.0,53.0)]:
        q=base.pt(x,y)
        if not filled.Contains(q):raise RuntimeError(f'In1 return absent at {(x,y)}')
        common&={i for i in range(filled.OutlineCount()) if filled.Outline(i).PointInside(q)}
    if not common:raise RuntimeError('route/stitches not in one filled polygon')
    uncovered=[]
    for a,b in zip(COORDS,COORDS[1:]):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        nx,ny=-dy/length*.1,dx/length*.1
        ribbon=p.SHAPE_POLY_SET();ribbon.NewOutline()
        for x,y in ((a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),
                    (b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)):
            ribbon.Append(base.pt(x,y))
        ribbon.BooleanSubtract(filled);uncovered.append(round(ribbon.Area()/1e12,9))
    if any(uncovered):raise RuntimeError(f'In1 return gap: {uncovered}')
    return {'same_filled_polygon_outlines':sorted(common),
            'uncovered_0p20mm_ribbon_area_mm2_by_segment':uncovered}

def main():
    with tempfile.TemporaryDirectory(prefix='crow-adc8n-capshift-') as folder:
        temp=Path(folder);shifted,source_hashes=generate(temp/'source')
        old=p.LoadBoard(str(base.SOURCE));new=p.LoadBoard(str(shifted))
        old_ledger=base.footprint_ledger(old);new_ledger=base.footprint_ledger(new)
        if set(old_ledger)!=set(new_ledger) or len(new_ledger)!=569:
            raise RuntimeError('footprint set drift')
        changed=sorted(ref for ref in old_ledger if old_ledger[ref]!=new_ledger[ref])
        wanted={'C_ADC_AC8N1':([198.0,59.65,0.0],(0,-.4)),
                'R_B8P':([193.75,60.8,0.0],(0,-.2)),
                'U_SPOKE8':([189.6,63.0,0.0],(-.4,0))}
        if changed!=sorted(wanted) or any(new_ledger[r]['pose']!=pose for r,(pose,_) in wanted.items()):
            raise RuntimeError(f'unexpected generated pose/pad change: {changed}')
        for ref,(_,delta) in wanted.items():
            before=old_ledger[ref]['pads'];after=new_ledger[ref]['pads']
            if len(before)!=len(after) or any(a[:4]!=b[:4] or
                    abs((a[4]+delta[0])-b[4])>1e-6 or
                    abs((a[5]+delta[1])-b[5])>1e-6 for a,b in zip(before,after)):
                raise RuntimeError(f'{ref} pad identity or translation drift')
        def distance(board,first,second):
            a=base.pad(board,*first).GetPosition();b=base.pad(board,*second).GetPosition()
            return math.hypot(base.mm(a.x-b.x),base.mm(a.y-b.y))
        related={
            'cap_iso8n_to_u_iso8_6':(('C_ADC_AC8N1','1'),('U_ISO8','6')),
            'cap_adc8n_to_cm8n_1':(('C_ADC_AC8N1','2'),('C_ADC_CM8N','1')),
            'spoke_in1_to_c_in1':(('U_SPOKE8','1'),('C_SPOKE_IN8','1')),
            'spoke_gnd6_to_c_in2':(('U_SPOKE8','6'),('C_SPOKE_IN8','2')),
            'spoke_out10_to_c_out1':(('U_SPOKE8','10'),('C_SPOKE_OUT8','1')),
            'spoke_gnd6_to_c_out2':(('U_SPOKE8','6'),('C_SPOKE_OUT8','2')),
            'spoke_ilim7_to_r_ilim1':(('U_SPOKE8','7'),('R_SPOKE_ILIM8','1')),
            'spoke_rtn5_to_r_ilim2':(('U_SPOKE8','5'),('R_SPOKE_ILIM8','2')),
            'spoke_dvdt8_to_c_dvdt1':(('U_SPOKE8','8'),('C_SPOKE_DVDT8','1')),
            'spoke_rtn5_to_c_dvdt2':(('U_SPOKE8','5'),('C_SPOKE_DVDT8','2')),
            'spoke_uvlo2_to_r_uvlo2':(('U_SPOKE8','2'),('R_SPOKE_UVLO8','2')),
            'bias_p_to_c_a8p2':(('R_B8P','1'),('C_A8P','2')),
            'vmid_to_r_b8n2':(('R_B8P','2'),('R_B8N','2')),
        }
        locality={name:[round(distance(board,a,b),6) for board in (old,new)]
                  for name,(a,b) in related.items()}
        fps={fp.GetReference():fp for fp in new.GetFootprints()}
        owner=yaml.safe_load(SOURCE.read_text())['placement']['regions']['analog_ch8']
        moved_envelopes={ref:full_box(fps[ref]) for ref in changed}
        if any(box[0]<owner[0] or box[1]<owner[1] or box[2]>owner[2] or box[3]>owner[3]
               for box in moved_envelopes.values()):
            raise RuntimeError(f'moved full envelope escapes analog_ch8: {moved_envelopes}')
        moved_hits={ref:sorted(other for other,fp in fps.items() if other!=ref and
                               box_gap(box,full_box(fp))<1e-6)
                    for ref,box in moved_envelopes.items()}
        if any(moved_hits.values()):raise RuntimeError(f'moved full-envelope collision: {moved_hits}')
        cap_box=full_box(fps['C_ADC_AC8N1'])
        if any(abs(a-b)>1e-6 for a,b in zip(cap_box,CAP)):
            raise RuntimeError(f'native shifted cap full envelope drift: {cap_box}')
        cap_hits=sorted(ref for ref,fp in fps.items() if ref!='C_ADC_AC8N1' and
                        box_gap(cap_box,full_box(fp))<1e-6)
        if cap_hits:raise RuntimeError(f'shifted cap full-envelope collision: {cap_hits}')
        support_gaps={ref:round(box_gap(cap_box,full_box(fps[ref])),6)
                      for ref in ('C_A8P','R_B8P','C_FILTER8N1')}
        fixed=yaml.safe_load((PROJECT/'03_src/rules/p1_corridor_requirements.yaml').read_text())['p1_fixed_refs']
        if len(fixed)!=27 or any(old_ledger[r]!=new_ledger[r] for r in fixed):
            raise RuntimeError('27 P1 fixed poses/pads drift')
        if base.pad(new,'C_ADC_AC8N1','2').GetNetname()!='ADC8N':
            raise RuntimeError('cap ADC8N pad drift')
        source_board_hash=sha(shifted)
        add_candidate(new)
        shape_screen(new)
        bare=temp/'routed.kicad_pcb';p.SaveBoard(str(bare),new)
        prof=temp/'profile';prof.mkdir()
        original,old_drc,old_via,_=base.profile('old',base.SOURCE,prof)
        moved,move_drc,move_via,_=base.profile('shifted',shifted,prof)
        routed,route_drc,route_via,_=base.profile('routed',bare,prof)
        checks=[(old_drc,old_via),(move_drc,move_via),(route_drc,route_via)]
        if any(via.get('fails') for _,via in checks):raise RuntimeError('V-PROCESS failure')
        issues=[set(map(base.issue,report['violations'])) for report,_ in checks]
        if issues[1]-issues[0] or issues[2]-issues[1]:
            raise RuntimeError(f'new DRC identities: placement {issues[1]-issues[0]}, route {issues[2]-issues[1]}')
        native=p.LoadBoard(str(routed))
        if base.footprint_ledger(native)!=new_ledger:raise RuntimeError('routed pose/pad drift')
        shape=shape_screen(native);ret=return_screen(native);gap=base.route_clearance(native)
        tracks=[t for t in native.GetTracks() if t.GetNetname()=='ADC8N']
        regions=yaml.safe_load(SOURCE.read_text())['placement']['regions']
        region_gaps={name:round(min(north.distance_to_shape(t,rect(box)) for t in tracks),6)
                     for name,box in regions.items() if name!='analog_ch8'}
        if min(region_gaps.values())<.20-1e-6:
            raise RuntimeError(f'foreign source region margin <0.20: {region_gaps}')
        if gap['minimum_effective_shape_copper_gap_mm']<.15:raise RuntimeError('subrule copper gap')
        native.BuildConnectivity();conn=native.GetConnectivity()
        linked={x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
                for x in conn.GetConnectedItems(base.pad(native,'C_ADC_AC8N1','2')) if isinstance(x,p.PAD)}
        if 'C_ADC_CM8N.1' not in linked:raise RuntimeError('ADC8N exact pad link absent')
        gnd_links=[]
        for xy,wanted in ((LAUNCH_GND,'C_FILTER8N1.2'),(RECEIVE_GND,'C_ADC_CM8N.2')):
            via=next(t for t in native.GetTracks() if isinstance(t,p.PCB_VIA) and
                     t.GetNetname()=='GND' and abs(base.mm(t.GetPosition().x)-xy[0])<.001 and
                     abs(base.mm(t.GetPosition().y)-xy[1])<.001)
            pads={x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
                  for x in conn.GetConnectedItems(via) if isinstance(x,p.PAD)}
            if wanted not in pads:raise RuntimeError(f'GND stitch missing named pad {wanted}')
            gnd_links.append({'via_center_mm':list(xy),'named_gnd_pad':wanted})
        areas=sorted(z.GetZoneName() for z in native.Zones() if z.GetIsRuleArea() and
                     z.GetZoneName().startswith('tmux4827_b2_pofv_'))
        if areas!=[f'tmux4827_b2_pofv_U_ISO{i}' for i in range(1,9)]:
            raise RuntimeError(f'POFV semantic area identity drift: {areas}')
        shutil.copy2(routed,HERE/'candidate_filled_profile.kicad_pcb')
        length=sum(math.dist(a,b) for a,b in zip(COORDS,COORDS[1:]))
        result={'schema':1,'status':'RESEARCH_COUPLED_PLACEMENT_ONLY',
                'input_sha256':source_hashes,'source_generated_unfilled_board_sha256_observation':source_board_hash,
                'source_pose_delta_refs':changed,'fixed_27_preserved':True,
                'footprint_count':len(new_ledger),'related_pad_center_locality_old_new':locality,
                'shifted_cap_other_full_envelope_hits':cap_hits,
                'moved_full_envelopes_mm':moved_envelopes,
                'moved_full_envelope_hits':moved_hits,
                'shifted_cap_support_full_envelope_gaps_mm':support_gaps,
                'route':{'vertices_mm':COORDS,'width_mm':.20,'layer':'F.Cu',
                 'length_mm':round(length,6),'segments':len(COORDS)-1},
                'shifted_cap_full_envelope_mm':CAP,'geometry':shape,
                'foreign_source_region_route_gaps_mm':region_gaps,
                'minimum_native_different_net_copper_gap':gap,'filled_return':ret,
                'native_connected_adc8n_pads':sorted(linked),
                'gnd_stitches_mm':[list(LAUNCH_GND),list(RECEIVE_GND)],
                'gnd_stitch_connected_pads':gnd_links,'pofv_rule_area_names':areas,
                'profile':{'violations':[len(x['violations']) for x,_ in checks],
                           'unconnected':[len(x['unconnected_items']) for x,_ in checks],
                           'added_violation_identities_old_to_shifted':len(issues[1]-issues[0]),
                           'added_violation_identities_shifted_to_routed':len(issues[2]-issues[1]),
                           'removed_violation_identities_old_to_shifted':len(issues[0]-issues[1]),
                           'removed_violation_identities_shifted_to_routed':len(issues[1]-issues[2]),
                           'via_process_fails':[via.get('fails') for _,via in checks]},
                'filled_candidate_board_sha256_observation':sha(HERE/'candidate_filled_profile.kicad_pcb')}
        (HERE/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'source_board':source_board_hash,'route_length':result['route']['length_mm'],
                          'cap_gap':shape['post_launch_cap_full_gap_mm'],
                          'usb_gap':shape['whole_route_usb_region_gap_mm'],
                          'native_gap':gap['minimum_effective_shape_copper_gap_mm'],
                          'drc':result['profile']['violations'],'opens':result['profile']['unconnected']},sort_keys=True))

if __name__=='__main__':main()
