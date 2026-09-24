#!/usr/bin/python3
"""Extract a nonqualifying connector-fit prototype from the pinned partial board.

Run: /usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/connector_fit_prototype.py
No Gerbers or drill files are emitted. The saved PCB is only a geometry screen.
"""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
import uuid
from pathlib import Path

import pcbnew
import yaml


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "projects/crow-usb-carrier-v1"
SOURCE = ROOT / "skills/kicad-pcb/scripts/tests/fixtures/crow_usb_partial_port/board.kicad_pcb"
FLOORPLAN = PROJECT / "03_src/floorplan.yaml"
GROUPS = PROJECT / "03_src/rules/connector_assemblies.yaml"
OUT = Path(__file__).with_name("connector_fit_prototype.kicad_pcb")
REPORT = Path(__file__).with_name("connector_fit_prototype.json")
SOURCE_SHA256 = "60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17"
REFS = tuple([f"J{i}" for i in range(1, 9)] + ["J_USB", "J_PWR", "J_JTAG"])


def pos(point):
    return [point.x, point.y]


def footprint_geometry(fp):
    pads = sorted(
        (
            p.GetNumber(), pos(p.GetPosition()), pos(p.GetSize()),
            p.GetOrientationDegrees(), int(p.GetShape()), int(p.GetAttribute()),
            pos(p.GetDrillSize()), p.GetLayerSet().FmtHex(),
        )
        for p in fp.Pads()
    )
    return (fp.GetFPIDAsString(), pos(fp.GetPosition()),
            fp.GetOrientationDegrees(), pads)


def edge_geometry(board):
    edges = [d for d in board.GetDrawings() if d.GetLayerName() == "Edge.Cuts"]
    assert edges and all(d.GetShapeStr() == "Line" for d in edges), "unexpected edge shape"
    return sorted((pos(d.GetStart()), pos(d.GetEnd()), d.GetWidth()) for d in edges)


def canonical_pcb_text(raw):
    """Stabilize pcbnew's unordered footprint output and new clone UUIDs."""
    parts = re.split(r'(?=^\t\((?:footprint|gr_line|embedded_fonts)\b)', raw, flags=re.M)
    assert len(parts) == 17, "unexpected serialized board structure"
    header, *items = parts
    footprints = [item for item in items if item.startswith("\t(footprint ")]
    edges = [item for item in items if item.startswith("\t(gr_line")]
    tail = [item for item in items if item.startswith("\t(embedded_fonts")]
    assert len(footprints) == 11 and len(edges) == 4 and len(tail) == 1
    def ref(item):
        match = re.search(r'\(property "Reference" "([^"]+)"', item)
        assert match
        return match.group(1)
    assert {ref(item) for item in footprints} == set(REFS)
    # Each edge is a line, and the start/end text is fixed by the source.
    def edge_key(item):
        match = re.search(r'\(start ([^)]+)\).*?\(end ([^)]+)\)', item, re.S)
        assert match
        return match.groups()
    uuid_pattern = re.compile(r'\(uuid "[0-9a-f-]+"\)')
    def order_arcs(item):
        # pcbnew also iterates coincident footprint arcs in variable order.
        chunks = re.split(r'(?=^\t\t\([a-z_]+\b)', item, flags=re.M)
        ordered_chunks = []
        arc_run = []
        def flush():
            ordered_chunks.extend(sorted(arc_run, key=lambda arc: uuid_pattern.sub("", arc)))
            arc_run.clear()
        for chunk in chunks:
            if chunk.startswith("\t\t(fp_arc"):
                arc_run.append(chunk)
            else:
                flush()
                ordered_chunks.append(chunk)
        flush()
        return "".join(ordered_chunks)
    ordered = header + "".join(order_arcs(item) for item in sorted(footprints, key=ref)) + "".join(sorted(edges, key=edge_key)) + tail[0]
    # UUIDs have no cross-references in this extracted board. Their ordinal is
    # stable after sorting and identifies each item uniquely on every run.
    return uuid_pattern.sub(
        lambda match, counter=iter(range(10000)): f'(uuid "{uuid.uuid5(uuid.NAMESPACE_URL, SOURCE_SHA256 + ":connector-fit:" + str(next(counter)))}")',
        ordered,
    )


def main():
    actual_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert actual_sha == SOURCE_SHA256, f"source changed: {actual_sha}"
    source = pcbnew.LoadBoard(str(SOURCE))
    source_fp = {fp.GetReference(): fp for fp in source.GetFootprints()}
    assert len(source_fp) == 569, "partial board population changed"
    assert all(ref in source_fp for ref in REFS)

    floorplan = yaml.safe_load(FLOORPLAN.read_text())
    anchors = floorplan["placement"]["anchors"]
    outline = floorplan["board"]["outline"]
    for ref in REFS:
        fp = source_fp[ref]
        x, y, angle = anchors[ref]
        assert pos(fp.GetPosition()) == [pcbnew.FromMM(x), pcbnew.FromMM(y)], ref
        assert fp.GetOrientationDegrees() == angle, ref
    assert pcbnew.ToMM(source.GetDesignSettings().GetBoardThickness()) == floorplan["board"]["stackup"]["nominal_thickness_mm"]
    source_edges = edge_geometry(source)
    vertices = {tuple(p) for start, end, _ in source_edges for p in (start, end)}
    expected_vertices = {
        (pcbnew.FromMM(x), pcbnew.FromMM(y))
        for x in (outline["x0"], outline["x1"])
        for y in (outline["y0"], outline["y1"])
    }
    assert len(source_edges) == 4 and vertices == expected_vertices

    coupon = pcbnew.BOARD()
    coupon.SetCopperLayerCount(source.GetCopperLayerCount())
    coupon.GetDesignSettings().SetBoardThickness(source.GetDesignSettings().GetBoardThickness())
    for ref in REFS:
        coupon.Add(source_fp[ref].Duplicate(False))
    for drawing in source.GetDrawings():
        if drawing.GetLayerName() == "Edge.Cuts":
            coupon.Add(drawing.Duplicate())
    # KiCad may create a .kicad_pro while loading a board. Keep those sidecars
    # inside a temporary directory and publish only the verified PCB bytes.
    with tempfile.TemporaryDirectory(prefix="crow-connector-fit-") as tmp:
        temporary_board = Path(tmp) / OUT.name
        pcbnew.SaveBoard(str(temporary_board), coupon)
        temporary_board.write_text(canonical_pcb_text(temporary_board.read_text()))
        saved = pcbnew.LoadBoard(str(temporary_board))
        board_bytes = temporary_board.read_bytes()
    saved_fp = {fp.GetReference(): fp for fp in saved.GetFootprints()}
    assert set(saved_fp) == set(REFS)
    assert edge_geometry(saved) == source_edges
    assert saved.GetDesignSettings().GetBoardThickness() == source.GetDesignSettings().GetBoardThickness()
    for ref in REFS:
        assert footprint_geometry(saved_fp[ref]) == footprint_geometry(source_fp[ref]), ref

    OUT.write_bytes(board_bytes)

    contract = yaml.safe_load(GROUPS.read_text())
    groups = {group["id"]: group["members"] for group in contract["simultaneous_groups"]}
    assert set(groups["normal_service"]) == set(REFS) - {"J_JTAG"}
    assert set(groups["bench_service"]) == set(REFS)
    REPORT.write_text(json.dumps({
        "status": "NONQUALIFYING_GEOMETRY_SCREEN_ONLY",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": actual_sha,
        "board": OUT.name,
        "board_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "connector_refs": list(REFS),
        "exact_native_footprint_pad_pose_edge_parity": True,
        "nominal_thickness_mm": pcbnew.ToMM(saved.GetDesignSettings().GetBoardThickness()),
        "simultaneous_groups": groups,
        "qualification_blockers": [
            "Exploratory rectangular outline is not an accepted final board outline.",
            "No board restraint or mounting-hole coordinates are defined in the source.",
            "No measured hand, cable, bend, or enclosure clearance envelopes exist.",
            "Physical mating, reaction, tolerance, and repeated-use observations are absent.",
        ],
        "gerbers_emitted": False,
    }, indent=2) + "\n")
    print(f"Wrote {OUT} and {REPORT}; native connector/pad/edge parity passed")


if __name__ == "__main__":
    main()
