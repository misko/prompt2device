"""Conservative drawing-bound affected-interface screen, not a stage receipt."""
import hashlib,itertools,json,math,shutil,sys
from pathlib import Path
import pcbnew as pcb

board_path,out=map(Path,sys.argv[1:])
external=Path('/home/mouse9911/gits/crow-first-run-5c10p-20261022/project')
assembly=external/'03_src/recovery/first-run-physical/assembly.json'
a=json.loads(assembly.read_text());b=pcb.LoadBoard(str(board_path))
feet={f.GetReference():f for f in b.GetFootprints()}
jy=pcb.ToMM(feet['J1'].GetPosition().y)
mouth_nominal=round(jy-13.7,6)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rotation_chord=2*math.sin(math.radians(.5))
def bound(ref,bounds,z,pose=True):
    f=feet[ref];ang=math.radians(f.GetOrientationDegrees())
    cx,cy=pcb.ToMM(f.GetPosition().x),pcb.ToMM(f.GetPosition().y)
    vertices=[]
    for x,y,zz in itertools.product((bounds[0],bounds[2]),(bounds[1],bounds[3]),z):
        xx=x*math.cos(ang)+y*math.sin(ang)
        yy=-x*math.sin(ang)+y*math.cos(ang)
        # Any rigid rotation <=1 degree moves this vertex by no more
        # than its radius times the chord; radial XY translation <=.10.
        delta=.1+rotation_chord*math.sqrt(x*x+y*y+zz*zz) if pose else 0
        vertices.append(([cx+xx,cy+yy,zz],delta))
    return [[min(v[k]-d for v,d in vertices) for k in range(3)],
            [max(v[k]+d for v,d in vertices) for k in range(3)]]
def separation(x,y):
    axes=[max(y[0][k]-x[1][k],x[0][k]-y[1][k],0) for k in range(3)]
    return {'axis_gaps_mm':axes,'lower_bound_mm':math.sqrt(sum(v*v for v in axes))}
jack=bound('J1',[-4.7,-1.3,4.7,14.1],[0,11.5])
neighbors={}
for ref in ('F1','D1','D3','C1'):
    model=a['models'][a['boards']['carrier']['references'][ref]]
    body=model['bodies'][0]
    bb=bound(ref,body['bounds'],body['z'])
    fields={field.GetName():field.GetText() for field in feet[ref].GetFields()}
    actual_mpn=fields.get('MPN',model['mpn'])
    neighbors[ref]={'mpn':actual_mpn,'historical_model_identity':model['mpn'],
        'local_body':body,'pose_bound':bb,
        'jack_separation':separation(jack,bb),'basis':model['basis']}
    if ref=='C1':
        assert actual_mpn=='CL31B106KBHNNNE'
        neighbors[ref]['current_identity_reconciliation']='Current Samsung CL31B106KBHNNNE max3.40x1.80x1.80mm is deliberately screened inside the retained broader3.60x1.90x2.05mm occupied envelope. Historical TDK identity is not the installed part. See current capacitor-review.md exact maker dimensions and adoption.'
    assert neighbors[ref]['jack_separation']['lower_bound_mm']>0
# Straight plug exterior: 8.5-mm maximum cover, centerline 6.50 +/-.20;
# mouth nominal1.5 +/-.40 from independently bounded body/pin dimensions.
# 36mm longitudinal sweep covers the34mm maximum overall plug at withdrawal.
# +.60 inward transition covers nose/insertion-depth tolerance differences.
mouth=[mouth_nominal-.4,mouth_nominal+.4]
plug_nominal=[[183.75,mouth[0]-36,2.05],[192.25,mouth[1]+.6,10.95]]
max_radius=max(math.sqrt((x-188)**2+(y-jy)**2+z*z)
    for x,y,z in itertools.product(*[(plug_nominal[0][k],plug_nominal[1][k]) for k in range(3)]))
pose_requirement=.1+rotation_chord*max_radius
assert pose_requirement<1.1
plug=[[plug_nominal[0][k]-1.1 for k in range(3)],
      [plug_nominal[1][k]+1.1 for k in range(3)]]
plug[1][2]+=.1 # seating elevation once
for ref,entry in neighbors.items():
    entry['plug_exterior_separation']=separation(plug,entry['pose_bound'])
    assert entry['plug_exterior_separation']['lower_bound_mm']>0
result={'scope':'Affected drawing-envelope clearance and straight-accessory approach only; no populated-assembly or vNext acceptance',
    'board_sha256':sha(board_path),'jack_pose':{'origin':[188,jy],'angle':180,'mouth_nominal_y':mouth_nominal,'direction':'native -Y'},
    'corrected_jack_local_box':{'xy':[-4.7,-1.3,4.7,14.1],'z':[0,11.5]},
    'jack_pose_bound':jack,'neighbors':neighbors,
    'plug':{'mpn':'PP3-002A','center_positive_required':True,'diameter_max_mm':8.5,
        'mouth_dimensional_range_y':mouth,'exterior_nominal_bounds':plug_nominal,
        'rotation_radius_mm':max_radius,'required_pose_expansion_mm':pose_requirement,
        'adopted_pose_expansion_mm':1.1,'exterior_reserved_bounds':plug,
        'finished_board_z_max_mm':.05,'board_gap_lower_bound_mm':plug[0][2]-.05,
        'own_interface':'Only compatible selected nose/barrel engages named jack receptacle; no whole-reference collision waiver or private-cavity simulation',
        'nose_nonowner_bound':'Barrel<=diameter5.55, axis6.50+/-.20, forward engagement<=9.8mm beyond mouth. All four nearby nonowners are disjoint in X or Y even before their broad exterior corridor bound.'},
    'underside':{'board_thickness_mm':1.6,'lead_projection_max_below_seating_mm':3.7,
        'native_terminal_centers':[[188,jy],[188,jy-6],[183.3,jy-3]],
        'nominal_xy_hole_column_radius_mm':.8,
        'limit':'Retain prescribed-hole occupancy and finite installed-pose projection controls; no standoff/enclosure/support/floor hardware in these columns. These are interface envelopes, not invented private tab profiles.'},
    'limitations':['Retain actual body/pose and first-article dimensional inspection holds; candidate3 narrow0.0369mm gap was rejected in favor of candidate4 outward0.5mm robustness shift.',
        'Unchanged distant board bodies retain prior source and substitution reviews; no new full populated 3D proof, unknown module height/enclosure or arbitrary cable approval.',
        'Only straight PP3-002A; no bend, right-angle boot or cable-assembly wiring test performed.',
        'Native holes are1.6mm drills, not guaranteed finished holes. Finished opening1.60..1.73, actual annulus>=.30, seating, solder fill>=75%, process agreement and representative29.4N mating/retention qualification remain unperformed.'],
    'sources':{str(p):sha(p) for p in [assembly,external/'03_src/recovery/ls43-mating/controls.md',
        external/'02_parts/P028/manufacturer.pdf',external/'02_parts/mechanical-ls33/pp3-002a.pdf',
        external/'02_parts/P032/manufacturer.pdf',external/'02_parts/P001/manufacturer.pdf',
        Path(__file__).resolve().parent.parent/'substitutions-20261101/capacitor-review.md',
        Path('/tmp/crow-cap-review-OSRijwkC/CL31B106KBHNNN-spec.pdf')]}}
retained=out.parent/'source-evidence';retained.mkdir(exist_ok=True)
result['retained_sources']={}
for i,source in enumerate(result['sources']):
    src=Path(source);dest=retained/(str(i)+'-'+src.parent.name+'-'+src.name)
    if dest.exists():assert sha(dest)==sha(src)
    else:shutil.copy2(src,dest)
    result['retained_sources'][str(dest.relative_to(out.parent))]=sha(dest)
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'D1_gap':neighbors['D1']['jack_separation'],'plug_pose_expansion_required':pose_requirement,
    'plug_corridor':plug,'board_gap':result['plug']['board_gap_lower_bound_mm']},indent=2))
