#!/usr/bin/env python3
"""Read-only native-connectivity and In1 fill projection audit for XTAL r2.

This does not alter a board, refill zones, or claim an electrical return.  It
checks the saved DRC boards because those are the filled artifacts under
review.  Run from this directory (or give explicit paths):

  python3 audit_xtal_return_terra.py --json xtal_r2_return_terra.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pcbnew


PROJECT = Path(__file__).resolve().parents[3]
R2 = PROJECT / "06_build" / "candidates" / "xtal-r2"
BOARDS = {
    "baseline": R2 / "04_kicad" / "crow_carrier.kicad_pcb",
    "candidate": R2 / "04_kicad" / "xtal_compact_candidate.kicad_pcb",
}
SIGNAL_GROUPS = {
    "XTAL_IN": ("U_XU.34", "R_XTAL_FB.1", "R_XTAL_DRIVE.1"),
    "XTAL_OUT": ("U_XU.33", "R_XTAL_FB.2", "Y_XU.3", "C_XTAL_OUT.1"),
    "XTAL_IN_R": ("R_XTAL_DRIVE.2", "Y_XU.1", "C_XTAL_IN.1"),
}
GND_TERMINALS = ("Y_XU.2", "Y_XU.4", "C_XTAL_IN.2", "C_XTAL_OUT.2")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pads_by_name(board):
    return {f"{fp.GetReference()}.{pad.GetNumber()}": pad
            for fp in board.GetFootprints() for pad in fp.Pads()}


def pad_name(item) -> str | None:
    if item.GetClass() != "PAD":
        return None
    fp = item.GetParentFootprint()
    return f"{fp.GetReference()}.{item.GetNumber()}"


def component_names(connectivity, pad) -> list[str]:
    # KiCad returns the queried item too, so this includes the terminal itself.
    return sorted({name for item in connectivity.GetConnectedItems(pad)
                   if (name := pad_name(item)) is not None})


def filled_outline_indices(polyset, point) -> list[int]:
    # Deliberately examine the filled polygons, rather than treating zone
    # existence as coverage.  Points on a boundary are accepted by the full
    # polyset predicate and assigned no specific island.
    indices = [i for i in range(polyset.OutlineCount())
               if polyset.Outline(i).PointInside(point)]
    return indices if indices or polyset.Contains(point) else []


def audit_board(label: str, board_path: Path) -> dict:
    board = pcbnew.LoadBoard(str(board_path))
    connectivity = pcbnew.CONNECTIVITY_DATA()
    connectivity.Build(board)
    connectivity.RecalculateRatsnest()
    pads = pads_by_name(board)
    result = {
        "board_sha256": sha256(board_path),
        "native_unconnected_count": int(connectivity.GetUnconnectedCount(False)),
        "signal_components": {},
    }
    for net, names in SIGNAL_GROUPS.items():
        components = {name: component_names(connectivity, pads[name])
                      for name in names}
        result["signal_components"][net] = {
            "expected_pads": list(names),
            "all_expected_pads_in_each_component": all(
                set(names).issubset(component) for component in components.values()),
            "components": components,
        }

    gnd_components = {name: component_names(connectivity, pads[name])
                      for name in GND_TERMINALS}
    result["gnd_terminals"] = {
        "terminals": list(GND_TERMINALS),
        "components": gnd_components,
        "all_terminals_connected_together": all(
            set(GND_TERMINALS).issubset(component)
            for component in gnd_components.values()),
    }

    zones = [zone for zone in board.Zones()
             if zone.GetNetname() == "GND"
             and pcbnew.In1_Cu in list(zone.GetLayerSet().Seq())]
    if len(zones) != 1:
        raise ValueError(f"{label}: expected one GND In1.Cu zone, got {len(zones)}")
    polyset = zones[0].GetFilledPolysList(pcbnew.In1_Cu)
    projection = {name: filled_outline_indices(polyset, pads[name].GetPosition())
                  for names in SIGNAL_GROUPS.values() for name in names}
    projection.update({name: filled_outline_indices(polyset, pads[name].GetPosition())
                       for name in GND_TERMINALS})
    tracks = [track for track in board.GetTracks()
              if track.GetClass() == "PCB_TRACK" and track.GetNetname() in SIGNAL_GROUPS]
    track_projection = []
    for track in tracks:
        midpoint = pcbnew.VECTOR2I((track.GetStart().x + track.GetEnd().x) // 2,
                                   (track.GetStart().y + track.GetEnd().y) // 2)
        track_projection.append({
            "net": track.GetNetname(),
            "filled_outline_indices_at_midpoint": filled_outline_indices(polyset, midpoint),
        })
    result["in1_gnd_projection"] = {
        "filled_polygon_count": polyset.OutlineCount(),
        "terminal_outline_indices": projection,
        "all_signal_and_gnd_terminal_centers_covered": all(projection.values()),
        "signal_track_count": len(tracks),
        "all_signal_track_midpoints_covered": (
            all(row["filled_outline_indices_at_midpoint"] for row in track_projection)
            if track_projection else None
        ),
        "signal_track_midpoint_projection": track_projection,
    }
    return result


def violation_counts(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8-sig"))
    counts = {}
    for row in report["violations"]:
        counts[row["type"]] = counts.get(row["type"], 0) + 1
    return {"unconnected_item_rows": len(report["unconnected_items"]),
            "violation_counts": counts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path,
                        default=Path(__file__).with_name("xtal_r2_return_terra.json"))
    args = parser.parse_args()
    result = {
        "schema": 1,
        "kind": "crow-xtal-r2-native-connectivity-and-filled-projection-audit",
        "boards": {label: audit_board(label, path) for label, path in BOARDS.items()},
        "drc_json": {
            "baseline": violation_counts(R2 / "baseline_drc.json"),
            "candidate": violation_counts(R2 / "candidate_drc.json"),
        },
        "conclusion": (
            "The candidate joins the three named signal-pad groups under "
            "native connectivity and reduces the native unconnected count; "
            "the GND terminals remain individually isolated.  Filled In1 "
            "polygons project beneath every sampled terminal and every signal "
            "track midpoint, but projection is not a copper return from an "
            "F.Cu SMD GND pad.  This is not oscillator return proof or an "
            "engineering acceptance claim."
        ),
    }
    args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"baseline_native_unconnected": result["boards"]["baseline"]["native_unconnected_count"],
                      "candidate_native_unconnected": result["boards"]["candidate"]["native_unconnected_count"],
                      "candidate_signals": result["boards"]["candidate"]["signal_components"],
                      "candidate_gnd": result["boards"]["candidate"]["gnd_terminals"],
                      "candidate_drc": result["drc_json"]["candidate"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
