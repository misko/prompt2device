"""Explicit final native schematic/PCB DRC parity in a new isolated packet.

Diagnostic producer, not stage acceptance. No library/model edits or automatic
schematic reconciliation. A failing candidate retains its complete CLI evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(board, schematic, output):
    board, schematic, output = map(Path, (board, schematic, output))
    if not board.is_file() or not schematic.is_file() or output.exists():
        raise ValueError('existing native inputs and NEW output directory required')
    if board.is_symlink() or schematic.is_symlink():
        raise ValueError('linked authoritative input refused')
    if output.resolve().is_relative_to(board.parent.resolve()):
        raise ValueError('output must be outside source resource directory')
    members = list(board.parent.rglob('*'))
    if any(p.is_symlink() for p in members):
        raise ValueError('linked native resource refused')
    inputs = {str(p.resolve()): digest(p) for p in members if p.is_file()}
    inputs[str(schematic.resolve())] = digest(schematic)
    output.mkdir(parents=True)
    native = output/'native'
    shutil.copytree(board.parent, native)
    target_schematic = native/(board.stem+'.kicad_sch')
    if target_schematic.exists():
        raise ValueError('ambiguous pre-existing native schematic')
    shutil.copyfile(schematic, target_schematic)
    command = ['kicad-cli', 'pcb', 'drc', '--format', 'json', '--units', 'mm',
               '--severity-all', '--all-track-errors', '--refill-zones',
               '--schematic-parity', '--exit-code-violations',
               '--output', str((output/'drc.json').resolve()),
               str((native/board.name).resolve())]
    process = subprocess.run(command, capture_output=True, text=True, timeout=300)
    (output/'stdout.txt').write_text(process.stdout)
    (output/'stderr.txt').write_text(process.stderr)
    changed = [name for name, expected in inputs.items() if digest(Path(name)) != expected]
    report_path = output/'drc.json'
    report = json.loads(report_path.read_text()) if report_path.is_file() else {}
    required = ('violations', 'unconnected_items', 'schematic_parity')
    complete = all(isinstance(report.get(k), list) for k in required)
    clean = complete and not any(report[k] for k in required)
    result = {'schema': 1, 'command': command, 'exit_code': process.returncode,
              'input_sha256': inputs, 'inputs_changed': changed,
              'kicad_version': subprocess.check_output(['kicad-cli', 'version'], text=True).strip(),
              'schematic_parity_executed': '--schematic-parity' in command,
              'counts': {k: len(report[k]) if isinstance(report.get(k), list) else None for k in required},
              'verdict': 'PASS' if process.returncode == 0 and clean and not changed else 'FAIL',
              'acceptance': False}
    (output/'parity.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('board', 'schematic', 'output'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args.board, args.schematic, args.output)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['verdict'] == 'PASS' else 1)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print('Native parity refused: '+str(error), file=sys.stderr)
        sys.exit(2)
