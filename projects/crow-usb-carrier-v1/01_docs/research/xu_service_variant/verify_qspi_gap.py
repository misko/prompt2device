#!/usr/bin/env python3
"""Verify the pinned QSPI gap regeneration."""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
RECT = Path('/tmp/crow-xu-rect-regen-sol/project')
GAP = Path('/tmp/crow-xu-qspi-gap-sol/project')
for name, project in [('rectangle', RECT), ('gap', GAP)]:
    if not project.is_dir():
        raise SystemExit(f'{name} project unavailable: {project}')
result = subprocess.run([sys.executable, str(HERE/'compare_qspi_gap.py'), str(RECT), str(GAP)],
                        check=True, capture_output=True, text=True)
actual = json.loads(result.stdout)
assert actual == json.loads((HERE/'qspi_gap.json').read_text())
assert not actual['region_overlaps'] and not actual['regions_outside_outline']
assert actual['diagnostic_window_fits_corridor']
assert actual['qspi_face']['raw_width_mm'] >= actual['qspi_face']['required_width_mm']
assert not actual['corridor_native_footprint_hits'] and not actual['corridor_native_pad_hits']
assert not actual['assigned_outside_owner'] and not actual['pad_identity_changed_refs']
assert not actual['p1_fixed_moved_refs'] and actual['p1_fixed_count'] == 27
assert actual['baseline']['footprints'] == actual['gap_variant']['footprints'] == 569
assert actual['baseline']['pads'] == actual['gap_variant']['pads'] == 1872
print('QSPI source-gap geometry reproduced; status remains INCOMPLETE_RESEARCH')
