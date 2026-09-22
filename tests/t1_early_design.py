#!/usr/bin/env python3
"""T1: fail-closed commission/parts/schematic design contracts."""
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import (ROOT, check, contains, main, must_fail, must_pass, run,  # noqa: E402
                     test, tmpdir)

ED = ROOT / "skills" / "kicad-pcb" / "scripts" / "early_design_check.py"


REQ = """schema: 1
power_claims:
  - id: ports
    rails: [P1, P2]
    count: 2
    simultaneous_count: 2
    current_A: 3.0
    voltage_min_V: 4.75
    voltage_max_V: 5.25
    duty: continuous
    measurement_plane: mated_test_plug
    boundary_evidence: qualified test plug at the receptacle interface
    included_elements: [protection_switch, pcb_copper_vias_joints, mated_power_contacts]
    excluded_elements: [cable, appliance]
"""

POWER = """schema: 1
effective_capacitance_banks:
  - name: output stability
    requirement_uF: 30
    requirement_evidence: fixture datasheet effective ceramic minimum
    accepted_dielectrics: [ceramic]
    contributors:
      - part: CAP_CER
        refs: [C1, C2]
        nominal_each_uF: 22
        dielectric: ceramic
        tolerance_minus_pct: 10
        dc_bias_derating_pct: 10
        temperature_derating_pct: 15
        lifecycle_derating_pct: 0
        basis: engineering_bound
        evidence: characterized voltage-bias curve plus conservative bound
fault_envelopes:
  - name: shared output bank
    normal_continuous_A: 6
    service_peak_A: 7.5
    service_peak_max_ms: 10
    downstream_limits:
      - name: three output switches
        count: 3
        simultaneous_count: 3
        worst_high_each_A: 2.849
        programmer_refs: [R16, R18, R20]
        evidence: fixture worst-high current-limit proof
    upstream:
      continuous_rating_A: 8
      peak_rating_A: 10
      evidence: fixture converter ratings
      overload_qualification_max_ms: 50
      overload_qualification_evidence: fixture bounded transient rating
    aggregate_breaker:
      programmer_ref: R26
      threshold_model:
        equation: inverse_resistance_with_offset
        coefficient_worst_low_A_ohm: 1275
        coefficient_worst_high_A_ohm: 1665
        current_offset_A: 0.11
        programmer_tcr_ppm_per_C: 25
        programmer_temperature_excursion_C: 100
      expected_threshold_worst_low_A: 6.160253
      expected_threshold_worst_high_A: 8.066419
      threshold_calculation_tolerance_A: 0.000001
      minimum_normal_margin_A: 0.1
      minimum_fault_coordination_margin_A: 0.1
      response: latch_off
      threshold_evidence: fixture current-limit formula and corners
      reset_evidence: fixture hard power-cycle reset path
      timer:
        capacitor_ref: C29
        capacitance_nominal_nF: 47
        tolerance_pct: 5
        temperature_minus_pct: 0.3
        temperature_plus_pct: 0.3
        dc_bias_minus_pct: 0
        aging_minus_pct: 0
        comparator_delta_min_V: 0.7
        comparator_delta_max_V: 1.3
        discharge_current_min_uA: 1.4
        discharge_current_max_uA: 2.8
        evidence: fixture timer electrical-characteristic corners
        startup:
          capacitor_ref: C30
          capacitance_nominal_nF: 3.3
          tolerance_pct: 2
          temperature_minus_pct: 0.3
          temperature_plus_pct: 0.3
          dc_bias_minus_pct: 0
          aging_minus_pct: 0
          vin_min_V: 5.014892
          gate_overdrive_V: 3.6
          dvdt_current_max_uA: 6.33
          itimer_divisor: 53000
          evidence: fixture startup relation and dVdt-current corner
rails:
  - &port
    name: P1
    vin_min: 12
    vin_max: 24
    vout_min: 5.17
    vout_max: 5.23
    iout_max_A: 3
    converter: BUCK
    external_output: true
    claim_id: ports
    load_uv_threshold: 4.75
    ir_budget_mohm: 100
    ir_budget_components_mohm:
      protection_switch: {value: 10, basis: maximum, evidence: DS max}
      pcb_copper_vias_joints: {value: 10, basis: budgeted_max, evidence: extraction}
      mated_power_contacts: {value: 80, basis: qualified_max, evidence: connector qualification}
  - <<: *port
    name: P2
  - name: LOGIC
    vin_min: 12
    vin_max: 24
    vout_min: 3.27
    vout_max: 3.33
    iout_max_A: 0.1
    converter: LDO
    external_output: false
"""

INVARIANTS = """invariants:
  - {assert: part_value, part: R16, equals: 43.2k, tolerance_pct: 0.1}
  - {assert: part_value, part: R18, equals: 43.2k, tolerance_pct: 0.1}
  - {assert: part_value, part: R20, equals: 43.2k, tolerance_pct: 0.1}
  - {assert: part_value, part: R26, equals: 210, tolerance_pct: 0.1}
  - {assert: part_value, part: C29, equals: 47nF, tolerance_pct: 5}
  - {assert: part_value, part: C30, equals: 3.3nF, tolerance_pct: 2}
"""

STAGES = """schema: 2
stages:
  - name: buck-a
    controller_ref: U1
    controller_part: CTRL
    switching_frequency_hz: 250000
    gate_drive_voltage_V: 7.4
    controller_current_limit_min_mA: 40
    controller_bias_current_max_mA: 5
    current_margin_pct: 20
    bias_source: internal_linear
    vin_max_V: 24
    controller_theta_ja_C_per_W: 40
    ambient_max_C: 60
    junction_max_C: 150
    temperature_margin_C: 20
    current_limit:
      output_current_max_A: 3
      vin_max_V: 24
      vout_V: 5.2
      inductor_each_uH_nominal: 10
      inductor_tolerance_pct: 20
      parallel_inductor_count: 1
      sense_resistor_each_mohm_nominal: 5
      sense_resistor_tolerance_pct: 1
      parallel_sense_resistor_count: 1
      threshold_nominal_mV: 50
      threshold_min_ratio: 0.9
      threshold_max_ratio: 1.1
      required_peak_margin_pct: 10
      sense_ripple_min_mV: 10
      peak_current_path_rating_A_min: 20
      peak_current_path_margin_pct: 10
      evidence: fixture bounded threshold, shunt, inductor and path ratings
    switches:
      - {refs: QH, part: NFET60, qg_nC: 20, qg_basis: maximum,
         qg_test_voltage_V: 10, evidence: datasheet table row}
      - {refs: QL, part: NFET60, qg_nC: 15, qg_basis: maximum,
         qg_test_voltage_V: 10, evidence: datasheet table row}
"""

SURGE = """schema: 1
paths:
  - name: input
    source_operating_max_V: 24
    source_tolerance_included: true
    source_boundary_evidence: commissioned absolute input limit
    voltage_margin_pct: 2
    tvs: {part: TVS24, standoff_V: 24, clamp_max_V: 38,
          waveform_duration_ms: 1, waveform: 10/1000 us,
          evidence: exact datasheet row}
    exposed:
      - ref: U4
        part: LOAD
        recommended_max_V: 32
        absolute_max_V: 40
        absolute_max_duration_ms: 400
        transient_qualification: {grade: cited, max_V: 39,
          max_duration_ms: 1, evidence: source transient specification}
      - ref: Q1
        part: FET
        recommended_max_V: 60
        absolute_max_V: 60
    gate_biases:
      - ref: Q1
        polarity: p_channel_source_upper_gate_lower_ground
        upper_resistors:
          - {ref: R1, ohm: 100000, tolerance_pct: 1}
          - {ref: R2, ohm: 100000, tolerance_pct: 1}
        lower_resistor: {ref: R3, ohm: 100000, tolerance_pct: 1}
        gate_leakage_abs_uA: 10
        drive_source_min_V: 12
        required_vgs_magnitude_min_V: 4.5
        transient_source_max_V: 38.76
        absolute_vgs_max_V: 60
        evidence: full leakage and resistor-tolerance gate-divider proof
"""


def project(req=REQ, power=POWER, stages=STAGES, surge=SURGE):
    d = tmpdir("early_design_")
    rules = d / "03_src" / "rules"
    rules.mkdir(parents=True)
    for name in ("CTRL", "NFET60", "TVS24", "LOAD", "FET", "CAP_CER",
                 "FIXED_LIMIT"):
        pd = d / "02_parts" / name
        pd.mkdir(parents=True)
        (pd / "part.yaml").write_text(f"mpn: {name}\ntype: fixture\n")
    (rules / "requirements.yaml").write_text(req)
    (rules / "power_tree.yaml").write_text(power)
    (rules / "power_stages.yaml").write_text(stages)
    (rules / "protection_paths.yaml").write_text(surge)
    (rules / "electrical_invariants.yaml").write_text(INVARIANTS)
    return d


@test("EARLY-DESIGN passes a fully bounded external-power design")
def t_clean():
    r = must_pass(run([sys.executable, ED, project()]), "clean early design")
    contains(r.out, "EARLY-DESIGN PASS", "clean verdict")
    for gate in ("D-SPEC/E-PATH", "E-SWDRV", "E-SURGE", "E-CAP", "E-FAULT"):
        contains(r.out, gate, "clean evidence")


@test("E-PATH accepts one qualified complete interconnect at the load plane")
def t_complete_interconnect():
    req = (REQ
           .replace("measurement_plane: mated_test_plug",
                    "measurement_plane: load")
           .replace("mated_power_contacts]",
                    "complete_type_c_interconnect]")
           .replace("excluded_elements: [cable, appliance]",
                    "excluded_elements: []"))
    power = POWER.replace(
        "mated_power_contacts: {value: 80, basis: qualified_max, evidence: connector qualification}",
        "complete_type_c_interconnect: {value: 80, basis: qualified_max, evidence: hot four-wire endpoints cover both mated pairs and cable}")
    r = must_pass(run([sys.executable, ED, project(req=req, power=power),
                       "--requirements"]), "complete interconnect boundary")
    contains(r.out, "at load", "complete interconnect evidence")


@test("E-PATH rejects overlapping complete and decomposed load boundaries",
      kind="known_bad")
def t_overlapping_interconnect():
    req = (REQ
           .replace("measurement_plane: mated_test_plug",
                    "measurement_plane: load")
           .replace("mated_power_contacts]",
                    "mated_power_contacts, cable, complete_type_c_interconnect]")
           .replace("excluded_elements: [cable, appliance]",
                    "excluded_elements: []"))
    power = POWER.replace(
        "      mated_power_contacts: {value: 80, basis: qualified_max, evidence: connector qualification}\n",
        "      mated_power_contacts: {value: 30, basis: qualified_max, evidence: connector qualification}\n"
        "      cable: {value: 20, basis: qualified_max, evidence: cable qualification}\n"
        "      complete_type_c_interconnect: {value: 30, basis: qualified_max, evidence: overlapping complete path}\n")
    must_fail(run([sys.executable, ED, project(req=req, power=power),
                   "--requirements"]), "overlapping interconnect boundary",
              "choose one non-overlapping measurement boundary")


@test("D-SPEC rejects a power claim with no measurement plane", kind="known_bad")
def t_missing_plane():
    p = project(req=REQ.replace("    measurement_plane: mated_test_plug\n", ""))
    must_fail(run([sys.executable, ED, p, "--requirements"]),
              "missing measurement plane", "measurement_plane")


@test("E-PATH rejects a claimed path that omits mated contacts", kind="known_bad")
def t_missing_path_element():
    bad = POWER.replace(
        "      mated_power_contacts: {value: 80, basis: qualified_max, evidence: connector qualification}\n",
        "      regulator_misc: {value: 80, basis: budgeted_max, evidence: typed budget}\n")
    must_fail(run([sys.executable, ED, project(power=bad), "--requirements"]),
              "incomplete output path", "mated_power_contacts")


@test("D-SPEC rejects prose-only boundaries without structured included and "
      "excluded elements", kind="known_bad")
def t_unstructured_boundary():
    bad = REQ.replace(
        "    included_elements: [protection_switch, pcb_copper_vias_joints, mated_power_contacts]\n",
        "")
    must_fail(run([sys.executable, ED, project(req=bad), "--requirements"]),
              "prose-only boundary", "included_elements")


@test("E-PATH rejects bare resistance scalars without worst-case evidence",
      kind="known_bad")
def t_bare_ir_scalar():
    bad = POWER.replace(
        "protection_switch: {value: 10, basis: maximum, evidence: DS max}",
        "protection_switch: 10")
    must_fail(run([sys.executable, ED, project(power=bad), "--requirements"]),
              "bare path scalar", "bare number")


@test("E-PATH rejects an externally exposed rail that has no claim",
      kind="known_bad")
def t_unclaimed_external():
    bad = POWER.replace("    external_output: false\n", "    external_output: true\n")
    must_fail(run([sys.executable, ED, project(power=bad), "--requirements"]),
              "unclaimed external rail", "has no D-SPEC power claim")


@test("E-SWDRV rejects typical-only MOSFET gate charge", kind="known_bad")
def t_typical_qg():
    bad = STAGES.replace("qg_basis: maximum", "qg_basis: typical", 1)
    must_fail(run([sys.executable, ED, project(stages=bad), "--switching"]),
              "typical gate charge", "typical values cannot prove")


@test("E-SWDRV rejects a component identity that does not resolve to the part "
      "dossiers", kind="known_bad")
def t_unknown_switch_part():
    bad = STAGES.replace("part: NFET60", "part: INVENTED_FET", 1)
    must_fail(run([sys.executable, ED, project(stages=bad), "--switching"]),
              "invented switch part", "does not resolve to 02_parts")


@test("E-SWDRV rejects gate plus bias current above the controller limit",
      kind="known_bad")
def t_gate_current():
    bad = STAGES.replace("controller_current_limit_min_mA: 40",
                         "controller_current_limit_min_mA: 15")
    must_fail(run([sys.executable, ED, project(stages=bad), "--switching"]),
              "overloaded gate driver", "exceeds 15")


@test("E-SWDRV schema 2 rejects a missing peak-current-limit proof",
      kind="known_bad")
def t_missing_current_limit():
    start = STAGES.index("    current_limit:\n")
    end = STAGES.index("    switches:\n", start)
    bad = STAGES[:start] + STAGES[end:]
    must_fail(run([sys.executable, ED, project(stages=bad), "--switching"]),
              "missing current-limit proof", "cannot be deferred")


@test("E-SWDRV rejects a current-limit tier below load plus ripple and margin",
      kind="known_bad")
def t_low_peak_current_limit():
    bad = STAGES.replace("threshold_nominal_mV: 50",
                         "threshold_nominal_mV: 20")
    must_fail(run([sys.executable, ED, project(stages=bad), "--switching"]),
              "under-rated peak current limit", "worst-low peak is below")


@test("E-SWDRV rejects a worst-high current limit above the power-path rating",
      kind="known_bad")
def t_high_peak_current_limit():
    bad = STAGES.replace("peak_current_path_rating_A_min: 20",
                         "peak_current_path_rating_A_min: 12")
    must_fail(run([sys.executable, ED, project(stages=bad), "--switching"]),
              "current limit above path rating", "worst-high peak exceeds")


@test("E-SURGE rejects a clamp above an exposed absolute maximum",
      kind="known_bad")
def t_clamp_over_abs():
    bad = SURGE.replace("absolute_max_V: 40", "absolute_max_V: 38")
    must_fail(run([sys.executable, ED, project(surge=bad), "--surge"]),
              "clamp over absolute maximum", "exceeds absolute maximum")


@test("E-SURGE rejects an owed transient qualification", kind="known_bad")
def t_owed_transient():
    bad = SURGE.replace("grade: cited", "grade: owed")
    must_fail(run([sys.executable, ED, project(surge=bad), "--surge"]),
              "owed transient qualification", "not measured/cited")


@test("E-SURGE rejects a gate-divider proof that ignores worst-case leakage",
      kind="known_bad")
def t_gate_bias_leakage():
    bad = SURGE.replace("gate_leakage_abs_uA: 10",
                        "gate_leakage_abs_uA: 100")
    must_fail(run([sys.executable, ED, project(surge=bad), "--surge"]),
              "under-driven gate corner", "worst-low |VGS|")


def prototype_esd_project(mutate=None):
    """CAR-F10: typical TLP clamp was misrepresented as a guaranteed 8/20 bound."""
    doc = yaml.safe_load(SURGE)
    doc["schema"] = 2
    doc["paths"][0]["qualification_mode"] = "bounded_transient"
    doc["paths"].append({
        "name": "audio", "qualification_mode": "unqualified_prototype_esd",
        "source_operating_min_V": 1.45, "source_operating_max_V": 3.5,
        "source_tolerance_included": True, "source_boundary_evidence": "fixture normal audio envelope",
        "tvs": {"part": "TVS24", "standoff_V": 5.5, "recommended_min_V": 0,
                "recommended_max_V": 5.5, "iec_contact_kV": 25, "iec_air_kV": 30,
                "evidence": "component IEC table; typical TLP is not a guaranteed clamp"},
        "exposed": [{"refs": ["U1", "U2"], "part": "TVS24", "recommended_min_V": 0,
                     "recommended_max_V": 5.5, "evidence": "normal VIO table"}],
        "qualification": {"status": "UNQUALIFIED", "board_survival_claim": False,
                          "installation_restriction": "laboratory prototype only, no outdoor installation",
                          "authorization": "prototype.md", "test_plan": "test-plan.md"},
    })
    if mutate:
        mutate(doc)
    d = project(surge=yaml.safe_dump(doc))
    (d / "prototype.md").write_text("Prototype design authorized; no board transient survival claim.\n")
    (d / "test-plan.md").write_text("Qualify actual connector-to-load ESD before installation.\n")
    return d


@test("E-SURGE prototype mode separates normal/component selection from unqualified board survival")
def t_prototype_esd_selection():
    r = must_pass(run([sys.executable, ED, prototype_esd_project(), "--surge"]), "honest prototype selection")
    contains(r.out, "2 exposed parts / 2 suppressors", "nonzero denominator")
    contains(r.out, "UNQUALIFIED E-SURGE audio", "board survival remains open")
    check("PASS UNQUALIFIED" not in r.out, "unqualified survival is never prefixed PASS")
    contains(r.out, "input/Q1 gate", "genuine input gate-stress proof retained")


@test("E-SURGE prototype mode rejects invented maxima and survival claims", kind="known_bad")
def t_prototype_esd_claim_laundering():
    edits = [
        lambda p: p["tvs"].update(clamp_max_V=12.4),
        lambda p: p["exposed"][0].update(absolute_max_V=14),
        lambda p: p["qualification"].update(board_survival_claim=True),
        lambda p: p["qualification"].update(status="PASS"),
        lambda p: p["qualification"].update(test_plan="../outside.md"),
        lambda p: p.update(source_operating_max_V=5.6),
        lambda p: p.update(source_operating_min_V=-0.1),
        lambda p: p["tvs"].update(iec_air_kV=0),
    ]
    for edit in edits:
        d = prototype_esd_project(lambda doc: edit(doc["paths"][1]))
        must_fail(run([sys.executable, ED, d, "--surge"]), "invented/unqualified survival", "E-SURGE")


@test("E-SURGE prototype mode rejects vacuous populations and ambiguous qualification modes", kind="known_bad")
def t_prototype_esd_mode_and_population():
    edits = [
        lambda p: p.pop("qualification_mode"),
        lambda p: p.update(qualification_mode="maybe"),
        lambda p: p.update(qualification_mode=[]),
        lambda p: p.update(qualification_mode="bounded_transient"),
        lambda p: p.update(exposed=[]),
        lambda p: p["exposed"][0].update(refs=[]),
        lambda p: p["exposed"][0].update(refs=["U1-U8"]),
        lambda p: p["exposed"][0].update(refs=["U1", "U1"]),
        lambda p: p["exposed"][0].update(part="LOAD"),
        lambda p: p.pop("qualification"),
    ]
    for edit in edits:
        d = prototype_esd_project(lambda doc: edit(doc["paths"][1]))
        must_fail(run([sys.executable, ED, d, "--surge"]), "mode/population fail closed", "E-SURGE")


@test("E-SURGE prototype admission cannot weaken a bounded input-surge path", kind="known_bad")
def t_prototype_esd_preserves_input_survival():
    d = prototype_esd_project(lambda doc: doc["paths"][0]["exposed"][0].update(absolute_max_V=38))
    must_fail(run([sys.executable, ED, d, "--surge"]), "bounded input still fails", "exceeds absolute maximum")
    d = prototype_esd_project(lambda doc: doc.update(schema=1))
    must_fail(run([sys.executable, ED, d, "--surge"]), "legacy schema cannot reinterpret modes", "requires schema 2")


@test("E-CAP applies tolerance, DC-bias, temperature and lifecycle derating")
def t_effective_capacitance_pass():
    r = must_pass(run([sys.executable, ED, project(), "--capacitance"]),
                  "effective-capacitance proof")
    contains(r.out, "30.294/30 uF", "prints the fully derated value")


@test("E-CAP rejects a nameplate value that falls below the effective minimum",
      kind="known_bad")
def t_effective_capacitance_shortfall():
    bad = POWER.replace("dc_bias_derating_pct: 10",
                        "dc_bias_derating_pct: 35")
    must_fail(run([sys.executable, ED, project(power=bad), "--capacitance"]),
              "DC-bias capacitance shortfall", "is below 30 uF required")


@test("E-CAP refuses an omitted derating term", kind="known_bad")
def t_effective_capacitance_missing_derating():
    bad = POWER.replace("        lifecycle_derating_pct: 0\n", "")
    must_fail(run([sys.executable, ED, project(power=bad), "--capacitance"]),
              "missing lifecycle derating", "lifecycle_derating_pct")


@test("E-CAP accepts an explicit evidenced no-requirements decision")
def t_effective_capacitance_explicit_not_applicable():
    start = POWER.index("effective_capacitance_banks:\n")
    end = POWER.index("fault_envelopes:\n", start)
    changed = (POWER[:start] +
               "no_effective_capacitance_requirements: no device in this fixture specifies an effective-capacitance minimum\n" +
               POWER[end:])
    r = must_pass(run([sys.executable, ED, project(power=changed)]),
                  "explicit E-CAP applicability decision")
    contains(r.out, "E-CAP not applicable", "prints the applicability result")


@test("E-CAP refuses contradictory requirements and N-A declarations",
      kind="known_bad")
def t_effective_capacitance_conflicting_applicability():
    changed = POWER.replace(
        "effective_capacitance_banks:\n",
        "no_effective_capacitance_requirements: not applicable\n"
        "effective_capacitance_banks:\n")
    must_fail(run([sys.executable, ED, project(power=changed), "--capacitance"]),
              "contradictory E-CAP applicability", "mutually exclusive")


@test("E-FAULT closes aggregate current, breaker, timer and startup corners")
def t_fault_envelope_pass():
    r = must_pass(run([sys.executable, ED, project(), "--fault-envelope"]),
                  "aggregate fault envelope")
    contains(r.out, "normal/peak/fault=6/7.5/8.547 A", "current envelope")
    contains(r.out, "timer=11.129", "worst-low timer")
    contains(r.out, "startup allows 82.795 nF", "startup relationship")


@test("E-FAULT applies an explicit downstream simultaneity rule")
def t_fault_mutually_exclusive_limits():
    changed = POWER.replace("        simultaneous_count: 3",
                            "        simultaneous_count: 1")
    r = must_pass(run([sys.executable, ED, project(power=changed),
                       "--fault-envelope"]),
                  "mutually exclusive downstream limits")
    contains(r.out, "normal/peak/fault=6/7.5/2.849 A", "simultaneity sum")


@test("E-FAULT accepts a dossier-backed fixed downstream load without a fake programmer")
def t_fault_fixed_limit_evidence_ref():
    changed = POWER.replace(
        "        evidence: fixture worst-high current-limit proof\n",
        "        evidence: fixture worst-high current-limit proof\n"
        "      - name: fixed converter load\n"
        "        count: 1\n"
        "        simultaneous_count: 1\n"
        "        worst_high_each_A: 0.1\n"
        "        evidence_refs: [FIXED_LIMIT]\n"
        "        evidence: fixture fixed-limit manufacturer proof\n")
    r = must_pass(run([sys.executable, ED, project(power=changed),
                       "--fault-envelope"]), "fixed downstream evidence")
    contains(r.out, "normal/peak/fault=6/7.5/8.647 A",
             "fixed load enters aggregate")


@test("E-FAULT supports slew-limited output-bank startup models")
def t_fault_slew_limited_startup():
    old = """          vin_min_V: 5.014892
          gate_overdrive_V: 3.6
          dvdt_current_max_uA: 6.33
          itimer_divisor: 53000
          evidence: fixture startup relation and dVdt-current corner
"""
    new = """          model: slew_limited_output_bank
          slew_coefficient_pF_V_per_ms: 2000
          output_capacitance_max_uF: 100
          expected_inrush_max_A: 0.062029
          calculation_tolerance_A: 0.000001
          evidence: fixture slew and output-bank proof
"""
    r = must_pass(run([sys.executable, ED, project(power=POWER.replace(old, new)),
                       "--fault-envelope"]), "slew-limited startup")
    contains(r.out, "startup=C30 gives 0.620 V/ms, 0.062 A",
             "derived startup inrush")


@test("E-FAULT catches the escaped X7R timer temperature corner",
      kind="known_bad")
def t_fault_timer_temperature_shortfall():
    bad = POWER.replace("        tolerance_pct: 5\n        temperature_minus_pct: 0.3",
                        "        tolerance_pct: 10\n        temperature_minus_pct: 15", 1)
    p = project(power=bad)
    inv = p / "03_src/rules/electrical_invariants.yaml"
    inv.write_text(INVARIANTS.replace(
        "part: C29, equals: 47nF, tolerance_pct: 5",
        "part: C29, equals: 47nF, tolerance_pct: 10"))
    must_fail(run([sys.executable, ED, p, "--fault-envelope"]),
              "X7R timer corner", "8.989 ms is below service peak duration 10 ms")


@test("E-FAULT derives threshold corners from the exact programmer and offset")
def t_fault_threshold_derivation():
    r = must_pass(run([sys.executable, ED, project(), "--fault-envelope"]),
                  "derived breaker threshold")
    contains(r.out, "breaker=6.16025", "derived low threshold")
    contains(r.out, "..8.06642 A", "derived high threshold")


@test("E-FAULT rejects a stale asserted threshold after formula correction",
      kind="known_bad")
def t_fault_stale_expected_threshold():
    bad = POWER.replace("expected_threshold_worst_high_A: 8.066419",
                        "expected_threshold_worst_high_A: 7.9255")
    must_fail(run([sys.executable, ED, project(power=bad), "--fault-envelope"]),
              "stale copied threshold", "does not match derived")


@test("E-FAULT refuses an omitted affine current offset", kind="known_bad")
def t_fault_missing_threshold_offset():
    bad = POWER.replace("        current_offset_A: 0.11\n", "")
    must_fail(run([sys.executable, ED, project(power=bad), "--fault-envelope"]),
              "missing datasheet equation term", "current_offset_A")


@test("E-FAULT enforces explicit margin above normal service",
      kind="known_bad")
def t_fault_normal_coordination_margin():
    bad = POWER.replace("    normal_continuous_A: 6",
                        "    normal_continuous_A: 6.1")
    must_fail(run([sys.executable, ED, project(power=bad), "--fault-envelope"]),
              "insufficient normal margin", "above normal load")


@test("E-FAULT enforces explicit margin below the downstream fault sum",
      kind="known_bad")
def t_fault_downstream_coordination_margin():
    bad = POWER.replace("        worst_high_each_A: 2.849",
                        "        worst_high_each_A: 2.7")
    must_fail(run([sys.executable, ED, project(power=bad), "--fault-envelope"]),
              "insufficient fault coordination margin",
              "above the breaker worst-high threshold")


@test("E-FAULT rejects a breaker threshold above upstream peak rating",
      kind="known_bad")
def t_fault_threshold_over_upstream():
    bad = POWER.replace("coefficient_worst_high_A_ohm: 1665",
                        "coefficient_worst_high_A_ohm: 2100").replace(
                            "expected_threshold_worst_high_A: 8.066419",
                            "expected_threshold_worst_high_A: 10.145123")
    must_fail(run([sys.executable, ED, project(power=bad), "--fault-envelope"]),
              "unsafe breaker threshold", "exceeds upstream peak rating")


@test("E-FAULT bounds time above the upstream continuous rating",
      kind="known_bad")
def t_fault_overload_window():
    bad = POWER.replace("overload_qualification_max_ms: 50",
                        "overload_qualification_max_ms: 40")
    must_fail(run([sys.executable, ED, project(power=bad), "--fault-envelope"]),
              "overlong upstream overload", "qualified overload window")


@test("E-FAULT rejects a timer capacitor too large for the startup ramp",
      kind="known_bad")
def t_fault_startup_relation():
    bad = POWER.replace("          capacitance_nominal_nF: 3.3",
                        "          capacitance_nominal_nF: 1.5")
    p = project(power=bad)
    inv = p / "03_src/rules/electrical_invariants.yaml"
    inv.write_text(INVARIANTS.replace("part: C30, equals: 3.3nF",
                                      "part: C30, equals: 1.5nF"))
    must_fail(run([sys.executable, ED, p, "--fault-envelope"]),
              "startup/timer incompatibility", "exceeds")


@test("E-FAULT refuses a missing interrupt timer", kind="known_bad")
def t_fault_missing_timer():
    start = POWER.index("      timer:\n")
    end = POWER.index("rails:\n", start)
    changed = POWER[:start] + POWER[end:]
    must_fail(run([sys.executable, ED, project(power=changed),
                   "--fault-envelope"]),
              "missing fault timer", "timer must be a mapping")


@test("E-FAULT accepts an explicit evidenced no-shared-upstream decision")
def t_fault_explicit_not_applicable():
    start = POWER.index("fault_envelopes:\n")
    end = POWER.index("rails:\n", start)
    changed = (POWER[:start] +
               "no_fault_envelope_requirements: all outputs have independent upstream sources and no shared constrained path\n" +
               POWER[end:])
    r = must_pass(run([sys.executable, ED, project(power=changed)]),
                  "explicit E-FAULT applicability decision")
    contains(r.out, "E-FAULT not applicable", "prints the applicability result")


@test("E-FAULT refuses contradictory envelope and N-A declarations",
      kind="known_bad")
def t_fault_conflicting_applicability():
    changed = POWER.replace(
        "fault_envelopes:\n",
        "no_fault_envelope_requirements: not applicable\n"
        "fault_envelopes:\n")
    must_fail(run([sys.executable, ED, project(power=changed),
                   "--fault-envelope"]),
              "contradictory E-FAULT applicability", "mutually exclusive")


PASSIVE_RAIL = """  - name: POD1
    stage: distribution
    vin_min: 11.2
    vin_max: 13.2
    vout_min: 10.8
    vout_max: 13.2
    iout_max_A: 0.1
    distribution:
      kind: passive_pptc
      series_devices: [1812L035-60MR]
      path_resistance_max_mohm: 1700
      hold_current_reference_A: 0.2
      hold_current_reference_temperature_C: 70
      operating_ambient_max_C: 70
      hold_current_reference_grade: manufacturer_reference
      hold_current_reference_locator: manufacturer table 1812L035/60 70 C column
      reverse_current_policy: downstream sources prohibited
"""

PASSIVE_FAULT = """passive_distribution_faults:
  - rail: POD1
    series_device: 1812L035-60MR
    prospective_current_min_A: 8
    prospective_current_max_A: 9
    prospective_current_evidence_grade: qualified_bound
    prospective_current_evidence_locator: fault-current extraction report section 4
    fault_current_withstand_A: 10
    fault_current_withstand_evidence_grade: guaranteed_rating
    fault_current_withstand_evidence_locator: manufacturer electrical table Imax
    ambient_min_C: 70
    ambient_max_C: 70
    maximum_trip_time_envelope:
      - current_A: 8
        time_max_s: 0.15
        temperature_C: 70
        evidence_grade: guaranteed_maximum
        evidence_locator: manufacturer maximum-time table exact row
    post_trip_leakage_max_A: 0.08
    post_trip_evidence_grade: guaranteed_maximum
    post_trip_evidence_locator: manufacturer hot-state leakage qualification
    protected_path_sustained_current_max_A: 0.1
    protected_path_sustained_current_evidence_grade: qualified_minimum
    protected_path_sustained_current_evidence_locator: cable connector copper load continuous qualification
    let_through_energy_max_J: 18
    protected_path_withstand_J: 20
    energy_withstand_evidence_grade: qualified_minimum
    energy_withstand_evidence_locator: cable connector copper load report section 7
"""


def with_passive_fault(power=POWER, qualification=PASSIVE_FAULT):
    return power.replace("fault_envelopes:\n", qualification +
                         "fault_envelopes:\n").replace(
                             "  - name: LOGIC\n", PASSIVE_RAIL +
                             "  - name: LOGIC\n")


@test("E-FAULT separately qualifies a passive distribution fault envelope")
def t_passive_fault_envelope_pass():
    r = must_pass(run([sys.executable, ED,
                       project(power=with_passive_fault()),
                       "--fault-envelope"]), "passive fault qualification")
    contains(r.out, "E-FAULT passive POD1", "passive fault verdict")


@test("passive normal metadata cannot bypass missing fault qualification",
      kind="known_bad")
def t_passive_missing_fault_qualification_fails():
    bad = with_passive_fault(qualification="")
    must_fail(run([sys.executable, ED, project(power=bad),
                   "--fault-envelope"]), "missing passive fault envelope",
              "normal E-TOPO hold-current PASS does not qualify fault clearing")


@test("passive PPTC N-A aggregate declaration still needs branch fault proof",
      kind="known_bad")
def t_passive_fault_cannot_hide_behind_aggregate_na():
    start = POWER.index("fault_envelopes:\n")
    end = POWER.index("rails:\n", start)
    aggregate_na = (POWER[:start] +
        "no_fault_envelope_requirements: no shared constrained path\n" +
        POWER[end:]).replace("  - name: LOGIC\n", PASSIVE_RAIL +
                            "  - name: LOGIC\n")
    must_fail(run([sys.executable, ED, project(power=aggregate_na),
                   "--fault-envelope"]), "passive fault hidden by N-A",
              "passive PPTC rails require")


@test("qualified passive branches cannot bypass aggregate coordination with N-A",
      kind="known_bad")
def t_passive_fault_qualified_but_aggregate_na_fails():
    start = POWER.index("fault_envelopes:\n")
    end = POWER.index("rails:\n", start)
    aggregate_na = (POWER[:start] + PASSIVE_FAULT +
        "no_fault_envelope_requirements: no shared constrained path\n" +
        POWER[end:]).replace("  - name: LOGIC\n", PASSIVE_RAIL +
                            "  - name: LOGIC\n")
    must_fail(run([sys.executable, ED, project(power=aggregate_na),
                   "--fault-envelope"]), "passive aggregate N-A bypass",
              "is forbidden when passive_pptc rails exist")


@test("passive trip coverage rejects current interpolation", kind="known_bad")
def t_passive_fault_rejects_current_interpolation():
    bad_fault = PASSIVE_FAULT.replace("      - current_A: 8",
                                      "      - current_A: 0.05")
    must_fail(run([sys.executable, ED,
                   project(power=with_passive_fault(qualification=bad_fault)),
                   "--fault-envelope"]), "passive trip current interpolation",
              "interpolation is not permitted")


@test("passive trip coverage rejects hot-point interpolation to cold corner",
      kind="known_bad")
def t_passive_fault_rejects_temperature_interpolation():
    bad_fault = PASSIVE_FAULT.replace("    ambient_min_C: 70",
                                      "    ambient_min_C: -40")
    must_fail(run([sys.executable, ED,
                   project(power=with_passive_fault(qualification=bad_fault)),
                   "--fault-envelope"]), "passive trip temperature interpolation",
              "interpolation is not permitted")


@test("passive trip evidence rejects typical curves", kind="known_bad")
def t_passive_fault_rejects_typical_trip_data():
    bad_fault = PASSIVE_FAULT.replace(
        "        evidence_grade: guaranteed_maximum",
        "        evidence_grade: typical_average")
    must_fail(run([sys.executable, ED,
                   project(power=with_passive_fault(qualification=bad_fault)),
                   "--fault-envelope"]), "typical PPTC curve misuse",
              "typical or average trip data cannot prove E-FAULT")


@test("passive post-trip evidence rejects typical dissipation", kind="known_bad")
def t_passive_fault_rejects_typical_post_trip_data():
    bad_fault = PASSIVE_FAULT.replace(
        "    post_trip_evidence_grade: guaranteed_maximum",
        "    post_trip_evidence_grade: typical_dissipation")
    must_fail(run([sys.executable, ED,
                   project(power=with_passive_fault(qualification=bad_fault)),
                   "--fault-envelope"]), "typical PPTC post-trip misuse",
              "post_trip_evidence_grade must be guaranteed_maximum")


@test("passive fault rejects missing protected-path sustained-current bound",
      kind="known_bad")
def t_passive_fault_requires_sustained_current_bound():
    bad_fault = PASSIVE_FAULT.replace(
        "    protected_path_sustained_current_max_A: 0.1\n", "")
    must_fail(run([sys.executable, ED,
                   project(power=with_passive_fault(qualification=bad_fault)),
                   "--fault-envelope"]), "missing sustained-current bound",
              "protected_path_sustained_current_max_A must be numeric")


@test("passive fault rejects post-trip leakage above path sustained current",
      kind="known_bad")
def t_passive_fault_rejects_excessive_sustained_leakage():
    bad_fault = PASSIVE_FAULT.replace(
        "    protected_path_sustained_current_max_A: 0.1",
        "    protected_path_sustained_current_max_A: 0.05")
    must_fail(run([sys.executable, ED,
                   project(power=with_passive_fault(qualification=bad_fault)),
                   "--fault-envelope"]), "excessive post-trip leakage",
              "post-trip leakage 0.08 A exceeds protected-path "
              "sustained-current maximum 0.05 A")


if __name__ == "__main__":
    sys.exit(main())
