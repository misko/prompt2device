#!/usr/bin/python3
"""Replay the unadopted 3313A rule and four native synthetic DRC controls."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pcbnew as p
import yaml

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
ROOT = HERE.parents[4]
BASE = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925'
HASHES = {
    '03_src/floorplan.yaml': '2f7843ada9eb08d19d268f0d6671079a8cf367629b2b3331119088927415b634',
    '03_src/rules/nets.yaml': '18033487a097b6d29abe3f9d8517879931cf80d278d8973adcf276010a5b7190',
    '03_src/route.yaml': 'f49ca740665ce4cfdceb1c82701ddae548f140c8ee1735746040c523c96c8608',
    '03_src/rules/rf.yaml': '833a8c022648859e65ba3b727bffd14c868214936a9751f12c5a15ecd3ea376c',
    '04_kicad/crow_carrier.kicad_pcb': 'fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16',
    '04_kicad/crow_carrier.kicad_pro': '7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094',
    '04_kicad/crow_carrier.kicad_dru': '00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a',
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--write-result', type=Path,
                    help='write a new immutable capture path; existing paths are refused')
parser.add_argument('--base', type=Path, default=BASE,
                    help='frozen input copy to verify; defaults to the expanded-locked board')
parser.add_argument('--verify-inputs-only', action='store_true',
                    help='verify all frozen hashes and exit before any proposal replay')
args = parser.parse_args()

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def run(cmd, **kw):
    out = subprocess.run(cmd, text=True, capture_output=True, **kw)
    if out.returncode and cmd[0] != 'kicad-cli':
        raise RuntimeError(f'{cmd}: {out.stdout[-1000:]} {out.stderr[-1000:]}')
    return out

for rel, expected in HASHES.items():
    actual = sha(args.base / rel)
    if actual != expected: raise RuntimeError(f'base hash drift: {rel}: {actual}')
if args.verify_inputs_only:
    print('FROZEN_3313_INPUT_HASHES_PASS')
    sys.exit(0)

rows = []
with tempfile.TemporaryDirectory(prefix='crow3313-coupon-') as raw:
    tmp = Path(raw)
    (tmp/'03_src/rules').mkdir(parents=True)
    (tmp/'04_kicad').mkdir()
    (tmp/'02_parts').symlink_to(args.base/'02_parts')
    for rel in list(HASHES)[:4] + ['03_src/rules/assembly.yaml']:
        shutil.copy2(args.base/rel, tmp/rel)
    for suffix in ('pcb', 'pro', 'dru'):
        shutil.copy2(args.base/f'04_kicad/crow_carrier.kicad_{suffix}',
                     tmp/f'04_kicad/crow_carrier.kicad_{suffix}')
    run(['patch', '-p1', '-d', str(tmp), '--input', str(HERE/'source_diff.patch')])
    run([sys.executable, str(ROOT/'skills/kicad-pcb/scripts/generate_rules_generic.py'), str(tmp)])
    dru = (tmp/'04_kicad/crow_carrier.kicad_dru').read_text()
    match = re.search(r'\(rule "controlled_pair_clr_USB_DEVICE"\n.*?\n  \(constraint clearance \(min 0\.1mm\)\)\)', dru, re.S)
    if not match: raise RuntimeError('generated exact pair rule absent')
    rule = match.group(0)
    sys.path.insert(0, str(ROOT/'skills/jlcpcb-fab/scripts'))
    from via_process_check import controlled_pair_dru_rules
    native = p.LoadBoard(str(tmp/'04_kicad/crow_carrier.kicad_pcb'))
    derived = controlled_pair_dru_rules(tmp/'03_src/rules/assembly.yaml', native)
    if len(derived) != 4 or derived[0] != rule or any(dru.count(item) != 1 for item in derived):
        raise RuntimeError('independent process rule re-derivation differs')
    nets_path = tmp/'03_src/rules/nets.yaml'
    valid_source = nets_path.read_text()
    negative_sources = []
    for name in ('widened_selector', 'second_pair', 'back_layer'):
        changed = yaml.safe_load(valid_source)
        spec = changed['controlled_pair_clearances'][0]
        if name == 'widened_selector': spec['nets_b'].append('OTHER')
        elif name == 'second_pair': changed['controlled_pair_clearances'].append(dict(spec))
        else: spec['layer'] = 'B.Cu'
        nets_path.write_text(yaml.safe_dump(changed, sort_keys=False))
        rejected = subprocess.run([sys.executable,
            str(ROOT/'skills/kicad-pcb/scripts/generate_rules_generic.py'), str(tmp)],
            capture_output=True, text=True)
        if rejected.returncode == 0:
            raise RuntimeError(f'{name}: widened source unexpectedly generated')
        negative_sources.append({'case': name, 'generator_rejected': True})
    nets_path.write_text(valid_source)
    run([sys.executable, str(ROOT/'skills/kicad-pcb/scripts/generate_rules_generic.py'), str(tmp)])
    cases = [('pair_100', .100, 'USB_DN', p.F_Cu, None, False),
             ('pair_099', .099, 'USB_DN', p.F_Cu, 'controlled_pair_clr_USB_DEVICE', False),
             ('foreign_140', .140, 'FOREIGN', p.F_Cu, 'generic_copper_clearance', False),
             ('back_pair_140', .140, 'USB_DN', p.B_Cu, 'generic_copper_clearance', False),
             ('full_pair_100', .100, 'USB_DN', p.F_Cu, None, True),
             ('full_pair_099', .099, 'USB_DN', p.F_Cu, 'controlled_pair_clr_USB_DEVICE', True),
             ('full_foreign_140', .140, 'FOREIGN', p.F_Cu, '0.1500 mm', True),
             ('full_in1_pair_140', .140, 'USB_DN', p.In1_Cu, 'controlled_pair_clr_USB_DEVICE_In1_Cu', True),
             ('full_in2_pair_140', .140, 'USB_DN', p.In2_Cu, 'controlled_pair_clr_USB_DEVICE_In2_Cu', True),
             ('full_back_pair_140', .140, 'USB_DN', p.B_Cu, '0.1500 mm', True)]
    for name, gap, second, layer, expected_rule, full_sidecar in cases:
        folder = tmp/name
        folder.mkdir()
        board = p.BOARD()
        board.SetCopperLayerCount(4)
        nets = {}
        for net in ('USB_DP', second):
            info = p.NETINFO_ITEM(board, net)
            board.Add(info)
            nets[net] = info
        for y, net in ((10.0, 'USB_DP'), (10.18+gap, second)):
            track = p.PCB_TRACK(board)
            track.SetStart(p.VECTOR2I_MM(10, y))
            track.SetEnd(p.VECTOR2I_MM(15, y))
            track.SetWidth(p.FromMM(.18))
            track.SetLayer(layer)
            track.SetNet(nets[net])
            board.Add(track)
        pcb = folder/'pair.kicad_pcb'
        p.SaveBoard(str(pcb), board)
        if full_sidecar:
            shutil.copy2(tmp/'04_kicad/crow_carrier.kicad_pro', folder/'pair.kicad_pro')
            shutil.copy2(tmp/'04_kicad/crow_carrier.kicad_dru', folder/'pair.kicad_dru')
        else:
            project = json.loads((tmp/'04_kicad/crow_carrier.kicad_pro').read_text())
            project['board']['design_settings']['rules']['min_clearance'] = .09
            (folder/'pair.kicad_pro').write_text(json.dumps(project))
            (folder/'pair.kicad_dru').write_text('(version 1)\n'
                '(rule "generic_copper_clearance" (constraint clearance (min 0.150mm)))\n'+rule+'\n')
        proc = run(['kicad-cli', 'pcb', 'drc', '--output', str(folder/'drc.txt'), str(pcb)])
        report = (folder/'drc.txt').read_text() if (folder/'drc.txt').exists() else ''
        clearances = [line for line in report.splitlines() if line.startswith('[clearance]:')]
        if expected_rule is None and clearances:
            raise RuntimeError(f'{name}: unexpected clearance {clearances}')
        if expected_rule is not None and (len(clearances) != 1 or expected_rule not in clearances[0]):
            raise RuntimeError(f'{name}: missing expected {expected_rule}: {clearances}; report={report[:1500]}')
        if 'error parsing' in proc.stderr.lower() or 'failed to load' in proc.stderr.lower():
            raise RuntimeError(f'{name}: KiCad rule parse failure: {proc.stderr}')
        rows.append({'case': name, 'clearance': clearances, 'board_sha256': sha(pcb),
                     'dru_sha256': sha(folder/'pair.kicad_dru'),
                     'drc_sha256': sha(folder/'drc.txt')})
    version = run(['kicad-cli', 'version'])
    result = {'status': 'PASS', 'base_sha256': HASHES, 'proposal_sha256': sha(HERE/'source_diff.patch'),
              'replay_sha256': sha(Path(__file__)),
              'kicad_cli_version': version.stdout.strip(), 'pcbnew_version': p.Version(),
              'negative_sources': negative_sources,
              'generated_rule_sha256': hashlib.sha256(rule.encode()).hexdigest(), 'controls': rows}
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.write_result:
        with args.write_result.open('x') as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
