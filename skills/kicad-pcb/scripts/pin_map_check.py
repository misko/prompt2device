#!/usr/bin/env python3
"""P-PINMAP: reconcile physical, schematic, and footprint pin identities.

The independent pin review remains the authority for what the datasheet says.
This early gate enforces that its ``02_parts/*/part.yaml`` pin set reaches
both producer artifacts. Any intentional collapse, such as a manufacturer-
fused drain land, must be declared under ``pin_aliases`` with evidence.

Example, keyed by the logical pin from ``pins``::

    pin_aliases:
      6:
        schematic: "6"
        footprint: "5"
        fused: true
        why: "manufacturer recommended land fuses drains 5-8"
        evidence: "datasheet rev 2.6 pp.11-13"

The default mapping is identity. Aliasing is never inferred from equal nets.

VACUITY: the machine can prove that a declared pin reached both artifacts, but
it cannot independently derive the physical pin set from an arbitrary PDF. A
consistently incomplete ``pins`` map can therefore pass. The fresh-context
datasheet review closes that channel before routing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pcbnew

try:
    import yaml
except ImportError:
    sys.exit("P-PINMAP: PyYAML is required")


from part_identity import alias_map, load_parts, part_ids, pin_name, sval


def load_circuit(path: Path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    comps = {x["source_component_id"]: x for x in data
             if x.get("type") == "source_component" and x.get("name")}
    ports = {cid: set() for cid in comps}
    for item in data:
        if item.get("type") != "source_port":
            continue
        cid = item.get("source_component_id")
        if cid not in ports:
            continue
        number = item.get("pin_number")
        if number is None:
            for hint in item.get("port_hints") or []:
                match = re.fullmatch(r"pin(.+)", sval(hint), re.I)
                # tscircuit emits one additional source_port for a repeated
                # physical pad as ``pin5_internal_1`` while retaining the
                # canonical ``pin5`` hint on that same port.  The suffix is a
                # producer identity, not a sixth connector pin; prefer the
                # canonical hint instead of inflating the physical pin set.
                if match and not re.search(r"_internal_\d+$", match.group(1), re.I):
                    number = match.group(1)
                    break
        if number is not None:
            ports[cid].add(sval(number))
    return {comp["name"]: (comp, ports[cid]) for cid, comp in comps.items()}


def supplier_ids(comp: dict) -> list[str]:
    out = []
    for values in (comp.get("supplier_part_numbers") or {}).values():
        if isinstance(values, list):
            out.extend(sval(v) for v in values if v)
        elif values:
            out.append(sval(values))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--board", required=True)
    ap.add_argument("--circuit-json")
    ap.add_argument("--parts")
    args = ap.parse_args(argv)

    project = Path(args.project).resolve()
    board_path = Path(args.board)
    if not board_path.is_absolute():
        board_path = project / board_path
    circuit_path = Path(args.circuit_json) if args.circuit_json else (
        project / "03_tscircuit/build/circuit.json")
    if not circuit_path.is_absolute():
        circuit_path = project / circuit_path
    parts_dir = Path(args.parts) if args.parts else project / "02_parts"
    if not parts_dir.is_absolute():
        parts_dir = project / parts_dir

    print(f"P-PINMAP input project: {project}")
    print(f"P-PINMAP input board: {board_path}")
    print(f"P-PINMAP input circuit: {circuit_path}")
    print(f"P-PINMAP input parts: {parts_dir}")

    missing = [p for p in (board_path, circuit_path, parts_dir) if not p.exists()]
    if missing:
        for path in missing:
            print(f"FAIL P-PINMAP: missing input {path}")
        return 2

    by_id, docs, errors = load_parts(parts_dir)
    try:
        circuit = load_circuit(circuit_path)
    except Exception as exc:
        print(f"FAIL P-PINMAP: cannot read circuit JSON: {exc}")
        return 2
    board = pcbnew.LoadBoard(str(board_path))

    graded = 0
    physical_total = 0
    for fp in sorted(board.GetFootprints(), key=lambda item: item.GetReference()):
        ref = fp.GetReference()
        if ref not in circuit:
            continue
        comp, schematic_pins = circuit[ref]
        candidates = supplier_ids(comp) + [fp.GetValue()]
        mpn = next((by_id[v] for v in candidates if v in by_id), None)
        if not mpn:
            numbered = {sval(p.GetNumber()) for p in fp.Pads() if sval(p.GetNumber())}
            if len(numbered) > 3:
                errors.append(f"{ref}: no part.yaml resolves supplier/value IDs "
                              f"{candidates}")
            continue
        doc, _ = docs[mpn]
        pins, mapping = alias_map(doc, mpn, errors)
        if len(pins) <= 3:
            continue
        graded += 1
        physical_total += len(pins)
        board_pins = {sval(p.GetNumber()) for p in fp.Pads() if sval(p.GetNumber())}
        mapped_schematic = {x["schematic"] for x in mapping.values()}
        mapped_footprint = {x["footprint"] for x in mapping.values()}

        for logical, spec in mapping.items():
            if spec["schematic"] not in schematic_pins:
                errors.append(f"{ref}/{mpn} logical pin {logical}: schematic pin "
                              f"{spec['schematic']} is absent")
            if spec["footprint"] not in board_pins:
                errors.append(f"{ref}/{mpn} logical pin {logical}: footprint pad "
                              f"{spec['footprint']} is absent")
        extra_sch = schematic_pins - mapped_schematic
        extra_fp = board_pins - mapped_footprint
        if extra_sch:
            errors.append(f"{ref}/{mpn}: schematic pins not owned by part.yaml: "
                          f"{sorted(extra_sch)}")
        if extra_fp:
            errors.append(f"{ref}/{mpn}: footprint pads not owned by part.yaml: "
                          f"{sorted(extra_fp)}")

        by_pad = {}
        for logical, spec in mapping.items():
            by_pad.setdefault(spec["footprint"], []).append(logical)
        for pad, logicals in by_pad.items():
            if len(logicals) <= 1:
                continue
            names = {pin_name(pins[x]).upper() for x in logicals}
            aliased = [x for x in logicals if mapping[x]["footprint"] != x]
            if not aliased or not all(mapping[x]["fused"] for x in aliased):
                errors.append(f"{ref}/{mpn}: logical pins {logicals} collapse to "
                              f"pad {pad} without fused:true")
            if len(names) != 1:
                errors.append(f"{ref}/{mpn}: fused logical pins {logicals} have "
                              f"different functions {sorted(names)}")

    print(f"P-PINMAP coverage: {graded} multi-pin ref(s), "
          f"{physical_total} declared physical pin identities graded")
    if graded == 0:
        errors.append("zero multi-pin refs graded")
    if errors:
        for item in errors:
            print(f"FAIL P-PINMAP: {item}")
        print(f"P-PINMAP FAIL: {len(errors)} finding(s)")
        return 1
    print("P-PINMAP PASS: every declared physical pin reaches the schematic "
          "and footprint, with every collapse explicit and evidenced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
