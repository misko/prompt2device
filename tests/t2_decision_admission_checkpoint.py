#!/usr/bin/env python3
"""T2: deterministic runner controls for Crow decision admission."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import ROOT, KPY, check, eq, main, must_pass, run, test, tmpdir  # noqa: E402

sys.path.insert(0, str(ROOT / "tests/checkpoints"))
import runner  # noqa: E402


CASE = ROOT / "tests/checkpoints/cases/crow_decision_admission"
DRIVER = CASE / "driver.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def codes(result):
    return [row["code"] for row in result.get("findings", [])]


def fresh_run(prefix="decision-checkpoint-"):
    run_dir = tmpdir(prefix) / "run"
    state = runner.prepare(CASE, run_dir, repo=ROOT)
    return run_dir, run_dir / "workspace", state


def apply(mode, workspace):
    must_pass(run([KPY, DRIVER, mode, ROOT, workspace]),
              f"decision checkpoint {mode}")


@test("decision checkpoint calibrates exact Crow failures and binds current conductors",
      kind="known_bad")
def t_initial_calibration_and_tool_binding():
    _run_dir, workspace, state = fresh_run()
    expected = json.loads((CASE / "case.json").read_text())["initial_findings"]
    eq(state["initial_grader"]["outcome"], "FAIL", "initial outcome")
    eq(codes(state["initial_grader"]), expected, "exact initial finding order")
    check(not (workspace / "06_build/route-command.json").exists(),
          "initial refusal must precede the disposable route command")

    # Runner receipts bind the current conductor and the helpers it directly or
    # transitively depends on, including the later checkpoint-family additions.
    trusted = state["tool_revision_hashes"]
    helpers = (
        "skills/pcb-design/scripts/design_decision_admission.py",
        "skills/kicad-pcb/scripts/pcb_flow.py",
        "skills/jlcpcb-fab/scripts/assembly_coverage.py",
        "skills/kicad-pcb/scripts/coupled_geometry_preflight.py",
        "skills/pcb-design/scripts/release_review_preflight.py",
        "skills/pcb-design/scripts/publication_transport_gate.py",
        "skills/kicad-pcb/scripts/release_required_check.py",
    )
    for relative in helpers:
        check(relative in trusted, f"runner omitted trusted helper {relative}")
        eq(trusted[relative], sha(ROOT / relative),
           f"runner bound stale helper bytes for {relative}")


@test("decision checkpoint reference repair passes through runner and updates HANDOFF")
def t_reference_repair():
    run_dir, workspace, state = fresh_run("decision-reference-")
    baseline_handoff = state["baseline"]["HANDOFF.md"]
    apply("reference", workspace)
    check(sha(workspace / "HANDOFF.md") != baseline_handoff,
          "reference repair did not update HANDOFF.md")
    result = runner.grade(run_dir)
    eq(result["outcome"], "PASS", str(result.get("findings")))
    eq(result["engineering_outcome"], "PASS", "engineering outcome")
    check(not result["findings"], "passing reference retained findings")
    marker = json.loads(
        (workspace / "06_build/route-command.json").read_text())
    eq(marker["command"], "disposable-route-recorder", "route command evidence")
    check(len(marker["admission_sha256"]) == 64,
          "route recorder did not bind the admission report")


@test("runner rejects editing the independent reviewed lock to bless a relaxation",
      kind="known_bad")
def t_protected_review_edit():
    run_dir, workspace, _state = fresh_run("decision-protected-lock-")
    apply("reference", workspace)
    lock_path = workspace / "03_src/reviews/accepted-nets.yaml"
    lock = yaml.safe_load(lock_path.read_text())
    lock["length_match"]["MCH_INPUT_SECTIONS"]["no_vias"] = False
    lock_path.write_text(yaml.safe_dump(lock, sort_keys=False))
    result = runner.grade(run_dir)
    eq(result["outcome"], "ERROR", "protected lock edit")
    eq(result["execution_status"], "NOT_RUN", "grader must not bless protected edits")
    check("WORKSPACE_SCOPE" in codes(result), "protected edit lacked runner finding")


@test("editable deletion bypass still fails the independent decision grader",
      kind="known_bad")
def t_editable_protected_group_bypass():
    run_dir, workspace, _state = fresh_run("decision-group-bypass-")
    apply("bypass", workspace)
    result = runner.grade(run_dir)
    eq(result["outcome"], "FAIL", "protected group deletion")
    check("DDA-PROTECTED-NETS-MISSING" in codes(result),
          "independent lock did not reject the deleted protected group")
    check("ADMISSION-COMMAND-FAILED" in codes(result),
          "nonzero production admission was not retained")
    check(not (workspace / "06_build/route-command.json").exists(),
          "routing recorder ran after admission refusal")


if __name__ == "__main__":
    sys.exit(main())
