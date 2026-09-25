#!/usr/bin/env python3
"""Verify the checked-in 4-layer research process-target coupon."""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

import pcbnew

parser = argparse.ArgumentParser()
parser.add_argument('--rebuild', action='store_true',
                    help='regenerate geometry; rebind the PCB hash before review/commit')
args = parser.parse_args()
root = Path(__file__).parent
board_path = root / 'usb4215_edge_registration_coupon_4l_target.kicad_pcb'
report = root / 'coupon_drc.txt'
if args.rebuild:
    subprocess.run([sys.executable, str(root / 'generate_coupon.py')], check=True)
subprocess.run(['kicad-cli', 'pcb', 'drc', str(board_path), '-o', str(report)], check=False)
text = report.read_text()
if 'Found 0 DRC violations' not in text or 'Found 8 unconnected pads' not in text:
    raise SystemExit('unexpected coupon DRC result')
board = pcbnew.LoadBoard(str(board_path))
if len(board.GetEnabledLayers().CuStack()) != 4:
    raise SystemExit('coupon process state changed: expected four copper layers')
if pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness()) != 1.6:
    raise SystemExit('coupon process state changed: expected 1.60 mm nominal thickness')
fp = next((x for x in board.GetFootprints() if x.GetReference() == 'J_EDGE'), None)
pose = None if fp is None else (pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y),
                                fp.GetOrientationDegrees())
if pose != (15.0, 2.995, 180.0):
    raise SystemExit(f'coupon J_EDGE pose mismatch: {pose!r}')
print('coupon geometric DRC: 0 violations; electrical topology intentionally incomplete: 8 unconnected')
print('coupon sha256:', hashlib.sha256(board_path.read_bytes()).hexdigest())
