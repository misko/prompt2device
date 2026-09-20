#!/usr/bin/env python3
"""T1 controls for append-only issue-level execution telemetry."""
from __future__ import annotations

import json
import multiprocessing
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import check, eq, main, test  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "pcb-design" / "scripts"))
from pipeline_issue_ledger import (  # noqa: E402
    LedgerConflictError, LedgerValidationError, append_event, record_run,
    record_start, summarize,
)


def event(event_id="run-1:terminal", *, run_id="run-1", issue="ISS-1",
          started="2026-01-01T00:00:00Z", finished="2026-01-01T00:00:10Z",
          elapsed=10.0, usage=None, response=None, scope=None, status="PASS"):
    return {"schema": 1, "event_id": event_id, "event_type": "TERMINAL",
            "response_id": response, "provider_scope": scope,
            "issue_id": issue, "attempt_id": "attempt-1", "run_id": run_id,
            "stage_id": "routing", "model": "test-model", "effort": None, "status": status,
            "started_at": started, "finished_at": finished, "elapsed_s": elapsed,
            "provenance": None, "token_usage": usage, "provider_cost_usd": None}


def ledger() -> Path:
    return Path(tempfile.mkdtemp(prefix="issue-ledger-")) / "usage.jsonl"


def rejects(fn, expected):
    try:
        fn()
    except LedgerValidationError as exc:
        check(expected in str(exc), f"{exc!s} lacks {expected!r}")
    else:
        raise AssertionError("malformed ledger data SHOULD HAVE FAILED")


@test("append-only events round-trip and repeat safely")
def t_append_and_replay():
    path = ledger()
    eq(append_event(path, event()).status, "APPENDED")
    eq(append_event(path, event()).status, "DUPLICATE")
    lines = path.read_text().splitlines()
    eq(len(lines), 1, "idempotent physical event count")
    eq(json.loads(lines[0])["run_id"], "run-1", "stored run attribution")


@test("conflicting event or provider response identities fail closed", kind="known_bad")
def t_identity_conflicts():
    path = ledger()
    append_event(path, event(response="rsp-1", scope="provider-a"))
    rejects(lambda: append_event(path, event(finished="2026-01-01T00:00:11Z")),
            "conflicting duplicate event_id")
    rejects(lambda: append_event(path, event("run-2:terminal", run_id="run-2",
            response="rsp-1", scope="provider-a")), "conflicting duplicate response_id")
    eq(append_event(path, event("run-3:terminal", run_id="run-3", response="rsp-1",
                                 scope="provider-b")).status, "APPENDED",
       "provider scope separates response identity")


@test("strict telemetry schema rejects cumulative and impossible usage", kind="known_bad")
def t_hostile_schema():
    path = ledger()
    bad = event()
    bad["token_count"] = 100
    rejects(lambda: append_event(path, bad), "unknown=['token_count']")
    bad = event(usage={"authority": "provider", "metric": "raw",
                       "input_tokens": 10, "cached_input_tokens": 11,
                       "output_tokens": 3, "reasoning_tokens": 4, "total_tokens": 13})
    rejects(lambda: append_event(path, bad), "subset of input_tokens")
    bad = event(usage={"authority": "provider", "metric": "raw",
                       "input_tokens": 10, "cached_input_tokens": 1,
                       "output_tokens": 3, "reasoning_tokens": 2, "total_tokens": 99})
    rejects(lambda: append_event(path, bad), "must equal input_tokens")


@test("durable starts survive a crash and terminal runs retain unknown usage")
def t_start_crash_and_unknown():
    path = ledger()
    record_start(path, issue_id="ISS-1", attempt_id="attempt-1", run_id="crashed",
                 stage_id="placement", started_at="2026-01-01T00:00:00Z",
                 provenance={"command_sha256": "a" * 64})
    record_start(path, issue_id="ISS-1", attempt_id="attempt-2", run_id="finished",
                 stage_id="routing", started_at="2026-01-01T00:01:00Z",
                 provenance={"source_sha256": "b" * 64})
    record_run(path, issue_id="ISS-1", attempt_id="attempt-2", outcome={
        "run_id": "finished", "stage_id": "routing", "status": "PASS",
        "started_at": "2026-01-01T00:01:00Z", "finished_at": "2026-01-01T00:01:05Z",
        "elapsed_s": 5})
    result = summarize(path)["issues"]["ISS-1"]
    eq(result["event_count"], 2, "collapsed run count")
    eq(result["incomplete_run_count"], 1, "durable lone start")
    eq(result["token_usage"]["status"], "UNKNOWN", "missing is not zero")
    check("totals" not in result["token_usage"], "unknown usage received totals")


@test("a run has immutable attribution and one terminal receipt", kind="known_bad")
def t_run_identity_is_immutable():
    path = ledger()
    record_start(path, issue_id="ISS #1", attempt_id="attempt-1", run_id="run-1",
                 stage_id="routing", started_at="2026-01-01T00:00:00Z")
    wrong_stage = event(issue="ISS #1", started="2026-01-01T00:00:00Z")
    wrong_stage["stage_id"] = "placement"
    wrong_stage["model"] = None
    rejects(lambda: append_event(path, wrong_stage), "conflicting stage_id")
    terminal = event(issue="ISS #1")
    terminal["model"] = None
    append_event(path, terminal)
    later = event("later:terminal", run_id="run-1", issue="ISS #1")
    later["model"] = None
    rejects(lambda: append_event(path, later),
            "multiple TERMINAL events")


@test("partial token fields stay unknown and metrics remain partitioned")
def t_partial_and_partitioned_usage():
    path = ledger()
    first = {"authority": "provider-a", "metric": "raw", "input_tokens": 10,
             "cached_input_tokens": 4, "output_tokens": 5, "reasoning_tokens": None,
             "total_tokens": 15}
    second = {"authority": "provider-b", "metric": "normalized", "input_tokens": 8,
              "cached_input_tokens": 3, "output_tokens": 2, "reasoning_tokens": 1,
              "total_tokens": 10}
    append_event(path, event("one:terminal", run_id="one", usage=first))
    append_event(path, event("two:terminal", run_id="two", usage=second))
    groups = summarize(path)["issues"]["ISS-1"]["token_usage"]
    eq(groups["status"], "PARTIAL", "mixed authorities are non-additive")
    eq(len(groups["groups"]), 2, "separate authority groups")
    a_group = groups["groups"][0]
    eq(a_group["totals"]["noncached_input_tokens"], 6,
       "derived uncached input")
    check("reasoning_tokens" not in a_group["totals"],
          "unknown reasoning was silently zeroed")


@test("raw duplicate records are rejected before summary accounting", kind="known_bad")
def t_raw_duplicate_is_refused():
    path = ledger()
    encoded = json.dumps(event(), sort_keys=True) + "\n"
    path.write_text(encoded + encoded)
    rejects(lambda: summarize(path), "duplicate event_id")


@test("complete provider usage remains measured with derived uncached tokens")
def t_complete_provider_usage():
    # RED against the first implementation's len(totals) equality after it
    # added the derived noncached field; restored by checking required keys.
    path = ledger()
    usage = {"authority": "provider-a", "metric": "raw",
             "input_tokens": 100, "cached_input_tokens": 80,
             "output_tokens": 10, "reasoning_tokens": 4, "total_tokens": 110}
    row = event(usage=usage, response="response-1", scope="account-a", status="FAIL")
    row["effort"] = "medium"
    row["provider_cost_usd"] = 0.25
    append_event(path, row)
    eq(append_event(path, row).status, "DUPLICATE", "provider replay counted once")
    result = summarize(path)["issues"]["ISS-1"]
    eq(result["token_usage"]["status"], "MEASURED", "complete usage")
    totals = result["token_usage"]["groups"][0]["totals"]
    eq(totals["noncached_input_tokens"], 20, "cached is a subset")
    eq(totals["total_tokens"], 110, "reasoning not added twice")
    eq(result["provider_cost_usd"]["total"], 0.25, "failed calls retain cost")


@test("interval union remains distinct from overlapping worker durations")
def t_overlap_summary():
    path = ledger()
    append_event(path, event("a:terminal", run_id="a", started="2026-01-01T00:00:00Z",
                             finished="2026-01-01T00:00:10Z", elapsed=10))
    append_event(path, event("b:terminal", run_id="b", started="2026-01-01T00:00:05Z",
                             finished="2026-01-01T00:00:15Z", elapsed=10))
    result = summarize(path)["issues"]["ISS-1"]
    eq(result["execution_interval_union_s"], 15.0, "wall interval union")
    eq(result["summed_worker_duration_s"], 20.0, "parallel worker sum")


def _append_worker(path: str, index: int) -> None:
    append_event(path, event(f"run-{index}:terminal", run_id=f"run-{index}"))


@test("concurrent appenders retain every whole JSONL event")
def t_concurrent_append():
    path = ledger()
    workers = [multiprocessing.Process(target=_append_worker, args=(str(path), i))
               for i in range(12)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(20)
        eq(worker.exitcode, 0, "concurrent writer exit")
    eq(len(path.read_text().splitlines()), 12, "whole append records")
    eq(summarize(path)["issues"]["ISS-1"]["event_count"], 12,
       "concurrently retained run count")


if __name__ == "__main__":
    raise SystemExit(main())
