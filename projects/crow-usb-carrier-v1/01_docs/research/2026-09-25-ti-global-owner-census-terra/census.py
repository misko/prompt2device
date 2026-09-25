#!/usr/bin/env python3
"""Hash-bound full-envelope census for the 15-part TI floorplan experiment.

Run from any directory: python3 census.py
It writes receipt.json beside this file.  This is a diagnostic only: it makes
no routing, DRC, P1, or P2 acceptance claim.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SCRIPTS = ROOT / "skills" / "kicad-pcb" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import pcbnew  # noqa: E402
import p1_corridor_capacity as checker  # noqa: E402

BOARD = ROOT / "projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb"
FLOORPLAN = ROOT / "projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol/floorplan.yaml"
PLAN = ROOT / "projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol/modular_plan.json"
EXPECTED_BOARD_SHA256 = "d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7"
FIXED = {*(f"J{i}" for i in range(1, 9)), "J_PWR", "J_USB", "J_JTAG", *(f"C_HOLD{i}" for i in range(1, 17))}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def overlaps(a, b) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def contains(outer, inner) -> bool:
    return outer[0] <= inner[0] and outer[1] <= inner[1] and outer[2] >= inner[2] and outer[3] >= inner[3]


def native_body(fp):
    return checker.box_mm(fp.GetBoundingBox(False, False))


def issue_row(ref, owner, env, pads, regions):
    primary = regions[owner]
    foreign = [name for name, box in sorted(regions.items()) if name != owner and (overlaps(env, box) or any(overlaps(p, box) for p in pads))]
    return {
        "ref": ref,
        "owner": owner,
        "envelope_mm": env,
        "envelope_in_primary_region": contains(primary, env),
        "all_pads_in_primary_region": all(contains(primary, pad) for pad in pads),
        "foreign_planning_regions": foreign,
    }


def main() -> None:
    if digest(BOARD) != EXPECTED_BOARD_SHA256:
        raise SystemExit(f"board SHA changed: {digest(BOARD)}")
    floorplan = yaml.safe_load(FLOORPLAN.read_text())
    modular = json.loads(PLAN.read_text())
    regions = {name: tuple(value) for name, value in floorplan["placement"]["regions"].items()}
    owner = {ref: block["id"] for block in modular["blocks"] for ref in block["refs"]}
    board = pcbnew.LoadBoard(str(BOARD))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    if set(owner) != set(fps):
        raise SystemExit("module/board reference set differs")
    if not FIXED <= set(fps):
        raise SystemExit("fixed reference set differs")

    data = {}
    outside, foreign_rows = [], []
    pair_refs = defaultdict(list)
    owner_outside = Counter()
    for ref, fp in sorted(fps.items()):
        env = checker._physical_envelope(fp)
        pads = [checker.box_mm(pad.GetBoundingBox()) for pad in fp.Pads()]
        row = issue_row(ref, owner[ref], env, pads, regions)
        data[ref] = {**row, "body_mm": native_body(fp), "pad_boxes_mm": pads}
        if not row["envelope_in_primary_region"] or not row["all_pads_in_primary_region"]:
            outside.append(row)
            owner_outside[owner[ref]] += 1
        for foreign in row["foreign_planning_regions"]:
            foreign_rows.append({"ref": ref, "owner": owner[ref], "foreign_region": foreign})
            pair_refs[(owner[ref], foreign)].append(ref)

    collision_rows = []
    refs = sorted(fps)
    for index, left in enumerate(refs):
        for right in refs[index + 1:]:
            if owner[left] == owner[right]:
                continue
            l, r = data[left], data[right]
            full = overlaps(l["envelope_mm"], r["envelope_mm"])
            body = overlaps(l["body_mm"], r["body_mm"])
            pad_pad = any(overlaps(a, b) for a in l["pad_boxes_mm"] for b in r["pad_boxes_mm"])
            env_pad = any(overlaps(l["envelope_mm"], b) for b in r["pad_boxes_mm"]) or any(overlaps(r["envelope_mm"], a) for a in l["pad_boxes_mm"])
            if full or body or pad_pad or env_pad:
                collision_rows.append({"refs": [left, right], "owners": [owner[left], owner[right]], "full_envelope_overlap": full, "body_overlap": body, "pad_to_pad_overlap": pad_pad, "envelope_to_pad_overlap": env_pad})

    fixed_issues = [data[ref] for ref in sorted(FIXED) if (not data[ref]["envelope_in_primary_region"] or not data[ref]["all_pads_in_primary_region"] or data[ref]["foreign_planning_regions"])]
    receipt = {
        "purpose": "Research-only source-authority census; no P1/P2 or route/return credit.",
        "inputs": {"board": str(BOARD.relative_to(ROOT)), "board_sha256": digest(BOARD), "floorplan": str(FLOORPLAN.relative_to(ROOT)), "floorplan_sha256": digest(FLOORPLAN), "modular_plan": str(PLAN.relative_to(ROOT)), "modular_plan_sha256": digest(PLAN), "checker": str((SCRIPTS / "p1_corridor_capacity.py").relative_to(ROOT)), "checker_sha256": digest(SCRIPTS / "p1_corridor_capacity.py")},
        "semantics": {"full_envelope": "checker._physical_envelope: body plus courtyard, excluding movable reference/value text", "pads": "native pad bounding boxes", "planning_overlap": "positive-area envelope-or-pad intersection with a source region", "outside_owner": "full envelope or any pad is outside the functional owner's primary source region"},
        "counts": {"board_footprints": len(fps), "module_refs": len(owner), "fixed_refs": len(FIXED), "fully_owner_contained": len(fps) - len(outside), "outside_owner": len(outside), "foreign_planning_refs": len({x["ref"] for x in foreign_rows}), "foreign_planning_incidences": len(foreign_rows), "cross_owner_native_interaction_pairs": len(collision_rows), "cross_owner_body_overlap_pairs": sum(x["body_overlap"] for x in collision_rows), "cross_owner_pad_overlap_pairs": sum(x["pad_to_pad_overlap"] for x in collision_rows)},
        "outside_by_owner": dict(owner_outside.most_common()),
        "top_foreign_planning_clusters": [{"owner": a, "foreign_region": b, "count": len(rs), "refs": sorted(rs)} for (a, b), rs in sorted(pair_refs.items(), key=lambda x: (-len(x[1]), x[0]))],
        "outside_owner_refs": outside,
        "fixed_ref_issues": fixed_issues,
        "cross_owner_native_interactions": collision_rows,
        "exclusive_rectangular_physical_cell_result": {"source_only_feasible": False, "reason": "C_IN3 and Q_PRE have a positive-area cross-owner checker full-envelope intersection. A physical cell must contain each assigned full envelope and cannot contain a foreign native footprint/pad, so two exclusive rectangles cannot satisfy current checker semantics without moving or reassigning a footprint.", "qualification": "This particular intersection is courtyard-only: body_overlap=false and pad_to_pad_overlap=false. It is nevertheless a checker-native envelope conflict, not text-only debt."},
    }
    (HERE / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
