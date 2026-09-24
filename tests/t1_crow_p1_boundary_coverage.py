#!/usr/bin/env python3
"""Focused Crow P1 boundary-coverage and source-reservation contract checks."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

from harness import ROOT, check, eq, main, test


PROJECT = ROOT / "projects" / "crow-usb-carrier-v1"
REQUIREMENTS = PROJECT / "03_src/rules/p1_corridor_requirements.yaml"
PLAN = PROJECT / "03_src/modular_plan.json"
SCRIPT = ROOT / "skills/kicad-pcb/scripts/p1_corridor_capacity.py"


def source_requirements():
    return yaml.safe_load(REQUIREMENTS.read_text())


def source_plan():
    import json
    return json.loads(PLAN.read_text())


def capacity_module():
    spec = importlib.util.spec_from_file_location("p1_corridor_capacity_under_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@test("Crow P1 coverage is exact-once across 59 declared interface nets")
def t_crow_p1_exact_coverage():
    value = source_requirements()
    coverage = {}
    for row in value["allocations"]:
        coverage[row["id"]] = set(row["coverage_nets"])
    coverage["power_boundary_windows"] = set(value["power_boundary_windows"]["coverage_nets"])

    module = capacity_module()
    eq(coverage, module.CROW_COVERAGE, "requirements/tool coverage parity")
    union = set().union(*coverage.values())
    eq(len(union), 59, "P1 interface union denominator")
    declared = {row["net"] for row in source_plan()["interfaces"]}
    eq(union, declared, "P1 coverage equals modular interface set")
    membership = {net: sum(net in nets for nets in coverage.values()) for net in union}
    check(all(count == 1 for count in membership.values()), "P1 coverage is not exact-once")


@test("CHASSIS is a power-boundary shell domain and USB shield remains local GND")
def t_chassis_boundary_evidence():
    value = source_requirements()
    usb = next(row for row in value["allocations"] if row["id"] == "usb_device_pair")
    boundary = value["power_boundary_windows"]
    check("CHASSIS" not in usb["coverage_nets"], "CHASSIS remained in USB pair allocation")
    check("CHASSIS" in boundary["coverage_nets"], "CHASSIS missing from boundary coverage")

    evidence = boundary["endpoint_evidence"]
    expected = {f"J{index}.{pad}" for index in range(1, 9) for pad in (9, 10)}
    eq(set(evidence["CHASSIS"]["native_required_pads"]), expected, "RJ45 shell pad denominator")
    chassis = next(row for row in source_plan()["interfaces"] if row["net"] == "CHASSIS")
    plan_pads = {pad for pads in chassis["endpoints"].values() for pad in pads}
    eq(plan_pads, expected, "RJ45 shell evidence matches modular interface")
    eq(evidence["usb_shield"]["net"], "GND", "USB shield net")
    eq(evidence["usb_shield"]["native_required_pads"], ["J_USB.SH"], "USB shield pad name")
    eq(evidence["usb_shield"]["multiplicity"], 4, "USB shield physical-pad count")


@test("Power reservations are concrete source bboxes but retain incomplete status")
def t_power_window_source_reservations():
    boundary = source_requirements()["power_boundary_windows"]
    geometry = boundary["geometry"]
    eq(boundary["status"], "INCOMPLETE", "boundary status")
    eq(geometry["status"], "INCOMPLETE", "geometry status")
    eq(geometry["schema"], "crow-power-boundary-windows-v1", "geometry schema")
    check("not-copper-lane-or-current-thermal-proof" in geometry["semantics"],
          "geometry claim boundary")

    windows = geometry["windows"]
    check(windows, "zero window denominator")
    covered = {row["net"] for row in windows}
    eq(covered, set(boundary["coverage_nets"]) - {"CHASSIS"}, "every electrical boundary net has geometry")
    ids = set()
    for row in windows:
        check(row["id"] not in ids, f"duplicate window {row['id']}")
        ids.add(row["id"])
        bbox = row["bbox"]
        check(len(bbox) == 4 and bbox[0] < bbox[2] and bbox[1] < bbox[3],
              f"non-positive bbox {row['id']}")


if __name__ == "__main__":
    main()
