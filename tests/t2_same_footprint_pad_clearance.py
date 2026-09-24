#!/usr/bin/env python3
"""Native KiCad proof for exact-reference intrinsic pad-clearance rules."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import KPY, SCRIPTS, eq, main, must_pass, run, test, tmpdir

GEN = SCRIPTS / "generate_rules_generic.py"


@test("exact intrinsic rule relaxes only its own pads; 0.10 and via pairs still fail",
      kind="known_bad")
def t_native_same_footprint_pad_clearance_scope():
    import yaml
    import pcbnew
    root = tmpdir("intrinsic_pad_native_")
    (root / "03_src/rules").mkdir(parents=True)
    (root / "04_kicad").mkdir()
    board = pcbnew.BOARD(); board.SetCopperLayerCount(4)
    nets = {}
    for name in ("A", "B", "C", "D", "E", "F", "G", "H"):
        net = pcbnew.NETINFO_ITEM(board, name); board.Add(net); nets[name] = net
    ids = {}
    def vec(x, y): return pcbnew.VECTOR2I(round(x * 1e6), round(y * 1e6))
    def pad(ref, number, x, y, net):
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            fp = pcbnew.FOOTPRINT(board); fp.SetReference(ref); board.Add(fp)
        p = pcbnew.PAD(fp); p.SetNumber(number); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        p.SetShape(pcbnew.PAD_SHAPE_RECT); p.SetSize(vec(.5, .5))
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); p.SetLayerSet(ls)
        fp.Add(p); p.SetPosition(vec(x, y)); p.SetNet(nets[net])
        ids[p.m_Uuid.AsString()] = f"{ref}.{number}"
    # U_FINE pads 1/2 have 0.15 mm edge gap and are the only waived pair;
    # pads 3/4 retain a 0.10 mm gap and must fail against the 0.15 rule.
    pad("U_FINE", "1", 5, 5, "A"); pad("U_FINE", "2", 5.651, 5, "B")
    pad("U_FINE", "3", 7, 5, "C"); pad("U_FINE", "4", 7.599, 5, "D")
    # Another footprint's otherwise identical 0.15 mm pair remains at default 0.2.
    pad("U_OTHER", "1", 10, 5, "E"); pad("U_OTHER", "2", 10.65, 5, "F")
    pad("U_FINE", "5", 13, 5, "G")
    via = pcbnew.PCB_VIA(board); via.SetPosition(vec(13.55, 5)); via.SetWidth(pcbnew.FromMM(.3))
    via.SetDrill(pcbnew.FromMM(.15)); via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(nets["H"]); board.Add(via)
    ids[via.m_Uuid.AsString()] = "VIA"
    for a, b in [((1, 1), (16, 1)), ((16, 1), (16, 9)), ((16, 9), (1, 9)), ((1, 9), (1, 1))]:
        edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetLayer(pcbnew.Edge_Cuts); edge.SetStart(vec(*a)); edge.SetEnd(vec(*b)); edge.SetWidth(pcbnew.FromMM(.05)); board.Add(edge)
    pcb = root / "04_kicad/fixture.kicad_pcb"; pcbnew.SaveBoard(str(pcb), board)
    (root / "04_kicad/fixture.kicad_pro").write_text("{}\n")
    (root / "03_src/floorplan.yaml").write_text(yaml.safe_dump({"board": {"layers": 4}, "design_rules": {"min_clearance": .09}}))
    (root / "03_src/rules/nets.yaml").write_text(yaml.safe_dump({
        "fab_tier": "jlc_4layer_advanced", "default_clearance": "0.2mm",
        "default_track_width": "0.2mm", "classes": {},
        "same_footprint_pad_clearances": [{"id": "fine_smd", "refs": ["U_FINE"],
            "clearance": "0.15mm", "evidence": "synthetic native fixture",
            "why": "Proves exact pad-only reference scope."}]}))
    must_pass(run([KPY, GEN, root]), "generate intrinsic rule")
    report = root / "drc.json"
    must_pass(run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", report, pcb]),
              "native intrinsic scope DRC")
    actual = set()
    for row in json.loads(report.read_text())["violations"]:
        if row["type"] == "clearance":
            actual.add(tuple(sorted(ids[item["uuid"]] for item in row["items"])))
    eq(actual, {("U_FINE.3", "U_FINE.4"), ("U_OTHER.1", "U_OTHER.2"), ("U_FINE.5", "VIA")},
       "only below-floor, other-footprint, and via pairs remain")


if __name__ == "__main__":
    sys.exit(main())
