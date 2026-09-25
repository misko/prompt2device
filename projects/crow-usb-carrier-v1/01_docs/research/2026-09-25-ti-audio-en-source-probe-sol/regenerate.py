#!/usr/bin/env python3
"""Regenerate the isolated AUDIO_EN trial from frozen TI sources and overlay."""
from __future__ import annotations
import argparse, hashlib, shutil, subprocess, tempfile
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
P = ROOT / 'projects/crow-usb-carrier-v1'
TI = P / '06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
GEN = ROOT / 'skills/kicad-pcb/scripts/generate_board_generic.py'
SOURCE = TI / '03_src/floorplan.yaml'
OVERLAY = HERE / 'generator_overlay.yaml'
EXPECTED = {
    'source': '0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868',
    'netlist': 'a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd',
    'overlay': '242837d37be4f0ceec3beb2a93900d136c37e5f6d7d5ed8b966460caf93a096a',
    'trial_board': 'f1f491c22b20c853fc9d208265237364cbcec3992e4818759281eaa32fc69eac',
    'baseline_board': '612d319fdafd5b9eaa085f64c7752f94a0953a659f9b883cd5008b6504eeab71',
}
TRIAL_REFS = ('R_AUDIO_PD', 'U_AUDIO', 'U_ISO1')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', action='store_true', help='omit the three AUDIO_EN trial anchors')
    ap.add_argument('--output', type=Path, help='board output; default is packet trial or /tmp baseline')
    args = ap.parse_args()
    if sha(SOURCE) != EXPECTED['source'] or sha(TI/'06_build/netlists/crow_carrier.net') != EXPECTED['netlist'] or sha(OVERLAY) != EXPECTED['overlay']:
        raise SystemExit('frozen source/netlist/overlay SHA drift')
    cfg = yaml.safe_load(OVERLAY.read_text())
    if args.baseline:
        original = yaml.safe_load(SOURCE.read_text())['placement']['post_anchors']
        for ref in TRIAL_REFS:
            if ref in original:
                cfg['placement']['post_anchors'][ref] = original[ref]
            else:
                cfg['placement']['post_anchors'].pop(ref, None)
    with tempfile.TemporaryDirectory(prefix='crow-audio-source-') as d:
        root = Path(d)
        (root/'03_src').mkdir(); (root/'04_kicad').mkdir(); (root/'06_build').mkdir()
        (root/'02_parts').symlink_to(TI/'02_parts', target_is_directory=True)
        (root/'03_src/lib').symlink_to(TI/'03_src/lib', target_is_directory=True)
        (root/'03_src/rules').symlink_to(TI/'03_src/rules', target_is_directory=True)
        (root/'06_build/netlists').symlink_to(TI/'06_build/netlists', target_is_directory=True)
        config = root/'03_src/floorplan.yaml'
        config.write_text(yaml.safe_dump(cfg, sort_keys=False))
        native = root/'04_kicad/crow_carrier.kicad_pcb'
        subprocess.run(['python3',str(GEN),str(config),'-o',str(native)],check=True)
        want = EXPECTED['baseline_board' if args.baseline else 'trial_board']
        if sha(native) != want: raise SystemExit(f'generated board SHA drift: {sha(native)} != {want}')
        out = args.output or (Path('/tmp/crow-audio-source-baseline.kicad_pcb') if args.baseline else HERE/'candidate.kicad_pcb')
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(native,out)
        print(f'{out}: {sha(out)}')

if __name__ == '__main__': main()
