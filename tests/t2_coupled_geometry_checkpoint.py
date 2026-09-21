#!/usr/bin/env python3
"""Deterministic native controls for the Crow coupled-geometry checkpoint.

The fixture is a synthetic R09-R12 reduction.  It checks a concrete combined
witness; it does not claim route-search completeness, global routability, a
finished routing stage, or a production Crow-board result.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pcbnew
import yaml

from harness import ROOT, KPY, check, eq, main, must_fail, run, test, tmpdir


CASE = ROOT / "tests/checkpoints/cases/crow_coupled_geometry"
sys.dont_write_bytecode = True
sys.path.insert(0, str(CASE))
import driver  # noqa: E402
from native_fixture import NETS, build_from_source  # noqa: E402
sys.path.insert(0, str(ROOT / "tests/checkpoints"))
import runner as checkpoint_runner  # noqa: E402


def fresh():
    workspace = tmpdir("crow_coupled_checkpoint_") / "workspace"
    with contextlib.redirect_stdout(io.StringIO()):
        rc = driver.prepare(ROOT, workspace)
    eq(rc, 0, "trusted prepare")
    return workspace


def grade(workspace):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        rc = driver.grade(ROOT, workspace)
    payload = json.loads(output.getvalue().splitlines()[-1])
    return rc, payload


def install_control(workspace, name):
    driver.apply_control(workspace, name)
    (workspace / "HANDOFF.md").write_text(
        f"Applied {name}; production coupled preflight is the bounded result.\n")


def source_doc(workspace):
    return yaml.safe_load((workspace / "03_src/route_geometry.yaml").read_text())


def write_source(workspace, doc):
    (workspace / "03_src/route_geometry.yaml").write_text(
        yaml.safe_dump(doc, sort_keys=False))


def native_drc(board_path, report_path):
    completed = run(["kicad-cli", "pcb", "drc", "--severity-all", "--format",
                     "json", "-o", report_path, board_path])
    eq(completed.rc, 0, f"native diagnostic invocation: {completed.out}")
    return json.loads(report_path.read_text())


def evidence_manifest(workspace):
    root = workspace / "06_build/coupled"
    paths = list((root / "gate").rglob("*"))
    canonical = root / "coupled-receipt.json"
    if canonical.is_file():
        paths.append(canonical)
    return {
        path.relative_to(workspace).as_posix():
            hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths if path.is_file()
    }


@test("coupled checkpoint reproduces isolated legality and a combined collision",
      kind="known_bad")
def t_initial_combined_collision():
    workspace = fresh()
    prepared = workspace / "06_build/coupled/prepared.kicad_pcb"
    witness = workspace / "06_build/coupled/witness.kicad_pcb"
    combined = native_drc(witness, workspace / "combined.json")
    eq([row["type"] for row in combined["violations"]], ["tracks_crossing"],
       "exact combined native defect")
    eq(combined["unconnected_items"], [], "all six terminals remain connected")

    seed_uuids = {item.m_Uuid.AsString() for item in
                  pcbnew.LoadBoard(str(prepared)).GetTracks()
                  if str(item.GetNetname()) == "ADC_TDM"}
    crossing_uuids = {item["uuid"] for row in combined["violations"]
                      for item in row.get("items", [])}
    check(seed_uuids & crossing_uuids,
          "early MCH branch did not block an inherited later ADC launch")

    for keep in NETS:
        board = pcbnew.LoadBoard(str(witness))
        for item in list(board.GetTracks()):
            if str(item.GetNetname()) != keep:
                board.Remove(item)
        isolated = workspace / f"isolated-{keep}.kicad_pcb"
        pcbnew.SaveBoard(str(isolated), board)
        report = native_drc(isolated, workspace / f"isolated-{keep}.json")
        eq(report["violations"], [], f"{keep} isolated copper is legal")

    rc, result = grade(workspace)
    eq(rc, 1, "blocked baseline")
    eq([row["code"] for row in result["findings"]],
       ["COMBINED-NATIVE-COLLISION", "COUPLED-PREFLIGHT-FAIL"],
       "exact ordered initial findings")


@test("coupled checkpoint accepts two alternate complete combined witnesses")
def t_alternate_combined_witnesses():
    route_hashes = set()
    for name in ("reference_above", "reference_below"):
        workspace = fresh()
        install_control(workspace, name)
        route_hashes.add(driver.sha(workspace / "03_src/route_geometry.yaml"))
        rc, result = grade(workspace)
        eq(rc, 0, f"{name}: {result['findings']}")
        eq(result["outcome"], "PASS", name)
        eq(result["evidence"]["native_violation_types"], [], name)
        eq(result["evidence"]["native_unconnected"], 0, name)
        eq(result["evidence"]["production_gate_status"], "PASS", name)
        eq(result["evidence"]["production_complete"], False,
           "local witness cannot complete the routing stage")
    eq(len(route_hashes), 2, "controls are genuinely alternate source geometries")


@test("coupled checkpoint rejects layer via width and terminal shortcuts",
      kind="known_bad")
def t_source_shortcuts():
    mutations = {
        "wrong_layer": (lambda doc: doc["routes"]["MCH_CLK"].update(layer="B.Cu"),
                        "FROZEN-LAYER-CONSTRAINT"),
        "via": (lambda doc: doc["routes"]["MCH_CLK"]["vias_mm"].append([10.0, 13.0]),
                "ZERO-VIA-CONSTRAINT"),
        "thin": (lambda doc: doc["routes"]["MCH_CLK"].update(width_mm=0.10),
                 "FROZEN-WIDTH-CONSTRAINT"),
        "missing_terminal":
            (lambda doc: doc["routes"]["MCH_CLK"]["trunks"].pop(),
             "REQUIRED-TERMINAL-UNCONNECTED"),
    }
    for name, (mutate, required) in mutations.items():
        workspace = fresh()
        install_control(workspace, "reference_above")
        doc = source_doc(workspace)
        mutate(doc)
        write_source(workspace, doc)
        rc, result = grade(workspace)
        codes = {row["code"] for row in result["findings"]}
        eq(rc, 1, f"{name} must fail: {result}")
        check(required in codes, f"{name} missing {required}: {codes}")
        check("COUPLED-PREFLIGHT-FAIL" in codes,
              f"{name} bypassed production gate: {codes}")


def mutate_witness(workspace, mutation):
    install_control(workspace, "reference_above")
    output = workspace / "06_build/coupled"
    prepared, witness = build_from_source(workspace, output)
    board = pcbnew.LoadBoard(str(witness))
    fp = next(fp for fp in board.GetFootprints() if fp.GetReference() == "U_ADC")
    pad = next(iter(fp.Pads()))
    if mutation == "move":
        at = pad.GetPosition()
        pad.SetPosition(pcbnew.VECTOR2I(at.x + pcbnew.FromMM(1.0), at.y))
    else:
        fp.Remove(pad)
    pcbnew.SaveBoard(str(witness), board)
    return prepared, witness


@test("production coupled gate rejects moved and missing pad witnesses",
      kind="known_bad")
def t_pad_bypasses():
    gate_script = ROOT / "skills/kicad-pcb/scripts/coupled_geometry_preflight.py"
    for mutation in ("move", "delete"):
        workspace = fresh()
        prepared, witness = mutate_witness(workspace, mutation)
        gate_workspace = workspace / f"direct-{mutation}-gate"
        receipt = workspace / f"direct-{mutation}.json"
        result = must_fail(run([
            KPY, gate_script, "grade", workspace,
            "--prepared", prepared, "--witness", witness,
            "--workspace", gate_workspace, "--json", receipt,
        ]), f"{mutation} pad bypass")
        eq(result.rc, 1, f"{mutation} is an engineering failure")
        payload = json.loads(receipt.read_text())
        eq(payload["checks"]["route_base"]["status"], "FAIL",
           f"{mutation} must fail prepared geometry identity")


@test("checkpoint grader regenerates current source instead of trusting local boards")
def t_source_regeneration():
    workspace = fresh()
    _prepared, stale_witness = mutate_witness(workspace, "move")
    stale_hash = driver.sha(stale_witness)
    rc, result = grade(workspace)
    eq(rc, 0, str(result["findings"]))
    eq(driver.sha(stale_witness), stale_hash,
       "grader rewrote the solver's retained moved-pad artifact")
    check(result["evidence"]["regenerated_witness"] !=
          "06_build/coupled/witness.kicad_pcb",
          "grader trusted the solver-local witness instead of regenerating")
    eq(result["evidence"]["source_regenerated"], True,
       "fresh trusted-producer evidence")


@test("runner solver command and repeated grades preserve immutable attempts")
def t_runner_replay_and_regrade():
    run_dir = tmpdir("crow_coupled_runner_replay_") / "run"
    command = [
        KPY, str(CASE / "controls/replay_observed_solver.py"),
        "{repo}", "{workspace}",
    ]
    result = checkpoint_runner.run_case(CASE, run_dir, command, repo=ROOT)
    eq(result["outcome"], "PASS", str(result.get("findings")))
    eq(result["agent_execution"]["returncode"], 0,
       "documented solver build-and-gate command")
    workspace = run_dir / "workspace"
    eq(driver.sha(workspace / "03_src/route_geometry.yaml"),
       "8fc61169c623af04b3bd2db3fdc820b6f0667c1385f958c0b525cfdf1b0e906f",
       "exact preserved Sol source repair")
    eq(driver.sha(workspace / "HANDOFF.md"),
       "f2c2b3276319d27b20056cbcf131bdca614117cc2a7315176612679b4154535f",
       "exact preserved Sol handoff")
    check((workspace / "06_build/coupled/coupled-receipt.json").is_file(),
          "documented solver receipt was not retained")
    check((workspace / "06_build/coupled/gate/repair-1/receipt.json").is_file(),
          "documented solver child receipt was not retained")
    check((workspace / "06_build/coupled/gate/repair-1-current-rules").is_dir(),
          "documented solver current-rule witness was not retained")

    prior = evidence_manifest(workspace)
    receipts = [result["evidence"]["production_receipt"]]
    for index in range(2):
        repeated = checkpoint_runner.grade(run_dir)
        eq(repeated["outcome"], "PASS",
           f"repeat grade {index + 1}: {repeated.get('findings')}")
        receipts.append(repeated["evidence"]["production_receipt"])
        after = evidence_manifest(workspace)
        eq({path: after.get(path) for path in prior}, prior,
           f"repeat grade {index + 1} changed earlier evidence")
        check(len(after) > len(prior),
              f"repeat grade {index + 1} wrote no new immutable attempt")
        prior = after
    eq(len(set(receipts)), 3,
       "each grader invocation needs a distinct UUID receipt")


@test("checkpoint classifies an incomplete production gate as grader error",
      kind="known_bad")
def t_gate_incomplete_classification():
    workspace = fresh()
    install_control(workspace, "reference_above")
    incomplete = subprocess.CompletedProcess(
        ["coupled_geometry_preflight.py"], 2,
        stdout="COUPLED-GEOMETRY INCOMPLETE: missing kicad-cli\n", stderr="")
    missing = workspace / "06_build/coupled/gate/missing-receipt.json"
    with patch.object(driver, "_production_gate",
                      return_value=(incomplete, missing, None)):
        rc, result = grade(workspace)
    eq(rc, 2, str(result))
    eq(result["outcome"], "ERROR", "infrastructure/tool incompleteness")
    eq([row["code"] for row in result["findings"]],
       ["COUPLED-PREFLIGHT-INCOMPLETE"], "exact incomplete classification")
    check("missing kicad-cli" in
          result["evidence"]["production_gate_output_tail"],
          "bounded production failure reason was omitted")

    prepared = workspace / "06_build/coupled/prepared.kicad_pcb"
    witness = workspace / "06_build/coupled/witness.kicad_pcb"

    def write_malformed_receipt(command, **_kwargs):
        receipt = Path(command[command.index("--json") + 1])
        receipt.write_text("{malformed")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    with patch.object(driver.subprocess, "run",
                      side_effect=write_malformed_receipt):
        malformed, receipt, payload = driver._production_gate(
            ROOT, workspace, prepared, witness, "malformed-receipt")
    eq(payload, None, "malformed receipt must not escape the grader")
    check(receipt.is_file(), "malformed receipt control was not written")
    check("invalid production receipt JSON" in malformed.stderr,
          "malformed receipt diagnostic was omitted")
    with patch.object(driver, "_production_gate",
                      return_value=(malformed, receipt, payload)):
        rc, result = grade(workspace)
    eq(rc, 2, str(result))
    eq(result["outcome"], "ERROR", "malformed receipt is infrastructure error")
    eq([row["code"] for row in result["findings"]],
       ["COUPLED-PREFLIGHT-INCOMPLETE"], "malformed receipt classification")
    check("invalid production receipt JSON" in
          result["evidence"]["production_gate_output_tail"],
          "bounded malformed receipt reason was omitted")


@test("coupled witness cannot be reported as a completed routing stage",
      kind="known_bad")
def t_scope_overclaim():
    workspace = fresh()
    install_control(workspace, "reference_below")
    (workspace / "HANDOFF.md").write_text(
        "Production gate passed, therefore the routing stage complete.\n")
    rc, result = grade(workspace)
    eq(rc, 1, str(result))
    codes = {row["code"] for row in result["findings"]}
    check("HANDOFF-SCOPE-OVERCLAIM" in codes, str(codes))
    eq(result["evidence"]["production_gate_status"], "PASS",
       "scope refusal is distinct from local engineering feasibility")


if __name__ == "__main__":
    raise SystemExit(main())
