#!/usr/bin/env python3
"""Native and historical checkpoint controls; never invokes a model."""
import json
import shutil
import sys

from harness import ROOT, KPY, check, eq, main, must_pass, run, test, tmpdir

sys.path.insert(0, str(ROOT / "tests/checkpoints"))
import runner

CASES = ROOT / "tests/checkpoints/cases"


def restored(name):
    case = CASES / name
    target = tmpdir("checkpoint-control-") / "run"
    state = runner.prepare(case, target)
    eq(state["initial_grader"]["outcome"], "FAIL", "initial calibration")
    return case, target, target / "workspace"


def handoff(workspace, text="Control repair applied; independent grader must evaluate final artifacts."):
    (workspace / "HANDOFF.md").write_text(text + "\n")


def reference(case, target, workspace):
    if case.name == "crow_routing_geometry":
        shutil.copy2(case / "reference/geometry.json", workspace / "geometry.json")
    else:
        must_pass(run([KPY, case / "driver.py", "reference", ROOT, workspace]), "reference repair")
    handoff(workspace)
    result = runner.grade(target)
    eq(result["outcome"], "PASS", f"reference {case.name}: {result.get('findings')}")


@test("checkpoint real case baselines fail and reference repairs pass")
def t_case_references():
    for name in ("crow_routing_geometry", "crow_assembly_population", "crow_release_evidence"):
        reference(*restored(name))


@test("checkpoint native routing accepts an alternate legal corridor")
def t_alternate_route():
    case, target, workspace = restored("crow_routing_geometry")
    geometry = json.loads((case / "reference/geometry.json").read_text())
    geometry["route"]["points_mm"] = [[20, 20], [30, 26], [50, 26], [60, 20]]
    (workspace / "geometry.json").write_text(json.dumps(geometry))
    handoff(workspace, "Alternative lower corridor; native DRC and connectivity are required.")
    result = runner.grade(target)
    eq(result["outcome"], "PASS", str(result.get("findings")))


@test("checkpoint native routing rejects a connected via shortcut", kind="known_bad")
def t_via_shortcut():
    case, target, workspace = restored("crow_routing_geometry")
    shutil.copy2(case / "bypass/geometry.json", workspace / "geometry.json")
    handoff(workspace, "Deliberately invalid via shortcut; it must be rejected.")
    result = runner.grade(target)
    eq(result["outcome"], "FAIL", str(result.get("findings")))
    check("ZERO_VIA_CONTRACT" in {row["code"] for row in result["findings"]}, "missing zero-via finding")


@test("checkpoint assembly rejects deleting the required sourcing declaration", kind="known_bad")
def t_population_shortcut():
    case, target, workspace = restored("crow_assembly_population")
    reference(case, target, workspace)
    (workspace / "03_src/rules/assembly.yaml").write_text("service: standard\nsides: [top]\nfiducials: none\n")
    handoff(workspace, "Attempted removal of required population sourcing; must fail.")
    result = runner.grade(target)
    eq(result["outcome"], "FAIL", str(result.get("findings")))
    check("U1-POPULATION-SOURCE" in {row["code"] for row in result["findings"]}, "missing required-population finding")


@test("checkpoint release rejects apparent agreement achieved by changing measurements", kind="known_bad")
def t_evidence_shortcut():
    case, target, workspace = restored("crow_release_evidence")
    reference(case, target, workspace)
    measured = workspace / "06_build/candidates/crow-recorder-v1.0/verification/erc.json"
    measured.write_text('{"sheets": []}\n')
    handoff(workspace, "Attempted evidence deletion; protected measurement must reject this.")
    result = runner.grade(target)
    eq(result["outcome"], "ERROR", str(result.get("findings")))
    check("WORKSPACE_SCOPE" in {row["code"] for row in result["findings"]}, "measurement was not protected")


if __name__ == "__main__":
    sys.exit(main())
