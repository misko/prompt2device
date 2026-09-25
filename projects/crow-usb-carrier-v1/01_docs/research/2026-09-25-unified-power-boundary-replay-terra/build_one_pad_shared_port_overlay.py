#!/usr/bin/env python3
"""Reproduce the research-only one-pad shared-power-port fail-open probe.

The generated files live outside the repository by default.  This program
pins every input before creating them and refuses an outcome that could be
mistaken for P1 acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / "projects/crow-usb-carrier-v1"
PACKET = PROJECT / "01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol"
BOARD = PROJECT / "01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb"
ALIASES = PROJECT / "02_parts/USB4215-03-A/part.yaml"
CHECKER = ROOT / "skills/kicad-pcb/scripts/p1_corridor_capacity.py"

EXPECTED = {
    "board": "d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7",
    "requirements": "f6f132891712bfcb1cec4d1df6714748337040ba5c42ae3fecd14fb9c35d1222",
    "contract": "18936dc3f3dd6e01637182b2dab57cb472a31bfa2eb345a20bd4f7867708777f",
    "floorplan": "7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0",
    "interfaces": "02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8",
    "aliases": "a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e",
    "checker": "05cf56078391cf4e092411dce2c81062ee28b86f7b606abb43af9774eed736d4",
}

LOCAL = {
    "GND": ("C_ADC_3V3X_OK_VDD.2", "adc_reference", "south", "north",
            [117.9, 85, 118.3, 85.5], [117.9, 84, 118.3, 85]),
    "N0V9": ("C_CORE_FF.1", "digital_power", "west", "east",
             [184.5, 116.5, 185, 117.3], [185, 116.5, 190, 117.3]),
    "N12V_PROTECTED": ("C_SPOKE_IN1.1", "analog_ch1", "north", "south",
                         [36.3, 83.5, 37.4, 84], [36.3, 84, 37.4, 85]),
    "N5V_LDO_HOLD": ("C_ISO1.1", "analog_ch1", "north", "south",
                       [33.6, 83.5, 34.3, 84], [33.6, 84, 34.3, 85]),
    "PWR_EN": ("U_ADC_PWR_BAD.2", "adc_reference", "south", "north",
               [100, 85, 100.5, 85.4], [100, 84, 100.5, 85]),
}

# These are deliberately insufficient declarations: one selected pad versus
# every interface terminal.  They exist only to make the checker gap auditable.
PROBE = [
    ("N1V8", "R_ADC_1V8_OK_TOP.1", "adc_reference", 114.40),
    ("N3V3X", "R_ADC_3V3X_OK_TOP.1", "adc_reference", 114.70),
    ("N3V3_ADC", "C_ADC_3V3X_OK_VDD.1", "adc_reference", 115.00),
    ("N5V_BUCK", "C_1V8_OK_VDD.1", "digital_power", 115.30),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_inputs() -> None:
    paths = {
        "board": BOARD, "requirements": PACKET / "p1_requirements.yaml",
        "contract": PACKET / "coarse.json",
        "floorplan": PACKET / "floorplan.yaml", "interfaces": PACKET / "modular_plan.json",
        "aliases": ALIASES, "checker": CHECKER,
    }
    for name, path in paths.items():
        actual = sha(path)
        if actual != EXPECTED[name]:
            raise SystemExit(f"{name} SHA drift: {actual}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=Path("/tmp/crow-unified-one-pad-power-port-terra"))
    parser.add_argument("--only-net", choices=[row[0] for row in PROBE],
                        help="run one of the four independent one-pad probes")
    args = parser.parse_args()
    require_inputs()
    if args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True)
    req_path, floor_path, iface_path, contract_path = (
        args.output / "p1_requirements.yaml", args.output / "floorplan.yaml",
        args.output / "modular_plan.json", args.output / "coarse.json")
    for src, dst in ((PACKET / "p1_requirements.yaml", req_path),
                     (PACKET / "floorplan.yaml", floor_path),
                     (PACKET / "modular_plan.json", iface_path),
                     (PACKET / "coarse.json", contract_path)):
        shutil.copy2(src, dst)
    source = yaml.safe_load(req_path.read_text())
    contract = json.loads(contract_path.read_text())
    allocation = next(a for a in contract["allocations"]
                      if a["id"] == "power_boundary_windows")
    for witness in allocation["boundary_witnesses"]:
        if witness["net"] not in LOCAL:
            continue
        source_pad, block, face, region_face, bbox, reservation = LOCAL[witness["net"]]
        assert (witness["source"], witness["block"]) == (source_pad, block)
        witness.update(kind="virtual_block_face", face=face, region_id=block,
                       region_face=region_face, boundary_bbox=bbox)
        witness["p2_obligation"] = {"status": "P2_REQUIRED", "source_pad": source_pad,
            "native_pad": witness["native"], "net": witness["net"], "block": block,
            "region_face": region_face, "layer": "F.Cu",
            "to_reservation": witness["reservation_id"]}
        next(r for r in allocation["reservations"] if r["nets"] == [witness["net"]])["bbox"] = reservation
    probe = [row for row in PROBE if args.only_net in (None, row[0])]
    ports = []
    for net, source_pad, block, y in probe:
        ident, reservation_id = f"probe_{net.lower()}", f"probe_res_{net.lower()}"
        bbox, reservation = [145, y, 145.1, y + .1], [144.9, y, 145, y + .1]
        endpoint = {"source_pad": source_pad, "native_pad": source_pad,
                    "net": net, "block": block}
        ports.append({"id": ident, "owner": "board_integration",
            "participants": ["adc_reference", "digital_power"],
            "geometry": {"type": "union_rectangles", "rectangles": [[144.9, y, 145.1, y + .1]]},
            "bbox": bbox, "reservation_bbox": reservation, "layers": ["F.Cu"],
            "face": "east", "reservation_id": reservation_id, "affected": [endpoint],
            "p2_obligations": [{"status": "P2_REQUIRED", **endpoint, "port_id": ident,
                                "layer": "F.Cu", "to_reservation": reservation_id}],
            "return_obligation": {"status": "P2_REQUIRED", "net": "GND", "port_id": ident,
                                  "layers": ["F.Cu"], "proof": "continuous_filled_reference"}})
        witness = next(w for w in allocation["boundary_witnesses"] if w["net"] == net)
        witness.clear()
        witness.update({"kind": "shared_transition_port", "port_id": ident, **endpoint,
            "face": "east", "layer": "F.Cu", "boundary_bbox": bbox,
            "reservation_id": reservation_id,
            "p2_obligation": {"status": "P2_REQUIRED", **endpoint, "port_id": ident,
                              "layer": "F.Cu", "to_reservation": reservation_id}})
        next(r for r in allocation["reservations"] if r["nets"] == [net]).update(
            id=reservation_id, kind="power_or_mechanical", bbox=reservation, layer="F.Cu", nets=[net])
    source["shared_transition_ports"] = ports
    req_path.write_text(yaml.safe_dump(source, sort_keys=False))
    contract.update(board_sha256=sha(BOARD), source_sha256=sha(req_path),
                    floorplan_sha256=sha(floor_path), interfaces_sha256=sha(iface_path),
                    aliases_sha256=sha(ALIASES))
    contract_path.write_text(json.dumps(contract, indent=2) + "\n")
    result_path = args.output / "result.json"
    command = [sys.executable, str(CHECKER), str(BOARD), str(contract_path), str(result_path),
        "--expected-contract-sha256", sha(contract_path), "--source-requirements", str(req_path),
        "--interfaces", str(iface_path), "--aliases", str(ALIASES), "--floorplan", str(floor_path),
        "--expected-source-sha256", sha(req_path), "--expected-interface-sha256", sha(iface_path),
        "--expected-alias-sha256", sha(ALIASES), "--expected-floorplan-sha256", sha(floor_path),
        "--diagnose-all"]
    subprocess.run(command, check=False)
    result = json.loads(result_path.read_text())
    power = next((a for a in result["allocations"] if a["id"] == "power_boundary_windows"), None)
    interfaces = json.loads(iface_path.read_text())
    denominators = {net: sum(len(pads) for pads in next(i for i in interfaces["interfaces"]
                    if i["net"] == net)["endpoints"].values()) for net, *_ in probe}
    expected_rejections = {f"probe_{net.lower()}: power port exact endpoint denominator missing for {net}"
                           for net, *_ in probe}
    rejections = [error for error in result["errors"] if error in expected_rejections]
    receipt = {"kind": "research-one-pad-shared-power-port", "status": result["status"],
        "p1_accepted": result["p1_accepted"], "routing_realized": result["routing_realized"],
        "inputs": EXPECTED, "overlay": {"contract_sha256": sha(contract_path),
        "requirements_sha256": sha(req_path), "result_sha256": sha(result_path)},
        "power_diagnostics": [d for d in result["diagnostics"] if d["allocation"] == "power_boundary_windows"],
        "power_status": power["status"] if power else "NOT_EVALUATED",
        "selected_port_endpoints": {net: source_pad for net, source_pad, *_ in probe},
        "full_endpoint_denominators": denominators,
        "checker_rejections": rejections,
        "admission": "REJECT: one-pad shared-port set is not the full per-net denominator."}
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if (result["p1_accepted"] or result["routing_realized"] or power is not None or
            len(rejections) != 1):
        raise SystemExit("unexpected probe outcome")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
