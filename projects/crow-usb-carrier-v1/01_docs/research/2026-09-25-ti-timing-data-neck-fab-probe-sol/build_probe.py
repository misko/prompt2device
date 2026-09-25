#!/usr/bin/env python3
"""Isolated 0.15-mm XU DATA neck fabrication geometry probe; no release credit."""
from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
sys.path.insert(0, str(RESEARCH / '2026-09-25-ti-timing-mouth-screen-sol'))
import build_screen as screen  # noqa: E402

pcbnew = screen.pcbnew
BASE = RESEARCH / '2026-09-25-ti-timing-coupled-placement-sol/candidate.kicad_pcb'
BASE_SHA256 = '53e6fb7809910946c36053e7ceeb77e7fc866456ff77775ed4c59b3e49278555'
BOARD_OUT = HERE / 'local_neck.kicad_pcb'
RULE_OUT = HERE / 'local_neck.kicad_dru'
PROJECT = HERE / 'local_neck.kicad_pro'
RESULT_OUT = HERE / 'result.json'
NET = 'TDM_DATA_1V8'
WIDTH = 0.15
LENGTH_LIMIT = 1.05  # Explicit diagnostic bound, not an XMOS electrical allowance.
START = (200.8375, 97.6)
END = (199.805, 97.6)
AREA = (199.7, 97.49, 200.95, 97.71)
AREA_NAME = 'TDM_DATA_107_NECK'
TRACK_UUID = '8d2f831e-bd45-4e0f-9f42-0659d20a8107'
AREA_UUID = 'd4a9f32e-481d-4a57-a691-9b65f86e60c3'
RULE = '''(version 1)
(rule "TDM_DATA_107_local_width"
  (condition "A.NetName == 'TDM_DATA_1V8' && A.insideArea('TDM_DATA_107_NECK')")
  (constraint track_width (min 0.15mm)))
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pos(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def rectangle(bounds):
    x0, y0, x1, y1 = bounds
    poly = pcbnew.SHAPE_POLY_SET()
    poly.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        poly.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    return poly


def stable_zone_order(text):
    # pcbnew serializes its native zone container in nondeterministic order.
    # Every top-level zone is contiguous just before embedded_fonts here.
    marks = list(re.finditer(r'\n\t\(zone\n', text))
    end = text.index('\n\t(embedded_fonts', marks[-1].start())
    positions = [m.start() for m in marks] + [end]
    blocks = [text[a:b] for a, b in zip(positions, positions[1:])]
    if any(block.count('\n\t(zone\n') != 1 for block in blocks):
        raise SystemExit('native top-level zone serialization shape drift')
    def zone_uuid(block):
        match = re.search(r'\(uuid "([^"]+)"\)', block)
        if not match:
            raise SystemExit('native zone UUID missing')
        return match.group(1)
    if len({zone_uuid(block) for block in blocks}) != len(blocks):
        raise SystemExit('native zone UUID collision')
    return text[:positions[0]] + ''.join(sorted(blocks, key=zone_uuid)) + text[end:]


def fill_ground(board):
    zones = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND'
             and z.IsOnLayer(pcbnew.In1_Cu)]
    if len(zones) != 1:
        raise SystemExit('In1.Cu GND zone denominator drift')
    pcbnew.ZONE_FILLER(board).Fill(zones)
    if not zones[0].IsFilled():
        raise SystemExit('In1.Cu GND zone did not fill')
    return zones[0].GetFilledPolysList(pcbnew.In1_Cu)


def drc(board, project, rule, folder, stem):
    board_copy = folder / (stem + '.kicad_pcb')
    project_copy = folder / (stem + '.kicad_pro')
    shutil.copyfile(board, board_copy)
    shutil.copyfile(project, project_copy)
    if rule:
        shutil.copyfile(rule, folder / (stem + '.kicad_dru'))
    report = folder / (stem + '.json')
    subprocess.run(['kicad-cli', 'pcb', 'drc', '--refill-zones', '--format', 'json', '-o', str(report),
                    str(board_copy)], check=True, capture_output=True, text=True)
    return json.loads(report.read_text())


def main():
    if digest(BASE) != BASE_SHA256:
        raise SystemExit('coupled-placement board drift')
    settings = json.loads(PROJECT.read_text())
    if settings['board']['design_settings']['rules']['min_track_width'] != 0.2:
        raise SystemExit('scratch project 0.20-mm physical floor drift')
    if settings['net_settings']['classes'][0]['clearance'] != 0.2:
        raise SystemExit('scratch project 0.20-mm clearance drift')
    board = pcbnew.LoadBoard(str(BASE))
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    pads = [p for p in fps['U_XU'].Pads() if p.GetNumber() == '107']
    if len(pads) != 1 or pads[0].GetNetname() != NET or not pads[0].IsOnLayer(pcbnew.F_Cu):
        raise SystemExit('native U_XU.107 identity drift')
    p = pads[0].GetPosition()
    if (round(pcbnew.ToMM(p.x), 4), round(pcbnew.ToMM(p.y), 4)) != START:
        raise SystemExit('native U_XU.107 position drift')
    if math.dist(START, END) > LENGTH_LIMIT + 1e-9:
        raise SystemExit('local diagnostic length bound failed')
    r = WIDTH / 2
    stroke_box = (min(START[0], END[0]) - r, START[1] - r,
                  max(START[0], END[0]) + r, START[1] + r)
    if not (AREA[0] < stroke_box[0] and AREA[1] < stroke_box[1]
            and stroke_box[2] < AREA[2] and stroke_box[3] < AREA[3]):
        raise SystemExit('full F.Cu stroke outside strictly scoped local rule area')

    area = pcbnew.ZONE(board)
    area.SetIsRuleArea(True)
    area.SetLayer(pcbnew.F_Cu)
    area.SetZoneName(AREA_NAME)
    for name in ('Tracks', 'Vias', 'Pads', 'Footprints', 'ZoneFills'):
        getattr(area, 'SetDoNotAllow' + name)(False)
    poly = area.Outline()
    poly.NewOutline()
    for x, y in ((AREA[0], AREA[1]), (AREA[2], AREA[1]),
                 (AREA[2], AREA[3]), (AREA[0], AREA[3])):
        poly.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    board.Add(area)
    track = pcbnew.PCB_TRACK(board)
    track.SetLayer(pcbnew.F_Cu)
    track.SetWidth(pcbnew.FromMM(WIDTH))
    track.SetNet(board.FindNet(NET))
    track.SetStart(pos(*START))
    track.SetEnd(pos(*END))
    board.Add(track)
    pcbnew.SaveBoard(str(BOARD_OUT), board)
    serialized = BOARD_OUT.read_text()
    for old, new in ((track.m_Uuid.AsString(), TRACK_UUID),
                     (area.m_Uuid.AsString(), AREA_UUID)):
        if serialized.count(old) != 1:
            raise SystemExit('native UUID serialization drift')
        serialized = serialized.replace(old, new)
    BOARD_OUT.write_text(stable_zone_order(serialized))
    RULE_OUT.write_text(RULE)
    # Fill after the deterministic unfilled board is saved. The filled zone is
    # checked natively in memory and independently by CLI --refill-zones DRC.
    filled = fill_ground(board)
    # The entire *bounding rectangle* of the neck, including its rounded caps,
    # is contained in filled GND. This is stronger than sampled centreline hits.
    missing = rectangle(stroke_box)
    missing.BooleanSubtract(filled)
    if missing.OutlineCount() != 0 or missing.Area() != 0:
        raise SystemExit('filled In1.Cu GND does not cover the full neck stroke')
    ids = [i for i in range(filled.OutlineCount()) if filled.Contains(pos(*START), i)]
    if len(ids) != 1:
        raise SystemExit('local neck does not lie in one filled GND polygon')
    with tempfile.TemporaryDirectory(prefix='crow-tdm-local-neck-') as name:
        folder = Path(name)
        a = drc(BASE, PROJECT, None, folder, 'baseline')
        b = drc(BOARD_OUT, PROJECT, RULE_OUT, folder, 'stub')
    def types(report):
        return dict(sorted(Counter(v['type'] for v in report['violations']).items()))
    track_items = [v for v in b['violations'] if any(
        'Track [TDM_DATA_1V8]' in item['description'] for item in v['items'])]
    if any(v['type'] in ('track_width', 'clearance') for v in track_items):
        raise SystemExit(f'native local width/clearance failed: {track_items}')
    if [v['type'] for v in track_items] != ['track_dangling']:
        raise SystemExit(f'unexpected local-neck DRC items: {track_items}')
    if types(a).get('clearance') != types(b).get('clearance'):
        raise SystemExit('whole-board native clearance count changed')
    access = []
    for f in board.GetFootprints():
        for pad in f.Pads():
            if pad.GetNetname() == 'GND' and pad.IsOnLayer(pcbnew.In1_Cu):
                at = pad.GetPosition()
                access.append((math.dist(START, (pcbnew.ToMM(at.x), pcbnew.ToMM(at.y))),
                               f'{f.GetReference()}.{pad.GetNumber()}',
                               [round(pcbnew.ToMM(at.x), 4), round(pcbnew.ToMM(at.y), 4)]))
    for via in board.GetTracks():
        if isinstance(via, pcbnew.PCB_VIA) and via.GetNetname() == 'GND' and via.IsOnLayer(pcbnew.In1_Cu):
            at = via.GetPosition()
            access.append((math.dist(START, (pcbnew.ToMM(at.x), pcbnew.ToMM(at.y))),
                           'GND via', [round(pcbnew.ToMM(at.x), 4), round(pcbnew.ToMM(at.y), 4)]))
    nearest = min(access)
    result = {'schema': 1, 'kind': 'isolated-tdm-data-local-neck-fabrication-probe',
              'status': 'FAB_GEOMETRY_ONLY_RETURN_ACCESS_UNPROVED',
              'p1_accepted': False, 'p2_accepted': False, 'electrical_qualified': False,
              'input_board_sha256': BASE_SHA256, 'board_sha256': digest(BOARD_OUT),
              'scratch_project_sha256': digest(PROJECT), 'rule_sha256': digest(RULE_OUT),
              'net': NET, 'pad': 'U_XU.107', 'layer': 'F.Cu', 'width_mm': WIDTH,
              'length_mm': round(math.dist(START, END), 4), 'diagnostic_max_length_mm': LENGTH_LIMIT,
              'start_mm': START, 'end_mm': END, 'full_stroke_bbox_mm': stroke_box,
              'rule_area_bbox_mm': AREA, 'full_shape_contained': True,
              'reference': {'net': 'GND', 'layer': 'In1.Cu', 'filled': True,
                            'neck_box_uncovered_area_mm2': 0, 'common_filled_polygon': ids[0],
                            'nearest_existing_plane_access': {'kind': nearest[1],
                                'at_mm': nearest[2], 'distance_to_pad_mm': round(nearest[0], 4)}},
              'drc': {'baseline_violations': len(a['violations']),
                      'neck_violations': len(b['violations']),
                      'baseline_unconnected': len(a['unconnected_items']),
                      'neck_unconnected': len(b['unconnected_items']),
                      'baseline_types': types(a), 'neck_types': types(b),
                      'neck_track_items': track_items},
              'limitations': ['not a source-backed XMOS electrical neck width or length',
                              'no local GND transition, full route, timing, USB, or crystal proof']}
    RESULT_OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'board_sha256': result['board_sha256'],
                      'drc': [len(a['violations']), len(b['violations'])],
                      'nearest_ground_access_mm': round(nearest[0], 4)}))


if __name__ == '__main__':
    main()
