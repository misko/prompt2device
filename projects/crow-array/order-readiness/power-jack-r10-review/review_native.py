"""Independent read-only source comparison and disposable native check staging."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
import pcbnew as pcb

old, new, out = map(Path, sys.argv[1:])
out.mkdir(parents=True, exist_ok=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def xy(v): return [round(pcb.ToMM(v.x), 6), round(pcb.ToMM(v.y), 6)]
def footprints(board):
    result = {}
    for foot in board.GetFootprints():
        result[foot.GetReference()] = {
            'uuid': foot.m_Uuid.AsString(), 'value': foot.GetValue(),
            'library': str(foot.GetFPID().GetLibItemName()),
            'position': xy(foot.GetPosition()), 'angle': foot.GetOrientationDegrees(),
            'layer': foot.GetLayer(),
            'pads': sorted([{
                'number': p.GetNumber(), 'net': p.GetNetname(),
                'position': xy(p.GetPosition()), 'local_position': xy(p.GetFPRelativePosition()),
                'size': xy(p.GetSize()), 'drill': xy(p.GetDrillSize()),
                'shape': int(p.GetShape()), 'attribute': int(p.GetAttribute()),
                'layers': p.GetLayerSet().FmtHex(),
            } for p in foot.Pads()], key=lambda p:(p['number'], p['local_position']))}
    return result
def tracks(board):
    return {t.m_Uuid.AsString(): {
        'kind': type(t).__name__, 'net': t.GetNetname(), 'layer': t.GetLayer(),
        'start': xy(t.GetStart()), 'end': xy(t.GetEnd()),
        'width': pcb.ToMM(t.GetWidth(pcb.F_Cu) if isinstance(t,pcb.PCB_VIA) else t.GetWidth()),
    } for t in board.GetTracks()}
ob, nb = pcb.LoadBoard(str(old)), pcb.LoadBoard(str(new))
of, nf = footprints(ob), footprints(nb)
ot, nt = tracks(ob), tracks(nb)
differences = {r:{'old':of.get(r), 'new':nf.get(r)} for r in set(of)|set(nf) if of.get(r)!=nf.get(r)}
changed_tracks={u:{'old':ot.get(u), 'new':nt.get(u)} for u in set(ot)|set(nt) if ot.get(u)!=nt.get(u)}
assert set(differences)=={'J1'}, differences.keys()
oj,nj=of['J1'],nf['J1']
assert {k:v for k,v in oj.items() if k not in ('position','angle','pads')} == {k:v for k,v in nj.items() if k not in ('position','angle','pads')}
assert [{k:v for k,v in p.items() if k!='position'} for p in oj['pads']]==[{k:v for k,v in p.items() if k!='position'} for p in nj['pads']]
assert nj['position'][0]==188.0 and nj['position'][1] in (15.2,14.7) and nj['angle']==180.0
jy=nj['position'][1]
assert [(p['number'],p['net'],p['position']) for p in nj['pads']]==[
    ('1','/VIN12',[188.0,jy]),('2','/GND',[188.0,round(jy-6,6)]),
    ('3','unconnected-(J1-SLEEVE_SWITCH-Pad3)',[183.3,round(jy-3,6)])]
assert pcb.ToMM(ob.GetDesignSettings().GetBoardThickness())==pcb.ToMM(nb.GetDesignSettings().GetBoardThickness())==1.6
def edges(board):
    return sorted([{'shape':int(d.GetShape()),'start':xy(d.GetStart()),
        'mid':xy(d.GetArcMid()) if d.GetShape()==pcb.SHAPE_T_ARC else None,
        'end':xy(d.GetEnd()),'width':d.GetWidth()}
        for d in board.GetDrawings() if d.GetLayer()==pcb.Edge_Cuts],key=str)
assert edges(ob)==edges(nb)
def zones(board):
    result=[]
    for z in board.Zones():
        poly=z.Outline()
        contours=[]
        for i in range(poly.OutlineCount()):
            line=poly.COutline(i)
            contours.append([xy(line.CPoint(k)) for k in range(line.PointCount())])
        result.append({'uuid':z.m_Uuid.AsString(),'net':z.GetNetname(),
            'layers':z.GetLayerSet().FmtHex(),'contours':contours})
    return sorted(result,key=str)
oz,nz=zones(ob),zones(nb)
zone_changes=[{'old':o,'new':n} for o,n in zip(oz,nz) if o!=n]
assert len(oz)==len(nz)
assert all(c['old']['net']==c['new']['net']=='/FUSED12' and
    c['old']['uuid']==c['new']['uuid'] and c['old']['layers']==c['new']['layers']
    for c in zone_changes)
subjects={str(old):sha(old),str(new):sha(new)}
companions={}
for ext in ('kicad_sch','kicad_pro'):
    op,np=old.with_suffix('.'+ext),new.with_suffix('.'+ext)
    assert op.read_bytes()==np.read_bytes(), ext
    companions[ext]={'old':sha(op),'new':sha(np),'byte_identical':True}
shutil.copytree(new.parent,out,dirs_exist_ok=True)
result={'subjects':subjects,'companions':companions,'footprint_count':len(of),
    'only_changed_footprint':'J1','footprint_differences':differences,
    'track_counts':{'old':len(ot),'new':len(nt)},'changed_tracks':changed_tracks,
    'board_thickness_mm':1.6,'outline_byte_geometry_unchanged':True,
    'zone_changes':zone_changes,'stage_acceptance':False}
(out/'source-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'footprints':len(of),'changed_footprints':list(differences),'changed_tracks':len(changed_tracks),'subjects':subjects},indent=2))
