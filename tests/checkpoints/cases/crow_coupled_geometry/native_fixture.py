#!/usr/bin/env python3
"""Protected native producer for the synthetic Crow coupled-geometry coupon."""
from __future__ import annotations

import json
from pathlib import Path

import pcbnew
import yaml


NETS = ("MCH_CLK", "ADC_TDM")
PAD_LAYOUT = {
    "MCH_CLK": (
        ("U_MCH", "1", (4.0, 10.6)),
        ("J_CLK", "1", (12.0, 9.0)),
        ("R_CLK", "1", (4.0, 12.0)),
    ),
    "ADC_TDM": (
        ("U_ADC", "25", (4.0, 10.0)),
        ("J_TDM", "2", (14.0, 10.0)),
        ("R_TDM", "2", (12.0, 11.5)),
    ),
}
SEEDS = {
    "MCH_CLK": (
        ((4.0, 10.6), (5.0, 10.6)),
        ((12.0, 9.0), (11.0, 9.0)),
        ((4.0, 12.0), (5.0, 12.0)),
    ),
    # The rejected early branch crosses this required later source launch,
    # rather than merely colliding with an incidental reference polyline.
    "ADC_TDM": (
        ((4.0, 10.0), (8.0, 10.0)),
        ((14.0, 10.0), (13.0, 10.0)),
        ((12.0, 11.5), (12.0, 10.5)),
    ),
}
MIN_WIDTH_MM = 0.25


def mm(value: float) -> int:
    return pcbnew.FromMM(float(value))


def point(value) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(value[0]), mm(value[1]))


def _read_geometry(path: Path) -> dict:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != 1:
        raise ValueError("route_geometry.yaml must have schema: 1")
    routes = doc.get("routes")
    if not isinstance(routes, dict) or set(routes) != set(NETS):
        raise ValueError("route_geometry.yaml must define exactly MCH_CLK and ADC_TDM")
    for net in NETS:
        row = routes[net]
        trunks = row.get("trunks") if isinstance(row, dict) else None
        if (not isinstance(trunks, list) or not trunks or
                not all(isinstance(poly, list) and len(poly) >= 2 and
                        all(isinstance(p, list) and len(p) == 2 and
                            all(isinstance(v, (int, float)) for v in p)
                            for p in poly) for poly in trunks)):
            raise ValueError(f"{net}.trunks must contain numeric polylines")
        if row.get("layer") not in ("F.Cu", "B.Cu"):
            raise ValueError(f"{net}.layer must be F.Cu or B.Cu")
        if not isinstance(row.get("width_mm"), (int, float)) or row["width_mm"] <= 0:
            raise ValueError(f"{net}.width_mm must be positive")
        if not isinstance(row.get("vias_mm", []), list):
            raise ValueError(f"{net}.vias_mm must be a list")
    return doc


def _add_pad(board, net, ref, number, location):
    footprint = pcbnew.FOOTPRINT(board)
    footprint.SetReference(ref)
    footprint.SetValue("SYNTHETIC_PINFIELD")
    footprint.Reference().SetVisible(False)
    footprint.Value().SetVisible(False)
    footprint.SetLayer(pcbnew.F_Cu)
    footprint.SetPosition(point(location))
    board.Add(footprint)
    pad = pcbnew.PAD(footprint)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(point((0.30, 0.30)))
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.F_Cu)
    pad.SetLayerSet(layers)
    pad.SetPosition(point(location))
    pad.SetNet(net)
    footprint.Add(pad)


def _add_track(board, net, start, end, width, layer=pcbnew.F_Cu):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(point(start))
    track.SetEnd(point(end))
    track.SetWidth(mm(width))
    track.SetLayer(layer)
    track.SetNet(net)
    board.Add(track)


def _outline(board):
    corners = ((2.0, 6.0), (16.0, 6.0), (16.0, 15.0), (2.0, 15.0))
    for start, end in zip(corners, corners[1:] + corners[:1]):
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetStart(point(start))
        edge.SetEnd(point(end))
        edge.SetWidth(mm(0.05))
        edge.SetLayer(pcbnew.Edge_Cuts)
        board.Add(edge)


def _project_doc():
    return {
        "board": {"design_settings": {"rules": {
            "min_clearance": 0.15,
            "min_track_width": 0.15,
            "min_via_diameter": 0.60,
            "min_through_hole_diameter": 0.30,
        }}},
        "net_settings": {
            "classes": [
                {"name": "Default", "clearance": 0.15,
                 "track_width": 0.25, "via_diameter": 0.60,
                 "via_drill": 0.30},
                {"name": "ADC_CLOCK", "clearance": 0.15,
                 "track_width": 0.25, "via_diameter": 0.60,
                 "via_drill": 0.30},
            ],
            "netclass_patterns": [
                {"netclass": "ADC_CLOCK", "pattern": "MCH_CLK"},
                {"netclass": "ADC_CLOCK", "pattern": "ADC_TDM"},
            ],
        },
    }


def build_from_source(project: Path, output: Path) -> tuple[Path, Path]:
    """Build prepared plus its exact superset witness from current source."""
    project, output = Path(project), Path(output)
    doc = _read_geometry(project / "03_src/route_geometry.yaml")
    output.mkdir(parents=True, exist_ok=True)
    prepared = output / "prepared.kicad_pcb"
    witness = output / "witness.kicad_pcb"
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    native_nets = {}
    for name in NETS:
        native_nets[name] = pcbnew.NETINFO_ITEM(board, name)
        board.Add(native_nets[name])
    _outline(board)
    for name in NETS:
        for pad_row in PAD_LAYOUT[name]:
            _add_pad(board, native_nets[name], *pad_row)
        for start, end in SEEDS[name]:
            _add_track(board, native_nets[name], start, end, MIN_WIDTH_MM)
    pcbnew.SaveBoard(str(prepared), board)
    prepared.with_suffix(".kicad_pro").write_text(
        json.dumps(_project_doc(), indent=2, sort_keys=True) + "\n")
    prepared.with_suffix(".kicad_dru").write_text("(version 1)\n")
    combined = pcbnew.LoadBoard(str(prepared))
    for name in NETS:
        row = doc["routes"][name]
        net = combined.FindNet(name)
        layer = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}[row["layer"]]
        for polyline in row["trunks"]:
            for start, end in zip(polyline, polyline[1:]):
                _add_track(combined, net, start, end, row["width_mm"], layer)
        for location in row.get("vias_mm", []):
            via = pcbnew.PCB_VIA(combined)
            via.SetPosition(point(location))
            via.SetWidth(mm(0.60))
            via.SetDrill(mm(0.30))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetNet(net)
            combined.Add(via)
    pcbnew.SaveBoard(str(witness), combined)
    return prepared, witness


def expected_pad_rows():
    return tuple((net, ref, number, location)
                 for net in NETS for ref, number, location in PAD_LAYOUT[net])
