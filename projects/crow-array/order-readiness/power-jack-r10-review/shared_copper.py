"""Independent source-bound zone contacts and local thermal-spreading audit."""
import hashlib,json,math,sys
from pathlib import Path
import pcbnew as pcb

old,new,out=map(Path,sys.argv[1:])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def vec(x,y):return pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y))
def rectangle(x0,y0,x1,y1):
    line=pcb.SHAPE_LINE_CHAIN()
    for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)):line.Append(vec(x,y))
    line.SetClosed(True)
    return pcb.SHAPE_POLY_SET(line)
def audit(path):
    b=pcb.LoadBoard(str(path));fs={f.GetReference():f for f in b.GetFootprints()}
    result={'sha256':sha(path),'zones':[],'power_pads':{}}
    for ref in ('J1','F1','D3','D1','C1','U10','D2','U3'):
        result['power_pads'][ref]=[{'pad':p.GetNumber(),'net':p.GetNetname(),
            'xy':[pcb.ToMM(p.GetPosition().x),pcb.ToMM(p.GetPosition().y)]}
            for p in fs[ref].Pads() if ref!='U3' or p.GetNetname() in ('/GND','/5V','/VSYS','/3V3')]
    for zone in b.Zones():
        net=zone.GetNetname()
        if net not in ('/GND','/12V','/FUSED12'):continue
        for layer in zone.GetLayerSet().Seq():
            poly=zone.GetFilledPolysList(layer)
            if not poly.OutlineCount():continue
            row={'uuid':zone.m_Uuid.AsString(),'net':net,'layer':b.GetLayerName(layer),
                'area_mm2':poly.Area()/1e12,'island_areas_mm2':[], 'pad_contacts':[],
                'D3_local_region_areas_mm2':{}}
            for i in range(poly.OutlineCount()):row['island_areas_mm2'].append(poly.COutline(i).Area()/1e12)
            for ref in ('J1','F1','D3','D1','C1','U10','D2'):
                for p in fs[ref].Pads():
                    if p.GetNetname()==net and p.IsOnLayer(layer) and poly.Collide(p.GetEffectiveShape(layer),0):
                        row['pad_contacts'].append(ref+'.'+p.GetNumber())
            if net=='/GND' and layer in (pcb.In1_Cu,pcb.In2_Cu):
                p2=next(p for p in fs['J1'].Pads() if p.GetNumber()=='2')
                cx,cy=pcb.ToMM(p2.GetPosition().x),pcb.ToMM(p2.GetPosition().y)
                row['J1_return_spoke_samples']=[{'r_mm':r,'angle_deg':angle,
                    'in_continuous_plane':poly.Collide(vec(cx+r*math.cos(math.radians(angle)),
                        cy+r*math.sin(math.radians(angle))),0)}
                    for r in (1.05,1.6,2.0) for angle in (45,135,225,315)]
                assert all(s['in_continuous_plane'] for s in row['J1_return_spoke_samples'])
            if net=='/FUSED12':
                for key,box in {'immediate_anode':[185,17.5,195,22.0],
                                'lower_lateral_spreading':[184,16.5,198,23],
                                'upper_spreading':[178,10,199,16.5]}.items():
                    crop=pcb.SHAPE_POLY_SET(poly);crop.BooleanIntersection(rectangle(*box))
                    row['D3_local_region_areas_mm2'][key]={'box':box,'area':crop.Area()/1e12}
                p2=next(p for p in fs['D3'].Pads() if p.GetNumber()=='2')
                row['D3_direct_island_areas_mm2']=[pcb.SHAPE_POLY_SET(poly.COutline(i)).Area()/1e12
                    for i in range(poly.OutlineCount()) if pcb.SHAPE_POLY_SET(poly.COutline(i)).Collide(p2.GetEffectiveShape(layer),0)]
            result['zones'].append(row)
    return result
def local_difference(box):
    shapes=[]
    for path in (old,new):
        b=pcb.LoadBoard(str(path));poly=pcb.SHAPE_POLY_SET()
        for z in b.Zones():
            if z.GetNetname()=='/FUSED12' and z.IsOnLayer(pcb.F_Cu):
                poly.BooleanAdd(z.GetFilledPolysList(pcb.F_Cu))
        poly.BooleanIntersection(rectangle(*box));shapes.append(poly)
    xor=pcb.SHAPE_POLY_SET(shapes[0]);xor.BooleanXor(shapes[1])
    return {'box':box,'old_area_mm2':shapes[0].Area()/1e12,
        'new_area_mm2':shapes[1].Area()/1e12,'xor_area_mm2':xor.Area()/1e12}
result={'old':audit(old),'new':audit(new),
    'D3_local_exact_copper_differences':[local_difference(box) for box in (
        [186,16.9,199,22.5],[185,17.5,195,22.0],[184,16.5,198,23])],
    'scope':'Connectivity and spreading geometry, not measured temperature or a theta-JA guarantee',
    'thermal_existing_model':{'whole_array_current_A':.68,'D3_drop_V':.75,'D3_loss_W':.51,
        'local_air_C':60,'neighbor_allocation_C':20,'theta_reference_K_per_W':110,
        'theta_sensitivity_K_per_W':130,'sensitivity_Tj_C':146.3,'Tj_limit_C':150,
        'theta_at150C_K_per_W':(150-80)/.51},
    'required_hardware_gate':'Full eight-pod hot-load, startup/inrush and local D2/D3/LMK temperature validation before deployment. No new fuse/current/ambient derating authority.'}
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:{'zones':len(v['zones']),'FUSED':[z for z in v['zones'] if z['net']=='/FUSED12']} for k,v in result.items() if k in ('old','new')},indent=2))
