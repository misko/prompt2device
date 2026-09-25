#!/usr/bin/env python3
"""Admit placement only when legality and declared route feasibility agree.

This is a read-only placement-stage compositor.  It combines the exact outline,
body and corridor-capacity checks with critical-pair inventory, route ownership,
layer eligibility, and explicit high-speed component topology declarations.
It does not generate accepted copper and therefore cannot become a hidden
routing stage.

Optional ``route.routability.topology`` rows have this schema::

  - ref: U_ESD1
    kind: shunt                   # shunt|series_flow_through|series_directional
    signal_pads: ["1", "2"]
    return_pads: ["3"]           # required for shunt
    pairs: [P1_PORT]             # or signal_nets for non-critical analog nets
    why: "direct-on-trace USB clamp"

When ``route.routability.require_topology`` is true, every footprint whose
part dossier declares ``layout.route_topology.kind`` must have a matching row.
The board row remains the instance authority; the dossier is the part-class
authority.
For non-critical analog circuits, ``signal_nets`` binds exact net names instead
of inventing a controlled-impedance pair. It cannot overlap any critical pair
or coexist with ``pairs``; critical routes still require the pair contract.

Two optional source contracts close common placement-time omissions without
turning this gate into a router:

``connector_lanes`` maps ordered physical pads to exact nets, so a correct
connector orientation cannot hide a crossed or reversed lane assignment.
``series_power_paths`` lists explicit copper and component transitions from
input to load, so a fuse/switch/protection device cannot be present but bypassed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import uuid
from pathlib import Path
from typing import Any, Mapping, Sequence

import pcbnew
import yaml

import critical_route_check
import board_authority
import coupled_geometry_preflight
import placement_cell_checks
import placement_gates
import route_candidate_workspace
import route_ownership_preflight
from tier_preflight import board_scoped

PCB_PIPELINE = Path(__file__).resolve().parents[2] / "pcb-design" / "scripts"
if str(PCB_PIPELINE) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(PCB_PIPELINE))
from pipeline_identity import TypedIdentityInput, subject_identity  # noqa: E402
from pipeline_contract import StageResult  # noqa: E402
from pipeline_stage_evidence import (  # noqa: E402
    new_run_id, require_safe_output_layout, utc_now, write_json_atomic,
)


KINDS = {"shunt", "series_flow_through", "series_directional"}
SHADOW_INPUTS = frozenset({
    "placement_cells", "stack_authority", "route_plan_authority",
    "topology_migration", "circuit", "functional_cell_observations",
})
AUTHORITATIVE_CHECKS = frozenset({
    "physical_placement", "critical_route_contract", "route_ownership",
    "endpoint_topology", "pair_footprint", "layer_eligibility", "connector_lane_order",
    "series_power_paths", "coupled_geometry",
})
CHECK_STATUSES = frozenset({"PASS", "N-A", "FAIL", "INCOMPLETE"})


def _mm(value: Any) -> float:
    if isinstance(value, bool):
        raise ValueError("boolean is not a dimension")
    result = float(str(value).removesuffix("mm"))
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"invalid positive dimension {value!r}")
    return result


def _pair_footprints(project: Path, board: Any, route_cfg: Mapping[str, Any],
                     nets_cfg: Mapping[str, Any]) -> dict[str, Any]:
    """Screen one uniform centered strip at every declared pair terminal.

    This local necessary-condition screen does not prove a route impossible.
    Native pad shapes perform the copper collision tests, including rotation
    and roundrect/oblong geometry. Source path leaves close the denominator.
    """
    pairs = (route_cfg.get("route") or {}).get("preflight_critical_pairs") or []
    if not pairs:
        source_pairs = [name for name, row in (nets_cfg.get("length_match") or {}).items()
                        if isinstance(row, dict) and
                        isinstance(row.get("members"), dict) and
                        {"P", "N"} <= set(row["members"])]
        class_pairs = [name for name, row in (nets_cfg.get("classes") or {}).items()
                       if isinstance(row, dict) and row.get("diff_pair")]
        if source_pairs or class_pairs:
            return {"status": "INCOMPLETE", "detail": "controlled source has no route pair inventory",
                    "pairs": [], "findings": [],
                    "unresolved": [f"missing preflight pair: {name}" for name in source_pairs + class_pairs]}
        return {"status": "N-A", "detail": "no controlled pairs declared",
                "pairs": [], "findings": []}
    findings: list[str] = []
    unknown: list[str] = []
    observed: list[dict[str, Any]] = []
    footprint_rows = list(board.GetFootprints())
    fps = {str(fp.GetReference()): fp for fp in footprint_rows}
    if len(fps) != len(footprint_rows):
        unknown.append("duplicate footprint reference in pair board")
    pad_rows = [(str(fp.GetReference()), str(pad.GetNumber()), pad)
                for fp in footprint_rows
                for pad in fp.Pads()]
    pads = {(ref, num): pad for ref, num, pad in pad_rows}
    # Resolve only dossiers actually used by a declared terminal. The board
    # value is the part identity; a missing/ambiguous alias is unresolved.
    dossiers: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
    for path in (project / "02_parts").glob("*/part.yaml"):
        doc = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        if isinstance(doc, dict):
            dossiers.setdefault(str(doc.get("mpn") or ""), []).append((path, doc))
    classes = nets_cfg.get("classes") or {}
    length = nets_cfg.get("length_match") or {}
    waves = {str(row.get("name")): row for row in
             (route_cfg.get("route") or {}).get("waves") or []
             if isinstance(row, dict)}
    for pair in pairs:
        if not isinstance(pair, dict) or not all(pair.get(k) for k in ("name", "p", "n")):
            unknown.append("malformed controlled-pair declaration")
            continue
        name, pnet, nnet = (str(pair[k]) for k in ("name", "p", "n"))
        label = f"{name} ({pnet}/{nnet})"
        memberships = [(key, value) for key, value in classes.items()
                       if isinstance(value, dict) and
                       {pnet, nnet} <= set(value.get("nets") or [])]
        wave = waves.get(str(pair.get("wave") or ""))
        if len(memberships) != 1 or not isinstance(wave, dict):
            unknown.append(f"{label}: one shared pair class and diff wave are required")
            continue
        class_name, cls = memberships[0]
        layer_names = (wave.get("layers") or pair.get("allowed_layers") or
                       (route_cfg.get("route") or {}).get("common", {}).get("layers"))
        if not isinstance(layer_names, list) or len(layer_names) != 1 or layer_names[0] not in {"F.Cu", "B.Cu"}:
            unknown.append(f"{label}: one supported pair signal layer is required")
            continue
        signal_layer = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}[layer_names[0]]
        try:
            diff = cls["diff_pair"]
            width, gap = _mm(diff["width"]), _mm(diff["gap"])
            if (abs(width - _mm(cls["min_width"])) > 1e-6 or
                    abs(width - _mm(wave["track_width"])) > 1e-6 or
                    abs(gap - _mm(wave["diff_pair_gap"])) > 1e-6):
                unknown.append(f"{label}: class and wave pair width/gap differ")
            default_clearance = _mm(nets_cfg["default_clearance"])
            pair_clearance = _mm(cls["clearance"])
        except (KeyError, TypeError, ValueError) as exc:
            unknown.append(f"{label}: pair dimensions/clearances unresolved: {exc}")
            continue
        relevant_scopes = [row for row in nets_cfg.get("scoped_clearances") or []
                           if isinstance(row, dict) and
                           ({pnet, nnet} & set((row.get("nets") or []) +
                                               (row.get("nets_a") or []) +
                                               (row.get("nets_b") or [])))]
        relevant_scopes += [row for row in nets_cfg.get("scoped_floors") or []
                            if isinstance(row, dict) and
                            (not row.get("nets") or
                             {pnet, nnet} & set(row.get("nets") or []))]
        contract = length.get(name)
        controlled = [row for row in nets_cfg.get("controlled_pair_clearances") or []
                      if isinstance(row, dict) and row.get("pair") == name]
        controlled_pair = (len(controlled) == 1 and
                           controlled[0].get("nets_a") == [pnet] and
                           controlled[0].get("nets_b") == [nnet] and
                           controlled[0].get("layer") == layer_names[0] and
                           contract.get("no_vias") is True if isinstance(contract, dict) else False)
        if controlled and not controlled_pair:
            unknown.append(f"{label}: controlled pair rule declaration unresolved")
        if controlled_pair:
            try:
                if abs(_mm(controlled[0]["clearance"]) - gap) > 1e-6:
                    unknown.append(f"{label}: controlled pair clearance differs from gap")
                else:
                    pair_clearance = gap
            except (KeyError, TypeError, ValueError):
                unknown.append(f"{label}: controlled pair clearance unresolved")
        if relevant_scopes:
            unknown.append(f"{label}: scoped pair width/clearance needs local rule-area evaluation")
        elif gap + 1e-6 < pair_clearance:
            findings.append(f"{label}: declared pair gap {gap:.3f} mm is below unscoped effective clearance {pair_clearance:.3f} mm; uniform pair rules conflict")
        contract = length.get(name)
        paths = contract.get("paths") if isinstance(contract, dict) else None
        if not isinstance(paths, dict) or not paths.get("P") or not paths.get("N"):
            unknown.append(f"{label}: complete P/N source path leaves are required")
            continue
        path_ids = {side: {str(row.get("id")) for row in paths[side]
                           if isinstance(row, dict)} for side in ("P", "N")}
        if path_ids["P"] != path_ids["N"] or not path_ids["P"] or any(
                len(path_ids[side]) != len(paths[side]) for side in ("P", "N")):
            unknown.append(f"{label}: P/N path IDs are not complete counterparts")
            continue
        expected: set[tuple[str, str]] = set()
        for side, net in (("P", pnet), ("N", nnet)):
            for row in paths[side]:
                for segment in row.get("segments") or []:
                    if not isinstance(segment, dict) or segment.get("net") != net:
                        unknown.append(f"{label}: {side} path segment net is unresolved")
                        continue
                    for endpoint in (segment.get("from"), segment.get("to")):
                        if not isinstance(endpoint, str) or "." not in endpoint:
                            unknown.append(f"{label}: malformed source endpoint {endpoint!r}")
                            continue
                        ref, source_num = endpoint.rsplit(".", 1)
                        fp = fps.get(ref)
                        if fp is None:
                            unknown.append(f"{label}: source endpoint {endpoint} footprint absent")
                            continue
                        native_num = source_num
                        matches = dossiers.get(str(fp.GetValue()), [])
                        if len(matches) == 1 and matches[0][1].get("pin_aliases"):
                            aliases = matches[0][1]["pin_aliases"]
                            native_matches = [str(a.get("footprint")) for a in aliases.values()
                                              if isinstance(a, dict) and
                                              str(a.get("schematic")) == source_num]
                            if len(native_matches) != 1:
                                unknown.append(f"{label}: {endpoint} alias unresolved")
                                continue
                            native_num = native_matches[0]
                        elif len(matches) > 1:
                            unknown.append(f"{label}: {ref} part dossier ambiguous")
                            continue
                        pad = pads.get((ref, native_num))
                        if pad is None or str(pad.GetNetname()) != net:
                            unknown.append(f"{label}: {endpoint} => {ref}.{native_num} absent or wrong net")
                            continue
                        expected.add((ref, native_num))
        pair_pads = {(ref, num): pad for (ref, num), pad in pads.items()
                     if str(pad.GetNetname()) in {pnet, nnet}}
        pair_rows = [(ref, num) for ref, num, pad in pad_rows
                     if str(pad.GetNetname()) in {pnet, nnet}]
        if len(pair_rows) != len(pair_pads):
            unknown.append(f"{label}: duplicate native pair pad identity")
        if not pair_pads or not expected <= set(pair_pads):
            unknown.append(f"{label}: declared terminal inventory is incomplete")
            continue
        extra = sorted(set(pair_pads) - expected)
        if extra:
            unknown.append(f"{label}: board has undeclared pair terminals "
                           + ", ".join(f"{ref}.{num}" for ref, num in extra))
        if relevant_scopes and gap + 1e-6 < pair_clearance:
            areas = {str(zone.GetZoneName()): zone.GetBoundingBox()
                     for zone in board.Zones() if zone.GetIsRuleArea()}
            outside = []
            for (ref, num), item in pair_pads.items():
                covered = False
                for rule in relevant_scopes:
                    box = areas.get(str(rule.get("zone")))
                    center = item.GetPosition()
                    if (box is not None and box.GetLeft() <= center.x <= box.GetRight()
                            and box.GetTop() <= center.y <= box.GetBottom()):
                        covered = True
                if not covered:
                    outside.append(f"{ref}.{num}")
            if outside:
                findings.append(f"{label}: declared {gap:.3f} mm pair gap is below "
                                f"{pair_clearance:.3f} mm class clearance outside "
                                f"scoped rule area(s); uncovered terminal centers: "
                                + ", ".join(sorted(outside)))
        # Board net inventory expands the declared leaves, so duplicate contacts
        # and extra shunt pads cannot silently escape the geometry denominator.
        for (ref, num), pad in sorted(pair_pads.items()):
            net = str(pad.GetNetname())
            if (not pad.GetLayerSet().Contains(signal_layer) or
                    pad.GetShape() == pcbnew.PAD_SHAPE_CUSTOM):
                unknown.append(f"{label}: {ref}.{num} pad copper shape/layer unsupported")
                continue
            layer = signal_layer
            shape = pad.GetEffectiveShape(layer)
            center = pad.GetPosition()
            # The centered track's width at its pad origin is a necessary
            # envelope for *any* longitudinal centered escape direction.
            launch_origin = pcbnew.SHAPE_SEGMENT(center, center,
                                                  pcbnew.FromMM(width))
            pad_issues = []
            for other_ref, other_num, other in pad_rows:
                if other is pad or not other.GetLayerSet().Contains(layer):
                    continue
                other_net = str(other.GetNetname())
                if other_net == net:
                    continue
                other_shape = other.GetEffectiveShape(layer)
                # A different-net pad must itself satisfy its copper rule.
                pad_clearance = pair_clearance
                other_classed = False
                for other_cls in classes.values():
                    if isinstance(other_cls, dict) and other_net in (other_cls.get("nets") or []):
                        try:
                            pad_clearance = max(pad_clearance, _mm(other_cls["clearance"]))
                            other_classed = True
                        except (KeyError, ValueError, TypeError):
                            unknown.append(f"{label}: {other_net} clearance unresolved")
                if not other_classed:
                    pad_clearance = max(pad_clearance, default_clearance)
                if ref == other_ref:
                    for rule in nets_cfg.get("same_footprint_pad_clearances") or []:
                        if ref in (rule.get("refs") or []):
                            pad_clearance = _mm(rule["clearance"])
                if shape.Collide(other_shape, pcbnew.FromMM(pad_clearance)):
                    pad_issues.append(f"pad copper {ref}.{num} to {other_ref}.{other_num} below {pad_clearance:.3f} mm")
                # Package pad exceptions never waive track-to-pad clearance.
                track_clearance = pair_clearance
                if other_net not in {pnet, nnet}:
                    other_classed = False
                    for other_cls in classes.values():
                        if isinstance(other_cls, dict) and other_net in (other_cls.get("nets") or []):
                            track_clearance = max(track_clearance,
                                                  _mm(other_cls["clearance"]))
                            other_classed = True
                    if not other_classed:
                        track_clearance = max(track_clearance, default_clearance)
                required = max(gap, track_clearance) if other_net in {pnet, nnet} else track_clearance
                if launch_origin.Collide(other_shape, pcbnew.FromMM(required)):
                    pad_issues.append(f"centered {width:.3f} mm launch envelope at {ref}.{num} conflicts with {other_ref}.{other_num} ({required:.3f} mm clearance)")
            if pad_issues:
                findings.extend(f"{label}: {issue}; uniform centered launch unsupported"
                                for issue in pad_issues)
            observed.append({"pair": name, "pad": f"{ref}.{num}", "net": net,
                             "source_declared": (ref, num) in expected,
                             "width_mm": width, "gap_mm": gap,
                             "status": "FAIL" if pad_issues else "PASS"})
    status = "INCOMPLETE" if unknown else "FAIL" if findings else "PASS"
    return {"status": status,
            "detail": f"{len(observed)} terminal pad(s) screened; centered uniform strategy only",
            "pairs": observed, "findings": findings, "unresolved": unknown}


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


def _functional_cell_needs_obstacles(contract: Mapping[str, Any]) -> bool:
    replicas = contract.get("replicas") or []
    if isinstance(replicas, list) and replicas:
        return True
    cells = contract.get("cells") or []
    if not isinstance(cells, list):
        return True
    return any(isinstance(cell, Mapping) and any(
        cell.get(name) for name in (
            "reservations", "route_reservations", "constrained_pads",
            "escape_decisions", "ground_egress", "ground_egresses",
            "critical_ground_egress")) for cell in cells)


def _functional_cell_shadow(
        config_path: Path, board: Any, *,
        observed_parts: Mapping[str, Any] | None = None,
        observed_obstacles: Sequence[Mapping[str, Any]] | None = None,
        observed_fabrication: Mapping[str, Any] | None = None,
        ) -> dict[str, Any]:
    """Grade the schema-1 functional-cell contract without owning admission.

    MPNs come from footprint properties or an independently generated
    ref-to-MPN observation supplied by the caller.  Obstacles and fabrication
    capability likewise come only from explicit observation inputs.  An
    authored ``snapshot`` block is ignored: it may describe an intended
    fixture, but its booleans cannot serve as the measurement that grades the
    same declaration.
    """
    contract = yaml.safe_load(
        config_path.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(contract, dict):
        raise ValueError("placement_cells.yaml must contain a mapping")
    if "snapshot" in contract and not isinstance(contract["snapshot"], Mapping):
        raise ValueError("placement_cells.snapshot must be a mapping")
    snapshot = placement_cell_checks.snapshot_from_pcbnew(
        board, observed_parts=observed_parts)
    if observed_obstacles is not None:
        if (not isinstance(observed_obstacles, Sequence) or
                isinstance(observed_obstacles, (str, bytes)) or
                any(not isinstance(row, Mapping) for row in observed_obstacles)):
            raise ValueError("observed functional-cell obstacles must be a list of mappings")
        snapshot["obstacles"] = [dict(row) for row in observed_obstacles]
    if observed_fabrication is not None:
        if not isinstance(observed_fabrication, Mapping):
            raise ValueError("observed fabrication facts must be a mapping")
        snapshot["fabrication"] = dict(observed_fabrication)
    report = placement_cell_checks.evaluate_placement_cells(contract, snapshot)
    observation_findings = []
    if (_functional_cell_needs_obstacles(contract) and
            observed_obstacles is None):
        observation_findings.append(
            "applicable collision/replica checks lack independently observed "
            "obstacle data")
    status = "INCOMPLETE" if observation_findings else report["status"]
    return {
        "status": status,
        "detail": ("; ".join(observation_findings) if observation_findings else
                   f"{report['coverage']['graded']}/"
                   f"{report['coverage']['total']} functional-cell facts graded"),
        "report": report,
        "observation_findings": observation_findings,
        "observations": {
            "mpn_source": ("caller" if observed_parts is not None
                           else "footprint_properties"),
            "obstacles_observed": observed_obstacles is not None,
            "obstacle_count": (len(observed_obstacles)
                               if observed_obstacles is not None else None),
            "fabrication_observed": observed_fabrication is not None,
            "authored_snapshot_ignored": "snapshot" in contract,
        },
        "authority": "SHADOW",
        "promotion_note": (
            "independent MPN/obstacle adapters and pcbnew-measured canary "
            "equivalence are required before promotion"),
    }


def _functional_observations(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, Mapping):
        raise ValueError("functional-cell observations must contain a mapping")
    required = {"schema", "kind", "parts", "obstacles"}
    allowed = required | {"fabrication"}
    if not required <= set(value) or set(value) - allowed:
        raise ValueError(
            "functional-cell observation fields differ "
            f"(missing={sorted(required - set(value))}, "
            f"unknown={sorted(set(value) - allowed)})")
    if (value["schema"] != 1 or
            value["kind"] != "functional-cell-observations-v1"):
        raise ValueError("unsupported functional-cell observation schema/kind")
    if not isinstance(value["parts"], Mapping):
        raise ValueError("functional-cell observations.parts must be a mapping")
    if (not isinstance(value["obstacles"], list) or
            any(not isinstance(row, Mapping) for row in value["obstacles"])):
        raise ValueError("functional-cell observations.obstacles must be a list")
    if not isinstance(value.get("fabrication", {}), Mapping):
        raise ValueError("functional-cell observations.fabrication must be a mapping")
    return {
        "parts": dict(value["parts"]),
        "obstacles": [dict(row) for row in value["obstacles"]],
        "fabrication": (dict(value["fabrication"])
                        if "fabrication" in value else None),
    }


def _observed_part_identities(circuit_json: Path | None) -> dict[str, dict[str, str]]:
    """Read independent exact ref-to-MPN identity from generated circuit JSON."""
    if circuit_json is None or not circuit_json.is_file():
        return {}
    payload = json.loads(circuit_json.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, list):
        raise ValueError("circuit.json must contain a list")
    result: dict[str, dict[str, str]] = {}
    for row in payload:
        if not isinstance(row, Mapping) or row.get("type") != "source_component":
            continue
        ref = str(row.get("name") or "").strip()
        mpn = str(row.get("manufacturer_part_number") or "").strip()
        if not ref or not mpn:
            continue
        if ref in result and result[ref]["mpn"] != mpn:
            raise ValueError(f"circuit.json assigns conflicting exact MPNs to {ref}")
        result[ref] = {"mpn": mpn}
    return result


def _observed_source_facts(board: Any,
                           circuit_json: Path | None = None) -> dict[str, Any]:
    """Extract live authority facts independently from the exact board/source.

    Refdes and net identity come from the loaded PCB.  Exact MPN population is
    read from the generated circuit artifact when present; it is never copied
    from the stack, route-plan, or migration contracts being checked.
    """
    refs: set[str] = set()
    nets: set[str] = set()
    for footprint in board.GetFootprints():
        ref = str(footprint.GetReference() or "").strip()
        if ref:
            refs.add(ref)
        for pad in footprint.Pads():
            net = str(pad.GetNetname() or "").strip()
            if net:
                nets.add(net)

    mpns = {row["mpn"] for row in
            _observed_part_identities(circuit_json).values()}
    return {
        "schema": "observed-source-facts-v1",
        "refs": sorted(refs),
        "nets": sorted(nets),
        "mpns": sorted(mpns),
        "occurrences": [],
    }


def _source_authority_shadow(stack_path: Path, route_plan_path: Path,
                             migration_path: Path | None, board: Any,
                             circuit_json: Path | None) -> dict[str, Any]:
    """Compile source-to-prep authority without changing admission yet."""
    stack = yaml.safe_load(stack_path.read_text(encoding="utf-8-sig")) or {}
    route_plan = yaml.safe_load(
        route_plan_path.read_text(encoding="utf-8-sig")) or {}
    migration = None
    if migration_path is not None:
        migration = yaml.safe_load(
            migration_path.read_text(encoding="utf-8-sig")) or {}
    observed = _observed_source_facts(board, circuit_json)
    report = board_authority.compile_source_prep_authority(
        stack=stack, observed=observed, route_plan=route_plan,
        migration=migration)
    valid, failures = board_authority.verify_authority(
        report, stack=stack, observed=observed, route_plan=route_plan,
        migration=migration)
    status = report["verdict"] if valid else "INCOMPLETE"
    return {
        "status": status,
        "detail": (f"{report['coverage']['owned_live_nets']}/"
                   f"{report['coverage']['live_nets']} live nets owned; "
                   f"{len(report['findings'])} finding(s)"),
        "report": report,
        "verification_failures": failures,
        "authority": "SHADOW",
        "promotion_note": (
            "dual-run until fleet canaries prove exact board/source extraction "
            "and no legacy gate is weakened"),
    }


def _topology(route_cfg: dict[str, Any], board: Any,
              project: Path) -> dict[str, Any]:
    route = route_cfg.get("route") or {}
    cfg = route.get("routability") or {}
    if not isinstance(cfg, dict):
        raise ValueError("route.routability must be a mapping")
    rows = cfg.get("topology") or []
    if not isinstance(rows, list):
        raise ValueError("route.routability.topology must be a list")
    if not rows and cfg.get("require_topology"):
        return {
            "status": "FAIL",
            "detail": "topology declarations are required but none exist",
            "rows": [],
            "findings": [
                "route.routability.require_topology is true but topology is empty"
            ],
        }
    if not rows:
        return {"status": "N-A", "detail": "no topology rows declared",
                "rows": [], "findings": []}
    footprints = {str(fp.GetReference()): fp for fp in board.GetFootprints()}
    dossiers = {}
    for path in sorted((project / "02_parts").glob("*/part.yaml")):
        value = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        if isinstance(value, dict) and value.get("mpn"):
            dossiers[str(value["mpn"])] = (path, value)
    pairs = {str(row.get("name")) for row in
             route.get("preflight_critical_pairs") or [] if isinstance(row, dict)}
    pair_nets = {
        str(row.get("name")): {str(row.get("p")), str(row.get("n"))}
        for row in route.get("preflight_critical_pairs") or []
        if isinstance(row, dict) and row.get("name") and row.get("p")
        and row.get("n")
    }
    seen, findings, graded = set(), [], []
    for index, raw in enumerate(rows):
        where = f"route.routability.topology[{index}]"
        if not isinstance(raw, dict):
            findings.append(f"{where}: expected a mapping")
            continue
        ref = str(raw.get("ref") or "").strip()
        part_mpn = str(raw.get("part_mpn") or "").strip()
        kind = str(raw.get("kind") or "").strip()
        why = str(raw.get("why") or "").strip()
        signal = [str(value) for value in raw.get("signal_pads") or []]
        returns = [str(value) for value in raw.get("return_pads") or []]
        common = [str(value) for value in raw.get("common_signal_pads") or []]
        selected = [str(value) for value in raw.get("selected_signal_pads") or []]
        unused = [str(value) for value in raw.get("unused_signal_pads") or []]
        inputs = [str(value) for value in raw.get("input_signal_pads") or []]
        outputs = [str(value) for value in raw.get("output_signal_pads") or []]
        row_pairs = [str(value) for value in raw.get("pairs") or []]
        named_nets = raw.get("signal_nets")
        if not ref or ref in seen:
            findings.append(f"{where}.ref must be non-empty and unique")
        seen.add(ref)
        fp = footprints.get(ref)
        if fp is None:
            findings.append(f"{where}: footprint {ref!r} is absent")
            continue
        dossier = dossiers.get(part_mpn)
        if dossier is None:
            findings.append(f"{where}.part_mpn {part_mpn!r} has no exact dossier")
        else:
            layout = dossier[1].get("layout") or {}
            dossier_topology = (layout.get("route_topology") or {}) \
                if isinstance(layout, dict) else {}
            declared = dossier_topology.get("kind")
            if declared != kind:
                findings.append(
                    f"{where}: instance kind {kind!r} disagrees with "
                    f"{part_mpn} dossier kind {declared!r}")
        if kind not in KINDS:
            findings.append(f"{where}.kind must be one of {sorted(KINDS)}")
        if not why:
            findings.append(f"{where}.why is required")
        if len(signal) < 2 or len(signal) != len(set(signal)):
            findings.append(f"{where}.signal_pads needs at least two unique pads")
        if kind == "shunt" and not returns:
            findings.append(f"{where}: shunt requires return_pads")
        if kind != "shunt" and returns:
            findings.append(f"{where}: series component may not declare return_pads")
        if kind == "series_directional":
            if (not common or not selected or len(common) != len(selected)
                    or set(signal) != set(common + selected)):
                findings.append(
                    f"{where}: series_directional requires equal common/selected "
                    "banks whose union is signal_pads")
            if set(unused) & set(signal):
                findings.append(f"{where}: unused_signal_pads overlaps signal_pads")
        elif common or selected or unused:
            findings.append(
                f"{where}: directional bank fields require series_directional")
        if kind == "series_flow_through":
            if (not inputs or not outputs or len(inputs) != len(outputs)
                    or set(signal) != set(inputs + outputs)):
                findings.append(
                    f"{where}: series_flow_through requires equal input/output "
                    "banks whose union is signal_pads")
        elif inputs or outputs:
            findings.append(
                f"{where}: input/output bank fields require series_flow_through")
        if named_nets is None:
            if not row_pairs or any(name not in pairs for name in row_pairs):
                findings.append(f"{where}.pairs must name declared critical pairs")
            expected_nets = set().union(*(pair_nets.get(name, set())
                                          for name in row_pairs))
        else:
            valid_names = (isinstance(named_nets, list) and len(named_nets) >= 2
                           and all(isinstance(n, str) and n.strip() == n and n
                                   for n in named_nets)
                           and len(set(named_nets)) == len(named_nets))
            expected_nets = set(named_nets) if valid_names else set()
            critical_nets = set().union(*pair_nets.values())
            if (not valid_names or "pairs" in raw or
                    expected_nets & critical_nets):
                findings.append(f"{where}.signal_nets must name unique non-critical "
                                "nets, exclusively instead of pairs")
        pad_numbers = {str(pad.GetNumber()) for pad in fp.Pads()}
        unknown = sorted(set(signal + returns + common + selected + unused
                             + inputs + outputs) - pad_numbers)
        if unknown:
            findings.append(f"{where}: unknown pad(s) {unknown} on {ref}")
        signal_nets = [str(pad.GetNetname()) for pad in fp.Pads()
                       if str(pad.GetNumber()) in signal]
        if kind == "shunt" and len(set(signal_nets)) != len(signal_nets):
            findings.append(f"{where}: shunt signal pads do not land on distinct nets")
        if expected_nets and set(signal_nets) != expected_nets:
            findings.append(
                f"{where}: signal-pad nets {sorted(set(signal_nets))} disagree "
                f"with declared signal nets {sorted(expected_nets)}")
        if dossier is not None:
            dossier_fields = {
                "shunt": ("signal_pads", "return_pads"),
                "series_directional": ("common_signal_pads",
                                       "selected_signal_pads",
                                       "unused_signal_pads"),
                "series_flow_through": ("input_signal_pads",
                                        "output_signal_pads"),
            }.get(kind, ())
            for field in dossier_fields:
                instance_value = [str(value) for value in raw.get(field) or []]
                dossier_value = [str(value) for value in
                                 dossier_topology.get(field) or []]
                if set(instance_value) != set(dossier_value):
                    findings.append(
                        f"{where}.{field} disagrees with {part_mpn} dossier: "
                        f"{sorted(instance_value)} != {sorted(dossier_value)}")
        graded.append({"ref": ref, "part_mpn": part_mpn, "kind": kind,
                       "part_yaml": str(dossier[0].resolve()) if dossier else None,
                       "signal_pads": signal,
                       "return_pads": returns,
                       "common_signal_pads": common,
                       "selected_signal_pads": selected,
                       "unused_signal_pads": unused,
                       "input_signal_pads": inputs,
                       "output_signal_pads": outputs, "pairs": row_pairs,
                       "signal_nets": signal_nets, "why": why})
    return {"status": "FAIL" if findings else "PASS",
            "detail": f"{len(graded)}/{len(rows)} topology row(s) graded",
            "rows": graded, "findings": findings}


def _layers(route_cfg: dict[str, Any], board: Any) -> dict[str, Any]:
    route = route_cfg.get("route") or {}
    cfg = route.get("routability") or {}
    roles = cfg.get("layer_roles") or {}
    eligibility = cfg.get("class_layers") or {}
    if not roles and not eligibility:
        return {"status": "N-A", "detail": "no executable layer roles declared",
                "findings": []}
    if not isinstance(roles, dict) or not isinstance(eligibility, dict):
        raise ValueError("routability layer_roles/class_layers must be mappings")
    enabled = {board.GetLayerName(layer) for layer in board.GetEnabledLayers().Seq()
               if pcbnew.IsCopperLayer(layer)}
    allowed_roles = {"signal", "reference_plane", "mixed_signal_pour",
                     "power_plane"}
    findings = []
    for layer, role in roles.items():
        if layer not in enabled:
            findings.append(f"layer_roles names disabled/unknown layer {layer}")
        if role not in allowed_roles:
            findings.append(f"layer_roles.{layer} has unknown role {role!r}")
    for class_name, layers in eligibility.items():
        if not isinstance(layers, list) or not layers:
            findings.append(f"class_layers.{class_name} must be a non-empty list")
            continue
        unknown = sorted(set(map(str, layers)) - enabled)
        if unknown:
            findings.append(f"class_layers.{class_name} names {unknown}")
        forbidden = [layer for layer in layers
                     if roles.get(str(layer)) in {"reference_plane", "power_plane"}]
        if forbidden:
            findings.append(f"class_layers.{class_name} uses plane-only {forbidden}")
    return {"status": "FAIL" if findings else "PASS",
            "detail": f"{len(roles)} layer role(s), {len(eligibility)} class map(s)",
            "roles": roles, "class_layers": eligibility,
            "findings": findings}


def _pads_by_ref(board: Any) -> dict[str, dict[str, Any]]:
    return {
        str(fp.GetReference()): {str(pad.GetNumber()): pad for pad in fp.Pads()}
        for fp in board.GetFootprints()
    }


def _connector_lanes(route_cfg: dict[str, Any], board: Any) -> dict[str, Any]:
    cfg = ((route_cfg.get("route") or {}).get("routability") or {})
    rows = cfg.get("connector_lanes") or []
    required = bool(cfg.get("require_connector_lanes"))
    if not isinstance(rows, list):
        raise ValueError("route.routability.connector_lanes must be a list")
    if not rows:
        return {
            "status": "FAIL" if required else "N-A",
            "detail": ("connector lane declarations are required but absent"
                       if required else "no connector lane rows declared"),
            "rows": [],
            "findings": (["require_connector_lanes is true but rows are empty"]
                         if required else []),
        }
    footprints = _pads_by_ref(board)
    findings, graded, seen = [], [], set()
    for index, raw in enumerate(rows):
        where = f"route.routability.connector_lanes[{index}]"
        if not isinstance(raw, dict):
            findings.append(f"{where}: expected a mapping")
            continue
        ref = str(raw.get("ref") or "").strip()
        why = str(raw.get("why") or "").strip()
        lanes = raw.get("lanes") or []
        if not ref or ref in seen:
            findings.append(f"{where}.ref must be non-empty and unique")
        seen.add(ref)
        if not why:
            findings.append(f"{where}.why is required")
        if not isinstance(lanes, list) or not lanes:
            findings.append(f"{where}.lanes must be a non-empty ordered list")
            continue
        pads = footprints.get(ref)
        if pads is None:
            findings.append(f"{where}: footprint {ref!r} is absent")
            continue
        observed, lane_seen = [], set()
        for lane_index, lane in enumerate(lanes):
            lane_where = f"{where}.lanes[{lane_index}]"
            if not isinstance(lane, dict) or set(lane) != {"pad", "net"}:
                findings.append(f"{lane_where}: requires exactly pad and net")
                continue
            pad_number, expected = str(lane["pad"]), str(lane["net"])
            if not pad_number or pad_number in lane_seen or not expected:
                findings.append(f"{lane_where}: pad must be unique and net non-empty")
                continue
            lane_seen.add(pad_number)
            pad = pads.get(pad_number)
            actual = None if pad is None else str(pad.GetNetname())
            observed.append({"pad": pad_number, "expected_net": expected,
                             "actual_net": actual})
            if pad is None:
                findings.append(f"{lane_where}: {ref}.{pad_number} is absent")
            elif actual != expected:
                findings.append(
                    f"{lane_where}: {ref}.{pad_number} is {actual!r}, "
                    f"expected {expected!r}")
        graded.append({"ref": ref, "lanes": observed, "why": why})
    return {"status": "FAIL" if findings else "PASS",
            "detail": f"{len(graded)}/{len(rows)} connector row(s) graded",
            "rows": graded, "findings": findings}


def _series_power_paths(route_cfg: dict[str, Any], board: Any) -> dict[str, Any]:
    cfg = ((route_cfg.get("route") or {}).get("routability") or {})
    rows = cfg.get("series_power_paths") or []
    required = bool(cfg.get("require_series_power_paths"))
    if not isinstance(rows, list):
        raise ValueError("route.routability.series_power_paths must be a list")
    if not rows:
        return {
            "status": "FAIL" if required else "N-A",
            "detail": ("series power paths are required but absent" if required
                       else "no series power paths declared"),
            "rows": [],
            "findings": (["require_series_power_paths is true but rows are empty"]
                         if required else []),
        }
    footprints = _pads_by_ref(board)
    findings, graded, seen_ids = [], [], set()

    def resolve(endpoint: str, where: str) -> tuple[str, str, str] | None:
        if "." not in endpoint:
            findings.append(f"{where}: endpoint must be REF.PAD")
            return None
        ref, pad_number = endpoint.split(".", 1)
        pad = footprints.get(ref, {}).get(pad_number)
        if pad is None:
            findings.append(f"{where}: endpoint {endpoint!r} is absent")
            return None
        return ref, pad_number, str(pad.GetNetname())

    for index, raw in enumerate(rows):
        where = f"route.routability.series_power_paths[{index}]"
        if not isinstance(raw, dict):
            findings.append(f"{where}: expected a mapping")
            continue
        path_id = str(raw.get("id") or "").strip()
        why = str(raw.get("why") or "").strip()
        transitions = raw.get("transitions") or []
        if not path_id or path_id in seen_ids:
            findings.append(f"{where}.id must be non-empty and unique")
        seen_ids.add(path_id)
        if not why:
            findings.append(f"{where}.why is required")
        if not isinstance(transitions, list) or not transitions:
            findings.append(f"{where}.transitions must be a non-empty list")
            continue
        observed = []
        for transition_index, transition in enumerate(transitions):
            tw = f"{where}.transitions[{transition_index}]"
            if (not isinstance(transition, dict) or
                    set(transition) != {"kind", "from", "to"}):
                findings.append(f"{tw}: requires exactly kind, from, and to")
                continue
            kind = str(transition["kind"])
            left = resolve(str(transition["from"]), f"{tw}.from")
            right = resolve(str(transition["to"]), f"{tw}.to")
            if kind not in {"copper", "component"}:
                findings.append(f"{tw}.kind must be copper or component")
            if left is None or right is None:
                continue
            if kind == "copper" and (not left[2] or left[2] != right[2]):
                findings.append(
                    f"{tw}: copper endpoints have different nets "
                    f"{left[2]!r}/{right[2]!r}")
            if kind == "component" and (left[0] != right[0] or
                                         left[1] == right[1] or
                                         left[2] == right[2]):
                findings.append(
                    f"{tw}: component transition must cross two pads/nets "
                    "of one footprint")
            observed.append({"kind": kind, "from": transition["from"],
                             "to": transition["to"],
                             "from_net": left[2], "to_net": right[2]})
        graded.append({"id": path_id, "transitions": observed, "why": why})
    return {"status": "FAIL" if findings else "PASS",
            "detail": f"{len(graded)}/{len(rows)} power path(s) graded",
            "rows": graded, "findings": findings}


def grade(project: Path, board_path: Path, *, board_name: str | None = None,
          placement_config: Path | None = None,
          coupled_witness: Path | None = None,
          coupled_workspace: Path | None = None,
          functional_cells_config: Path | None = None,
          functional_cell_observations: Path | None = None,
          stack_authority: Path | None = None,
          route_plan_authority: Path | None = None,
          topology_migration: Path | None = None) -> dict[str, Any]:
    project, board_path = project.resolve(), board_path.resolve()
    route_path, route_note = board_scoped(project, "route.yaml", board_name)
    nets_path, nets_note = board_scoped(project, "rules/nets.yaml", board_name)
    if route_path is None or not route_path.is_file():
        raise ValueError(f"route contract unresolved: {route_note}")
    if nets_path is None or not nets_path.is_file():
        raise ValueError(f"net rules unresolved: {nets_note}")
    route_cfg = yaml.safe_load(route_path.read_text(encoding="utf-8-sig")) or {}
    placement_cfg = {}
    if placement_config is not None and placement_config.is_file():
        placement_cfg = json.loads(
            placement_config.read_text(encoding="utf-8-sig"))
    checks: dict[str, dict[str, Any]] = {}
    try:
        physical = placement_gates.inspect(board_path, placement_cfg)
        checks["physical_placement"] = {
            "status": physical["verdict"],
            "detail": f"{len(physical['failures'])} failure(s), "
                      f"{len(physical['warnings'])} warning(s)",
            "report": physical,
        }
    except Exception as exc:
        checks["physical_placement"] = {"status": "INCOMPLETE",
                                         "detail": str(exc)}
    try:
        notes = critical_route_check.check(
            project, board_path, False, route_path=route_path,
            nets_path=nets_path)
        count = sum(not note.startswith("no critical routes:") for note in notes)
        checks["critical_route_contract"] = {
            "status": "PASS", "detail": f"{count} critical pair(s) contracted",
            "notes": notes}
    except Exception as exc:
        checks["critical_route_contract"] = {"status": "FAIL", "detail": str(exc)}
    try:
        board_nets, pad_counts = route_ownership_preflight._load_board_facts(
            board_path)
        nets_cfg = yaml.safe_load(nets_path.read_text(encoding="utf-8-sig")) or {}
        ownership = route_ownership_preflight.audit_config(
            route_cfg, pad_counts=pad_counts, board_nets=board_nets,
            nets_cfg=nets_cfg)
        checks["route_ownership"] = {
            "status": ownership["verdict"],
            "detail": f"{len(ownership['findings'])} finding(s)",
            "report": ownership}
    except Exception as exc:
        checks["route_ownership"] = {"status": "INCOMPLETE", "detail": str(exc)}
    board = pcbnew.LoadBoard(str(board_path))
    try:
        checks["endpoint_topology"] = _topology(route_cfg, board, project)
    except Exception as exc:
        checks["endpoint_topology"] = {"status": "INCOMPLETE", "detail": str(exc)}
    try:
        checks["pair_footprint"] = _pair_footprints(project, board, route_cfg,
                                                     nets_cfg)
    except Exception as exc:
        checks["pair_footprint"] = {"status": "INCOMPLETE", "detail": str(exc)}
    try:
        checks["layer_eligibility"] = _layers(route_cfg, board)
    except Exception as exc:
        checks["layer_eligibility"] = {"status": "INCOMPLETE", "detail": str(exc)}
    try:
        checks["connector_lane_order"] = _connector_lanes(route_cfg, board)
    except Exception as exc:
        checks["connector_lane_order"] = {"status": "INCOMPLETE", "detail": str(exc)}
    try:
        checks["series_power_paths"] = _series_power_paths(route_cfg, board)
    except Exception as exc:
        checks["series_power_paths"] = {"status": "INCOMPLETE", "detail": str(exc)}
    coupled_rows = (((route_cfg.get("route") or {}).get("routability") or {})
                    .get("coupled_neighborhoods") or [])
    if coupled_rows:
        declared = (((route_cfg.get("route") or {}).get("routability") or {})
                    .get("coupled_witness"))
        witness = coupled_witness
        if witness is None and declared:
            relative = Path(str(declared))
            if relative.is_absolute() or ".." in relative.parts:
                checks["coupled_geometry"] = {
                    "status": "INCOMPLETE",
                    "detail": "route.routability.coupled_witness must be project-relative",
                }
                witness = None
            else:
                witness = project / relative
        if witness is None or coupled_workspace is None:
            missing = []
            if witness is None:
                missing.append("combined witness")
            if coupled_workspace is None:
                missing.append("fresh evidence workspace")
            checks.setdefault("coupled_geometry", {
                "status": "INCOMPLETE",
                "detail": f"declared coupled neighborhoods lack {', '.join(missing)}",
            })
        elif "coupled_geometry" not in checks:
            try:
                report = coupled_geometry_preflight.grade(
                    project, board_path, Path(witness), coupled_workspace,
                    board_name=board_name)
                checks["coupled_geometry"] = {
                    "status": report["status"],
                    "detail": (f"{len(report['neighborhoods'])} combined "
                               f"neighborhood(s), {len(report['required_nets'])} net(s)"),
                    "report": report,
                }
            except Exception as exc:
                checks["coupled_geometry"] = {
                    "status": "INCOMPLETE", "detail": str(exc)}
    else:
        checks["coupled_geometry"] = {
            "status": "N-A", "detail": "no coupled neighborhoods declared"}
    statuses = {row["status"] for row in checks.values()}
    verdict = ("INCOMPLETE" if "INCOMPLETE" in statuses else
               "REJECTED" if "FAIL" in statuses else "ACCEPTED")
    inputs = {"board": _record(board_path), "route": _record(route_path),
              "nets": _record(nets_path),
              "checker_placement": _record(Path(__file__).resolve())}
    if placement_config is not None and placement_config.is_file():
        inputs["placement_config"] = _record(placement_config.resolve())
    for row in checks.get("endpoint_topology", {}).get("rows", []):
        if row.get("part_yaml"):
            key = "part_" + row["part_mpn"].lower().replace("/", "_")
            inputs.setdefault(key, _record(Path(row["part_yaml"])))
    if checks.get("pair_footprint", {}).get("status") != "N-A":
        for path in sorted((project / "02_parts").glob("*/part.yaml")):
            # Alias authority can change the source-to-native terminal mapping.
            inputs.setdefault("pair_part_" + path.parent.name, _record(path))
    coupled_report = checks.get("coupled_geometry", {}).get("report") or {}
    for name, record in (coupled_report.get("inputs") or {}).items():
        inputs.setdefault(f"coupled_{name}", dict(record))
    child = coupled_report.get("child_receipt")
    if isinstance(child, Mapping):
        inputs["coupled_child_receipt"] = dict(child)
    return {
        "schema": 2, "kind": "placement-routability-receipt-v2",
        "verdict": verdict, "subject": inputs["board"], "inputs": inputs,
        "checks": checks,
        "coverage": {"passing": sum(row["status"] in {"PASS", "N-A"}
                                     for row in checks.values()),
                     "total": len(checks)},
    }


def _placement_shadow_request(
        project: Path, subject: Mapping[str, Any], *,
        board_name: str | None = None,
        functional_cells_config: Path | None = None,
        functional_cell_observations: Path | None = None,
        stack_authority: Path | None = None,
        route_plan_authority: Path | None = None,
        topology_migration: Path | None = None) -> dict[str, Any]:
    """Describe deferred placement shadows without executing them."""
    project = Path(project)

    def configured(explicit: Path | None, relative: str) -> Path | None:
        del relative
        return Path(explicit) if explicit is not None else None

    cells = configured(functional_cells_config, "rules/placement_cells.yaml")
    observations = (Path(functional_cell_observations)
                    if functional_cell_observations is not None else None)
    stack = configured(stack_authority, "rules/stackup.yaml")
    plan = configured(route_plan_authority, "rules/route_plan.yaml")
    migration = configured(
        topology_migration, "rules/topology_migration.yaml")
    functional_requested = cells is not None or observations is not None
    source_requested = any(path is not None for path in (stack, plan, migration))

    def pending(requested: bool, detail: str) -> dict[str, Any]:
        return {
            "status": "INCOMPLETE" if requested else "N-A",
            "detail": detail if requested else "no shadow contract selected",
            "authority": "SHADOW",
        }

    return {
        "schema": 1, "kind": "placement-routability-shadow-v1",
        "authority": "SHADOW", "subject": dict(subject),
        "checks": {
            "functional_cells": pending(
                functional_requested,
                "requested; run in a separate bounded placement-shadow task"),
            "source_prep_authority": pending(
                source_requested,
                "requested; run in a separate bounded source-authority task"),
        },
        "requested_paths": {
            name: str(path) if path is not None else None
            for name, path in (
                ("functional_cells", cells),
                ("functional_cell_observations", observations),
                ("stack_authority", stack), ("route_plan_authority", plan),
                ("topology_migration", migration),
            )
        },
    }


def verify(receipt_path: Path) -> tuple[bool, list[str]]:
    failures = []
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return False, [f"receipt cannot be read: {exc}"]
    if not isinstance(receipt, Mapping):
        return False, ["placement-routability receipt must be a mapping"]
    if (receipt.get("schema") != 2 or
            receipt.get("kind") != "placement-routability-receipt-v2"):
        failures.append("unsupported receipt schema/kind")
    inputs = receipt.get("inputs")
    if not isinstance(inputs, Mapping):
        failures.append("receipt inputs must be a mapping")
        inputs = {}
    required_inputs = {"board", "route", "nets", "checker_placement"}
    if not required_inputs <= set(inputs):
        failures.append(
            f"receipt inputs omit required authority: "
            f"{sorted(required_inputs - set(inputs))}")
    for name, record in sorted(inputs.items()):
        if (not isinstance(record, Mapping) or
                set(record) != {"path", "sha256", "size"}):
            failures.append(f"input record is malformed: {name}")
            continue
        if name in SHADOW_INPUTS:
            continue
        path = Path(str(record.get("path") or ""))
        if not path.is_file() or _record(path) != record:
            failures.append(f"input moved or changed: {name}")
    if receipt.get("subject") != inputs.get("board"):
        failures.append("receipt subject must equal the exact board input record")

    checks = receipt.get("checks")
    if not isinstance(checks, Mapping):
        failures.append("receipt checks must be a mapping")
        checks = {}
    if set(checks) != AUTHORITATIVE_CHECKS:
        failures.append(
            "authoritative check inventory differs "
            f"(missing={sorted(AUTHORITATIVE_CHECKS - set(checks))}, "
            f"unknown={sorted(set(checks) - AUTHORITATIVE_CHECKS)})")
    statuses: list[str] = []
    for name, row in sorted(checks.items()):
        if not isinstance(row, Mapping) or row.get("status") not in CHECK_STATUSES:
            failures.append(f"authoritative check status is malformed: {name}")
            continue
        statuses.append(str(row["status"]))
    coupled_child = inputs.get("coupled_child_receipt")
    coupled = checks.get("coupled_geometry")
    if isinstance(coupled, Mapping) and isinstance(coupled.get("report"), Mapping):
        required_coupled = {
            "coupled_checker", "coupled_candidate_checker",
            "coupled_route_base_checker", "coupled_authority_parser",
            "coupled_kicad_cli", "coupled_kicad_python",
            "coupled_pcbnew_module", "coupled_pcbnew_native",
            "coupled_rules_generator", "coupled_current_rules_board",
            "coupled_current_rules_project", "coupled_current_rules_rules",
            "coupled_child_receipt",
        }
        missing_coupled = sorted(required_coupled - set(inputs))
        if missing_coupled:
            failures.append(
                f"coupled receipt inputs omit producer authority: {missing_coupled}")
    if isinstance(coupled, Mapping) and isinstance(coupled.get("report"), Mapping):
        valid_report, report_failures = coupled_geometry_preflight.verify_mapping(
            coupled["report"])
        failures.extend(f"coupled report: {row}" for row in report_failures)
        if not valid_report and not report_failures:
            failures.append("coupled report verification failed")
        if coupled.get("status") != coupled["report"].get("status"):
            failures.append("coupled check status differs from verified report")
    if isinstance(coupled, Mapping) and coupled.get("status") == "PASS":
        if not isinstance(coupled_child, Mapping):
            failures.append("passing coupled geometry has no bound child receipt")
        else:
            valid, child_failures = route_candidate_workspace.verify_receipt(
                Path(str(coupled_child.get("path") or "")))
            failures.extend(f"coupled child: {row}" for row in child_failures)
            if not valid and not child_failures:
                failures.append("coupled child receipt verification failed")
    if isinstance(checks.get("pair_footprint"), Mapping) and not failures:
        try:
            route_cfg = yaml.safe_load(Path(inputs["route"]["path"]).read_text(
                encoding="utf-8-sig")) or {}
            nets_cfg = yaml.safe_load(Path(inputs["nets"]["path"]).read_text(
                encoding="utf-8-sig")) or {}
            board = pcbnew.LoadBoard(str(inputs["board"]["path"]))
            source_dirs = [parent for parent in Path(inputs["route"]["path"]).parents
                           if parent.name == "03_src"]
            if len(source_dirs) != 1:
                raise ValueError("route input has no unique 03_src ancestor")
            project = source_dirs[0].parent
            if checks["pair_footprint"].get("status") != "N-A":
                for path in sorted((project / "02_parts").glob("*/part.yaml")):
                    key = "pair_part_" + path.parent.name
                    if inputs.get(key) != _record(path):
                        failures.append(f"pair footprint alias authority omitted: {key}")
            expected_pair = _pair_footprints(project, board, route_cfg, nets_cfg)
            if checks["pair_footprint"] != expected_pair:
                failures.append("pair footprint report differs from regraded source/native geometry")
        except Exception as exc:
            failures.append(f"pair footprint regrade incomplete: {exc}")
    if statuses and len(statuses) == len(AUTHORITATIVE_CHECKS):
        expected_verdict = (
            "INCOMPLETE" if "INCOMPLETE" in statuses else
            "REJECTED" if "FAIL" in statuses else "ACCEPTED")
        if receipt.get("verdict") != expected_verdict:
            failures.append(
                "receipt verdict disagrees with authoritative check statuses")
        expected_coverage = {
            "passing": sum(status in {"PASS", "N-A"}
                           for status in statuses),
            "total": len(AUTHORITATIVE_CHECKS),
        }
        if receipt.get("coverage") != expected_coverage:
            failures.append(
                "receipt coverage disagrees with closed authoritative inventory")
    elif receipt.get("verdict") == "ACCEPTED":
        failures.append("accepted receipt has zero or incomplete check coverage")
    return not failures, failures


def _publish_feasibility(receipt: dict[str, Any], receipt_path: Path,
                         bundle_path: Path, stage_path: Path) -> None:
    """Write one bounded shadow request; never accept a P-FEAS bundle."""
    del receipt_path, bundle_path
    semantic = {
        "legacy_verdict": receipt.get("verdict"),
        "subject": receipt.get("subject"),
        "required_checks": sorted(AUTHORITATIVE_CHECKS),
    }
    authoritative_bytes = json.dumps(
        semantic, sort_keys=True, separators=(",", ":")).encode("utf-8")
    identity = subject_identity("placement-feasibility", 1, [TypedIdentityInput(
        "placement", "mapping", semantic, authoritative_bytes)])
    now = utc_now()
    result = StageResult(
        stage_id="P-FEASIBILITY", run_id=new_run_id(), subject=identity,
        applicability="APPLIES", applicability_reason=None,
        status="INCOMPLETE", started_at=now, finished_at=now, elapsed_s=0.0,
        graded=0, total=len(AUTHORITATIVE_CHECKS), outputs=[],
        findings=[{
            "code": "P-FEAS-PROMOTION-DISABLED",
            "detail": ("receipt reopening is structural only; independent "
                       "authoritative-predicate regrade is not implemented"),
        }], resume=None,
    )
    write_json_atomic(stage_path, result.to_mapping())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    grade_parser = sub.add_parser("grade")
    grade_parser.add_argument("project", type=Path)
    grade_parser.add_argument("--board", type=Path, required=True)
    grade_parser.add_argument("--board-name")
    grade_parser.add_argument("--placement-config", type=Path)
    grade_parser.add_argument("--coupled-witness", type=Path)
    grade_parser.add_argument("--coupled-workspace", type=Path)
    grade_parser.add_argument("--functional-cells", type=Path)
    grade_parser.add_argument("--functional-cell-observations", type=Path)
    grade_parser.add_argument("--stack-authority", type=Path)
    grade_parser.add_argument("--route-plan-authority", type=Path)
    grade_parser.add_argument("--topology-migration", type=Path)
    grade_parser.add_argument("--json", type=Path, required=True)
    grade_parser.add_argument("--stage-bundle", type=Path)
    grade_parser.add_argument("--stage-result", type=Path)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("receipt", type=Path)
    pair_parser = sub.add_parser("pair-footprint")
    pair_parser.add_argument("project", type=Path)
    pair_parser.add_argument("--board", type=Path, required=True)
    pair_parser.add_argument("--board-name")
    args = parser.parse_args(argv)
    if args.command == "verify":
        valid, failures = verify(args.receipt)
        for failure in failures:
            print(f"  FAIL {failure}")
        print(f"PLACEMENT-ROUTABILITY RECEIPT {'PASS' if valid else 'FAIL'}")
        return 0 if valid else 1
    if args.command == "pair-footprint":
        try:
            route_path, route_note = board_scoped(args.project, "route.yaml",
                                                   args.board_name)
            nets_path, nets_note = board_scoped(args.project, "rules/nets.yaml",
                                                 args.board_name)
            if route_path is None or nets_path is None:
                raise ValueError(f"source unresolved: {route_note}; {nets_note}")
            route_cfg = yaml.safe_load(route_path.read_text(encoding="utf-8-sig")) or {}
            nets_cfg = yaml.safe_load(nets_path.read_text(encoding="utf-8-sig")) or {}
            result = _pair_footprints(args.project, pcbnew.LoadBoard(str(args.board)),
                                      route_cfg, nets_cfg)
        except Exception as exc:
            result = {"status": "INCOMPLETE", "detail": str(exc),
                      "pairs": [], "findings": [], "unresolved": [str(exc)]}
        print(json.dumps(result, indent=2, sort_keys=True))
        return {"PASS": 0, "N-A": 0, "FAIL": 1, "INCOMPLETE": 2}[result["status"]]
    if bool(args.stage_bundle) != bool(args.stage_result):
        print("PLACEMENT-ROUTABILITY INCOMPLETE: --stage-bundle and "
              "--stage-result must be supplied together")
        return 2
    shadow_path = args.json.with_name(f"{args.json.stem}.shadow.json")
    if args.coupled_workspace is None:
        args.coupled_workspace = (args.json.with_name(
            f"{args.json.stem}.coupled-workspace") /
            f"attempt-{uuid.uuid4().hex}")
    output_paths = {"receipt": args.json, "shadow": shadow_path,
                    "coupled_workspace": args.coupled_workspace}
    if args.stage_bundle:
        output_paths.update({"stage_bundle": args.stage_bundle,
                             "stage_result": args.stage_result})
    try:
        require_safe_output_layout(
            output_paths,
            directory_outputs=(
                ("stage_bundle", "coupled_workspace")
                if args.stage_bundle else ("coupled_workspace",)),
            protected_paths={"project": args.project, "board": args.board},
        )
    except ValueError as exc:
        print(f"PLACEMENT-ROUTABILITY INCOMPLETE: {exc}")
        return 2
    try:
        receipt = grade(args.project, args.board, board_name=args.board_name,
                        placement_config=args.placement_config,
                        coupled_witness=args.coupled_witness,
                        coupled_workspace=args.coupled_workspace,
                        functional_cells_config=args.functional_cells,
                        functional_cell_observations=(
                            args.functional_cell_observations),
                        stack_authority=args.stack_authority,
                        route_plan_authority=args.route_plan_authority,
                        topology_migration=args.topology_migration)
    except Exception as exc:
        print(f"PLACEMENT-ROUTABILITY INCOMPLETE: {exc}")
        return 2
    try:
        post_output_paths = {
            name: path for name, path in output_paths.items()
            if name != "coupled_workspace"
        }
        require_safe_output_layout(
            post_output_paths,
            directory_outputs=("stage_bundle",) if args.stage_bundle else (),
            protected_paths={
                "project": args.project,
                **{f"input_{name}": Path(record["path"])
                   for name, record in (receipt.get("inputs") or {}).items()},
            },
        )
    except ValueError as exc:
        print(f"PLACEMENT-ROUTABILITY INCOMPLETE: {exc}")
        return 2
    _atomic_json(args.json, receipt)
    try:
        _atomic_json(shadow_path, _placement_shadow_request(
            args.project, receipt["subject"], board_name=args.board_name,
            functional_cells_config=args.functional_cells,
            functional_cell_observations=args.functional_cell_observations,
            stack_authority=args.stack_authority,
            route_plan_authority=args.route_plan_authority,
            topology_migration=args.topology_migration))
    except Exception as exc:
        print(f"PLACEMENT-ROUTABILITY SHADOW INCOMPLETE: {exc}")
    if args.stage_bundle:
        try:
            _publish_feasibility(receipt, args.json.resolve(),
                                 args.stage_bundle.resolve(),
                                 args.stage_result.resolve())
        except Exception as exc:
            print(f"PLACEMENT-ROUTABILITY INCOMPLETE: shadow stage evidence: {exc}")
            # Optional shadow publication cannot alter the legacy compositor
            # result or turn a prior accepted bundle into current authority.
    coverage = receipt["coverage"]
    print(f"PLACEMENT-ROUTABILITY {receipt['verdict']}: "
          f"{coverage['passing']}/{coverage['total']} checks passing or N-A; "
          f"receipt={args.json.resolve()}")
    return {"ACCEPTED": 0, "REJECTED": 1, "INCOMPLETE": 2}[receipt["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
