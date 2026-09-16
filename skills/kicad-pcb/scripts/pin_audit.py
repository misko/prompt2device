#!/usr/bin/env python3
"""Pin-audit dossier extractor: everything a FRESH-CONTEXT reviewer needs to
verify one part's pins against the datasheet and electrical intent - and
nothing of the authors' conclusions.

Per part it emits <ref>.md containing:
  - the pad table straight from the BOARD: pad number, component-top local
    position, native board position, side, size, and the NET actually connected
  - every unnumbered paste/mechanical feature: stable dossier identity, pad
    type, shape, drill, layer mask, component-top and native board coordinates
  - mounted side and the explicit rotation/reflection used for the local frame
  - the computed pin-1 corner and winding direction (CW/CCW, top view)
  - the pin-function map from 02_parts/<MPN>/part.yaml (datasheet-sourced)
  - the datasheet path, so the reviewer can check the pinout figure directly
  - join gaps: pads missing from the yaml pin map and vice versa

It deliberately draws NO conclusions: the reviewer must independently derive
the expected winding from the datasheet package drawing and judge whether
each pin's net makes electrical sense. (A mirror-numbered footprint shipped
twice because every automated gate compared our artifacts against each other
- they were consistently wrong together. Fresh eyes break that loop.)

usage: pin_audit.py BOARD BOM_JLC_CSV PARTS_DIR OUTDIR [--refs U1,U2,...]
Default ref set: every part with more than 3 pads (ICs, FETs, connectors).

Run with the KiCad-bundled python (/usr/bin/python3).
"""
import argparse
import csv
import hashlib
import math
import re
import sys
from pathlib import Path

import pcbnew

try:
    import yaml
except ImportError:
    yaml = None


PAD_ATTRIBUTES = {
    pcbnew.PAD_ATTRIB_PTH: "PTH",
    pcbnew.PAD_ATTRIB_SMD: "SMD",
    pcbnew.PAD_ATTRIB_CONN: "connector",
    pcbnew.PAD_ATTRIB_NPTH: "NPTH",
}

PAD_SHAPES = {
    pcbnew.PAD_SHAPE_CIRCLE: "circle",
    pcbnew.PAD_SHAPE_RECT: "rectangle",
    pcbnew.PAD_SHAPE_OVAL: "oval",
    pcbnew.PAD_SHAPE_TRAPEZOID: "trapezoid",
    pcbnew.PAD_SHAPE_ROUNDRECT: "roundrect",
    pcbnew.PAD_SHAPE_CHAMFERED_RECT: "chamfered-rectangle",
    pcbnew.PAD_SHAPE_CUSTOM: "custom",
}


def local_pads(fp):
    """Component-top coordinates, +x right/+y down, without editing the board.

    KiCad's native relative position undoes board translation and rotation,
    but retains the back-mounted footprint's reflection about local x. Undo
    that y reflection ONLY when native IsFlipped() is true. This is a change
    of observation side, never a correction based on an expected pin winding;
    a physically mirrored footprint remains mirrored on either mounted side.
    """
    y_sign = -1 if fp.IsFlipped() else 1
    out = []
    for p in fp.Pads():
        n = str(p.GetNumber())
        local = p.GetFPRelativePosition()
        board_pos = p.GetPosition()
        drill = p.GetDrillSize()
        out.append({
            "num": n,
            "x": local.x / 1e6,
            "y": y_sign * local.y / 1e6,
            "board_x": board_pos.x / 1e6,
            "board_y": board_pos.y / 1e6,
            "w": round(p.GetSize(pcbnew.F_Cu).x / 1e6, 2),
            "h": round(p.GetSize(pcbnew.F_Cu).y / 1e6, 2),
            "net": p.GetNetname() or "(no net)",
            "tht": drill.x > 0,
            "kind": PAD_ATTRIBUTES.get(p.GetAttribute(), f"unknown-{p.GetAttribute()}"),
            "shape": PAD_SHAPES.get(p.GetShape(), f"unknown-{p.GetShape()}"),
            "drill_w": round(drill.x / 1e6, 2),
            "drill_h": round(drill.y / 1e6, 2),
            "layers": p.GetLayerSet().FmtHex(),
        })
    return out


def side_of(p, pads):
    xs = [q["x"] for q in pads]
    ys = [q["y"] for q in pads]
    mx, my = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    dx, dy = p["x"] - mx, p["y"] - my
    if abs(dx) < 0.3 and abs(dy) < 0.3:
        return "center"
    # KiCad frame: +y is DOWN on the top view
    return ("E" if dx > 0 else "W") if abs(dx) > abs(dy) else ("S" if dy > 0 else "N")


def winding(pads):
    """CW/CCW of numeric pin sequence around the centroid, TOP view.
    KiCad's +y-down means a mathematically-positive angle sweep is CW on
    screen; report in top-view screen terms (what a datasheet figure shows)."""
    seq = sorted((p for p in pads if p["num"].isdigit() and p["side"] != "center"),
                 key=lambda p: int(p["num"]))
    if len(seq) < 3:
        return "n/a (too few perimeter pins)"
    # Aliased composite lands are omitted upstream. The surviving pins can
    # therefore occupy one straight row, which has no winding. In that case
    # atan2's +/-pi tie would otherwise invent a direction around the row's
    # centroid. Do not infer the missing physical terminal positions.
    origin = seq[0]
    farthest = max(seq, key=lambda p: (p["x"] - origin["x"]) ** 2
                   + (p["y"] - origin["y"]) ** 2)
    dx, dy = farthest["x"] - origin["x"], farthest["y"] - origin["y"]
    tolerance = 1e-9 * max(1.0, dx * dx + dy * dy)
    if all(abs(dx * (p["y"] - origin["y"])
               - dy * (p["x"] - origin["x"])) <= tolerance for p in seq):
        return "n/a (collinear perimeter pins)"
    xs = [p["x"] for p in seq]
    ys = [p["y"] for p in seq]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    total = 0.0
    for a, b in zip(seq, seq[1:]):
        a1 = math.atan2(a["y"] - cy, a["x"] - cx)
        a2 = math.atan2(b["y"] - cy, b["x"] - cx)
        d = a2 - a1
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        total += d
    # +y down: positive accumulated angle = clockwise as drawn/viewed from top
    return "CW (top view)" if total > 0 else "CCW (top view)"


def datasheet_path(part_dir, declared):
    """Resolve the vendored PDF by its declared digest, never directory order.

    A dossier once selected the older non-automotive PDF merely because it
    sorted first beside the exact Q-grade authority. Fresh review must see
    the bytes whose digest part.yaml actually asserts. A URL, a sole PDF, or
    an adjacent family document is not review evidence: fail before dossiers
    are commissioned if the authority is absent or its bytes do not match.
    """
    want = str((declared or {}).get("sha256") or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", want):
        raise RuntimeError(
            f"P-AUTH {part_dir}: datasheet.sha256 is missing or malformed; "
            "fresh pin review requires a digest-selected local PDF")
    pdfs = sorted(part_dir.glob("*.pdf"))
    for pdf in pdfs:
        if hashlib.sha256(pdf.read_bytes()).hexdigest().lower() == want:
            return str(pdf)
    raise RuntimeError(
        f"P-AUTH {part_dir}: no local PDF matches declared SHA-256 {want}; "
        f"found {len(pdfs)} PDF(s)")


def part_authority(parts_dir, exact_mpn):
    """Return ``(part_dir, parsed_part_yaml)`` for one exact BOM MPN.

    An exact orderable MPN can contain characters that cannot safely be used
    as one directory component (for example ``MCP2221A-I/SL``), so directory
    spelling is not identity.  Resolve through the dossier's authoritative
    ``mpn:`` field, never through punctuation stripping or another fuzzy
    normalization.  The directory name remains the compatibility fallback
    only for older dossiers that omit ``mpn:``.

    Duplicate exact identities are an ambiguity and therefore a hard
    P-AUTH failure.  This deliberately scans the small dossier tree instead
    of guessing which filesystem-safe spelling an author intended.
    """
    parts_dir = Path(parts_dir)
    if yaml is None:
        raise RuntimeError("P-AUTH: PyYAML is required to resolve exact MPN dossiers")
    matches = []
    for ypath in sorted(parts_dir.glob("*/part.yaml")):
        try:
            data = yaml.safe_load(ypath.read_text(encoding="utf-8-sig")) or {}
        except Exception as exc:  # noqa: BLE001 - surface the exact bad authority
            raise RuntimeError(f"P-AUTH {ypath}: cannot parse part.yaml: {exc}") from exc
        if not isinstance(data, dict):
            raise RuntimeError(f"P-AUTH {ypath}: part.yaml must contain a mapping")
        declared_mpn = str(data.get("mpn") or ypath.parent.name).strip()
        if declared_mpn == exact_mpn:
            matches.append((ypath.parent, data))
    if not matches:
        raise RuntimeError(
            f"P-AUTH {parts_dir}: exact BOM MPN {exact_mpn!r} resolves to no "
            "part.yaml `mpn:` identity")
    if len(matches) != 1:
        paths = ", ".join(str(part_dir / "part.yaml") for part_dir, _ in matches)
        raise RuntimeError(
            f"P-AUTH {parts_dir}: exact BOM MPN {exact_mpn!r} is ambiguous "
            f"across {len(matches)} dossiers: {paths}")
    return matches[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("bom")
    ap.add_argument("parts_dir")
    ap.add_argument("outdir")
    ap.add_argument("--refs", default="")
    args = ap.parse_args()

    board = pcbnew.LoadBoard(args.board)
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    parts = Path(args.parts_dir)

    ref_mpn = {}
    for row in csv.DictReader(open(args.bom, encoding="utf-8-sig")):
        for ref in row["Designator"].split(","):
            ref_mpn[ref.strip()] = row.get("MPN", "")

    want = [r.strip() for r in args.refs.split(",") if r.strip()]
    made = []
    for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        ref = fp.GetReference()
        pads = local_pads(fp)
        numbered = [p for p in pads if p["num"]]
        if want:
            if ref not in want:
                continue
        elif len(numbered) <= 3:
            continue
        for p in pads:
            p["side"] = side_of(p, numbered)
        mpn = ref_mpn.get(ref, "")
        ymap, aliases, ds, verified = {}, {}, "(none)", ""
        if mpn:
            part_dir, y = part_authority(parts, mpn)
            ymap = {str(k): v for k, v in (y.get("pins") or {}).items()}
            aliases = {str(k): v for k, v in (y.get("pin_aliases") or {}).items()}
            d = y.get("datasheet") or {}
            ds = datasheet_path(part_dir, d)
            verified = y.get("verified", "")
        physical_map = dict(ymap)
        semantic_seen = set()
        alias_targets = set()
        for semantic, spec in aliases.items():
            if not isinstance(spec, dict) or not spec.get("footprint"):
                continue
            target = str(spec["footprint"])
            alias_targets.add(target)
            if semantic in ymap:
                physical_map[target] = ymap[semantic]
        winding_pads = [p for p in numbered
                        if p["num"] in physical_map and p["num"] not in alias_targets]
        lines = [
            f"# pin dossier: {ref}  ({mpn or 'MPN unknown'})",
            "",
            f"- footprint: {fp.GetFPID().GetUniStringLibId()}",
            f"- board position: ({fp.GetPosition().x/1e6:.6f}, {fp.GetPosition().y/1e6:.6f}) rot {fp.GetOrientationDegrees():.6f} degrees (native KiCad)",
            f"- mounted side: {'back (B.Cu)' if fp.IsFlipped() else 'front (F.Cu)'}",
            f"- computed winding of pins 1..N: **{winding(winding_pads)}**",
            f"- datasheet: {ds}",
            f"- part.yaml verification note: {verified or '(none)'}",
            "",
            "Local coordinates are COMPONENT-TOP mm: looking at the component from its mounted side,",
            "with board translation and rotation undone; +x is RIGHT, +y is DOWN.",
            ("Back mount: native KiCad relative coordinates are reflected y -> -y after undoing rotation."
             if fp.IsFlipped() else "Front mount: native KiCad relative coordinates need no reflection."),
            "Winding and N/S/E/W sides use this component-top frame; compare a manufacturer TOP VIEW by rotation only.",
            "The native board coordinates retain the board-front projection, +x right/+y down, without any transform.",
            "Frame conversion does not validate the footprint or electrical connections.",
            "",
            "| pad | local (x,y) | side | size | function (part.yaml) | NET on board | native board (x,y) |",
            "|---|---|---|---|---|---|---|",
        ]
        seen = set()
        for p in sorted(numbered, key=lambda q: (len(q["num"]), q["num"])):
            fn = physical_map.get(p["num"], "(not in yaml)")
            if isinstance(fn, dict):
                fn = fn.get("name", str(fn))
            seen.add(p["num"])
            for semantic, spec in aliases.items():
                if isinstance(spec, dict) and str(spec.get("footprint", "")) == p["num"]:
                    semantic_seen.add(semantic)
            lines.append(f"| {p['num']} | ({p['x']:+.6f},{p['y']:+.6f}) | {p['side']} "
                         f"| {p['w']}x{p['h']}{' THT' if p['tht'] else ''} | {fn} | {p['net']} "
                         f"| ({p['board_x']:+.6f},{p['board_y']:+.6f}) |")
        if aliases:
            lines += ["", "Declared pin aliases (review these against the manufacturer drawing):"]
            for semantic, spec in sorted(aliases.items()):
                if isinstance(spec, dict):
                    lines.append(
                        f"- `{semantic}`: schematic `{spec.get('schematic', '')}`, "
                        f"footprint `{spec.get('footprint', '')}`, "
                        f"fused: `{str(bool(spec.get('fused', False))).lower()}`; "
                        f"why: {spec.get('why', '(none)')}; evidence: {spec.get('evidence', '(none)')}"
                    )
        missing = [k for k in ymap if k not in seen and k not in semantic_seen]
        if missing:
            lines += ["", f"part.yaml pins with NO pad on the footprint: {missing}"]
        anonymous = sorted(
            (p for p in pads if not p["num"]),
            key=lambda p: (p["x"], p["y"], p["kind"], p["shape"],
                           p["w"], p["h"], p["layers"]),
        )
        if anonymous:
            lines += [
                "",
                "Native unnumbered paste/mechanical features (complete footprint inventory):",
                "",
                "| feature | type | shape | local (x,y) | size | drill | layer mask | native board (x,y) |",
                "|---|---|---|---|---|---|---|---|",
            ]
            for index, p in enumerate(anonymous, 1):
                drill = (f"{p['drill_w']}x{p['drill_h']}"
                         if p["drill_w"] or p["drill_h"] else "none")
                lines.append(
                    f"| anonymous-{index} | {p['kind']} | {p['shape']} "
                    f"| ({p['x']:+.6f},{p['y']:+.6f}) | {p['w']}x{p['h']} "
                    f"| {drill} | `{p['layers']}` "
                    f"| ({p['board_x']:+.6f},{p['board_y']:+.6f}) |"
                )
        (out / f"{ref}.md").write_text("\n".join(lines) + "\n")
        made.append(ref)
    print(f"dossiers: {len(made)} -> {out}  ({', '.join(made)})")


if __name__ == "__main__":
    main()
