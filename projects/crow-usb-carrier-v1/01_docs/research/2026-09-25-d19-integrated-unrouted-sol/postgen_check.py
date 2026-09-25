#!/usr/bin/env /usr/bin/python3
"""D19 mandatory native checks; P1/P2 engineering review remains separate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pcbnew as pcb

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
ROOT = HERE.parents[4]
BASE = PROJECT / "06_build/prototype_board_diagnostic"
REFERENCE = BASE / "current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb"
OUTPUT = BASE / "d19-integrated-native-candidate-20260925"
COPY = OUTPUT / "project"
BOARD = COPY / "04_kicad/crow_carrier.kicad_pcb"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pose(fp) -> tuple:
    p = fp.GetPosition()
    return (round(pcb.ToMM(p.x), 4), round(pcb.ToMM(p.y), 4), round(fp.GetOrientationDegrees(), 4))


def inventory(path: Path) -> dict:
    board = pcb.LoadBoard(str(path))
    footprints = {}
    for fp in board.GetFootprints():
        pads = sorted((p.GetNumber(), p.GetNetname(), tuple(p.GetSize()),
                       int(p.GetShape()), p.GetLayerSet().FmtBin()) for p in fp.Pads())
        footprints[fp.GetReference()] = (pose(fp), fp.GetLayerName(), fp.GetFPIDAsString(), pads)
    tracks = sorted((type(t).__name__, t.GetNetname(), t.GetLayerName(),
                     tuple(t.GetPosition()), t.GetWidth(pcb.F_Cu),
                     t.GetDrillValue() if isinstance(t, pcb.PCB_VIA) else 0) for t in board.GetTracks())
    zones = sorted((z.GetZoneName(), z.GetNetname(), z.GetLayerName(), bool(z.GetIsRuleArea()),
                    tuple(z.GetBoundingBox().GetPosition()), tuple(z.GetBoundingBox().GetSize()),
                    bool(z.IsFilled())) for z in board.Zones())
    edges = sorted((type(d).__name__, tuple(d.GetBoundingBox().GetPosition()),
                    tuple(d.GetBoundingBox().GetSize())) for d in board.GetDrawings()
                   if d.GetLayerName() == "Edge.Cuts")
    return {"footprints": footprints, "tracks": tracks, "zones": zones, "edges": edges}


def run(name: str, argv: list[str]) -> dict:
    proc = subprocess.run(argv, cwd=COPY, capture_output=True, text=True)
    record = {"argv": argv, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    (OUTPUT / f"{name}.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    if not BOARD.is_file() or not (OUTPUT / "generation_receipt.json").is_file():
        raise SystemExit("D19_POSTGEN_REFUSED: no single generated candidate")
    receipt = json.loads((OUTPUT / "generation_receipt.json").read_text())
    if receipt["board_sha256"] != sha(BOARD):
        raise SystemExit("D19_POSTGEN_REFUSED: generated board drift")
    old, new = inventory(REFERENCE), inventory(BOARD)
    failures = []
    if old["footprints"].keys() != new["footprints"].keys():
        failures.append("footprint set")
    for ref, value in old["footprints"].items():
        current = new["footprints"].get(ref)
        if ref == "C_XU_VDD_105":
            if not current or current[0] != (198.25, 97.05, 180.0) or current[1:] != value[1:]:
                failures.append("C105 exact pose/body/pads")
        elif current != value:
            failures.append("unexpected footprint/pad delta " + ref)
    if new["tracks"] != old["tracks"] or len(new["tracks"]) != 14:
        failures.append("saved copper")
    if new["edges"] != old["edges"]:
        failures.append("outline")
    if new["zones"] != old["zones"] or any(z[-1] for z in new["zones"]):
        failures.append("zone/rule area or saved fill")
    if sum(len(v[-1]) for k,v in new["footprints"].items() if not k.startswith("H")) != 1872:
        failures.append("raw pad denominator")
    via = run("via_process", ["/usr/bin/python3", str(ROOT / "skills/jlcpcb-fab/scripts/via_process_check.py"),
                              str(BOARD), "--assembly", str(COPY / "03_src/rules/assembly.yaml"),
                              "--json", str(OUTPUT / "via_process_result.json")])
    count = run("count_parity", ["/usr/bin/python3", str(ROOT / "skills/kicad-pcb/scripts/count_parity.py"), str(COPY)])
    pin = run("pin_map", ["/usr/bin/python3", str(ROOT / "skills/kicad-pcb/scripts/pin_map_check.py"),
                          str(COPY), "--board", str(BOARD), "--circuit-json",
                          str(COPY / "03_tscircuit/build/circuit.json"), "--parts", str(COPY / "02_parts")])
    drc_out = OUTPUT / "drc_disposable_refill.json"
    drc = run("native_drc", ["kicad-cli", "pcb", "drc", "--severity-all", "--refill-zones",
                             "--schematic-parity", "--format", "json", "-o", str(drc_out), str(BOARD)])
    if any(r["returncode"] for r in (via,count,pin,drc)):
        failures.append("native command failed")
    if drc_out.is_file():
        data = json.loads(drc_out.read_text())
        keys = ("violations", "unconnected_items", "schematic_parity")
        if any(not isinstance(data.get(key), list) for key in keys):
            failures.append("native DRC missing list-valued coverage")
        if any(data.get(key) for key in ("violations", "schematic_parity")):
            failures.append("native DRC or performed schematic parity")
        if len(data.get("unconnected_items", [])) != 499:
            failures.append("native open count changed")
        output = drc["stdout"] + drc["stderr"]
        if "Failed to fetch schematic netlist" in output or "Found 0 schematic parity issues" not in output:
            failures.append("schematic parity was not performed")
        counts = {key: len(data[key]) for key in keys if isinstance(data.get(key), list)}
    else:
        failures.append("missing native DRC report")
        counts = {}
    result = {"status": "NATIVE_CHECK_PASS_P1_P2_PENDING" if not failures else "FAILED_RESEARCH",
              "board_sha256": sha(BOARD), "findings": failures,
              "native_drc_counts": counts,
              "p1_accepted": False, "p2_accepted": False, "routing_realized": False,
              "next_gate": "New exact-board P1 coarse rebind and independent all-P1/affected-P2 engineering review"}
    (OUTPUT / "native_postgen_receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
