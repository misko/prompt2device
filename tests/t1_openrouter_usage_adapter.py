#!/usr/bin/env python3
"""T1 controls for offline OpenRouter usage receipt normalization."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "pcb-design" / "scripts"))
from openrouter_usage_adapter import OpenRouterReceiptError, parse_response  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import check, eq, main, test  # noqa: E402


def receipt(**overrides):
    value = {
        "id": "gen-123",
        "model": "provider/model",
        "created": 1_700_000_000,
        "choices": [{"finish_reason": "stop", "message": {"content": "private"}}],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
            "cost": 0.0125,
            "prompt_tokens_details": {"cached_tokens": 30},
            "completion_tokens_details": {"reasoning_tokens": 7},
        },
        "authorization": "must never escape",
    }
    value.update(overrides)
    return value


def rejects(value, expected):
    try:
        parse_response(value)
    except OpenRouterReceiptError as exc:
        check(expected in str(exc), f"{exc!s} lacks {expected!r}")
    else:
        raise AssertionError("hostile receipt SHOULD HAVE FAILED")


@test("clean OpenRouter receipt retains only measured accounting fields")
def t_clean_receipt():
    result = parse_response(receipt())
    eq(set(result), {"response_id", "model", "usage", "provider_cost_usd", "status", "observed_at"})
    eq(result["response_id"], "gen-123")
    eq(result["status"], "PASS", "provider completion only")
    eq(result["observed_at"], "2023-11-14T22:13:20Z", "created is an observation")
    eq(result["provider_cost_usd"], 0.0125)
    eq(result["usage"], {
        "authority": "openrouter-reported", "metric": "provider_tokens",
        "input_tokens": 100, "cached_input_tokens": 30, "output_tokens": 20,
        "reasoning_tokens": 7, "total_tokens": 120,
    })
    check("authorization" not in result and "content" not in repr(result), "receipt data leaked")


@test("partial receipts preserve unknown telemetry and incomplete completion")
def t_missing_usage_and_verdict():
    result = parse_response(receipt(usage=None, created=None, choices=[]))
    eq(result["usage"], None)
    eq(result["provider_cost_usd"], None)
    eq(result["observed_at"], None)
    eq(result["status"], "INCOMPLETE")


@test("cache read token receipts map only an actually observed cache value")
def t_cache_read_tokens():
    value = receipt()
    value["usage"]["prompt_tokens_details"] = {"cache_read_tokens": 30}
    eq(parse_response(value)["usage"]["cached_input_tokens"], 30)


@test("length and provider error receipts never become engineering success")
def t_incomplete_and_error_statuses():
    eq(parse_response(receipt(choices=[{"finish_reason": "length"}]))["status"], "INCOMPLETE")
    eq(parse_response(receipt(choices=[{"finish_reason": "error", "error": {"code": 1}}]))["status"], "ERROR")
    eq(parse_response(receipt(error={"message": "provider failed"}))["status"], "ERROR")


@test("hostile counts costs types and response identities fail closed", kind="known_bad")
def t_hostile_receipts():
    rejects(receipt(id=None), "id: required")
    rejects(receipt(usage={"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 99}), "must equal input_tokens")
    rejects(receipt(usage={"prompt_tokens": 10, "prompt_tokens_details": {"cached_tokens": 11}}), "subset of input_tokens")
    rejects(receipt(usage={"cost": float("nan")}), "usage.cost")
    rejects(receipt(usage={"prompt_tokens": "100"}), "usage.prompt_tokens")
    rejects(receipt(created=True), "created")


if __name__ == "__main__":
    raise SystemExit(main())
