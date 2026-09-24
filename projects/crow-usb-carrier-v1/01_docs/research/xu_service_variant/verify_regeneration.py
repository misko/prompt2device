#!/usr/bin/env python3
"""Verify the pinned, read-only rectangle regeneration record."""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BASE = Path('/tmp/crow-usb-regions-terra-HqnO4Z/project')
VARIANT = Path('/tmp/crow-xu-rect-regen-sol/project')
for name, path in [('baseline', BASE), ('variant', VARIANT)]:
    if not path.is_dir():
        raise SystemExit(f'{name} project absent: {path}')
result = subprocess.run([sys.executable, str(HERE/'compare_regenerated.py'),
                         str(BASE), str(VARIANT)], check=True, capture_output=True, text=True)
actual = json.loads(result.stdout)
expected = json.loads((HERE/'regeneration.json').read_text())
assert actual == expected, 'regeneration measurement changed'
assert len(actual['moved_footprints']) == 10
assert not actual['changed_pad_identity_refs']
assert not actual['p1_fixed_moved_refs']
assert not actual['assigned_outside_cell']
assert not actual['source_region_intersections']
assert actual['zone_inventory_equal']
assert all(not hits for hits in actual['diagnostic_window_footprint_hits'].values())
print('rectangle regeneration reproduced; status remains INCOMPLETE_RESEARCH')
