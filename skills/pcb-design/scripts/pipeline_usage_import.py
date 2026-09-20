#!/usr/bin/env python3
"""Offline, explicitly attributed usage import. No provider calls or transcripts out.

Schema-1 manifest: provider_scope, expected_session_ids, sources. Each source
has format and path (relative to the manifest). codex-rollout-v1 additionally
has assignments mapping exact turn IDs to {issue_id, attempt_id}; an
openrouter-response-v1 source instead has issue_id and attempt_id directly.
Expected session IDs describe declared coverage, never proof of all descendants.
Only per-response Codex token_usage_record increments are imported. Other
records, including cumulative token_count, are not usage. Model/effort come
only from the same turn's explicit context. Missing timings remain unknown.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from pipeline_issue_ledger import (append_events, normalize_event, equivalent_event,
                                  validate_event_batch, validate_response_id)


class ImportValidationError(ValueError):
    pass


def exact(value, fields, where):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ImportValidationError(f"{where}: expected exact fields {sorted(fields)}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ImportValidationError("duplicate JSON object key")
        result[key] = value
    return result


def load_json(text):
    return json.loads(text, object_pairs_hook=unique_object)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def usage_event(record, assignment, scope):
    """Stable response identity across files and imports; no path-dependent key."""
    response = record["response_id"]
    run_id = "usage-" + digest([scope, response])
    # Hash only allowlisted normalized observation, never prompt/message bytes.
    event = {"schema": 2, "event_id": run_id, "event_type": "USAGE",
             "response_id": response, "provider_scope": scope,
             "issue_id": assignment["issue_id"], "attempt_id": assignment["attempt_id"],
             "run_id": run_id, "stage_id": None,
             "model": record.get("model"), "effort": record.get("effort"),
             "status": record["status"], "started_at": None, "finished_at": None,
             "elapsed_s": None, "observed_at": record.get("observed_at"),
             "provenance": {"observation_sha256": digest(
                 {k: v for k, v in record.items() if k != "observed_at"})},
             "token_usage": record["usage"], "provider_cost_usd": record["provider_cost_usd"]}
    return normalize_event(event)


def codex_source(path, assignments, scope):
    if not isinstance(assignments, dict):
        raise ImportValidationError("assignments must map exact turn IDs")
    for turn_id, assignment in assignments.items():
        if not isinstance(turn_id, str) or not turn_id:
            raise ImportValidationError("assignment turn IDs must be nonempty strings")
        exact(assignment, {"issue_id", "attempt_id"}, "assignment")
    contexts, events, seen_turns = {}, [], set()
    report = {"format": "codex-rollout-v1", "session_id": None,
              "usage_records_seen": 0, "selected_records": 0,
              "unassigned_records": 0, "ignored_cumulative_records": 0,
              "missing_turn_context": 0}
    source_hash = hashlib.sha256()
    with path.open("rb") as stream:
        for line_number, line in enumerate(stream, 1):
            source_hash.update(line)
            if not line.endswith(b"\n"):
                raise ImportValidationError(f"incomplete source JSONL line {line_number}; use a stable snapshot")
            try:
                row = load_json(line)
            except (ValueError, UnicodeError) as exc:
                raise ImportValidationError(f"invalid source JSONL line {line_number}") from exc
            if not isinstance(row, dict):
                raise ImportValidationError(f"source line {line_number} must be an object")
            kind, payload = row.get("type"), row.get("payload")
            if kind not in {"session_meta", "turn_context", "token_usage_record", "event_msg"}:
                continue
            if not isinstance(payload, dict):
                raise ImportValidationError(f"{kind}: payload must be an object")
            if kind == "session_meta":
                session = payload.get("id")
                if not isinstance(session, str) or not session:
                    raise ImportValidationError("session_meta requires id")
                if report["session_id"] not in (None, session):
                    raise ImportValidationError("source changes session identity")
                report["session_id"] = session
            elif kind == "turn_context":
                turn = payload.get("turn_id")
                if isinstance(turn, str):
                    contexts[turn] = (payload.get("model"), payload.get("effort"))
            elif kind == "event_msg":
                if payload.get("type") == "token_count":
                    report["ignored_cumulative_records"] += 1
            else:
                report["usage_records_seen"] += 1
                turn = payload.get("turn_id")
                if not isinstance(turn, str) or not turn:
                    raise ImportValidationError("token_usage_record requires turn_id")
                seen_turns.add(turn)
                if turn not in assignments:
                    report["unassigned_records"] += 1
                    continue
                response = payload.get("response_id")
                if not isinstance(response, str) or not response:
                    raise ImportValidationError("token_usage_record requires response_id")
                raw_usage = payload.get("usage")
                if raw_usage is not None and not isinstance(raw_usage, dict):
                    raise ImportValidationError("per-response usage must be an object or null")
                usage = None if raw_usage is None else {
                    "authority": "codex-token-usage-record-v1", "metric": "provider_tokens",
                    "input_tokens": raw_usage.get("input_tokens"),
                    "cached_input_tokens": raw_usage.get("cached_input_tokens"),
                    "output_tokens": raw_usage.get("output_tokens"),
                    "reasoning_tokens": raw_usage.get("reasoning_output_tokens"),
                    "total_tokens": raw_usage.get("total_tokens")}
                if turn not in contexts:
                    report["missing_turn_context"] += 1
                model, effort = contexts.get(turn, (None, None))
                record = {"response_id": response, "model": model, "effort": effort,
                          "usage": usage, "provider_cost_usd": None,
                          "status": "INCOMPLETE", "observed_at": row.get("timestamp")}
                events.append(usage_event(record, assignments[turn], scope))
                report["selected_records"] += 1
    if report["session_id"] is None:
        raise ImportValidationError("Codex source lacks session_meta identity")
    report["unmatched_assignment_turns"] = sorted(set(assignments) - seen_turns)
    report["source_sha256"] = source_hash.hexdigest()
    return events, report


def prepare_import(manifest_path):
    manifest_path = Path(manifest_path)
    manifest = load_json(manifest_path.read_text())
    exact(manifest, {"schema", "provider_scope", "expected_session_ids", "sources"}, "manifest")
    if type(manifest["schema"]) is not int or manifest["schema"] != 1:
        raise ImportValidationError("manifest requires schema 1")
    scope = manifest["provider_scope"]
    if not isinstance(scope, str) or not scope:
        raise ImportValidationError("provider_scope must be a stable nonsecret account/machine identifier")
    validate_response_id(scope + "/openrouter")
    expected = manifest["expected_session_ids"]
    if not isinstance(expected, list) or any(not isinstance(x, str) or not x for x in expected) or len(set(expected)) != len(expected):
        raise ImportValidationError("expected_session_ids must be unique nonempty strings")
    if not isinstance(manifest["sources"], list) or not manifest["sources"]:
        raise ImportValidationError("sources must be a nonempty list")
    events, reports = [], []
    for source in manifest["sources"]:
        if not isinstance(source, dict):
            raise ImportValidationError("source must be an object")
        kind = source.get("format")
        if kind == "codex-rollout-v1":
            exact(source, {"format", "path", "assignments"}, "Codex source")
        elif kind == "openrouter-response-v1":
            exact(source, {"format", "path", "issue_id", "attempt_id"}, "OpenRouter source")
        else:
            raise ImportValidationError("unsupported source format")
        if not isinstance(source["path"], str) or not source["path"]:
            raise ImportValidationError("source path must be nonempty")
        path = Path(source["path"])
        path = path if path.is_absolute() else manifest_path.parent / path
        if kind == "codex-rollout-v1":
            selected, report = codex_source(path, source["assignments"], scope + "/codex")
        else:
            from openrouter_usage_adapter import parse_response
            content = path.read_bytes()
            record = parse_response(load_json(content))
            selected = [usage_event(record, source, scope + "/openrouter")]
            report = {"format": kind, "source_sha256": hashlib.sha256(content).hexdigest(),
                      "selected_records": 1}
        events.extend(selected)
        reports.append(report)
    observed = {r["session_id"] for r in reports if r.get("session_id")}
    missing = sorted(set(expected) - observed)
    unassigned = sum(r.get("unassigned_records", 0) for r in reports)
    unmatched = sum(len(r.get("unmatched_assignment_turns", [])) for r in reports)
    report = {"schema": 1, "authority": "ACCOUNTING_ONLY", "sources": reports,
              "selected_records": len(events), "unassigned_records": unassigned,
              "missing_expected_sessions": missing,
              "unexpected_sessions": sorted(observed - set(expected)),
              "all_descendants_verified": False,
              "coverage": "PARTIAL" if missing or unassigned or unmatched or observed - set(expected) else "DECLARED_SOURCES_COMPLETE"}
    return events, report


def import_usage(manifest_path, ledger_path, *, dry_run=False, require_complete=False):
    events, report = prepare_import(manifest_path)
    if require_complete and report["coverage"] != "DECLARED_SOURCES_COMPLETE":
        raise ImportValidationError("declared source coverage is partial; ledger unchanged")
    # Prevalidate duplicates and attribution even in dry-run, without touching
    # the destination ledger. Commit uses one locked atomic batch.
    unique = {}
    for event in events:
        key = (event["provider_scope"], event["response_id"])
        if key in unique and not equivalent_event(unique[key], event):
            raise ImportValidationError("conflicting provider response observations")
        unique.setdefault(key, event)
    validate_event_batch(list(unique.values()))
    report["unique_responses"] = len(unique)
    report["within_import_duplicates"] = len(events) - len(unique)
    report["dry_run"] = dry_run
    report["destination_checked"] = not dry_run
    if not dry_run:
        results = append_events(ledger_path, list(unique.values()))
        report["appended"] = sum(r.status == "APPENDED" for r in results)
        report["already_recorded"] = sum(r.status == "DUPLICATE" for r in results)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = import_usage(args.manifest, args.ledger, dry_run=args.dry_run,
                              require_complete=args.require_complete)
        print(json.dumps(report, sort_keys=True, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        # Parser exceptions never include response content or source lines.
        print(f"usage import refused: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
