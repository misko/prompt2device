#!/usr/bin/env python3
"""Compose exact-code manufacturing readiness into one hash-bound receipt.

Selection mode runs before part freeze and proves that every source component
has exactly one JLC code or an explicit unassembled/manual disposition, that
every declared MPN resolves to one exact dossier, and that the existing part-
facts and source-value gates pass. Prelayout mode additionally requires either
a quantity-expanded JLCPCB PCBA receipt or an explicitly bounded public-catalog
design screen. Order mode requires a fresh ALLOCATED receipt and quote for the
exact release BOM instead of treating catalog stock, raw MOQ, or an earlier
AVAILABLE result as permanent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml
from stock_surplus_policy import parse_policy, surplus_for


SCRIPTS = Path(__file__).resolve().parent
PCB_PIPELINE = SCRIPTS.parents[1] / "pcb-design" / "scripts"
if str(PCB_PIPELINE) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(PCB_PIPELINE))
KICAD_SCRIPTS = SCRIPTS.parents[1] / "kicad-pcb" / "scripts"
if str(KICAD_SCRIPTS) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(KICAD_SCRIPTS))

from pipeline_identity import TypedIdentityInput, subject_identity  # noqa: E402
from pipeline_stage_evidence import (  # noqa: E402
    require_safe_output_layout, write_shadow_stage_result,
)
from process_runner import run_bounded  # noqa: E402
from jlc_pcba_availability import verify_receipt  # noqa: E402
from critical_part_selection_admission import release_selection_errors  # noqa: E402


def _record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": str(path.resolve()),
            "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def _run(label: str, command: list[str], cwd: Path) -> dict[str, Any]:
    started = time.monotonic()
    completed = run_bounded(
        command, cwd=cwd, timeout_s=900, heartbeat_s=10,
        label=f"manufacturing-readiness-{label}", echo=False)
    status = "PASS" if completed.returncode == 0 else (
        "FAIL" if completed.returncode == 1 else "INCOMPLETE")
    return {"status": status, "detail": f"exit {completed.returncode}",
            "elapsed_s": round(time.monotonic() - started, 6),
            "output": completed.output[-8000:]}


def _pcba_check(receipt: Path | None, *, phase: str,
                bom: Path | None = None,
                predicate: str = "availability") -> dict[str, Any]:
    if receipt is None:
        return {"status": "INCOMPLETE",
                "detail": f"{phase} requires --pcba-receipt",
                "output": "catalog stock is not JLCPCB assembly authority"}
    if bom is None:
        return {
            "status": "INCOMPLETE",
            "detail": f"{phase} receipt verification requires the current circuit/BOM",
            "output": "a PCBA receipt may not be verified without its current subject",
        }
    try:
        receipt_identity = _record(receipt)
    except OSError as exc:
        return {"status": "INCOMPLETE", "detail": f"receipt unreadable: {exc}",
                "output": ""}
    try:
        valid, failures, data = verify_receipt(
            receipt, bom=bom, required_phase=phase)
    except Exception as exc:
        return {"status": "INCOMPLETE", "detail": f"receipt unreadable: {exc}",
                "output": ""}
    checked = {
        "status": "PASS" if valid else "FAIL",
        "detail": "JLCPCB PCBA receipt verified" if valid else
                  "JLCPCB PCBA receipt rejected",
        "output": "\n".join(failures),
    }
    if not valid:
        return checked
    if predicate == "availability":
        verdict = data.get("availability_verdict", data.get("verdict"))
    elif predicate == "economics":
        verdict = data.get("economics_verdict")
        if verdict is None:
            checked.update(
                status="INCOMPLETE",
                detail="legacy PCBA receipt has no procurement economics",
                output="schema-v2 MOQ/cost evidence and policy are required")
            return checked
    else:
        return {"status": "INCOMPLETE", "detail": f"unknown predicate {predicate}",
                "output": ""}
    try:
        if _record(receipt) != receipt_identity:
            return {
                "status": "FAIL",
                "detail": "JLCPCB PCBA receipt changed during verification",
                "output": "the verified receipt bytes were replaced before consumption",
            }
    except OSError as exc:
        return {
            "status": "FAIL",
            "detail": "JLCPCB PCBA receipt changed during verification",
            "output": f"receipt disappeared before consumption: {exc}",
        }
    if verdict != "ACCEPTED":
        checked["status"] = "FAIL" if verdict == "REJECTED" else "INCOMPLETE"
        checked["detail"] = f"JLCPCB PCBA {predicate} verdict {verdict}"
    else:
        checked["detail"] = f"JLCPCB PCBA {predicate} accepted"
    return checked


def _distributor_prelayout_rows(project: Path, request: dict[str, Any],
                                policy_path: Path, quotes_path: Path,
                                exact_rows: list[dict[str, Any]], *,
                                allow_blocked_sourcing: bool = False) -> tuple[dict, dict]:
    """Grade explicitly approved exact-part observations, not JLC allocation.

    Observations are human-read public product pages. Hashes preserve what was
    recorded; they do not independently prove the observer copied a page
    correctly or that stock remains reserved. No procurement is authorized.
    """
    project = project.resolve()

    def local(path: Path) -> Path:
        absolute = Path(os.path.abspath(path if path.is_absolute() else project / path))
        try:
            relative = absolute.relative_to(project)
        except ValueError as exc:
            raise ValueError('distributor authority escapes project') from exc
        current = project
        for part in relative.parts:
            current /= part
            if current.is_symlink():
                raise ValueError('symlink distributor authority')
        if not absolute.is_file():
            raise ValueError(f'missing distributor authority: {absolute}')
        return absolute

    # CLI paths follow the other grade arguments (cwd-relative); references
    # inside the policy remain project-relative. Keep symlink checks intact.
    policy_path = local(Path(os.path.abspath(policy_path)))
    quotes_path = local(Path(os.path.abspath(quotes_path)))
    assembly_path = local(Path("03_src/rules/assembly.yaml"))
    policy = yaml.safe_load(policy_path.read_text())
    quotes = yaml.safe_load(quotes_path.read_text())
    assembly = yaml.safe_load(assembly_path.read_text()) or {}
    surplus, overrides = parse_policy(assembly, project)
    if (not isinstance(policy, dict) or policy.get('schema') != 1 or
            policy.get('scope') != 'prelayout-only' or
            policy.get('order_authorized') is not False):
        raise ValueError('distributor policy must be schema1 prelayout-only, no order authority')
    directive = policy.get('directive')
    if not isinstance(directive, str) or not directive.strip():
        raise ValueError('distributor policy has no explicit directive')
    brief = local(Path(policy.get('brief') or ''))
    decision = local(Path(policy.get('decision') or ''))
    decision_text = decision.read_text()
    if directive not in brief.read_text() or directive not in decision_text:
        raise ValueError('distributor directive is absent from brief/decision')
    if not all(term in decision_text for term in ('public-catalog', 'pre-layout', 'DO-NOT-ORDER')):
        raise ValueError('distributor decision lacks design-only boundary')
    rules = policy.get('rows')
    observations = quotes.get('quotes') if isinstance(quotes, dict) else None
    if not isinstance(rules, list) or not rules or not isinstance(observations, list):
        raise ValueError('distributor policy/quote denominator is empty or malformed')
    wanted = {row['requested_lcsc']: row for row in request.get('rows') or []}
    approved = {}
    for row in rules:
        code = row.get('lcsc')
        if not re.fullmatch(r'C\d+', str(code)) or code not in wanted or code in approved:
            raise ValueError('unknown or duplicate distributor policy code')
        identity_keys = ('mpn', 'manufacturer', 'footprint', 'distributor', 'url', 'packaging')
        if any(not isinstance(row.get(key), str) or not row[key].strip() for key in identity_keys):
            raise ValueError(f'{code}: incomplete distributor identity')
        refs = row.get('designators')
        if (not isinstance(refs, list) or not refs or len(set(refs)) != len(refs) or
                sorted(refs) != sorted(wanted[code]['designators'])):
            raise ValueError(f'{code}: distributor policy designators differ from request')
        source = [item for item in exact_rows if code in item.get('jlc_codes', [])]
        if sorted(item['ref'] for item in source) != sorted(refs):
            raise ValueError(f'{code}: distributor source population differs')
        for item in source:
            dossier = yaml.safe_load(local(Path(item.get('dossier') or '')).read_text())
            if (item.get('mpn') != row['mpn'] or item.get('footprint') != row['footprint'] or
                    any(dossier.get(key) != row[key] for key in ('mpn', 'manufacturer', 'footprint'))):
                raise ValueError(f'{code}: distributor identity differs from exact source/dossier')
        url = urlsplit(row['url'])
        # Each admitted provider has a narrow, tested public product-page
        # shape. Exact row/quote equality below binds the observed page.
        provider_paths = {
            'digikey': ('www.digikey.com', '/en/products/detail/', 'product_page'),
            'mouser': ('www.mouser.com', '/en/ProductDetail/', 'product_page'),
            'trustedparts': ('www.trustedparts.com', '/en/manufacturers/',
                             'authorized_inventory_aggregator'),
        }
        provider = provider_paths.get(row['distributor'])
        if (provider is None or url.scheme != 'https' or
                url.netloc != provider[0] or not url.path.startswith(provider[1]) or
                url.path == provider[1] or url.query or url.fragment):
            raise ValueError(f'{code}: unsupported distributor product URL')
        found = [q for q in observations if isinstance(q, dict) and
                 q.get('mpn') == row['mpn'] and q.get('distributor') == row['distributor']]
        if len(found) != 1:
            raise ValueError(f'{code}: missing or ambiguous exact distributor quote')
        quote = found[0]
        if (any(quote.get(key) != row[key] for key in
                ('mpn', 'manufacturer', 'distributor', 'url', 'packaging')) or
                quote.get('source') != provider[2] or
                quote.get('lifecycle') != 'Active'):
            raise ValueError(f'{code}: non-product-page or mismatched distributor observation')
        if provider[2] == 'product_page':
            if not isinstance(quote.get('dpn'), str) or not quote['dpn'].strip():
                raise ValueError(f'{code}: product-page observation lacks distributor part number')
        elif (quote.get('authority') != 'ECIA' or
              quote.get('authorized_only') is not True or
              quote.get('aggregation_scope') != 'authorized-distributors-only'):
            raise ValueError(f'{code}: aggregator does not prove ECIA authorized-only inventory')
        try:
            checked = datetime.fromisoformat(str(quote.get('checked_at') or '').replace('Z', '+00:00'))
            if checked.tzinfo is None:
                raise ValueError('timezone missing')
            age = datetime.now(timezone.utc) - checked.astimezone(timezone.utc)
            if age < timedelta(0) or age > timedelta(hours=24):
                raise ValueError('observation outside24h window')
        except ValueError as exc:
            raise ValueError(f'{code}: invalid distributor observation time: {exc}') from exc
        quantities = [quote.get(key) for key in ('stock', 'min', 'mult')]
        if (type(quantities[0]) is not int or quantities[0] < 0 or
                any(type(value) is not int or value <= 0 for value in quantities[1:])):
            raise ValueError(f'{code}: stock must be a nonnegative integer and minimum/multiple must be positive integers')
        stock, minimum, multiple = quantities
        required = wanted[code].get('required_qty')
        if type(required) is not int or required <= 0:
            raise ValueError(f'{code}: invalid requested quantity')
        applied_surplus = surplus_for(surplus, overrides, code, row['mpn'], refs)
        public_threshold = required + applied_surplus
        purchase_quantity = ((max(public_threshold, minimum) + multiple - 1) // multiple) * multiple
        blocked = stock < purchase_quantity
        if blocked and not allow_blocked_sourcing:
            raise ValueError(
                f'{code}: distributor stock below build plus configured surplus quantity')
        approved[code] = dict(stock=stock, required_qty=required,
                              public_stock_surplus=applied_surplus,
                              public_stock_threshold=public_threshold,
                              purchase_quantity=purchase_quantity, mpn=row['mpn'],
                              distributor=row['distributor'], url=row['url'],
                              checked_at=quote['checked_at'], order_authorized=False,
                              sourcing_state=('BLOCKED-SOURCING' if blocked else 'AVAILABLE'))
    inputs = {name: _record(path) for name, path in (
        ('distributor_policy', policy_path), ('distributor_quotes', quotes_path),
        ('distributor_assembly', assembly_path),
        ('distributor_decision', decision), ('distributor_brief', brief))}
    return approved, inputs


def _catalog_prelayout_check(request_path: Path | None,
                             evidence_path: Path | None,
                             decision_path: Path | None, *,
                             distributors: dict | None = None,
                             allow_blocked_sourcing: bool = False,
                             expected_min_surplus: int | None = None,
                             expected_overrides: dict | None = None,
                             exact_rows: list[dict[str, Any]] | None = None,
                             selection_snapshot: dict | None = None,
                             project: Path | None = None) -> dict[str, Any]:
    """Verify a user-accepted public-catalog pre-layout negative filter.

    This deliberately cannot be used for the order phase.  It proves only
    exact-code catalog coverage for the requested build quantity and binds the
    explicit project decision that defers allocation/economics to the uploader.
    """
    if not all((request_path, evidence_path, decision_path)):
        return {"status": "INCOMPLETE",
                "detail": "catalog prelayout requires request, evidence, and decision",
                "output": "public catalog evidence is not order allocation"}
    try:
        request = json.loads(request_path.read_text(encoding="utf-8-sig"))
        evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
        decision = decision_path.read_text(encoding="utf-8-sig")
    except Exception as exc:
        return {"status": "INCOMPLETE", "detail": f"catalog evidence unreadable: {exc}",
                "output": ""}
    failures = []
    distributors = distributors or {}
    expected_overrides = expected_overrides or {}
    # Preserve and grade the original failed JLC rows. Only an independently
    # validated, explicitly approved distributor observation can cover a
    # LOW_STOCK row. Network errors/missing codes/other failures still block.
    replaced = {row.get('lcsc') for row in evidence.get('lines') or []
                if row.get('lcsc') in distributors and
                str(row.get('status', '')).startswith('LOW_STOCK(')}
    blocked_catalog = {row.get('lcsc') for row in evidence.get('lines') or []
                       if allow_blocked_sourcing and row.get('lcsc') not in replaced and
                       str(row.get('status', '')).startswith('LOW_STOCK(')}
    blocked = ({code for code in replaced
                if distributors[code].get('sourcing_state') == 'BLOCKED-SOURCING'} |
               blocked_catalog)
    if blocked and not allow_blocked_sourcing:
        failures.append('blocked distributor stock requires explicit blocked-sourcing continuation')
    if request.get("phase") != "prelayout" or request.get("schema") != 2:
        failures.append("request is not a schema-v2 prelayout request")
    if evidence.get("tool") != "jlc_stock_check.py":
        failures.append("catalog evidence was not emitted by jlc_stock_check.py")
    if evidence.get("stock_source") != "lcsc_catalog_stockCount":
        failures.append("catalog evidence does not identify the public LCSC catalog stock field")
    covered_failures = replaced | blocked_catalog
    if evidence.get("verdict") != ("FAIL" if covered_failures else "PASS"):
        failures.append(f"catalog verdict is {evidence.get('verdict')!r}, not PASS")
    if evidence.get("predicts_jlc_assembly_allocation") is not False:
        failures.append("catalog evidence does not preserve its non-allocation scope")
    age_reference = datetime.now(timezone.utc)
    max_age = timedelta(hours=24)
    if selection_snapshot is not None:
        try:
            if not isinstance(selection_snapshot, dict) or project is None:
                raise ValueError("snapshot needs project and mapping")
            declared = selection_snapshot.get("path")
            if not isinstance(declared, str) or not declared.strip():
                raise ValueError("snapshot needs project-relative path")
            pinned_path = (project / declared).resolve()
            if (project.resolve() not in pinned_path.parents or
                    pinned_path != evidence_path.resolve()):
                raise ValueError("snapshot path differs from current catalog evidence")
            digest = selection_snapshot.get("sha256")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("snapshot needs exact SHA-256")
            if hashlib.sha256(evidence_path.read_bytes()).hexdigest() != digest:
                failures.append("catalog initial snapshot digest changed")
            checked = datetime.fromisoformat(
                str(selection_snapshot.get("initial_checked_at") or "").replace("Z", "+00:00"))
            if checked.tzinfo is None:
                raise ValueError("initial_checked_at needs timezone")
            age_reference = checked.astimezone(timezone.utc)
            if age_reference > datetime.now(timezone.utc):
                failures.append("catalog initial check is future-dated")
            hours = selection_snapshot.get("max_age_hours")
            if isinstance(hours, bool) or not isinstance(hours, int) or hours <= 0:
                raise ValueError("snapshot max_age_hours must be positive integer")
            max_age = timedelta(hours=hours)
        except (ValueError, OSError) as exc:
            failures.append(f"catalog initial snapshot invalid: {exc}")
    try:
        generated = datetime.fromisoformat(str(evidence.get("generated_at") or "").replace("Z", "+00:00"))
        if generated.tzinfo is None:
            raise ValueError("timezone missing")
        age = age_reference - generated.astimezone(timezone.utc)
        if age < timedelta(0) or age > max_age:
            failures.append("catalog evidence is future-dated or stale at stock check time")
    except ValueError as exc:
        failures.append(f"catalog generated_at is invalid: {exc}")
    request_rows = request.get("rows") or []
    evidence_rows = evidence.get("lines") or []
    wanted = {row.get("requested_lcsc"): row for row in request_rows}
    observed = {row.get("lcsc"): row for row in evidence_rows}
    if len(wanted) != len(request_rows) or None in wanted or "" in wanted:
        failures.append("request contains duplicate or empty LCSC identities")
    if len(observed) != len(evidence_rows) or None in observed or "" in observed:
        failures.append("catalog evidence contains duplicate or empty LCSC identities")
    if not wanted or set(wanted) != set(observed):
        failures.append("catalog code set does not exactly match the request")
    for code, override in expected_overrides.items():
        source = [item for item in (exact_rows or [])
                  if code in item.get("jlc_codes", [])]
        if (sorted(item.get("ref") for item in source) != ["U_XU"] or
                any(item.get("mpn") != override["mpn"] for item in source)):
            failures.append(f"{code}: override differs from exact source identity")
    try:
        build_quantity = int(request.get("build_quantity"))
        if build_quantity <= 0:
            raise ValueError
    except (TypeError, ValueError):
        build_quantity = -1
        failures.append("request build_quantity is not a positive integer")
    try:
        if int(evidence.get("min_stock_per_board")) != build_quantity:
            failures.append("catalog build quantity does not match the request")
    except (TypeError, ValueError):
        failures.append("catalog min_stock_per_board is not integral")
    try:
        min_surplus = int(evidence.get("min_absolute_surplus"))
        if min_surplus < 0:
            raise ValueError
        if (expected_min_surplus is not None and
                min_surplus != expected_min_surplus):
            failures.append(
                "catalog absolute surplus does not match assembly policy")
    except (TypeError, ValueError):
        min_surplus = -1
        failures.append("catalog min_absolute_surplus is not a non-negative integer")
    observed_overrides = evidence.get("public_stock_surplus_overrides", [])
    expected_override_rows = [{"lcsc": code, **entry}
                              for code, entry in sorted(expected_overrides.items())]
    if observed_overrides != expected_override_rows:
        failures.append("catalog exact stock surplus overrides do not match assembly policy")
    expected_count = len(request_rows)
    for field, expected in (("graded_lines", expected_count),
                            ("total_lines", expected_count),
                            ("failures", len(covered_failures)), ("uncoded_lines", 0)):
        try:
            if int(evidence.get(field)) != expected:
                failures.append(f"catalog {field} is not {expected}")
        except (TypeError, ValueError):
            failures.append(f"catalog {field} is not integral")
    for code, row in wanted.items():
        got = observed.get(code) or {}
        if exact_rows is not None:
            source = [item for item in exact_rows
                      if code in item.get("jlc_codes", [])]
            if sorted(item.get("ref") for item in source) != sorted(
                    row.get("designators") or []):
                failures.append(f"{code}: catalog request differs from exact source population")
            for item in source:
                source_mpn = item.get("mpn")
                accepted_mpns = {source_mpn}
                dossier_path = item.get("dossier")
                if dossier_path:
                    dossier = yaml.safe_load(
                        Path(dossier_path).read_text(encoding="utf-8-sig")) or {}
                    catalog_mpn = (dossier.get("sourcing") or {}).get("catalog_mpn")
                    if catalog_mpn is not None:
                        if not isinstance(catalog_mpn, str) or not catalog_mpn.strip():
                            failures.append(f"{code}: invalid dossier catalog_mpn alias")
                        elif (dossier.get("mpn") != source_mpn or
                              (dossier.get("sourcing") or {}).get("lcsc") != code):
                            failures.append(f"{code}: catalog_mpn alias is not bound to exact dossier identity")
                        else:
                            accepted_mpns.add(catalog_mpn)
                if not source_mpn or got.get("mpn") not in accepted_mpns:
                    failures.append(f"{code}: catalog MPN {got.get('mpn')!r} differs from exact source {source_mpn!r}")
        if got.get("status") != "OK" and code not in covered_failures:
            failures.append(f"{code}: catalog status {got.get('status')!r}")
            continue
        try:
            per_board = int(got.get("qty"))
            required = int(got.get("required_qty"))
            threshold = int(got.get("stock_threshold"))
            surplus = int(got.get("absolute_surplus"))
            stock = int(got.get("stock"))
        except (TypeError, ValueError):
            failures.append(f"{code}: qty/required/threshold/surplus/stock is not integral")
            continue
        if per_board != int(row.get("per_board_qty") or -1):
            failures.append(f"{code}: per-board quantity disagrees with request")
        request_required = int(row.get("required_qty") or -1)
        try:
            applied_surplus = surplus_for(min_surplus, expected_overrides,
                                          code, got.get("mpn"), row.get("designators"))
        except ValueError as exc:
            failures.append(str(exc))
            continue
        expected_threshold = request_required + applied_surplus
        if expected_overrides and got.get("applied_surplus") != applied_surplus:
            failures.append(f"{code}: catalog applied surplus disagrees with policy")
        if required != request_required or threshold != expected_threshold:
            failures.append(f"{code}: catalog required quantity disagrees with request")
        expected_designators = sorted(str(ref) for ref in row.get("designators") or [])
        observed_designators = sorted(
            ref.strip() for ref in str(got.get("designators") or "").split(",")
            if ref.strip())
        if observed_designators != expected_designators:
            failures.append(f"{code}: catalog designators disagree with request")
        if surplus != stock - request_required:
            failures.append(f"{code}: catalog surplus arithmetic is inconsistent")
        if code in covered_failures and (got.get('status') != f'LOW_STOCK({stock})' or
                                         stock < 0 or stock >= expected_threshold):
            failures.append(f'{code}: inconsistent original JLC low-stock observation')
        if stock < expected_threshold and code not in covered_failures:
            failures.append(
                f"{code}: catalog stock {stock} below configured threshold")
    required_decision_terms = ("public-catalog", "pre-layout", "DO-NOT-ORDER")
    if any(term not in decision for term in required_decision_terms):
        failures.append("decision does not explicitly bound catalog use to pre-layout/DO-NOT-ORDER")
    return {
        "status": "FAIL" if failures else "PASS",
        "detail": ("; ".join(failures) if failures else
                   f"{len(wanted)}/{len(wanted)} exact public-source lines passed "
                   f"{'pinned initial' if selection_snapshot is not None else 'rolling'} stock screen "
                   f"({len(replaced)} approved distributor observation(s), "
                   f"{len(blocked)} blocked); user accepted for pre-layout only"),
        "output": "public stock design screen only; original JLC observations retained; final JLC uploader allocation and economics remain mandatory",
        "distributor_rows": {code: distributors[code] for code in sorted(replaced)},
        "sourcing_state": "BLOCKED-SOURCING" if blocked else "AVAILABLE",
    }


def _find_circuit(project: Path) -> Path:
    choices = [project / "03_tscircuit/build/circuit.json",
               project / "03_tscircuit/dist/circuit.json"]
    found = [path for path in choices if path.is_file()]
    if len(found) != 1:
        raise ValueError(f"expected one canonical circuit.json, found {found}")
    return found[0]


def exact_code_check(project: Path, circuit: Path,
                     assembly: Path) -> tuple[dict[str, Any], list[Path]]:
    items = json.loads(circuit.read_text(encoding="utf-8-sig"))
    components = [row for row in items
                  if isinstance(row, dict) and row.get("type") == "source_component"]
    assembly_data = yaml.safe_load(assembly.read_text(encoding="utf-8-sig")) or {}
    manual = {str(ref) for row in assembly_data.get("not_assembled") or []
              if isinstance(row, dict) for ref in row.get("refs") or []}
    dossiers: dict[str, tuple[Path, dict[str, Any]]] = {}
    duplicate_mpn = set()
    for path in sorted((project / "02_parts").glob("*/part.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        if not isinstance(data, dict) or not data.get("mpn"):
            continue
        mpn = str(data["mpn"])
        if mpn in dossiers:
            duplicate_mpn.add(mpn)
        dossiers[mpn] = (path, data)
    failures = [f"duplicate exact dossier identity {mpn!r}"
                for mpn in sorted(duplicate_mpn)]
    rows, used_dossiers = [], []
    for component in components:
        ref = str(component.get("name") or "")
        mpn = str(component.get("manufacturer_part_number") or "").strip()
        raw_supplier = ((component.get("supplier_part_numbers") or {})
                        .get("jlcpcb") or [])
        if isinstance(raw_supplier, str):
            raw_supplier = [raw_supplier]
        if not isinstance(raw_supplier, list):
            failures.append(f"{ref}: jlcpcb supplier identity must be a list")
            raw_supplier = []
        supplier_values = [str(value).strip() for value in raw_supplier
                           if str(value).strip()]
        codes = [value for value in supplier_values
                 if re.fullmatch(r"C\d+", value)]
        handles = [value for value in supplier_values if value not in codes]
        disposition = "jlc" if len(codes) == 1 else "manual" if ref in manual else "invalid"
        if len(codes) > 1:
            failures.append(f"{ref}: multiple JLC codes {codes}")
        if codes and handles:
            failures.append(
                f"{ref}: JLC supplier field mixes catalog code(s) and "
                f"non-code handle(s) {handles}")
        if not codes and ref not in manual:
            failures.append(f"{ref}: no JLC code and no not_assembled disposition")
        if ref in manual and codes:
            failures.append(f"{ref}: manual/unassembled ref also declares JLC code {codes}")
        dossier = dossiers.get(mpn) if mpn else None
        if mpn and dossier is None:
            failures.append(f"{ref}: exact MPN {mpn!r} has no dossier")
        if dossier:
            used_dossiers.append(dossier[0])
            sourcing = dossier[1].get("sourcing") or {}
            declared_code = str(sourcing.get("lcsc") or "").strip()
            if codes and declared_code and declared_code != codes[0]:
                failures.append(
                    f"{ref}: source code {codes[0]} disagrees with "
                    f"{mpn} dossier code {declared_code}")
            footprint = dossier[1].get("footprint")
            if disposition == "jlc" and (
                    not isinstance(footprint, str) or not footprint.strip()):
                failures.append(
                    f"{ref}: JLC-assembled exact MPN {mpn!r} has no frozen "
                    "footprint in its dossier")
        rows.append({"ref": ref, "mpn": mpn or None, "jlc_codes": codes,
                     "supplier_handles": handles,
                     "disposition": disposition,
                     "dossier": str(dossier[0].resolve()) if dossier else None,
                     "footprint": (dossier[1].get("footprint")
                                   if dossier else None)})
    return ({
        "status": "FAIL" if failures else "PASS",
        "detail": f"{len(rows)}/{len(components)} source component(s) graded",
        "coverage": {"graded": len(rows), "total": len(components)},
        "manual_refs": sorted(manual), "rows": rows, "findings": failures,
    }, sorted(set(used_dossiers)))


def grade(project: Path, *, phase: str, release: Path | None = None,
          pcba_receipt: Path | None = None,
          catalog_request: Path | None = None,
          catalog_evidence: Path | None = None,
          catalog_decision: Path | None = None,
          distributor_policy: Path | None = None,
          distributor_quotes: Path | None = None,
          allow_blocked_sourcing: bool = False) -> dict[str, Any]:
    if allow_blocked_sourcing and (phase != 'prelayout' or
                                   distributor_policy is None or
                                   distributor_quotes is None):
        raise ValueError('blocked sourcing requires explicit public prelayout distributor evidence')
    if distributor_policy is not None or distributor_quotes is not None:
        if (phase != 'prelayout' or pcba_receipt is not None or
                distributor_policy is None or distributor_quotes is None or
                catalog_request is None):
            raise ValueError('distributor evidence requires explicit public prelayout mode and both inputs')
    project = project.resolve()
    if phase == "order":
        selection_errors = release_selection_errors(project)
        if selection_errors:
            raise ValueError("critical selection order hold: " + "; ".join(selection_errors))
    circuit = _find_circuit(project)
    assembly = project / "03_src/rules/assembly.yaml"
    if not assembly.is_file():
        raise ValueError(f"missing {assembly}")
    checks: dict[str, dict[str, Any]] = {}
    exact, dossiers = exact_code_check(project, circuit, assembly)
    checks["exact_code_identity"] = exact
    checks["source_value_identity"] = _run(
        "source value identity",
        ["/usr/bin/python3", str(SCRIPTS / "bom_source_check.py"),
         "--circuit-only", str(circuit), "--parts", str(project / "02_parts")],
        project)
    inputs = {"circuit": _record(circuit), "assembly": _record(assembly)}
    for index, path in enumerate(dossiers):
        inputs[f"part_{index:03d}"] = _record(path)

    if pcba_receipt is not None:
        pcba_receipt = pcba_receipt.resolve()
        if pcba_receipt.is_file():
            inputs["pcba_receipt"] = _record(pcba_receipt)

    if phase == "prelayout":
        if pcba_receipt is not None:
            checks["jlc_pcba_availability"] = _pcba_check(
                pcba_receipt, phase="prelayout", bom=circuit,
                predicate="availability")
            checks["procurement_exposure"] = _pcba_check(
                pcba_receipt, phase="prelayout", bom=circuit,
                predicate="economics")
        else:
            distributors = {}
            assembly_rules = yaml.safe_load(
                assembly.read_text(encoding="utf-8-sig")) or {}
            sourcing_authority = assembly_rules.get("sourcing_authority")
            configured_surplus, overrides = parse_policy(assembly_rules, project)
            if distributor_policy is not None:
                distributors, distributor_inputs = _distributor_prelayout_rows(
                    project, json.loads(catalog_request.read_text()),
                    distributor_policy, distributor_quotes, exact['rows'],
                    allow_blocked_sourcing=allow_blocked_sourcing)
                inputs.update(distributor_inputs)
            checks["public_catalog_prelayout"] = _catalog_prelayout_check(
                catalog_request, catalog_evidence, catalog_decision,
                distributors=distributors,
                allow_blocked_sourcing=allow_blocked_sourcing,
                expected_min_surplus=configured_surplus,
                expected_overrides=overrides,
                exact_rows=exact['rows'],
                selection_snapshot=assembly_rules.get("public_stock_selection_snapshot"),
                project=project)
            if (sourcing_authority is not None and
                    sourcing_authority != "public-observations"):
                checks["public_catalog_prelayout"] = {
                    "status": "FAIL",
                    "detail": "assembly sourcing_authority does not admit public observations",
                    "output": "public design screen requires explicit project authority",
                }
            checks["procurement_exposure"] = {
                "status": checks["public_catalog_prelayout"]["status"],
                "detail": ("deferred to final JLC uploader under explicit user decision"
                           if checks["public_catalog_prelayout"]["status"] == "PASS"
                           else "catalog acceptance decision is incomplete"),
                "output": "no preorder, MOQ, allocation, or payment is authorized by this pre-layout result",
            }
            for name, path in (("catalog_request", catalog_request),
                               ("catalog_evidence", catalog_evidence),
                               ("catalog_decision", catalog_decision)):
                if path is not None and path.is_file():
                    inputs[name] = _record(path.resolve())

    if phase == "order":
        if release is None or not release.is_dir():
            raise ValueError("order phase requires --release directory")
        release = release.resolve()
        manifest = release / "MANIFEST.txt"
        readme = release / "ORDER_README.md"
        for name, path in (("release_manifest", manifest),
                           ("order_instructions", readme)):
            if not path.is_file():
                raise ValueError(f"missing {path}")
            inputs[name] = _record(path)
        checks["assembly_population"] = _run(
            "assembly population",
            ["/usr/bin/python3", str(SCRIPTS / "assembly_coverage.py"),
             str(release), "--assembly", str(assembly)], project)
        checks["realized_part_facts"] = _run(
            "realized part facts",
            ["/usr/bin/python3", str(SCRIPTS / "part_facts_check.py"),
             str(release), "--parts", str(project / "02_parts"), "--strict"],
            project)
        checks["jlc_order_allocation"] = _pcba_check(
            pcba_receipt, phase="order", bom=release / "fab/bom.csv",
            predicate="availability")
        checks["order_procurement_exposure"] = _pcba_check(
            pcba_receipt, phase="order", bom=release / "fab/bom.csv",
            predicate="economics")
        checks["order_time_sourcing"] = _run(
            "order-time sourcing",
            ["/usr/bin/python3", str(SCRIPTS / "release_freshness_check.py"),
             str(release), "--claim", "sourcing", "--assembly", str(assembly),
             "--sourcing-authority", "jlc-pcba", "--pcba-evidence",
             str(pcba_receipt or "")],
            project)

    if pcba_receipt is not None and "pcba_receipt" in inputs:
        try:
            receipt_stable = _record(pcba_receipt) == inputs["pcba_receipt"]
        except OSError:
            receipt_stable = False
        if not receipt_stable:
            checks["pcba_receipt_stability"] = {
                "status": "FAIL",
                "detail": "PCBA receipt changed during readiness composition",
                "output": "the final receipt identity differs from the input census",
            }

    statuses = {row["status"] for row in checks.values()}
    verdict = ("INCOMPLETE" if "INCOMPLETE" in statuses else
               "REJECTED" if "FAIL" in statuses else "ACCEPTED")
    return {
        "schema": 1, "kind": "manufacturing-readiness-receipt-v1",
        "phase": phase, "verdict": verdict, "project": project.name,
        "inputs": inputs, "checks": checks,
        "coverage": {"passing": sum(row["status"] == "PASS"
                                     for row in checks.values()),
                     "total": len(checks)},
    }


def verify(path: Path) -> tuple[bool, list[str]]:
    failures = []
    try:
        receipt = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return False, [f"receipt cannot be read: {exc}"]
    if (receipt.get("schema") != 1 or
            receipt.get("kind") != "manufacturing-readiness-receipt-v1"):
        failures.append("unsupported receipt schema/kind")
    for name, record in sorted((receipt.get("inputs") or {}).items()):
        source = Path(str(record.get("path") or ""))
        if not source.is_file() or _record(source) != record:
            failures.append(f"input moved or changed: {name}")
    if receipt.get("verdict") == "ACCEPTED":
        bad = [name for name, row in (receipt.get("checks") or {}).items()
               if row.get("status") != "PASS"]
        if bad:
            failures.append(f"accepted receipt contains bad checks: {bad}")
    return not failures, failures


def _publish_part_freeze(result: dict[str, Any], receipt_path: Path,
                         bundle_path: Path, stage_path: Path) -> None:
    """Emit a typed shadow request; never replace an accepted bundle."""
    if result.get("phase") != "prelayout":
        raise ValueError("S-PART-FREEZE publication requires phase prelayout")
    if result.get("verdict") != "ACCEPTED":
        raise ValueError("S-PART-FREEZE cannot publish non-accepted evidence")
    semantic = {
        "phase": result["phase"], "project": result.get("project"),
        "legacy_verdict": result.get("verdict"),
        "inputs": {name: record.get("sha256")
                   for name, record in sorted(
                       (result.get("inputs") or {}).items())},
    }
    payload = json.dumps(
        semantic, sort_keys=True, separators=(",", ":")).encode("utf-8")
    identity = subject_identity("part-freeze", 1, [TypedIdentityInput(
        "readiness", "mapping", semantic, payload)])
    del receipt_path, bundle_path
    coverage = result["coverage"]
    write_shadow_stage_result(
        stage_id="S-PART-FREEZE", subject=identity,
        stage_result_path=stage_path, total=coverage["total"],
        finding_code="S-PART-PROMOTION-DISABLED",
        finding_detail=(
            "manufacturing-readiness receipt is legacy authority; accepted "
            "bundle unchanged until one atomic pointer-last transaction exists"),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    grade_parser = sub.add_parser("grade")
    grade_parser.add_argument("project", type=Path)
    grade_parser.add_argument("--phase", choices=("selection", "prelayout", "order"),
                              default="selection")
    grade_parser.add_argument("--release", type=Path)
    grade_parser.add_argument("--pcba-receipt", type=Path)
    grade_parser.add_argument("--catalog-request", type=Path)
    grade_parser.add_argument("--catalog-evidence", type=Path)
    grade_parser.add_argument("--catalog-decision", type=Path)
    grade_parser.add_argument("--distributor-policy", type=Path)
    grade_parser.add_argument("--distributor-quotes", type=Path)
    grade_parser.add_argument("--allow-blocked-sourcing", action="store_true",
                              help="prelayout design continuation only; keep exact sourcing as a loud order hold")
    grade_parser.add_argument("--json", type=Path, required=True)
    grade_parser.add_argument("--stage-bundle", type=Path)
    grade_parser.add_argument("--stage-result", type=Path)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("receipt", type=Path)
    args = parser.parse_args(argv)
    if args.command == "verify":
        valid, failures = verify(args.receipt)
        for failure in failures:
            print(f"  FAIL {failure}")
        print(f"MANUFACTURING-READINESS RECEIPT {'PASS' if valid else 'FAIL'}")
        return 0 if valid else 1
    if bool(args.stage_bundle) != bool(args.stage_result):
        print("MANUFACTURING-READINESS INCOMPLETE: --stage-bundle and "
              "--stage-result must be supplied together")
        return 2
    output_paths = {"receipt": args.json}
    if args.stage_bundle:
        output_paths.update({"stage_bundle": args.stage_bundle,
                             "stage_result": args.stage_result})
    try:
        require_safe_output_layout(
            output_paths,
            directory_outputs=("stage_bundle",) if args.stage_bundle else (),
            protected_paths={"project": args.project},
        )
    except ValueError as exc:
        print(f"MANUFACTURING-READINESS INCOMPLETE: {exc}")
        return 2
    try:
        result = grade(args.project, phase=args.phase, release=args.release,
                       pcba_receipt=args.pcba_receipt,
                       catalog_request=args.catalog_request,
                       catalog_evidence=args.catalog_evidence,
                       catalog_decision=args.catalog_decision,
                       distributor_policy=args.distributor_policy,
                       distributor_quotes=args.distributor_quotes,
                       allow_blocked_sourcing=args.allow_blocked_sourcing)
    except Exception as exc:
        print(f"MANUFACTURING-READINESS INCOMPLETE: {exc}")
        return 2
    try:
        require_safe_output_layout(
            output_paths,
            directory_outputs=("stage_bundle",) if args.stage_bundle else (),
            protected_paths={
                "project": args.project,
                **{f"input_{name}": Path(record["path"])
                   for name, record in (result.get("inputs") or {}).items()},
            },
        )
    except ValueError as exc:
        print(f"MANUFACTURING-READINESS INCOMPLETE: {exc}")
        return 2
    _atomic_json(args.json, result)
    if args.stage_bundle:
        try:
            _publish_part_freeze(result, args.json.resolve(),
                                 args.stage_bundle.resolve(),
                                 args.stage_result.resolve())
        except Exception as exc:
            print(f"MANUFACTURING-READINESS INCOMPLETE: shadow stage evidence: {exc}")
            # Optional part-freeze publication remains shadow authority.
            # Preserve the legacy readiness verdict and prior accepted bundle.
    coverage = result["coverage"]
    print(f"MANUFACTURING-READINESS {result['verdict']}: "
          f"{coverage['passing']}/{coverage['total']} checks pass; "
          f"phase={result['phase']}; receipt={args.json.resolve()}")
    return {"ACCEPTED": 0, "REJECTED": 1, "INCOMPLETE": 2}[result["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
