#!/usr/bin/env python3
"""T1: pin-audit dossiers use exact authorities and semantic pad aliases."""
import hashlib
import importlib.util
import math
import sys
import pcbnew
from harness import Failed, KPY, ROOT, SCRIPTS, contains, main, must_pass, not_contains, run, test, tmpdir

SCRIPT = SCRIPTS / "pin_audit.py"
PROJECT = ROOT / "archived_projects" / "programmable-usb2-hub"
RELEASE = PROJECT / "07_releases" / "v1.0-2026-08-01"

_spec = importlib.util.spec_from_file_location("pin_audit_under_test", SCRIPT)
_pin_audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pin_audit)


def _native_frame_fixture(mirrored=False):
    """Asymmetric physical pin geometry, independently prescribed top view.

    A wrong footprint changes ONLY its physical x coordinates. Native Flip
    then mounts each good/bad footprint on either side, at varied rotations.
    """
    board = pcbnew.BOARD()
    points = [(-1.3, -1.1), (-1.3, 0.2), (-1.3, 1.6),
              (0.8, 1.6), (0.8, -1.1)]
    for back in (False, True):
        for flip_axis in (pcbnew.FLIP_DIRECTION_LEFT_RIGHT,
                          pcbnew.FLIP_DIRECTION_TOP_BOTTOM):
            for rotation in (0, 30, 37.5, 90, 180, 270):
                fp = pcbnew.FOOTPRINT(board)
                board.Add(fp)
                fp.SetReference(f"U{len(list(board.GetFootprints()))}")
                fp.SetValue("FRAME_TEST")
                fp.SetPosition(pcbnew.VECTOR2I(21000000, 17000000))
                for i, (x, y) in enumerate(points, 1):
                    pad = pcbnew.PAD(fp)
                    pad.SetNumber(str(i))
                    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
                    layers = pcbnew.LSET()
                    layers.AddLayer(pcbnew.F_Cu)
                    pad.SetLayerSet(layers)
                    pad.SetSize(pcbnew.VECTOR2I(600000, 350000))
                    fp.Add(pad)
                    pad.SetFPRelativePosition(pcbnew.VECTOR2I(
                        round(x * (-1 if mirrored else 1) * 1e6), round(y * 1e6)))
                    net = pcbnew.NETINFO_ITEM(board, f"{fp.GetReference()}_PIN{i}")
                    board.Add(net)
                    pad.SetNet(net)
                if back:
                    fp.Flip(fp.GetPosition(), flip_axis)
                fp.SetOrientationDegrees(rotation)
    return board, points


def _native_snapshot(board):
    return [(f.GetReference(), f.IsFlipped(), f.GetLayer(),
             f.GetPosition().x, f.GetPosition().y, f.GetOrientationDegrees(),
             [(p.GetNumber(), p.GetPosition().x, p.GetPosition().y,
               p.GetOrientationDegrees(), p.GetNetname(), p.GetLayerSet().FmtHex())
              for p in f.Pads()]) for f in board.GetFootprints()]


@test("native front/back component-top frame preserves pads and geometry",
      kind="known_bad")
def t_native_mounted_frame():
    # RED against c4acef1e: back mounting was omitted and inverted winding.
    board, points = _native_frame_fixture()
    before = _native_snapshot(board)
    errors = []
    for fp in board.GetFootprints():
        pads = _pin_audit.local_pads(fp)
        if len(pads) != len(points):
            raise Failed("a native pad vanished")
        for p in pads:
            x, y = points[int(p["num"]) - 1]
            if abs(p["x"] - x) > 0.000002 or abs(p["y"] - y) > 0.000002:
                errors.append((fp.GetReference(), fp.IsFlipped(), p["num"], p["x"], p["y"]))
            if p["net"] != f"{fp.GetReference()}_PIN{p['num']}":
                raise Failed("native pad/net identity changed")
            p["side"] = _pin_audit.side_of(p, pads)
        if _pin_audit.winding(pads) != "CCW (top view)":
            errors.append((fp.GetReference(), "wrong component-top winding"))
    if _native_snapshot(board) != before:
        errors.append("extraction mutated native board geometry")
    if errors:
        raise Failed(f"{len(errors)} frame/preservation defects; first: {errors[:6]}")


@test("native physical-pin mirror remains wrong on front and back", kind="known_bad")
def t_native_mirror_stays_wrong():
    board, points = _native_frame_fixture(mirrored=True)
    before = _native_snapshot(board)
    wrong = []
    for fp in board.GetFootprints():
        pads = _pin_audit.local_pads(fp)
        for p in pads:
            p["side"] = _pin_audit.side_of(p, pads)
        if _pin_audit.winding(pads) != "CW (top view)":
            wrong.append(fp.GetReference())
    if wrong:
        raise Failed(f"physical manufacturer mirror hidden on {len(wrong)} instances: {wrong}")
    if _native_snapshot(board) != before:
        raise Failed("mirror extraction mutated native geometry")


@test("CLI dossier declares mount and frame while retaining native board positions",
      kind="known_bad")
def t_native_frame_dossier():
    out = tmpdir("pin_frame_dossier_")
    board, points = _native_frame_fixture()
    pcb = out / "frame.kicad_pcb"
    board.Save(str(pcb))
    before = pcb.read_bytes()
    bom = out / "bom.csv"
    bom.write_text("Designator,MPN\n" + "\n".join(
        f"{fp.GetReference()},FRAME_TEST" for fp in board.GetFootprints()) + "\n")
    part = out / "parts" / "FRAME_TEST"
    part.mkdir(parents=True)
    authority = part / "frame.pdf"
    authority.write_bytes(b"Synthetic test authority; physical geometry prescribed in test.")
    digest = hashlib.sha256(authority.read_bytes()).hexdigest()
    (part / "part.yaml").write_text(
        f"mpn: FRAME_TEST\ndatasheet: {{sha256: {digest}}}\n"
        "pins: {1: NC, 2: NC, 3: IO1, 4: GND, IO2: IO2}\n"
        "pin_aliases:\n  IO2: {schematic: '5', footprint: '5', fused: false, "
        "why: synthetic alias preservation control, evidence: test fixture}\n")
    must_pass(run([KPY, SCRIPT, pcb, bom, out / "parts", out / "dossiers"]),
              "generate native mounted dossiers")
    native = pcbnew.LoadBoard(str(pcb))
    for fp in native.GetFootprints():
        text = (out / "dossiers" / f"{fp.GetReference()}.md").read_text()
        mount = "back (B.Cu)" if fp.IsFlipped() else "front (F.Cu)"
        contains(text, f"- mounted side: {mount}", "native mounted side")
        contains(text, "COMPONENT-TOP", "explicit observation frame")
        contains(text, "y -> -y" if fp.IsFlipped() else "no reflection", "mount transform")
        contains(text, "native board (x,y)", "preserved world positions")
        contains(text, "**CCW (top view)**", "top-view winding")
        contains(text, "`IO2`: schematic `5`, footprint `5`, fused: `false`", "alias identity")
        not_contains(text, "part.yaml pins with NO pad", "alias join preserved")
        for p in fp.Pads():
            contains(text, f"({p.GetPosition().x/1e6:+.6f},{p.GetPosition().y/1e6:+.6f})",
                     "native pad position survives extraction")
            contains(text, p.GetNetname(), "native pad net survives extraction")
    if pcb.read_bytes() != before:
        raise Failed("extractor changed input PCB bytes")


@test("two-pin connector dossier exposes its unnumbered retention peg",
      kind="known_bad")
def t_unnumbered_mechanical_feature_dossier():
    out = tmpdir("pin_mechanical_dossier_")
    board = pcbnew.BOARD()
    fp = pcbnew.FOOTPRINT(board)
    board.Add(fp)
    fp.SetReference("J9")
    fp.SetValue("TWO_PIN_WITH_PEG")
    fp.SetPosition(pcbnew.VECTOR2I(12000000, 8000000))
    for number, x in (("1", 0), ("2", 3000000)):
        pad = pcbnew.PAD(fp)
        fp.Add(pad)
        pad.SetNumber(number)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetSize(pcbnew.VECTOR2I(1800000, 1800000))
        pad.SetDrillSize(pcbnew.VECTOR2I(1000000, 1000000))
        pad.SetFPRelativePosition(pcbnew.VECTOR2I(x, 0))
    peg = pcbnew.PAD(fp)
    fp.Add(peg)
    peg.SetNumber("")
    peg.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    peg.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    peg.SetSize(pcbnew.VECTOR2I(3000000, 3000000))
    peg.SetDrillSize(pcbnew.VECTOR2I(3000000, 3000000))
    peg.SetFPRelativePosition(pcbnew.VECTOR2I(1500000, -4320000))
    pcb = out / "connector.kicad_pcb"
    board.Save(str(pcb))
    before = pcb.read_bytes()
    bom = out / "bom.csv"
    bom.write_text("Designator,MPN\nJ9,TWO_PIN_WITH_PEG\n")
    part = out / "parts" / "TWO_PIN_WITH_PEG"
    part.mkdir(parents=True)
    authority = part / "connector.pdf"
    authority.write_bytes(b"Synthetic exact two-pin connector authority.")
    digest = hashlib.sha256(authority.read_bytes()).hexdigest()
    (part / "part.yaml").write_text(
        f"mpn: TWO_PIN_WITH_PEG\ndatasheet: {{sha256: {digest}}}\n"
        "pins: {1: CIRCUIT_1, 2: CIRCUIT_2}\n")
    must_pass(run([KPY, SCRIPT, pcb, bom, out / "parts", out / "dossiers",
                   "--refs", "J9"]), "generate retention-feature dossier")
    dossier = (out / "dossiers" / "J9.md").read_text()
    contains(dossier, "complete footprint inventory", "inventory completeness claim")
    contains(dossier, "| anonymous-1 | NPTH | circle", "retention peg identity")
    contains(dossier, "(+1.500000,-4.320000)", "component-top peg coordinate")
    contains(dossier, "3.0x3.0 | 3.0x3.0", "peg size and drill")
    contains(dossier, "(+13.500000,+3.680000)", "native peg coordinate")
    not_contains(dossier, "not shown", "anonymous evidence is no longer hidden")
    if pcb.read_bytes() != before:
        raise Failed("extractor changed connector PCB bytes")


@test("collinear surviving pins cannot establish package winding", kind="known_bad")
def t_collinear_winding_is_indeterminate():
    # RED against 53725e6c: excluding a fused drain land leaves four pins
    # on one side; atan2's +/-pi tie falsely labels that line CW or CCW.
    for angle in (0, 30, 90, 180, 270):
        radians = math.radians(angle)
        pads = [{"num": str(i + 1), "side": "W",
                 "x": 7 + y * math.sin(radians),
                 "y": -3 + y * math.cos(radians)}
                for i, y in enumerate((-0.975, -0.325, 0.325, 0.975))]
        contains(_pin_audit.winding(pads), "n/a (collinear perimeter pins)",
                 "a rotated line has no winding")


@test("noncollinear perimeter winding distinguishes mirrored pin sequences")
def t_winding_mirror_discrimination():
    points = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
    for mirror, expected in ((1, "CCW"), (-1, "CW")):
        pads = [{"num": str(i + 1), "side": "W", "x": mirror * x, "y": y}
                for i, (x, y) in enumerate(points)]
        if _pin_audit.winding(pads) != expected + " (top view)":
            raise Failed("a real perimeter must retain mirror discrimination")


@test("pin dossier resolves exact digest PDF and excludes aliased shell pads from winding",
      kind="known_bad")
def t_exact_pdf_alias_and_winding():
    out = tmpdir("pin_audit_")
    must_pass(run([
        KPY, SCRIPT,
        RELEASE / "source" / "programmable_usb2_hub.kicad_pcb",
        RELEASE / "fab" / "bom.csv",
        PROJECT / "02_parts", out, "--refs", "J2,U4",
    ]), "generate focused dossiers")
    j2 = (out / "J2.md").read_text()
    contains(j2, "**CCW (top view)**", "shell lands cannot reverse contact winding")
    contains(j2, "| SHIELD | GND |", "semantic SH alias resolves to physical pad 5")
    contains(j2, "fused: `true`", "intentional physical collapse is explicit")
    not_contains(j2, "part.yaml pins with NO pad", "resolved alias is not a join gap")
    u4 = (out / "U4.md").read_text()
    contains(u4, "AP63200Q-AP63205Q.pdf", "digest-selected automotive authority")
    not_contains(u4, "AP63200-AP63205.pdf", "generic variant PDF is not reviewed")


@test("P-AUTH resolves only the local PDF selected by datasheet.sha256")
def t_authority_exact_digest():
    d = tmpdir("pin_authority_")
    exact = d / "exact.pdf"
    adjacent = d / "adjacent.pdf"
    exact.write_bytes(b"exact authority")
    adjacent.write_bytes(b"neighboring family")
    digest = hashlib.sha256(exact.read_bytes()).hexdigest()
    got = _pin_audit.datasheet_path(d, {"sha256": digest})
    if got != str(exact):
        raise Failed(f"digest-selected authority: got {got!r}, want {str(exact)!r}")


@test("P-AUTH rejects a missing digest instead of falling back to the sole PDF",
      kind="known_bad")
def t_authority_missing_digest():
    d = tmpdir("pin_authority_missing_")
    (d / "plausible.pdf").write_bytes(b"not bound")
    try:
        _pin_audit.datasheet_path(d, {})
    except RuntimeError as exc:
        contains(str(exc), "P-AUTH", "typed authority failure")
        return
    raise Failed("missing digest selected the sole PDF")


@test("P-AUTH rejects a mismatched digest instead of falling back to a URL or PDF",
      kind="known_bad")
def t_authority_mismatched_digest():
    d = tmpdir("pin_authority_mismatch_")
    (d / "wrong.pdf").write_bytes(b"wrong revision")
    try:
        _pin_audit.datasheet_path(d, {"sha256": "0" * 64,
                                      "url": "https://example.invalid/right.pdf"})
    except RuntimeError as exc:
        contains(str(exc), "no local PDF matches", "digest mismatch evidence")
        return
    raise Failed("mismatched digest selected adjacent authority")


@test("exact BOM MPN resolves through the authoritative field, not directory punctuation")
def t_exact_mpn_filesystem_safe_directory():
    d = tmpdir("pin_mpn_safe_")
    safe = d / "MCP2221A-I-SL"
    safe.mkdir()
    (safe / "part.yaml").write_text("mpn: MCP2221A-I/SL\npins: {1: VDD}\n")
    got_dir, got = _pin_audit.part_authority(d, "MCP2221A-I/SL")
    if got_dir != safe or got.get("mpn") != "MCP2221A-I/SL":
        raise Failed(f"exact field identity did not resolve safe directory: {got_dir}, {got}")
    try:
        _pin_audit.part_authority(d, "MCP2221A-I-SL")
    except RuntimeError as exc:
        contains(str(exc), "exact BOM MPN", "punctuation-normalized alias rejected")
    else:
        raise Failed("filesystem spelling was accepted as an exact MPN alias")


@test("duplicate exact MPN dossier identities fail closed", kind="known_bad")
def t_exact_mpn_duplicate_is_ambiguous():
    d = tmpdir("pin_mpn_duplicate_")
    for name in ("safe-one", "safe-two"):
        p = d / name
        p.mkdir()
        (p / "part.yaml").write_text("mpn: '74LVC08APW,118'\npins: {1: 1A}\n")
    try:
        _pin_audit.part_authority(d, "74LVC08APW,118")
    except RuntimeError as exc:
        contains(str(exc), "ambiguous", "duplicate exact identities rejected")
        return
    raise Failed("duplicate exact MPN identities resolved silently")


if __name__ == "__main__":
    sys.exit(main())
