#!/usr/bin/env python3
"""Read-only exact-MPN discovery. Snapshot evidence is never sourcing admission."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


def discover(payload, mpn, need):
    rows = payload.get("components") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("unexpected jlcsearch response schema")
    matches = []
    for row in rows:
        # API field 'mfr' means manufacturer PART NUMBER, not manufacturer name.
        if row.get("mfr") != mpn:
            continue
        count = row.get("stock")
        count = count if type(count) is int and count >= 0 else None
        status = ("stock_unknown" if count is None else
                  "reported_out_of_stock" if count == 0 else
                  "reported_insufficient" if count < need else "reported_sufficient")
        matches.append({"mpn": mpn, "lcsc": row.get("lcsc"),
                        "package": row.get("package"), "manufacturer": None,
                        "stock_count": count, "status": status})
    return {"lookup_state": "exact_matches" if matches else "no_exact_match",
            "matches": matches, "returned_rows": len(rows)}


def public_evidence(html, mpn, expected_code=None):
    """Extract exact-object observations, never page-wide 'In Stock' text.

    Next.js transport is undocumented: changes fail closed to no exact evidence.
    Counts retain their original field names; overseas/presale is NOT PCBA stock.
    """
    chunks = []
    for match in re.finditer(r'self\.__next_f\.push\((\[.*?\])\)</script>', html, re.S):
        try:
            item = json.loads(match[1])
            if item[0] == 1 and isinstance(item[1], str):
                chunks.append(item[1])
        except (ValueError, TypeError, IndexError):
            continue
    text = "".join(chunks)
    decoder = json.JSONDecoder()
    evidence = []
    for match in re.finditer(r'"componentInfo":\s*(?=\{)', text):
        try:
            obj, _ = decoder.raw_decode(text, match.end())
        except ValueError:
            continue
        if obj.get("componentModelEn") != mpn or (expected_code and obj.get("componentCode") != expected_code):
            continue
        keys = ("componentModelEn", "componentBrandEn", "componentCode",
                "componentSpecificationEn", "stockCount", "overseasStockCount",
                "canPresaleNumber", "isBuyComponent", "noBuyReason")
        item = {key: obj[key] for key in keys if key in obj}
        if item not in evidence:
            evidence.append(item)
    return {"lookup_state": "exact_identity_observed" if evidence else "no_exact_evidence",
            "observations": evidence,
            "availability_verified": False,
            "limit": "Identity/raw fields only; interpret inventory pool and freshness separately."}


def fetch(url):
    request = Request(url, headers={"User-Agent": "vnext-stock-lookup/1.0", "Accept": "application/json,text/html"})
    with urlopen(request, timeout=15) as response:
        raw = response.read(4_000_001)
        if len(raw) > 4_000_000:
            raise ValueError("response exceeds 4 MB limit")
        return raw.decode("utf-8"), {
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "url": response.url, "sha256": hashlib.sha256(raw).hexdigest(),
            "http_date": response.headers.get("Date"),
            "http_age": response.headers.get("Age"),
        }


def lookup(mpn, need, jlc_url=None, getter=fetch):
    if not mpn.strip() or type(need) is not int or need <= 0:
        raise ValueError("MPN and positive build quantity required")
    url = "https://jlcsearch.tscircuit.com/api/search?" + urlencode({"q": mpn, "limit": 5})
    result = {"authority": "LOOKUP_EVIDENCE_ONLY", "mpn": mpn, "build_need": need,
              "inventory_updated_at": None, "source_kind": "aggregate_snapshot",
              "sourcing_guard": "provisional", "request_url": url}
    try:
        body, provenance = getter(url)
        result.update(discover(json.loads(body), mpn, need), provenance=provenance)
        result["raw_response"] = json.loads(body)
    except (OSError, ValueError, TimeoutError) as exc:
        result.update(lookup_state="lookup_failed", error=str(exc))
    if jlc_url:
        parsed = urlparse(jlc_url)
        if parsed.scheme != "https" or parsed.hostname != "jlcpcb.com" or not parsed.path.startswith("/partdetail/"):
            raise ValueError("use an observed https://jlcpcb.com/partdetail/ product URL")
        try:
            body, provenance = getter(jlc_url)
            code = parsed.path.rstrip("/").rsplit("/", 1)[-1]
            if not re.fullmatch(r"C\d+", code):
                raise ValueError("public URL must identify an exact JLCPCB C-code")
            result["public_jlcpcb"] = {**public_evidence(body, mpn, code), "provenance": provenance}
        except (OSError, ValueError, TimeoutError) as exc:
            result["public_jlcpcb"] = {"lookup_state": "lookup_failed", "error": str(exc)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mpn")
    parser.add_argument("--need", required=True, type=int)
    parser.add_argument("--jlc-url", help="Observed exact public product URL; optional verification evidence")
    parser.add_argument("--output", type=Path, help="Save new evidence JSON; refuses overwriting")
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error("output already exists; preserve prior observations")
    result = lookup(args.mpn, args.need, args.jlc_url)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        with args.output.open("x") as stream:
            stream.write(rendered + "\n")
    print(rendered)
    return 2 if result["lookup_state"] == "lookup_failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
