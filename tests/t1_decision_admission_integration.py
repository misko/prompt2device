#!/usr/bin/env python3
"""T1: D-DESIGN-ADMISSION is a real, early production-flow boundary.

RED was reproduced from repository commit e1c8f2bb in an isolated skill tree:
its real ``pcb_flow.py run --stage placement`` launched the recorder once even
after the reviewed no-via policy was relaxed.  The current conductor refuses
the same fixture before launch; restoring the protected policy launches it
exactly once.
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import (KPY, ROOT, SCRIPTS, check, contains, eq, main,  # noqa: E402
                     must_fail, must_pass, run, test, tmpdir)


FLOW = SCRIPTS / "pcb_flow.py"
PRE_FIX_COMMIT = "e1c8f2bb"


def source_fixture():
    root = tmpdir("decision-flow-")
    for rel in ("02_parts/CONN", "03_src/reviews", "03_src/rules",
                "03_tscircuit/build", "04_kicad", "06_build"):
        (root / rel).mkdir(parents=True, exist_ok=True)
    (root / "02_parts/CONN/part.yaml").write_text(
        "mpn: CONN\nfootprint: Fixture:CONN\n"
        "sourcing: {lcsc: C100}\n"
        "pins:\n  1: CLK_P\n  2: CLK_N\n")
    circuit = [
        {"type": "source_component", "source_component_id": "c1",
         "name": "J1", "manufacturer_part_number": "CONN",
         "supplier_part_numbers": {"jlcpcb": ["C100"]}},
        {"type": "source_port", "source_component_id": "c1",
         "source_port_id": "p1", "pin_number": 1, "name": "CLK_P",
         "port_hints": ["pin1", "1"]},
        {"type": "source_port", "source_component_id": "c1",
         "source_port_id": "p2", "pin_number": 2, "name": "CLK_N",
         "port_hints": ["pin2", "2"]},
    ]
    (root / "03_tscircuit/build/circuit.json").write_text(json.dumps(circuit))
    (root / "03_src/rules/assembly.yaml").write_text(
        "schema: 1\nservice: JLCPCB_PCBA\nsides: [top]\n"
        "not_assembled: []\nconsigned: []\n")
    (root / "03_src/floorplan.yaml").write_text(
        "project: {name: demo}\nconstraints: {}\n")
    route = {
        "project": {"name": "demo", "board": "04_kicad/demo.kicad_pcb",
                    "build_dir": "06_build/route"},
        "flow": {"decision_admission": {
            "mode": "enforce",
            "locked_route": "03_src/reviews/accepted-route-contract.yaml",
            "locked_nets": "03_src/reviews/accepted-nets-contract.yaml",
        }},
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
    lock = json.loads(json.dumps(route))
    lock.pop("flow")
    (root / "03_src/route.yaml").write_text(yaml.safe_dump(route, sort_keys=False))
    (root / "03_src/reviews/accepted-route-contract.yaml").write_text(
        yaml.safe_dump(lock, sort_keys=False))
    nets = {
        "length_match": {
            "MCH_INPUT_SECTIONS": {
                "adr": "0010-route-stack-and-current-paths",
                "intent": "Reduced Crow clock-input path protection fixture.",
                "members": {"MCLK": ["CLK_P"], "BCLK": ["CLK_N"]},
                "topology": "tree",
                "congruent_pads": False,
                "no_vias": False,
                "max_spread_mm": "report",
                "router_moves": "any",
            }
        }
    }
    locked_nets = json.loads(json.dumps(nets))
    locked_nets["length_match"]["MCH_INPUT_SECTIONS"]["no_vias"] = True
    (root / "03_src/rules/nets.yaml").write_text(
        yaml.safe_dump(nets, sort_keys=False))
    (root / "03_src/reviews/accepted-nets-contract.yaml").write_text(
        yaml.safe_dump(locked_nets, sort_keys=False))
    (root / "03_src/rebuild_all.sh").write_text("#!/bin/bash\nexit 0\n")
    recorder = root / "recorder.py"
    recorder.write_text(
        "from pathlib import Path\nimport sys\n"
        "p=Path(sys.argv[1]); p.write_text(p.read_text()+'launch\\n' if p.exists() else 'launch\\n')\n")
    return root, recorder, root / "launches.txt"


def launch(flow, root, recorder, log, stage="placement", require=True):
    args = [KPY, flow, "run", root, "--stage", stage]
    if require:
        args.append("--require-decision-admission")
    return run([*args, "--",
                sys.executable, recorder, log])


def line_count(path):
    return len(path.read_text().splitlines()) if path.exists() else 0


def isolated_prefx_flow():
    tree = tmpdir("decision-prefx-")
    scripts = tree / "skills/kicad-pcb/scripts"
    scripts.mkdir(parents=True)
    def frozen(rel):
        return subprocess.run(
            ["git", "show", f"{PRE_FIX_COMMIT}:{rel}"], cwd=ROOT,
            check=True, capture_output=True).stdout

    (scripts / "pcb_flow.py").write_bytes(
        frozen("skills/kicad-pcb/scripts/pcb_flow.py"))
    (scripts / "process_runner.py").write_bytes(
        frozen("skills/kicad-pcb/scripts/process_runner.py"))
    design_scripts = tree / "skills/pcb-design/scripts"
    design_scripts.mkdir(parents=True)
    (design_scripts / "pipeline_runtime.py").write_bytes(
        frozen("skills/pcb-design/scripts/pipeline_runtime.py"))
    return scripts / "pcb_flow.py"


@test("true pre-fix pcb_flow launches placement despite Crow-style no-via drift",
      kind="known_bad")
def t_prefx_red_real_cli():
    root, recorder, log = source_fixture()
    result = must_pass(launch(isolated_prefx_flow(), root, recorder, log,
                              require=False),
                       "isolated pre-fix production placement path")
    eq(line_count(log), 1, "pre-fix downstream launches")
    check("decision_admission" not in result.out,
          "pre-fix conductor unexpectedly ran the new boundary")


@test("production placement blocks relaxed Crow-style group and launches correction once",
      kind="known_bad")
def t_source_admission_orders_real_cli():
    root, recorder, log = source_fixture()
    bad = must_fail(launch(FLOW, root, recorder, log),
                    "protected nets relaxation", "DDA-PROTECTED-NETS-DRIFT")
    eq(line_count(log), 0, "downstream launches after refusal")
    contains(bad.out, "decision_admission_source", "production source stage")

    nets_path = root / "03_src/rules/nets.yaml"
    nets = yaml.safe_load(nets_path.read_text())
    del nets["length_match"]["MCH_INPUT_SECTIONS"]
    nets_path.write_text(yaml.safe_dump(nets, sort_keys=False))
    must_fail(launch(FLOW, root, recorder, log), "deleted protected nets group",
              "DDA-PROTECTED-NETS-MISSING")
    eq(line_count(log), 0, "downstream launches after protected-group deletion")

    nets = yaml.safe_load(
        (root / "03_src/reviews/accepted-nets-contract.yaml").read_text())
    nets_path.write_text(yaml.safe_dump(nets, sort_keys=False))
    must_pass(launch(FLOW, root, recorder, log), "corrected admitted placement")
    eq(line_count(log), 1, "corrected downstream launches")


@test("adopted config cannot lose its lock and fall through to placement",
      kind="known_bad")
def t_adopted_missing_lock_is_configuration_error():
    root, recorder, log = source_fixture()
    path = root / "03_src/route.yaml"
    route = yaml.safe_load(path.read_text())
    del route["flow"]["decision_admission"]["locked_route"]
    path.write_text(yaml.safe_dump(route, sort_keys=False))
    must_fail(launch(FLOW, root, recorder, log), "adopted config without lock",
              "locked_route is required")
    eq(line_count(log), 0, "downstream launches without adopted lock")


@test("unadopted projects remain visibly legacy and receive no admission credit")
def t_legacy_is_explicit():
    root, recorder, log = source_fixture()
    path = root / "03_src/route.yaml"
    route = yaml.safe_load(path.read_text())
    route["flow"]["decision_admission"] = {"mode": "legacy_unmigrated"}
    path.write_text(yaml.safe_dump(route, sort_keys=False))
    result = must_pass(launch(FLOW, root, recorder, log, require=False),
                       "legacy placement")
    contains(result.out, "LEGACY_UNMIGRATED", "explicit legacy status")
    contains(result.out, "no D-DESIGN-ADMISSION credit", "legacy non-credit")
    eq(line_count(log), 1, "legacy downstream launches")


@test("new-template adoption cannot be deleted into the legacy path",
      kind="known_bad")
def t_required_adoption_cannot_downgrade():
    root, recorder, log = source_fixture()
    path = root / "03_src/route.yaml"
    route = yaml.safe_load(path.read_text())
    del route["flow"]["decision_admission"]
    path.write_text(yaml.safe_dump(route, sort_keys=False))
    must_fail(launch(FLOW, root, recorder, log), "deleted template adoption",
              "--require-decision-admission needs")
    eq(line_count(log), 0, "new-template launch after adoption deletion")
    route["flow"]["decision_admission"] = {"mode": "legacy_unmigrated"}
    path.write_text(yaml.safe_dump(route, sort_keys=False))
    must_fail(launch(FLOW, root, recorder, log), "template changed to legacy",
              "--require-decision-admission needs")
    eq(line_count(log), 0, "new-template launch after legacy downgrade")


@test("new templates enforce admission before placement and route preparation")
def t_template_invocation_boundaries():
    template = yaml.safe_load(
        (ROOT / "skills/pcb-design/templates/03_src/route.yaml").read_text())
    decision = template["flow"]["decision_admission"]
    eq(decision["mode"], "enforce", "new-project admission mode")
    check(bool(decision.get("locked_route")), "new-project lock path is absent")
    check(bool(decision.get("locked_nets")), "new-project nets lock path is absent")

    for name in ("rebuild_all.sh", "rebuild_reuse.sh"):
        text = (ROOT / "skills/pcb-design/templates/03_src" / name).read_text()
        contains(text, "--require-decision-admission",
                 f"{name} adoption ratchet")
        placement = text.index("run_stage placement")
        generate = text.index('"$S/generate_board_generic.py"', placement)
        route_prep = text.index("run_stage route_prep")
        route_tool = text.index('"$S/route_and_stitch_generic.py" prep', route_prep)
        check(placement < generate < route_prep < route_tool,
              f"{name} admission boundary order regressed")


@test("routing launch invokes native admission before its command",
      kind="known_bad")
def t_native_admission_blocks_downstream():
    root, recorder, log = source_fixture()
    result = must_fail(launch(FLOW, root, recorder, log, stage="routing"),
                       "native admission without board")
    contains(result.out, "decision_admission_native", "production native stage")
    eq(line_count(log), 0, "routing launches before native admission")


if __name__ == "__main__":
    sys.exit(main())
