#!/usr/bin/env /usr/bin/python3
"""Grade all five P1 coarse allocations on unchanged D19 board, with no credit."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
ROOT = HERE.parents[4]
BASE = PROJECT / "06_build/prototype_board_diagnostic"
BOARD = BASE / "d19-integrated-native-candidate-20260925/project/04_kicad/crow_carrier.kicad_pcb"
PRO = BOARD.with_suffix(".kicad_pro")
DRU = BOARD.with_suffix(".kicad_dru")
PREFLIGHT = BASE / "d19-integrated-source-preflight-r3-20260925/preflight.json"
P1 = PREFLIGHT.parent / "p1_packet"
NATIVE_FLOOR = PREFLIGHT.parent / "03_src/floorplan.yaml"
NATIVE_NETS = PREFLIGHT.parent / "03_src/rules/nets.yaml"
RESET = HERE.parent / "2026-09-25-reset-two-corridor-schema-probe-sol/build_linked.py"
CHECKER = ROOT / "skills/kicad-pcb/scripts/p1_corridor_capacity.py"
REBINDER = ROOT / "skills/pcb-design/scripts/integration_candidate.py"
ALIASES = PROJECT / "02_parts/USB4215-03-A/part.yaml"
EXPECTED = {
    "board": "ffb51cc31c5b1b0caada7e360c727848a1117b9cd94f6160fde2ca18ceb8625f",
    "pro": "2d0bf4d9c14fedee82e1ba22f06d05a4ba97e7b7fe39a66e086ec1c48b408c1a",
    "dru": "32a4dbacf8b1b2b8be93aa0a8308de483f183344bed98f42209ed62f82920992",
    "preflight": "5b5972ac77e4ae3fb9b02e06d985b3d50f07d68b6487e3a0562757685ee7c1cb",
    "reset": "69f064a7185accb2868926fc88fcb4fd0d03fd78d0751fe03e8b1a7f8d6611aa",
    "checker": "c6609198e3daa5fc9718436194945f4cb0f39f4e9095ec991674479f798e7b46",
    "rebinder": "48102e1322cbb3a0cbae297909a35fe6c4adcf7b7a37c4a269a35048eef5e905",
    "aliases": "a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("D19_P1_DIAGNOSTIC_FAIL: " + message)


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("out", type=Path, help="fresh ignored output directory")
    args = ap.parse_args()
    out = args.out.resolve()
    require(out.is_relative_to(BASE.resolve()) and not out.exists(), "fresh ignored output required")
    paths = {"board": BOARD, "pro": PRO, "dru": DRU, "preflight": PREFLIGHT,
             "reset": RESET, "checker": CHECKER, "rebinder": REBINDER, "aliases": ALIASES}
    require({key: sha(path) for key, path in paths.items()} == EXPECTED, "input drift")
    pre = json.loads(PREFLIGHT.read_text())
    for name, expected in pre["p1_packet_sha256"].items():
        require(sha(P1 / name) == expected, "P1 packet drift " + name)
    require(sha(NATIVE_FLOOR) == pre["scratch_sha256"]["floorplan.yaml"], "native floorplan drift")
    require(sha(NATIVE_NETS) == pre["scratch_sha256"]["rules/nets.yaml"], "native USB rules drift")
    native_floor = yaml.safe_load(NATIVE_FLOOR.read_text())
    p1_floor = yaml.safe_load((P1 / "floorplan.yaml").read_text())
    require(native_floor["board"] == p1_floor["board"] and
            native_floor["placement"]["post_anchors"] == p1_floor["placement"]["post_anchors"],
            "P1/native stack or anchor mismatch")
    require("JLC04161H-3313A" in str(native_floor["board"]["stackup"]), "3313A hypothesis absent")
    with tempfile.TemporaryDirectory(prefix="crow-d19-reset-source-") as scratch:
        reset_out = Path(scratch) / "reset"
        subprocess.run(["/usr/bin/python3", str(RESET), "--out", str(reset_out)],
                       check=True, capture_output=True, text=True)
        old = json.loads((reset_out / "coarse.json").read_text())
    require([row["id"] for row in old["allocations"]] == ["usb_device_pair", "xmos_service_escape",
            "adc_timing_xmos_bundle", "adc_analog_boundary", "power_boundary_windows"], "five allocations")
    old["source_sha256"] = sha(P1 / "p1_requirements.yaml")
    old["floorplan_sha256"] = sha(P1 / "floorplan.yaml")
    old["interfaces_sha256"] = sha(P1 / "modular_plan.json")
    old["aliases_sha256"] = sha(ALIASES)
    rebinder = load("d19_rebinder", REBINDER)
    proposal = rebinder.propose_native_witnesses(BOARD, old)
    contract = proposal["proposed_contract"]
    out.mkdir()
    contract_path = out / "coarse.json"
    contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n")
    checker = load("d19_p1_checker", CHECKER)
    result = checker.evaluate_coarse(BOARD, contract_path, sha(contract_path),
        source_path=P1 / "p1_requirements.yaml", interface_path=P1 / "modular_plan.json",
        alias_path=ALIASES, floorplan_path=P1 / "floorplan.yaml",
        expected_source_sha256=sha(P1 / "p1_requirements.yaml"),
        expected_interface_sha256=sha(P1 / "modular_plan.json"),
        expected_alias_sha256=sha(ALIASES), expected_floorplan_sha256=sha(P1 / "floorplan.yaml"),
        diagnose_all=True)
    (out / "full_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary = {"kind": "D19_EXACT_BOARD_P1_COARSE_DIAGNOSTIC", "status": result["status"],
               "historical_d19_status": "FAILED_RESEARCH", "p1_accepted": False,
               "p2_accepted": False, "routing_realized": False,
               "board_sha256": EXPECTED["board"], "pro_sha256": EXPECTED["pro"],
               "dru_sha256": EXPECTED["dru"], "preflight_sha256": EXPECTED["preflight"],
               "native_floorplan_sha256": sha(NATIVE_FLOOR),
               "native_nets_sha256": sha(NATIVE_NETS),
               "p1_source_sha256": sha(P1 / "p1_requirements.yaml"),
               "p1_floorplan_sha256": sha(P1 / "floorplan.yaml"),
               "p1_interfaces_sha256": sha(P1 / "modular_plan.json"),
               "contract_sha256": sha(contract_path), "checker_sha256": EXPECTED["checker"],
               "errors": result.get("errors", []), "diagnostics": result.get("diagnostics", []),
               "allocations": [{"id": row.get("id"), "status": row.get("status"),
                                "reason": row.get("reason")}
                               for row in result.get("allocations", [])],
               "new_witness_changes": proposal["geometry_changes"],
               "note": "All five coarse screens are supporting evidence only; affected P2 duties remain owed."}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
