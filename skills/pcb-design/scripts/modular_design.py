#!/usr/bin/env python3
"""Independent block-coverage and child-work checks for modular PCB work.

This is a diagnostic inside the existing architecture, placement and routing
stages.  It neither creates lifecycle stages nor accepts PCB geometry.  The
authored plan is compared with the component/pad connectivity observed in a
generated tscircuit ``circuit.json``.  Optional work observations describe
task progress only; owning electrical and geometry gates remain authoritative.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from pipeline_execution import ExecutionValidationError, TaskAttempt
from pipeline_identity import TypedIdentityInput, subject_identity


SCHEMA = 1
PHASES = ("P1_FLOORPLAN", "P2_BLOCK_PLACEMENT", "P3_CRITICAL_LOCAL_ROUTES",
          "P4_JOINT_PROOF", "P5_INTEGRATED_PLACEMENT_REVIEW")
PHASE_RANK = {phase: index for index, phase in enumerate(PHASES)}
TOKEN = re.compile(r"^[a-z][a-z0-9_-]*$")
REF = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")
ENDPOINT = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*\.[^.\s\[\]{}]+$")
STAGE_IDS = frozenset({"PCB-ARCHITECTURE", "KICAD-SCHEMATIC",
                       "KICAD-PLACEMENT", "KICAD-ROUTING"})


class ModularDesignError(ValueError):
    pass


def _fail(message: str) -> None:
    raise ModularDesignError(message)


def _exact(row: Any, fields: set[str], where: str) -> Mapping[str, Any]:
    if not isinstance(row, Mapping):
        _fail(f"{where}: expected a mapping")
    missing, unknown = fields - set(row), set(row) - fields
    if missing or unknown:
        _fail(f"{where}: fields differ (missing={sorted(missing)}, unknown={sorted(unknown)})")
    return row


def _list(value: Any, where: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list):
        _fail(f"{where}: expected a list")
    if nonempty and not value:
        _fail(f"{where}: cannot be empty")
    return value


def _strings(value: Any, where: str, *, nonempty: bool = False,
             pattern: re.Pattern[str] | None = None) -> tuple[str, ...]:
    rows = _list(value, where, nonempty=nonempty)
    if any(not isinstance(item, str) or not item.strip() for item in rows):
        _fail(f"{where}: every item must be non-empty text")
    if rows != sorted(set(rows)):
        _fail(f"{where}: values must be sorted and unique")
    if pattern and any(pattern.fullmatch(item) is None for item in rows):
        _fail(f"{where}: value does not match {pattern.pattern}")
    return tuple(rows)


def _paths(value: Any, where: str, *, nonempty: bool = False) -> tuple[str, ...]:
    rows = _strings(value, where, nonempty=nonempty)
    for item in rows:
        path = Path(item)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != item or item in {"", "."}:
            _fail(f"{where}: {item!r} is not a safe relative POSIX path")
    return rows


def _token(value: Any, where: str) -> str:
    if not isinstance(value, str) or TOKEN.fullmatch(value) is None:
        _fail(f"{where}: expected {TOKEN.pattern}")
    return value


def _elements(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        value = value.get("elements")
    if not isinstance(value, list) or not value:
        _fail("circuit: expected a non-empty element list")
    if any(not isinstance(row, Mapping) for row in value):
        _fail("circuit: every element must be a mapping")
    return value


def observe_circuit(value: Any) -> dict[str, Any]:
    """Extract refs and complete net endpoint membership independently."""
    elements = _elements(value)
    components: dict[str, str] = {}
    for row in elements:
        if row.get("type") != "source_component":
            continue
        cid, ref = row.get("source_component_id"), row.get("name")
        if not isinstance(cid, str) or not isinstance(ref, str) or not ref:
            _fail("circuit: source_component lacks stable id/name")
        if cid in components or ref in components.values():
            _fail(f"circuit: duplicate component identity {cid!r}/{ref!r}")
        components[cid] = ref
    if not components:
        _fail("circuit: observed zero source components")

    parent: dict[str, str] = {}
    def find(item: str) -> str:
        parent.setdefault(item, item)
        if parent[item] != item:
            parent[item] = find(parent[item])
        return parent[item]
    def union(items: Sequence[str]) -> None:
        items = [item for item in items if item]
        if not items:
            return
        root = find(items[0])
        for item in items[1:]:
            parent[find(item)] = root

    net_names: dict[str, str] = {}
    seen_net_ids: set[str] = set()
    for row in elements:
        if row.get("type") != "source_net":
            continue
        nid = row.get("source_net_id")
        sub, key = row.get("subcircuit_id"), row.get("subcircuit_connectivity_map_key")
        name = row.get("name") or row.get("source_net_id")
        if not isinstance(nid, str) or not nid:
            _fail("circuit: source_net lacks a stable id")
        if nid in seen_net_ids:
            _fail(f"circuit: duplicate source_net id {nid!r}")
        seen_net_ids.add(nid)
        if isinstance(name, str) and name:
            net_names[f"net:{nid}"] = name
            if isinstance(sub, str) and isinstance(key, str):
                union((f"net:{nid}", f"key:{sub}:{key}"))

    source_ports: dict[str, Mapping[str, Any]] = {}
    for row in elements:
        if row.get("type") == "source_port":
            pid = row.get("source_port_id")
            if not isinstance(pid, str) or not pid:
                _fail("circuit: source_port lacks a stable id")
            if pid in source_ports:
                _fail(f"circuit: duplicate source_port id {pid!r}")
            source_ports[pid] = row
    source_net_ids = {row.get("source_net_id") for row in elements
                      if row.get("type") == "source_net"}
    traced_ports: set[str] = set()
    for row in elements:
        if row.get("type") != "source_trace":
            continue
        connected_ports = row.get("connected_source_port_ids", [])
        connected_nets = row.get("connected_source_net_ids", [])
        if (not isinstance(connected_ports, list) or
                any(not isinstance(value, str) for value in connected_ports)):
            _fail("circuit: source_trace connected_source_port_ids must be a string list")
        if (not isinstance(connected_nets, list) or
                any(not isinstance(value, str) for value in connected_nets)):
            _fail("circuit: source_trace connected_source_net_ids must be a string list")
        for pid in connected_ports:
            if pid not in source_ports:
                _fail(f"circuit: source_trace references unknown port {pid!r}")
            traced_ports.add(pid)
        for nid in connected_nets:
            if nid not in source_net_ids:
                _fail(f"circuit: source_trace references unknown net {nid!r}")

    ports: dict[str, str] = {}
    for pid, row in source_ports.items():
        pid, cid, pin = row.get("source_port_id"), row.get("source_component_id"), row.get("pin_number")
        if cid not in components:
            _fail(f"circuit: source_port references unknown component {cid!r}")
        if pin is None:
            if pid in traced_ports:
                _fail(f"circuit: connected source_port {pid!r} lacks pin_number")
            continue
        if (isinstance(pin, bool) or
                not ((isinstance(pin, int) and pin > 0) or
                     (isinstance(pin, str) and pin.strip() == pin and pin and
                      not any(char.isspace() for char in pin)))):
            _fail(f"circuit: source_port {pid!r} has unsupported pin_number {pin!r}")
        if not isinstance(pid, str):
            _fail("circuit: connected source_port lacks an id")
        ports[pid] = f"{components[cid]}.{pin}"
        sub, key = row.get("subcircuit_id"), row.get("subcircuit_connectivity_map_key")
        if isinstance(sub, str) and isinstance(key, str):
            union((f"port:{pid}", f"key:{sub}:{key}"))

    for row in elements:
        if row.get("type") != "source_trace":
            continue
        identities = [f"port:{pid}" for pid in row.get("connected_source_port_ids", [])]
        identities += [f"net:{nid}" for nid in row.get("connected_source_net_ids", [])]
        sub, key = row.get("subcircuit_id"), row.get("subcircuit_connectivity_map_key")
        if isinstance(sub, str) and isinstance(key, str):
            identities.append(f"key:{sub}:{key}")
        union(identities)

    endpoints: dict[str, set[str]] = defaultdict(set)
    group_names: dict[str, set[str]] = defaultdict(set)
    for identity, name in net_names.items():
        group_names[find(identity)].add(name)
    for names in group_names.values():
        if len(names) > 1:
            _fail(f"circuit: connectivity joins differently named nets {sorted(names)}")
    name_roots: dict[str, set[str]] = defaultdict(set)
    for root, names in group_names.items():
        for name in names:
            name_roots[name].add(root)
    for name, roots in name_roots.items():
        if len(roots) > 1:
            _fail(f"circuit: net name {name!r} identifies multiple disconnected nets")
    for pid, endpoint in ports.items():
        root = find(f"port:{pid}")
        names = group_names.get(root)
        if names:
            net = next(iter(names))
        else:
            keys = sorted(item.removeprefix("key:") for item in parent if item.startswith("key:") and find(item) == root)
            net = keys[0] if keys else f"unnamed:{root}"
        endpoints[net].add(endpoint)
    return {"refs": sorted(components.values()),
            "nets": {net: sorted(pads) for net, pads in sorted(endpoints.items())}}


def _parse_plan(plan: Any) -> dict[str, Any]:
    plan = _exact(plan, {"schema", "stage_id", "blocks", "interfaces",
                         "shared_responsibilities", "work_items"}, "plan")
    if plan["schema"] != SCHEMA or isinstance(plan["schema"], bool):
        _fail("plan.schema: only schema 1 is supported")
    if plan["stage_id"] not in STAGE_IDS:
        _fail(f"plan.stage_id: expected one of {sorted(STAGE_IDS)}")

    blocks: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(_list(plan["blocks"], "plan.blocks", nonempty=True)):
        row = _exact(raw, {"id", "refs", "responsibilities"}, f"blocks[{index}]")
        bid = _token(row["id"], f"blocks[{index}].id")
        if bid in blocks:
            _fail(f"blocks: duplicate id {bid}")
        blocks[bid] = {"id": bid,
                       "refs": _strings(row["refs"], f"blocks[{index}].refs", nonempty=True, pattern=REF),
                       "responsibilities": _strings(row["responsibilities"], f"blocks[{index}].responsibilities", nonempty=True)}

    shared = []
    for index, raw in enumerate(_list(plan["shared_responsibilities"], "plan.shared_responsibilities", nonempty=True)):
        row = _exact(raw, {"id", "owner", "requirements"}, f"shared_responsibilities[{index}]")
        sid = _token(row["id"], f"shared_responsibilities[{index}].id")
        owner = row["owner"]
        if owner != "board_integration" and owner not in blocks:
            _fail(f"shared_responsibilities[{index}].owner: unknown owner {owner!r}")
        shared.append({"id": sid, "owner": owner,
                       "requirements": _strings(row["requirements"], f"shared_responsibilities[{index}].requirements", nonempty=True)})
    if len({row["id"] for row in shared}) != len(shared):
        _fail("shared_responsibilities: duplicate id")

    interfaces = []
    for index, raw in enumerate(_list(plan["interfaces"], "plan.interfaces")):
        row = _exact(raw, {"net", "endpoints", "requirements", "disposition"}, f"interfaces[{index}]")
        net = row["net"]
        if not isinstance(net, str) or not net:
            _fail(f"interfaces[{index}].net: expected non-empty text")
        eps = row["endpoints"]
        if not isinstance(eps, Mapping) or len(eps) < 2:
            _fail(f"interfaces[{index}].endpoints: expected at least two block mappings")
        parsed_eps = {}
        for bid, values in eps.items():
            if bid not in blocks:
                _fail(f"interfaces[{index}].endpoints: unknown block {bid!r}")
            parsed_eps[bid] = _strings(values, f"interfaces[{index}].endpoints.{bid}",
                                       nonempty=True, pattern=ENDPOINT)
        interfaces.append({"net": net, "endpoints": parsed_eps,
                           "requirements": _strings(row["requirements"], f"interfaces[{index}].requirements", nonempty=True),
                           "disposition": str(row["disposition"]).strip()})
        if not interfaces[-1]["disposition"]:
            _fail(f"interfaces[{index}].disposition: expected non-empty text")
    if len({row["net"] for row in interfaces}) != len(interfaces):
        _fail("interfaces: each crossing net must have one combined disposition")

    items: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(_list(plan["work_items"], "plan.work_items", nonempty=True)):
        row = _exact(raw, {"id", "phase", "stage_id", "blocks", "depends_on",
                           "max_attempts", "backtrack_to", "evidence"}, f"work_items[{index}]")
        wid = _token(row["id"], f"work_items[{index}].id")
        if wid in items:
            _fail(f"work_items: duplicate id {wid}")
        phase, stage = row["phase"], row["stage_id"]
        if phase not in PHASE_RANK:
            _fail(f"work_items[{index}].phase: expected one of {list(PHASES)}")
        if stage not in STAGE_IDS:
            _fail(f"work_items[{index}].stage_id: unknown existing stage")
        if stage != "KICAD-PLACEMENT":
            _fail(f"work_items[{index}].stage_id: P1-P5 child work stays inside KICAD-PLACEMENT")
        owned = _strings(row["blocks"], f"work_items[{index}].blocks", nonempty=True)
        if any(bid not in blocks for bid in owned):
            _fail(f"work_items[{index}].blocks: unknown block")
        attempts = row["max_attempts"]
        if not isinstance(attempts, int) or isinstance(attempts, bool) or not 1 <= attempts <= 3:
            _fail(f"work_items[{index}].max_attempts: expected integer 1..3")
        items[wid] = {"id": wid, "phase": phase, "stage_id": stage, "blocks": owned,
                      "depends_on": _strings(row["depends_on"], f"work_items[{index}].depends_on"),
                      "max_attempts": attempts,
                      "backtrack_to": _strings(row["backtrack_to"], f"work_items[{index}].backtrack_to"),
                      "evidence": _paths(row["evidence"], f"work_items[{index}].evidence", nonempty=True)}
    for item in items.values():
        for dependency in item["depends_on"]:
            if dependency not in items:
                _fail(f"work item {item['id']}: unknown dependency {dependency}")
            if PHASE_RANK[items[dependency]["phase"]] > PHASE_RANK[item["phase"]]:
                _fail(f"work item {item['id']}: dependency {dependency} is from a later phase")
        for target in item["backtrack_to"]:
            if target not in items:
                _fail(f"work item {item['id']}: unknown backtrack target {target}")
            if PHASE_RANK[items[target]["phase"]] >= PHASE_RANK[item["phase"]]:
                _fail(f"work item {item['id']}: backtrack target {target} is not earlier")
    _acyclic(items)
    all_blocks = set(blocks)
    p1 = [row for row in items.values() if row["phase"] == "P1_FLOORPLAN"]
    if len(p1) != 1 or set(p1[0]["blocks"]) != all_blocks:
        _fail("work_items: exactly one P1 floorplan covering every block is required")
    p2_blocks = {bid for row in items.values() if row["phase"] == "P2_BLOCK_PLACEMENT" for bid in row["blocks"]}
    if p2_blocks != all_blocks:
        _fail("work_items: P2 placement work must cover every block")
    for row in items.values():
        if row["phase"] == "P4_JOINT_PROOF" and len(row["blocks"]) < 2:
            _fail(f"work item {row['id']}: P4 joint proof needs at least two blocks")
    p5 = [row for row in items.values() if row["phase"] == "P5_INTEGRATED_PLACEMENT_REVIEW"]
    if len(p5) != 1 or set(p5[0]["blocks"]) != all_blocks:
        _fail("work_items: exactly one P5 integrated placement review covering every block is required")
    required_ids = set(items) - {p5[0]["id"]}
    if not required_ids.issubset(_ancestors(p5[0]["id"], items)):
        _fail("work_items: P5 must depend transitively on every prior work item")
    return {"stage_id": plan["stage_id"], "blocks": blocks, "interfaces": interfaces,
            "shared_responsibilities": shared, "work_items": items}


def _acyclic(items: Mapping[str, Mapping[str, Any]]) -> None:
    visiting, done = set(), set()
    def visit(wid: str) -> None:
        if wid in visiting:
            _fail(f"work_items: dependency cycle at {wid}")
        if wid in done:
            return
        visiting.add(wid)
        for dep in items[wid]["depends_on"]:
            visit(dep)
        visiting.remove(wid); done.add(wid)
    for wid in items:
        visit(wid)


def _ancestors(wid: str, items: Mapping[str, Mapping[str, Any]]) -> set[str]:
    result = set(items[wid]["depends_on"])
    for dep in tuple(result):
        result.update(_ancestors(dep, items))
    return result


def work_subject(plan: Any, circuit: Any):
    """Return the existing two-part identity used by task-attempt receipts."""
    plan_bytes = json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()
    circuit_bytes = json.dumps(circuit, sort_keys=True, separators=(",", ":")).encode()
    return subject_identity("modular_work", 1, (
        TypedIdentityInput("block_plan", "mapping", plan, plan_bytes),
        TypedIdentityInput("circuit", "sequence" if isinstance(circuit, list) else "mapping",
                           circuit, circuit_bytes),
    ))


def _work_order(items: Mapping[str, Mapping[str, Any]]) -> list[str]:
    remaining, done, ordered = set(items), set(), []
    while remaining:
        ready = [wid for wid in remaining if set(items[wid]["depends_on"]) <= done]
        if not ready:
            _fail("work_items: dependency graph could not be ordered")
        wid = min(ready, key=lambda item: (PHASE_RANK[items[item]["phase"]], item))
        remaining.remove(wid); done.add(wid); ordered.append(wid)
    return ordered


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reopen_regular(root: Path, relative: str, where: str) -> Path:
    root = root.resolve()
    path = root / relative
    current = root
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            _fail(f"{where}: symlink is forbidden: {relative}")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        _fail(f"{where}: missing path {relative!r}: {exc}")
    if not resolved.is_relative_to(root) or not resolved.is_file():
        _fail(f"{where}: path is not a regular file below evidence_root: {relative}")
    return resolved


def evaluate(plan: Any, circuit: Any, observations: Sequence[Mapping[str, Any]] = (),
             *, evidence_root: Path | None = None) -> dict[str, Any]:
    parsed, observed = _parse_plan(plan), observe_circuit(circuit)
    subject = work_subject(plan, circuit)
    owners: dict[str, list[str]] = defaultdict(list)
    for bid, block in parsed["blocks"].items():
        for ref in block["refs"]:
            owners[ref].append(bid)
    findings: list[str] = []
    for ref in observed["refs"]:
        if len(owners.get(ref, ())) != 1:
            findings.append(f"component {ref}: expected exactly one owner, observed {owners.get(ref, [])}")
    for ref in sorted(set(owners) - set(observed["refs"])):
        findings.append(f"component {ref}: declared but absent from circuit census")

    actual: dict[str, dict[str, list[str]]] = {}
    for net, endpoints in observed["nets"].items():
        by_block: dict[str, list[str]] = defaultdict(list)
        for endpoint in endpoints:
            ref = endpoint.rsplit(".", 1)[0]
            if len(owners.get(ref, ())) == 1:
                by_block[owners[ref][0]].append(endpoint)
        if len(by_block) > 1:
            actual[net] = {bid: sorted(rows) for bid, rows in sorted(by_block.items())}
    declared = {row["net"]: {bid: list(endpoints) for bid, endpoints in row["endpoints"].items()}
                for row in parsed["interfaces"]}
    for net in sorted(set(actual) | set(declared)):
        if net not in actual:
            findings.append(f"interface {net}: declared but is not an observed cross-block net")
        elif net not in declared:
            findings.append(f"interface {net}: observed crossing omitted; endpoints={actual[net]}")
        elif declared[net] != actual[net]:
            findings.append(f"interface {net}: endpoint coverage differs; expected={actual[net]} declared={declared[net]}")

    obs_by_item: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for index, row in enumerate(observations):
        row = _exact(row, {"attempt_path"}, f"observations[{index}]")
        relative = row["attempt_path"]
        if evidence_root is None:
            _fail("observations require evidence_root to reopen TaskAttempt files")
        if not isinstance(relative, str) or Path(relative).is_absolute() or ".." in Path(relative).parts:
            _fail(f"observations[{index}].attempt_path: expected safe relative path")
        attempt_path = _reopen_regular(evidence_root, relative, f"observations[{index}]")
        try:
            raw_attempt = json.loads(attempt_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            _fail(f"observations[{index}]: cannot reopen TaskAttempt: {exc}")
        try:
            attempt = TaskAttempt.from_mapping(raw_attempt)
        except ExecutionValidationError as exc:
            _fail(f"observations[{index}]: invalid TaskAttempt: {exc}")
        wid = attempt.task_id
        if wid not in parsed["work_items"]:
            _fail(f"observations[{index}]: unknown work item {wid!r}")
        if attempt.subject != subject:
            _fail(f"observations[{index}]: stale subject for work item {wid}")
        completion = attempt.output.get("completion") if isinstance(attempt.output, Mapping) else None
        evidence: tuple[str, ...] = ()
        if completion is None:
            if attempt.status == "PASS":
                _fail(f"observations[{index}]: passing TaskAttempt has no completion")
        else:
            if (not isinstance(completion, Mapping) or completion.get("schema") != 1 or
                    not isinstance(completion.get("outputs"), Mapping)):
                _fail(f"observations[{index}]: malformed schema-1 completion")
            evidence = tuple(sorted(name for name in completion["outputs"] if name != "result.json"))
            for name, record in completion["outputs"].items():
                if not isinstance(record, Mapping) or set(record) != {"sha256", "size"}:
                    _fail(f"observations[{index}]: malformed completion record {name!r}")
                output_relative = (attempt_path.parent.relative_to(evidence_root.resolve()) / "outputs" / name).as_posix()
                output_path = _reopen_regular(evidence_root, output_relative, f"observations[{index}]")
                if _sha256(output_path) != record["sha256"] or output_path.stat().st_size != record["size"]:
                    _fail(f"observations[{index}]: stale or missing completed output {name!r}")
        identity = (attempt.replacement_index, attempt.attempt_index)
        if any(row["identity"] == identity for row in obs_by_item[wid]):
            _fail(f"observations: duplicate attempt identity for {wid}: {identity}")
        obs_by_item[wid].append({"status": attempt.status, "evidence": evidence,
                                 "attempt_index": attempt.attempt_index, "identity": identity})
    for rows in obs_by_item.values():
        rows.sort(key=lambda row: row["identity"])
    work = {}
    completed = set()
    for wid in _work_order(parsed["work_items"]):
        item = parsed["work_items"][wid]
        attempts = obs_by_item.get(wid, [])
        last = attempts[-1]["status"] if attempts else None
        deps_missing = sorted(set(item["depends_on"]) - completed)
        evidence_seen = set(attempts[-1]["evidence"]) if attempts else set()
        evidence_missing = sorted(set(item["evidence"]) - evidence_seen)
        if len(attempts) > item["max_attempts"]:
            state = "ATTEMPT_LIMIT_EXCEEDED"
        elif deps_missing:
            state = "BLOCKED"
        elif last == "PASS" and not evidence_missing:
            state = "WORK_RECORDED"
            completed.add(wid)
        elif len(attempts) >= item["max_attempts"] and last != "PASS":
            state = "BACKTRACK_REQUIRED"
        else:
            state = "READY"
        work[wid] = {"phase": item["phase"], "state": state,
                     "attempts": len(attempts), "max_attempts": item["max_attempts"],
                     "blocked_by": deps_missing, "missing_evidence": evidence_missing,
                     "backtrack_to": list(item["backtrack_to"]),
                     "engineering_acceptance": "NOT_EVALUATED"}
    return {"schema": SCHEMA, "status": "PASS" if not findings else "FAIL",
            "stage_id": parsed["stage_id"],
            "coverage": {"components_observed": len(observed["refs"]),
                         "components_singly_owned": sum(len(owners.get(ref, ())) == 1 for ref in observed["refs"]),
                         "crossing_nets_observed": len(actual),
                         "crossing_nets_exactly_declared": sum(net in declared and declared[net] == rows for net, rows in actual.items()),
                         "shared_responsibilities": len(parsed["shared_responsibilities"])},
            "findings": findings, "observed_crossings": actual, "work": work,
            "claim_limit": "Work progress only; no placement, route, geometry, gate-reuse, or lifecycle acceptance."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("circuit", type=Path)
    parser.add_argument("--observations", type=Path)
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text())
        circuit = json.loads(args.circuit.read_text())
        observations = json.loads(args.observations.read_text()) if args.observations else []
        result = evaluate(plan, circuit, observations, evidence_root=args.evidence_root)
    except (OSError, json.JSONDecodeError, ModularDesignError) as exc:
        print(f"MODULAR DESIGN: ERROR: {exc}")
        return 2
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.write_text(text)
    print(f"MODULAR DESIGN: {result['status']} ({result['coverage']['components_singly_owned']}/{result['coverage']['components_observed']} components; {result['coverage']['crossing_nets_exactly_declared']}/{result['coverage']['crossing_nets_observed']} crossings)")
    for finding in result["findings"]:
        print(f"- {finding}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
