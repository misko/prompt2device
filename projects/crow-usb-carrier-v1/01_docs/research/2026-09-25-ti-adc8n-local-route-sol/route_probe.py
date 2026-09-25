#!/usr/bin/env python3
"""Isolated ADC8N F.Cu local route candidate and filled-profile comparison."""
from __future__ import annotations
import hashlib, heapq, json, math, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
import yaml

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
PROJECT=ROOT/'projects/crow-usb-carrier-v1'
SOURCE=PROJECT/'01_docs/research/2026-09-25-ti-adc8-cap-integrated-replay-sol/candidate.kicad_pcb'
PROFILE=HERE/'profile'
FROZEN_TI=Path('/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project')
GEN=ROOT/'skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py'
VIA_CHECK=ROOT/'skills/jlcpcb-fab/scripts/via_process_check.py'
ASSEMBLY=FROZEN_TI/'03_src/rules/assembly.yaml'
EXPECTED={'board':'0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93',
          'pro':'7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094',
          'dru':'00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a',
          'assembly':'76071a9190ae3923a7a1b4b709a5b3160ce1f06b8d8fb22292ce1cea23664cf3',
          'producer':'b3906f63e07e9f04ada58e757f4095989f6933eca98d93b0f1165e91064529b7'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def mm(v):return p.ToMM(v)
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def run(args):
    q=subprocess.run(args,text=True,capture_output=True)
    if q.returncode:raise RuntimeError(f'{args}: {q.stdout[-800:]} {q.stderr[-800:]}')
    return q.stdout

def pad(board,ref,num):
    fp=next(f for f in board.GetFootprints() if f.GetReference()==ref)
    return next(q for q in fp.Pads() if q.GetNumber()==num)

def astar(board):
    # 0.10-mm grid, conservative 0.25-mm pad-bbox expansion = half of the
    # 0.20-mm track plus the project's 0.15-mm ADC signal clearance.
    obstacles=[]
    for fp in board.GetFootprints():
        for q in fp.Pads():
            if q.GetNetname()=='ADC8N':continue
            bb=q.GetBoundingBox(); box=[mm(v) for v in (bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom())]
            if box[2]<183 or box[0]>203 or box[3]<54 or box[1]>71:continue
            obstacles.append((fp.GetReference()+'.'+q.GetNumber(),
                              [box[0]-.26,box[1]-.26,box[2]+.26,box[3]+.26]))
    start=(1998,600);goal=(1875,665);step=.1
    def free(x,y):
        a,b=x*step,y*step
        return 183<=a<=203 and 54<=b<=71 and all(not(v[0]<=a<=v[2] and v[1]<=b<=v[3]) for _,v in obstacles)
    dirs=[(dx,dy) for dx in(-1,0,1) for dy in(-1,0,1) if dx or dy]
    if not free(*start) or not free(*goal):raise RuntimeError('endpoint grid point blocked')
    source=(start,None); heap=[(0.0,0.0,source)]; cost={source:0.0};prev={}
    terminal=None
    while heap:
        _,g,(xy,dr)=heapq.heappop(heap)
        state=(xy,dr)
        if g>cost[state]+1e-8:continue
        if xy==goal:terminal=state;break
        for nd in dirs:
            nxt=(xy[0]+nd[0],xy[1]+nd[1])
            # Check diagonal swept endpoints and the corner's orthogonal
            # neighbors; this is deliberately more conservative than native.
            if not free(*nxt) or (nd[0] and nd[1] and
                                  (not free(xy[0]+nd[0],xy[1]) or not free(xy[0],xy[1]+nd[1]))):continue
            edge=math.hypot(*nd)+(.40 if dr is not None and nd!=dr else 0)
            ng=g+edge; ns=(nxt,nd)
            if ng<cost.get(ns,1e99)-1e-8:
                cost[ns]=ng;prev[ns]=state
                heapq.heappush(heap,(ng+math.hypot(nxt[0]-goal[0],nxt[1]-goal[1]),ng,ns))
    if terminal is None:raise RuntimeError('conservative grid path absent')
    seq=[terminal]
    while seq[-1]!=source:seq.append(prev[seq[-1]])
    seq=list(reversed(seq)); vertices=[seq[0][0]]
    for i in range(1,len(seq)-1):
        if seq[i][1]!=seq[i+1][1]:vertices.append(seq[i][0])
    vertices.append(seq[-1][0])
    coords=[(199.8,60.05)]+[(round(x*step,3),round(y*step,3)) for x,y in vertices]+[(187.52,66.5)]
    coords=[v for i,v in enumerate(coords) if i==0 or v!=coords[i-1]]
    return coords,obstacles

def add_route(board,coords):
    net=board.FindNet('ADC8N')
    if net is None:raise RuntimeError('ADC8N net missing')
    for a,b in zip(coords,coords[1:]):
        if a==b:continue
        track=p.PCB_TRACK(board);track.SetStart(pt(*a));track.SetEnd(pt(*b))
        track.SetLayer(p.F_Cu);track.SetWidth(p.FromMM(.20));track.SetNet(net);board.Add(track)
    gnd=board.FindNet('GND')
    via=p.PCB_VIA(board);via.SetPosition(pt(199.8,58.0));via.SetWidth(p.FromMM(.60))
    via.SetDrill(p.FromMM(.30));via.SetViaType(p.VIATYPE_THROUGH)
    via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(gnd);board.Add(via)
    neck=p.PCB_TRACK(board);neck.SetStart(pt(199.8,58.0));neck.SetEnd(pt(198.1,56.5))
    neck.SetLayer(p.F_Cu);neck.SetWidth(p.FromMM(.20));neck.SetNet(gnd);board.Add(neck)
    via2=p.PCB_VIA(board);via2.SetPosition(pt(188.95,66.5));via2.SetWidth(p.FromMM(.60))
    via2.SetDrill(p.FromMM(.30));via2.SetViaType(p.VIATYPE_THROUGH)
    via2.SetLayerPair(p.F_Cu,p.B_Cu);via2.SetNet(gnd);board.Add(via2)
    neck2=p.PCB_TRACK(board);neck2.SetStart(pt(188.48,66.5));neck2.SetEnd(pt(188.95,66.5))
    neck2.SetLayer(p.F_Cu);neck2.SetWidth(p.FromMM(.20));neck2.SetNet(gnd);board.Add(neck2)

def profile(name,board_path,temp):
    dest=temp/name;dest.mkdir();out=dest/'crow_carrier.kicad_pcb'
    shutil.copy2(board_path,out)
    for ext in ('pro','dru'):
        shutil.copy2(PROFILE/f'crow_carrier.kicad_{ext}',dest/f'crow_carrier.kicad_{ext}')
    run(['python3',str(GEN),str(out),'--assembly',str(ASSEMBLY)])
    via_json=dest/'via.json'
    run(['python3',str(VIA_CHECK),str(out),'--assembly',str(ASSEMBLY),'--json',str(via_json)])
    drc=dest/'drc.json'
    run(['kicad-cli','pcb','drc','--format','json','--refill-zones','--save-board','--output',str(drc),str(out)])
    data=json.loads(drc.read_text())
    return out,data,json.loads(via_json.read_text()),drc

def issue(v):return(v['type'],v['description'],tuple(sorted(i['uuid'] for i in v['items'])))
def footprint_ledger(board):
    return {fp.GetReference():{
        'pose':[mm(fp.GetPosition().x),mm(fp.GetPosition().y),fp.GetOrientationDegrees()],
        'pads':sorted((q.GetNumber(),q.GetNetname(),q.GetLayerSet().FmtBin(),
                       int(q.GetShape()),mm(q.GetPosition().x),mm(q.GetPosition().y))
                      for q in fp.Pads())} for fp in board.GetFootprints()}

def route_clearance(board):
    routes=[t for t in board.GetTracks() if t.GetNetname()=='ADC8N']
    other=[]
    for fp in board.GetFootprints():
        for q in fp.Pads():
            if q.GetNetname()!='ADC8N' and q.IsOnLayer(p.F_Cu):
                other.append((fp.GetReference()+'.'+q.GetNumber(),q))
    for t in board.GetTracks():
        if t.GetNetname()!='ADC8N' and t.IsOnLayer(p.F_Cu):
            xy=t.GetPosition() if isinstance(t,p.PCB_VIA) else t.GetStart()
            other.append((('via' if isinstance(t,p.PCB_VIA) else 'track')+' '+t.GetNetname()+
                          f'@{mm(xy.x):.3f},{mm(xy.y):.3f}',t))
    best=(float('inf'),None)
    for track in routes:
        bb=track.GetBoundingBox();shape=track.GetEffectiveShape(p.F_Cu)
        for name,item in other:
            ib=item.GetBoundingBox()
            if mm(max(bb.GetLeft()-ib.GetRight(),ib.GetLeft()-bb.GetRight(),
                      bb.GetTop()-ib.GetBottom(),ib.GetTop()-bb.GetBottom()))>2:continue
            target=item.GetEffectiveShape(p.F_Cu)
            if target is None:continue
            lo,hi=0,p.FromMM(2)
            if not shape.Collide(target,hi):continue
            for _ in range(22):
                mid=(lo+hi)//2
                if shape.Collide(target,mid):hi=mid
                else:lo=mid
            if hi<best[0]:
                best=(hi,{'obstacle':name,'segment_mm':[[mm(track.GetStart().x),mm(track.GetStart().y)],
                                                   [mm(track.GetEnd().x),mm(track.GetEnd().y)]]})
    return {'minimum_effective_shape_copper_gap_mm':round(mm(best[0]),6),**best[1]}

def return_coverage(board,coords):
    zones=[z for z in board.Zones() if z.GetNetname()=='GND' and p.In1_Cu in z.GetLayerSet().Seq()]
    if len(zones)!=1 or not zones[0].IsFilled():raise RuntimeError('In1 GND fill absent')
    filled=zones[0].GetFilledPolysList(p.In1_Cu)
    locations=coords+[(199.8,58.0),(188.95,66.5),(199.0,53.0)]
    common=set(range(filled.OutlineCount()))
    for x,y in locations:
        point=pt(x,y)
        if not filled.Contains(point):raise RuntimeError(f'GND fill absent at {x},{y}')
        common&={i for i in range(filled.OutlineCount()) if filled.Outline(i).PointInside(point)}
    if not common:raise RuntimeError('route and GND stitches not in one filled polygon outline')
    uncovered=[]
    for a,c in zip(coords,coords[1:]):
        dx,dy=c[0]-a[0],c[1]-a[1];length=math.hypot(dx,dy)
        nx,ny=-dy/length*.1,dx/length*.1
        ribbon=p.SHAPE_POLY_SET();ribbon.NewOutline()
        for x,y in ((a[0]+nx,a[1]+ny),(c[0]+nx,c[1]+ny),
                    (c[0]-nx,c[1]-ny),(a[0]-nx,a[1]-ny)):
            ribbon.Append(pt(x,y))
        ribbon.BooleanSubtract(filled)
        uncovered.append(round(ribbon.Area()/1e12,9))
    if any(uncovered):raise RuntimeError(f'In1 GND gap under route: {uncovered}')
    return {'filled_polygon_count':filled.OutlineCount(),
            'common_filled_outline_indices':sorted(common),
            'uncovered_0p20mm_route_ribbon_area_mm2_by_segment':uncovered}

def main():
    files={'board':SOURCE,'pro':PROFILE/'crow_carrier.kicad_pro',
           'dru':PROFILE/'crow_carrier.kicad_dru','assembly':ASSEMBLY,'producer':GEN}
    actual={k:sha(v) for k,v in files.items()}
    if actual!=EXPECTED:raise RuntimeError(f'profile input SHA drift: {actual}')
    if sha(PROFILE/'assembly.yaml')!=actual['assembly']:
        raise RuntimeError('archived TI assembly snapshot drift')
    b=p.LoadBoard(str(SOURCE)); f={q.GetReference():q for q in b.GetFootprints()}
    if len(f)!=569:raise RuntimeError('footprint denominator drift')
    before=footprint_ledger(b)
    fixed=yaml.safe_load((PROJECT/'03_src/rules/p1_corridor_requirements.yaml').read_text())['p1_fixed_refs']
    if len(fixed)!=27:raise RuntimeError('fixed denominator drift')
    s=pad(b,'C_ADC_AC8N1','2');t=pad(b,'C_ADC_CM8N','1')
    if s.GetNetname()!='ADC8N' or t.GetNetname()!='ADC8N':raise RuntimeError('net drift')
    coords,obstacles=astar(b)
    add_route(b,coords)
    bare=HERE/'candidate_unfilled.kicad_pcb';p.SaveBoard(str(bare),b)
    length=sum(math.dist(a,c) for a,c in zip(coords,coords[1:]))
    with tempfile.TemporaryDirectory(prefix='crow-adc8n-') as folder:
        temp=Path(folder)
        old,old_drc,old_via,old_drc_path=profile('baseline',SOURCE,temp)
        new,new_drc,new_via,new_drc_path=profile('routed',bare,temp)
        shutil.copy2(old_drc_path,HERE/'baseline_drc.json')
        shutil.copy2(new_drc_path,HERE/'candidate_drc.json')
        old_issues=set(map(issue,old_drc['violations']));new_issues=set(map(issue,new_drc['violations']))
        filled=HERE/'candidate_filled_profile.kicad_pcb';shutil.copy2(new,filled)
        native=p.LoadBoard(str(filled))
        areas=sorted(z.GetZoneName() for z in native.Zones() if z.GetIsRuleArea() and
                     z.GetZoneName().startswith('tmux4827_b2_pofv_'))
        if areas!=[f'tmux4827_b2_pofv_U_ISO{i}' for i in range(1,9)]:
            raise RuntimeError(f'POFV rule-area identity drift: {areas}')
        after=footprint_ledger(native)
        if before!=after:raise RuntimeError('footprint pose/pad identity drift')
        gz=[z for z in native.Zones() if z.GetNetname()=='GND' and p.In1_Cu in z.GetLayerSet().Seq()]
        if new_issues-old_issues or old_via.get('fails') or new_via.get('fails'):
            raise RuntimeError('new DRC or via-process failure')
        route_gap=route_clearance(native)
        if route_gap['minimum_effective_shape_copper_gap_mm']<.15:
            raise RuntimeError('ADC8N route copper gap below 0.15 mm')
        coverage=return_coverage(native,coords)
        conn=native.GetConnectivity();native.BuildConnectivity()
        linked={x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
                for x in conn.GetConnectedItems(pad(native,'C_ADC_AC8N1','2')) if isinstance(x,p.PAD)}
        if 'C_ADC_CM8N.1' not in linked:raise RuntimeError('ADC8N native pads not connected')
        stitch_links=[]
        for xy,wanted in [((199.8,58.0),'C_FILTER8N1.2'),((188.95,66.5),'C_ADC_CM8N.2')]:
            via=next(t for t in native.GetTracks() if isinstance(t,p.PCB_VIA) and
                     t.GetNetname()=='GND' and abs(mm(t.GetPosition().x)-xy[0])<.001 and
                     abs(mm(t.GetPosition().y)-xy[1])<.001)
            pads={x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
                  for x in conn.GetConnectedItems(via) if isinstance(x,p.PAD)}
            if wanted not in pads:raise RuntimeError(f'GND neck not connected: {wanted}')
            stitch_links.append({'via_center_mm':list(xy),'named_gnd_pad':wanted,
                                 'connected_gnd_pad_count':len(pads)})
        def open_key(row):return tuple(sorted(item['uuid'] for item in row['items']))
        old_open={open_key(x) for x in old_drc['unconnected_items']}
        new_open={open_key(x) for x in new_drc['unconnected_items']}
        adc8n_reported=any('[ADC8N]' in str(row) for row in old_drc['unconnected_items']+new_drc['unconnected_items'])
        receipt={'schema':1,'status':'RESEARCH_ONLY','input_sha256':actual,
                 'endpoint_pads':['C_ADC_AC8N1.2','C_ADC_CM8N.1'],
                 'route':{'layer':'F.Cu','width_mm':.20,'vertices_mm':coords,'length_mm':round(length,6),
                          'segments':len(coords)-1},
                 'gnd_stitch':{'center_mm':[199.8,58.0],'diameter_mm':.60,'drill_mm':.30,
                               'fcu_neck_to':'C_FILTER8N1.2','fcu_neck_length_mm':round(math.dist((199.8,58.0),(198.1,56.5)),6),
                               'receiver_center_mm':[188.95,66.5],
                               'receiver_neck_to':'C_ADC_CM8N.2','receiver_neck_length_mm':.47},
                 'baseline':{'violations':len(old_drc['violations']),'unconnected':len(old_drc['unconnected_items'])},
                 'routed':{'violations':len(new_drc['violations']),'unconnected':len(new_drc['unconnected_items'])},
                 'unconnected_pair_identity_delta':{'added':len(new_open-old_open),
                                                     'removed':len(old_open-new_open),
                                                     'adc8n_reported_in_either':adc8n_reported},
                 'issue_delta':{'added':[list(k) for k in sorted(new_issues-old_issues)],
                                'removed':[list(k) for k in sorted(old_issues-new_issues)]},
                 'via_process':{'baseline_fails':old_via.get('fails'),
                                'candidate_fails':new_via.get('fails')},
                 'pofv_rule_area_names':areas,
                 'gnd_in1_zone_count':len(gz),'gnd_in1_zone_filled':[z.IsFilled() for z in gz],
                 'filled_return_geometry':coverage,'adc8n_route_clearance':route_gap,
                 'gnd_stitch_native_connectivity':stitch_links,
                 'adc8n_native_connected_pads':sorted(linked),
                 'bare_board_sha256_observation':sha(bare),'filled_board_sha256_observation':sha(filled),
                 'fixed_27_pose_unchanged':all(before[x]==after[x] for x in fixed),
                 'original_569_footprint_pose_pad_ledgers_unchanged':before==after,
                 'grid_obstacle_count':len(obstacles)}
        (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'length_mm':receipt['route']['length_mm'],'segments':receipt['route']['segments'],
                          'drc':[receipt['baseline'],receipt['routed']],
                          'added':len(new_issues-old_issues),'removed':len(old_issues-new_issues),
                          'zone_filled':receipt['gnd_in1_zone_filled']},sort_keys=True))

if __name__=='__main__':main()
