#!/usr/bin/env python3
"""Grade one explicit combined-copper witness against the current prepared board.

This gate is a witness checker, not a router or an impossibility prover.  The
prepared board owns placement, pads, inherited copper, and native rule
sidecars.  The witness may add alternate legal copper, but it may not move or
delete that prepared authority.  Required net sets come only from
``route.routability.coupled_neighborhoods``.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Mapping

import pcbnew
import yaml

import promoted_route_check
import route_candidate_workspace
import dru_subject
import generate_rules_generic
from tier_preflight import board_scoped


STATUSES = {"PASS", "FAIL", "INCOMPLETE", "N-A"}
CHECKS = frozenset({"route_base", "candidate", "realized_policy"})
GRAPHICS = frozenset({
    "gr_line", "gr_arc", "gr_rect", "gr_circle", "gr_poly", "gr_curve",
})


def _record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": str(path.resolve()),
            "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def _paths(project: Path, board_name: str | None) -> tuple[Path, Path]:
    route, route_note = board_scoped(project, "route.yaml", board_name)
    nets, nets_note = board_scoped(project, "rules/nets.yaml", board_name)
    if route is None or not route.is_file():
        raise ValueError(f"route contract unresolved: {route_note}")
    if nets is None or not nets.is_file():
        raise ValueError(f"net rules unresolved: {nets_note}")
    return route.resolve(), nets.resolve()


def neighborhoods(route_cfg: Mapping[str, Any]) -> list[dict[str, Any]]:
    cfg = ((route_cfg.get("route") or {}).get("routability") or {})
    rows = cfg.get("coupled_neighborhoods") or []
    if not isinstance(rows, list):
        raise ValueError("route.routability.coupled_neighborhoods must be a list")
    result, ids = [], set()
    for index, raw in enumerate(rows):
        where = f"route.routability.coupled_neighborhoods[{index}]"
        if not isinstance(raw, Mapping) or set(raw) != {"id", "nets", "why"}:
            raise ValueError(f"{where} requires exactly id, nets, and why")
        identity, why = str(raw["id"]).strip(), str(raw["why"]).strip()
        nets = raw["nets"]
        if not identity or identity in ids:
            raise ValueError(f"{where}.id must be non-empty and unique")
        ids.add(identity)
        if (not isinstance(nets, list) or len(nets) < 2 or
                any(not isinstance(net, str) or not net.strip() or
                    net.strip() != net for net in nets) or
                len(set(nets)) != len(nets)):
            raise ValueError(
                f"{where}.nets needs at least two unique exact net names")
        if not why:
            raise ValueError(f"{where}.why must be non-empty")
        result.append({"id": identity, "nets": list(nets), "why": why})
    return result


def _net_classes(nets_cfg: Mapping[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    classes = nets_cfg.get("classes") or {}
    if not isinstance(classes, Mapping):
        raise ValueError("nets classes must be a mapping")
    for class_name, raw in classes.items():
        if not isinstance(raw, Mapping):
            raise ValueError(f"nets class {class_name} must be a mapping")
        members = raw.get("nets") or []
        if not isinstance(members, list):
            raise ValueError(f"nets class {class_name}.nets must be a list")
        for net in members:
            result.setdefault(str(net), []).append(str(class_name))
    return result


def _reference_layers(nets_cfg: Mapping[str, Any]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    rows = nets_cfg.get("reference_plane_checks") or {}
    if not isinstance(rows, Mapping):
        raise ValueError("reference_plane_checks must be a mapping")
    for name, raw in rows.items():
        if not isinstance(raw, Mapping):
            raise ValueError(f"reference_plane_checks.{name} must be a mapping")
        layer, members = raw.get("signal_layer"), raw.get("signal_nets") or []
        if not layer or not isinstance(members, list):
            continue
        for net in members:
            result.setdefault(str(net), set()).add(str(layer))
    return result


def _no_via_nets(nets_cfg: Mapping[str, Any]) -> set[str]:
    result = set()
    groups = nets_cfg.get("length_match") or {}
    if not isinstance(groups, Mapping):
        raise ValueError("length_match must be a mapping")
    for name, raw in groups.items():
        if not isinstance(raw, Mapping):
            raise ValueError(f"length_match.{name} must be a mapping")
        if raw.get("no_vias") is not True:
            continue
        members = raw.get("members") or {}
        if not isinstance(members, Mapping):
            raise ValueError(f"length_match.{name}.members must be a mapping")
        for chain in members.values():
            if not isinstance(chain, list):
                raise ValueError(
                    f"length_match.{name} member chains must be lists")
            result.update(map(str, chain))
    return result


def _realized_policy(board_path: Path, required_nets: list[str],
                     route_cfg: Mapping[str, Any],
                     nets_cfg: Mapping[str, Any]) -> dict[str, Any]:
    board = pcbnew.LoadBoard(str(board_path))
    live = {
        str(pad.GetNetname()) for footprint in board.GetFootprints()
        for pad in footprint.Pads() if str(pad.GetNetname())
    } | {str(item.GetNetname()) for item in board.GetTracks()
         if str(item.GetNetname())}
    class_membership = _net_classes(nets_cfg)
    references = _reference_layers(nets_cfg)
    no_vias = _no_via_nets(nets_cfg)
    routability = ((route_cfg.get("route") or {}).get("routability") or {})
    class_layers = routability.get("class_layers") or {}
    common_layers = ((route_cfg.get("route") or {}).get("common") or {}).get(
        "layers")
    if not isinstance(class_layers, Mapping):
        raise ValueError("route.routability.class_layers must be a mapping")
    if common_layers is not None and not isinstance(common_layers, list):
        raise ValueError("route.common.layers must be a list when present")

    findings, rows = [], []
    copper: dict[str, list[Any]] = {net: [] for net in required_nets}
    for item in board.GetTracks():
        name = str(item.GetNetname())
        if name in copper:
            copper[name].append(item)
    for net in required_nets:
        memberships = class_membership.get(net, [])
        if len(memberships) > 1:
            findings.append(
                f"{net}: belongs to multiple net classes {sorted(memberships)}")
        class_name = memberships[0] if len(memberships) == 1 else None
        explicit = (class_layers.get(class_name) if class_name is not None
                    else class_layers.get("Default"))
        if explicit is not None and (not isinstance(explicit, list) or not explicit):
            findings.append(f"{net}: class layer authority is not a non-empty list")
            explicit = None
        allowed = set(map(str, explicit)) if explicit else (
            set(map(str, common_layers)) if common_layers else None)
        narrowed = references.get(net)
        if narrowed:
            allowed = set(narrowed) if allowed is None else allowed & narrowed
            if not allowed:
                findings.append(
                    f"{net}: class/default layers conflict with reference-plane "
                    f"signal layers {sorted(narrowed)}")
        if net not in live:
            findings.append(f"{net}: absent from witness board")
        tracks = copper[net]
        if not tracks:
            findings.append(f"{net}: no realized copper in combined witness")
        layers, vias = set(), 0
        for item in tracks:
            if item.GetClass() == "PCB_VIA":
                vias += 1
                continue
            layer = str(item.GetLayerName())
            layers.add(layer)
            if allowed is not None and layer not in allowed:
                findings.append(
                    f"{net}: realized layer {layer} outside {sorted(allowed)}")
        if net in no_vias and vias:
            findings.append(
                f"{net}: {vias} via(s) violate existing no_vias authority")
        rows.append({
            "net": net, "class": class_name,
            "allowed_layers": sorted(allowed) if allowed is not None else None,
            "layer_authority": ("reference_plane" if narrowed else
                                "class" if explicit else
                                "route.common" if common_layers else
                                "unrestricted"),
            "realized_layers": sorted(layers), "track_items": len(tracks) - vias,
            "vias": vias, "no_vias": net in no_vias,
            "width_authority": "native prepared .kicad_dru physical_drc",
        })
    default_width = nets_cfg.get("default_track_width")
    if default_width is not None:
        minimum = float(str(default_width).lower().replace("mm", "").strip())
        for net in required_nets:
            if class_membership.get(net):
                continue
            for item in copper[net]:
                if item.GetClass() == "PCB_VIA":
                    continue
                actual = pcbnew.ToMM(item.GetWidth())
                if actual + 1e-9 < minimum:
                    findings.append(
                        f"{net}: realized width {actual:g}mm below current "
                        f"default_track_width {minimum:g}mm")
    return {
        "status": "FAIL" if findings else "PASS",
        "detail": f"{len(required_nets)} net policy census; {len(findings)} finding(s)",
        "nets": rows, "findings": findings,
        "coverage": {
            "nets": len(required_nets),
            "layer_restricted": sum(row["allowed_layers"] is not None for row in rows),
            "no_vias": sum(row["no_vias"] for row in rows),
            "width_native": len(rows),
            "default_width_source": sum(
                not class_membership.get(net) for net in required_nets)
                if default_width is not None else 0,
        },
    }


def _native_runtime(kicad_python: str, kicad_cli: str) -> dict[str, Any]:
    import _pcbnew
    cli = Path(shutil.which(kicad_cli) or kicad_cli).resolve()
    python = Path(shutil.which(kicad_python) or kicad_python).resolve()
    module = Path(str(pcbnew.__file__)).resolve()
    native_module = Path(str(_pcbnew.__file__)).resolve()
    if (not cli.is_file() or not python.is_file() or not module.is_file() or
            not native_module.is_file()):
        raise ValueError("native KiCad/Python runtime cannot be resolved")
    version = subprocess.run(
        [str(cli), "--version"], check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.strip()
    return {
        "kicad_cli": _record(cli), "kicad_python": _record(python),
        "pcbnew_module": _record(module),
        "pcbnew_native": _record(native_module),
        "kicad_cli_version": version,
        "pcbnew_version": str(pcbnew.GetBuildVersion()),
        "python_version": sys.version,
    }


def _regenerate_rules(project: Path, prepared: Path, nets_path: Path,
                      workspace: Path) -> dict[str, Path]:
    """Run the owning source-to-native rule emitter in an isolated tree."""
    rules_root = workspace.with_name(workspace.name + "-current-rules")
    if rules_root.exists():
        raise ValueError(f"current-rule workspace already exists: {rules_root}")
    source = project / "03_src"
    if source.is_dir():
        shutil.copytree(source, rules_root / "03_src")
    else:
        (rules_root / "03_src").mkdir(parents=True)
    flat_nets = rules_root / "03_src/rules/nets.yaml"
    flat_nets.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(nets_path, flat_nets)
    native = rules_root / "04_kicad"
    native.mkdir()
    board = native / "subject.kicad_pcb"
    pro = native / "subject.kicad_pro"
    dru = native / "subject.kicad_dru"
    shutil.copy2(prepared, board)
    shutil.copy2(prepared.with_suffix(".kicad_pro"), pro)
    shutil.copy2(prepared.with_suffix(".kicad_dru"), dru)
    with open(os.devnull, "w", encoding="utf-8") as sink, \
            contextlib.redirect_stdout(sink):
        generate_rules_generic.main([str(rules_root)])
    return {"root": rules_root, "board": board, "project": pro, "rules": dru}


def _canonical_node(node: Any) -> Any:
    if not isinstance(node, list):
        return node
    if node and node[0] in {"uuid", "tstamp"}:
        return None
    values = [_canonical_node(value) for value in node]
    return tuple(value for value in values if value is not None)


def _board_nonrouting_authority(path: Path,
                                route_cfg: Mapping[str, Any]) -> dict[str, Any]:
    """Inventory geometry a copper witness may consume but never redefine."""
    board = pcbnew.LoadBoard(str(path))
    copper = tuple(board.GetLayerName(layer)
                   for layer in board.GetEnabledLayers().CuStack())
    parsed = dru_subject.sexp(path.read_text(encoding="utf-8-sig"))
    root = parsed[0] if len(parsed) == 1 and isinstance(parsed[0], list) else parsed
    keepout_layers = set(map(str, (((route_cfg.get("prep") or {})
                                    .get("keepouts") or {})
                                   .get("layers") or [])))
    rule_areas, outline, keepout_drawings = [], [], []
    for node in root[1:] if isinstance(root, list) else []:
        if not isinstance(node, list) or not node:
            continue
        head = node[0]
        layer = dru_subject.kid(node, "layer")
        layer_name = str(layer[1]) if layer and len(layer) > 1 else None
        canonical = _canonical_node(node)
        if head == "zone" and dru_subject.kid(node, "keepout") is not None:
            rule_areas.append(canonical)
        elif head in GRAPHICS and layer_name == "Edge.Cuts":
            outline.append(canonical)
        elif head in GRAPHICS and layer_name in keepout_layers:
            keepout_drawings.append(canonical)
    key = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"))
    return {
        "enabled_copper_layers": copper,
        "rule_areas": sorted(rule_areas, key=key),
        "outline": sorted(outline, key=key),
        "keepout_drawings": sorted(keepout_drawings, key=key),
    }


def _nonrouting_authority(prepared: Path, witness: Path,
                          route_cfg: Mapping[str, Any]) -> dict[str, Any]:
    before = _board_nonrouting_authority(prepared, route_cfg)
    after = _board_nonrouting_authority(witness, route_cfg)
    labels = {
        "enabled_copper_layers": "enabled copper stack",
        "rule_areas": "rule-area/keepout geometry",
        "outline": "Edge.Cuts geometry",
        "keepout_drawings": "declared keepout-layer drawings",
    }
    findings = [f"prepared {labels[name]} differs in combined witness"
                for name in labels if before[name] != after[name]]
    return {
        "status": "FAIL" if findings else "PASS", "findings": findings,
        "coverage": {
            "enabled_copper_layers": len(before["enabled_copper_layers"]),
            "rule_areas": len(before["rule_areas"]),
            "outline_items": len(before["outline"]),
            "keepout_drawings": len(before["keepout_drawings"]),
        },
    }


def _route_base(prepared: Path, witness: Path,
                route_cfg: Mapping[str, Any]) -> dict[str, Any]:
    failures, footprints, vias, tracks = promoted_route_check.compare(
        prepared, witness, route_cfg=route_cfg)
    nonrouting = _nonrouting_authority(prepared, witness, route_cfg)
    failures.extend(nonrouting["findings"])
    return {
        "status": "FAIL" if failures else "PASS",
        "detail": (f"{len(failures)} finding(s); {footprints} footprints / "
                   f"{vias} vias / {tracks} inherited tracks compared"),
        "findings": failures,
        "coverage": {"footprints": footprints, "vias": vias,
                     "tracks": tracks,
                     "nonrouting": nonrouting["coverage"]},
    }


def _verdict(checks: Mapping[str, Mapping[str, Any]]) -> str:
    statuses = {str(row.get("status")) for row in checks.values()}
    return ("INCOMPLETE" if "INCOMPLETE" in statuses else
            "FAIL" if "FAIL" in statuses else "PASS")


def grade(project: Path, prepared: Path, witness: Path, workspace: Path, *,
          board_name: str | None = None,
          kicad_python: str = "/usr/bin/python3",
          kicad_cli: str = "kicad-cli") -> dict[str, Any]:
    project, prepared, witness, workspace = map(
        lambda value: Path(value).resolve(),
        (project, prepared, witness, workspace))
    route_path, nets_path = _paths(project, board_name)
    route_cfg = yaml.safe_load(route_path.read_text(encoding="utf-8-sig")) or {}
    nets_cfg = yaml.safe_load(nets_path.read_text(encoding="utf-8-sig")) or {}
    groups = neighborhoods(route_cfg)
    if not groups:
        raise ValueError("no coupled neighborhoods are declared")
    required_nets = sorted({net for row in groups for net in row["nets"]})
    native_runtime = _native_runtime(kicad_python, kicad_cli)
    checks: dict[str, dict[str, Any]] = {}

    if not prepared.is_file() or not witness.is_file():
        missing = [str(path) for path in (prepared, witness) if not path.is_file()]
        checks = {
            "route_base": {"status": "INCOMPLETE",
                           "detail": f"board input missing: {missing}"},
            "candidate": {"status": "N-A", "detail": "no readable witness"},
            "realized_policy": {"status": "N-A", "detail": "no readable witness"},
        }
        return _receipt(project, prepared, witness, route_path, nets_path,
                        workspace, groups, required_nets, checks, None,
                        native_runtime, None)

    regenerated = None
    try:
        regenerated = _regenerate_rules(project, prepared, nets_path, workspace)
    except BaseException as exc:
        checks = {
            "route_base": {"status": "INCOMPLETE",
                           "detail": f"current native rules unavailable: {exc}"},
            "candidate": {"status": "N-A", "detail": "rules unavailable"},
            "realized_policy": {"status": "N-A", "detail": "rules unavailable"},
        }
        return _receipt(project, prepared, witness, route_path, nets_path,
                        workspace, groups, required_nets, checks, None,
                        native_runtime, regenerated)

    try:
        checks["route_base"] = _route_base(prepared, witness, route_cfg)
    except Exception as exc:
        checks["route_base"] = {"status": "INCOMPLETE", "detail": str(exc)}

    child = None
    if checks["route_base"]["status"] == "PASS":
        try:
            child = route_candidate_workspace.grade_candidate(
                regenerated["board"], witness, workspace,
                required_nets=required_nets,
                kicad_python=kicad_python, kicad_cli=kicad_cli)
            valid, failures = route_candidate_workspace.verify_receipt(
                workspace / "receipt.json")
            if not valid:
                checks["candidate"] = {
                    "status": "INCOMPLETE",
                    "detail": "child receipt failed independent verification",
                    "findings": failures,
                }
            else:
                status = {"ACCEPTED": "PASS", "REJECTED": "FAIL",
                          "INCOMPLETE": "INCOMPLETE"}.get(
                              str(child.get("verdict")), "INCOMPLETE")
                checks["candidate"] = {
                    "status": status,
                    "detail": f"candidate workspace verdict {child.get('verdict')}",
                    "receipt": _record(workspace / "receipt.json"),
                    "checks": child.get("checks"),
                }
        except Exception as exc:
            checks["candidate"] = {"status": "INCOMPLETE", "detail": str(exc)}
    else:
        checks["candidate"] = {
            "status": "N-A", "detail": "route-base authority did not pass"}

    try:
        checks["realized_policy"] = _realized_policy(
            witness, required_nets, route_cfg, nets_cfg)
    except Exception as exc:
        checks["realized_policy"] = {"status": "INCOMPLETE", "detail": str(exc)}
    return _receipt(project, prepared, witness, route_path, nets_path,
                    workspace, groups, required_nets, checks, child,
                    native_runtime, regenerated)


def _receipt(project: Path, prepared: Path, witness: Path, route_path: Path,
             nets_path: Path, workspace: Path, groups: list[dict[str, Any]],
             required_nets: list[str], checks: dict[str, dict[str, Any]],
             child: dict[str, Any] | None,
             native_runtime: dict[str, Any],
             regenerated: dict[str, Path] | None) -> dict[str, Any]:
    inputs = {
        "route": _record(route_path), "nets": _record(nets_path),
        "checker": _record(Path(__file__).resolve()),
        "candidate_checker": _record(
            Path(route_candidate_workspace.__file__).resolve()),
        "route_base_checker": _record(
            Path(promoted_route_check.__file__).resolve()),
        "authority_parser": _record(Path(dru_subject.__file__).resolve()),
        "rules_generator": _record(Path(generate_rules_generic.__file__).resolve()),
        "kicad_cli": native_runtime["kicad_cli"],
        "kicad_python": native_runtime["kicad_python"],
        "pcbnew_module": native_runtime["pcbnew_module"],
        "pcbnew_native": native_runtime["pcbnew_native"],
    }
    for name, path in (("prepared", prepared), ("witness", witness),
                       ("prepared_project", prepared.with_suffix(".kicad_pro")),
                       ("prepared_rules", prepared.with_suffix(".kicad_dru"))):
        if path.is_file():
            inputs[name] = _record(path)
    if regenerated is not None:
        for name in ("board", "project", "rules"):
            inputs[f"current_rules_{name}"] = _record(regenerated[name])
    receipt = {
        "schema": 1, "kind": "coupled-geometry-receipt-v1",
        "status": _verdict(checks), "project": str(project),
        "subject": inputs.get("witness"), "inputs": inputs,
        "neighborhoods": groups, "required_nets": required_nets,
        "checks": checks, "workspace": str(workspace),
        "coverage": {"checks_expected": sorted(CHECKS),
                     "checks_total": len(CHECKS),
                     "required_nets_total": len(required_nets),
                     "neighborhoods_total": len(groups)},
        "native_runtime": {
            key: native_runtime[key] for key in
            ("kicad_cli_version", "pcbnew_version", "python_version")},
    }
    if child is not None and (workspace / "receipt.json").is_file():
        receipt["child_receipt"] = _record(workspace / "receipt.json")
    return receipt


def verify_mapping(receipt: Any) -> tuple[bool, list[str]]:
    failures = []
    if (not isinstance(receipt, Mapping) or receipt.get("schema") != 1 or
            receipt.get("kind") != "coupled-geometry-receipt-v1"):
        failures.append("unsupported coupled-geometry receipt schema/kind")
        return False, failures
    checks = receipt.get("checks")
    if not isinstance(checks, Mapping) or set(checks) != CHECKS:
        failures.append("coupled-geometry check inventory differs")
        checks = {}
    for name, row in checks.items():
        if not isinstance(row, Mapping) or row.get("status") not in STATUSES:
            failures.append(f"malformed check: {name}")
    if checks and receipt.get("status") != _verdict(checks):
        failures.append("receipt status disagrees with checks")
    inputs = receipt.get("inputs")
    if not isinstance(inputs, Mapping):
        failures.append("receipt inputs must be a mapping")
        inputs = {}
    required_inputs = {
        "route", "nets", "checker", "candidate_checker",
        "route_base_checker", "authority_parser", "kicad_cli",
        "kicad_python", "pcbnew_module", "pcbnew_native", "rules_generator",
    }
    missing_inputs = sorted(required_inputs - set(inputs))
    if missing_inputs:
        failures.append(f"receipt inputs omit producer authority: {missing_inputs}")
    for name, record in inputs.items():
        if not isinstance(record, Mapping) or set(record) != {"path", "sha256", "size"}:
            failures.append(f"malformed input record: {name}")
            continue
        path = Path(str(record["path"]))
        if not path.is_file() or _record(path) != record:
            failures.append(f"input moved or changed: {name}")
    if "witness" in inputs and receipt.get("subject") != inputs["witness"]:
        failures.append("receipt subject differs from exact witness input")
    expected_coverage = {
        "checks_expected": sorted(CHECKS), "checks_total": len(CHECKS),
        "required_nets_total": len(receipt.get("required_nets") or []),
        "neighborhoods_total": len(receipt.get("neighborhoods") or []),
    }
    if receipt.get("coverage") != expected_coverage:
        failures.append("receipt coverage denominator differs")
    runtime = receipt.get("native_runtime")
    if not isinstance(runtime, Mapping) or set(runtime) != {
            "kicad_cli_version", "pcbnew_version", "python_version"}:
        failures.append("native runtime identity is malformed")
    try:
        groups = neighborhoods({"route": {"routability": {
            "coupled_neighborhoods": receipt.get("neighborhoods")}}})
        derived_nets = sorted({net for row in groups for net in row["nets"]})
        if receipt.get("required_nets") != derived_nets:
            failures.append("required net scope disagrees with neighborhoods")
    except Exception as exc:
        failures.append(f"neighborhood receipt scope is malformed: {exc}")
    child_record = receipt.get("child_receipt")
    child = None
    if child_record is not None:
        if not isinstance(child_record, Mapping):
            failures.append("child receipt record is malformed")
        else:
            child_path = Path(str(child_record.get("path") or ""))
            if not child_path.is_file() or _record(child_path) != child_record:
                failures.append("child receipt moved or changed")
            else:
                valid, child_failures = route_candidate_workspace.verify_receipt(
                    child_path)
                failures.extend(f"child: {row}" for row in child_failures)
                if not valid and not child_failures:
                    failures.append("child receipt verification failed")
                try:
                    child = json.loads(child_path.read_text(encoding="utf-8-sig"))
                    if child.get("required_nets") != receipt.get("required_nets"):
                        failures.append("child required-net scope differs")
                except Exception as exc:
                    failures.append(f"child required-net scope unreadable: {exc}")
    if receipt.get("status") == "PASS" and child_record is None:
        failures.append("passing receipt has no independently verified child")
    if receipt.get("status") in {"PASS", "FAIL"}:
        required_subject = {
            "prepared", "witness", "prepared_project", "prepared_rules",
            "current_rules_board", "current_rules_project",
            "current_rules_rules"}
        missing_subject = sorted(required_subject - set(inputs))
        if missing_subject:
            failures.append(
                f"graded receipt omits exact board/rule authority: {missing_subject}")
        elif (inputs["current_rules_board"].get("sha256") !=
              inputs["prepared"].get("sha256")):
            failures.append("current-rule regeneration changed prepared board bytes")
    if all(name in inputs for name in ("route", "nets", "prepared", "witness")):
        try:
            route_cfg = yaml.safe_load(Path(inputs["route"]["path"]).read_text(
                encoding="utf-8-sig")) or {}
            nets_cfg = yaml.safe_load(Path(inputs["nets"]["path"]).read_text(
                encoding="utf-8-sig")) or {}
            prepared = Path(inputs["prepared"]["path"])
            witness = Path(inputs["witness"]["path"])
            expected_base = _route_base(prepared, witness, route_cfg)
            if checks.get("route_base") != expected_base:
                failures.append("route-base check differs from bound inputs")
            expected_policy = _realized_policy(
                witness, list(receipt.get("required_nets") or []),
                route_cfg, nets_cfg)
            if checks.get("realized_policy") != expected_policy:
                failures.append("realized-policy check differs from bound inputs")
        except Exception as exc:
            failures.append(f"bound policy cannot be independently regraded: {exc}")
    if child is not None:
        expected_status = {"ACCEPTED": "PASS", "REJECTED": "FAIL",
                           "INCOMPLETE": "INCOMPLETE"}.get(
                               str(child.get("verdict")), "INCOMPLETE")
        expected_candidate = {
            "status": expected_status,
            "detail": f"candidate workspace verdict {child.get('verdict')}",
            "receipt": dict(child_record),
            "checks": child.get("checks"),
        }
        if checks.get("candidate") != expected_candidate:
            failures.append("candidate check differs from verified child receipt")
    if isinstance(runtime, Mapping) and all(
            name in inputs for name in ("kicad_cli", "kicad_python")):
        try:
            current_runtime = _native_runtime(
                inputs["kicad_python"]["path"], inputs["kicad_cli"]["path"])
            expected_runtime = {key: current_runtime[key] for key in (
                "kicad_cli_version", "pcbnew_version", "python_version")}
            if runtime != expected_runtime:
                failures.append("native runtime metadata differs")
        except Exception as exc:
            failures.append(f"native runtime cannot be independently identified: {exc}")
    return not failures, failures


def verify(receipt_path: Path) -> tuple[bool, list[str]]:
    try:
        receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return False, [f"receipt cannot be read: {exc}"]
    return verify_mapping(receipt)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    grader = sub.add_parser("grade")
    grader.add_argument("project", type=Path)
    grader.add_argument("--prepared", type=Path, required=True)
    grader.add_argument("--witness", type=Path, required=True)
    grader.add_argument("--workspace", type=Path, required=True)
    grader.add_argument("--json", type=Path, required=True)
    grader.add_argument("--board-name")
    grader.add_argument("--kicad-python", default="/usr/bin/python3")
    grader.add_argument("--kicad-cli", default="kicad-cli")
    verifier = sub.add_parser("verify")
    verifier.add_argument("receipt", type=Path)
    args = parser.parse_args(argv)
    if args.command == "verify":
        valid, failures = verify(args.receipt)
        for failure in failures:
            print(f"  FAIL {failure}")
        print(f"COUPLED-GEOMETRY RECEIPT {'PASS' if valid else 'FAIL'}")
        return 0 if valid else 1
    try:
        output = args.json.resolve()
        workspace = args.workspace.resolve()
        if output.exists():
            raise ValueError(f"receipt output already exists: {output}")
        if workspace.exists():
            raise ValueError(f"attempt workspace already exists: {workspace}")
        receipt = grade(
            args.project, args.prepared, args.witness, args.workspace,
            board_name=args.board_name, kicad_python=args.kicad_python,
            kicad_cli=args.kicad_cli)
        _atomic_json(output, receipt)
        valid, failures = verify(output)
        if not valid:
            output.unlink(missing_ok=True)
            for failure in failures:
                print(f"  FAIL {failure}")
            print("COUPLED-GEOMETRY INCOMPLETE: freshly written receipt did "
                  "not survive independent verification")
            return 2
    except Exception as exc:
        print(f"COUPLED-GEOMETRY INCOMPLETE: {exc}")
        return 2
    print(f"COUPLED-GEOMETRY {receipt['status']}: "
          f"{len(receipt['required_nets'])} required net(s); "
          f"receipt={args.json.resolve()}")
    return {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}[receipt["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
