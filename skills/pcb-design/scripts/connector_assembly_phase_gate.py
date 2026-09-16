#!/usr/bin/env python3
"""Grade connector facts at the source or full physical-qualification phase.

This is an additive wrapper around ``connector_assembly_contract.py``.  It
never changes or relabels the base receipt.  ``source`` may admit only unknown
facts explicitly classified by the separately bound phase policy as physical
qualification work.  ``full`` requires the base receipt itself to be PASS
with zero unknowns.  Schema, identity, path, or stale-input defects exit 1;
represented phase incompleteness exits 2.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

import connector_assembly_contract as base


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
RECEIPT_KIND = "connector-assembly-phase-gate-receipt"
RECEIPT_SCHEMA = 1
POLICY_ID = "connector-phase-policy-v1"
DEFAULT_POLICY = Path("03_src/rules/connector_assembly_phases.yaml")
DEFAULT_BASE_RECEIPT = Path(
    "06_build/verification/connector_assembly_contract.json")
DEFAULT_SOURCE_OUTPUT = Path(
    "06_build/verification/connector_assembly_source_gate.json")
DEFAULT_FULL_OUTPUT = Path(
    "06_build/verification/connector_assembly_full_gate.json")

ContractError = base.ContractError

_PHASES = frozenset({"source", "full"})
_ALLOWED_CLASSES = {
    "interface": "realized-interface-fit",
    "reaction": "reaction-qualification",
    "operation": "simultaneous-operation-qualification",
    "cable": "installed-cable-route-qualification",
    "tolerance": "installed-tolerance-qualification",
}
_UNKNOWN_PATH = re.compile(
    r"^assemblies\[(\d+)\]\.([a-z_]+)(?:\[(\d+)\])?\.evidence$")


class _StrictLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: _StrictLoader, node: yaml.Node,
                       deep: bool = False) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise ContractError("YAML mapping keys must be scalar") from exc
        if duplicate:
            raise ContractError(f"duplicate YAML key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _exact_mapping(value: Any, keys: set[str], where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{where}: expected mapping")
    actual = set(value)
    if actual != keys or not all(isinstance(key, str) for key in actual):
        raise ContractError(
            f"{where}: exact schema violation missing={sorted(keys - actual)} "
            f"unknown={sorted(actual - keys, key=str)}")
    return value


def _string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ContractError(f"{where}: expected non-empty trimmed string")
    return value


def _strict_json(raw: bytes, where: str) -> Mapping[str, Any]:
    try:
        text = raw.decode("utf-8")

        def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            value: dict[str, Any] = {}
            for key, item in pairs:
                if key in value:
                    raise ContractError(f"{where}: duplicate JSON key {key!r}")
                value[key] = item
            return value

        value = json.loads(text, object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"{where}: cannot parse strict UTF-8 JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ContractError(f"{where}: expected JSON object")
    return value


def _load_yaml(project: Path, path: Path, where: str) -> tuple[Mapping[str, Any], dict[str, Any]]:
    binding, raw = base._ordinary_file(project, path, where)  # noqa: SLF001
    try:
        value = yaml.load(raw.decode("utf-8"), Loader=_StrictLoader)
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError(f"{where}: cannot parse strict UTF-8 YAML: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ContractError(f"{where}: expected YAML mapping")
    return value, binding


def _load_base_receipt(project: Path, receipt_path: Path,
                       contract_path: Path) -> tuple[Mapping[str, Any], dict[str, Any]]:
    binding, raw = base._ordinary_file(  # noqa: SLF001
        project, receipt_path, "base receipt")
    receipt = _strict_json(raw, "base receipt")
    valid, findings = base.validate_receipt(
        receipt, project, expected_contract_path=contract_path)
    if not valid:
        raise ContractError("base receipt is stale or invalid: " + "; ".join(findings))
    return receipt, binding


def _gate_binding() -> dict[str, Any]:
    raw = SCRIPT_PATH.read_bytes()
    try:
        relative = SCRIPT_PATH.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:  # pragma: no cover - installation invariant
        raise ContractError("phase gate is outside repository root") from exc
    return {"path": relative, "sha256": _digest(raw), "size": len(raw)}


def _target_table(document: Mapping[str, Any]) -> tuple[
        dict[tuple[str, str, str], Mapping[str, Any]],
        dict[str, tuple[str, str, str]],
]:
    assemblies = document.get("assemblies")
    if not isinstance(assemblies, list):
        raise ContractError("contract.assemblies: expected list")
    targets: dict[tuple[str, str, str], Mapping[str, Any]] = {}
    paths: dict[str, tuple[str, str, str]] = {}
    for assembly_index, raw_assembly in enumerate(assemblies):
        assembly = _exact_mapping(
            raw_assembly,
            {"id", "instances", "receptacle", "mate", "interface", "grip",
             "fastening", "tool", "torque", "reaction", "cable",
             "operations", "tolerances"},
            f"contract.assemblies[{assembly_index}]",
        )
        assembly_id = _string(assembly["id"], f"assemblies[{assembly_index}].id")
        for kind in (
                "receptacle", "mate", "interface", "grip", "fastening",
                "tool", "torque", "reaction", "cable"):
            target = assembly[kind]
            if not isinstance(target, Mapping):
                raise ContractError(
                    f"assemblies[{assembly_index}].{kind}: expected mapping")
            key = (assembly_id, kind, kind)
            targets[key] = target
            paths[f"assemblies[{assembly_index}].{kind}.evidence"] = key
        for plural, kind in (("operations", "operation"),
                             ("tolerances", "tolerance")):
            rows = assembly[plural]
            if not isinstance(rows, list):
                raise ContractError(
                    f"assemblies[{assembly_index}].{plural}: expected list")
            for row_index, row in enumerate(rows):
                if not isinstance(row, Mapping):
                    raise ContractError(
                        f"assemblies[{assembly_index}].{plural}[{row_index}]: "
                        "expected mapping")
                target_id = _string(
                    row.get("id"),
                    f"assemblies[{assembly_index}].{plural}[{row_index}].id")
                key = (assembly_id, kind, target_id)
                if key in targets:
                    raise ContractError(f"phase target: duplicate stable identity {key}")
                targets[key] = row
                paths[
                    f"assemblies[{assembly_index}].{plural}[{row_index}].evidence"
                ] = key
    return targets, paths


def _evidence(target: Mapping[str, Any], where: str) -> Mapping[str, Any]:
    value = target.get("evidence")
    if not isinstance(value, Mapping):
        raise ContractError(f"{where}.evidence: expected mapping")
    return value


def _parse_policy(document: Mapping[str, Any],
                  targets: Mapping[tuple[str, str, str], Mapping[str, Any]]) -> tuple[
                      str, dict[tuple[str, str, str], dict[str, Any]]]:
    root = _exact_mapping(
        document, {"schema", "phase_policy_id", "source_deferrals"},
        "phase policy")
    if root["schema"] != 1 or isinstance(root["schema"], bool):
        raise ContractError("phase policy.schema: only schema 1 is supported")
    authored_id = _string(root["phase_policy_id"], "phase policy.phase_policy_id")
    rows = root["source_deferrals"]
    if not isinstance(rows, list):
        raise ContractError("phase policy.source_deferrals: expected list")
    result: dict[tuple[str, str, str], dict[str, Any]] = {}
    for index, raw in enumerate(rows):
        row = _exact_mapping(
            raw,
            {"assembly_id", "target_kind", "target_id", "unknown_class",
             "plan_source_ids", "rationale"},
            f"phase policy.source_deferrals[{index}]",
        )
        assembly_id = _string(
            row["assembly_id"], f"source_deferrals[{index}].assembly_id")
        target_kind = _string(
            row["target_kind"], f"source_deferrals[{index}].target_kind")
        target_id = _string(
            row["target_id"], f"source_deferrals[{index}].target_id")
        unknown_class = _string(
            row["unknown_class"], f"source_deferrals[{index}].unknown_class")
        expected_class = _ALLOWED_CLASSES.get(target_kind)
        if expected_class is None or unknown_class != expected_class:
            raise ContractError(
                f"source_deferrals[{index}]: class/path mismatch; "
                f"{target_kind!r} requires {expected_class!r}")
        key = (assembly_id, target_kind, target_id)
        if key not in targets:
            raise ContractError(
                f"source_deferrals[{index}]: unknown stable target {key}")
        if key in result:
            raise ContractError(
                f"source_deferrals[{index}]: duplicate stable target {key}")
        plan_source_ids = row["plan_source_ids"]
        if (not isinstance(plan_source_ids, list) or not plan_source_ids or
                any(not isinstance(item, str) or not item.strip()
                    for item in plan_source_ids) or
                len(plan_source_ids) != len(set(plan_source_ids))):
            raise ContractError(
                f"source_deferrals[{index}].plan_source_ids: expected non-empty "
                "unique string list")
        evidence = _evidence(targets[key], f"phase target {key}")
        target_sources = evidence.get("source_ids")
        if not isinstance(target_sources, list):
            raise ContractError(f"phase target {key}.evidence.source_ids: expected list")
        missing_sources = sorted(set(plan_source_ids) - set(target_sources))
        if missing_sources:
            raise ContractError(
                f"source_deferrals[{index}].plan_source_ids: not cited by target "
                f"evidence: {missing_sources}")
        result[key] = {
            "unknown_class": unknown_class,
            "plan_source_ids": sorted(plan_source_ids),
            "rationale": _string(
                row["rationale"], f"source_deferrals[{index}].rationale"),
        }
    return authored_id, result


def _source_prerequisite_finding(
        key: tuple[str, str, str], target: Mapping[str, Any]) -> str | None:
    _assembly_id, kind, _target_id = key
    evidence = _evidence(target, f"phase target {key}")
    source_ids = evidence.get("source_ids")
    if not isinstance(source_ids, list) or not source_ids:
        return "unknown physical qualification has no bound plan evidence"
    if kind == "interface":
        value = target.get("orientation_source_id")
        if not isinstance(value, str) or not value.strip():
            return "realized interface deferral lacks typed orientation authority"
    elif kind == "reaction":
        for field in ("method", "load_path"):
            value = target.get(field)
            if not isinstance(value, str) or not value.strip():
                return f"reaction qualification lacks selected {field}"
    elif kind == "cable":
        for field in ("kind", "manufacturer", "mpn", "exit"):
            value = target.get(field)
            if not isinstance(value, str) or not value.strip():
                return f"installed cable-route qualification lacks selected {field}"
    elif kind == "tolerance":
        applies_to = target.get("applies_to")
        if (not isinstance(applies_to, str) or
                not applies_to.startswith(("installed_", "realized_"))):
            return (
                "unknown tolerance is not typed as an installed_/realized_ "
                "physical stack")
        if target.get("minus_mm") is not None or target.get("plus_mm") is not None:
            return "unknown installed tolerance must not smuggle numeric bounds"
    return None


def _census(base_receipt: Mapping[str, Any]) -> dict[str, Any]:
    assemblies = base_receipt.get("assemblies")
    groups = base_receipt.get("simultaneous_groups")
    if not isinstance(assemblies, list) or not isinstance(groups, list):
        raise ContractError("base receipt: malformed connector populations")
    assembly_ids: list[str] = []
    refs: list[str] = []
    for assembly in assemblies:
        if not isinstance(assembly, Mapping):
            raise ContractError("base receipt.assemblies: malformed row")
        assembly_ids.append(_string(assembly.get("id"), "base assembly id"))
        instances = assembly.get("instances")
        if not isinstance(instances, list):
            raise ContractError("base receipt assembly.instances: expected list")
        for instance in instances:
            if not isinstance(instance, Mapping):
                raise ContractError("base receipt instance: expected mapping")
            refs.append(_string(instance.get("ref"), "base connector ref"))
    group_ids = [
        _string(group.get("id"), "base simultaneous group id")
        for group in groups if isinstance(group, Mapping)
    ]
    if len(group_ids) != len(groups):
        raise ContractError("base receipt.simultaneous_groups: malformed row")
    if len(refs) != len(set(refs)):
        raise ContractError("base receipt census: duplicate connector refs")
    return {
        "assembly_ids": sorted(assembly_ids),
        "refs": sorted(refs),
        "simultaneous_group_ids": sorted(group_ids),
    }


def _identity_findings(base_receipt: Mapping[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for assembly in base_receipt.get("assemblies", []):
        assembly_id = str(assembly.get("id", "<missing>"))
        for kind in ("receptacle", "mate"):
            value = assembly.get(kind)
            if not isinstance(value, Mapping):
                findings.append({
                    "code": "SOURCE-IDENTITY",
                    "path": f"assembly:{assembly_id}/{kind}",
                    "message": "selected connector identity is absent",
                })
                continue
            identity_ok = all(
                isinstance(value.get(field), str) and value[field].strip()
                for field in ("manufacturer", "mpn"))
            evidence = value.get("evidence")
            evidence_ok = (isinstance(evidence, Mapping) and
                           evidence.get("grade") in {"exact", "conservative"})
            if not identity_ok or not evidence_ok:
                findings.append({
                    "code": "SOURCE-IDENTITY",
                    "path": f"assembly:{assembly_id}/{kind}",
                    "message": (
                        "source phase requires nonempty selected manufacturer/MPN "
                        "and non-unknown identity evidence"),
                })
    return findings


def grade_phase(
        base_receipt: Mapping[str, Any], contract_document: Mapping[str, Any],
        phase_policy_document: Mapping[str, Any], phase: str,
) -> dict[str, Any]:
    """Purely classify a validated base receipt for one explicit phase."""
    if phase not in _PHASES:
        raise ContractError(f"phase: expected one of {sorted(_PHASES)}")
    if base_receipt.get("kind") != base.RECEIPT_KIND or \
            base_receipt.get("schema") != base.RECEIPT_SCHEMA:
        raise ContractError("base receipt: kind/schema mismatch")
    targets, path_targets = _target_table(contract_document)
    authored_policy_id, policy = _parse_policy(phase_policy_document, targets)
    census = _census(base_receipt)
    base_status = base_receipt.get("status")
    if base_status == "N-A":
        if census["refs"] or base_receipt.get("unknowns"):
            raise ContractError("base N-A receipt has a nonempty census or unknowns")
        return {
            "phase_policy_id": authored_policy_id,
            "status": "N-A",
            "census": census,
            "unknowns": [],
            "findings": [],
        }
    if not census["refs"]:
        raise ContractError("operated connector census is empty")

    findings = _identity_findings(base_receipt)
    stable_unknowns: list[dict[str, Any]] = []
    raw_unknowns = base_receipt.get("unknowns")
    if not isinstance(raw_unknowns, list):
        raise ContractError("base receipt.unknowns: expected list")
    for index, raw in enumerate(raw_unknowns):
        if not isinstance(raw, Mapping):
            raise ContractError(f"base receipt.unknowns[{index}]: expected mapping")
        path = _string(raw.get("path"), f"base unknowns[{index}].path")
        rationale = _string(
            raw.get("rationale"), f"base unknowns[{index}].rationale")
        key = path_targets.get(path)
        if key is None:
            if not _UNKNOWN_PATH.fullmatch(path):
                raise ContractError(f"base unknown path is not phase-addressable: {path}")
            raise ContractError(
                f"base unknown path does not resolve to a stable target: {path}")
        target = targets[key]
        deferral = policy.get(key)
        expected_class = _ALLOWED_CLASSES.get(key[1])
        source_allowed = False
        message: str | None = None
        if deferral is None:
            message = "unknown fact has no typed source-phase deferral"
            unknown_class = "unclassified"
        else:
            unknown_class = deferral["unknown_class"]
            if expected_class != unknown_class:
                raise ContractError(
                    f"phase policy class/path mismatch for stable target {key}")
            message = _source_prerequisite_finding(key, target)
            source_allowed = message is None
        row = {
            "assembly_id": key[0],
            "target_kind": key[1],
            "target_id": key[2],
            "unknown_class": unknown_class,
            "path": path,
            "rationale": rationale,
            "source_allowed": source_allowed,
        }
        stable_unknowns.append(row)
        if phase == "source" and not source_allowed:
            findings.append({
                "code": "SOURCE-UNKNOWN",
                "path": f"assembly:{key[0]}/{key[1]}:{key[2]}",
                "message": message or "unknown is not source-admissible",
            })
        if phase == "full":
            findings.append({
                "code": "FULL-UNKNOWN",
                "path": f"assembly:{key[0]}/{key[1]}:{key[2]}",
                "message": "full phase requires the base receipt to contain no unknowns",
            })

    if phase == "full" and (base_status != "PASS" or stable_unknowns):
        if not stable_unknowns:
            findings.append({
                "code": "FULL-BASE-STATUS",
                "path": "base.status",
                "message": "full phase requires base status PASS",
            })
    status = "PASS" if not findings else "INCOMPLETE"
    return {
        "phase_policy_id": authored_policy_id,
        "status": status,
        "census": census,
        "unknowns": sorted(
            stable_unknowns,
            key=lambda row: (row["assembly_id"], row["target_kind"],
                             row["target_id"]),
        ),
        "findings": sorted(
            findings, key=lambda row: (row["code"], row["path"], row["message"])),
    }


def compile_phase_gate(
        project: str | Path, *, phase: str,
        expected_contract_path: str | Path = base.DEFAULT_CONTRACT,
        phase_policy_path: str | Path = DEFAULT_POLICY,
        base_receipt_path: str | Path = DEFAULT_BASE_RECEIPT,
) -> dict[str, Any]:
    """Compile a deterministic phase receipt from a freshly validated base."""
    root = base._project_directory(Path(project))  # noqa: SLF001
    contract_path = Path(expected_contract_path)
    base_receipt, base_binding = _load_base_receipt(
        root, Path(base_receipt_path), contract_path)
    contract_document, _contract_binding = _load_yaml(
        root, contract_path, "connector contract")
    phase_policy_document, phase_policy_binding = _load_yaml(
        root, Path(phase_policy_path), "connector phase policy")
    grade = grade_phase(
        base_receipt, contract_document, phase_policy_document, phase)
    authority = {
        "phase_policy_id": grade["phase_policy_id"],
        "contract_path": base_receipt["inputs"]["contract"]["path"],
        "base_kind": base_receipt["kind"],
        "base_schema": base_receipt["schema"],
        "base_status": base_receipt["status"],
        "base_semantic_sha256": base_receipt["semantic_sha256"],
        "base_subject_sha256": base_receipt["subject_sha256"],
    }
    inputs = {
        "base_receipt": base_binding,
        "base_inputs": base_receipt["inputs"],
        "phase_policy": phase_policy_binding,
        "phase_gate": _gate_binding(),
    }
    summary = {
        "assembly_count": len(grade["census"]["assembly_ids"]),
        "instance_count": len(grade["census"]["refs"]),
        "simultaneous_group_count": len(
            grade["census"]["simultaneous_group_ids"]),
        "base_unknown_count": len(grade["unknowns"]),
        "source_admitted_unknown_count": sum(
            1 for row in grade["unknowns"] if row["source_allowed"]),
        "finding_count": len(grade["findings"]),
    }
    semantic = {
        "phase": phase,
        "policy_id": POLICY_ID,
        "authority": authority,
        "status": grade["status"],
        "census": grade["census"],
        "unknowns": grade["unknowns"],
        "findings": grade["findings"],
        "summary": summary,
    }
    semantic_sha256 = _digest(_canonical_bytes(semantic))
    subject_sha256 = _digest(_canonical_bytes({
        "semantic_sha256": semantic_sha256,
        "base_subject_sha256": base_receipt["subject_sha256"],
        "inputs": inputs,
    }))
    return {
        "kind": RECEIPT_KIND,
        "schema": RECEIPT_SCHEMA,
        "phase": phase,
        "policy_id": POLICY_ID,
        "status": grade["status"],
        "authority": authority,
        "inputs": inputs,
        "census": grade["census"],
        "unknowns": grade["unknowns"],
        "findings": grade["findings"],
        "summary": summary,
        "semantic_sha256": semantic_sha256,
        "subject_sha256": subject_sha256,
    }


def validate_phase_gate(
        receipt: Mapping[str, Any], project: str | Path, *, expected_phase: str,
        expected_contract_path: str | Path = base.DEFAULT_CONTRACT,
        expected_phase_policy_path: str | Path = DEFAULT_POLICY,
        expected_base_receipt_path: str | Path = DEFAULT_BASE_RECEIPT,
) -> tuple[bool, list[str]]:
    """Reopen all inputs and require the caller-selected phase and exact bytes."""
    if expected_phase not in _PHASES:
        return False, [f"expected_phase: expected one of {sorted(_PHASES)}"]
    if not isinstance(receipt, Mapping):
        return False, ["phase receipt: expected mapping"]
    expected_keys = {
        "kind", "schema", "phase", "policy_id", "status", "authority",
        "inputs", "census", "unknowns", "findings", "summary",
        "semantic_sha256", "subject_sha256",
    }
    if set(receipt) != expected_keys:
        return False, [
            "phase receipt: exact schema violation "
            f"missing={sorted(expected_keys - set(receipt))} "
            f"unknown={sorted(set(receipt) - expected_keys, key=str)}"
        ]
    if receipt.get("kind") != RECEIPT_KIND or \
            receipt.get("schema") != RECEIPT_SCHEMA:
        return False, ["phase receipt: kind/schema mismatch"]
    if receipt.get("phase") != expected_phase:
        return False, [
            f"phase receipt: phase {receipt.get('phase')!r} does not match "
            f"caller-required {expected_phase!r}"]
    if receipt.get("policy_id") != POLICY_ID:
        return False, ["phase receipt: compiler-owned policy_id mismatch"]
    try:
        current = compile_phase_gate(
            project, phase=expected_phase,
            expected_contract_path=expected_contract_path,
            phase_policy_path=expected_phase_policy_path,
            base_receipt_path=expected_base_receipt_path,
        )
    except ContractError as exc:
        return False, [f"phase receipt source reopen failed: {exc}"]
    if _canonical_bytes(dict(receipt)) == _canonical_bytes(current):
        return True, []
    findings: list[str] = []
    for key in expected_keys:
        if receipt.get(key) != current.get(key):
            findings.append(f"phase receipt.{key}: differs from freshly compiled value")
    return False, sorted(findings) or ["phase receipt: deterministic payload differs"]


def regrade_phase_gate(
        receipt_path: str | Path, project: str | Path, *, expected_phase: str,
        expected_contract_path: str | Path = base.DEFAULT_CONTRACT,
        expected_phase_policy_path: str | Path = DEFAULT_POLICY,
        expected_base_receipt_path: str | Path = DEFAULT_BASE_RECEIPT,
) -> tuple[bool, list[str]]:
    try:
        root = base._project_directory(Path(project))  # noqa: SLF001
        _binding, raw = base._ordinary_file(  # noqa: SLF001
            root, Path(receipt_path), "phase receipt")
        receipt = _strict_json(raw, "phase receipt")
    except ContractError as exc:
        return False, [f"phase receipt: cannot load: {exc}"]
    return validate_phase_gate(
        receipt, root, expected_phase=expected_phase,
        expected_contract_path=expected_contract_path,
        expected_phase_policy_path=expected_phase_policy_path,
        expected_base_receipt_path=expected_base_receipt_path,
    )


def _write_receipt(
        project: Path, output: Path, receipt: Mapping[str, Any], *,
        expected_phase: str, expected_contract_path: Path,
        expected_phase_policy_path: Path, expected_base_receipt_path: Path,
) -> Path:
    candidate, _relative = base._project_path(  # noqa: SLF001
        project, output, "phase output")
    protected = {
        base._absolute_lexical(  # noqa: SLF001
            project / Path(receipt["inputs"]["base_receipt"]["path"])),
        base._absolute_lexical(  # noqa: SLF001
            project / Path(receipt["inputs"]["phase_policy"]["path"])),
        base._absolute_lexical(SCRIPT_PATH),  # noqa: SLF001
    }
    base_inputs = receipt["inputs"]["base_inputs"]
    protected.add(base._absolute_lexical(  # noqa: SLF001
        project / Path(base_inputs["contract"]["path"])))
    protected.add(base._absolute_lexical(  # noqa: SLF001
        REPO_ROOT / Path(base_inputs["compiler"]["path"])))
    protected.update(
        base._absolute_lexical(project / Path(row["path"]))  # noqa: SLF001
        for row in base_inputs["evidence_files"])
    if candidate in protected:
        raise ContractError("phase output aliases a governed input")
    base._reject_symlink_components(  # noqa: SLF001
        candidate.parent, "phase output parent", allow_missing_tail=True)
    candidate.parent.mkdir(parents=True, exist_ok=True)
    base._reject_symlink_components(  # noqa: SLF001
        candidate.parent, "phase output parent")
    parent_stat = candidate.parent.lstat()
    if not stat.S_ISDIR(parent_stat.st_mode) or stat.S_ISLNK(parent_stat.st_mode):
        raise ContractError("phase output parent: expected ordinary directory")
    if not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW"):
        raise ContractError("phase output: platform lacks no-follow publication support")
    directory_fd = os.open(
        candidate.parent,
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
        (os.O_CLOEXEC if hasattr(os, "O_CLOEXEC") else 0),
    )
    temporary_name: str | None = None
    published_identity: tuple[int, int] | None = None
    payload = (json.dumps(
        receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")

    def remove_own_output() -> None:
        if published_identity is None:
            return
        try:
            current = os.stat(candidate.name, dir_fd=directory_fd,
                              follow_symlinks=False)
        except FileNotFoundError:
            return
        if (current.st_dev, current.st_ino) == published_identity:
            os.unlink(candidate.name, dir_fd=directory_fd)
            os.fsync(directory_fd)

    try:
        existing: os.stat_result | None
        try:
            existing = os.stat(candidate.name, dir_fd=directory_fd,
                               follow_symlinks=False)
        except FileNotFoundError:
            existing = None
        if existing is not None and (
                not stat.S_ISREG(existing.st_mode) or stat.S_ISLNK(existing.st_mode) or
                existing.st_nlink != 1):
            raise ContractError("phase output: existing target is not an ordinary file")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        if hasattr(os, "O_CLOEXEC"):
            flags |= os.O_CLOEXEC
        for _ in range(128):
            temporary_name = f".{candidate.name}.{secrets.token_hex(12)}.tmp"
            try:
                descriptor = os.open(
                    temporary_name, flags, 0o600, dir_fd=directory_fd)
                break
            except FileExistsError:
                continue
        else:  # pragma: no cover
            raise ContractError("phase output: cannot allocate temporary file")
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        staged = os.stat(temporary_name, dir_fd=directory_fd,
                         follow_symlinks=False)
        published_identity = (staged.st_dev, staged.st_ino)
        os.replace(temporary_name, candidate.name,
                   src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        temporary_name = None
        os.fsync(directory_fd)
        valid, findings = validate_phase_gate(
            receipt, project, expected_phase=expected_phase,
            expected_contract_path=expected_contract_path,
            expected_phase_policy_path=expected_phase_policy_path,
            expected_base_receipt_path=expected_base_receipt_path,
        )
        if not valid:
            remove_own_output()
            raise ContractError(
                "inputs changed during phase receipt publication: " +
                "; ".join(findings))
        read_flags = os.O_RDONLY | os.O_NOFOLLOW
        if hasattr(os, "O_CLOEXEC"):
            read_flags |= os.O_CLOEXEC
        descriptor = os.open(candidate.name, read_flags, dir_fd=directory_fd)
        try:
            current = os.fstat(descriptor)
            if (current.st_dev, current.st_ino) != published_identity:
                raise ContractError("phase output changed during publication")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
        finally:
            os.close(descriptor)
        if b"".join(chunks) != payload:
            remove_own_output()
            raise ContractError("published phase receipt bytes differ")
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name, dir_fd=directory_fd)
            except FileNotFoundError:
                pass
        os.close(directory_fd)
    return candidate


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--phase", choices=sorted(_PHASES), required=True)
    parser.add_argument("--contract", type=Path, default=base.DEFAULT_CONTRACT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--base-receipt", type=Path, default=DEFAULT_BASE_RECEIPT)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    output = args.output or (
        DEFAULT_SOURCE_OUTPUT if args.phase == "source" else DEFAULT_FULL_OUTPUT)
    try:
        project = base._project_directory(args.project)  # noqa: SLF001
        receipt = compile_phase_gate(
            project, phase=args.phase,
            expected_contract_path=args.contract,
            phase_policy_path=args.policy,
            base_receipt_path=args.base_receipt,
        )
        valid, findings = validate_phase_gate(
            receipt, project, expected_phase=args.phase,
            expected_contract_path=args.contract,
            expected_phase_policy_path=args.policy,
            expected_base_receipt_path=args.base_receipt,
        )
        if not valid:
            raise ContractError(
                "inputs changed before phase receipt publication: " +
                "; ".join(findings))
        written = _write_receipt(
            project, Path(output), receipt,
            expected_phase=args.phase,
            expected_contract_path=args.contract,
            expected_phase_policy_path=args.policy,
            expected_base_receipt_path=args.base_receipt,
        )
    except (ContractError, OSError) as exc:
        print(f"CONNECTOR-PHASE FAIL: {exc}", file=sys.stderr)
        return 1
    summary = receipt["summary"]
    print(
        f"CONNECTOR-PHASE {args.phase.upper()} {receipt['status']} "
        f"assemblies={summary['assembly_count']} "
        f"instances={summary['instance_count']} "
        f"base_unknown={summary['base_unknown_count']} "
        f"source_admitted={summary['source_admitted_unknown_count']} "
        f"findings={summary['finding_count']} output={written}")
    return 0 if receipt["status"] in {"PASS", "N-A"} else 2


if __name__ == "__main__":
    sys.exit(main())
