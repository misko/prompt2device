# Spoke interface review snapshot

Informational engineering snapshot; executable power bounds belong to
`03_src/rules/power_tree.yaml`. This is not an independently graded rule schema.

```yaml
schema: 1
candidate: TPS26625DRCR_per_spoke
status: SOURCE_CANDIDATE_ONLY_NOT_ELECTRICALLY_ADMITTED

preserved_external_interface:
  connectors: [J1, J2, J3, J4, J5, J6, J7, J8]
  connector_mpn: 615008160221
  pin_map:
    1: 12V_PODx
    2: GND
    3: 12V_PODx
    4: AUDIO_Nx
    5: AUDIO_Px
    6: GND
    7: 12V_PODx
    8: GND
    9: CHASSIS
    10: CHASSIS
  nominal_load_each_A: 0.10
  simultaneous_spokes: 8
  connector_plane_minimum_V: 10.8
  admitted_input_range_V: [11.4, 13.2]
  audio_and_chassis_behavior: unchanged_from_retained_analog_source

per_spoke_internal_interface:
  input: 12V_PROTECTED
  output: 12V_PODx
  ground: GND
  local_return: SPOKE_RTNx
  control_nets: [SPOKE_UVLOx, SPOKE_ILIMx, SPOKE_DVDTx]
  device: TPS26625DRCR
  pin_connections:
    IN_1: 12V_PROTECTED
    UVLO_2: SPOKE_UVLOx_via_1M_to_IN
    OVP_3: SPOKE_RTNx
    SHDN_4: 12V_PROTECTED
    RTN_5: SPOKE_RTNx
    GND_6: GND
    ILIM_7: SPOKE_ILIMx_via_44k2_to_RTN
    dVdT_8: SPOKE_DVDTx_via_10nF_to_RTN
    FLT_9: unconnected_per_datasheet_when_unused
    OUT_10: 12V_PODx
    PowerPAD_11: SPOKE_RTNx_with_separate_pin5_connection
  local_bypass:
    input: CC0805KRX7R9BB104_100nF_50V_X7R_to_GND
    output: CC0805KRX7R9BB104_100nF_50V_X7R_to_GND

qualified_normal_bounds:
  device_ron_max_ohm_minus40_to125C: 0.800
  device_drop_max_mV_at_0p10A: 80
  inherited_load_allocation_A: 2.12
  statement: >-
    This bounds only the TPS26625 series-device drop. Connector, harness,
    copper, joint, upstream source-stage and thermal-realization bounds are
    required before the 10.8 V connector-plane floor can be admitted.

engineering_screen_only:
  current_limit_A: [0.145, 0.159]
  condition: VIN=24V, VIN-VOUT=1V, RILIM=44.2kohm, electrical-table temperature range
  warning: This range is not a guaranteed 12V hard-short current bound.
  device_quiescent_current_max_uA_each_at_24V_table_condition: 482
  eight_device_quiescent_current_screen_mA: 3.856
  source_side_normal_current_screen_A: 2.123856
  iq_warning: The 482uA maximum uses the 24V global table condition and is not a guaranteed 11.4-13.2V bound.

required_source_contract:
  status: OPEN
  source_identity: COMPLIANT_ISOLATED_SUPPLY_OR_EXACT_MPN
  connector_input_operating_envelope:
    voltage_V: [11.4, 13.2]
    continuous_current_min_A: 2.185
    condition: At J_PWR after source cable loss across the declared 70C operating envelope.
  inherited_continuous_normal_load_A: 2.12
  candidate_continuous_delivery_screen_A: 2.123856
  one_fault_arithmetic_screen_A: 2.185
  one_fault_unrounded_screen_A: 2.182856
  one_fault_screen_basis: 1.32A digital plus seven 0.10A healthy spokes plus 0.159A table-conditioned fault output current plus 3.856mA maximum eFuse IQ; rounded upward
  must_bound:
    - eFuse supply current across 11.4-13.2V, tolerance and temperature
    - prospective short-circuit current and cold source/harness impedance
    - current-limit and foldback or hiccup thresholds over tolerance and temperature
    - source output-capacitance discharge into a fault and recovery trajectory
    - minimum source voltage during eFuse fast-trip, regulation, thermal shutdown and retry
    - interaction with the input 2920L330/24DR PPTC at 70C and cold-start
  acceptance_rule: >-
    The source and upstream protection must keep seven healthy spokes and all
    required digital rails inside their voltage limits for the measured and
    bounded fault envelope. The 2.185 A screen is not an acceptance guarantee.

open_admission_flags:
  - Replace F_IN 2920L330/24DR with an input protection element whose guaranteed 70C continuous rating exceeds 2.185A with engineering margin and whose trip curve coordinates with a 0.159A spoke limiter; the present 2.25A reference hold leaves only 65mA against the rounded fault screen.
  - Qualify every simultaneous pod load and capacitance startup state with 10nF dVdT capacitors.
  - Prove exposed-pad copper, junction temperature and 70C ambient behavior for normal, overload, hard-short and retry operation.
  - Measure common-bus droop and source recovery for hot-short, powered-on short, retry and short removal.
  - Qualify externally powered pod and reverse-current states.
  - Obtain allocation and price evidence for TPS26625DRCR.
```
