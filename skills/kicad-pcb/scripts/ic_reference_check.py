#!/usr/bin/env python3
"""Grade source-selected IC reference research and per-instance applicability.

Usage: ic_reference_check.py PROJECT [--json OUTPUT] [--print-bindings]
The packet is project source, never a route or layout acceptance receipt.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

import yaml

from generate_board_generic import parse_netlist


NON_IC_TYPES = re.compile(
    r"connector|header|receptacle|crystal|mosfet|transistor|"
    r"inductor|resistor|capacitor|diode|fuse|transformer|test_point|jumper", re.I)
IC_TYPES = re.compile(
    r"supervisor|translator|converter|amplifier|analog_switch|protection_array|"
    r"efuse|power_module|inverter|logic|microcontroller|adc|flash|regulator|"
    r"flip_flop|multivibrator|buffer|comparator|driver|controller|isolator|sensor|oscillator|"
    r"(?:and|or|nand|nor|xor|xnor)_gate", re.I)


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def source_bindings(project: Path, *, binding_schema: int = 1) -> dict[str, str]:
    if binding_schema not in (1, 2) or isinstance(binding_schema, bool):
        raise ValueError("IC binding_schema must be 1 or 2")
    floor = yaml.safe_load((project / "03_src/floorplan.yaml").read_text()) or {}
    nets = yaml.safe_load((project / "03_src/rules/nets.yaml").read_text()) or {}
    route = yaml.safe_load((project / "03_src/route.yaml").read_text()) or {}
    rf_path = project / "03_src/rules/rf.yaml"
    rf = (yaml.safe_load(rf_path.read_text()) or {}) if rf_path.is_file() else {}
    rf_ports = (rf.get("rf") or {}).get("ports")
    if binding_schema == 2:
        # Schema 2 binds electrical targets, while selected MPNs and nets are
        # already bound by the instance/circuit records. Legacy packets retain
        # their exact schema-1 digest until deliberately migrated.
        rf_ports = [
            {key: port.get(key) for key in
             ("id", "nets", "band_hz", "z0_ohm", "reference_layer")}
            for port in (rf_ports or [])
        ]
    board = floor.get("board") or {}
    stack = {
        "layers": board.get("layers"), "stackup": board.get("stackup"),
        "design_rules": floor.get("design_rules"), "zones": floor.get("zones"),
        "keepouts": floor.get("keepouts"),
        "rf_cross_sections": (rf.get("rf") or {}).get("cross_sections"),
        "rf_ports": rf_ports,
    }
    rules = {
        key: nets.get(key) for key in ("fab_tier", "default_clearance",
        "default_track_width", "classes", "scoped_floors", "scoped_clearances",
        "same_footprint_pad_clearances")
    }
    rules.update({"route_common": (route.get("route") or {}).get("common"),
                  "route_waves": (route.get("route") or {}).get("waves")})
    return {"stackup_sha256": digest(stack), "route_rules_sha256": digest(rules)}


def selected_components(project: Path) -> tuple[list[dict], list[str]]:
    circuit = project / "03_tscircuit/build/circuit.json"
    floor = yaml.safe_load((project / "03_src/floorplan.yaml").read_text()) or {}
    netlist = project / (floor.get("project") or {}).get("netlist", "")
    if not circuit.is_file() or not netlist.is_file():
        raise ValueError("fresh circuit.json and source-declared netlist are required")
    payload = json.loads(circuit.read_text())
    if not isinstance(payload, list):
        raise ValueError("circuit.json must contain a component list")
    comps, pad_net, _ = parse_netlist(netlist)
    source = [x for x in payload if isinstance(x, dict) and x.get("type") == "source_component"]
    if not source:
        raise ValueError("circuit.json has zero source components")
    dossiers = defaultdict(list)
    for path in sorted((project / "02_parts").glob("*/part.yaml")):
        part = yaml.safe_load(path.read_text()) or {}
        if not isinstance(part, dict):
            raise ValueError(f"malformed dossier {path}")
        dossiers[str(part.get("mpn") or "")].append((path, part))
    findings, selected, seen = [], [], set()
    for row in source:
        ref = str(row.get("name") or "")
        mpn = str(row.get("manufacturer_part_number") or "")
        if not ref or ref in seen:
            findings.append(f"duplicate/blank source component ref {ref!r}")
            continue
        seen.add(ref)
        if ref not in comps:
            findings.append(f"{ref}: absent from source netlist")
            continue
        footprint, value = comps[ref]
        matches = [(path, part) for path, part in dossiers.get(mpn, [])
                   if str(part.get("footprint") or "") == footprint]
        if len(matches) != 1:
            findings.append(f"{ref}: expected one exact MPN+footprint dossier for "
                            f"{mpn!r}/{footprint!r}, found {len(matches)}")
            continue
        path, part = matches[0]
        kind = str(part.get("type") or "")
        pins = part.get("pins") or {}
        if not isinstance(pins, dict):
            findings.append(f"{ref}: malformed dossier pins")
            continue
        is_ic = bool(IC_TYPES.search(kind))
        if not is_ic and len(pins) > 2 and not NON_IC_TYPES.search(kind):
            findings.append(f"{ref}: unknown multi-pin part type {kind!r}; classify IC status")
            continue
        if not is_ic:
            continue
        pad_nets = sorted((str(pad), net) for (owner, pad), net in pad_net.items()
                          if owner == ref)
        selected.append({"refdes": ref, "mpn": mpn,
                         "package": str(part.get("package") or ""),
                         "footprint": footprint, "value": value,
                         "pad_nets": pad_nets,
                         "dossier": path, "layout_refs": part.get("layout_refs") or [],
                         "circuit_sha256": digest({"mpn": mpn, "footprint": footprint,
                                                    "value": value, "pad_nets": pad_nets})})
    missing = sorted(set(comps) - seen)
    if missing:
        findings.append(f"netlist components absent from circuit: {missing[:8]} ({len(missing)})")
    return sorted(selected, key=lambda x: x["refdes"]), findings


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def subject_digest(selected: list[dict], bindings: dict[str, str]) -> str:
    return digest({"source": bindings, "instances": [
        {key: row[key] for key in ("refdes", "mpn", "package", "footprint", "circuit_sha256")}
        for row in selected]})


def semantic_receipt(project: Path, packet_path: Path, packet: dict,
                     selected: list[dict], bindings: dict[str, str]) -> tuple[str, list[str]]:
    path = project / "08_reviews/ic_reference_semantic_review.yaml"
    if not path.is_file():
        return "UNVERIFIED", ["independent IC reference semantic review receipt missing"]
    try:
        review = yaml.safe_load(path.read_text()) or {}
    except Exception as exc:
        return "STALE", [f"semantic review receipt unreadable: {exc}"]
    reviewer = review.get("reviewer")
    owners = {str(row.get("research_owner") or "").strip().casefold()
              for row in packet.get("parts") or [] if isinstance(row, dict)}
    expected_refs = [row["refdes"] for row in selected]
    failures = []
    if review.get("schema") != 1 or review.get("verdict") != "approved":
        failures.append("semantic receipt needs schema:1 and verdict:approved")
    if not (_nonempty(reviewer) and re.fullmatch(r"[A-Za-z0-9._@/-]+", reviewer)
            and _nonempty(review.get("reviewed_at"))):
        failures.append("semantic receipt needs stable reviewer principal and reviewed_at")
    if _nonempty(reviewer) and reviewer.strip().casefold() in owners:
        failures.append("semantic reviewer must differ from packet research_owner")
    if review.get("scope") != "IC reference record semantics only":
        failures.append("semantic receipt scope cannot claim P1/layout approval")
    evidence = review.get("evidence") or {}
    if not isinstance(evidence, dict) or not (_nonempty(evidence.get("path"))
            and _nonempty(evidence.get("sha256")) and _nonempty(evidence.get("locator"))):
        failures.append("semantic receipt needs evidence path/sha256/locator")
    else:
        evidence_path = (project / evidence["path"]).resolve()
        if project not in evidence_path.parents or not evidence_path.is_file():
            failures.append("semantic receipt evidence path missing/escapes project")
        elif hashlib.sha256(evidence_path.read_bytes()).hexdigest() != evidence["sha256"]:
            failures.append("semantic receipt evidence content hash is stale")
    if review.get("packet_sha256") != hashlib.sha256(packet_path.read_bytes()).hexdigest():
        failures.append("semantic receipt packet_sha256 is stale")
    if review.get("subject_sha256") != subject_digest(selected, bindings):
        failures.append("semantic receipt subject_sha256 is stale")
    if review.get("reviewed_refs") != expected_refs:
        failures.append("semantic receipt reviewed_refs do not cover exact selected IC census")
    return ("STALE", failures) if failures else ("APPROVED", [])


def _inspected(project: Path, record: dict, label: str, findings: list[str],
               dossier_dir: Path | None = None) -> bool:
    if record.get("inspected") is not True:
        return False
    inspection = record.get("inspection") or {}
    if not isinstance(inspection, dict) or not (_nonempty(inspection.get("locator"))
            and _nonempty(inspection.get("notes"))):
        findings.append(f"{label}: inspected requires inspection.locator and notes")
        return False
    source_path = inspection.get("source_path")
    claimed_hash = inspection.get("sha256")
    if source_path:
        raw = Path(str(source_path))
        project_path = (project / raw).resolve()
        path = project_path if project_path.is_file() or dossier_dir is None else (dossier_dir / raw).resolve()
        if project.resolve() not in path.parents or not path.is_file():
            findings.append(f"{label}: inspected source_path missing/escapes project")
            return False
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != claimed_hash:
            findings.append(f"{label}: inspected source content hash is stale")
            return False
    elif not (isinstance(claimed_hash, str) and re.fullmatch(r"[0-9a-f]{64}", claimed_hash)):
        findings.append(f"{label}: inspected remote artifact needs content sha256")
        return False
    return True


def evaluate(project: Path, allow_unmigrated: bool = False) -> dict:
    project = project.resolve()
    packet_path = project / "03_src/rules/ic_reference_research.yaml"
    if not packet_path.is_file():
        return {"status": "UNMIGRATED" if allow_unmigrated else "INCOMPLETE",
                "coverage": {"selected_ic": None, "applications": 0},
                "findings": [] if allow_unmigrated else ["missing ic_reference_research.yaml"]}
    try:
        selected, findings = selected_components(project)
        packet = yaml.safe_load(packet_path.read_text()) or {}
        binding_schema = packet.get("binding_schema", 1) if isinstance(packet, dict) else 1
        bindings = source_bindings(project, binding_schema=binding_schema)
    except Exception as exc:
        return {"status": "FAIL", "coverage": {"selected_ic": None, "applications": 0},
                "findings": [f"unreadable source/packet: {exc}"]}
    if not isinstance(packet, dict) or packet.get("schema") != 1 or not isinstance(packet.get("parts"), list):
        findings.append("packet requires schema: 1 and parts: list")
        rows = []
    else:
        rows = packet["parts"]
        if packet.get("engineering_status") != "INCOMPLETE":
            findings.append("packet engineering_status must remain INCOMPLETE; reference research is not layout proof")
    by_ref = {x["refdes"]: x for x in selected}
    seen_apps = Counter()
    docs_only, completed, missing_evidence = [], [], []
    for i, row in enumerate(rows):
        label = f"parts[{i}]"
        if not isinstance(row, dict):
            findings.append(f"{label}: expected mapping")
            continue
        mpn, package = row.get("mpn"), row.get("package")
        group = [x for x in selected if x["mpn"] == mpn and x["package"] == package]
        if not group:
            findings.append(f"{label}: no selected IC has exact MPN/package {mpn!r}/{package!r}")
        state = row.get("state")
        if state not in ("complete", "missing_evidence"):
            findings.append(f"{label}: state must be complete or missing_evidence")
        if not (_nonempty(row.get("research_owner")) and _nonempty(row.get("next_action"))):
            findings.append(f"{label}: research_owner and next_action are required")
        if state == "missing_evidence":
            missing_evidence.append(f"{mpn}/{package}")
        artifact_inspected = False
        artifacts = row.get("artifacts") or []
        if not isinstance(artifacts, list) or not artifacts:
            findings.append(f"{label}: artifacts must record the inspected or unavailable reference search")
            artifacts = []
        for j, artifact in enumerate(artifacts):
            alabel = f"{label}.artifacts[{j}]"
            if not isinstance(artifact, dict):
                findings.append(f"{alabel}: expected mapping")
                continue
            if not (_nonempty(artifact.get("publisher")) and _nonempty(artifact.get("artifact"))
                    and _nonempty(artifact.get("url")) and artifact.get("tier") in (1, 2, 3, 4)
                    and _nonempty(artifact.get("format")) and isinstance(artifact.get("editable"), bool)
                    and isinstance(artifact.get("inspected"), bool)):
                findings.append(f"{alabel}: incomplete artifact identity/retrieval fields")
            for part in group:
                matches = [ref for ref in part["layout_refs"] if isinstance(ref, dict)
                           and ref.get("artifact") == artifact.get("artifact")
                           and ref.get("tier") == artifact.get("tier")]
                if not matches:
                    findings.append(f"{alabel}: artifact/tier absent from {part['dossier']} layout_refs")
                elif artifact.get("inspected") is True and not any(ref.get("reached") is True for ref in matches):
                    findings.append(f"{alabel}: inspected artifact contradicts dossier reached: false")
            retrieval = artifact.get("retrieval") or {}
            if not isinstance(retrieval, dict) or retrieval.get("status") not in ("retrieved", "unavailable", "restricted", "found") \
                    or not _nonempty(retrieval.get("at")) or not _nonempty(retrieval.get("detail")):
                findings.append(f"{alabel}: retrieval needs status/at/detail; task packet absence is not search")
            elif retrieval["status"] in ("unavailable", "restricted"):
                detail = retrieval["detail"].lower()
                if "task packet" in detail and not re.search(
                        r"search|request|contact|vendor|download|catalog|repository|http", detail):
                    findings.append(f"{alabel}: missing task packet alone is not a public-file search")
            if artifact.get("inspected") is True:
                artifact_inspected |= _inspected(
                    project, artifact, alabel, findings,
                    group[0]["dossier"].parent if group else None)
            elif retrieval.get("status") == "retrieved":
                findings.append(f"{alabel}: retrieved URL/file remains uninspected")
        fallback = row.get("docs_fallback") or {}
        fallback_inspected = False
        if fallback:
            if not isinstance(fallback, dict) or not (_nonempty(fallback.get("artifact"))
                    and _nonempty(fallback.get("url")) and isinstance(fallback.get("inspected"), bool)
                    and isinstance(fallback.get("extracted_guidance"), list)):
                findings.append(f"{label}: malformed docs_fallback")
            elif fallback.get("inspected"):
                for part in group:
                    if not any(isinstance(ref, dict) and ref.get("artifact") == fallback.get("artifact")
                               and ref.get("reached") is True for ref in part["layout_refs"]):
                        findings.append(f"{label}.docs_fallback: artifact absent from {part['dossier']} layout_refs")
                fallback_inspected = _inspected(
                    project, fallback, f"{label}.docs_fallback", findings,
                    group[0]["dossier"].parent if group else None)
                if not fallback.get("extracted_guidance"):
                    findings.append(f"{label}: inspected docs_fallback needs extracted_guidance")
        if state == "complete" and not (artifact_inspected or fallback_inspected):
            findings.append(f"{label}: complete research has no inspected artifact or docs fallback")
        if fallback_inspected and not artifact_inspected:
            docs_only.append(f"{mpn}/{package}")
        for j, app in enumerate(row.get("applications") or []):
            app_label = f"{label}.applications[{j}]"
            app_start = len(findings)
            if not isinstance(app, dict):
                findings.append(f"{app_label}: expected mapping")
                continue
            ref = str(app.get("refdes") or "")
            seen_apps[ref] += 1
            source = by_ref.get(ref)
            if source is None or source["mpn"] != mpn or source["package"] != package:
                findings.append(f"{app_label}: {ref} is not selected under exact MPN/package")
                continue
            if app.get("footprint") != source["footprint"]:
                findings.append(f"{app_label}: stale footprint for {ref}")
            if not (_nonempty(app.get("mode")) and _nonempty(app.get("stackup"))
                    and _nonempty(app.get("route_rules"))
                    and isinstance(app.get("critical_pins_or_nets"), list)
                    and bool(app.get("critical_pins_or_nets"))
                    and isinstance(app.get("extracted_constraints"), list)):
                findings.append(f"{app_label}: mode/stack/rules/pins/constraints incomplete")
            critical = app.get("critical_pins_or_nets") or []
            connected = [(pad, net) for pad, net in source["pad_nets"]
                         if not net.startswith(("unconnected-", "Net-("))]
            allowed = {net for _, net in connected} | {
                f"{ref}.{pad}" for pad, _ in connected}
            if any(not isinstance(item, str) or item not in allowed for item in critical):
                findings.append(f"{app_label}: critical_pins_or_nets must name connected source net or {ref}.pad; NC is not a critical launch")
            constraints = app.get("extracted_constraints") or []
            concrete = [rule for rule in constraints if isinstance(rule, str)
                        and len(rule.strip()) >= 20
                        and "use the retained manufacturer primary layout guidance" not in rule.lower()
                        and any(isinstance(item, str) and item in re.sub(
                            r"\s*Applies to\s+[A-Za-z0-9_]+\.[A-Za-z0-9_]+\.?\s*$", "", rule,
                            flags=re.I) for item in critical)]
            if not concrete:
                findings.append(f"{app_label}: extracted_constraints need concrete rule tied to a listed source pin/net")
            applicability = app.get("applicability") or {}
            if not isinstance(applicability, dict) or applicability.get("status") not in ("applicable", "limited", "not_applicable", "unknown"):
                findings.append(f"{app_label}: applicability status missing/invalid")
                continue
            reviewed = applicability.get("reviewed_for") or {}
            expected = {"mpn": mpn, "package": package, "mode": app.get("mode"),
                        "circuit_sha256": source["circuit_sha256"], **bindings}
            if reviewed != expected:
                findings.append(f"{app_label}: stale applicability reviewed_for binding")
            if applicability["status"] in ("limited", "not_applicable", "unknown") and not applicability.get("reasons"):
                findings.append(f"{app_label}: limited/unknown applicability needs reasons")
            if (len(findings) == app_start and applicability["status"] in ("applicable", "limited")
                    and app.get("extracted_constraints")):
                completed.append(ref)
    for ref in by_ref:
        if seen_apps[ref] != 1:
            findings.append(f"{ref}: selected IC requires exactly one application, found {seen_apps[ref]}")
    if not selected:
        findings.append("source-derived selected IC census is empty")
    status = "FAIL" if findings else ("INCOMPLETE" if missing_evidence
                                      or len(completed) != len(selected) else "COVERAGE_PASS")
    semantic_status, semantic_findings = semantic_receipt(
        project, packet_path, packet if isinstance(packet, dict) else {}, selected, bindings)
    return {"status": status, "engineering_status": "INCOMPLETE",
            "semantic_review": semantic_status,
            "semantic_findings": semantic_findings,
            "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
            "subject_sha256": subject_digest(selected, bindings),
            "scope": "machine-checkable reference coverage/identity only; independent semantic review and layout acceptance owed",
            "coverage": {"selected_ic": len(selected),
            "applications": sum(seen_apps.values()), "research_covered": len(completed)},
            "selected_refs": sorted(by_ref), "docs_only": docs_only,
            "missing_evidence": missing_evidence,
            "bindings": bindings, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--print-bindings", action="store_true")
    parser.add_argument("--allow-unmigrated", action="store_true")
    parser.add_argument("--require-semantic-review", action="store_true")
    args = parser.parse_args()
    try:
        if args.print_bindings:
            selected, findings = selected_components(args.project)
            packet = yaml.safe_load((args.project / "03_src/rules/ic_reference_research.yaml").read_text()) or {}
            binding_schema = packet.get("binding_schema", 1)
            bindings = source_bindings(args.project, binding_schema=binding_schema)
            result = {"source": bindings, "binding_schema": binding_schema,
                      "instances": {x["refdes"]: {"mpn": x["mpn"],
                                   "package": x["package"],
                                   "footprint": x["footprint"],
                                   "circuit_sha256": x["circuit_sha256"]} for x in selected},
                      "subject_sha256": subject_digest(selected, bindings),
                      "findings": findings}
            print(json.dumps(result, indent=2, sort_keys=True))
            return 1 if findings else 0
        result = evaluate(args.project, args.allow_unmigrated)
    except Exception as exc:
        result = {"status": "FAIL", "findings": [str(exc)]}
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"P-PREC/P-LAYOUT-IC {result['status']}: {result.get('coverage')}; "
          f"semantic={result.get('semantic_review', 'UNVERIFIED')}; "
          f"engineering={result.get('engineering_status', 'INCOMPLETE')}")
    for finding in result.get("findings", [])[:20]:
        print("  ", finding)
    if args.require_semantic_review:
        for finding in result.get("semantic_findings", []):
            print("  ", finding)
        return 0 if result["status"] == "COVERAGE_PASS" and result.get("semantic_review") == "APPROVED" else 2
    return 0 if result["status"] in ("COVERAGE_PASS", "UNMIGRATED") else 2


if __name__ == "__main__":
    sys.exit(main())
