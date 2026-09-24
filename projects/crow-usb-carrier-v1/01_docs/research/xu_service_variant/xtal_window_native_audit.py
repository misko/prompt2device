#!/usr/bin/env python3
"""Native, hash-pinned audit of the XMOS crystal window in the QSPI-gap probe.

This is research evidence only.  It reads the isolated regenerated board and
the packet's source variant; it changes neither canonical source nor board.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / "projects/crow-usb-carrier-v1"
PACKET = HERE / "p1_qspi_packet"
BOARD = Path("/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb")
FLOORPLAN = PACKET / "floorplan_qspi_gap.yaml"
SOURCE = PACKET / "p1_source_variant.yaml"
CONTRACT = PACKET / "coarse_contract.json"
INTERFACES = PROJECT / "03_src/modular_plan.json"
ALIASES = PROJECT / "02_parts/USB4215-03-A/part.yaml"
CHECKER = ROOT / "skills/kicad-pcb/scripts/p1_corridor_capacity.py"
OUT = HERE / "xtal_window_native_audit.json"

EXPECTED = {
    "board": "fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27",
    "floorplan": "cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925",
    "source": "9a13c0999d29f17280bb5d8ffb98a5e0d59afe3ee4511eb004e436bffc13ece4",
    "contract": "b17a94fedafbc334bdc0721535c640fb786f4b632b1abddf487289fdb19fbda4",
}
ENDPOINTS = (
    ("U_XU.34", "XTAL_IN", "xmos_core"),
    ("R_XTAL_DRIVE.1", "XTAL_IN", "clock_flash_debug"),
    ("R_XTAL_FB.1", "XTAL_IN", "clock_flash_debug"),
    ("U_XU.33", "XTAL_OUT", "xmos_core"),
    ("C_XTAL_OUT.1", "XTAL_OUT", "clock_flash_debug"),
    ("R_XTAL_FB.2", "XTAL_OUT", "clock_flash_debug"),
    ("Y_XU.3", "XTAL_OUT", "clock_flash_debug"),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox_mm(box):
    return [round(v / 1_000_000, 6) for v in
            (box.GetX(), box.GetY(), box.GetRight(), box.GetBottom())]


def contains(box: list[float], point_box: list[float]) -> bool:
    return (box[0] <= point_box[0] and box[1] <= point_box[1]
            and point_box[2] <= box[2] and point_box[3] <= box[3])


def load_checker():
    spec = importlib.util.spec_from_file_location("p1_corridor_capacity", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def main() -> None:
    paths = {"board": BOARD, "floorplan": FLOORPLAN, "source": SOURCE,
             "contract": CONTRACT}
    hashes = {name: digest(path) for name, path in paths.items()}
    for name, expected in EXPECTED.items():
        if hashes[name] != expected:
            raise RuntimeError(f"{name} hash drift: {hashes[name]}")

    checker = load_checker()
    board = checker.pcbnew.LoadBoard(str(BOARD))
    floorplan = yaml.safe_load(FLOORPLAN.read_text())
    source = yaml.safe_load(SOURCE.read_text())
    contract = json.loads(CONTRACT.read_text())
    regions = floorplan["placement"]["regions"]
    allocation = next(a for a in contract["allocations"]
                      if a["id"] == "xmos_service_escape")
    window = next(r for r in allocation["reservations"]
                  if r["id"] == "crystal_clock_cell")["bbox"]

    pads = {}
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            pads[f"{footprint.GetReference()}.{pad.GetNumber()}"] = pad
    rows = []
    for ref_pad, net, owner in ENDPOINTS:
        pad = pads.get(ref_pad)
        if pad is None:
            raise RuntimeError(f"missing native pad {ref_pad}")
        if pad.GetNetname() != net:
            raise RuntimeError(f"{ref_pad}: expected {net}, got {pad.GetNetname()}")
        box = bbox_mm(pad.GetBoundingBox())
        rows.append({"ref_pad": ref_pad, "net": net, "owner": owner,
                     "pad_bbox_mm": box, "inside_crystal_window": contains(window, box)})

    # Reuse the current native checker for the two only cross-owner endpoints.
    # Its witness envelopes end at the clock-cell edge and must not traverse
    # the intervening board-integration/QSPI region.
    outline = checker.pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise RuntimeError("native outline unavailable")
    _, native_pads = checker.graph.board_index(board)
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    interfaces = json.loads(INTERFACES.read_text())
    owned_pads = {}
    for interface in interfaces["interfaces"]:
        for block, members in interface["endpoints"].items():
            owned_pads.setdefault((interface["net"], block), set()).update(members)
    coverage, _ = checker.graph.source_inventory(source, interfaces)
    corridors = checker._integration_corridors(
        source, interfaces, board, outline, regions, list(board.Zones()), coverage,
        aliases, native_pads, {})
    witnesses = [w for w in allocation["boundary_witnesses"]
                 if w.get("source") in {"U_XU.33", "U_XU.34"}]
    bridge_results = []
    for witness in witnesses:
        try:
            checker._coarse_witness(
                board, witness, witness["net"], owned_pads, aliases, native_pads,
                outline, regions, set(source["p1_fixed_refs"]), {}, corridors)
        except checker.ContractError as exc:
            bridge_results.append({"ref_pad": witness["source"], "status": "REJECTED",
                                   "reason": str(exc),
                                   "boundary_bbox_mm": witness["boundary_bbox"]})
        else:
            raise RuntimeError(f"{witness['source']}: expected bridge rejection drift")
    if len(bridge_results) != 2:
        raise RuntimeError("cross-owner oscillator witness denominator drift")

    result = {
        "schema": 1,
        "kind": "crow-xtal-window-native-audit",
        "status": "REJECTED_SOURCE_LOCAL_HANDOFF",
        "hashes": {**hashes, "checker": digest(CHECKER)},
        "board_path": str(BOARD),
        "crystal_window_mm": window,
        "exact_endpoint_count": len(rows),
        "exact_endpoints": rows,
        "cross_owner_witness_count": len(bridge_results),
        "cross_owner_witnesses": bridge_results,
        "finding": ("The two XMOS pads require a handoff across the QSPI-gap "
                    "region; the current checker rejects each witness as a "
                    "nonlocal bridge.  The existing local crystal window also "
                    "excludes U_XU.33, U_XU.34, R_XTAL_DRIVE.1 and Y_XU.3."),
        "next_action": ("The owning floorplan/interface author must declare and "
                        "place a local oscillator cell whose endpoint ownership "
                        "does not cross board_integration_qspi, then supply native "
                        "P2 pad access and filled In1.Cu return evidence.  Do not "
                        "promote this as P1 acceptance."),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "hashes": result["hashes"],
                      "rejected": [r["ref_pad"] for r in bridge_results]}, indent=2))


if __name__ == "__main__":
    main()
