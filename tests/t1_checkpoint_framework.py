#!/usr/bin/env python3
"""Deterministic controls for the resumable checkpoint runner and adapter."""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKPOINTS = HERE / "checkpoints"
sys.path.insert(0, str(CHECKPOINTS))
sys.path.insert(0, str(HERE))

from harness import check, eq, main, test, tmpdir  # noqa: E402
import agent_run  # noqa: E402
import runner  # noqa: E402
import select_cases  # noqa: E402


REPO = HERE.parent
CaseError = runner.CaseError


def make_case(*, grader=None, timeout=2, grader_timeout=2):
    """A tiny known-bad policy with an independent deterministic grader."""
    root = tmpdir("checkpoint-framework-")
    case = root / "case"
    snapshot = case / "snapshot"
    snapshot.mkdir(parents=True)
    (snapshot / "policy.txt").write_text("broken\n")
    (case / "task.md").write_text("Repair policy.txt and write HANDOFF.md.\n")
    (case / "grader.py").write_text(
        "import json, pathlib, sys\n"
        "p = pathlib.Path(sys.argv[1]) / 'policy.txt'\n"
        "good = p.read_text().strip() == 'fixed'\n"
        "outcome = 'PASS' if good else 'FAIL'\n"
        "findings = [] if good else [{'code':'BROKEN','message':'policy remains broken'}]\n"
        "print(json.dumps({'schema':1,'outcome':outcome,'findings':findings}))\n"
        "raise SystemExit(0 if good else 1)\n")
    manifest = {
        "schema": 1, "id": "synthetic-policy", "title": "Synthetic policy repair",
        "tags": ["synthetic"],
        "origin": {"board": "synthetic", "revision": "fixture-v1", "evidence": [],
                   "reduction": "One text policy and a deterministic independent grader."},
        "checkpoint": {"stage_id": "JLC-ASSEMBLY-VERIFY",
                       "states": {"JLC-ASSEMBLY-VERIFY": "blocked"}, "history": []},
        "task_file": "task.md", "snapshot_dir": "snapshot",
        "editable": ["policy.txt", "HANDOFF.md"], "prepare": [],
        "grader": grader or [sys.executable, "{case}/grader.py", "{workspace}"],
        "initial_findings": ["BROKEN"], "timeout_s": timeout,
        "grader_timeout_s": grader_timeout,
    }
    (case / "case.json").write_text(json.dumps(manifest))
    return case


def fresh_run(prefix="checkpoint-run-"):
    return tmpdir(prefix) / "run"


def complete_workspace(run):
    ws = run / "workspace"
    (ws / "policy.txt").write_text("fixed\n")
    (ws / "HANDOFF.md").write_text("Changed policy; deterministic grader passes.\n")
    return ws


@test("checkpoint calibrates FAIL, loads current context, and accepts reference repair")
def t_reference_repair():
    case, run = make_case(), fresh_run()
    state = runner.prepare(case, run, repo=REPO)
    eq(state["initial_grader"]["outcome"], "FAIL", "initial grader")
    eq(state["initial_grader"]["findings"][0]["code"], "BROKEN", "initial finding")
    start = run / "workspace/.checkpoint_context/START.md"
    check(start.is_file() and "JLC-ASSEMBLY-VERIFY" in start.read_text(),
          "prepared current checkpoint context/START.md is missing")
    check((run / "workspace/.checkpoint_context/skills/pcb-design/SKILL.md").is_file(),
          "current PCB skill context was not loaded")
    check(state["skill_revision_hashes"], "prepared skill revision hashes are empty")
    complete_workspace(run)
    result = runner.grade(run)
    eq(result["outcome"], "PASS", "repaired policy")


@test("checkpoint preserves retired investigation history and rejects incompatible stages", kind="known_bad")
def t_graph_history():
    case = make_case()
    path = case / "case.json"
    manifest = json.loads(path.read_text())
    manifest["checkpoint"]["history"] = [{"attempt": 2, "result": "failed",
        "disposition": "retired: deleting the required part hides the defect",
        "reconsider_when": "requirements explicitly remove that function"}]
    path.write_text(json.dumps(manifest))
    target = fresh_run()
    runner.prepare(case, target)
    start = (target / "workspace/.checkpoint_context/START.md").read_text()
    check("deleting the required part" in start and "requirements explicitly remove" in start,
          "retired approach and reconsideration condition were not disclosed")
    manifest["checkpoint"]["stage_id"] = "REMOVED-STAGE"
    path.write_text(json.dumps(manifest))
    try:
        runner.prepare(case, fresh_run())
    except CaseError:
        pass
    else:
        raise AssertionError("incompatible graph stage was silently accepted")


@test("checkpoint detects trusted skill source drift in an isolated repository", kind="known_bad")
def t_skill_source_drift():
    repo = tmpdir("checkpoint-skill-copy-")
    for skill in ("pcb-design", "kicad-pcb", "jlcpcb-fab"):
        shutil.copytree(REPO / "skills" / skill, repo / "skills" / skill,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    case, target = make_case(), fresh_run()
    runner.prepare(case, target, repo=repo)
    complete_workspace(target)
    eq(runner.grade(target)["outcome"], "PASS", "unchanged skill control")
    source = repo / "skills/jlcpcb-fab/scripts/assembly_coverage.py"
    source.write_text(source.read_text() + "\n# changed checker source\n")
    try:
        result = runner.grade(target)
    except CaseError:
        result = json.loads((target / "result.json").read_text())
    eq(result["outcome"], "ERROR", "stale trusted skill")


@test("checkpoint agent timeout cannot pass with repaired files", kind="known_bad")
def t_agent_timeout():
    case, target = make_case(timeout=0.2), fresh_run()
    result = runner.run_case(case, target, [sys.executable, "-c",
        "from pathlib import Path; import time; Path('policy.txt').write_text('fixed'); "
        "Path('HANDOFF.md').write_text('repair'); time.sleep(5)"])
    eq(result["outcome"], "ERROR", "timed-out solver")
    eq(result["engineering_outcome"], "PASS", "artifact verdict retained")
    eq(result["agent_execution"]["status"], "TIMED_OUT", "timeout execution retained")


@test("checkpoint does not accept an unchanged placeholder handoff", kind="known_bad")
def t_stale_handoff():
    case, target = make_case(), fresh_run()
    (case / "snapshot/HANDOFF.md").write_text("pending repair\n")
    runner.prepare(case, target)
    (target / "workspace/policy.txt").write_text("fixed\n")
    eq(runner.grade(target)["outcome"], "ERROR", "unchanged handoff")


@test("checkpoint exit-zero unsolved workspace remains FAIL", kind="known_bad")
def t_unsolved_is_fail():
    case, run = make_case(), fresh_run()
    runner.prepare(case, run, repo=REPO)
    (run / "workspace/HANDOFF.md").write_text("Attempted repair.\n")
    result = runner.grade(run)
    eq(result["outcome"], "FAIL", "unsolved policy")
    eq(result["findings"][0]["code"], "BROKEN", "unsolved finding")


@test("checkpoint rejects protected workspace mutations before grading", kind="known_bad")
def t_protected_mutations():
    case, run = make_case(), fresh_run()
    runner.prepare(case, run, repo=REPO)
    complete_workspace(run)
    (run / "workspace/README.md").write_text("out of scope\n")
    result = runner.grade(run)
    eq(result["outcome"], "ERROR", "out-of-scope result")
    eq(result["execution_status"], "NOT_RUN", "out-of-scope grader status")
    (run / "workspace/.checkpoint_context/START.md").write_text("tampered\n")
    try:
        runner.grade(run)
    except CaseError as exc:
        check("context" in str(exc), f"wrong protected-context rejection: {exc}")
    else:
        raise AssertionError("tampered protected skill context was accepted")


@test("checkpoint requires a fresh run directory", kind="known_bad")
def t_stale_run_dir():
    case, run = make_case(), fresh_run()
    run.mkdir()
    (run / "stale").write_text("old run\n")
    try:
        runner.prepare(case, run, repo=REPO)
    except CaseError as exc:
        check("fresh" in str(exc), f"wrong stale-run rejection: {exc}")
    else:
        raise AssertionError("preexisting run directory was accepted")


@test("checkpoint rejects malformed, crashing, and timed-out graders", kind="known_bad")
def t_bad_graders():
    cases = [
        (make_case(grader=[sys.executable, "-c", "import json; print(json.dumps(dict(schema=2,outcome='PASS',findings=[])))"]),
         2, "grader JSON"),
        (make_case(grader=[sys.executable, "-c", "raise SystemExit(7)"]), 2,
         ("initial grader calibration", "exactly one JSON object")),
        (make_case(grader=[sys.executable, "-c", "import time; time.sleep(4)"],
                   grader_timeout=0.2), 0.2,
         ("initial grader calibration", "exactly one JSON object")),
    ]
    for case, _, expected in cases:
        try:
            runner.prepare(case, fresh_run(), repo=REPO)
        except CaseError as exc:
            accepted = (expected,) if isinstance(expected, str) else expected
            check(any(message in str(exc) for message in accepted),
                  f"wrong grader failure {exc!r}, expected one of {accepted!r}")
        else:
            raise AssertionError(f"invalid grader was accepted ({expected})")


@test("checkpoint persists malformed final grader output as ERROR", kind="known_bad")
def t_malformed_final_grade():
    case = make_case()
    (case / "grader.py").write_text(
        "import json, pathlib, sys\n"
        "workspace = pathlib.Path(sys.argv[1]); marker = pathlib.Path(sys.argv[2]).parent / '.grade-count'\n"
        "count = int(marker.read_text()) if marker.exists() else 0\n"
        "marker.write_text(str(count + 1))\n"
        "if count: print('malformed final grader output')\n"
        "else:\n"
        " good = (workspace / 'policy.txt').read_text().strip() == 'fixed'\n"
        " outcome = 'PASS' if good else 'FAIL'\n"
        " findings = [] if good else [{'code':'BROKEN','message':'policy remains broken'}]\n"
        " print(json.dumps(dict(schema=1,outcome=outcome,findings=findings)))\n"
        " raise SystemExit(0 if good else 1)\n")
    manifest = json.loads((case / "case.json").read_text())
    manifest["grader"] = [sys.executable, "{case}/grader.py", "{workspace}", "{case}"]
    (case / "case.json").write_text(json.dumps(manifest))
    run = fresh_run()
    runner.prepare(case, run, repo=REPO)
    complete_workspace(run)
    result = runner.grade(run)
    eq(result["outcome"], "ERROR", "malformed final grader outcome")
    eq(result["findings"][0]["code"], "RUNNER_CONTRACT", "malformed grader finding")
    persisted = json.loads((run / "result.json").read_text())
    eq(persisted["outcome"], "ERROR", "persisted malformed grader outcome")


@test("checkpoint keeps nonzero solver exit as ERROR even after an apparent repair", kind="known_bad")
def t_nonzero_solver_exit_sticky():
    case, run = make_case(), fresh_run()
    command = [sys.executable, "-c",
               "import pathlib,sys; p=pathlib.Path(sys.argv[1]); (p/'policy.txt').write_text('fixed\\n'); (p/'HANDOFF.md').write_text('Repair attempted.\\n'); raise SystemExit(7)",
               "{workspace}"]
    result = runner.run_case(case, run, command, repo=REPO)
    eq(result["outcome"], "ERROR", "nonzero solver result")
    eq(result["engineering_outcome"], "PASS", "engineering grader result")
    eq(result["findings"][-1]["code"], "AGENT_EXECUTION", "solver exit finding")
    persisted = json.loads((run / "result.json").read_text())
    eq(persisted["outcome"], "ERROR", "persisted nonzero solver result")
    regraded = runner.grade(run)
    eq(regraded["outcome"], "ERROR", "regraded nonzero solver result")
    eq(regraded["engineering_outcome"], "PASS", "regraded engineering result")
    check("agent_execution" in regraded, "regrade discarded solver execution record")


@test("checkpoint selector narrows known case edits and keeps full suite for unknown paths")
def t_selector_conservative():
    root = tmpdir("checkpoint-select-")
    (root / "cases/a").mkdir(parents=True)
    (root / "cases/b").mkdir(parents=True)
    for name in ("a", "b"):
        (root / "cases" / name / "case.json").write_text(json.dumps({"tags": [name]}))
    (root / "suites.json").write_text(json.dumps({"schema": 1, "suites": {"smoke": ["a", "b"]}}))
    narrowed = select_cases.select(root=root, changed=["tests/checkpoints/cases/a/case.json"])
    eq([p.name for p in narrowed], ["a"], "known case edit selection")
    conservative = select_cases.select(root=root, changed=["tests/t1_checkpoint_framework.py"])
    eq([p.name for p in conservative], ["a", "b"], "unknown edit selection")
    try:
        select_cases.select(root=root, tags=["missing"])
    except ValueError as exc:
        check("empty" in str(exc), f"wrong empty-selection rejection: {exc}")
    else:
        raise AssertionError("empty tag selection was accepted")


@test("agent adapter fixes explicit model and workspace-write sandbox")
def t_agent_command_policy():
    run = fresh_run()
    argv = agent_run.command(run, "test-model", "low", executable="codex-stub")
    eq(argv[argv.index("--sandbox") + 1], "workspace-write", "agent sandbox")
    eq(argv[argv.index("-m") + 1], "test-model", "explicit model")
    eq(argv[argv.index("-a") + 1], "never", "approval policy")
    check("--dangerously-bypass-approvals-and-sandbox" not in argv,
          "agent adapter bypasses approvals or sandbox")
    check(str((run / "workspace").resolve()) == argv[argv.index("-C") + 1],
          "agent current directory is not the prepared workspace")


@test("agent usage stays UNKNOWN when absent and sums reported completed turns")
def t_agent_usage_report():
    root = tmpdir("checkpoint-usage-")
    log = root / "events.jsonl"
    log.write_text("")
    missing = agent_run.usage_from_log(log)
    eq(missing["status"], "UNKNOWN", "missing usage status")
    check(all(value is None for value in missing["tokens"].values()),
          "missing token usage was invented")
    log.write_text("\n".join([
        json.dumps({"type": "turn.completed", "usage": {"input_tokens": 10, "cached_input_tokens": 3, "output_tokens": 4}}),
        json.dumps({"type": "error", "message": "interrupted"}),
        json.dumps({"type": "turn.completed", "usage": {"input_tokens": 7, "cached_input_tokens": 2, "output_tokens": 5}}),
    ]) + "\n")
    reported = agent_run.usage_from_log(log)
    eq(reported["status"], "REPORTED", "reported usage status")
    eq(reported["tokens"], {"input_tokens": 17, "cached_input_tokens": 5, "output_tokens": 9},
       "reported token totals")
    eq(reported["error_events"], ["error"], "interrupted event")
    check("interrupted-turn usage may be missing" in reported["coverage"],
          "interrupted-turn limitation was omitted")


@test("agent usage marks incomplete provider records PARTIAL", kind="known_bad")
def t_partial_usage():
    log = tmpdir("checkpoint-partial-") / "events.jsonl"
    log.write_text(json.dumps({"type": "turn.completed", "usage": {
        "input_tokens": 10, "cached_input_tokens": 3, "output_tokens": 4}}) + "\n" +
        json.dumps({"type": "turn.completed", "usage": {}}) + "\n")
    reported = agent_run.usage_from_log(log)
    eq(reported["status"], "PARTIAL", "malformed usage cannot be fully reported")
    check(reported["incomplete_fields"], "missing-field reason must be retained")


@test("sandbox preflight fails before invoking a model", kind="known_bad")
def t_sandbox_preflight():
    result = agent_run.sandbox_preflight("/bin/false")
    eq(result["outcome"], "ERROR", "unavailable sandbox")
    eq(result["returncode"], 1, "probe return code")


if __name__ == "__main__":
    sys.exit(main())
