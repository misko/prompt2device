"""Native-board diagnostic renders; no CAD mutations or acceptance receipts."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[2] / 'tools'
sys.path.insert(0, str(TOOLS))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def views():
    result = {'top': ([0,0,1],[0,1,0]), 'bottom': ([0,0,-1],[0,1,0]),
              'north': ([0,1,0],[0,0,1]), 'south': ([0,-1,0],[0,0,1]),
              'east': ([1,0,0],[0,0,1]), 'west': ([-1,0,0],[0,0,1])}
    for elevation in (45,-45):
        for az in range(0,360,45):
            a,e = math.radians(az), math.radians(elevation)
            result[f'{"upper" if elevation>0 else "lower"}_{az:03d}'] = (
                [math.cos(e)*math.cos(a),math.cos(e)*math.sin(a),math.sin(e)], [0,0,1])
    return result


def native_point(point, footprint):
    a=math.radians(footprint['angle']);x,y=point
    return [footprint['position'][0]+math.cos(a)*x+math.sin(a)*y,
            footprint['position'][1]-math.sin(a)*x+math.cos(a)*y]


def connector_check(f, spec):
    if f.get('mpn') != spec['mpn']:
        raise ValueError('Connector MPN does not match native source: '+f['ref'])
    if f['bottom']:
        raise ValueError('Bottom connector registration unsupported: '+f['ref'])
    if len(spec['expected_pads']) < 2:
        raise ValueError('At least two numbered-pad witnesses required')
    witnesses=[]
    for number,local in spec['expected_pads'].items():
        targets=[p['position'] for p in f['pads'] if p['number']==number]
        if not targets: raise ValueError('Missing numbered pad '+number)
        expected=native_point(local,f)
        witnesses.append(dict(pad=number,expected=expected,error_mm=min(math.dist(expected,t) for t in targets)))
    pegs=[p['position'] for p in f['pads'] if not p['number'] and max(p['drill'])>0]
    for local in spec.get('expected_pegs',[]):
        expected=native_point(local,f)
        witnesses.append(dict(peg=local,expected=expected,error_mm=min((math.dist(expected,t) for t in pegs),default=1e9)))
    x,y=spec['mouth_direction'];a=math.radians(f['angle'])
    actual=[math.cos(a)*x+math.sin(a)*y,-math.sin(a)*x+math.cos(a)*y]
    intended=spec['intended_direction']
    norm=math.hypot(*actual)*math.hypot(*intended)
    if norm==0:raise ValueError('Zero direction')
    dot=sum(x*y for x,y in zip(actual,intended))/norm
    return dict(mpn=spec['mpn'],source=spec['source'],limitations=spec['limitations'],
                witnesses=witnesses, registration='PASS' if max(w['error_mm'] for w in witnesses)<=spec['tolerance_mm'] else 'FAIL',
                actual_native_direction=actual,intended_native_direction=intended,
                direction='PASS' if dot>1-1e-6 else 'FAIL',access='NOT_EVALUATED')


def primitive(s,k):
    cq=k.cq
    if s['kind']=='box':
        x,y,z,X,Y,Z=s['bounds']
        shape=cq.Solid.makeBox(X-x,Y-y,Z-z,cq.Vector(x,-Y,z))
    elif s['kind']=='cylinder':
        x,y,z=s['base'];dx,dy,dz=s['axis']
        shape=cq.Solid.makeCylinder(s['radius'],s['length'],cq.Vector(x,-y,z),cq.Vector(dx,-dy,dz))
    else:raise ValueError('Unknown primitive '+s['kind'])
    for cut in s.get('cuts',[]):shape=shape.cut(primitive(cut,k))
    return k.solid_check(shape)


def make_renderer(parts,colors,k):
    import vtk
    renderer=vtk.vtkRenderer();renderer.SetBackground(.94,.96,.98)
    window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetMultiSamples(0);window.AddRenderer(renderer)
    actors={}
    for name,shape in parts.items():
        vertices,triangles=shape.tessellate(.08,.2);points=vtk.vtkPoints()
        for v in vertices:points.InsertNextPoint(v.x,v.y,v.z)
        cells=vtk.vtkCellArray()
        for tri in triangles:
            cells.InsertNextCell(3)
            for i in tri:cells.InsertCellPoint(i)
        mesh=vtk.vtkPolyData();mesh.SetPoints(points);mesh.SetPolys(cells)
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(mesh)
        actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*colors[name]);renderer.AddActor(actor);actors[name]=actor
    for ref in sorted({n.split('/')[0] for n in parts if '/' in n}):
        boxes=[k.bounds(s) for n,s in parts.items() if n.startswith(ref+'/')]
        x=(min(b[0] for b in boxes)+max(b[3] for b in boxes))/2
        y=(min(b[1] for b in boxes)+max(b[4] for b in boxes))/2
        z=max(b[5] for b in boxes)+.3
        label=vtk.vtkBillboardTextActor3D();label.SetInput(ref);label.SetPosition(x,y,z)
        label.GetTextProperty().SetFontSize(17);label.GetTextProperty().SetColor(.95,.70,.15)
        label.GetTextProperty().SetJustificationToCentered();renderer.AddActor(label);actors[ref+'/label']=label
    title=vtk.vtkTextActor();title.SetPosition(15,15);title.GetTextProperty().SetFontSize(17);title.GetTextProperty().SetColor(.05,.08,.12);renderer.AddViewProp(title)
    def render(path,frame,label,visible=None):
        for name,actor in actors.items():
            show=visible is None or name in visible
            if visible is not None and name.endswith('/label'):
                show=any(n.startswith(name.split('/')[0]+'/') for n in visible)
            actor.SetVisibility(show)
        title.SetInput(label);window.SetSize(frame['width'],frame['height'])
        c=renderer.GetActiveCamera();c.ParallelProjectionOn();c.SetPosition(*frame['position']);c.SetFocalPoint(*frame['focal_point']);c.SetViewUp(*frame['up']);c.SetParallelScale(frame['parallel_scale']);c.SetClippingRange(*frame['clip'])
        renderer.ResetCameraClippingRange();window.Render()
        capture=vtk.vtkWindowToImageFilter();capture.SetInput(window);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
        writer=vtk.vtkPNGWriter();writer.SetFileName(str(path));writer.SetInputConnection(capture.GetOutputPort());writer.Write()
    return render,window


def build(board,inspection,output,kicad_python,width=1400):
    import mechanical_kernel as k
    from PIL import Image,ImageDraw
    if output.exists():raise ValueError('Refusing existing output')
    spec=json.loads(inspection.read_text())
    if spec['version']!=1:raise ValueError('Unsupported version')
    source_hash=sha(board);snapshot=json.loads(subprocess.check_output([kicad_python,str(HERE/'native_snapshot.py'),str(board)],text=True))
    refs={f['ref']:f for f in snapshot['footprints']}
    for ref in spec['connectors']:
        if ref not in refs:raise ValueError('Unknown connector '+ref)
    output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='render-board-native-') as tmp:
        copied=Path(tmp)/'native';shutil.copytree(board.parent,copied)
        command=['kicad-cli','pcb','export','step','--no-components','--user-origin','0x0mm','--output',str(output/'native-board.step'),str(copied/board.name)]
        result=subprocess.run(command,text=True,capture_output=True)
        (output/'export.log').write_text(result.stdout+result.stderr)
        result.check_returncode()
    raw=k.load_step(output/'native-board.step');top=k.bounds(raw)[5]
    bare=raw.translate((0,0,-top));parts={'board':bare};colors={'board':(.08,.35,.23)}
    coverage={};checks={}
    for ref,f in refs.items():
        if f['dnp']:
            coverage[ref]='native_DNP_not_rendered';continue
        if ref in spec['connectors']:
            s=spec['connectors'][ref];checks[ref]=connector_check(f,s)
            coverage[ref]='drawing_derived_inspection_solids'
            for i,solid in enumerate(s['solids']):
                name=f'{ref}/{i}';parts[name]=k.pose(primitive(solid,k),(f['position'][0],-f['position'][1],0),(0,0,f['angle']))
                colors[name]=solid.get('color',[.18,.19,.21])
        elif not ref.startswith(('H','TP')):
            x,y,X,Y=f['bounds'];z=-snapshot['thickness_mm']-1 if f['bottom'] else 0
            if X<=x or Y<=y:continue
            parts[ref]=primitive(dict(kind='box',bounds=[x,y,z,X,Y,z+1]),k)
            colors[ref]=(.55,.59,.64);coverage[ref]='unqualified_footprint_envelope_height_1mm'
    boxes=[k.bounds(s) for s in parts.values()]
    box=[min(b[i] for b in boxes) for i in range(3)]+[max(b[i] for b in boxes) for i in range(3,6)]
    render,window=make_renderer(parts,colors,k);frames={};height=round(width*.67)
    try:
        for name,(direction,up) in views().items():
            frame=k.camera_frame(box,direction,up,width,height);frames[name]=frame
            render(output/f'{name}.png',frame,f'{spec["label"]} | {name} | DRAWING-DERIVED DIAGNOSTIC; NOT ACCEPTED')
        for ref in spec['connectors']:
            names={n for n in parts if n.startswith(ref+'/')};bounds=[k.bounds(parts[n]) for n in names]
            if not bounds:continue
            close=[min(b[i] for b in bounds)-3 for i in range(3)]+[max(b[i] for b in bounds)+3 for i in range(3,6)]
            for view in ('top','bottom','upper_045','upper_135','upper_225','upper_315','lower_045'):
                name=f'detail-{ref}-{view}';d,u=views()[view];frame=k.camera_frame(close,d,u,width,height);frames[name]=frame
                render(output/f'{name}.png',frame,f'{spec["label"]} {ref} | {view} | ISOLATED; OTHER COMPONENTS HIDDEN',{'board'}|names)
    finally:window.Finalize()
    thumbnails=[]
    for name in ('top','bottom','upper_045','upper_135','upper_225','upper_315'):
        with Image.open(output/f'{name}.png') as im:
            im=im.convert('RGB');im.thumbnail((600,420));thumbnails.append((name,im.copy()))
    sheet=Image.new('RGB',(1200,3*450),'white');draw=ImageDraw.Draw(sheet)
    for i,(name,im) in enumerate(thumbnails):
        x=(i%2)*600;y=(i//2)*450;sheet.paste(im,(x,y));draw.text((x+12,y+420),name,fill='black')
    sheet.save(output/'overview.png')
    pages=''.join(f'<figure><a href="{html.escape(n)}.png"><img width="600" src="{html.escape(n)}.png"></a><figcaption>{html.escape(n)}</figcaption></figure>' for n in frames)
    (output/'gallery.html').write_text('<!doctype html><meta charset="utf-8"><title>Board inspection</title><h1>'+html.escape(spec['label'])+'</h1><p>Drawing-derived diagnostics, not assembly approval. Gray non-connector envelopes have illustrative heights. See report.json for failures/unknowns.</p>'+pages)
    report=dict(accepted=False,coordinates='right handed X, -nativeY, Z above native STEP top',
                board= str(board),source_sha256=source_hash,inspection=str(inspection),inspection_sha256=sha(inspection),
                sources={str(p):sha(p) for p in (HERE/'render_board.py',HERE/'native_snapshot.py',TOOLS/'mechanical_kernel.py')},
                coverage=coverage,connectors=checks,model_notes=spec.get('model_notes',[]),
                missing_connector_reviews=[r for r in refs if r.startswith(('J','P')) and not r.startswith('TP') and r not in checks],
                frames=frames,view_count=len(views()),declared_thickness_mm=snapshot['thickness_mm'],rendered_native_step_thickness_mm=k.bounds(bare)[5]-k.bounds(bare)[2],
                limitations=['Native dielectric STEP, not finished copper/mask thickness.','No clearance/plug-fit check.','Module connectors require explicit declaration.','Inspection solids are not independent manufacturer CAD.'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if sha(board)!=source_hash:raise ValueError('Native source changed')
    for path in output.glob('*.png'):
        with Image.open(path) as im:
            if not any(a!=b for a,b in im.convert('RGB').getextrema()):raise ValueError('Blank image')
    (output/'manifest.json').write_text(json.dumps({p.name:sha(p) for p in output.iterdir() if p.is_file()},indent=2)+'\n')
    return dict(output=str(output),views=len(frames),connector_results={r:(c['registration'],c['direction']) for r,c in checks.items()},accepted=False)


def verify(output):
    expected=json.loads((output/'manifest.json').read_text());actual={p.name:sha(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}
    if actual!=expected:raise ValueError('Output bytes changed')
    r=json.loads((output/'report.json').read_text())
    sources={r['board']:r['source_sha256'],r['inspection']:r['inspection_sha256'],**r['sources']}
    if any(sha(p)!=h for p,h in sources.items()):raise ValueError('Source bytes changed')
    return dict(result='PASS_INTEGRITY_ONLY',accepted=False,files=len(actual))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--board',type=Path);p.add_argument('--inspection',type=Path);p.add_argument('--output',type=Path);p.add_argument('--verify',type=Path);p.add_argument('--kicad-python',default='/usr/bin/python3');p.add_argument('--width',type=int,default=1400);a=p.parse_args()
    if a.verify: result=verify(a.verify.resolve())
    else:
        if not(a.board and a.inspection and a.output):p.error('--board, --inspection and --output required')
        result=build(a.board.resolve(),a.inspection.resolve(),a.output.resolve(),a.kicad_python,a.width)
    print(json.dumps(result,indent=2))
