#!/usr/bin/env python3
"""T1: connector mouth/edge geometry and hash-bound human evidence."""

import hashlib
import copy
from unittest.mock import patch
import json
import shutil
import sys
from pathlib import Path

import yaml
import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import (FAB_SCRIPTS, KPY, ROOT, check, contains, eq, main,  # noqa: E402
                     must_fail, must_pass, run, test, tmpdir)

GATE = FAB_SCRIPTS / "connector_orientation_gate.py"
sys.path.insert(0, str(FAB_SCRIPTS))
import connector_orientation_gate as orientation_gate  # noqa: E402
SOURCE_PROJECT = ROOT / "archived_projects/usb-controlled-debug-hub-v1"
SOURCE_BOARD = SOURCE_PROJECT / "04_kicad/usb_controlled_debug_hub.kicad_pcb"


def fixture(kind="usb_b"):
    project = tmpdir("connector_orientation_") / "board"
    board_dir = project / "04_kicad"
    model_dir = project / "03_src/lib/3d"
    rules_dir = project / "03_src/rules"
    for directory in (board_dir, model_dir, rules_dir):
        directory.mkdir(parents=True, exist_ok=True)
    board = board_dir / SOURCE_BOARD.name
    shutil.copy2(SOURCE_BOARD, board)

    if kind == "usb_b":
        refs = ["J_UP"]
        model_name = "JLC_C86462_USB-B_TH_BF90.step"
        edge_rows = [{"ref": "J_UP", "edge": "x0", "min_offset_mm": 0.5}]
        orientation = {
            "authority": "TE ENG_CD_292304 Rev D4 and exact official STEP",
            "mount_side": "front",
            "footprint_access_axis_local": [0, 1, 0],
            # The exact STEP/renderer model mouth is native -Y. KiCad maps
            # native Y-up into footprint Y-down before the footprint rotation.
            "model_access_axis_local": [0, -1, 0],
            "model_up_axis_local": [0, 0, 1],
            "mating_plane_offset_mm": 12.45,
            "edge_offset_range_mm": [0.0, 0.4],
            "key_pad": "1",
            "model_z_offset_range_mm": [-0.01, 0.01],
        }
    else:
        refs = ["J_PORT1", "J_PORT2"]
        model_name = "KH-AF90DIP-112.step"
        edge_rows = [
            {"ref": ref, "edge": "y0", "min_offset_mm": 1.0}
            for ref in refs
        ]
        orientation = {
            "authority": "Kinghelm drawing and exact-code STEP",
            "mount_side": "front",
            "footprint_access_axis_local": [0, 1, 0],
            # The exact STEP/renderer model mouth is native -Y. KiCad maps
            # native Y-up into footprint Y-down before the footprint rotation.
            "model_access_axis_local": [0, -1, 0],
            "model_up_axis_local": [0, 0, 1],
            "mating_plane_offset_mm": 13.49,
            "edge_offset_range_mm": [-0.35, -0.05],
            "key_pad": "1",
            "model_z_offset_range_mm": [-0.01, 0.01],
        }

    source_model = SOURCE_PROJECT / "03_src/lib/3d" / model_name
    shutil.copy2(source_model, model_dir / model_name)
    keep = tuple(refs)
    mutate = (
        "import pcbnew,sys\n"
        "p=sys.argv[1]; b=pcbnew.LoadBoard(p); keep=set(" + repr(keep) + ")\n"

        "clean=pcbnew.BOARD()\n"
        "for ref in keep: clean.Add(pcbnew.Cast_to_FOOTPRINT(b.FindFootprintByReference(ref).Duplicate(False)))\n"
        "poly=pcbnew.SHAPE_POLY_SET(); assert b.GetBoardPolygonOutlines(poly,False) and poly.OutlineCount()==1\n"
        "outline=poly.Outline(0)\n"
        "for i in range(outline.PointCount()):\n"
        "  edge=pcbnew.PCB_SHAPE(clean); edge.SetShape(pcbnew.SHAPE_T_SEGMENT); edge.SetLayer(pcbnew.Edge_Cuts)\n"
        "  edge.SetStart(outline.CPoint(i)); edge.SetEnd(outline.CPoint((i+1)%outline.PointCount())); edge.SetWidth(50000); clean.Add(edge)\n"
        "clean.Save(p)\n"
    )
    must_pass(run([KPY, "-c", mutate, board]), "reduce exact board fixture")
    model_sha = hashlib.sha256((model_dir / model_name).read_bytes()).hexdigest()
    config = {
        "schema": 1,
        "groups": [{
            "id": kind,
            "refs": refs,
            "model_sha256": model_sha,
            "orientation": orientation,
        }],
        "orientation_exemptions": [],
    }
    (rules_dir / "model_registration.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    (project / "03_src/floorplan.yaml").write_text(
        yaml.safe_dump({"asserts": {"edge_faces": edge_rows}}, sort_keys=False),
        encoding="utf-8")
    return project, board, refs


def command(project, *extra):
    return [
        KPY, GATE, project, "--board",
        "04_kicad/usb_controlled_debug_hub.kicad_pcb",
        "--width", "800", "--height", "600", *extra,
    ]


@test("inside-camera grey-blue board strips remain measurable")
def t_inside_camera_board_strip_colour():
    image = orientation_gate.Image.new("RGB", (240, 160), (164, 164, 188))
    for y in range(78, 82):
        for x in range(30, 210):
            image.putpixel((x, y), (107, 111, 125))
    x0, x1, y = orientation_gate.side_board_span(image)
    eq((x0, x1), (30, 209), "cool reverse-camera board edge span")
    check(78 <= y <= 81, "cool reverse-camera board edge row")
    lit = orientation_gate.Image.new("RGB", (240, 160), (164, 164, 188))
    for y in range(78, 82):
        for x in range(30, 210):
            lit.putpixel((x, y), (137, 145, 96))
    x0, x1, y = orientation_gate.side_board_span(lit)
    eq((x0, x1), (30, 209), "fixed-light olive board edge span")
    check(78 <= y <= 81, "fixed-light olive board edge row")


@test("human-review renders use lighting that exposes mouth geometry")
def t_review_render_lighting():
    calls = []
    original = orientation_gate.subprocess.run
    class Result:
        returncode = 0
        stdout = ""
        stderr = ""
    try:
        orientation_gate.subprocess.run = lambda argv, **_kwargs: (
            calls.append(argv) or Result())
        scratch = tmpdir("orientation_lighting")
        board_path = scratch / "board.kicad_pcb"
        board_path.write_text("synthetic renderer command fixture")
        orientation_gate.render(board_path, scratch / "view.png", "front", 800, 600)
    finally:
        orientation_gate.subprocess.run = original
    argv = calls[0]
    for option, value in (("--quality", "high"), ("--light-top", "0.8"),
                          ("--light-bottom", "0.2"), ("--light-side", "0.6"),
                          ("--light-camera", "0.8")):
        eq(argv[argv.index(option) + 1], value, f"{option} review rendering")


@test("footprint axes use pcbnew's y-down transform at 90 and 270 degrees")
def t_footprint_axis_transform_matches_real_pad_positions():
    board = pcbnew.LoadBoard(str(SOURCE_BOARD))
    original = board.FindFootprintByReference("J_UP")
    for angle in (90.0, 270.0):
        fp = pcbnew.Cast_to_FOOTPRINT(original.Duplicate(False))
        fp.SetPosition(pcbnew.VECTOR2I(0, 0))
        fp.SetOrientationDegrees(angle)
        pad = next(item for item in fp.Pads() if str(item.GetNumber()) == "1")
        actual = (pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6)
        predicted = orientation_gate.footprint_to_board((1.25, -2.0, 0.0), fp)
        check(abs(actual[0] - predicted[0]) < 1e-6 and
              abs(actual[1] - predicted[1]) < 1e-6,
              f"{angle:g} degree axis transform matches pcbnew pad position")


@test("model axes use KiCad native Y, stored rotation signs/order, scale, and side")
def t_native_model_axis_transform():
    transform = getattr(
        orientation_gate, "model_to_footprint",
        lambda vector, rotation, scale, _side:
            orientation_gate.rotate_xyz(vector, rotation, scale))
    cases = [
        ((0, -1, 0), (0, 0, 0), (1, 1, 1), "front", (0, 1, 0),
         "front native-Y reflection"),
        ((0, 1, 0), (0, 0, 90), (1, 1, 1), "front", (1, 0, 0),
         "negative stored Z rotation before Y reflection"),
        ((0, 1, 0), (90, 0, 0), (1, 1, 1), "front", (0, 0, -1),
         "negative stored X rotation"),
        ((0, 0, 1), (0, 90, 0), (1, 1, 1), "front", (-1, 0, 0),
         "negative stored Y rotation"),
        ((1, 0, 0), (0, 90, 90), (1, 1, 1), "front", (0, 0, 1),
         "stored X then Y then Z application order"),
        ((1, 1, 0), (0, 0, 0), (2, 1, 3), "front",
         (2 / 5**0.5, -1 / 5**0.5, 0), "nonuniform positive scale"),
        ((-1, 0, 0), (0, 0, 0), (1, 1, 1), "back", (1, 0, 0),
         "back-side X reflection"),
    ]
    for vector, rotation, scale, side, expected, label in cases:
        actual = transform(vector, rotation, scale, side)
        check(all(abs(a - e) < 1e-9 for a, e in zip(actual, expected)), label)


@test("wrong native axis, roll, and mirror are independently rejected",
      kind="known_bad")
def t_native_model_axis_controls():
    for field, value, expected in (
        ("model_access_axis_local", [0, 1, 0], "model access axis disagrees"),
        ("model_up_axis_local", [0, 0, -1], "model up axis is inverted/rolled"),
    ):
        project, _board, _refs = fixture("usb_b")
        config_path = project / "03_src/rules/model_registration.yaml"
        config = yaml.safe_load(config_path.read_text())
        config["groups"][0]["orientation"][field] = value
        config_path.write_text(yaml.safe_dump(config, sort_keys=False))
        must_fail(run(command(project, "--machine-only")), field, expected)

    project, board_path, _refs = fixture("usb_b")
    text = board_path.read_text()
    old = "\t\t\t\t(xyz 1 1 1)"
    check(text.count(old) == 1, "single retained model scale in reduced fixture")
    board_path.write_text(text.replace(old, "\t\t\t\t(xyz -1 1 1)"))
    must_fail(run(command(project, "--machine-only")), "mirrored model scale",
              "model scale is mirrored or degenerate")


@test("connector orientation pauses for a real hash-bound human decision")
def t_review_pause_and_approval():
    project, _board, refs = fixture("usb_b")
    pending = run(command(project))
    eq(pending.rc, 2, "clean machine result without human approval")
    contains(pending.out, "P-ORIENT REVIEW REQUIRED: machine 1/1 PASS",
             "explicit review pause")
    check(not (project / "08_reviews/connector_orientation.yaml").exists(),
          "machine pass did not self-approve")

    out = project / "06_build/pre_route/orientation"
    receipt = json.loads((out / "orientation_receipt.json").read_text())
    eq(receipt["verdict"], "PASS", "machine verdict")
    eq(receipt["refs"], refs, "complete connector denominator")
    eq(receipt["review_groups"][0]["refs"], refs,
       "visual representative denominator")
    for suffix in ("top", "outside", "inside"):
        image = out / "views" / f"J_UP_{suffix}.png"
        check(image.is_file() and image.stat().st_size > 1000,
              f"required {suffix} evidence exists")

    approved = must_pass(
        run(command(project, "--approve-reviewer", "regression-human")),
        "explicit synthetic human approval")
    contains(approved.out, "P-ORIENT PASS: machine 1/1, human 1/1",
             "human denominator")
    approval = yaml.safe_load(
        (project / "08_reviews/connector_orientation.yaml").read_text())
    eq(approval["subject_sha256"], receipt["subject_sha256"],
       "approval binds the semantic subject")
    eq(approval["refs"], refs, "approval binds the complete ref denominator")
    eq(approval["schema"], 1, "fresh explicit approvals remain strict schema1")
    eq(approval["evidence_sha256"], receipt["evidence"], "approve exact user-viewed image hashes")
    check("P-ORIENT render " not in approved.out, "approval must not regenerate unseen images")
    continuation = must_pass(run(command(project)), "ordinary strict approval continuation")
    check("P-ORIENT render " not in continuation.out, "continuation reuses verified viewed evidence")


@test("semantic-subject approval survives regenerated pixels only")
def t_semantic_subject_approval_carry_forward():
    project = tmpdir("connector_semantic_approval")
    approval = project / "approval.yaml"
    refs = ["J_DATA", "J_PORT1"]
    old_evidence = {
        "views/J_DATA_top.png": "1" * 64,
        "views/J_PORT1_top.png": "2" * 64,
    }
    new_evidence = {
        "views/J_DATA_top.png": "3" * 64,
        "views/J_PORT1_top.png": "4" * 64,
    }
    value = {
        "schema": 2,
        "kind": orientation_gate.APPROVAL_KIND,
        "verdict": "APPROVED",
        "subject_sha256": "a" * 64,
        "refs": refs,
        "reviewer": "regression-human",
        "confirmed_at": "2026-08-19T00:00:00Z",
        "approval_basis": "semantic-subject-unchanged",
        "evidence_sha256": old_evidence,
    }
    approval.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    passed, reason = orientation_gate.validate_approval(
        approval, "a" * 64, refs, new_evidence)
    check(passed, "same semantic subject accepts regenerated pixels")
    contains(reason, "semantic subject unchanged", "carry-forward reason")


@test("semantic-subject approval rejects geometry or denominator changes")
def t_semantic_subject_approval_rejects_real_change():
    project = tmpdir("connector_semantic_reject")
    approval = project / "approval.yaml"
    evidence = {"views/J_DATA_top.png": "1" * 64}
    value = {
        "schema": 2,
        "kind": orientation_gate.APPROVAL_KIND,
        "verdict": "APPROVED",
        "subject_sha256": "a" * 64,
        "refs": ["J_DATA"],
        "reviewer": "regression-human",
        "confirmed_at": "2026-08-19T00:00:00Z",
        "approval_basis": "semantic-subject-unchanged",
        "evidence_sha256": evidence,
    }
    approval.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    passed, reason = orientation_gate.validate_approval(
        approval, "b" * 64, ["J_DATA"], evidence)
    check(not passed, "changed semantic subject requires reapproval")
    contains(reason, "subject or denominator is stale", "subject failure")
    passed, reason = orientation_gate.validate_approval(
        approval, "a" * 64, ["J_DATA", "J_PORT1"], evidence)
    check(not passed, "changed connector denominator requires reapproval")
    contains(reason, "subject or denominator is stale", "denominator failure")


@test("a reversed connector fails before human approval", kind="known_bad")
def t_reversed_board_axis_fails():
    project, board, _refs = fixture("usb_b")
    mutate = (
        "import pcbnew,sys\n"
        "p=sys.argv[1]; b=pcbnew.LoadBoard(p); f=b.FindFootprintByReference('J_UP')\n"
        "f.SetOrientationDegrees(90); b.Save(p)\n"
    )
    must_pass(run([KPY, "-c", mutate, board]), "reverse connector fixture")
    bad = must_fail(run(command(project, "--machine-only")),
                    "backwards connector",
                    "board access axis disagrees with contract")
    contains(bad.out, "P-ORIENT FAIL", "machine refusal")


@test("identical repeated connectors share views but not machine coverage")
def t_repeated_tuple_visual_compression():
    project, _board, refs = fixture("usb_a")
    result = must_pass(run(command(project, "--machine-only")),
                       "repeated USB-A orientation")
    contains(result.out, "P-ORIENT render 5/5",
             "all tuples share five fixed exact-board cameras")
    receipt = json.loads((project /
        "06_build/pre_route/orientation/orientation_receipt.json").read_text())
    eq(receipt["refs"], refs, "both physical refs remain machine graded")
    eq(len(receipt["measurements"]), 2, "two instance measurements")
    eq(len(receipt["review_groups"]), 1, "one exact visual tuple")
    eq(receipt["review_groups"][0]["refs"], refs,
       "representative lists every covered instance")


@test("canonical rebuilds run bounded orientation after model registration")
def t_template_wiring():
    for path in (
        ROOT / "skills/pcb-design/templates/03_src/rebuild_all.sh",
        ROOT / "skills/pcb-design/templates/03_src/rebuild_reuse.sh",
    ):
        text = path.read_text()
        model = text.index("model_registration_gate.py")
        orient = text.index("connector_orientation_gate.py")
        review = text.index("pre_route_review_check.py", orient)
        check(model < orient < review, f"{path.name} canonical gate order")
        contains(text[orient - 140:orient], "timeout",
                 f"{path.name} bounds the renderer")


@test("native scene resolver propagates explicit substitutions to CLI and environment")
def t_native_scene_explicit_resolver():
    # RED verified against the exact prior gate: resolver returns the literal
    # unresolved variable and renderer never passes its synthesized fallback.
    scratch = tmpdir("orientation_scene_resolver")
    model = scratch / "part.step"
    model.write_text("synthetic file identity for command test")
    board = scratch / "board.kicad_pcb"
    board.write_text("synthetic board identity for command test")
    table = {"KICAD10_3DMODEL_DIR": str(scratch), "KIPRJMOD": str(scratch)}
    sys.path.insert(0, str(ROOT / "skills/kicad-pcb/scripts"))
    import model_coverage_check
    with patch.object(model_coverage_check, "kicad_env", return_value=table), \
         patch.object(orientation_gate, "kicad_env", return_value=table, create=True):
        eq(orientation_gate.resolve_model(board, "${KICAD10_3DMODEL_DIR}/part.step"),
           model, "shared resolver fallback")
        calls = []
        class Result:
            returncode = 0
            stdout = stderr = ""
        with patch.object(orientation_gate.subprocess, "run", side_effect=lambda argv, **kw: calls.append((argv, kw)) or Result()):
            orientation_gate.render(board, scratch / "view.png", "top", 800, 600)
        argv, kwargs = calls[0]
        check("--define-var" in argv, "explicit CLI variable definition")
        check("KICAD10_3DMODEL_DIR=" + str(scratch) in argv, "resolved fallback reaches native CLI")
        eq(kwargs["env"]["KICAD10_3DMODEL_DIR"], str(scratch), "same environment precedence")
        check(kwargs["env"]["KICAD_CONFIG_HOME"] != str(Path.home()), "isolated native config")
        eq(argv[argv.index("--preset")+1], "", "all footprint classes explicitly enabled")


@test("native scene missing required model refuses before rendering", kind="known_bad")
def t_native_scene_missing_dependency():
    project, board_path, _refs = fixture("usb_b")
    board = pcbnew.LoadBoard(str(board_path))
    fp = pcbnew.Cast_to_FOOTPRINT(board.FindFootprintByReference("J_UP").Duplicate(False))
    fp.SetReference("U_OCCLUDER")
    model = list(fp.Models())[0]
    model.m_Filename = "${KICAD10_3DMODEL_DIR}/missing-required-body.step"
    fp.Models()[0] = model
    board.Add(fp)
    board.Save(str(board_path))
    must_fail(run(command(project, "--machine-only")), "missing nonconnector scene dependency",
              "required native scene model is unresolved")


def scene_subject(board, board_path):
    # Old owner bound only connector placements; use exactly that projection
    # as the RED control, then exercise the new whole-scene projection.
    if hasattr(orientation_gate, "scene_dependencies"):
        return orientation_gate.canonical_sha(orientation_gate.scene_dependencies(
            board, board_path, orientation_gate.kicad_env(board_path)))
    return orientation_gate.canonical_sha(orientation_gate.placement_projection(
        board, ["J_UP"], orientation_gate.board_outline(board)))


@test("native scene geometry transforms model bytes and camera stale both approval schemas", kind="known_bad")
def t_native_scene_subject_approval():
    project, board_path, _refs = fixture("usb_b")
    board = pcbnew.LoadBoard(str(board_path))
    fp = pcbnew.Cast_to_FOOTPRINT(board.FindFootprintByReference("J_UP").Duplicate(False))
    fp.SetReference("U_OCCLUDER")
    board.Add(fp)
    original = scene_subject(board, board_path)
    evidence = {"views/J_UP_inside.png": "1" * 64}
    approval = project / "approval.yaml"
    def stale(changed):
        check(changed != original, "nonconnector scene change alters semantic subject")
        for schema in (1, 2):
            value = {"schema": schema, "kind": orientation_gate.APPROVAL_KIND,
                     "verdict": "APPROVED", "subject_sha256": original,
                     "refs": ["J_UP"], "reviewer": "synthetic-control",
                     "confirmed_at": "2026-09-12T00:00:00Z", "evidence_sha256": evidence}
            if schema == 2:
                value["approval_basis"] = "semantic-subject-unchanged"
            approval.write_text(yaml.safe_dump(value))
            check(not orientation_gate.validate_approval(approval, changed, ["J_UP"], evidence)[0],
                  f"schema {schema} refuses changed scene")
    pos = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(pos.x+1000000, pos.y))
    stale(scene_subject(board, board_path)); fp.SetPosition(pos)
    m = list(fp.Models())[0]
    offset = m.m_Offset.z
    m.m_Offset.z += 1
    fp.Models()[0] = m
    stale(scene_subject(board, board_path)); m.m_Offset.z = offset
    fp.Models()[0] = m
    rotation = m.m_Rotation.y
    m.m_Rotation.y += 20
    fp.Models()[0] = m
    stale(scene_subject(board, board_path)); m.m_Rotation.y = rotation
    fp.Models()[0] = m
    pad = next(iter(fp.Pads())); size = pad.GetSize()
    pad.SetSize(pcbnew.VECTOR2I(size.x+1000000, size.y))
    stale(scene_subject(board, board_path)); pad.SetSize(size)
    fp.SetDNP(True); stale(scene_subject(board, board_path)); fp.SetDNP(False)
    m.m_Show = False; fp.Models()[0] = m
    stale(scene_subject(board, board_path)); m.m_Show = True; fp.Models()[0] = m
    model_path = orientation_gate.resolve_model(board_path, m.m_Filename)
    model_bytes = model_path.read_bytes()
    model_path.write_bytes(model_bytes+b"\n")
    stale(scene_subject(board, board_path)); model_path.write_bytes(model_bytes)
    options = orientation_gate.RENDER_OPTIONS
    with patch.object(orientation_gate, "RENDER_OPTIONS", options + ["--perspective"]):
        stale(scene_subject(board, board_path))
    # Pure routing addition stays outside the semantic orientation subject.
    track = pcbnew.PCB_TRACK(board); track.SetStart(pcbnew.VECTOR2I(1,1)); track.SetEnd(pcbnew.VECTOR2I(2,2)); board.Add(track)
    eq(scene_subject(board, board_path), original, "routing-only byte churn is reusable")


@test("strict schema1 refuses image hash and exact image-key census changes", kind="known_bad")
def t_strict_image_approval():
    p = tmpdir("orientation_strict") / "approval.yaml"
    evidence = {"views/J1_top.png": "1"*64, "views/J1_inside.png": "2"*64}
    value = {"schema": 1, "kind": orientation_gate.APPROVAL_KIND, "verdict": "APPROVED",
             "subject_sha256": "a"*64, "refs": ["J1"], "reviewer": "synthetic-control",
             "confirmed_at": "2026-09-12T00:00:00Z", "evidence_sha256": evidence}
    p.write_text(yaml.safe_dump(value))
    check(orientation_gate.validate_approval(p,"a"*64,["J1"],evidence)[0], "strict positive")
    for changed in ({**evidence, "views/J1_inside.png": "3"*64},
                    {"views/J1_top.png": "1"*64},
                    {**evidence, "views/J1_extra.png": "4"*64}):
        check(not orientation_gate.validate_approval(p,"a"*64,["J1"],changed)[0], "strict evidence mismatch")


@test("opposing rows select deterministic elevated full frames without cardinal crop")
def t_native_scene_elevated_recipe():
    faces = {"J1": {"edge": "y0"}, "J5": {"edge": "y1"}, "J9": {"edge": "x0"}}
    check(hasattr(orientation_gate, "inside_recipe"), "owning gate supports depth-separated rear evidence")
    for edge, angle in (("y0", "300,0,0"), ("y1", "60,0,0")):
        recipe = orientation_gate.inside_recipe(edge, faces)
        eq(recipe, {"side": "top", "rotate": angle, "projection": "orthographic", "framing": "full-frame"}, "measured elevated recipe")
    eq(orientation_gate.inside_recipe("x0", faces)["framing"], "cardinal-window", "single west connector unchanged")


@test("machine direction accepts overlapping opposing rows whose rear is hidden",
      kind="vacuity", gate="connector_orientation_gate.py")
def t_machine_direction_not_visibility():
    project, board_path, refs = fixture("usb_a")
    board = pcbnew.LoadBoard(str(board_path))
    polygon = orientation_gate.board_outline(board)
    config = yaml.safe_load((project / "03_src/rules/model_registration.yaml").read_text())
    group = config["groups"][0]; orientation = orientation_gate.normalized_orientation(group)
    north, south = (board.FindFootprintByReference(ref) for ref in refs)
    south.SetOrientationDegrees(0)
    south.SetPosition(pcbnew.VECTOR2I(north.GetPosition().x,
        round((max(y for x,y in polygon)-13.69)*1e6)))
    for fp, edge in ((north,"y0"),(south,"y1")):
        row = orientation_gate.grade_ref(fp, board_path, orientation,
            {"edge":edge},group["model_sha256"],polygon)
        eq(row["failures"], [], "machine direction passes despite opposing-depth occluder")
    # Independent board-coordinate projection: same X interval is collapsed
    # by the front cardinal camera, while the nearer row has full body height.
    eq(north.GetPosition().x, south.GetPosition().x, "opposing bodies share cardinal projection")
    check(south.GetPosition().y > north.GetPosition().y, "south row is in front of target north rear")
    south.SetOrientationDegrees(180)
    bad = orientation_gate.grade_ref(south,board_path,orientation,{"edge":"y1"},group["model_sha256"],polygon)
    check(bool(bad["failures"]), "contrast: wrong physical mouth direction still fails")


@test("explicit approval refuses absent stale or tampered user-viewed bundle", kind="known_bad")
def t_approval_requires_viewed_bundle():
    project, board_path, refs = fixture("usb_b")
    must_fail(run(command(project,"--approve-reviewer","synthetic-control")),
              "approve without prior viewed bundle", "review bundle is absent, stale, or tampered")
    eq(run(command(project)).rc, 2, "generate a bundle for review")
    out = project / "06_build/pre_route/orientation"
    image = out / "views/J_UP_inside.png"
    image.write_bytes(image.read_bytes()+b"tamper")
    must_fail(run(command(project,"--approve-reviewer","synthetic-control")),
              "approve tampered bundle", "review bundle is absent, stale, or tampered")
    check(not (project/"08_reviews/connector_orientation.yaml").exists(), "no approval manufactured")
    eq(run(command(project)).rc, 2, "ordinary run regenerates for new review")
    board = pcbnew.LoadBoard(str(board_path))
    fp = board.FindFootprintByReference(refs[0]); fp.SetPosition(fp.GetPosition()+pcbnew.VECTOR2I(0,1000000)); board.Save(str(board_path))
    must_fail(run(command(project,"--approve-reviewer","synthetic-control")),
              "approve stale semantic bundle", "review bundle is absent, stale, or tampered")


@test("real native stale scene cannot be approved by relabeling its receipt", kind="known_bad")
def t_receipt_integrity_native():
    # RED against candidate-two: its main approves these real stale pixels
    # after ONLY subject_sha256 is replaced; renderer is forbidden throughout
    # reuse. The physical body and unchanged native image hashes are independent
    # witnesses, not assertions about a validation helper's implementation.
    project, board_path, refs = fixture("usb_b")
    args = [str(project), "--board", str(board_path), "--width", "800", "--height", "600"]
    out = project / "06_build/pre_route/orientation"
    rp = out / "orientation_receipt.json"
    approval = project / "08_reviews/connector_orientation.yaml"
    eq(orientation_gate.main(args), 2, "real native fixture needs review")
    original = json.loads(rp.read_text())
    original_board = board_path.read_bytes()
    images = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (out / "views").iterdir()}
    def approve():
        with patch.object(orientation_gate, "render", side_effect=AssertionError("approval must not render")):
            return orientation_gate.main(args + ["--approve-reviewer", "synthetic-integrity-control"])
    eq(approve(), 0, "exact existing pixels approve without render")
    eq(yaml.safe_load(approval.read_text())["schema"], 1, "fresh approval stays strict schema1")
    approval.unlink()
    board = pcbnew.LoadBoard(str(board_path))
    body = pcbnew.Cast_to_FOOTPRINT(board.FindFootprintByReference("J_UP").Duplicate(False))
    body.SetReference("U_OCCLUDER")
    body.SetPosition(body.GetPosition() + pcbnew.VECTOR2I(15000000, 0))
    board.Add(body); board.Save(str(board_path))
    eq(approve(), 1, "material body change refuses normally")
    captured = {}
    previous = orientation_gate.existing_review
    def capture(outdir, subject, *pos, **kw):
        captured["subject"] = subject
        return previous(outdir, subject, *pos, **kw)
    with patch.object(orientation_gate, "existing_review", side_effect=capture):
        eq(approve(), 1, "capture freshly derived current subject")
    check(captured["subject"] != original["subject_sha256"], "real added body changes subject")
    check("U_OCCLUDER" in {fp.GetReference() for fp in board.GetFootprints()}, "physical body exists")
    check("U_OCCLUDER" not in {r["ref"] for r in original["scene"]["placements"]}, "old scene lacks body")
    stale = copy.deepcopy(original); stale["subject_sha256"] = captured["subject"]
    rp.write_text(json.dumps(stale))
    eq(approve(), 1, "subject relabel cannot approve pixels lacking current body")
    check(not approval.exists(), "stale scene never writes approval")
    eq({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (out / "views").iterdir()}, images,
       "rejection preserves native viewed pixels")
    eq(json.loads(rp.read_text()), stale, "contradictory receipt is not silently repaired")
    board_path.write_bytes(original_board)
    mutations = {
        "schema": 2, "tool_identity": "unrelated-tool", "scene": {"placements": []},
        "inside_recipes": {}, "render_size": [1, 1], "measurements": [],
        "failures": ["contradictory PASS"], "rendered_board_sha256": "0" * 64,
        "config_sha256": "0" * 64, "floorplan_sha256": "0" * 64,
        "notes": ["invented"], "subject": {}, "producer_evidence": {},
        "refs": [], "review_groups": [], "observed_board_sha256": "0" * 64,
        "evidence": {**original["evidence"], "views/invented.png": "0" * 64},
    }
    for key, value in mutations.items():
        altered = copy.deepcopy(original); altered[key] = value
        rp.write_text(json.dumps(altered))
        eq(approve(), 1, "contradictory receipt field " + key)
        check(not approval.exists(), "no approval for " + key)
    for key in original:
        altered = copy.deepcopy(original); del altered[key]
        rp.write_text(json.dumps(altered))
        eq(approve(), 1, "missing receipt field " + key)
    altered = copy.deepcopy(original); altered["unknown_field"] = True
    rp.write_text(json.dumps(altered)); eq(approve(), 1, "extra receipt field refuses")
    rp.write_text("[]"); eq(approve(), 1, "nonmapping receipt refuses")
    rp.write_text(json.dumps(original)[:-1] + ', "schema": 1}')
    eq(approve(), 1, "duplicate receipt field refuses")
    # Native command origin is an independent retained producer witness.
    rp.write_text(json.dumps(original))
    native = out / "renders/populated_top.command.json"
    command_bytes = native.read_bytes()
    command = json.loads(command_bytes)
    for key, value in (("observed_board_sha256", "0"*64), ("subject_sha256", "0"*64),
                       ("tool_identity", "unrelated"), ("command", []), ("config", {})):
        altered = copy.deepcopy(command); altered[key] = value
        native.write_text(json.dumps(altered))
        eq(approve(), 1, "tampered native producer " + key)
    native.write_bytes(command_bytes)
    for key, value in (("observed_board_sha256", "0"*64), ("subject_sha256", "0"*64),
                       ("tool_identity", "unrelated"), ("command", []), ("config", {}),
                       ("invented", True)):
        altered = copy.deepcopy(command); altered[key] = value
        native.write_text(json.dumps(altered))
        rewritten = copy.deepcopy(original)
        rewritten["producer_evidence"][native.relative_to(out).as_posix()] = hashlib.sha256(native.read_bytes()).hexdigest()
        rp.write_text(json.dumps(rewritten))
        eq(approve(), 1, "rehashed contradictory native producer " + key)
    native.write_bytes(command_bytes); rp.write_text(json.dumps(original))
    for path in (out / "renders/rendered_board.kicad_pcb", out / "observed_board.kicad_pcb",
                 out / "renders/populated_top.png", out / "renders/populated_top.log"):
        data = path.read_bytes(); path.write_bytes(data + b"tampered")
        eq(approve(), 1, "changed producer or observation bytes " + path.name)
        path.write_bytes(data)
    # Routing-only physical track changes preserve subject and original render
    # origin, while current observed bytes differ. The gate must not repaint.
    board = pcbnew.LoadBoard(str(board_path))
    track = pcbnew.PCB_TRACK(board); track.SetStart(pcbnew.VECTOR2I(10000000,10000000))
    track.SetEnd(pcbnew.VECTOR2I(11000000,10000000)); track.SetWidth(200000)
    board.Add(track); board.Save(str(board_path))
    check(board_path.read_bytes() != original_board, "routing control changes actual board bytes")
    eq(approve(), 0, "routing-only current board reuses exact pixels")
    after = json.loads(rp.read_text())
    eq(after["rendered_board_sha256"], hashlib.sha256(original_board).hexdigest(), "native producer origin preserved")
    eq(after["observed_board_sha256"], hashlib.sha256(board_path.read_bytes()).hexdigest(), "current observation updated")
    eq(after["evidence"], original["evidence"], "routing preserves exact reviewed image hashes")
    eq(approve(), 0, "repeated routing-only reuse also remains valid")


if __name__ == "__main__":
    sys.exit(main())
