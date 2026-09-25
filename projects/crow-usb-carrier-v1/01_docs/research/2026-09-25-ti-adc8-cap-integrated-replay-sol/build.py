#!/usr/bin/env python3
"""Source-generate the exact integrated TI union with only the ADC8 cap recut."""
from __future__ import annotations
import hashlib, json, shutil, subprocess, tempfile
from pathlib import Path
import yaml

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
P=ROOT/'projects/crow-usb-carrier-v1'
TI=P/'06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
PRIOR=P/'01_docs/research/2026-09-25-ti-integrated-placement-sol'
TERRA=P/'01_docs/research/2026-09-25-ti-adc8-pocket-adjustment-terra.md'
SOURCE=TI/'03_src/floorplan.yaml'
POSES=PRIOR/'expected_poses.json'
BOARD=HERE/'candidate.kicad_pcb'
GEN=ROOT/'skills/kicad-pcb/scripts/generate_board_generic.py'
EXPECTED={
 'source':'0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868',
 'netlist':'a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd',
 'poses':'76ba7ace1275fe1a8d6bc69d452037672519d70a21b8b02fff67f8c7d8a647bb',
 'prior_board':'20373950748ac51113b115b2d12d169160c24024a2a000572bb70c67b0f60919',
 'terra_note':'afa8fe17f6790197ec7ef8d28bc687dea15c212b5978b03c82019dcb234399a1',
}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    paths={'source':SOURCE,'netlist':TI/'06_build/netlists/crow_carrier.net',
           'poses':POSES,'prior_board':PRIOR/'candidate.kicad_pcb','terra_note':TERRA}
    found={k:sha(v) for k,v in paths.items()}
    if found!=EXPECTED:raise SystemExit(f'input SHA drift: {found}')
    expected=json.loads(POSES.read_text())
    if len(expected['move_union'])!=45 or expected['move_union']['C_ADC_AC8N1']!=[198.2,60.25,0.0]:
        raise SystemExit('prior integrated pose denominator/ADC8 cap drift')
    cfg=yaml.safe_load(SOURCE.read_text())
    if cfg['placement']['post_anchors']['Q_PRE']!=[46.0,106.85,0]:
        raise SystemExit('frozen TI Q_PRE baseline drift')
    cfg['placement']['post_anchors']['Q_PRE']=[46.0,107.15,0]
    cfg['placement']['post_anchors'].update(expected['move_union'])
    cfg['placement']['post_anchors']['C_ADC_AC8N1']=[198.0,60.05,0]
    with tempfile.TemporaryDirectory(prefix='crow-adc8-cap-source-') as d:
        root=Path(d)
        (root/'03_src').mkdir();(root/'04_kicad').mkdir();(root/'06_build').mkdir()
        (root/'02_parts').symlink_to(TI/'02_parts',target_is_directory=True)
        (root/'03_src/lib').symlink_to(TI/'03_src/lib',target_is_directory=True)
        (root/'03_src/rules').symlink_to(TI/'03_src/rules',target_is_directory=True)
        (root/'06_build/netlists').symlink_to(TI/'06_build/netlists',target_is_directory=True)
        config=root/'03_src/floorplan.yaml'
        config.write_text(yaml.safe_dump(cfg,sort_keys=False))
        native=root/'04_kicad/crow_carrier.kicad_pcb'
        subprocess.run(['python3',str(GEN),str(config),'-o',str(native)],check=True)
        shutil.copy2(native,BOARD)
    print(json.dumps({'trial_board_sha256':sha(BOARD),'cap_pose_mm':[198.0,60.05,0]},sort_keys=True))

if __name__=='__main__':main()
