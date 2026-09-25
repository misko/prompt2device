#!/usr/bin/env python3
"""Read-only exact-board pose, DRC, and P1 receipt verification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BASE = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-six-20260925/project/04_kicad/crow_carrier.kicad_pcb'
PRIVATE = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925'
BOARD = PRIVATE / '04_kicad/crow_carrier.kicad_pcb'
FLOOR = PRIVATE / '03_src/floorplan.yaml'
DRC = PRIVATE / '06_build/drc/expanded_locked_pre_route.json'
DRC_LOG = PRIVATE / '06_build/expanded_locked_drc.log'
EXPECTED = {
    'base': '009ecf6383f07129653758fdc0855c793d8915e4ae5b0980278e7a5fa4fc47c7',
    'board': 'fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16',
    'floor': '2f7843ada9eb08d19d268f0d6671079a8cf367629b2b3331119088927415b634',
}
HOLES = {'H1': (30, 40), 'H2': (130, 40), 'H3': (211.5, 45),
         'H4': (18, 82), 'H5': (130, 142), 'H6': (230, 130)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def poses(path: Path) -> dict[str, tuple[int, int, float]]:
    board = pcbnew.LoadBoard(str(path))
    return {fp.GetReference(): (fp.GetPosition().x, fp.GetPosition().y,
                                fp.GetOrientationDegrees())
            for fp in board.GetFootprints()}


def main() -> None:
    for name, path in {'base': BASE, 'board': BOARD, 'floor': FLOOR}.items():
        if sha(path) != EXPECTED[name]:
            raise SystemExit(f'{name}: pinned SHA drift')
    before, after = poses(BASE), poses(BOARD)
    electrical = {ref for ref in before if not ref.startswith('H')}
    if len(electrical) != 569 or any(before[ref] != after.get(ref)
                                     for ref in electrical):
        raise SystemExit('electrical pose drift')
    if {ref for ref in after if ref.startswith('H')} != set(HOLES):
        raise SystemExit('mounting-hole ref denominator drift')
    for ref, (x, y) in HOLES.items():
        if after[ref] != (pcbnew.FromMM(x), pcbnew.FromMM(y), 0):
            raise SystemExit(f'{ref}: mounting-hole pose drift')
    drc = json.loads(DRC.read_text())
    counts = {key: len(drc[key]) for key in
              ('violations', 'schematic_parity', 'unconnected_items')}
    if counts != {'violations': 0, 'schematic_parity': 0,
                  'unconnected_items': 499}:
        raise SystemExit(f'DRC shape drift: {counts}')
    if ('Failed to fetch schematic netlist for parity tests.' not in
            DRC_LOG.read_text()):
        raise SystemExit('native schematic-parity availability changed')
    p1 = json.loads((HERE/'receipt.json').read_text())
    if (p1['board_sha256'] != EXPECTED['board'] or
            p1['status'] != 'INCOMPLETE' or p1['p1_accepted'] or
            p1['routing_realized'] or p1['errors'] or p1['diagnostics'] or
            p1['unchanged_virtual_power_windows'] != 9 or
            any(status != 'INCOMPLETE' for status in p1['allocations'].values())):
        raise SystemExit('P1 no-credit receipt drift')
    print(json.dumps({'status': 'RESEARCH_INCOMPLETE',
                      'board_sha256': EXPECTED['board'],
                      'electrical_poses_preserved': len(electrical),
                      'mounting_holes': HOLES, 'drc_counts': counts,
                      'native_schematic_parity_performed': False,
                      'p1_status': p1['status'],
                      'p1_diagnostics': len(p1['diagnostics'])}, indent=2))


if __name__ == '__main__':
    main()
