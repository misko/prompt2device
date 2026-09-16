#!/usr/bin/env python3
"""Prepare and grade a source-bound physical connector qualification coupon.

The PCB connector phase gate deliberately stops before routing when installed
fit, cable, reaction, operation, or tolerance facts are unknown.  This tool
turns that pause into an executable workflow without relabeling it:

``prepare``
    Reopens the canonical connector contract and source-phase classification,
    copies every operated connector plus the declared board-only datums onto a
    full-outline, same-layer-count, same-thickness mechanical coupon, proves
    normalized pad/courtyard/edge geometry equality, exports bare-board Gerbers
    and drills, and emits a hash-bound physical-test response template.

``grade``
    Reopens the request, source board, coupon board, package artifacts, exact
    hardware/sample/instrument census, measurements, and every evidence file.
    Missing observations are ``INCOMPLETE`` (exit 2), represented negative
    results are ``FAIL`` (exit 1), and only complete positive evidence is
    ``PASS`` (exit 0).

``verify``
    Deterministically recompiles a published grade receipt against current
    inputs and requires byte-for-byte semantic equality.

A PASS receipt is evidence, not a bypass.  The project must cite it from the
ordinary connector contract, fill the measured fields there, and recompile the
base receipt before CONNECTOR-FULL can pass.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path
from typing import Any, Mapping, Sequence

import pcbnew
import yaml

import connector_assembly_contract as base
import connector_assembly_phase_gate as phase


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
REQUEST_KIND = "connector-qualification-coupon-request"
REQUEST_SCHEMA = 1
RESPONSE_KIND = "connector-qualification-coupon-response"
RESPONSE_SCHEMA = 1
RECEIPT_KIND = "connector-qualification-coupon-receipt"
RECEIPT_SCHEMA = 1
DEFAULT_CONFIG = Path("03_src/connector_qualification_coupon.yaml")
DEFAULT_OUT = Path("06_build/connector_qualification_coupon/current")
_RESULTS = frozenset({"PASS", "FAIL", "UNOBSERVED"})
_EVIDENCE_KINDS = frozenset({
    "photo", "video", "measurement_sheet", "continuity_log",
    "calibration_record", "lot_label", "datasheet", "other",
})
_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+-]*$")
_PLACEHOLDER = re.compile(r"^(?:replace|todo|tbd|unknown|unobserved|n/?a)?$", re.I)
_MECHANICAL_DRC_TYPES = frozenset({
    "courtyards_overlap", "npth_inside_courtyard", "solder_mask_bridge",
    "drilled_holes_too_close", "hole_clearance", "copper_edge_clearance",
    "malformed_courtyard", "invalid_outline",
})

ContractError = base.ContractError


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


def _binding_bytes(path: Path, relative: str | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": relative if relative is not None else path.as_posix(),
        "sha256": _digest(data),
        "size": len(data),
    }


def _exact(value: Any, keys: set[str], where: str) -> Mapping[str, Any]:
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


def _concrete(value: Any, where: str) -> str:
    result = _string(value, where)
    if _PLACEHOLDER.fullmatch(result):
        raise ContractError(f"{where}: placeholder text is not evidence")
    return result


def _identifier(value: Any, where: str) -> str:
    return base._identifier(value, where)  # noqa: SLF001


def _finite(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{where}: expected finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ContractError(f"{where}: expected finite number")
    return result


def _strict_yaml(project: Path, path: Path,
                 where: str) -> tuple[Mapping[str, Any], dict[str, Any]]:
    binding, raw = base._ordinary_file(project, path, where)  # noqa: SLF001
    try:
        value = yaml.load(raw.decode("utf-8"), Loader=_StrictLoader)
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError(f"{where}: invalid strict UTF-8 YAML: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ContractError(f"{where}: expected YAML mapping")
    return value, binding


def _strict_json(project: Path, path: Path,
                 where: str) -> tuple[Mapping[str, Any], dict[str, Any]]:
    binding, raw = base._ordinary_file(project, path, where)  # noqa: SLF001
    try:
        def reject(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            out: dict[str, Any] = {}
            for key, item in pairs:
                if key in out:
                    raise ContractError(f"{where}: duplicate JSON key {key!r}")
                out[key] = item
            return out
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=reject)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"{where}: invalid strict UTF-8 JSON: {exc}") from exc
    if not isinstance(value, Mapping):
        raise ContractError(f"{where}: expected JSON object")
    return value, binding


def _ordinary_directory(project: Path, raw: str,
                        where: str) -> tuple[Path, str]:
    path, relative = base._project_path(project, Path(raw), where)  # noqa: SLF001
    base._reject_symlink_components(path, where)  # noqa: SLF001
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise ContractError(f"{where}: cannot inspect {relative}: {exc}") from exc
    if not stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
        raise ContractError(f"{where}: expected ordinary directory")
    return path, relative


def _natural(value: str) -> tuple[Any, ...]:
    return tuple(int(part) if part.isdigit() else part
                 for part in re.split(r"(\d+)", value))


def _unique_strings(value: Any, where: str, *, ids: bool = False,
                    nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        raise ContractError(f"{where}: expected {'non-empty ' if nonempty else ''}list")
    result = [(_identifier(item, f"{where}[{index}]") if ids
               else _string(item, f"{where}[{index}]"))
              for index, item in enumerate(value)]
    if len(result) != len(set(result)):
        raise ContractError(f"{where}: duplicate values are forbidden")
    return result


def _parse_config(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _exact(document, {
        "schema", "coupon_id", "source_board", "connector_contract",
        "phase_policy", "base_receipt", "board_only_refs",
        "local_footprint_libraries", "fabrication", "qualification",
    }, "config")
    if root["schema"] != 1 or isinstance(root["schema"], bool):
        raise ContractError("config.schema: only schema 1 is supported")
    coupon_id = _identifier(root["coupon_id"], "config.coupon_id")
    paths = {
        key: Path(_string(root[key], f"config.{key}"))
        for key in ("source_board", "connector_contract", "phase_policy",
                    "base_receipt")
    }
    board_only_refs = _unique_strings(
        root["board_only_refs"], "config.board_only_refs", nonempty=True)

    libraries = root["local_footprint_libraries"]
    if not isinstance(libraries, Mapping) or not libraries:
        raise ContractError(
            "config.local_footprint_libraries: expected non-empty mapping")
    local_libraries: dict[str, str] = {}
    for name, path in libraries.items():
        name = _string(name, "config.local_footprint_libraries key")
        if not _SAFE_NAME.fullmatch(name):
            raise ContractError(
                f"config.local_footprint_libraries: unsafe library name {name!r}")
        local_libraries[name] = _string(
            path, f"config.local_footprint_libraries.{name}")

    fab = _exact(root["fabrication"], {
        "copper_layers", "pcb_thickness_mm", "surface_finish",
        "soldermask", "silkscreen", "population_method",
        "accepted_drc_warning_types",
    }, "config.fabrication")
    layers = fab["copper_layers"]
    if isinstance(layers, bool) or not isinstance(layers, int) or layers < 2:
        raise ContractError("config.fabrication.copper_layers: expected integer >= 2")
    thickness = _finite(
        fab["pcb_thickness_mm"], "config.fabrication.pcb_thickness_mm")
    if thickness <= 0:
        raise ContractError("config.fabrication.pcb_thickness_mm: expected > 0")
    accepted_warnings = _unique_strings(
        fab["accepted_drc_warning_types"],
        "config.fabrication.accepted_drc_warning_types")
    fabrication = {
        "copper_layers": layers,
        "pcb_thickness_mm": thickness,
        "surface_finish": _string(
            fab["surface_finish"], "config.fabrication.surface_finish"),
        "soldermask": _string(fab["soldermask"], "config.fabrication.soldermask"),
        "silkscreen": _string(fab["silkscreen"], "config.fabrication.silkscreen"),
        "population_method": _string(
            fab["population_method"], "config.fabrication.population_method"),
        "accepted_drc_warning_types": sorted(accepted_warnings),
    }

    qual = _exact(root["qualification"], {
        "minimum_samples", "required_sample_evidence_kinds",
        "required_instrument_roles", "target_hardware", "targets",
    }, "config.qualification")
    minimum_samples = qual["minimum_samples"]
    if not isinstance(minimum_samples, Mapping) or not minimum_samples:
        raise ContractError(
            "config.qualification.minimum_samples: expected non-empty mapping")
    sample_counts: dict[str, int] = {}
    for assembly_id, count in minimum_samples.items():
        aid = _identifier(assembly_id, "minimum_samples assembly_id")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ContractError(f"minimum_samples.{aid}: expected integer >= 1")
        sample_counts[aid] = count
    sample_kinds = _unique_strings(
        qual["required_sample_evidence_kinds"],
        "config.qualification.required_sample_evidence_kinds", nonempty=True)
    if unknown := sorted(set(sample_kinds) - _EVIDENCE_KINDS):
        raise ContractError(f"required_sample_evidence_kinds: unknown {unknown}")
    instrument_roles = _unique_strings(
        qual["required_instrument_roles"],
        "config.qualification.required_instrument_roles", ids=True,
        nonempty=True)

    target_hardware: list[dict[str, str]] = []
    if not isinstance(qual["target_hardware"], list):
        raise ContractError("config.qualification.target_hardware: expected list")
    hardware_keys: set[tuple[str, str]] = set()
    for index, raw in enumerate(qual["target_hardware"]):
        item = _exact(raw, {"assembly_id", "role", "manufacturer", "product"},
                      f"target_hardware[{index}]")
        row = {
            "assembly_id": _identifier(item["assembly_id"], f"target_hardware[{index}].assembly_id"),
            "role": _identifier(item["role"], f"target_hardware[{index}].role"),
            "manufacturer": _string(item["manufacturer"], f"target_hardware[{index}].manufacturer"),
            "product": _string(item["product"], f"target_hardware[{index}].product"),
        }
        key = (row["assembly_id"], row["role"])
        if key in hardware_keys:
            raise ContractError(f"target_hardware[{index}]: duplicate {key}")
        hardware_keys.add(key)
        target_hardware.append(row)

    targets: list[dict[str, Any]] = []
    target_keys: set[tuple[str, str, str]] = set()
    if not isinstance(qual["targets"], list) or not qual["targets"]:
        raise ContractError("config.qualification.targets: expected non-empty list")
    for index, raw in enumerate(qual["targets"]):
        item = _exact(raw, {
            "assembly_id", "target_kind", "target_id",
            "required_measurements", "required_evidence_kinds",
        }, f"targets[{index}]")
        key = (
            _identifier(item["assembly_id"], f"targets[{index}].assembly_id"),
            _identifier(item["target_kind"], f"targets[{index}].target_kind"),
            _identifier(item["target_id"], f"targets[{index}].target_id"),
        )
        if key in target_keys:
            raise ContractError(f"targets[{index}]: duplicate stable target {key}")
        target_keys.add(key)
        measurements: list[dict[str, Any]] = []
        measurement_names: set[str] = set()
        if not isinstance(item["required_measurements"], list) or not item["required_measurements"]:
            raise ContractError(
                f"targets[{index}].required_measurements: expected non-empty list")
        for mindex, raw_measurement in enumerate(item["required_measurements"]):
            measure = _exact(raw_measurement, {"name", "unit", "minimum", "maximum"},
                             f"targets[{index}].required_measurements[{mindex}]")
            name = _identifier(measure["name"], f"measurement[{mindex}].name")
            if name in measurement_names:
                raise ContractError(f"targets[{index}]: duplicate measurement {name}")
            measurement_names.add(name)
            minimum = (None if measure["minimum"] is None else
                       _finite(measure["minimum"], f"measurement[{mindex}].minimum"))
            maximum = (None if measure["maximum"] is None else
                       _finite(measure["maximum"], f"measurement[{mindex}].maximum"))
            if minimum is not None and maximum is not None and minimum > maximum:
                raise ContractError(f"measurement {name}: minimum exceeds maximum")
            measurements.append({
                "name": name,
                "unit": _string(measure["unit"], f"measurement[{mindex}].unit"),
                "minimum": minimum,
                "maximum": maximum,
            })
        evidence_kinds = _unique_strings(
            item["required_evidence_kinds"],
            f"targets[{index}].required_evidence_kinds", nonempty=True)
        if unknown := sorted(set(evidence_kinds) - _EVIDENCE_KINDS):
            raise ContractError(f"targets[{index}].required_evidence_kinds: unknown {unknown}")
        targets.append({
            "assembly_id": key[0], "target_kind": key[1], "target_id": key[2],
            "required_measurements": sorted(measurements, key=lambda row: row["name"]),
            "required_evidence_kinds": sorted(evidence_kinds),
        })

    return {
        "schema": 1, "coupon_id": coupon_id, **paths,
        "board_only_refs": sorted(board_only_refs, key=_natural),
        "local_footprint_libraries": dict(sorted(local_libraries.items())),
        "fabrication": fabrication,
        "qualification": {
            "minimum_samples": dict(sorted(sample_counts.items())),
            "required_sample_evidence_kinds": sorted(sample_kinds),
            "required_instrument_roles": sorted(instrument_roles),
            "target_hardware": sorted(
                target_hardware, key=lambda row: (row["assembly_id"], row["role"])),
            "targets": sorted(
                targets, key=lambda row: (
                    row["assembly_id"], row["target_kind"], row["target_id"])),
        },
    }


def _script_binding() -> dict[str, Any]:
    data = SCRIPT_PATH.read_bytes()
    try:
        relative = SCRIPT_PATH.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:  # pragma: no cover
        raise ContractError("coupon producer/verifier is outside repository root") from exc
    return {"path": relative, "sha256": _digest(data), "size": len(data)}


def _load_context(project: Path, config_path: Path) -> dict[str, Any]:
    raw_config, config_binding = _strict_yaml(project, config_path, "coupon config")
    config = _parse_config(raw_config)
    source_board_binding, _ = base._ordinary_file(  # noqa: SLF001
        project, config["source_board"], "source board")
    base_receipt, base_binding = _strict_json(
        project, config["base_receipt"], "base connector receipt")
    valid, findings = base.validate_receipt(
        base_receipt, project, expected_contract_path=config["connector_contract"])
    if not valid:
        raise ContractError("base connector receipt is stale: " + "; ".join(findings))
    source_phase = phase.compile_phase_gate(
        project, phase="source",
        expected_contract_path=config["connector_contract"],
        phase_policy_path=config["phase_policy"],
        base_receipt_path=config["base_receipt"],
    )
    if source_phase["status"] != "PASS" or not source_phase["unknowns"]:
        raise ContractError(
            "coupon requires a source-phase PASS with a nonempty physical unknown census")
    unknown_keys = {
        (row["assembly_id"], row["target_kind"], row["target_id"])
        for row in source_phase["unknowns"]
    }
    config_keys = {
        (row["assembly_id"], row["target_kind"], row["target_id"])
        for row in config["qualification"]["targets"]
    }
    if unknown_keys != config_keys:
        raise ContractError(
            "config.qualification.targets must exactly cover the source-phase "
            f"physical unknown census; missing={sorted(unknown_keys - config_keys)} "
            f"extra={sorted(config_keys - unknown_keys)}")
    assembly_ids = {row["id"] for row in base_receipt["assemblies"]}
    sample_ids = set(config["qualification"]["minimum_samples"])
    if sample_ids != assembly_ids:
        raise ContractError(
            "config.qualification.minimum_samples must exactly cover assemblies; "
            f"missing={sorted(assembly_ids - sample_ids)} "
            f"extra={sorted(sample_ids - assembly_ids)}")
    for row in config["qualification"]["target_hardware"]:
        if row["assembly_id"] not in assembly_ids:
            raise ContractError(
                f"target_hardware names unknown assembly {row['assembly_id']!r}")

    libraries: list[dict[str, Any]] = []
    for name, raw_path in config["local_footprint_libraries"].items():
        directory, relative = _ordinary_directory(
            project, raw_path, f"local footprint library {name}")
        files = []
        for entry in sorted(directory.glob("*.kicad_mod")):
            binding, _ = base._ordinary_file(  # noqa: SLF001
                project, Path(entry.relative_to(project)),
                f"local footprint library {name} member")
            files.append(binding)
        if not files:
            raise ContractError(f"local footprint library {name}: contains no .kicad_mod files")
        libraries.append({"name": name, "path": relative, "files": files})
    return {
        "config": config,
        "config_binding": config_binding,
        "source_board_binding": source_board_binding,
        "base_receipt": base_receipt,
        "base_binding": base_binding,
        "source_phase": source_phase,
        "libraries": libraries,
    }


def _canonical_ring(points: list[tuple[int, int]]) -> list[list[int]]:
    if points and points[0] == points[-1]:
        points = points[:-1]
    if not points:
        return []
    candidates = []
    for seq in (points, list(reversed(points))):
        for index in range(len(seq)):
            candidates.append(seq[index:] + seq[:index])
    best = min(candidates)
    return [[x, y] for x, y in best]


def _poly_rows(poly: Any) -> list[list[list[int]]]:
    rows = []
    for index in range(poly.OutlineCount()):
        outline = poly.Outline(index)
        rows.append(_canonical_ring([
            (outline.CPoint(point).x, outline.CPoint(point).y)
            for point in range(outline.PointCount())
        ]))
    return sorted(rows)


def _bbox_row(box: Any) -> list[int]:
    return [box.GetLeft(), box.GetTop(), box.GetRight(), box.GetBottom()]


def _footprint_geometry(board: Any, fp: Any) -> dict[str, Any]:
    courtyard_layer = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    courtyard = fp.GetCourtyard(courtyard_layer)
    pads = []
    for pad in fp.Pads():
        pads.append({
            "number": pad.GetNumber(),
            "position_nm": [pad.GetPosition().x, pad.GetPosition().y],
            "orientation_microdegrees": int(round(pad.GetOrientationDegrees() * 1_000_000)),
            "size_nm": [pad.GetSize().x, pad.GetSize().y],
            "drill_nm": [pad.GetDrillSize().x, pad.GetDrillSize().y],
            "offset_nm": [pad.GetOffset().x, pad.GetOffset().y],
            "shape": int(pad.GetShape()),
            "drill_shape": int(pad.GetDrillShape()),
            "attribute": int(pad.GetAttribute()),
            "layers": pad.GetLayerSet().FmtHex(),
        })
    models = []
    for model in fp.Models():
        models.append({
            "file": model.m_Filename,
            "offset": [model.m_Offset.x, model.m_Offset.y, model.m_Offset.z],
            "scale": [model.m_Scale.x, model.m_Scale.y, model.m_Scale.z],
            "rotation": [model.m_Rotation.x, model.m_Rotation.y, model.m_Rotation.z],
        })
    return {
        "ref": fp.GetReference(),
        "value": fp.GetValue(),
        "fpid": fp.GetFPID().GetUniStringLibId(),
        "position_nm": [fp.GetPosition().x, fp.GetPosition().y],
        "orientation_microdegrees": int(round(fp.GetOrientationDegrees() * 1_000_000)),
        "flipped": bool(fp.IsFlipped()),
        "attributes": int(fp.GetAttributes()),
        "body_bbox_nm": _bbox_row(fp.GetBoundingBox(False, False)),
        "courtyard": _poly_rows(courtyard),
        "pads": sorted(pads, key=lambda row: (_natural(row["number"]), row["position_nm"])),
        "models": sorted(models, key=lambda row: row["file"]),
    }


def _board_geometry(board: Any, connector_refs: list[str],
                    board_only_refs: list[str]) -> dict[str, Any]:
    wanted = set(connector_refs) | set(board_only_refs)
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()
                  if fp.GetReference() in wanted}
    if set(footprints) != wanted:
        raise ContractError(
            f"board geometry: missing refs {sorted(wanted - set(footprints), key=_natural)}")
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False) or not outline.OutlineCount():
        raise ContractError("board geometry: invalid or empty Edge.Cuts outline")
    outline_rows = _poly_rows(outline)
    flat = [point for ring in outline_rows for point in ring]
    bbox = [min(row[0] for row in flat), min(row[1] for row in flat),
            max(row[0] for row in flat), max(row[1] for row in flat)]
    pairs = []
    for index, left in enumerate(connector_refs):
        a = footprints[left].GetPosition()
        for right in connector_refs[index + 1:]:
            b = footprints[right].GetPosition()
            pairs.append({
                "refs": [left, right],
                "anchor_vector_nm": [b.x - a.x, b.y - a.y],
            })
    rows = [_footprint_geometry(board, footprints[ref])
            for ref in sorted(wanted, key=_natural)]
    return {
        "copper_layers": board.GetCopperLayerCount(),
        "pcb_thickness_nm": board.GetDesignSettings().GetBoardThickness(),
        "outline": outline_rows,
        "outline_bbox_nm": bbox,
        "footprints": rows,
        "connector_pair_vectors": pairs,
    }


def _assembly_rows(base_receipt: Mapping[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    connector_refs: list[str] = []
    rows: list[dict[str, Any]] = []
    for assembly in base_receipt["assemblies"]:
        refs = sorted((item["ref"] for item in assembly["instances"]), key=_natural)
        connector_refs.extend(refs)
        rows.append({
            "assembly_id": assembly["id"],
            "refs": refs,
            "receptacle": {
                key: assembly["receptacle"][key]
                for key in ("manufacturer", "mpn", "mounting_method")
            },
            "mate": {
                key: assembly["mate"][key]
                for key in ("manufacturer", "mpn", "part_kind")
            },
            "cable": {
                key: assembly["cable"][key]
                for key in ("manufacturer", "mpn", "kind")
            },
            "tool": {
                key: assembly["tool"][key]
                for key in ("kind", "identifier")
            },
        })
    if len(connector_refs) != len(set(connector_refs)):
        raise ContractError("connector contract contains duplicate instance refs")
    return sorted(connector_refs, key=_natural), sorted(rows, key=lambda row: row["assembly_id"])


def _copy_coupon(source: Any, output: Path, connector_refs: list[str],
                 board_only_refs: list[str], coupon_id: str) -> Any:
    pcbnew.KIID.SeedGenerator(zlib.crc32(coupon_id.encode("utf-8")))
    coupon = pcbnew.BOARD()
    coupon.SetCopperLayerCount(source.GetCopperLayerCount())
    coupon.GetDesignSettings().SetBoardThickness(
        source.GetDesignSettings().GetBoardThickness())
    wanted = set(connector_refs) | set(board_only_refs)
    copied: set[str] = set()
    for footprint in source.GetFootprints():
        ref = footprint.GetReference()
        if ref not in wanted:
            continue
        duplicate = pcbnew.Cast_to_FOOTPRINT(footprint.Duplicate(False))
        for pad in duplicate.Pads():
            pad.SetNetCode(0)
        coupon.Add(duplicate)
        copied.add(ref)
    if copied != wanted:
        raise ContractError(
            f"coupon copy: missing refs {sorted(wanted - copied, key=_natural)}")
    edge_count = 0
    for drawing in source.GetDrawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts:
            coupon.Add(drawing.Duplicate())
            edge_count += 1
    if not edge_count:
        raise ContractError("coupon copy: source has no Edge.Cuts primitives")
    coupon.Save(str(output))
    reopened = pcbnew.LoadBoard(str(output))
    if reopened is None:
        raise ContractError("coupon copy: pcbnew could not reopen saved coupon")
    return reopened


def _write_fp_lib_table(work: Path, source: Any, context: Mapping[str, Any]) -> None:
    local = {row["name"] for row in context["libraries"]}
    used = sorted({str(fp.GetFPID().GetLibNickname())
                   for fp in source.GetFootprints()
                   if str(fp.GetFPID().GetLibNickname())})
    major_match = re.match(r"\d+", pcbnew.Version())
    if not major_match:
        raise ContractError(f"cannot determine KiCad major from {pcbnew.Version()!r}")
    major = major_match.group()
    lines = ["(fp_lib_table", "  (version 7)"]
    for name in used:
        if not _SAFE_NAME.fullmatch(name):
            raise ContractError(f"unsafe footprint library nickname {name!r}")
        if name in local:
            uri = f"${{KIPRJMOD}}/libraries/{name}.pretty"
        else:
            uri = f"${{KICAD{major}_FOOTPRINT_DIR}}/{name}.pretty"
        lines.append(
            f'  (lib (name "{name}")(type "KiCad")(uri "{uri}")'
            f'(options "")(descr ""))')
    lines.append(")")
    (work / "fp-lib-table").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _copy_libraries(project: Path, work: Path,
                    context: Mapping[str, Any]) -> None:
    root = work / "libraries"
    root.mkdir()
    for library in context["libraries"]:
        dest = root / f"{library['name']}.pretty"
        dest.mkdir()
        for binding in library["files"]:
            source = project / binding["path"]
            (dest / source.name).write_bytes(source.read_bytes())


def _run(command: list[str], cwd: Path, what: str) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise ContractError(
            f"{what}: command exited {result.returncode}: "
            f"{(result.stdout + result.stderr)[-3000:]}")
    return result.stdout + result.stderr


def _project_argument(project: Path) -> str:
    try:
        return project.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return project.as_posix()


def _write_csvs(work: Path, assemblies: list[dict[str, Any]],
                population_method: str) -> None:
    with (work / "connector-population.csv").open(
            "w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "Assembly", "References", "Quantity", "Manufacturer", "MPN",
            "Mounting method", "Population method",
        ])
        for row in assemblies:
            writer.writerow([
                row["assembly_id"], " ".join(row["refs"]), len(row["refs"]),
                row["receptacle"]["manufacturer"], row["receptacle"]["mpn"],
                row["receptacle"]["mounting_method"], population_method,
            ])
    with (work / "qualification-hardware.csv").open(
            "w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "Assembly", "Role", "Manufacturer", "MPN", "Description",
        ])
        for row in assemblies:
            writer.writerow([
                row["assembly_id"], "mate", row["mate"]["manufacturer"],
                row["mate"]["mpn"], row["mate"]["part_kind"],
            ])
            writer.writerow([
                row["assembly_id"], "cable", row["cable"]["manufacturer"],
                row["cable"]["mpn"], row["cable"]["kind"],
            ])
            writer.writerow([
                row["assembly_id"], "installed tool", "",
                row["tool"]["identifier"] or "NONE", row["tool"]["kind"],
            ])


def _export_fabrication(work: Path, board_path: Path, layers: int) -> list[Path]:
    cli = shutil.which("kicad-cli")
    if not cli:
        raise ContractError("kicad-cli is required to export coupon fabrication files")
    fab = work / "fab"
    fab.mkdir()
    copper = ["F.Cu"] + [f"In{index}.Cu" for index in range(1, layers - 1)] + ["B.Cu"]
    plot_layers = copper + [
        "F.Silkscreen", "B.Silkscreen", "F.Mask", "B.Mask", "Edge.Cuts",
    ]
    _run([
        cli, "pcb", "export", "gerbers", "--no-netlist", "--layers",
        ",".join(plot_layers), "-o", str(fab), str(board_path),
    ], work, "Gerber export")
    _run([
        cli, "pcb", "export", "drill", "--excellon-separate-th", "-o",
        str(fab), str(board_path),
    ], work, "drill export")
    files = sorted(path for path in fab.iterdir() if path.is_file())
    suffixes = {path.suffix.lower() for path in files}
    required = {".gtl", ".gbl", ".gts", ".gbs", ".gm1", ".drl"}
    if missing := sorted(required - suffixes):
        raise ContractError(f"fabrication export: missing required suffixes {missing}")
    archive = work / f"{board_path.stem}_gerbers.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            info = zipfile.ZipInfo(path.name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, path.read_bytes())
    with zipfile.ZipFile(archive) as bundle:
        if bundle.namelist() != [path.name for path in files]:
            raise ContractError("fabrication archive member census differs from export")
    return files + [archive]


def _drc_summary(drc: Mapping[str, Any],
                 accepted_warning_types: list[str]) -> dict[str, Any]:
    violations = drc.get("violations")
    unconnected = drc.get("unconnected_items")
    if not isinstance(violations, list) or not isinstance(unconnected, list):
        raise ContractError("coupon DRC: missing violation/unconnected arrays")
    errors = [row for row in violations if row.get("severity") == "error"]
    mechanical = [row for row in violations if row.get("type") in _MECHANICAL_DRC_TYPES]
    warning_types = sorted({row.get("type") for row in violations
                            if row.get("severity") == "warning"})
    unexpected = sorted(set(warning_types) - set(accepted_warning_types))
    if errors or mechanical or unexpected or unconnected:
        raise ContractError(
            "coupon DRC is not fabrication-clean: "
            f"errors={len(errors)} mechanical={len(mechanical)} "
            f"unconnected={len(unconnected)} unexpected_warnings={unexpected}")
    return {
        "violation_count": len(violations),
        "error_count": len(errors),
        "mechanical_finding_count": len(mechanical),
        "unconnected_count": len(unconnected),
        "warning_types": warning_types,
        "accepted_warning_types": sorted(accepted_warning_types),
    }


def _run_drc_and_renders(work: Path, board_path: Path,
                         accepted_warning_types: list[str]) -> tuple[dict[str, Any], list[Path]]:
    cli = shutil.which("kicad-cli")
    if not cli:
        raise ContractError("kicad-cli is required to grade and render the coupon")
    drc_path = work / "drc.json"
    _run([
        cli, "pcb", "drc", "--severity-all", "--format", "json", "-o",
        str(drc_path), str(board_path),
    ], work, "coupon DRC")
    try:
        drc = json.loads(drc_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"coupon DRC: cannot parse JSON: {exc}") from exc
    summary = _drc_summary(drc, accepted_warning_types)
    render_paths = []
    for side in ("top", "front", "back"):
        output = work / f"render-{side}.png"
        _run([
            cli, "pcb", "render", "-o", str(output), "--side", side,
            "--quality", "high", "--width", "1600", "--height", "1000",
            str(board_path),
        ], work, f"coupon {side} render")
        if not output.is_file() or output.stat().st_size == 0:
            raise ContractError(f"coupon {side} render is empty")
        render_paths.append(output)
    return summary, [drc_path] + render_paths


def _artifact(path: Path, project: Path, final_root: Path,
              work: Path) -> dict[str, Any]:
    relative_inside = path.relative_to(work)
    final = final_root / relative_inside
    return _binding_bytes(path, final.relative_to(project).as_posix())


def _response_template(request: Mapping[str, Any], request_sha256: str,
                       config: Mapping[str, Any]) -> dict[str, Any]:
    observations = []
    for target in config["qualification"]["targets"]:
        observations.append({
            "assembly_id": target["assembly_id"],
            "target_kind": target["target_kind"],
            "target_id": target["target_id"],
            "result": "UNOBSERVED",
            "tested_refs": [],
            "measurements": [
                {"name": row["name"], "unit": row["unit"], "values": []}
                for row in target["required_measurements"]
            ],
            "evidence": [],
            "notes": "",
        })
    return {
        "schema": RESPONSE_SCHEMA,
        "kind": RESPONSE_KIND,
        "request_sha256": request_sha256,
        "coupon_id": config["coupon_id"],
        "target_hardware": [],
        "samples": [],
        "instruments": [],
        "observations": observations,
    }


def _qualification_rows(context: Mapping[str, Any],
                        assemblies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    target_lookup = {
        (row["assembly_id"], row["target_kind"], row["target_id"]): row
        for row in context["config"]["qualification"]["targets"]
    }
    refs_by_assembly = {
        row["assembly_id"]: row["refs"] for row in assemblies
    }
    targets = []
    for unknown in context["source_phase"]["unknowns"]:
        key = (unknown["assembly_id"], unknown["target_kind"], unknown["target_id"])
        required = target_lookup[key]
        targets.append({
            **{name: unknown[name] for name in (
                "assembly_id", "target_kind", "target_id", "unknown_class",
                "path", "rationale")},
            "required_refs": refs_by_assembly[key[0]],
            "required_measurements": required["required_measurements"],
            "required_evidence_kinds": required["required_evidence_kinds"],
        })
    return targets


def _write_readme(work: Path, config: Mapping[str, Any]) -> None:
    fab = config["fabrication"]
    (work / "README.md").write_text(
        f"# {config['coupon_id']} physical connector coupon\n\n"
        "This is a non-functional, connector-only qualification coupon. It is "
        "not the carrier PCB and must never be used as a product board.\n\n"
        "## Bare-board order\n\n"
        f"- Copper layers: {fab['copper_layers']}\n"
        f"- Finished thickness: {fab['pcb_thickness_mm']:.3f} mm\n"
        f"- Surface finish: {fab['surface_finish']}\n"
        f"- Soldermask / silkscreen: {fab['soldermask']} / {fab['silkscreen']}\n"
        f"- Population: {fab['population_method']} after bare-board fabrication\n"
        "- Upload the `*_gerbers.zip` archive for PCB fabrication only.\n"
        "- Do not upload a PCBA BOM/CPL: the connector population is deliberately "
        "hand-installed so exact lot identity and seating can be photographed.\n\n"
        "The coupon preserves the source carrier's complete outline, mounting "
        "holes, fiducials, connector anchors, footprint pad/hole geometry, layer "
        "count, and thickness. All signal pads are intentionally isolated.\n\n"
        "Populate only the exact parts in `connector-population.csv`, gather the "
        "exact mates/cables in `qualification-hardware.csv`, then fill "
        "`physical-response.yaml`. Run the grade command recorded in "
        "`request.json`; an unfilled template is intentionally INCOMPLETE.\n",
        encoding="utf-8")


def prepare(project_raw: Path, config_path: Path, out_path: Path) -> Path:
    project = base._project_directory(project_raw)  # noqa: SLF001
    context = _load_context(project, config_path)
    config = context["config"]
    project_argument = _project_argument(project)
    final_root, final_relative = base._project_path(project, out_path, "coupon output")  # noqa: SLF001
    base._reject_symlink_components(  # noqa: SLF001
        final_root.parent, "coupon output parent", allow_missing_tail=True)
    final_root.parent.mkdir(parents=True, exist_ok=True)
    base._reject_symlink_components(final_root.parent, "coupon output parent")  # noqa: SLF001
    if final_root.exists() or final_root.is_symlink():
        raise ContractError(
            f"coupon output already exists: {final_relative}; archive it before preparing a new subject")
    work: Path | None = Path(tempfile.mkdtemp(
        prefix=f".{config['coupon_id']}.", dir=final_root.parent))
    try:
        source_path = project / context["source_board_binding"]["path"]
        source = pcbnew.LoadBoard(str(source_path))
        if source is None:
            raise ContractError("source board: pcbnew could not load it")
        connector_refs, assemblies = _assembly_rows(context["base_receipt"])
        all_refs = [fp.GetReference() for fp in source.GetFootprints()]
        if len(all_refs) != len(set(all_refs)):
            raise ContractError("source board: duplicate footprint references")
        board_only = sorted(
            (fp.GetReference() for fp in source.GetFootprints()
             if fp.GetAttributes() & pcbnew.FP_BOARD_ONLY), key=_natural)
        if board_only != config["board_only_refs"]:
            raise ContractError(
                "config.board_only_refs differs from source board; "
                f"configured={config['board_only_refs']} actual={board_only}")
        by_ref = {fp.GetReference(): fp for fp in source.GetFootprints()}
        for assembly in assemblies:
            for ref in assembly["refs"]:
                if ref not in by_ref:
                    raise ContractError(f"source board is missing operated connector {ref}")
                if by_ref[ref].GetValue() != assembly["receptacle"]["mpn"]:
                    raise ContractError(
                        f"{ref}: board value {by_ref[ref].GetValue()!r} differs from "
                        f"contract receptacle MPN {assembly['receptacle']['mpn']!r}")
        if source.GetCopperLayerCount() != config["fabrication"]["copper_layers"]:
            raise ContractError("source board copper-layer count differs from coupon config")
        source_thickness = pcbnew.ToMM(source.GetDesignSettings().GetBoardThickness())
        if abs(source_thickness - config["fabrication"]["pcb_thickness_mm"]) > 1e-9:
            raise ContractError(
                "source board thickness differs from coupon config: "
                f"{source_thickness} != {config['fabrication']['pcb_thickness_mm']}")

        stem = config["coupon_id"]
        board_path = work / f"{stem}.kicad_pcb"
        coupon = _copy_coupon(source, board_path, connector_refs, board_only, stem)
        source_geometry = _board_geometry(source, connector_refs, board_only)
        coupon_geometry = _board_geometry(coupon, connector_refs, board_only)
        if source_geometry != coupon_geometry:
            raise ContractError(
                "coupon geometry differs from source connector/datum/outline geometry")

        source_project = source_path.with_suffix(".kicad_pro")
        source_project_binding, source_project_raw = base._ordinary_file(  # noqa: SLF001
            project, Path(source_project.relative_to(project)), "source KiCad project")
        (work / f"{stem}.kicad_pro").write_bytes(source_project_raw)
        _copy_libraries(project, work, context)
        _write_fp_lib_table(work, coupon, context)
        _write_csvs(work, assemblies, config["fabrication"]["population_method"])
        _write_readme(work, config)
        fab_paths = _export_fabrication(
            work, board_path, config["fabrication"]["copper_layers"])
        drc_summary, review_paths = _run_drc_and_renders(
            work, board_path,
            config["fabrication"]["accepted_drc_warning_types"])
        # KiCad render updates a per-user local preferences file beside the
        # board.  It is process state, not coupon content, and the repository
        # globally ignores it.  Never bind it into the portable request.
        local_preferences = work / f"{stem}.kicad_prl"
        if local_preferences.is_symlink():
            raise ContractError("coupon render created a symlinked local-preferences file")
        if local_preferences.exists():
            local_preferences.unlink()

        current_files = sorted(
            path for path in work.rglob("*") if path.is_file())
        artifacts = [_artifact(path, project, final_root, work)
                     for path in current_files]
        targets = _qualification_rows(context, assemblies)
        request = {
            "kind": REQUEST_KIND,
            "schema": REQUEST_SCHEMA,
            "status": "READY_FOR_FABRICATION",
            "coupon_id": config["coupon_id"],
            "inputs": {
                "config": context["config_binding"],
                "source_board": context["source_board_binding"],
                "source_kicad_project": source_project_binding,
                "base_receipt": context["base_binding"],
                "base_inputs": context["base_receipt"]["inputs"],
                "phase_policy": context["source_phase"]["inputs"]["phase_policy"],
                "phase_gate": context["source_phase"]["inputs"]["phase_gate"],
                "producer_verifier": _script_binding(),
                "local_footprint_libraries": context["libraries"],
            },
            "authority": {
                "base_semantic_sha256": context["base_receipt"]["semantic_sha256"],
                "base_subject_sha256": context["base_receipt"]["subject_sha256"],
                "source_phase_subject_sha256": context["source_phase"]["subject_sha256"],
            },
            "fabrication": config["fabrication"],
            "board": {
                "source": context["source_board_binding"],
                "coupon": _artifact(board_path, project, final_root, work),
                "connector_refs": connector_refs,
                "board_only_refs": board_only,
                "source_geometry_sha256": _digest(_canonical_bytes(source_geometry)),
                "coupon_geometry_sha256": _digest(_canonical_bytes(coupon_geometry)),
                "geometry": coupon_geometry,
            },
            "assemblies": assemblies,
            "qualification": {
                "minimum_samples": config["qualification"]["minimum_samples"],
                "required_sample_evidence_kinds": config["qualification"]["required_sample_evidence_kinds"],
                "required_instrument_roles": config["qualification"]["required_instrument_roles"],
                "target_hardware": config["qualification"]["target_hardware"],
                "targets": targets,
            },
            "drc": drc_summary,
            "artifacts": artifacts,
            "commands": {
                "grade": (
                    f"/usr/bin/python3 {SCRIPT_PATH.relative_to(REPO_ROOT).as_posix()} "
                    f"grade --project {project_argument} "
                    f"--request {final_relative}/request.json "
                    f"--response {final_relative}/physical-response.yaml "
                    f"--output {final_relative}/qualification-receipt.json"),
            },
            "summary": {
                "assembly_count": len(assemblies),
                "connector_count": len(connector_refs),
                "board_only_datum_count": len(board_only),
                "physical_target_count": len(targets),
                "artifact_count": len(artifacts),
                "gerber_or_drill_count": len(fab_paths),
                "review_artifact_count": len(review_paths),
            },
        }
        request_path = work / "request.json"
        request_path.write_text(
            json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        request_sha = _digest(request_path.read_bytes())
        template = _response_template(request, request_sha, config)
        (work / "physical-response.yaml").write_text(
            yaml.safe_dump(template, sort_keys=False), encoding="utf-8")
        checksummed = sorted(path for path in work.rglob("*") if path.is_file())
        (work / "SHA256SUMS").write_text(
            "".join(f"{_digest(path.read_bytes())}  {path.relative_to(work).as_posix()}\n"
                    for path in checksummed), encoding="utf-8")
        os.replace(work, final_root)
        work = None
        print(
            f"CONNECTOR-COUPON READY assemblies={len(assemblies)} "
            f"connectors={len(connector_refs)} datums={len(board_only)} "
            f"targets={len(targets)} geometry=EXACT drc_errors=0 "
            f"output={final_root}")
        return final_root
    finally:
        if work is not None and work.exists():
            shutil.rmtree(work)


def _validate_request_current(project: Path, request_path: Path,
                              request: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    expected = {
        "kind", "schema", "status", "coupon_id", "inputs", "authority",
        "fabrication", "board", "assemblies", "qualification", "drc",
        "artifacts", "commands", "summary",
    }
    _exact(request, expected, "request")
    if request["kind"] != REQUEST_KIND or request["schema"] != REQUEST_SCHEMA:
        raise ContractError("request: kind/schema mismatch")
    if request["status"] != "READY_FOR_FABRICATION":
        raise ContractError("request: status is not READY_FOR_FABRICATION")
    inputs = _exact(request["inputs"], {
        "config", "source_board", "source_kicad_project", "base_receipt",
        "base_inputs", "phase_policy", "phase_gate", "producer_verifier",
        "local_footprint_libraries",
    }, "request.inputs")
    if not isinstance(inputs.get("config"), Mapping):
        raise ContractError("request.inputs.config: missing binding")
    config_path = Path(_string(inputs["config"].get("path"), "request.inputs.config.path"))
    context = _load_context(project, config_path)
    if context["config_binding"] != inputs["config"]:
        raise ContractError("request: coupon config is stale")
    if context["source_board_binding"] != inputs.get("source_board"):
        raise ContractError("request: source board is stale")
    source_path = project / context["source_board_binding"]["path"]
    source_project_path = source_path.with_suffix(".kicad_pro")
    source_project_binding, _ = base._ordinary_file(  # noqa: SLF001
        project, Path(source_project_path.relative_to(project)),
        "source KiCad project")
    if source_project_binding != inputs.get("source_kicad_project"):
        raise ContractError("request: source KiCad project is stale")
    if context["base_binding"] != inputs.get("base_receipt"):
        raise ContractError("request: base connector receipt is stale")
    if context["base_receipt"]["inputs"] != inputs.get("base_inputs"):
        raise ContractError("request: base connector inputs are stale")
    if context["source_phase"]["inputs"]["phase_policy"] != inputs.get("phase_policy"):
        raise ContractError("request: connector phase policy is stale")
    if context["source_phase"]["inputs"]["phase_gate"] != inputs.get("phase_gate"):
        raise ContractError("request: connector phase gate is stale")
    if _script_binding() != inputs.get("producer_verifier"):
        raise ContractError("request: producer/verifier implementation is stale")
    if context["libraries"] != inputs.get("local_footprint_libraries"):
        raise ContractError("request: local footprint libraries are stale")
    config = context["config"]
    if request["coupon_id"] != config["coupon_id"]:
        raise ContractError("request: coupon ID differs from current config")
    if request["fabrication"] != config["fabrication"]:
        raise ContractError("request: fabrication requirements differ from current config")
    authority = request["authority"]
    if authority != {
        "base_semantic_sha256": context["base_receipt"]["semantic_sha256"],
        "base_subject_sha256": context["base_receipt"]["subject_sha256"],
        "source_phase_subject_sha256": context["source_phase"]["subject_sha256"],
    }:
        raise ContractError("request: connector authority hashes are stale")
    expected_refs, expected_assemblies = _assembly_rows(context["base_receipt"])
    if request["assemblies"] != expected_assemblies:
        raise ContractError("request: assembly census differs from base connector receipt")
    expected_targets = _qualification_rows(context, expected_assemblies)
    expected_qualification = {
        "minimum_samples": config["qualification"]["minimum_samples"],
        "required_sample_evidence_kinds":
            config["qualification"]["required_sample_evidence_kinds"],
        "required_instrument_roles":
            config["qualification"]["required_instrument_roles"],
        "target_hardware": config["qualification"]["target_hardware"],
        "targets": expected_targets,
    }
    if request["qualification"] != expected_qualification:
        raise ContractError("request: qualification census differs from current inputs")
    board = _exact(request["board"], {
        "source", "coupon", "connector_refs", "board_only_refs",
        "source_geometry_sha256", "coupon_geometry_sha256", "geometry",
    }, "request.board")
    if not isinstance(board.get("coupon"), Mapping):
        raise ContractError("request.board.coupon: missing binding")
    coupon_path = Path(_string(board["coupon"].get("path"), "request.board.coupon.path"))
    coupon_binding, _ = base._ordinary_file(project, coupon_path, "coupon board")  # noqa: SLF001
    if coupon_binding != board["coupon"]:
        raise ContractError("request: coupon board bytes are stale")
    source = pcbnew.LoadBoard(str(project / context["source_board_binding"]["path"]))
    coupon = pcbnew.LoadBoard(str(project / coupon_path))
    if source is None or coupon is None:
        raise ContractError("request: cannot reopen source/coupon board")
    connector_refs = board.get("connector_refs")
    board_only_refs = board.get("board_only_refs")
    if not isinstance(connector_refs, list) or not isinstance(board_only_refs, list):
        raise ContractError("request.board: missing ref censuses")
    if connector_refs != expected_refs:
        raise ContractError("request.board.connector_refs differs from base connector receipt")
    if board_only_refs != config["board_only_refs"]:
        raise ContractError("request.board.board_only_refs differs from current config")
    if board.get("source") != context["source_board_binding"]:
        raise ContractError("request.board.source differs from current source board")
    source_geometry = _board_geometry(source, connector_refs, board_only_refs)
    coupon_geometry = _board_geometry(coupon, connector_refs, board_only_refs)
    if source_geometry != coupon_geometry or coupon_geometry != board.get("geometry"):
        raise ContractError("request: normalized source/coupon geometry is stale")
    if _digest(_canonical_bytes(source_geometry)) != board.get("source_geometry_sha256"):
        raise ContractError("request: source geometry hash is stale")
    if _digest(_canonical_bytes(coupon_geometry)) != board.get("coupon_geometry_sha256"):
        raise ContractError("request: coupon geometry hash is stale")
    artifacts = request["artifacts"]
    if not isinstance(artifacts, list) or not artifacts:
        raise ContractError("request.artifacts: expected non-empty list")
    for index, expected_binding in enumerate(artifacts):
        if not isinstance(expected_binding, Mapping):
            raise ContractError(f"request.artifacts[{index}]: expected binding")
        path = Path(_string(expected_binding.get("path"), f"artifacts[{index}].path"))
        current, _ = base._ordinary_file(project, path, f"coupon artifact {index}")  # noqa: SLF001
        if current != expected_binding:
            raise ContractError(f"request: artifact is stale: {path}")
    artifact_paths = [row.get("path") for row in artifacts]
    if len(artifact_paths) != len(set(artifact_paths)):
        raise ContractError("request.artifacts: duplicate paths are forbidden")
    request_absolute, request_relative = base._project_path(  # noqa: SLF001
        project, request_path, "coupon request")
    del request_absolute
    output_relative = Path(request_relative).parent
    drc_relative = (output_relative / "drc.json").as_posix()
    if drc_relative not in artifact_paths:
        raise ContractError("request.artifacts: governed DRC JSON is absent")
    drc_document, _ = _strict_json(project, Path(drc_relative), "coupon DRC")
    current_drc = _drc_summary(
        drc_document, config["fabrication"]["accepted_drc_warning_types"])
    if request["drc"] != current_drc:
        raise ContractError("request: DRC summary differs from governed DRC JSON")
    expected_command = {
        "grade": (
            f"/usr/bin/python3 {SCRIPT_PATH.relative_to(REPO_ROOT).as_posix()} "
            f"grade --project {_project_argument(project)} "
            f"--request {(output_relative / 'request.json').as_posix()} "
            f"--response {(output_relative / 'physical-response.yaml').as_posix()} "
            f"--output {(output_relative / 'qualification-receipt.json').as_posix()}")
    }
    if request["commands"] != expected_command:
        raise ContractError("request: grade command differs from current subject")
    fab_count = sum(
        1 for raw in artifact_paths
        if Path(str(raw)).parent == output_relative / "fab"
        or str(raw).endswith("_gerbers.zip"))
    review_names = {"drc.json", "render-top.png", "render-front.png", "render-back.png"}
    review_count = sum(
        1 for raw in artifact_paths
        if Path(str(raw)).parent == output_relative
        and Path(str(raw)).name in review_names)
    expected_summary = {
        "assembly_count": len(expected_assemblies),
        "connector_count": len(expected_refs),
        "board_only_datum_count": len(config["board_only_refs"]),
        "physical_target_count": len(expected_targets),
        "artifact_count": len(artifacts),
        "gerber_or_drill_count": fab_count,
        "review_artifact_count": review_count,
    }
    if request["summary"] != expected_summary:
        raise ContractError("request: summary differs from exact artifact census")
    return context, coupon_binding


def _evidence_rows(project: Path, value: Any, where: str,
                   findings: list[dict[str, str]], required: set[str],
                   evidence_bindings: dict[str, dict[str, Any]]) -> set[str]:
    if not isinstance(value, list):
        findings.append({"code": "EVIDENCE-SCHEMA", "path": where,
                         "message": "expected evidence list"})
        return set()
    kinds: set[str] = set()
    for index, raw in enumerate(value):
        path_where = f"{where}[{index}]"
        try:
            item = _exact(raw, {"kind", "path"}, path_where)
            kind = _string(item["kind"], f"{path_where}.kind")
            if kind not in _EVIDENCE_KINDS:
                raise ContractError(f"{path_where}.kind: unsupported {kind!r}")
            path = Path(_string(item["path"], f"{path_where}.path"))
            binding, _ = base._ordinary_file(project, path, path_where)  # noqa: SLF001
            kinds.add(kind)
            evidence_bindings[binding["path"]] = binding
        except ContractError as exc:
            findings.append({"code": "EVIDENCE-FILE", "path": path_where,
                             "message": str(exc)})
    if missing := sorted(required - kinds):
        findings.append({"code": "EVIDENCE-MISSING", "path": where,
                         "message": f"missing evidence kinds {missing}"})
    return kinds


def _grade_response(project: Path, request: Mapping[str, Any],
                    response: Mapping[str, Any], config: Mapping[str, Any]) -> tuple[
                        str, list[dict[str, str]], list[dict[str, Any]],
                        list[dict[str, Any]], list[dict[str, Any]],
                        list[dict[str, Any]], list[dict[str, Any]]]:
    _exact(response, {
        "schema", "kind", "request_sha256", "coupon_id", "target_hardware",
        "samples", "instruments", "observations",
    }, "response")
    if response["schema"] != RESPONSE_SCHEMA or response["kind"] != RESPONSE_KIND:
        raise ContractError("response: kind/schema mismatch")
    if response["coupon_id"] != request["coupon_id"]:
        raise ContractError("response.coupon_id differs from request")
    findings: list[dict[str, str]] = []
    evidence_bindings: dict[str, dict[str, Any]] = {}
    qual = config["qualification"]
    refs_by_assembly = {row["assembly_id"]: row["refs"]
                        for row in request["assemblies"]}

    samples_out: list[dict[str, Any]] = []
    samples = response["samples"]
    if not isinstance(samples, list):
        raise ContractError("response.samples: expected list")
    sample_ids: set[str] = set()
    sample_counts = {key: 0 for key in qual["minimum_samples"]}
    for index, raw in enumerate(samples):
        item = _exact(raw, {
            "sample_id", "assembly_id", "receptacle_lot", "mate_lot",
            "cable_lot", "evidence",
        }, f"samples[{index}]")
        sample_id = _identifier(item["sample_id"], f"samples[{index}].sample_id")
        if sample_id in sample_ids:
            raise ContractError(f"samples[{index}]: duplicate sample_id {sample_id!r}")
        sample_ids.add(sample_id)
        assembly_id = _identifier(item["assembly_id"], f"samples[{index}].assembly_id")
        if assembly_id not in sample_counts:
            raise ContractError(f"samples[{index}]: unknown assembly {assembly_id!r}")
        sample_counts[assembly_id] += 1
        lots = {}
        for field in ("receptacle_lot", "mate_lot", "cable_lot"):
            try:
                lots[field] = _concrete(item[field], f"samples[{index}].{field}")
            except ContractError as exc:
                findings.append({"code": "SAMPLE-IDENTITY", "path": f"samples[{index}].{field}",
                                 "message": str(exc)})
                lots[field] = item[field]
        _evidence_rows(
            project, item["evidence"], f"samples[{index}].evidence", findings,
            set(qual["required_sample_evidence_kinds"]), evidence_bindings)
        samples_out.append({"sample_id": sample_id, "assembly_id": assembly_id,
                            **lots, "evidence": item["evidence"]})
    for assembly_id, minimum in qual["minimum_samples"].items():
        if sample_counts[assembly_id] < minimum:
            findings.append({
                "code": "SAMPLE-CENSUS", "path": f"samples:{assembly_id}",
                "message": f"{sample_counts[assembly_id]}/{minimum} required samples represented",
            })

    hardware_out: list[dict[str, Any]] = []
    hardware = response["target_hardware"]
    if not isinstance(hardware, list):
        raise ContractError("response.target_hardware: expected list")
    hardware_seen: set[tuple[str, str]] = set()
    required_hardware = {
        (row["assembly_id"], row["role"]): row
        for row in qual["target_hardware"]
    }
    for index, raw in enumerate(hardware):
        item = _exact(raw, {
            "assembly_id", "role", "manufacturer", "product", "model",
            "revision", "serial", "evidence",
        }, f"target_hardware[{index}]")
        key = (
            _identifier(item["assembly_id"], f"target_hardware[{index}].assembly_id"),
            _identifier(item["role"], f"target_hardware[{index}].role"),
        )
        if key in hardware_seen:
            raise ContractError(f"target_hardware[{index}]: duplicate {key}")
        hardware_seen.add(key)
        expected = required_hardware.get(key)
        if expected is None:
            raise ContractError(f"target_hardware[{index}]: unexpected {key}")
        for field in ("manufacturer", "product"):
            if item[field] != expected[field]:
                findings.append({"code": "HARDWARE-IDENTITY",
                                 "path": f"target_hardware[{index}].{field}",
                                 "message": f"{item[field]!r} != required {expected[field]!r}"})
        for field in ("model", "revision", "serial"):
            try:
                _concrete(item[field], f"target_hardware[{index}].{field}")
            except ContractError as exc:
                findings.append({"code": "HARDWARE-IDENTITY",
                                 "path": f"target_hardware[{index}].{field}",
                                 "message": str(exc)})
        _evidence_rows(
            project, item["evidence"], f"target_hardware[{index}].evidence",
            findings, {"photo", "lot_label"}, evidence_bindings)
        hardware_out.append(dict(item))
    for key in sorted(set(required_hardware) - hardware_seen):
        findings.append({"code": "HARDWARE-CENSUS", "path": f"target_hardware:{key}",
                         "message": "required target hardware identity is absent"})

    instruments_out: list[dict[str, Any]] = []
    instruments = response["instruments"]
    if not isinstance(instruments, list):
        raise ContractError("response.instruments: expected list")
    instrument_ids: set[str] = set()
    covered_roles: set[str] = set()
    for index, raw in enumerate(instruments):
        item = _exact(raw, {
            "instrument_id", "roles", "maker", "model", "serial",
            "resolution", "calibration_date", "evidence",
        }, f"instruments[{index}]")
        iid = _identifier(item["instrument_id"], f"instruments[{index}].instrument_id")
        if iid in instrument_ids:
            raise ContractError(f"instruments[{index}]: duplicate instrument_id {iid!r}")
        instrument_ids.add(iid)
        roles = _unique_strings(item["roles"], f"instruments[{index}].roles",
                                ids=True, nonempty=True)
        covered_roles.update(roles)
        for field in ("maker", "model", "serial", "resolution"):
            try:
                _concrete(item[field], f"instruments[{index}].{field}")
            except ContractError as exc:
                findings.append({"code": "INSTRUMENT-IDENTITY",
                                 "path": f"instruments[{index}].{field}",
                                 "message": str(exc)})
        date = item["calibration_date"]
        if not isinstance(date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            findings.append({"code": "INSTRUMENT-CALIBRATION",
                             "path": f"instruments[{index}].calibration_date",
                             "message": "expected YYYY-MM-DD calibration date"})
        _evidence_rows(
            project, item["evidence"], f"instruments[{index}].evidence",
            findings, {"calibration_record"}, evidence_bindings)
        instruments_out.append(dict(item))
    if missing := sorted(set(qual["required_instrument_roles"]) - covered_roles):
        findings.append({"code": "INSTRUMENT-CENSUS", "path": "instruments",
                         "message": f"missing instrument roles {missing}"})

    target_requirements = {
        (row["assembly_id"], row["target_kind"], row["target_id"]): row
        for row in qual["targets"]
    }
    observations = response["observations"]
    if not isinstance(observations, list):
        raise ContractError("response.observations: expected list")
    observations_out: list[dict[str, Any]] = []
    observed_keys: set[tuple[str, str, str]] = set()
    any_negative = False
    for index, raw in enumerate(observations):
        item = _exact(raw, {
            "assembly_id", "target_kind", "target_id", "result",
            "tested_refs", "measurements", "evidence", "notes",
        }, f"observations[{index}]")
        key = (
            _identifier(item["assembly_id"], f"observations[{index}].assembly_id"),
            _identifier(item["target_kind"], f"observations[{index}].target_kind"),
            _identifier(item["target_id"], f"observations[{index}].target_id"),
        )
        if key in observed_keys:
            raise ContractError(f"observations[{index}]: duplicate stable target {key}")
        observed_keys.add(key)
        required = target_requirements.get(key)
        if required is None:
            raise ContractError(f"observations[{index}]: unexpected target {key}")
        result = _string(item["result"], f"observations[{index}].result")
        if result not in _RESULTS:
            raise ContractError(f"observations[{index}].result: expected {sorted(_RESULTS)}")
        if result == "FAIL":
            any_negative = True
        if result == "UNOBSERVED":
            findings.append({"code": "TARGET-UNOBSERVED",
                             "path": f"target:{key}",
                             "message": "physical target has not been observed"})
            observations_out.append(dict(item))
            continue
        expected_refs = refs_by_assembly[key[0]]
        try:
            tested_refs = sorted(_unique_strings(
                item["tested_refs"], f"observations[{index}].tested_refs",
                nonempty=True), key=_natural)
        except ContractError as exc:
            findings.append({"code": "TARGET-REF-CENSUS", "path": f"target:{key}",
                             "message": str(exc)})
            tested_refs = []
        if tested_refs != expected_refs:
            findings.append({"code": "TARGET-REF-CENSUS", "path": f"target:{key}",
                             "message": f"tested refs {tested_refs} != required {expected_refs}"})
        measurements = item["measurements"]
        if not isinstance(measurements, list):
            findings.append({"code": "MEASUREMENT-SCHEMA", "path": f"target:{key}",
                             "message": "expected measurement list"})
            measurements = []
        measurement_map: dict[str, Mapping[str, Any]] = {}
        for mindex, raw_measurement in enumerate(measurements):
            try:
                measure = _exact(raw_measurement, {"name", "unit", "values"},
                                 f"observations[{index}].measurements[{mindex}]")
                name = _identifier(measure["name"], f"measurement[{mindex}].name")
                if name in measurement_map:
                    raise ContractError(f"duplicate measurement {name!r}")
                measurement_map[name] = measure
            except ContractError as exc:
                findings.append({"code": "MEASUREMENT-SCHEMA", "path": f"target:{key}",
                                 "message": str(exc)})
        required_measurements = {row["name"]: row for row in required["required_measurements"]}
        if set(measurement_map) != set(required_measurements):
            findings.append({"code": "MEASUREMENT-CENSUS", "path": f"target:{key}",
                             "message": f"names {sorted(measurement_map)} != required {sorted(required_measurements)}"})
        for name, spec in required_measurements.items():
            measure = measurement_map.get(name)
            if measure is None:
                continue
            if measure["unit"] != spec["unit"]:
                findings.append({"code": "MEASUREMENT-UNIT", "path": f"target:{key}/{name}",
                                 "message": f"{measure['unit']!r} != {spec['unit']!r}"})
            values = measure["values"]
            if not isinstance(values, list):
                findings.append({"code": "MEASUREMENT-SCHEMA", "path": f"target:{key}/{name}",
                                 "message": "values must be a list"})
                continue
            seen_refs: set[str] = set()
            for vindex, raw_value in enumerate(values):
                try:
                    value_row = _exact(raw_value, {"ref", "value"},
                                       f"target:{key}/{name}.values[{vindex}]")
                    ref = _string(value_row["ref"], f"target:{key}/{name}.ref")
                    if ref in seen_refs:
                        raise ContractError(f"duplicate measurement ref {ref!r}")
                    seen_refs.add(ref)
                    number = _finite(value_row["value"], f"target:{key}/{name}/{ref}")
                    if spec["minimum"] is not None and number < spec["minimum"]:
                        findings.append({"code": "MEASUREMENT-LOW", "path": f"target:{key}/{name}/{ref}",
                                         "message": f"{number} < {spec['minimum']}"})
                        any_negative = True
                    if spec["maximum"] is not None and number > spec["maximum"]:
                        findings.append({"code": "MEASUREMENT-HIGH", "path": f"target:{key}/{name}/{ref}",
                                         "message": f"{number} > {spec['maximum']}"})
                        any_negative = True
                except ContractError as exc:
                    findings.append({"code": "MEASUREMENT-SCHEMA", "path": f"target:{key}/{name}",
                                     "message": str(exc)})
            if sorted(seen_refs, key=_natural) != expected_refs:
                findings.append({"code": "MEASUREMENT-REF-CENSUS", "path": f"target:{key}/{name}",
                                 "message": f"refs {sorted(seen_refs, key=_natural)} != required {expected_refs}"})
        _evidence_rows(
            project, item["evidence"], f"observations[{index}].evidence",
            findings, set(required["required_evidence_kinds"]), evidence_bindings)
        try:
            _concrete(item["notes"], f"observations[{index}].notes")
        except ContractError as exc:
            findings.append({"code": "TARGET-NOTES", "path": f"target:{key}",
                             "message": str(exc)})
        observations_out.append(dict(item))
    for key in sorted(set(target_requirements) - observed_keys):
        findings.append({"code": "TARGET-CENSUS", "path": f"target:{key}",
                         "message": "required physical target row is absent"})

    hard_fail_codes = {
        "EVIDENCE-FILE", "HARDWARE-IDENTITY", "MEASUREMENT-LOW",
        "MEASUREMENT-HIGH",
    }
    if any_negative or any(row["code"] in hard_fail_codes for row in findings):
        status = "FAIL"
    elif findings:
        status = "INCOMPLETE"
    else:
        status = "PASS"
    return (
        status,
        sorted(findings, key=lambda row: (row["code"], row["path"], row["message"])),
        sorted(samples_out, key=lambda row: row["sample_id"]),
        sorted(hardware_out, key=lambda row: (row["assembly_id"], row["role"])),
        sorted(instruments_out, key=lambda row: row["instrument_id"]),
        sorted(observations_out, key=lambda row: (
            row["assembly_id"], row["target_kind"], row["target_id"])),
        [evidence_bindings[key] for key in sorted(evidence_bindings)],
    )


def compile_grade(project_raw: Path, request_path: Path,
                  response_path: Path) -> dict[str, Any]:
    project = base._project_directory(project_raw)  # noqa: SLF001
    request, request_binding = _strict_json(project, request_path, "coupon request")
    context, coupon_binding = _validate_request_current(project, request_path, request)
    response, response_binding = _strict_yaml(project, response_path, "physical response")
    if response.get("request_sha256") != request_binding["sha256"]:
        raise ContractError("response.request_sha256 differs from exact request bytes")
    status, findings, samples, hardware, instruments, observations, evidence = _grade_response(
        project, request, response, context["config"])
    summary = {
        "assembly_count": len(request["assemblies"]),
        "connector_count": len(request["board"]["connector_refs"]),
        "physical_target_count": len(request["qualification"]["targets"]),
        "pass_target_count": sum(1 for row in observations if row["result"] == "PASS"),
        "fail_target_count": sum(1 for row in observations if row["result"] == "FAIL"),
        "unobserved_target_count": sum(
            1 for row in observations if row["result"] == "UNOBSERVED"),
        "sample_count": len(samples),
        "instrument_count": len(instruments),
        "evidence_file_count": len(evidence),
        "finding_count": len(findings),
    }
    semantic = {
        "status": status,
        "coupon_id": request["coupon_id"],
        "samples": samples,
        "target_hardware": hardware,
        "instruments": instruments,
        "observations": observations,
        "findings": findings,
        "summary": summary,
    }
    semantic_sha = _digest(_canonical_bytes(semantic))
    inputs = {
        "request": request_binding,
        "response": response_binding,
        "coupon_board": coupon_binding,
        "producer_verifier": _script_binding(),
        "evidence_files": evidence,
    }
    return {
        "kind": RECEIPT_KIND,
        "schema": RECEIPT_SCHEMA,
        "status": status,
        "coupon_id": request["coupon_id"],
        "authority": request["authority"],
        "inputs": inputs,
        "samples": samples,
        "target_hardware": hardware,
        "instruments": instruments,
        "observations": observations,
        "findings": findings,
        "summary": summary,
        "semantic_sha256": semantic_sha,
        "subject_sha256": _digest(_canonical_bytes({
            "semantic_sha256": semantic_sha,
            "authority": request["authority"],
            "inputs": inputs,
        })),
    }


def _write_json_atomic(project: Path, output: Path,
                       value: Mapping[str, Any]) -> Path:
    candidate, _ = base._project_path(project, output, "receipt output")  # noqa: SLF001
    candidate.parent.mkdir(parents=True, exist_ok=True)
    base._reject_symlink_components(candidate.parent, "receipt output parent")  # noqa: SLF001
    if candidate.is_symlink():
        raise ContractError("receipt output: symlink destination is forbidden")
    temporary = candidate.parent / f".{candidate.name}.{secrets.token_hex(12)}.tmp"
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, candidate)
    finally:
        if temporary.exists():
            temporary.unlink()
    return candidate


def grade(project_raw: Path, request_path: Path, response_path: Path,
          output_path: Path) -> tuple[Path, Mapping[str, Any]]:
    project = base._project_directory(project_raw)  # noqa: SLF001
    receipt = compile_grade(project, request_path, response_path)
    output = _write_json_atomic(project, output_path, receipt)
    current = compile_grade(project, request_path, response_path)
    if _canonical_bytes(receipt) != _canonical_bytes(current):
        output.unlink(missing_ok=True)
        raise ContractError("coupon inputs changed during receipt publication")
    print(
        f"CONNECTOR-COUPON {receipt['status']} "
        f"targets={receipt['summary']['pass_target_count']}/"
        f"{receipt['summary']['physical_target_count']} "
        f"samples={receipt['summary']['sample_count']} "
        f"evidence={receipt['summary']['evidence_file_count']} "
        f"findings={receipt['summary']['finding_count']} output={output}")
    return output, receipt


def verify(project_raw: Path, request_path: Path, response_path: Path,
           receipt_path: Path) -> Mapping[str, Any]:
    project = base._project_directory(project_raw)  # noqa: SLF001
    receipt, _ = _strict_json(project, receipt_path, "qualification receipt")
    expected = compile_grade(project, request_path, response_path)
    if _canonical_bytes(receipt) != _canonical_bytes(expected):
        raise ContractError("qualification receipt differs from fresh regrade")
    print(
        f"CONNECTOR-COUPON VERIFY PASS status={receipt['status']} "
        f"targets={receipt['summary']['pass_target_count']}/"
        f"{receipt['summary']['physical_target_count']}")
    return receipt


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--project", type=Path, required=True)
    prepare_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    prepare_parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    for command in ("grade", "verify"):
        child = sub.add_parser(command)
        child.add_argument("--project", type=Path, required=True)
        child.add_argument("--request", type=Path, required=True)
        child.add_argument("--response", type=Path, required=True)
        if command == "grade":
            child.add_argument("--output", type=Path, required=True)
        else:
            child.add_argument("--receipt", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        if args.command == "prepare":
            prepare(args.project, args.config, args.out)
            return 0
        if args.command == "grade":
            _output, receipt = grade(
                args.project, args.request, args.response, args.output)
            return {"PASS": 0, "INCOMPLETE": 2, "FAIL": 1}[receipt["status"]]
        receipt = verify(
            args.project, args.request, args.response, args.receipt)
        return {"PASS": 0, "INCOMPLETE": 2, "FAIL": 1}[receipt["status"]]
    except ContractError as exc:
        print(f"CONNECTOR-COUPON FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
