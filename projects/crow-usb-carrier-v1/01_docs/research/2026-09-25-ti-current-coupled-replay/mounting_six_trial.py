#!/usr/bin/env python3
"""Regenerate one private mechanical-support placement trial for Crow."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import yaml

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
REPO = PROJECT.parents[1]
BASE = PROJECT / '06_build/prototype_board_diagnostic/current-ti-audio-en-three-pose-20260925/project'
OUTPUT = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-six-20260925'
HOLES = [[30, 40], [130, 40], [212, 45], [30, 82], [130, 132], [230, 130]]
EXPECTED = {
    'board': '0bd3ac8dd8c80177958c009a0644f0bc723bcee7ad7085c2fb76c09c5df958f5',
    'floor': '5d705a162c5ad4c8ee797dfeb3921b230b16126e603341b43fffbc21de602bcb',
    'pro': '7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094',
    'dru': '00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a',
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args: str, allow_drc: bool = False) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode and not allow_drc:
        raise RuntimeError(f'{args[0]}: {result.stdout[-1000:]} {result.stderr[-1000:]}')


def main() -> None:
    if {'board': sha(BASE / '04_kicad/crow_carrier.kicad_pcb'),
        'floor': sha(BASE / '03_src/floorplan.yaml'),
        'pro': sha(BASE / '04_kicad/crow_carrier.kicad_pro'),
        'dru': sha(BASE / '04_kicad/crow_carrier.kicad_dru')} != EXPECTED:
        raise RuntimeError('exact private source board or rules changed')
    if OUTPUT.exists():
        raise RuntimeError('refusing to overwrite the private support trial')
    shutil.copytree(BASE, OUTPUT / 'project')
    copy = OUTPUT / 'project'
    floor = copy / '03_src/floorplan.yaml'
    data = yaml.safe_load(floor.read_text())
    if data['board'].get('mounting_holes'):
        raise RuntimeError('source already declares mounting holes')
    data['board']['mounting_holes'] = {
        'footprint': 'MountingHole:MountingHole_3.2mm_M3',
        'refdes_prefix': 'H', 'at': HOLES}
    floor.write_text(yaml.safe_dump(data, sort_keys=False))
    board = copy / '04_kicad/crow_carrier.kicad_pcb'
    run(sys.executable, str(REPO / 'skills/kicad-pcb/scripts/generate_board_generic.py'),
        str(floor), '--netlist', str(copy / '06_build/netlists/crow_carrier.net'),
        '-o', str(board))
    run(sys.executable, str(REPO / 'skills/kicad-pcb/scripts/generate_rules_generic.py'), str(copy))
    run(sys.executable, str(REPO / 'skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py'),
        str(board), '--assembly', str(copy / '03_src/rules/assembly.yaml'))
    if sha(board.with_suffix('.kicad_pro')) != EXPECTED['pro'] or \
            sha(board.with_suffix('.kicad_dru')) != EXPECTED['dru']:
        raise RuntimeError('effective rules changed')
    run(sys.executable, str(REPO / 'skills/kicad-pcb/scripts/count_parity.py'), str(copy))
    run(sys.executable, str(REPO / 'skills/kicad-pcb/scripts/pin_map_check.py'),
        str(copy), '--board', str(board), '--circuit-json',
        str(copy / '03_tscircuit/build/circuit.json'), '--parts', str(copy / '02_parts'))
    report = OUTPUT / 'drc.json'
    run('kicad-cli', 'pcb', 'drc', '--severity-all', '--refill-zones',
        '--schematic-parity', '--format', 'json', '--output', str(report), str(board),
        allow_drc=True)
    drc = json.loads(report.read_text())
    counts = {key: len(drc.get(key, [])) for key in
              ('violations', 'unconnected_items', 'schematic_parity')}
    if counts != {'violations': 0, 'unconnected_items': 499, 'schematic_parity': 0}:
        raise RuntimeError(f'native DRC changed: {counts}')
    receipt = {'status': 'RESEARCH_DIAGNOSTIC', 'board_sha256': sha(board),
               'baseline_board_sha256': EXPECTED['board'],
               'floorplan_sha256': sha(floor), 'mounting_holes': HOLES,
               'drc_counts': counts, 'p1_accepted': False,
               'connector_full': False, 'routing_realized': False,
               'release_admitted': False, 'order_admitted': False}
    (OUTPUT / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
