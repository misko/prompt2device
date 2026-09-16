#!/usr/bin/env python3
"""Fail closed unless both child boards implement the canonical spoke contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import yaml


EXPECTED = {'schema': 1,
 'kind': 'crow_roof_array_analog_spoke',
 'connector': {'manufacturer': 'Wurth Elektronik',
               'family': 'WR-MJ',
               'pcb_header_mpn': '615008160221',
               'positions': 8,
               'electrical_pads': 10,
               'orientation': 'right_angle',
               'mounting': 'through_hole',
               'category': 'Cat6',
               'shielded': True,
               'rows': 2,
               'row_spacing_mm': 4.0,
               'same_row_pitch_mm': 2.04,
               'x_stagger_mm': 1.02,
               'footprint_carrier': 'crow_audio_carrier:Wurth_615008160221_RJ45',
               'footprint_pod': 'crow_mic_pod_v3:Wurth_615008160221_RJ45',
               'contact_rating_a': 1.5,
               'contact_rating_qualification_status': 'MANUFACTURER_JACK_RATING_ONLY',
               'contact_resistance_max_mohm': 20.0},
 'pins': [{'number': 1,
           'signal': '+12V_POD',
           'canonical_net': '12V_POD',
           'direction': 'carrier_to_pod',
           'function': 'power'},
          {'number': 2,
           'signal': 'GND',
           'canonical_net': 'GND',
           'direction': 'return_to_carrier',
           'function': 'power_return'},
          {'number': 3,
           'signal': '+12V_POD',
           'canonical_net': '12V_POD',
           'direction': 'carrier_to_pod',
           'function': 'power'},
          {'number': 4,
           'signal': 'AUDIO−',
           'canonical_net': 'AUDIO_N',
           'direction': 'pod_to_carrier',
           'function': 'active_balanced_negative'},
          {'number': 5,
           'signal': 'AUDIO+',
           'canonical_net': 'AUDIO_P',
           'direction': 'pod_to_carrier',
           'function': 'active_balanced_positive'},
          {'number': 6,
           'signal': 'GND',
           'canonical_net': 'GND',
           'direction': 'return_to_carrier',
           'function': 'power_return'},
          {'number': 7,
           'signal': '+12V_POD',
           'canonical_net': '12V_POD',
           'direction': 'carrier_to_pod',
           'function': 'power'},
          {'number': 8,
           'signal': 'GND',
           'canonical_net': 'GND',
           'direction': 'return_to_carrier',
           'function': 'power_return'}],
 'shell_pads': [{'number': 9, 'carrier_net': 'CHASSIS', 'pod_net': 'POD_SHIELD'},
                {'number': 10, 'carrier_net': 'CHASSIS', 'pod_net': 'POD_SHIELD'}],
 'cable': {'manufacturer': 'Weidmuller',
           'assembly_mpn': '8909650150',
           'assembly_order_code': '8909650150',
           'exact_assembly_source': 'https://eshop.weidmueller.com/en/ie-c6es8ug0150a40a40-e/p/8909650150',
           'bulk_cable_mpn': None,
           'bulk_cable_source': None,
           'construction': {'pairs': 4,
                            'conductor_awg': 26,
                            'stranding': 7,
                            'conductor_material': 'tinned_copper',
                            'jacket': 'PUR',
                            'jacket_color': 'green',
                            'shield': 'S/FTP',
                            'uv_resistant': None,
                            'oil_resistant': True,
                            'operating_temperature_min_c': -40.0,
                            'operating_temperature_max_c': 80.0,
                            'maximum_loop_dcr_ohm_per_km_at_20c': 290.0,
                            'copper_clad_aluminum_permitted': False},
           'length_m': 15.0,
           'nominal_array_radius_m': 4.0,
           'installed_length_per_port_status': 'OWED',
           'qualification_reference_length_m': 15.0,
           'maximum_design_length_m': 15.0,
           'qualified_maximum_length_m': None,
           'length_qualification_status': 'OWED',
           'termination': 'factory_male_to_male_8p8c_t568b_both_ends',
           'plug_bom_mpn': None,
           'plug_quantity_per_cord': 2,
           'cable_bom_mpn': None,
           'straight_pin_identity': True,
           'cavity_numbering_view': 'primary_manufacturer_drawing',
           'topology': 'four_twisted_pairs_sftp',
           'outer_diameter_nominal_mm': None,
           'outer_diameter_min_mm': 6.1,
           'outer_diameter_max_mm': 6.5,
           'full_boot_length_approx_mm': None,
           'full_boot_length_guaranteed_max_mm': None,
           'plug_width_mm': 13.7,
           'plug_height_mm': 18.456687,
           'manufacturer_bend_radius_singular_d': 5.0,
           'manufacturer_bend_radius_repeated_d': 10.0,
           'bend_radius_singular_nominal_mm': None,
           'bend_radius_repeated_nominal_mm': None,
           'project_minimum_bend_radius_mm': 67.0,
           'project_bend_basis': 'retained_67mm_planning_floor_exceeds_manufacturer_10D_times_6.5mm_maximum_OD_65mm_installed_fit_still_owed',
           'ingress_rating': 'IP20',
           'enclosure_constraint': 'plugs_and_connections_inside_dry_zones',
           'pair_allocation': {'orange': [1, 2], 'green': [3, 6], 'blue': [4, 5], 'brown': [7, 8]},
           'conductor_map': [{'cavity': 1,
                              'signal': '+12V_POD',
                              'pair': 'orange',
                              'color': 'white_orange'},
                             {'cavity': 2, 'signal': 'GND', 'pair': 'orange', 'color': 'orange'},
                             {'cavity': 3,
                              'signal': '+12V_POD',
                              'pair': 'green',
                              'color': 'white_green'},
                             {'cavity': 4, 'signal': 'AUDIO−', 'pair': 'blue', 'color': 'blue'},
                             {'cavity': 5,
                              'signal': 'AUDIO+',
                              'pair': 'blue',
                              'color': 'white_blue'},
                             {'cavity': 6, 'signal': 'GND', 'pair': 'green', 'color': 'green'},
                             {'cavity': 7,
                              'signal': '+12V_POD',
                              'pair': 'brown',
                              'color': 'white_brown'},
                             {'cavity': 8, 'signal': 'GND', 'pair': 'brown', 'color': 'brown'}],
           'continuity_test': 'unpowered straight-through1-1 through8-8 and shield continuity; no '
                              'cross-short; finished-cord DC loop resistance <=2.2 ohm at maximum '
                              'service temperature',
           'shield_continuous': True,
           'shield_bonding': 'carrier_EMI_fingers_to_grounded_metal_panel; '
                             'pod_local_island_POD_SHIELD_isolated_from_signal_GND',
           'pcb_power_fanout': 'three_distinct_contacts_per_rail_paralleled_on_each_PCB_no_joined_wires',
           'power_budget': {'reference_temperature_c': 20.0,
                            'hot_resistance_multiplier': 1.25,
                            'parallel_balanced_power_pairs': 3,
                            'loop_contact_allocation_ohm': 0.3,
                            'allocation_status': 'DESIGN_ALLOCATION_MEASUREMENT_OWED',
                            'computed_hot_loop_ohm': 2.1125,
                            'computed_drop_v_at_max_current': 0.21125,
                            'computed_pod_min_v': 10.58875,
                            'maximum_service_temperature_c': 75.0},
           'plug_contact_rating_a': None,
           'plug_contact_resistance_max_ohm': None,
           'plug_contact_qualification_status': 'OWED',
           'uv_qualification_status': 'OWED_BEFORE_OUTDOOR_DEPLOYMENT',
           'nominal_model_end_length_mm': 57.98,
           'nominal_model_grip_diameter_mm': 22.986,
           'mechanical_tolerances_status': 'OWED',
           'factory_assembly_identity_authority': 'exact_orderable_cord_no_separate_bulk_or_plug_order_code_claim'},
 'electrical': {'supply_nominal_v': 12.0,
                'carrier_header_supply_min_v': 10.8,
                'carrier_header_supply_max_v': 13.2,
                'maximum_cable_and_contact_loop_resistance_ohm': 2.2,
                'pod_header_supply_min_v_at_max_current_and_length': 10.5,
                'maximum_continuous_pod_current_a': 0.1,
                'nominal_current_per_parallel_contact_a': 0.03333333333333333,
                'hot_plug_permitted': False,
                'pod_input_capacitance_max_uf': 47.0,
                'inrush_qualification_status': 'OWED',
                'carrier_protection_hold_min_a_at_70c': 0.1,
                'carrier_protection_trip_max_a_at_25c': 0.7,
                'fault_clearing_requirement': 'carrier_limits_cable_and_pre_pod_faults_while_pod_protection_limits_downstream_board_faults_and_one_faulted_spoke_does_not_reset_other_seven',
                'audio_interface': 'active_balanced_analog',
                'pod_output_coupling': 'dc_coupled',
                'pod_audio_common_mode_nominal_v': 2.5,
                'pod_audio_common_mode_min_v': 2.35,
                'pod_audio_common_mode_max_v': 2.65,
                'pod_source_impedance_nominal_ohm_each_leg': 100.0,
                'pod_source_impedance_maximum_mismatch_ohm': 2.0,
                'pod_maximum_output_differential_vrms': 1.2,
                'carrier_input_coupling': 'ac_coupled_each_leg',
                'carrier_input_coupling_capacitance_uf_each_leg': 1.0,
                'carrier_input_bias_resistance_ohm_each_leg': 100000,
                'receiver_full_scale_differential_vrms': 2.0,
                'acoustic_polarity_target': 'positive_pressure_drives_AUDIO+_positive_relative_to_AUDIO−',
                'acoustic_polarity_qualification_status': 'OWED',
                'ethernet': False,
                'poe': False,
                'supply_plane': 'carrier_RJ45_parallel_contacts_1_3_7_to_2_6_8'},
 'physical_qualification_status': 'OWED',
 'straight_through': True}


class ContractError(ValueError):
    pass


CHILD_KIND = "crow-spoke-implementation-v1"
CHILD_TIMEOUT_S = 60
CHILDREN = {
    "carrier": {
        "root": "projects/crow-audio-carrier-v1",
        "checker": "03_src/check_spoke_implementation.py",
        "board": "04_kicad/crow_audio_carrier_v1.kicad_pcb",
        "schematic": "04_kicad/crow_audio_carrier_v1.kicad_sch",
        "refs": tuple(f"J{index}" for index in range(1, 9)),
        "footprint": "crow_audio_carrier:Wurth_615008160221_RJ45",
    },
    "pod": {
        "root": "projects/crow-mic-pod-v3",
        "checker": "03_src/check_spoke_implementation.py",
        "board": "04_kicad/crow_mic_pod_v3.kicad_pcb",
        "schematic": "04_kicad/crow_mic_pod_v3.kicad_sch",
        "refs": ("J1",),
        "footprint": (
            "crow_mic_pod_v3:"
            "Wurth_615008160221_RJ45"
        ),
    },
}


class StrictSafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(loader: StrictSafeLoader, node: yaml.Node,
                              deep: bool = False) -> dict:
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key: {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_contract(path: Path) -> tuple[dict, bytes]:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"missing regular contract: {path}")
    try:
        raw = path.read_bytes()
        value = yaml.load(raw.decode("utf-8"), Loader=StrictSafeLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"contract must be a mapping: {path}")
    if value != EXPECTED:
        raise ContractError(f"contract differs from canonical spoke interface: {path}")
    return value, raw


def cable_power_budget(value: dict) -> dict:
    """Screen three distinct balanced power pairs and the complete hot DC loop.

    Manufacturer maximum DCR is a pair LOOP value; dividing by three accounts
    for the three independently terminated pairs in parallel. The contact
    allowance is an unmeasured design allocation, never a cord rating.
    """
    cable = value["cable"]
    rows = cable["conductor_map"]
    expected = {1: ("orange", "+12V_POD"), 2: ("orange", "GND"),
                3: ("green", "+12V_POD"), 6: ("green", "GND"),
                7: ("brown", "+12V_POD"), 8: ("brown", "GND")}
    power_rows = [row for row in rows if row.get("signal") in {"+12V_POD", "GND"}]
    actual = {row.get("cavity"): (row.get("pair"), row.get("signal")) for row in power_rows}
    if len(power_rows) != 6 or actual != expected:
        raise ContractError("power requires six distinct correctly paired contacts")

    def positive(name: str, number: object) -> float:
        if (isinstance(number, bool) or not isinstance(number, (int, float))
                or not math.isfinite(number) or number <= 0):
            raise ContractError(f"{name} must be finite and positive")
        return float(number)

    budget = cable["power_budget"]
    electrical = value["electrical"]
    length = positive("design length", cable["maximum_design_length_m"])
    dcr = positive("pair loop DCR", cable["construction"]["maximum_loop_dcr_ohm_per_km_at_20c"])
    hot_factor = positive("hot factor", budget["hot_resistance_multiplier"])
    allocation = positive("contact allocation", budget["loop_contact_allocation_ohm"])
    current = positive("pod current", electrical["maximum_continuous_pod_current_a"])
    supply = positive("carrier minimum", electrical["carrier_header_supply_min_v"])
    limit = positive("finished loop limit", electrical["maximum_cable_and_contact_loop_resistance_ohm"])
    minimum = positive("pod minimum", electrical["pod_header_supply_min_v_at_max_current_and_length"])
    if current > 0.100:
        raise ContractError("pod current exceeds the commissioned 0.100 A boundary")
    hot_loop = length / 1000 * dcr / 3 * hot_factor + allocation
    drop = hot_loop * current
    pod_voltage = supply - drop
    if hot_loop > limit or pod_voltage < minimum:
        raise ContractError(f"hot harness loop fails: {hot_loop:.6f} ohm, {pod_voltage:.6f} V")
    return {"power_conductors": 6,
            "design_hot_loop_ohm": round(hot_loop, 6),
            "design_drop_v": round(drop, 6),
            "design_pod_min_v": round(pod_voltage, 6),
            "physical_qualification": "OWED"}


def verify_contracts(repo_root: Path) -> dict:
    paths = [
        repo_root / "projects/crow-roof-array-v1/03_src/rules/spoke_interface.yaml",
        repo_root / "projects/crow-audio-carrier-v1/03_src/rules/spoke_interface.yaml",
        repo_root / "projects/crow-mic-pod-v3/03_src/rules/spoke_interface.yaml",
    ]
    loaded = [load_contract(path) for path in paths]
    values = [item[0] for item in loaded]
    payloads = [item[1] for item in loaded]
    if any(item != values[0] for item in values[1:]):
        raise ContractError("parent/carrier/pod spoke contract values disagree")
    if any(item != payloads[0] for item in payloads[1:]):
        raise ContractError("parent/carrier/pod spoke contract bytes disagree")
    return {
        "schema": 1,
        "kind": "crow-roof-array-spoke-interface-check-v1",
        "status": "PASS",
        "contracts": [str(path.relative_to(repo_root)) for path in paths],
        "contract_sha256": hashlib.sha256(payloads[0]).hexdigest(),
        "pins": 8,
        "electrical_pads_per_connector": 10,
        "straight_through": True,
        "cable_power_budget": cable_power_budget(values[0]),
    }


def _record(base: Path, path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"expected ordinary file: {path}")
    payload = path.read_bytes()
    return {
        "path": path.relative_to(base).as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "size": len(payload),
    }


def _unique_json_pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"child receipt has duplicate JSON key {key!r}")
        result[key] = value
    return result


def _expected_nets(role: str, ref: str) -> dict[int, str]:
    suffix = str(int(ref[1:])) if role == "carrier" else ""
    shell = "CHASSIS" if role == "carrier" else "POD_SHIELD"
    return {1: f"12V_POD{suffix}", 2: "GND", 3: f"12V_POD{suffix}",
            4: f"AUDIO_N{suffix}", 5: f"AUDIO_P{suffix}", 6: "GND",
            7: f"12V_POD{suffix}", 8: "GND", 9: shell, 10: shell}


def _validate_binding(project_root: Path, binding: object,
                      expected_path: str, label: str) -> dict:
    if not isinstance(binding, dict) or set(binding) != {"path", "sha256", "size"}:
        raise ContractError(f"{label} binding must contain path/sha256/size exactly")
    if binding.get("path") != expected_path:
        raise ContractError(
            f"{label} path {binding.get('path')!r}, expected {expected_path!r}"
        )
    actual = _record(project_root, project_root / expected_path)
    if binding != actual:
        raise ContractError(f"{label} binding is stale: {binding!r} != {actual!r}")
    return actual


def _validate_child_receipt(repo_root: Path, role: str, receipt: object) -> dict:
    spec = CHILDREN[role]
    project_root = repo_root / spec["root"]
    if not isinstance(receipt, dict):
        raise ContractError(f"{role} checker did not emit a JSON mapping")
    required = {
        "schema", "kind", "role", "contract_sha256", "denominator",
        "board", "schematic", "connectors",
    }
    if set(receipt) != required:
        raise ContractError(
            f"{role} receipt fields differ: missing={sorted(required-set(receipt))}, "
            f"unknown={sorted(set(receipt)-required)}"
        )
    if (receipt.get("schema"), receipt.get("kind"), receipt.get("role")) != (
            1, CHILD_KIND, role):
        raise ContractError(f"{role} receipt schema/kind/role is invalid")
    contract_path = repo_root / spec["root"] / "03_src/rules/spoke_interface.yaml"
    contract_sha = hashlib.sha256(contract_path.read_bytes()).hexdigest()
    if receipt.get("contract_sha256") != contract_sha:
        raise ContractError(f"{role} receipt is bound to the wrong spoke contract")

    refs = tuple(spec["refs"])
    denominator = receipt.get("denominator")
    if denominator != {"expected": len(refs), "realized": len(refs)}:
        raise ContractError(f"{role} denominator is not closed: {denominator!r}")
    board = _validate_binding(
        project_root, receipt.get("board"), str(spec["board"]), f"{role} board"
    )
    schematic = _validate_binding(
        project_root, receipt.get("schematic"), str(spec["schematic"]),
        f"{role} schematic",
    )

    connectors = receipt.get("connectors")
    if not isinstance(connectors, list) or len(connectors) != len(refs):
        raise ContractError(
            f"{role} connector denominator is "
            f"{len(connectors) if isinstance(connectors, list) else 'invalid'}/"
            f"{len(refs)}"
        )
    by_ref: dict[str, dict] = {}
    for connector in connectors:
        if not isinstance(connector, dict) or set(connector) != {
                "ref", "mpn", "footprint", "pads"}:
            raise ContractError(f"{role} connector row has an invalid schema")
        ref = connector.get("ref")
        if not isinstance(ref, str) or ref in by_ref:
            raise ContractError(f"{role} connector ref is empty or duplicated: {ref!r}")
        by_ref[ref] = connector
    if set(by_ref) != set(refs):
        raise ContractError(
            f"{role} realized refs {sorted(by_ref)!r}, expected {list(refs)!r}"
        )
    for ref in refs:
        row = by_ref[ref]
        if row["mpn"] != EXPECTED["connector"]["pcb_header_mpn"]:
            raise ContractError(f"{role} {ref} uses the wrong connector MPN")
        if row["footprint"] != spec["footprint"]:
            raise ContractError(f"{role} {ref} uses the wrong exact footprint")
        pads = row["pads"]
        if not isinstance(pads, list) or any(
                not isinstance(pad, dict) or set(pad) != {"number", "net"}
                for pad in pads):
            raise ContractError(f"{role} {ref} pad rows have an invalid schema")
        actual_pads = {pad["number"]: pad["net"] for pad in pads}
        if len(actual_pads) != len(pads) or actual_pads != _expected_nets(role, ref):
            raise ContractError(
                f"{role} {ref} realized pad map {actual_pads!r}, "
                f"expected {_expected_nets(role, ref)!r}"
            )
    return {
        "role": role,
        "denominator": denominator,
        "board": board,
        "schematic": schematic,
        "connectors": len(connectors),
    }


def _run_child_checker(repo_root: Path, role: str) -> dict:
    spec = CHILDREN[role]
    project_root = repo_root / spec["root"]
    checker = project_root / spec["checker"]
    checker_record = _record(repo_root, checker)
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            [sys.executable, "-B", str(checker), str(project_root), "--json"],
            cwd=repo_root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=CHILD_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as exc:
        raise ContractError(
            f"{role} implementation checker exceeded {CHILD_TIMEOUT_S}s"
        ) from exc
    if completed.returncode != 0:
        detail = (completed.stdout + completed.stderr)[-3000:]
        raise ContractError(f"{role} implementation checker failed: {detail}")
    try:
        receipt = json.loads(completed.stdout, object_pairs_hook=_unique_json_pairs)
    except (json.JSONDecodeError, ContractError) as exc:
        raise ContractError(f"{role} checker emitted invalid JSON: {exc}") from exc
    if _record(repo_root, checker) != checker_record:
        raise ContractError(f"{role} implementation checker changed while executing")
    result = _validate_child_receipt(repo_root, role, receipt)
    result["checker"] = checker_record
    return result


def verify(repo_root: Path) -> dict:
    """Verify the three contracts and both generated child implementations."""
    repo_root = Path(repo_root).resolve()
    contract_result = verify_contracts(repo_root)
    implementations = [
        _run_child_checker(repo_root, role) for role in ("carrier", "pod")
    ]
    return {
        **contract_result,
        "kind": "crow-roof-array-spoke-system-check-v1",
        "implementations": implementations,
        "realized_connectors": 9,
        "realized_straight_through_pin_paths": 64,
        "realized_shell_pads": 18,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = verify(args.root.resolve())
    except ContractError as exc:
        print(f"CROW-SPOKE FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("CROW-SPOKE PASS: 3/3 contracts; carrier 8/8 + pod 1/1 "
              "generated connectors; 64/64 straight-through contact paths; 18/18 shell pads")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
