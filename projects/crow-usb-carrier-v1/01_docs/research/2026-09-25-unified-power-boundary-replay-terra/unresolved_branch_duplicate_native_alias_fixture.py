#!/usr/bin/env python3
"""Adversarial fixture: two J_USB sources must not share one native pad."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "skills/kicad-pcb/scripts"))
try:
    import pcbnew
except ImportError:
    sys.path.append("/usr/lib/python3/dist-packages")
    import pcbnew
import p1_corridor_capacity as checker


def iu(mm): return pcbnew.FromMM(mm)


def add_pad(board, ref, net, x, y):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref); fp.SetValue("fixture"); fp.SetLayer(pcbnew.F_Cu)
    fp.SetPosition(pcbnew.VECTOR2I(iu(x), iu(y)))
    item = pcbnew.PAD(fp); item.SetNumber("1"); item.SetNet(board.FindNet(net))
    item.SetAttribute(pcbnew.PAD_ATTRIB_SMD); item.SetShape(pcbnew.PAD_SHAPE_RECT)
    item.SetSize(pcbnew.VECTOR2I(iu(.4), iu(.4))); item.SetPosition(fp.GetPosition())
    item.SetLayerSet(pcbnew.LSET.FrontMask())
    native_net = board.FindNet(net)
    if native_net is None:
        native_net = pcbnew.NETINFO_ITEM(board, net); board.Add(native_net)
    item.SetNet(native_net)
    fp.Add(item); board.Add(fp)


def main():
    board = pcbnew.BOARD()
    add_pad(board, "J_USB", "TREE", 2, 2); add_pad(board, "J_B", "TREE", 5, 5); add_pad(board, "J_C", "TREE", 6, 5)
    _, pads = checker.graph.board_index(board)
    aliases = checker.graph.alias_inventory({"pin_aliases": {
        "a": {"schematic": "A1", "footprint": "1"},
        "b": {"schematic": "B1", "footprint": "1"}}})
    pairs = [("J_USB.A1", "a"), ("J_USB.B1", "a"), ("J_B.1", "b"), ("J_C.1", "b")]
    endpoints = sorted(({"source_pad": s, "native_pad": checker.graph.native_identity(s, aliases),
                         "net": "TREE", "block": block} for s, block in pairs),
                       key=lambda row: (row["source_pad"], row["native_pad"], row["block"]))
    p2 = [{"status": "P2_REQUIRED", **row, "branch_id": "tree", "layer": "F.Cu",
           "proof": "native_pad_to_unplaced_tree"} for row in endpoints]
    branch = {"id": "tree", "owner": "board_integration", "allocation_id": "signal", "net": "TREE",
              "layer": "F.Cu", "reference_layer": "B.Cu", "reservation_id": "tree_unplaced",
              "terminal_count": 4, "minimum_tree_edges": 3, "endpoints": endpoints, "p2_obligations": p2,
              "physical_blockers": [{"source_pad": "J_C.1", "native_pad": "J_C.1", "block": "b",
                                     "foreign_regions": ["foreign"]}],
              "tree_obligation": {"status": "P3_REQUIRED", "net": "TREE", "terminal_count": 4,
                                  "minimum_tree_edges": 3, "proof": "one_connected_native_net_without_unrelated_branches"},
              "return_obligation": {"status": "P2_REQUIRED", "net": "GND", "branch_id": "tree",
                                    "reference_layer": "B.Cu", "proof": "continuous_filled_reference_under_actual_tree"}}
    interfaces = {"interfaces": [{"net": "TREE", "endpoints": {"a": ["J_USB.A1", "J_USB.B1"],
                                                          "b": ["J_B.1", "J_C.1"]}}]}
    try:
        checker._unresolved_branches({"unresolved_multiterminal_branches": [branch]}, interfaces, board,
            {"a": [1, 1, 3, 3], "b": [4, 4, 7, 6], "foreign": [5.7, 4.7, 6.5, 5.5]},
            {"signal": {"TREE"}}, aliases, pads)
    except checker.ContractError as exc:
        print(f"PASS: rejected duplicate native alias: {exc}")
        return
    raise SystemExit("FAIL: accepted J_USB.A1/J_USB.B1 -> J_USB.1 duplicate native pad")


if __name__ == "__main__": main()
