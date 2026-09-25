#!/usr/bin/env python3
"""One 1.20mm N12V_PROTECTED input-bypass loop closure on the pinned TI board."""
from __future__ import annotations
import hashlib,importlib.util,json,math,shutil,sys,tempfile
from pathlib import Path
import yaml
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
HERE=Path(__file__).resolve().parent
PREV=HERE.parent/'2026-09-25-ti-tps26625-return-trial-sol'
spec=importlib.util.spec_from_file_location('return_trial_probe',PREV/'probe.py')
trial=importlib.util.module_from_spec(spec);spec.loader.exec_module(trial)
base=trial.prior.base
PINNED_PREV_BOARD_SHA='9f5a3b11a5c6cf42e9979bc5f4d74eb202af4f79fbe6f0bc9dd85e576d0b9ede'
SUPPLY_START=(188.3,45.9)
SUPPLY_END=(188.3,44.0)
SUPPLY_WIDTH_MM=1.2
GND_PATH=trial.LOCAL_RETURN_PATHS['gnd_cin_to_u6'][1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def tracks(board):
    items=[]
    for t in board.GetTracks():
      ends=tuple(sorted(((base.mm(t.GetStart().x),base.mm(t.GetStart().y)),
                         (base.mm(t.GetEnd().x),base.mm(t.GetEnd().y)))))
      drill=round(base.mm(t.GetDrillValue()),6) if isinstance(t,p.PCB_VIA) else None
      width=t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth()
      items.append((t.GetNetname(),t.GetLayerName(),round(base.mm(width),6),drill,ends))
    return sorted(items,key=repr)
def add_supply(board):
    net=board.FindNet('N12V_PROTECTED')
    if net is None:raise RuntimeError('N12V_PROTECTED absent')
    t=p.PCB_TRACK(board);t.SetStart(base.pt(*SUPPLY_START));t.SetEnd(base.pt(*SUPPLY_END))
    t.SetWidth(p.FromMM(SUPPLY_WIDTH_MM));t.SetLayer(p.F_Cu);t.SetNet(net);board.Add(t)
    return t
def polygon_area(vertices):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(vertices,vertices[1:]+vertices[:1])))/2
def copper_gap(shape_a,shape_b):
    if shape_a.Collide(shape_b,0):return 0.0
    lo,hi=0,p.FromMM(2)
    if not shape_a.Collide(shape_b,hi):return None
    while hi-lo>100:
      mid=(lo+hi)//2
      if shape_a.Collide(shape_b,mid):hi=mid
      else:lo=mid
    return round(base.mm(hi),6)

def main():
  previous=PREV/'candidate_filled_profile.kicad_pcb'
  if sha(previous)!=PINNED_PREV_BOARD_SHA:
    raise RuntimeError(f'previous reviewed board SHA drift: {sha(previous)}')
  with tempfile.TemporaryDirectory(prefix='crow-tps26625-input-') as tmp:
    root=Path(tmp);source,inputs=trial.generate(root/'source')
    nets=yaml.safe_load((trial.prior.TI/'03_src/rules/nets.yaml').read_text())
    trunk=nets['classes']['INPUT_TRUNK']
    if 'N12V_PROTECTED' not in trunk['nets'] or trunk['min_width']!='1.2mm':
      raise RuntimeError('source INPUT_TRUNK width assignment drift')
    board=p.LoadBoard(str(source))
    trial.prior.add_candidate(board);trial.add_local_returns(board)
    prior_native=p.LoadBoard(str(previous))
    if base.footprint_ledger(board)!=base.footprint_ledger(prior_native) or tracks(board)!=tracks(prior_native):
      raise RuntimeError('reconstructed source-generated partial-return baseline drift')
    before=root/'before.kicad_pcb';p.SaveBoard(str(before),board)
    t=add_supply(board)
    after=root/'after.kicad_pcb';p.SaveBoard(str(after),board)
    prof=root/'profile';prof.mkdir()
    _,before_drc,before_via,_=base.profile('before',before,prof)
    output,after_drc,after_via,_=base.profile('after',after,prof)
    old=set(map(base.issue,before_drc['violations']))
    new=set(map(base.issue,after_drc['violations']))
    if new-old or old-new or any(v.get('fails') for v in (before_via,after_via)):
      raise RuntimeError(f'native issue/V-PROCESS delta: +{new-old} -{old-new}')
    native=p.LoadBoard(str(output))
    if base.footprint_ledger(native)!=base.footprint_ledger(prior_native):
      raise RuntimeError('native footprint/pad pose drift')
    native.BuildConnectivity();conn=native.GetConnectivity()
    linked={q.GetParentFootprint().GetReference()+'.'+q.GetNumber()
            for q in conn.GetConnectedItems(base.pad(native,'U_SPOKE8','1')) if isinstance(q,p.PAD)}
    gnd={q.GetParentFootprint().GetReference()+'.'+q.GetNumber()
         for q in conn.GetConnectedItems(base.pad(native,'U_SPOKE8','6')) if isinstance(q,p.PAD)}
    rtn={q.GetParentFootprint().GetReference()+'.'+q.GetNumber()
         for q in conn.GetConnectedItems(base.pad(native,'U_SPOKE8','11')) if isinstance(q,p.PAD)}
    u=base.pad(native,'U_SPOKE8','1').GetPosition()
    ci=base.pad(native,'C_SPOKE_IN8','1').GetPosition()
    cg=base.pad(native,'C_SPOKE_IN8','2').GetPosition()
    ug=base.pad(native,'U_SPOKE8','6').GetPosition()
    points=[(base.mm(u.x),base.mm(u.y)),SUPPLY_START,SUPPLY_END,
            (base.mm(ci.x),base.mm(ci.y)),(base.mm(cg.x),base.mm(cg.y))]+GND_PATH[1:]
    if points[-1]!=(base.mm(ug.x),base.mm(ug.y)):
      raise RuntimeError('GND path endpoint drift')
    if ('C_SPOKE_IN8.1' not in linked or 'C_SPOKE_IN8.2' not in gnd or
        'C_SPOKE_IN8.2' in rtn or 'U_SPOKE8.11' in gnd):
      raise RuntimeError('input/GND/RTN loop connectivity failure')
    zone=[z for z in native.Zones() if z.GetNetname()=='GND' and p.In1_Cu in z.GetLayerSet().Seq()]
    if len(zone)!=1 or not zone[0].IsFilled():raise RuntimeError('filled In1 GND absent')
    fill=zone[0].GetFilledPolysList(p.In1_Cu)
    common=set(range(fill.OutlineCount()))
    for xy in GND_PATH:
      q=base.pt(*xy)
      if not fill.Contains(q):raise RuntimeError(f'GND return outside fill {xy}')
      common&={i for i in range(fill.OutlineCount()) if fill.Outline(i).PointInside(q)}
    if not common:raise RuntimeError('GND return not over one polygon')
    if (base.pad(native,'U_SPOKE8','1').GetNetname()!='N12V_PROTECTED' or
        base.pad(native,'C_SPOKE_IN8','1').GetNetname()!='N12V_PROTECTED'):
      raise RuntimeError('supply endpoint net drift')
    supply=next(x for x in native.GetTracks() if x.GetNetname()=='N12V_PROTECTED' and
                x.GetLayer()==p.F_Cu and abs(base.mm(x.GetWidth())-SUPPLY_WIDTH_MM)<1e-6)
    supply_shape=supply.GetEffectiveShape(p.F_Cu)
    neighbor_gaps={f'{ref}.{pin}':copper_gap(supply_shape,
       base.pad(native,ref,pin).GetEffectiveShape(p.F_Cu))
       for ref,pin in (('U_SPOKE8','2'),('U_SPOKE8','11'),
                       ('R_SPOKE_UVLO8','2'),('C_SPOKE_IN8','2'))}
    if min(neighbor_gaps.values())<.2-1e-6:
      raise RuntimeError(f'INPUT_TRUNK neighbor copper clearance: {neighbor_gaps}')
    pad_center_supply_mm=sum(math.dist(a,b) for a,b in zip(points[:4],points[1:4]))
    result={'schema':1,'status':'INPUT_LOOP_NATIVE_TRIAL',
      'prior_reviewed_board_sha256':PINNED_PREV_BOARD_SHA,'source_input_sha256':inputs,
      'source_generated_unfilled_board_sha256_observation':sha(source),
      'footprint_count':len(base.footprint_ledger(native)),'fixed_27_preserved':True,
      'supply_track':{'net':'N12V_PROTECTED','layer':'F.Cu','width_mm':SUPPLY_WIDTH_MM,
                      'start_mm':SUPPLY_START,'end_mm':SUPPLY_END,
                      'native_track_centerline_length_mm':round(math.dist(SUPPLY_START,SUPPLY_END),6),
                      'pad_center_path_surrogate_mm':round(pad_center_supply_mm,6),
                      'nearby_foreign_pad_effective_shape_gaps_mm':neighbor_gaps},
      'input_loop':{'polygon_vertices_mm':points,
                    'projected_centerline_area_mm2':round(polygon_area(points),6),
                    'gnd_return_track_length_mm':round(sum(math.dist(a,b)
                      for a,b in zip(GND_PATH,GND_PATH[1:])),6),
                    'closure_chords':['C_SPOKE_IN8.1→C_SPOKE_IN8.2 internal capacitor',
                                      'U_SPOKE8.6→U_SPOKE8.1 internal device'],
                    'same_filled_in1_gnd_outline_ids':sorted(common)},
      'native_connected_supply_pads':sorted(linked),
      'native_connected_gnd_pads':sorted(gnd),
      'native_connected_rtn_pads':sorted(rtn),
      'native_profile':{'violations':[len(before_drc['violations']),len(after_drc['violations'])],
          'unconnected':[len(before_drc['unconnected_items']),len(after_drc['unconnected_items'])],
          'added_issue_identities':len(new-old),'removed_issue_identities':len(old-new),
          'new_issue_types':sorted({x[0] for x in new-old}),
          'via_process_fails':[before_via.get('fails'),after_via.get('fails')]},
      'input_trunk_source_min_width_mm':1.2,
      'filled_board_sha256_observation':sha(output)}
    shutil.copy2(output,HERE/'candidate_filled_profile.kicad_pcb')
    (HERE/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'area':result['input_loop']['projected_centerline_area_mm2'],
          'supply_connected':'C_SPOKE_IN8.1' in linked,'profile':result['native_profile']},sort_keys=True))
if __name__=='__main__':main()
