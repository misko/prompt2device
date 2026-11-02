#!/usr/bin/python3
"""Read-only native power/return/preservation snapshot; no acceptance claim."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import pcbnew as p
from author_power_jack import SOURCE, BASE, nodes

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def mmpt(point): return [p.ToMM(v) for v in point]
def blocks(text,kind):
    return [text[a:b].strip() for a,b in nodes(text)
            if text[a:b].startswith('\t('+kind+' ') or text[a:b].startswith('\t('+kind+'\n')]
def native(path):
    b=p.LoadBoard(str(path))
    footprints={f.GetReference():{'uuid':f.m_Uuid.AsString(),'xy_mm':mmpt(f.GetPosition()),
        'angle_deg':f.GetOrientationDegrees(),'pads':{a.GetNumber():{
        'uuid':a.m_Uuid.AsString(),'net':a.GetNetname(),'xy_mm':mmpt(a.GetPosition()),
        'size_mm':mmpt(a.GetSize()),'drill_mm':mmpt(a.GetDrillSize()),
        'shape':a.GetShape(),'attribute':a.GetAttribute()} for a in f.Pads()}}
        for f in b.GetFootprints()}
    tracks={t.m_Uuid.AsString():{'net':t.GetNetname(), 'layer':b.GetLayerName(t.GetLayer()),
        'start_mm':mmpt(t.GetStart()),'end_mm':mmpt(t.GetEnd()),
        'via':isinstance(t,p.PCB_VIA),
        'width_mm':None if isinstance(t,p.PCB_VIA) else p.ToMM(t.GetWidth()),
        'length_mm':0 if isinstance(t,p.PCB_VIA) else p.ToMM(t.GetLength())}
        for t in b.GetTracks()}
    zones={}
    for z in b.Zones():
        if not z.GetNetname(): continue
        layer=z.GetLayer();poly=z.GetFilledPolysList(layer)
        row={'net':z.GetNetname(),'layer':b.GetLayerName(layer),
            'area_mm2':p.ToMM(p.ToMM(z.GetFilledArea())),
            'polygon_areas_mm2':[p.ToMM(p.ToMM(poly.COutline(i).Area())) for i in range(poly.OutlineCount())],
            'outline_mm':[mmpt(z.GetCornerPosition(i)) for i in range(z.GetNumCorners())],
            'connection_mode':z.GetPadConnection(),'thermal_spoke_mm':p.ToMM(z.GetThermalReliefSpokeWidth()),
            'thermal_gap_mm':p.ToMM(z.GetThermalReliefGap())}
        if z.GetNetname()=='/FUSED12':
            rect=p.SHAPE_POLY_SET();rect.NewOutline()
            for x,y in [(186,16.9),(199,16.9),(199,22.5),(186,22.5)]:rect.Append(p.FromMM(x),p.FromMM(y))
            clipped=p.SHAPE_POLY_SET();clipped.BooleanIntersection(poly,rect)
            row['D3_adjacent_region_rectangle_mm']=[186,16.9,199,22.5]
            row['D3_adjacent_region_filled_area_mm2']=p.ToMM(p.ToMM(clipped.Area()))
        if z.GetNetname()=='/GND' and layer in (p.In1_Cu,p.In2_Cu):
            a=footprints['J1']['pads']['2']['xy_mm'];samples=[]
            for angle in (45,135,225,315):
                for radius in (1.05,1.6,2):
                    xy=[a[0]+radius*math.cos(math.radians(angle)),a[1]+radius*math.sin(math.radians(angle))]
                    samples.append({'angle_deg':angle,'radius_mm':radius,
                        'in_same_filled_ground_polygon':poly.Contains(p.VECTOR2I(*(p.FromMM(v) for v in xy)))})
            row['J1_GND_thermal_and_escape_samples']=samples
        zones[z.m_Uuid.AsString()]=row
    return {'footprints':footprints,'tracks':tracks,'zones':zones}

def main():
    arg=argparse.ArgumentParser();arg.add_argument('candidate');a=arg.parse_args()
    out=BASE/a.candidate; dest=out/'native/pcb/carrier/carrier.kicad_pcb'
    source=SOURCE/'carrier.kicad_pcb'
    old=native(source);new=native(dest)
    s=source.read_text();d=dest.read_text()
    def fp(text):return {re.search(r'\(property "Reference" "([^"]+)"',v)[1]:v for v in blocks(text,'footprint')}
    f0=fp(s);f1=fp(d)
    t0=old['tracks'];t1=new['tracks'];shared=set(t0)&set(t1)
    evidence={'scope':'Author engineering evidence, not independent or manufacturing acceptance',
        'source_sha256':sha(source),'native_sha256':sha(dest),
        'preservation':{'footprints_source':len(f0),'footprints_candidate':len(f1),
            'changed_footprints':[k for k in f0 if f0[k]!=f1[k]],
            'protected_raw_nodes_equal':{kind:sorted(blocks(s,kind))==sorted(blocks(d,kind))
                for kind in ('via','setup','layers','gr_line','gr_arc','gr_rect','gr_poly')},
            'common_tracks':len(shared),'changed_common_tracks':[k for k in shared if t0[k]!=t1[k]],
            'changed_adjacent_resources': [str(f.relative_to(SOURCE)) for f in SOURCE.rglob('*')
                if f.is_file() and f.name!='carrier.kicad_pcb' and sha(f)!=sha(dest.parent/f.relative_to(SOURCE))]},
        'J1_before':old['footprints']['J1'],'J1_after':new['footprints']['J1'],
        'removed_tracks':{k:t0[k] for k in set(t0)-set(t1)},
        'added_tracks':{k:t1[k] for k in set(t1)-set(t0)},
        'zones_before':old['zones'],'zones_after':new['zones'],
        'power_trace_estimate':{}}
    for net in ('/VIN12','/FUSED12'):
        lengths=[sum(v['length_mm'] for v in state['tracks'].values() if v['net']==net) for state in (old,new)]
        # Native F.Cu specifies35um. rho at20C; warm sensitivity, not ampacity approval.
        resistances=[.01724*length/1000/(.8*.035) for length in lengths]
        evidence['power_trace_estimate'][net]={'total_authored_length_mm_before_after':lengths,
            'all_route_widths_mm':sorted({v['width_mm'] for v in new['tracks'].values() if v['net']==net}),
            'R_20C_ohm_before_after':resistances,
            'R_100C_ohm_before_after':[r*(1+.00393*80) for r in resistances],
            'at_680mA_100C_new_drop_V':.68*resistances[1]*(1+.00393*80),
            'at_1A_100C_new_loss_W':resistances[1]*(1+.00393*80),
            'limitation':'FUSED total includes redundant cooling branch; ignores beneficial zone parallel copper. No contact, fuse, diode or stack tolerance estimate; not IPC ampacity qualification.'}
    (out/'native-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({'preservation':evidence['preservation'],'power':evidence['power_trace_estimate']},indent=2))

if __name__=='__main__':main()
