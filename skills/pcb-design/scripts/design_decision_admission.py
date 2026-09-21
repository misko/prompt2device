#!/usr/bin/env python3
"""Admit settled interface, assembly, and protected-route decisions.

This is a small lifecycle compositor.  It does not own pin-map semantics,
assembly stock, or critical-route semantics.  Source admission uses the
existing assembly policy and exact-code identity checker, and compares an
adopted ``no_vias`` contract with a separately reviewed route input.  Native
admission additionally runs P-PINMAP, reopens the board for every authored
ref/pad anchor, and applies the existing assembly-side predicate.

The source phase is suitable before placement.  The native phase is required
before placement acceptance or routing; selecting the source phase never
claims that native checks ran.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml
import pcbnew


SCRIPT_DIR = Path(__file__).resolve().parent
SKILLS = SCRIPT_DIR.parents[1]
FAB_SCRIPTS = SKILLS / "jlcpcb-fab" / "scripts"
KICAD_SCRIPTS = SKILLS / "kicad-pcb" / "scripts"
for directory in (FAB_SCRIPTS, KICAD_SCRIPTS):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from assembly_coverage import (  # noqa: E402
    AssemblyConfigError,
    check_assembly_sides,
    load_assembly,
    read_footprints,
    validate_population_dispositions,
)
from manufacturing_readiness import exact_code_check  # noqa: E402
from critical_route_check import (  # noqa: E402
    RouteContractError,
    check as critical_route_check,
)
from copper_length_audit import AuditError, load_groups  # noqa: E402


class AdmissionInputError(ValueError):
    """An input is absent, unreadable, or not structurally gradeable."""


@dataclass
class AdmissionResult:
    phase: str
    findings: list[dict[str, str]] = field(default_factory=list)
    coverage: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    _input_paths: dict[str, Path] = field(default_factory=dict, repr=False)

    @property
    def passed(self) -> bool:
        return not self.findings

    def add(self, code: str, message: str) -> None:
        self.findings.append({"code": code, "message": message})

    def bind(self, label: str, path: Path) -> None:
        path = path.resolve()
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise AdmissionInputError(f"cannot bind {label} {path}: {exc}") from exc
        self._input_paths[label] = path
        self.inputs[label] = {
            "path": str(path), "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
        }

    def verify_inputs(self) -> None:
        for label, path in sorted(self._input_paths.items()):
            try:
                data = path.read_bytes()
                current = {"path": str(path),
                           "sha256": hashlib.sha256(data).hexdigest(),
                           "size": len(data)}
            except OSError as exc:
                self.add("DDA-INPUT-CHANGED",
                         f"bound input {label} disappeared during admission: {exc}")
                continue
            if current != self.inputs[label]:
                self.add("DDA-INPUT-CHANGED",
                         f"bound input {label} changed during admission: {path}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": 1,
            "gate": "D-DESIGN-ADMISSION",
            "phase": self.phase,
            "status": "PASS" if self.passed else "FAIL",
            "findings": self.findings,
            "coverage": self.coverage,
            "inputs": self.inputs,
            "claims": {
                "assembly_identity": "source responsibility only; no stock or allocation claim",
                "production_stage": "not complete",
            },
        }


def _resolve(project: Path, value: Path | None, default: str) -> Path:
    path = value if value is not None else Path(default)
    return path.resolve() if path.is_absolute() else (project / path).resolve()


def _load_mapping(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise AdmissionInputError(f"missing {label}: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    except (OSError, yaml.YAMLError) as exc:
        raise AdmissionInputError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AdmissionInputError(f"{label} must be a YAML mapping: {path}")
    return data


def _critical_rows(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = ((doc.get("route") or {}).get("preflight_critical_pairs"))
    if not isinstance(rows, list):
        raise AdmissionInputError("route.preflight_critical_pairs must be a list")
    out: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise AdmissionInputError(
                f"route.preflight_critical_pairs[{index}] must be a mapping")
        name = str(row.get("name") or "").strip()
        if not name:
            raise AdmissionInputError(
                f"route.preflight_critical_pairs[{index}].name is required")
        if name in out:
            raise AdmissionInputError(f"duplicate critical-pair name {name!r}")
        if not isinstance(row.get("no_vias"), bool):
            raise AdmissionInputError(
                f"route.preflight_critical_pairs[{index}].no_vias must be "
                f"boolean true/false, got {row.get('no_vias')!r}")
        out[name] = row
    return out


def _length_groups(path: Path) -> dict[str, dict[str, Any]]:
    """Validate an arbitrary nets snapshot with the owning R-LEN loader."""
    if not path.is_file():
        raise AdmissionInputError(f"missing nets authority: {path}")
    with tempfile.TemporaryDirectory(prefix="decision-admission-nets-") as raw:
        project = Path(raw)
        target = project / "03_src/rules/nets.yaml"
        target.parent.mkdir(parents=True)
        shutil.copyfile(path, target)
        try:
            groups, _ = load_groups(project)
        except AuditError as exc:
            raise AdmissionInputError(str(exc)) from exc
    for name, row in groups.items():
        if "no_vias" in row and not isinstance(row.get("no_vias"), bool):
            raise AdmissionInputError(
                f"length_match.{name}.no_vias must be boolean true/false, "
                f"got {row.get('no_vias')!r}")
    return groups


def _grade_nets_lock(result: AdmissionResult, nets_path: Path,
                     locked_nets_path: Path | None, *,
                     require_locked_nets: bool = False) -> None:
    current = _length_groups(nets_path)
    current_protected = {name: row for name, row in current.items()
                         if row.get("no_vias") is True}
    result.coverage["current_length_groups"] = len(current)
    result.coverage["current_no_vias_groups"] = len(current_protected)
    if locked_nets_path is None:
        if require_locked_nets or current_protected:
            result.add(
                "DDA-NETS-LOCK-MISSING",
                (f"{len(current_protected)} adopted length group(s) with "
                 "no_vias:true require a separate reviewed --locked-nets input"
                 if current_protected else
                 "enforced decision admission requires a separate reviewed "
                 "--locked-nets input"))
        result.coverage["locked_no_vias_groups"] = 0
        return
    if nets_path.resolve() == locked_nets_path.resolve():
        result.add("DDA-NETS-LOCK-NOT-INDEPENDENT",
                   "--locked-nets resolves to current nets authority")
        return
    locked = _length_groups(locked_nets_path)
    protected = {name: row for name, row in locked.items()
                 if row.get("no_vias") is True}
    result.coverage["locked_no_vias_groups"] = len(protected)
    fields = ("members", "paths", "octilinear_endpoints", "topology", "no_vias")
    for name, expected in sorted(protected.items()):
        got = current.get(name)
        if got is None:
            result.add("DDA-PROTECTED-NETS-MISSING",
                       f"reviewed no_vias length group {name!r} is absent")
            continue
        drift = [key for key in fields if got.get(key) != expected.get(key)]
        if drift:
            result.add("DDA-PROTECTED-NETS-DRIFT",
                       f"reviewed no_vias length group {name!r} changed "
                       f"protected field(s): {', '.join(drift)}")


def _grade_route_lock(result: AdmissionResult, route_path: Path,
                      locked_route_path: Path | None, *,
                      require_locked_route: bool = False) -> None:
    current_doc = _load_mapping(route_path, "current route authority")
    current = _critical_rows(current_doc)
    current_protected = {name: row for name, row in current.items()
                         if row.get("no_vias") is True}
    result.coverage["current_critical_pairs"] = len(current)
    result.coverage["current_no_vias_pairs"] = len(current_protected)

    if locked_route_path is None:
        if require_locked_route or current_protected:
            result.add(
                "DDA-ROUTE-LOCK-MISSING",
                (f"{len(current_protected)} adopted no_vias pair(s) require a "
                 "separate reviewed --locked-route input" if current_protected else
                 "enforced decision admission requires a separate reviewed "
                 "--locked-route input"))
        result.coverage["locked_no_vias_pairs"] = 0
        return
    if route_path.resolve() == locked_route_path.resolve():
        result.add(
            "DDA-ROUTE-LOCK-NOT-INDEPENDENT",
            "--locked-route resolves to the current route authority; a current "
            "file cannot approve its own relaxation")
        return
    locked_doc = _load_mapping(locked_route_path, "reviewed route lock")
    locked = _critical_rows(locked_doc)
    protected = {name: row for name, row in locked.items()
                 if row.get("no_vias") is True}
    result.coverage["locked_no_vias_pairs"] = len(protected)
    for name, expected in sorted(protected.items()):
        got = current.get(name)
        if got is None:
            result.add("DDA-PROTECTED-ROUTE-MISSING",
                       f"reviewed no_vias pair {name!r} is absent from current route")
            continue
        fields = ("p", "n", "allowed_layers", "no_vias")
        drift = [key for key in fields if got.get(key) != expected.get(key)]
        if drift:
            result.add(
                "DDA-PROTECTED-ROUTE-DRIFT",
                f"reviewed no_vias pair {name!r} changed protected field(s): "
                + ", ".join(drift))


def _assembly_assignments(assembly: dict[str, Any],
                          exact: dict[str, Any]) -> tuple[dict[str, str], set[str]]:
    not_rows: dict[str, dict[str, Any]] = {}
    duplicate: set[str] = set()
    for row in assembly.get("not_assembled") or []:
        for value in row.get("refs") or []:
            ref = str(value)
            if ref in not_rows:
                duplicate.add(ref)
            not_rows[ref] = row
    consigned: set[str] = set()
    for row in assembly.get("consigned") or []:
        for value in row.get("refs") or []:
            ref = str(value)
            if ref in consigned:
                duplicate.add(ref)
            consigned.add(ref)
    duplicate |= set(not_rows) & consigned

    owners: dict[str, str] = {}
    for row in exact.get("rows") or []:
        ref = str(row.get("ref") or "")
        if ref in consigned:
            owners[ref] = "consigned-machine"
        elif row.get("disposition") == "jlc":
            owners[ref] = "jlc-machine"
        elif ref in not_rows:
            reason = str(not_rows[ref].get("reason") or "")
            owners[ref] = "not-populated" if reason in {
                "dnp_by_design", "test_point"
            } else "manual"
    return owners, duplicate


def _grade_assembly_policy(result: AdmissionResult,
                           assembly: dict[str, Any],
                           exact: dict[str, Any]) -> set[str]:
    sides = assembly.get("sides")
    if (not isinstance(sides, list) or not sides
            or any(side not in ("top", "bottom") for side in sides)
            or len(set(sides)) != len(sides)):
        result.add("DDA-ASSEMBLY-SIDES",
                   "assembly.sides must be a non-empty list of distinct top/bottom values")
    for finding in validate_population_dispositions(assembly):
        result.add("DDA-ASSEMBLY-DISPOSITION", finding)
    exact_rows = {str(row.get("ref") or ""): row
                  for row in exact.get("rows") or []}
    validated_consigned: set[str] = set()
    for index, row in enumerate(assembly.get("consigned") or []):
        refs = [str(ref) for ref in row.get("refs") or []]
        declared_code = str(row.get("lcsc") or "")
        valid_shape = bool(re.fullmatch(r"C\d+", declared_code))
        valid_shape &= bool(str(row.get("msl") or "").strip())
        if not re.fullmatch(r"C\d+", declared_code):
            result.add("DDA-ASSEMBLY-DISPOSITION",
                       f"consigned[{index}] {refs} requires exact lcsc: C<number>")
        if not str(row.get("msl") or "").strip():
            result.add("DDA-ASSEMBLY-DISPOSITION",
                       f"consigned[{index}] {refs} requires an MSL declaration")
        for ref in refs:
            source = exact_rows.get(ref)
            dossier_path = Path(str((source or {}).get("dossier") or ""))
            dossier_code = ""
            if dossier_path.is_file():
                dossier = yaml.safe_load(
                    dossier_path.read_text(encoding="utf-8-sig")) or {}
                dossier_code = str((dossier.get("sourcing") or {}).get("lcsc") or "")
            if not dossier_code or declared_code != dossier_code:
                result.add(
                    "DDA-ASSEMBLY-DISPOSITION",
                    f"consigned[{index}] {ref} code {declared_code!r} disagrees "
                    f"with canonical dossier code {dossier_code!r}")
            elif valid_shape:
                validated_consigned.add(ref)
    return validated_consigned


def grade_source(project: Path, *, route_path: Path, assembly_path: Path,
                 circuit_path: Path, locked_route_path: Path | None = None,
                 nets_path: Path | None = None,
                 locked_nets_path: Path | None = None,
                 parts_path: Path | None = None,
                 require_locked_route: bool = False,
                 require_locked_nets: bool = False) -> tuple[AdmissionResult, dict[str, str], dict[str, Any]]:
    """Grade decisions available before placement; makes no native-board claim."""
    project = project.resolve()
    result = AdmissionResult("source")
    if not circuit_path.is_file():
        raise AdmissionInputError(f"missing circuit JSON: {circuit_path}")
    if not assembly_path.is_file():
        raise AdmissionInputError(f"missing assembly authority: {assembly_path}")
    # exact_code_check uses the canonical project 02_parts directory.  A
    # different parts root is supported by a narrow temporary project view in
    # the CLI only when it is the canonical directory; accepting another root
    # here would silently change that owning module's semantics.
    canonical_parts = (project / "02_parts").resolve()
    if parts_path is not None and parts_path.resolve() != canonical_parts:
        raise AdmissionInputError("--parts must resolve to PROJECT/02_parts")
    result.bind("route", route_path)
    result.bind("assembly", assembly_path)
    result.bind("circuit_json", circuit_path)
    if locked_route_path is not None:
        result.bind("locked_route", locked_route_path)
    if nets_path is None:
        nets_path = project / "03_src/rules/nets.yaml"
    result.bind("nets", nets_path)
    if locked_nets_path is not None:
        result.bind("locked_nets", locked_nets_path)
    part_files = sorted(canonical_parts.glob("*/part.yaml"))
    for path in part_files:
        result.bind(f"part:{path.parent.name}", path)
    result.coverage["part_dossiers_bound"] = len(part_files)
    try:
        assembly = load_assembly(assembly_path)
    except AssemblyConfigError as exc:
        raise AdmissionInputError(str(exc)) from exc
    exact, _dossiers = exact_code_check(project, circuit_path, assembly_path)
    consigned = _grade_assembly_policy(result, assembly, exact)
    result.coverage["source_components"] = (exact.get("coverage") or {}).get("total", 0)
    result.coverage["source_assignments_graded"] = (exact.get("coverage") or {}).get("graded", 0)
    if (exact.get("coverage") or {}).get("total", 0) == 0:
        result.add("DDA-SOURCE-POPULATION-EMPTY",
                   "zero source components were available for decision admission")
    consigned_missing = {f"{ref}: no JLC code and no not_assembled disposition"
                         for ref in consigned}
    for finding in exact.get("findings") or []:
        if str(finding) in consigned_missing:
            continue
        result.add("DDA-ASSEMBLY-OWNER", str(finding))
    owners, duplicate = _assembly_assignments(assembly, exact)
    for ref in sorted(duplicate):
        result.add("DDA-ASSEMBLY-OWNER-DUPLICATE",
                   f"{ref} has more than one authored assembly disposition")
    result.coverage["assembly_owners"] = len(owners)
    _grade_route_lock(result, route_path, locked_route_path,
                      require_locked_route=require_locked_route)
    _grade_nets_lock(result, nets_path, locked_nets_path,
                     require_locked_nets=require_locked_nets)
    result.verify_inputs()
    return result, owners, assembly


def _board_index(footprints: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["ref"]): row for row in footprints}


_ENDPOINT = re.compile(r"^([A-Za-z_][A-Za-z_0-9]*)\.([^\s.]+)$")


def _as_values(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def _anchor_rows(node: Any, location: str = "") -> Iterable[tuple[str, str, str | None, str]]:
    """Yield ref/pad/net/location from existing floorplan and route shapes."""
    if isinstance(node, dict):
        refs = _as_values(node.get("refs")) or _as_values(node.get("ref"))
        if refs:
            pad_values: list[str] = []
            for key, value in node.items():
                if key == "pad" or key == "pads" or key.endswith("_pads"):
                    pad_values.extend(_as_values(value))
            for lane_index, lane in enumerate(node.get("lanes") or []):
                if isinstance(lane, dict) and lane.get("pad") is not None:
                    for ref in refs:
                        yield ref, str(lane["pad"]), (
                            str(lane["net"]) if lane.get("net") is not None else None
                        ), f"{location}.lanes[{lane_index}]"
            for ref in refs:
                for pad in pad_values:
                    yield ref, pad, (str(node["net"])
                                     if node.get("net") is not None else None), location
        for key in ("pin", "from", "to"):
            value = node.get(key)
            if isinstance(value, str):
                match = _ENDPOINT.fullmatch(value.strip())
                if match:
                    yield match.group(1), match.group(2), (
                        str(node["net"]) if node.get("net") is not None else None
                    ), f"{location}.{key}"
        for key, value in node.items():
            yield from _anchor_rows(value, f"{location}.{key}" if location else str(key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _anchor_rows(value, f"{location}[{index}]")


def _grade_anchors(result: AdmissionResult, board_path: Path,
                   floorplan_path: Path, route_path: Path) -> None:
    footprints = read_footprints(board_path)
    board = _board_index(footprints)
    native = pcbnew.LoadBoard(str(board_path))
    native_nets = {
        fp.GetReference(): {
            str(pad.GetNumber()): str(pad.GetNetname())
            for pad in fp.Pads() if str(pad.GetNumber())
        }
        for fp in native.GetFootprints()
    }
    docs = [(_load_mapping(floorplan_path, "floorplan authority"), "floorplan"),
            (_load_mapping(route_path, "route authority"), "route")]
    rows: list[tuple[str, str, str | None, str]] = []
    for doc, label in docs:
        rows.extend(_anchor_rows(doc, label))
    seen = set()
    for ref, pad, declared_net, location in rows:
        identity = (ref, pad, location)
        if identity in seen:
            continue
        seen.add(identity)
        fp = board.get(ref)
        if fp is None:
            result.add("DDA-RETIRED-REF-ANCHOR",
                       f"{location} names absent board reference {ref}")
        elif pad not in fp.get("pads", set()):
            result.add("DDA-RETIRED-PAD-ANCHOR",
                       f"{location} names absent native pad {ref}.{pad}")
        elif declared_net is not None:
            actual_net = native_nets.get(ref, {}).get(pad, "")
            if actual_net != declared_net:
                result.add(
                    "DDA-STALE-NET-ANCHOR",
                    f"{location} declares {ref}.{pad} on {declared_net!r}; "
                    f"native board net is {actual_net!r}")
    result.coverage["native_ref_pad_anchors"] = len(seen)


def _run_pin_map(project: Path, board_path: Path, circuit_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/usr/bin/python3", str(KICAD_SCRIPTS / "pin_map_check.py"),
         str(project), "--board", str(board_path),
         "--circuit-json", str(circuit_path),
         "--parts", str(project / "02_parts")],
        text=True, capture_output=True, timeout=120)


def grade_native(project: Path, *, board_path: Path, floorplan_path: Path,
                 route_path: Path, assembly_path: Path, circuit_path: Path,
                 locked_route_path: Path | None = None,
                 nets_path: Path | None = None,
                 locked_nets_path: Path | None = None,
                 parts_path: Path | None = None,
                 require_locked_route: bool = False,
                 require_locked_nets: bool = False) -> AdmissionResult:
    """Regrade source decisions plus mandatory native board predicates."""
    source, owners, assembly = grade_source(
        project, route_path=route_path, assembly_path=assembly_path,
        circuit_path=circuit_path, locked_route_path=locked_route_path,
        nets_path=nets_path, locked_nets_path=locked_nets_path,
        parts_path=parts_path, require_locked_route=require_locked_route,
        require_locked_nets=require_locked_nets)
    result = AdmissionResult("native", list(source.findings), dict(source.coverage),
                             dict(source.inputs), dict(source._input_paths))
    for path, label in ((board_path, "native board"),
                        (floorplan_path, "floorplan authority")):
        if not path.is_file():
            raise AdmissionInputError(f"missing {label}: {path}")
    result.bind("board", board_path)
    result.bind("floorplan", floorplan_path)

    pin = _run_pin_map(project, board_path, circuit_path)
    result.coverage["pin_map_exit"] = pin.returncode
    if pin.returncode != 0:
        detail = (pin.stdout + pin.stderr).strip().splitlines()
        result.add("DDA-PINMAP-NATIVE",
                   detail[-1] if detail else f"P-PINMAP exited {pin.returncode}")

    footprints = read_footprints(board_path)
    side_fails, side_summary = check_assembly_sides(footprints, [], assembly)
    result.coverage.update({
        "native_smd_population": side_summary.get("smd_side_graded", 0),
        "native_smd_sides": side_summary.get("smd_population_sides", {}),
    })
    for finding in side_fails:
        result.add("DDA-ASSEMBLY-SIDE", finding.strip())
    dnp = {str(ref) for row in assembly.get("not_assembled") or []
           if row.get("reason") in {"dnp_by_design", "test_point"}
           for ref in row.get("refs") or []}
    for fp in footprints:
        ref = str(fp.get("ref") or "")
        if (fp.get("smd_copper_pads", 0) and ref not in dnp
                and ref not in owners):
            result.add("DDA-SMD-OWNER-MISSING",
                       f"populated native SMD {ref} has no authored assembly owner")

    _grade_anchors(result, board_path, floorplan_path, route_path)
    try:
        critical_route_check(project, board_path, False, route_path=route_path)
        result.coverage["critical_route_contract"] = "PASS"
    except (RouteContractError, OSError, yaml.YAMLError) as exc:
        result.coverage["critical_route_contract"] = "FAIL"
        result.add("DDA-CRITICAL-ROUTE", str(exc))
    result.verify_inputs()
    return result


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", type=Path)
    ap.add_argument("--phase", choices=("source", "native"), required=True)
    ap.add_argument("--route", type=Path)
    ap.add_argument("--locked-route", type=Path)
    ap.add_argument("--require-locked-route", action="store_true",
                    help="enforced adoption: reject an absent independent lock "
                         "even if the current route deleted every protected row")
    ap.add_argument("--nets", type=Path)
    ap.add_argument("--locked-nets", type=Path)
    ap.add_argument("--require-locked-nets", action="store_true",
                    help="enforced adoption: require an independent reviewed "
                         "nets snapshot even if current protected groups vanished")
    ap.add_argument("--assembly", type=Path)
    ap.add_argument("--circuit-json", type=Path)
    ap.add_argument("--parts", type=Path)
    ap.add_argument("--board", type=Path)
    ap.add_argument("--floorplan", type=Path)
    ap.add_argument("--json", type=Path, help="write the complete result JSON")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    project = args.project.resolve()
    try:
        route = _resolve(project, args.route, "03_src/route.yaml")
        assembly = _resolve(project, args.assembly, "03_src/rules/assembly.yaml")
        circuit = _resolve(project, args.circuit_json, "03_tscircuit/build/circuit.json")
        parts = _resolve(project, args.parts, "02_parts")
        locked = (_resolve(project, args.locked_route, "")
                  if args.locked_route is not None else None)
        nets = _resolve(project, args.nets, "03_src/rules/nets.yaml")
        locked_nets = (_resolve(project, args.locked_nets, "")
                       if args.locked_nets is not None else None)
        if args.phase == "source":
            result, _owners, _assembly = grade_source(
                project, route_path=route, assembly_path=assembly,
                circuit_path=circuit, locked_route_path=locked,
                nets_path=nets, locked_nets_path=locked_nets,
                parts_path=parts,
                require_locked_route=args.require_locked_route,
                require_locked_nets=args.require_locked_nets)
        else:
            if args.board is None:
                raise AdmissionInputError("native phase requires --board")
            board = _resolve(project, args.board, "")
            floorplan = _resolve(project, args.floorplan, "03_src/floorplan.yaml")
            result = grade_native(
                project, board_path=board, floorplan_path=floorplan,
                route_path=route, assembly_path=assembly,
                circuit_path=circuit, locked_route_path=locked,
                nets_path=nets, locked_nets_path=locked_nets,
                parts_path=parts,
                require_locked_route=args.require_locked_route,
                require_locked_nets=args.require_locked_nets)
    except (AdmissionInputError, OSError, json.JSONDecodeError,
            yaml.YAMLError, ValueError) as exc:
        print(f"D-DESIGN-ADMISSION ERROR: {exc}")
        return 2
    payload = result.as_dict()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.json:
        output = args.json if args.json.is_absolute() else project / args.json
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
        temporary.write_text(rendered, encoding="utf-8")
        os.replace(temporary, output)
    print(rendered, end="")
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
