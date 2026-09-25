#!/usr/bin/env python3
"""Replay the prior 45-pose union against the current private TI baseline."""
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
BASE = PROJECT / "06_build/prototype_board_diagnostic/current-ti-baseline-final-20260925"
OUTPUT = PROJECT / "06_build/prototype_board_diagnostic/current-ti-coupled-replay-20260925"
POSES = HERE.parent / "2026-09-25-ti-integrated-placement-sol/expected_poses.json"
EXPECTED = {
    "board": "c5229350807edd85ce95eadd4ec8e4190941b0dd27edcf0a54a6defda145e6b8",
    "floorplan": "c2a6562c1a012e692109b852158af2ef73a432f712a62ae87cbd8e49c4c4ecd6",
    "poses": "76ba7ace1275fe1a8d6bc69d452037672519d70a21b8b02fff67f8c7d8a647bb",
    "pro": "7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094",
    "dru": "00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a",
    "netlist": "a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd",
    "circuit": "580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d",
    "board_generator": "8a5fa1d48d80138458601a097ab6260565841510a498e44cb9c5773652215b3c",
    "rules_generator": "3f423340be27471ce7edca2b66a633dd0898b0a172b7abf12fa944e83690f026",
    "pofv_generator": "b3906f63e07e9f04ada58e757f4095989f6933eca98d93b0f1165e91064529b7",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*args: str, allow_drc: bool = False) -> int:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode and not allow_drc:
        raise RuntimeError(f"{args[0]}: {result.stderr[-1000:]} {result.stdout[-1000:]}")
    return result.returncode


def main() -> None:
    source = BASE / "project"
    baseline = source / "04_kicad/crow_carrier.kicad_pcb"
    base_floorplan = source / "03_src/floorplan.yaml"
    if {"board": sha(baseline), "floorplan": sha(base_floorplan),
        "poses": sha(POSES),
        "pro": sha(source / "04_kicad/crow_carrier.kicad_pro"),
        "dru": sha(source / "04_kicad/crow_carrier.kicad_dru"),
        "netlist": sha(source / "06_build/netlists/crow_carrier.net"),
        "circuit": sha(source / "03_tscircuit/build/circuit.json"),
        "board_generator": sha(REPO / "skills/kicad-pcb/scripts/generate_board_generic.py"),
        "rules_generator": sha(REPO / "skills/kicad-pcb/scripts/generate_rules_generic.py"),
        "pofv_generator": sha(REPO / "skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py")} != EXPECTED:
        raise RuntimeError("baseline, pose set or effective rule bytes changed")
    if OUTPUT.exists():
        raise RuntimeError("refusing to overwrite the private replay")
    pose_set = json.loads(POSES.read_text())["move_union"]
    if len(pose_set) != 45 or "Q_PRE" in pose_set:
        raise RuntimeError("45-pose replay denominator changed")
    shutil.copytree(source, OUTPUT / "project", symlinks=False)
    copy = OUTPUT / "project"
    floorplan = copy / "03_src/floorplan.yaml"
    data = yaml.safe_load(floorplan.read_text())
    anchors = data["placement"]["post_anchors"]
    if anchors.get("Q_PRE") != [46.0, 107.15, 0]:
        raise RuntimeError("current Q_PRE anchor absent")
    for ref, target in pose_set.items():
        anchors[ref] = target
    floorplan.write_text(yaml.safe_dump(data, sort_keys=False))
    board = copy / "04_kicad/crow_carrier.kicad_pcb"
    pro = board.with_suffix(".kicad_pro")
    dru = board.with_suffix(".kicad_dru")
    command(sys.executable, str(REPO / "skills/kicad-pcb/scripts/generate_board_generic.py"),
            str(floorplan), "--netlist", str(copy / "06_build/netlists/crow_carrier.net"),
            "-o", str(board))
    command(sys.executable, str(REPO / "skills/kicad-pcb/scripts/generate_rules_generic.py"),
            str(copy))
    command(sys.executable, str(REPO / "skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py"),
            str(board), "--assembly", str(copy / "03_src/rules/assembly.yaml"))
    if sha(pro) != EXPECTED["pro"] or sha(dru) != EXPECTED["dru"]:
        raise RuntimeError("effective rules changed on coupled replay")
    command(sys.executable, str(REPO / "skills/jlcpcb-fab/scripts/via_process_check.py"),
            str(board), "--assembly", str(copy / "03_src/rules/assembly.yaml"),
            "--json", str(OUTPUT / "via_process.json"))
    command(sys.executable, str(REPO / "skills/kicad-pcb/scripts/count_parity.py"), str(copy))
    command(sys.executable, str(REPO / "skills/kicad-pcb/scripts/pin_map_check.py"),
            str(copy), "--board", str(board), "--circuit-json",
            str(copy / "03_tscircuit/build/circuit.json"), "--parts", str(copy / "02_parts"))
    drc_path = OUTPUT / "drc.json"
    rc = command("kicad-cli", "pcb", "drc", "--severity-all", "--refill-zones",
                 "--schematic-parity", "--format", "json", "--output", str(drc_path),
                 str(board), allow_drc=True)
    drc = json.loads(drc_path.read_text())
    receipt = {"schema": 1, "status": "RESEARCH_DIAGNOSTIC", "board_sha256": sha(board),
               "baseline_board_sha256": EXPECTED["board"],
               "floorplan_sha256": sha(floorplan), "pose_set_sha256": EXPECTED["poses"],
               "pose_count": len(pose_set), "pro_sha256": sha(pro), "dru_sha256": sha(dru),
               "drc_sha256": sha(drc_path), "drc_exit_code": rc,
               "drc_counts": {name: len(drc.get(name, [])) for name in
                              ("violations", "unconnected_items", "schematic_parity")},
               "drc_issue_types": sorted({row.get("type", "") for row in drc.get("violations", [])}),
               "engineering_acceptance": False, "p1_accepted": False,
               "p2_accepted": False, "route_credit": False,
               "release_admitted": False, "order_admitted": False}
    (OUTPUT / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
