#!/usr/bin/env python3
"""Reproduce the first native-rule failure of the coupled TDM route probe."""
from __future__ import annotations

import hashlib
import json
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
OUT = HERE / 'data_west_stub.kicad_pcb'
RESULT = HERE / 'result.json'
NET = 'TDM_DATA_1V8'
PAD = 'U_XU.107'
WIDTH_MM = 0.2
EXIT_MM = (199.805, 97.6)
TRACK_UUID = '8d2f831e-bd45-4e0f-9f42-0659d20a8107'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def drc(path, report):
    cmd = ['kicad-cli', 'pcb', 'drc', '--format', 'json', '-o', str(report), str(path)]
    run = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(report.read_text()), run.stdout.strip()


def main():
    if digest(BASE) != BASE_SHA256:
        raise SystemExit('coupled-placement board drift')
    board = pcbnew.LoadBoard(str(BASE))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    pads = [pad for pad in fps['U_XU'].Pads() if pad.GetNumber() == '107']
    if len(pads) != 1 or pads[0].GetNetname() != NET or not pads[0].IsOnLayer(pcbnew.F_Cu):
        raise SystemExit('exact native DATA pad identity drift')
    start = pads[0].GetPosition()
    if (round(pcbnew.ToMM(start.x), 4), round(pcbnew.ToMM(start.y), 4)) != (200.8375, 97.6):
        raise SystemExit('native DATA pad position drift')
    track = pcbnew.PCB_TRACK(board)
    track.SetLayer(pcbnew.F_Cu)
    track.SetNet(board.FindNet(NET))
    track.SetWidth(pcbnew.FromMM(WIDTH_MM))
    track.SetStart(start)
    track.SetEnd(pcbnew.VECTOR2I(*(pcbnew.FromMM(v) for v in EXIT_MM)))
    board.Add(track)
    pcbnew.SaveBoard(str(OUT), board)
    text = OUT.read_text()
    generated_uuid = track.m_Uuid.AsString()
    if text.count(generated_uuid) != 1:
        raise SystemExit('added track UUID serialization drift')
    OUT.write_text(text.replace(generated_uuid, TRACK_UUID))

    # Run both boards in the same clean temporary project environment, keeping
    # their embedded board rules intact and comparing the one added track only.
    with tempfile.TemporaryDirectory(prefix='crow-tdm-stop-') as temp:
        place = Path(temp)
        before = place / 'baseline.kicad_pcb'
        after = place / 'stub.kicad_pcb'
        shutil.copyfile(BASE, before)
        shutil.copyfile(OUT, after)
        a, _ = drc(before, place / 'baseline.json')
        b, _ = drc(after, place / 'stub.json')
    def categories(report):
        return dict(sorted(Counter(v['type'] for v in report['violations']).items()))
    new_track_errors = [v for v in b['violations'] if any(
        'Track [TDM_DATA_1V8]' in item['description'] for item in v['items'])]
    clearance = [v for v in new_track_errors if v['type'] == 'clearance'
                 and '0.1750 mm' in v['description']
                 and any('Pad 108 ' in item['description'] for item in v['items'])]
    if len(clearance) != 1:
        raise SystemExit(f'exact pad-108 clearance stop not reproduced: {new_track_errors}')
    if any(v['type'] == 'track_width' for v in new_track_errors):
        raise SystemExit('0.20-mm native minimum track unexpectedly rejected')
    result = {'schema': 1, 'kind': 'tdm-data-native-clearance-stop',
              'status': 'STOP_DATA_WEST_PAD_ESCAPE_CLEARANCE', 'p1_accepted': False,
              'routing_accepted': False, 'input_board_sha256': BASE_SHA256,
              'fixture_board_sha256': digest(OUT), 'added_track': {'net': NET,
                  'start_pad': PAD, 'start_mm': [200.8375, 97.6],
                  'end_mm': list(EXIT_MM), 'layer': 'F.Cu', 'width_mm': WIDTH_MM},
              'native_rule_mm': {'minimum_track_width': 0.2, 'clearance': 0.2},
              'geometry_mm': {'adjacent_pad': 'U_XU.108', 'pad_pitch': 0.4,
                              'adjacent_pad_half_height': 0.125,
                              'trace_half_width': 0.1,
                              'resulting_gap': 0.175},
              'drc': {'before_violations': len(a['violations']),
                      'after_violations': len(b['violations']),
                      'before_unconnected': len(a['unconnected_items']),
                      'after_unconnected': len(b['unconnected_items']),
                      'before_types': categories(a), 'after_types': categories(b),
                      'new_data_track_items': new_track_errors},
              'return_assessment': 'Not attempted after first native F.Cu clearance contradiction; no legal timing route exists in this fixture.'}
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'before': len(a['violations']),
                      'after': len(b['violations']), 'fixture_sha256': result['fixture_board_sha256']}))


if __name__ == '__main__':
    main()
