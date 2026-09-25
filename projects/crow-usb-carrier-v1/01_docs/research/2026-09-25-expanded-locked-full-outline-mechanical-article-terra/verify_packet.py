#!/usr/bin/env python3
"""Verify the research packet without creating a board or fabrication file."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
PRIVATE = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925'
BOARD = PRIVATE / '04_kicad/crow_carrier.kicad_pcb'
DRC = PRIVATE / '06_build/drc/expanded_locked_pre_route.json'
EXPECTED = 'fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16'

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> None:
    if sha(BOARD) != EXPECTED:
        raise SystemExit('private board SHA drift')
    subprocess.run([sys.executable, str(HERE / 'extract_geometry.py')], check=True)
    geo = json.loads((HERE / 'native_geometry.json').read_text())
    if (geo['source_board_sha256'] != EXPECTED or len(geo['connectors']) != 11 or
            len(geo['mounting_holes']) != 6 or geo['board_target'] != {
                'outline_mm': [10, 20, 240, 150], 'size_mm': [230, 130],
                'copper_layers': 4, 'nominal_thickness_mm': 1.63}):
        raise SystemExit('mechanical geometry manifest drift')
    drc = json.loads(DRC.read_text())
    counts = {k: len(drc[k]) for k in ('violations', 'unconnected_items')}
    if counts != {'violations': 0, 'unconnected_items': 499}:
        raise SystemExit(f'native DRC drift: {counts}')
    print(json.dumps({'status': geo['status'], 'board_sha256': EXPECTED,
                      'connectors': 11, 'mounting_holes': 6, 'native_drc': counts,
                      'fabrication_payload': False, 'connector_full_credit': False}, indent=2))

if __name__ == '__main__':
    main()
