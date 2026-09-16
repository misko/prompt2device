"""Hostile locator controls; native fixture authored independently of emitter."""
from pathlib import Path
import csv
import contextlib
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import pcbnew
from PIL import Image, ImageDraw, PngImagePlugin

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import assembly_locator as producer
import assembly_locator_check as checker


class LocatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.TemporaryDirectory(prefix="locator-fixture-")
        root = Path(cls.base.name)
        board = pcbnew.BOARD()
        net = pcbnew.NETINFO_ITEM(board, "SIGNAL")
        board.Add(net)
        records = []
        for index, ref in enumerate(["R1", "R2", "R3"], 1):
            x, y = index*10, 10
            fp = pcbnew.FOOTPRINT(board)
            fp.SetReference(ref)
            fp.SetValue("10k")
            fp.SetAttributes(pcbnew.FP_SMD)
            fp.SetPosition(pcbnew.VECTOR2I(x*1000000, y*1000000))
            fp.Reference().SetLayer(pcbnew.F_SilkS)
            fp.Reference().SetVisible(index == 3)
            shape = pcbnew.PCB_SHAPE(fp)
            shape.SetShape(pcbnew.SHAPE_T_RECT)
            shape.SetLayer(pcbnew.F_Fab)
            shape.SetStart(pcbnew.VECTOR2I(int((x-.8)*1e6), int((y-.4)*1e6)))
            shape.SetEnd(pcbnew.VECTOR2I(int((x+.8)*1e6), int((y+.4)*1e6)))
            fp.Add(shape)
            for number, dx in [("1", -.825), ("2", .825)]:
                pad = pcbnew.PAD(fp)
                pad.SetNumber(number)
                pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
                pad.SetShape(pcbnew.PAD_SHAPE_RECT)
                pad.SetSize(pcbnew.VECTOR2I(800000, 950000))
                pad.SetPosition(pcbnew.VECTOR2I(round((x+dx)*1e6), y*1000000))
                layers = pcbnew.LSET()
                layers.AddLayer(pcbnew.F_Cu)
                pad.SetLayerSet(layers)
                pad.SetNet(net)
                fp.Add(pad)
            board.Add(fp)
            if index < 3:
                records.append({"ref": ref, "value": "10k", "mpn": "R-10K", "lcsc": "C100",
                                "x": x, "y": y, "rotation": 0, "side": "top",
                                "pads": [{"number": "1", "net": "SIGNAL"}, {"number": "2", "net": "SIGNAL"}]})
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_RECT)
        edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetStart(pcbnew.VECTOR2I(0, 0))
        edge.SetEnd(pcbnew.VECTOR2I(40000000, 20000000))
        board.Add(edge)
        pcbnew.SaveBoard(str(root / "board.kicad_pcb"), board)
        (root / "bom.csv").write_text('Designator,Comment,MPN,LCSC\n"R1,R2,R3",10k,R-10K,C100\n')
        (root / "cpl.csv").write_text('Designator,Mid X,Mid Y,Layer,Rotation\nR1,10,-10,Top,0\nR2,20,-10,Top,0\nR3,30,-10,Top,0\n')
        (root / "config.yaml").write_text(json.dumps({"schema": 1, "title": "Test board",
            "owner": "test owner", "orientation": "Component side up; origin upper left.", "exceptions": records}))
        producer.generate(root / "board.kicad_pcb", root / "bom.csv", root / "cpl.csv", root / "config.yaml", root / "out")

    @classmethod
    def tearDownClass(cls):
        cls.base.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="locator-hostile-")
        self.root = Path(self.temp.name) / "fixture"
        shutil.copytree(self.base.name, self.root)
        self.out = self.root / "out"

    def tearDown(self):
        self.temp.cleanup()

    def check(self):
        return checker.check(self.root / "board.kicad_pcb", self.root / "bom.csv",
                             self.root / "cpl.csv", self.root / "config.yaml", self.out)

    def read(self, name):
        return json.loads((self.out / name).read_text())

    def write(self, name, data):
        (self.out / name).write_text(json.dumps(data))

    def rehash_members(self):
        doc = self.read("assembly_locator_manifest.json")
        for rec in doc["members"]:
            path = self.out / rec["path"]
            rec.update(sha256=checker.digest(path), size=path.stat().st_size)
        self.write("assembly_locator_manifest.json", doc)

    def update_data(self, mutate):
        data = self.read("assembly_locator.json")
        mutate(data)
        self.write("assembly_locator.json", data)
        html = self.out / "assembly_locator.html"
        text = re.sub(r"const DATA=.*?;const byRef=", lambda _: "const DATA=" + json.dumps(data) + ";const byRef=", html.read_text(), flags=re.S)
        html.write_text(text)
        self.rehash_members()

    def accept_new_input_hash(self, key, path):
        self.update_data(lambda data: data.update({key: checker.digest(path)}))
        manifest = self.read("assembly_locator_manifest.json")
        manifest[key] = checker.digest(path)
        self.write("assembly_locator_manifest.json", manifest)

    def test_clean_full_denominators(self):
        self.assertEqual(self.check(), {"assembled_refs": 3, "pads": 6, "exceptions": 2, "pages": 2, "manifest_members": 5})

    def mixed_fixture(self, rotation=0):
        # Real native flip; off-centre B.Fab and unequal pad offsets distinguish
        # reflection, wrong-side decoys and rotations. RED on frozen top-only
        # source: generation rejects R3; GREEN on mounted-side implementation.
        path = self.root / "board.kicad_pcb"
        board = pcbnew.LoadBoard(str(path))
        fp = board.FindFootprintByReference("R3")
        fp.Flip(fp.GetPosition(), False)
        shape = next(g for g in fp.GraphicalItems() if g.GetClass() == "PCB_SHAPE")
        shape.SetStart(pcbnew.VECTOR2I(28000000, 9200000))
        shape.SetEnd(pcbnew.VECTOR2I(30600000, 10300000))
        pads = sorted(fp.Pads(), key=lambda p: p.GetNumber())
        pads[0].SetPosition(pcbnew.VECTOR2I(28100000, 9700000))
        pads[1].SetPosition(pcbnew.VECTOR2I(30300000, 10100000))
        fp.SetOrientationDegrees(rotation)
        decoy = pcbnew.PCB_SHAPE(fp)
        decoy.SetShape(pcbnew.SHAPE_T_RECT)
        decoy.SetLayer(pcbnew.F_Fab)
        decoy.SetStart(pcbnew.VECTOR2I(31000000, 11000000))
        decoy.SetEnd(pcbnew.VECTOR2I(34000000, 12000000))
        fp.Add(decoy)
        pcbnew.SaveBoard(str(path), board)
        cpl = self.root / "cpl.csv"
        cpl.write_text(cpl.read_text().replace("R3,30,-10,Top,0", f"R3,30,-10,Bottom,{rotation}"))
        producer.generate(path, self.root / "bom.csv", cpl, self.root / "config.yaml", self.out)
        return board, fp

    def test_mixed_side_native_projection_and_ui(self):
        for angle in (0, 90, 270):
            with self.subTest(rotation=angle):
                # reset because Flip is a native operation, not a side flag.
                shutil.copyfile(Path(self.base.name) / "board.kicad_pcb", self.root / "board.kicad_pcb")
                shutil.copyfile(Path(self.base.name) / "cpl.csv", self.root / "cpl.csv")
                board, fp = self.mixed_fixture(angle)
                self.assertEqual(self.check()["assembled_refs"], 3)
                data = self.read("assembly_locator.json")
                row = next(r for r in data["parts"] if r["ref"] == "R3")
                self.assertEqual(row["side"], "bottom")
                self.assertFalse(row["hidden"])
                self.assertEqual(data["hidden"], ["R1", "R2"])
                self.assertIn("Bottom", data["view"])
                text = (self.out / "assembly_locator.html").read_text()
                import xml.etree.ElementTree as ET
                svg = ET.fromstring(re.search(r"<svg\b.*?</svg>", text, re.S).group(0))
                group = next(g for g in svg.findall("g") if g.get("data-ref") == "R3")
                rect = group.find("rect")
                body = next(g for g in fp.GraphicalItems() if g.GetClass() == "PCB_SHAPE" and g.GetLayer() == pcbnew.B_Fab).GetBoundingBox()
                edge = board.GetBoardEdgesBoundingBox()
                expected_left = (2*edge.GetX()+edge.GetWidth()-body.GetX()-body.GetWidth())/1e6
                self.assertAlmostEqual(float(rect.get("x")), expected_left, places=6)
                self.assertNotAlmostEqual(float(rect.get("x")), body.GetX()/1e6, places=3)
                runtime = shutil.which("bun") or shutil.which("node")
                result = subprocess.run([runtime, str(Path(__file__).with_name("locator_ui_control.js")), str(self.out / "assembly_locator.html")], capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bottom_wrong_native_side_and_body_rejected(self):
        self.mixed_fixture()
        original = self.read("assembly_locator.json")
        for key, value, message in [("side", "top", "side"), ("body", [31, 11, 34, 12], "body geometry")]:
            self.update_data(lambda d: d.update(json.loads(json.dumps(original))))
            self.update_data(lambda d: next(r for r in d["parts"] if r["ref"] == "R3").update({key: value}))
            with self.assertRaisesRegex(ValueError, message):
                self.check()

    def test_bottom_unmirrored_html_rejected(self):
        self.mixed_fixture()
        row = next(r for r in self.read("assembly_locator.json")["parts"] if r["ref"] == "R3")
        path = self.out / "assembly_locator.html"
        text = path.read_text()
        text = re.sub(r'(<g class="part" data-ref="R3">.*?<rect class="body" x=")[^"]+', lambda m: m.group(1) + str(row["body"][0]), text, count=1)
        path.write_text(text)
        self.rehash_members()
        with self.assertRaisesRegex(ValueError, "HTML body geometry"):
            self.check()

    def test_bottom_cpl_side_rejected(self):
        self.mixed_fixture()
        path = self.root / "cpl.csv"
        path.write_text(path.read_text().replace("Bottom", "Top"))
        self.accept_new_input_hash("cpl_sha256", path)
        with self.assertRaisesRegex(ValueError, "CPL side R3"):
            self.check()

    def test_bottom_fab_requires_mounted_layer(self):
        self.mixed_fixture()
        path = self.root / "board.kicad_pcb"
        board = pcbnew.LoadBoard(str(path))
        fp = board.FindFootprintByReference("R3")
        for shape in list(fp.GraphicalItems()):
            if shape.GetClass() == "PCB_SHAPE" and shape.GetLayer() == pcbnew.B_Fab:
                fp.Remove(shape)
        pcbnew.SaveBoard(str(path), board)
        self.accept_new_input_hash("board_sha256", path)
        with self.assertRaisesRegex(ValueError, "missing native body R3"):
            self.check()
        with self.assertRaisesRegex(ValueError, "missing native body context for R3"):
            producer.collect(path, self.root / "bom.csv", self.root / "cpl.csv", self.root / "config.yaml")

    def test_native_frame_and_declared_projection_rejected(self):
        for mutate, message in [(lambda d: d["frame"].__setitem__(0, 1), "board frame"),
                                (lambda d: d.update(view="Bottom X right, unmirrored"), "viewing convention")]:
            original = self.read("assembly_locator.json")
            self.update_data(mutate)
            with self.assertRaisesRegex(ValueError, message):
                self.check()
            self.update_data(lambda d: d.update(original))

    def test_fresh_dom_startup_references(self):
        # RED against exact reviewed candidate1, including native mixed sides;
        # GREEN after fail-closed startup and malformed-fragment handling.
        self.mixed_fixture()
        runtime = shutil.which("bun") or shutil.which("node")
        result = subprocess.run([runtime, str(Path(__file__).with_name("locator_ui_control.js")),
                                 str(self.out / "assembly_locator.html")], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("8/8 independent fresh-DOM startup cases", result.stdout)

    def test_stale_board(self):
        path = self.root / "board.kicad_pcb"
        path.write_text(path.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "stale board"):
            self.check()

    def test_bom_mpn_mutation_with_fresh_hash(self):
        path = self.root / "bom.csv"
        path.write_text(path.read_text().replace("R-10K", "WRONG-MPN"))
        self.accept_new_input_hash("bom_sha256", path)
        with self.assertRaisesRegex(ValueError, "BOM identity"):
            self.check()

    def test_cpl_coordinate_side_rotation_with_fresh_hash(self):
        path = self.root / "cpl.csv"
        original = path.read_text()
        for replacement, reason in [("R1,11,-10,Top,0", "datum"), ("R1,10,-10,Bottom,0", "side"), ("R1,10,-10,Top,90", "rotation")]:
            with self.subTest(reason=reason):
                path.write_text(original.replace("R1,10,-10,Top,0", replacement))
                self.accept_new_input_hash("cpl_sha256", path)
                with self.assertRaisesRegex(ValueError, "CPL " + reason):
                    self.check()

    def test_missing_reference(self):
        self.update_data(lambda data: data["parts"].pop())
        with self.assertRaisesRegex(ValueError, "denominator"):
            self.check()

    def test_duplicate_reference(self):
        self.update_data(lambda data: data["parts"].__setitem__(1, data["parts"][0]))
        with self.assertRaisesRegex(ValueError, "reference set/duplicate"):
            self.check()

    def test_swapped_pad_net(self):
        self.update_data(lambda data: data["parts"][0]["pads"][0].update(net="WRONG_NET"))
        with self.assertRaisesRegex(ValueError, "pad identity"):
            self.check()

    def test_extra_hidden_native_reference(self):
        path = self.root / "board.kicad_pcb"
        board = pcbnew.LoadBoard(str(path))
        board.FindFootprintByReference("R3").Reference().SetVisible(False)
        pcbnew.SaveBoard(str(path), board)
        self.accept_new_input_hash("board_sha256", path)
        with self.assertRaisesRegex(ValueError, "omission sets"):
            self.check()

    def test_html_data_disagreement(self):
        path = self.out / "assembly_locator.html"
        path.write_text(path.read_text().replace('"value":"10k"', '"value":"WRONG"', 1))
        self.rehash_members()
        with self.assertRaisesRegex(ValueError, "HTML/JSON"):
            self.check()

    def test_missing_and_duplicate_page_records(self):
        original = self.read("assembly_locator_manifest.json")
        for records in [original["page_refs"][:1], [original["page_refs"][0], original["page_refs"][0]]]:
            doc = dict(original, page_refs=records)
            self.write("assembly_locator_manifest.json", doc)
            with self.assertRaisesRegex(ValueError, "atlas"):
                self.check()

    def test_wrong_pdf_page_order_even_with_rehashed_manifest(self):
        pages = [Image.open(self.out / f"assembly_locator_{i:03d}.png").convert("RGB") for i in [2, 1]]
        pages[0].save(self.out / "assembly_locator.pdf", save_all=True, append_images=pages[1:], resolution=200)
        self.rehash_members()
        with self.assertRaisesRegex(ValueError, "PDF/PNG"):
            self.check()

    def test_wrong_png_reference_even_with_rehashed_manifest(self):
        shutil.copyfile(self.out / "assembly_locator_002.png", self.out / "assembly_locator_001.png")
        self.rehash_members()
        with self.assertRaisesRegex(ValueError, "PNG reference"):
            self.check()

    def test_missing_manifest_member(self):
        (self.out / "assembly_locator_001.png").unlink()
        with self.assertRaisesRegex(ValueError, "missing/corrupt"):
            self.check()

    def test_corrupt_manifest_member(self):
        path = self.out / "assembly_locator_001.png"
        path.write_bytes(path.read_bytes() + b"corrupt")
        with self.assertRaisesRegex(ValueError, "missing/corrupt"):
            self.check()

    def test_unknown_query_clears_previous_selection(self):
        runtime = shutil.which("bun") or shutil.which("node")
        self.assertIsNotNone(runtime, "JavaScript runtime required for locator transition control")
        result = subprocess.run([runtime, str(Path(__file__).with_name("locator_ui_control.js")),
                                 str(self.out / "assembly_locator.html")], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_html_wrong_body_with_correct_data(self):
        path = self.out / "assembly_locator.html"
        path.write_text(path.read_text().replace('class="body" x="', 'class="body" x="1', 1))
        self.rehash_members()
        with self.assertRaisesRegex(ValueError, "HTML body geometry"):
            self.check()

    def test_html_selection_code_changed(self):
        path = self.out / "assembly_locator.html"
        path.write_text(path.read_text().replace("location.hash='';", "location.hash='R1';", 1))
        self.rehash_members()
        with self.assertRaisesRegex(ValueError, "HTML executable"):
            self.check()

    def test_wrong_unique_reference(self):
        self.update_data(lambda data: data["parts"][0].update(ref="WRONG_REF"))
        with self.assertRaisesRegex(ValueError, "reference set"):
            self.check()

    def make_release(self):
        release = self.root / "07_releases/v1-2026-09-11"
        source = release / "source"
        source.mkdir(parents=True)
        shutil.copytree(self.out, release / "fab")
        for old, new in [("board.kicad_pcb", "board.kicad_pcb"), ("config.yaml", "assembly_locator.yaml")]:
            shutil.copyfile(self.root / old, source / new)
        for name in ["bom.csv", "cpl.csv"]:
            shutil.copyfile(self.root / name, release / "fab" / name)
        (source / "locator_tools").mkdir()
        for name in ["assembly_locator.py", "assembly_locator.html", "assembly_locator_check.py"]:
            shutil.copyfile(SCRIPTS / name, source / "locator_tools" / name)
        waiver = [{"id": "P-SILK-REF", "refs": ["R1", "R2"],
                   "why": "These exact two references use the independently reviewed assembly atlas and native identity records.",
                   "evidence": [{"command": "/usr/bin/python3 assembly_locator_check.py project fixture"}]}]
        (source / "policy_waivers.yaml").write_text(json.dumps(waiver))
        self.write_review(release / "verification/render_review.md")
        return release

    def write_review(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("reviewer: synthetic fixture reviewer\ncompleted_at: 2026-09-11T00:00:00Z\n"
            "review_stage: pre-route\nreview_kind: render\ndesign_verdict: SOUND\n"
            "board_sha256: " + checker.digest(self.root / "board.kicad_pcb") + "\n"
            "locator_manifest_sha256: " + checker.digest(self.out / "assembly_locator_manifest.json") + "\n"
            'locator_reviewed_refs: ["R1", "R2"]\n')

    def make_project(self):
        release = self.make_release()
        rules = self.root / "03_src/rules"
        rules.mkdir(parents=True)
        shutil.copyfile(self.root / "config.yaml", rules / "assembly_locator.yaml")
        shutil.copyfile(release / "source/policy_waivers.yaml", rules / "policy_waivers.yaml")
        self.write_review(self.root / "08_reviews/pre-route_render.md")
        part = self.root / "02_parts/R-10K/part.yaml"
        part.parent.mkdir(parents=True)
        part.write_text("mpn: R-10K\n")
        part_sha = hashlib.sha256(part.relative_to(self.root).as_posix().encode() + b"\0" + part.read_bytes() + b"\0").hexdigest()
        board_sha = checker.digest(self.root / "board.kicad_pcb")
        for kind in ("pin", "layout"):
            (self.root / f"08_reviews/pre-route_{kind}.md").write_text(
                f"review_stage: pre-route\nreview_kind: {kind}\ndesign_verdict: SOUND\n"
                f"board_sha256: {board_sha}\nparts_sha256: {part_sha}\n")
        (self.root / "08_reviews/overlay.md").write_text(f"a-render_verdict: PASS\nboard_sha256: {board_sha}\n")
        config = {"flow": {"pre_route_reviews": {"board": "board.kicad_pcb",
            **{kind: f"08_reviews/pre-route_{kind}.md" for kind in ("pin", "layout", "render")},
            "a_render": "08_reviews/overlay.md"}}}
        (self.root / "03_src/route.yaml").write_text(json.dumps(config))
        target = self.root / "06_build/pre_route/current_assembly"
        shutil.copytree(self.out, target)
        for name in ("bom.csv", "cpl.csv"):
            shutil.copyfile(self.root / name, target / name)
        return release, target

    def test_rehashed_visible_tamper_stales_independent_acceptance(self):
        # The original checker accepted this actual false label after rehash.
        # Exact identity checking still cannot read pixels; owning review gates
        # must reject the now-unreviewed manifest instead.
        release, target = self.make_project()
        sys.path.insert(0, str(SCRIPTS.parents[1] / "kicad-pcb/scripts"))
        import pre_route_review_check
        def placement():
            output = io.StringIO()
            with patch("promoted_route_check.check", return_value=([], "fixture: no promoted route", 0, 0, 0)), contextlib.redirect_stdout(output):
                code = pre_route_review_check.main([str(self.root), "--phase", "placement"])
            return code, output.getvalue()
        self.assertEqual(placement()[0], 0)
        self.assertEqual(checker.release_check(release)["pages"], 2)
        page = self.out / "assembly_locator_001.png"
        with Image.open(page) as original:
            altered = original.convert("RGB")
            metadata = PngImagePlugin.PngInfo()
            for key, value in original.info.items():
                if isinstance(value, str):
                    metadata.add_text(key, value)
        drawing = ImageDraw.Draw(altered)
        drawing.rectangle((0, 0, 1000, 140), fill="white")
        drawing.text((20, 30), "WRONG VISIBLE ID: J999", fill="black")
        altered.save(page, pnginfo=metadata)
        images = [Image.open(self.out / row["path"]).convert("RGB")
                  for row in self.read("assembly_locator_manifest.json")["page_refs"]]
        images[0].save(self.out / "assembly_locator.pdf", format="PDF", save_all=True,
                       append_images=images[1:], resolution=200)
        for image in images:
            image.close()
        self.rehash_members()
        self.assertEqual(self.check()["pages"], 2)
        shutil.copytree(self.out, target, dirs_exist_ok=True)
        shutil.copytree(self.out, release / "fab", dirs_exist_ok=True)
        code, output = placement()
        self.assertNotEqual(code, 0)
        self.assertIn("A-LOCATOR: independent locator review manifest is stale", output)
        with self.assertRaisesRegex(ValueError, "review manifest is stale"):
            checker.release_check(release)

    def test_visual_review_requires_complete_unique_refs_and_sound_verdict(self):
        release = self.make_release()
        path = release / "verification/render_review.md"
        original = path.read_text()
        for before, after, error in [
            ('["R1", "R2"]', '["R1"]', "reference coverage"),
            ('["R1", "R2"]', '["R1", "R1"]', "reference coverage"),
            ('["R1", "R2"]', '["R1", "WRONG"]', "reference coverage"),
            ("design_verdict: SOUND", "design_verdict: DEFECTIVE", "not SOUND"),
            ("reviewer: synthetic fixture reviewer", "reviewer:", "reviewer/date"),
        ]:
            path.write_text(original.replace(before, after))
            with self.assertRaisesRegex(ValueError, error):
                checker.release_check(release)
        path.unlink()
        with self.assertRaisesRegex(ValueError, "render review is missing"):
            checker.release_check(release)

    def test_release_reads_only_its_shipped_sources(self):
        release = self.make_release()
        (self.root / "bom.csv").write_text("mutable project changed")
        self.assertEqual(checker.release_check(release)["exceptions"], 2)

    def test_release_missing_source_and_wrong_waiver_set(self):
        release = self.make_release()
        config = release / "source/assembly_locator.yaml"
        data = config.read_bytes()
        config.unlink()
        with self.assertRaisesRegex(ValueError, "source contract"):
            checker.release_check(release)
        config.write_bytes(data)
        waiver = release / "source/policy_waivers.yaml"
        entries = json.loads(waiver.read_text())
        entries[0]["refs"] = ["R1"]
        waiver.write_text(json.dumps(entries))
        with self.assertRaisesRegex(ValueError, "waiver/locator sets"):
            checker.release_check(release)

    def test_freshness_composes_locator_failure(self):
        import release_freshness_check
        release = self.make_release()
        (release / "fab/assembly_locator_001.png").unlink()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = release_freshness_check.main([str(release), "--claim", "design"])
        self.assertNotEqual(result, 0)
        self.assertIn("A-LOCATOR FAIL", output.getvalue())

    def test_project_requires_human_waiver(self):
        rules = self.root / "03_src/rules"
        rules.mkdir(parents=True)
        shutil.copyfile(self.root / "config.yaml", rules / "assembly_locator.yaml")
        with self.assertRaisesRegex(ValueError, "source policy waiver"):
            checker.project_check(self.root, self.root / "board.kicad_pcb", self.out)

    def test_placement_review_composes_locator_failure(self):
        kicad = SCRIPTS.parents[1] / "kicad-pcb/scripts"
        sys.path.insert(0, str(kicad))
        import pre_route_review_check
        rules = self.root / "03_src/rules"
        rules.mkdir(parents=True)
        shutil.copyfile(self.root / "config.yaml", rules / "assembly_locator.yaml")
        part = self.root / "02_parts/R-10K"
        part.mkdir(parents=True)
        (part / "part.yaml").write_text("mpn: R-10K\n")
        config = {"flow": {"pre_route_reviews": {"board": "board.kicad_pcb",
            "pin": "missing-pin.md", "layout": "missing-layout.md", "render": "missing-render.md", "a_render": "missing-overlay.md"}}}
        (self.root / "03_src/route.yaml").write_text(json.dumps(config))
        output = io.StringIO()
        with patch("promoted_route_check.check", return_value=([], "fixture: no promoted route", 0, 0, 0)), contextlib.redirect_stdout(output):
            result = pre_route_review_check.main([str(self.root), "--phase", "placement"])
        self.assertNotEqual(result, 0)
        self.assertIn("A-LOCATOR", output.getvalue())
        self.assertIn("source policy waiver record is missing", output.getvalue())


if __name__ == "__main__":
    unittest.main()
