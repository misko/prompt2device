#!/usr/bin/env /usr/bin/python3
"""Prepare one D19 source-only scratch packet; never generate a native board."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import pcbnew
import yaml

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
ROOT = HERE.parents[4]
REFERENCE = PROJECT / "06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925"
PROPOSAL = HERE.parent / "2026-09-25-unadopted-3313a-controlled-pair-sol/source_diff.patch"
RESET = HERE.parent / "2026-09-25-reset-two-corridor-schema-probe-sol/build_linked.py"
P1_BASE = HERE.parent / "2026-09-25-ti-expanded-locked-p1-sol"
EXPECTED = {
    "board": "fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16",
    "pro": "7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094",
    "dru": "00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a",
    "floorplan": "2f7843ada9eb08d19d268f0d6671079a8cf367629b2b3331119088927415b634",
    "nets": "18033487a097b6d29abe3f9d8517879931cf80d278d8973adcf276010a5b7190",
    "route": "f49ca740665ce4cfdceb1c82701ddae548f140c8ee1735746040c523c96c8608",
    "rf": "833a8c022648859e65ba3b727bffd14c868214936a9751f12c5a15ecd3ea376c",
    "proposal": "707d8b94075190bf601aba410738b5fbefbd7036ca539ff967c9ae1fd90f7d82",
    "reset_builder": "69f064a7185accb2868926fc88fcb4fd0d03fd78d0751fe03e8b1a7f8d6611aa",
    "circuit": "580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d",
    "netlist": "a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd",
    "c105_receipt": "beac75216c5dab7a12642678d6d6839248c22086492d8af3e746e6ca0f7c6de9",
    "jlc_sensitivity": "9e08ce38014bde96465cea15ce70a48c0cf0efaa7b17c19ea5a8b7f808bdae18",
    "pair_controls": "2ef86d1c3b69c4e00e9013d9588bd0bc048ef33983a8936f8b27d0bd79358819",
    "fp_lib_table": "f7d3e5557b95cf52fb52294c497f6cf2680f0c750acc550b1b9d808973dc8b55",
}
SOURCE_TREE = "7c7ca378c0ed49a49711c1611f2df4097c751a962924b45da42f2f3488526f0c"
TOOLS = {
    "board_generator": ("skills/kicad-pcb/scripts/generate_board_generic.py", "8a5fa1d48d80138458601a097ab6260565841510a498e44cb9c5773652215b3c"),
    "rule_generator": ("skills/kicad-pcb/scripts/generate_rules_generic.py", "80d8c5c01888bd1053c28945333efdfedca90f7ccfd25b047bcd829c55b82d01"),
    "pofv_generator": ("skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py", "b3906f63e07e9f04ada58e757f4095989f6933eca98d93b0f1165e91064529b7"),
    "via_checker": ("skills/jlcpcb-fab/scripts/via_process_check.py", "db3f759078909228d9a509721951b30bec4476db4cb1bce864fc42a83a3e5e5e"),
    "p1_checker": ("skills/kicad-pcb/scripts/p1_corridor_capacity.py", "c6609198e3daa5fc9718436194945f4cb0f39f4e9095ec991674479f798e7b46"),
}
CHANGED = ["floorplan.yaml", "rules/nets.yaml", "route.yaml", "rules/rf.yaml"]
OLD_C105 = "    C_XU_VDD_105:\n    - 196.5\n    - 96.3\n    - 180.0\n"
NEW_C105 = "    C_XU_VDD_105:\n    - 198.25\n    - 97.05\n    - 180.0\n"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_sha(path: Path) -> str:
    h = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        h.update(item.relative_to(path).as_posix().encode() + b"\0")
        h.update(bytes.fromhex(sha(item)))
    return h.hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("D19_SOURCE_PREFLIGHT_FAIL: " + message)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("out", type=Path, help="fresh scratch directory; existing path refused")
    args = ap.parse_args()
    out = args.out.resolve()
    require(not out.exists(), "output exists")
    inputs = {
        "board": REFERENCE / "04_kicad/crow_carrier.kicad_pcb",
        "pro": REFERENCE / "04_kicad/crow_carrier.kicad_pro",
        "dru": REFERENCE / "04_kicad/crow_carrier.kicad_dru",
        "floorplan": REFERENCE / "03_src/floorplan.yaml",
        "nets": REFERENCE / "03_src/rules/nets.yaml",
        "route": REFERENCE / "03_src/route.yaml",
        "rf": REFERENCE / "03_src/rules/rf.yaml",
        "proposal": PROPOSAL,
        "reset_builder": RESET,
        "circuit": REFERENCE / "03_tscircuit/build/circuit.json",
        "netlist": REFERENCE / "06_build/netlists/crow_carrier.net",
        "c105_receipt": HERE.parent / "2026-09-25-expanded-tdm-c105-placement-sol/receipt.json",
        "jlc_sensitivity": HERE.parent / "2026-09-25-jlc-3313-uniform-usb-solve-sol/mask_sensitivity_capture.json",
        "pair_controls": HERE.parent / "2026-09-25-unadopted-3313a-controlled-pair-sol/native-replay-full-sidecar-independent-terra.json",
        "fp_lib_table": REFERENCE / "04_kicad/fp-lib-table",
    }
    require({k: sha(v) for k, v in inputs.items()} == EXPECTED, "frozen input drift")
    require(tree_sha(REFERENCE / "03_src") == SOURCE_TREE, "complete frozen source tree drift")
    require(all(sha(ROOT / rel) == expected for rel, expected in TOOLS.values()), "generator/checker drift")
    require(out.is_relative_to((PROJECT / "06_build/prototype_board_diagnostic").resolve()), "scratch path")
    out.mkdir(parents=True)
    shutil.copytree(REFERENCE / "03_src", out / "03_src")
    shutil.copytree(REFERENCE / "02_parts", out / "02_parts")
    (out / "04_kicad").mkdir()
    shutil.copy2(inputs["pro"], out / "04_kicad/crow_carrier.kicad_pro")
    shutil.copy2(inputs["dru"], out / "04_kicad/crow_carrier.kicad_dru")
    shutil.copy2(REFERENCE / "04_kicad/fp-lib-table", out / "04_kicad/fp-lib-table")
    (out / "03_tscircuit/build").mkdir(parents=True)
    (out / "06_build/netlists").mkdir(parents=True)
    shutil.copy2(inputs["circuit"], out / "03_tscircuit/build/circuit.json")
    shutil.copy2(inputs["netlist"], out / "06_build/netlists/crow_carrier.net")
    # The accepted research proposal changes only four copied source files.
    subprocess.run(["patch", "--batch", "--forward", "-p1", "-i", str(PROPOSAL)], cwd=out, check=True,
                   capture_output=True, text=True)
    floor = out / "03_src/floorplan.yaml"
    content = floor.read_text()
    require(content.count(OLD_C105) == 1, "C105 post-anchor source form")
    floor.write_text(content.replace(OLD_C105, NEW_C105))
    native_floor = yaml.safe_load(floor.read_text())
    require(native_floor["placement"]["post_anchors"]["C_XU_VDD_105"] == [198.25, 97.05, 180.0], "C105 source pose")
    reset_tmp = out / "reset_builder_output"
    subprocess.run(["/usr/bin/python3", str(RESET), "--out", str(reset_tmp)], check=True,
                   capture_output=True, text=True)
    p1 = out / "p1_packet"
    p1.mkdir()
    for name in ("p1_requirements.yaml", "floorplan.yaml"):
        shutil.copy2(reset_tmp / name, p1 / name)
    shutil.copy2(P1_BASE / "modular_plan.json", p1 / "modular_plan.json")
    p1_floor = yaml.safe_load((p1 / "floorplan.yaml").read_text())
    require(p1_floor["placement"]["post_anchors"]["C_XU_VDD_105"] == [196.5, 96.3, 180.0], "P1 C105 base")
    p1_floor["placement"]["post_anchors"]["C_XU_VDD_105"] = [198.25, 97.05, 180.0]
    p1_floor["board"]["stackup"] = native_floor["board"]["stackup"]
    require(p1_floor["board"] == native_floor["board"], "P1 and native board/stack identity")
    require(p1_floor["placement"]["post_anchors"] == native_floor["placement"]["post_anchors"],
            "P1 and native post-anchor identity")
    (p1 / "floorplan.yaml").write_text(yaml.safe_dump(p1_floor, sort_keys=False))
    # Deliberately exclude the reset builder's frozen-board coarse/result files.
    # One fresh P1 contract must be generated and graded on the D19 native board.
    shutil.rmtree(reset_tmp)
    changed = sorted(str(p.relative_to(out / "03_src")) for p in (out / "03_src").rglob("*")
                     if p.is_file() and sha(p) != sha(REFERENCE / "03_src" / p.relative_to(out / "03_src")))
    require(changed == sorted(CHANGED), f"source allowlist {changed}")
    diff = []
    for name in CHANGED:
        a = (REFERENCE / "03_src" / name).read_text().splitlines(keepends=True)
        b = (out / "03_src" / name).read_text().splitlines(keepends=True)
        diff += list(difflib.unified_diff(a, b, fromfile="frozen/03_src/" + name,
                                          tofile="d19/03_src/" + name))
    (out / "source_diff.patch").write_text("".join(diff))
    receipt = {
        "attempt": "D19-INTEGRATED-UNROUTED-ONE",
        "status": "AUTHOR_SOURCE_PREFLIGHT_ONLY",
        "board_generated": False,
        "route_executed": False,
        "independent_preflight_signed": False,
        "stage_credit": False,
        "inputs_sha256": EXPECTED,
        "source_tree_sha256": SOURCE_TREE,
        "scratch_source_tree_sha256": tree_sha(out / "03_src"),
        "generator_checker_sha256": {k: v[1] for k, v in TOOLS.items()},
        "recipe_sha256": sha(Path(__file__)),
        "generation_recipe_sha256": sha(HERE / "generate_once.py"),
        "postgen_checker_sha256": sha(HERE / "postgen_check.py"),
        "kicad_cli_version": subprocess.run(["kicad-cli", "version"], check=True, capture_output=True, text=True).stdout.strip(),
        "pcbnew_version": pcbnew.Version(),
        "reference_lib_tree_sha256": tree_sha(REFERENCE / "03_src/lib"),
        "reference_parts_tree_sha256": tree_sha(REFERENCE / "02_parts"),
        "copied_parts_tree_sha256": tree_sha(out / "02_parts"),
        "changed_source_files": CHANGED,
        "scratch_sha256": {name: sha(out / "03_src" / name) for name in CHANGED},
        "source_diff_sha256": sha(out / "source_diff.patch"),
        "p1_packet_sha256": {p.name: sha(p) for p in sorted(p1.iterdir()) if p.is_file()},
        "copied_sidecar_sha256": {"pro": sha(out / "04_kicad/crow_carrier.kicad_pro"),
                                  "dru": sha(out / "04_kicad/crow_carrier.kicad_dru"),
                                  "fp_lib_table": sha(out / "04_kicad/fp-lib-table")},
        "next_gate": "Independent Terra preflight on this exact packet before any native generation",
    }
    (out / "preflight.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"scratch": str(out), "preflight_sha256": sha(out / "preflight.json"),
                      "source_diff_sha256": receipt["source_diff_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
