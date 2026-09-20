#!/usr/bin/env python3
"""Append-only, bounded issue-level execution telemetry.

This is accounting evidence, not an execution controller, acceptance gate, or
provider client.  A JSONL ledger contains durable START and TERMINAL events.
Every event is attributed to an ``issue_id``, ``attempt_id``, and ``run_id``;
``model`` is an optional provider/model label.  ``token_usage`` is nullable:
missing telemetry remains unknown and is never changed to zero.

Public API
----------
``append_event(path, event)`` validates and atomically appends an event under
an advisory file lock.  Replaying an identical ``event_id`` (or scoped non-null
``response_id``) returns ``DUPLICATE``; a reused identity with different data
raises ``LedgerConflictError``.  ``record_run(...)`` adapts an existing
``RuntimeOutcome`` and optional ``StageResult`` (or their mappings), without
importing either module.  ``summarize(path, issue_id=None)`` returns per-issue
token/cost coverage and both interval-union wall time and summed worker time.

The schema intentionally has no cumulative ``token_count`` event: each run has
at most one START and one TERMINAL observation, so retries can be deduplicated.
A crash is represented by an ``INCOMPLETE`` start with null finish/duration;
such a record remains visible in summaries. Schema-2 USAGE observations carry
per-response spending without inventing execution timing. The separate
pipeline_usage_import adapter owns source parsing and explicit attribution.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import math
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA = 1
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$")
_UTC_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z$")
_STATUSES = frozenset({"PASS", "FAIL", "ERROR", "TIMED_OUT", "INCOMPLETE", "CANCELLED"})
_FIELDS = frozenset({"schema", "event_id", "event_type", "response_id", "provider_scope", "issue_id", "attempt_id", "run_id", "stage_id", "model", "effort", "status", "started_at", "finished_at", "elapsed_s", "provenance", "token_usage", "provider_cost_usd"})
_USAGE_FIELDS = frozenset({"authority", "metric", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens", "total_tokens"})


class LedgerValidationError(ValueError):
    """An event or persisted ledger record violates the closed schema."""


class LedgerConflictError(LedgerValidationError):
    """An event or provider response identity was reused with different data."""


@dataclass(frozen=True)
class AppendResult:
    status: str
    event_id: str


def _fail(message: str) -> None:
    raise LedgerValidationError(message)


def _id(value: Any, where: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        _fail(f"{where}: expected a non-empty safe identifier")
    return value


def _issue_id(value: Any) -> str:
    """Issue systems own their identifiers; preserve any bounded text key."""
    if (not isinstance(value, str) or not value.strip() or len(value) > 200 or
            "\0" in value or "\n" in value or "\r" in value):
        _fail("issue_id: expected a non-empty bounded identifier without controls")
    return value


def _timestamp(value: Any, where: str, *, nullable: bool = False) -> tuple[str | None, datetime | None]:
    if value is None and nullable:
        return None, None
    if not isinstance(value, str) or _UTC_RE.fullmatch(value) is None:
        _fail(f"{where}: expected canonical RFC3339 UTC timestamp ending in Z")
    try:
        return value, datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise LedgerValidationError(f"{where}: invalid RFC3339 UTC timestamp") from exc


def _number(value: Any, where: str, *, nullable: bool = False) -> float | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        _fail(f"{where}: expected a non-negative finite number")
    return float(value)


def normalize_usage(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping) or set(value) != _USAGE_FIELDS:
        _fail("token_usage: expected its exact schema-1 fields")
    authority, metric = value["authority"], value["metric"]
    if not isinstance(authority, str) or not authority.strip():
        _fail("token_usage.authority: expected a non-empty string")
    if not isinstance(metric, str) or not metric.strip():
        _fail("token_usage.metric: expected a non-empty string")
    result: dict[str, Any] = {"authority": authority, "metric": metric}
    for name in _USAGE_FIELDS - {"authority", "metric"}:
        raw = value[name]
        if raw is not None and (isinstance(raw, bool) or not isinstance(raw, int) or raw < 0):
            _fail(f"token_usage.{name}: expected null or a non-negative integer")
        result[name] = raw
    cached, input_tokens = result["cached_input_tokens"], result["input_tokens"]
    reasoning, output = result["reasoning_tokens"], result["output_tokens"]
    if cached is not None and (input_tokens is None or cached > input_tokens):
        _fail("token_usage.cached_input_tokens must be a subset of input_tokens")
    if reasoning is not None and (output is None or reasoning > output):
        _fail("token_usage.reasoning_tokens must be a subset of output_tokens")
    total = result["total_tokens"]
    if total is not None and input_tokens is not None and output is not None and total != input_tokens + output:
        _fail("token_usage.total_tokens must equal input_tokens + output_tokens when both are known")
    return result


def _provenance(value: Any) -> dict[str, str] | None:
    """Accept only named SHA-256 evidence; raw commands and credentials stay out."""
    if value is None:
        return None
    if not isinstance(value, Mapping) or not value:
        _fail("provenance: expected null or a non-empty mapping of SHA-256 digests")
    result = {}
    for key, digest in value.items():
        if (not isinstance(key, str) or not _ID_RE.fullmatch(key) or
                not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None):
            _fail("provenance: keys must be safe identifiers and values lowercase SHA-256 digests")
        result[key] = digest
    return dict(sorted(result.items()))


def normalize_event(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return a validated plain event mapping with canonical numeric values."""
    if not isinstance(value, Mapping):
        _fail("event: expected a mapping")
    schema = value.get("schema")
    if schema not in (1, 2) or isinstance(schema, bool):
        _fail("schema: only schema 1 execution and schema 2 usage observations are supported")
    fields = _FIELDS | {"observed_at"} if schema == 2 else _FIELDS
    if set(value) != fields:
        _fail(f"event: fields differ (missing={sorted(fields - set(value))}, unknown={sorted(set(value) - fields)})")
    event_id = _id(value["event_id"], "event_id")
    event_type = value["event_type"]
    if event_type not in ({"USAGE"} if schema == 2 else {"START", "TERMINAL"}):
        _fail("event_type: schema 1 requires START/TERMINAL; schema 2 requires USAGE")
    response_id = _id(value["response_id"], "response_id", nullable=True)
    provider_scope = _id(value["provider_scope"], "provider_scope", nullable=True)
    if (response_id is None) != (provider_scope is None):
        _fail("response_id and provider_scope must both be null or both be explicit")
    issue_id = _issue_id(value["issue_id"])
    attempt_id = _id(value["attempt_id"], "attempt_id")
    run_id = _id(value["run_id"], "run_id")
    stage_id = _id(value["stage_id"], "stage_id", nullable=True)
    model = value["model"]
    if model is not None and (not isinstance(model, str) or not model.strip() or len(model) > 200):
        _fail("model: expected null or a non-empty string of at most 200 characters")
    effort = value["effort"]
    if effort is not None and (not isinstance(effort, str) or not effort.strip() or len(effort) > 200):
        _fail("effort: expected null or a non-empty string of at most 200 characters")
    status = value["status"]
    if status not in _STATUSES:
        _fail(f"status: expected one of {sorted(_STATUSES)}")
    started_at, started = _timestamp(value["started_at"], "started_at", nullable=schema == 2)
    finished_at, finished = _timestamp(value["finished_at"], "finished_at", nullable=True)
    elapsed = _number(value["elapsed_s"], "elapsed_s", nullable=True)
    if event_type == "USAGE":
        if response_id is None or any(value[key] is not None for key in
                                     ("started_at", "finished_at", "elapsed_s")):
            _fail("USAGE requires a scoped response ID and null execution timing")
        _timestamp(value["observed_at"], "observed_at", nullable=True)
    elif event_type == "START":
        if status != "INCOMPLETE" or finished is not None or elapsed is not None:
            _fail("START events require INCOMPLETE status and null finished_at/elapsed_s")
        if response_id is not None or value["token_usage"] is not None or value["provider_cost_usd"] is not None:
            _fail("START events cannot carry provider response, usage, or cost")
    elif status == "INCOMPLETE":
        # A terminal INCOMPLETE may carry a measured elapsed duration when a
        # bounded launcher returns a partial receipt before process recovery.
        pass
    elif finished is None or elapsed is None:
        _fail("terminal events require finished_at and elapsed_s")
    if event_type == "TERMINAL" and status == "INCOMPLETE" and (finished is None or elapsed is None):
        _fail("terminal INCOMPLETE events require finished_at and elapsed_s")
    if finished is not None and finished < started:
        _fail("finished_at cannot precede started_at")
    return {"schema": schema, "event_id": event_id, "event_type": event_type,
            "response_id": response_id, "provider_scope": provider_scope,
            "issue_id": issue_id, "attempt_id": attempt_id, "run_id": run_id,
            "stage_id": stage_id, "model": model, "effort": effort, "status": status,
            "started_at": started_at, "finished_at": finished_at, "elapsed_s": elapsed,
            "provenance": _provenance(value["provenance"]),
            "token_usage": normalize_usage(value["token_usage"]),
            "provider_cost_usd": _number(value["provider_cost_usd"], "provider_cost_usd", nullable=True),
            **({"observed_at": value["observed_at"]} if schema == 2 else {})}


def _canonical(event: Mapping[str, Any]) -> str:
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def validate_response_id(value: Any) -> str:
    """Shared provider-response identity grammar for ingestion adapters."""
    return _id(value, "response_id")


def equivalent_event(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    """USAGE observation clocks can differ across parent/child log copies.

    Preserve the first observed_at; every identity, attribution, usage, cost,
    model and provenance field must agree. Execution events remain exact.
    """
    if left.get("schema") == right.get("schema") == 2:
        return ({k: v for k, v in left.items() if k != "observed_at"} ==
                {k: v for k, v in right.items() if k != "observed_at"})
    return left == right


def validate_event_batch(events: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Public, pure validation boundary; grants no persistence or acceptance."""
    normalized = [normalize_event(event) for event in events]
    _validate_ledger(normalized)
    return normalized


def _locked(path: Path, exclusive: bool):
    path.parent.mkdir(parents=True, exist_ok=True)
    return (path.with_name(path.name + ".lock")).open("a+"), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH


def _read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.endswith("\n"):
                _fail(f"ledger line {number}: incomplete JSONL record")
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LedgerValidationError(f"ledger line {number}: invalid JSON") from exc
            try:
                events.append(normalize_event(raw))
            except LedgerValidationError as exc:
                raise LedgerValidationError(f"ledger line {number}: {exc}") from exc
    _validate_ledger(events)
    return events


def _validate_ledger(events: list[dict[str, Any]]) -> None:
    """Reject impossible hand-written/recovered logs before they can count."""
    event_ids: set[str] = set()
    responses: set[tuple[str, str]] = set()
    runs: dict[str, dict[str, Any]] = {}
    run_types: dict[str, set[str]] = {}
    for event in events:
        if event["event_id"] in event_ids:
            _fail(f"ledger: duplicate event_id {event['event_id']!r}")
        event_ids.add(event["event_id"])
        if event["response_id"] is not None:
            response = (event["provider_scope"], event["response_id"])
            if response in responses:
                _fail(f"ledger: duplicate scoped response_id {response!r}")
            responses.add(response)
        prior = runs.setdefault(event["run_id"], event)
        for key in ("issue_id", "attempt_id", "stage_id", "model", "effort", "started_at"):
            if prior[key] != event[key]:
                _fail(f"ledger: run_id {event['run_id']!r} has conflicting {key}")
        types = run_types.setdefault(event["run_id"], set())
        if types and (event["event_type"] == "USAGE" or "USAGE" in types):
            _fail("ledger: a USAGE observation must have its own response run_id")
        if event["event_type"] in types:
            _fail(f"ledger: run_id {event['run_id']!r} has multiple {event['event_type']} events")
        types.add(event["event_type"])


def append_events(path: str | Path, events: list[Mapping[str, Any]]) -> list[AppendResult]:
    """Validate a batch once and atomically publish its append-only suffix.

    A shared sidecar lock protects both single and batch writers. A malformed
    late observation cannot leave an earlier half-import committed. Existing
    bytes are preserved exactly; replacement only commits the appended suffix.
    """
    ledger = Path(path)
    candidates = [normalize_event(event) for event in events]
    lock, mode = _locked(ledger, True)
    temporary = None
    try:
        fcntl.flock(lock.fileno(), mode)
        existing = _read_events(ledger)
        by_id = {event["event_id"]: event for event in existing}
        by_response = {(event["provider_scope"], event["response_id"]): event
                       for event in existing if event["response_id"] is not None}
        additions, results = [], []
        for candidate in candidates:
            key = (candidate["provider_scope"], candidate["response_id"])
            prior = by_id.get(candidate["event_id"])
            identity = "event_id"
            if prior is None and candidate["response_id"] is not None:
                prior, identity = by_response.get(key), "response_id"
            if prior is not None:
                if not equivalent_event(prior, candidate):
                    raise LedgerConflictError(f"conflicting duplicate {identity}")
                results.append(AppendResult("DUPLICATE", candidate["event_id"]))
                continue
            by_id[candidate["event_id"]] = candidate
            if candidate["response_id"] is not None:
                by_response[key] = candidate
            additions.append(candidate)
            results.append(AppendResult("APPENDED", candidate["event_id"]))
        _validate_ledger(existing + additions)
        if additions:
            with tempfile.NamedTemporaryFile(dir=ledger.parent, prefix=".usage-",
                                             delete=False) as stream:
                temporary = Path(stream.name)
                if ledger.exists():
                    stream.write(ledger.read_bytes())
                for event in additions:
                    stream.write((_canonical(event) + "\n").encode("utf-8"))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, ledger)
            temporary = None
            directory_fd = os.open(ledger.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        return results
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


def append_event(path: str | Path, event: Mapping[str, Any]) -> AppendResult:
    """Durably append one event, or identify its exact idempotent replay."""
    return append_events(path, [event])[0]


def _field(value: Any, key: str, default: Any = None) -> Any:
    return value.get(key, default) if isinstance(value, Mapping) else getattr(value, key, default)


def record_run(path: str | Path, *, issue_id: str, attempt_id: str, outcome: Any,
               stage_result: Any = None, event_id: str | None = None, model: str | None = None,
               token_usage: Mapping[str, Any] | None = None, provider_cost_usd: float | None = None,
               response_id: str | None = None, provider_scope: str | None = None,
               provenance: Mapping[str, str] | None = None,
               effort: str | None = None) -> AppendResult:
    """Adapt a RuntimeOutcome/StageResult or mapping into one ledger event.

    ``event_id`` defaults to ``run_id:terminal``.  A separate provider response
    needs a separate ``run_id`` under the same attempt.
    """
    run_id = _field(outcome, "run_id") or _field(stage_result, "run_id")
    status = _field(outcome, "status") or _field(stage_result, "status")
    event = {"schema": SCHEMA, "event_id": event_id or f"{run_id}:terminal", "event_type": "TERMINAL",
             "response_id": response_id, "provider_scope": provider_scope,
             "issue_id": issue_id, "attempt_id": attempt_id, "run_id": run_id,
             "stage_id": _field(outcome, "stage_id", _field(stage_result, "stage_id")),
             "model": model, "effort": effort, "status": status,
             "started_at": _field(outcome, "started_at", _field(stage_result, "started_at")),
             "finished_at": _field(outcome, "finished_at", _field(stage_result, "finished_at")),
             "elapsed_s": _field(outcome, "elapsed_s", _field(stage_result, "elapsed_s")), "provenance": provenance,
             "token_usage": token_usage, "provider_cost_usd": provider_cost_usd}
    return append_event(path, event)


def record_start(path: str | Path, *, issue_id: str, attempt_id: str, run_id: str,
                 stage_id: str | None, started_at: str, provenance: Mapping[str, str] | None = None,
                 model: str | None = None, effort: str | None = None,
                 event_id: str | None = None) -> AppendResult:
    """Persist launch intent before work begins; a lone start remains incomplete."""
    return append_event(path, {"schema": SCHEMA, "event_id": event_id or f"{run_id}:start",
        "event_type": "START", "response_id": None, "provider_scope": None,
        "issue_id": issue_id, "attempt_id": attempt_id, "run_id": run_id,
        "stage_id": stage_id, "model": model, "effort": effort, "status": "INCOMPLETE",
        "started_at": started_at, "finished_at": None, "elapsed_s": None,
        "provenance": provenance, "token_usage": None, "provider_cost_usd": None})


def _union_seconds(events: list[dict[str, Any]]) -> float:
    intervals = []
    for event in events:
        if event["finished_at"] is not None:
            start = _timestamp(event["started_at"], "started_at")[1]
            end = _timestamp(event["finished_at"], "finished_at")[1]
            intervals.append((start, end))
    total = 0.0
    last_start = last_end = None
    for start, end in sorted(intervals):
        if last_end is None or start > last_end:
            if last_end is not None:
                total += (last_end - last_start).total_seconds()
            last_start, last_end = start, end
        elif end > last_end:
            last_end = end
    if last_end is not None:
        total += (last_end - last_start).total_seconds()
    return total


def _token_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    usages = [event["token_usage"] for event in events]
    measured = [usage for usage in usages if usage is not None]
    coverage = {"run_count": len(events), "measured_run_count": len(measured), "unknown_run_count": len(events) - len(measured)}
    if not measured:
        return {"status": "UNKNOWN", "coverage": coverage}
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for usage in measured:
        groups.setdefault((usage["authority"], usage["metric"]), []).append(usage)
    result_groups = []
    token_fields = _USAGE_FIELDS - {"authority", "metric"}
    for (authority, metric), rows in sorted(groups.items()):
        totals = {}
        for key in sorted(token_fields):
            values = [row[key] for row in rows]
            if all(value is not None for value in values):
                totals[key] = sum(values)
        if "input_tokens" in totals and "cached_input_tokens" in totals:
            totals["noncached_input_tokens"] = (totals["input_tokens"] -
                                                totals["cached_input_tokens"])
        group_status = "MEASURED" if len(rows) == len(events) and token_fields <= totals.keys() else "PARTIAL"
        result_groups.append({"authority": authority, "metric": metric,
                              "status": group_status, "measured_run_count": len(rows),
                              "run_count": len(events),
                              "unknown_field_names": sorted(token_fields - set(totals)),
                              **({"totals": totals} if totals else {})})
    status = "MEASURED" if len(result_groups) == 1 and result_groups[0]["status"] == "MEASURED" else "PARTIAL"
    return {"status": status, "coverage": coverage, "groups": result_groups}


def _issue_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    # A run starts durably, then receives at most one terminal observation.
    # Terminal rows supersede their own start for all totals, preserving lone
    # starts as explicit crash/incomplete evidence.
    by_run: dict[str, dict[str, Any]] = {}
    for event in events:
        prior = by_run.get(event["run_id"])
        if prior is None or event["event_type"] == "TERMINAL":
            by_run[event["run_id"]] = event
    events = list(by_run.values())
    costs = [event["provider_cost_usd"] for event in events]
    measured_costs = [x for x in costs if x is not None]
    executions = [x for x in events if x["event_type"] != "USAGE"]
    completed = [x for x in executions if x["status"] != "INCOMPLETE"]
    return {"event_count": len(events), "completed_run_count": len(completed),
            "incomplete_run_count": len(executions) - len(completed),
            "usage_observation_count": len(events) - len(executions),
            "timing_coverage": {"execution_count": len(executions),
                                "unknown_duration_count": sum(x["elapsed_s"] is None for x in executions),
                                "usage_unknown_duration_count": len(events) - len(executions)},
            "execution_interval_union_s": _union_seconds(events),
            "summed_worker_duration_s": sum(x["elapsed_s"] or 0.0 for x in events),
            "token_usage": _token_summary(events),
            "provider_cost_usd": {"status": "MEASURED" if len(measured_costs) == len(events) else ("PARTIAL" if measured_costs else "UNKNOWN"),
                                  "measured_run_count": len(measured_costs), "run_count": len(events),
                                  **({"total": sum(measured_costs)} if measured_costs else {})},
            "status_counts": {status: sum(x["status"] == status for x in executions) for status in sorted(_STATUSES) if any(x["status"] == status for x in executions)}}


def summarize(path: str | Path, issue_id: str | None = None) -> dict[str, Any]:
    """Read a consistent ledger snapshot and summarize one or all issues."""
    ledger = Path(path)
    if issue_id is not None:
        _issue_id(issue_id)
    lock, mode = _locked(ledger, False)
    try:
        fcntl.flock(lock.fileno(), mode)
        events = _read_events(ledger)
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        if issue_id is None or event["issue_id"] == issue_id:
            grouped.setdefault(event["issue_id"], []).append(event)
    return {"schema": SCHEMA, "ledger_event_count": len(events), "issues": {key: _issue_summary(rows) for key, rows in sorted(grouped.items())}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    sub = parser.add_subparsers(dest="command", required=True)
    append = sub.add_parser("append", help="append one strict event JSON object")
    append.add_argument("--ledger", required=True)
    append.add_argument("--event-json", required=True, help="JSON file path or - for stdin")
    summary = sub.add_parser("summary", help="summarize ledger telemetry")
    summary.add_argument("--ledger", required=True)
    summary.add_argument("--issue-id")
    args = parser.parse_args(argv)
    try:
        if args.command == "append":
            text = sys.stdin.read() if args.event_json == "-" else Path(args.event_json).read_text(encoding="utf-8")
            result = append_event(args.ledger, json.loads(text))
            print(json.dumps({"status": result.status, "event_id": result.event_id}, sort_keys=True))
        else:
            print(json.dumps(summarize(args.ledger, args.issue_id), sort_keys=True, allow_nan=False))
    except (OSError, json.JSONDecodeError, LedgerValidationError) as exc:
        print(f"pipeline_issue_ledger: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
