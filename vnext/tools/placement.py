"""Small source-owned native placement producer. Geometry PASS is not acceptance."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid
import xml.etree.ElementTree as ET

import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = '01_docs/placement-contract.json'
RECEIPT = '06_build/checkpoints/placement_reviewed.json'
CRITERIA = {'completeness','mechanical','electrical','routability','reproducibility','applicability'}


def need(value, message):
    if not value:
        raise ValueError(message)


def pairs(items):
    out = {}
    for k,v in items:
        need(k not in out, 'duplicate JSON key: '+k)
        out[k] = v
    return out


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError('nonfinite number')))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(root, name, exists=True):
    need(isinstance(name,str) and name and not Path(name).is_absolute()
         and '..' not in Path(name).parts and str(Path(name))==name, 'invalid relative path')
    p = root/name
    need(p.resolve().is_relative_to(root.resolve()), 'path escapes project')
    if exists:
        need(p.is_file(), 'missing input: '+name)
    return p


def number(x):
    need(type(x) in (int,float) and math.isfinite(x), 'finite numeric geometry required')
    return float(x)


def rect(value):
    need(isinstance(value,list) and len(value)==4, 'rectangle needs four numbers')
    r = list(map(number,value))
    need(r[0]<r[2] and r[1]<r[3], 'empty or reversed rectangle')
    return r


def overlap(a,b,gap=0):
    return a[0]<b[2]+gap-1e-6 and b[0]<a[2]+gap-1e-6 and a[1]<b[3]+gap-1e-6 and b[1]<a[3]+gap-1e-6


def inside(r,w,h):
    return r[0]>=-1e-5 and r[1]>=-1e-5 and r[2]<=w+1e-5 and r[3]<=h+1e-5


def point(pos, xy):
    x,y,a=pos; c=math.cos(math.radians(a)); s=math.sin(math.radians(a))
    return [x+c*xy[0]+s*xy[1], y-s*xy[0]+c*xy[1]]


def vector(x,y):
    return pcb.VECTOR2I(round(x*1e6),round(y*1e6))


def box(item):
    b=item.GetBoundingBox()
    return [b.GetX()/1e6,b.GetY()/1e6,b.GetRight()/1e6,b.GetBottom()/1e6]


def courtyard_box(item):
    # KiCad's graphical bounding box includes line thickness. Courtyard
    # boundaries already include the component's mechanical allowance;
    # drawing ink must not add a second, stroke-dependent clearance.
    need(isinstance(item,pcb.PCB_SHAPE), 'unsupported courtyard graphic')
    r=box(item); half=item.GetWidth()/2e6
    return [r[0]+half,r[1]+half,r[2]-half,r[3]-half]


def command(args):
    p=subprocess.run(args,capture_output=True,text=True,timeout=90)
    need(p.returncode==0, 'command failed: '+str(args)+'\n'+p.stderr+p.stdout)
    return p.stdout


def upstream(project):
    c=read(local(project,CONTRACT))
    need(c.get('version') in (1,2), 'unsupported placement contract')
    archive=local(ROOT,c['upstream_toolchain']+'/tools/schematic_admission.py').parents[1]
    need(c.get('archive_files'), 'empty toolchain archive identity')
    actual={p.relative_to(archive).as_posix():sha(p) for p in archive.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    need(actual==c['archive_files'], 'upstream toolchain archive changed')
    need(sha(local(project,c['schematic_receipt']))==c['schematic_receipt_sha256'],
         'schematic receipt changed; explicit placement re-adoption required')
    need(sha(local(project,c['authority']))==c['authority_sha256'], 'placement authority changed')
    command([sys.executable,str(archive/'tools/schematic_admission.py'),'--project',str(project),'check'])
    return c


def inputs(project, name):
    data=read(local(project,name))
    need(data.get('version')==1 and data.get('boards'), 'nonempty placement input boards required')
    contract=read(local(project,CONTRACT))
    accepted=read(local(project,contract['schematic_receipt']))
    need(set(data['boards'])==set(accepted['assembly']['boards']), 'placement board scope differs from accepted assembly')
    source_contract=read(local(project,'01_docs/schematic-contract.json'))
    manifest_name=source_contract['manifest']
    manifest=read(local(project,manifest_name))
    for name in ('01_docs/schematic-contract.json',manifest_name):
        need(accepted['subjects'].get(name)==sha(local(project,name)), 'unbound schematic assembly declaration')
    for key,s in data['boards'].items():
        need(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',key), 'unsafe board id')
        intent=read(local(project,s['intent']))
        owner=manifest['boards'][key]
        need(owner.get('producer')=='imported','placement adapter currently requires imported flat schematic source')
        declaration=read(local(project,owner['source']))
        need(accepted['subjects'].get(owner['source'])==sha(local(project,owner['source'])), 'unbound board source declaration')
        need(s['intent']==declaration['intent'] and s['netlist']==owner['output']+'/native.xml',
             'board inputs differ from their accepted assembly owner: '+key)
        for bound in (s['intent'],s['netlist'],*s['footprints'].values()):
            need(accepted['subjects'].get(bound)==sha(local(project,bound)),
                 'placement input not bound by accepted schematic: '+bound)
        comps={c['ref']:c for c in intent['components'] if c.get('physical')}
        need(comps and len(comps)==sum(bool(c.get('physical')) for c in intent['components']), 'invalid part coverage')
        tree=ET.parse(local(project,s['netlist']))
        observed={c.get('ref'):c for c in tree.findall('./components/comp')}
        xmlnets={(n.get('ref'),n.get('pin')):net.get('name','').removeprefix('/')
                 for net in tree.findall('./nets/net') for n in net.findall('node')}
        s['_native_net_names']=native_net_names(list(comps.values()), tree)
        s['_native_pin_nets']=native_pin_nets(list(comps.values()), tree)
        for ref,c in comps.items():
            need(ref in observed, 'native netlist missing '+ref)
            need(observed[ref].findtext('footprint')==c['footprint'], 'netlist footprint mismatch '+ref)
            for p in c['pins']:
                if 'net' in p:
                    need(xmlnets.get((ref,p['number']))==p['net'], 'native net mismatch '+ref+'/'+p['number'])
            local(project,s['footprints'][c['footprint']])
        need(set(s['footprints'])=={c['footprint'] for c in comps.values()}, 'footprint library coverage differs')
        revisions=s.get('npth_revisions',{})
        need(isinstance(revisions,dict) and set(revisions)<=set(comps), 'unknown mechanical revision owner')
        for ref,revision in revisions.items():
            need(isinstance(revision,dict) and set(revision)=={'reason','evidence','holes'},
                 'mechanical revision needs reason/evidence/holes')
            need(isinstance(revision['reason'],str) and revision['reason'].strip() and
                 isinstance(revision['evidence'],list) and revision['evidence'], 'mechanical revision lacks evidence')
            for evidence in revision['evidence']:local(project,evidence)
            need(isinstance(revision['holes'],list) and revision['holes'], 'empty mechanical revision')
    return data


def revise_npth(footprint, holes):
    """Source recipe, not a waiver: resize identified round mechanical holes only.

    Apply before placement. Baseline library remains schematic-bound; native
    replay and a new placement review bind this recipe and its exact evidence.
    No moved/added/deleted holes, numbered pads or electrical copper are allowed.
    """
    seen=set()
    for row in holes:
        need(isinstance(row,dict) and set(row)=={'at','before_mm','after_mm',
             'before_clearance_mm','after_clearance_mm'}, 'unsupported mechanical hole edit')
        xy=row['at'];need(isinstance(xy,list) and len(xy)==2,'hole needs local XY')
        xy=tuple(number(v) for v in xy)
        need(xy not in seen,'duplicate mechanical hole edit');seen.add(xy)
        before,after=(number(row[k]) for k in ('before_mm','after_mm'))
        old_gap=None if row['before_clearance_mm'] is None else number(row['before_clearance_mm'])
        new_gap=number(row['after_clearance_mm'])
        need(before>0 and after>0 and (old_gap is None or old_gap>=0) and new_gap>=0,
             'invalid mechanical hole size/clearance')
        need(all(abs(v*1e6-round(v*1e6))<1e-6 for v in (*xy,before,after,new_gap)
                 + (() if old_gap is None else (old_gap,))),
             'mechanical revision is below native coordinate resolution')
        need(round(after*1e6)>0 and
             (round(before*1e6),None if old_gap is None else round(old_gap*1e6))!=
             (round(after*1e6),round(new_gap*1e6)), 'empty mechanical hole edit')
        matches=[pad for pad in footprint.Pads() if pad.GetPosition()==vector(*xy)]
        need(len(matches)==1,'mechanical hole missing or ambiguous')
        pad=matches[0]
        need(not pad.GetNumber() and not pad.GetNetname() and
             pad.GetAttribute()==pcb.PAD_ATTRIB_NPTH and pad.GetShape()==pcb.PAD_SHAPE_CIRCLE and
             pad.GetDrillShape()==pcb.PAD_DRILL_SHAPE_CIRCLE,'revision target is not an unnumbered round NPTH')
        need(pad.GetSize()==vector(before,before) and pad.GetDrillSize()==vector(before,before) and
             pad.GetLocalClearance()==(None if old_gap is None else round(old_gap*1e6)),
             'mechanical hole baseline differs')
        pad.SetSize(vector(after,after));pad.SetDrillSize(vector(after,after))
        pad.SetLocalClearance(round(new_gap*1e6))


def native_net_names(components, tree):
    """Preserve native namespace after intent matching; never merge /N with N."""
    nodes={}
    for net in tree.findall('./nets/net'):
        name=net.get('name');need(isinstance(name,str) and name, 'empty native net name')
        for node in net.findall('node'):
            key=(node.get('ref'),node.get('pin'))
            need(key not in nodes,'duplicate native pin membership')
            nodes[key]=name
    names={}
    for component in components:
        for pin in component['pins']:
            if 'net' not in pin:continue
            intent=pin['net'];native=nodes.get((component['ref'],pin['number']))
            need(native is not None and native.removeprefix('/')==intent,
                 'native/intent net identity differs')
            need(intent not in names or names[intent]==native,'ambiguous native namespace')
            names[intent]=native
    need(len(set(names.values()))==len(names),'merged native namespaces')
    return names


def native_pin_nets(components, tree):
    native_net_names(components,tree)
    nodes={}
    for net in tree.findall('./nets/net'):
        members=net.findall('node')
        for node in members:nodes[(node.get('ref'),node.get('pin'))]=(net.get('name'),node,len(members))
    result={}
    for component in components:
        for pin in component['pins']:
            key=(component['ref'],pin['number']);need(key in nodes,'native pin membership absent')
            name,node,count=nodes[key]
            if 'net' not in pin:
                need(pin.get('nc') is True and count==1 and name.startswith('unconnected-') and
                     'no_connect' in node.get('pintype',''),'NC pin not isolated in native schematic')
            result[key]=name
    return result


def edge_notches(b):
    """Bounded radiused edge recesses, not arbitrary polygon/outline imports."""
    w,h=map(number,b['outline']);rows=b.get('edge_notches',[])
    need(isinstance(rows,list),'edge notches must be a list')
    result=[]
    for row in rows:
        need(set(row)=={'edge','start_mm','end_mm','depth_mm','radius_mm',
                       'overhang_refs','reason','evidence'},'unsupported edge notch')
        edge=row['edge'];need(edge in ('north','east','south','west'),'invalid notch edge')
        a,z,d,r=[number(row[k]) for k in ('start_mm','end_mm','depth_mm','radius_mm')]
        length,across=(w,h) if edge in ('north','south') else (h,w)
        need(0<a<z<length and 0<r<d<across and 2*r<z-a,'invalid notch dimensions')
        need(all(abs(v*1e6-round(v*1e6))<1e-5 for v in (a,z,d,r)),
             'notch below native resolution')
        owners=row['overhang_refs']
        need(isinstance(owners,list) and all(isinstance(v,str) for v in owners) and
             len(set(owners))==len(owners) and set(owners)<=set(b['placements']),
             'unknown/duplicate notch overhang owner')
        need(isinstance(row['reason'],str) and row['reason'].strip() and
             isinstance(row['evidence'],list) and row['evidence'] and
             all(isinstance(v,str) and v for v in row['evidence']),'notch lacks evidence')
        box={'north':[a,0,z,d],'east':[w-d,a,w,z],
             'south':[w-z,h-d,w-a,h],'west':[0,h-z,d,h-a]}[edge]
        need(not any(overlap(box,other[1]) for other in result),'overlapping edge notches')
        result.append((row,box))
    return result


def outline_paths(b):
    w,h=b['outline'];notches=edge_notches(b);paths=[]
    transforms={'north':lambda t,u:(t,u),'east':lambda t,u:(w-u,t),
                'south':lambda t,u:(w-t,h-u),'west':lambda t,u:(u,h-t)}
    for edge,length in [('north',w),('east',h),('south',w),('west',h)]:
        at=0;transform=transforms[edge]
        def add(*points):paths.append([transform(*point) for point in points])
        for row,_ in sorted((pair for pair in notches if pair[0]['edge']==edge),
                            key=lambda pair:pair[0]['start_mm']):
            a,z,d,r=[row[k] for k in ('start_mm','end_mm','depth_mm','radius_mm')]
            q=r/math.sqrt(2)
            add((at,0),(a,0));add((a,0),(a,d-r))
            add((a,d-r),(a+r-q,d-r+q),(a+r,d))
            add((a+r,d),(z-r,d))
            add((z-r,d),(z-r+q,d-r+q),(z,d-r))
            add((z,d-r),(z,0));at=z
        add((at,0),(length,0))
    return paths


def validate_plan(data,plan):
    need(plan.get('version')==1 and set(plan.get('boards',{}))==set(data['boards']), 'board coverage differs')
    for key,b in plan['boards'].items():
        need(set(b)<= {'outline','layers','layer_plan','placements','mounts','blocks','notes','reservations','board_keepouts','edge_notches'}, 'unknown board plan fields')
        need(len(b['outline'])==2 and all(number(n)>0 for n in b['outline']), 'invalid outline')
        need(b['layers'] in (2,4) and isinstance(b['layer_plan'],str) and b['layer_plan'].strip(), 'layer roles required')
        refs={c['ref'] for c in data['boards'][key]['_components']}
        owners=b.get('board_keepouts',[])
        need(isinstance(owners,list) and all(isinstance(v,str) for v in owners)
             and len(set(owners))==len(owners) and set(owners)<=refs,
             'invalid board keepout owners')
        need(set(b['placements'])==refs, 'physical component membership differs: '+key)
        for ref,p in b['placements'].items():
            need(len(p)==3 and all(math.isfinite(number(n)) for n in p) and p[2] in (0,90,180,270), 'invalid placement '+ref)
        members=[r for block in b['blocks'] for r in block['members']]
        need(set(members)==refs and len(members)==len(refs), 'block membership must partition physical refs')
        need(len({x['id'] for x in b['blocks']})==len(b['blocks']), 'duplicate block id')
        for m in b['mounts']:
            need(len(m)==4 and all(math.isfinite(number(n)) for n in m) and m[3]>m[2]>0, 'invalid mounting hole')
        edge_notches(b)


def load(project,inp,plan_path):
    data=inputs(project,inp)
    for s in data['boards'].values():
        s['_components']=[c for c in read(local(project,s['intent']))['components'] if c.get('physical')]
    plan=read(local(project,plan_path)); validate_plan(data,plan)
    for b in plan['boards'].values():
        for row,_ in edge_notches(b):
            for name in row['evidence']:local(project,name)
    return data,plan


def shape(parent, layer, kind, start, end, width=.05):
    s=pcb.PCB_SHAPE(parent);s.SetShape(kind);s.SetLayer(layer)
    s.SetStart(vector(*start));s.SetEnd(vector(*end));s.SetWidth(round(width*1e6));parent.Add(s)
    return s


def board_keepouts(board, refs):
    """Move declared footprint rule areas without changing their placed geometry.

    All UUIDs must already be stable. A native board group keeps the owner and
    areas together during edits. This is a placement-owned representation change,
    not permission to remove a keepout or move a frozen component during routing.
    """
    for ref in refs:
        f=board.FindFootprintByReference(ref)
        need(f is not None, 'missing keepout owner: '+ref)
        try: zones=list(f.Zones())
        except TypeError: zones=[]  # KiCad SWIG represents an empty vector opaquely.
        need(zones and all(z.GetIsRuleArea() for z in zones), 'owner needs rule areas: '+ref)
        group=pcb.PCB_GROUP(board);group.SetName(ref+' and board-level keepouts')
        group.m_Uuid.Clone(pcb.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL,'vnext-placement/keepouts/'+ref))))
        parent=f.GetParentGroup()
        if parent: parent.RemoveItem(f)
        group.AddItem(f)
        for zone in zones:
            ident=zone.m_Uuid.AsString()
            parent=zone.GetParentGroup()
            if parent: parent.RemoveItem(zone)
            moved=pcb.ZONE(zone);moved.SetParent(board)
            moved.m_Uuid.Clone(pcb.KIID(ident))
            f.Remove(zone);board.Add(moved);group.AddItem(moved)
        board.Add(group)


def make_board(project,spec,b,target):
    board=pcb.BOARD();board.SetCopperLayerCount(b['layers'])
    nets={p['net'] for c in spec['_components'] for p in c['pins'] if 'net' in p}
    ni={}
    # Live load() supplies exact names from accepted native XML. Direct synthetic
    # fixture callers without a netlist may supply their already-native names.
    need('netlist' not in spec or '_native_net_names' in spec,'missing native namespace binding')
    names=spec.get('_native_net_names',{name:name for name in nets})
    need(set(names)==nets and len(set(names.values()))==len(nets),'native namespace coverage differs')
    pin_nets=spec.get('_native_pin_nets',{
        (c['ref'],pin['number']):names[pin['net']]
        for c in spec['_components'] for pin in c['pins'] if 'net' in pin})
    for name in sorted(set(pin_nets.values())):
        ni[name]=pcb.NETINFO_ITEM(board,name);board.Add(ni[name])
    for c in spec['_components']:
        path=local(project,spec['footprints'][c['footprint']])
        f=pcb.FootprintLoad(str(path.parent),path.stem)
        need(f is not None,'cannot load footprint '+str(path))
        if c['ref'] in spec.get('npth_revisions',{}):
            revise_npth(f,spec['npth_revisions'][c['ref']]['holes'])
        f.SetReference(c['ref']);f.SetValue(c['value']);f.SetFPIDAsString(c['footprint'])
        for k,v in c.get('fields',{}).items():
            field=pcb.PCB_FIELD(f,pcb.FIELD_T_USER,k);field.SetText(str(v));field.SetVisible(False);f.Add(field)
        envelope=spec.get('rules',{}).get('envelopes',{}).get(c['ref'])
        if envelope:
            r=rect(envelope)
            for item in list(f.GraphicalItems()):
                if item.GetLayer()==pcb.F_CrtYd:f.Remove(item)
            shape(f,pcb.F_CrtYd,pcb.SHAPE_T_RECT,r[:2],r[2:])
            shape(f,pcb.F_Fab,pcb.SHAPE_T_RECT,r[:2],r[2:])
        pins={p['number']:p for p in c['pins']}
        found=set()
        for p in f.Pads():
            no=p.GetNumber()
            if not no:
                need(p.GetAttribute()==pcb.PAD_ATTRIB_NPTH,'unnumbered electrical pad '+c['ref'])
                continue
            need(no in pins,'extra footprint pin '+c['ref']+'/'+no)
            found.add(no)
            if (c['ref'],no) in pin_nets:p.SetNet(ni[pin_nets[(c['ref'],no)]])
        need(found==set(pins),'footprint pin coverage differs '+c['ref'])
        x,y,angle=b['placements'][c['ref']]
        f.SetPosition(vector(x,y));f.SetOrientationDegrees(angle)
        # Readable placement references; values remain available as properties.
        f.Value().SetVisible(False)
        f.Reference().SetTextSize(vector(.75,.75));f.Reference().SetTextThickness(100000)
        f.Reference().SetTextAngle(pcb.EDA_ANGLE(0,pcb.DEGREES_T))
        f.Reference().SetPosition(vector(x,y-1.7))
        board.Add(f)
    for points in outline_paths(b):
        if len(points)==2:shape(board,pcb.Edge_Cuts,pcb.SHAPE_T_SEGMENT,*points)
        else:
            edge=pcb.PCB_SHAPE(board);edge.SetShape(pcb.SHAPE_T_ARC);edge.SetLayer(pcb.Edge_Cuts)
            edge.SetWidth(50000);edge.SetArcGeometry(*(vector(*point) for point in points));board.Add(edge)
    for i,(x,y,d,k) in enumerate(b['mounts']):
        f=pcb.FOOTPRINT(board);f.SetReference('MH'+str(i+1));f.SetValue('NPTH mounting')
        f.SetAttributes(pcb.FP_BOARD_ONLY | pcb.FP_EXCLUDE_FROM_BOM | pcb.FP_EXCLUDE_FROM_POS_FILES)
        p=pcb.PAD(f);p.SetAttribute(pcb.PAD_ATTRIB_NPTH);p.SetShape(pcb.PAD_SHAPE_CIRCLE)
        p.SetSize(vector(d,d));p.SetDrillSize(vector(d,d));p.SetLayerSet(pcb.LSET.AllCuMask());f.Add(p)
        shape(f,pcb.F_CrtYd,pcb.SHAPE_T_CIRCLE,[0,0],[k/2,0]);f.SetPosition(vector(x,y));board.Add(f)
    # KiCad serializes some collections by UUID. Stable identities make the
    # complete native file replayable rather than only comparing summary fields.
    for f in board.GetFootprints():
        prefix='vnext-placement/'+f.GetReference()
        f.m_Uuid.Clone(pcb.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL,prefix))))
        for group,items in [('pad',f.Pads()),('graphic',f.GraphicalItems()),('field',f.GetFields()),('zone',f.Zones())]:
            for i,item in enumerate(items):
                item.m_Uuid.Clone(pcb.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL,prefix+'/'+group+'/'+str(i)))))
        done=set()
        def group_identity(g, visiting=None):
            marker=int(g.this)
            if marker in done:return
            visiting=set() if visiting is None else visiting
            need(marker not in visiting,'cyclic footprint groups')
            for member in g.GetItems():
                if isinstance(member,pcb.PCB_GROUP):group_identity(member,visiting|{marker})
            signature='|'.join(sorted(str(member.m_Uuid.AsString()) for member in g.GetItems()))
            g.m_Uuid.Clone(pcb.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL,prefix+'/group/'+signature))))
            done.add(marker)
        for g in f.Groups():group_identity(g)
    for i,item in enumerate(board.GetDrawings()):
        item.m_Uuid.Clone(pcb.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL,'vnext-placement/edge/'+str(i)))))
    board_keepouts(board,b.get('board_keepouts',[]))
    pcb.SaveBoard(str(target),board)


def observe(path):
    board=pcb.LoadBoard(str(path));parts={}
    need(not list(board.GetTracks()) and all(z.GetIsRuleArea() for z in board.Zones()),
         'placement contains routed copper/zones')
    for f in board.GetFootprints():
        ref=f.GetReference();need(ref not in parts,'duplicate placed reference')
        bodies=[courtyard_box(g) for g in f.GraphicalItems() if g.GetLayer()==pcb.F_CrtYd]
        need(bodies,'missing courtyard '+ref)
        bounds=[min(r[0] for r in bodies),min(r[1] for r in bodies),max(r[2] for r in bodies),max(r[3] for r in bodies)]
        bounds=[round(n,6) for n in bounds]
        pads={}
        for p in f.Pads():
            pads.setdefault(p.GetNumber(),[]).append({'xy':[p.GetPosition().x/1e6,p.GetPosition().y/1e6],
                'box':box(p),'net':p.GetNetname(),'size':[p.GetSize().x/1e6,p.GetSize().y/1e6],
                'drill':[p.GetDrillSize().x/1e6,p.GetDrillSize().y/1e6]})
        parts[ref]={'box':bounds,'pads':pads,'xy':[f.GetPosition().x/1e6,f.GetPosition().y/1e6],
                    'angle':f.GetOrientationDegrees(),'footprint':f.GetFPIDAsString(),'value':f.GetValue()}
    return parts


def geometry(spec,b,parts):
    failures=[];w,h=b['outline'];rules=spec.get('rules',{})
    notches=edge_notches(b)
    refs=list(parts)
    for i,ref in enumerate(refs):
        r=parts[ref]['box']
        if not inside(r,w,h):failures.append('edge:'+ref)
        for row,removed in notches:
            if overlap(r,removed) and ref not in row['overhang_refs']:
                failures.append('notch-body:'+ref)
        for other in refs[i+1:]:
            if overlap(r,parts[other]['box']):failures.append('collision:'+ref+':'+other)
        for pads in parts[ref]['pads'].values():
            for p in pads:
                if not inside(p['box'],w,h):failures.append('pad-outside:'+ref)
                if any(overlap(p['box'],removed) for _,removed in notches):
                    failures.append('notch-pad:'+ref)
    for row in rules.get('proximity',[]):
        a,ap=row['a'];bb,bp=row['b']
        need(a in parts and bb in parts and ap in parts[a]['pads'] and bp in parts[bb]['pads'],'unknown proximity endpoint')
        d=min(math.dist(p['xy'],q['xy']) for p in parts[a]['pads'][ap] for q in parts[bb]['pads'][bp])
        limit=number(row['max_mm']);need(limit>0,'proximity budget must be positive')
        if d>limit+1e-5:failures.append('proximity:'+row['id']+':'+str(round(d,3)))
    for row in rules.get('access',[]):
        need(len(row['point'])==2 and len(row['direction'])==2,'access coordinates need two numbers')
        for v in row['point']+row['direction']:number(v)
        need(number(row['width_mm'])>0 and number(row['depth_mm'])>0 and number(row['max_gap_mm'])>=0,
             'access width/depth must be positive and gap nonnegative')
        ref=row['ref'];pos=b['placements'][ref];p=point(pos,row['point'])
        q=point([0,0,pos[2]],row['direction']);dx,dy=q
        need(abs(abs(dx)+abs(dy)-1)<1e-5 and min(abs(dx),abs(dy))<1e-5,'access direction must be cardinal unit vector')
        gap=(w-p[0] if dx>.5 else p[0] if dx<-.5 else h-p[1] if dy>.5 else p[1])
        if gap<-.05 or gap>row['max_gap_mm']:failures.append('access-edge:'+ref+':'+str(round(gap,3)))
        length=max(0,gap)+number(row['depth_mm']);half=number(row['width_mm'])/2
        r=[min(p[0],p[0]+dx*length)-(half if abs(dy)>.5 else 0),
           min(p[1],p[1]+dy*length)-(half if abs(dx)>.5 else 0),
           max(p[0],p[0]+dx*length)+(half if abs(dy)>.5 else 0),
           max(p[1],p[1]+dy*length)+(half if abs(dx)>.5 else 0)]
        for other in refs:
            if other!=ref and overlap(r,parts[other]['box']):failures.append('access-blocked:'+ref+':'+other)
    reservations=b.get('reservations',[])
    for i,row in enumerate(reservations):
        r=rect(row['rect'])
        allowed_layers=('F.Cu','B.Cu') if b.get('layers',2)==2 else ('F.Cu','In1.Cu','In2.Cu','B.Cu')
        need(row['layer'] in allowed_layers,'reservation layer unavailable in selected stack')
        if not inside(r,w,h):failures.append('reservation-outside:'+row['id'])
        if any(overlap(r,removed) for _,removed in notches):
            failures.append('reservation-notch:'+row['id'])
        owners=set(row['owner_refs']);need(owners<=set(parts),'unknown reservation owner')
        # Through-hole pads obstruct all layers; surface pads only obstruct front.
        for ref,fp in parts.items():
            if ref in owners:continue
            for pads in fp['pads'].values():
                for p in pads:
                    if (row['layer']=='F.Cu' or max(p['drill'])>0) and overlap(r,p['box']):
                        failures.append('reservation-pad:'+row['id']+':'+ref)
        for other in reservations[i+1:]:
            if row['layer']==other['layer'] and overlap(r,rect(other['rect'])):
                failures.append('reservation-conflict:'+row['id']+':'+other['id'])
    return {'physical_parts':len(spec['_components']),'mounts':len(b['mounts']),
            'proximity_checks':len(rules.get('proximity',[])),'access_checks':len(rules.get('access',[])),
            'reservation_checks':len(reservations),'failures':sorted(set(failures)),
            'verdict':'FAIL' if failures else 'PASS'}


def canonical(path):
    return re.sub(r'\(uuid\s+"?[0-9a-fA-F-]+"?\)', '(uuid OMITTED)',path.read_text())


def canonical_svg(path):
    # Plot timestamp is non-geometric metadata; retain every path/text/style.
    return re.sub(r'(<title>SVG Image created as [^<]*? date )\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\s*</title>)',
                  r'\1OMITTED\2',path.read_text())


def subjects(project,inp,plan,out):
    data=inputs(project,inp);names={inp,plan,CONTRACT}
    for b in read(local(project,plan))['boards'].values():
        for row,_ in edge_notches(b):names.update(row['evidence'])
    c=read(local(project,CONTRACT));names.update((c['authority'],c['schematic_receipt']))
    for key,s in data['boards'].items():
        names.update((s['intent'],s['netlist'],*s['footprints'].values(),*s.get('evidence',[])))
        for revision in s.get('npth_revisions',{}).values():names.update(revision['evidence'])
        names.update(f'{out}/{key}.{ext}' for ext in ('kicad_pcb','svg','json'))
    names.add(out+'/checks.json')
    return {name:sha(local(project,name)) for name in sorted(names)}


def build(project,inp,plan_name,out_name):
    data,plan=load(project,inp,plan_name);out=local(project,out_name,exists=False)
    need(not out.exists(),'refusing existing output');out.mkdir(parents=True)
    checks={}
    for key,b in plan['boards'].items():
        file=out/(key+'.kicad_pcb');make_board(project,data['boards'][key],b,file)
        observed=observe(file);checks[key]=geometry(data['boards'][key],b,observed)
        (out/(key+'.json')).write_text(json.dumps(observed,indent=2,sort_keys=True)+'\n')
        command(['kicad-cli','pcb','export','svg','--mode-single','--fit-page-to-board',
                 '--exclude-drawing-sheet','--layers','F.Cu,F.SilkS,F.Fab,Edge.Cuts',
                 '--output',str(out/(key+'.svg')),str(file)])
    (out/'checks.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
    return checks


def verify(project,inp,plan_name,out_name):
    upstream(project);data,plan=load(project,inp,plan_name);checks={}
    with tempfile.TemporaryDirectory(prefix='vnext-placement-replay-') as tmp:
        for key,b in plan['boards'].items():
            actual=local(project,out_name+'/'+key+'.kicad_pcb');fresh=Path(tmp)/(key+'.kicad_pcb')
            make_board(project,data['boards'][key],b,fresh)
            need(canonical(fresh)==canonical(actual),'native placement replay differs: '+key)
            observed=observe(actual)
            need(observed==read(local(project,out_name+'/'+key+'.json')),'observed geometry snapshot differs')
            checks[key]=geometry(data['boards'][key],b,observed)
            svg=Path(tmp)/(key+'.svg')
            command(['kicad-cli','pcb','export','svg','--mode-single','--fit-page-to-board',
                 '--exclude-drawing-sheet','--layers','F.Cu,F.SilkS,F.Fab,Edge.Cuts',
                 '--output',str(svg),str(actual)])
            need(canonical_svg(svg)==canonical_svg(local(project,out_name+'/'+key+'.svg')),'native preview differs: '+key)
    need(checks==read(local(project,out_name+'/checks.json')),'stale geometry checks')
    return {'checks':checks,'subjects':subjects(project,inp,plan_name,out_name),
            'note':'Geometry and native replay only; no global routing or physical qualification proof.'}


def certificate(project,review_name):
    need(re.fullmatch(r'08_reviews/\d{4}-\d{2}-\d{2}[^/]*-placement\.md',review_name),'dated placement review required')
    path=local(project,review_name);blocks=re.findall(r'```json\s*\n(.*?)\n```',path.read_text(),re.S)
    need(len(blocks)==1,'one JSON review block required');r=json.loads(blocks[0],object_pairs_hook=pairs)
    need(r['schema']==1 and r['stage']=='KICAD-PLACEMENT' and r['verdict']=='PASS','placement review not PASS')
    need(r['author'].strip() and r['reviewer'].strip() and r['author'].strip().casefold()!=r['reviewer'].strip().casefold(),'independent reviewer required')
    result=verify(project,r['inputs'],r['plan'],r['output'])
    need(all(c['verdict']=='PASS' for c in result['checks'].values()),'placement geometry has failures')
    need(set(r['checks'])==CRITERIA,'review criteria differ')
    for p,h in r['subjects'].items():need(sha(local(project,p))==h,'stale review subject: '+p)
    need(result['subjects'].items()<=r['subjects'].items(),'review lacks producer subjects')
    for key,c in r['checks'].items():
        need(c['verdict']=='PASS' and c['rationale'].strip() and c['evidence'] and
             all(p in r['subjects'] for p in c['evidence']),'incomplete review criterion '+key)
    import critical_routes
    critical_routes.verify(project,r,{key:r['output']+'/'+key+'.kicad_pcb'
                                     for key in result['checks']})
    stages=read(ROOT/'skills/pcb-design/workflow/graph.json')['stages']
    specs=[s['spec'] for s in stages if s['spec']['id']=='KICAD-PLACEMENT']
    need(len(specs)==1 and specs[0]['requires']==['schematic_reviewed'] and
         specs[0]['produces']==['placement_reviewed'],'placement graph contract differs')
    return {'schema':1,'role':'placement_reviewed','stage':'KICAD-PLACEMENT','review':review_name,
            'stage_spec':specs[0],
            'review_sha256':sha(path),'subjects':r['subjects'],'checks':result['checks'],
            'tool_sha256':sha(Path(__file__)),'kicad_version':pcb.Version(),
            'critical_routes_tools':critical_routes.tool_identities(),
            'instruction_sha256':sha(ROOT/'skills/pcb-design/workflow/stages/placement.md'),
            'manual_sha256':sha(ROOT/'skills/pcb-design/procedures/placement/tooling.md')}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['build','verify','issue','check'])
    p.add_argument('--project',type=Path,required=True)
    for arg in ('inputs','plan','output','review','receipt'):p.add_argument('--'+arg)
    a=p.parse_args();project=a.project.resolve()
    try:
        if a.action in ('build','verify'):
            need(not a.receipt,'receipt path is only for issue/check')
            need(a.inputs and a.plan and a.output,'inputs/plan/output required')
            result=(build if a.action=='build' else verify)(project,a.inputs,a.plan,a.output)
        elif a.action=='issue':
            result=certificate(project,a.review);target=local(project,a.receipt or RECEIPT,exists=False)
            need(not target.exists(),'refusing existing placement receipt')
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        else:
            old=read(local(project,a.receipt or RECEIPT));result=certificate(project,old['review'])
            need(result==old,'stale placement receipt')
        print(json.dumps(result,indent=2,sort_keys=True));return 0
    except (ValueError,KeyError,TypeError,OSError,ET.ParseError,subprocess.TimeoutExpired) as e:
        print('Placement refused: '+str(e),file=sys.stderr);return 1


if __name__=='__main__':sys.exit(main())
