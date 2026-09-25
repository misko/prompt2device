#!/usr/bin/env python3
"""Build one private, unrouted TI geometry subject; no placement admission."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


BOARD = "crow_carrier"
FROZEN = "06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project"
PRIVATE = "06_build/prototype_only/20260925T044907Z-581549"
SEED_SHA256 = {
    "seed_pro": "7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094",
    "seed_dru": "00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a",
}
RULE_NAME = re.compile(r'\(rule\s+"?([^"\s()]+)"?')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(path: Path) -> str:
    h = hashlib.sha256()
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        h.update(file.relative_to(path).as_posix().encode() + b"\0")
        h.update(bytes.fromhex(digest(file)))
    return h.hexdigest()


def check_rule_seed(pro: Path, dru: Path) -> None:
    for name, path in (("seed_pro", pro), ("seed_dru", dru)):
        if digest(path) != SEED_SHA256[name]:
            raise RuntimeError(f"unreviewed KiCad rule seed: {name}")


def check_effective_dru(seed: Path, effective: Path) -> set[str]:
    seed_rules = set(RULE_NAME.findall(seed.read_text()))
    effective_rules = set(RULE_NAME.findall(effective.read_text()))
    if not effective_rules or effective_rules - seed_rules:
        raise RuntimeError(f"unexpected effective DRU rules: {sorted(effective_rules - seed_rules)}")
    return effective_rules


def geometry_digest(board_path: Path) -> str:
    """Order/UUID independent diagnostic identity of native placed objects."""
    import pcbnew as pcb

    board = pcb.LoadBoard(str(board_path))
    def xy(value):
        return [value.x, value.y]
    footprints = []
    for fp in board.GetFootprints():
        pads = sorted((pad.GetNumber(), pad.GetNetname(), xy(pad.GetPosition()),
                       xy(pad.GetSize()), int(pad.GetShape()),
                       pad.GetLayerSet().FmtBin()) for pad in fp.Pads())
        footprints.append((fp.GetReference(), xy(fp.GetPosition()),
                           fp.GetOrientationDegrees(), fp.GetLayerName(), pads))
    zones = []
    for zone in board.Zones():
        box = zone.GetBoundingBox()
        zones.append((zone.GetZoneName(), zone.GetNetname(), zone.GetLayerName(),
                      bool(zone.GetIsRuleArea()), [box.GetX(), box.GetY(),
                                                  box.GetWidth(), box.GetHeight()]))
    tracks = sorted((type(track).__name__, track.GetNetname(),
                     xy(track.GetPosition()), track.GetWidth(pcb.F_Cu), track.GetLayerName())
                    for track in board.GetTracks())
    payload = {"footprints": sorted(footprints), "zones": sorted(zones),
               "tracks": tracks}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def run(*argv: str, cwd: Path | None = None, allow_drc: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    if result.returncode and not allow_drc:
        raise RuntimeError(f"{argv[0]} exited {result.returncode}: {result.stdout[-1000:]} {result.stderr[-1000:]}")
    return result


def validated_inputs(project: Path, tools: Path) -> dict[str, Path]:
    source = project / "03_src"
    private = project / PRIVATE
    frozen = project / FROZEN
    paths = {
        "floorplan": source / "floorplan.yaml",
        "assembly": source / "rules/assembly.yaml",
        "critical_selection": source / "rules/critical_part_selection.yaml",
        "circuit": project / "03_tscircuit/build/circuit.json",
        "netlist": project / "06_build/netlists/crow_carrier.net",
        "private_circuit": private / "circuit.json",
        "private_netlist": private / "crow_carrier.net",
        "private_receipt": private / "receipt.json",
        "seed_pro": frozen / "04_kicad/crow_carrier.kicad_pro",
        "seed_dru": frozen / "04_kicad/crow_carrier.kicad_dru",
        "board_generator": tools / "skills/kicad-pcb/scripts/generate_board_generic.py",
        "rules_generator": tools / "skills/kicad-pcb/scripts/generate_rules_generic.py",
        "pofv_generator": tools / "skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py",
        "via_checker": tools / "skills/jlcpcb-fab/scripts/via_process_check.py",
        "selection_gate": tools / "skills/pcb-design/scripts/critical_part_selection_admission.py",
        "pause_gate": tools / "skills/pcb-design/scripts/pause_state.py",
    }
    for name, path in paths.items():
        if not path.is_file() or not path.stat().st_size:
            raise RuntimeError(f"missing {name}: {path}")
    check_rule_seed(paths["seed_pro"], paths["seed_dru"])
    receipt = json.loads(paths["private_receipt"].read_text())
    if receipt.get("status") != "PROTOTYPE_ONLY":
        raise RuntimeError("source bundle is not PROTOTYPE_ONLY")
    for name, artifact in (("circuit", "circuit.json"), ("netlist", "crow_carrier.net")):
        expected = receipt.get("artifacts", {}).get(artifact)
        if expected != digest(paths[f"private_{name}"]) or digest(paths[name]) != expected:
            raise RuntimeError(f"current {name} differs from reviewed private TI bundle")
    for rel, expected in receipt.get("inputs", {}).items():
        current = project / rel
        if not current.is_file() or digest(current) != expected:
            raise RuntimeError(f"prototype source changed since private TI bundle: {rel}")
    if "TPD2EUSB30ADRTR" not in paths["netlist"].read_text():
        raise RuntimeError("TI ESD identity absent from current netlist")
    run(sys.executable, str(paths["selection_gate"]), str(project), "--require-prototype")
    run(sys.executable, str(paths["pause_gate"]), "verify", str(project))
    return paths


def build(project: Path, tools: Path, output: Path) -> dict:
    project, tools, output = project.resolve(), tools.resolve(), output.resolve()
    if not output.is_relative_to((project / "06_build/prototype_board_diagnostic").resolve()):
        raise RuntimeError("output must be below private prototype_board_diagnostic")
    if output.exists():
        raise RuntimeError("refusing to overwrite diagnostic output")
    paths = validated_inputs(project, tools)  # no output or budget mutation before gates
    output.mkdir(parents=True)
    copy = output / "project"
    (copy / "03_src").mkdir(parents=True)
    (copy / "04_kicad").mkdir()
    (copy / "03_tscircuit/build").mkdir(parents=True)
    (copy / "06_build/netlists").mkdir(parents=True)
    shutil.copytree(project / "02_parts", copy / "02_parts", symlinks=False)
    shutil.copytree(project / "03_src", copy / "03_src", dirs_exist_ok=True, symlinks=False)
    shutil.copy2(paths["circuit"], copy / "03_tscircuit/build/circuit.json")
    shutil.copy2(paths["netlist"], copy / "06_build/netlists/crow_carrier.net")
    board = copy / f"04_kicad/{BOARD}.kicad_pcb"
    pro = copy / f"04_kicad/{BOARD}.kicad_pro"
    dru = copy / f"04_kicad/{BOARD}.kicad_dru"
    shutil.copy2(paths["seed_pro"], pro)
    shutil.copy2(paths["seed_dru"], dru)
    original = {name: digest(path) for name, path in paths.items()}
    original["source_tree"] = tree_digest(project / "03_src")
    original["parts_tree"] = tree_digest(project / "02_parts")
    run(sys.executable, str(paths["board_generator"]), str(copy / "03_src/floorplan.yaml"),
        "--netlist", str(copy / "06_build/netlists/crow_carrier.net"), "-o", str(board))
    run(sys.executable, str(paths["rules_generator"]), str(copy))
    run(sys.executable, str(paths["pofv_generator"]), str(board),
        "--assembly", str(copy / "03_src/rules/assembly.yaml"))
    # The generator intentionally preserves some prior DRU rules. The pinned
    # seed is the sole permitted source of those retained rules. A new rule
    # name appearing in the effective profile is not accepted by this trial.
    effective_rules = check_effective_dru(paths["seed_dru"], dru)
    # This first baseline changes placement only. Any effective rule-byte
    # change needs a separately reviewed authority packet before another run.
    check_rule_seed(pro, dru)
    via_report = output / "via_process.json"
    run(sys.executable, str(paths["via_checker"]), str(board), "--assembly",
        str(copy / "03_src/rules/assembly.yaml"), "--json", str(via_report))
    drc_path = output / "drc.json"
    drc_run = run("kicad-cli", "pcb", "drc", "--severity-all", "--refill-zones",
                  "--schematic-parity", "--format", "json", "--output", str(drc_path),
                  str(board), allow_drc=True)
    if not drc_path.is_file():
        raise RuntimeError(f"native DRC did not emit JSON: {drc_run.stderr[-500:]}")
    drc = json.loads(drc_path.read_text())
    via = json.loads(via_report.read_text())
    if via.get("fails"):
        raise RuntimeError("V-PROCESS found failures")
    # The parity scripts read their private project copy, never canonical outputs.
    parity = run(sys.executable, str(tools / "skills/kicad-pcb/scripts/count_parity.py"), str(copy))
    pinmap = run(sys.executable, str(tools / "skills/kicad-pcb/scripts/pin_map_check.py"),
                 str(copy), "--board", str(board), "--circuit-json",
                 str(copy / "03_tscircuit/build/circuit.json"), "--parts", str(copy / "02_parts"))
    for name, path in paths.items():
        if digest(path) != original[name]:
            raise RuntimeError(f"input changed during build: {name}")
    if tree_digest(project / "03_src") != original["source_tree"] or tree_digest(project / "02_parts") != original["parts_tree"]:
        raise RuntimeError("source or parts changed during build")
    receipt = {
        "schema": 1, "status": "PROTOTYPE_ONLY", "scope": "PRIVATE_NATIVE_GEOMETRY_DIAGNOSTIC",
        "engineering_acceptance": False, "p1_accepted": False, "p2_accepted": False,
        "p3_route_credit": False, "fabrication_admitted": False, "order_admitted": False,
        "inputs_sha256": original,
        "outputs_sha256": {"board": digest(board), "pro": digest(pro), "dru": digest(dru),
                           "drc": digest(drc_path), "via_process": digest(via_report)},
        "geometry_sha256": geometry_digest(board),
        "effective_dru_rule_names": sorted(effective_rules),
        "native_drc": {"violations": len(drc.get("violations", [])),
                       "unconnected_items": len(drc.get("unconnected_items", [])),
                       "schematic_parity_issues": len(drc.get("schematic_parity", [])),
                       "exit_code": drc_run.returncode},
        "count_parity_stdout": parity.stdout.strip(), "pin_map_stdout": pinmap.stdout.strip(),
        "output": output.relative_to(project).as_posix(),
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--tools-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output or args.project / "06_build/prototype_board_diagnostic" / stamp
    try:
        receipt = build(args.project, args.tools_root, output)
    except Exception as exc:
        print(f"PROTOTYPE BOARD DIAGNOSTIC REFUSED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
