"""Source-bound assembly envelopes and independent admission; no order authority."""
import argparse
import csv
from html import escape
import json
import math
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
import fabrication as fab

p = fab.p
CONTRACT = '01_docs/assembly-contract.json'
RECEIPT = '06_build/checkpoints/assembly_verified.json'
STAGE = 'skills/pcb-design/workflow/stages/assembly-verify.md'
MANUAL = 'skills/pcb-design/procedures/fabrication/assembly-tooling.md'
CRITERIA = {'population', 'geometry', 'polarity', 'access', 'instructions', 'handoff'}


def local(root, name, exists=True):
    path = p.local(root, name, exists)
    p.need(not any((root / Path(*Path(name).parts[:i])).is_symlink()
                   for i in range(1, len(Path(name).parts)+1)), 'linked assembly input')
    return path


def evidence(root, names, subjects):
    p.need(isinstance(names, list) and names and all(isinstance(n, str) for n in names),
           'retained assembly evidence required')
    for name in names: subjects[name] = p.sha(local(root, name))


def text(value):
    p.need(isinstance(value, str) and value.strip(), 'nonempty assembly rationale required')
    return value


def xy(value):
    p.need(isinstance(value, list) and len(value) == 2, 'two coordinates required')
    return list(map(p.number, value))


def volume(row, pos):
    z = xy(row['z']); p.need(z[0] < z[1], 'empty/reversed height interval')
    shape = row['shape']
    if shape == 'box':
        p.need(set(row) == {'shape', 'bounds', 'z'}, 'unsupported box fields')
        a,b,c,d = p.rect(row['bounds'])
        corners = [p.point(pos, q) for q in ([a,b],[a,d],[c,b],[c,d])]
        return dict(shape=shape, bounds=[min(q[0] for q in corners), min(q[1] for q in corners),
                                         max(q[0] for q in corners), max(q[1] for q in corners)], z=z)
    p.need(shape == 'circle' and set(row) == {'shape','center','radius','z'}, 'unsupported body shape')
    center = p.point(pos, xy(row['center'])); radius = p.number(row['radius'])
    p.need(radius > 0, 'positive body radius required')
    return dict(shape=shape, center=center, radius=radius, z=z,
                bounds=[center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius])


def collision(a, b):
    if min(a['z'][1], b['z'][1]) <= max(a['z'][0], b['z'][0])+1e-6: return False
    if not p.overlap(a['bounds'], b['bounds']): return False
    if a['shape'] == b['shape'] == 'box': return True
    if a['shape'] == b['shape'] == 'circle':
        return math.dist(a['center'], b['center']) < a['radius']+b['radius']-1e-6
    if a['shape'] == 'box': a,b = b,a
    x,y = a['center']; l,t,r,d = b['bounds']
    return math.dist([x,y], [max(l,min(x,r)), max(t,min(y,d))]) < a['radius']-1e-6


def outline(board):
    points=outline_contour(board)
    return [min(v[0] for v in points),min(v[1] for v in points),
            max(v[0] for v in points),max(v[1] for v in points)]


def outline_contour(board):
    """Native closed outer contour for overview only; real STEP owns clearance.

    KiCad tessellates arcs for this display polygon. Do not use its bounding
    rectangle as a board solid or as proof that a body over a recess is supported.
    Internal Edge.Cuts islands/cutouts require a separate explicit extension.
    """
    edges=[e for e in board.GetDrawings() if e.GetLayer()==p.pcb.Edge_Cuts]
    p.need(edges and all(e.GetShape() in (p.pcb.S_SEGMENT,p.pcb.S_ARC,p.pcb.S_RECT)
                        for e in edges),'unsupported native assembly outline')
    poly=p.pcb.SHAPE_POLY_SET()
    p.need(board.GetBoardPolygonOutlines(poly,False) and poly.OutlineCount()==1 and
           poly.HoleCount(0)==0,'open/disjoint/internal-cutout assembly outline')
    contour=poly.COutline(0)
    p.need(contour.PointCount()>=3,'empty assembly contour')
    return [[contour.CPoint(i).x/1e6,contour.CPoint(i).y/1e6]
            for i in range(contour.PointCount())]


def model_check(model):
    p.need(set(model) == {'manufacturer','mpn','footprint','evidence','basis','polarity','bodies','contacts'},
           'unsupported assembly model')
    for key in ('manufacturer','mpn','footprint','basis','polarity'): text(model[key])
    p.need(isinstance(model['bodies'],list) and model['bodies'], 'mounted body coverage required')
    for body in model['bodies']: volume(body, [0,0,0])
    contacts=model['contacts']; p.need(isinstance(contacts,dict) and contacts, 'contact coverage required')
    for number,row in contacts.items():
        text(number); p.need(set(row)=={'xy','tolerance_mm'}, 'unsupported contact geometry')
        xy(row['xy']); p.need(p.number(row['tolerance_mm']) >= 0, 'negative contact tolerance')


def board_geometry(board, spec, models, rows):
    p.need(set(spec)=={'source_sha256','references','access'}, 'unsupported board assembly fields')
    parts={}
    for fp in board.GetFootprints():
        ref=fp.GetReference(); p.need(ref not in parts, 'duplicate native reference'); parts[ref]=fp
    policies={r['reference']:r for r in rows}
    p.need(len(policies)==len(rows) and set(parts)==set(policies), 'native/population reference census differs')
    populated={r for r,v in policies.items() if v['mode'] in {'factory','consigned','manual'}}
    p.need(populated and set(spec['references'])==populated, 'mounted reference coverage differs')
    result={'outline':outline(board),'references':{},'access':[], 'failures':[], 'overhangs':[],
            'native_pads':[],
            'policy_counts':{mode:sum(r['mode']==mode for r in rows)
                             for mode in ('factory','consigned','manual','dnp','mechanical')}}
    contour=outline_contour(board)
    l,t,r,b=result['outline']
    if {tuple(v) for v in contour}!={(l,t),(r,t),(r,b),(l,b)}:
        result['outline_contour']=contour
        result['outline_limitation']='Tessellated native overview; overhang list covers outer bounds only. Registered solid checks own recess/support clearance.'
    for ref,fp in sorted(parts.items()):
        for pad in fp.Pads():
            result['native_pads'].append(dict(reference=ref,mode=policies[ref]['mode'],number=pad.GetNumber(),
                center=[pad.GetPosition().x/1e6,pad.GetPosition().y/1e6],bounds=p.box(pad),
                drill=[pad.GetDrillSize().x/1e6,pad.GetDrillSize().y/1e6],drill_angle_deg=pad.GetOrientationDegrees()))
    result['native_pads'].sort(key=lambda row:(row['reference'],row['number'],row['center'],row['drill']))
    bodies=[]
    for ref,key in sorted(spec['references'].items()):
        p.need(key in models, 'unknown assembly model'); model=models[key]; fp=parts[ref]; row=policies[ref]
        for field,native in [('manufacturer','Manufacturer'),('mpn','MPN')]:
            p.need(model[field]==row[field]==fp.GetFieldText(native), 'assembly identity differs: '+ref)
        p.need(model['footprint']==row['footprint']==fp.GetFPIDAsString(), 'assembly footprint differs: '+ref)
        p.need(not fp.IsFlipped(), 'bottom assembly needs explicit supported geometry')
        angle=fp.GetOrientationDegrees()
        p.need(abs(angle/90-round(angle/90))<1e-6, 'noncardinal assembly angle unsupported')
        pos=[fp.GetPosition().x/1e6,fp.GetPosition().y/1e6,angle]
        pads=[pad for pad in fp.Pads() if pad.GetNumber()]
        p.need({pad.GetNumber() for pad in pads}==set(model['contacts']), 'contact number coverage differs: '+ref)
        observed=[]
        for pad in pads:
            number=pad.GetNumber(); contact=model['contacts'][number]
            actual=[pad.GetPosition().x/1e6,pad.GetPosition().y/1e6]
            expected=p.point(pos,contact['xy']); error=math.dist(actual,expected)
            if error>contact['tolerance_mm']+1e-6:result['failures'].append('contact:'+ref+':'+number)
            observed.append(dict(number=number,actual=actual,expected=expected,error_mm=error,
                                 bounds=p.box(pad),drill=[pad.GetDrillSize().x/1e6,pad.GetDrillSize().y/1e6],
                                 net=pad.GetNetname()))
        mounted=[volume(v,pos) for v in model['bodies']]
        result['references'][ref]=dict(model=key,mode=row['mode'],position=pos,bodies=mounted,
                                       pads=sorted(observed,key=lambda q:(q['number'],q['actual'])),
                                       polarity=model['polarity'],basis=model['basis'])
        l,t,r,b=result['outline']
        for v in mounted:
            a,c,d,e=v['bounds']
            if a<l-1e-6 or c<t-1e-6 or d>r+1e-6 or e>b+1e-6:result['overhangs'].append(ref)
            bodies.append((ref,v))
    for i,(ref,a) in enumerate(bodies):
        for other,b in bodies[i+1:]:
            if ref!=other and collision(a,b):result['failures'].append('body:'+ref+':'+other)
    p.need(isinstance(spec['access'],list), 'explicit access applicability required')
    ids=set()
    for a in spec['access']:
        p.need(set(a)=={'id','ref','bounds','z','evidence'} and a['ref'] in populated,
               'invalid access owner/fields')
        text(a['id']);p.need(a['id'] not in ids,'duplicate access ID'); ids.add(a['id'])
        v=volume(dict(shape='box',bounds=a['bounds'],z=a['z']),[0,0,0])
        result['access'].append(dict(id=a['id'],ref=a['ref'],**v))
        for other,b in bodies:
            if other!=a['ref'] and collision(v,b):result['failures'].append('access:'+a['id']+':'+other)
    result['failures']=sorted(set(result['failures'])); result['overhangs']=sorted(set(result['overhangs']))
    result['verdict']='FAIL' if result['failures'] else 'PASS'
    return result


def svg(key, data, populated):
    boxes=[data['outline']]+[b['bounds'] for v in data['references'].values() for b in v['bodies']]+[
        a['bounds'] for a in data['access']]
    l=min(b[0] for b in boxes)-8;t=min(b[1] for b in boxes)-12
    r=max(b[2] for b in boxes)+8;bottom=max(b[3] for b in boxes)+8
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{l} {t} {r-l} {bottom-t}" width="1200">',
         '<rect x="-10000" y="-10000" width="20000" height="20000" fill="white"/>',
         f'<text x="{l+2}" y="{t+4}" font-size="2">{escape(key)} — '+
         ('POPULATED ENVELOPES' if populated else 'BARE PAD BOUNDS')+'</text>',
         f'<text x="{l+2}" y="{t+7}" font-size="1.5">Top view, native mm; common datum; not physical qualification</text>']
    def rect(box,attrs):
        x,y,x2,y2=box;return f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" {attrs}/>'
    if 'outline_contour' in data:
        points=' '.join(f'{x},{y}' for x,y in data['outline_contour'])
        out.append(f'<polygon points="{points}" fill="#fafafa" stroke="black" stroke-width="0.15"/>')
        out.append(f'<text x="{l+2}" y="{t+9}" font-size="1.2">Native contour tessellated for overview; registered STEP owns clearance</text>')
    else:
        out.append(rect(data['outline'],'fill="#fafafa" stroke="black" stroke-width="0.15"'))
    for ref,v in data['references'].items():
        if populated:
            for body in v['bodies']:
                attr='fill="#c2e7db" fill-opacity="0.7" stroke="#006d52" stroke-width="0.12"'
                if body['shape']=='box':out.append(rect(body['bounds'],attr))
                else:
                    x,y=body['center'];out.append(f'<circle cx="{x}" cy="{y}" r="{body["radius"]}" {attr}/>')
        x,y,_=v['position'];out.append(f'<text x="{x+0.6}" y="{y-0.6}" font-size="1.2">{escape(ref)}</text>')
    for pad in data['native_pads']:
        color='#777' if pad['mode'] in ('mechanical','dnp') else '#c72525' if pad['number']=='1' else '#245b88'
        out.append(rect(pad['bounds'],f'fill="none" stroke="{color}" stroke-width="0.08"'))
        dx,dy=pad['drill']
        if dx>0 and dy>0:
            cx,cy=pad['center'];angle=-pad['drill_angle_deg']
            out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{dx/2}" ry="{dy/2}" '+
                       f'transform="rotate({angle} {cx} {cy})" fill="white" stroke="#666" stroke-width="0.07"/>')
    for a in data['access']:
        out.append(rect(a['bounds'],'fill="none" stroke="#b46b00" stroke-width="0.13" stroke-dasharray="1,1"'))
    return '\n'.join(out+['</svg>'])+'\n'


def contract(project):
    c=p.read(local(project,CONTRACT))
    fields={'version','authority','authority_sha256','fabrication_receipt_sha256'}
    if c.get('version')==2:fields.add('mechanical')
    p.need(set(c)==fields and c['version'] in (1,2),
           'unsupported assembly contract')
    p.need(p.sha(local(project,c['authority']))==c['authority_sha256'],'assembly authority changed')
    p.need(p.sha(local(project,fab.RECEIPT))==c['fabrication_receipt_sha256'],'fabrication adoption changed')
    return c


def upstream(project):
    c=contract(project)
    receipt=fab.check(project)
    review=fab.seal.r.review_json(project,receipt['review'])
    subjects=dict(receipt['subjects'])
    evidence(project,[CONTRACT,c['authority'],fab.RECEIPT,receipt['review']],subjects)
    return review['output'],subjects


def payload(project, name, package_name, subjects):
    spec=p.read(local(project,name)); subjects=dict(subjects); evidence(project,[name],subjects)
    p.need(set(spec)=={'version','package','models','boards','instructions','handoff'} and spec['version']==1,
           'unsupported assembly manifest')
    p.need(spec['package']==package_name,'assembly must use exact accepted fabrication package')
    package=local(project,package_name,False)
    bundle=p.read(package/'native/bundle.json')
    p.need(set(spec['boards'])==set(bundle['boards']) and spec['boards'],'assembly board coverage differs')
    with (package/'assembly/population.csv').open() as f: rows=list(csv.DictReader(f))
    models=spec['models']; p.need(isinstance(models,dict) and models,'assembly models required')
    for model in models.values():model_check(model);evidence(project,model['evidence'],subjects)
    used={k for board in spec['boards'].values() for k in board['references'].values()}
    p.need(used==set(models),'unused/missing assembly models')
    for field in ('instructions','handoff'):evidence(project,spec[field],subjects)
    report={}; outputs={}
    for key,board in spec['boards'].items():
        native=local(package/'native',bundle['boards'][key]['native'])
        p.need(board['source_sha256']==p.sha(native),'stale assembly geometry source: '+key)
        for access in board['access']:evidence(project,access['evidence'],subjects)
        report[key]=board_geometry(p.pcb.LoadBoard(str(native)),board,models,[r for r in rows if r['board']==key])
        for populated,label in [(False,'bare'),(True,'populated')]:outputs[key+'-'+label+'.svg']=svg(key,report[key],populated)
    report={'boards':report,'accepted':False,'order_status':'DO-NOT-ORDER',
            'scope':'dimensioned assembly envelopes; not performed assembly or vendor preview',
            'order_holds':p.read(package/'fabrication.json')['order_holds']}
    outputs['geometry.json']=json.dumps(report,indent=2,sort_keys=True)+'\n'
    record={'version':1,'manifest':name,'package':package_name,'subjects':subjects,
            'tools':{n:p.sha(Path(__file__).parent/n) for n in (*fab.TOOLS,'assembly_verify.py')},
            'guidance':{n:p.sha(p.ROOT/n) for n in (STAGE,MANUAL)}}
    outputs['assembly.json']=json.dumps(record,indent=2,sort_keys=True)+'\n'
    return outputs,report,subjects


def deliverable(project,name,package,subjects):
    files,report,subjects=payload(project,name,package,subjects)
    # Isolated envelope fixtures remain available, but cannot issue new acceptance.
    if not (project/CONTRACT).exists() or p.read(project/CONTRACT)['version']==1:
        return files,report,subjects
    import assembly_3d
    c=contract(project)
    result=assembly_3d.scene(project,c['mechanical'],name,p.read(local(project,name)),report,subjects)
    subjects=result['subjects']
    record=json.loads(files['assembly.json']);record['version']=2
    record['subjects']=subjects
    record['tools'].update({n:p.sha(Path(__file__).parent/n) for n in ('assembly_3d.py','mating_admission.py')})
    record['guidance'][assembly_3d.GUIDANCE]=p.sha(p.ROOT/assembly_3d.GUIDANCE)
    files['assembly.json']=json.dumps(record,indent=2,sort_keys=True)+'\n'
    files['mechanical.json']=json.dumps(result,indent=2,sort_keys=True)+'\n'
    return files,report,subjects


def build(project,name,output):
    package,subjects=upstream(project); files,report,_=deliverable(project,name,package,subjects)
    dest=local(project,output,False);p.need(not dest.exists(),'refusing existing assembly output')
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.assembly-',dir=dest.parent) as tmp:
        stage=Path(tmp)/'payload';stage.mkdir()
        for n,value in files.items():(stage/n).write_text(value)
        stage.rename(dest)
    return report


def verify(project,name,output):
    package,subjects=upstream(project);files,report,subjects=deliverable(project,name,package,subjects)
    dest=local(project,output,False)
    p.need(dest.is_dir(),'missing assembly output')
    paths=list(dest.rglob('*'));p.need(not any(f.is_symlink() for f in paths),'linked assembly output')
    p.need({str(f.relative_to(dest)) for f in paths if f.is_file()}==set(files),'assembly output census differs')
    for n,value in files.items():
        p.need((dest/n).read_bytes()==value.encode(),'stale assembly output: '+n)
        subjects[output+'/'+n]=p.sha(dest/n)
    p.need(all(b['verdict']=='PASS' for b in report['boards'].values()),'assembly geometry findings unresolved')
    return {'subjects':subjects,'report':report}


def certificate(project,name,historical=False):
    stages=[s for s in p.read(p.ROOT/'skills/pcb-design/workflow/graph.json')['stages']
            if s['spec']['id']=='JLC-ASSEMBLY-VERIFY']
    p.need(len(stages)==1,'assembly stage identity differs');stage=stages[0]
    p.need(stage['spec']['requires']==['fabrication_staged'] and stage['spec']['produces']==['assembly_verified'],
           'assembly graph contract differs')
    binding=stage.get('local_execution',{})
    p.need('local_definition' not in stage and binding.get('tool')=='tools/assembly_verify.py' and
           binding.get('contract')==STAGE and binding.get('status')=='pilot_under_validation','assembly adapter not adopted')
    c=p.read(local(project,CONTRACT))
    p.need(historical or c.get('version')==2,'new assembly acceptance requires registered3D contract version2')
    review=fab.seal.r.review_json(project,name)
    result=verify(project,review['manifest'],review['output'])
    spec=p.read(local(project,review['manifest']));out=review['output']
    extra_tools=();extra_guidance=()
    if c['version']==2:
        import assembly_3d
        assembly_3d.judgments(project,review.get('mechanical'),p.read(local(project,out+'/mechanical.json')),
                              spec,result['subjects'])
        extra_tools=('assembly_3d.py','mating_admission.py');extra_guidance=(assembly_3d.GUIDANCE,)
    p.need(review.get('schema')==1 and review.get('stage')=='JLC-ASSEMBLY-VERIFY' and review.get('verdict')=='PASS',
           'assembly review not PASS')
    p.need(text(review['author']).casefold()!=text(review['reviewer']).casefold(),'independent assembly reviewer required')
    p.need(result['subjects'].items()<=review.get('subjects',{}).items(),'assembly review subject coverage differs')
    for n,digest in review['subjects'].items():p.need(p.sha(local(project,n))==digest,'stale assembly review subject: '+n)
    checks=review.get('checks',{});p.need(set(checks)==CRITERIA,'assembly review criteria differ')
    geometry={out+'/geometry.json',out+'/assembly.json'}|{
        out+'/'+key+'-'+view+'.svg' for key in spec['boards'] for view in ('bare','populated')}
    maker={n for m in spec['models'].values() for n in m['evidence']}
    access={n for b in spec['boards'].values() for a in b['access'] for n in a['evidence']}
    population_files={spec['package']+'/assembly/'+f.name
                      for f in local(project,spec['package'],False).joinpath('assembly').iterdir() if f.suffix=='.csv'}
    required={'population':population_files|{out+'/geometry.json'},
              'geometry':geometry|maker,'polarity':maker|{out+'/geometry.json'},
              'access':geometry|access,'instructions':set(spec['instructions']),
              'handoff':set(spec['handoff'])|{spec['package']+'/fabrication.json'}}
    for key,row in checks.items():
        p.need(row.get('verdict')=='PASS','assembly criterion not PASS: '+key);text(row.get('rationale'))
        ev=row.get('evidence');p.need(isinstance(ev,list) and ev and all(n in review['subjects'] for n in ev)
                                    and required[key]<=set(ev),'assembly review omits '+key+' evidence')
    return dict(schema=1,role='assembly_verified',review=name,review_sha256=p.sha(local(project,name)),
                subjects=review['subjects'],stage_spec=stage['spec'],
                toolchain={n:p.sha(Path(__file__).parent/n) for n in (*fab.TOOLS,'assembly_verify.py',*extra_tools)},
                guidance={n:p.sha(p.ROOT/n) for n in (STAGE,MANUAL,*extra_guidance)},
                order_status='DO-NOT-ORDER',next_owner='PCB-RELEASE-REVIEW')


def check(project):
    old=p.read(local(project,RECEIPT));p.need(old==certificate(project,old['review'],historical=True),'stale assembly receipt');return old


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['build','verify','issue','check']);parser.add_argument('--project',type=Path,required=True)
    for key in ('manifest','output','review'):parser.add_argument('--'+key)
    args=parser.parse_args();root=args.project.resolve()
    try:
        if args.action in ('build','verify'):
            p.need(args.manifest and args.output,'manifest/output required')
            result=(build if args.action=='build' else verify)(root,args.manifest,args.output)
        elif args.action=='check':result=check(root)
        else:
            p.need(args.review,'review required');result=certificate(root,args.review)
            target=local(root,RECEIPT,False);target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True)
        print(json.dumps(result,indent=2));return 0
    except (ValueError,KeyError,TypeError,OSError,AttributeError) as exc:
        print('Assembly refused: '+str(exc),file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
