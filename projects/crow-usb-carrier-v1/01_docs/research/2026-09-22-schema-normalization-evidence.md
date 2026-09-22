# Dossier schema normalization evidence — 2026-09-22

These verbatim YAML values were moved out of unconsumed dossier keys during source admission. They remain human engineering evidence; executable authority stays in the existing machine-read rules and canonical dossier fields.

## `0451004.MRL`

```yaml
engineering_bound:
  standard_continuous_derating_pct: 25
  temperature_factor_at_70C_screen: 0.95
  continuous_current_screen_A_at_70C: 2.85
  required_one_fault_current_A: 2.185
  margin_A: 0.665
  margin_pct: 30.4
  caveat: The 70C factor is conservatively read from the graphical manufacturer curve;
    it is an engineering screen, not a tabulated production minimum.
```

## `744373240047`

```yaml
series: WE-LHMI
qualification:
  aec_q200: Grade 1 marking shown on primary drawing
  moisture_sensitivity_level: 1
procurement:
  classification: current availability and pricing not qualified in this packet
  lcsc: C19270343
```

## `CC0805KRX7R9BB104`

```yaml
use: local TPS26625 IN and OUT high-frequency capacitors; no effective-capacitance
  or transient-clamp guarantee inferred
```

## `CL21A106KOCLRNC`

```yaml
voltage: 16V
tolerance: 10%
dielectric: X5R
source_url: https://product.samsungsem.com/mlcc/CL21A106KOCLRN.do
characteristics_note: Samsung exact-family typical design-reference curves are not
  guaranteed worst-case limits. DC retention is 35.9598% at the measured 5.11605V
  point above the 5.05V maximum. The separate adverse low-amplitude AC sample retains
  75.475%; multiplied combined typical retention is 27.14%.
design_curve_screen: Samsung typical DC retention at5.11605V is35.959775%; separate
  low-amplitude AC retention is75.4752%. Multiplication screens to about27.14%; use
  the more adverse25% combined engineering retention. Two10uF parts with0.90 tolerance,0.25
  DC/AC,0.85 temperature and0.90 lifecycle give3.4425uF versus3uF required. Separate
  typical curves and selected reserves are not guaranteed joint PVT/aging limits;
  input ripple/startup/transient qualification remains required.
```

## `CRCW0402680RFKED`

```yaml
technology: thick_film
ordering_code:
  family_and_size: CRCW0402 = D/CRCW 0402 thick-film chip resistor
  resistance: 680R = 680Ω (R is the decimal designator)
  tolerance: F = ±1%
  tcr: K = ±100 ppm/K
  packaging: ED = ET7, lead-free paper tape, 10,000 pieces, 180 mm reel
  termination: E.. = lead-free; product description defines e3 as pure-tin termination
    finish
role:
  refdes: R_XTAL_DRIVE
  circuit: XU316 24 MHz crystal network
  connection: series from XTAL_IN to XTAL_IN_R
  rationale: The exact 680Ω value and ±1% tolerance preserve the existing crystal-drive
    damping. This is a low-voltage AC series role with no DC 680Ω load; 0.063 W and
    50 V standard-mode ratings exceed the circuit requirement.
```

## `DMP6023LFG-13`

```yaml
native_pad_map:
  1: 1
  2: 2
  3: 3
  4: 4
  5: manufacturer-fused drain land for logical pins 5-8
```

## `GRM155R71H103KA88D`

```yaml
voltage: 50V
tolerance: 10%
dielectric: X7R
use: TPS389018 CT timing capacitor
```

## `RT0603BRD0744K2L`

```yaml
ordering_decode: B is 0.1 percent tolerance; D is 25 ppm/C TCR; 44K2 is 44.2 kohm;
  L is reel packaging.
```

## `SN74AUP3G34DCUR`

```yaml
supply: 0.8V_to_3.6V
input_tolerance: 3.6V_with_Ioff_partial_power_down
operating_temperature: -40C_to_85C
sourceability:
  ti_status: active
  digikey: 296-25595 series exact DCUR authorized listing
  mouser: exact DCUR listing not independently closed; DQE family variant stocked
    but not footprint-compatible
```

## `TPS26625DRCR`

```yaml
design_binding:
  rilim: RT0603BRD0744K2L
  rilim_nominal_ohm: 44200
  rilim_tolerance_pct: 0.1
  rilim_tcr_ppm_per_C: 25
  uvlo: 1M from IN to UVLO as required when UVLO is unused
  ovp: OVP tied to RTN; upstream rail owns the admitted overvoltage envelope
  shutdown: SHDN tied to IN; no control or floating state
  fault: FLT left unconnected because the pin-functions table directs this when unused
  dvdt: 10nF to RTN, provisional startup slew selection pending all pod load states
  rtn: dedicated local RTN island; never short RTN directly to GND
  powerpad: pin 11 tied to RTN plane, with a separate pin-5 RTN connection
evidence_limits:
- The 0.145/0.152/0.159A table row is characterized at 24V and VIN-VOUT=1V over the
  table temperature range. It is not claimed as a guaranteed 12V hard-short bound.
- The 482uA maximum supply-current entry also uses the electrical table's 24V global
  condition; its eight-device sum is a planning screen, not a guaranteed 11.4-13.2V
  bound.
- The 1.6A fast-trip threshold and 220ns response are typical behavior, not maximum
  transient guarantees.
- The 512ms timing is nominal and depends on operating mode, CdVdT, voltage drop and
  thermal shutdown. No bounded common-bus disturbance is claimed.
- Thermal shutdown time depends on exposed-pad copper and ambient. The candidate has
  no PCB or thermal proof.
- TI's application section is explicitly not a component specification; system fault
  containment needs source, harness and first-article evidence.
```

## `W25Q128JWSIQ`

```yaml
ordering_decode:
  W: 1.7V to 1.95V supply
  S: 8-pin SOIC 208mil
  I: industrial temperature grade
  Q: QE bit fixed at 1 in Status Register-2
boot_compatibility:
  controller_document: XMOS XU316/XU316-QF60B/XU316-QF128B Datasheet XM-014532-PC
    v2.0.0 section 9.1
  controller_document_sha256: a2ce2dc835df06793a4e1aa6c5d226c6a01c25c979a63b09a2b57059c17321cf
  protocol: 0xEB Quad I/O Read with three address bytes, one mode byte, then dummy
    clocks
  power_up: Device powers up in SPI mode; fixed-QE ordering option permits quad data
    pins without a status-register write.
  readiness: Winbond tVSL maximum is 20us; XU316 boot requires the device to be QSPI-access-ready
    within 300us.
  addressability: 128Mbit is 16MiB and fits the XU316 ROM's 24-bit boot address range
    starting at address zero.
  clock_alignment: XMOS XTC Tools15.3 explicitly specifies six post-address clocks.
    Winbond RevH consumes two mode clocks plus four dummy clocks before data; this
    resolves the older XU316 one-dummy-byte shorthand.
  clock_alignment_source: https://www.xmos.com/documentation/XM-014363-PC/html/tools-guide/tools-ref/libraries/libquadflash-included-devices/libquadflash-devices.html
package_geometry_mm:
  body_d_min: 5.18
  body_d_nom: 5.28
  body_d_max: 5.38
  body_e_min: 5.18
  body_e_nom: 5.28
  body_e_max: 5.38
  lead_span_h_min: 7.7
  lead_span_h_nom: 7.9
  lead_span_h_max: 8.1
  pitch: 1.27
  lead_width_min: 0.35
  lead_width_nom: 0.42
  lead_width_max: 0.48
footprint_check: KiCad Package_SO:SOIC-8_5.3x5.3mm_P1.27mm matches the Rev H nominal
  5.28mm square body and 1.27mm pitch; no native footprint change is required.
```

## `GRM21BR60J226ME39L`

```yaml
characteristics_note: Murata SimSurfing typical curves; not guaranteed worst-case
  limits
characteristics_pdf: 02_parts/GRM21BR60J226ME39L/GRM21BR60J226ME39-characteristics.pdf
design_curve_screen: Murata typical curve is approximately 54% retained at 3.3 V;
  two parallel output parts screen to 16.16 uF after 0.80 tolerance and an additional
  0.85 temperature allowance, versus TPS62825 minimum-effective COUT 10 uF. The 44-uF
  nominal bank is treated as the Table 8-3 47-uF class; curve and 0.85 factor are
  engineering screens, not guaranteed PVT limits.
```

## `LT3045EDD-PBF`

```yaml
programming:
  rset:
    ref: R_LDO_SET
    nominal_ohm: 33000
    tolerance: 0.001
    nominal_vout_V: 3.3
    full_range_screen_V:
    - 3.228766
    - 3.371366
    engineering_band_V:
    - 3.22
    - 3.38
    note: Includes resistor tolerance, full-temperature 98-102uA SET current and +/-2mV
      offset. The conservative 3.22-3.38V engineering band contains this result and
      remains within every actual held-load operating range; the prior 3.23-3.35V
      declaration was optimistic and no user hard limit supports it.
  cset:
    refs:
    - C_LDO_NR4
    - C_LDO_NR5
    total_uF_nominal: 4.701
    t90_ms_fast_start_disabled: 356.3859
    noise_typ_uVrms_10Hz_100kHz: 0.8
    note: 4.7uF is the Rev.D low-noise condition. PGFB fast start avoids the disabled-fast-start
      RC delay; exact ramp under candidate load remains an owed transient check.
  ilim:
    ref: R_LDO_ILIM
    nominal_ohm: 300
    specified_limit_A:
    - 0.45
    - 0.55
    source: Rev.D electrical table pp4-5. Existing 300ohm exact resistor dossier reused.
  pgfb:
    top: R_LDO_PG_TOP=100k 1%
    bottom: R_LDO_PG_BOT_A=10k 0.1% plus R_LDO_PG_BOT_B=1k 0.1%
    rising_output_threshold_nominal_V: 3.02727
    rising_output_threshold_screen_V:
    - 2.906
    - 3.149
    effect: Fast-start current remains active until the output reaches the screened
      threshold; PG remains floating. Datasheet example is 10ms typical with 4.7uF
      and fast start, but candidate ramp is not guaranteed by that example.
  enable:
    source_net: LDO_EN
    rising_range_V:
    - 1.18
    - 1.32
    hysteresis_typ_V: 0.13
    note: 74LVC1G14 held-domain driver swings between GND and 5V_LDO_HOLD; native
      timing and transition measurement remain owed.
rail_screen:
  load_allocation_A: 0.25
  capacity_margin_A: 0.25
  capacity_ratio: 2.0
  min_headroom_V: 0.72
  dropout_margin_at_500mA_V: 0.27
  dissipation_W_at_5V05_3V22_250mA_before_ground_current: 0.4575
  conservative_dissipation_W_using_25mA_ground_current_bound: 0.58375
  board_engineering_capacity_W: 0.65
  max_ambient_C: 70
  effective_theta_ja_max_C_per_W: 84.6
  power_reserve_W: 0.06625
  power_reserve_pct: 11.35
  note: 250mA allocation incorporates the independent 224.831mA held-domain static
    audit plus 25.169mA reserve. The 25mA ground-current bound is specified at 500mA
    and is deliberately conservative here. The 650mW board capacity at 70C requires
    effective thetaJA <=84.6C/W to remain at or below the 125C E-grade junction limit.
    Native extraction and thermal measurement remain physical qualification.
stability:
  input: C_LDO_IN is 47uF X7R, above the 4.7uF minimum; effective capacitance and
    input-loop geometry remain layout checks.
  output: C_LDO_OUT and C_OPA_BULK are separate 47uF X7R ceramics, above the 10uF
    minimum. Each installed effective capacitance must remain >=10uF; ESR must be
    <20mohm and ESL <2nH.
  minimum_load: The datasheet requires 10uA only when VOUT<1V. At 3.3V there is no
    specified minimum-load requirement; the retained 200ohm bleed also provides a
    large load while enabled.
```

## `744373240047` nested normalization

```yaml
datasheet.date: '2024-12-27'
layout.recommended_lands_mm:
  pad_size:
  - 1.5
  - 2.4
  pad_centers:
  - - -1.85
    - 0
  - - 1.85
    - 0
  overall_span_x: 5.2
  inner_restricted_gap_x: 2.2
layout.restriction: No vias or traces in the 2.2-mm central restricted area shown
  by the primary drawing.
```

## `W25Q128JWSIQ` nested normalization

```yaml
datasheet.retained_from: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8919/256_W25Q128JW.pdf
layout_refs_extra:
- interface timing: null
  ordering table and package drawing: null
- {}
```

## `IS25WP032D-JBLE` nested normalization

```yaml
datasheet.mirror_url: https://www.ic-components.com/files/0c/IS25LP032D-JBLE.pdf
lcsc: C1349020
```

## `XU316-1024-TQ128-C24` nested normalization

```yaml
pin_domains:
  1: IOL_1V8_SELECTED
  2: IOL_1V8_SELECTED
  3: IOL_1V8_SELECTED
  4: IOL_1V8_SELECTED
  5: CORE_0V9
  6: IOL_1V8_SELECTED
  7: IOL_1V8_SELECTED
  8: IOL_1V8_SELECTED
  9: IOL_1V8_SELECTED
  10: IOL_1V8_SELECTED
  11: CORE_0V9
  12: IOL_1V8_SELECTED
  13: IOL_1V8_SELECTED
  14: CORE_0V9
  15: IOL_1V8_SELECTED
  16: IOL_1V8_SELECTED
  17: IOL_1V8_SELECTED
  18: CORE_0V9
  19: IOL_1V8_SELECTED
  20: IOL_1V8_SELECTED
  21: IOL_1V8_SELECTED
  22: IOL_1V8_SELECTED
  23: IOL_1V8_SELECTED
  24: MIPI_UNUSED_GND
  25: MIPI_UNUSED_NC
  26: MIPI_UNUSED_NC
  27: MIPI_UNUSED_GND
  28: MIPI_UNUSED_NC
  29: MIPI_UNUSED_NC
  30: GND
  31: MIPI_UNUSED_NC
  32: MIPI_UNUSED_NC
  33: IOB_1V8_FIXED
  34: IOB_1V8_FIXED
  35: IOB_1V8_FIXED
  36: IOB_1V8_FIXED
  37: IOB_1V8_FIXED
  38: IOB_1V8_FIXED
  39: CORE_0V9
  40: IOB_1V8_FIXED
  41: PLL_0V9_FILTERED
  42: GND
  43: IOB_1V8_FIXED
  44: IOB_1V8_FIXED
  45: CORE_0V9
  46: IOB_1V8_FIXED
  47: IOB_1V8_FIXED
  48: IOB_1V8_FIXED
  49: IOB_1V8_FIXED
  50: CORE_0V9
  51: IOB_1V8_FIXED
  52: IOB_1V8_FIXED
  53: IOB_1V8_FIXED
  54: CORE_0V9
  55: NC
  56: IOB_1V8_FIXED
  57: IOB_1V8_FIXED
  58: USB_PHY
  59: USB_PHY
  60: USB_PHY
  61: USB_3V3
  62: USB_1V8
  63: IOR_1V8_SELECTED
  64: IOR_1V8_SELECTED
  65: IOR_1V8_SELECTED
  66: IOR_1V8_SELECTED
  67: IOR_1V8_SELECTED
  68: CORE_0V9
  69: IOR_1V8_SELECTED
  70: IOR_1V8_SELECTED
  71: IOR_1V8_SELECTED
  72: IOR_1V8_SELECTED
  73: IOR_1V8_SELECTED
  74: IOR_1V8_SELECTED
  75: IOR_1V8_SELECTED
  76: IOR_1V8_SELECTED
  77: IOR_1V8_SELECTED
  78: IOR_1V8_SELECTED
  79: IOR_1V8_SELECTED
  80: IOR_1V8_SELECTED
  81: IOR_1V8_SELECTED
  82: IOR_1V8_SELECTED
  83: IOR_1V8_SELECTED
  84: IOR_1V8_SELECTED
  85: CORE_0V9
  86: IOR_1V8_SELECTED
  87: IOR_1V8_SELECTED
  88: IOR_1V8_SELECTED
  89: IOR_1V8_SELECTED
  90: IOR_1V8_SELECTED
  91: IOR_1V8_SELECTED
  92: IOR_1V8_SELECTED
  93: IOR_1V8_SELECTED
  94: IOR_1V8_SELECTED
  95: CORE_0V9
  96: IOR_1V8_SELECTED
  97: IOR_1V8_SELECTED
  98: IOT_1V8_SELECTED
  99: IOT_1V8_SELECTED
  100: IOT_1V8_SELECTED
  101: IOT_1V8_SELECTED
  102: IOT_1V8_SELECTED
  103: IOT_1V8_SELECTED
  104: CORE_0V9
  105: CORE_0V9
  106: CORE_0V9
  107: IOT_1V8_SELECTED
  108: IOT_1V8_SELECTED
  109: IOT_1V8_SELECTED
  110: IOT_1V8_SELECTED
  111: IOT_1V8_SELECTED
  112: IOT_1V8_SELECTED
  113: CORE_0V9
  114: IOT_1V8_SELECTED
  115: IOT_1V8_SELECTED
  116: IOT_1V8_SELECTED
  117: IOT_1V8_SELECTED
  118: IOT_1V8_SELECTED
  119: IOT_1V8_SELECTED
  120: IOT_1V8_SELECTED
  121: IOT_1V8_SELECTED
  122: IOT_1V8_SELECTED
  123: IOT_1V8_SELECTED
  124: IOT_1V8_SELECTED
  125: IOT_1V8_SELECTED
  126: IOT_1V8_SELECTED
  127: IOL_1V8_SELECTED
  128: IOL_1V8_SELECTED
  129: GND
sourcing.jlcpcb:
  lcsc: C6362698
  checked_at: '2026-09-22T02:31:00-07:00'
  catalog_mpn: XU316-1024-TQ128-C24
  catalog_manufacturer: XMOS
  stock: 46
  note: Exact MPN/manufacturer identity from live JLC parts API; design-stage observation
    only.
```

## `TPS26625DRCR` nested normalization

```yaml
sourcing.allocation: UNQUALIFIED
sourcing.jlcpcb:
  lcsc: C2862873
  checked_at: '2026-09-22T02:31:00-07:00'
  catalog_mpn: TPS26625DRCR
  catalog_manufacturer: Texas Instruments
  stock: 3091
  note: Exact MPN/manufacturer identity from live JLC parts API; design-stage observation
    only.
sourcing.ti_store_observation_2026_09_22: active production, out of stock, no public
  unit price
```

## `CC0805KRX7R9BB104` nested normalization

```yaml
sourcing.allocation: unqualified_for_candidate
```

## `RT0603BRD0744K2L` nested normalization

```yaml
sourcing.allocation: unqualified_for_candidate
```

## `power_tree.yaml` duplicate prose

```yaml
source_voltage_boundary.maximum_operating_V: 13.2
rails.ir_budget_evidence:
  N12V_POD1: 'The 11.006 V protected-rail floor provides 206 mV above the 10.8 V connector-plane
    floor. After the owning gate''s 20% delivery margin, the admitted path is 1710
    milliohm: 171 mV nominal and 205.2 mV charged at 0.10 A. TPS26625 consumes at
    most 800 milliohm at its guaranteed hot RON; 910 milliohm remains for copper,
    joints and connector contacts and must be checked on the native board.'
  N12V_POD2: 'The 11.006 V protected-rail floor provides 206 mV above the 10.8 V connector-plane
    floor. After the owning gate''s 20% delivery margin, the admitted path is 1710
    milliohm: 171 mV nominal and 205.2 mV charged at 0.10 A. TPS26625 consumes at
    most 800 milliohm at its guaranteed hot RON; 910 milliohm remains for copper,
    joints and connector contacts and must be checked on the native board.'
  N12V_POD3: 'The 11.006 V protected-rail floor provides 206 mV above the 10.8 V connector-plane
    floor. After the owning gate''s 20% delivery margin, the admitted path is 1710
    milliohm: 171 mV nominal and 205.2 mV charged at 0.10 A. TPS26625 consumes at
    most 800 milliohm at its guaranteed hot RON; 910 milliohm remains for copper,
    joints and connector contacts and must be checked on the native board.'
  N12V_POD4: 'The 11.006 V protected-rail floor provides 206 mV above the 10.8 V connector-plane
    floor. After the owning gate''s 20% delivery margin, the admitted path is 1710
    milliohm: 171 mV nominal and 205.2 mV charged at 0.10 A. TPS26625 consumes at
    most 800 milliohm at its guaranteed hot RON; 910 milliohm remains for copper,
    joints and connector contacts and must be checked on the native board.'
  N12V_POD5: 'The 11.006 V protected-rail floor provides 206 mV above the 10.8 V connector-plane
    floor. After the owning gate''s 20% delivery margin, the admitted path is 1710
    milliohm: 171 mV nominal and 205.2 mV charged at 0.10 A. TPS26625 consumes at
    most 800 milliohm at its guaranteed hot RON; 910 milliohm remains for copper,
    joints and connector contacts and must be checked on the native board.'
  N12V_POD6: 'The 11.006 V protected-rail floor provides 206 mV above the 10.8 V connector-plane
    floor. After the owning gate''s 20% delivery margin, the admitted path is 1710
    milliohm: 171 mV nominal and 205.2 mV charged at 0.10 A. TPS26625 consumes at
    most 800 milliohm at its guaranteed hot RON; 910 milliohm remains for copper,
    joints and connector contacts and must be checked on the native board.'
  N12V_POD7: 'The 11.006 V protected-rail floor provides 206 mV above the 10.8 V connector-plane
    floor. After the owning gate''s 20% delivery margin, the admitted path is 1710
    milliohm: 171 mV nominal and 205.2 mV charged at 0.10 A. TPS26625 consumes at
    most 800 milliohm at its guaranteed hot RON; 910 milliohm remains for copper,
    joints and connector contacts and must be checked on the native board.'
  N12V_POD8: 'The 11.006 V protected-rail floor provides 206 mV above the 10.8 V connector-plane
    floor. After the owning gate''s 20% delivery margin, the admitted path is 1710
    milliohm: 171 mV nominal and 205.2 mV charged at 0.10 A. TPS26625 consumes at
    most 800 milliohm at its guaranteed hot RON; 910 milliohm remains for copper,
    joints and connector contacts and must be checked on the native board.'
```
