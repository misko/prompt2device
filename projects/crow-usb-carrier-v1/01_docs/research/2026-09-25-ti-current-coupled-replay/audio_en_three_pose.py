#!/usr/bin/env python3
"""Replay one AUDIO_EN owner-placement candidate on the private TI board."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
REPO = PROJECT.parents[1]
BASE = PROJECT / '06_build/prototype_board_diagnostic/current-ti-coupled-replay-20260925/project'
OUTPUT = PROJECT / '06_build/prototype_board_diagnostic/current-ti-audio-en-three-pose-20260925'
EXPECTED = {
    'board': 'bdd5bccb2617d7bbe1de9cd27cda1a0e2f68467bedd169704473a010286a948b',
    'floor': 'c773e0703b79b7c37350e54da34ecf39da8148e2476996b6d1990126db55efa0',
    'pro': '7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094',
    'dru': '00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a',
}
POSES = {'U_ISO1': [27.05, 74.6, 0],
         'U_AUDIO': [28.7, 109.85, 0],
         'R_AUDIO_PD': [28.45, 106.1, 90]}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args: str, drc: bool = False) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode and not drc:
        raise RuntimeError(f'{args[0]}: {result.stdout[-1000:]} {result.stderr[-1000:]}')


def main() -> None:
    if {'board': sha(BASE / '04_kicad/crow_carrier.kicad_pcb'),
        'floor': sha(BASE / '03_src/floorplan.yaml'),
        'pro': sha(BASE / '04_kicad/crow_carrier.kicad_pro'),
        'dru': sha(BASE / '04_kicad/crow_carrier.kicad_dru')} != EXPECTED:
        raise RuntimeError('exact private TI input or rules changed')
    if OUTPUT.exists():
        raise RuntimeError('refusing to overwrite the private candidate')
    shutil.copytree(BASE, OUTPUT / 'project')
    copy = OUTPUT / 'project'
    floor = copy / '03_src/floorplan.yaml'
    data = yaml.safe_load(floor.read_text())
    for ref, pose in POSES.items():
        data['placement']['post_anchors'][ref] = pose
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
        '--schematic-parity', '--format', 'json', '--output', str(report), str(board), drc=True)
    data = json.loads(report.read_text())
    counts = {key: len(data.get(key, [])) for key in
              ('violations', 'unconnected_items', 'schematic_parity')}
    if counts != {'violations': 0, 'unconnected_items': 499, 'schematic_parity': 0}:
        raise RuntimeError(f'native DRC changed: {counts}')
    receipt = {'status': 'RESEARCH_DIAGNOSTIC', 'board_sha256': sha(board),
               'baseline_board_sha256': EXPECTED['board'],
               'floorplan_sha256': sha(floor), 'poses': POSES,
               'drc_counts': counts, 'p1_accepted': False,
               'routing_realized': False, 'release_admitted': False}
    (OUTPUT / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
