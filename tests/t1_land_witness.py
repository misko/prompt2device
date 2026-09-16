#!/usr/bin/env python3
"""Native finite launch witness tests; persistent fixtures and bounded CLI oracle."""
import json
import os
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import ROOT, KPY, SCRIPTS, FIXTURES, test, check, eq, contains, must_pass, main, tmpdir
sys.path.insert(0, str(ROOT / "skills/pcb-design/scripts"))
from pipeline_runtime import run_stage


def bounded(argv, folder, label, env=None):
    argv = [str(x) for x in argv]
    result = run_stage({"id": label, "work_class": "local", "timeout_s": 60},
                       argv, log_path=folder / (label + ".log"), cwd=ROOT,
                       env=dict(os.environ) if env is None else env, console=None).to_mapping()
    result["argv"] = argv
    (folder / (label + ".process.json")).write_text(json.dumps(result, indent=2))
    return SimpleNamespace(rc=result["returncode"], out=(folder / (label + ".log")).read_text())


def complete_fixture(mode):
    folder = tmpdir("land_complete_")
    shutil.copytree(FIXTURES / "land_witness" / mode, folder, dirs_exist_ok=True)
    return folder


@test("native-clean complete-class public acceptance and census")
def t_complete_public():
    # SAME neutral assertion is run RED against cb0d0cf6 before public repair.
    folder = complete_fixture("base")
    r = bounded([KPY, SCRIPTS / "escape_check.py", "--board", folder / "public.kicad_pcb", "--verbose"], folder, "public")
    contains(r.out, "2 graded / 5 copper pads")
    contains(r.out, "3 no declared width floor")
    must_pass(r, "native-clean five-pad complete classes (X1.1)")


@test("native complete-class oracle contrast", kind="known_bad")
def t_complete_native():
    for mode, count in [("base", 0), ("hostile", 2)]:
        folder = complete_fixture(mode)
        r = bounded(["kicad-cli", "pcb", "drc", "--severity-all", "--all-track-errors", "--exit-code-violations", "--format", "json", "-o", folder / "drc.json", folder / "oracle.kicad_pcb"], folder, "native")
        j = json.loads((folder / "drc.json").read_text())
        eq(len(j["unconnected_items"]), 0, mode + " opens")
        eq(len(j["violations"]), count, mode + " violations")
        eq(r.rc, 0 if count == 0 else 5, mode + " native exit")
        if count:
            eq({v["type"] for v in j["violations"]}, {"clearance"}, "hostile type")
            pads = {i["description"].split(" ")[1] for v in j["violations"] for i in v["items"] if i["description"].startswith("Pad ")}
            import pcbnew
            board = pcbnew.LoadBoard(str(folder / "oracle.kicad_pcb"))
            target = next(t for t in board.GetTracks() if t.GetNetname() == "TARGET")
            target_id = target.m_Uuid.AsString()
            expected = {frozenset((target_id, p.m_Uuid.AsString())) for f in board.GetFootprints() for p in f.Pads() if f.GetReference() == "X1" and p.GetNumber() in ("3", "4")}
            actual = {frozenset(i["uuid"] for i in v["items"]) for v in j["violations"]}
            eq(actual, expected, "exact hostile UUID pairs X1.3/X1.4")



@test("native matrix, precedence, Boolean, area and width controls", kind="known_bad")
def t_native_controls():
    sys.path.insert(0, str(SCRIPTS))
    from land_witness import BoardContext
    sources = list((FIXTURES / "land_witness" / "matrix").glob("*"))
    for group in ("native-controls", "semantics-controls", "focused"):
        sources += list((FIXTURES / "land_witness" / group).glob("*"))
    expected_groups = {
        "matrix": {"base", "hostile"},
        "native-controls": {"custom_below_board", "fp_nonzero_wins", "fp_zero_then_custom", "local_below_board", "pad_masks_fp", "pad_nonzero_wins", "pad_zero_masks_fp", "pad_zero_then_custom", "zero_below_board", "zero_without_custom"},
        "semantics-controls": {"area_overlap_1iu", "area_overlap_2um", "area_touch", "bracket_literal", "case_insensitive", "mixed_and_or"},
        "focused": {"area_relax_1iu", "width_below_board_allowed", "width_below_board_rejected"},
    }
    for group, expected in expected_groups.items():
        eq({p.name for p in sources if p.parent.name == group}, expected, group + " exact fixture membership")
    observations = []; matrix_uuids = set()
    for source in sources:
        folder = tmpdir("land_native_")
        shutil.copytree(source, folder, dirs_exist_ok=True)
        board_path = folder / "matrix.kicad_pcb"
        r = bounded(["kicad-cli", "pcb", "drc", "--severity-all", "--all-track-errors", "--exit-code-violations", "--format", "json", "-o", folder / "drc.json", board_path], folder, "native")
        report = json.loads((folder / "drc.json").read_text())
        check(r.rc in (0,5), 'native process completed with a DRC verdict')
        eq(len(report["unconnected_items"]), 0, str(source) + " opens")
        if source.parent.name == "matrix":
            eq(len(report["violations"]), 0 if source.name == "base" else 18, "matrix native contrast")
        c = BoardContext(board_path)
        eq(len(c.tracks), 18, str(source) + ' exact track coverage')
        if source.parent.name == 'matrix':
            expected_ids = {row['track_uuid'] for row in json.loads((source / 'cases.json').read_text())}
            eq({t.m_Uuid.AsString() for t in c.tracks}, expected_ids, 'frozen matrix UUIDs')
            matrix_uuids.update(expected_ids)
        for track in c.tracks:
            start, end = track.GetStart(), track.GetEnd()
            sources_at_start = [p for p in c.pads if p['net'] == track.GetNetname() and track.GetLayer() in p['layers'] and p['shapes'][track.GetLayer()].Collide(start, 0)]
            eq(len(sources_at_start), 1, "track source pad")
            result = c.validate(sources_at_start[0], (start.x,start.y), (end.x,end.y), track.GetWidth(), track.GetLayer(), require_declared=False)
            uuid = track.m_Uuid.AsString()
            native = [v for v in report['violations'] if v['type'] in ('clearance','track_width') and any(i['uuid'] == uuid for i in v['items'])]
            eq(result['valid'], not native, str(source.relative_to(FIXTURES)) + ' ' + track.GetNetname())
            if native:
                eq(result['reason'], native[0]['type'], 'native failure identity')
                if result['reason'] == 'clearance':
                    check(any(any(i['uuid'] == result['limiting_pair']['uuid'] for i in v['items']) for v in native), 'limiting pair is native target')
            observations.append({'fixture': str(source.relative_to(FIXTURES)), 'track_uuid': uuid, 'result': result, 'native': native})
        (folder / "comparisons.json").write_text(json.dumps(observations, indent=2))
    eq(len(matrix_uuids), 36, "36 distinct frozen matrix track UUID outcomes")



@test("complete syntax admission blocks malformed and unsupported rules", kind="known_bad")
def t_syntax_admission():
    sys.path.insert(0, str(SCRIPTS))
    from land_witness import read_rules, Unsupported
    folder = tmpdir("land_syntax_")
    bad = [
        '("version" "1")',
        '(version 1) (rule bad (condition "false") (constraint diff_pair_gap (min broken)))',
        '(version 1) (rule bad (condition "false && B.NetName == \'X\'") (constraint track_width (min 0.2mm)))',
        '(version 1) (rule bad (condition "true || B.Type == \'Pad\'") (constraint track_width (min 0.2mm)))',
        '(version 1) (rule bad (condition "A.Unknown == \'x\'") (constraint clearance (min 0.2mm)))',
        '(version 1) (rule bad (condition "true") (constraint disallow track))',
        '(version 1) (rule bad (condition "true") (constraint clearance (min nanmm)))',
        '(version 1) (rule bad (condition "true") (constraint clearance (min 0.2mm) (min 0.1mm)))',
        '(version 1) (rule bad (condition "true") (condition "false") (constraint clearance (min 0.2mm)))',
        '(version 1) (rule bad (condition "A.NetClass == \'L*\'") (constraint clearance (min 0.2mm)))',
        '(version 1) (rule bad (condition "A.NetName == \'x\' trailing") (constraint clearance (min 0.2mm)))',
        '(version 1) (rule bad (condition "true") (constraint clearance (min 0.2mm))) trailing',
        '(version 1) (rule bad (condition "true") (constraint clearance (min 0.2mm))',
    ]
    for i, content in enumerate(bad):
        path = folder / (str(i) + '.kicad_dru'); path.write_text(content)
        try: read_rules(path)
        except Unsupported: pass
        else: check(False, 'unsupported syntax admitted ' + content)
    path = folder / 'good.kicad_dru'
    path.write_text('(version 1) (rule gap (condition "false") (constraint diff_pair_gap (min 0.145mm) (opt 0.15mm)))')
    rules, outside = read_rules(path)
    eq(len(outside), 1, 'valid diff pair gap explicit scope')


def compare_specified(folder, name):
    from land_witness import BoardContext
    bp = folder / 'oracle.kicad_pcb'
    r = bounded(['kicad-cli', 'pcb', 'drc', '--severity-all', '--all-track-errors', '--exit-code-violations', '--format', 'json', '-o', folder / 'drc.json', bp], folder, name)
    check(r.rc in (0,5), 'native process completed with a DRC verdict')
    report = json.loads((folder / 'drc.json').read_text())
    eq(len(report['unconnected_items']), 0, name + ' opens')
    c = BoardContext(bp); p = next(p for p in c.pads if p['num'] == '1')
    t = next(t for t in c.tracks if t.GetNetname() == 'TARGET')
    a,b = t.GetStart(),t.GetEnd()
    result = c.validate(p,(a.x,a.y),(b.x,b.y),t.GetWidth(),t.GetLayer())
    target = [v for v in report['violations'] if v['type'] in ('clearance','track_width') and any(i['uuid'] == t.m_Uuid.AsString() for i in v['items'])]
    eq(result['valid'], not target, name + ' native parity')
    (folder / 'comparison.json').write_text(json.dumps({'result': result, 'native_target': target}, indent=2))
    return c, result, target


@test("native clearance thresholds and no-net Default class controls", kind="known_bad")
def t_thresholds_and_no_net():
    import pcbnew
    sys.path.insert(0, str(SCRIPTS))
    from land_witness import BoardContext
    for gap in (99999,100000,100001,99499,99500,99501):
        folder = complete_fixture('base'); bp = folder / 'oracle.kicad_pcb'
        pro = bp.with_suffix('.kicad_pro').read_bytes()
        b = pcbnew.LoadBoard(str(bp))
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if p.GetNumber() in ('3','4'):
                    p.Move(pcbnew.VECTOR2I((210000-gap)*(1 if p.GetNumber()=='3' else -1), 0))
        pcbnew.SaveBoard(str(bp), b); bp.with_suffix('.kicad_pro').write_bytes(pro)
        c,result,target = compare_specified(folder, 'gap_' + str(gap))
        eq(c.epsilon, 500, 'qualified native epsilon')
        eq(result['valid'], gap >= 99500, 'native exact adjusted collision boundary')
    for custom in (False, True):
        folder = complete_fixture('base'); bp = folder / 'oracle.kicad_pcb'
        project = json.loads(bp.with_suffix('.kicad_pro').read_text())
        for klass in project['net_settings']['classes']:
            if klass['name'] == 'Default': klass['clearance'] = .3
        bp.with_suffix('.kicad_pro').write_text(json.dumps(project))
        b = pcbnew.LoadBoard(str(bp))
        p = next(p for f in b.GetFootprints() for p in f.Pads() if p.GetNumber() == '3'); p.SetNetCode(0)
        pcbnew.SaveBoard(str(bp), b); bp.with_suffix('.kicad_pro').write_text(json.dumps(project))
        if custom:
            with bp.with_suffix('.kicad_dru').open('a') as f:
                f.write('\n(rule default_pair (condition "B.NetClass == \'Default\'") (constraint clearance (min 0.25mm)))\n')
        c,result,target = compare_specified(folder, 'no_net_' + str(custom))
        check(not result['valid'], 'no-net Default obstacle must reject')
        eq(result['limiting_pair']['pad'], 'X1.3', 'no-net obstacle identity')


@test("NetName wildcard and complete composite native controls", kind="known_bad")
def t_native_strings_and_classes():
    import pcbnew
    sys.path.insert(0, str(SCRIPTS))
    for value, expected in [('t?rg*',False), ('[T]ARGET',True), ('target',False)]:
        folder=complete_fixture('base');bp=folder/'oracle.kicad_pcb'
        with bp.with_suffix('.kicad_dru').open('a') as f:
            f.write('\n(rule string (condition "A.NetName == \'' + value + '\'") (constraint track_width (min 0.3mm)))\n')
        c,result,target=compare_specified(folder,'strings')
        eq(result['valid'],expected,'native property-specific matching')
    folder=complete_fixture('base');bp=folder/'oracle.kicad_pcb'
    project=json.loads(bp.with_suffix('.kicad_pro').read_text())
    project['net_settings']['netclass_patterns'].append({'pattern':'TARGET','netclass':'Low'})
    bp.with_suffix('.kicad_pro').write_text(json.dumps(project))
    c,result,target=compare_specified(folder,'composite')
    check(result['valid'],'complete native composite baseline')
    check(len(c.class_members['TARGET'])>=2,'native constituent membership')



@test("native zero-epsilon exact clearance boundary", kind="known_bad")
def t_zero_epsilon():
    import pcbnew
    for gap in (99999,100000,100001):
        folder=complete_fixture('base');bp=folder/'oracle.kicad_pcb'
        pro=bp.with_suffix('.kicad_pro').read_bytes();b=pcbnew.LoadBoard(str(bp))
        for f in b.GetFootprints():
            for p in f.Pads():
                if p.GetNumber() in ('3','4'):
                    p.Move(pcbnew.VECTOR2I((210000-gap)*(1 if p.GetNumber()=='3' else -1),0))
        pcbnew.SaveBoard(str(bp),b);bp.with_suffix('.kicad_pro').write_bytes(pro)
        config=folder/'config'/'10.0';config.mkdir(parents=True)
        (config/'kicad_advanced').write_text('DRCEpsilon=0\n')
        driver=folder/'check.py'
        driver.write_text("import wx\napp=wx.App(False)\nimport sys\nfrom pathlib import Path\nsys.path.insert(0,"+repr(str(ROOT/'tests'))+")\nfrom t1_land_witness import compare_specified\nsys.path.insert(0,"+repr(str(SCRIPTS))+")\nc,r,n=compare_specified(Path("+repr(str(folder))+"),'native-zero')\nassert c.epsilon==0,c.epsilon\nassert r['valid']=="+repr(gap>=100000)+"\nprint('native zero epsilon',c.epsilon,r)\n")
        env=dict(os.environ);env['KICAD_CONFIG_HOME']=str(config.parent)
        must_pass(bounded(['xvfb-run','-a',KPY,driver],folder,'zero-driver',env),'native epsilon zero parity')



@test("thirteen retained ADC zero-margin witnesses validate natively")
def t_adc_zero_margins():
    import pcbnew
    sys.path.insert(0,str(SCRIPTS))
    from land_witness import BoardContext
    records=json.loads((FIXTURES/'land_witness/adc-zero-margin.json').read_text())
    eq({r['num'] for r in records},{'14','15','16','19','20','21','22','39','40','41','45','46','47'},'exact ADC source identities')
    src=FIXTURES/'land_witness/adc/crow_audio_carrier_v1.kicad_pcb'
    folder=tmpdir('land_adc_');bp=folder/src.name
    for ext in ('.kicad_pcb','.kicad_pro','.kicad_dru'):shutil.copyfile(src.with_suffix(ext),bp.with_suffix(ext))
    c=BoardContext(bp);ids=set();results=[]
    for r in records:
        p=next(p for p in c.pads if p['ref']==r['ref'] and p['num']==r['num']);w=r['witness']
        start=tuple(round(v*1e6) for v in w['start']);end=tuple(round(v*1e6) for v in w['end']);width=round(w['width']*1e6)
        result=c.validate(p,start,end,width,pcbnew.F_Cu)
        check(result['valid'],'retained ADC '+r['num']+' '+str(result))
        t=c.track(p,start,end,width,pcbnew.F_Cu);c.board.Add(t);ids.add(t.m_Uuid.AsString());results.append({'pad':r['num'],'track_uuid':t.m_Uuid.AsString(),'result':result})
    pro=bp.with_suffix('.kicad_pro').read_bytes();pcbnew.SaveBoard(str(bp),c.board);bp.with_suffix('.kicad_pro').write_bytes(pro)
    bounded(['kicad-cli','pcb','drc','--severity-all','--all-track-errors','--exit-code-violations','--format','json','-o',folder/'drc.json',bp],folder,'native-adc')
    report=json.loads((folder/'drc.json').read_text())
    targets=[v for v in report['violations'] if v['type'] in ('clearance','track_width') and any(i['uuid'] in ids for i in v['items'])]
    eq(targets,[],'all thirteen ADC target width/pair native findings')
    (folder/'comparisons.json').write_text(json.dumps({'results':results,'unrelated_native_violations':len(report['violations']),'native_opens':len(report['unconnected_items'])},indent=2))


@test("native source-layer admission, topology and remote local obstacle guards",kind="known_bad")
def t_native_support_guards():
    import pcbnew
    sys.path.insert(0,str(SCRIPTS))
    from land_witness import BoardContext,Unsupported
    folder=complete_fixture('base');c=BoardContext(folder/'oracle.kicad_pcb');p=next(p for p in c.pads if p['num']=='1')
    try:c.validate(p,(10000000,10000000),(10000000,11000000),200000,pcbnew.In1_Cu)
    except Unsupported:pass
    else:check(False,'disabled layer accepted')
    check(not c.validate(p,(20000000,20000000),(20000000,21000000),200000,pcbnew.F_Cu)['valid'],'outside-source start rejected')
    poly=pcbnew.SHAPE_POLY_SET();poly.NewOutline()
    for x,y in [(0,0),(100,0),(100,100),(0,100)]:poly.Append(x,y)
    poly.NewHole(0)
    for x,y in [(20,20),(20,80),(80,80),(80,20)]:poly.Append(x,y,0,0)
    try:c.admit_polygon(poly,'custom')
    except Unsupported:pass
    else:check(False,'hole topology accepted')
    folder=complete_fixture('base');bp=folder/'oracle.kicad_pcb';pro=bp.with_suffix('.kicad_pro').read_bytes();b=pcbnew.LoadBoard(str(bp))
    q=next(p for f in b.GetFootprints() for p in f.Pads() if p.GetNumber()=='5')
    q.SetLocalClearance(5000000)
    pcbnew.SaveBoard(str(bp),b);bp.with_suffix('.kicad_pro').write_bytes(pro)
    c,result,target=compare_specified(folder,'remote-local')
    check(not result['valid'],'large remote local clearance blocks')
    eq(result['limiting_pair']['pad'],'X1.5','obstacle beyond old radius is included')



@test("hostile free-search has complete native candidate coverage",kind="known_bad")
def t_hostile_exhaustion():
    import pcbnew
    sys.path.insert(0,str(SCRIPTS))
    from land_witness import BoardContext
    import math
    folder=complete_fixture('hostile');bp=folder/'oracle.kicad_pcb';c=BoardContext(bp)
    p=next(p for p in c.pads if p['num']=='1');result=c.search(p)
    check(not result['valid'] and result['coverage']['complete'],'finite hostile search exhausted')
    ids=set();records=[]
    for layer in sorted(p['layers']):
        starts,proposals=c.starts(p,layer)
        for width in c.widths:
            for start in starts:
                for direction in range(48):
                    angle=2*math.pi*direction/48
                    end=(start[0]+round(1e6*math.cos(angle)),start[1]+round(1e6*math.sin(angle)))
                    t=c.track(p,start,end,width,layer);c.board.Add(t);uuid=t.m_Uuid.AsString();ids.add(uuid)
                    records.append({'uuid':uuid,'start_iu':start,'end_iu':end,'width_iu':width,'layer':c.board.GetLayerName(layer)})
    eq(len(ids),result['coverage']['attempted'],'every production candidate serialized')
    (folder/'coverage.json').write_text(json.dumps({'production':result,'serialized':records},indent=2))
    native_ids=set()
    # KiCad caps reported findings. Separate batches keep every native report
    # below that cap while preserving each exact candidate and original pads.
    for index in range(0,len(records),100):
        part=folder/('batch_'+str(index));shutil.copytree(FIXTURES/'land_witness/hostile',part)
        path=part/'oracle.kicad_pcb';batch=BoardContext(path);source=next(p for p in batch.pads if p['num']=='1')
        expected=set()
        for row in records[index:index+100]:
            t=batch.track(source,row['start_iu'],row['end_iu'],row['width_iu'],pcbnew.F_Cu)
            batch.board.Add(t);row['native_uuid']=t.m_Uuid.AsString();expected.add(row['native_uuid'])
        pro=path.with_suffix('.kicad_pro').read_bytes();pcbnew.SaveBoard(str(path),batch.board);path.with_suffix('.kicad_pro').write_bytes(pro)
        r=bounded(['kicad-cli','pcb','drc','--severity-all','--all-track-errors','--exit-code-violations','--format','json','-o',part/'drc.json',path],part,'native-exhaustion')
        eq(r.rc,5,'hostile native batch exit')
        report=json.loads((part/'drc.json').read_text());eq(len(report['unconnected_items']),0,'hostile exhaustive opens')
        observed={i['uuid'] for v in report['violations'] if v['type'] in ('clearance','track_width','shorting_items') for i in v['items'] if i['uuid'] in expected}
        eq(len(observed),len(expected),'each bounded native batch covers all candidates')
        native_ids.update(observed)
    eq(len(native_ids),len(ids),'all prescribed candidates independently rejected by native CLI')
    (folder/'coverage.json').write_text(json.dumps({'production':result,'serialized':records},indent=2))



@test("public checker blocks incoherent native configuration and weakened inputs",kind="known_bad")
def t_public_input_guards():
    folder=complete_fixture('base');bp=folder/'public.kicad_pcb'
    config=folder/'config'/'10.0';config.mkdir(parents=True);(config/'kicad_advanced').write_text('DRCEpsilon=0\n')
    env=dict(os.environ);env['KICAD_CONFIG_HOME']=str(config.parent)
    r=bounded([KPY,SCRIPTS/'escape_check.py','--board',bp],folder,'configured-public',env)
    check(r.rc!=0,'public native configuration mismatch blocks')
    contains(r.out,'native configuration mismatch','legible config reason')
    for flag,value in [('--dirs','12'),('--reach','0.1'),('--project',str(folder/'absent.kicad_pro')),('--dru',str(folder/'absent.kicad_dru'))]:
        r=bounded([KPY,SCRIPTS/'escape_check.py','--board',bp,flag,value],folder,'input-'+flag[2:])
        check(r.rc!=0,'weakened or missing explicit input blocks')
        contains(r.out,'UNSUPPORTED','legible input admission')



@test("complete native class and THT admission guards",kind="known_bad")
def t_class_and_tht_admission():
    import pcbnew
    sys.path.insert(0,str(SCRIPTS))
    from land_witness import BoardContext,Unsupported
    for mutation in ('unknown','missing'):
        folder=complete_fixture('base');bp=folder/'public.kicad_pcb';pro=bp.with_suffix('.kicad_pro')
        data=json.loads(pro.read_text())
        if mutation=='unknown':data['net_settings']['netclass_patterns'].append({'pattern':'TARGET','netclass':'UNKNOWN'})
        else:del data['net_settings']['classes'][0]['clearance']
        pro.write_text(json.dumps(data))
        try:BoardContext(bp)
        except Unsupported:pass
        else:check(False,'incomplete native class silently admitted')
    folder=complete_fixture('base');bp=folder/'public.kicad_pcb';pro=bp.with_suffix('.kicad_pro').read_bytes();b=pcbnew.LoadBoard(str(bp))
    p=next(p for f in b.GetFootprints() for p in f.Pads() if p.GetNumber()=='1')
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH);p.SetDrillSize(pcbnew.VECTOR2I(40000,40000));p.SetLayerSet(pcbnew.LSET.AllCuMask())
    pcbnew.SaveBoard(str(bp),b);bp.with_suffix('.kicad_pro').write_bytes(pro)
    c=BoardContext(bp);p=next(p for p in c.pads if p['num']=='1')
    eq(p['layers'],frozenset((pcbnew.F_Cu,pcbnew.B_Cu)),'THT only enabled copper layers admitted')
    try:c.validate(p,(10000000,10000000),(10000000,11000000),200000,pcbnew.In1_Cu)
    except Unsupported:pass
    else:check(False,'disabled THT candidate layer admitted')



@test("public malformed project blocks with a named input reason",kind="known_bad")
def t_public_malformed_project():
    for value in ([], {'net_settings':[]}, {'net_settings':{'classes':[42]}}):
        folder=complete_fixture('base');bp=folder/'public.kicad_pcb'
        bp.with_suffix('.kicad_pro').write_text(json.dumps(value))
        r=bounded([KPY,SCRIPTS/'escape_check.py','--board',bp],folder,'malformed-project')
        check(r.rc!=0,'malformed project cannot pass')
        contains(r.out,'UNSUPPORTED','legible malformed project reason')
        check('Traceback' not in r.out,'malformed project is classified')


if __name__ == "__main__":
    sys.exit(main())
