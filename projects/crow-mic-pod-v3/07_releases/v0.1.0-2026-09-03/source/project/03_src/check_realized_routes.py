#!/usr/bin/env python3
"""Grade the crow pod's safety- and stability-critical realized copper.

Placement distance is not route distance. This checker reopens the exact saved
KiCad board, builds a layer-aware copper graph, and proves that the regulator
capacitors and exposed-line clamps are reached by short, via-free F.Cu paths.
It also proves downstream branches include the complete connector-to-clamp
prefix and that every physical prefix edge dominates each downstream target,
so a longer parallel pre-clamp bypass cannot be hidden by shortest-path choice.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


class AuditError(RuntimeError):
    pass


@dataclass(frozen=True)
class PathResult:
    start: str
    end: str
    net: str
    length_mm: float
    physical_edges: frozenset[int]
    via_count: int
    layers: frozenset[str]


SHORT_PATHS = (
    ("D1.1", "D2.1", 12.0, "reverse diode to input TVS"),
    # Placement remains inside the 4.0 mm pad-centre rule.  The 4.2 mm copper
    # limit admits only the small package-entry detour needed to clear U3's NC
    # land while still rejecting the former 13 mm/two-via exposed trace.
    ("J1.3", "U3.3", 4.2, "AUDIO+ connector to ESD clamp"),
    ("J1.4", "U3.5", 4.2, "AUDIO- connector to ESD clamp"),
    ("U2.8", "C1.1", 3.0, "LDO input bulk capacitor"),
    ("U2.8", "C2.1", 3.0, "LDO input HF capacitor"),
    ("U2.1", "C5.1", 3.0, "LDO output bulk capacitor"),
    ("U2.1", "C6.1", 3.0, "LDO output HF capacitor"),
    ("U2.6", "C4.1", 3.0, "LDO noise-reduction capacitor"),
    ("U2.2", "C3.2", 3.0, "LDO feed-forward FB side"),
    ("U2.1", "C3.1", 3.0, "LDO feed-forward OUT side"),
    ("U1.4", "C10.1", 3.0, "OPA1679 local bypass"),
    ("R12.2", "TP5.1", 5.0, "AUDIO+ probe branch"),
    ("R13.2", "TP6.1", 5.0, "AUDIO- probe branch"),
)

PREFIXES = (
    ("D1.1", "D2.1", ("C1.1", "C2.1", "U2.8", "U2.5", "R14.1"),
     "the TVS must be first after the reverse diode"),
    ("J1.3", "U3.3", ("TP5.1", "R12.2"),
     "AUDIO+ must reach U3 before any probe/output branch"),
    ("J1.4", "U3.5", ("TP6.1", "R13.2"),
     "AUDIO- must reach U3 before any probe/output branch"),
)


def grade(oracle: Callable[[str, str], PathResult]) -> dict:
    rows: list[dict] = []
    findings: list[str] = []
    cache: dict[tuple[str, str], PathResult] = {}

    def path(start: str, end: str) -> PathResult:
        key = (start, end)
        if key not in cache:
            cache[key] = oracle(start, end)
        return cache[key]

    dominance = getattr(oracle, "bypassed_prefix_edges", None)
    if not callable(dominance):
        raise AuditError("route oracle does not provide clamp-dominance proof")

    for start, end, maximum, why in SHORT_PATHS:
        item = path(start, end)
        failures = []
        if item.length_mm > maximum + 1e-9:
            failures.append(f"{item.length_mm:.6f} mm exceeds {maximum:.3f} mm")
        if item.via_count:
            failures.append(f"uses {item.via_count} via(s)")
        if item.layers != frozenset({"F.Cu"}):
            failures.append(f"uses layers {sorted(item.layers)} instead of F.Cu only")
        verdict = "PASS" if not failures else "FAIL"
        rows.append({
            "kind": "short_path", "start": start, "end": end,
            "net": item.net, "length_mm": round(item.length_mm, 6),
            "maximum_mm": maximum, "via_count": item.via_count,
            "layers": sorted(item.layers), "why": why, "verdict": verdict,
        })
        if failures:
            findings.append(f"{start}->{end}: " + "; ".join(failures))

    for start, clamp, targets, why in PREFIXES:
        prefix = path(start, clamp)
        for target in targets:
            downstream = path(start, target)
            missing = sorted(prefix.physical_edges - downstream.physical_edges)
            bypassed = sorted(dominance(
                start, clamp, target, prefix.physical_edges
            ))
            verdict = "PASS" if not missing and not bypassed else "FAIL"
            rows.append({
                "kind": "branch_after_clamp", "start": start,
                "clamp": clamp, "target": target, "net": prefix.net,
                "prefix_edge_count": len(prefix.physical_edges),
                "missing_prefix_edge_count": len(missing),
                "bypassed_prefix_edge_count": len(bypassed),
                "why": why, "verdict": verdict,
            })
            if missing:
                findings.append(
                    f"{start}->{target} branches before {clamp}; "
                    f"{len(missing)} clamp-prefix edge(s) are bypassed"
                )
            if bypassed:
                findings.append(
                    f"{start}->{target} has parallel copper bypassing "
                    f"{clamp}; {len(bypassed)} prefix edge(s) are not cuts"
                )

    return {
        "schema": 1,
        "kind": "crow-pod-realized-route-audit-v1",
        "verdict": "PASS" if not findings else "FAIL",
        "graded": len(rows),
        "rows": rows,
        "findings": findings,
    }


def _load_copper_module(repo: Path):
    path = repo / "skills/kicad-pcb/scripts/copper_length_audit.py"
    spec = importlib.util.spec_from_file_location("crow_copper_length", path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load canonical copper reader: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def board_oracle(board_path: Path) -> Callable[[str, str], PathResult]:
    board_path = board_path.resolve()
    if not board_path.is_file() or board_path.is_symlink():
        raise AuditError(f"board is missing or not a regular file: {board_path}")
    project = Path(__file__).resolve().parents[1]
    repo = Path(os.environ.get("CIRCUITS_ROOT", project.parents[1])).resolve()
    copper = _load_copper_module(repo)
    nets, layers, text = copper.read_copper(board_path)
    pads = copper.read_pad_shapes(text)
    plated = copper.read_plated_pads(text)
    if layers != ["F.Cu", "B.Cu"]:
        raise AuditError(f"expected exact two-layer board, got {layers}")

    pad_to_net: dict[str, str] = {}
    for net, net_pads in pads.items():
        for pad in net_pads:
            ident = f"{pad['ref']}.{pad['pad']}"
            if ident in pad_to_net and pad_to_net[ident] != net:
                raise AuditError(f"ambiguous pad identity {ident}")
            pad_to_net[ident] = net

    graphs: dict[str, tuple[dict, dict]] = {}

    def graph_for(net: str):
        if net not in graphs:
            if net not in nets:
                raise AuditError(f"net {net!r} has no routed copper")
            graph, error = copper._path_graph(
                nets[net], layers, [1.6], pads.get(net, []), plated.get(net, [])
            )
            if error or graph is None:
                raise AuditError(f"cannot build {net} copper graph: {error}")
            graphs[net] = (graph, nets[net])
        return graphs[net]

    def oracle(start: str, end: str) -> PathResult:
        start_net = pad_to_net.get(start)
        end_net = pad_to_net.get(end)
        if not start_net or not end_net:
            raise AuditError(f"missing exact pad endpoint {start} or {end}")
        if start_net != end_net:
            raise AuditError(f"{start} is {start_net}, but {end} is {end_net}")
        graph, entry = graph_for(start_net)
        length, used, error = copper._shortest_declared_path(graph, start, end)
        if error or length is None:
            raise AuditError(error or f"no path from {start} to {end}")
        segment_count = len(entry["segs"])
        via_count = sum(
            1 for edge in used
            if segment_count <= edge < segment_count + len(entry["vias"])
        )
        layers_used = frozenset(
            entry["segs"][edge][0]
            for edge in used if 0 <= edge < segment_count
        )
        return PathResult(
            start=start, end=end, net=start_net, length_mm=float(length),
            physical_edges=frozenset(used), via_count=via_count,
            layers=layers_used,
        )

    def bypassed_prefix_edges(start: str, clamp: str, target: str,
                              prefix_edges: frozenset[int]) -> frozenset[int]:
        """Return prefix edges that are not start-to-target graph cuts."""
        start_net = pad_to_net.get(start)
        clamp_net = pad_to_net.get(clamp)
        target_net = pad_to_net.get(target)
        if not start_net or start_net != clamp_net or start_net != target_net:
            raise AuditError(
                f"dominance endpoints disagree: {start}, {clamp}, {target}"
            )
        graph, _entry = graph_for(start_net)
        starts = graph["anchors"].get(start) or []
        ends = set(graph["anchors"].get(target) or [])
        if not starts or not ends:
            raise AuditError(
                f"dominance endpoint lacks copper: {start} or {target}"
            )

        bypassed: set[int] = set()
        for blocked in prefix_edges:
            seen = set(starts)
            stack = list(starts)
            while stack and not (seen & ends):
                node = stack.pop()
                for nxt, _weight, edge_id in graph["adj"].get(node, []):
                    if edge_id == blocked or nxt in seen:
                        continue
                    seen.add(nxt)
                    stack.append(nxt)
            if seen & ends:
                bypassed.add(blocked)
        return frozenset(bypassed)

    setattr(oracle, "bypassed_prefix_edges", bypassed_prefix_edges)

    return oracle


def audit(board_path: Path) -> dict:
    receipt = grade(board_oracle(board_path))
    receipt["board"] = str(board_path.resolve())
    receipt["board_sha256"] = hashlib.sha256(board_path.read_bytes()).hexdigest()
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    try:
        receipt = audit(args.board)
    except (AuditError, ValueError, OSError) as exc:
        print(f"FAIL R-POD-PATH: {exc}")
        return 1
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    for row in receipt["rows"]:
        if row["kind"] == "short_path":
            print(f"{row['verdict']} {row['start']}->{row['end']} "
                  f"{row['length_mm']:.6f}mm vias={row['via_count']} "
                  f"layers={','.join(row['layers'])}")
        else:
            print(f"{row['verdict']} {row['start']}->{row['clamp']} "
                  f"before {row['target']}")
    print(f"R-POD-PATH {receipt['verdict']}: {receipt['graded']} graded, "
          f"{len(receipt['findings'])} findings")
    return 0 if receipt["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
