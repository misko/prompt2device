#!/usr/bin/env python3
"""Grade selective IPC-4761 via intent against the exact KiCad board.

    /usr/bin/python3 via_process_check.py BOARD.kicad_pcb
        [--assembly 03_src/rules/assembly.yaml] [--json OUT]

KiCad can store capping/filling per via, but a Gerber order does not carry
those native item attributes.  A selective process therefore needs a
fabricator-visible selector.  This gate uses the drill family declared in
``assembly.yaml`` and proves both directions:

* every protected drill is Type VII filled+capped at a declared geometry;
* every ordinary drill is unprotected and belongs to the declared ordinary
  family.

The optional protected_geometries list permits multiple copper diameters in
one selected drill family (Crow's LT3045 plus TMUX4827 consumer).  The legacy
protected_geometry mapping remains valid.  The order remark is also graded
because it is the instruction the fabricator actually receives.  DRC cannot
establish any of these manufacturing facts.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import pcbnew
from tmux4827_pofv import (ABSOLUTE_FLOORS, activated as tmux_activated,
                           audit as audit_tmux, contract as tmux_contract,
                           dru_rules as tmux_dru_rules, REFS as TMUX_REFS)

try:
    import yaml
except ImportError:
    sys.exit("V-PROCESS: PyYAML is required")


TOL_MM = 0.0015


def intrinsic_pad_dru_rules(assembly_path: Path) -> list[str]:
    """Return only source-declared, non-relaxing intrinsic pad rules.

    The TMUX profile owns every clearance rule below the ordinary 0.15-mm
    floor.  `generate_rules_generic.py` may additionally emit a 0.15-mm
    package-land rule, but accept it here only when the exact bytes can be
    re-derived from the current project's `nets.yaml`.  A hand-appended rule,
    altered predicate, unknown reference, missing provenance, or sub-0.15
    value remains in the residual and fails closed below.
    """
    root = assembly_path.resolve().parents[2]
    path = root / "03_src" / "rules" / "nets.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    specs = data.get("same_footprint_pad_clearances") or []
    if not isinstance(specs, list):
        raise ValueError("TMUX-DRU: same_footprint_pad_clearances must be a list")
    out, seen = [], set()
    for i, spec in enumerate(specs):
        if not isinstance(spec, dict):
            raise ValueError(f"TMUX-DRU: intrinsic source entry {i} is not a mapping")
        ident = str(spec.get("id") or "").strip()
        refs = spec.get("refs")
        if (not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", ident)
                or not isinstance(refs, list) or not refs
                or any(not isinstance(ref, str)
                       or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", ref)
                       for ref in refs)):
            raise ValueError(f"TMUX-DRU: intrinsic source entry {i} has invalid id/refs")
        if not str(spec.get("evidence") or "").strip() or not str(spec.get("why") or "").strip():
            raise ValueError(f"TMUX-DRU: intrinsic source entry {i} lacks evidence/why")
        try:
            clearance = float(str(spec.get("clearance") or "").lower().replace("mm", "").strip())
        except ValueError as exc:
            raise ValueError(f"TMUX-DRU: intrinsic source entry {i} has invalid clearance") from exc
        if not math.isfinite(clearance) or clearance < .15:
            raise ValueError(f"TMUX-DRU: intrinsic source entry {i} clearance below 0.15mm")
        for ref in refs:
            name = f"intrinsic_pad_clr_{ident}_{ref}"
            if ref in seen:
                raise ValueError(f"TMUX-DRU: duplicate intrinsic source reference {ref}")
            seen.add(ref)
            condition = ("A.Type == 'Pad' && B.Type == 'Pad' && "
                         f"A.memberOfFootprint('{ref}') && B.memberOfFootprint('{ref}')")
            out.append(f'(rule "{name}"\n'
                       f'  (condition "{condition}")\n'
                       f'  (constraint clearance (min {round(clearance, 3)}mm)))')
    return out


def pair_scoped_dru_rules(assembly_path: Path, board, floor: dict) -> list[str]:
    """Re-derive only exact, F.Cu pair rules that cannot match a TMUX pad.

    This is intentionally narrower than the generic rule generator.  Its
    legacy one-sided `nets` scope and its hole-clearance feature remain foreign
    to the TMUX process guard.  Both the copied source and the native area are
    checked before removing any rule text from the foreign-constraint scan.
    """
    root = assembly_path.resolve().parents[2]
    data = yaml.safe_load((root / "03_src/rules/nets.yaml").read_text(encoding="utf-8-sig")) or {}
    specs = data.get("scoped_clearances") or []
    if not isinstance(specs, list):
        raise ValueError("TMUX-DRU: scoped_clearances must be a list")
    areas = floor.get("keepouts") or []
    if not isinstance(areas, list):
        raise ValueError("TMUX-DRU: floorplan keepouts must be a list")
    tmux_nets = {pad.GetNetname() for fp in board.GetFootprints()
                 if fp.GetReference() in TMUX_REFS for pad in fp.Pads()}
    if not tmux_nets or "GND" not in tmux_nets:
        raise ValueError("TMUX-DRU: native TMUX pad net census unavailable")
    out, seen = [], set()
    for i, spec in enumerate(specs):
        if not isinstance(spec, dict):
            raise ValueError(f"TMUX-DRU: scoped source entry {i} is not a mapping")
        if not (spec.get("nets_a") or spec.get("nets_b")):
            continue  # Legacy/wide rules remain in the residual foreign scan.
        if (set(spec) != {"zone", "nets_a", "nets_b", "clearance", "why"}
                or not str(spec["why"]).strip()):
            raise ValueError(f"TMUX-DRU: pair source entry {i} has extra/missing fields")
        zone = spec["zone"]
        a, b = spec["nets_a"], spec["nets_b"]
        valid = lambda name: isinstance(name, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name)
        if (not valid(zone) or zone in seen or not isinstance(a, list) or not isinstance(b, list)
                or len(a) != 1 or len(b) != 1 or not all(valid(n) for n in a + b)
                or len(set(a + b)) != len(a + b) or set(a + b) & tmux_nets):
            raise ValueError(f"TMUX-DRU: pair source entry {i} widens selector or reaches TMUX nets")
        seen.add(zone)
        matches = [item for item in areas if isinstance(item, dict) and item.get("name") == zone]
        if len(matches) != 1 or set(matches[0]) != {"name", "layers", "deny", "rect"} or \
                matches[0]["layers"] != ["F.Cu"] or matches[0]["deny"] != []:
            raise ValueError(f"TMUX-DRU: pair area {zone} is not one permissive F.Cu area")
        rect = matches[0]["rect"]
        if (not isinstance(rect, list) or len(rect) != 4
                or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in rect)
                or rect[0] >= rect[2] or rect[1] >= rect[3]):
            raise ValueError(f"TMUX-DRU: pair area {zone} has invalid bounds")
        native = [z for z in board.Zones() if z.GetZoneName() == zone]
        if len(native) != 1 or not native[0].GetIsRuleArea() or \
                [board.GetLayerName(layer) for layer in native[0].GetLayerSet().Seq()] != ["F.Cu"] or \
                any((native[0].GetDoNotAllowTracks(), native[0].GetDoNotAllowVias(),
                     native[0].GetDoNotAllowPads(), native[0].GetDoNotAllowFootprints(),
                     native[0].GetDoNotAllowZoneFills())):
            raise ValueError(f"TMUX-DRU: native pair area {zone} differs")
        box = native[0].GetBoundingBox()
        if [box.GetLeft(), box.GetTop(), box.GetRight(), box.GetBottom()] != \
                [pcbnew.FromMM(value) for value in rect]:
            raise ValueError(f"TMUX-DRU: native pair area {zone} bounds drift")
        try:
            clearance = round(float(str(spec["clearance"]).lower().replace("mm", "").strip()), 3)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"TMUX-DRU: pair source entry {i} clearance invalid") from exc
        if not math.isfinite(clearance) or clearance < ABSOLUTE_FLOORS["min_clearance"]:
            raise ValueError(f"TMUX-DRU: pair source entry {i} below absolute floor")
        a_on_a = " || ".join(f"A.NetName == '{n}'" for n in a)
        b_on_b = " || ".join(f"B.NetName == '{n}'" for n in b)
        a_on_b = " || ".join(f"A.NetName == '{n}'" for n in b)
        b_on_a = " || ".join(f"B.NetName == '{n}'" for n in a)
        clause = f"(({a_on_a}) && ({b_on_b})) || (({a_on_b}) && ({b_on_a}))"
        condition = f"A.insideArea('{zone}') && B.insideArea('{zone}') && ({clause})"
        out.append(f'(rule "scoped_clr_{zone}"\n'
                   f'  (condition "{condition}")\n'
                   f'  (constraint clearance (min {clearance}mm)))')
    return out


def audit_dru_constraints(actual: str, expected: list[str], intrinsic: list[str],
                          pair_scoped: list[str]) -> list[str]:
    """Keep the historical foreign-constraint veto after exact rule removal."""
    fails = []
    residual = actual
    for rule in expected:
        if actual.count("\n" + rule) != 1 or actual.count(rule) != 1:
            fails.append("TMUX-DRU: missing or altered generated rule " + rule.split('"')[1])
        residual = residual.replace(rule, "", 1)
    for rule in intrinsic:
        count = actual.count(rule)
        if count == 0:
            continue  # Existing boards may omit this optional generic feature.
        if actual.count("\n" + rule) != 1 or count != 1:
            fails.append("TMUX-DRU: missing or altered intrinsic rule " + rule.split('"')[1])
            continue
        residual = residual.replace(rule, "", 1)
    for rule in pair_scoped:
        if actual.count("\n" + rule) != 1 or actual.count(rule) != 1:
            fails.append("TMUX-DRU: missing or altered exact pair rule " + rule.split('"')[1])
            continue
        residual = residual.replace(rule, "", 1)
    if re.search(r"\(\s*constraint\s+(?:clearance|physical_clearance|via_diameter|annular_width|hole_size|hole_clearance)\b", residual):
        fails.append("TMUX-DRU: foreign clearance/via/hole constraint")
    return fails


def find_assembly(board_path: Path, explicit: str | None = None):
    if explicit:
        path = Path(explicit).resolve()
        return path
    board_path = board_path.resolve()
    for anc in [board_path.parent, *board_path.parents]:
        candidate = anc / "03_src" / "rules" / "assembly.yaml"
        if candidate.is_file():
            return candidate
    return None


def load_assembly(board_path: Path, explicit: str | None = None):
    path = find_assembly(board_path, explicit)
    if path is None or not path.is_file():
        return {}, path
    data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top level must be a mapping")
    return data, path


def _via_counts(board):
    protected = ordinary = partial = 0
    for item in board.GetTracks():
        if item.GetClass() != "PCB_VIA":
            continue
        capped = item.GetCappingMode() == pcbnew.CAPPING_MODE_CAPPED
        filled = item.GetFillingMode() == pcbnew.FILLING_MODE_FILLED
        if capped != filled:
            partial += 1
        elif capped:
            protected += 1
        else:
            ordinary += 1
    return protected, ordinary, partial, len(via_in_pad_hits(board))


def via_order_note(data: dict, source: Path | None = None,
                   board=None) -> str | None:
    process = data.get("via_process")
    if not isinstance(process, dict):
        return None
    remark = str(process.get("order_remark") or "").strip()
    if not remark:
        return None
    origin = source.as_posix() if source else "assembly.yaml"
    confirm = bool(process.get("uploader_confirmation_required"))
    census = ""
    if board is not None:
        protected, ordinary, partial, vip = _via_counts(board)
        census = (f"\nExact board census: {protected} protected, {ordinary} "
                  f"ordinary, {partial} partial; {vip} via-in-pad sites.")
    return (
        "JLCPCB VIA PROCESS — GENERATED; DO NOT RE-TYPE\n"
        f"Source: {origin}\n"
        f"Order remark: {remark}{census}\n"
        "Uploader confirmation required: " + ("YES" if confirm else "NO")
        + "\n"
    )


def close(a, b):
    return abs(float(a) - float(b)) <= TOL_MM


def via_in_pad_hits(board):
    """Map via UUIDs to exact undrilled component lands containing them.

    Same-net via/pad overlap is intentionally DRC-clean, but an open barrel
    beneath an SMT paste aperture is not assembly-neutral.  Use KiCad's exact
    pad hit-test rather than a rectangular approximation and require every
    such barrel to belong to the declared filled/capped process.
    """
    copper_layers = [layer for layer in board.GetEnabledLayers().Seq()
                     if pcbnew.IsCopperLayer(layer)]
    pads = []
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            if (pad.GetDrillSize().x > 0
                    or not any(pad.IsOnLayer(layer)
                               for layer in copper_layers)):
                continue
            pads.append((footprint.GetReference(), pad,
                         pad.GetBoundingBox()))
    out = {}
    for via in board.GetTracks():
        if via.GetClass() != "PCB_VIA":
            continue
        pos = via.GetPosition()
        hits = [f"{ref}.{pad.GetNumber()}"
                for ref, pad, bbox in pads
                if bbox.Contains(pos) and pad.HitTest(pos)]
        if hits:
            out[via.m_Uuid.AsString()] = hits
    return out


def _mm(value, path, fails):
    if isinstance(value, bool):
        fails.append(f"V-SCHEMA {path}: expected a number, got {value!r}")
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        fails.append(f"V-SCHEMA {path}: expected a number, got {value!r}")
        return None
    if not math.isfinite(value) or value <= 0:
        fails.append(f"V-SCHEMA {path}: must be finite and positive, got {value}")
        return None
    return value


def check(board_path: Path, assembly: str | None = None):
    data, apath = load_assembly(board_path, assembly)
    board = pcbnew.LoadBoard(str(board_path))
    vip_hits = via_in_pad_hits(board)
    protected_without_contract = [
        item for item in board.GetTracks()
        if item.GetClass() == "PCB_VIA"
        and (item.GetCappingMode() == pcbnew.CAPPING_MODE_CAPPED
             or item.GetFillingMode() == pcbnew.FILLING_MODE_FILLED)
    ]
    out = {
        "board": str(board_path), "assembly": str(apath) if apath else None,
        "fails": [], "oks": [], "coverage": {}, "na": None, "census": {},
    }
    vp = data.get("via_process")
    if vp is None:
        if vip_hits or protected_without_contract:
            out["fails"].append(
                "V-SCHEMA assembly.yaml declares no via_process although "
                f"the board has {len(vip_hits)} via-in-pad site(s) and "
                f"{len(protected_without_contract)} via(s) carrying native "
                "fill/cap flags")
        else:
            out["na"] = "V-PROCESS N-A: assembly.yaml declares no via_process"
        return out
    if not isinstance(vp, dict):
        out["fails"].append("V-SCHEMA via_process: expected a mapping")
        return out

    try:
        tmux = tmux_contract(data, apath)
        if tmux is not None:
            profile, part, _ = tmux
            floor = yaml.safe_load((apath.resolve().parents[1] / "floorplan.yaml").read_text()) or {}
            tmux_activated(apath.resolve().parents[2], floor)
            out["fails"].extend(audit_tmux(board, profile, part))
            pro = board_path.with_suffix(".kicad_pro")
            project = json.loads(pro.read_text()) if pro.is_file() else {}
            physical = project.get("board", {}).get("design_settings", {}).get("rules", {})
            absolute = {"min_clearance": ABSOLUTE_FLOORS["min_clearance"],
                        "min_via_diameter": ABSOLUTE_FLOORS["via_min_size"],
                        "min_via_annular_width": ABSOLUTE_FLOORS["via_min_annulus"],
                        "min_hole_clearance": ABSOLUTE_FLOORS["hole_clearance"]}
            if any(physical.get(key) != value for key, value in absolute.items()):
                out["fails"].append("TMUX-PRO: advanced absolute floors are missing or stale")
            classes = project.get("net_settings", {}).get("classes", [])
            if not classes or any(float(row.get("clearance", 0)) < .15 for row in classes):
                out["fails"].append("TMUX-PRO: ordinary netclass clearance below 0.15")
            # The exact source-owned rules are required after the generic
            # generator.  Foreign relaxed rules could otherwise mask a DRC
            # error while the identity checker still passes.
            dru = board_path.with_suffix(".kicad_dru")
            actual = dru.read_text() if dru.is_file() else ""
            # Exact source/native-bound pair rules may join the existing TMUX
            # and intrinsic rules; every other clearance still fails closed.
            out["fails"].extend(audit_dru_constraints(
                actual, tmux_dru_rules(), intrinsic_pad_dru_rules(apath),
                pair_scoped_dru_rules(apath, board, floor)))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        out["fails"].append(f"TMUX-PROFILE: {exc}")

    # A single drill family may contain more than one approved copper diameter.
    # Keep the legacy singular key for existing boards; reject an ambiguous mix.
    singular = vp.get("protected_geometry")
    plural = vp.get("protected_geometries")
    selector = vp.get("fabricator_selector")
    has_singular = "protected_geometry" in vp
    has_plural = "protected_geometries" in vp
    if has_singular and has_plural:
        out["fails"].append(
            "V-SCHEMA use protected_geometry or protected_geometries, not both")
    if has_plural:
        if not isinstance(plural, list) or not plural:
            out["fails"].append(
                "V-SCHEMA via_process.protected_geometries: expected a non-empty list")
            raw_geoms = []
        else:
            raw_geoms = plural
    else:
        if not isinstance(singular, dict):
            out["fails"].append(
                "V-SCHEMA via_process.protected_geometry: expected a mapping")
            singular = {}
        raw_geoms = [singular]
    if not isinstance(selector, dict):
        out["fails"].append(
            "V-SCHEMA via_process.fabricator_selector: expected a mapping")
        selector = {}

    geoms = []
    for i, geom in enumerate(raw_geoms):
        path = (f"via_process.protected_geometries[{i}]" if has_plural
                else "via_process.protected_geometry")
        if not isinstance(geom, dict):
            out["fails"].append(f"V-SCHEMA {path}: expected a mapping")
            continue
        size = _mm(geom.get("via_diameter_mm"), f"{path}.via_diameter_mm",
                   out["fails"])
        drill = _mm(geom.get("drill_mm"), f"{path}.drill_mm",
                    out["fails"])
        if size is not None and drill is not None:
            if size <= drill:
                out["fails"].append(
                    f"V-SCHEMA {path}: via diameter must exceed drill")
            if any(close(size, prior_size) and close(drill, prior_drill)
                   for prior_size, prior_drill in geoms):
                out["fails"].append(
                    f"V-SCHEMA {path}: duplicate protected geometry")
            geoms.append((size, drill))
    kind = selector.get("kind")
    if kind != "drill_family":
        out["fails"].append(
            "V-SCHEMA via_process.fabricator_selector.kind: must be "
            "'drill_family' because Gerber order remarks cannot select native "
            "KiCad per-via flags")
    protected_drill = _mm(
        selector.get("protected_drill_mm"),
        "via_process.fabricator_selector.protected_drill_mm", out["fails"])
    ordinary = selector.get("ordinary_drill_mm")
    if not isinstance(ordinary, list) or not ordinary:
        out["fails"].append(
            "V-SCHEMA via_process.fabricator_selector.ordinary_drill_mm: "
            "expected a non-empty list")
        ordinary_drills = []
    else:
        ordinary_drills = [
            value for i, raw in enumerate(ordinary)
            if (value := _mm(
                raw,
                f"via_process.fabricator_selector.ordinary_drill_mm[{i}]",
                out["fails"])) is not None
        ]
    for _, drill in geoms:
        if protected_drill is not None and not close(drill, protected_drill):
            out["fails"].append(
                f"V-SCHEMA protected geometry drill {drill:g}mm disagrees with "
                f"fabricator selector {protected_drill:g}mm")
    if protected_drill is not None and any(
            close(protected_drill, value) for value in ordinary_drills):
        out["fails"].append(
            "V-SCHEMA protected and ordinary drill families overlap")

    remark = str(vp.get("order_remark") or "").strip()
    if not remark:
        out["fails"].append("V-ORDER via_process.order_remark is missing")
    else:
        low = remark.lower()
        for word in ("fill", "cap"):
            if word not in low:
                out["fails"].append(
                    f"V-ORDER order_remark does not name {word!r}")
        if protected_drill is not None and f"{protected_drill:.2f}" not in remark:
            out["fails"].append(
                f"V-ORDER order_remark does not name protected "
                f"{protected_drill:.2f} mm drill family")
        for value in ordinary_drills:
            if f"{value:.2f}" not in remark:
                out["fails"].append(
                    f"V-ORDER order_remark does not name ordinary "
                    f"{value:.2f} mm drill family")
    if vp.get("uploader_confirmation_required") is not True:
        out["fails"].append(
            "V-ORDER uploader_confirmation_required must be true for a "
            "selective via process")

    protected = ordinary_count = partial = 0
    census = {}
    for item in board.GetTracks():
        if item.GetClass() != "PCB_VIA":
            continue
        diameter = pcbnew.ToMM(item.GetWidth(pcbnew.F_Cu))
        hole = pcbnew.ToMM(item.GetDrill())
        capped = item.GetCappingMode() == pcbnew.CAPPING_MODE_CAPPED
        filled = item.GetFillingMode() == pcbnew.FILLING_MODE_FILLED
        key = f"{diameter:.3f}/{hole:.3f};cap={int(capped)};fill={int(filled)}"
        census[key] = census.get(key, 0) + 1
        pos = item.GetPosition()
        where = (f"{item.GetNetname() or '(no net)'} at "
                 f"({pcbnew.ToMM(pos.x):.3f},{pcbnew.ToMM(pos.y):.3f})")
        pads = vip_hits.get(item.m_Uuid.AsString(), [])
        if pads and not (capped and filled):
            out["fails"].append(
                f"V-VIP {where}: ordinary/unprotected via is centred in "
                f"SMT land(s) {', '.join(pads)}; declare and realize a "
                "filled+capped process or move the via")
        if capped != filled:
            partial += 1
            out["fails"].append(
                f"V-FLAGS {where}: partial Type-VII state "
                f"cap={int(capped)} fill={int(filled)}")
            continue
        if capped and filled:
            protected += 1
            if geoms and not any(close(diameter, size) and close(hole, drill)
                                 for size, drill in geoms):
                expected = " or ".join(
                    f"{size:.3f}/{drill:.3f}mm" for size, drill in geoms)
                out["fails"].append(
                    f"V-GEOM {where}: protected via is "
                    f"{diameter:.3f}/{hole:.3f}mm, expected "
                    f"{expected}")
            if protected_drill is not None and not close(hole, protected_drill):
                out["fails"].append(
                    f"V-SELECT {where}: protected via is outside the "
                    f"{protected_drill:.3f}mm drill family")
        else:
            ordinary_count += 1
            if protected_drill is not None and close(hole, protected_drill):
                out["fails"].append(
                    f"V-SELECT {where}: ordinary via shares protected "
                    f"{protected_drill:.3f}mm drill family")
            elif ordinary_drills and not any(close(hole, x) for x in ordinary_drills):
                out["fails"].append(
                    f"V-SELECT {where}: ordinary {hole:.3f}mm drill is not in "
                    f"declared families {ordinary_drills}")

    total = protected + ordinary_count + partial
    # Legacy prose sometimes hard-coded a prior release's census.  If it does,
    # it must agree with this exact board; otherwise a superficially complete
    # order note can send the fabricator an obsolete drill-family count.
    stated = re.search(
        r"census\s+is\s+(\d+)\s+protected.*?(\d+)\s+ordinary", remark,
        re.I | re.S)
    if stated and (int(stated.group(1)), int(stated.group(2))) != \
            (protected, ordinary_count):
        out["fails"].append(
            "V-ORDER stale hard-coded census: order_remark says "
            f"{stated.group(1)} protected / {stated.group(2)} ordinary, "
            f"exact board is {protected} / {ordinary_count}")
    out["census"] = census
    out["coverage"] = {
        "V-FLAGS": f"{total}/{total} vias graded",
        "V-SELECT": f"{total}/{total} vias compared with drill families",
        "V-VIP": f"{len(vip_hits)}/{len(vip_hits)} via-in-pad sites graded",
    }
    if total == 0:
        out["fails"].append(
            "V-COVER: via_process is declared but the exact board has 0 vias")
    if protected == 0:
        out["fails"].append(
            "V-COVER: via_process is declared but 0 protected vias were found")
    if not out["fails"]:
        out["oks"].append(
            f"V-PROCESS {protected} protected / {ordinary_count} ordinary / "
            f"{partial} partial; process families are drill-disjoint")
        out["oks"].append("V-ORDER exact generated order remark is complete")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("--assembly")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    result = check(Path(args.board), args.assembly)
    if args.json:
        json_path = Path(args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2) + "\n")
    if result.get("na"):
        print(result["na"])
        return 0
    for name, value in result["coverage"].items():
        print(f"  coverage {name}: {value}")
    for key, count in sorted(result["census"].items()):
        print(f"  census {count:3d} x {key}")
    for value in result["oks"]:
        print(f"  ok   {value}")
    for value in result["fails"]:
        print(f"  FAIL {value}")
    if result["fails"]:
        print(f"V-PROCESS FAIL: {len(result['fails'])} finding(s)")
        return 1
    print("V-PROCESS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
