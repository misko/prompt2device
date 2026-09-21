#!/usr/bin/env python3
"""T1: early interface, assembly, and protected-route admission."""
import json
import importlib.util
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import (  # noqa: E402
    KPY, ROOT, contains, main, must_fail, must_pass, run, test, tmpdir,
)


GATE = ROOT / "skills/pcb-design/scripts/design_decision_admission.py"
CRITICAL = ROOT / "skills/kicad-pcb/scripts/critical_route_check.py"
CASE_DRIVER = ROOT / "tests/checkpoints/cases/crow_decision_admission/driver.py"


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("decision_admission_tested", GATE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def case_workspace(mode=None):
    root = tmpdir("decision_case_control_")
    workspace = root / "workspace"
    must_pass(run([KPY, CASE_DRIVER, "prepare", ROOT, workspace]),
              "prepare decision checkpoint")
    if mode:
        must_pass(run([KPY, CASE_DRIVER, mode, ROOT, workspace]),
                  f"apply {mode} control")
    return workspace


def _write_part(root, name, pins):
    target = root / "02_parts" / name
    target.mkdir(parents=True)
    target.joinpath("part.yaml").write_text(
        f"mpn: {name}\n"
        f"footprint: Fixture:{name}\n"
        f"sourcing: {{lcsc: C{'100' if name == 'CONN' else '200'}}}\n"
        "pins:\n" + "".join(f"  {pin}: P{pin}\n" for pin in pins))


def fixture():
    root = tmpdir("decision_admission_")
    for path in ("03_src/rules", "03_src/reviews", "03_tscircuit/build", "04_kicad"):
        (root / path).mkdir(parents=True, exist_ok=True)
    _write_part(root, "CONN", ("1", "2", "3", "4"))
    _write_part(root, "TERM", ("1", "2"))
    circuit = []
    for ci, (ref, mpn, code, pins) in enumerate((
            ("J1", "CONN", "C100", ("1", "2", "3", "4")),
            ("U1", "TERM", "C200", ("1", "2")))):
        cid = f"source_component_{ci}"
        circuit.append({"type": "source_component", "source_component_id": cid,
                        "name": ref, "manufacturer_part_number": mpn,
                        "supplier_part_numbers": {"jlcpcb": [code]}})
        circuit.extend(
            {"type": "source_port", "source_component_id": cid,
             "source_port_id": f"{cid}_p{pin}", "pin_number": int(pin),
             "name": f"P{pin}", "port_hints": [f"pin{pin}", pin]}
            for pin in pins)
    (root / "03_tscircuit/build/circuit.json").write_text(json.dumps(circuit))
    (root / "03_src/rules/assembly.yaml").write_text(
        "schema: 1\nservice: JLCPCB_PCBA\nsides: [top]\n"
        "not_assembled: []\nconsigned: []\n")
    (root / "03_src/floorplan.yaml").write_text(
        "constraints:\n  pad_net:\n"
        "    - {ref: J1, pad: '1', net: CLK_P}\n"
        "    - {ref: J1, pad: '2', net: CLK_N}\n")
    route = {
        "prep": {"waves": {"groups": {"clock": ["CLK_P", "CLK_N"]}}},
        "route": {
            "preflight_critical_pairs": [{
                "name": "CLOCK", "p": "CLK_P", "n": "CLK_N",
                "wave": "clock", "allowed_layers": ["F.Cu"],
                "no_vias": True,
            }],
            "waves": [{"name": "clock", "group": "clock", "engine": "diff",
                       "layers": ["F.Cu"],
                       "length_match_group": ["CLK_P", "CLK_N"]}],
        },
    }
    for rel in ("03_src/route.yaml", "03_src/reviews/accepted-route.yaml"):
        (root / rel).write_text(yaml.safe_dump(route, sort_keys=False))
    nets = {
        "length_match": {
            "MCH_INPUT_SECTIONS": {
                "adr": "0010-route-stack-and-current-paths",
                "intent": "Crow-inspired reduced digital sections remain via-free",
                "members": {"MCLK": ["CLK_P"], "BCLK": ["CLK_N"]},
                "topology": "chain", "no_vias": True,
                "max_spread_mm": "report",
            }
        }
    }
    for rel in ("03_src/rules/nets.yaml", "03_src/reviews/accepted-nets.yaml"):
        (root / rel).write_text(yaml.safe_dump(nets, sort_keys=False))
    board = root / "04_kicad/demo.kicad_pcb"
    code = r'''
import pcbnew,sys
b=pcbnew.CreateEmptyBoard()
nets={}
for name in ('CLK_P','CLK_N'):
 n=pcbnew.NETINFO_ITEM(b,name); b.Add(n); nets[name]=n
for ri,(ref,value,pins) in enumerate((('J1','CONN',(('1','CLK_P'),('2','CLK_N'),('3','CLK_P'),('4','CLK_N'))),('U1','TERM',(('1','CLK_P'),('2','CLK_N'))))):
 f=pcbnew.FOOTPRINT(b); f.SetReference(ref); f.SetValue(value); f.SetLayer(pcbnew.F_Cu); b.Add(f)
 for pi,(number,net) in enumerate(pins):
  p=pcbnew.PAD(f); p.SetNumber(number); p.SetShape(pcbnew.PAD_SHAPE_RECT)
  p.SetSize(pcbnew.VECTOR2I_MM(1,1)); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
  p.SetLayerSet(pcbnew.PAD.SMDMask()); p.SetNet(nets[net]); f.Add(p)
  p.SetPosition(pcbnew.VECTOR2I_MM(10+pi*1.5,10+ri*5))
pcbnew.SaveBoard(sys.argv[1],b)
'''
    must_pass(run([KPY, "-c", code, board]), "native fixture board")
    return root, board


def gate(root, board=None, phase="native", *, lock=True, require_lock=True):
    args = [KPY, GATE, root, "--phase", phase]
    if require_lock:
        args += ["--require-locked-route", "--require-locked-nets"]
    if lock:
        args += ["--locked-route", "03_src/reviews/accepted-route.yaml",
                 "--locked-nets", "03_src/reviews/accepted-nets.yaml"]
    if phase == "native":
        args += ["--board", board]
    return run(args)


@test("design admission CLI accepts complete source and native decisions")
def t_cli_clean():
    root, board = fixture()
    source = must_pass(gate(root, phase="source"), "source admission")
    contains(source.out, '"phase": "source"', "source phase report")
    native = must_pass(gate(root, board), "native admission")
    contains(native.out, '"status": "PASS"', "native report")
    contains(native.out, '"pin_map_exit": 0', "native pin mapping ran")


@test("admission output binds stable exact source and native identities")
def t_input_identity_census():
    root, board = fixture()
    first = json.loads(must_pass(gate(root, board), "first identity census").out)
    second = json.loads(must_pass(gate(root, board), "stable identity census").out)
    assert first["inputs"] == second["inputs"]
    for required in ("route", "locked_route", "nets", "locked_nets",
                     "assembly", "circuit_json", "part:CONN", "part:TERM",
                     "board", "floorplan"):
        assert len(first["inputs"][required]["sha256"]) == 64
    part = root / "02_parts/CONN/part.yaml"
    part.write_text(part.read_text() + "description: identity mutation\n")
    nets_path = root / "03_src/rules/nets.yaml"
    nets = yaml.safe_load(nets_path.read_text())
    nets["length_match"]["MCH_INPUT_SECTIONS"]["intent"] += " changed"
    nets_path.write_text(yaml.safe_dump(nets, sort_keys=False))
    changed = json.loads(must_pass(gate(root, board), "changed identity census").out)
    assert changed["inputs"]["part:CONN"]["sha256"] != first["inputs"]["part:CONN"]["sha256"]
    assert changed["inputs"]["nets"]["sha256"] != first["inputs"]["nets"]["sha256"]
    assert changed["inputs"]["locked_nets"] == first["inputs"]["locked_nets"]


@test("admission rejects a bound input replaced during grading", kind="known_bad")
def t_input_changed_during_gate():
    root, _board = fixture()
    module = _load_gate_module()
    original = module._grade_nets_lock

    def changing(result, nets_path, locked_nets_path, **kwargs):
        original(result, nets_path, locked_nets_path, **kwargs)
        assembly = root / "03_src/rules/assembly.yaml"
        assembly.write_text(assembly.read_text() + "# changed during gate\n")

    module._grade_nets_lock = changing
    try:
        result, _owners, _assembly = module.grade_source(
            root, route_path=root / "03_src/route.yaml",
            locked_route_path=root / "03_src/reviews/accepted-route.yaml",
            nets_path=root / "03_src/rules/nets.yaml",
            locked_nets_path=root / "03_src/reviews/accepted-nets.yaml",
            assembly_path=root / "03_src/rules/assembly.yaml",
            circuit_path=root / "03_tscircuit/build/circuit.json",
            require_locked_route=True, require_locked_nets=True)
    finally:
        module._grade_nets_lock = original
    codes = {row["code"] for row in result.findings}
    assert "DDA-INPUT-CHANGED" in codes


@test("source admission blocks an adopted no-via contract without an independent lock",
      kind="known_bad")
def t_lock_required():
    root, _board = fixture()
    must_fail(gate(root, phase="source", lock=False), "missing reviewed lock",
              "DDA-ROUTE-LOCK-MISSING")


@test("enforced admission cannot bypass a lock by deleting every current pair",
      kind="known_bad")
def t_enforced_lock_survives_empty_current_contract():
    root, _board = fixture()
    path = root / "03_src/route.yaml"
    route = yaml.safe_load(path.read_text())
    route["route"]["preflight_critical_pairs"] = []
    route["route"]["no_critical_routes"] = "forged empty current contract"
    path.write_text(yaml.safe_dump(route, sort_keys=False))
    must_fail(gate(root, phase="source", lock=False), "deleted lock and pairs",
              "DDA-ROUTE-LOCK-MISSING")


@test("Crow-named no_vias length group cannot be relaxed", kind="known_bad")
def t_crow_length_group_no_vias_relaxation():
    root, _board = fixture()
    path = root / "03_src/rules/nets.yaml"
    nets = yaml.safe_load(path.read_text())
    nets["length_match"]["MCH_INPUT_SECTIONS"]["no_vias"] = False
    path.write_text(yaml.safe_dump(nets, sort_keys=False))
    must_fail(gate(root, phase="source"), "Crow R11 length group relaxation",
              "DDA-PROTECTED-NETS-DRIFT")


@test("protected no_vias drift is rejected before routing", kind="known_bad")
def t_no_vias_relaxation():
    """RED evidence: the preexisting R-PAIRMAP source predicate accepts the
    otherwise-valid `no_vias: false` candidate; the reviewed-lock compositor
    is the added boundary that must reject it before route execution."""
    root, board = fixture()
    route_path = root / "03_src/route.yaml"
    route = yaml.safe_load(route_path.read_text())
    route["route"]["preflight_critical_pairs"][0]["no_vias"] = False
    route_path.write_text(yaml.safe_dump(route, sort_keys=False))
    must_pass(run([KPY, CRITICAL, root, "--board", board]),
              "pre-fix owning route contract admits deliberate relaxation")
    must_fail(gate(root, phase="source"), "locked zero-via relaxation",
              "DDA-PROTECTED-ROUTE-DRIFT")


@test("native admission rejects a retired connector pad anchor", kind="known_bad")
def t_retired_pad_anchor():
    root, board = fixture()
    floorplan = root / "03_src/floorplan.yaml"
    floorplan.write_text(floorplan.read_text().replace("pad: '1'", "pad: '9'", 1))
    must_fail(gate(root, board), "stale migration anchor",
              "DDA-RETIRED-PAD-ANCHOR")


@test("native admission rejects an existing pad anchored to an obsolete net",
      kind="known_bad")
def t_wrong_net_anchor():
    root, board = fixture()
    floorplan = root / "03_src/floorplan.yaml"
    floorplan.write_text(floorplan.read_text().replace("net: CLK_P", "net: RETIRED_CLK", 1))
    must_fail(gate(root, board), "stale migration net anchor",
              "DDA-STALE-NET-ANCHOR")


@test("route seed-stub pin anchors are checked against native pad nets",
      kind="known_bad")
def t_route_pin_anchor_wrong_net():
    root, board = fixture()
    route_path = root / "03_src/route.yaml"
    route = yaml.safe_load(route_path.read_text())
    route.setdefault("prep", {}).setdefault("seed_stubs", {})["stubs"] = [
        {"net": "RETIRED_CLK", "pin": "J1.1", "segments": []}]
    route_path.write_text(yaml.safe_dump(route, sort_keys=False))
    must_fail(gate(root, board), "stale route pin anchor",
              "DDA-STALE-NET-ANCHOR")


@test("native admission requires real pin-map agreement", kind="known_bad")
def t_native_pin_map():
    root, board = fixture()
    code = r'''
import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]); f=b.FindFootprintByReference('J1')
for p in list(f.Pads()):
 if p.GetNumber()=='4': f.Remove(p)
pcbnew.SaveBoard(sys.argv[1],b)
'''
    must_pass(run([KPY, "-c", code, board]), "remove native connector land")
    must_fail(gate(root, board), "native pin-map mismatch", "DDA-PINMAP-NATIVE")


@test("source admission rejects an unresolved assembly owner", kind="known_bad")
def t_owner_missing():
    root, _board = fixture()
    path = root / "03_tscircuit/build/circuit.json"
    circuit = json.loads(path.read_text())
    next(row for row in circuit if row.get("name") == "U1")[
        "supplier_part_numbers"] = {"jlcpcb": []}
    path.write_text(json.dumps(circuit))
    must_fail(gate(root, phase="source"), "unowned SMD source reference",
              "DDA-ASSEMBLY-OWNER")


@test("source admission rejects an empty source population", kind="known_bad")
def t_empty_source_population():
    root, _board = fixture()
    (root / "03_tscircuit/build/circuit.json").write_text("[]\n")
    must_fail(gate(root, phase="source"), "zero component design",
              "DDA-SOURCE-POPULATION-EMPTY")


@test("source admission rejects an invalid manual disposition", kind="known_bad")
def t_invalid_manual_disposition():
    root, _board = fixture()
    circuit_path = root / "03_tscircuit/build/circuit.json"
    circuit = json.loads(circuit_path.read_text())
    next(row for row in circuit if row.get("name") == "U1")[
        "supplier_part_numbers"] = {"jlcpcb": []}
    circuit_path.write_text(json.dumps(circuit))
    (root / "03_src/rules/assembly.yaml").write_text(
        "schema: 1\nservice: JLCPCB_PCBA\nsides: [top]\n"
        "not_assembled:\n  - {refs: [U1], reason: made_up}\nconsigned: []\n")
    must_fail(gate(root, phase="source"), "invented manual disposition",
              "DDA-ASSEMBLY-DISPOSITION")


@test("source admission rejects absent assembly side coverage", kind="known_bad")
def t_missing_assembly_sides():
    root, _board = fixture()
    (root / "03_src/rules/assembly.yaml").write_text(
        "schema: 1\nservice: JLCPCB_PCBA\nnot_assembled: []\nconsigned: []\n")
    must_fail(gate(root, phase="source"), "ungraded assembly sides",
              "DDA-ASSEMBLY-SIDES")


@test("valid exact consignment owns a fitted SMD without a circuit JLC code")
def t_valid_consigned_owner():
    root, board = fixture()
    circuit_path = root / "03_tscircuit/build/circuit.json"
    circuit = json.loads(circuit_path.read_text())
    next(row for row in circuit if row.get("name") == "U1")[
        "supplier_part_numbers"] = {"jlcpcb": []}
    circuit_path.write_text(json.dumps(circuit))
    (root / "03_src/rules/assembly.yaml").write_text(
        "schema: 1\nservice: JLCPCB_PCBA\nsides: [top]\nnot_assembled: []\n"
        "consigned:\n"
        "  - refs: [U1]\n"
        "    lcsc: C200\n"
        "    msl: MSL3\n"
        "    evidence: '2026-09-20 exact TERM reels held for consignment'\n"
        "    disposition: 'Supply exact TERM reels to JLC for machine placement'\n")
    must_pass(gate(root, board), "exact consigned machine owner")


@test("consignment code must match the canonical ref dossier identity",
      kind="known_bad")
def t_wrong_consigned_code():
    root, _board = fixture()
    circuit_path = root / "03_tscircuit/build/circuit.json"
    circuit = json.loads(circuit_path.read_text())
    next(row for row in circuit if row.get("name") == "U1")[
        "supplier_part_numbers"] = {"jlcpcb": []}
    circuit_path.write_text(json.dumps(circuit))
    (root / "03_src/rules/assembly.yaml").write_text(
        "schema: 1\nservice: JLCPCB_PCBA\nsides: [top]\nnot_assembled: []\n"
        "consigned:\n"
        "  - refs: [U1]\n"
        "    lcsc: C999\n"
        "    msl: MSL3\n"
        "    evidence: '2026-09-20 exact TERM reels held for consignment'\n"
        "    disposition: 'Supply exact TERM reels to JLC for machine placement'\n")
    result = must_fail(gate(root, phase="source"), "wrong consigned identity",
                       "DDA-ASSEMBLY-DISPOSITION")
    contains(result.out, "C999", "wrong consigned code")
    contains(result.out, "C200", "canonical dossier code")
    contains(result.out, "no JLC code", "missing source code remains unsuppressed")


@test("malformed consignment cannot suppress a missing source code",
      kind="known_bad")
def t_malformed_consigned_owner():
    root, _board = fixture()
    circuit_path = root / "03_tscircuit/build/circuit.json"
    circuit = json.loads(circuit_path.read_text())
    next(row for row in circuit if row.get("name") == "U1")[
        "supplier_part_numbers"] = {"jlcpcb": []}
    circuit_path.write_text(json.dumps(circuit))
    (root / "03_src/rules/assembly.yaml").write_text(
        "schema: 1\nservice: JLCPCB_PCBA\nsides: [top]\nnot_assembled: []\n"
        "consigned:\n"
        "  - refs: [U1]\n"
        "    lcsc: not-an-exact-code\n"
        "    msl: ''\n"
        "    evidence: '2026-09-20 exact TERM reels held for consignment'\n"
        "    disposition: 'Supply exact TERM reels to JLC for machine placement'\n")
    result = must_fail(gate(root, phase="source"), "malformed consignment",
                       "DDA-ASSEMBLY-DISPOSITION")
    contains(result.out, "requires exact lcsc", "consignment exact identity")
    contains(result.out, "requires an MSL declaration", "consignment handling")


@test("native admission accepts an explicit manual SMD owner when policy chooses it")
def t_manual_smd_owner_is_deliberate_policy():
    root, board = fixture()
    circuit_path = root / "03_tscircuit/build/circuit.json"
    circuit = json.loads(circuit_path.read_text())
    next(row for row in circuit if row.get("name") == "U1")[
        "supplier_part_numbers"] = {"jlcpcb": []}
    circuit_path.write_text(json.dumps(circuit))
    (root / "03_src/rules/assembly.yaml").write_text(
        "schema: 1\nservice: JLCPCB_PCBA\nsides: [top]\n"
        "not_assembled:\n"
        "  - refs: [U1]\n"
        "    reason: user_supplied\n"
        "    evidence: '2026-09-20 fixture manual SMD assignment'\n"
        "    disposition: 'Hand fit after automated assembly'\n"
        "consigned: []\n")
    must_pass(gate(root, board), "explicit manual SMD assembly policy")


@test("native admission accepts explicit manual through-hole assembly")
def t_manual_tht_owner_is_valid():
    root, board = fixture()
    circuit_path = root / "03_tscircuit/build/circuit.json"
    circuit = json.loads(circuit_path.read_text())
    next(row for row in circuit if row.get("name") == "U1")[
        "supplier_part_numbers"] = {"jlcpcb": []}
    circuit_path.write_text(json.dumps(circuit))
    (root / "03_src/rules/assembly.yaml").write_text(
        "schema: 1\nservice: JLCPCB_PCBA\nsides: [top]\n"
        "not_assembled:\n"
        "  - refs: [U1]\n"
        "    reason: process_incompatible\n"
        "    evidence: '2026-09-20 fixture manual THT assignment'\n"
        "    disposition: 'Hand solder after automated SMD assembly'\n"
        "consigned: []\n")
    code = r'''
import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]); f=b.FindFootprintByReference('U1')
for p in f.Pads():
 p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
 p.SetDrillSize(pcbnew.VECTOR2I_MM(0.5,0.5))
 p.SetLayerSet(pcbnew.PAD.PTHMask())
pcbnew.SaveBoard(sys.argv[1],b)
'''
    must_pass(run([KPY, "-c", code, board]), "make U1 through-hole")
    must_pass(gate(root, board), "explicit manual THT assembly policy")


@test("native admission rejects bottom SMD under a top-only policy",
      kind="known_bad")
def t_native_side():
    root, board = fixture()
    code = r'''
import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]); b.FindFootprintByReference('U1').SetLayer(pcbnew.B_Cu)
pcbnew.SaveBoard(sys.argv[1],b)
'''
    must_pass(run([KPY, "-c", code, board]), "move populated SMD to bottom")
    must_fail(gate(root, board), "top-only side mismatch", "DDA-ASSEMBLY-SIDE")


@test("removing a protected pair cannot bypass the reviewed lock", kind="known_bad")
def t_protected_pair_removal():
    root, _board = fixture()
    path = root / "03_src/route.yaml"
    route = yaml.safe_load(path.read_text())
    route["route"]["preflight_critical_pairs"] = []
    route["route"]["no_critical_routes"] = "fixture claims none"
    path.write_text(yaml.safe_dump(route, sort_keys=False))
    must_fail(gate(root, phase="source"), "deleted protected pair",
              "DDA-PROTECTED-ROUTE-MISSING")


@test("locked route cannot be the current self-approved file", kind="known_bad")
def t_lock_independence():
    root, _board = fixture()
    result = run([KPY, GATE, root, "--phase", "source",
                  "--locked-route", "03_src/route.yaml"])
    must_fail(result, "self-approved lock", "DDA-ROUTE-LOCK-NOT-INDEPENDENT")


@test("malformed route no_vias is an input error, never an unprotected skip",
      kind="known_bad")
def t_malformed_route_no_vias():
    root, _board = fixture()
    path = root / "03_src/route.yaml"
    route = yaml.safe_load(path.read_text())
    route["route"]["preflight_critical_pairs"][0]["no_vias"] = "true"
    path.write_text(yaml.safe_dump(route, sort_keys=False))
    must_fail(gate(root, phase="source"), "string route no_vias",
              "must be boolean true/false")


@test("malformed nets no_vias cannot disappear from the protected denominator",
      kind="known_bad")
def t_malformed_nets_no_vias():
    root, _board = fixture()
    path = root / "03_src/rules/nets.yaml"
    nets = yaml.safe_load(path.read_text())
    nets["length_match"]["MCH_INPUT_SECTIONS"]["no_vias"] = "true"
    path.write_text(yaml.safe_dump(nets, sort_keys=False))
    must_fail(gate(root, phase="source"), "string nets no_vias",
              "must be boolean true/false")


@test("integer no_vias cannot masquerade as boolean in current or reviewed locks",
      kind="known_bad")
def t_integer_no_vias_is_rejected_everywhere():
    mutations = (
        ("03_src/route.yaml", "route"),
        ("03_src/reviews/accepted-route.yaml", "route"),
        ("03_src/rules/nets.yaml", "nets"),
        ("03_src/reviews/accepted-nets.yaml", "nets"),
    )
    for rel, authority in mutations:
        root, _board = fixture()
        path = root / rel
        doc = yaml.safe_load(path.read_text())
        if authority == "route":
            doc["route"]["preflight_critical_pairs"][0]["no_vias"] = 1
        else:
            doc["length_match"]["MCH_INPUT_SECTIONS"]["no_vias"] = 1
        path.write_text(yaml.safe_dump(doc, sort_keys=False))
        must_fail(gate(root, phase="source"), f"integer no_vias in {rel}",
                  "must be boolean true/false")


@test("decision checkpoint reference repair passes through a real command recorder")
def t_checkpoint_reference_control():
    workspace = case_workspace("reference")
    result = must_pass(run([KPY, CASE_DRIVER, "grade", ROOT, workspace]),
                       "checkpoint reference repair")
    report = json.loads(result.out)
    assert report["evidence"]["production_complete"] is False
    marker = json.loads((workspace / "06_build/route-command.json").read_text())
    assert marker["command"] == "disposable-route-recorder"
    assert len(marker["admission_sha256"]) == 64


@test("decision checkpoint rejects protected, generated-only, manual, and side shortcuts",
      kind="known_bad")
def t_checkpoint_bypass_controls():
    expected = {
        "bypass": "DDA-PROTECTED-NETS-MISSING",
        "generated-bypass": "CIRCUIT-NOT-REGENERATED",
        "manual-bypass": "U1-MACHINE-ASSEMBLY-REQUIRED",
        "side-bypass": "CROW-TOP-ONLY-REQUIRED",
    }
    for mode, code in expected.items():
        workspace = case_workspace(mode)
        result = must_fail(run([KPY, CASE_DRIVER, "grade", ROOT, workspace]),
                           f"checkpoint {mode}")
        if result.out:
            contains(result.out, code, f"checkpoint {mode} diagnosis")
        assert not (workspace / "06_build/route-command.json").exists()


@test("checkpoint refuses a nonzero gate even beside stale PASS evidence",
      kind="known_bad")
def t_checkpoint_stale_pass_report():
    workspace = case_workspace("reference")
    must_pass(run([KPY, CASE_DRIVER, "grade", ROOT, workspace]),
              "materialize prior PASS report")
    marker_path = workspace / "06_build/route-command.json"
    prior_marker = marker_path.read_bytes()
    route_path = workspace / "03_src/route.yaml"
    route = yaml.safe_load(route_path.read_text())
    route["route"]["preflight_critical_pairs"] = [{
        "name": "BAD", "p": "CLK_P", "n": "CLK_N",
        "allowed_layers": ["F.Cu"], "no_vias": "true"}]
    route_path.write_text(yaml.safe_dump(route, sort_keys=False))
    result = must_fail(run([KPY, CASE_DRIVER, "grade", ROOT, workspace]),
                       "nonzero gate beside stale report")
    if result.out:
        contains(result.out, "ADMISSION-COMMAND-FAILED", "nonzero gate diagnosis")
        contains(result.out, "ROUTE-RAN-AFTER-REFUSAL", "stale recorder diagnosis")
    assert marker_path.read_bytes() == prior_marker


if __name__ == "__main__":
    sys.exit(main())
