#!/usr/bin/env python3
"""T1: generate_board_generic.py — the generic board generator.

Clean cases: parts land where the config says. Must-fail cases: a missing
FPID is a HARD ERROR (the defect that matters most — a silently un-placed
part is an electrically-wrong board that still passes DRC).
"""
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import (KPY, ROOT, SCRIPTS, board_nodes, check, contains, eq,  # noqa: E402
                     main, must_fail, must_pass, run, test, tmpdir)

GEN = SCRIPTS / "generate_board_generic.py"
MODEL_COVERAGE = SCRIPTS / "model_coverage_check.py"
LC = ROOT / "archived_projects" / "cook-loadcell"
HUB4 = ROOT / "archived_projects" / "usb-hub-3s-v4"
PLUTO_RX2 = ROOT / "archived_projects" / "pluto-rx2-8way"
CROW_USB = ROOT / "projects" / "crow-usb-carrier-v1"


@test("Crow native lands follow retained Samtec and TI drawings; old pads overlap",
      kind="known_bad")
def t_crow_native_lands_from_drawings():
    import pcbnew

    def page(path, n):
        return subprocess.check_output(
            ["pdftotext", "-f", str(n), "-l", str(n), "-layout",
             str(path), "-"], text=True)

    parts = CROW_USB / "02_parts"
    sam = page(parts / "FTSH-105-01-L-DV-K/Samtec_FTSH_footprint_revH.pdf", 1)
    dck = page(parts / "SN74LVC1G04DCKR/SN74LVC1G04-SCES214.pdf", 35)
    dct = page(parts / "SN74LVC2G74DCTR/SN74LVC2G74-SCES203Q.pdf", 20)

    def dimension(text, pattern):
        match = re.search(pattern, text)
        check(match is not None, f"manufacturer dimension missing: {pattern}")
        return float(match.group(1))

    # These are measured source dimensions, not a duplicate of the edited
    # footprint constants.  The opposing row spacing for Samtec is derived
    # from outer span minus pad length on the drawing.
    sam_pitch = dimension(sam, r"\.050\s+([0-9.]+)")
    sam_length = dimension(sam, r"\.110\s+([0-9.]+)")
    sam_width = dimension(sam, r"\.029\s+([0-9.]+)")
    sam_span = dimension(sam, r"\.270\s+([0-9.]+)")
    dck_lands = [float(x) for x in re.findall(r"5X \(([0-9.]+)\)", dck)]
    dct_lands = [float(x) for x in re.findall(r"8X \(([0-9.]+)\)", dct)]
    eq(len(dck_lands), 2, "DCK example gives length then width")
    eq(len(dct_lands), 2, "DCT example gives length then width")
    def row_separation(text):
        drawing = text.split("LAND PATTERN EXAMPLE", 1)[0]
        return float(re.findall(r"\(([0-9.]+)\)", drawing)[-1])
    cases = [
        ("Samtec_FTSH_105_01_L_DV_K", 10, sam_pitch, sam_length,
         sam_width, sam_span - sam_length),
        ("TI_DCK0005A_SC70_5", 5,
         dimension(dck, r"2X \(([0-9.]+)\)"),
         dck_lands[0], dck_lands[1], row_separation(dck)),
        ("TI_DCT0008A_SM8", 8,
         dimension(dct, r"6X \(([0-9.]+)\)"),
         dct_lands[0], dct_lands[1], row_separation(dct)),
    ]
    lib = CROW_USB / "03_src/lib/crow_usb_digital.pretty"
    tsx = (CROW_USB / "03_tscircuit/src/crow_usb_digital.tsx").read_text()

    def contacts(fp):
        return {p.GetNumber(): (pcbnew.ToMM(p.GetPosition().x),
                                pcbnew.ToMM(p.GetPosition().y),
                                pcbnew.ToMM(p.GetSize().x),
                                pcbnew.ToMM(p.GetSize().y))
                for p in fp.Pads()}

    def same_row_overlap(rows):
        return [(a, b) for a, pa in rows.items() for b, pb in rows.items()
                if a < b and math.isclose(pa[0], pb[0], abs_tol=1e-6)
                and abs(pa[1] - pb[1]) < (pa[3] + pb[3]) / 2 - 1e-6]

    for name, count, pitch, length, width, separation in cases:
        fp = pcbnew.FootprintLoad(str(lib), name)
        check(fp is not None, f"{name} loads")
        pads = contacts(fp)
        eq(set(pads), {str(i) for i in range(1, count + 1)},
           f"{name} retains pin identities")
        for x, y, sx, sy in pads.values():
            check(math.isclose(sx, length, abs_tol=1e-6) and
                  math.isclose(sy, width, abs_tol=1e-6),
                  f"{name} pad shape disagrees with manufacturer land")
        xs = sorted({v[0] for v in pads.values()})
        eq(len(xs), 2, f"{name} opposing rows")
        check(math.isclose(xs[1] - xs[0], separation, abs_tol=1e-6),
              f"{name} opposing row spacing")
        for x in xs:
            ys = sorted(v[1] for v in pads.values() if v[0] == x)
            step = 2 * pitch if count == 5 and len(ys) == 2 else pitch
            check(all(math.isclose(b - a, step, abs_tol=1e-6)
                      for a, b in zip(ys, ys[1:])), f"{name} contact pitch")
        eq(same_row_overlap(pads), [], f"{name} different nets have copper gap")
        # TI's land drawings label pin 1 at the upper left in a Y-down top
        # view. Samtec Fig 1 labels odd contacts on the lower row.  Checking
        # signed positions catches a mirrored footprint that passes all
        # width, pitch and short checks.
        if count == 10:
            check(pads["1"][1] > pads["9"][1] and
                  math.isclose(pads["1"][1], pads["2"][1], abs_tol=1e-6),
                  "Samtec odd/even orientation from Rev H Fig 1")
            expr = re.search(r"function FTSH2x5Land\(\).*?\sy=\{([^}]+)\}", tsx).group(1)
            tsx_pin1_y = eval(expr, {"__builtins__": {}}, {"row": 0})
        elif count == 5:
            check(pads["1"][1] < pads["2"][1] < pads["3"][1],
                  "DCK pin 1 is upper left in TI land drawing")
            expr = re.search(r"function SC70_5Land\(\).*?<P n=\{1\}.*?\sy=\{([^}]+)\}", tsx).group(1)
            tsx_pin1_y = eval(expr, {"__builtins__": {}}, {})
        else:
            check(pads["1"][1] < pads["2"][1] < pads["3"][1] < pads["4"][1],
                  "DCT pin 1 is upper left in TI land drawing")
            expr = re.search(r"function SM8_DCTLand\(\).*?\sy=\{([^}]+)\}", tsx).group(1)
            tsx_pin1_y = eval(expr, {"__builtins__": {}}, {"i": 0})
        check(math.isclose(float(tsx_pin1_y), -pads["1"][1], abs_tol=1e-6),
              f"{name} TSX Y-up and native KiCad Y-down pin 1 parity")
        # Recreate the formerly oversized along-pitch pad while retaining
        # the manufacturer's pitch: the collision detector must turn red.
        old_extent = {10: 1.5, 5: 1.0, 8: 1.2}[count]
        bad = {pin: (x, y, sx, old_extent) for pin, (x, y, sx, sy) in pads.items()}
        check(same_row_overlap(bad), f"{name} old overlong lands must fail")


@test("Crow DSE, DMQ and DCU lands follow TI pin-1 orientation and dimensions",
      kind="known_bad")
def t_crow_native_ti_chip_orientation():
    import pcbnew

    parts = CROW_USB / "02_parts"
    sources = [
        ("TI_DSE0006A_WSON6", "TPS389030DSER/TPS3890-SBVS228A.pdf", 25,
         6, 0.5, 0.25, 0.7),
        ("TI_DMQ0006A_VSON6", "TPS62825DMQR/TPS6282x-SLVSEF9I.pdf", 33,
         6, 0.5, 0.25, 0.6),
        ("TI_DCU0008A_VSSOP8", "SN74AUP3G34DCUR/SN74AUP3G34-SCES766C.pdf", 24,
         8, 0.5, 0.3, 0.85),
    ]
    lib = CROW_USB / "03_src/lib/crow_usb_digital.pretty"
    tsx = (CROW_USB / "03_tscircuit/src/crow_usb_digital.tsx").read_text()
    function = {"TI_DSE0006A_WSON6": "DSE0006ALand",
                "TI_DMQ0006A_VSON6": "DMQ0006ALand",
                "TI_DCU0008A_VSSOP8": "Dcu0008ALand"}
    for name, pdf, page_no, count, pitch, width, left_length in sources:
        drawing = subprocess.check_output(
            ["pdftotext", "-f", str(page_no), "-l", str(page_no),
             "-layout", str(parts / pdf), "-"], text=True)
        check("LAND PATTERN EXAMPLE" in drawing and
              "EXAMPLE BOARD LAYOUT" in drawing, f"{name} selected TI page")
        check(re.search(rf"\({pitch:g}\)", drawing) or
              re.search(rf"4X\s+{pitch:g}", drawing),
              f"{name} manufacturer pitch")
        check(re.search(rf"\({width:g}\)", drawing),
              f"{name} manufacturer width")
        check(re.search(rf"\({left_length:g}\)", drawing),
              f"{name} manufacturer left land length")
        fp = pcbnew.FootprintLoad(str(lib), name)
        check(fp is not None, f"{name} loads")
        pads = {p.GetNumber(): (pcbnew.ToMM(p.GetPosition().x),
                                pcbnew.ToMM(p.GetPosition().y),
                                pcbnew.ToMM(p.GetSize().x),
                                pcbnew.ToMM(p.GetSize().y)) for p in fp.Pads()}
        eq(set(pads), {str(i) for i in range(1, count + 1)},
           f"{name} pin set")
        check(pads["1"][1] < pads["2"][1] < pads["3"][1],
              f"{name} TI land drawing labels pin1 upper-left")
        check(all(math.isclose(pads[str(i+1)][1] - pads[str(i)][1], pitch,
                               abs_tol=1e-6) for i in range(1, count//2)),
              f"{name} left-side pitch")
        check(all(math.isclose(row[3], width, abs_tol=1e-6)
                  for row in pads.values()), f"{name} pad width")
        check(math.isclose(pads["2"][2], left_length, abs_tol=1e-6),
              f"{name} left land length")
        if count == 8:
            opposing = float(re.search(r"\(3\.1\)", drawing).group(0)[1:-1])
            check(math.isclose(pads["8"][0] - pads["1"][0], opposing,
                               abs_tol=1e-6), "DCU opposing row spacing")
        elif name == "TI_DSE0006A_WSON6":
            pin1_length = float(re.search(r"\(0\.8\)", drawing).group(0)[1:-1])
            check(math.isclose(pads["1"][2], pin1_length, abs_tol=1e-6),
                  "DSE pin1 has distinct manufacturer land length")
        else:
            right_length = float(re.search(r"3X \(1\)", drawing).group(0)[4:-1])
            check(all(math.isclose(pads[str(i)][2], right_length, abs_tol=1e-6)
                      for i in (4, 5, 6)), "DMQ long right lands")
        pattern = rf"function {function[name]}\(\).*?\sy=\{{([^}}]+)\}}"
        expr = re.search(pattern, tsx).group(1)
        tsx_pin1_y = eval(expr, {"__builtins__": {}}, {"i": 0})
        check(math.isclose(float(tsx_pin1_y), -pads["1"][1], abs_tol=1e-6),
              f"{name} TSX/native signed pin1 parity")
        bad = {pin: (x, -y, sx, sy) for pin, (x, y, sx, sy) in pads.items()}
        check(bad["1"][1] > bad["3"][1],
              f"{name} formerly mirrored pin sequence must fail")


@test("native USB4105 aliases preserve every logical contact and NC land")
def t_native_usb4105_aliases():
    import pcbnew
    sys.path.insert(0, str(SCRIPTS))
    from generate_board_generic import resolve_pad_aliases
    logical = {
        ("J_USB", str(i)): ("NC6" if i == 6 else "NC14" if i == 14 else
                            "GND" if i in (1, 8, 9, 16, 17) else
                            "VBUS" if i in (2, 7, 10, 15) else f"USB{i}")
        for i in range(1, 18)
    }
    mapped, expected = resolve_pad_aliases(
        {"J_USB": ("crow_usb_carrier_v1:GCT_USB4105_GF_A_120",
                   "USB4105-GF-A-120")}, logical, CROW_USB / "02_parts")
    fp = pcbnew.FootprintLoad(
        str(CROW_USB / "03_src/lib/crow_usb_carrier_v1.pretty"),
        "GCT_USB4105_GF_A_120")
    check(fp is not None, "native USB4105 footprint loads")
    physical = {p.GetNumber() for p in fp.Pads() if p.GetNumber()}
    eq(expected["J_USB"], physical, "all 17 declared physical contacts")
    eq(len(mapped), 17, "no logical contact dropped or merged")
    eq(mapped[("J_USB", "A8")], "NC6", "SBU1 no-connect")
    eq(mapped[("J_USB", "B8")], "NC14", "SBU2 no-connect")
    eq(mapped[("J_USB", "SH")], "GND", "shell")


@test("board alias resolver rejects unevidenced, missing and conflicting maps",
      kind="known_bad")
def t_native_alias_fail_closed():
    import yaml
    sys.path.insert(0, str(SCRIPTS))
    from generate_board_generic import FloorplanError, resolve_pad_aliases

    d = tmpdir("gbg_alias_")
    parts = d / "02_parts" / "PART"
    parts.mkdir(parents=True)
    base = {"mpn": "PART", "footprint": "fixture:part",
            "pins": {"A": "GND", "B": "NC", "C": "GND"},
            "pin_aliases": {
                "A": {"schematic": "1", "footprint": "A", "why": "drawing",
                      "evidence": "fixture drawing"},
                "B": {"schematic": "2", "footprint": "B", "why": "drawing",
                      "evidence": "fixture drawing"},
                "C": {"schematic": "3", "footprint": "C", "why": "drawing",
                      "evidence": "fixture drawing"}}}
    comps = {"J1": ("fixture:part", "PART")}

    def attempt(doc, nodes):
        (parts / "part.yaml").write_text(yaml.safe_dump(doc))
        return resolve_pad_aliases(comps, {("J1", k): v for k, v in nodes.items()},
                                   d / "02_parts")

    good, pins = attempt(base, {"1": "GND", "3": "GND"})
    eq(pins["J1"], {"A", "B", "C"}, "unused NC pad stays declared")
    eq(good, {("J1", "A"): "GND", ("J1", "C"): "GND"},
       "unconnected NC has no invented net")
    cases = [
        (lambda x: x["pin_aliases"]["A"].pop("evidence"),
         {"1": "GND"}, "why and evidence"),
        (lambda x: x["pin_aliases"].pop("B"),
         {"1": "GND", "2": "NC"}, "no evidenced alias"),
        (lambda x: x["pin_aliases"]["B"].update(
            {"footprint": "A", "fused": True}),
         {"1": "GND"}, "matching functions"),
        (lambda x: x["pin_aliases"]["C"].update(
            {"footprint": "A", "fused": True}),
         {"1": "GND", "3": "OTHER"}, "conflicting nets"),
    ]
    for change, nodes, message in cases:
        doc = json.loads(json.dumps(base))
        change(doc)
        try:
            attempt(doc, nodes)
        except FloorplanError as error:
            contains(str(error), message, "alias failure diagnostic")
        else:
            check(False, f"invalid alias passed: {message}")
    (parts / "part.yaml").write_text(yaml.safe_dump(base))
    try:
        resolve_pad_aliases({"J1": ("fixture:part", "UNKNOWN")},
                            {("J1", "1"): "GND"}, d / "02_parts")
    except FloorplanError as error:
        contains(str(error), "does not identify that part",
                 "same footprint cannot establish part identity")
    else:
        check(False, "unknown value borrowed alias from matching footprint")


@test("board aliases leave identity parts unchanged")
def t_native_alias_identity():
    sys.path.insert(0, str(SCRIPTS))
    from generate_board_generic import resolve_pad_aliases
    original = {("R1", "1"): "VIN", ("R1", "2"): "GND"}
    resolved, expected = resolve_pad_aliases(
        {"R1": ("Resistor_SMD:R_0402_1005Metric", "10k")},
        original, CROW_USB / "02_parts")
    eq(resolved, original, "native number and net preserved")
    eq(expected, {}, "no alias constraints for identity part")


def gen(cfg, out, cwd=LC, expect_ok=True):
    r = run([KPY, GEN, cfg, "-o", out], cwd=cwd)
    return must_pass(r, "generate_board_generic") if expect_ok else r


def scratch_config(mutate, name="fp.yaml"):
    """Copy cook-loadcell's real floorplan and mutate it — a known-bad
    fixture is a GOOD config broken in exactly one way."""
    import yaml
    d = tmpdir("gbg_")
    cfg = yaml.safe_load((LC / "03_src" / "floorplan.yaml").read_text())
    # the copy lives outside the project, so re-root its relative paths
    cfg["project"]["netlist"] = str(LC / cfg["project"]["netlist"])
    if cfg["project"].get("parts_dir"):
        cfg["project"]["parts_dir"] = str(LC / cfg["project"]["parts_dir"])
    mutate(cfg)
    p = d / name
    p.write_text(yaml.safe_dump(cfg))
    return d, p


def archived_config(project, scratch):
    """Recreate disposable netlist input from the committed native schematic.

    These real-board geometry fixtures must run in a clean checkout where
    archived 06_build/netlists is absent. Export into private scratch and
    retain every placement/rule value from the committed floorplan.
    """
    import yaml
    cfg = yaml.safe_load((project / '03_src/floorplan.yaml').read_text())
    stem = cfg['project']['name']
    netlist = scratch / f'{stem}.net'
    must_pass(run(['kicad-cli', 'sch', 'export', 'netlist', '-o', netlist,
                   project / '04_kicad' / f'{stem}.kicad_sch']),
              'export archived geometry fixture netlist')
    cfg['project']['netlist'] = str(netlist)
    cfg['project']['parts_dir'] = str(project / cfg['project']['parts_dir'])
    for index, entry in enumerate(cfg.get('libraries', [])):
        if isinstance(entry, dict):
            entry['path'] = str(project / entry['path'])
        else:
            cfg['libraries'][index] = str(project / entry)
    path = scratch / 'floorplan.yaml'
    path.write_text(yaml.safe_dump(cfg))
    return path


def _isolated_pad_consumer(patterns, *, sides=None, expected_alias_pads=None):
    """Call the real place_parts consumer with native pads, without a BOARD.

    The fake container owns Add/GetFootprints only. No BoardBuilder constructor,
    fill, save or routing is involved. Native getters are the independent oracle.
    Bottom-side Flip requires a native BOARD and is deliberately not exercised.
    """
    import pcbnew
    sys.path.insert(0, str(SCRIPTS))
    import generate_board_generic as g
    from types import SimpleNamespace
    from unittest.mock import patch

    class Container:
        def __init__(self): self.footprints = []
        def Add(self, fp): self.footprints.append(fp)
        def GetFootprints(self): return self.footprints

    def load(ref, fpid, val):
        fp = pcbnew.FootprintLoad(
            '/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0402_1005Metric')
        check(fp is not None, 'isolated native footprint available')
        return fp

    builder = object.__new__(g.BoardBuilder)
    builder.place_cfg = {'patterns': patterns,
                         'anchors': {r: [10, 20, 90] for r in ('C1', 'C2', 'R1')},
                         'sides': sides or {}}
    builder.comps = {r: ('fixture:native', 'fixture') for r in ('C1', 'C2', 'R1')}
    builder.identity_fields = {}
    builder.res = SimpleNamespace(load=load)
    builder.board = Container()
    builder.pad_net = {(r, n): ('GND' if n == '2' else 'OTHER')
                       for r in builder.comps for n in ('1', '2')}
    builder.expected_alias_pads = expected_alias_pads or {}
    builder.netmap = {'GND': pcbnew.NETINFO_ITEM(None, 'GND', 1),
                      'OTHER': pcbnew.NETINFO_ITEM(None, 'OTHER', 2)}
    builder.say = lambda message: None
    with patch.object(pcbnew, 'BOARD', side_effect=AssertionError('BOARD forbidden')), \
         patch.object(pcbnew, 'LoadBoard', side_effect=AssertionError('LoadBoard forbidden')), \
         patch.object(pcbnew, 'SaveBoard', side_effect=AssertionError('SaveBoard forbidden')):
        eq(builder.place_parts(), 3, 'actual consumer placement count')
    return builder


@test("board generator refuses a missing unconnected alias pad", kind="known_bad")
def t_native_alias_missing_nc_footprint_pad():
    sys.path.insert(0, str(SCRIPTS))
    from generate_board_generic import FloorplanError
    try:
        _isolated_pad_consumer([], expected_alias_pads={"C1": {"1", "2", "NC"}})
    except FloorplanError as error:
        contains(str(error), "missing ['NC']", "missing NC land diagnostic")
    else:
        check(False, "missing unconnected alias pad passed")


def _isolated_modes(builder):
    return {(fp.GetReference(), p.GetNumber()): p.GetLocalZoneConnection()
            for fp in builder.board.GetFootprints() for p in fp.Pads()}


@test('pad override consumer maps all three explicit modes on native pads')
def t_pad_override_native_modes():
    """RED against pre-fix consumer: NONE remained native INHERITED."""
    import pcbnew
    for mode, expected in [('full', pcbnew.ZONE_CONNECTION_FULL),
                           ('thermal', pcbnew.ZONE_CONNECTION_THERMAL),
                           ('none', pcbnew.ZONE_CONNECTION_NONE)]:
        b = _isolated_pad_consumer([{'match': ['C1'], 'pad_overrides': [
            {'pads': ['2'], 'on_net': 'GND', 'zone_connection': mode}]}])
        observed = _isolated_modes(b)
        eq(observed[('C1', '2')], expected, mode + ' native getter')
        for key, value in observed.items():
            if key != ('C1', '2'):
                eq(value, pcbnew.ZONE_CONNECTION_INHERITED, str(key))
        fp = b.fps['C1']
        eq(fp.GetLayer(), pcbnew.F_Cu, 'top-side unchanged')
        eq(fp.GetOrientationDegrees(), 90, 'rotation unchanged')
        eq(fp.GetPosition(), pcbnew.VECTOR2I_MM(10, 20), 'anchor unchanged')
        eq({p.GetNumber(): p.GetNetname() for p in fp.Pads()},
           {'1': 'OTHER', '2': 'GND'}, 'native net assignment precedes mode')


@test('pad override consumer preserves absent mode and clearance-only inheritance')
def t_pad_override_native_inheritance():
    import pcbnew
    for patterns in [[], [{'match': 'C*', 'pad_overrides': [{}]}],
                     [{'match': ['C1'], 'pad_overrides': [{'pads': ['2'], 'clearance': .3}]}]]:
        b = _isolated_pad_consumer(patterns)
        check(all(v == pcbnew.ZONE_CONNECTION_INHERITED for v in _isolated_modes(b).values()),
              'absent mode inherits')
    pad = next(p for p in b.fps['C1'].Pads() if p.GetNumber() == '2')
    eq(pad.GetLocalClearance(), pcbnew.FromMM(.3), 'clearance-only still applies')
    # A later clearance-only row must retain an earlier explicit mode.
    b = _isolated_pad_consumer([{'match': 'C1', 'pad_overrides': [
        {'zone_connection': 'full'}, {'clearance': .3}]}])
    eq(_isolated_modes(b)[('C1', '2')], pcbnew.ZONE_CONNECTION_FULL, 'later absence preserves full')


@test('pad override consumer retains generic glob, scalar, list, pad and net selectors')
def t_pad_override_native_generic_selectors():
    import pcbnew
    cases = [
        ({'match': 'C*', 'pad_overrides': [{'on_net': 'GND', 'zone_connection': 'full'}]},
         {('C1', '2'), ('C2', '2')}),
        ({'match': ['C?', 'R1'], 'pad_overrides': [{'pads': [1], 'zone_connection': 'full'}]},
         {('C1', '1'), ('C2', '1'), ('R1', '1')}),
        ({'match': '*', 'pad_overrides': [{'zone_connection': 'full'}]},
         {(r, n) for r in ('C1', 'C2', 'R1') for n in ('1', '2')}),
        ({'match': ['C1'], 'pad_overrides': [{'pads': ['1'], 'on_net': 'GND', 'zone_connection': 'full'}]}, set()),
        ({'match': ['ABSENT'], 'pad_overrides': [{'zone_connection': 'full'}]}, set()),
    ]
    for pattern, wanted in cases:
        modes = _isolated_modes(_isolated_pad_consumer([pattern]))
        eq({k for k, v in modes.items() if v == pcbnew.ZONE_CONNECTION_FULL}, wanted,
           'generic selector population')
        check(all(v == pcbnew.ZONE_CONNECTION_INHERITED for k, v in modes.items() if k not in wanted),
              'filtered native pads still inherit')


@test('pad override consumer rejects malformed modes even behind nonmatching selectors', kind='known_bad')
def t_pad_override_native_invalid_modes():
    """RED against pre-fix: typo accepted instead of FloorplanError."""
    sys.path.insert(0, str(SCRIPTS))
    import generate_board_generic as g
    for value in ['typo', 'FULL', ' none ', '', None, False, 0, 1, [], {}, ['none']]:
        for match, extra in [('C1', {}), ('ABSENT', {}), ('C1', {'pads': ['9']}),
                             ('C1', {'on_net': 'ABSENT'})]:
            try:
                _isolated_pad_consumer([{'match': match, 'pad_overrides': [
                    {'zone_connection': value, **extra}]}])
            except g.FloorplanError as error:
                contains(str(error), 'zone_connection', 'closed mode diagnostic')
                contains(str(error), 'full|thermal|none', 'valid enum diagnostic')
            else:
                check(False, f'invalid mode accepted: {value!r}, {match!r}, {extra!r}')


@test("generate_board_generic places every netlist part per the config")
def t_places():
    d = tmpdir("gbg_")
    out = d / "b.kicad_pcb"
    r = gen(LC / "03_src" / "floorplan.yaml", out)
    contains(r.out, "placed 29 footprints", "generator stdout")
    contains(r.out, "asserts: 8 passed", "generator stdout")
    check(out.is_file(), "no board written")
    nodes = board_nodes(out)
    # anchored parts must be exactly where the config put them, untouched
    # by the legalizer
    code = ("import pcbnew,sys\nb=pcbnew.LoadBoard(sys.argv[1])\n"
            "f=b.FindFootprintByReference('U1')\n"
            "print('@@%.3f,%.3f' % (pcbnew.ToMM(f.GetPosition().x),"
            " pcbnew.ToMM(f.GetPosition().y)))\n")
    rr = must_pass(run([KPY, "-c", code, out]), "probe U1")
    x, y = [float(v) for v in rr.out.split("@@")[1].strip().split(",")]
    check(abs(x - 38.0) < 0.001 and abs(y - 42.0) < 0.001,
          f"anchored U1 moved: ({x},{y}) != (38.0,42.0)")
    check(len(nodes) == 77, f"expected 77 netted pads, got {len(nodes)}")


@test("model_override is source-bound and the independent model coverage gate "
      "fails after that body disappears", kind="known_bad")
def t_model_override_and_coverage():
    import yaml
    d = tmpdir("gbg_model_")
    body = d / "body.step"
    body.write_text("ISO-10303-21;\nEND-ISO-10303-21;\n")
    cfg = yaml.safe_load((LC / "03_src" / "floorplan.yaml").read_text())
    cfg["project"]["netlist"] = str(LC / cfg["project"]["netlist"])
    if cfg["project"].get("parts_dir"):
        cfg["project"]["parts_dir"] = str(LC / cfg["project"]["parts_dir"])
    cfg["placement"].setdefault("patterns", []).append({
        "match": "*", "model_override": {
            "file": "${KIPRJMOD}/body.step",
            "offset": [1.25, -2.5, 0.1],
            "scale": [1, 1, 1],
            "rotate": [0, 0, 270],
        }})
    floorplan = d / "floorplan.yaml"
    floorplan.write_text(yaml.safe_dump(cfg))
    board = d / "board.kicad_pcb"
    built = gen(floorplan, board)
    contains(built.out, "3D model overrides: 29 footprints",
             "generator model-override coverage")

    clean = run([KPY, MODEL_COVERAGE, board])
    must_pass(clean, "model coverage on resolvable local bodies")
    # The cook-loadcell fixture has 29 generated component footprints, seven
    # deliberately excluded from its fitted BOM population.
    contains(clean.out, "PASS MODEL-COVERAGE: 22/22", "coverage verdict")

    code = ("import pcbnew,sys\n"
            "b=pcbnew.LoadBoard(sys.argv[1])\n"
            "m=list(b.FindFootprintByReference('U1').Models())[0]\n"
            "print('@@',m.m_Offset.x,m.m_Offset.y,m.m_Offset.z,"
            "m.m_Rotation.x,m.m_Rotation.y,m.m_Rotation.z)\n")
    probe = must_pass(run([KPY, "-c", code, board]),
                      "probe explicit model transform")
    contains(probe.out, "@@ 1.25 -2.5 0.1 0.0 0.0 270.0",
             "model_override mapping transform")

    body.unlink()
    broken = run([KPY, MODEL_COVERAGE, board])
    must_fail(broken, "model coverage after its source body is removed",
              "FAIL MODEL-COVERAGE: 0/22")


@test("placement.sides flips only named footprints and validates its closed "
      "top/bottom vocabulary", kind="known_bad")
def t_explicit_placement_sides():
    import yaml
    d, cfgp = scratch_config(
        lambda cfg: cfg["placement"].update({"sides": {"U1": "bottom"}}),
        "bottom.yaml")
    board = d / "bottom.kicad_pcb"
    built = gen(cfgp, board)
    contains(built.out, "placed 1 footprint(s) on B.Cu",
             "explicit bottom-side count")
    code = ("import pcbnew,sys\n"
            "b=pcbnew.LoadBoard(sys.argv[1])\n"
            "u=b.FindFootprintByReference('U1'); "
            "j=b.FindFootprintByReference('J1')\n"
            "print('@@',u.IsFlipped(),j.IsFlipped(),"
            "u.Reference().GetLayer()==pcbnew.B_SilkS,"
            "u.Reference().IsMirrored(),"
            "j.Reference().GetLayer()==pcbnew.F_SilkS,"
            "not j.Reference().IsMirrored(),"
            "any(t.GetClass()=='PCB_TEXT' and t.GetText()=='U1' and "
            "t.GetLayer()==pcbnew.B_Fab and t.IsMirrored() "
            "for t in b.GetDrawings()))\n")
    probe = must_pass(run([KPY, "-c", code, board]), "probe footprint sides")
    contains(probe.out, "@@ True False True True True True True",
             "bottom part keeps back-side silk/Fab text while default-top "
             "text remains unmirrored on the front")

    bad_d, bad_cfg = scratch_config(
        lambda cfg: cfg["placement"].update({"sides": {"U1": "inner"}}),
        "bad-side.yaml")
    bad = gen(bad_cfg, bad_d / "bad.kicad_pcb", expect_ok=False)
    must_fail(bad, "invalid placement side", "accepts only top|bottom")

    ghost_d, ghost_cfg = scratch_config(
        lambda cfg: cfg["placement"].update(
            {"sides": {"U_NOT_PRESENT": "bottom"}}), "ghost-side.yaml")
    ghost = gen(ghost_cfg, ghost_d / "ghost.kicad_pcb", expect_ok=False)
    must_fail(ghost, "unknown side refdes", "names unknown refdes")


@test("generate_board_generic writes an F.Fab refdes copy for every part")
def t_fab_copy():
    d = tmpdir("gbg_")
    out = d / "b.kicad_pcb"
    gen(LC / "03_src" / "floorplan.yaml", out)
    code = ("import pcbnew,sys\nb=pcbnew.LoadBoard(sys.argv[1])\n"
            "n=sum(1 for t in b.GetDrawings() if t.GetClass()=='PCB_TEXT'"
            " and t.IsOnLayer(pcbnew.F_Fab))\nprint('@@',n)\n")
    r = must_pass(run([KPY, "-c", code, out]), "count F.Fab")
    n = int(r.out.split("@@")[1].strip())
    check(n >= 33, f"expected >=33 F.Fab refdes copies (29 parts + 4 holes), got {n}")


@test("source identity fields survive generated-board save/reopen, decode escaped "
      "supplier JSON, and do not become required for legacy parts")
def t_source_identity_fields_round_trip():
    """Electrical source metadata wins over footprint-library defaults.

    The fixture adds authoritative identity fields only to U1.  It uses an
    escaped JSON supplier payload, then reads the SAVED board with pcbnew;
    the adjacent legacy J1 control proves omitted fields stay omitted.
    Before parse_identity_fields(), U1 had neither source value after the
    generated-board save/reopen, so this test failed while placement/parity
    remained green.
    """
    d = tmpdir("gbg_identity_")
    net = (LC / "06_build" / "netlists" / "cook_loadcell.net").read_text()
    match = re.search(r'(\(comp\s+\(ref\s+"U1"\).*?)(?=\(comp\s+\(ref|\(libparts)',
                      net, re.S)
    check(match is not None, "U1 fixture component was not found")
    component = match.group(1)
    supplier = '{"LCSC":"C12345","note":"quoted \\"source\\" value"}'
    fields = (f'\n(property (name {json.dumps("Manufacturer Part Number")}) '
              f'(value {json.dumps("SOURCE-MPN-42")}))'
              f'\n(property (name {json.dumps("Supplier Part Numbers")}) '
              f'(value {json.dumps(supplier)}))')
    value = re.search(r'\(value "(?:\\.|[^"\\])*"\)', component)
    check(value is not None, "U1 fixture has no value property")
    component = component[:value.end()] + fields + component[value.end():]
    identity_net = d / "identity.net"
    identity_net.write_text(net[:match.start()] + component + net[match.end():])
    import yaml
    cfg = yaml.safe_load((LC / "03_src" / "floorplan.yaml").read_text())
    cfg["project"]["netlist"] = str(identity_net)
    cfg["project"]["parts_dir"] = str(LC / cfg["project"]["parts_dir"])
    # Put an explicitly stale identity field in a private U1 footprint.  The
    # emitted board must take its MPN from the native netlist instead.
    stale_lib = d / "stale-footprints" / "Package_SO.pretty"
    stale_lib.mkdir(parents=True)
    source_mod = Path("/usr/share/kicad/footprints/Package_SO.pretty/"
                      "SOIC-16_3.9x9.9mm_P1.27mm.kicad_mod")
    stale_mod = stale_lib / source_mod.name
    stale_text = source_mod.read_text()
    stale_field = ('\n\t(property "Manufacturer Part Number" "STALE-LIBRARY-MPN"\n'
                   '\t\t(at 0 0 0)\n\t\t(layer "F.Fab")\n\t\t(hide yes)\n'
                   '\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n')
    stale_mod.write_text(stale_text.rstrip()[:-1] + stale_field + ')\n')
    cfg["libraries"] = [str(d / "stale-footprints"), "/usr/share/kicad/footprints"]
    floorplan = d / "floorplan.yaml"
    floorplan.write_text(yaml.safe_dump(cfg))
    board = d / "identity.kicad_pcb"
    gen(floorplan, board)
    # Saving via pcbnew first catches fields that exist only in generator
    # memory, rather than serialising into a KiCad board consumers can reopen.
    saved = d / "identity-saved.kicad_pcb"
    probe = (
        "import pcbnew,sys,json\n"
        "b=pcbnew.LoadBoard(sys.argv[1]); pcbnew.SaveBoard(sys.argv[2],b)\n"
        "b=pcbnew.LoadBoard(sys.argv[2])\n"
        "def fields(ref):\n"
        " return {f.GetName():f.GetText() for f in b.FindFootprintByReference(ref).GetFields()}\n"
        "print('@@'+json.dumps({'u1':fields('U1'),'j1':fields('J1')},sort_keys=True))\n")
    result = must_pass(run([KPY, "-c", probe, board, saved]),
                       "identity save/reopen probe")
    observed = json.loads(result.out.split("@@", 1)[1])
    eq(observed["u1"].get("Manufacturer Part Number"), "SOURCE-MPN-42",
       "source MPN overrides any stale library identity")
    eq(observed["u1"].get("Supplier Part Numbers"), supplier,
       "escaped supplier JSON survives source -> board -> reopen")
    check("Manufacturer Part Number" not in observed["j1"] and
          "Supplier Part Numbers" not in observed["j1"],
          "legacy part with no source identity fields was made to require them")


@test("MISSING FPID is a hard error, not a silent skip", kind="known_bad")
def t_missing_fpid():
    """The netlist's footprint field is blanked for one part and 02_parts
    has no override. The generator must REFUSE to build the board."""
    d = tmpdir("gbg_")
    net = (LC / "06_build" / "netlists" / "cook_loadcell.net").read_text()
    # blank U1's footprint exactly as a broken schematic footprint-map would
    i = net.index('(ref "U1")')
    j = net.index('(footprint "', i)
    k = net.index('"', j + 12)
    broken = net[:j] + '(footprint ""' + net[k + 1:]
    check(broken != net, "fixture did not actually blank the FPID")
    bad_net = d / "broken.net"
    bad_net.write_text(broken)

    import yaml
    cfg = yaml.safe_load((LC / "03_src" / "floorplan.yaml").read_text())
    cfg["project"]["netlist"] = str(bad_net)
    cfg["project"].pop("parts_dir", None)     # no override to rescue it
    p = d / "fp.yaml"
    p.write_text(yaml.safe_dump(cfg))

    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator on a blank-FPID netlist", "U1 has no footprint FPID")
    check(not (d / "b.kicad_pcb").exists(),
          "generator wrote a board despite the hard error")


@test("an FPID naming a footprint no library has is a hard error", kind="known_bad")
def t_unknown_footprint():
    d = tmpdir("gbg_")
    net = (LC / "06_build" / "netlists" / "cook_loadcell.net").read_text()
    broken = net.replace("Package_SO:SOIC-16_3.9x9.9mm_P1.27mm",
                         "Package_SO:NoSuchFootprint_ZZZ", 1)
    if broken == net:      # netlist uses a different U1 package — blanket swap
        import re as _re
        broken = _re.sub(r'\(footprint "[^"]*SOIC[^"]*"\)',
                         '(footprint "Package_SO:NoSuchFootprint_ZZZ")', net, count=1)
    check(broken != net, "fixture did not inject an unknown footprint")
    bad = d / "broken.net"
    bad.write_text(broken)
    import yaml
    cfg = yaml.safe_load((LC / "03_src" / "floorplan.yaml").read_text())
    cfg["project"]["netlist"] = str(bad)
    p = d / "fp.yaml"
    p.write_text(yaml.safe_dump(cfg))
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator on an unknown footprint", "footprint not found")


@test("a violated polarity assert blocks the build", kind="known_bad")
def t_bad_assert():
    """Flip a pad-net assert to the wrong net. The generator must refuse
    rather than ship a board with a backwards diode."""
    def mutate(cfg):
        for a in cfg["asserts"]["pad_net"]:
            if a["ref"] == "D1":
                a["net"] = "GND"          # D1 pad1 is really on DAT
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with a wrong polarity assert",
              "POLARITY/ROLE ASSERT: D1 pad 1")


@test("an over-subscribed floorplan fails loudly, not by stacking parts",
      kind="known_bad")
def t_legalizer_gives_up():
    """Shrink the legalizer's search radius to nothing while forcing every
    passive to start on the same point. It must raise, not silently leave
    parts overlapping."""
    def mutate(cfg):
        cfg["placement"]["seeds"] = {k: [38.0, 42.0] for k in cfg["placement"]["seeds"]}
        cfg["placement"]["legalize"]["ring_max"] = 2
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with an impossible floorplan", "no clear spot for")


@test("post_anchors moves only reviewed refs after legalization, preserving "
      "every other footprint position")
def t_post_anchors_preserve_legalizer_result():
    import yaml
    d = tmpdir("gbg_post_")
    base = yaml.safe_load((LC / "03_src" / "floorplan.yaml").read_text())
    base["project"]["netlist"] = str(LC / base["project"]["netlist"])
    if base["project"].get("parts_dir"):
        base["project"]["parts_dir"] = str(LC / base["project"]["parts_dir"])
    p0, p1 = d / "base.yaml", d / "post.yaml"
    p0.write_text(yaml.safe_dump(base))
    changed = yaml.safe_load(yaml.safe_dump(base))
    changed["placement"]["post_anchors"] = {"R1": [30.0, 39.5, 0]}
    p1.write_text(yaml.safe_dump(changed))
    b0, b1 = d / "base.kicad_pcb", d / "post.kicad_pcb"
    gen(p0, b0)
    r = gen(p1, b1)
    contains(r.out, "post-anchored 1 reviewed local part(s)",
             "generator stdout")
    code = (
        "import pcbnew,sys\n"
        "def poses(p):\n"
        " b=pcbnew.LoadBoard(p)\n"
        " return {f.GetReference():(f.GetPosition().x,f.GetPosition().y,"
        "round(f.GetOrientationDegrees(),6)) for f in b.GetFootprints()}\n"
        "a,c=poses(sys.argv[1]),poses(sys.argv[2])\n"
        "print('@@'+','.join(sorted(r for r in a if a[r]!=c[r])))\n")
    rr = must_pass(run([KPY, "-c", code, b0, b1]), "compare post anchors")
    eq(rr.out.split("@@", 1)[1].strip(), "R1",
       "post_anchors changed a footprint other than the named ref")


@test("a zone on a net the netlist does not have is a hard error", kind="known_bad")
def t_bad_zone_net():
    def mutate(cfg):
        cfg["zones"][0]["net"] = "GNDA"       # typo for GND
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with a typo'd zone net", "zone on unknown net")


@test("a multi-layer rule area really lands on every layer it declares")
def t_multilayer_rule_area():
    """The 4-layer plane/isolation path, in a unit test.

    cook-loadcell is 2-layer with no keepouts, so this asked the generator
    for something no existing floorplan did: a rule area on four layers of a
    board that HAS four layers.
    """
    def mutate(cfg):
        cfg["board"]["layers"] = 4
        cfg["keepouts"] = [{"name": "ANT", "deny": ["tracks", "vias", "pours"],
                            "layers": ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"],
                            "rect": [30, 30, 40, 40]}]
    d, p = scratch_config(mutate)
    out = d / "b.kicad_pcb"
    gen(p, out)
    code = ("import pcbnew,sys\nb=pcbnew.LoadBoard(sys.argv[1])\n"
            "z=[z for z in b.Zones() if z.GetIsRuleArea()][0]\n"
            "print('@@'+','.join(sorted(b.GetLayerName(l) "
            "for l in z.GetLayerSet().Seq())))\n")
    r = must_pass(run([KPY, "-c", code, out]), "probe rule area")
    got = r.out.split("@@")[1].strip()
    eq(got, "B.Cu,F.Cu,In1.Cu,In2.Cu", "rule area layer set")


@test("a PERMISSIVE named rule area forbids nothing (it is a DRU anchor)")
def t_permissive_rule_area():
    """`deny: []` with a name is a real and distinct use: the area exists
    only so generate_rules.py can scope a .kicad_dru rule to
    insideArea('<name>') (cook-hub's u7_taps, usb-power-3s's SW_TAP_A/B).
    An implementation that always denies would silently fence off copper on
    boards whose rules depend on that area being open."""
    def mutate(cfg):
        cfg["keepouts"] = [{"name": "SW_TAP", "deny": [],
                            "layers": ["F.Cu"], "rect": [30, 30, 40, 40]}]
    d, p = scratch_config(mutate)
    out = d / "b.kicad_pcb"
    gen(p, out)
    code = ("import pcbnew,sys\nb=pcbnew.LoadBoard(sys.argv[1])\n"
            "z=[z for z in b.Zones() if z.GetIsRuleArea()][0]\n"
            "print('@@%s|%s' % (z.GetZoneName(), ','.join(str(int(v)) for v in ("
            "z.GetDoNotAllowTracks(), z.GetDoNotAllowVias(),"
            " z.GetDoNotAllowPads(), z.GetDoNotAllowZoneFills()))))\n")
    r = must_pass(run([KPY, "-c", code, out]), "probe permissive rule area")
    name, flags = r.out.split("@@")[1].strip().split("|")
    eq(name, "SW_TAP", "rule area name (generate_rules scopes .kicad_dru to it)")
    eq(flags, "0,0,0,0", "a permissive rule area must forbid NOTHING")


@test("a ref-bound package rule area follows realised copper pads")
def t_ref_bound_rule_area():
    """Package-local DRU scopes must move with the package.  A static rect
    survived a USB-switch translation and silently left all ten pads outside
    the intended clearance exception."""
    def mutate(cfg):
        cfg["keepouts"] = [{"name": "FOLLOW_J1", "deny": [],
                            "layers": ["F.Cu"], "ref": "J1",
                            "margin_mm": 0.4}]
    d, p = scratch_config(mutate)
    out = d / "b.kicad_pcb"
    gen(p, out)
    code = ("import pcbnew,sys\n"
            "b=pcbnew.LoadBoard(sys.argv[1])\n"
            "f=b.FindFootprintByReference('J1')\n"
            "pbs=[p.GetBoundingBox() for p in f.Pads()]\n"
            "z=[z for z in b.Zones() if z.GetZoneName()=='FOLLOW_J1'][0]\n"
            "q=z.GetBoundingBox()\n"
            "v=(min(x.GetLeft() for x in pbs)-q.GetLeft(),"
            "min(x.GetTop() for x in pbs)-q.GetTop(),"
            "q.GetRight()-max(x.GetRight() for x in pbs),"
            "q.GetBottom()-max(x.GetBottom() for x in pbs))\n"
            "print('@@'+','.join('%.3f'%pcbnew.ToMM(x) for x in v))\n")
    r = must_pass(run([KPY, "-c", code, out]), "probe ref-bound rule area")
    eq(r.out.split("@@")[1].strip(), "0.400,0.400,0.400,0.400",
       "ref-bound rule area pad margins")


@test("a ref-bound rule area with an unknown owner is a hard error",
      kind="known_bad")
def t_ref_bound_rule_area_unknown_ref():
    def mutate(cfg):
        cfg["keepouts"] = [{"name": "LOST", "deny": [],
                            "layers": ["F.Cu"], "ref": "U_DOES_NOT_EXIST",
                            "margin_mm": 0.4}]
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with a ref-bound area whose owner is absent",
              "unknown ref 'U_DOES_NOT_EXIST'")


@test("a rule area on a layer the stackup does not have is a hard error",
      kind="known_bad")
def t_rule_area_layer_not_in_stackup():
    """Found while proving the 4-layer path: `LSET` accepts In1.Cu on a
    2-layer board without complaint, so a rule area (or plane) could be
    declared on a layer that does not exist. It never fills, DRC is clean,
    and the isolation you asked for is simply absent."""
    def mutate(cfg):
        cfg["board"]["layers"] = 2                    # ...but ask for inners
        cfg["keepouts"] = [{"name": "ANT", "deny": ["tracks"],
                            "layers": ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"],
                            "rect": [30, 30, 40, 40]}]
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with a rule area off the stackup",
              "not in the stackup")


@test("a PLANE on a layer the stackup does not have is a hard error",
      kind="known_bad")
def t_zone_layer_not_in_stackup():
    """Same defect on the pour path — an inner GND plane that silently is
    not there is worse than a missing keepout."""
    def mutate(cfg):
        cfg["board"]["layers"] = 2
        cfg["zones"].append({"net": "GND", "layers": ["In1.Cu"], "priority": 0})
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with a plane off the stackup", "not in the stackup")


@test("a 6-layer board places inner GND planes on In3.Cu and In4.Cu")
def t_six_layer_inner_planes():
    """The mixed-signal-audio-hub (crow-recorder-central-v2) needs a 6-layer
    In1+In4 GND-plane stackup. generate_board_generic's LAYER_NAMES/INNER_LAYERS
    must know In3.Cu/In4.Cu — before they did not, and a declared In4.Cu plane
    failed 'zone on GND on unknown layer In4.Cu' (the error that surfaced
    building central-v2). This is the GREEN half; reverting the In3/In4 rows in
    LAYER_NAMES/INNER_LAYERS turns it RED (verified 2026-07-23)."""
    def mutate(cfg):
        cfg["board"]["layers"] = 6
        cfg["zones"].append({"net": "GND", "layers": ["In3.Cu", "In4.Cu"],
                             "priority": 0})
    d, p = scratch_config(mutate)
    out = d / "b.kicad_pcb"
    gen(p, out)
    code = ("import pcbnew,sys\nb=pcbnew.LoadBoard(sys.argv[1])\n"
            "ls=set()\n"
            "for z in b.Zones():\n"
            "  if not z.GetIsRuleArea():\n"
            "    ls|={b.GetLayerName(l) for l in z.GetLayerSet().Seq()}\n"
            "print('@@'+','.join(sorted(ls)))\n")
    r = must_pass(run([KPY, "-c", code, out]), "probe inner planes")
    got = r.out.split("@@")[1].strip()
    contains(got, "In3.Cu", "GND plane on In3.Cu")
    contains(got, "In4.Cu", "GND plane on In4.Cu")


@test("an In4.Cu plane on a 4-layer board is a hard error", kind="known_bad")
def t_in4_needs_six_layers():
    """In4.Cu is in LAYER_NAMES but INNER_LAYERS requires >=6 copper layers;
    declaring it on a 4-layer board must be REJECTED by check_layer, not
    silently dropped onto a layer the stackup lacks (the same failure class as
    t_zone_layer_not_in_stackup, one layer up)."""
    def mutate(cfg):
        cfg["board"]["layers"] = 4
        cfg["zones"].append({"net": "GND", "layers": ["In4.Cu"], "priority": 0})
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with an In4 plane on a 4-layer board",
              "not in the stackup")


@test("a bbox_override on a part the legalizer may move is a hard error",
      kind="known_bad")
def t_bbox_override_unpinned():
    """A bbox_override is an ABSOLUTE rect. On a floating part it would go
    stale the moment the legalizer moved it, and every later collision test
    would be computed against empty space."""
    def mutate(cfg):
        cfg["placement"]["bbox_override"] = {"C1": [30, 30, 40, 40]}
        cfg["placement"]["pin"] = ["U*"]          # C1 floats
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with a bbox_override on a floating part",
              "which the legalizer may move")


@test("a connector whose mouth faces the wrong way blocks the build",
      kind="known_bad")
def t_body_offset_assert():
    """`body_offset` is the only check that catches a 180-degree flip of a
    connector whose pads are symmetric — pad_order cannot see it."""
    def mutate(cfg):
        cfg.setdefault("asserts", {})["body_offset"] = [
            {"ref": "J1", "axis": "x", "sign": "+"},
            {"ref": "J1", "axis": "x", "sign": "-"},   # both cannot hold
        ]
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with a contradictory body_offset assert",
              "opening faces the wrong way")


@test("an edge connector whose mouth faces away from its declared board edge "
      "blocks the build", kind="known_bad")
def t_edge_faces_assert():
    """Board-edge intent must be explicit.  Contradictory x0/x1 claims prove
    the realised footprint geometry is consumed without depending on the
    fixture connector's particular authored rotation convention."""
    def mutate(cfg):
        cfg.setdefault("asserts", {})["edge_faces"] = [
            {"ref": "J1", "edge": "x0"},
            {"ref": "J1", "edge": "x1"},   # both cannot hold
        ]
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with a connector facing away from its board edge",
              "mating face points away from its declared board edge")


@test("a functional pad bank facing away from its adjacent cell blocks the "
      "build", kind="known_bad")
def t_pad_bank_faces_assert():
    """Proximity cannot distinguish a mux/ESD body whose signal bank faces
    its neighbour from the same body rotated 180 degrees.  Two opposing bank
    claims cannot both be true, so this fixture is independent of the exact
    cook-loadcell placement while proving the realised-pad check bites."""
    def mutate(cfg):
        cfg.setdefault("asserts", {})["pad_bank_faces"] = [
            {"ref": "J1", "pads": [1], "toward_ref": "U1",
             "toward_pads": [1], "behind_pads": [2]},
            {"ref": "J1", "pads": [2], "toward_ref": "U1",
             "toward_pads": [1], "behind_pads": [1]},
        ]
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with an outward-facing functional pad bank",
              "functional pad bank faces the wrong cell")


@test("an edge-launch clearing that lands ON the board blocks the build",
      kind="known_bad")
def t_pad_beyond_edge_assert():
    """shitty-kitty's ESP32-S3 is only legal because its antenna keepout
    hangs off the south edge. Creep it inboard and the keepout sits on live
    copper; `pad_beyond_edge` is what refuses."""
    def mutate(cfg):
        cfg.setdefault("asserts", {})["pad_beyond_edge"] = [
            {"ref": "U1", "pad": 1, "offset": 0.0, "edge": "y1"}]
    d, p = scratch_config(mutate)
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generator with an on-board edge clearing", "INSIDE the y1 edge")


@test("an fp-lib-table is emitted BY DEFAULT beside the output board")
def t_fp_lib_table_default():
    """Emission used to be opt-in and the v4 canary never opted in: 116
    lib_footprint_issues at first DRC, one per footprint. A fresh board must
    get the table with no config at all; `fp_lib_table: false` opts out; the
    env var must match the RUNNING KiCad major (a ${KICAD9_*} table on
    KiCad 10 resolves only through back-compat luck)."""
    d = tmpdir("gbg_")
    out = d / "b.kicad_pcb"
    gen(LC / "03_src" / "floorplan.yaml", out)
    table = d / "fp-lib-table"
    check(table.is_file(), "no fp-lib-table emitted by default")
    txt = table.read_text()
    for lib in ("Capacitor_SMD", "Resistor_SMD", "MountingHole"):
        contains(txt, f'(name "{lib}")', "fp-lib-table rows")
    r = must_pass(run([KPY, "-c",
                       "import pcbnew,re;"
                       "print('@@'+re.match(r'\\d+', pcbnew.Version()).group())"]),
                  "kicad major")
    major = r.out.split("@@")[1].strip()
    contains(txt, "${KICAD%s_FOOTPRINT_DIR}" % major,
             "the env var must match the running KiCad major")
    # explicit opt-out still works
    def mutate(cfg):
        cfg["project"]["fp_lib_table"] = False
    d2, p2 = scratch_config(mutate)
    gen(p2, d2 / "b.kicad_pcb")
    check(not (d2 / "fp-lib-table").exists(),
          "fp_lib_table: false must suppress emission")


@test("DRC's lib_footprint_issues class is EMPTY on a fresh board, and "
      "would not be without the table", kind="known_bad")
def t_kb_lib_footprint_issues():
    """The v4 composition: 116 of 648 first-DRC findings were 'The current
    configuration does not include the footprint library X'. Both ways: with
    the emitted table the class is empty; DELETE the table and the same DRC
    reports the class for every footprint — proving the detection has teeth
    and the fix is the table, not a quieter checker."""
    d = tmpdir("gbg_")
    out = d / "b.kicad_pcb"
    gen(LC / "03_src" / "floorplan.yaml", out)

    def lib_issues():
        import json
        outj = d / "drc.json"
        run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json",
             "-o", outj, out])
        g = json.loads(outj.read_text())
        return sum(1 for v in g["violations"]
                   if v["type"] == "lib_footprint_issues")
    eq(lib_issues(), 0, "lib_footprint_issues on a fresh board WITH its table")
    (d / "fp-lib-table").unlink()
    n = lib_issues()
    check(n >= 33, f"deleting the table must expose the class for every "
                   f"footprint (29 parts + 4 holes), got {n}")


@test("netlist parity 0 vs the sealed cook-loadcell board")
def t_parity_loadcell():
    d = tmpdir("gbg_")
    out = d / "cook_loadcell.kicad_pcb"
    gen(LC / "03_src" / "floorplan.yaml", out)
    r = must_pass(run([KPY, SCRIPTS / "board_netlist_parity.py", out,
                       LC / "04_kicad" / "cook_loadcell.kicad_pcb"]),
                  "board_netlist_parity")
    contains(r.out, "BOARD PARITY 0 -> PASS", "parity output")


def _tiered_silk_tree(min_size):
    """A scratch floorplan tree that DECLARES a fab tier (03_src/rules/
    nets.yaml beside the config) with one silk height set explicitly."""
    def mutate(cfg):
        cfg["silk"]["refdes"] = dict(cfg["silk"]["refdes"],
                                     min_size=min_size)
    d, p = scratch_config(mutate)
    (d / "03_src" / "rules").mkdir(parents=True)
    (d / "03_src" / "rules" / "nets.yaml").write_text(
        "fab_tier: jlc_2layer_default\n")
    return d, p


@test("silk heights at the declared tier's floor still generate (control)")
def t_silk_at_tier_floor():
    d, p = _tiered_silk_tree(0.45)
    gen(p, d / "ok.kicad_pcb")


@test("the board's silk DRC constraints derive from the declared tier "
      "(not KiCad's 0.8mm default)")
def t_silk_constraints_from_tier():
    """pcbnew's fresh-BOARD default m_MinSilkTextHeight is 0.8mm, ABOVE the
    0.6mm refdes this generator emits — so a fresh tiered board failed its
    own silk at first DRC (112 text_height findings on the v4 112-part
    board, 2026-07-21; the shipped 2-layer boards only pass because their
    sealed .kicad_pro was hand-set to 0.6). The constraint must derive from
    the same tier the text heights are floored at. RED-verified against the
    pre-fix generator (git show HEAD swap, 2026-07-21): it leaves 0.8/0.08
    and this test fails."""
    d, p = _tiered_silk_tree(0.45)
    out = d / "b.kicad_pcb"
    gen(p, out)
    code = ("import pcbnew,sys\nb=pcbnew.LoadBoard(sys.argv[1])\n"
            "ds=b.GetDesignSettings()\n"
            "print('@@%.6f,%.6f' % (ds.m_MinSilkTextHeight/1e6,"
            " ds.m_MinSilkTextThickness/1e6))\n")
    r = must_pass(run([KPY, "-c", code, out]), "probe silk constraints")
    h, t = [float(v) for v in r.out.split("@@")[1].strip().split(",")]
    want_h, want_t = _tier_silk_floors()
    check(abs(h - want_h) < 1e-6,
          f"silk height constraint is {h}, want the tier floor {want_h}")
    check(abs(t - want_t) < 1e-6,
          f"silk stroke constraint is {t}, want the tier floor {want_t}")
    # and no emitted silk text may sit below the constraint it now carries
    code = ("import pcbnew,sys\nb=pcbnew.LoadBoard(sys.argv[1])\nbad=[]\n"
            "silk={pcbnew.F_SilkS,pcbnew.B_SilkS}\n"
            "def scan(t,who):\n"
            "  if not callable(getattr(t,'GetTextSize',None)): return\n"
            "  if t.GetLayer() not in silk: return\n"
            "  if hasattr(t,'IsVisible') and not t.IsVisible(): return\n"
            f"  if t.GetTextSize().y<{int(want_h*1e6)-1000} or "
            f"t.GetTextThickness()<{int(want_t*1e6)-1000}:\n"
            "    bad.append((who,t.GetTextSize().y/1e6,t.GetTextThickness()/1e6))\n"
            "for f in b.GetFootprints():\n"
            "  scan(f.Reference(),f.GetReference()); scan(f.Value(),f.GetReference())\n"
            "  for g in f.GraphicalItems(): scan(g,f.GetReference())\n"
            "for g in b.GetDrawings(): scan(g,'board')\n"
            "print('@@'+repr(bad))\n")
    r = must_pass(run([KPY, "-c", code, out]), "scan silk text floors")
    got = r.out.split("@@")[1].strip()
    check(got == "[]", f"silk text below the tier floors survived: {got}")


def _tiny_text_tree():
    """A scratch tree with a declared tier and ONE part on a project-local
    library whose footprint carries a 0.3mm F.SilkS user text — the
    footprint-INTERNAL text nothing policed (the library never declared a
    tier, so generation must normalize, not error)."""
    import yaml
    d = tmpdir("gbg_tiny_")
    net = (LC / "06_build" / "netlists" / "cook_loadcell.net").read_text()
    broken = net.replace('(footprint "Capacitor_SMD:C_0805_2012Metric")',
                         '(footprint "local:C_0805_2012Metric")', 1)
    check(broken != net, "fixture netlist rewrite failed")
    (d / "06_build").mkdir()
    (d / "06_build" / "tiny.net").write_text(broken)
    pretty = d / "03_src" / "lib" / "local.pretty"
    pretty.mkdir(parents=True)
    mod = Path("/usr/share/kicad/footprints/Capacitor_SMD.pretty/"
               "C_0805_2012Metric.kicad_mod").read_text()
    tiny = ('\t(fp_text user "TINY"\n\t\t(at 0 2.6 0)\n'
            '\t\t(layer "F.SilkS")\n\t\t(effects\n\t\t\t(font\n'
            '\t\t\t\t(size 0.3 0.3)\n\t\t\t\t(thickness 0.05)\n'
            '\t\t\t)\n\t\t)\n\t)\n)\n')
    body = mod.rstrip()
    (pretty / "C_0805_2012Metric.kicad_mod").write_text(
        body[:body.rfind(")")] + tiny)
    cfg = yaml.safe_load((LC / "03_src" / "floorplan.yaml").read_text())
    cfg["project"]["netlist"] = str(d / "06_build" / "tiny.net")
    if cfg["project"].get("parts_dir"):
        cfg["project"]["parts_dir"] = str(LC / cfg["project"]["parts_dir"])
    libs = cfg.get("libraries") or ["/usr/share/kicad/footprints"]
    cfg["libraries"] = [{"lib": "local",
                         "path": "03_src/lib/local.pretty"}] + list(libs)
    (d / "03_src" / "rules").mkdir(parents=True)
    (d / "03_src" / "rules" / "nets.yaml").write_text(
        "fab_tier: jlc_2layer_default\n")
    p = d / "fp.yaml"
    p.write_text(yaml.safe_dump(cfg))
    return d, p


@test("footprint-INTERNAL 0.3mm silk text is normalized to the tier floor "
      "at generation")
def t_fp_internal_text_normalized():
    """silk_h() floors what the generator EMITS; this pins what it PLACES: a
    library footprint arriving with sub-floor silk text of its own must come
    out at the tier floor (v4 evidence: 112 text_height findings, all on
    footprint fields). RED-verified against the pre-fix generator (git show
    HEAD swap, 2026-07-21): the 0.3mm text survives and this test fails."""
    d, p = _tiny_text_tree()
    out = d / "b.kicad_pcb"
    r = gen(p, out)
    contains(r.out, "normalized", "generation must report the normalization")
    code = ("import pcbnew,sys\nb=pcbnew.LoadBoard(sys.argv[1])\n"
            "hits=[]\n"
            "for f in b.GetFootprints():\n"
            "  for g in f.GraphicalItems():\n"
            "    if callable(getattr(g,'GetText',None)) and g.GetText()=='TINY':\n"
            "      hits.append((g.GetTextSize().y/1e6, g.GetTextThickness()/1e6))\n"
            "print('@@'+repr(hits))\n")
    rr = must_pass(run([KPY, "-c", code, out]), "probe TINY text")
    hits = eval(rr.out.split("@@")[1].strip())
    check(hits, "the TINY fixture text is missing from the board")
    h, t = hits[0]
    check(abs(h - 0.45) < 1e-6,
          f"footprint-internal text height is {h}, want normalized 0.45")
    _, want_t = _tier_silk_floors()
    check(t >= want_t - 1e-9,
          f"footprint-internal text stroke is {t}, want >= {want_t}")


@test("an explicit design_rules silk constraint below the tier floor FAILS "
      "naming the tier", kind="known_bad")
def t_kb_silk_constraint_below_tier():
    """A sub-tier DRC constraint means DRC stops policing sub-floor silk —
    the check would exist but could not bite. RED-verified against the
    pre-fix generator (git show HEAD swap, 2026-07-21): the old code has no
    silk_text_height key and rejects it as unknown, but with the key mapped
    it applied any value without consulting the tier."""
    def mutate(cfg):
        cfg["design_rules"] = dict(cfg.get("design_rules") or {},
                                   silk_text_height=0.3)
    d, p = scratch_config(mutate)
    (d / "03_src" / "rules").mkdir(parents=True)
    (d / "03_src" / "rules" / "nets.yaml").write_text(
        "fab_tier: jlc_2layer_default\n")
    r = run([KPY, GEN, p, "-o", d / "b.kicad_pcb"], cwd=LC)
    must_fail(r, "generate with a sub-tier silk DRC constraint",
              "jlc_2layer_default")
    contains(r.out, "min_silk_text_height", "the failure must cite the floor")


@test("an EXPLICIT silk text height below the tier floor FAILS naming the "
      "tier", kind="known_bad")
def t_kb_silk_below_tier():
    """The clean-room 3S run hand-carried its fab's silk floor because
    nothing read the declared tier; sub-floor silk prints illegibly and no
    gate saw it. Explicit sub-floor heights must be a hard error naming the
    tier (defaults are floored, never errored). The control test above
    proves the failure is the height, not the tier scaffolding. RED-verified
    against the pre-fix generator (git stash: the old code generates happily
    at 0.3mm) — 2026-07-21."""
    d, p = _tiered_silk_tree(0.3)
    r = gen(p, d / "bad.kicad_pcb", expect_ok=False)
    must_fail(r, "generate with a sub-tier silk height", "jlc_2layer_default")
    contains(r.out, "min_silk_text_height", "the failure must cite the floor")




def _tier_silk_floors(tier="jlc_4layer_advanced"):
    """Read the floors FROM fab_tiers.yaml. These tests are named "derive from
    the declared tier" and used to pin the literal 0.15 instead — so when
    G-SELFCON (ADR-0007) corrected the stroke floor to the value the 0.45 height
    can actually carry, both went red for the one reason a derivation test must
    not: the config it derives from changed, exactly as intended."""
    import yaml
    d = yaml.safe_load((ROOT / "skills" / "kicad-pcb" / "references" /
                        "fab_tiers.yaml").read_text())
    e = d["tiers"][tier]
    return float(e["min_silk_text_height"]), float(e["min_silk_stroke"])


# ------------------------------------------------- the stroke/height coupling
@test("the EMITTED stroke follows the generator's own formula: 0.60mm text "
      "gets 0.13, and 0.15 needs 0.9375mm")
def t_silk_stroke_threshold():
    """fab_tiers.yaml declared for one day (ad487df) that 'to reach the
    published 0.15 stroke, text must be >= 0.60mm'. IT IS 0.9375mm. The
    generator emits max(min_silk_stroke, 0.13, 0.16 x size), clamped to KiCad's
    0.25 x size, so 0.60 / 0.70 / 0.80 ALL emit 0.13 and only 0.16 x h >= 0.15
    gets there. MEASURED on shipped output: pluto-rx2-8way's 0.95mm port
    captions print 0.152 and its 0.60mm safety captions print 0.130.

    This test pins the EMITTER; t1_gate_contract pins the RULE FILE that
    documents it, against the same function. Both move together or neither
    does. RED-verified two ways (2026-07-29): against the corollary as written
    (0.60mm emits 0.1300, so the claimed 0.15 is off by 13%), and against the
    pre-fix generator run out of a temp repo copy — it emits **0.1300** for the
    0.45mm caption below, above KiCad's own 0.25 x height clamp of 0.1125, i.e.
    it stored a stroke KiCad cannot plot. The clamp is a no-op at every height
    at or above 0.52mm, which is every height any shipped board uses."""
    def mutate(cfg):
        cfg["silk"]["min_text_height"] = 0.45
        cfg["silk"]["captions"] = [
            {"text": "SIXTENTHS", "at": [45.0, 45.0], "size": 0.6},
            {"text": "REACHES", "at": [45.0, 50.0], "size": 0.9375},
            {"text": "SEVENTENTHS", "at": [55.0, 45.0], "size": 0.7},
            {"text": "CLAMPED", "at": [55.0, 50.0], "size": 0.45},
        ]
    d, p = scratch_config(mutate)
    (d / "03_src" / "rules").mkdir(parents=True)
    (d / "03_src" / "rules" / "nets.yaml").write_text(
        "fab_tier: jlc_2layer_default\n")
    out = d / "b.kicad_pcb"
    gen(p, out)
    code = ("import pcbnew,sys\nb=pcbnew.LoadBoard(sys.argv[1])\ng={}\n"
            "for t in b.GetDrawings():\n"
            "  if t.GetClass()=='PCB_TEXT' and t.IsOnLayer(pcbnew.F_SilkS):\n"
            "    g[t.GetText()]=(t.GetTextSize().y/1e6,t.GetTextThickness()/1e6)\n"
            "print('@@'+repr(g))\n")
    r = must_pass(run([KPY, "-c", code, out]), "probe caption strokes")
    got = eval(r.out.split("@@")[1].strip())
    for txt, want_h, want_t in (("SIXTENTHS", 0.6, 0.13),
                                ("SEVENTENTHS", 0.7, 0.13),
                                ("REACHES", 0.9375, 0.15),
                                ("CLAMPED", 0.45, 0.1125)):
        h, t = got[txt]
        check(abs(h - want_h) < 1e-6, f"{txt} height {h} != {want_h}")
        check(abs(t - want_t) < 1e-6,
              f"{txt} at {want_h}mm emits a {t}mm stroke, not {want_t} — the "
              f"fab_tiers.yaml corollary and the emitter disagree")


# ------------------------------------------------------ silk OWNERSHIP (M-COVER)
def _measure_ownership(out):
    """Ownership measured from the SAVED BOARD by code that shares nothing
    with the placer (canon M1): for every visible silk refdes and every board
    silk text, the nearest footprint centroid to the text's box centre.
    Mounting holes/fiducials print no designator, so they do not compete —
    the same exclusion `_ownership` makes, stated rather than shared.
    Returns (mislabelled_refdes, {text: nearest_ref})."""
    code = ("import pcbnew,sys,math,re\nb=pcbnew.LoadBoard(sys.argv[1])\n"
            "MM=pcbnew.ToMM\nfps={f.GetReference():f for f in b.GetFootprints()}\n"
            "cen={r:(MM(f.GetPosition().x),MM(f.GetPosition().y))\n"
            "     for r,f in fps.items() if not re.match(r'H\\d|FID',r)}\n"
            "def near(x,y,skip=None):\n"
            "  best=(1e9,None)\n"
            "  for r,(cx,cy) in cen.items():\n"
            "    if r==skip: continue\n"
            "    d=math.hypot(cx-x,cy-y)\n"
            "    if d<best[0]: best=(d,r)\n"
            "  return best\n"
            "def ctr(t):\n"
            "  bb=t.GetBoundingBox()\n"
            "  return (MM((bb.GetLeft()+bb.GetRight())//2),\n"
            "          MM((bb.GetTop()+bb.GetBottom())//2))\n"
            "mis=[]\n"
            "for r,f in sorted(fps.items()):\n"
            "  t=f.Reference()\n"
            "  if not t.IsVisible() or r not in cen: continue\n"
            "  if t.GetLayer() not in (pcbnew.F_SilkS,pcbnew.B_SilkS): continue\n"
            "  x,y=ctr(t); own=math.hypot(cen[r][0]-x,cen[r][1]-y)\n"
            "  d,o=near(x,y,r)\n"
            "  if d<own: mis.append((r,round(own,2),o,round(d,2)))\n"
            "txt={}\n"
            "for g in b.GetDrawings():\n"
            "  if g.GetClass()=='PCB_TEXT' and g.IsOnLayer(pcbnew.F_SilkS):\n"
            "    x,y=ctr(g); d,o=near(x,y); txt[g.GetText()]=(o,round(d,2))\n"
            "print('@@'+repr((mis,txt)))\n")
    r = must_pass(run([KPY, "-c", code, out]), "measure silk ownership")
    return eval(r.out.split("@@")[1].strip())


@test("every silk refdes lands nearer its OWN part than any other, and the "
      "placer reports the ownership denominator")
def t_silk_ownership():
    """THE MISSING OBJECTIVE. The slot search took the first non-colliding
    offset out to ~11mm and never asked whose label it was, so a label naming
    its neighbour was indistinguishable from a correct one. Measured on shipped
    output 2026-07-29: pluto-cal-switch 36 of 73 refdes nearer another part
    than their own, pluto-rx2-8way 40 of 64, and on a board with ten
    near-identical SMA jacks that is a mis-mate hazard, not a cosmetic one.

    RED-VERIFIED against the pre-fix placer (`git show HEAD:...
    generate_board_generic.py` run out of a temp dir with PYTHONPATH into
    skills/kicad-pcb/scripts, 2026-07-29): on cook-loadcell it places **6 of
    29** refdes nearer another part — C7 (own 6.00mm vs SJ1 3.50), J1 (7.00 vs
    Q1 5.09), J6 (3.60 vs D1 1.75), TP6 (7.07 vs D1 3.22), TP7 (6.00 vs D2
    2.83), U1 (6.00 vs C5 5.79) — and prints NO ownership line at all, so both
    assertions here fail. After the term: 0 of 29, and 36/36 owned labels.

    Tightening the METRIC does not substitute for the TERM: pluto-cal-switch
    tried courtyard-edge distance instead of centroid and it rescued ZERO of
    its 36."""
    d = tmpdir("gbg_own_")
    out = d / "b.kicad_pcb"
    r = gen(LC / "03_src" / "floorplan.yaml", out)
    contains(r.out, "silk ownership:", "the placer must report ownership")
    m = re.search(r"silk ownership: (\d+)/(\d+) owned labels", r.out)
    check(m is not None, f"no ownership denominator (canon M-COVER): {r.out[-400:]!r}")
    ok, tot = int(m.group(1)), int(m.group(2))
    check(tot >= 29, f"only {tot} labels graded on a 29-part board — the "
                     f"denominator has gone quiet")
    mis, _ = _measure_ownership(out)
    check(mis == [], f"labels nearer another part than their own: {mis}")
    check(ok == tot, f"placer claims {ok}/{tot} owned but the board measures "
                     f"clean — the report and the board disagree")


@test("a label that CANNOT own its slot is REPORTED with its measured lead, "
      "never silently first-slotted", kind="known_bad")
def t_kb_silk_ownership_degraded():
    """THE HONEST DEGRADATION. Some labels genuinely cannot be nearest their
    own part — cooksense's J_ISOLOOP has its pads at the CENTRE of the body in
    x, so anything printed either side is under the moulding once fitted. The
    failure mode to prevent is not the degradation, it is the SILENCE: the
    pre-fix placer took the first clear slot and said nothing, which is how 36
    of 73 shipped.

    The fixture crowds three caps into the left edge so TP2's 'S+' terminal
    legend has no owned slot in the whole 84-offset search. Note it is a
    FUNCTIONAL label — the safety-legible class — not a refdes.

    Not an exit code, deliberately: a board with an unownable label is still
    buildable, so the contract is an EVIDENCED report with the measured lead
    and a denominator. RED-verified against the pre-fix placer (same temp-dir
    swap as the test above, 2026-07-29): it prints no WARN and no ownership
    line for this fixture, and every assertion below fails; the 'S+' legend
    still lands 3.04mm from R2 against 4.40mm from its own TP2."""
    def mutate(cfg):
        cfg["placement"]["anchors"].update({
            "C1": [20.9, 38.0, 0], "C2": [24.5, 38.0, 0],
            "C3": [20.9, 41.6, 0], "C4": [20.9, 34.4, 0]})
    d, p = scratch_config(mutate)
    out = d / "b.kicad_pcb"
    r = gen(p, out)
    contains(r.out, "WARN silk ownership:", "the degradation must be reported")
    m = re.search(r"WARN silk ownership: (\w+) '([^']+)' for (\w+) lands "
                  r"([\d.]+)mm from \w+ but ([\d.]+)mm from (\w+)", r.out)
    check(m is not None, f"the WARN carries no measured lead: {r.out[-600:]!r}")
    kind, txt, ref, d_own, d_oth, oth = m.groups()
    check(float(d_oth) < float(d_own),
          f"the reported lead is not a degradation: {m.group(0)}")
    dm = re.search(r"silk ownership: (\d+)/(\d+) owned labels sit nearer "
                   r"their own part than any other; (\d+) degraded", r.out)
    check(dm is not None, f"no ownership summary: {r.out[-400:]!r}")
    check(int(dm.group(3)) >= 1, "a degradation happened but 0 were counted")
    # canon M1: the REPORT's claim must survive an independent measurement of
    # the saved board — a gate that grades its own arithmetic proves nothing.
    mis, texts = _measure_ownership(out)
    if kind == "refdes":
        check(any(x[0] == ref for x in mis),
              f"reported {ref} degraded, but the board measures it owned: {mis}")
    else:
        check(texts.get(txt, (None,))[0] == oth,
              f"report says {txt!r} is nearest {oth}; the board says "
              f"{texts.get(txt)}")

# --------------------------------------------- escape corridors (Phase F)
@test("escape_corridors expands to a named footprint/pour rule area")
def t_corridor_clean():
    d, cfg = scratch_config(lambda c: c.update(
        {"escape_corridors": [{"ref": "U1", "side": "N", "depth_mm": 3.0}]}))
    out = d / "b.kicad_pcb"
    gen(cfg, out)
    txt = out.read_text()
    check('esc_U1_N' in txt, "corridor rule area esc_U1_N not on the board")


@test("escape_corridor with an unknown ref is a HARD generation error",
      kind="known_bad")
def t_corridor_bad_ref():
    d, cfg = scratch_config(lambda c: c.update(
        {"escape_corridors": [{"ref": "U99", "side": "N", "depth_mm": 3.0}]}))
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "corridor on unknown ref", "unknown ref")


@test("escape_corridor with a bad side is a HARD generation error",
      kind="known_bad")
def t_corridor_bad_side():
    d, cfg = scratch_config(lambda c: c.update(
        {"escape_corridors": [{"ref": "U1", "side": "Q", "depth_mm": 3.0}]}))
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "corridor with bad side", "side must be")


# ---------------------------------------------------------------- P-COLLIDE
# RED-VERIFIED against the pre-fix generator (2026-07-25): with
# check_placement_collisions() removed from build(), BOTH known-bad cases below
# generate cleanly and exit 0 — which is exactly how smc0985-cooksense v1.3
# committed a board with U_COMP2 anchored ON TOP OF Q_SWA (byte-identical
# anchors [30.0,88.0,0]) and J_ESTOPLOOP inside J_DOOR, shorting the
# opto-isolated 30V contactor loop to 3V3/GND/DOOR_RAW. kicad DRC does catch it
# (6 shorting_items) but nothing forces DRC to run before the router does.

@test("P-COLLIDE passes a placement whose parts do not overlap")
def t_collide_clean():
    d = tmpdir("gbg_")
    r = gen(LC / "03_src" / "floorplan.yaml", d / "b.kicad_pcb")
    contains(r.out, "P-COLLIDE: 0 inter-footprint pad overlaps/shorts, 0 fixed courtyard overlap",
             "generator stdout")


@test("P-COLLIDE FAILS two parts anchored at the SAME coordinate",
      kind="known_bad")
def t_kb_anchor_collision():
    # J2 dropped exactly onto J1: the cooksense U_COMP2/Q_SWA defect, minimised.
    def mutate(c):
        c["placement"]["anchors"]["J2"] = list(
            c["placement"]["anchors"]["J1"])
    d, cfg = scratch_config(mutate)
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "coincident anchors", "P-COLLIDE")
    contains(r.out, "PINNED-LAP", "P-COLLIDE report")
    contains(r.out, "SHORT", "P-COLLIDE report")


@test("P-COLLIDE names BOTH refs and the shorted nets, not just a count")
def t_collide_names_the_nets():
    def mutate(c):
        c["placement"]["anchors"]["J2"] = list(
            c["placement"]["anchors"]["J1"])
    d, cfg = scratch_config(mutate)
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    txt = r.out
    for want in ("J1", "J2"):
        contains(txt, want, "P-COLLIDE names the colliding refs")


@test("P-COLLIDE FAILS an anchored courtyard overlap with no pad short",
      kind="known_bad")
def t_collide_pinned_lap_fails():
    """Placement owns assembly clearance. Deferring an anchored overlap to
    final DRC allowed the programmable USB hub's resistor/module interference
    to survive until render review. Archived boards remain immutable; every
    newly generated or materially revised board must move the anchors."""
    # slide J2 into J1's courtyard, but not far enough for pads to touch:
    # B3B-XH courtyard is 10.99 wide on an 11.1mm pitch, pads at 2.5mm pitch.
    def mutate(c):
        a = c["placement"]["anchors"]
        a["J2"] = [a["J1"][0] + 10.6, a["J1"][1], a["J1"][2]]
    d, cfg = scratch_config(mutate)
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "anchored courtyard overlap", "P-COLLIDE")
    contains(r.out, "FAIL P-COLLIDE PINNED-LAP", "generator stdout")


@test("P-COLLIDE treats mounting holes as fixed placement datums",
      kind="known_bad")
def t_collide_mounting_hole_lap_fails():
    """Holes are emitted before component anchors and are not legalizer
    inputs.  A connector courtyard grazing a mounting-hole courtyard used to
    disappear from P-COLLIDE entirely and survive until KiCad DRC."""
    def mutate(c):
        # J1's courtyard starts at x=27.205.  The M3 courtyard at x=24.0
        # reaches x=27.495, while its copper-free NPTH stops well short of
        # J1's pads.  This isolates the fixed-courtyard predicate.
        c["board"]["mounting_holes"]["at"][0] = [24.0, 24.2]
    d, cfg = scratch_config(mutate)
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "mounting-hole/anchor courtyard overlap", "P-COLLIDE")
    contains(r.out, "PINNED-LAP", "fixed mounting-hole report")
    contains(r.out, "J1", "fixed mounting-hole report")
    contains(r.out, "H1", "fixed mounting-hole report")


@test("P-COLLIDE treats fiducials as fixed placement datums",
      kind="known_bad")
def t_collide_fiducial_lap_fails():
    """Fiducials are board-only fixed footprints too; their courtyard must
    not be allowed beneath an anchored connector body."""
    def mutate(c):
        c["board"].pop("mounting_holes", None)
        c["board"]["fiducials"] = {
            "footprint": "Fiducial:Fiducial_1mm_Mask2mm",
            "at": [[26.1, 24.2], [72.0, 30.0], [72.0, 50.0]],
        }
    d, cfg = scratch_config(mutate)
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "fiducial/anchor courtyard overlap", "P-COLLIDE")
    contains(r.out, "PINNED-LAP", "fixed fiducial report")
    contains(r.out, "J1", "fixed fiducial report")
    contains(r.out, "FID1", "fixed fiducial report")


@test("P-COLLIDE uses rotated courtyard polygons, not intersecting bboxes")
def t_rotated_courtyard_bbox_is_not_overlap():
    """The Pluto RX2 radial SMA ring has six rotated-jack pairs, plus its
    radial R_T1/R_T2 pair, whose axis-aligned courtyard boxes intersect while
    KiCad's actual polygons are separated.  The pre-fix generator called all
    seven PINNED-LAP and aborted before writing the board.  Preserve those
    electrically-derived anchors and prove the exact predicate on real output.
    """
    d = tmpdir("gbg_pluto_rotated_")
    out = d / "pluto_rx2_8way.kicad_pcb"
    r = gen(archived_config(PLUTO_RX2, d), out,
            cwd=PLUTO_RX2)
    contains(r.out,
             "P-COLLIDE: 0 inter-footprint pad overlaps/shorts, 0 fixed courtyard overlap",
             "rotated-courtyard generator result")
    code = (
        "import pcbnew,sys\n"
        "b=pcbnew.LoadBoard(sys.argv[1])\n"
        "f={x.GetReference():x for x in b.GetFootprints()}\n"
        "pairs=[('J_ANT2','J_ANT1'),('J_ANT4','J_ANT3'),"
        "('J_ANT6','J_ANT5'),('J_RX1','J_ANT7'),('J_RX1','J_ANT8'),"
        "('J_RX2','J_ANT1'),('R_T2','R_T1')]\n"
        "n=0\n"
        "for a,c in pairs:\n"
        " p=f[a].GetCourtyard(pcbnew.F_CrtYd);q=f[c].GetCourtyard(pcbnew.F_CrtYd)\n"
        " assert p.BBox().Intersects(q.BBox()) and not p.Collide(q),(a,c)\n"
        " n+=1\n"
        "print('@@%d' % n)\n")
    rr = must_pass(run([KPY, "-c", code, out]),
                   "probe rotated courtyard bbox false positives")
    eq(rr.out.split("@@", 1)[1].strip(), "7",
       "rotated bbox-only false-positive denominator")


# ------------------------------------------------------- edge-reaching notch
# A cutout rect that pokes THROUGH a board side is boundary geometry: the side
# has to be split around it. Emitted as a closed rectangle (pre-2026-07-25
# behaviour) the untouched side segment runs straight through it and the board
# has no valid outline at all — kicad DRC `invalid_outline`, "malformed outline
# (self-intersecting)". cooksense v1.3's H4 keypad-isolation notch shipped that
# way into a commit and was measured on "filled copper" that KiCad had healed.

def _outline_probe(board, pts):
    """Ask pcbnew whether the assembled Edge.Cuts polygon is valid, and which
    of `pts` are inside it. Independent of the generator's own geometry code."""
    code = ("import pcbnew,sys\n"
            "b=pcbnew.LoadBoard(sys.argv[1])\n"
            "s=pcbnew.SHAPE_POLY_SET()\n"
            "ok=b.GetBoardPolygonOutlines(s,False)\n"
            "r=['VALID=%s' % ok, 'RINGS=%d' % s.OutlineCount()]\n"
            "for a in sys.argv[2:]:\n"
            "    x,y=[float(v) for v in a.split(',')]\n"
            "    r.append('IN(%s)=%s' % (a, s.Contains("
            "pcbnew.VECTOR2I_MM(x,y))))\n"
            "print('@@'+';'.join(r))\n")
    rr = must_pass(run([KPY, "-c", code, board] + [f"{x},{y}" for x, y in pts]),
                   "outline probe")
    return dict(kv.split("=") for kv in rr.out.split("@@")[1].strip().split(";"))


@test("an EDGE-REACHING cutout is cut into the boundary, not drawn as an island")
def t_edge_notch_outline():
    # cook-loadcell outline is x[20,75] y[20,65]; notch the EAST side.
    d, cfg = scratch_config(lambda c: c["board"].update(
        {"cutouts": [{"rect": [70.0, 40.0, 76.0, 42.0]}]}))
    out = d / "b.kicad_pcb"
    r = gen(cfg, out)
    contains(r.out, "1 edge notch(es) cut into the boundary", "generator stdout")
    p = _outline_probe(out, [(72.0, 41.0), (68.0, 41.0), (72.0, 38.0)])
    check(p["VALID"] == "True", f"outline not valid: {p}")
    check(p["RINGS"] == "1", f"expected one outer ring, got {p}")
    check(p["IN(72.0,41.0)"] == "False", f"notch interior still board: {p}")
    check(p["IN(68.0,41.0)"] == "True", f"west of notch should be board: {p}")
    check(p["IN(72.0,38.0)"] == "True", f"south of notch should be board: {p}")


@test("an INTERNAL cutout is still an island (no regression)")
def t_internal_cutout_still_island():
    d, cfg = scratch_config(lambda c: c["board"].update(
        {"cutouts": [{"rect": [60.0, 40.0, 64.0, 42.0]}]}))
    out = d / "b.kicad_pcb"
    r = gen(cfg, out)
    check("edge notch" not in r.out,
          f"internal cutout misclassified as a notch: {r.out}")
    p = _outline_probe(out, [(62.0, 41.0), (58.0, 41.0)])
    check(p["VALID"] == "True", f"outline not valid: {p}")
    check(p["IN(62.0,41.0)"] == "False", f"island interior still board: {p}")
    check(p["IN(58.0,41.0)"] == "True", f"outside the island should be board: {p}")


@test("a cutout crossing TWO sides (a corner) is a HARD error, not a guess",
      kind="known_bad")
def t_kb_corner_cutout():
    d, cfg = scratch_config(lambda c: c["board"].update(
        {"cutouts": [{"rect": [70.0, 60.0, 76.0, 66.0]}]}))
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "corner-crossing cutout", "reaches past 2 board sides")


@test("a cutout spanning a WHOLE side severs the board and is a HARD error",
      kind="known_bad")
def t_kb_severing_cutout():
    d, cfg = scratch_config(lambda c: c["board"].update(
        {"cutouts": [{"rect": [70.0, 15.0, 76.0, 70.0]}]}))
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "board-severing cutout", "not a notch")


@test("a declared physical stackup is emitted, parseable, and preserved")
def t_stackup_roundtrip():
    def mutate(c):
        c["board"]["stackup"] = {
            "nominal_thickness_mm": 1.6,
            "thickness_tolerance_mm": 0.02,
            "copper_finish": "ENIG",
            "dielectric_constraints": True,
            "mask_thickness_mm": 0.01,
            "copper_thickness_mm": [0.035, 0.035],
            "dielectrics": [{
                "type": "core", "thickness_mm": 1.53,
                "material": "FR4", "epsilon_r": 4.4,
                "loss_tangent": 0.02,
            }],
        }
    d, cfg = scratch_config(mutate)
    out = d / "b.kicad_pcb"
    r = gen(cfg, out)
    contains(r.out, "stackup authored: 2 copper layers", "generator stdout")
    text = out.read_text()
    contains(text, "(stackup", "generated board")
    contains(text, '(copper_finish "ENIG")', "generated board")
    contains(text, '(layer "dielectric 1"', "generated board")
    # pcbnew must accept the native block and preserve it through a save.
    rt = d / "roundtrip.kicad_pcb"
    code = ("import pcbnew,sys\n"
            "b=pcbnew.LoadBoard(sys.argv[1])\n"
            "pcbnew.SaveBoard(sys.argv[2],b)\n"
            "print('@@%.3f' % pcbnew.ToMM(b.GetDesignSettings().GetBoardThickness()))\n")
    rr = must_pass(run([KPY, "-c", code, out, rt]), "stackup roundtrip")
    contains(rr.out, "@@1.600", "stackup roundtrip")
    contains(rt.read_text(), "(stackup", "round-tripped board")


@test("a stackup with the wrong layer cardinality is a hard error",
      kind="known_bad")
def t_kb_stackup_cardinality():
    def mutate(c):
        c["board"]["stackup"] = {
            "nominal_thickness_mm": 1.6,
            "copper_thickness_mm": [0.035],
            "dielectrics": [{
                "type": "core", "thickness_mm": 1.53,
                "material": "FR4", "epsilon_r": 4.4,
                "loss_tangent": 0.02,
            }],
        }
    d, cfg = scratch_config(mutate)
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "one-copper-entry stackup",
              "copper_thickness_mm must contain exactly 2 entries")


@test("board-level via protection emits parseable capping/filling setup tokens")
def t_via_protection():
    def mutate(c):
        c["board"]["via_protection"] = {"capping": True, "filling": True}
    d, cfg = scratch_config(mutate)
    out = d / "b.kicad_pcb"
    r = gen(cfg, out)
    contains(r.out, "via protection authored (board-level): capping=yes, filling=yes",
             "generator stdout")
    text = out.read_text()
    eq(len(re.findall(r"\(capping yes\)", text)), 1,
       "generated board capping token")
    eq(len(re.findall(r"\(filling yes\)", text)), 1,
       "generated board filling token")
    check("(capping no)" not in text and "(filling no)" not in text,
          "generator left contradictory disabled via-protection tokens")
    # The text injection must be native pcbnew state, not a comment-like patch:
    # downstream route/stitch stages load and save the board repeatedly.
    roundtrip = d / "roundtrip.kicad_pcb"
    code = ("import pcbnew,sys\n"
            "b=pcbnew.LoadBoard(sys.argv[1])\n"
            "pcbnew.SaveBoard(sys.argv[2],b)\n"
            "print('@@%d' % len(list(b.GetFootprints())))\n")
    rr = must_pass(run([KPY, "-c", code, out, roundtrip]),
                   "via-protection roundtrip")
    contains(rr.out, "@@33", "via-protection parse")
    contains(roundtrip.read_text(), "(capping yes)",
             "round-tripped board capping token")
    contains(roundtrip.read_text(), "(filling yes)",
             "round-tripped board filling token")


@test("invalid via-protection values fail before a board can claim a process",
      kind="known_bad")
def t_kb_via_protection_value():
    def mutate(c):
        c["board"]["via_protection"] = {"capping": "sometimes"}
    d, cfg = scratch_config(mutate)
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "invalid via-protection value",
              "board.via_protection.capping must be a boolean (yes/no)")


@test("marked footprint heatsink holes promote to real board vias with exact "
      "geometry and net")
def t_promote_heatsink_pads_to_vias():
    d = tmpdir("gbg_thermal_")
    out = d / "usb_hub_3s_v4.kicad_pcb"
    r = gen(archived_config(HUB4, d), out, cwd=HUB4)
    contains(r.out, "thermal vias: emitted 48 explicit + promoted 0 marked "
             "heatsink pad(s) across 8 footprint(s)", "promotion coverage")
    code = (
        "import pcbnew,sys,collections\n"
        "b=pcbnew.LoadBoard(sys.argv[1])\n"
        "refs={'U1','U2','U3','U4','U5','U6','U9'}\n"
        "marked=sum(1 for f in b.GetFootprints() if f.GetReference() in refs "
        "for p in f.Pads() if p.GetProperty()==pcbnew.PAD_PROP_HEATSINK "
        "and p.GetDrillSize().x>0)\n"
        "v=[t for t in b.GetTracks() if t.GetClass()=='PCB_VIA']\n"
        "linked=[f for f in b.GetFootprints() if f.GetReference() in refs "
        "and f.GetFPIDAsString() and 'generated thermal-via promotion' "
        "not in f.GetLibDescription()]\n"
        "geo=collections.Counter((round(t.GetWidth(pcbnew.F_Cu)/1e6,3),"
        "round(t.GetDrill()/1e6,3),t.GetNetname()) for t in v)\n"
        "prot=collections.Counter((t.GetCappingMode(),t.GetFillingMode()) "
        "for t in v)\n"
        "owned=[]\n"
        "for f in b.GetFootprints():\n"
        "  for p in f.Pads():\n"
        "    if p.GetNumber() in ('17','18','19','20','21','22','25','26','11','2'):\n"
        "      for t in v:\n"
        "        if t.GetNetCode()==p.GetNetCode() and p.HitTest(t.GetPosition(),0,pcbnew.F_Cu):\n"
        "          owned.append((f.GetReference(),p.GetNumber(),t.GetNetname()))\n"
        "print('@@%d|%d|%d|%r|%r|%r' % (marked,len(v),len(linked),"
        "sorted(geo.items()),sorted(owned),sorted(prot.items())))\n")
    rr = must_pass(run([KPY, "-c", code, out]), "probe promoted thermal vias")
    result = rr.out.split("@@", 1)[1].strip()
    check(result.startswith("0|48|7|"),
          f"expected zero drilled heatsink pads, 48 true vias and seven "
          f"library-linked parity-safe footprints, got {result}")
    contains(result, "(0.5, 0.2, '5VA_RAW'), 4",
             "0.20mm eFuse input thermal via family")
    contains(result, "(0.5, 0.2, 'GND'), 44",
             "JLC-compatible 0.20mm ground thermal via family")
    contains(result, "((1, 1), 48)",
             "every explicit thermal via carries item-level Type VII intent")
    contains(result, "('U9', '25', '5VA_RAW')",
             "rotated split input field remains inside U9 pad 25")
    contains(result, "('U9', '26', 'GND')",
             "rotated split ground field remains inside U9 pad 26")
    contains(result, "('C23', '2', 'GND')",
             "cold-socket ground vias remain inside C23 pad 2")


@test("thermal-via promotion refuses a named footprint with no marked holes",
      kind="known_bad")
def t_kb_promote_heatsink_empty_match():
    def mutate(c):
        c["thermal_vias"] = {"promote_heatsink_pads": ["U1"]}
    d, cfg = scratch_config(mutate)
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "empty heatsink-pad promotion", "has no drilled "
              "pad_prop_heatsink pads")


@test("an explicit thermal-via field refuses an unknown footprint",
      kind="known_bad")
def t_kb_thermal_field_unknown_ref():
    def mutate(c):
        c["thermal_vias"] = {"fields": [{"ref": "U_DOES_NOT_EXIST",
                                           "pad": 1, "size": 0.5,
                                           "drill": 0.2,
                                           "at": [[0, 0]]}]}
    d, cfg = scratch_config(mutate)
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "unknown explicit thermal field", "unknown ref")


@test("an invalid item-level thermal-via process is a hard error",
      kind="known_bad")
def t_kb_thermal_field_bad_protection():
    code = (
        "import pcbnew,sys\n"
        f"sys.path.insert(0,{str(SCRIPTS)!r})\n"
        "from pcb_toolkit import apply_via_protection\n"
        "b=pcbnew.BOARD(); v=pcbnew.PCB_VIA(b)\n"
        "apply_via_protection(v,{'capping':'perhaps'},"
        "'thermal_vias.fields[0].protection')\n")
    r = run([KPY, "-c", code])
    must_fail(r, "invalid item-level via protection",
              "thermal_vias.fields[0].protection.capping must be a boolean")


@test("a self-intersecting zone polygon fails before KiCad can discard its "
      "power-cell fill", kind="known_bad")
def t_kb_zone_polygon_self_intersection():
    def mutate(c):
        z = c["zones"][0]
        z.pop("rect", None)
        z.pop("region", None)
        # Crossed quadrilateral with NONZERO signed area, so this exercises
        # the segment-intersection guard rather than only the area guard.
        z["points"] = [[25, 25], [35, 25], [25, 35], [33, 35]]
    d, cfg = scratch_config(mutate)
    r = gen(cfg, d / "b.kicad_pcb", expect_ok=False)
    must_fail(r, "self-intersecting zone", "self-intersection/overlap")


@test("M-REPRO: two runs from identical source are BYTE-IDENTICAL, and no "
      "two objects share a UUID", kind="known_bad")
def t_uuid_determinism():
    """THE INCIDENT (2026-07-26, usb-hub-3s-v3 v1.6 STAGED-NOT-SEALED).
    Three from-source regenerations of identical source gave 292/294/293
    vias. The generator was deterministic in every VALUE (identical
    footprint hashes across isolated runs) but minted FRESH RANDOM UUIDs
    each run; KiCad serialises footprints in UUID order, so the zone filler
    walked zones in a different order, Clipper tessellated pour boundaries
    differently, and island_rescue inherited all of it. Fixed by seeding
    KiCad's own KIID generator (KIID::SeedGenerator, mt19937 — stable
    across runs AND machines) from the output board name before any object
    is created.

    On byte comparison: tests/README bans GOLDEN files because KRT routing
    is stochastic. This test stores no golden — it compares two FRESH runs
    of the same (KRT-free) generate stage to each other, and byte-identity
    of that pair IS the property under test (canon M-REPRO).

    The uniqueness half is the collision proof the fix's comment promises:
    a deterministic UUID scheme must never assign two objects one identity,
    so |uuid set| must equal |object count| on a real generated board.

    RED-VERIFIED 2026-07-26: with the pre-fix generator (seed_uuids()
    removed) restored, the two runs differ at the first footprint uuid and
    the byte-identity assertion FAILS; confirmed, then the fix restored."""
    d = tmpdir("gbg_")
    # SAME board name in two dirs: the UUID seed is derived from the output
    # board name (identical source => identical name => identical stream),
    # so a differing name is a differing source, not a repro of this run.
    (d / "r1").mkdir(); (d / "r2").mkdir()
    a, b = d / "r1" / "b.kicad_pcb", d / "r2" / "b.kicad_pcb"
    gen(LC / "03_src" / "floorplan.yaml", a)
    gen(LC / "03_src" / "floorplan.yaml", b)
    ba, bb = a.read_bytes(), b.read_bytes()
    check(ba == bb,
          "two generate runs from identical source differ — UUID minting is "
          "nondeterministic again, and every downstream fill/tessellation/"
          "island decision inherits it (the 292/294/293-via class)")
    code = (
        "import pcbnew,sys\n"
        "b=pcbnew.LoadBoard(sys.argv[1])\n"
        "items=[]\n"
        "for f in b.GetFootprints():\n"
        "  items.append(f.m_Uuid.AsString())\n"
        "  items+=[p.m_Uuid.AsString() for p in f.Pads()]\n"
        "  items+=[g.m_Uuid.AsString() for g in f.GraphicalItems()]\n"
        "items+=[t.m_Uuid.AsString() for t in b.GetTracks()]\n"
        "items+=[z.m_Uuid.AsString() for z in b.Zones()]\n"
        "items+=[dr.m_Uuid.AsString() for dr in b.GetDrawings()]\n"
        "print('@@%d,%d' % (len(items), len(set(items))))\n")
    r = must_pass(run([KPY, "-c", code, a]), "uuid uniqueness probe")
    n, uniq = [int(v) for v in r.out.split("@@")[1].strip().split(",")]
    check(n > 100, f"probe saw only {n} objects — the board did not build")
    eq(uniq, n, "UUID set size vs object count (a collision means two "
                "objects share one identity)")



# ------------------------------------------------ exact refdes priority
_PRIORITY_PROBE = r"""
import json, sys, pcbnew
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
from generate_board_generic import BoardBuilder, FloorplanError
from pathlib import Path

def build(options, name, blocked=False):
    # Two distinct native footprint positions compete for a narrow label
    # strip. Restrict the fixture's offset search, not the collision/ownership
    # predicates or the native text shape. Far-away refs expose fallback order.
    b = BoardBuilder.__new__(BoardBuilder)
    b.board = pcbnew.BOARD(); b.silk_cfg = {'refdes': dict(
        size=0.7, min_size=0.7, fab_copy=True, priority_prefixes='J', **options)}
    b.fps = {}; b.hole_refs = {'H1'}; b.tier = None
    b.waived = []; b.log = []; b.X0=b.Y0=0; b.X1=b.Y1=100
    b.OFF = [(0,-2)]
    for ref,x,y in [('R_FIRST',10,10),('R_LAST',10.1,10),
                    ('J1',30,30),('C1',50,50),('TP1',70,70),('H1',80,80)]:
        fp=pcbnew.FOOTPRINT(b.board); fp.SetReference(ref)
        fp.SetPosition(pcbnew.VECTOR2I_MM(x,y)); b.board.Add(fp); b.fps[ref]=fp
        pad=pcbnew.PAD(fp); pad.SetNumber('1'); pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(pcbnew.VECTOR2I_MM(0.02,0.02)); pad.SetPosition(fp.GetPosition())
        fp.Add(pad)
    if blocked:
        # A real copper pad covers the only proposed label strip. Priority
        # must never turn collision rejection into force-placement.
        pad=pcbnew.PAD(b.fps['R_LAST']); pad.SetNumber('2')
        pad.SetShape(pcbnew.PAD_SHAPE_RECT); pad.SetSize(pcbnew.VECTOR2I_MM(15,3))
        pad.SetPosition(pcbnew.VECTOR2I_MM(10,8)); b.fps['R_LAST'].Add(pad)
    def geometry(board):
        return sorted((f.GetReference(),f.GetPosition().x,f.GetPosition().y,
                       f.GetOrientationDegrees(), sorted((p.GetNumber(),
                       p.GetPosition().x,p.GetPosition().y,p.GetSize().x,
                       p.GetSize().y,p.GetNetname()) for p in f.Pads()))
                      for f in board.GetFootprints())
    before=geometry(b.board); order=[]; place=b._place_owned
    def recording(*args, **kwargs):
        if args[5]=='refdes': order.append(args[4])
        return place(*args, **kwargs)
    b._place_owned=recording
    try: b.add_silk()
    except FloorplanError as e: return {'error':str(e)}
    out=Path(sys.argv[2])/(name+'.kicad_pcb'); pcbnew.SaveBoard(str(out),b.board)
    saved=pcbnew.LoadBoard(str(out))
    return {'order':order, 'degraded':[row[1] for row in b.own_deg], 'hidden':sorted(f.GetReference() for f in saved.GetFootprints()
                if not f.Reference().IsVisible()), 'geometry_equal':before==geometry(saved),
            'fields':sorted((f.GetReference(),f.Reference().IsVisible(),
                f.Reference().GetPosition().x,f.Reference().GetPosition().y,
                f.Reference().GetTextAngleDegrees(),f.Reference().GetTextSize().x,
                f.Reference().GetTextThickness()) for f in saved.GetFootprints())}

results={'default':build({},'default'), 'empty':build({'priority_refs':[]},'empty'),
    'priority':build({'priority_refs':['R_LAST','C1']},'priority'),
    'blocked':build({'priority_refs':['R_LAST']},'blocked',True),
    'invalid':[build({'priority_refs':v},'bad'+str(i)) for i,v in enumerate(
        [None,'R_LAST',{},[3],[''],['R_LAST','R_LAST'],['R_*'],['UNKNOWN'],['H1']])]}
results.update({
    'offset':build({'preferred_offsets':{'R_LAST':[[1.5,1]]}},'offset'),
    'empty_offsets':build({'preferred_offsets':{}},'empty_offsets'),
    'blocked_offset':build({'preferred_offsets':{'R_LAST':[[0,-2]]}},'blocked_offset'),
    'degraded_offset':build({'preferred_offsets':{'R_LAST':[[-1.5,1]]}},'degraded_offset'),
    'invalid_offsets':[build({'preferred_offsets':v},'bad_offset'+str(i)) for i,v in enumerate([
        None, [], {'UNKNOWN':[[0,1]]}, {'H1':[[0,1]]}, {'R_*':[[0,1]]},
        {'R_LAST':[]}, {'R_LAST':'0,1'}, {'R_LAST':[[1]]}, {'R_LAST':[[1,2,3]]},
        {'R_LAST':[[True,1]]}, {'R_LAST':[['1',1]]}, {'R_LAST':[[float('nan'),1]]},
        {'R_LAST':[[float('inf'),1]]}, {'R_LAST':[[0,3]]},
        {'R_LAST':[[0,1],[0,1]]}, {'R_LAST':[[0,1],[1,0]]}])]})
print('@@'+json.dumps(results))
"""


def _priority_probe():
    d=tmpdir('gbg_priority_')
    rr=must_pass(run([KPY, '-B', '-c', _PRIORITY_PROBE, SCRIPTS, d]),
                 'native refdes priority fixture')
    return json.loads(rr.out.split('@@',1)[1])


@test('exact silk priority changes the contested native label winner and preserves geometry')
def t_silk_exact_priority():
    # Run RED against the actual pre-feature producer before implementation;
    # the unrecognized field leaves R_LAST hidden while the default passes.
    p=_priority_probe()
    eq(p['default']['order'], ['J1','TP1','C1','R_FIRST','R_LAST'], 'legacy order')
    eq(p['priority']['order'], ['R_LAST','C1','J1','TP1','R_FIRST'], 'explicit order then fallback')
    check('R_LAST' in p['default']['hidden'], 'fixture has no contested label')
    check('R_LAST' not in p['priority']['hidden'] and
          'R_FIRST' in p['priority']['hidden'], 'priority did not change saved native winner')
    check(all(p[k]['geometry_equal'] for k in ['default','empty','priority','blocked']),
          'silk ordering changed physical geometry')


@test('omitted and empty silk priority preserve native fields; prioritized labels still collide', kind='known_bad')
def t_silk_exact_priority_preserves_checks():
    p=_priority_probe()
    eq(p['default']['fields'],p['empty']['fields'],'empty priority changes native fields')
    check('R_LAST' in p['blocked']['hidden'] and 'R_FIRST' in p['blocked']['hidden'],
          'explicit priority forced a label through copper')


@test('exact silk priority rejects malformed duplicate unknown wildcard and hole refs', kind='known_bad')
def t_silk_exact_priority_invalid():
    p=_priority_probe()
    eq(len(p['invalid']),9,'hostile denominator')
    for i,r in enumerate(p['invalid']):
        check('error' in r and 'silk.refdes.priority_refs' in r['error'],
              f'bad priority case {i} was accepted: {r}')




@test('preferred silk offsets recover a native label without moving the visible winner')
def t_silk_preferred_offsets():
    # Executed against the real pre-feature producer before implementation.
    p=_priority_probe()
    check('R_LAST' in p['default']['hidden'], 'fixture was not contested')
    eq(p['offset']['hidden'],['H1'],'preferred offset did not recover saved native label')
    eq(p['offset']['order'],p['default']['order'],'offset changed label order')
    a={r[0]:r for r in p['default']['fields']};b={r[0]:r for r in p['offset']['fields']}
    eq({r:v for r,v in a.items() if r!='R_LAST'},
       {r:v for r,v in b.items() if r!='R_LAST'},'other native text fields moved')
    check(p['offset']['geometry_equal'],'preferred label moved physical pads')


@test('preferred silk offsets retain collision rejection and explicit phase2 degradation',kind='known_bad')
def t_silk_preferred_offset_checks():
    p=_priority_probe()
    eq(p['empty_offsets']['fields'],p['default']['fields'],'empty offset mapping changed fields')
    check('R_LAST' in p['blocked_offset']['hidden'],'preferred offset forced a colliding label')
    check('R_LAST' not in p['degraded_offset']['hidden'] and
          'R_LAST' in p['degraded_offset']['degraded'],
          'phase2 fallback was silently changed or its ownership warning lost')
    check(p['degraded_offset']['geometry_equal'],'phase2 changed physical geometry')


@test('preferred silk offsets reject malformed unknown nonfinite and out-of-budget targets',kind='known_bad')
def t_silk_preferred_offsets_invalid():
    p=_priority_probe()
    eq(len(p['invalid_offsets']),16,'hostile offset denominator')
    for i,r in enumerate(p['invalid_offsets']):
        check('error' in r and 'silk.refdes.preferred_offsets' in r['error'],
              f'bad preferred offset {i} accepted: {r}')


@test('thermal spoke angles are exact selected-pad geometry with closed numeric bounds')
def t_pad_thermal_angle():
    import pcbnew
    sys.path.insert(0, str(SCRIPTS))
    import generate_board_generic as g
    b = _isolated_pad_consumer([{'match': ['C1'], 'pad_overrides': [
        {'pads': ['2'], 'on_net': 'GND', 'thermal_spoke_angle_deg': 45}]}])
    pads = {(fp.GetReference(), p.GetNumber()): p
            for fp in b.board.GetFootprints() for p in fp.Pads()}
    eq(pads['C1', '2'].GetThermalSpokeAngleDegrees(), 45, 'selected native angle')
    for key, pad in pads.items():
        if key != ('C1', '2'):
            eq(pad.GetThermalSpokeAngleDegrees(), 90, 'other pad unchanged')
    for bad in [-1, 360, True, '45', float('nan'), float('inf')]:
        try:
            _isolated_pad_consumer([{'match': ['ABSENT'], 'pad_overrides': [
                {'thermal_spoke_angle_deg': bad}]}])
        except g.FloorplanError:
            pass
        else:
            check(False, f'invalid angle accepted under nonmatching selector: {bad!r}')


if __name__ == "__main__":
    sys.exit(main())
