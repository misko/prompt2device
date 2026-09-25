#!/usr/bin/env python3
"""One source-generated TPS26625 channel-8 support and local-return trial."""
from __future__ import annotations
import hashlib,json,math,shutil,subprocess,sys,tempfile
from pathlib import Path
import yaml
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
HERE=Path(__file__).resolve().parent
PREV=HERE.parent/'2026-09-25-ti-adc8n-coupled-south-route-sol'
sys.path.insert(0,str(PREV));import probe as prior
ROOT=HERE.parents[4];PROJECT=ROOT/'projects/crow-usb-carrier-v1'
GROUP={
 'U_SPOKE8':[190.0,47.5,0],
 'C_SPOKE_IN8':[189.75,44.0,0],
 'C_SPOKE_OUT8':[194.6,46.7,0],
 'R_SPOKE_ILIM8':[191.0,51.0,180],
 'C_SPOKE_DVDT8':[193.9,49.3,180],
 'R_SPOKE_UVLO8':[186.5,46.8,0],
}
LOCAL_RETURN_PATHS={
 'gnd_cin_to_u6':('GND',[(190.7,44.0),(192.5,44.0),(192.5,48.5),(191.4,48.5)]),
 'gnd_cout_to_join':('GND',[(195.55,46.7),(195.55,48.5),(192.5,48.5)]),
 'rtn_rilim_to_ep11':('SPOKE_RTN8',[(190.175,51.0),(190.175,49.8),(190.0,49.625),(190.0,47.5)]),
 'rtn_dvdt_to_ep11':('SPOKE_RTN8',[(193.42,49.3),(190.0,49.3)]),
 'rtn_u3_to_ep11':('SPOKE_RTN8',[(188.6,47.5),(190.0,47.5)]),
 'rtn_u5_to_ep11':('SPOKE_RTN8',[(188.6,48.5),(189.0,48.5),(190.0,47.5)]),
}
PAIRS={
 'IN_to_CIN':('1','C_SPOKE_IN8','1','N12V_PROTECTED'),
 'GND_to_CIN':('6','C_SPOKE_IN8','2','GND'),
 'OUT_to_COUT':('10','C_SPOKE_OUT8','1','N12V_POD8'),
 'GND_to_COUT':('6','C_SPOKE_OUT8','2','GND'),
 'ILIM_to_RILIM':('7','R_SPOKE_ILIM8','1','SPOKE_ILIM8'),
 'RTN5_to_RILIM':('5','R_SPOKE_ILIM8','2','SPOKE_RTN8'),
 'EP11_to_RILIM':('11','R_SPOKE_ILIM8','2','SPOKE_RTN8'),
 'DVDT_to_CDVDT':('8','C_SPOKE_DVDT8','1','SPOKE_DVDT8'),
 'RTN5_to_CDVDT':('5','C_SPOKE_DVDT8','2','SPOKE_RTN8'),
 'EP11_to_CDVDT':('11','C_SPOKE_DVDT8','2','SPOKE_RTN8'),
 'UVLO_to_RUVLO':('2','R_SPOKE_UVLO8','2','SPOKE_UVLO8'),
 'IN_to_RUVLO':('1','R_SPOKE_UVLO8','1','N12V_PROTECTED'),
}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def copper_gap(a,b):
    x=a.GetEffectiveShape(p.F_Cu);y=b.GetEffectiveShape(p.F_Cu)
    if x.Collide(y,0):return 0.0
    lo,hi=0,30000000
    if not x.Collide(y,hi):raise RuntimeError('pad separation >30mm')
    while hi-lo>1000:
        m=(lo+hi)//2
        if x.Collide(y,m):hi=m
        else:lo=m
    return round(hi/1e6,6)

def add_local_returns(board):
    for netname,vertices in LOCAL_RETURN_PATHS.values():
      net=board.FindNet(netname)
      if net is None:raise RuntimeError(f'net missing: {netname}')
      for a,b in zip(vertices,vertices[1:]):
        t=p.PCB_TRACK(board);t.SetStart(prior.base.pt(*a));t.SetEnd(prior.base.pt(*b))
        t.SetWidth(p.FromMM(.20));t.SetLayer(p.F_Cu);t.SetNet(net);board.Add(t)
    via=p.PCB_VIA(board);via.SetPosition(prior.base.pt(195.55,48.5))
    via.SetWidth(p.FromMM(.60));via.SetDrill(p.FromMM(.30))
    via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu)
    via.SetNet(board.FindNet('GND'));board.Add(via)

def generate(root):
    found={'source':sha(prior.SOURCE),'netlist':sha(prior.NETLIST),
           'poses':sha(prior.POSES),'southwest_board':sha(prior.base.SOURCE),
           'generic_generator':sha(prior.GEN)}
    if found!=prior.EXPECTED:raise RuntimeError(f'input hash drift: {found}')
    cfg=yaml.safe_load(prior.SOURCE.read_text());poses=json.loads(prior.POSES.read_text())
    if len(poses['move_union'])!=45:raise RuntimeError('placement union drift')
    cfg['placement']['post_anchors']['Q_PRE']=[46,107.15,0]
    cfg['placement']['post_anchors'].update(poses['move_union'])
    cfg['placement']['post_anchors'].update({
        'C_ADC_AC8N1':[198,59.65,0], 'R_B8P':[193.75,60.8,0], **GROUP})
    root.mkdir();(root/'03_src').mkdir();(root/'04_kicad').mkdir();(root/'06_build').mkdir()
    (root/'02_parts').symlink_to(prior.TI/'02_parts',target_is_directory=True)
    (root/'03_src/lib').symlink_to(prior.TI/'03_src/lib',target_is_directory=True)
    (root/'03_src/rules').symlink_to(prior.TI/'03_src/rules',target_is_directory=True)
    (root/'06_build/netlists').symlink_to(prior.TI/'06_build/netlists',target_is_directory=True)
    config=root/'03_src/floorplan.yaml';config.write_text(yaml.safe_dump(cfg,sort_keys=False))
    board=root/'04_kicad/crow_carrier.kicad_pcb'
    q=subprocess.run(['python3',str(prior.GEN),str(config),'-o',str(board)],capture_output=True,text=True)
    if q.returncode:raise RuntimeError(f'producer failed: {q.stdout[-800:]} {q.stderr[-800:]}')
    return board,found

def main():
  with tempfile.TemporaryDirectory(prefix='crow-tps26625-group-') as tmp:
    root=Path(tmp);source,inputs=generate(root/'source')
    baseline=p.LoadBoard(str(PREV/'candidate_filled_profile.kicad_pcb'))
    new=p.LoadBoard(str(source))
    old_ledger=prior.base.footprint_ledger(baseline)
    new_ledger=prior.base.footprint_ledger(new)
    if set(old_ledger)!=set(new_ledger) or len(new_ledger)!=569:raise RuntimeError('footprint denominator drift')
    changed=sorted(r for r in new_ledger if old_ledger[r]!=new_ledger[r])
    if changed!=sorted(GROUP):raise RuntimeError(f'pose/pad delta refs {changed}')
    for ref,pose in GROUP.items():
      if new_ledger[ref]['pose']!=[float(v) for v in pose]:raise RuntimeError(f'{ref} pose drift')
      before=old_ledger[ref];after=new_ledger[ref]
      turn=(after['pose'][2]-before['pose'][2])%360
      if turn not in (0,180):raise RuntimeError(f'{ref} unsupported pad transform {turn}')
      sign=1 if turn==0 else -1
      if len(before['pads'])!=len(after['pads']) or any(a[:4]!=b[:4] or
           abs(after['pose'][0]+sign*(a[4]-before['pose'][0])-b[4])>1e-6 or
           abs(after['pose'][1]+sign*(a[5]-before['pose'][1])-b[5])>1e-6
           for a,b in zip(before['pads'],after['pads'])):
        raise RuntimeError(f'{ref} native pad identity drift')
    fixed=yaml.safe_load((PROJECT/'03_src/rules/p1_corridor_requirements.yaml').read_text())['p1_fixed_refs']
    if len(fixed)!=27 or any(old_ledger[r]!=new_ledger[r] for r in fixed):
      raise RuntimeError('P1 fixed pose drift')
    fs={f.GetReference():f for f in new.GetFootprints()}
    source_cfg=yaml.safe_load(prior.SOURCE.read_text())
    regions=source_cfg['placement']['regions']
    owner=regions['analog_ch8']
    owners={ref:[row['region'] for row in source_cfg['placement']['patterns']
                 if ref in row.get('match',[])] for ref in GROUP}
    if any(value!=['analog_ch8'] for value in owners.values()):
      raise RuntimeError(f'source owner pattern drift: {owners}')
    boxes={r:prior.full_box(f) for r,f in fs.items()}
    intersections={r:sorted(q for q,b in boxes.items() if q!=r and prior.box_gap(boxes[r],b)<1e-6)
                   for r in GROUP}
    out={r:b for r,b in boxes.items() if r in GROUP and
         (b[0]<owner[0] or b[1]<owner[1] or b[2]>owner[2] or b[3]>owner[3])}
    foreign_group={r:sorted(name for name,region in regions.items() if name!='analog_ch8'
                            and prior.box_gap(boxes[r],region)<1e-6) for r in GROUP}
    if out or any(intersections.values()) or any(foreign_group.values()):
      raise RuntimeError(f'owner/collision: {out} {intersections} {foreign_group}')
    contacts={}
    for name,(upin,ref,pin,net) in PAIRS.items():
      u=prior.base.pad(new,'U_SPOKE8',upin);q=prior.base.pad(new,ref,pin)
      if u.GetNetname()!=net or q.GetNetname()!=net:raise RuntimeError(f'{name} net drift')
      contacts[name]={'a':f'U_SPOKE8.{upin}','b':f'{ref}.{pin}','net':net,
                      'direct_native_copper_gap_mm':copper_gap(u,q)}
    if prior.base.pad(new,'U_SPOKE8','6').GetNetname()!='GND' or any(
      prior.base.pad(new,'U_SPOKE8',pin).GetNetname()!='SPOKE_RTN8' for pin in ('3','5','11')):
      raise RuntimeError('system GND / isolated RTN identity failure')
    if any(contacts[k]['direct_native_copper_gap_mm']>2.5 for k in ('IN_to_CIN','ILIM_to_RILIM')):
      raise RuntimeError('existing IN/ILIM project ceiling failure')
    prior.add_candidate(new)
    add_local_returns(new)
    shape=prior.shape_screen(new)
    bare=root/'routed.kicad_pcb';p.SaveBoard(str(bare),new)
    prof=root/'profile';prof.mkdir()
    _,base_drc,base_via,_=prior.base.profile('baseline',prior.base.SOURCE,prof)
    routed,drc,via,_=prior.base.profile('group',bare,prof)
    new_issues=set(map(prior.base.issue,drc['violations']));old_issues=set(map(prior.base.issue,base_drc['violations']))
    native=p.LoadBoard(str(routed));ret=prior.return_screen(native)
    if prior.base.footprint_ledger(native)!=new_ledger:raise RuntimeError('profile pose/pad drift')
    route=prior.shape_screen(native)
    native.BuildConnectivity();conn=native.GetConnectivity()
    linked={q.GetParentFootprint().GetReference()+'.'+q.GetNumber()
            for q in conn.GetConnectedItems(prior.base.pad(native,'C_ADC_AC8N1','2'))
            if isinstance(q,p.PAD)}
    if 'C_ADC_CM8N.1' not in linked:raise RuntimeError('ADC8N local link missing')
    local_links={}
    for ref,pin in (('U_SPOKE8','6'),('U_SPOKE8','11')):
      q=prior.base.pad(native,ref,pin)
      local_links[f'{ref}.{pin}']=sorted(x.GetParentFootprint().GetReference()+'.'+x.GetNumber()
        for x in conn.GetConnectedItems(q) if isinstance(x,p.PAD))
    needed_gnd={'U_SPOKE8.6','C_SPOKE_IN8.2','C_SPOKE_OUT8.2'}
    needed_rtn={'U_SPOKE8.3','U_SPOKE8.5','U_SPOKE8.11',
                'R_SPOKE_ILIM8.2','C_SPOKE_DVDT8.2'}
    if not needed_gnd.issubset(local_links['U_SPOKE8.6']) or not needed_rtn.issubset(
       local_links['U_SPOKE8.11']) or set(local_links['U_SPOKE8.6']) & needed_rtn or set(
       local_links['U_SPOKE8.11']) & needed_gnd:
      raise RuntimeError('local GND/RTN native connectivity or distinction failure')
    zone=[z for z in native.Zones() if z.GetNetname()=='GND' and
          p.In1_Cu in z.GetLayerSet().Seq()]
    if len(zone)!=1 or not zone[0].IsFilled():raise RuntimeError('In1 GND fill absent')
    fill=zone[0].GetFilledPolysList(p.In1_Cu)
    gnd_pts=[xy for net,v in LOCAL_RETURN_PATHS.values() if net=='GND' for xy in v]
    common=set(range(fill.OutlineCount()))
    for xy in gnd_pts:
      q=prior.base.pt(*xy)
      if not fill.Contains(q):raise RuntimeError(f'GND return point outside In1 fill: {xy}')
      common&={i for i in range(fill.OutlineCount()) if fill.Outline(i).PointInside(q)}
    if not common:raise RuntimeError('GND paths not over one In1 polygon')
    tracks=[t for t in native.GetTracks() if t.GetNetname()=='ADC8N']
    foreign={name:round(min(prior.north.distance_to_shape(t,prior.rect(box)) for t in tracks),6)
             for name,box in regions.items() if name!='analog_ch8'}
    if min(foreign.values())<.2-1e-6:raise RuntimeError('foreign planning region margin')
    shutil.copy2(routed,HERE/'candidate_filled_profile.kicad_pcb')
    receipt={'schema':1,'status':'RESEARCH_PARTIAL_RETURN_TRIAL','input_sha256':inputs,
             'source_generated_unfilled_board_sha256_observation':sha(source),
             'source_pose_delta_refs':changed,'group_poses_mm':GROUP,'footprint_count':569,
             'fixed_27_preserved':True,'native_pad_identities_preserved':True,
             'group_full_envelopes_mm':{r:boxes[r] for r in GROUP},
             'group_full_envelope_collisions':intersections,'contacts':contacts,
             'source_owner_pattern_by_ref':owners,
             'group_foreign_source_region_intersections':foreign_group,
             'existing_project_direct_gap_ceilings_mm':{'IN_to_CIN':2.5,'ILIM_to_RILIM':2.5},
             'gnd_rtn_distinct':True,'local_return_paths':LOCAL_RETURN_PATHS,
             'local_return_path_lengths_mm':{name:round(sum(math.dist(a,b) for a,b in zip(v,v[1:])),6)
                  for name,(_,v) in LOCAL_RETURN_PATHS.items()},
             'gnd_local_stitch_center_mm':[195.55,48.5],
             'gnd_local_return_same_filled_in1_polygon_outlines':sorted(common),
             'adc8n_route_geometry':route,'foreign_region_route_gaps_mm':foreign,
             'filled_return':ret,'native_connected_adc8n_pads':sorted(linked),
             'native_local_return_connected_pads':local_links,
             'local_spoke_rtn_copper_island_proven':False,
             'native_profile':{'violations':[len(base_drc['violations']),len(drc['violations'])],
                'unconnected':[len(base_drc['unconnected_items']),len(drc['unconnected_items'])],
                'added_issue_identities':len(new_issues-old_issues),
                'removed_issue_identities':len(old_issues-new_issues),
                'via_process_fails':[base_via.get('fails'),via.get('fails')]},
             'filled_board_sha256_observation':sha(HERE/'candidate_filled_profile.kicad_pcb')}
    (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'worst':sorted((v['direct_native_copper_gap_mm'],k) for k,v in contacts.items())[-5:],
           'profile':receipt['native_profile'],'source':receipt['source_generated_unfilled_board_sha256_observation']},sort_keys=True))
if __name__=='__main__':main()
