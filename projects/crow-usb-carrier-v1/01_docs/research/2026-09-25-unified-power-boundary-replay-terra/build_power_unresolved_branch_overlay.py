#!/usr/bin/env python3
"""Reproduce no-credit power branches on the unified P1 diagnostic board."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import yaml

from build_one_pad_shared_port_overlay import (ALIASES, BOARD, CHECKER, EXPECTED,
                                                LOCAL, PACKET, sha)

try:
    import pcbnew
except ImportError:
    sys.path.append("/usr/lib/python3/dist-packages")
    import pcbnew

NETS = ("N1V8", "N3V3X", "N3V3_ADC", "N5V_BUCK")


def checker_module():
    spec = importlib.util.spec_from_file_location("power_branch_checker", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def require_inputs() -> None:
    paths = {"board": BOARD, "requirements": PACKET / "p1_requirements.yaml",
             "contract": PACKET / "coarse.json", "floorplan": PACKET / "floorplan.yaml",
             "interfaces": PACKET / "modular_plan.json", "aliases": ALIASES,
             "checker": CHECKER}
    for name, path in paths.items():
        if sha(path) != EXPECTED[name]:
            raise SystemExit(f"{name} SHA drift")


def branch(net, interfaces, aliases, pads, regions, helper):
    item = next(row for row in interfaces["interfaces"] if row["net"] == net)
    entries = sorted({(source_pad, helper.graph.native_identity(source_pad, aliases), net, block)
                      for block, names in item["endpoints"].items() for source_pad in names})
    blockers = []
    for source_pad, native_pad, _, block in entries:
        found = pads.get(native_pad, [])
        if len(found) != 1:
            raise SystemExit(f"{net}: native pad identity is not singular: {native_pad}")
        box = helper.box_mm(found[0].GetBoundingBox())
        # Keep the exact endpoint even when the current schema cannot assign
        # its physical cell.  The checker must reject that condition itself;
        # dropping it here would turn a schema-gap probe into a false pass.
        foreign = sorted(name for name, region in regions.items()
                         if name != block and helper.intersects(box, region))
        if foreign:
            blockers.append({"source_pad": source_pad, "native_pad": native_pad,
                             "block": block, "foreign_regions": foreign})
    ident, reservation_id = f"power_{net.lower()}_unplaced_tree", f"power_{net.lower()}_unresolved_tree"
    endpoint_rows = [{"source_pad": source_pad, "native_pad": native_pad,
                      "net": net, "block": block}
                     for source_pad, native_pad, _, block in entries]
    p2 = [{"status": "P2_REQUIRED", **endpoint, "branch_id": ident, "layer": "F.Cu",
           "proof": "native_pad_to_unplaced_tree"} for endpoint in endpoint_rows]
    row = {"id": ident, "owner": "board_integration", "allocation_id": "power_boundary_windows",
           "net": net, "layer": "F.Cu", "reference_layer": "In1.Cu",
           "reservation_id": reservation_id, "terminal_count": len(entries),
           "minimum_tree_edges": len(entries) - 1, "endpoints": endpoint_rows,
           "physical_blockers": blockers, "p2_obligations": p2,
           "tree_obligation": {"status": "P3_REQUIRED", "net": net,
                               "terminal_count": len(entries), "minimum_tree_edges": len(entries) - 1,
                               "proof": "one_connected_native_net_without_unrelated_branches"},
           "return_obligation": {"status": "P2_REQUIRED", "net": "GND", "branch_id": ident,
                                 "reference_layer": "In1.Cu",
                                 "proof": "continuous_filled_reference_under_actual_tree"}}
    return row, entries[0], helper.box_mm(pads[entries[0][1]][0].GetBoundingBox())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=Path("/tmp/crow-unified-power-branches-terra"))
    args = parser.parse_args()
    require_inputs()
    if args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True)
    req_path, floor_path, iface_path, contract_path = (args.output / "p1_requirements.yaml",
        args.output / "floorplan.yaml", args.output / "modular_plan.json", args.output / "coarse.json")
    for source, target in ((PACKET / "p1_requirements.yaml", req_path),
                           (PACKET / "floorplan.yaml", floor_path),
                           (PACKET / "modular_plan.json", iface_path),
                           (PACKET / "coarse.json", contract_path)):
        shutil.copy2(source, target)
    source, floor, interfaces = (yaml.safe_load(req_path.read_text()), yaml.safe_load(floor_path.read_text()),
                                 json.loads(iface_path.read_text()))
    contract = json.loads(contract_path.read_text())
    helper = checker_module()
    aliases = helper.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    board = pcbnew.LoadBoard(str(BOARD))
    _, pads = helper.graph.board_index(board)
    regions = floor["placement"]["regions"]
    allocation = next(row for row in contract["allocations"] if row["id"] == "power_boundary_windows")
    for witness in allocation["boundary_witnesses"]:
        if witness["net"] not in LOCAL:
            continue
        source_pad, block, face, region_face, bbox, reservation = LOCAL[witness["net"]]
        witness.update(kind="virtual_block_face", face=face, region_id=block,
                       region_face=region_face, boundary_bbox=bbox)
        witness["p2_obligation"] = {"status": "P2_REQUIRED", "source_pad": source_pad,
            "native_pad": witness["native"], "net": witness["net"], "block": block,
            "region_face": region_face, "layer": "F.Cu", "to_reservation": witness["reservation_id"]}
        next(r for r in allocation["reservations"] if r["nets"] == [witness["net"]])["bbox"] = reservation
    branches = []
    for net in NETS:
        row, representative, pad_bbox = branch(net, interfaces, aliases, pads, regions, helper)
        branches.append(row)
        source["unresolved_multiterminal_branches"].append(row)
        source_pad, native_pad, _, block = representative
        witness = next(w for w in allocation["boundary_witnesses"] if w["net"] == net)
        witness.clear()
        witness.update({"kind": "unresolved_multiterminal_branch", "branch_id": row["id"],
            "source": source_pad, "native": native_pad, "net": net, "block": block,
            "face": "north", "layer": "F.Cu", "boundary_bbox": pad_bbox,
            "reservation_id": row["reservation_id"],
            "p2_obligation": next(p for p in row["p2_obligations"] if p["source_pad"] == source_pad)})
        reservation = next(r for r in allocation["reservations"] if r["nets"] == [net])
        reservation.clear()
        reservation.update({"id": row["reservation_id"], "kind": "unresolved_multiterminal_branch",
                            "branch_id": row["id"], "layer": "F.Cu", "nets": [net]})
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
    power = next((row for row in result["allocations"] if row["id"] == "power_boundary_windows"), None)
    power_diags = [row for row in result["diagnostics"] if row["allocation"] == "power_boundary_windows"]
    receipt = {"kind": "research-unified-power-unresolved-branches", "status": result["status"],
        "p1_accepted": result["p1_accepted"], "routing_realized": result["routing_realized"],
        "inputs": EXPECTED, "overlay": {"requirements_sha256": sha(req_path),
        "contract_sha256": sha(contract_path), "result_sha256": sha(result_path)},
        "power": {"diagnostics": power_diags,
                  "status": power["status"] if power else "NOT_EVALUATED",
                  "branches": [{"net": row["net"], "terminal_count": row["terminal_count"],
                                "minimum_tree_edges": row["minimum_tree_edges"],
                                "p2_obligations": len(row["p2_obligations"]),
                                "physical_blockers": row["physical_blockers"]} for row in branches]},
        "global_errors": result["errors"]}
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if (result["p1_accepted"] or result["routing_realized"] or
            sum(row["terminal_count"] for row in branches) != 171 or
            not any("branch pad outside source owner region" in error for error in result["errors"])):
        raise SystemExit("unexpected branch overlay outcome")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
