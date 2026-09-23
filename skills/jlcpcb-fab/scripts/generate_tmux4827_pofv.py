#!/usr/bin/env python3
"""Emit the exact Crow TMUX4827 B2 native DRC aids from placed pads.

Run after generate_rules_generic.py and before native DRC. The independent
via_process_check.py grades the realized vias, areas and rule authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pcbnew as p
import yaml

from tmux4827_pofv import (AREA_PREFIX, REFS, area_bounds, audit,
                           center_pads, contract, dru_rules)


def emit(board_path: Path, assembly_path: Path):
    data = yaml.safe_load(assembly_path.read_text())
    selected = contract(data, assembly_path)
    if selected is None:
        return False
    profile, part, _ = selected
    board = p.LoadBoard(str(board_path))
    pro_path = board_path.with_suffix(".kicad_pro")
    if not pro_path.is_file():
        raise ValueError("TMUX-PROFILE: generated .kicad_pro is missing")
    # pcbnew.SaveBoard can replace generated netclasses with the board's
    # in-memory defaults. Preserve the generic emitter's exact project JSON.
    project_text = pro_path.read_text()
    project = json.loads(project_text)
    incoming = project.get("board", {}).get("design_settings", {}).get("rules", {})
    baseline = (incoming.get("min_via_diameter"), incoming.get("min_via_annular_width"))
    if baseline != (.45, .13):
        raise ValueError("TMUX-PROFILE: expected authored ordinary board floors 0.45/0.13 before profile")
    failures = audit(board, profile, part, require_areas=False, require_vias=False)
    if failures:
        raise ValueError("\n".join(failures))
    centers = center_pads(board, part, [])
    for zone in list(board.Zones()):
        if zone.GetIsRuleArea() and zone.GetZoneName().startswith(AREA_PREFIX):
            board.Remove(zone)
    for ref in REFS:
        z = p.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetZoneName(AREA_PREFIX+ref)
        z.SetLayer(p.F_Cu)
        layers = p.LSET(); layers.AddLayer(p.F_Cu)
        z.SetLayerSet(layers)
        z.SetDoNotAllowTracks(False)
        z.SetDoNotAllowVias(False)
        z.SetDoNotAllowPads(False)
        x0,y0,x1,y1 = area_bounds(centers[ref])
        z.Outline().NewOutline()
        for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)):
            z.Outline().Append(p.VECTOR2I_MM(x,y))
        board.Add(z)
    p.SaveBoard(str(board_path), board)

    # pcbnew.SaveBoard may rewrite project netclasses. Restore the complete
    # generic project, including its original ordinary .45/.13 board floors.
    pro_path.write_text(project_text)

    dru_path = board_path.with_suffix(".kicad_dru")
    if not dru_path.is_file():
        raise ValueError("TMUX-PROFILE: generic .kicad_dru is missing")
    start, end = "# BEGIN TMUX4827_YBH_B2_POFV", "# END TMUX4827_YBH_B2_POFV"
    content = dru_path.read_text()
    if (start in content) != (end in content):
        raise ValueError("TMUX-PROFILE: damaged generated DRU block")
    if start in content:
        content = content[:content.index(start)] + content[content.index(end)+len(end):]
    content = content.rstrip() + "\n" + start + "\n" + "\n".join(dru_rules()) + "\n" + end + "\n"
    dru_path.write_text(content)
    failures = audit(p.LoadBoard(str(board_path)), profile, part, require_vias=False)
    if failures:
        raise ValueError("\n".join(failures))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board", type=Path)
    ap.add_argument("--assembly", type=Path, required=True)
    args = ap.parse_args()
    try:
        active = emit(args.board, args.assembly)
    except (ValueError, KeyError, OSError) as exc:
        ap.exit(1, f"TMUX-PROFILE FAIL: {exc}\n")
    print("TMUX-PROFILE: " + ("eight exact B2 areas and rules emitted" if active else "N-A"))


if __name__ == "__main__":
    main()
