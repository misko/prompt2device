#!/usr/bin/env python3
"""T1: declarative stage registry and non-authoritative shadow planning."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import check, eq, main, test  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "pcb-design" / "scripts"))
from pipeline_contract import StageSpec  # noqa: E402
from pipeline_registry import RegistryValidationError, StageRegistry  # noqa: E402


def spec(stage_id, *, cost="cheap", lifecycle="schematic", requires=(), produces=(), invalidated_by=()):
    return StageSpec(
        id=stage_id,
        owner="pcb-design",
        lifecycle=lifecycle,
        cost=cost,
        work_class="network" if cost == "external" else "local",
        timeout_s=30,
        requires=tuple(sorted(requires)),
        produces=tuple(sorted(produces)),
        blocks=(),
        invalidated_by=tuple(sorted(invalidated_by)),
    )


def fixture_registry():
    return StageRegistry((
        spec("P-SCHEMA", produces=("schema_valid",)),
        spec("P-FETCH", cost="external", lifecycle="sourcing",
             requires=("part_codes",), produces=("catalog_facts",)),
        spec("P-BUILD", cost="bounded", requires=("schema_valid",),
             produces=("generated_schematic",)),
        spec("P-REVIEW", cost="review", requires=("generated_schematic",),
             produces=("schematic_review",)),
    ))


@test("registry resolves dependencies and orders cheap runnable work first")
def t_resolve():
    registry = fixture_registry()
    plan = registry.resolve(available=("part_codes",))
    eq(tuple(item.id for item in plan),
       ("P-SCHEMA", "P-BUILD", "P-FETCH", "P-REVIEW"),
       "deterministic cheap-first plan")


@test("targeted shadow plan contains only the required closure")
def t_target_closure():
    registry = fixture_registry()
    plan = registry.resolve(("P-REVIEW",), available=("part_codes",))
    eq(tuple(item.id for item in plan),
       ("P-SCHEMA", "P-BUILD", "P-REVIEW"), "review closure")


@test("shadow comparison reports exact agreement without executing stages")
def t_shadow_agreement():
    registry = fixture_registry()
    expected = ("P-SCHEMA", "P-BUILD", "P-FETCH", "P-REVIEW")
    comparison = registry.compare_shadow(expected, available=("part_codes",))
    check(comparison.matches, "equal shadow plan did not match")
    eq(comparison.first_divergence, None, "agreement divergence")


@test("shadow comparison REFUSES a reordered legacy observation", kind="known_bad")
def t_shadow_order_mismatch():
    registry = fixture_registry()
    observed = ("P-FETCH", "P-SCHEMA", "P-BUILD", "P-REVIEW")
    comparison = registry.compare_shadow(observed, available=("part_codes",))
    check(not comparison.matches, "reordered legacy plan was accepted")
    eq(comparison.first_divergence, 0, "first order divergence")


@test("registry REFUSES an unresolved requirement", kind="known_bad")
def t_missing_requirement():
    registry = fixture_registry()
    try:
        registry.resolve(("P-FETCH",))
    except RegistryValidationError as exc:
        check("has no producer" in str(exc), "missing requirement diagnosis")
    else:
        raise AssertionError("unresolved external fact entered the plan")


@test("registry REFUSES unused or misspelled available facts", kind="known_bad")
def t_unknown_available_fact():
    registry = fixture_registry()
    try:
        registry.resolve(available=("part_codes", "part/codes"))
    except RegistryValidationError as exc:
        check("not required" in str(exc), "unused available-fact diagnosis")
    else:
        raise AssertionError("unused path-shaped available fact was accepted")


@test("registry REFUSES multiple producers for one fact", kind="known_bad")
def t_duplicate_producer():
    try:
        StageRegistry((
            spec("P-ONE", produces=("same_fact",)),
            spec("P-TWO", produces=("same_fact",)),
        ))
    except RegistryValidationError as exc:
        check("multiple producers" in str(exc), "producer collision diagnosis")
    else:
        raise AssertionError("ambiguous fact producer was accepted")


@test("registry REFUSES a dependency cycle", kind="known_bad")
def t_cycle():
    try:
        StageRegistry((
            spec("P-ONE", requires=("fact_two",), produces=("fact_one",)),
            spec("P-TWO", requires=("fact_one",), produces=("fact_two",)),
        ))
    except RegistryValidationError as exc:
        check("cycle" in str(exc), "cycle diagnosis")
    else:
        raise AssertionError("cyclic registry was accepted")



def impact_registry():
    return StageRegistry((
        spec("P-PARTS", lifecycle="sourcing", requires=("part_selection",),
             produces=("parts_ready",), invalidated_by=("stock_expiry",)),
        spec("P-PLACE", lifecycle="placement", requires=("placement_source",),
             produces=("placed_board",)),
        spec("P-ROUTE", lifecycle="routing", requires=("placed_board",),
             produces=("routed_board",), invalidated_by=("route_method",)),
        spec("P-NATIVE", lifecycle="layout_seal", requires=("routed_board",),
             produces=("native_checked",)),
        spec("P-STAGE", lifecycle="release_staging",
             requires=("native_checked", "parts_ready"), produces=("release_staged",)),
    ))


@test("impact propagates placement through routing native check and staging")
def t_impact_placement():
    result = impact_registry().change_impact(changed_symbols=("placement_source",))
    eq(result["affected"], ["P-PLACE", "P-ROUTE", "P-NATIVE", "P-STAGE"], "downstream")
    eq(result["unaffected"], ["P-PARTS"], "independent sourcing")
    eq(result["authority"], "DIAGNOSTIC_ONLY", "not acceptance")
    eq(result["reuse_authorized"], False, "unaffected is not reusable evidence")


@test("impact preserves upstream work for route-method changes")
def t_impact_method():
    result = impact_registry().change_impact(changed_categories=("route_method",))
    eq(result["affected"], ["P-ROUTE", "P-NATIVE", "P-STAGE"], "method descendants")
    eq(impact_registry().change_impact()["affected"], [], "no declared changes")


@test("impact rejects misspelled changes rather than reporting nothing", kind="known_bad")
def t_impact_unknown():
    for kwargs in ({"changed_symbols": ["place_source"]},
                   {"changed_stage_ids": ["P-ABSENT"]},
                   {"changed_categories": ["expired"]},
                   {"changed_symbols": "placement_source"}):
        try:
            impact_registry().change_impact(**kwargs)
        except RegistryValidationError:
            pass
        else:
            raise AssertionError(f"unknown or malformed change accepted: {kwargs}")


@test("changed produced artifact invalidates producer and all consumers", kind="known_bad")
def t_impact_tampered_output():
    result = impact_registry().change_impact(changed_symbols=("routed_board",))
    eq(result["affected"], ["P-ROUTE", "P-NATIVE", "P-STAGE"], "tampered output")
    # No available-fact shortcut is exposed by change_impact.
    try:
        impact_registry().change_impact(changed_stage_ids=("P-PLACE",),
                                       available=("routed_board",))
    except TypeError:
        pass
    else:
        raise AssertionError("old available artifact suppressed invalidation")


@test("impact records converging reasons and preserves deterministic ordering")
def t_impact_multiple_reasons():
    result = impact_registry().change_impact(
        changed_stage_ids=("P-NATIVE",), changed_categories=("stock_expiry",))
    eq(result["affected"], ["P-PARTS", "P-NATIVE", "P-STAGE"], "ordered union")
    eq(result["reasons"]["P-STAGE"], ["upstream:P-NATIVE", "upstream:P-PARTS"],
       "both reasons retained")


if __name__ == "__main__":
    raise SystemExit(main())
