#!/usr/bin/env python3
"""T2: Crow review/publication preflight and real agent-open boundary.

RED is pinned against the immutable 6fdf970a ``pcb_flow.py``: its actual
``agent-open`` path reaches the disposable opener for the matching-three stale
packet because release-review admission did not yet exist. The current path
refuses the same packet before attempt allocation.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import ROOT, check, contains, eq, main, test, tmpdir  # noqa: E402

CASE = ROOT / "tests/checkpoints/cases/crow_publication_preflight"
DRIVER_PATH = CASE / "driver.py"
PRE_FIX_COMMIT = "6fdf970a"

sys.path.insert(0, str(ROOT / "tests/checkpoints"))
import runner  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


driver = load("crow_publication_case_driver", DRIVER_PATH)


def fresh_run(label="publication-checkpoint-"):
    parent = tmpdir(label)
    run_dir = parent / "run"
    state = runner.prepare(CASE, run_dir, repo=ROOT)
    return run_dir, run_dir / "workspace", state


def codes(result):
    return [row["code"] for row in result["findings"]]


@test("Crow publication checkpoint has calibrated fail, valid repair, and shortcut controls",
      kind="known_bad")
def t_checkpoint_controls():
    run_dir, workspace, state = fresh_run()
    eq(codes(state["initial_grader"]), [
        "RP-SUBJECT", "RP-SOURCE", "RP-GIT", "RP-OPERATION",
        "REVIEW-NOT-ALLOCATED",
    ], "calibrated initial defects")
    driver.apply_reference(ROOT, workspace)
    result = runner.grade(run_dir)
    eq(result["outcome"], "PASS", str(result.get("findings")))
    eq(result["evidence"]["opener_calls"], 1, "READY reaches disposable opener once")
    check(not result["evidence"]["host_reviewer_called"],
          "fixture must not claim a host reviewer was launched")
    check(not result["evidence"]["production_complete"],
          "preflight must not claim final completion")

    bypass_run, bypass_workspace, _ = fresh_run("publication-bypass-")
    driver.apply_bypass(ROOT, bypass_workspace)
    rejected = runner.grade(bypass_run)
    eq(rejected["outcome"], "FAIL", "evidence-dropping shortcut")
    check("RP-REQUIRED" in codes(rejected), "required artifact deletion rejected")

    content_run, content_workspace, _ = fresh_run("publication-content-")
    driver.apply_reference(ROOT, content_workspace)
    archive = content_workspace / driver.CANDIDATE / "verification/evidence.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        output.writestr("leaf.txt", b"unrelated replacement evidence\n")
    driver.write_manifest(content_workspace)
    driver.git(content_workspace, "add", str(driver.CANDIDATE))
    driver.git(content_workspace, "commit", "-q", "-m", "invalid evidence substitution")
    driver.write_assertions(ROOT, content_workspace)
    (content_workspace / "HANDOFF.md").write_text(
        "Replaced required evidence with unrelated bytes; must fail.\n")
    content_result = runner.grade(content_run)
    eq(content_result["outcome"], "FAIL", "logical evidence substitution")
    check("EVIDENCE-CONTENT" in codes(content_result),
          "independent logical evidence obligation rejected substitution")


@test("matching stale receipt commission and envelope are reopened against current producers",
      kind="known_bad")
def t_matching_three_stale_assertions():
    _, workspace, state = fresh_run("publication-stale-")
    receipt = json.loads((workspace / driver.RECEIPT).read_text())
    commission = json.loads((workspace / driver.COMMISSION).read_text())
    envelope = json.loads((workspace / driver.ENVELOPE).read_text())
    eq(receipt["subject"], commission["subject"], "receipt/commission stale subject")
    eq(receipt["subject"], envelope["subject"], "receipt/envelope stale subject")
    initial = state["initial_grader"]
    check("RP-SUBJECT" in codes(initial), "current producer mismatch rejected")
    check("RP-SOURCE" in codes(initial), "current live source mismatch rejected")
    eq(initial["evidence"]["opener_calls"], 0,
       "actual current agent-open refused before attempt allocation")
    eq(initial["evidence"]["pcb_flow_exit"], 2,
       "operational archive refusal is distinct")


@test("recipient Git omission and default recursive archive ceiling are independently visible",
      kind="known_bad")
def t_git_and_archive_census():
    _, workspace, state = fresh_run("publication-census-")
    initial = state["initial_grader"]
    preflight = initial["evidence"]["preflight"]
    eq(preflight["status"], "INCOMPLETE", "depth ceiling result")
    check("RP-GIT" in codes(initial), "required untracked drill rejected")
    check("RP-OPERATION" in codes(initial), "recursive archive ceiling rejected")
    eq(preflight["census"]["archive_inspection"]["max_depth"], 4,
       "production default inspected to its ceiling")
    tracked = subprocess.run(
        ["git", "cat-file", "-e",
         "HEAD:06_build/candidates/crow-publication-v0.1/fab/board-PTH.drl"],
        cwd=workspace, capture_output=True).returncode == 0
    check(not tracked, "omitted drill must really be absent from recipient HEAD")
    check((workspace / driver.CANDIDATE / "fab/board-PTH.drl").is_file(),
          "omitted drill remains a real candidate member")


@test("declared tiny transport cap exercises RP-TRANSPORT without changing production defaults",
      kind="known_bad")
def t_transport_resource_cap():
    _, workspace, _ = fresh_run("publication-transport-")
    driver.apply_reference(ROOT, workspace)
    payload = workspace / driver.CANDIDATE / "verification/transport-fixture.bin"
    payload.write_bytes(b"x" * 512)
    driver.write_manifest(workspace)
    driver.git(workspace, "add", str(driver.CANDIDATE))
    driver.git(workspace, "commit", "-q", "-m", "test-only outgoing population")
    driver.write_assertions(ROOT, workspace)

    pre, _, _ = driver.load_modules(ROOT)
    import publication_transport_gate as transport
    eq(transport.DEFAULT_BLOB_LIMIT, 100 * 1024 * 1024,
       "production blob limit remains separately owned")
    eq(transport.DEFAULT_BATCH_LIMIT, 1536 * 1024 * 1024,
       "production batch limit remains separately owned")
    actual_grade = transport.grade

    def resource_limited(repo, head, bases):
        return actual_grade(repo, head, bases, blob_limit=256, batch_limit=1024)

    with patch.object(pre, "transport_grade", resource_limited):
        admission, _, _, _ = driver.admission(ROOT, workspace)
    eq(admission.status, "REFUSED", "test-resource transport verdict")
    check(any(row.code == "RP-TRANSPORT" for row in admission.findings),
          "outgoing blob excess reached owning preflight")


@test("pre-fix real pcb_flow allocated stale release review", kind="known_bad")
def t_prefx_agent_open_red():
    _, workspace, _ = fresh_run("publication-prefx-")
    isolated = tmpdir("publication-old-flow-") / "skills/kicad-pcb/scripts"
    isolated.mkdir(parents=True)
    source = subprocess.run(
        ["git", "show", f"{PRE_FIX_COMMIT}:skills/kicad-pcb/scripts/pcb_flow.py"],
        cwd=ROOT, check=True, capture_output=True).stdout
    old_path = isolated / "pcb_flow.py"
    old_path.write_bytes(source)
    old_flow = load("publication_prefx_pcb_flow", old_path)
    calls = []

    def recorder(envelope, *, cwd):
        calls.append(envelope)
        return {"attempt": "recorded", "envelope_sha256": "old-path",
                "output_dir": "recorded", "scratch_dir": "recorded",
                "deadline_at": envelope.deadline_at}

    output = io.StringIO()
    with patch("pipeline_runtime.open_agent_attempt", recorder), \
            contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        rc = old_flow.main([
            "agent-open", str(workspace), "--envelope",
            str(workspace / driver.ENVELOPE),
        ])
    eq(rc, 0, output.getvalue())
    eq(len(calls), 1, "pre-fix stale attempt allocation")
    check("release-review-preflight-v1" not in output.getvalue(),
          "pre-fix path unexpectedly ran current admission")


@test("READY preflight defers exactly four outputs and cannot seal")
def t_ready_does_not_seal():
    _, workspace, _ = fresh_run("publication-ready-")
    driver.apply_reference(ROOT, workspace)
    admission, envelope, pcb_flow, base = driver.admission(ROOT, workspace)
    eq(admission.status, "READY", str(admission.to_mapping()))
    eq(tuple(admission.deferred_review_outputs), driver.DEFERRED,
       "legitimate future output census")
    for relative in driver.DEFERRED:
        check(not (workspace / driver.CANDIDATE / relative).exists(),
              f"preflight created future review output {relative}")
    rc, opened, output = driver.open_boundary(workspace, envelope, pcb_flow, base)
    eq((rc, opened), (0, 1), output)
    check(not (workspace / "07_releases/sealed").exists(),
          "agent-open/preflight fabricated a release seal")


if __name__ == "__main__":
    raise SystemExit(main())
