#!/usr/bin/env /usr/bin/python3
"""Read-only D19 checker correction on unchanged bytes; never changes D19 status."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pcbnew as pcb

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
BASE = PROJECT / "06_build/prototype_board_diagnostic"
FROZEN = BASE / "current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb"
CANDIDATE = BASE / "d19-integrated-native-candidate-20260925/project"
BOARD = CANDIDATE / "04_kicad/crow_carrier.kicad_pcb"
GENERATION = BASE / "d19-integrated-native-candidate-20260925/generation_receipt.json"
ORIGINAL_POSTGEN = BASE / "d19-integrated-native-candidate-20260925/native_postgen_receipt.json"
PREFLIGHT = BASE / "d19-integrated-source-preflight-r3-20260925/preflight.json"
SCHEMATIC = PROJECT / "06_build/prototype_only/20260925T044907Z-581549/crow_carrier.kicad_sch"
PROTOTYPE_RECEIPT = PROJECT / "06_build/prototype_only/20260925T044907Z-581549/receipt.json"
EXPECTED = {
    "board": "ffb51cc31c5b1b0caada7e360c727848a1117b9cd94f6160fde2ca18ceb8625f",
    "pro": "2d0bf4d9c14fedee82e1ba22f06d05a4ba97e7b7fe39a66e086ec1c48b408c1a",
    "dru": "32a4dbacf8b1b2b8be93aa0a8308de483f183344bed98f42209ed62f82920992",
    "fp_lib_table": "f7d3e5557b95cf52fb52294c497f6cf2680f0c750acc550b1b9d808973dc8b55",
    "schematic": "758e29b0d9606a6b8f123a2dca474ce62871a85e08fb2fb9024c5a7a3d04610d",
    "prototype_receipt": "5cccaaa7b577a9ad07b647e77a7759ce203e81d8e6efd35a3fa55e7a9ab5cd42",
    "circuit": "580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d",
    "netlist": "a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd",
    "preflight": "5b5972ac77e4ae3fb9b02e06d985b3d50f07d68b6487e3a0562757685ee7c1cb",
    "frozen": "fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16",
    "generation_receipt": "8e3d9630ffed83a63f994dd76e28e1b0a970cb8b444e2e7f56a759ebda8981aa",
    "original_failed_postgen": "a119396aa76658a6603e8155abcd65f1f0923d84f711263183c495d1ae6575a5",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_sha(path: Path) -> str:
    h = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        h.update(item.relative_to(path).as_posix().encode() + b"\0")
        h.update(bytes.fromhex(sha(item)))
    return h.hexdigest()


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise SystemExit("D19_CHECKER_REPLAY_FAIL: " + msg)


def bbox(b) -> tuple[int, int, int, int]:
    p, s = b.GetPosition(), b.GetSize()
    return p.x, p.y, s.x, s.y


def native_inventory(path: Path) -> dict:
    board = pcb.LoadBoard(str(path))
    edges = sorted((type(d).__name__, d.GetLayerName(), bbox(d.GetBoundingBox()))
                   for d in board.GetDrawings() if d.GetLayerName() == "Edge.Cuts")
    zones = sorted((z.GetZoneName(), z.GetNetname(), z.GetLayerName(),
                    bool(z.GetIsRuleArea()), bbox(z.GetBoundingBox()), bool(z.IsFilled()))
                   for z in board.Zones())
    return {"edges": edges, "zones": zones}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-result", type=Path, help="new result path; existing path refused")
    args = ap.parse_args()
    if args.write_result:
        require(not args.write_result.exists(), "result exists")
    paths = {
        "board": BOARD, "pro": BOARD.with_suffix(".kicad_pro"),
        "dru": BOARD.with_suffix(".kicad_dru"),
        "fp_lib_table": BOARD.parent / "fp-lib-table",
        "schematic": SCHEMATIC, "prototype_receipt": PROTOTYPE_RECEIPT,
        "circuit": CANDIDATE / "03_tscircuit/build/circuit.json",
        "netlist": CANDIDATE / "06_build/netlists/crow_carrier.net",
        "preflight": PREFLIGHT, "frozen": FROZEN,
        "generation_receipt": GENERATION, "original_failed_postgen": ORIGINAL_POSTGEN,
    }
    observed = {k: sha(v) for k, v in paths.items()}
    require(observed == EXPECTED, "exact input byte drift")
    preflight = json.loads(PREFLIGHT.read_text())
    generation = json.loads(GENERATION.read_text())
    require(generation["preflight_sha256"] == EXPECTED["preflight"] and
            generation["board_sha256"] == EXPECTED["board"], "attempt identity")
    require(tree_sha(CANDIDATE / "03_src") == preflight["scratch_source_tree_sha256"], "source tree drift")
    require(tree_sha(CANDIDATE / "02_parts") == preflight["copied_parts_tree_sha256"], "parts drift")
    require(tree_sha(CANDIDATE / "03_src/lib") == preflight["reference_lib_tree_sha256"], "library drift")
    prototype = json.loads(PROTOTYPE_RECEIPT.read_text())
    require(prototype.get("status") == "PROTOTYPE_ONLY" and
            prototype.get("artifacts", {}).get("crow_carrier.kicad_sch") == EXPECTED["schematic"] and
            prototype.get("artifacts", {}).get("circuit.json") == EXPECTED["circuit"] and
            prototype.get("artifacts", {}).get("crow_carrier.net") == EXPECTED["netlist"], "schematic provenance")
    old, new = native_inventory(FROZEN), native_inventory(BOARD)
    footprint_dir = Path(os.environ.get("KICAD10_FOOTPRINT_DIR", "/usr/share/kicad/footprints"))
    require((footprint_dir / "Resistor_SMD.pretty").is_dir(), "KiCad footprint context")
    version = subprocess.run(["kicad-cli", "version"], check=True, capture_output=True, text=True).stdout.strip()
    require(version == "10.0.4", "KiCad version")
    with tempfile.TemporaryDirectory(prefix="crow-d19-checker-only-") as temporary:
        temp = Path(temporary)
        cad = temp / "04_kicad"
        cad.mkdir()
        for source in (BOARD, BOARD.with_suffix(".kicad_pro"), BOARD.with_suffix(".kicad_dru"),
                       BOARD.parent / "fp-lib-table", SCHEMATIC):
            shutil.copy2(source, cad / source.name)
        shutil.copytree(CANDIDATE / "03_src/lib", temp / "03_src/lib")
        drc_path = temp / "drc.json"
        env = os.environ.copy()
        env["KICAD10_FOOTPRINT_DIR"] = str(footprint_dir)
        command = ["kicad-cli", "pcb", "drc", "--severity-all", "--refill-zones",
                   "--schematic-parity", "--format", "json", "-o", str(drc_path),
                   str(cad / "crow_carrier.kicad_pcb")]
        run = subprocess.run(command, env=env, capture_output=True, text=True)
        output = run.stdout + run.stderr
        require(drc_path.is_file(), "native DRC output absent")
        drc = json.loads(drc_path.read_text())
        keys = ("violations", "unconnected_items", "schematic_parity")
        require(all(isinstance(drc.get(k), list) for k in keys), "DRC coverage fields")
        counts = {k: len(drc[k]) for k in keys}
        performed = run.returncode == 0 and "Failed to fetch schematic netlist" not in output and \
                    "Found 0 schematic parity issues" in output
    after = {k: sha(v) for k, v in paths.items()}
    require(after == observed and tree_sha(CANDIDATE / "03_src") == preflight["scratch_source_tree_sha256"] and
            tree_sha(CANDIDATE / "02_parts") == preflight["copied_parts_tree_sha256"], "input changed during replay")
    result = {
        "kind": "D19_CHECKER_ONLY_CORRECTION",
        "historical_d19_status": "FAILED_RESEARCH",
        "candidate_board_sha256": EXPECTED["board"],
        "exact_input_sha256": EXPECTED,
        "outline_equal": old["edges"] == new["edges"],
        "zone_equal": old["zones"] == new["zones"],
        "outline_count": [len(old["edges"]), len(new["edges"])],
        "zone_count": [len(old["zones"]), len(new["zones"])],
        "native_drc_counts": counts,
        "native_schematic_parity_performed": performed,
        "diagnostic_pass": old["edges"] == new["edges"] and old["zones"] == new["zones"] and
                           performed and counts == {"violations": 0, "unconnected_items": 499, "schematic_parity": 0},
        "p1_accepted": False, "p2_accepted": False, "route_credit": False,
    }
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_result:
        args.write_result.write_text(serialized)
    print(serialized, end="")
    if not result["diagnostic_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
