#!/usr/bin/env python3
"""Read-only A-LOCATOR identity and packaging gate, separate from rendering.

Checks all native identities, declared omissions, CSV datums, embedded HTML,
PNG identities and PDF page image order. Hashes prove binding, not usability;
independent visual judgment is still required before adopting an exception.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

import pcbnew
import yaml
from PIL import Image, PdfParser

STEM = "assembly_locator"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def near(left, right):
    return abs(float(left) - float(right)) <= 0.000001


def bounds(item):
    rect = item.GetBoundingBox()
    return [rect.GetX()/1e6, rect.GetY()/1e6,
            (rect.GetX()+rect.GetWidth())/1e6, (rect.GetY()+rect.GetHeight())/1e6]


def same_box(left, right):
    return isinstance(left, list) and len(left) == 4 and all(near(a, b) for a, b in zip(left, right))


def csv_index(path, grouped=False):
    result = {}
    with Path(path).open(encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            refs = row["Designator"].split(",") if grouped else [row["Designator"]]
            for ref in refs:
                ref = ref.strip()
                require(ref and ref not in result, "duplicate/empty CSV reference")
                result[ref] = row
    return result


def check(board_path, bom_path, cpl_path, config_path, out_dir, tool_source=None):
    out = Path(out_dir)
    manifest = json.loads((out / f"{STEM}_manifest.json").read_text())
    data = json.loads((out / f"{STEM}.json").read_text())
    cfg = yaml.safe_load(Path(config_path).read_text())
    require(isinstance(cfg, dict) and set(cfg) == {"schema", "title", "owner", "orientation", "exceptions"}
            and cfg["schema"] == 1, "invalid locator source schema")
    require(manifest.get("schema") == 1 and manifest.get("kind") == "assembly-locator-v1", "invalid manifest schema")
    require(data.get("schema") == 1, "invalid data schema")
    tool_source = Path(tool_source) if tool_source else Path(__file__).parent
    for key, name in [("generator_sha256", "assembly_locator.py"),
                      ("template_sha256", "assembly_locator.html"),
                      ("checker_sha256", "assembly_locator_check.py")]:
        require(manifest.get(key) == digest(tool_source / name), "stale/missing locator tool " + name)
    for key, path in [("board_sha256", board_path), ("bom_sha256", bom_path),
                      ("cpl_sha256", cpl_path), ("config_sha256", config_path)]:
        actual = digest(path)
        require(data.get(key) == actual and manifest.get(key) == actual, "stale " + key)
    require(manifest.get("owner") == cfg["owner"] and cfg["owner"], "missing/different waiver owner")
    records = manifest.get("members")
    require(isinstance(records, list) and records, "missing manifest members")
    names = [r["path"] for r in records]
    require(len(names) == len(set(names)), "duplicate manifest member")
    for row in records:
        name = row["path"]
        require(isinstance(name, str) and Path(name).name == name, "unsafe manifest path")
        path = out / name
        require(path.is_file() and path.stat().st_size == row["size"]
                and digest(path) == row["sha256"], "missing/corrupt manifest member " + name)
    board = pcbnew.LoadBoard(str(board_path))
    native = {fp.GetReference(): fp for fp in board.GetFootprints()
              if not fp.GetAttributes() & pcbnew.FP_BOARD_ONLY}
    require(same_box(data.get("frame"), [board.GetBoardEdgesBoundingBox().GetX()/1e6,
                                    board.GetBoardEdgesBoundingBox().GetY()/1e6,
                                    board.GetBoardEdgesBoundingBox().GetRight()/1e6,
                                    board.GetBoardEdgesBoundingBox().GetBottom()/1e6]), "native board frame")
    require(data.get("view") == ("Top: native KiCad X right / Y down. Bottom: viewed from below, "
            "flipped left-to-right about the board frame centre; X left / Y down. "
            "Coordinates and rotations remain native KiCad millimetres/degrees. "
            "Bounding envelopes are locator context, not manufacturing geometry."), "viewing convention")
    rows = data.get("parts")
    require(isinstance(rows, list) and len(rows) == len(native) and native, "assembled denominator")
    refs = [r["ref"] for r in rows]
    require(len(refs) == len(set(refs)) and set(refs) == set(native), "reference set/duplicate")
    by_ref = {r["ref"]: r for r in rows}
    hidden = {ref for ref, fp in native.items()
              if not fp.Reference().IsVisible() or fp.Reference().GetLayer() !=
              (pcbnew.B_SilkS if fp.IsFlipped() else pcbnew.F_SilkS)}
    source_rows = cfg["exceptions"]
    require(isinstance(source_rows, list) and source_rows, "empty source exception set")
    source = {r["ref"]: r for r in source_rows}
    require(len(source) == len(source_rows), "duplicate source exception")
    require(isinstance(data.get("hidden"), list) and len(data["hidden"]) == len(set(data["hidden"])), "hidden list")
    require(set(source) == set(data["hidden"]) == hidden, "native/source/locator omission sets differ")
    require(data.get("assembly_count") == len(native), "declared assembled denominator")
    bom, cpl = csv_index(bom_path, True), csv_index(cpl_path)
    require(set(cpl) <= set(bom) <= set(native), "CSV reference coverage")
    pads_checked = 0
    for ref, fp in native.items():
        row = by_ref[ref]
        side = "bottom" if fp.IsFlipped() else "top"
        require(row["side"] == side, "unsupported/wrong side " + ref)
        if ref in cpl:
            require(cpl[ref]["Layer"].lower() == side, "CPL side " + ref)
        require(near(row["x"], fp.GetPosition().x/1e6) and near(row["y"], fp.GetPosition().y/1e6), "position " + ref)
        require(near(row["rotation"], fp.GetOrientationDegrees()), "rotation " + ref)
        require(row["value"] == fp.GetValue() and row["hidden"] == (ref in hidden), "value/visibility " + ref)
        actual = sorted((p.GetNumber(), p.GetNetname(), bounds(p)) for p in fp.Pads())
        given = sorted((p["number"], p["net"], p["box"]) for p in row["pads"])
        require(len(actual) == len(given), "pad denominator " + ref)
        for native_pad, reported_pad in zip(actual, given):
            require(native_pad[:2] == reported_pad[:2] and same_box(reported_pad[2], native_pad[2]), "pad identity/geometry " + ref)
        pads_checked += len(actual)
        shapes = [bounds(g) for g in fp.GraphicalItems()
                  if g.GetClass() == "PCB_SHAPE" and g.GetLayer() == (pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)]
        require(shapes, "missing native body " + ref)
        extent = [min(x[0] for x in shapes), min(x[1] for x in shapes),
                  max(x[2] for x in shapes), max(x[3] for x in shapes)]
        require(same_box(row["body"], extent), "body geometry " + ref)
        if ref in bom:
            require(row["mpn"] == bom[ref]["MPN"] and row["lcsc"] == bom[ref]["LCSC"], "BOM identity " + ref)
        if ref in hidden:
            require(ref in bom and ref in cpl, "omitted reference missing from BOM/CPL " + ref)
            wanted = source[ref]
            require(wanted.get("side") == "top" and 1 <= len(wanted.get("pads", [])) <= 4, "unsupported exception side/pads " + ref)
            require(set(wanted) == {"ref", "value", "mpn", "lcsc", "x", "y", "rotation", "side", "pads"}, "unknown/missing source identity fields")
            for key in ("ref", "value", "mpn", "lcsc", "side"):
                require(wanted[key] == row[key], "source identity " + ref + ":" + key)
            for key in ("x", "y", "rotation"):
                require(near(wanted[key], row[key]), "source geometry " + ref + ":" + key)
            require(sorted((p["number"], p["net"]) for p in wanted["pads"]) ==
                    sorted((p["number"], p["net"]) for p in row["pads"]), "source pad identity " + ref)
            require(cpl[ref]["Layer"].lower() == "top", "CPL side " + ref)
            require(near(cpl[ref]["Mid X"], row["x"]) and near(cpl[ref]["Mid Y"], -row["y"]), "CPL datum " + ref)
            # The reviewed exception set consists of rotation-symmetric 2-pad
            # passives. Native-to-CPL rotation is explicitly identity-bound;
            # do not silently apply the supplier's generic rotation fallback.
            require(near(float(cpl[ref]["Rotation"]) % 360, float(row["rotation"]) % 360), "CPL rotation " + ref)
    text = (out / f"{STEM}.html").read_text()
    match = re.search(r"const DATA=(.*?);const byRef=", text, re.S)
    require(match is not None and json.loads(match.group(1)) == data, "HTML/JSON disagreement")
    require(data["view"] in text, "HTML viewing convention")
    groups = re.findall(r'<g class="part" data-ref="([^"]+)">', text)
    require(len(groups) == len(set(groups)) and set(groups) == set(native), "HTML clickable reference set")
    script = re.search(r"<script>(.*?)</script>", text, re.S).group(1)
    expected_script = re.search(r"<script>(.*?)</script>", (tool_source / "assembly_locator.html").read_text(), re.S).group(1)
    require(re.sub(r"const DATA=.*?;const byRef=", "const DATA=DATAJSON;const byRef=", script, flags=re.S) == expected_script,
            "HTML executable differs from bound source template")
    svg = ET.fromstring(re.search(r"<svg\b.*?</svg>", text, re.S).group(0))
    require(svg.get("viewBox") == " ".join(str(v) for v in [data["frame"][0]-3, data["frame"][1]-3, data["frame"][2]-data["frame"][0]+6, data["frame"][3]-data["frame"][1]+6]), "HTML board frame")
    require(not svg.get("transform"), "HTML unexpected view transform")
    for group in svg.findall("g"):
        if group.get("class") != "part":
            continue
        row = by_ref[group.get("data-ref")]
        require(not group.get("transform"), "HTML unexpected part transform")
        geometry = {"body": [], "pad": []}
        for rect in group.findall("rect"):
            require(not rect.get("transform"), "HTML unexpected shape transform")
            x, y = float(rect.get("x")), float(rect.get("y"))
            geometry[rect.get("class")].append([x, y, x+float(rect.get("width")), y+float(rect.get("height"))])
        # Independently project native bounds; never import emitter geometry.
        def viewed(box):
            if not native[row["ref"]].IsFlipped():
                return box
            frame = board.GetBoardEdgesBoundingBox()
            axis = (2*frame.GetX()+frame.GetWidth())/1e6
            return [axis-box[2], box[1], axis-box[0], box[3]]
        require(len(geometry["body"]) == 1 and same_box(geometry["body"][0], viewed(row["body"])), "HTML body geometry " + row["ref"])
        wanted_pads = sorted(viewed(p["box"]) for p in row["pads"])
        require(len(geometry["pad"]) == len(wanted_pads) and all(same_box(a, b) for a, b in zip(sorted(geometry["pad"]), wanted_pads)),
                "HTML pad geometry " + row["ref"])
    page_rows = manifest.get("page_refs")
    require(isinstance(page_rows, list) and len(page_rows) == len(hidden), "atlas page denominator")
    require([r["page"] for r in page_rows] == list(range(1, len(hidden)+1)), "atlas page order/duplicate")
    page_refs = [r["ref"] for r in page_rows]
    require(len(set(page_refs)) == len(page_refs) and set(page_refs) == hidden, "atlas reference set/duplicate")
    expected_names = {f"{STEM}.json", f"{STEM}.html", f"{STEM}.pdf"} | {r["path"] for r in page_rows}
    require(set(names) == expected_names and len(expected_names) == len(hidden)+3, "manifest/page membership")
    require({p.name for p in out.glob(f"{STEM}_*.png")} == {r["path"] for r in page_rows}, "unlisted/missing atlas image")
    pdf = PdfParser.PdfParser(filename=str(out / f"{STEM}.pdf"))
    try:
        require(len(pdf.pages) == len(hidden), "PDF page count")
        for row, page_ref in zip(page_rows, pdf.pages):
            ref = row["ref"]
            with Image.open(out / row["path"]) as page_image:
                identity = hashlib.sha256(json.dumps(by_ref[ref], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                require(page_image.info.get("reference") == ref and page_image.info.get("board_sha256") == data["board_sha256"]
                        and page_image.info.get("identity_sha256") == identity, "PNG reference/identity " + ref)
                page = pdf.read_indirect(page_ref)
                width, height = page_image.width * 72/200, page_image.height * 72/200
                require(page[b"MediaBox"] == [0, 0, width, height], "PDF page dimensions " + ref)
                content = pdf.read_indirect(page[b"Contents"]).buf.decode("ascii")
                transform = re.fullmatch(r"\s*q\s+([\d.]+)\s+0\s+0\s+([\d.]+)\s+0\s+0\s+cm\s+/image\s+Do\s+Q\s*", content)
                require(transform is not None and near(transform.group(1), width) and near(transform.group(2), height), "PDF image transform " + ref)
                images = page[b"Resources"][b"XObject"]
                require(len(images) == 1, "unexpected PDF page image denominator")
                stream = pdf.read_indirect(next(iter(images.values())))
                encoded = io.BytesIO()
                page_image.convert("RGB").save(encoded, format="JPEG")
                with Image.open(io.BytesIO(stream.buf)) as pdf_image, Image.open(io.BytesIO(encoded.getvalue())) as expected:
                    require(pdf_image.size == expected.size and pdf_image.tobytes() == expected.tobytes(), "PDF/PNG image disagreement " + ref)
    finally:
        pdf.close()
    return {"assembled_refs": len(native), "pads": pads_checked, "exceptions": len(hidden),
            "pages": len(page_rows), "manifest_members": len(names)}


def waiver_refs(path):
    require(Path(path).is_file(), "source policy waiver record is missing")
    entries = yaml.safe_load(Path(path).read_text())
    require(isinstance(entries, list), "policy waivers must be a list")
    selected = [row for row in entries if row.get("id") == "P-SILK-REF"]
    require(selected, "P-SILK-REF source waiver is missing")
    refs = []
    for row in selected:
        require(isinstance(row.get("refs"), list) and row["refs"], "waiver reference set is empty")
        require(len(str(row.get("why", ""))) >= 40, "waiver rationale is missing")
        require(any("assembly_locator_check.py" in str(item.get("command", ""))
                    for item in row.get("evidence", []) if isinstance(item, dict)), "waiver has no locator evidence command")
        refs.extend(row["refs"])
    require(len(refs) == len(set(refs)), "duplicate policy waiver reference")
    return set(refs)


def waiver_requires_locator(path):
    if not Path(path).is_file():
        return False
    entries = yaml.safe_load(Path(path).read_text())
    require(isinstance(entries, list), "policy waivers must be a list")
    return any("assembly_locator_check.py" in str(item.get("command", ""))
               for row in entries if isinstance(row, dict)
               for item in row.get("evidence", []) if isinstance(item, dict))


def check_visual_review(review_path, out):
    """Bind independent usability judgment to actual pixels via the manifest.

    Identity checks cannot read text in a raster page. The existing render
    reviewer supplies this acceptance; producers must never create it.
    """
    review_path, out = Path(review_path), Path(out)
    require(review_path.is_file(), "independent locator render review is missing")
    wanted_keys = {"reviewer", "completed_at", "review_kind", "design_verdict",
                   "board_sha256", "locator_manifest_sha256", "locator_reviewed_refs"}
    fields = {}
    for line in review_path.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^[>\s*#`-]*([a-z][a-z0-9_-]*)\s*:\s*(.*?)\s*$", line, re.I)
        if match and match.group(1).lower() in wanted_keys:
            key = match.group(1).lower()
            require(key not in fields, "duplicate locator review field " + key)
            fields[key] = match.group(2).strip().strip("`*")
    require(wanted_keys <= set(fields), "independent locator review fields are missing")
    require(fields["reviewer"] and fields["completed_at"], "locator reviewer/date are missing")
    require(fields["review_kind"].lower() == "render" and fields["design_verdict"].upper() == "SOUND",
            "independent locator render review is not SOUND")
    manifest_path = out / f"{STEM}_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    require(fields["locator_manifest_sha256"].lower() == digest(manifest_path),
            "independent locator review manifest is stale")
    require(fields["board_sha256"].lower() == manifest["board_sha256"], "locator review board is stale")
    refs = json.loads(fields["locator_reviewed_refs"])
    require(isinstance(refs, list) and all(isinstance(ref, str) for ref in refs)
            and len(refs) == len(set(refs))
            and set(refs) == {row["ref"] for row in manifest["page_refs"]},
            "independent locator review reference coverage differs")


def project_check(project, board=None, out=None):
    project = Path(project).resolve()
    config = project / "03_src/rules/assembly_locator.yaml"
    target = Path(out) if out else project / "06_build/pre_route/current_assembly"
    if not config.exists():
        require(not (target / f"{STEM}_manifest.json").exists()
                and not waiver_requires_locator(project / "03_src/rules/policy_waivers.yaml"), "locator evidence has no source contract")
        return None
    require(waiver_refs(project / "03_src/rules/policy_waivers.yaml") ==
            {r["ref"] for r in yaml.safe_load(config.read_text())["exceptions"]}, "policy waiver/locator exception sets differ")
    if board is None:
        boards = list((project / "04_kicad").glob("*.kicad_pcb"))
        require(len(boards) == 1, "locator board is ambiguous/missing")
        board = boards[0]
    result = check(board, target / "bom.csv", target / "cpl.csv", config, target)
    route = project / "03_src/route.yaml"
    flow = (yaml.safe_load(route.read_text()) or {}).get("flow", {}) if route.is_file() else {}
    review = (flow.get("pre_route_reviews") or {}).get("render", "08_reviews/pre-route_render.md")
    check_visual_review(project / review, target)
    return result


def release_check(release):
    """Only sealed source and shipped artifacts; never consult live project data."""
    release = Path(release)
    config = release / "source/assembly_locator.yaml"
    target = release / "fab"
    if (not config.exists() and not list(target.glob(f"{STEM}*"))
            and not waiver_requires_locator(release / "source/policy_waivers.yaml")):
        return None
    require(config.is_file(), "release locator source contract is missing")
    require(waiver_refs(release / "source/policy_waivers.yaml") ==
            {r["ref"] for r in yaml.safe_load(config.read_text())["exceptions"]}, "release policy waiver/locator sets differ")
    boards = list((release / "source").glob("*.kicad_pcb"))
    require(len(boards) == 1, "release locator board is missing/ambiguous")
    result = check(boards[0], target / "bom.csv", target / "cpl.csv", config, target,
                   tool_source=release / "source/locator_tools")
    check_visual_review(release / "verification/render_review.md", target)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    exact = sub.add_parser("exact")
    for name in ("board", "bom", "cpl", "config", "out"):
        exact.add_argument(name)
    project = sub.add_parser("project")
    project.add_argument("project")
    project.add_argument("--board")
    project.add_argument("--out")
    release = sub.add_parser("release")
    release.add_argument("release")
    args = parser.parse_args(argv)
    try:
        if args.command == "exact":
            result = check(args.board, args.bom, args.cpl, args.config, args.out)
        elif args.command == "release":
            result = release_check(args.release)
        else:
            result = project_check(args.project, args.board, args.out)
        if result is None:
            print("A-LOCATOR N-A: no authored locator contract")
        else:
            print("A-LOCATOR PASS: " + json.dumps(result, sort_keys=True))
            print(f"A-LOCATOR coverage: {result['assembled_refs']}/{result['assembled_refs']} references; "
                  f"{result['pages']}/{result['exceptions']} exception pages")
            print(result["exceptions"])
        return 0
    except (OSError, KeyError, TypeError, ValueError, AttributeError) as exc:
        print("A-LOCATOR FAIL: " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
