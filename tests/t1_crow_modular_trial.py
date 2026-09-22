#!/usr/bin/env python3
"""T1: Crow modular replay preparation preserves inputs and removes solutions."""

from __future__ import annotations

import importlib.util
import sys
from copy import deepcopy

import yaml

from harness import ROOT, check, eq, main, test


SCRIPT = ROOT / "tests/checkpoints/crow_modular_trial.py"
_spec = importlib.util.spec_from_file_location("crow_modular_trial", SCRIPT)
assert _spec and _spec.loader
trial = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(trial)
SOURCE = ROOT / "projects/crow-audio-carrier-v1"


@test("Crow trial transform preserves inherited envelope and clears solutions")
def t_floorplan_transform():
    original = yaml.safe_load((SOURCE / "03_src/floorplan.yaml").read_text())
    result = trial.sanitized_floorplan(SOURCE)
    eq(result["board"]["outline"], original["board"]["outline"], "outline")
    eq(result["board"]["mounting_holes"],
       original["board"]["mounting_holes"], "mounting holes")
    eq(result["board"]["outline"]["x1"], 172.0, "pinned east edge")
    eq(result["placement"]["anchors"], {}, "component anchors")
    expected_models = trial.model_only_patterns(original, SOURCE)
    eq(result["placement"]["patterns"], expected_models, "model-only bindings")
    eq(len(expected_models), 3, "model-only binding count")
    for pattern in expected_models:
        eq(set(pattern), {"match", "model_override"}, "model binding fields")
        check(trial.resolve_inherited_model(
            SOURCE, pattern["model_override"]).is_file(),
            "model binding does not resolve to retained asset")
    for key in ("thermal_vias", "zones", "keepouts", "silk"):
        check(key not in result, f"solution-derived {key} survived")
    for key in ("fiducials",):
        check(key not in result["board"], f"solution-derived board {key} survived")
    for key in ("repeat", "regions", "legalize"):
        check(key not in result["placement"],
              f"solution-derived placement {key} survived")


@test("hardcoded proposed Crow envelope is rejected", kind="known_bad")
def t_proposed_envelope_rejected():
    original = yaml.safe_load((SOURCE / "03_src/floorplan.yaml").read_text())
    result = trial.sanitized_floorplan(SOURCE)
    result["board"]["outline"] = {
        "x0": 16.0, "y0": 20.0, "x1": 170.0, "y1": 120.0,
    }
    try:
        trial.validate_floorplan_transform(original, result, SOURCE)
    except ValueError as exc:
        check("outline differs" in str(exc), f"wrong refusal: {exc}")
    else:
        raise AssertionError("proposed 154 mm envelope replaced pinned input")


@test("mixed model pattern cannot leak placement geometry", kind="known_bad")
def t_mixed_model_pattern_rejected():
    original = yaml.safe_load((SOURCE / "03_src/floorplan.yaml").read_text())
    mixed = deepcopy(original)
    model_pattern = next(
        pattern for pattern in mixed["placement"]["patterns"]
        if "model_override" in pattern)
    model_pattern.update({
        "region": "solved-cell", "near": "U_ADC", "at": [91.0, 64.0],
        "rotation": 180, "side": "F.Cu",
    })
    projected = trial.model_only_patterns(mixed, SOURCE)
    eq(set(projected[0]), {"match", "model_override"}, "projection fields")
    result = trial.sanitized_floorplan(SOURCE)
    result["placement"]["patterns"][0]["near"] = "U_ADC"
    try:
        trial.validate_floorplan_transform(original, result, SOURCE)
    except ValueError as exc:
        check("model bindings differ" in str(exc) or "placement" in str(exc),
              f"wrong refusal: {exc}")
    else:
        raise AssertionError("model path smuggled solved placement geometry")


@test("model binding rejects traversal and transform maps", kind="known_bad")
def t_model_binding_scope_rejected():
    bad_values = (
        "${KIPRJMOD}/../03_src/lib/3dmodels/../../route/final_chain.kicad_pcb",
        {"file": "${KIPRJMOD}/../03_src/lib/3dmodels/kicad/model.step",
         "offset": [1, 2, 3]},
    )
    for value in bad_values:
        try:
            trial.resolve_inherited_model(SOURCE, value)
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe model binding accepted: {value!r}")


@test("dirty Crow reconstruction input is rejected", kind="known_bad")
def t_dirty_source_rejected():
    state = {"git_status": " M projects/crow-audio-carrier-v1/03_src/floorplan.yaml\n"}
    try:
        trial.require_clean_source_state(state)
    except SystemExit as exc:
        check("dirty" in str(exc), f"wrong refusal: {exc}")
    else:
        raise AssertionError("dirty source input was accepted")


@test("future Crow boundary labels baseline geometry inherited")
def t_boundary_is_honest():
    text = trial.boundary_text()
    prose = " ".join(text.split())
    check("Inherited physical inputs" in text, "missing inherited classification")
    check("not newly established hard requirements" in prose,
          "boundary promotes inherited geometry to authority")
    check("154 x 100 mm" not in text, "obsolete proposed envelope remains")
    check("model-only bindings" in text, "missing model identity boundary")
    check("no model transform" in text, "model pose exclusion is unstated")


if __name__ == "__main__":
    sys.exit(main())
