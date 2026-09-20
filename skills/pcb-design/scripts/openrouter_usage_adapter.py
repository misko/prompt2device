#!/usr/bin/env python3
"""Normalize saved OpenRouter response receipts for usage accounting only.

The adapter is deliberately offline: it accepts a decoded response mapping and
returns only provider identity, completion state, observation time, cost, and
token telemetry.  It neither reads receipt files nor exposes response content.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any, Mapping

from pipeline_issue_ledger import LedgerValidationError, validate_response_id, normalize_usage


class OpenRouterReceiptError(ValueError):
    """A saved provider receipt cannot be used as accounting evidence."""


def _fail(message: str) -> None:
    raise OpenRouterReceiptError(message)


def _nonnegative_number(value: Any, where: str) -> float:
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or
            not math.isfinite(value) or value < 0):
        _fail(f"{where}: expected a non-negative finite number")
    return float(value)


def _token(value: Any, where: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail(f"{where}: expected null or a non-negative integer")
    return value


def _details(value: Any, where: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        _fail(f"{where}: expected a mapping when present")
    return value


def _cached_tokens(details: Mapping[str, Any]) -> int | None:
    cached_seen = "cached_tokens" in details
    read_seen = "cache_read_tokens" in details
    cached = _token(details.get("cached_tokens"), "usage.prompt_tokens_details.cached_tokens")
    read = _token(details.get("cache_read_tokens"), "usage.prompt_tokens_details.cache_read_tokens")
    if cached_seen and read_seen and cached is not None and read is not None and cached != read:
        _fail("usage prompt cached token fields disagree")
    # Accept either explicitly supplied spelling; never infer a missing count.
    return cached if cached is not None else read


def _normalize_usage(value: Any) -> tuple[dict[str, Any] | None, float | None]:
    if value is None:
        return None, None
    if not isinstance(value, Mapping):
        _fail("usage: expected a mapping or null")
    prompt_details = _details(value.get("prompt_tokens_details"), "usage.prompt_tokens_details")
    completion_details = _details(value.get("completion_tokens_details"), "usage.completion_tokens_details")
    candidate = {
        "authority": "openrouter-reported",
        "metric": "provider_tokens",
        "input_tokens": _token(value.get("prompt_tokens"), "usage.prompt_tokens"),
        "cached_input_tokens": _cached_tokens(prompt_details),
        "output_tokens": _token(value.get("completion_tokens"), "usage.completion_tokens"),
        "reasoning_tokens": _token(completion_details.get("reasoning_tokens"),
                                   "usage.completion_tokens_details.reasoning_tokens"),
        "total_tokens": _token(value.get("total_tokens"), "usage.total_tokens"),
    }
    try:
        normalized = normalize_usage(candidate)
    except LedgerValidationError as exc:
        raise OpenRouterReceiptError(str(exc)) from exc
    cost = None
    if "cost" in value and value["cost"] is not None:
        cost = _nonnegative_number(value["cost"], "usage.cost")
    return normalized, cost


def _observed_at(value: Any) -> str | None:
    if value is None:
        return None
    timestamp = _nonnegative_number(value, "created")
    try:
        observed = datetime.fromtimestamp(timestamp, timezone.utc)
    except (OverflowError, OSError, ValueError) as exc:
        raise OpenRouterReceiptError("created: unsupported Unix timestamp") from exc
    if observed.microsecond:
        return observed.isoformat(timespec="microseconds").replace("+00:00", "Z")
    return observed.isoformat(timespec="seconds").replace("+00:00", "Z")


def _status(value: Mapping[str, Any]) -> str:
    if value.get("error") is not None:
        return "ERROR"
    choices = value.get("choices")
    if not isinstance(choices, list) or not choices:
        return "INCOMPLETE"
    complete = True
    for choice in choices:
        if not isinstance(choice, Mapping):
            return "INCOMPLETE"
        if choice.get("error") is not None or choice.get("finish_reason") == "error":
            return "ERROR"
        if choice.get("finish_reason") != "stop":
            complete = False
    return "PASS" if complete else "INCOMPLETE"


def parse_response(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return a closed, content-free accounting view of one saved receipt.

    A receipt must carry an OpenRouter response ID so a ledger consumer can
    deduplicate it.  Missing usage and creation time remain unknown; no token
    totals, cache amounts, cost, duration, or completion verdict is inferred.
    """
    if not isinstance(value, Mapping):
        _fail("response: expected a mapping")
    try:
        response_id = validate_response_id(value.get("id"))
    except LedgerValidationError as exc:
        raise OpenRouterReceiptError("id: required safe response identifier") from exc
    model = value.get("model")
    if model is not None and (not isinstance(model, str) or not model.strip() or len(model) > 200):
        _fail("model: expected null or a non-empty string of at most 200 characters")
    usage, cost = _normalize_usage(value.get("usage"))
    return {
        "response_id": response_id,
        "model": model,
        "usage": usage,
        "provider_cost_usd": cost,
        "status": _status(value),
        "observed_at": _observed_at(value.get("created")),
    }
