#!/usr/bin/env python3
"""Build and grade the reduced Crow ADC F.Cu launch checkpoint.

The board is generated from editable source geometry so connectivity and DRC
are native KiCad observations, while this case's deliberately narrow contract
remains explicit: ADC_DOUT must be wholly F.Cu and use zero vias.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pcbnew

PAD_POINTS = [[20.0, 20.0], [60.0, 20.0]]
WALL_START = [40.0, 17.0]
WALL_END = [40.0, 23.0]

def mm(value: float) -> int:
    return pcbnew.FromMM(float(value))


def load_geometry(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    route = doc.get("route") if isinstance(doc, dict) else None
    pads = doc.get("pads_mm") if isinstance(doc, dict) else None
    if (doc.get("schema") != 1 or doc.get("net") != "ADC_DOUT" or
            not isinstance(route, dict) or not isinstance(pads, list) or
            pads != PAD_POINTS):
        raise ValueError("geometry must retain schema=1, ADC_DOUT, and two pads_mm points")
    points = route.get("points_mm")
    if (route.get("width_mm", 0) < 0.25 or not isinstance(points, list) or
            len(points) < 2 or not all(isinstance(p, list) and len(p) == 2 for p in points)):
        raise ValueError("route needs width_mm >= 0.25 and at least two points_mm")
    if not isinstance(doc.get("vias_mm", []), list):
        raise ValueError("vias_mm must be a list")
    return doc


def add_pad(board, net, reference: str, number: str, point: list[float]):
    footprint = pcbnew.FOOTPRINT(board)
    footprint.SetReference(reference)
    footprint.Reference().SetVisible(False)
    pad = pcbnew.PAD(footprint)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(pcbnew.VECTOR2I(mm(1.2), mm(1.2)))
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.F_Cu)
    layers.AddLayer(pcbnew.F_Mask)
    pad.SetLayerSet(layers)
    pad.SetPosition(pcbnew.VECTOR2I(mm(point[0]), mm(point[1])))
    pad.SetNet(net)
    footprint.Add(pad)
    board.Add(footprint)


def add_outline(board) -> None:
    corners = [(10.0, 10.0), (70.0, 10.0), (70.0, 30.0), (10.0, 30.0)]
    for start, end in zip(corners, corners[1:] + corners[:1]):
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetStart(pcbnew.VECTOR2I(mm(start[0]), mm(start[1])))
        edge.SetEnd(pcbnew.VECTOR2I(mm(end[0]), mm(end[1])))
        edge.SetLayer(pcbnew.Edge_Cuts)
        board.Add(edge)


def build(geometry: Path, board_path: Path) -> None:
    doc = load_geometry(geometry)
    board = pcbnew.BOARD()
    net = pcbnew.NETINFO_ITEM(board, "ADC_DOUT")
    board.Add(net)
    wall_net = pcbnew.NETINFO_ITEM(board, "GND")
    board.Add(wall_net)
    add_outline(board)
    add_pad(board, net, "U_ADC", "DOUT", doc["pads_mm"][0])
    add_pad(board, net, "J_ADC", "1", doc["pads_mm"][1])
    add_pad(board, wall_net, "WALL_GND_A", "1", WALL_START)
    add_pad(board, wall_net, "WALL_GND_B", "1", WALL_END)
    wall = pcbnew.PCB_TRACK(board)
    wall.SetStart(pcbnew.VECTOR2I(mm(WALL_START[0]), mm(WALL_START[1])))
    wall.SetEnd(pcbnew.VECTOR2I(mm(WALL_END[0]), mm(WALL_END[1])))
    wall.SetWidth(mm(0.8))
    wall.SetLayer(pcbnew.F_Cu)
    wall.SetNet(wall_net)
    board.Add(wall)
    layer = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}.get(doc["route"].get("layer"))
    if layer is None:
        raise ValueError("route.layer must be F.Cu or B.Cu")
    points = doc["route"]["points_mm"]
    for start, end in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(mm(start[0]), mm(start[1])))
        track.SetEnd(pcbnew.VECTOR2I(mm(end[0]), mm(end[1])))
        track.SetWidth(mm(doc["route"]["width_mm"]))
        track.SetLayer(layer)
        track.SetNet(net)
        board.Add(track)
    for point in doc.get("vias_mm", []):
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pcbnew.VECTOR2I(mm(point[0]), mm(point[1])))
        via.SetWidth(mm(0.6))
        via.SetDrill(mm(0.3))
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        via.SetNet(net)
        board.Add(via)
    board_path.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(board_path), board)


def findings_for(board_path: Path) -> list[dict]:
    board = pcbnew.LoadBoard(str(board_path))
    pads = [pad for footprint in board.GetFootprints() for pad in footprint.Pads()
            if pad.GetNetname() == "ADC_DOUT"]
    findings = []
    if len(pads) != 2:
        findings.append({"code": "ADC_PAD_CENSUS", "message": f"expected 2 ADC_DOUT pads, got {len(pads)}"})
    else:
        connectivity = board.GetConnectivity()
        connectivity.Build(board)
        # KiCad returns the complete native cluster, not merely a one-segment
        # neighbor list. The accepted control has four bends/five segments.
        connected = list(connectivity.GetConnectedItems(pads[0]))
        if pads[1] not in connected:
            findings.append({"code": "ADC_DOUT_UNCONNECTED", "message": "native pcbnew connectivity does not join U_ADC.DOUT to J_ADC.1"})
    vias = [item for item in board.GetTracks() if item.GetClass() == "PCB_VIA"]
    if vias:
        findings.append({"code": "ZERO_VIA_CONTRACT", "message": f"ADC source-launch route contains {len(vias)} via(s)"})
    wrong_layer = [item for item in board.GetTracks()
                   if item.GetClass() != "PCB_VIA" and item.GetLayer() != pcbnew.F_Cu]
    if wrong_layer:
        findings.append({"code": "FRONT_COPPER_CONTRACT", "message": "ADC source-launch route contains non-F.Cu copper"})
    return findings


def native_drc(board_path: Path) -> tuple[bool, str]:
    report = board_path.with_suffix(".drc")
    result = subprocess.run(
        ["kicad-cli", "pcb", "drc", "--severity-all", "--exit-code-violations",
         "--output", str(report), str(board_path)], text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45, check=False)
    return result.returncode == 0, result.stdout[-4000:]


def emit(outcome: str, findings: list[dict], exit_code: int) -> int:
    print(json.dumps({"schema": 1, "outcome": outcome, "findings": findings}, sort_keys=True))
    return exit_code


def prepare(case: Path, workspace: Path) -> int:
    # The checkpoint runner materializes snapshot/ before calling prepare.
    # Keep this compatibility action non-destructive for direct invocations.
    if not (workspace / "geometry.json").is_file():
        return emit("ERROR", [{"code": "WORKSPACE_MISSING_SNAPSHOT", "message": "runner did not materialize snapshot geometry"}], 2)
    return emit("PASS", [], 0)


def grade(case: Path, workspace: Path) -> int:
    geometry = workspace / "geometry.json"
    board_path = workspace / "native" / "adc_launch.kicad_pcb"
    try:
        build(geometry, board_path)
        findings = findings_for(board_path)
        drc_ok, drc_output = native_drc(board_path)
        if not drc_ok:
            findings.append({"code": "NATIVE_DRC", "message": drc_output or "kicad-cli DRC failed"})
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        return emit("ERROR", [{"code": "CASE_ERROR", "message": str(exc)}], 2)
    return emit("PASS" if not findings else "FAIL", findings, 0 if not findings else 1)


def main(argv: list[str]) -> int:
    if len(argv) != 5 or argv[1] not in {"prepare", "grade"}:
        print("usage: driver.py prepare|grade REPO CASE WORKSPACE", file=sys.stderr)
        return 2
    _, action, _repo, case_arg, workspace_arg = argv
    case, workspace = Path(case_arg), Path(workspace_arg)
    return prepare(case, workspace) if action == "prepare" else grade(case, workspace)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
