#!/usr/bin/env python3
"""Generate an exact-board assembly locator for explicitly reviewed omissions.

This emits identification evidence, never a waiver or an order authorization.
The separate assembly_locator_check module owns validation. Mixed-side board
context uses each mounted side; reviewed exceptions remain top-side only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import textwrap
from pathlib import Path

import pcbnew
import yaml
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

STEM = "assembly_locator"
VIEW = ("Top: native KiCad X right / Y down. Bottom: viewed from below, "
        "flipped left-to-right about the board frame centre; X left / Y down. "
        "Coordinates and rotations remain native KiCad millimetres/degrees. "
        "Bounding envelopes are locator context, not manufacturing geometry.")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_config(path):
    data = yaml.safe_load(Path(path).read_text())
    keys = {"schema", "title", "owner", "orientation", "exceptions"}
    if not isinstance(data, dict) or set(data) != keys or data["schema"] != 1:
        raise ValueError("assembly locator requires closed schema 1")
    for key in ("title", "owner", "orientation"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"assembly locator {key} is empty")
    records = data["exceptions"]
    if not isinstance(records, list) or not records:
        raise ValueError("assembly locator exceptions must be nonempty")
    required = {"ref", "value", "mpn", "lcsc", "x", "y", "rotation", "side", "pads"}
    for row in records:
        if not isinstance(row, dict) or set(row) != required:
            raise ValueError("assembly locator exception has unknown/missing fields")
        if row["side"] != "top" or not row["mpn"] or not 1 <= len(row["pads"]) <= 4:
            raise ValueError("assembly locator requires top-side exact identities with 1–4 pads")
        for pad in row["pads"]:
            if not isinstance(pad, dict) or set(pad) != {"number", "net"}:
                raise ValueError("assembly locator pad requires number and net")
    refs = [r["ref"] for r in records]
    if len(refs) != len(set(refs)):
        raise ValueError("duplicate assembly locator exception")
    return data


def box(item):
    bounds = item.GetBoundingBox()
    return [bounds.GetLeft() / 1e6, bounds.GetTop() / 1e6,
            bounds.GetRight() / 1e6, bounds.GetBottom() / 1e6]


def collect(board_path, bom_path, cpl_path, config_path):
    cfg = load_config(config_path)
    board = pcbnew.LoadBoard(str(board_path))
    with Path(bom_path).open(encoding="utf-8-sig") as stream:
        bom = {}
        for row in csv.DictReader(stream):
            for ref in row["Designator"].split(","):
                if ref.strip() in bom:
                    raise ValueError(f"duplicate BOM reference {ref}")
                bom[ref.strip()] = row
    exceptions = {r["ref"]: r for r in cfg["exceptions"]}
    rows = []
    for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        if fp.GetAttributes() & pcbnew.FP_BOARD_ONLY:
            continue
        ref = fp.GetReference()
        side = "bottom" if fp.IsFlipped() else "top"
        fab_layer = pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab
        silk_layer = pcbnew.B_SilkS if fp.IsFlipped() else pcbnew.F_SilkS
        bodies = [box(g) for g in fp.GraphicalItems()
                  if g.GetClass() == "PCB_SHAPE" and g.GetLayer() == fab_layer]
        if not bodies:
            raise ValueError(f"missing native body context for {ref}")
        hidden = not fp.Reference().IsVisible() or fp.Reference().GetLayer() != silk_layer
        row = {
            "ref": ref, "value": fp.GetValue(),
            "mpn": bom.get(ref, {}).get("MPN", "See manual assembly record"),
            "lcsc": bom.get(ref, {}).get("LCSC", ""),
            "x": fp.GetPosition().x / 1e6, "y": fp.GetPosition().y / 1e6,
            "rotation": fp.GetOrientationDegrees(), "side": side, "hidden": hidden,
            "body": [min(b[0] for b in bodies), min(b[1] for b in bodies),
                     max(b[2] for b in bodies), max(b[3] for b in bodies)],
            "pads": [{"number": p.GetNumber(), "net": p.GetNetname(), "box": box(p)}
                     for p in fp.Pads()],
        }
        if ref in exceptions:
            identity = {k: row[k] for k in exceptions[ref] if k != "pads"}
            identity["pads"] = [{"number": p["number"], "net": p["net"]}
                                for p in row["pads"]]
            identity["pads"].sort(key=lambda p: (p["number"], p["net"]))
            expected = dict(exceptions[ref])
            expected["pads"] = sorted(expected["pads"], key=lambda p: (p["number"], p["net"]))
            if identity != expected:
                raise ValueError(f"source locator identity is stale for {ref}")
        rows.append(row)
    hidden = sorted(r["ref"] for r in rows if r["hidden"])
    if set(hidden) != set(exceptions):
        raise ValueError("native omissions do not equal authored exception set")
    edge = board.GetBoardEdgesBoundingBox()
    frame = [edge.GetLeft() / 1e6, edge.GetTop() / 1e6,
             edge.GetRight() / 1e6, edge.GetBottom() / 1e6]
    return cfg, {
        "schema": 1, "board_sha256": sha(board_path), "bom_sha256": sha(bom_path),
        "cpl_sha256": sha(cpl_path), "config_sha256": sha(config_path),
        "frame": frame, "parts": rows, "hidden": hidden, "assembly_count": len(rows),
        "view": VIEW,
    }


def render_html(cfg, data, destination):
    def rect(bounds, kind, side):
        x0, y0, x1, y1 = bounds
        if side == "bottom":
            centre_sum = data["frame"][0] + data["frame"][2]
            x0, x1 = centre_sum-x1, centre_sum-x0
        return f'<rect class="{kind}" x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}"/>'
    groups = []
    for row in data["parts"]:
        groups.append('<g class="part" data-ref="' + html.escape(row["ref"]) + '"><title>'
                      + html.escape(row["ref"] + " " + row["value"]) + "</title>"
                      + rect(row["body"], "body", row["side"])
                      + "".join(rect(p["box"], "pad", row["side"]) for p in row["pads"]) + "</g>")
    x0, y0, x1, y1 = data["frame"]
    replacements = {
        "TITLE": html.escape(cfg["title"]), "ORIENTATION": html.escape(cfg["orientation"]),
        "CONVENTION": html.escape(data["view"]),
        "VIEWBOX": f"{x0-3} {y0-3} {x1-x0+6} {y1-y0+6}",
        "FRAME": f'x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}"',
        "PARTS": "".join(groups),
        "OPTIONS": "".join('<option value="' + html.escape(r["ref"]) + '">'
                           for r in data["parts"]),
        "DATAJSON": json.dumps(data, separators=(",", ":")).replace("<", "\\u003c"),
    }
    page = Path(__file__).with_suffix(".html").read_text()
    for key, value in replacements.items():
        page = page.replace(key, value)
    destination.write_text(page)


def render_atlas(cfg, data, out):
    font_dir = Path("/usr/share/fonts/truetype/dejavu")
    def font(size, bold=False):
        return ImageFont.truetype(str(font_dir / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)
    lookup = {r["ref"]: r for r in data["parts"]}
    def draw_map(draw, region, canvas, target, labels=False):
        x0, y0, x1, y1 = region
        px, py, width, height = canvas
        scale = min(width / (x1-x0), height / (y1-y0))
        def xy(x, y):
            return px + (x-x0)*scale, py + (y-y0)*scale
        draw.rectangle([px, py, px+width, py+height], fill="#eef3ee", outline="#627b6e", width=2)
        for row in data["parts"]:
            if row["side"] != lookup[target]["side"]:
                continue
            bounds = row["body"]
            if bounds[2] < x0 or bounds[0] > x1 or bounds[3] < y0 or bounds[1] > y1:
                continue
            shapes = [(row["body"], "#ec7455" if row["ref"] == target else "#bcc8bd")]
            shapes += [(p["box"], "#ffe3a2") for p in row["pads"]]
            for bounds, fill in shapes:
                a, b = xy(bounds[0], bounds[1]), xy(bounds[2], bounds[3])
                clipped = [max(px, a[0]), max(py, a[1]), min(px+width, b[0]), min(py+height, b[1])]
                if clipped[2] >= clipped[0] and clipped[3] >= clipped[1]:
                    draw.rectangle(clipped, fill=fill, outline="#627b6e", width=2)
            if labels and row["ref"] == target:
                for pad in row["pads"]:
                    q = pad["box"]
                    draw.text(xy((q[0]+q[2])/2, (q[1]+q[3])/2), pad["number"],
                              font=font(24, True), fill="#981e09", anchor="mm")
        row = lookup[target]
        cx, cy = xy(row["x"], row["y"])
        radius = max(12, scale*max((row["body"][2]-row["body"][0])/2+.5,
                                  (row["body"][3]-row["body"][1])/2+.5))
        draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], outline="#a22d18", width=4)
    pages, records = [], []
    for index, ref in enumerate(data["hidden"], 1):
        row = lookup[ref]
        page = Image.new("RGB", (2400, 1600), "white")
        draw = ImageDraw.Draw(page)
        draw.text((80, 50), f'{ref} · {row["value"]}', font=font(46, True), fill="#173e32")
        draw.text((80, 118), f'{row["mpn"]} | {row["lcsc"]} | Top side, {row["rotation"]:g}°', font=font(26), fill="#27382d")
        draw.text((80, 163), f'KiCad X {row["x"]:.3f} mm / Y {row["y"]:.3f} mm', font=font(26), fill="#27382d")
        draw.text((80, 229), "Whole board · top side up (top components only)", font=font(25, True), fill="#173e32")
        draw_map(draw, data["frame"], (80, 275, 940, 630), ref)
        draw.text((1100, 229), "Exact target · highlighted body and numbered pads", font=font(25, True), fill="#173e32")
        draw_map(draw, [row["x"]-10, row["y"]-9, row["x"]+10, row["y"]+9], (1100, 275, 1220, 1100), ref, True)
        lines = ["Use only with the exact release identified below.", "Top-side orientation: " + cfg["orientation"],
                 "Bottom-side context: select a bottom part in the HTML locator.",
                 "Identify the red target from its pad pattern and coordinates.",
                 "Check MPN/value against the exact released BOM.",
                 "Before power or rework, verify pad/net assignment.",
                 "Do not rely on a nearby silk name as a locator.",
                 "Bounding envelopes are context, not production geometry."]
        wrapped = [part for text in lines for part in textwrap.wrap(text, width=72)]
        for line, text in enumerate(wrapped):
            draw.text((80, 960+line*35), text, font=font(22, line == 0), fill="#25372b")
        for index_pad, pad in enumerate(row["pads"]):
            draw.text((80, 1300+index_pad*35), f'Pad {pad["number"]}: {pad["net"]}', font=font(23), fill="#25372b")
        draw.text((80, 1480), "PCB SHA-256: " + data["board_sha256"], font=font(22), fill="#25372b")
        draw.text((80, 1520), f'Locator {index}/{len(data["hidden"])} · {ref}', font=font(22), fill="#25372b")
        name = f"{STEM}_{index:03d}.png"
        metadata = PngInfo()
        metadata.add_text("reference", ref)
        metadata.add_text("board_sha256", data["board_sha256"])
        metadata.add_text("identity_sha256", hashlib.sha256(
            json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
        page.save(out / name, pnginfo=metadata)
        records.append({"ref": ref, "page": index, "path": name})
        pages.append(page)
    pages[0].save(out / f"{STEM}.pdf", save_all=True, append_images=pages[1:],
                  resolution=200.0, creationDate="D:20000101000000Z", modDate="D:20000101000000Z")
    return records


def generate(board_path, bom_path, cpl_path, config_path, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / f"{STEM}_manifest.json"
    manifest_path.unlink(missing_ok=True)
    cfg, data = collect(board_path, bom_path, cpl_path, config_path)
    (out / f"{STEM}.json").write_text(json.dumps(data, indent=2) + "\n")
    render_html(cfg, data, out / f"{STEM}.html")
    pages = render_atlas(cfg, data, out)
    paths = [f"{STEM}.json", f"{STEM}.html", f"{STEM}.pdf"] + [r["path"] for r in pages]
    manifest = {
        "schema": 1, "kind": "assembly-locator-v1", "owner": cfg["owner"],
        "board_sha256": data["board_sha256"], "bom_sha256": data["bom_sha256"],
        "cpl_sha256": data["cpl_sha256"], "config_sha256": data["config_sha256"],
        "generator_sha256": sha(__file__), "template_sha256": sha(Path(__file__).with_suffix(".html")),
        "checker_sha256": sha(Path(__file__).with_name("assembly_locator_check.py")),
        "page_refs": pages,
        "members": [{"path": name, "sha256": sha(out / name), "size": (out / name).stat().st_size}
                    for name in paths],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return [out / name for name in paths] + [manifest_path]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("board", "bom", "cpl", "config", "out"):
        parser.add_argument(name)
    args = parser.parse_args(argv)
    files = generate(args.board, args.bom, args.cpl, args.config, args.out)
    print(f"Assembly locator: {len(files)} exact-board artifacts generated; independent validation required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
