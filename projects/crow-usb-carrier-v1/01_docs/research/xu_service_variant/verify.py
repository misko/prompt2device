#!/usr/bin/env python3
"""Reproduce and check the bounded XU service ownership measurement."""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BOARD = Path('/tmp/crow-usb-regions-terra-HqnO4Z/project/04_kicad/crow_carrier.kicad_pcb')
if not BOARD.is_file():
    raise SystemExit(f'pinned native board unavailable: {BOARD}')
actual = json.loads(subprocess.run([sys.executable, str(HERE/'measure.py'), str(BOARD)],
                                   check=True, capture_output=True, text=True).stdout)
expected = json.loads((HERE/'measurement.json').read_text())
assert actual == expected, 'measurement changed'
assert not actual['cell_intersections']
assert actual['native_rule_area_count'] == 0 and not actual['source_keepouts_mm']
assert all(f['inside_owner'] and not f['crosses_boundary_y114']
           for f in actual['assigned_native_footprints'])
assert all(not b['native_footprint_hits'] and not b['native_pad_hits']
           for b in actual['boundaries'].values())
assert all(f['width_margin_mm'] > 0 and not f['native_footprint_hits']
           and not f['native_pad_hits'] and not f['native_rule_area_hits']
           and not f['source_keepout_hits']
           and not f['foreign_source_region_hits'] for f in actual['faces'].values())
assert len(actual['endpoints']) == 33
assert all(len(e['native_pads']) == 1 and e['native_pads'][0]['net'] == e['net']
           for e in actual['endpoints'])
assert sum(not e['fixed_p1'] for e in actual['endpoints']) == 28
assert actual['p1_fixed_ref_count'] == 27 and not actual['p1_fixed_native_missing']
print('XU service geometry diagnostic reproduced; status remains INCOMPLETE_RESEARCH')
