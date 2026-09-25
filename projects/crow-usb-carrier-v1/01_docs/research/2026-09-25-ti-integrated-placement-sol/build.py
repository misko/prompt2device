#!/usr/bin/env python3
"""Generate a research-only union of the independently reviewed placement poses."""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
P = ROOT / 'projects/crow-usb-carrier-v1'
TI = P / '06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
SOURCE = TI / '03_src/floorplan.yaml'
CANONICAL = P / '03_src/floorplan.yaml'
NETLIST = TI / '06_build/netlists/crow_carrier.net'
ADC8 = P / '01_docs/research/2026-09-25-ti-cin3-qpre-owner-repair-sol/generator_overlay.yaml'
TIMING = P / '01_docs/research/2026-09-25-ti-timing-coupled-placement-sol/result.json'
GEN = ROOT / 'skills/kicad-pcb/scripts/generate_board_generic.py'
EXPECTED = {
    'source': '0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868',
    'canonical_floorplan': 'c2a6562c1a012e692109b852158af2ef73a432f712a62ae87cbd8e49c4c4ecd6',
    'netlist': 'a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd',
    'adc8_overlay': 'b52d3bceae1440da47baef1e05291048e6ea0ec4b7de2b7fbb32f0e8382a62f3',
    'timing_result': 'f92b04a311432f42c721ed4619631f06568821816409bb5fd97742c666d16b71',
}

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    paths = {'source': SOURCE, 'canonical_floorplan': CANONICAL, 'netlist': NETLIST,
             'adc8_overlay': ADC8, 'timing_result': TIMING}
    actual = {name: sha(path) for name, path in paths.items()}
    if actual != EXPECTED:
        raise SystemExit(f'bound input drift: {actual}')
    source = yaml.safe_load(SOURCE.read_text())
    canonical = yaml.safe_load(CANONICAL.read_text())
    adc8 = yaml.safe_load(ADC8.read_text())
    timing = json.loads(TIMING.read_text())
    base_anchors = source['placement']['post_anchors']
    prior_anchors = adc8['placement']['post_anchors']
    if canonical['placement']['post_anchors']['Q_PRE'] != [46.0, 107.15, 0]:
        raise SystemExit('reviewed canonical Q_PRE pose absent')
    if base_anchors['Q_PRE'] != [46.0, 106.85, 0]:
        raise SystemExit('frozen TI Q_PRE baseline drift')
    local = {ref: pose for ref, pose in prior_anchors.items() if ref not in base_anchors}
    if len(local) != 19:
        raise SystemExit(f'expected four ADC7 and fifteen analog/VMID moves, got {len(local)}')
    if set(local) & set(timing['moves']) != {'C_ADC_I2C_B'}:
        raise SystemExit('unexpected local/timing move overlap')
    if len(timing['moves']) != 27:
        raise SystemExit('timing pose denominator drift')
    source['placement']['post_anchors']['Q_PRE'] = canonical['placement']['post_anchors']['Q_PRE']
    if not args.baseline:
        source['placement']['post_anchors'].update(local)
        for ref, row in timing['moves'].items():
            if ref == 'C_ADC_I2C_B' and list(local[ref]) != [172.8, 95, 0]:
                raise SystemExit('timing transition starts from wrong ADC7 pose')
            source['placement']['post_anchors'][ref] = row['to']
    with tempfile.TemporaryDirectory(prefix='crow-integrated-placement-') as d:
        root = Path(d)
        (root / '03_src').mkdir(); (root / '04_kicad').mkdir(); (root / '06_build').mkdir()
        (root / '02_parts').symlink_to(TI / '02_parts', target_is_directory=True)
        (root / '03_src/lib').symlink_to(TI / '03_src/lib', target_is_directory=True)
        (root / '03_src/rules').symlink_to(TI / '03_src/rules', target_is_directory=True)
        (root / '06_build/netlists').symlink_to(TI / '06_build/netlists', target_is_directory=True)
        config = root / '03_src/floorplan.yaml'
        config.write_text(yaml.safe_dump(source, sort_keys=False))
        board = root / '04_kicad/crow_carrier.kicad_pcb'
        subprocess.run(['python3', str(GEN), str(config), '-o', str(board)], check=True)
        output = HERE / ('baseline.kicad_pcb' if args.baseline else 'candidate.kicad_pcb')
        shutil.copy2(board, output)
    if args.baseline:
        print(sha(HERE / 'baseline.kicad_pcb'))
        return
    (HERE / 'expected_poses.json').write_text(json.dumps({
        'source_sha256': actual['source'],
        'candidate_sha256': sha(HERE / 'candidate.kicad_pcb'),
        'canonical_qpre': canonical['placement']['post_anchors']['Q_PRE'],
        'adc7_ch8_vmid_count': len(local),
        'timing_count': len(timing['moves']),
        'timing_supersedes': ['C_ADC_I2C_B'],
        'move_union': {**local, **{r: row['to'] for r, row in timing['moves'].items()}},
    }, indent=2, sort_keys=True) + '\n')
    print(sha(HERE / 'candidate.kicad_pcb'))

if __name__ == '__main__': main()
