#!/usr/bin/env python3
"""Shared short-path/prefix proof: native saved text and hostile topology.

The pod's original policy fixtures also run unchanged through its compatibility
entry point. New cases exercise exact four-layer carrier-style geometry and
longer parallel bypasses, where shortest-path inclusion alone would pass.
"""
from pathlib import Path
import copy
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from harness import check,eq,test,main,tmpdir,must_pass,must_fail,run,KPY,SCRIPTS
sys.path.insert(0,str(SCRIPTS))
import critical_path_check as gate
import yaml

CONFIG={'schema':1,'layers':['F.Cu','In1.Cu','In2.Cu','B.Cu'],'stackup_mm':[.2104,1.065,.2104],
        'short_paths':[{'from':'J1.5','to':'U1.3','max_length_mm':4.2,'layer':'B.Cu','max_pad_centre_mm':4.,'why':'connector entry clamp'}],
        'prefixes':[{'from':'J1.5','through':'U1.3','targets':['C1.1'],'why':'coupling after clamp'}]}

def board(segments=None, extra='', clamp_x=2):
    if segments is None:segments=[(0,0,clamp_x,0),(clamp_x,0,6,0)]
    s='(kicad_pcb\n\t(layers\n\t\t(0 "F.Cu" signal)\n\t\t(4 "In1.Cu" signal)\n\t\t(6 "In2.Cu" signal)\n\t\t(2 "B.Cu" signal)\n\t)\n'
    for ref,pin,x in [('J1','5',0),('U1','3',clamp_x),('C1','1',6)]:
        s+=f'\t(footprint "test:pad"\n\t\t(layer "B.Cu")\n\t\t(at {x} 0)\n\t\t(property "Reference" "{ref}")\n\t\t(pad "{pin}" smd rect (at 0 0) (size 0.4 0.4) (layers "B.Cu") (net 1 "AUDIO"))\n\t)\n'
    for a,b,c,d in segments:
        s+=f'\t(segment (start {a} {b}) (end {c} {d}) (width 0.2) (layer "B.Cu") (net "AUDIO"))\n'
    return s+extra+'\n)\n'

def invoke(text=None,config=None):
    d=tmpdir();(d/'b.kicad_pcb').write_text(text or board());(d/'policy.yaml').write_text(yaml.safe_dump(config or CONFIG))
    return run([KPY,str(SCRIPTS/'critical_path_check.py'),str(d/'b.kicad_pcb'),'--config',str(d/'policy.yaml'),'--json',str(d/'report.json')])

def reject_config(data):
    try:gate.validate_config(data)
    except gate.AuditError:return
    raise AssertionError('bad configuration accepted')

@test('shared path checker accepts an exact four-layer branch-after-clamp board')
def clean():
    r=invoke();must_pass(r, "critical-path fixture");check('R-CRITICAL-PATH PASS: 2 graded' in r.out,r.out)

@test('short-path checker rejects excess length and pad span',kind='known_bad')
def long():
    r=invoke(board(clamp_x=4.3));must_fail(r, "critical-path fixture");check('exceeds' in r.out,r.out)

@test('short-path checker rejects wrong layer',kind='known_bad')
def wrong_layer():
    r=invoke(board().replace('(layer "B.Cu") (net "AUDIO")','(layer "F.Cu") (net "AUDIO")'));must_fail(r, "critical-path fixture")

@test('prefix checker rejects branch before clamp',kind='known_bad')
def bypass():
    r=invoke(board([(0,0,1,0),(1,0,2,0),(1,0,1,1),(1,1,6,1),(6,1,6,0)]));must_fail(r, "critical-path fixture");check('branches before' in r.out,r.out)

@test('prefix checker rejects longer parallel bypass despite shortest-path inclusion',kind='known_bad')
def longer_bypass():
    r=invoke(board([(0,0,1,0),(1,0,2,0),(2,0,6,0),(1,0,1,2),(1,2,6,2),(6,2,6,0)]));must_fail(r, "critical-path fixture");check('parallel copper' in r.out,r.out)

@test('unsplit tee cannot silently escape prefix graph',kind='known_bad')
def unsplit():
    r=invoke(board([(0,0,2,0),(2,0,6,0),(1,0,1,2),(1,2,6,2),(6,2,6,0)]));must_fail(r, "critical-path fixture");check('unsplit' in r.out,r.out)

@test('unrepresented graded-net zones are rejected',kind='known_bad')
def zone():
    r=invoke(board(extra='\t(zone (net_name "AUDIO") (layer "B.Cu"))'));must_fail(r, "critical-path fixture");check('zone copper' in r.out,r.out)

@test('critical path missing copper cannot pass',kind='known_bad')
def no_copper():
    must_fail(invoke(board([])), "critical-path fixture")

@test('empty, duplicate, unknown and nonfinite config are rejected',kind='known_bad')
def config_cases():
    for mutate in [lambda d:d.update(short_paths=[]),lambda d:d['short_paths'].append(copy.deepcopy(d['short_paths'][0])),lambda d:d.update(unknown=True),lambda d:d['short_paths'][0].update(max_length_mm=float('nan')),lambda d:d['prefixes'][0].update(targets=[]),lambda d:d.update(stackup_mm=[1.6])]:
        d=copy.deepcopy(CONFIG);mutate(d);reject_config(d)

@test('component clamp failure is outside geometric path proof',kind='vacuity',gate='critical_path_check.py')
def physical_clamp_vacuity():
    # Mark a failed-open physical device without altering its copper. Geometry
    # is still valid; changing its routed prefix to a bypass supplies contrast.
    must_pass(invoke(board(extra='\t(property "physical_U1_status" "failed-open")')), "critical-path fixture")
    must_fail(invoke(board([(0,0,1,0),(1,0,2,0),(1,0,1,1),(1,1,6,1),(6,1,6,0)])), "critical-path fixture")

def native_pad_fixture(offset=.4, bypass=True, transform=None, serialize=None):
    """Independent reviewer geometry reproduced through pcbnew save/reopen.

    The 1 mm connector land touches the longer route between its endpoints.
    offset=.4 crosses its interior; .55 touches only via track half-width.
    Original shared checker falsely passed both with native two-track contact.
    """
    import pcbnew
    d=tmpdir();b=pcbnew.BOARD();b.SetCopperLayerCount(2)
    net=pcbnew.NETINFO_ITEM(b,'AUDIO');b.Add(net)
    for ref,num,x,size in [('J1','5',10,1.),('U1','3',12,.4),('C1','1',16,.4)]:
        f=pcbnew.FOOTPRINT(b);f.SetReference(ref);f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(10)));b.Add(f)
        p=pcbnew.PAD(f);p.SetNumber(num);p.SetAttribute(pcbnew.PAD_ATTRIB_SMD);p.SetShape(pcbnew.PAD_SHAPE_RECT);p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(size),pcbnew.FromMM(size)))
        ls=pcbnew.LSET();ls.AddLayer(pcbnew.B_Cu);p.SetLayerSet(ls);p.SetPosition(f.GetPosition());p.SetNet(net);f.Add(p)
    segments=[(10,10,12,10),(12,10,16,10)]
    if bypass:segments.extend([(9,10+offset,11,10+offset),(11,10+offset,11,12),(11,12,16,12),(16,12,16,10)])
    for a,y,c,z in segments:
        t=pcbnew.PCB_TRACK(b);t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a),pcbnew.FromMM(y)));t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(c),pcbnew.FromMM(z)));t.SetLayer(pcbnew.B_Cu);t.SetWidth(pcbnew.FromMM(.2));t.SetNet(net);b.Add(t)
    verify=transform(b,net) if transform else None
    path=d/'board.kicad_pcb';pcbnew.SaveBoard(str(path),b)
    if serialize:path.write_text(serialize(path.read_text()))
    native=pcbnew.LoadBoard(str(path));native.BuildConnectivity()
    if verify:verify(native)
    pad=next(p for f in native.GetFootprints() if f.GetReference()=='J1' for p in f.Pads())
    eq(len(native.GetConnectivity().GetConnectedTracks(pad)),2 if bypass else 1,'native connector track census')
    cfg=copy.deepcopy(CONFIG);cfg['layers']=['F.Cu','B.Cu'];cfg['stackup_mm']=[1.6]
    (d/'policy.yaml').write_text(yaml.safe_dump(cfg))
    return run([KPY,str(SCRIPTS/'critical_path_check.py'),str(path),'--config',str(d/'policy.yaml')])

@test('native pad-center tree retains correct acceptance')
def native_clean():
    must_pass(native_pad_fixture(bypass=False), 'native ordinary clamp tree')

@test('native pad-interior bypass cannot escape endpoint graph',kind='known_bad')
def native_pad_interior():
    # RED against the frozen source reviewed at 18:39Z: native two tracks,
    # shared false PASS. GREEN requires represented or refused contact.
    must_fail(native_pad_fixture(.4), 'native pad-interior bypass',expect='pad')

@test('native pad-width-only bypass cannot escape endpoint graph',kind='known_bad')
def native_pad_width():
    must_fail(native_pad_fixture(.55), 'native pad-width-only bypass',expect='pad')

@test('native absolute pad angle rejects false contact after footprint rotation',kind='known_bad',gate='copper_length_audit.py')
def native_pad_angle():
    # RED against 01fab37b read_pad_shapes: footprint angle was added twice.
    # Native square pads or only 0/180 rotations would hide the defect.
    import pcbnew
    import copper_length_audit as copper
    V=lambda x,y:pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
    discriminated=False
    for angle in (0,90,180,270):
        b=pcbnew.BOARD();b.SetCopperLayerCount(2);net=pcbnew.NETINFO_ITEM(b,'AUDIO');b.Add(net)
        f=pcbnew.FOOTPRINT(b);f.SetReference('J1');f.SetPosition(V(10,10));b.Add(f)
        p=pcbnew.PAD(f);p.SetNumber('5');p.SetAttribute(pcbnew.PAD_ATTRIB_SMD);p.SetShape(pcbnew.PAD_SHAPE_RECT);p.SetSize(V(1,.4));ls=pcbnew.LSET();ls.AddLayer(pcbnew.B_Cu);p.SetLayerSet(ls);p.SetPosition(f.GetPosition());p.SetNet(net);f.Add(p);f.SetOrientationDegrees(angle)
        path=tmpdir()/'rotated.kicad_pcb';pcbnew.SaveBoard(str(path),b);native=pcbnew.LoadBoard(str(path));pad=next(p for f in native.GetFootprints() for p in f.Pads())
        raw=copper.read_pad_shapes(path.read_text())['AUDIO'][0]
        for x,y in [(10.4,10),(10,10.4),(9.6,10),(10,9.6)]:
            hit=bool(pad.HitTest(V(x,y)))
            if angle==90 and x==10.4:
                check(not hit,'native false-contact control must discriminate')
                bad=dict(raw,angle=180.)
                check(copper._point_in_pad(bad,x,y),'old double-rotation must hit wrong arm')
                discriminated=True
            eq(copper._point_in_pad(raw,x,y),hit,f'pad contact angle={angle} point={(x,y)}')
    check(discriminated,'rotation fixture must exercise false hit at90 degrees')


def native_contact_case(case, serialize=None):
    """Native controls reproduced from the independent frozen-source review.

    These cases went RED against that frozen checker. Native contacts are
    asserted before asking the independently parsed-text gate to refuse them.
    """
    import pcbnew
    V=lambda x,y:pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
    b=pcbnew.BOARD();b.SetCopperLayerCount(4 if case in ('interior_via','interior_pad') else 2)
    net=pcbnew.NETINFO_ITEM(b,'AUDIO');b.Add(net)
    def pad(ref,num,x,y,size=1.,through=False,rounded=False):
        f=pcbnew.FOOTPRINT(b);f.SetReference(ref);f.SetPosition(V(x,y));b.Add(f)
        p=pcbnew.PAD(f);p.SetNumber(num);p.SetAttribute(pcbnew.PAD_ATTRIB_PTH if through else pcbnew.PAD_ATTRIB_SMD)
        p.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT if rounded else pcbnew.PAD_SHAPE_RECT);p.SetSize(V(size,size))
        ls=pcbnew.LSET();ls.AddLayer(pcbnew.B_Cu);p.SetLayerSet(ls);p.SetPosition(f.GetPosition());p.SetNet(net)
        if through:p.SetDrillSize(V(.3,.3));p.SetLayerSet(pcbnew.LSET.AllCuMask())
        if rounded:p.SetRoundRectRadiusRatio(.25)
        f.Add(p)
    def track(a,y,c,z,layer=pcbnew.B_Cu,width=.2):
        t=pcbnew.PCB_TRACK(b);t.SetStart(V(a,y));t.SetEnd(V(c,z));t.SetLayer(layer);t.SetWidth(pcbnew.FromMM(width));t.SetNet(net);b.Add(t)
    def via(x,y):
        v=pcbnew.PCB_VIA(b);v.SetPosition(V(x,y));v.SetWidth(pcbnew.FromMM(.4));v.SetDrill(pcbnew.FromMM(.2));v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu);v.SetNet(net);b.Add(v)
    pad('J1','5',10,10,rounded=case=='roundrect')
    pad('U1','3',12,10,.4)
    pad('C1','1',10 if case=='overlap' else 16,10.8 if case=='overlap' else 10,
        1. if case in ('overlap','offcenter_pth') else .4,through=case in ('via_pad','interior_via','offcenter_pth'))
    if case=='roundrect':track(10.47,10.47,12,10,width=.02);track(12,10,16,10,width=.02)
    elif case=='overlap':
        for t in [(10,10,12,10),(12,10,13,10),(13,10,13,12),(13,12,10,12),(10,12,10,10.8)]:track(*t)
    elif case=='via_pad':
        track(10,10,12,10);track(12,10,16,10);via(10,10.6)
        track(10,10.6,16,10.6,pcbnew.F_Cu);track(16,10.6,16,10,pcbnew.F_Cu)
    elif case=='interior_pad':
        track(10,10,11,10);track(11,10,12,10);track(12,10,16,10)
        track(11,10,11,12);track(16,10,16,12);via(11,12);via(16,12)
        pad('TP1','1',13.5,12)
        ip=next(p for f in b.GetFootprints() if f.GetReference()=='TP1' for p in f.Pads())
        ip.SetSize(V(6,.6));ls=pcbnew.LSET();ls.AddLayer(pcbnew.In1_Cu);ip.SetLayerSet(ls)
    else:
        track(10,10,11,10);track(11,10,12,10);track(12,10,16,10)
        track(11,10,11,12);via(11,12)
        layer=pcbnew.In1_Cu if case=='interior_via' else pcbnew.F_Cu
        track(11,12,16,12,layer);track(16,12,16,10.4 if case=='offcenter_pth' else 10,layer)
    path=tmpdir()/'native.kicad_pcb';pcbnew.SaveBoard(str(path),b)
    if serialize:path.write_text(serialize(path.read_text()))
    native=pcbnew.LoadBoard(str(path));native.BuildConnectivity();conn=native.GetConnectivity()
    pads={f.GetReference():next(iter(f.Pads())) for f in native.GetFootprints()}
    if case=='roundrect':eq(len(conn.GetConnectedTracks(pads['J1'])),0,'native rounded corner is disconnected')
    elif case=='overlap':eq(len(conn.GetConnectedPads(pads['J1'])),1,'native overlapping lands are connected')
    elif case=='via_pad':eq(len(conn.GetConnectedTracks(pads['J1'])),2,'native pad contacts track and via')
    elif case=='interior_pad':
        eq(len(conn.GetConnectedTracks(pads['TP1'])),2,'native internal land bridges both through vias')
        eq(len(conn.GetConnectedTracks(pads['C1'])),2,'native downstream branch reaches bridge')
    else:
        eq(len(conn.GetConnectedTracks(pads['C1'])),2,'native plated land connects both layers')
        v=next(t for t in native.GetTracks() if isinstance(t,pcbnew.PCB_VIA))
        eq(len(conn.GetConnectedTracks(v)),2,'native via connects both branch tracks')
    cfg=copy.deepcopy(CONFIG)
    if case not in ('interior_via','interior_pad'):cfg['layers']=['F.Cu','B.Cu'];cfg['stackup_mm']=[1.6]
    policy=path.with_suffix('.yaml');policy.write_text(yaml.safe_dump(cfg))
    return run([KPY,str(SCRIPTS/'critical_path_check.py'),str(path),'--config',str(policy)])

@test('native via annulus touching land cannot hide a bypass',kind='known_bad')
def native_via_pad():must_fail(native_contact_case('via_pad'),'native via-pad bypass',expect='pad-via')

@test('native overlapping lands cannot hide a bypass',kind='known_bad')
def native_overlap():must_fail(native_contact_case('overlap'),'native land overlap',expect='distinct pads')

@test('native rounded pad corner cannot invent a connection',kind='known_bad')
def native_roundrect():must_fail(native_contact_case('roundrect'),'native rounded corner',expect='rounded-corner')

@test('native through via interior layer cannot hide a bypass',kind='known_bad')
def native_interior_via():must_fail(native_contact_case('interior_via'),'native interior via layer',expect='interior via-layer')

@test('native through vias bridged by an internal pad cannot hide a bypass',kind='known_bad')
def native_interior_pad():must_fail(native_contact_case('interior_pad'),'native internal pad bridge',expect='interior via-pad')

@test('native off-center plated land cannot hide a barrel transition',kind='known_bad')
def native_offcenter_pth():must_fail(native_contact_case('offcenter_pth'),'native off-center PTH',expect='PTH layer transition')


def native_pad_modifier(kind, serialize=None):
    # Independent second review found both classes falsely accepted after the
    # first geometry fix. Verify disconnected copper through native KiCad.
    import pcbnew
    V=lambda x,y:pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
    b=pcbnew.BOARD();b.SetCopperLayerCount(2);net=pcbnew.NETINFO_ITEM(b,'AUDIO');b.Add(net)
    for ref,num,x,size in [('J1','5',10,1.),('U1','3',12,.4),('C1','1',16,.4)]:
        f=pcbnew.FOOTPRINT(b);f.SetReference(ref);f.SetPosition(V(x,10));b.Add(f)
        p=pcbnew.PAD(f);p.SetNumber(num);p.SetAttribute(pcbnew.PAD_ATTRIB_SMD);p.SetShape(pcbnew.PAD_SHAPE_RECT)
        p.SetSize(V(size,size));ls=pcbnew.LSET();ls.AddLayer(pcbnew.B_Cu);p.SetLayerSet(ls);p.SetPosition(f.GetPosition());p.SetNet(net);f.Add(p)
        if ref=='J1':
            if kind=='chamfer':p.SetShape(pcbnew.PAD_SHAPE_CHAMFERED_RECT);p.SetChamferRectRatio(.5);p.SetChamferPositions(15)
            else:p.SetOffset(V(0,1.))
    for a,y,c,z in [(10.34 if kind=='chamfer' else 10,10.34 if kind=='chamfer' else 10,12,10),(12,10,16,10)]:
        t=pcbnew.PCB_TRACK(b);t.SetStart(V(a,y));t.SetEnd(V(c,z));t.SetLayer(pcbnew.B_Cu);t.SetWidth(pcbnew.FromMM(.2));t.SetNet(net);b.Add(t)
    path=tmpdir()/'modifier.kicad_pcb';pcbnew.SaveBoard(str(path),b)
    if serialize:path.write_text(serialize(path.read_text()))
    n=pcbnew.LoadBoard(str(path));n.BuildConnectivity()
    pad=next(p for f in n.GetFootprints() if f.GetReference()=='J1' for p in f.Pads())
    eq(len(n.GetConnectivity().GetConnectedTracks(pad)),0,'native modified pad is disconnected')
    cfg=copy.deepcopy(CONFIG);cfg['layers']=['F.Cu','B.Cu'];cfg['stackup_mm']=[1.6]
    policy=path.with_suffix('.yaml');policy.write_text(yaml.safe_dump(cfg))
    return run([KPY,str(SCRIPTS/'critical_path_check.py'),str(path),'--config',str(policy)])

@test('native chamfer modifiers cannot be mistaken for a filled rounded land',kind='known_bad')
def native_chamfer():must_fail(native_pad_modifier('chamfer'),'native chamfer false connection',expect='unsupported pad geometry')

@test('native offset copper cannot be mistaken for the pad anchor',kind='known_bad')
def native_offset():must_fail(native_pad_modifier('offset'),'native offset false connection',expect='unsupported pad geometry')


def graphic_transform(copper=True):
    import pcbnew
    V=lambda x,y:pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
    def produce(b,net):
        for a,z in [((10,10),(10,12)),((10,12),(16,12)),((16,12),(16,10))]:
            shape=pcbnew.PCB_SHAPE(b);shape.SetShape(pcbnew.SHAPE_T_SEGMENT);shape.SetStart(V(*a));shape.SetEnd(V(*z));shape.SetWidth(pcbnew.FromMM(.2))
            shape.SetLayer(pcbnew.B_Cu if copper else pcbnew.F_SilkS)
            if copper:shape.SetNet(net)
            b.Add(shape)
        def verify(n):
            shapes=list(n.GetDrawings());eq(len(shapes),3,'native graphic census')
            if copper:
                c=n.GetConnectivity()
                eq(sorted(len(c.GetConnectedPads(x)) for x in shapes),[0,1,1],'native graphics touch both end lands')
                eq(sorted(len(c.GetConnectedTracks(x)) for x in shapes),[0,1,1],'native graphics touch end tracks')
                points=lambda v:(pcbnew.ToMM(v.x),pcbnew.ToMM(v.y))
                adj={}
                for x in shapes:
                    a,z=points(x.GetStart()),points(x.GetEnd());adj.setdefault(a,[]).append(z);adj.setdefault(z,[]).append(a)
                todo=[(10.,10.)];seen=set(todo)
                while todo:
                    for node in adj[todo.pop()]:
                        if node not in seen:seen.add(node);todo.append(node)
                check((16.,10.) in seen and (12.,10.) not in seen,'native graphic path must bypass clamp')
        return verify
    return produce

@test('native copper graphics cannot hide a bypass; silk is not copper',kind='known_bad')
def native_copper_graphics():
    must_pass(native_pad_fixture(bypass=False,transform=graphic_transform(False)),'ordinary silk graphics')
    must_fail(native_pad_fixture(bypass=False,transform=graphic_transform()),'native copper graphic bypass',expect='copper graphics')

def quantized_transform(width):
    import pcbnew
    V=lambda x,y:pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
    def produce(b,net):
        t=next(t for t in b.GetTracks() if t.GetStart()==V(10,10));t.SetEnd(V(10.9998,10));t.SetWidth(pcbnew.FromMM(width))
        u=pcbnew.PCB_TRACK(b);u.SetStart(V(11.0002,10));u.SetEnd(V(12,10));u.SetLayer(pcbnew.B_Cu);u.SetWidth(pcbnew.FromMM(width));u.SetNet(net);b.Add(u)
        def verify(n):
            first=next(t for t in n.GetTracks() if t.GetStart()==V(10,10))
            eq(len(n.GetConnectivity().GetConnectedTracks(first)),0 if width==.0001 else 1,'native gap/overlap must discriminate graph quantization')
        return verify
    return produce

@test('graph rounding must not close a native copper gap',kind='known_bad')
def native_quantized_gap():
    # Deliberately below manufacturing floors: this checker cannot silently
    # rely on a downstream DRC width gate it does not run. RED on prior code.
    must_fail(native_pad_fixture(bypass=False,transform=quantized_transform(.0001)),'native quantized gap',expect='quantization merges')

@test('safe submicrometre endpoint rounding retains native connected copper')
def native_quantized_overlap():
    must_pass(native_pad_fixture(bypass=False,transform=quantized_transform(.2)),'native safely overlapping endpoints')

@test('ordinary via after clamp and a plated target remain admitted')
def native_downstream_via():
    import pcbnew
    V=lambda x,y:pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
    def produce(b,net):
        last=next(t for t in b.GetTracks() if t.GetStart()==V(12,10));b.Remove(last)
        pad=next(p for f in b.GetFootprints() if f.GetReference()=='C1' for p in f.Pads())
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH);pad.SetDrillSize(V(.2,.2));pad.SetLayerSet(pcbnew.LSET.AllCuMask())
        for a,z,layer in [(12,14,pcbnew.B_Cu),(14,16,pcbnew.F_Cu)]:
            t=pcbnew.PCB_TRACK(b);t.SetStart(V(a,10));t.SetEnd(V(z,10));t.SetWidth(pcbnew.FromMM(.2));t.SetLayer(layer);t.SetNet(net);b.Add(t)
        v=pcbnew.PCB_VIA(b);v.SetPosition(V(14,10));v.SetWidth(pcbnew.FromMM(.4));v.SetDrill(pcbnew.FromMM(.2));v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu);v.SetNet(net);b.Add(v)
        def verify(n):
            via=next(t for t in n.GetTracks() if isinstance(t,pcbnew.PCB_VIA))
            eq(len(n.GetConnectivity().GetConnectedTracks(via)),2,'native downstream via joins both layers')
        return verify
    must_pass(native_pad_fixture(bypass=False,transform=produce),'native downstream layer transition')

@test('equivalent whitespace keeps the same physical item visible')
def hidden_serialization():
    text=board().replace('\t(segment (start 2 0)', '    (segment (start 2 0)')
    must_pass(invoke(text),'equivalent track serialization')


def net_spelling(ref, variant):
    # Only serialization changes. KiCad reload/connectivity assertions in the
    # fixture run AFTER this mutation, independently of the checked parser.
    def rewrite(text):
        import re
        pattern=r'\(footprint\b'
        # Balanced object extraction is test setup, not the native oracle.
        for tag, body in list(gate.syntax_blocks(text)):
            if tag=='footprint' and f'"{ref}"' in body:
                changed=body.replace('(net "AUDIO")',variant)
                check(changed!=body,'fixture must change exact selected net spelling')
                return text.replace(body,changed)
        raise AssertionError('selected native footprint missing')
    return rewrite

@test('native bare graphic layer still blocks a copper bypass',kind='known_bad')
def native_bare_graphic_layer():
    must_fail(native_pad_fixture(bypass=False,transform=graphic_transform(),
        serialize=lambda s:s.replace('(layer "B.Cu")','(layer B.Cu)')),
        'bare-layer native copper bypass',expect='copper graphics')

@test('native pad modifiers remain blocked with spaced and numbered nets',kind='known_bad')
def native_modifier_net_dialects():
    # Four independent third-review false PASS cases. RED before AST fix.
    for shape in ('chamfer','offset'):
        for value in ('(net "AUDIO" )','(net 1 "AUDIO")'):
            must_fail(native_pad_modifier(shape,net_spelling('J1',value)),
                f'{shape} {value}',expect='unsupported pad geometry')

@test('native internal pad bridges remain visible with bare or spaced nets',kind='known_bad')
def native_bridge_net_dialects():
    for value in ('(net AUDIO)','(net "AUDIO"\n)'):
        must_fail(native_contact_case('interior_pad',net_spelling('TP1',value)),
            f'internal pad {value}',expect='interior via-pad')

@test('ordinary native paths tolerate equivalent net/layer/whitespace spelling')
def native_equivalent_syntax():
    for value in ('(net AUDIO)','(net "AUDIO" )','(net 1 "AUDIO")'):
        def rewrite(s):
            return net_spelling('J1',value)(s).replace('(layer "B.Cu")','(layer B.Cu)').replace('\t','   ')
        must_pass(native_pad_fixture(bypass=False,serialize=rewrite),'native equivalent clean path')

@test('native strings are opt-in; existing rule parser stays strict',kind='known_bad')
def strict_tokenizer_compatibility():
    from land_witness import sexpressions,Unsupported
    text='(property "Value" "quoted \\\"text\\\"")'
    try:sexpressions(text)
    except Unsupported:pass
    else:raise AssertionError('default rule-language parser accepted escape')
    forms=sexpressions(text,allow_escaped_strings=True)
    eq(forms[0][2].text,'quoted "text"','native escaped metadata decoded')

@test('complete board syntax and unambiguous geometry are mandatory',kind='known_bad')
def ast_complete_geometry():
    for text in (board()+')',board()+' (net "ORPHAN")',
                 board().replace('(at 0 0)','(at 0 0) (at 100 100)',1),
                 board().replace('(net 1 "AUDIO")','(net 1 "DIFFERENT")',1)):
        must_fail(invoke(text),'ambiguous or incomplete board syntax')


@test('stackup layers and escaped display metadata do not become geometry')
def full_board_metadata():
    import json
    text=board(extra='(setup (stackup (layer "F.Cu" (type "copper") (thickness 0.035)) (layer "B.Cu" (type "copper") (thickness 0.035))))')
    text=text.replace('(property "Reference" "J1")','(property "Value" '+json.dumps('quoted "display"')+' (at 100 200)) (property "Reference" "J1")')
    must_pass(invoke(text),'native metadata and repeated stackup layers')


def native_identity_case(case):
    """Native identity oracle independent of the analysis decoder.

    Fourth review exposed valid KiCad literals which JSON decoded into other
    nets/references/pad numbers. Every hostile case went RED on frozen AST.
    """
    import pcbnew
    V=lambda x,y:pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
    b=pcbnew.BOARD();b.SetCopperLayerCount(2)
    netname='AU/DIO' if case=='slash_net' else 'AUDIO'
    net=pcbnew.NETINFO_ITEM(b,netname);b.Add(net)
    for ref,num,x,size in [('J1','5',10,1.),('U1','3',12,.4),('C1','1',16,.4)]:
        f=pcbnew.FOOTPRINT(b);f.SetReference(ref);f.SetPosition(V(x,10));b.Add(f)
        if case=='metadata':f.SetValue('display "quote" and \\ path')
        p=pcbnew.PAD(f);p.SetNumber(num);p.SetAttribute(pcbnew.PAD_ATTRIB_SMD);p.SetShape(pcbnew.PAD_SHAPE_RECT);p.SetSize(V(size,size))
        ls=pcbnew.LSET();ls.AddLayer(pcbnew.B_Cu);p.SetLayerSet(ls);p.SetPosition(f.GetPosition());p.SetNet(net);f.Add(p)
    for a,z in [(10,12),(12,16)]:
        t=pcbnew.PCB_TRACK(b);t.SetStart(V(a,10));t.SetEnd(V(z,10));t.SetWidth(pcbnew.FromMM(.2));t.SetLayer(pcbnew.B_Cu);t.SetNet(net);b.Add(t)
    path=tmpdir()/'identity.kicad_pcb';pcbnew.SaveBoard(str(path),b);text=path.read_text()
    replacements={
        'unicode_net':('(net "AUDIO")',r'(net "\u0041UDIO")'),
        'slash_net':('(net "AU/DIO")',r'(net "AU\/DIO")'),
        'reference':('(property "Reference" "J1"',r'(property "Reference" "\u004a1"'),
        'property_key':('(property "Reference" "J1"',r'(property "\u0052eference" "J1"'),
        'pad_number':('(pad "5"',r'(pad "\u0035"'),
    }
    if case in replacements:
        old,new=replacements[case]
        # Native formatting puts property fields on separate lines. Mutate
        # those exact scalar tokens independent of AST canonicalization.
        for tag,body in list(gate.syntax_blocks(text)):
            if tag=='footprint' and '"J1"' in body:
                if case in ('reference','property_key'):
                    old,new=(('"J1"',r'"\u004a1"') if case=='reference' else ('"Reference"',r'"\u0052eference"'))
                changed=body.replace(old,new,1);check(changed!=body,'native identity fixture must change spelling');text=text.replace(body,changed);break
        else:raise AssertionError('native J1 footprint missing')
        path.write_text(text)
    native=pcbnew.LoadBoard(str(path));native.BuildConnectivity();fps={f.GetReference():f for f in native.GetFootprints()}
    if case in ('unicode_net','slash_net'):
        j=next(iter(fps['J1'].Pads()));u=next(iter(fps['U1'].Pads()))
        eq(j.GetNetname(),r'\u0041UDIO' if case=='unicode_net' else r'AU\/DIO','native literal net identity')
        check(j.GetNetname()!=u.GetNetname(),'native nets must remain distinct')
    elif case=='reference':
        check('J1' not in fps and r'\u004a1' in fps,'native literal reference differs from requested endpoint')
    elif case=='property_key':
        check('J1' not in fps,'native escaped property key must not create Reference')
    elif case=='pad_number':
        eq(next(iter(fps['J1'].Pads())).GetNumber(),r'\u0035','native literal pad number')
    else:
        eq(fps['J1'].GetValue(),'display "quote" and \\ path','native escaped display metadata')
        eq(len(native.GetConnectivity().GetConnectedTracks(next(iter(fps['J1'].Pads())))),1,'native clean metadata contact')
    cfg=copy.deepcopy(CONFIG);cfg['layers']=['F.Cu','B.Cu'];cfg['stackup_mm']=[1.6]
    policy=path.with_suffix('.yaml');policy.write_text(yaml.safe_dump(cfg))
    return run([KPY,str(SCRIPTS/'critical_path_check.py'),str(path),'--config',str(policy)])

@test('literal unicode net escape cannot merge distinct native nets',kind='known_bad')
def native_unicode_net():must_fail(native_identity_case('unicode_net'),'native unicode net identity',expect='unsupported native string escape')

@test('literal slash net escape cannot merge distinct native nets',kind='known_bad')
def native_slash_net():must_fail(native_identity_case('slash_net'),'native slash net identity',expect='unsupported native string escape')

@test('literal escaped reference cannot create a requested endpoint',kind='known_bad')
def native_escaped_reference():must_fail(native_identity_case('reference'),'native reference identity',expect='unsupported native string escape')

@test('literal escaped property key cannot create Reference',kind='known_bad')
def native_escaped_property():must_fail(native_identity_case('property_key'),'native property identity',expect='unsupported native string escape')

@test('literal escaped pad number cannot create a requested endpoint',kind='known_bad')
def native_escaped_pad_number():must_fail(native_identity_case('pad_number'),'native pad identity',expect='unsupported native string escape')

@test('escaped display quotes and backslashes remain valid native metadata')
def native_escaped_metadata():must_pass(native_identity_case('metadata'),'native escaped display value')

@test('raw geometry escapes and decoded control characters are refused',kind='known_bad')
def identity_raw_spelling():
    for text in (board().replace('"AUDIO"',r'"AUDIO\t"'),board().replace('"J1"',r'"J1\b"'),board().replace('"Reference"',r'"Refer\tence"')):
        must_fail(invoke(text),'escaped geometry identity',expect='unsupported escaped geometry identity')

if __name__=='__main__':sys.exit(main())
