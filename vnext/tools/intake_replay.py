"""Standalone, deterministic Crow intake fixture and output grader.

This checks a candidate's stated reconstruction, not its reasoning process,
engineering acceptance, a full schematic replay, or LLM determinism.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

CASE = Path(__file__).resolve().parents[1] / "tests/replay/crow_initial"
INPUTS = ("PROMPT.md", "USER_DECISIONS.md", "capability-profile.json", "TASK.md")
SOURCES = {"PROMPT.md", "USER_DECISIONS.md"}
EXPECTED = {
    "microphone_count": 8,
    "array_diameter_m": 8,
    "build_quantity": 3,
    "recording_target_m": 50,
    "array_budget_ceiling_usd": 600,
    "budget_minimum_usd": 0,
    "radial_cable_m": 4,
    "nominal_supply_v": 12,
    "planar": True,
    "usb_audio_available": True,
    "persistent_identity_required": False,
    "localization": "direction_or_position",
    "ethernet_cable": True,
}
UNKNOWN = {"supply_current_a", "supply_tolerance_v", "sample_rate_hz", "bit_depth"}
SOURCING = {
    "preferred_supplier": "JLCPCB",
    "prototype_usb_two_source_exception": True,
    "seller_in_stock_badge_sufficient": True,
    "numeric_stock_count_required": False,
    "second_independent_supplier_required": False,
    "western_fallback": True,
    "ask_user_if_unavailable": True,
    "vnext_default": True,
}
PROTECTION_SCOPE = {
    "internal_converter_12v_to_5v_pass_through_extra_protection_required": False,
    "normal_12v_to_5v_conversion_required": True,
    "startup_shutdown_short_esd_obligations_waived": False,
}
WORKFLOW = {
    "accepted_stages": [],
    "next_stage": "PCB-COMMISSION",
    "schematic_goal": True,
    "delegate_sol_where_possible": True,
    "vnext_only": True,
    "log_attempts_and_backtracks": True,
    "replay_from_initial_inputs": True,
    "bounded_topology_backtrack_authorized": True,
    "nonaccepted_schematic_draft_authorized": True,
    "draft_is_engineering_acceptance": False,
}
# Crow-specific declared preferences, not a scheduler or universal PCB policy.
EXECUTION_PREFERENCES = {
    "required_models": {
        "planning": "Astra", "fixing": "Astra", "vnext_writing": "Astra",
    },
    "preferred_models": {
        "bounded_research": "SOL", "inventory": "SOL",
        "test_execution": "SOL", "independent_review": "SOL",
    },
}
STOPS = {"schematic", "placement", "routing", "release"}
# This intake's decision IDs/values are test expectations, not generic skill rules.
DECISION_GROUPS = {
    "D16": {
        "retain_manufacturer_reference_filters": True,
        "reference_filter_banks": 2,
        "reference_filter_feed_ohm": 1,
        "reference_filter_parallel_capacitances_uf": [470, 4.7, 0.47],
    },
    "D17": {
        "power_backtrack_authorized": True,
        "power_author_attempt_limit": 1,
        "power_reviewed_repair_limit": 1,
        "preserve_prior_attempts": True,
        "automatic_budget_reset_authorized": False,
        "independent_power_review_before_integration": True,
    },
    "D18": {
        "diode_qualification_authorized": True,
        "diode_automatic_adoption_authorized": False,
        "independent_diode_review_before_adoption": True,
        "availability_before_electrical_qualification": True,
        "all_three_diode_roles_require_qualification": True,
        "diode_qualification_topology_redesign_authorized": False,
        "power_obligations_waived": False,
        "purchase_authorized": False,
        "diodes_per_hub": 3,
        "diode_qualification_total_quantity": 9,
    },
    "D19": {
        "shutdown_reassessment_authorized": True,
        "shutdown_control_power_budget_in_scope": True,
        "amplifier_adc_off_state_interface_in_scope": True,
        "shutdown_preserve_prior_spent_attempts": True,
        "shutdown_automatic_budget_reset_authorized": False,
        "shutdown_independent_review_required": True,
        "shutdown_broad_architecture_change_authorized": False,
        "shutdown_reference_filter_change_authorized": False,
        "shutdown_purchase_authorized": False,
        "shutdown_hardware_test_authorized": False,
        "shutdown_author_attempt_limit": 1,
        "shutdown_reviewed_repair_limit": 1,
    },
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(workspace: Path) -> None:
    if workspace.exists() and any(workspace.iterdir()):
        raise ValueError("candidate directory must be empty")
    workspace.mkdir(parents=True, exist_ok=True)
    for name in INPUTS:
        shutil.copyfile(CASE / name, workspace / name)


def grade(workspace: Path) -> dict:
    findings: list[dict[str, str]] = []

    def fail(code: str, detail: str) -> None:
        findings.append({"code": code, "detail": detail})

    for name in INPUTS:
        source, copy = CASE / name, workspace / name
        if not copy.is_file() or copy.read_bytes() != source.read_bytes():
            fail("INPUT_CHANGED", name)
    output = workspace / "REQUIREMENTS.json"
    if not output.is_file():
        fail("OUTPUT_MISSING", "REQUIREMENTS.json")
    else:
        try:
            data = json.loads(output.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("top-level JSON value must be an object")
            hashes = data.get("input_hashes")
            if not isinstance(hashes, dict) or any(
                hashes.get(name) != digest(CASE / name) for name in SOURCES
            ):
                fail("PROMPT_BINDING", "original prompt and decisions must be hash-bound")
            values = data.get("requirements")
            if not isinstance(values, dict):
                raise ValueError("requirements must be an object")
            for key, expected in EXPECTED.items():
                actual = values.get(key)
                if type(expected) is bool:
                    typed = type(actual) is bool
                elif type(expected) is int:
                    typed = type(actual) in (int, float)
                else:
                    typed = type(actual) is str
                if not typed or actual != expected:
                    fail("REQUIREMENT_MISMATCH", key)
            if UNKNOWN & values.keys():
                fail("INVENTED_CERTAINTY", "unconfirmed supply/audio-format facts in requirements")
            unknown = data.get("unconfirmed")
            if not isinstance(unknown, list) or not all(type(x) is str for x in unknown) or not UNKNOWN <= set(unknown):
                fail("INVENTED_CERTAINTY", "supply current/tolerance and sample format remain unconfirmed")
            provenance = data.get("provenance")
            if not isinstance(provenance, dict):
                raise ValueError("provenance must be an object")
            for key in EXPECTED:
                refs = provenance.get(key)
                if not isinstance(refs, list) or not refs or not all(type(x) is str and x in SOURCES for x in refs):
                    fail("PROVENANCE_MISSING", key)
            if "PROMPT.md" not in provenance.get("microphone_count", []):
                fail("PROMPT_PROVENANCE", "microphone_count must cite original prompt")
            for key in ("recording_target_m", "build_quantity", "array_budget_ceiling_usd", "budget_minimum_usd"):
                if "USER_DECISIONS.md" not in provenance.get(key, []):
                    fail("DECISION_PROVENANCE", key)
            protection = data.get("protection_scope")
            if not isinstance(protection, dict):
                fail("PROTECTION_SCOPE_MISSING", "explicit converter-fault scope and non-waiver required")
            else:
                for key, expected in PROTECTION_SCOPE.items():
                    if type(protection.get(key)) is not bool or protection[key] is not expected:
                        fail("PROTECTION_SCOPE_MISMATCH", key)
            scope = data.get("decision_scope")
            if isinstance(scope, dict) and "additional_topology_redesign_authorized" in scope:
                fail("AMBIGUOUS_AUTHORIZATION_SCOPE", "use task-scoped topology/shutdown fields")
            decision_refs = data.get("decision_provenance")
            valid_ids = {f"USER_DECISIONS.md#{item}" for item in DECISION_GROUPS}
            for decision_id, fields in DECISION_GROUPS.items():
                for key, expected in fields.items():
                    actual = scope.get(key) if isinstance(scope, dict) else None
                    if type(expected) is list:
                        matches = (isinstance(actual, list)
                                   and all(type(x) in (int, float) for x in actual)
                                   and sorted(actual) == sorted(expected))
                    elif type(expected) is int:
                        matches = type(actual) in (int, float) and actual == expected
                    else:
                        matches = type(actual) is type(expected) and actual == expected
                    if not matches:
                        fail("DECISION_SCOPE_MISMATCH", key)
                    refs = decision_refs.get(key) if isinstance(decision_refs, dict) else None
                    if (not isinstance(refs, list) or not refs
                            or not all(type(x) is str and x in valid_ids for x in refs)
                            or f"USER_DECISIONS.md#{decision_id}" not in refs):
                        fail("DECISION_ID_PROVENANCE", key)
            sourcing = data.get("sourcing_policy")
            if not isinstance(sourcing, dict):
                raise ValueError("sourcing_policy must be an object")
            for key, expected in SOURCING.items():
                if type(sourcing.get(key)) is not type(expected) or sourcing.get(key) != expected:
                    fail("SOURCING_MISMATCH", key)
            workflow = data.get("workflow")
            if not isinstance(workflow, dict):
                raise ValueError("workflow must be an object")
            for key, expected in WORKFLOW.items():
                if type(workflow.get(key)) is not type(expected) or workflow.get(key) != expected:
                    fail("WORKFLOW_MISMATCH", key)
            preferences = data.get("execution_preferences")
            if not isinstance(preferences, dict):
                fail("EXECUTION_PREFERENCES_MISSING", "latest role-specific model preferences required")
            else:
                for key, expected in EXECUTION_PREFERENCES.items():
                    if preferences.get(key) != expected:
                        fail("EXECUTION_PREFERENCES_MISMATCH", key)
            stops = workflow.get("stop_after")
            if not isinstance(stops, list) or not all(type(x) is str for x in stops) or set(stops) != STOPS:
                fail("CHECKPOINT_LOST", "schematic, placement, routing, release")
            action = workflow.get("next_action")
            if not isinstance(action, str) or len(action.strip()) < 20:
                fail("NEXT_ACTION_MISSING", "bounded commission action required")
            if any(key in data for key in ("acceptance", "accepted_schematic", "selected_parts", "schematic")):
                fail("PREMATURE_ENGINEERING", "no acceptance or design artifact belongs in initial intake")
        except (OSError, UnicodeError, ValueError, TypeError) as exc:
            fail("OUTPUT_INVALID", str(exc))
    return {
        "schema": 1,
        "outcome": "FAIL" if findings else "PASS",
        "findings": findings,
        "evidence": {
            "scope": "initial-intake reconstruction only",
            "engineering_acceptance": False,
            "full_schematic_replay": False,
            "llm_determinism": False,
            "model_enforcement": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "grade"))
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.workspace)
        print(json.dumps({"schema": 1, "workspace": str(args.workspace.resolve()), "task": "TASK.md"}))
        return 0
    result = grade(args.workspace)
    print(json.dumps(result, sort_keys=True))
    return int(result["outcome"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
