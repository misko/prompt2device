#!/usr/bin/env python3
"""Verify the checked-in research coupon; --rebuild creates a new revision candidate."""
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
board_path = root / 'usb4215_edge_registration_coupon.kicad_pcb'
report = root / 'coupon_drc.txt'
if args.rebuild:
    subprocess.run([sys.executable, str(root / 'generate_coupon.py')], check=True)
subprocess.run(['kicad-cli', 'pcb', 'drc', str(board_path), '-o', str(report)], check=False)
text = report.read_text()
if 'Found 0 DRC violations' not in text or 'Found 8 unconnected pads' not in text:
    raise SystemExit('unexpected coupon DRC result')
b = pcbnew.LoadBoard(str(board_path))
if len(b.GetEnabledLayers().CuStack()) != 2:
    raise SystemExit('coupon process state changed: expected two copper layers')
f = next((x for x in b.GetFootprints() if x.GetReference() == 'J_EDGE'), None)
if f is None or (pcbnew.ToMM(f.GetPosition().x), pcbnew.ToMM(f.GetPosition().y),
                 f.GetOrientationDegrees()) != (15.0, 2.995, 180.0):
    raise SystemExit('coupon J_EDGE pose mismatch')
print('coupon geometric DRC: 0 violations; electrical topology intentionally incomplete: 8 unconnected')
print('coupon sha256:', hashlib.sha256(board_path.read_bytes()).hexdigest())
