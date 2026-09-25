#!/usr/bin/env python3
"""Focused production checks for combined routing-geometry admission."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "skills/kicad-pcb/scripts"))
import coupled_geometry_preflight as coupled  # noqa: E402
import placement_routability_preflight as placement  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import check, eq, main, test, tmpdir  # noqa: E402


def vec(x, y):
    return pcbnew.VECTOR2I(round(x * 1e6), round(y * 1e6))


def make_board(path, routes=None, *, move_pad=False, add_via=False,
               width=.18, route_layer=pcbnew.F_Cu,
               rule_area_box=(5.8, 4.6, 6.4, 5.4), include_keepout=True,
               copper_layers=2, outline_shift=0):
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(copper_layers)
    endpoints = {
        "MCH_CLK": ((5, 5), (9, 5)),
        "ADC_TDM": ((7, 3), (7, 7)),
    }
    nets = {}
    for net_name, points in endpoints.items():
        net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(net)
        nets[net_name] = net
        for index, point in enumerate(points):
            fp = pcbnew.FOOTPRINT(board)
            fp.SetReference(("J10" if net_name == "MCH_CLK" else "U_ADC") +
                            str(index + 1))
            fp.SetPosition(vec(*(point if not (move_pad and net_name == "ADC_TDM"
                                               and index == 1)
                                 else (point[0] + 0.5, point[1]))))
            board.Add(fp)
            pad = pcbnew.PAD(fp)
            pad.SetNumber("1")
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad.SetSize(vec(.3, .3))
            layers = pcbnew.LSET(); layers.AddLayer(pcbnew.F_Cu)
            pad.SetLayerSet(layers); fp.Add(pad)
            pad.SetPosition(fp.GetPosition()); pad.SetNet(net)
    for net_name, points in (routes or {}).items():
        for start, end in zip(points, points[1:]):
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(vec(*start)); track.SetEnd(vec(*end))
            track.SetWidth(pcbnew.FromMM(width)); track.SetLayer(route_layer)
            track.SetNet(nets[net_name]); board.Add(track)
    if add_via:
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(vec(6, 5)); via.SetWidth(pcbnew.FromMM(.5))
        via.SetDrill(pcbnew.FromMM(.2)); via.SetNet(nets["MCH_CLK"])
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); board.Add(via)
    if rule_area_box is not None:
        zone = pcbnew.ZONE(board)
        zone.SetIsRuleArea(True); zone.SetZoneName("LAUNCH_LOCAL")
        layers = pcbnew.LSET(); layers.AddLayer(pcbnew.F_Cu)
        zone.SetLayer(pcbnew.F_Cu); zone.SetLayerSet(layers)
        zone.SetDoNotAllowTracks(False); zone.SetDoNotAllowVias(False)
        zone.SetDoNotAllowPads(False); zone.Outline().NewOutline()
        x0, y0, x1, y1 = rule_area_box
        for point in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            zone.Outline().Append(vec(*point))
        board.Add(zone)
    if include_keepout:
        keepout = pcbnew.PCB_SHAPE(board)
        keepout.SetShape(pcbnew.SHAPE_T_POLY)
        keepout.SetPolyPoints(pcbnew.VECTOR_VECTOR2I([
            vec(12, 4), vec(13, 4), vec(13, 6), vec(12, 6)]))
        keepout.SetLayer(pcbnew.User_2); keepout.SetFilled(False)
        keepout.SetWidth(pcbnew.FromMM(.05)); board.Add(keepout)
    for start, end in zip(((1 + outline_shift, 1), (15, 1), (15, 10), (1, 10)),
                          ((15, 1), (15, 10), (1, 10), (1, 1))):
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetStart(vec(*start)); edge.SetEnd(vec(*end))
        edge.SetWidth(pcbnew.FromMM(.05)); board.Add(edge)
    pcbnew.SaveBoard(str(path), board)


def fixture():
    root = tmpdir("coupled_geometry_")
    project = root / "project"
    (project / "03_src/rules").mkdir(parents=True)
    route = {
        "prep": {"keepouts": {"layers": ["User.2"]}},
        "route": {
            "preflight_critical_pairs": [],
            "no_critical_routes": "reduced fixture has no controlled pairs",
            "routability": {
                "coupled_neighborhoods": [{
                    "id": "clock-launches",
                    "nets": ["MCH_CLK", "ADC_TDM"],
                    "why": "adjacent source launches must coexist",
                }],
                "coupled_witness": "06_build/combined.kicad_pcb",
                "class_layers": {"ADC_CLOCK": ["F.Cu"]},
            },
            "common": {"layers": ["F.Cu", "B.Cu"]},
        }
    }
    nets = {
        "fab_tier": "jlc_2layer_default",
        "classes": {"ADC_CLOCK": {
            "nets": ["MCH_CLK", "ADC_TDM"], "min_width": "0.18mm"}},
        "reference_plane_checks": {"DIGITAL": {
            "signal_layer": "F.Cu", "reference_layer": "B.Cu",
            "reference_net": "GND", "signal_nets": ["MCH_CLK", "ADC_TDM"]}},
        "length_match": {"DIGITAL": {
            "members": {"MCH": ["MCH_CLK"], "ADC": ["ADC_TDM"]},
            "no_vias": True}},
    }
    (project / "03_src/route.yaml").write_text(json.dumps(route))
    (project / "03_src/rules/nets.yaml").write_text(json.dumps(nets))
    (project / "03_src/floorplan.yaml").write_text("{}\n")
    build = project / "06_build"; build.mkdir()
    prepared = build / "prepared.kicad_pcb"
    make_board(prepared)
    prepared.with_suffix(".kicad_pro").write_text(json.dumps({
        "board": {"design_settings": {"rules": {
            "min_clearance": .127, "min_track_width": .127}}}}))
    prepared.with_suffix(".kicad_dru").write_text(
        '(version 1)\n(rule "ADC_CLOCK_width"\n'
        '  (condition "A.NetClass == \'ADC_CLOCK\'")\n'
        '  (constraint track_width (min 0.18mm)))\n')
    return root, project, prepared, build / "combined.kicad_pcb"


BLOCKED = {
    "MCH_CLK": [(5, 5), (9, 5)],
    "ADC_TDM": [(7, 3), (7, 7)],
}
CORRECTED = {
    "MCH_CLK": [(5, 5), (9, 5)],
    "ADC_TDM": [(7, 3), (11, 3), (11, 7), (7, 7)],
}


@test("combined native crossing fails while alternate legal geometry passes")
def t_combined_collision_and_alternate():
    root, project, prepared, witness = fixture()
    make_board(witness, BLOCKED)
    blocked = coupled.grade(project, prepared, witness, root / "blocked-grade")
    eq(blocked["status"], "FAIL", "blocked combined witness")
    eq(blocked["checks"]["candidate"]["checks"]["physical_drc"]["hard_types"],
       ["tracks_crossing"], "exact historical classifier gap is now hard")
    make_board(witness, CORRECTED)
    accepted = coupled.grade(project, prepared, witness, root / "clean-grade")
    eq(accepted["status"], "PASS", "alternate combined witness")
    receipt_path = root / "coupled.json"
    coupled._atomic_json(receipt_path, accepted)
    eq(coupled.verify(receipt_path), (True, []), "receipt independent reopen")
    check(coupled.verify(root / "missing.json")[0] is False,
          "missing receipt refuses verification")


@test("witness cannot move prepared pads or omit a later required launch")
def t_source_identity_and_future_launch():
    root, project, prepared, witness = fixture()
    make_board(witness, CORRECTED, move_pad=True)
    moved = coupled.grade(project, prepared, witness, root / "moved-grade")
    eq(moved["status"], "FAIL", "moved prepared pad")
    eq(moved["checks"]["route_base"]["status"], "FAIL",
       "placement authority rejects before candidate grading")
    check(any("placement differs" in row
              for row in moved["checks"]["route_base"]["findings"]),
          "exact moved-pad finding")

    # The first branch is legal alone, but the declared later launch is absent.
    make_board(witness, {"MCH_CLK": BLOCKED["MCH_CLK"]})
    future = coupled.grade(project, prepared, witness, root / "future-grade")
    eq(future["status"], "FAIL", "missing later launch")
    eq(future["checks"]["candidate"]["checks"]["connectivity"]["status"],
       "FAIL", "full-pad connectivity blocks isolated success")


@test("existing no-via authority and absent evidence fail at distinct boundaries")
def t_no_via_and_incomplete():
    root, project, prepared, witness = fixture()
    make_board(witness, CORRECTED, add_via=True)
    via = coupled.grade(project, prepared, witness, root / "via-grade")
    eq(via["status"], "FAIL", "governed via")
    eq(via["checks"]["realized_policy"]["status"], "FAIL", "policy status")
    check(any("no_vias" in row
              for row in via["checks"]["realized_policy"]["findings"]),
          "existing no-via authority cited")
    forged = json.loads(json.dumps(via))
    for row in forged["checks"].values():
        row["status"] = "PASS"
    forged["status"] = "PASS"
    valid, failures = coupled.verify_mapping(forged)
    check(not valid and any("candidate check differs" in row
                            for row in failures),
          "rejected child cannot be wrapped as outer PASS")

    missing = coupled.grade(project, prepared, root / "absent.kicad_pcb",
                            root / "absent-grade")
    eq(missing["status"], "INCOMPLETE", "absent witness is unresolved")
    check(all("impossible" not in json.dumps(row).lower()
              for row in missing["checks"].values()),
          "absence never claims impossibility")


@test("prepared native width rules and source-owned layer policy both apply")
def t_width_and_layer():
    root, project, prepared, witness = fixture()
    make_board(witness, CORRECTED, width=.17)
    thin = coupled.grade(project, prepared, witness, root / "thin-grade")
    eq(thin["status"], "FAIL", "sub-floor width")
    eq(thin["checks"]["candidate"]["checks"]["physical_drc"]["hard_types"],
       ["track_width"], "prepared scoped rule grades width")

    make_board(witness, CORRECTED, route_layer=pcbnew.B_Cu)
    back = coupled.grade(project, prepared, witness, root / "back-grade")
    eq(back["status"], "FAIL", "forbidden signal layer")
    check(any("outside ['F.Cu']" in row
              for row in back["checks"]["realized_policy"]["findings"]),
          "source-owned layer authority cited")

    make_board(witness, CORRECTED, width=.20)
    nets_path = project / "03_src/rules/nets.yaml"
    nets = json.loads(nets_path.read_text())
    nets["classes"]["ADC_CLOCK"]["min_width"] = "0.25mm"
    nets_path.write_text(json.dumps(nets))
    stale = coupled.grade(project, prepared, witness, root / "stale-grade")
    eq(stale["status"], "FAIL", "current source defeats stale permissive DRU")
    eq(stale["checks"]["candidate"]["status"], "FAIL",
       "regenerated native class width finding")

    nets["classes"]["ADC_CLOCK"]["min_width"] = "0.18mm"
    nets["scoped_floors"] = [{
        "zone": "LAUNCH_LOCAL", "nets": ["MCH_CLK"],
        "min_width": "0.25mm", "why": "mutation control",
    }]
    nets_path.write_text(json.dumps(nets))
    scoped = coupled.grade(project, prepared, witness, root / "scoped-grade")
    eq(scoped["status"], "FAIL", "current scoped source defeats stale DRU")
    eq(scoped["checks"]["candidate"]["status"], "FAIL",
       "regenerated scoped source width finding")

    nets.pop("scoped_floors")
    nets["classes"] = {}
    nets["default_track_width"] = "0.25mm"
    nets_path.write_text(json.dumps(nets))
    default = coupled.grade(project, prepared, witness, root / "default-grade")
    eq(default["status"], "FAIL", "current Default source defeats stale DRU")
    eq(default["checks"]["realized_policy"]["status"], "FAIL",
       "explicit Default source width finding")


@test("current scoped clearance is regenerated before native admission")
def t_current_scoped_clearance():
    root, project, prepared, witness = fixture()
    box = (4, 4, 10, 5.5)
    make_board(prepared, rule_area_box=box)
    close = {
        "MCH_CLK": [(5, 5), (9, 5)],
        "ADC_TDM": [(7, 3), (5, 3), (5, 4.6), (9, 4.6),
                    (9, 7), (7, 7)],
    }
    make_board(witness, close, rule_area_box=box)
    nets_path = project / "03_src/rules/nets.yaml"
    nets = json.loads(nets_path.read_text())
    nets["scoped_clearances"] = [{
        "zone": "LAUNCH_LOCAL", "nets_a": ["MCH_CLK"],
        "nets_b": ["ADC_TDM"], "clearance": "0.5mm",
        "why": "mutation control",
    }]
    nets_path.write_text(json.dumps(nets))
    result = coupled.grade(project, prepared, witness, root / "clearance-grade")
    eq(result["status"], "FAIL", "current scoped clearance blocks stale DRU")
    eq(result["checks"]["candidate"]["status"], "FAIL",
       "regenerated scoped clearance reaches native DRC")


@test("witness cannot enlarge scoped rule areas or delete prepared keepouts")
def t_nonrouting_authority():
    root, project, prepared, witness = fixture()
    make_board(witness, CORRECTED, rule_area_box=(5.5, 4.3, 6.7, 5.7))
    enlarged = coupled.grade(project, prepared, witness, root / "area-grade")
    eq(enlarged["status"], "FAIL", "modified rule area")
    check(any("rule-area/keepout geometry" in row
              for row in enlarged["checks"]["route_base"]["findings"]),
          "rule-area authority finding")

    make_board(witness, CORRECTED, include_keepout=False)
    removed = coupled.grade(project, prepared, witness, root / "keepout-grade")
    eq(removed["status"], "FAIL", "removed prepared keepout")
    check(any("keepout-layer drawings" in row
              for row in removed["checks"]["route_base"]["findings"]),
          "keepout drawing authority finding")

    make_board(witness, CORRECTED, outline_shift=.2)
    outline = coupled.grade(project, prepared, witness, root / "outline-grade")
    eq(outline["checks"]["route_base"]["status"], "FAIL",
       "changed outline rejected")
    check(any("Edge.Cuts geometry" in row
              for row in outline["checks"]["route_base"]["findings"]),
          "outline authority finding")

    make_board(witness, CORRECTED, copper_layers=4)
    stack = coupled.grade(project, prepared, witness, root / "stack-grade")
    eq(stack["checks"]["route_base"]["status"], "FAIL",
       "changed enabled copper stack rejected")
    check(any("enabled copper stack" in row
              for row in stack["checks"]["route_base"]["findings"]),
          "stack authority finding")


@test("leaf CLI preserves immutable attempt evidence and binds native runtime")
def t_cli_immutable_runtime():
    root, project, prepared, witness = fixture()
    make_board(witness, CORRECTED)
    workspace, receipt = root / "cli-workspace", root / "cli.json"
    script = Path(coupled.__file__).resolve()
    command = ["/usr/bin/python3", str(script), "grade", str(project),
               "--prepared", str(prepared), "--witness", str(witness),
               "--workspace", str(workspace), "--json", str(receipt)]
    first = subprocess.run(command, text=True, capture_output=True)
    eq(first.returncode, 0, first.stdout + first.stderr)
    before = receipt.read_bytes()
    second = subprocess.run(command, text=True, capture_output=True)
    eq(second.returncode, 2, "reused attempt refuses admission")
    eq(receipt.read_bytes(), before, "prior outer receipt remains immutable")
    value = json.loads(before)
    check({"kicad_cli", "kicad_python", "pcbnew_module", "pcbnew_native",
           "rules_generator", "current_rules_rules"} <=
          set(value["inputs"]), "native executables/modules hash-bound")
    eq(value["coverage"]["checks_total"], 3, "closed check denominator")


@test("placement compositor consumes and binds the combined witness receipt")
def t_placement_composition():
    root, project, prepared, witness = fixture()
    make_board(witness, CORRECTED)
    receipt = placement.grade(
        project, prepared, coupled_workspace=root / "placement-coupled")
    eq(receipt["checks"]["coupled_geometry"]["status"], "PASS",
       "placement combined check")
    check("coupled_child_receipt" in receipt["inputs"],
          "placement binds verified child receipt")
    check("coupled_authority_parser" in receipt["inputs"],
          "placement binds native authority parser")
    forged = json.loads(json.dumps(receipt))
    forged["checks"]["coupled_geometry"]["status"] = "FAIL"
    forged_path = root / "placement-forged.json"
    placement._atomic_json(forged_path, forged)
    valid, failures = placement.verify(forged_path)
    check(not valid and any("coupled check status differs" in row
                            for row in failures),
          "placement cannot misstate coupled report status")
    eq(receipt["checks"]["pair_footprint"]["status"], "N-A",
       "ordinary fixture has no controlled pair")
    forged_pair = json.loads(json.dumps(receipt))
    forged_pair["checks"]["pair_footprint"]["status"] = "PASS"
    forged_pair_path = root / "placement-pair-forged.json"
    placement._atomic_json(forged_pair_path, forged_pair)
    valid, failures = placement.verify(forged_pair_path)
    check(not valid and any("pair footprint report differs" in row
                            for row in failures),
          "placement cannot launder pair footprint report")
    receipt_path = root / "placement.json"
    placement._atomic_json(receipt_path, receipt)
    eq(placement.verify(receipt_path), (True, []),
       "placement receipt independently reopens coupled evidence")


def pair_footprint_fixture(*, xu_pitch=.8, xu_neighbor_gap=None,
                           omit_esd=False, scoped=False, rotate=False,
                           unnetted_neighbor=False, duplicate_foreign=False):
    root = tmpdir("pair_footprint_")
    project = root / "project"
    (project / "03_src/rules").mkdir(parents=True)
    dossier = project / "02_parts/CONNECTOR/part.yaml"
    dossier.parent.mkdir(parents=True)
    dossier.write_text(json.dumps({"mpn": "CONNECTOR", "pin_aliases": {
        "A6": {"schematic": "4", "footprint": "A6"},
        "A7": {"schematic": "5", "footprint": "A7"},
        "B6": {"schematic": "12", "footprint": "B6"},
        "B7": {"schematic": "13", "footprint": "B7"}}}))
    paths = {side: [{"id": name, "segments": [{"net": net,
              "from": source, "to": f"U1.{pin}"}]} for name, source in starts]
             for side, net, pin, starts in (
                 ("P", "DP", "60", [("a", "J1.4"), ("b", "J1.12"),
                                     ("esd", "D1.1")]),
                 ("N", "DN", "59", [("a", "J1.5"), ("b", "J1.13"),
                                     ("esd", "D1.2")]))}
    route = {"route": {"preflight_critical_pairs": [{
        "name": "USB", "p": "DP", "n": "DN", "wave": "usb"}],
        "waves": [{"name": "usb", "track_width": .41,
                   "diff_pair_gap": .15, "layers": ["F.Cu"]}]}}
    nets = {"default_clearance": ".15mm", "classes": {"USB": {
        "nets": ["DP", "DN"], "min_width": ".41mm",
        "clearance": ".15mm", "diff_pair": {"width": ".41mm",
                                            "gap": ".15mm"}}},
        "length_match": {"USB": {"members": {"P": ["DP"], "N": ["DN"]},
                                 "paths": paths}},
        "same_footprint_pad_clearances": [{"refs": ["U1"],
                                            "clearance": ".15mm"}]}
    if scoped:
        nets["scoped_clearances"] = [{"zone": "XU_LOCAL", "nets_a": ["DP"],
                                       "nets_b": ["DN"], "clearance": ".1mm"}]
    (project / "03_src/route.yaml").write_text(json.dumps(route))
    (project / "03_src/rules/nets.yaml").write_text(json.dumps(nets))
    board = pcbnew.BOARD()
    nets_native = {}
    for name in ("DP", "DN", "GND"):
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net); nets_native[name] = net
    def footprint(ref, value):
        fp = pcbnew.FOOTPRINT(board)
        fp.SetReference(ref); fp.SetValue(value); board.Add(fp)
        return fp
    def pad(fp, number, net, x, y, size=(.25, 1.475), angle=90,
            shape=pcbnew.PAD_SHAPE_ROUNDRECT):
        item = pcbnew.PAD(fp)
        item.SetNumber(number); item.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        item.SetShape(shape); item.SetSize(vec(*size))
        if shape == pcbnew.PAD_SHAPE_ROUNDRECT:
            item.SetRoundRectRadiusRatio(.2)
        item.SetOrientationDegrees(angle)
        layers = pcbnew.LSET(); layers.AddLayer(pcbnew.F_Cu)
        item.SetLayerSet(layers); fp.Add(item)
        item.SetPosition(vec(x, y))
        if net:
            item.SetNet(nets_native[net])
        return item
    j = footprint("J1", "CONNECTOR")
    for number, net, x in (("A6", "DP", 1), ("A7", "DN", 2),
                           ("B6", "DP", 3), ("B7", "DN", 4)):
        pad(j, number, net, x, 1, size=(.3, 1), angle=0)
    d = footprint("D1", "ESD")
    if not omit_esd:
        pad(d, "1", "DP", 1, 5, size=(.3, .3), angle=0)
    pad(d, "2", "DN", 2, 5, size=(.3, .3), angle=0)
    u = footprint("U1", "PHY")
    if rotate:
        pad(u, "59", "DN", 10, 10, size=(1.475, .25), angle=0)
        pad(u, "60", "DP", 10, 10 + xu_pitch,
            size=(1.475, .25), angle=0)
    else:
        pad(u, "59", "DN", 10, 10)
        pad(u, "60", "DP", 10, 10 + xu_pitch)
    if xu_neighbor_gap is not None:
        pad(u, "58", "" if unnetted_neighbor else "GND", 10,
            10 - (.25 + xu_neighbor_gap))
        if duplicate_foreign:
            pad(u, "58", "GND", 20, 20)
    return root, project, board, route, nets


@test("early pair footprint uses all alias-resolved connector and ESD leaves")
def t_pair_footprint_aliases_and_missing():
    _, project, board, route, nets = pair_footprint_fixture()
    clean = placement._pair_footprints(project, board, route, nets)
    eq(clean["status"], "PASS", "wide centered terminals")
    eq(len(clean["pairs"]), 8, "four connector, two ESD, two PHY pads")
    check(all(row["source_declared"] for row in clean["pairs"]),
          "all source aliases resolved")
    _, project, board, route, nets = pair_footprint_fixture(omit_esd=True)
    missing = placement._pair_footprints(project, board, route, nets)
    eq(missing["status"], "INCOMPLETE", "missing source ESD leaf")
    check(any("D1.1" in row for row in missing["unresolved"]),
          "missing exact endpoint named")
    _, project, board, route, nets = pair_footprint_fixture()
    route["route"]["preflight_critical_pairs"][0]["name"] = "USB"
    next(row for row in nets["length_match"]["USB"]["paths"]["P"]
         if row["id"] == "esd")["segments"] = []
    undeclared = placement._pair_footprints(project, board, route, nets)
    eq(undeclared["status"], "INCOMPLETE", "stale source omits ESD leaf")
    check(any("D1.1" in row for row in undeclared["unresolved"]),
          "undeclared native terminal exposed")


@test("centered native envelope detects rotated pitch and foreign pad clearance")
def t_pair_footprint_geometry():
    _, project, board, route, nets = pair_footprint_fixture(xu_pitch=.4,
                                                               rotate=True)
    tight = placement._pair_footprints(project, board, route, nets)
    eq(tight["status"], "FAIL", "rotated roundrect centered launch")
    check(any("U1.59 conflicts with U1.60" in row for row in tight["findings"]),
          "pair gap applied at rotated pad")
    _, project, board, route, nets = pair_footprint_fixture(
        xu_neighbor_gap=.10)
    foreign = placement._pair_footprints(project, board, route, nets)
    eq(foreign["status"], "FAIL", "pad gap below global clearance")
    check(any("pad copper U1.59 to U1.58 below 0.150" in row
              for row in foreign["findings"]), "D15-like pad copper gap")
    _, project, board, route, nets = pair_footprint_fixture(
        xu_neighbor_gap=.15, unnetted_neighbor=True)
    blank = placement._pair_footprints(project, board, route, nets)
    eq(blank["status"], "FAIL", "unnetted pad remains foreign copper")
    check(any("launch envelope at U1.59 conflicts with U1.58" in row
              for row in blank["findings"]), "pad exception cannot waive track gap")
    _, project, board, route, nets = pair_footprint_fixture(
        xu_neighbor_gap=.15, unnetted_neighbor=True, duplicate_foreign=True)
    duplicate = placement._pair_footprints(project, board, route, nets)
    eq(duplicate["status"], "FAIL", "same-number foreign pads both screened")
    check(any("launch envelope at U1.59 conflicts with U1.58" in row
              for row in duplicate["findings"]), "near duplicate pad not collapsed")
    _, project, board, route, nets = pair_footprint_fixture(xu_pitch=.45)
    nets["classes"]["USB"]["diff_pair"]["gap"] = ".10mm"
    route["route"]["waves"][0]["diff_pair_gap"] = .10
    gap = placement._pair_footprints(project, board, route, nets)
    eq(gap["status"], "FAIL", "class clearance exceeds nominal pair gap")
    check(any("U1.59 conflicts with U1.60 (0.150 mm clearance)" in row
              for row in gap["findings"]), "effective pair track-to-pad clearance")
    _, project, board, route, nets = pair_footprint_fixture(xu_pitch=.8)
    nets["classes"]["USB"]["diff_pair"]["gap"] = ".10mm"
    route["route"]["waves"][0]["diff_pair_gap"] = .10
    wide = placement._pair_footprints(project, board, route, nets)
    eq(wide["status"], "FAIL", "source rule conflict independent of geometry")
    check(any("below unscoped effective clearance" in row
              for row in wide["findings"]), "numeric source rule conflict")


@test("partial scoped pair rules and ordinary boards cannot fabricate a pass")
def t_pair_footprint_scope_and_na():
    _, project, board, route, nets = pair_footprint_fixture(scoped=True)
    nets["classes"]["USB"]["diff_pair"]["gap"] = ".10mm"
    route["route"]["waves"][0]["diff_pair_gap"] = .10
    scoped = placement._pair_footprints(project, board, route, nets)
    eq(scoped["status"], "INCOMPLETE", "scoped rule requires local evaluation")
    check(any("uncovered terminal centers" in row for row in scoped["findings"]),
          "partial scoped exception exposes global gap at other terminals")
    _, project, board, route, nets = pair_footprint_fixture()
    nets["default_clearance"] = ".20mm"
    classed = placement._pair_footprints(project, board, route, nets)
    eq(classed["status"], "PASS", "Default does not widen two explicit pair nets")
    route["route"]["preflight_critical_pairs"] = []
    omitted = placement._pair_footprints(project, board, route, nets)
    eq(omitted["status"], "INCOMPLETE", "length pair cannot disappear from route")
    nets["length_match"] = {}
    nets["classes"] = {}
    ordinary = placement._pair_footprints(project, board, route, nets)
    eq(ordinary["status"], "N-A", "no pair declaration")


@test("early pair CLI reads a small native board without changing input files")
def t_pair_footprint_cli_read_only():
    root, project, board, _, _ = pair_footprint_fixture()
    board_path = root / "small.kicad_pcb"
    pcbnew.SaveBoard(str(board_path), board)
    before = {str(path): path.read_bytes() for path in root.rglob("*")
              if path.is_file()}
    result = subprocess.run(
        ["/usr/bin/python3", str(Path(placement.__file__).resolve()),
         "pair-footprint", str(project), "--board", str(board_path)],
        text=True, capture_output=True)
    eq(result.returncode, 0, result.stderr)
    eq(json.loads(result.stdout)["status"], "PASS", "early CLI verdict")
    after = {str(path): path.read_bytes() for path in root.rglob("*")
             if path.is_file()}
    eq(after, before, "early CLI leaves project and board bytes untouched")


@test("pair report regrade resolves project identity from named-board source")
def t_pair_footprint_named_board_verify():
    root, project, board, _, _ = pair_footprint_fixture()
    board_path = root / "small.kicad_pcb"
    pcbnew.SaveBoard(str(board_path), board)
    scoped = project / "03_src/demo"
    (scoped / "rules").mkdir(parents=True)
    route_path = project / "03_src/route.yaml"
    nets_path = project / "03_src/rules/nets.yaml"
    target_route = scoped / "route.yaml"
    target_nets = scoped / "rules/nets.yaml"
    route_path.rename(target_route)
    nets_path.rename(target_nets)
    rows = {name: {"status": "N-A"}
            for name in placement.AUTHORITATIVE_CHECKS}
    rows["pair_footprint"] = placement._pair_footprints(
        project, board, json.loads(target_route.read_text()),
        json.loads(target_nets.read_text()))
    inputs = {"board": placement._record(board_path),
              "route": placement._record(target_route),
              "nets": placement._record(target_nets),
              "checker_placement": placement._record(Path(placement.__file__))}
    for dossier in (project / "02_parts").glob("*/part.yaml"):
        inputs["pair_part_" + dossier.parent.name] = placement._record(dossier)
    receipt = {"schema": 2, "kind": "placement-routability-receipt-v2",
               "verdict": "ACCEPTED", "subject": inputs["board"],
               "inputs": inputs, "checks": rows,
               "coverage": {"passing": len(rows), "total": len(rows)}}
    path = root / "named.json"
    placement._atomic_json(path, receipt)
    eq(placement.verify(path), (True, []), "named-board alias regrade")


if __name__ == "__main__":
    raise SystemExit(main())
