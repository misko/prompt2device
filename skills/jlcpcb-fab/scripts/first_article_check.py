#!/usr/bin/env python3
"""Authorize or hold a staged first-power attempt from measured evidence.

The card is design-time policy; the record is bench evidence. Missing exposed
pad confirmation, population drift, missing units/probe points, or any reading
outside its declared range produces HOLD. Firmware is intentionally outside
this contract unless a project separately requests it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


def _names(value: Any, where: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item
                                               for item in value):
        raise ValueError(f"{where} must be a list of non-empty strings")
    return value


_EXACT_REFDES = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def _refdes(value: Any, where: str) -> list[str]:
    """Return a closed list of literal reference designators.

    Population cards are executable evidence, not prose.  A token such as
    ``R5-R13`` is one literal string to the old checker, so a record repeating
    that token could authorize a board without ever naming R5 through R13.
    Likewise, ``exposed_pads`` means component refdes with hidden solder lands,
    not probe names, nets, pins, or ranges.
    """
    names = _names(value, where)
    if len(names) != len(set(names)):
        raise ValueError(f"{where} must not contain duplicate refdes")
    malformed = [name for name in names if not _EXACT_REFDES.fullmatch(name)]
    if malformed:
        raise ValueError(
            f"{where} must contain literal refdes only; ranges/pins are not "
            f"expanded: {malformed!r}"
        )
    return names


def _measurement(measurements: dict[str, Any], rail: str, kind: str,
                 *, unit: str, probe: str, low: float, high: float,
                 findings: list[dict[str, str]]) -> None:
    row = ((measurements.get(rail) or {}).get(kind) or {})
    subject = f"{rail}.{kind}"
    if not isinstance(row, dict) or "value" not in row:
        findings.append({"code": "FA-MISSING", "subject": subject,
                         "message": "measurement is missing"})
        return
    if str(row.get("unit")) != unit or str(row.get("probe")) != probe:
        findings.append({"code": "FA-METHOD", "subject": subject,
                         "message": f"requires unit {unit} at probe {probe}"})
        return
    try:
        value = float(row["value"])
    except (TypeError, ValueError):
        findings.append({"code": "FA-METHOD", "subject": subject,
                         "message": "value must be numeric"})
        return
    if not low <= value <= high:
        findings.append({"code": "FA-ABORT", "subject": subject,
                         "message": f"{value:g}{unit} outside [{low:g}, {high:g}]"})


def check(card: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    stages = card.get("stages") or []
    if not isinstance(stages, list) or not stages:
        raise ValueError("card.stages must be a non-empty list")
    validated_stages: dict[str, tuple[dict[str, Any], list[str], list[str]]] = {}
    for index, row in enumerate(stages):
        if not isinstance(row, dict) or not isinstance(row.get("name"), str) \
                or not row["name"]:
            raise ValueError(f"card.stages[{index}] must be a named mapping")
        name = row["name"]
        if name in validated_stages:
            raise ValueError(f"card.stages repeats name {name!r}")
        installed = _refdes(row.get("installed"),
                            f"stage {name}.installed")
        exposed = _refdes(row.get("exposed_pads", []),
                          f"stage {name}.exposed_pads")
        not_installed = sorted(set(exposed) - set(installed))
        if not_installed:
            raise ValueError(
                f"stage {name}.exposed_pads names refdes not installed in "
                f"that stage: {not_installed!r}"
            )
        validated_stages[name] = (row, installed, exposed)
    stage_name = str(record.get("stage") or "")
    if stage_name not in validated_stages:
        raise ValueError(f"record.stage {stage_name!r} must select one card stage")
    stage, installed, exposed = validated_stages[stage_name]
    expected = set(installed)
    actual = set(_refdes(record.get("installed"), "record.installed"))
    if actual != expected:
        findings.append({"code": "FA-POP", "subject": stage_name,
                         "message": f"installed mismatch missing={sorted(expected-actual)} "
                                    f"extra={sorted(actual-expected)}"})

    assembly = record.get("assembly_confirmations") or {}
    if not isinstance(assembly, dict):
        raise ValueError("record.assembly_confirmations must be a mapping")
    for ref in exposed:
        if assembly.get(f"{ref}.exposed_pad") is not True:
            findings.append({"code": "FA-EP", "subject": ref,
                             "message": "exposed ground/thermal pad is not confirmed soldered"})

    measurements = record.get("measurements") or {}
    if not isinstance(measurements, dict):
        raise ValueError("record.measurements must be a mapping")
    rails = card.get("rails") or []
    if not isinstance(rails, list) or not rails:
        raise ValueError("card.rails must be a non-empty list")
    for rail in rails:
        if not isinstance(rail, dict) or not rail.get("name"):
            raise ValueError("every card rail must be a named mapping")
        name = str(rail["name"])
        resistance = rail.get("resistance") or {}
        voltage = rail.get("voltage") or {}
        current = rail.get("no_load_current") or {}
        supply = rail.get("supply") or {}
        for block_name, block in (("resistance", resistance), ("voltage", voltage),
                                  ("no_load_current", current), ("supply", supply)):
            if not isinstance(block, dict):
                raise ValueError(f"rail {name}.{block_name} must be a mapping")
        _measurement(measurements, name, "resistance", unit="ohm",
                     probe=str(resistance.get("probe") or ""),
                     low=float(resistance["min_ohm"]), high=float(resistance["max_ohm"]),
                     findings=findings)
        _measurement(measurements, name, "voltage", unit="V",
                     probe=str(voltage.get("probe") or ""),
                     low=float(voltage["min_v"]), high=float(voltage["max_v"]),
                     findings=findings)
        _measurement(measurements, name, "no_load_current", unit="A",
                     probe=str(current.get("probe") or "supply"),
                     low=float(current.get("min_a", 0)), high=float(current["max_a"]),
                     findings=findings)
        _measurement(measurements, name, "supply_voltage", unit="V",
                     probe=str(supply.get("probe") or "supply"),
                     low=float(supply["min_v"]), high=float(supply["max_v"]),
                     findings=findings)
        limit = ((measurements.get(name) or {}).get("current_limit") or {})
        if (not isinstance(limit, dict) or limit.get("unit") != "A" or
                float(limit.get("value", float("inf"))) > float(supply["max_current_limit_a"])):
            findings.append({"code": "FA-LIMIT", "subject": name,
                             "message": "bench current limit missing, unqualified, or too high"})

    return {"schema": 1, "stage": stage_name,
            "verdict": "HOLD" if findings else "AUTHORIZED",
            "findings": findings,
            "scope": "staged first power only; not production or firmware approval"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--card", type=Path)
    parser.add_argument("--record", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    project = args.project.resolve()
    card_path = args.card or project / "03_src/rules/first_article.yaml"
    record_path = args.record or project / "01_docs/journal/first_article.json"
    try:
        card = yaml.safe_load(card_path.read_text(encoding="utf-8-sig")) or {}
        record = json.loads(record_path.read_text(encoding="utf-8-sig"))
        result = check(card, record)
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    except Exception as exc:
        print(f"FIRST-ARTICLE INCOMPLETE: {exc}")
        return 2
    for finding in result["findings"]:
        print(f"  {finding['code']} {finding['subject']}: {finding['message']}")
    print(f"FIRST-ARTICLE {result['verdict']}: {len(result['findings'])} finding(s)")
    print(f"coverage: {len(card.get('rails') or [])} rail(s), "
          f"{len((card.get('stages') or []))} population stage(s) declared")
    return 0 if result["verdict"] == "AUTHORIZED" else 1


if __name__ == "__main__":
    sys.exit(main())
