#!/usr/bin/env python3
"""Native KiCad oracle for source-emitted pad-only clearance rules.

The fixture has legal pad pairs plus intentionally tight tracks, vias, wrong
nets, outside-area pairs and a pair below the local floor. The false-scope
arm is the pre-fix behavior: same physical board, lost type guard. No board
under projects/ is edited or used as the expected verdict.
RED verified 2026-09-08 using the exact emitter from 06d3bd3e: native DRC
misses the two intentionally tight track/via pairs while the fixed emitter
reports them. The filled-zone arm stays unchanged in both versions.
"""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import KPY, SCRIPTS, check, eq, main, must_pass, run, test, tmpdir
GEN_RULES = SCRIPTS/'generate_rules_generic.py'


@test("native pad-only rules preserve track/via/zone and out-of-scope clearance",
      kind="known_bad")
def t_native_pad_only_controls():
    import pcbnew
    import yaml
    def vec(x,y): return pcbnew.VECTOR2I(round(x*1e6),round(y*1e6))
    results = {}
    for pad_only in (True, False):
        root = tmpdir('pad_only_native_')
        (root/'03_src/rules').mkdir(parents=True); (root/'04_kicad').mkdir()
        board = pcbnew.BOARD(); board.SetCopperLayerCount(4)
        codes = {}
        for name in ('A','B','C'):
            n=pcbnew.NETINFO_ITEM(board,name);board.Add(n);codes[name]=n
        ids = {}; scopes = []
        def pad(label,x,y,net):
            fp=pcbnew.FOOTPRINT(board);fp.SetReference(label);board.Add(fp)
            p=pcbnew.PAD(fp);p.SetNumber('1');p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            p.SetShape(pcbnew.PAD_SHAPE_RECT);p.SetSize(vec(.5,.5))
            layers=pcbnew.LSET();layers.AddLayer(pcbnew.F_Cu);p.SetLayerSet(layers)
            fp.Add(p);p.SetPosition(vec(x,y));p.SetNet(codes[net])
            ids[p.m_Uuid.AsString()]=label
            return p
        def area(name, rect):
            z=pcbnew.ZONE(board);z.SetIsRuleArea(True);z.SetZoneName(name);z.SetLayer(pcbnew.F_Cu)
            z.SetDoNotAllowTracks(False);z.SetDoNotAllowVias(False)
            z.SetDoNotAllowZoneFills(False);z.SetDoNotAllowPads(False)
            z.Outline().NewOutline()
            x0,y0,x1,y1=rect
            for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:z.Outline().Append(round(x*1e6),round(y*1e6))
            board.Add(z)
            scopes.append(dict(zone=name,nets_a=['A'],nets_b=['B'],clearance='0.15mm',
                               pads_only=pad_only,why='Synthetic native DRC discrimination fixture.'))
        for i, kind in enumerate(('pad','track','via','wrong','outside','one_side','reverse','below')):
            x=5+i*5;pad(kind+'_A',x,5,'B' if kind=='reverse' else 'A')
            if kind=='track':
                item=pcbnew.PCB_TRACK(board);item.SetStart(vec(x+.53,4.5));item.SetEnd(vec(x+.53,5.5))
                item.SetWidth(pcbnew.FromMM(.2));item.SetLayer(pcbnew.F_Cu);item.SetNet(codes['B']);board.Add(item)
                ids[item.m_Uuid.AsString()]=kind+'_B'
            elif kind=='via':
                item=pcbnew.PCB_VIA(board);item.SetPosition(vec(x+.58,5));item.SetWidth(pcbnew.FromMM(.3))
                item.SetDrill(pcbnew.FromMM(.15));item.SetViaType(pcbnew.VIATYPE_THROUGH)
                item.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu);item.SetNet(codes['B']);board.Add(item)
                ids[item.m_Uuid.AsString()]=kind+'_B'
            else:pad(kind+'_B',x+(.64 if kind=='below' else .68),5,'C' if kind=='wrong' else 'A' if kind=='reverse' else 'B')
            area(kind, [x-1,4,x+(.30 if kind=='one_side' else 2),6] if kind!='outside' else [x-1,7,x+2,8])
        pad('zone_A',46,5,'A');area('zone',[45,4,48,6])
        zone=pcbnew.ZONE(board);zone.SetLayer(pcbnew.F_Cu);zone.SetNet(codes['B'])
        zone.SetLocalClearance(pcbnew.FromMM(.15));zone.SetMinThickness(pcbnew.FromMM(.05))
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
        zone.Outline().NewOutline()
        for x,y in [(46.43,4),(48,4),(48,6),(46.43,6)]:zone.Outline().Append(round(x*1e6),round(y*1e6))
        board.Add(zone)
        for a,b in [((2,2),(50,2)),((50,2),(50,10)),((50,10),(2,10)),((2,10),(2,2))]:
            edge=pcbnew.PCB_SHAPE(board);edge.SetShape(pcbnew.SHAPE_T_SEGMENT);edge.SetLayer(pcbnew.Edge_Cuts)
            edge.SetStart(vec(*a));edge.SetEnd(vec(*b));edge.SetWidth(pcbnew.FromMM(.05));board.Add(edge)
        pcb=root/'04_kicad/fixture.kicad_pcb';pcbnew.SaveBoard(str(pcb),board)
        (root/'04_kicad/fixture.kicad_pro').write_text('{}\n')
        (root/'03_src/floorplan.yaml').write_text(yaml.safe_dump({'board':{'layers':4},'design_rules':{'min_clearance':.127}}))
        (root/'03_src/rules/nets.yaml').write_text(yaml.safe_dump(dict(fab_tier='jlc_4layer_advanced',
            default_clearance='0.25mm',default_track_width='0.18mm',classes={},scoped_clearances=scopes)))
        must_pass(run([KPY,GEN_RULES,root]),'generate real rule file')
        report=root/'drc.json'
        must_pass(run(['kicad-cli','pcb','drc','--severity-all','--refill-zones','--save-board',
                       '--format','json','-o',report,pcb]),'native diagnostic report')
        data=json.loads(report.read_text());pairs=set()
        for row in data['violations']:
            if row['type']=='clearance':pairs.add(tuple(sorted(ids[i['uuid']] for i in row['items'])))
        expected={'wrong','outside','one_side','below'}|({'track','via'} if pad_only else set())
        eq(pairs,{(name+'_A',name+'_B') for name in expected},'native exact clearance findings')
        saved=pcbnew.LoadBoard(str(pcb))
        actual_pad=next(p for fp in saved.GetFootprints() if fp.GetReference()=='zone_A' for p in fp.Pads())
        actual_zone=next(z for z in saved.Zones() if not z.GetIsRuleArea())
        filled=actual_zone.GetFilledPolysList(pcbnew.F_Cu)
        check(filled.Area()>0,'zone has real filled copper')
        collision=pcbnew.SHAPE.Collide(filled,actual_pad.GetEffectiveShape(pcbnew.F_Cu),pcbnew.FromMM(.24))
        # Native filler retains >=0.24mm in BOTH arms; only the track/via
        # findings discriminate the missing guard. Do not invent a zone flip.
        eq(collision,False,'native filled zone retains ordinary clearance')
        results[pad_only]=len(pairs)
    eq(results,{True:6,False:4},'type-guard contrast on identical geometry')
    print('18/18 native sites graded across two arms; clearance findings 6 guarded / 4 unguarded; both filled-zone screens retain ordinary clearance')


if __name__=='__main__': sys.exit(main())
