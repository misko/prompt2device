#!/usr/bin/env python3
"""Read-only, report-only jlcsearch discovery and selected-BOM screening.

The hosted catalog is a derivative of JLC's supply pool. Its search index may
omit out-of-stock parts. A result is never PCBA availability or allocation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://jlcsearch.tscircuit.com"
ENDPOINT = "/components/list.json"
SOURCE = "tscircuit/jlcsearch (JLC-derived catalog; same supply pool)"
TTL_SECONDS = 24 * 60 * 60
MAX_BYTES = 2_000_000
USER_AGENT = "CircuitsJlcsearchReport/1.0"


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def code_of(value):
    text = str(value).strip().upper()
    return text if re.fullmatch(r"C[1-9][0-9]*", text) else None


def circuit_identities(path):
    """Return refdes -> (selected code, exact MPN) from source components."""
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("circuit JSON must be a record list")
    identities = {}
    for record in records:
        if not isinstance(record, dict) or record.get("type") != "source_component":
            continue
        mpn = record.get("manufacturer_part_number")
        ref = record.get("name")
        supplier = record.get("supplier_part_numbers") or {}
        codes = supplier.get("jlcpcb", []) if isinstance(supplier, dict) else []
        if not isinstance(codes, list):
            continue
        if isinstance(ref, str) and isinstance(mpn, str) and mpn.strip() and len(codes) == 1:
            code = code_of(codes[0])
            if code:
                identities.setdefault(ref, set()).add((code, mpn.strip()))
    return identities


def parse_components(raw):
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("components"), list):
        raise ValueError("response lacks components array")
    if len(data["components"]) > 1000:
        raise ValueError("response exceeds component limit")
    if any(not isinstance(part, dict) for part in data["components"]):
        raise ValueError("component is not an object")
    return data["components"]


class Client:
    def __init__(self, cache_dir, max_requests, timeout):
        self.cache_dir = cache_dir
        self.max_requests = max_requests
        self.timeout = timeout
        self.requests = 0
        self.blocked = None

    def get(self, query):
        url = BASE + ENDPOINT + "?" + urllib.parse.urlencode({"search": query})
        key = sha(url.encode())
        cache = self.cache_dir / (key + ".json")
        if cache.is_file():
            try:
                saved = json.loads(cache.read_text(encoding="utf-8"))
                parsed_at = datetime.fromisoformat(saved["fetched_at"])
                if parsed_at.tzinfo is None or parsed_at.utcoffset().total_seconds() != 0:
                    raise ValueError("cache timestamp is not UTC")
                age = (datetime.now(timezone.utc) - parsed_at).total_seconds()
                raw = bytes.fromhex(saved["body_hex"])
                if (saved["url"] == url and 0 <= age <= TTL_SECONDS
                        and sha(raw) == saved["sha256"]):
                    return parse_components(raw), self._proof(url, raw, saved["fetched_at"], True, cache)
            except (ValueError, KeyError, TypeError, OSError):
                pass
        if self.blocked:
            raise RuntimeError("request skipped after " + self.blocked)
        if self.requests >= self.max_requests:
            raise RuntimeError("request budget exhausted")
        self.requests += 1
        if self.requests > 1:
            time.sleep(0.2)
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                raw = response.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise ValueError("response exceeds byte limit")
                components = parse_components(raw)
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403, 429):
                self.blocked = f"HTTP {exc.code}"
            raise RuntimeError(f"HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            self.blocked = "transport failure"
            raise RuntimeError(f"transport failure: {exc}") from exc
        fetched = now()
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps({"url": url, "fetched_at": fetched,
            "sha256": sha(raw), "body_hex": raw.hex()}), encoding="utf-8")
        return components, self._proof(url, raw, fetched, False, cache)

    @staticmethod
    def _proof(url, raw, fetched, cached, cache):
        return {"provider": SOURCE, "url": url, "http_status": 200,
                "fetched_at": fetched, "cache_hit": cached,
                "raw_response_sha256": sha(raw), "raw_response_bytes": len(raw),
                "raw_cache_path": str(cache),
                "upstream_stock_timestamp": None}


def screen(request_path, circuit_path, client):
    request_raw = request_path.read_bytes()
    request = json.loads(request_raw)
    if request.get("kind") not in ("jlc-pcba-availability-request-v1",
                                     "jlc-pcba-availability-request-v2"):
        raise ValueError("expected a JLC PCBA availability request")
    rows = request.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("request has no BOM rows")
    identities = circuit_identities(circuit_path)
    result = []
    seen_codes = set()
    seen_refs = set()
    for row in rows:
        code = code_of(row.get("requested_lcsc")) if isinstance(row, dict) else None
        refs = row.get("designators") if isinstance(row, dict) else None
        qty = row.get("required_qty") if isinstance(row, dict) else None
        ref_identities = [identities.get(ref, set()) for ref in refs] if isinstance(refs, list) else []
        valid_refs = (bool(ref_identities) and all(isinstance(ref, str) and ref and
                      len(found) == 1 for ref, found in zip(refs, ref_identities))
                      and len(refs) == len(set(refs)) and not seen_refs.intersection(refs))
        pairs = {next(iter(found)) for found in ref_identities} if valid_refs else set()
        valid = (code and code not in seen_codes and valid_refs and len(pairs) == 1
                 and next(iter(pairs))[0] == code and isinstance(qty, int)
                 and not isinstance(qty, bool) and qty > 0
                 and isinstance(row.get("per_board_qty"), int)
                 and row["per_board_qty"] == len(refs)
                 and isinstance(request.get("build_quantity"), int)
                 and request["build_quantity"] > 0
                 and qty == len(refs) * request["build_quantity"])
        if code:
            seen_codes.add(code)
        if isinstance(refs, list):
            seen_refs.update(ref for ref in refs if isinstance(ref, str))
        mpn = next(iter(pairs))[1] if valid else None
        item = {"requested_lcsc": code, "selected_mpn": mpn,
                "designators": row.get("designators") if isinstance(row, dict) else None,
                "required_qty": qty, "status": "UNKNOWN", "observed_stock": None,
                "stock_vs_required": "UNKNOWN", "evidence": None}
        if not valid:
            item["reason"] = "invalid/duplicate request row or source refdes/code/MPN/quantity mismatch"
        else:
            try:
                parts, proof = client.get(code)
                exact = [part for part in parts if code_of("C" + str(part.get("lcsc", ""))) == code]
                matched = [part for part in exact if part.get("mfr") == item["selected_mpn"]]
                item["evidence"] = proof
                if len(matched) != 1:
                    item["reason"] = ("selected code absent from search index" if not exact
                                      else "selected MPN mismatch or ambiguous catalog result")
                else:
                    stock = matched[0].get("stock")
                    if isinstance(stock, int) and not isinstance(stock, bool) and stock >= 0:
                        item["status"] = "CATALOG_OBSERVED"
                        item["observed_stock"] = stock
                        item["stock_vs_required"] = "MEETS" if stock >= qty else "BELOW"
                        item["catalog_part"] = matched[0]
                        item["reason"] = "catalog observation only; PCBA fulfillment unverified"
                    else:
                        item["reason"] = "matched catalog record lacks valid stock"
            except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
                item["reason"] = str(exc)
                item["evidence"] = {"provider": SOURCE,
                    "url": BASE + ENDPOINT + "?" + urllib.parse.urlencode({"search": code}),
                    "fetched_at": now(), "error": str(exc)}
        result.append(item)
    observed = sum(row["status"] == "CATALOG_OBSERVED" for row in result)
    return {"kind": "jlcsearch-screen-report-v1", "report_only": True,
            "provider": SOURCE, "generated_at": now(),
            "request": {"path": str(request_path), "sha256": sha(request_raw)},
            "circuit": {"path": str(circuit_path), "sha256": sha(circuit_path.read_bytes())},
            "coverage": {"total": len(result), "catalog_observed": observed,
                         "unknown": len(result) - observed},
            "network_requests": client.requests, "rows": result}


def discover(query, client):
    try:
        components, proof = client.get(query)
        return {"kind": "jlcsearch-discovery-report-v1", "report_only": True,
                "query": query, "generated_at": now(),
                "status": "CANDIDATES_OBSERVED" if components else "NOT_OBSERVED",
                "evidence": proof, "candidates": components,
                "warning": "Candidates require exact electrical, package and MPN review."}
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return {"kind": "jlcsearch-discovery-report-v1", "report_only": True,
                "query": query, "generated_at": now(), "status": "UNKNOWN",
                "reason": str(exc), "candidates": []}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    discovery = sub.add_parser("discover", help="report-only candidate discovery")
    discovery.add_argument("query")
    screening = sub.add_parser("screen", help="report-only selected BOM screening")
    screening.add_argument("request", type=Path)
    screening.add_argument("--circuit-json", type=Path, required=True)
    for command in (discovery, screening):
        command.add_argument("--out", type=Path, required=True)
        command.add_argument("--cache-dir", type=Path,
                             default=Path.home() / ".cache/circuits/jlcsearch")
        command.add_argument("--max-requests", type=int, default=100)
        command.add_argument("--timeout", type=float, default=8.0)
    args = parser.parse_args(argv)
    if not 0 <= args.max_requests <= 100 or not 0 < args.timeout <= 30:
        parser.error("max-requests must be 0..100 and timeout must be >0..30 seconds")
    client = Client(args.cache_dir, args.max_requests, args.timeout)
    try:
        report = (discover(args.query, client) if args.command == "discover" else
                  screen(args.request, args.circuit_json, client))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.command == "screen":
        print(f"JLCSEARCH REPORT ONLY: {report['coverage']['catalog_observed']}/"
              f"{report['coverage']['total']} catalog observed; "
              f"{report['coverage']['unknown']} unknown; {client.requests} network requests")
    else:
        print(f"JLCSEARCH REPORT ONLY: {report['status']}; "
              f"{len(report['candidates'])} candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
