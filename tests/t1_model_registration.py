#!/usr/bin/env python3
"""T1: independent native-model registration and project orchestration.

The regression fixture starts from the exact Pluto v5 board and exact native
Amphenol model, then changes only J2's internal model offset by 5 mm.  This is
the failure the gate exists to catch: model pixels can remain self-consistent
with their own mesh while missing F.Fab, F.CrtYd, and drilled attachment
datums.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import (FAB_SCRIPTS, KPY, ROOT, contains, main, must_fail,  # noqa: E402
                     must_pass, run, test, tmpdir, check, eq)

sys.path.insert(0, str(ROOT / "skills/pcb-design/scripts"))
from pipeline_contract import StageResult  # noqa: E402
from pipeline_readiness import evaluate  # noqa: E402

ENGINE = FAB_SCRIPTS / "native_model_registration.py"
GATE = FAB_SCRIPTS / "model_registration_gate.py"
SOURCE_PROJECT = ROOT / "projects/pluto-rx2-8way-v5"
SOURCE_BOARD = SOURCE_PROJECT / "04_kicad/pluto_rx2_8way_v5.kicad_pcb"
SOURCE_MODEL = (SOURCE_PROJECT /
                "03_src/lib/3dmodels/Amphenol_901_143_6RFX-JLC-C429844.step")


def project_fixture(*, shifted=False, inverted=False, kept_refs=("J2",),
                    smd_only=False, registration_datum=None, mount_side=None):
    project = tmpdir("model_registration_") / "pluto"
    board_dir = project / "04_kicad"
    model_dir = project / "03_src/lib/3dmodels"
    rules_dir = project / "03_src/rules"
    for directory in (board_dir, model_dir, rules_dir):
        directory.mkdir(parents=True, exist_ok=True)
    board = board_dir / SOURCE_BOARD.name
    model = model_dir / SOURCE_MODEL.name
    shutil.copy2(SOURCE_BOARD, board)
    shutil.copy2(SOURCE_MODEL, model)

    # Keep the exact J2 footprint and exact native model.  The optional fault
    # changes only the footprint-local model transform, preserving model bytes.
    mutate = (
        "import pcbnew,sys\n"
        f"p=sys.argv[1]; b=pcbnew.LoadBoard(p); keep=set({tuple(sorted(kept_refs))!r})\n"
        "for fp in b.GetFootprints():\n"
        "  if fp.GetReference() not in keep: fp.Models().clear()\n"
        "  elif fp.GetReference() == 'J2':\n"
        "    models=fp.Models(); model=models[0]\n"
        f"    model.m_Offset.x={5.0 if shifted else 0.0}; models[0]=model\n"
        f"    if {inverted!r}:\n"
        "      model=models[0]; model.m_Rotation.x += 180.0; models[0]=model\n"
        f"    if {smd_only!r}:\n"
        "      for pad in fp.Pads():\n"
        "        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD); "
        "pad.SetDrillSize(pcbnew.VECTOR2I(0,0))\n"
        "b.Save(p)\n"
    )
    must_pass(run([KPY, "-c", mutate, board]), "inject 5 mm model offset")
    model_sha = hashlib.sha256(model.read_bytes()).hexdigest()
    config = {
        "schema": 1,
        "groups": [{
            "id": "shifted_sma",
            "refs": ["J2"],
            "model_sha256": model_sha,
            "fit_tolerance_mm": 1.0,
            "courtyard_containment_tolerance_mm": 0.25,
            "search_margin_mm": 8.0,
            "render_width": 1200,
            "render_height": 800,
        }],
    }
    if registration_datum is not None:
        config["groups"][0]["registration_datum"] = registration_datum
    if mount_side is not None:
        config["groups"][0]["orientation"] = {"mount_side": mount_side}
    (rules_dir / "model_registration.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return project, board, model_sha


def broken_project():
    return project_fixture(shifted=True)


def inverted_project():
    return project_fixture(inverted=True, mount_side="front")


def accepted_bytes(path):
    return {
        item.relative_to(path).as_posix(): item.read_bytes()
        for item in path.rglob("*") if item.is_file()
    }


def gate_command(project, board, out="06_build/pre_route/model_registration.md"):
    return [
        KPY, GATE, project, "--board", f"04_kicad/{board.name}",
        "--out", out,
    ]


def readiness_result(project, stage):
    receipts = project / "06_build/receipts"
    receipts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(project / "06_build/pre_route/model_registration.stage.json",
                 receipts / "P-MODEL-REG.json")
    registry = {
        "schema": 1,
        "profile": "model-registration-test",
        "target": "DESIGN_CLEAN",
        "subject": stage.subject.to_mapping(),
        "receipts_dir": "06_build/receipts",
        "stages": [{
            "stage_id": "P-MODEL-REG",
            "required_for": "DESIGN_CLEAN",
            "applicability": "APPLIES",
            "minimum_total": 1,
            "bundles": {
                "model_registration_bundle":
                    "06_build/pre_route/model_registration_bundle/bundle.json",
            },
        }],
    }
    path = project / "03_src/rules/receipt_readiness.yaml"
    path.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")
    return evaluate(project, path)


@test("model registration publishes a strict tuple receipt and StageResult")
def t_clean_receipt_bundle_and_stage_result():
    project, board, _model_sha = project_fixture()
    first = must_pass(run(gate_command(project, board)),
                      "model registration clean fixture")
    contains(first.out, "P-MODEL-REG PASS: 1/1 group(s) graded",
             "clean aggregate denominator")
    aggregate = (project / "06_build/pre_route/model_registration.md").read_text()
    contains(aggregate, "a-render_verdict: PASS",
             "legacy aggregate verdict remains machine-readable")
    contains(aggregate, f"board_sha256: {hashlib.sha256(board.read_bytes()).hexdigest()}",
             "legacy aggregate board binding remains machine-readable")

    bundle = project / "06_build/pre_route/native_registration/shifted_sma"
    manifest = json.loads((bundle / "bundle.json").read_text())
    receipt = json.loads(
        (bundle / "model_registration_receipt.json").read_text())
    stage = StageResult.from_json(
        (project / "06_build/pre_route/model_registration.stage.json").read_text())
    aggregate_bundle = project / "06_build/pre_route/model_registration_bundle"
    aggregate_manifest = json.loads((aggregate_bundle / "bundle.json").read_text())
    aggregate_index = json.loads(
        (aggregate_bundle / "model_registration_index.json").read_text())
    eq(stage.stage_id, "P-MODEL-REG", "stage id")
    eq(stage.status, "PASS", "outer verdict")
    eq(stage.outputs, ("model_registration_bundle",), "outer output symbol")
    eq(stage.graded, 1, "outer graded groups")
    eq(stage.total, 1, "outer total groups")
    eq(aggregate_manifest["run_id"], stage.run_id,
       "aggregate bundle run matches stage")
    eq(aggregate_manifest["subject"], stage.subject.to_mapping(),
       "aggregate bundle subject matches stage")
    eq(aggregate_index["subject"], stage.subject.to_mapping(),
       "aggregate index subject matches stage")
    eq(aggregate_index["groups"][0]["manifest"],
       "06_build/pre_route/native_registration/shifted_sma/bundle.json",
       "aggregate index points to exact group manifest")
    eq(readiness_result(project, stage)["status"], "PASS",
       "StageResult output reopens through readiness")
    eq(receipt["kind"], "model-registration-receipt-v1", "domain receipt kind")
    eq(set(receipt["tuple"]), {
        "footprint_sha256", "model_sha256", "transform_sha256",
        "contract_sha256", "tool_identity",
    }, "exact tuple fields")
    check("status" not in receipt and "verdict" not in receipt,
          "domain receipt duplicated outer verdict")
    eq(receipt["refs"], ["J2"], "receipt ref denominator")
    eq(receipt["measurements"][0]["attachment_centres_graded"], 5,
       "graded drilled attachment centres")
    eq(receipt["evidence"], sorted(set(receipt["evidence"])),
       "deterministic evidence ordering")
    check((bundle / "native_coupon.kicad_pcb").is_file(),
          "origin-centred coupon persisted")
    for name, record in manifest["outputs"].items():
        artifact = bundle / name
        eq(hashlib.sha256(artifact.read_bytes()).hexdigest(), record["sha256"],
           f"manifest binds {name}")

    before = accepted_bytes(bundle)
    second = must_pass(run(gate_command(project, board)),
                       "model registration tuple cache fixture")
    contains(second.out, "P-MODEL-REG CACHE-HIT: shifted_sma",
             "unchanged tuple is reused")
    eq(accepted_bytes(bundle), before, "cache hit leaves accepted bundle immutable")

    custom_out = "06_build/custom/model_registration.md"
    must_pass(run(gate_command(project, board, custom_out)),
              "custom aggregate output location")
    custom = project / custom_out
    contains(custom.read_text(),
             "accepted_bundle: 06_build/custom/model_registration_bundle/bundle.json",
             "custom output derives its aggregate bundle path")
    check((project / "06_build/custom/model_registration_bundle/bundle.json").is_file(),
          "custom aggregate bundle was published beside its report")


@test("aggregate index is deterministic and readiness-safe for multiple groups")
def t_multi_group_aggregate_index():
    project, board, _model_sha = project_fixture(kept_refs=("J2", "J3"))
    config_path = project / "03_src/rules/model_registration.yaml"
    config = yaml.safe_load(config_path.read_text())
    base = config["groups"][0]
    config["groups"] = [
        {**base, "id": "zeta_group", "refs": ["J2"]},
        {**base, "id": "alpha_group", "refs": ["J3"]},
    ]
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    must_pass(run(gate_command(project, board)), "multi-group model registration")
    stage = StageResult.from_json(
        (project / "06_build/pre_route/model_registration.stage.json").read_text())
    bundle = project / "06_build/pre_route/model_registration_bundle"
    manifest = json.loads((bundle / "bundle.json").read_text())
    index = json.loads((bundle / "model_registration_index.json").read_text())
    eq([group["id"] for group in index["groups"]],
       ["alpha_group", "zeta_group"], "deterministic group index order")
    eq((stage.graded, stage.total), (2, 2), "multi-group denominator")
    eq(manifest["run_id"], stage.run_id, "multi-group aggregate run binding")
    eq(manifest["subject"], stage.subject.to_mapping(),
       "multi-group aggregate subject binding")
    eq(index["run_id"], stage.run_id, "multi-group index run binding")
    eq(index["subject"], stage.subject.to_mapping(),
       "multi-group index subject binding")
    eq(readiness_result(project, stage)["status"], "PASS",
       "multi-group aggregate passes readiness bundle audit")


@test("SMD-only native bodies use an explicit all-pad-centre registration datum")
def t_smd_all_pad_centre_registration():
    project, board, _model_sha = project_fixture(
        smd_only=True, registration_datum="all_pad_centres")
    result = must_pass(run(gate_command(project, board)),
                       "SMD all-pad-centre registration")
    contains(result.out, "P-MODEL-REG PASS: 1/1 group(s) graded",
             "SMD group reaches the measured denominator")
    receipt = json.loads((project /
        "06_build/pre_route/native_registration/shifted_sma/"
        "model_registration_receipt.json").read_text())
    eq(receipt["measurements"][0]["attachment_centres_total"], 5,
       "all five SMD pad centres are graded")
    eq(receipt["measurements"][0]["attachment_centres_graded"], 5,
       "all five SMD pad centres lie within the registered body")


@test("extended SMD lands require actual positive copper overlap and signed bodies",
      kind="known_bad")
def t_extended_smd_overlap():
    # RED verified against db865861 native engine/gate in an isolated script tree;
    # the old gate refuses the explicit new datum after rejecting extended centers.
    import pcbnew
    sys.path.insert(0, str(FAB_SCRIPTS))
    from native_model_registration import smd_pad_plan_overlap_mm2
    project = tmpdir("extended_smd_") / "fixture"
    for directory in ("04_kicad", "03_src/rules", "03_src/lib/3dmodels"):
        (project / directory).mkdir(parents=True, exist_ok=True)
    model = project / "03_src/lib/3dmodels/body.wrl"
    model.write_text('''#VRML V2.0 utf8
Transform { scale 0.393700787 0.393700787 0.393700787 children [
 Transform { translation 0 0 0.225 children [ Shape {
 appearance Appearance { material Material { diffuseColor 0.2 0.2 0.2 } }
 geometry Box { size 1.6 0.8 0.45 } } ] } ] }
''')
    board = project / "04_kicad/fixture.kicad_pcb"
    b = pcbnew.BOARD()
    fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Resistor_SMD.pretty",
                             "R_0603_1608Metric")
    fp.SetReference("R1"); b.Add(fp)
    fp.SetPosition(pcbnew.VECTOR2I(10000000, 10000000))
    fp.Models().clear()
    native = pcbnew.FP_3DMODEL(); native.m_Filename = str(model)
    fp.Models().push_back(native)
    for start, end in [((0, 0), (20, 0)), ((20, 0), (20, 20)),
                       ((20, 20), (0, 20)), ((0, 20), (0, 0))]:
        edge = pcbnew.PCB_SHAPE(b); edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetStart(pcbnew.VECTOR2I(*(int(x * 1e6) for x in start)))
        edge.SetEnd(pcbnew.VECTOR2I(*(int(x * 1e6) for x in end)))
        edge.SetLayer(pcbnew.Edge_Cuts); edge.SetWidth(50000); b.Add(edge)
    b.Save(str(board))
    config = {"schema": 1, "groups": [{"id": "extended", "refs": ["R1"],
        "model_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
        "registration_datum": "all_pad_centres", "mount_side": "front",
        "fit_tolerance_mm": 0.2, "courtyard_containment_tolerance_mm": 0.25,
        "search_margin_mm": 1.5, "render_width": 2400, "render_height": 1600}]}
    rules = project / "03_src/rules/model_registration.yaml"
    rules.write_text(yaml.safe_dump(config))
    old = must_fail(run(gate_command(project, board)), "extended centers are outside body")
    contains(old.out, "outside body", "old datum fails for the intended reason")
    config["groups"][0]["registration_datum"] = "all_smd_pad_overlap"
    rules.write_text(yaml.safe_dump(config))
    must_pass(run(gate_command(project, board)), "extended copper overlaps measured body")
    receipt = json.loads((project / "06_build/pre_route/native_registration/extended/"
                         "model_registration_receipt.json").read_text())
    eq(receipt["measurements"][0]["attachment_overlaps_total"], 2, "complete pad denominator")
    eq(receipt["measurements"][0]["attachment_overlaps_graded"], 2, "both pads overlap")
    must_pass(run(gate_command(project, board)), "overlap receipt cache reopens")
    pad = list(fp.Pads())[0]
    # Independent exact rectangle area; tangency and rounded-corner bbox traps.
    pad.SetPosition(pcbnew.VECTOR2I(0, 0)); pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    eq(round(smd_pad_plan_overlap_mm2(pad, (-.2, -.2, .2, .2)), 6), .16,
       "native intersection matches analytic rectangle")
    eq(smd_pad_plan_overlap_mm2(pad, (.4, -.1, .5, .1)), 0, "edge tangency has no area")
    pad.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT); pad.SetRoundRectRadiusRatio(.25)
    eq(smd_pad_plan_overlap_mm2(pad, (.38, .455, .399, .474)), 0,
       "bbox corner lacks actual rounded copper")
    pad.SetOrientationDegrees(90)
    check(smd_pad_plan_overlap_mm2(pad, (.42, -.05, .46, .05)) > 0,
          "rotation applied to effective copper")
    pad.SetPosition(pcbnew.VECTOR2I(15000000, 10000000)); b.Save(str(board))
    bad = must_fail(run(gate_command(project, board)), "detached pad blocks registration")
    contains(bad.out, "no positive model-plan overlap", "missing attachment is explicit")
    # Restore the good board, then invert only the model across the PCB side.
    pad.SetPosition(pcbnew.VECTOR2I(9175000, 10000000)); pad.SetOrientationDegrees(0)
    native.m_Rotation.x = 180; fp.Models().clear(); fp.Models().push_back(native)
    b.Save(str(board))
    bad = must_fail(run(gate_command(project, board)), "overlap cannot hide wrong signed side")
    contains(bad.out, "FAIL", "signed body inversion rejected")


@test("SMD-only native bodies fail under the default drilled-centre policy",
      kind="known_bad")
def t_smd_default_drilled_policy_fails_closed():
    project, board, _model_sha = project_fixture(smd_only=True)
    failed = must_fail(run(gate_command(project, board)),
                       "SMD default drilled-centre policy")
    contains(failed.out, "no drilled_centres",
             "missing drilled denominator is explicit")


@test("one physical ref cannot inflate more than one group denominator",
      kind="known_bad")
def t_duplicate_group_ref_is_rejected():
    project, board, _model_sha = project_fixture()
    config_path = project / "03_src/rules/model_registration.yaml"
    config = yaml.safe_load(config_path.read_text())
    base = config["groups"][0]
    config["groups"] = [
        {**base, "id": "alpha_group"},
        {**base, "id": "zeta_group"},
    ]
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    failed = must_fail(run(gate_command(project, board)),
                       "duplicate registration ref denominator")
    contains(failed.out, "ref J2 appears in both alpha_group and zeta_group",
             "duplicate ref diagnosis")


@test("model-transform change invalidates cache and preserves prior PASS",
      kind="known_bad")
def t_transform_change_invalidates_without_clobbering_accepted_bundle():
    project, board, _model_sha = project_fixture()
    must_pass(run(gate_command(project, board)), "seed accepted model receipt")
    bundle = project / "06_build/pre_route/native_registration/shifted_sma"
    before = accepted_bytes(bundle)
    mutate = (
        "import pcbnew,sys\n"
        "p=sys.argv[1]; b=pcbnew.LoadBoard(p); fp=b.FindFootprintByReference('J2')\n"
        "models=fp.Models(); model=models[0]; model.m_Offset.x=5.0; "
        "models[0]=model; b.Save(p)\n"
    )
    must_pass(run([KPY, "-c", mutate, board]), "change native model transform")
    failed = must_fail(run(gate_command(project, board)),
                       "changed tuple registration", expect="P-MODEL-REG FAIL")
    check("CACHE-HIT" not in failed.out, "changed transform reused old tuple")
    eq(accepted_bytes(bundle), before, "failed tuple preserves prior PASS bundle")
    diagnostics = project / "06_build/pre_route/native_registration/failed_attempts"
    check(any(path.name == "invocation.log" for path in diagnostics.rglob("*")),
          "failed attempt diagnostics were retained")
    stage = StageResult.from_json(
        (project / "06_build/pre_route/model_registration.stage.json").read_text())
    eq(stage.status, "FAIL", "outer receipt owns failed verdict")
    eq(stage.outputs, (), "failed receipt does not name prior accepted output")
    eq((stage.graded, stage.total), (0, 1), "failed group denominator")


@test("native registration rejects a provenance-correct model shifted 5 mm",
      kind="known_bad")
def t_native_engine_and_project_gate_reject_shifted_model():
    project, board, model_sha = broken_project()
    direct = must_fail(run([
        KPY, ENGINE, board, project / "direct", "--refs", "J2",
        "--model-sha256", model_sha, "--fit-tol-mm", "1.0",
        "--courtyard-tol-mm", "0.25", "--search-margin-mm", "8.0",
        "--width", "1200", "--height", "800",
    ]), "native_model_registration.py shifted-model fixture",
        expect="P-MODEL-REG FAIL")
    contains(direct.out, "body exceeds F.CrtYd",
             "direct gate identifies physical courtyard excursion")

    aggregate = must_fail(run(gate_command(project, board)),
        "model_registration_gate.py shifted-model fixture",
        expect="P-MODEL-REG FAIL")
    contains(aggregate.out, "0/1 group(s) graded",
             "project gate reports its complete group denominator")


@test("signed side views reject a model whose bulk is below its declared mount side",
      kind="known_bad")
def t_native_registration_rejects_inverted_model_z_side():
    project, board, model_sha = inverted_project()
    direct = must_fail(run([
        KPY, ENGINE, board, project / "direct", "--refs", "J2",
        "--model-sha256", model_sha, "--fit-tol-mm", "1.0",
        "--courtyard-tol-mm", "0.25", "--search-margin-mm", "8.0",
        "--width", "1200", "--height", "800", "--mount-side", "front",
    ]), "inverted signed-mount-side fixture", expect="P-MODEL-REG FAIL")
    contains(direct.out, "measured side-view solid on front mount side",
             "direct gate names the signed-Z body-side failure")

    aggregate = must_fail(run(gate_command(project, board)),
        "aggregate inverted signed-mount-side fixture",
        expect="P-MODEL-REG FAIL")
    contains(aggregate.out, "0/1 group(s) graded",
             "aggregate fails the complete connector group")


@test("package mount side is independent of connector orientation and rejects conflicts", kind="known_bad")
def t_package_mount_side_contract():
    """RED against a1369d44: group mount_side was silently discarded."""
    sys.path.insert(0, str(FAB_SCRIPTS))
    from model_registration_gate import normalized_group
    group = {"refs": ["U1"], "model_sha256": "a" * 64,
             "registration_datum": "all_pad_centres", "mount_side": "front"}
    eq(normalized_group("package", group)["mount_side"], "front")
    legacy = dict(group, orientation={"mount_side": "front"})
    eq(normalized_group("package", legacy)["mount_side"], "front")
    for bad in [dict(group, mount_side="up"),
                dict(group, orientation={"mount_side": "back"})]:
        try:
            normalized_group("package", bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid/conflicting package mount side accepted")


@test("absent vendor body requires exact authority and signed registration; relocated evidence reopens", kind="known_bad", slow=True)
def t_absent_vendor_native_authority():
    import pcbnew
    sys.path.insert(0, str(FAB_SCRIPTS))
    from jlc_twin import retain_absent_vendor_body
    from native_representation import declarations, check_overlay_receipt
    project, board, model_sha = project_fixture(
        registration_datum="all_pad_centres", mount_side="front")
    config_file = project / "03_src/rules/model_registration.yaml"
    config = yaml.safe_load(config_file.read_text())
    config["groups"][0].pop("orientation")
    config["groups"][0]["mount_side"] = "front"
    config_file.write_text(yaml.safe_dump(config))
    must_pass(run([KPY, GATE, project, "--board", board]), "signed native fixture registration")
    b = pcbnew.LoadBoard(str(board)); fp = b.FindFootprintByReference("J2")
    source = project / "03_src"
    footprint = source / (str(fp.GetFPID().GetLibItemName()) + ".kicad_mod")
    footprint.write_text("reviewed fixture footprint authority\n")
    authority = source / "drawing.txt"; authority.write_text("fixture drawing source\n")
    vendor = project / "vendor.kicad_mod"; vendor.write_text('(footprint "fixture" (layer "F.Cu"))\n')
    digest = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
    record = lambda f: {"path": f.relative_to(project).as_posix(), "sha256": digest(f)}
    spec = {"reason": "vendor_model_absent", "mpn": "FixturePart",
            "vendor_footprint_sha256": digest(vendor), "model_sha256": model_sha,
            "registration_group": "shifted_sma", "native_footprint": record(footprint),
            "authority": {**record(authority), "pages": [1], "revision": "A"},
            "generator": record(authority), "provenance": record(authority),
            "reviewer": "independent fixture", "reviewed_on": "2026-09-11",
            "limitations": "Fixture identity, not actual product authority"}
    row = {"lcsc": "C123", "refs": ["J2"], "render_model_source": "native", "native_representation": spec}
    selected = declarations([row])["J2"]
    out = project / "twin"; out.mkdir()
    retained = retain_absent_vendor_body(board, fp, selected, vendor, [], "C123", "FixturePart", out)
    b.Save(str(out / "twin.kicad_pcb"))
    receipt = {"schema": 1, "source_board_sha256": digest(board),
               "twin_board_sha256": digest(out / "twin.kicad_pcb"), "rows": [retained]}
    (out / "native_representation_receipt.json").write_text(json.dumps(receipt))
    moved = project / "moved"; shutil.move(str(out), str(moved))
    original_model = project / "03_src/lib/3dmodels" / SOURCE_MODEL.name
    original_bytes = original_model.read_bytes(); original_model.unlink()
    check_overlay_receipt(moved, board, "J2", "C123", vendor, 0, selected)
    original_model.write_bytes(original_bytes)
    # A distinct NO-CAD path must have independent absence/pin evidence and
    # a current exact transport observation. It never fabricates vendor pads.
    from datetime import datetime, timezone, timedelta
    cad_spec = {k: v for k, v in spec.items() if k != "vendor_footprint_sha256"}
    body = b'{"success":false,"code":404,"message":"Component not found"}'
    cad_spec.update(reason="vendor_cad_absent", catalog_comparison="unavailable",
                    catalog_response_body_sha256=hashlib.sha256(body).hexdigest(),
                    absence_review=record(authority), pin_review=record(authority))
    cad_selected = declarations([{**row, "native_representation": cad_spec}])["J2"]
    cad_out = project / "cad-twin"; cache = cad_out / "easyeda/C123"; cache.mkdir(parents=True)
    stamp = datetime.now(timezone.utc).isoformat()
    observation = {"schema": 1, "lcsc": "C123", "observed_at": stamp,
        "url": "https://easyeda.com/api/products/C123/components",
        "response_url": "https://easyeda.com/api/products/C123/components",
        "status": 200, "classification": "absent", "body_size": len(body),
        "body_sha256": hashlib.sha256(body).hexdigest(), "parsed": json.loads(body)}
    response_file = cache / "catalog-response.json"
    response_file.write_text(json.dumps(observation)); (cache / "catalog-response.body").write_bytes(body)
    cb = pcbnew.LoadBoard(str(board)); cf = cb.FindFootprintByReference("J2")
    cad_retained = retain_absent_vendor_body(board, cf, cad_selected, None, [], "C123", "FixturePart", cad_out)
    cb.Save(str(cad_out / "twin.kicad_pcb"))
    cad_receipt = {"schema": 1, "created_at": datetime.now(timezone.utc).isoformat(),
                   "source_board_sha256": digest(board), "twin_board_sha256": digest(cad_out / "twin.kicad_pcb"),
                   "rows": [cad_retained]}
    (cad_out / "native_representation_receipt.json").write_text(json.dumps(cad_receipt))
    cad_moved = project / "cad-relocated"; shutil.move(str(cad_out), str(cad_moved))
    original_model.unlink(); authority_bytes = authority.read_bytes(); authority.unlink()
    check_overlay_receipt(cad_moved, board, "J2", "C123", None, 0, cad_selected)
    original_model.write_bytes(original_bytes); authority.write_bytes(authority_bytes)
    # Exercise the owning twin CLI with no fetched footprint at all, then
    # actual same-camera renders and the overlay CLI. The exact HTTP seam is
    # independently exercised by t1_jlc_twin; this stub models confirmed NO-CAD.
    cli_out = project / "cad-cli"
    shutil.copytree(cad_moved / "easyeda", cli_out / "easyeda")
    stub = project / "fetch_fixture"
    stub.write_text("#!/bin/sh\nprintf 'no CAD data\\n'\n")
    stub.chmod(0o755)
    bom = project / "bom.csv"; bom.write_text("Designator,LCSC,MPN\nJ2,C123,FixturePart\n")
    cpl = project / "cpl.csv"; cpl.write_text("Designator\nJ2\n")
    adjudications = project / "adjudications.yaml"
    adjudications.write_text(yaml.safe_dump([{**row, "native_representation": cad_spec}]))
    cli = must_pass(run([KPY, FAB_SCRIPTS / "jlc_twin.py", board, bom, cli_out,
                        "--cpl", cpl, "--adjudications", adjudications],
                       env={"EASYEDA2KICAD": str(stub), "JLC_TWIN_FETCH_ATTEMPTS": "1"}),
                    "one native NO-CAD body through actual twin CLI")
    contains(cli.out, "bodies mounted: 1/1", "full CPL denominator")
    report = (cli_out / "twin_report.csv").read_text()
    contains(report, "NO-CAD", "missing catalog claim retained")
    not_vendor = [s for s in ("PAD-GEOM", "PAD-MISMATCH", "fit=0.00") if s in report]
    eq(not_vendor, [], "no fabricated catalog fit")
    overlay_cmd = [KPY, FAB_SCRIPTS / "twin_overlay.py", board, cli_out / "twin_top.png",
                   "--bare", cli_out / "twin_bare_top.png", "--side", "top", "--twin-dir", cli_out,
                   "--bom", bom, "--adjudications", adjudications,
                   "--out", project / "overlay", "--report", project / "overlay.md"]
    must_pass(run(overlay_cmd), "actual NO-CAD body image extraction")
    saved_observation = (cli_out / "easyeda/C123/catalog-response.json").read_bytes()
    (cli_out / "easyeda/C123/catalog-response.json").unlink()
    must_fail(run(overlay_cmd), "NO-CAD overlay requires the actual observation")
    (cli_out / "easyeda/C123/catalog-response.json").write_bytes(saved_observation)
    from native_representation import check_vendor
    cache = cad_moved / "easyeda/C123"; response_file = cache / "catalog-response.json"
    for changes in [{"status": 403}, {"lcsc": "C999"}, {"classification": "unrecognized"},
                    {"observed_at": (datetime.now(timezone.utc)-timedelta(days=2)).isoformat()},
                    {"observed_at": (datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()}]:
        response_file.write_text(json.dumps({**observation, **changes}))
        try:
            check_vendor(cad_selected, "C123", None, 0, cache)
        except ValueError:
            pass
        else:
            raise AssertionError("unproven/stale catalog absence accepted")
    response_file.write_text(json.dumps(observation))
    later_cad = cache / "new.kicad_mod"; later_cad.write_text("new vendor CAD")
    try:
        check_vendor(cad_selected, "C123", None, 0, cache)
    except ValueError:
        pass
    else:
        raise AssertionError("new vendor CAD did not reopen absence selection")
    later_cad.unlink()
    evidence_file = cad_moved / cad_retained["source_files"]["pin_review"]
    evidence_file.write_text("changed review")
    try:
        check_overlay_receipt(cad_moved, board, "J2", "C123", None, 0, cad_selected)
    except ValueError:
        pass
    else:
        raise AssertionError("changed delivered pin review accepted")
    for patch in [dict(row, refs=["J2", "J2"]), dict(row, refs=["J*"]),
                  dict(row, native_representation={**spec, "unknown": True}),
                  dict(row, native_representation={**spec, "registration_group": "../escape"}),
                  dict(row, native_representation={**spec, "authority": {**spec["authority"], "pages": [0]}})]:
        try:
            declarations([patch])
        except ValueError:
            pass
        else:
            raise AssertionError("invalid native selection accepted")
    for patch, count, code in [(selected, 1, "C123"), (selected, 0, "C999"),
                               ({**selected, "vendor_footprint_sha256": "0" * 64}, 0, "C123")]:
        try:
            check_overlay_receipt(moved, board, "J2", code, vendor, count, patch)
        except ValueError:
            pass
        else:
            raise AssertionError("changed vendor body/code/hash accepted")
    (moved / retained["model"]).write_text("changed model")
    try:
        check_overlay_receipt(moved, board, "J2", "C123", vendor, 0, selected)
    except ValueError:
        pass
    else:
        raise AssertionError("changed native model accepted")
    # A shifted source attachment changes the registration tuple even though
    # model bytes and the declaration remain identical.
    original = list(fp.Models())[0]; original.m_Filename = str(project / "03_src/lib/3dmodels" / SOURCE_MODEL.name)
    original.m_Offset.x += 5; fp.Models().clear(); fp.Models().push_back(original); b.Save(str(board))
    try:
        retain_absent_vendor_body(board, fp, selected, vendor, [], "C123", "FixturePart", moved)
    except ValueError:
        pass
    else:
        raise AssertionError("stale signed registration accepted")


def mounted_fixture(side="back"):
    """Three asymmetric local bodies at 0/90/270; asymmetric coupon occupancy."""
    import pcbnew
    project = tmpdir("mounted_side_") / "fixture"
    for directory in ("04_kicad", "03_src/rules", "03_src/lib/3dmodels"):
        (project / directory).mkdir(parents=True, exist_ok=True)
    model = project / "03_src/lib/3dmodels/body.wrl"
    model.write_text('''#VRML V2.0 utf8
Transform { scale 0.393700787 0.393700787 0.393700787 children [
 Transform { translation 0 0 1.5 children [ Shape {
 appearance Appearance { material Material { diffuseColor 0.2 0.2 0.2 } }
 geometry Box { size 1.6 0.8 3.0 } } ] } ] }
''')
    b = pcbnew.BOARD()
    for index, angle in enumerate((0, 90, 270), 1):
        fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Resistor_SMD.pretty",
                                 "R_0603_1608Metric")
        fp.SetReference(f"R{index}"); b.Add(fp)
        # Independent source geometry is displaced from the footprint origin
        # in BOTH axes; KiCad's model Y is opposite board Y on the front.
        for item in [*fp.GraphicalItems(), *fp.Pads()]:
            item.Move(pcbnew.VECTOR2I(2000000, -1000000))
        fp.Models().clear()
        model_pose = pcbnew.FP_3DMODEL(); model_pose.m_Filename = str(model)
        model_pose.m_Offset.x = 2; model_pose.m_Offset.y = 1
        fp.Models().push_back(model_pose)
        if side == "back":
            fp.Flip(fp.GetPosition(), False)
        fp.SetOrientationDegrees(angle)
        fp.SetPosition(pcbnew.VECTOR2I(index * 17000000, index * 13000000))
    board = project / "04_kicad/fixture.kicad_pcb"; b.Save(str(board))
    group = {"id": "mounted", "refs": ["R1", "R2", "R3"],
        "model_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
        "registration_datum": "all_smd_pad_overlap", "mount_side": side,
        "fit_tolerance_mm": 0.2, "courtyard_containment_tolerance_mm": 0.25,
        "search_margin_mm": 1.5, "render_width": 1200, "render_height": 1000}
    (project / "03_src/rules/model_registration.yaml").write_text(
        yaml.safe_dump({"schema": 1, "groups": [group]}))
    return project, board, group


@test("mounted-side native datums reject opposite-side decoys and mixed groups", kind="known_bad")
def t_mounted_side_native_datums():
    # RED verified by swapping the exact frozen pre-fix engine (998dc697...)
    # back into the isolated script tree, then restoring the candidate.
    import pcbnew
    sys.path.insert(0, str(FAB_SCRIPTS))
    import native_model_registration as native
    from model_registration_gate import normalized_group, tuple_for
    project, board, group = mounted_fixture()
    b, rows = native.collect_source_rows(board, group["refs"], group["model_sha256"],
                                         "all_smd_pad_overlap")
    projections = [native.normalized_footprint_projection(row["fp"], "all_smd_pad_overlap")
                   for row in rows]
    eq(projections[0], projections[1], "90 degree normalization")
    eq(projections[0], projections[2], "270 degree normalization")
    values = normalized_group("mounted", group)
    initial, _ = tuple_for(board, values)
    for layer in (pcbnew.B_Fab, pcbnew.B_CrtYd):
        bad = pcbnew.LoadBoard(str(board)); fp = bad.FindFootprintByReference("R1")
        # Keep convincing opposite-side geometry, but no owned-side datum.
        for item in fp.GraphicalItems():
            if item.GetLayer() == layer:
                item.SetLayer(pcbnew.F_Fab if layer == pcbnew.B_Fab else pcbnew.F_CrtYd)
        path = board.with_name(f"decoy-{layer}.kicad_pcb"); bad.Save(str(path))
        failed = must_fail(run(gate_command(project, path)), "opposite-side decoy")
        contains(failed.out, "B.Fab body and B.CrtYd", "owned-side missing geometry")
    fp = b.FindFootprintByReference("R1"); fp.Flip(fp.GetPosition(), False); b.Save(str(board))
    failed = must_fail(run(gate_command(project, board)), "mixed mounted sides")
    contains(failed.out, "mixed mounted-side", "mixed-side group explicitly refused")
    fp.Flip(fp.GetPosition(), False)
    for item in fp.GraphicalItems():
        if item.GetLayer() == pcbnew.B_Fab:
            item.Move(pcbnew.VECTOR2I(100000, 0))
    b.Save(str(board))
    try:
        tuple_for(board, values)
    except ValueError as exc:
        contains(str(exc), "one registration footprint", "changed owned-side geometry invalidates tuple")
    else:
        raise AssertionError("changed B.Fab geometry reused tuple")


@test("mounted-side rendered asymmetric front and back bodies preserve cache and reject faults", kind="known_bad")
def t_mounted_side_rendered_registration():
    import pcbnew
    sys.path.insert(0, str(FAB_SCRIPTS))
    from model_registration_gate import normalized_group, tuple_for
    for side in ("back", "front"):
        project, board, group = mounted_fixture(side)
        must_pass(run(gate_command(project, board)), f"asymmetric {side} native render")
        bundle = project / "06_build/pre_route/native_registration/mounted"
        report = (bundle / "native_model_registration.md").read_text()
        contains(report, f"plan_camera: {'top' if side == 'front' else 'bottom'}", "actual camera")
        receipt = json.loads((bundle / "model_registration_receipt.json").read_text())
        eq(len(receipt["measurements"]), 3, "all normalized orientations rendered")
        for row in receipt["measurements"]:
            eq(row["attachment_overlaps_graded"], 2, "both actual copper polygons overlap")
            check(row["centre_delta_mm"] < .1, "render agrees with independent asymmetric Fab")
        cached = must_pass(run(gate_command(project, board)), "mounted-side cache reopens")
        contains(cached.out, "CACHE-HIT", "unchanged side cache")
        accepted = accepted_bytes(bundle)
        rules = project / "03_src/rules/model_registration.yaml"
        rules.write_text(yaml.safe_dump({"schema": 1, "groups": [{**group,
            "mount_side": "front" if side == "back" else "back"}]}))
        failed = must_fail(run(gate_command(project, board)), "incorrect side declaration")
        contains(failed.out, "differs from actual", "declared vs mounted side")
        check("CACHE-HIT" not in failed.out, "side declaration cannot reuse cache")
        rules.write_text(yaml.safe_dump({"schema": 1, "groups": [group]}))
        b = pcbnew.LoadBoard(str(board)); original = board.read_bytes()
        for fault, offset, rotation in (("displaced", 5, 0), ("inverted", 2, 180),
                                         ("rotated", 2, 90)):
            b = pcbnew.LoadBoard(str(board))
            for fp in b.GetFootprints():
                pose = fp.Models()[0]; pose.m_Offset.x = offset
                if fault == "inverted": pose.m_Rotation.x = rotation
                if fault == "rotated": pose.m_Rotation.z = rotation
                fp.Models()[0] = pose
            b.Save(str(board))
            failed = must_fail(run(gate_command(project, board)), f"{side} {fault} model")
            contains(failed.out, "P-MODEL-REG FAIL", "rendered fault is rejected")
            check("CACHE-HIT" not in failed.out, "native transform invalidates cache")
            eq(accepted_bytes(bundle), accepted, "failed attempt preserves accepted images")
            board.write_bytes(original)
        if side == "back":
            # Discriminate the tempting wrong operator with actual renderer
            # evidence: a 3-site coupon is not invariant under X reflection.
            hostile = project / "wrong-camera"; hostile.mkdir()
            shutil.copy2(FAB_SCRIPTS / "twin_overlay.py", hostile / "twin_overlay.py")
            engine = hostile / ENGINE.name
            engine.write_text(ENGINE.read_text().replace(
                'mirror = plan_camera == "bottom"', 'mirror = False'))
            failed = must_fail(run([KPY, engine, board, project / "unmirrored",
                "--refs", "R1,R2,R3", "--model-sha256", group["model_sha256"],
                "--registration-datum", "all_smd_pad_overlap", "--mount-side", "back",
                "--fit-tol-mm", ".2", "--courtyard-tol-mm", ".25",
                "--search-margin-mm", "1.5", "--width", "1200", "--height", "1000"]),
                "counterfactual unmirrored bottom projection")
            contains(failed.out, "P-MODEL-REG FAIL", "asymmetric pixels discriminate wrong handedness")


@test("native signed-side visibility omits buried model volume",
      kind="vacuity", gate="native_model_registration.py")
def t_native_signed_side_visibility_omits_buried_volume():
    # Independently qualified through native VRML export: this nested model
    # imports with 0.30315 mm outside the back and 0.69685 mm inside the
    # nominal 1.6 mm board. Original front and corrected back engines share
    # the false PASS. The exact direct-coordinate product model is qualified
    # separately; this fixture records the visible-pixel predicate's limit.
    import pcbnew
    project, board, group = mounted_fixture("back")
    model = project / "03_src/lib/3dmodels/body.wrl"
    original_model = model.read_text()
    b = pcbnew.LoadBoard(str(board))
    for fp in b.GetFootprints():
        pose = fp.Models()[0]
        pose.m_Rotation.x = 180
        fp.Models()[0] = pose
    b.Save(str(board))

    def set_height(height):
        # The only independent contrast variable is h; translation h/2
        # preserves the same intended base plane. XY, poses and limits stay.
        model.write_text(original_model.replace(
            "translation 0 0 1.5", f"translation 0 0 {height / 2}").replace(
            "size 1.6 0.8 3.0", f"size 1.6 0.8 {height}"))
        rules = {**group, "model_sha256": hashlib.sha256(model.read_bytes()).hexdigest()}
        (project / "03_src/rules/model_registration.yaml").write_text(
            yaml.safe_dump({"schema": 1, "groups": [rules]}))

    set_height(1.0)
    malicious = must_pass(run(gate_command(project, board)),
                          "visible exterior pixels omit buried model volume")
    contains(malicious.out, "P-MODEL-REG PASS: 1/1 group(s) graded",
             "malicious subject actually graded")
    bundle = project / "06_build/pre_route/native_registration/mounted"
    receipt = json.loads((bundle / "model_registration_receipt.json").read_text())
    eq(len(receipt["measurements"]), 3, "all three native orientations graded")

    set_height(3.0)
    contrast = must_fail(run(gate_command(project, board)),
                         "height-only contrast exposes wrong signed side")
    contains(contrast.out, "native body occupies only", "signed-side failure")
    contains(contrast.out, "minimum is 0.750", "unchanged signed-side floor")


def thin_exterior_fixture(width):
    """Direct-coordinate mesh: no nested transforms or imported shape assumptions."""
    import pcbnew
    project = tmpdir("thin_exterior_") / "fixture"
    for directory in ("04_kicad", "03_src/rules", "03_src/lib/3dmodels"):
        (project / directory).mkdir(parents=True, exist_ok=True)
    model = project / "03_src/lib/3dmodels/body.wrl"
    def box(x0, x1, y0, y1, z0, z1):
        points = [(x,y,z) for z in (z0,z1) for y in (y0,y1) for x in (x0,x1)]
        # KiCad VRML model coordinates are 0.1-inch units; direct mesh only.
        coords = ", ".join(" ".join(str(v / 2.54) for v in p) for p in points)
        return ('Shape { appearance Appearance { material Material { diffuseColor 0.2 0.2 0.2 } } '
                'geometry IndexedFaceSet { solid FALSE coord Coordinate { point [ ' + coords +
                ' ] } coordIndex [0,2,3,1,-1,4,5,7,6,-1,0,1,5,4,-1,2,6,7,3,-1,0,4,6,2,-1,1,3,7,5,-1] } }')
    model.write_text("#VRML V2.0 utf8\n" + box(-.8,.8,-.4,.4,0,1) + "\n" +
                     box(.8,3.0,-width/2,width/2,0,1) + "\n")
    b = pcbnew.BOARD()
    fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Resistor_SMD.pretty", "R_0603_1608Metric")
    fp.SetReference("R1"); b.Add(fp); fp.SetPosition(pcbnew.VECTOR2I(20000000,20000000))
    fp.Models().clear(); pose=pcbnew.FP_3DMODEL();pose.m_Filename=str(model);fp.Models().push_back(pose)
    board=project / "04_kicad/fixture.kicad_pcb";b.Save(str(board))
    group={"id":"thin", "refs":["R1"], "model_sha256":hashlib.sha256(model.read_bytes()).hexdigest(),
           "registration_datum":"all_smd_pad_overlap", "mount_side":"front", "fit_tolerance_mm":.2,
           "courtyard_containment_tolerance_mm":.25,"search_margin_mm":4.0,"render_width":1200,"render_height":1000}
    (project / "03_src/rules/model_registration.yaml").write_text(yaml.safe_dump({"schema":1,"groups":[group]}))
    return project,board


@test("native plan erosion omits thin exterior geometry beyond courtyard",
      kind="vacuity", gate="native_model_registration.py")
def t_native_plan_erosion_omits_thin_exterior_geometry():
    # Subject first: x extent is 3 mm, beyond the unchanged resistor courtyard.
    # A direct mesh avoids the prior nested-transform native-import incident.
    project, board = thin_exterior_fixture(.01)
    blind = must_pass(run(gate_command(project, board)), "thin exterior false PASS")
    contains(blind.out, "P-MODEL-REG PASS: 1/1 group(s) graded", "actual graded subject")
    bundle=project / "06_build/pre_route/native_registration/thin"
    # Reopen the actual native VRML consumer output, including its model mesh.
    export=project / "native.wrl"
    native=run(["kicad-cli","pcb","export","vrml","--units","mm","-o",export,
                bundle / "native_coupon.kicad_pcb"])
    check(native.rc == 0, "native geometry export completed")
    import re
    text=export.read_text()
    arrays=re.findall(r"point\s*\[([^]]+)\]", text, re.S)
    triples=[]
    for array in arrays:
        nums=[float(x) for x in re.findall(r"[-+]?(?:[0-9]*\.)?[0-9]+(?:[eE][-+]?[0-9]+)?",array)]
        triples.extend(zip(nums[::3],nums[1::3],nums[2::3]))
    check(len(arrays) >= 2, "native exporter emitted body and exterior meshes")
    # Closed fixture-specific reader: inspect the two first native mesh blocks
    # and every transform preceding them, refusing an unexpected transform.
    prefix=text[:text.index(arrays[1])]
    scales=re.findall(r"(?m)^  scale ([^\n]+)",prefix)
    eq(scales, ["2.54 2.54 2.54"] + ["1 1 1"] * (len(scales)-1),
       "actual native transform scale population")
    for rotation in re.findall(r"(?m)^  rotation ([^\n]+)",prefix):
        eq(rotation,"0 0 1 0","native mesh has no hidden rotation")
    for translation in re.findall(r"(?m)^  translation ([^\n]+)",prefix):
        values=[float(v) for v in translation.split()]
        eq(values[:2],[0.0,0.0],"native coupon mesh XY origin")
    values=[float(x) for x in re.findall(r"[-+]?(?:[0-9]*\.)?[0-9]+(?:[eE][-+]?[0-9]+)?",arrays[1])]
    feature=list(zip(values[::3],values[1::3],values[2::3]))
    bounds=[min(p[i] for p in feature)*2.54 for i in range(3)]+[max(p[i] for p in feature)*2.54 for i in range(3)]
    for measured,expected in zip(bounds,[.8,-.005,0,3,.005,1]):
        check(abs(measured-expected)<1e-6,"actual imported thin feature dimension")
    check(bounds[3]>1.6+.25,"actual feature beyond unchanged courtyard and tolerance")
    (project / "native-point-census.json").write_text(json.dumps({"points":triples,
        "note":"Native exporter points; placement transform is retained in native.wrl."}))
    # The same endpoint and depth, with only projected width changed.
    thick, thick_board = thin_exterior_fixture(.6)
    contrast=must_fail(run(gate_command(thick,thick_board)),"thickness-only exterior contrast")
    contains(contrast.out,"P-MODEL-REG FAIL","unchanged native gate rejects broad exterior")


if __name__ == "__main__":
    sys.exit(main())
