#!/usr/bin/env python3
"""Focused regressions for the crow carrier's staged first-power policy."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

from harness import ROOT, check, eq, main, test


FAB_SCRIPTS = ROOT / "skills/jlcpcb-fab/scripts"
sys.path.insert(0, str(FAB_SCRIPTS))

from first_article_check import check as check_first_article  # noqa: E402


PROJECT = ROOT / "projects/crow-audio-carrier-v1"
CARD_PATH = PROJECT / "03_src/rules/first_article.yaml"
POWER_TREE_PATH = PROJECT / "03_src/rules/power_tree.yaml"


def policy():
    return yaml.safe_load(CARD_PATH.read_text(encoding="utf-8-sig"))


def nominal_record(card):
    stage = card["stages"][0]
    measurements = {}
    for rail in card["rails"]:
        resistance = rail["resistance"]
        voltage = rail["voltage"]
        current = rail["no_load_current"]
        supply = rail["supply"]
        measurements[rail["name"]] = {
            "resistance": {
                "value": (resistance["min_ohm"] + resistance["max_ohm"]) / 2,
                "unit": "ohm",
                "probe": resistance["probe"],
            },
            "voltage": {
                "value": (voltage["min_v"] + voltage["max_v"]) / 2,
                "unit": "V",
                "probe": voltage["probe"],
            },
            "no_load_current": {
                "value": 0.080,
                "unit": "A",
                "probe": current["probe"],
            },
            "supply_voltage": {
                "value": supply["min_v"],
                "unit": "V",
                "probe": supply["probe"],
            },
            "current_limit": {
                "value": supply["max_current_limit_a"],
                "unit": "A",
            },
        }
    return {
        "stage": stage["name"],
        "installed": stage["installed"],
        "assembly_confirmations": {
            f"{ref}.exposed_pad": True for ref in stage["exposed_pads"]
        },
        "measurements": measurements,
    }


@test("crow carrier first-power limits agree with the governed delivery floor")
def t_current_policy_is_coherent():
    card = policy()
    tree = yaml.safe_load(POWER_TREE_PATH.read_text(encoding="utf-8-sig"))
    rails = {row["name"]: row for row in card["rails"]}
    eq(
        rails["12V_PROTECTED"]["voltage"]["min_v"],
        tree["upstream_delivery"]["destination_floor_V"],
        "protected-rail first-power floor",
    )
    probes = {row["no_load_current"]["probe"] for row in rails.values()}
    ceilings = {row["no_load_current"]["max_a"] for row in rails.values()}
    eq(probes, {"bench_supply"}, "global no-load current probe")
    eq(ceilings, {0.120}, "global steady-state input-current ceiling")
    eq(check_first_article(card, nominal_record(card))["verdict"], "AUTHORIZED",
       "complete in-range synthetic record")


@test("crow carrier current and protected-voltage abort bounds fail closed",
      kind="known_bad")
def t_abnormal_power_record_holds():
    card = policy()
    record = copy.deepcopy(nominal_record(card))
    record["measurements"]["12V_PROTECTED"]["voltage"]["value"] = 11.15
    record["measurements"]["5V_BUCK"]["no_load_current"]["value"] = 0.121
    result = check_first_article(card, record)
    eq(result["verdict"], "HOLD", "out-of-range first-power record")
    subjects = {row["subject"] for row in result["findings"]}
    check("12V_PROTECTED.voltage" in subjects,
          "protected-rail floor did not hold")
    check("5V_BUCK.no_load_current" in subjects,
          "steady-state input-current ceiling did not hold")


if __name__ == "__main__":
    sys.exit(main())
