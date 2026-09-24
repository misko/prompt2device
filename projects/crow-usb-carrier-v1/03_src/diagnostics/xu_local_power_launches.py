#!/usr/bin/env python3
"""Audit and emit exact, inactive XU local-power launch exceptions.

A reviewed isolated board/config is required. This tool does not consume or
change Crow's canonical floorplan. It does not approve route current or release.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import pcbnew
import yaml

REQUIRED = {
    "XU_VDD14_LOCAL": ("14", "N0V9", "C_XU_VDD_14", "1"),
    "XU_VDDIO17_LOCAL": ("17", "N1V8", "C_XU_VDDIO_17", "1"),
}
NECK_WIDTH = 0.15
ORDINARY_WIDTH = 0.60
MAX_WINDOW_AREA_MM2 = 0.90
EPS = 1e-6
BEGIN = "# XU_LOCAL_POWER_LAUNCHES_BEGIN"
END = "# XU_LOCAL_POWER_LAUNCHES_END"


def die(message):
    raise ValueError(message)


def mm(value):
    return pcbnew.ToMM(value)


def xy(point):
    return (mm(point.x), mm(point.y))


def in_rect(point, rect, margin=0.0):
    x, y = point
    return (rect[0] + margin - EPS <= x <= rect[2] - margin + EPS
            and rect[1] + margin - EPS <= y <= rect[3] - margin + EPS)


def copper_box(track):
    a, b = xy(track.GetStart()), xy(track.GetEnd())
    half = mm(track.GetWidth()) / 2
    return (min(a[0], b[0]) - half, min(a[1], b[1]) - half,
            max(a[0], b[0]) + half, max(a[1], b[1]) + half)


def box_inside(box, rect):
    return (box[0] >= rect[0] - EPS and box[1] >= rect[1] - EPS
            and box[2] <= rect[2] + EPS and box[3] <= rect[3] + EPS)


def box_touches(box, rect):
    return not (box[2] < rect[0] - EPS or box[0] > rect[2] + EPS
                or box[3] < rect[1] - EPS or box[1] > rect[3] + EPS)


def via_touches_rect(via, rect):
    """Test the F.Cu copper disc, including a centre outside the area."""
    x, y = xy(via.GetPosition())
    radius = mm(via.GetWidth(pcbnew.F_Cu)) / 2
    nearest_x = max(rect[0], min(x, rect[2]))
    nearest_y = max(rect[1], min(y, rect[3]))
    return math.hypot(x - nearest_x, y - nearest_y) <= radius + EPS


def footprint(board, ref):
    item = board.FindFootprintByReference(ref)
    if item is None:
        die(f"missing footprint {ref}")
    return item


def pad(board, ref, number):
    item = footprint(board, ref).FindPadByNumber(str(number))
    if item is None:
        die(f"missing pad {ref}.{number}")
    return item


def load(path):
    data = yaml.safe_load(Path(path).read_text()) or {}
    _header(data)
    entries = data.get("launches")
    if not isinstance(entries, list) or len(entries) != len(REQUIRED):
        die("exactly two XU local-power launches required")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            die("launch must be a mapping")
        ident = entry.get("id")
        if ident not in REQUIRED or ident in seen:
            die(f"unknown or duplicate launch {ident}")
        seen.add(ident)
        number, net, target_ref, target_pad = REQUIRED[ident]
        if (entry.get("ref") != "U_XU" or str(entry.get("pad")) != number
                or entry.get("net") != net
                or entry.get("target") != {"ref": target_ref, "pad": target_pad}):
            die(f"{ident}: exact pin/net/target identity changed")
        if "window" in entry:
            window(entry)
    if seen != set(REQUIRED):
        die("missing required XU launch")
    return data


def _header(data):
    if data.get("status") != "placement_review_required":
        die("must remain placement_review_required")
    if (data.get("width_mm") != NECK_WIDTH
            or data.get("ordinary_width_mm") != ORDINARY_WIDTH
            or data.get("layer") != "F.Cu"):
        die("fixed width/layer contract changed")


def window(entry):
    rect = entry.get("window")
    if (not isinstance(rect, list) or len(rect) != 4
            or any(not isinstance(v, (int, float)) or isinstance(v, bool)
                   or not math.isfinite(v) for v in rect)
            or rect[0] >= rect[2] or rect[1] >= rect[3]):
        die(f"{entry['id']}: invalid window")
    cap = entry.get("max_window_area_mm2")
    if (not isinstance(cap, (int, float)) or isinstance(cap, bool)
            or not math.isfinite(cap) or cap <= 0
            or cap > MAX_WINDOW_AREA_MM2 + EPS
            or (rect[2] - rect[0]) * (rect[3] - rect[1]) > cap + EPS):
        die(f"{entry['id']}: widened or unbounded window")
    return rect


def validate(board, config):
    # Do not trust a caller that bypassed load().
    _header(config)
    if (not isinstance(config.get("launches"), list)
            or len(config["launches"]) != len(REQUIRED)):
        die("exactly two XU local-power launches required")
    seen = set()
    for entry in config["launches"]:
        ident = entry.get("id")
        if ident not in REQUIRED or ident in seen:
            die(f"unknown or duplicate launch {ident}")
        seen.add(ident)
        number, net, target_ref, target_pad = REQUIRED[ident]
        if (entry.get("ref") != "U_XU" or str(entry.get("pad")) != number
                or entry.get("net") != net
                or entry.get("target") != {"ref": target_ref, "pad": target_pad}):
            die(f"{ident}: exact pin/net/target identity changed")
        source = pad(board, "U_XU", number)
        target = pad(board, target_ref, target_pad)
        if source.GetNetname() != net or target.GetNetname() != net:
            die(f"{ident}: native pad net changed")
        rect = window(entry)
        flare = entry.get("flare")
        if (not isinstance(flare, list) or len(flare) != 2
                or any(not isinstance(v, (int, float)) or isinstance(v, bool)
                       or not math.isfinite(v) for v in flare)
                or not in_rect(xy(source.GetPosition()), rect, NECK_WIDTH / 2)
                or not in_rect(flare, rect, NECK_WIDTH / 2)
                or tuple(flare) == xy(source.GetPosition())):
            die(f"{ident}: window must bind XU pad centre and distinct flare")
    if seen != set(REQUIRED):
        die("missing required XU launch")
    return config["launches"]


def _path(segments, start, end, ident):
    if not segments:
        die(f"{ident}: missing narrow launch")
    graph = {}
    for track in segments:
        a, b = track.GetStart(), track.GetEnd()
        va, vb = (a.x, a.y), (b.x, b.y)
        if va == vb:
            die(f"{ident}: zero-length narrow segment")
        graph.setdefault(va, []).append(vb)
        graph.setdefault(vb, []).append(va)
    if start not in graph or end not in graph:
        die(f"{ident}: narrow launch does not meet pad centre and flare")
    for node, neighbors in graph.items():
        expected_degree = 1 if node in (start, end) else 2
        if len(neighbors) != expected_degree:
            die(f"{ident}: branch, gap, or extra narrow endpoint")
    visited = {start}
    node, previous = start, None
    while node != end:
        choices = [v for v in graph[node] if v != previous]
        if len(choices) != 1 or choices[0] in visited:
            die(f"{ident}: narrow launch is not one simple path")
        previous, node = node, choices[0]
        visited.add(node)
    if len(visited) != len(graph):
        die(f"{ident}: disconnected narrow copper")


def audit(board, config):
    launches = validate(board, config)
    narrow = {entry["id"]: [] for entry in launches}
    flares = {entry["id"]: False for entry in launches}
    for track in board.GetTracks():
        if track.Type() == pcbnew.PCB_VIA_T:
            if any(via_touches_rect(track, entry["window"])
                   for entry in launches):
                die("via in launch window")
            continue
        if track.Type() != pcbnew.PCB_TRACE_T:
            continue
        layer = track.GetLayer()
        net = track.GetNetname()
        width = mm(track.GetWidth())
        box = copper_box(track)
        hit = [entry for entry in launches if layer == pcbnew.F_Cu
               and box_touches(box, entry["window"])]
        if hit and any(net != entry["net"] for entry in hit):
            die("foreign-net F.Cu copper in launch window")
        if net in ("N0V9", "N1V8") and width < ORDINARY_WIDTH - EPS:
            matching = [entry for entry in launches if entry["net"] == net
                        and layer == pcbnew.F_Cu
                        and box_inside(box, entry["window"])]
            if len(matching) != 1 or abs(width - NECK_WIDTH) > EPS:
                die("offsite, partial, or wrong-width narrow power track")
            narrow[matching[0]["id"]].append(track)
        for entry in hit:
            if (net == entry["net"] and width >= ORDINARY_WIDTH - EPS
                    and (tuple(xy(track.GetStart())) == tuple(entry["flare"])
                         or tuple(xy(track.GetEnd())) == tuple(entry["flare"]))):
                flares[entry["id"]] = True
    for entry in launches:
        ident = entry["id"]
        point = pad(board, "U_XU", REQUIRED[ident][0]).GetPosition()
        start = (point.x, point.y)
        end_point = pcbnew.VECTOR2I_MM(*entry["flare"])
        _path(narrow[ident], start, (end_point.x, end_point.y), ident)
        if not flares[ident]:
            die(f"{ident}: missing ordinary-width flare continuation")


def _zone_rect(zone):
    outline = zone.Outline()
    if outline.OutlineCount() != 1 or outline.Outline(0).PointCount() != 4:
        die(f"{zone.GetZoneName()}: native area shape changed")
    chain = outline.Outline(0)
    return sorted((round(mm(chain.CPoint(i).x), 6),
                   round(mm(chain.CPoint(i).y), 6)) for i in range(4))


def emit(board, config, dru):
    launches = validate(board, config)
    path = Path(dru)
    if not path.is_file():
        die("ordinary DRU must exist before local rule emission")
    original = path.read_text()
    if not re.search(r'\(rule "DIGITAL_POWER_width"\s*\(condition "A\.NetClass == \'DIGITAL_POWER\'"\)\s*\(constraint track_width \(min 0\.6mm\)\)\)', original):
        die("ordinary DIGITAL_POWER 0.60-mm rule missing or changed")
    names = []
    rules = []
    for entry in launches:
        rect = entry["window"]
        name = "xu_launch_" + entry["id"].lower()
        names.append(name)
        wanted = [(rect[0], rect[1]), (rect[2], rect[1]),
                  (rect[2], rect[3]), (rect[0], rect[3])]
        normalized = sorted((round(x, 6), round(y, 6)) for x, y in wanted)
        existing = [zone for zone in board.Zones() if zone.GetZoneName() == name]
        if len(existing) > 1:
            die(f"{name}: duplicate native areas")
        if existing:
            zone = existing[0]
            if (not zone.GetIsRuleArea()
                    or list(zone.GetLayerSet().CuStack()) != [pcbnew.F_Cu]
                    or not zone.GetDoNotAllowVias()
                    or zone.GetDoNotAllowTracks()
                    or zone.GetDoNotAllowPads()
                    or _zone_rect(zone) != normalized):
                die(f"{name}: existing native area changed")
        else:
            zone = pcbnew.ZONE(board)
            zone.SetIsRuleArea(True)
            zone.SetZoneName(name)
            zone.SetLayer(pcbnew.F_Cu)
            layers = pcbnew.LSET()
            layers.AddLayer(pcbnew.F_Cu)
            zone.SetLayerSet(layers)
            zone.SetDoNotAllowVias(True)
            zone.SetDoNotAllowTracks(False)
            zone.SetDoNotAllowPads(False)
            outline = zone.Outline()
            outline.NewOutline()
            for point in wanted:
                outline.Append(pcbnew.VECTOR2I_MM(*point))
            board.Add(zone)
        condition = (f"A.Type == 'Track' && A.NetName == '{entry['net']}' "
                     f"&& A.insideArea('{name}')")
        rules.append(f'(rule "{name}_width"\n  (layer "F.Cu")\n'
                     f'  (condition "{condition}")\n'
                     '  (constraint track_width (min 0.15mm)))')
    block = BEGIN + "\n" + "\n".join(rules) + "\n" + END
    begin_count, end_count = original.count(BEGIN), original.count(END)
    if begin_count != end_count or begin_count > 1:
        die("damaged local DRU markers")
    if begin_count:
        begin = original.index(BEGIN)
        end = original.index(END, begin) + len(END)
        updated = original[:begin] + block + original[end:]
    else:
        updated = original.rstrip() + "\n" + block + "\n"
    path.write_text(updated)
    return names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("board")
    parser.add_argument("config")
    parser.add_argument("--emit-dru")
    parser.add_argument("--save")
    args = parser.parse_args()
    config = load(args.config)
    board = pcbnew.LoadBoard(args.board)
    audit(board, config)
    names = emit(board, config, args.emit_dru) if args.emit_dru else []
    if args.save:
        pcbnew.SaveBoard(args.save, board)
    print(json.dumps({"status": "PLACEMENT_REVIEW_REQUIRED", "areas": names,
                      "launches": [entry["id"] for entry in config["launches"]]}))


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        sys.exit(f"xu_local_power_launches: {error}")
