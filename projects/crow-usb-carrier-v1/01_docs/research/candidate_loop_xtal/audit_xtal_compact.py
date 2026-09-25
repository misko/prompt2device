#!/usr/bin/env python3
"""Read-only exact pad-center connectivity census for the isolated r2 board."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pcbnew

from run_xtal_escape import sha


PADS = {
    "XTAL_IN": {"U_XU.34", "R_XTAL_FB.1", "R_XTAL_DRIVE.1"},
    "XTAL_OUT": {"U_XU.33", "R_XTAL_FB.2", "Y_XU.3", "C_XTAL_OUT.1"},
    "XTAL_IN_R": {"R_XTAL_DRIVE.2", "Y_XU.1", "C_XTAL_IN.1"},
}
OSC_REFS = {"Y_XU", "R_XTAL_FB", "R_XTAL_DRIVE", "C_XTAL_IN", "C_XTAL_OUT"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--board", type=Path, required=True)
    ap.add_argument("--drc", type=Path, required=True)
    ap.add_argument("--json", type=Path, required=True)
    args = ap.parse_args()
    board = pcbnew.LoadBoard(str(args.board))
    all_pads = {f"{fp.GetReference()}.{pad.GetNumber()}": pad
                for fp in board.GetFootprints() for pad in fp.Pads()}
    result = {"schema": 1, "kind": "crow-xtal-r2-saved-board-component-audit",
              "board_sha256": sha(args.board), "drc_sha256": sha(args.drc),
              "nets": {}, "ground": {}}
    for net, names in PADS.items():
        parent = {}

        def find(x):
            parent.setdefault(x, x)
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(a, b):
            parent[find(a)] = find(b)

        tracks = [t for t in board.GetTracks() if t.GetNetname() == net]
        for track in tracks:
            if track.GetLayer() != pcbnew.F_Cu:
                raise ValueError(f"{net}: non-F.Cu copper in candidate")
            a, b = track.GetStart(), track.GetEnd()
            union((a.x, a.y), (b.x, b.y))
        pad_roots = {}
        for name in sorted(names):
            pad = all_pads[name]
            if pad.GetNetname() != net:
                raise ValueError(f"{name}: unexpected net {pad.GetNetname()}")
            pos = pad.GetPosition()
            xy = (pos.x, pos.y)
            pad_roots[name] = find(xy) if xy in parent else None
        connected = all(root is not None for root in pad_roots.values()) and len(set(pad_roots.values())) == 1
        result["nets"][net] = {"pads": sorted(names), "pad_count": len(names),
                               "F_Cu_segments": len(tracks), "connected_by_exact_endpoints": connected}
    zones = [z for z in board.Zones() if z.GetNetname() == "GND" and
             pcbnew.In1_Cu in list(z.GetLayerSet().Seq())]
    result["ground"]["In1_Cu_zone_count"] = len(zones)
    result["ground"]["filled_polygon_count"] = sum(
        z.GetFilledPolysList(pcbnew.In1_Cu).OutlineCount() for z in zones)
    drc = json.loads(args.drc.read_text(encoding="utf-8-sig"))
    ground_rows = []
    for row in drc["unconnected_items"]:
        descriptions = [item.get("description", "") for item in row.get("items", [])]
        if any("[GND]" in desc and any(f"of {ref} " in desc for ref in OSC_REFS)
               for desc in descriptions):
            ground_rows.append(descriptions)
    result["ground"]["oscillator_GND_open_rows"] = ground_rows
    result["ground"]["oscillator_GND_open_count"] = len(ground_rows)
    result["claim_limit"] = "Exact pad-center track graph only; DRC, ground-pad returns, crystal electrical/loop checks, and P1/P2 acceptance remain independent."
    args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"nets": result["nets"], "ground": {k: v for k, v in result["ground"].items() if k != "oscillator_GND_open_rows"}}, indent=2))
    return 0 if all(row["connected_by_exact_endpoints"] for row in result["nets"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
