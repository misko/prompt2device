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

from tmux4827_pofv import (ABSOLUTE_FLOORS, AREA_PREFIX, REFS, activated,
                           area_bounds, audit, center_pads, contract, dru_rules)


def emit(board_path: Path, assembly_path: Path):
    data = yaml.safe_load(assembly_path.read_text())
    selected = contract(data, assembly_path)
    if selected is None:
        return False
    profile, part, _ = selected
    floor = yaml.safe_load((assembly_path.resolve().parents[1] / "floorplan.yaml").read_text()) or {}
    if not activated(assembly_path.resolve().parents[2], floor):
        raise ValueError("TMUX-PROFILE: floorplan activation missing")
    board = p.LoadBoard(str(board_path))
    pro_path = board_path.with_suffix(".kicad_pro")
    if not pro_path.is_file():
        raise ValueError("TMUX-PROFILE: generated .kicad_pro is missing")
    # pcbnew.SaveBoard can replace generated netclasses with the board's
    # in-memory defaults. Preserve the generic emitter's exact project JSON.
    project_text = pro_path.read_text()
    project = json.loads(project_text)
    incoming = project.get("board", {}).get("design_settings", {}).get("rules", {})
    expected = {"min_clearance": ABSOLUTE_FLOORS["min_clearance"],
                "min_via_diameter": ABSOLUTE_FLOORS["via_min_size"],
                "min_via_annular_width": ABSOLUTE_FLOORS["via_min_annulus"],
                "min_hole_clearance": ABSOLUTE_FLOORS["hole_clearance"]}
    if any(incoming.get(key) != value for key, value in expected.items()):
        raise ValueError("TMUX-PROFILE: expected exact advanced absolute board floors")
    classes = project.get("net_settings", {}).get("classes", [])
    if not classes or any(float(row.get("clearance", 0)) < .15 for row in classes):
        raise ValueError("TMUX-PROFILE: ordinary netclass clearance below 0.15")
    failures = audit(board, profile, part, require_areas=False, require_vias=False)
    if failures:
        raise ValueError("\n".join(failures))
    existing = [z for z in board.Zones() if z.GetIsRuleArea()
                and z.GetZoneName().startswith(AREA_PREFIX)]
    if existing:
        # A replay must never silently repair a widened or moved exemption.
        failures = audit(board, profile, part, require_vias=False)
        if failures:
            raise ValueError("\n".join(failures))
    else:
        bounds = {ref: area_bounds(pad) for ref, pad in center_pads(board, part, []).items()}
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
            x0,y0,x1,y1 = bounds[ref]
            z.Outline().NewOutline()
            for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)):
                z.Outline().Append(p.VECTOR2I_MM(x,y))
            board.Add(z)
        p.SaveBoard(str(board_path), board)

    # pcbnew.SaveBoard may rewrite project netclasses. Restore the complete
    # generic project; exact ordinary constraints live in classes/custom rules.
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
