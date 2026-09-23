"""Native synthetic profile fixture; no Crow board generation or routing."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
PARTDIR = ROOT / "projects/crow-usb-carrier-v1/03_src/lib/crow_usb_analog.pretty"
ASSEMBLY = ROOT / "projects/crow-usb-carrier-v1/03_src/rules/assembly.yaml"
COUPON_PRO = ROOT / "projects/crow-usb-carrier-v1/02_parts/TMUX4827YBHR/qualification/coupon.kicad_pro"
FAB = ROOT / "skills/jlcpcb-fab/scripts"
sys.path.insert(0, str(FAB))
from generate_tmux4827_pofv import emit
from via_process_check import check
from tmux4827_pofv import audit, contract, dru_rules
import yaml


def fixture(path):
    b = p.BOARD(); b.SetCopperLayerCount(4)
    nets = {}
    for name in ("GND", *[f"SIG{i}_{j}" for i in range(1,9) for j in (1,2,3,4,6,7,8,9)]):
        n = p.NETINFO_ITEM(b,name);b.Add(n);nets[name]=n
    for i in range(1,9):
        f = p.FootprintLoad(str(PARTDIR), "TI_YBH0009_C02_TMUX4827")
        f.SetFPIDAsString("crow_usb_analog:TI_YBH0009_C02_TMUX4827")
        f.SetReference(f"U_ISO{i}");f.SetValue("TMUX4827YBHR")
        f.SetPosition(p.VECTOR2I_MM(10+i*5,20));b.Add(f)
        for pad in f.Pads():
            pad.SetNet(nets["GND" if pad.GetNumber()=="5" else f"SIG{i}_{pad.GetNumber()}"])
        c=next(x for x in f.Pads() if x.GetNumber()=="5")
        v=p.PCB_VIA(b);v.SetPosition(c.GetPosition());v.SetWidth(p.FromMM(.35));v.SetDrill(p.FromMM(.20));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets["GND"]);v.SetPrimaryDrillFilledFlag(True);v.SetPrimaryDrillCappedFlag(True);b.Add(v)
    p.SaveBoard(str(path),b)
    project=json.loads(COUPON_PRO.read_text())
    project["board"]["design_settings"]["rules"].update(min_via_diameter=.45,min_via_annular_width=.13)
    project["board"]["design_settings"]["rules"]["min_clearance"] = .15
    project["net_settings"]["classes"][0]["clearance"] = .15
    path.with_suffix(".kicad_pro").write_text(json.dumps(project))
    path.with_suffix(".kicad_dru").write_text("(version 1)\n")


class TmuxProfile(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.board=Path(self.tmp.name)/"profile.kicad_pcb"
        fixture(self.board)
        self.assertTrue(emit(self.board, ASSEMBLY))

    def result(self):
        return check(self.board, str(ASSEMBLY))["fails"]

    def mutate(self, fn):
        pro=self.board.with_suffix(".kicad_pro")
        saved=pro.read_text()
        b=p.LoadBoard(str(self.board));fn(b);p.SaveBoard(str(self.board),b)
        pro.write_text(saved)

    def vias(self,b):
        return [v for v in b.GetTracks() if v.GetClass()=="PCB_VIA"]

    def test_positive(self):
        self.assertEqual(self.result(), [])
        self.assertTrue(emit(self.board, ASSEMBLY))
        self.assertEqual(self.result(), [])

    def test_wrong_net_offset_missing_fill_and_cap(self):
        for change in ("net","offset","fill","cap","missing","diameter","drill"):
            with self.subTest(change=change):
                fixture(self.board);emit(self.board,ASSEMBLY)
                def alter(b):
                    v=self.vias(b)[0]
                    if change=="net":
                        v.SetNet(b.FindNet("SIG1_1"))
                        profile,part,_=contract(yaml.safe_load(ASSEMBLY.read_text()),ASSEMBLY)
                        self.assertTrue(any("TMUX-VIA" in s for s in audit(b,profile,part)))
                        return
                    elif change=="offset":v.SetPosition(p.VECTOR2I_MM(15.03,20))
                    elif change=="fill":v.SetPrimaryDrillFilledFlag(False)
                    elif change=="cap":v.SetPrimaryDrillCappedFlag(False)
                    elif change=="missing":b.Remove(v)
                    elif change=="diameter":v.SetWidth(p.FromMM(.4))
                    elif change=="drill":v.SetDrill(p.FromMM(.25))
                self.mutate(alter)
                if change != "net":
                    self.assertTrue(any("TMUX-VIA" in s for s in self.result()))

    def test_extra_protected_and_foreign_area_member(self):
        def alter(b):
            v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I_MM(2,2));v.SetWidth(p.FromMM(.35));v.SetDrill(p.FromMM(.2));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet("GND"));v.SetPrimaryDrillFilledFlag(True);v.SetPrimaryDrillCappedFlag(True);b.Add(v)
        self.mutate(alter)
        self.assertTrue(any("outside exact" in s for s in self.result()))

    def test_wrong_ref_pad_neighbor_and_area(self):
        for change in ("ref","pad","neighbor","area","stale_area","footprint"):
            with self.subTest(change=change):
                fixture(self.board);emit(self.board,ASSEMBLY)
                def alter(b):
                    f=next(f for f in b.GetFootprints() if f.GetReference()=="U_ISO1")
                    if change=="ref":f.SetReference("U_WRONG")
                    elif change=="pad":next(x for x in f.Pads() if x.GetNumber()=="5").SetName("B2")
                    elif change=="neighbor":next(x for x in f.Pads() if x.GetNumber()=="2").SetPosition(p.VECTOR2I_MM(15,19.95))
                    elif change=="area":b.Remove(next(z for z in b.Zones() if z.GetZoneName().endswith("U_ISO1")))
                    elif change=="stale_area":next(z for z in b.Zones() if z.GetZoneName().endswith("U_ISO1")).Move(p.VECTOR2I_MM(.1,0))
                    elif change=="footprint":f.SetFPIDAsString("wrong:TI_YBH0009_C02_TMUX4827")
                self.mutate(alter)
                self.assertTrue(self.result())

    def test_coupon_and_global_dru_exception(self):
        data=yaml.safe_load(ASSEMBLY.read_text())
        data["via_process"]["named_profiles"][0]["evidence"]["coupon_sha256"]="0"*64
        local=Path(self.tmp.name)/"bad_assembly.yaml";local.write_text(yaml.safe_dump(data))
        # Contract paths are project-relative. A modified source copy in the
        # actual project is unnecessary: call contract with the real path.
        with self.assertRaises(ValueError):contract(data,ASSEMBLY)
        dru=self.board.with_suffix(".kicad_dru")
        dru.write_text(dru.read_text()+"\n(rule \"leak\" (condition \"A.NetName == 'GND'\") (constraint clearance (min 0.10mm)))\n")
        self.assertTrue(any("foreign" in s for s in self.result()))
        dru.write_text(dru.read_text().replace('(rule "leak" (condition "A.NetName == \'GND\'") (constraint clearance (min 0.10mm)))',
                                               '(rule "leak" (condition "A.NetName == \'GND\'") (constraint clearance (min -1mm)))'))
        self.assertTrue(any("foreign" in s for s in self.result()))
        dru.write_text(dru.read_text().split('\n(rule "leak"')[0] +
                       '\n  (rule "indented_leak" (condition "A.NetName == \'GND\'") (constraint clearance (min .1)))\n')
        self.assertTrue(any("foreign" in s for s in self.result()))

    def test_schema_rejects_widened_identity(self):
        source=yaml.safe_load(ASSEMBLY.read_text())
        for key,value in (("refs",["U_ISO1"]*8),("net","5V"),("pad","B2"),
                          ("tier","jlc_4layer_standard"),("expected_count",9)):
            with self.subTest(key=key):
                data=copy.deepcopy(source)
                data["via_process"]["named_profiles"][0][key]=value
                with self.assertRaises(ValueError):contract(data,ASSEMBLY)
        data=copy.deepcopy(source)
        data["via_process"]["named_profiles"][0]["geometry"]["via_diameter_mm"] = .45
        with self.assertRaises(ValueError):contract(data,ASSEMBLY)

    def test_native_ordinary_via_floor_and_b2_clearance(self):
        # Use exactly the authored ordinary board minima on input. The
        # producer changes only the physical envelope and emits both scopes.
        pro=self.board.with_suffix(".kicad_pro")
        saved=json.loads(pro.read_text())
        self.assertEqual(saved["board"]["design_settings"]["rules"]["min_via_diameter"],.45)
        def drc():
            result=subprocess.run(["kicad-cli","pcb","drc",str(self.board),"-o",str(Path(self.tmp.name)/"drc.txt")],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            return (Path(self.tmp.name)/"drc.txt").read_text()
        positive=drc()
        self.assertNotIn("[via_diameter]",positive)
        self.assertNotIn("[annular_width]",positive)
        self.assertNotIn("actual 0.1000 mm",positive)
        dru=self.board.with_suffix(".kicad_dru")
        scoped=dru.read_text()
        for rule in dru_rules():
            if rule.split('"')[1].endswith("_via"):
                scoped=scoped.replace(rule,"")
        dru.write_text(scoped)
        hard_report=drc()
        self.assertIn("[via_diameter]: Via diameter (rule 'tmux_ordinary_via_floor'",hard_report)
        self.assertIn("[annular_width]: Annular width (rule 'tmux_ordinary_via_floor'",hard_report)
        emit(self.board,ASSEMBLY)
        def extra(b):
            v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I_MM(2,2));v.SetWidth(p.FromMM(.35));v.SetDrill(p.FromMM(.2));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet("GND"));b.Add(v)
        self.mutate(extra)
        hostile=drc()
        self.assertIn("[via_diameter]: Via diameter (rule 'tmux_ordinary_via_floor'",hostile)
        self.assertIn("[annular_width]: Annular width (rule 'tmux_ordinary_via_floor'",hostile)


if __name__ == "__main__":
    unittest.main()
