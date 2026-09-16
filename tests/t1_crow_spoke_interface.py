#!/usr/bin/env python3
"""Cross-board crow spoke pinout and contract regression tests."""

from __future__ import annotations

import sys
import copy
import importlib.util
import hashlib
import json
import subprocess
from unittest import mock
from pathlib import Path
import tempfile

import yaml

from harness import check, eq, main, test


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "projects/crow-roof-array-v1/03_src/check_spoke_interface.py"

spec = importlib.util.spec_from_file_location("crow_spoke_interface", CHECKER)
check(spec is not None and spec.loader is not None, "load checker module")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture() -> Path:
    root = Path(tempfile.mkdtemp(prefix="crow-spoke-interface-"))
    for rel in (
        "projects/crow-roof-array-v1/03_src/rules/spoke_interface.yaml",
        "projects/crow-audio-carrier-v1/03_src/rules/spoke_interface.yaml",
        "projects/crow-mic-pod-v3/03_src/rules/spoke_interface.yaml",
    ):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(module.EXPECTED, sort_keys=False), encoding="utf-8")
    return root


@test("crow spoke checker closes parent/carrier/pod pin and assembly identity")
def t_real_tree():
    result = module.verify(ROOT)
    eq(result["status"], "PASS", "real contract status")
    eq(result["pins"], 8, "closed pin denominator")
    eq(len(result["contracts"]), 3, "closed contract denominator")
    eq(result["realized_connectors"], 9, "closed board connector denominator")
    eq(result["realized_straight_through_pin_paths"], 64,
       "closed cross-board pin denominator")


@test("crow spoke checker rejects the archived power/ground swap", kind="known_bad")
def t_power_ground_swap():
    root = fixture()
    path = root / "projects/crow-audio-carrier-v1/03_src/rules/spoke_interface.yaml"
    value = copy.deepcopy(module.EXPECTED)
    value["pins"][0], value["pins"][1] = value["pins"][1], value["pins"][0]
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    try:
        module.verify_contracts(root)
    except module.ContractError:
        return
    raise AssertionError("power/ground swap was accepted")


@test("crow spoke checker rejects a missing represented child", kind="known_bad")
def t_missing_child():
    root = fixture()
    (root / "projects/crow-mic-pod-v3/03_src/rules/spoke_interface.yaml").unlink()
    try:
        module.verify_contracts(root)
    except module.ContractError:
        return
    raise AssertionError("missing pod contract was accepted")


@test("crow spoke checker rejects formatting-only authority drift", kind="known_bad")
def t_byte_drift():
    root = fixture()
    path = root / "projects/crow-audio-carrier-v1/03_src/rules/spoke_interface.yaml"
    path.write_text("# divergent copy\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        module.verify_contracts(root)
    except module.ContractError:
        return
    raise AssertionError("byte-distinct child contract was accepted")


@test("crow spoke checker rejects duplicate YAML keys", kind="known_bad")
def t_duplicate_key():
    root = fixture()
    path = root / "projects/crow-mic-pod-v3/03_src/rules/spoke_interface.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "schema: 1\n", encoding="utf-8")
    try:
        module.verify_contracts(root)
    except module.ContractError:
        return
    raise AssertionError("duplicate-key contract was accepted")


@test("Cat harness preserves one audio pair and three independently twisted power loops")
def t_cat_pair_map():
    value, _ = module.load_contract(ROOT / "projects/crow-roof-array-v1/03_src/rules/spoke_interface.yaml")
    rows = value["cable"]["conductor_map"]
    eq(len(rows), 8, "all eight conductors represented")
    eq(len({row["color"] for row in rows}), 8, "no duplicated conductor")
    pairs = {pair: {r["cavity"] for r in rows if r["pair"] == pair}
             for pair in {r["pair"] for r in rows}}
    eq(pairs, {"blue": {4, 5}, "orange": {1, 2}, "green": {3, 6}, "brown": {7, 8}},
       "audio and power remain within actual twisted pairs")
    budget = module.cable_power_budget(value)
    check(budget["design_hot_loop_ohm"] < 2.2, "hot loop meets original limit")
    check(budget["design_pod_min_v"] >= 10.5, "pod remains above minimum voltage")
    eq(budget["physical_qualification"], "OWED", "calculation is not bench qualification")


@test("Cat harness rejects consistently miswired audio on all three contracts", kind="known_bad")
def t_cat_split_audio_pair():
    root = fixture()
    for path in root.glob("projects/*/03_src/rules/spoke_interface.yaml"):
        value = yaml.safe_load(path.read_text())
        value["cable"]["conductor_map"][1]["color"] = "green"
        value["cable"]["conductor_map"][1]["pair"] = "green"
        path.write_text(yaml.safe_dump(value, sort_keys=False))
    try:
        module.verify_contracts(root)
    except module.ContractError:
        return
    raise AssertionError("all-three-copy miswire accepted")


@test("Cat harness hot-loop calculation rejects a single power pair", kind="known_bad")
def t_cat_single_power_pair():
    value = copy.deepcopy(module.EXPECTED)
    value["cable"]["conductor_map"] = [r for r in value["cable"]["conductor_map"]
                                         if r["pair"] in {"blue", "orange"}]
    try:
        module.cable_power_budget(value)
    except module.ContractError:
        return
    raise AssertionError("one power pair passed the original resistance limit")


@test("RJ45 harness budget includes both ends of the mated contacts", kind="known_bad")
def t_cat_bad_contact_budget():
    value = copy.deepcopy(module.EXPECTED)
    value["cable"]["power_budget"]["loop_contact_allocation_ohm"] = 1.5
    try:
        module.cable_power_budget(value)
    except module.ContractError:
        return
    raise AssertionError("excessive non-cable resistance was ignored")



@test("RJ45 checker rejects missing and duplicate parallel contacts", kind="known_bad")
def t_rj45_parallel_contact_census():
    for duplicate in (False, True):
        value = copy.deepcopy(module.EXPECTED)
        rows = value["cable"]["conductor_map"]
        row = next(r for r in rows if r["cavity"] == 7)
        if duplicate: row["cavity"] = 3
        else: rows.remove(row)
        try: module.cable_power_budget(value)
        except module.ContractError: continue
        raise AssertionError("incomplete or duplicate power contact accepted")

@test("RJ45 budget rejects invalid scalars and excess pod current", kind="known_bad")
def t_rj45_invalid_budget():
    for group, field, bad in [
        ("construction", "maximum_loop_dcr_ohm_per_km_at_20c", float("nan")),
        ("power_budget", "hot_resistance_multiplier", -1),
        ("power_budget", "loop_contact_allocation_ohm", float("inf")),
        ("electrical", "maximum_continuous_pod_current_a", 0.11)]:
        value = copy.deepcopy(module.EXPECTED)
        owner = value[group] if group == "electrical" else value["cable"][group]
        owner[field] = bad
        try: module.cable_power_budget(value)
        except module.ContractError: continue
        raise AssertionError(f"invalid {group}.{field} accepted")

@test("RJ45 budget independently reproduces the maximum-length hot loop")
def t_rj45_hot_loop():
    budget = module.cable_power_budget(copy.deepcopy(module.EXPECTED))
    eq(budget["design_hot_loop_ohm"], 2.1125, "15 m hot loop")
    eq(budget["design_pod_min_v"], 10.58875, "pod minimum")



def receipt_fixture(contract_bytes=None):
    """Ordinary dummy subject bytes exercise binding, not native geometry.

    These cases distinguish the rejected 2026-09-12 author proposal (which
    accepted stale subjects and duplicate pads) from the preserved checker.
    Root retained RED/GREEN evidence against that unadopted proposal.
    """
    root = fixture()
    spec = module.CHILDREN["pod"]
    project = root / spec["root"]
    if contract_bytes is not None:
        (project / "03_src/rules/spoke_interface.yaml").write_bytes(contract_bytes)
    bindings = {}
    for kind in ("board", "schematic"):
        path = project / spec[kind]
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = ("fixture " + kind + " bytes\n").encode()
        path.write_bytes(payload)
        bindings[kind] = {"path": spec[kind], "size": len(payload),
                          "sha256": hashlib.sha256(payload).hexdigest()}
    checker = project / spec["checker"]
    checker.parent.mkdir(parents=True, exist_ok=True)
    checker.write_text("# immutable mocked child checker\n")
    raw = (project / "03_src/rules/spoke_interface.yaml").read_bytes()
    pads = {1: "12V_POD", 2: "GND", 3: "12V_POD", 4: "AUDIO_N",
            5: "AUDIO_P", 6: "GND", 7: "12V_POD", 8: "GND",
            9: "POD_SHIELD", 10: "POD_SHIELD"}
    receipt = {"schema": 1, "kind": "crow-spoke-implementation-v1", "role": "pod",
               "contract_sha256": hashlib.sha256(raw).hexdigest(),
               "denominator": {"expected": 1, "realized": 1}, **bindings,
               "connectors": [{"ref": "J1", "mpn": "615008160221",
                               "footprint": "crow_mic_pod_v3:Wurth_615008160221_RJ45",
                               "pads": [{"number": n, "net": net} for n, net in pads.items()]}]}
    return root, receipt


@test("RJ45 receipts bind both current board and schematic bytes", kind="known_bad")
def t_rj45_stale_subject_receipt():
    for kind in ("board", "schematic"):
        root, receipt = receipt_fixture()
        module._validate_child_receipt(root, "pod", receipt)
        subject = root / module.CHILDREN["pod"]["root"] / receipt[kind]["path"]
        subject.write_bytes(subject.read_bytes() + b"changed")
        try:
            module._validate_child_receipt(root, "pod", receipt)
        except module.ContractError:
            continue
        raise AssertionError(f"stale {kind} receipt accepted")


@test("RJ45 receipts reject duplicate physical pad records", kind="known_bad")
def t_rj45_duplicate_pad_receipt():
    root, receipt = receipt_fixture()
    module._validate_child_receipt(root, "pod", receipt)
    pads = receipt["connectors"][0]["pads"]
    pads.append(copy.deepcopy(pads[0]))
    try:
        module._validate_child_receipt(root, "pod", receipt)
    except module.ContractError:
        return
    raise AssertionError("duplicate pad record accepted")


@test("RJ45 child execution rejects duplicate JSON keys", kind="known_bad")
def t_rj45_duplicate_receipt_json():
    root, receipt = receipt_fixture()
    raw = json.dumps(receipt)
    result = subprocess.CompletedProcess(["fixture"], 0, stdout=raw, stderr="")
    with mock.patch.object(module.subprocess, "run", return_value=result):
        module._run_child_checker(root, "pod")
    result.stdout = raw[:-1] + ', "schema": 1}'
    with mock.patch.object(module.subprocess, "run", return_value=result):
        try:
            module._run_child_checker(root, "pod")
        except module.ContractError:
            return
    raise AssertionError("duplicate receipt JSON key accepted")

if __name__ == "__main__":
    sys.exit(main())
