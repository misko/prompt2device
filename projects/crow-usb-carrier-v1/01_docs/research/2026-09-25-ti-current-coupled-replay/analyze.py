#!/usr/bin/env python3
"""Compare exact current-source TI boards with native geometry checks."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

import pcbnew as pcb
import yaml

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
RESEARCH = PROJECT / "01_docs/research"
BASE = PROJECT / "06_build/prototype_board_diagnostic/current-ti-baseline-final-20260925"
TRIAL = PROJECT / "06_build/prototype_board_diagnostic/current-ti-coupled-replay-20260925"
EXPECTED = {
    "base": "c5229350807edd85ce95eadd4ec8e4190941b0dd27edcf0a54a6defda145e6b8",
    "trial": "bdd5bccb2617d7bbe1de9cd27cda1a0e2f68467bedd169704473a010286a948b",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def census(census_module, board: Path, floorplan: Path, plan: Path) -> dict:
    census_module.BOARD = board
    census_module.EXPECTED_BOARD_SHA256 = sha(board)
    census_module.FLOORPLAN = floorplan
    census_module.PLAN = plan
    with tempfile.TemporaryDirectory(prefix="crow-current-owner-census-") as tmp:
        census_module.HERE = Path(tmp)
        census_module.main()
        return json.loads((Path(tmp) / "receipt.json").read_text())


def observed(screen, footprints: dict) -> list:
    rows = []
    for ref, fp in footprints.items():
        courtyard = fp.GetCourtyard(pcb.F_CrtYd)
        box = courtyard.BBox() if courtyard.OutlineCount() else fp.GetBoundingBox(False, False)
        rows.append((ref + ":native", screen.bbox(box)))
        for pad in fp.Pads():
            if pad.IsOnLayer(pcb.F_Cu):
                rows.append((ref + ":pad" + pad.GetNumber(), screen.bbox(pad.GetBoundingBox())))
    return rows


def main() -> None:
    old_board = BASE / "project/04_kicad/crow_carrier.kicad_pcb"
    new_board = TRIAL / "project/04_kicad/crow_carrier.kicad_pcb"
    if {"base": sha(old_board), "trial": sha(new_board)} != EXPECTED:
        raise RuntimeError("current-source board subject changed")
    old = pcb.LoadBoard(str(old_board))
    new = pcb.LoadBoard(str(new_board))
    old_fp = {fp.GetReference(): fp for fp in old.GetFootprints()}
    new_fp = {fp.GetReference(): fp for fp in new.GetFootprints()}
    if len(old_fp) != 569 or set(old_fp) != set(new_fp):
        raise RuntimeError("569-ref comparison denominator changed")
    prior = module("prior_ti_analysis", RESEARCH / "2026-09-25-ti-integrated-placement-sol/analyze.py")
    moves = json.loads((RESEARCH / "2026-09-25-ti-integrated-placement-sol/expected_poses.json").read_text())["move_union"]
    changed = {ref for ref in old_fp if prior.pose(old_fp[ref]) != prior.pose(new_fp[ref])}
    if changed != set(moves) or any(prior.pose(new_fp[ref]) != list(target)
                                    for ref, target in moves.items()):
        raise RuntimeError("native pose delta differs from 45 reviewed research targets")
    fixed = yaml.safe_load((PROJECT / "03_src/rules/p1_corridor_requirements.yaml").read_text())["p1_fixed_refs"]
    if len(fixed) != 27 or any(ref in changed for ref in fixed):
        raise RuntimeError("P1-fixed pose changed")
    if any(prior.sig(old, old_fp[ref]) != prior.sig(new, new_fp[ref]) for ref in old_fp):
        raise RuntimeError("native pad identity or relative geometry changed")
    screen = module("current_mouth_screen", RESEARCH / "2026-09-25-ti-timing-mouth-screen-sol/build_screen.py")
    portal = [166, 83.9, 167.12, 85]
    results = {}
    for name, footprints in (("baseline", old_fp), ("trial", new_fp)):
        rows = observed(screen, footprints)
        results[name] = {
            "adc7_portal_hits": [ref for ref, box in rows if screen.intersects(portal, box)],
            "rough_timing_slots": {key: screen.mouth_screen(box, axis, rows)["raw_slots"]
                                   for key, (box, axis, _demand) in prior.MOUTHS.items()},
        }
    if results["trial"]["adc7_portal_hits"] or len(results["baseline"]["adc7_portal_hits"]) != 2:
        raise RuntimeError("ADC7 portal observation changed")
    floorplan = PROJECT / "03_src/floorplan.yaml"
    plan = PROJECT / "03_src/modular_plan.json"
    census_module = module("current_owner_census", RESEARCH / "2026-09-25-ti-global-owner-census-terra/census.py")
    before = census(census_module, old_board, floorplan, plan)
    after = census(census_module, new_board, floorplan, plan)
    if before["cross_owner_native_interactions"] or after["cross_owner_native_interactions"]:
        raise RuntimeError("cross-owner native interaction introduced")
    old_drc = json.loads((BASE / "drc.json").read_text())
    new_drc = json.loads((TRIAL / "drc.json").read_text())
    for report in (old_drc, new_drc):
        if report.get("violations") or len(report.get("unconnected_items", [])) != 499 or report.get("schematic_parity"):
            raise RuntimeError("native DRC/parity comparison changed")
    comparison = {
        "schema": 1, "status": "RESEARCH_IMPROVEMENT_NO_ENGINEERING_CREDIT",
        "board_sha256": EXPECTED, "pose_changes": len(changed), "fixed_refs_unchanged": len(fixed),
        "pad_identity_and_local_geometry_preserved": True,
        "baseline": {**results["baseline"], "owner_counts": before["counts"]},
        "trial": {**results["trial"], "owner_counts": after["counts"]},
        "native_drc": {"violations": [0, 0], "unconnected": [499, 499],
                       "schematic_parity": [0, 0]},
        "p1_accepted": False, "p2_accepted": False, "route_credit": False,
        "return_credit": False, "release_admitted": False,
        "input_sha256": {"current_floorplan": sha(floorplan), "modular_plan": sha(plan),
                         "pose_targets": sha(RESEARCH / "2026-09-25-ti-integrated-placement-sol/expected_poses.json"),
                         "native_census": sha(RESEARCH / "2026-09-25-ti-global-owner-census-terra/census.py"),
                         "mouth_screen": sha(RESEARCH / "2026-09-25-ti-timing-mouth-screen-sol/build_screen.py")},
    }
    (HERE / "comparison.json").write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n")
    print(json.dumps(comparison, sort_keys=True))


if __name__ == "__main__":
    main()
