#!/usr/bin/env python3
"""Native neighborhood composition coupons, independent of any project.

Two pads at 0.5 mm pitch launch individually legal paths whose combined
copper crosses. A geometry correction keeps both terminal sets unchanged.
These coupons test fixed witnesses, not autorouter completeness or routability.
No passing coupon grants a board release or replaces full native DRC.
"""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import check, eq, main, must_pass, run, test, tmpdir


def native_report(paths, order):
    import pcbnew
    root = tmpdir('route_neighborhood_')
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    def vec(x, y):
        return pcbnew.VECTOR2I(round(x * 1e6), round(y * 1e6))
    identities = {}
    for name in order:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        points = paths[name]
        for index, point in enumerate((points[0], points[-1])):
            fp = pcbnew.FOOTPRINT(board)
            fp.SetReference(f'{name}{index}')
            board.Add(fp)
            pad = pcbnew.PAD(fp)
            pad.SetNumber('1'); pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetShape(pcbnew.PAD_SHAPE_RECT); pad.SetSize(vec(.3, .3))
            layers = pcbnew.LSET(); layers.AddLayer(pcbnew.F_Cu)
            pad.SetLayerSet(layers); fp.Add(pad)
            pad.SetPosition(vec(*point)); pad.SetNet(net)
            identities[pad.m_Uuid.AsString()] = name
        for start, end in zip(points, points[1:]):
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(vec(*start)); track.SetEnd(vec(*end))
            track.SetWidth(pcbnew.FromMM(.18)); track.SetLayer(pcbnew.F_Cu)
            track.SetNet(net); board.Add(track)
            identities[track.m_Uuid.AsString()] = name
    for start, end in zip(((1, 1), (15, 1), (15, 10), (1, 10)),
                          ((15, 1), (15, 10), (1, 10), (1, 1))):
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetStart(vec(*start)); edge.SetEnd(vec(*end))
        edge.SetWidth(pcbnew.FromMM(.05)); board.Add(edge)
    pcb = root / 'coupon.kicad_pcb'
    pcbnew.SaveBoard(str(pcb), board)
    pcb.with_suffix('.kicad_pro').write_text(json.dumps({
        'board': {'design_settings': {'rules': {
            'min_clearance': .127, 'min_track_width': .127}}}}))
    report = root / 'drc.json'
    must_pass(run(['kicad-cli', 'pcb', 'drc', '--severity-all', '--format',
                   'json', '-o', report, pcb]), 'native coupon diagnostic')
    data = json.loads(report.read_text())
    # Unconnected items remain an independent required property, even when
    # the coupled arm also has a short. Do not summarize them as congestion.
    eq(data['unconnected_items'], [], 'all intended terminals connected')
    eq(sum(len(list(fp.Pads())) for fp in board.GetFootprints()),
       2 * len(order), 'nonempty exact terminal census')
    check(all(item.GetLayer() == pcbnew.F_Cu and
              not isinstance(item, pcbnew.PCB_VIA) for item in board.GetTracks()),
          'coupon keeps every governed path front-only and zero-via')
    copper_types = {'clearance', 'shorting_items', 'tracks_crossing'}
    eq([row['type'] for row in data['violations']
        if row['type'] not in copper_types], [], 'no unclassified native violations')
    copper = [row for row in data['violations'] if row['type'] in copper_types]
    pairs = {tuple(sorted({identities[item['uuid']] for item in row['items']}))
             for row in copper}
    return pairs


@test('individually legal branches fail when composed across a neighboring escape',
      kind='known_bad')
def t_branch_composition():
    blocked = {'ESCAPE': [(5, 5), (9, 5)],
               'BRANCH': [(5, 5.5), (6, 5.5), (6, 4), (9, 4)]}
    for name in blocked:
        eq(native_report(blocked, [name]), set(), 'isolated copper is legal')
    for order in (['ESCAPE', 'BRANCH'], ['BRANCH', 'ESCAPE']):
        eq(native_report(blocked, order), {('BRANCH', 'ESCAPE')},
           'exact coupled foreign-net conflict in either insertion order')


@test('moving the branch around the exit preserves connected front-only witnesses')
def t_branch_geometry_correction():
    corrected = {'ESCAPE': [(5, 5), (9, 5)],
                 'BRANCH': [(5, 5.5), (5, 7), (11, 7), (11, 4), (9, 4)]}
    for order in (['ESCAPE', 'BRANCH'], ['BRANCH', 'ESCAPE']):
        eq(native_report(corrected, order), set(), 'corrected coupled copper')


if __name__ == '__main__':
    raise SystemExit(main())
