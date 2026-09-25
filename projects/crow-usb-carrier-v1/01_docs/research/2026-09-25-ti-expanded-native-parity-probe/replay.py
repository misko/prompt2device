#!/usr/bin/env python3
"""Run native KiCad parity for the exact private TI board, without editing it."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
PRIVATE = PROJECT / "06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925"
PCB_DIR = PRIVATE / "04_kicad"
SCHEMATIC = PROJECT / "06_build/prototype_only/20260925T044907Z-581549/crow_carrier.kicad_sch"
PROTOTYPE_RECEIPT = PROJECT / "06_build/prototype_only/20260925T044907Z-581549/receipt.json"
CIRCUIT = PRIVATE / "03_tscircuit/build/circuit.json"
NETLIST = PRIVATE / "06_build/netlists/crow_carrier.net"
LIB = PRIVATE / "03_src/lib"
EXPECTED = {
    "crow_carrier.kicad_pcb": "fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16",
    "crow_carrier.kicad_pro": "7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094",
    "crow_carrier.kicad_dru": "00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a",
    "fp-lib-table": "f7d3e5557b95cf52fb52294c497f6cf2680f0c750acc550b1b9d808973dc8b55",
    "crow_carrier.kicad_sch": "758e29b0d9606a6b8f123a2dca474ce62871a85e08fb2fb9024c5a7a3d04610d",
    "lib_tree": "f2e98dd48c28fc6a752f2ff891ca15e07e1c3dfec18238eb8f9693027f604c32",
    "prototype_receipt": "5cccaaa7b577a9ad07b647e77a7759ce203e81d8e6efd35a3fa55e7a9ab5cd42",
    "circuit": "580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d",
    "netlist": "a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_sha(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(file.relative_to(path).as_posix().encode() + b"\0")
        digest.update(bytes.fromhex(sha(file)))
    return digest.hexdigest()


def main() -> None:
    inputs = {name: PCB_DIR / name for name in
              ("crow_carrier.kicad_pcb", "crow_carrier.kicad_pro",
               "crow_carrier.kicad_dru", "fp-lib-table")}
    inputs["crow_carrier.kicad_sch"] = SCHEMATIC
    observed = {name: sha(path) for name, path in inputs.items()}
    observed["lib_tree"] = tree_sha(LIB)
    observed["prototype_receipt"] = sha(PROTOTYPE_RECEIPT)
    observed["circuit"] = sha(CIRCUIT)
    observed["netlist"] = sha(NETLIST)
    if observed != EXPECTED:
        raise SystemExit("exact native parity inputs drifted")
    prototype = json.loads(PROTOTYPE_RECEIPT.read_text())
    if (prototype.get("status") != "PROTOTYPE_ONLY" or
            prototype.get("artifacts", {}).get("crow_carrier.kicad_sch") !=
            EXPECTED["crow_carrier.kicad_sch"] or
            prototype.get("artifacts", {}).get("circuit.json") != EXPECTED["circuit"] or
            prototype.get("artifacts", {}).get("crow_carrier.net") != EXPECTED["netlist"]):
        raise SystemExit("prototype schematic provenance mismatch")
    footprint_dir = Path(os.environ.get("KICAD10_FOOTPRINT_DIR", "/usr/share/kicad/footprints"))
    if not (footprint_dir / "Resistor_SMD.pretty").is_dir():
        raise SystemExit("KiCad 10 standard footprint library unavailable")
    version = subprocess.run(["kicad-cli", "version"], check=True,
                             capture_output=True, text=True).stdout.strip()
    if version != "10.0.4":
        raise SystemExit(f"KiCad version changed: {version}")
    with tempfile.TemporaryDirectory(prefix="crow-native-parity-") as tmp:
        root = Path(tmp)
        cad = root / "04_kicad"
        cad.mkdir()
        for name, source in inputs.items():
            shutil.copy2(source, cad / name)
        shutil.copytree(LIB, root / "03_src/lib")
        report = root / "drc.json"
        env = os.environ.copy()
        env["KICAD10_FOOTPRINT_DIR"] = str(footprint_dir)
        run = subprocess.run([
            "kicad-cli", "pcb", "drc", "--severity-all", "--refill-zones",
            "--schematic-parity", "--format", "json", "--output", str(report),
            str(cad / "crow_carrier.kicad_pcb"),
        ], env=env, capture_output=True, text=True)
        output = run.stdout + run.stderr
        if run.returncode or "Failed to fetch schematic netlist" in output or \
                "Found 0 schematic parity issues" not in output:
            raise SystemExit(f"native parity did not complete: {output[-1200:]}")
        data = json.loads(report.read_text())
        counts = {key: len(data.get(key, [])) for key in
                  ("violations", "unconnected_items", "schematic_parity")}
        if counts != {"violations": 0, "unconnected_items": 499,
                      "schematic_parity": 0}:
            raise SystemExit(f"native result changed: {counts}")
    receipt = {
        "status": "RESEARCH_DIAGNOSTIC", "board_sha256": EXPECTED["crow_carrier.kicad_pcb"],
        "schematic_sha256": EXPECTED["crow_carrier.kicad_sch"],
        "prototype_receipt_sha256": EXPECTED["prototype_receipt"],
        "circuit_sha256": EXPECTED["circuit"],
        "netlist_sha256": EXPECTED["netlist"],
        "kicad_version": version, "native_schematic_parity_performed": True,
        "drc_counts": counts, "p1_accepted": False, "routing_realized": False,
        "release_admitted": False, "order_admitted": False,
    }
    (HERE / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
