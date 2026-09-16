# Independent schematic topology witness

subject: crow-audio-carrier-v1 frozen schematic  
source_commit: b8c26163c6a264af5c184a64d0cf64e4d4e4e115  
date: 2026-09-10  
reviewer: carrier_schematic_topology_20260910 independent subagent  
context-given: Fresh-context commission and frozen project/external_hardware packet only  
independence: Independent manufacturer-reference and native-netlist examination; no other review, live journal, STATUS, or gate verdict used as evidence  
review_stage: pre-route  
review_kind: topology  
design_verdict: SOUND  
order_verdict: DO-NOT-ORDER  
completed_at: 2026-09-10T03:29:32Z  
commission_sha256: 7df8a217ddc8d72c260c18274b450c7ffa20626a81f34c999a62847aed329e39  
subject_packet_sha256: ed1ac9f2f8f5f432259885d3fd0e0aab47f67b64a0c01aa757561f9b984f9590  
netlist_sha256: ea6b7755b478e43eacc403f4b69797f3a800d0e05c45ddd26e875cc0bfa42512  
parts_sha256: 999609a09ecdf1b80be4238fbe138fd772d08577b282df38a1ed588dd0e5998d  
design_rules_sha256: 672f0b9be3b3f9b6c2a9c9c1b1ea0e12ff4d91f061ede29ac36d6ac71965b8a4  
circuit_json_sha256: 1207938f7076659ae9bba0305dba320c88b5f1d08222bde2ecdfdd4b3e1447a5  
schematic_pdf_sha256: a60ecc459b40f6f7d7480a33ec54ed65cbd52dd05bda819eb88440466d5a3ab0  
native_schematic_raw_sha256: d546f64709c99f8f958c03e0d8c5e692c95a22f975dfb2fe71dec849549c27c3  
native_netlist_raw_sha256: c4fa53111717a9413978aea1ea0af0ad9ba519eb2940884ad57e8d614a081d66  

## Verdict and scope

The frozen native-netlist topology is SOUND for the expressly unqualified prototype boundary. No known in-boundary electrical topology defect was identified. This verdict does not establish measured transient safety, analog performance, installed stability, fault selectivity, thermal performance, or order readiness.

All assigned functional blocks were examined. The unresolved rows below are substantive qualification obligations, not completed tests. Failure of their declared engineering envelopes requires reassessment or redesign.

The subject remained read-only. Commission, packet, raw artifact hashes, and all three owning binding hashes were independently recalculated before and after examination and matched. Only binding functions from the permitted `pre_route_review_check.py` method were used; its review-checking entry point was not run. Source ADRs were consulted for intent and declared boundaries. Embedded author/checker assertions in those ADRs were not used as proof.

## Evidence and method

The complete native netlist was independently parsed into component/pin/net relationships: 333 components, 937 nodes, and 220 nets. All 42 singleton nets are explicitly named no-connects; there are no unexplained non-NC singleton nets. Repeated channels were examined individually, not accepted from generator symmetry alone.

Manufacturer references reopened from the frozen packet included:

- ADI LT3041 Rev. A: electrical specifications, pin functions, output-capacitor requirements, output-overshoot recovery, reverse-current protection, and thermal discussion.
- Cirrus CS5308P DS1314F1: pin functions, operating/absolute limits, supply connections, hardware straps, startup sequence, clocking, and TDM format.
- Cirrus AN0556R1 §1.2 and July 2025 schematic/layout guidelines §§1.6–1.10.
- TI OPA2320 SBOS513F, TMUX28xx SCDS488, TPS3890 SLVSD65A, TPS3839 SBVS193D, SN74LVC1G123 SCES586E, SN74LVC3G34 SCES366L, and SN74LVC1G125 SCES223U.
- Nexperia 74LVC1G14 Rev.19 and 74LVC1G17 Rev.16.
- Diodes AP63205 DS41326 Rev.3-2, DMP6023LFG, US1B, B340A, and BZT52; Littelfuse 2920L, 1812L, and SMBJ references.
- AO3400A/AO3401A manufacturer references, Coilcraft XGL4020 data, Yageo exact 33 kΩ reference, and the miniDSP MCHStreamer manual.

Manufacturer typical values and source engineering allocations are identified as such below.

## Completed topology checks

### 1. Input protection and eight spoke supplies

J9.1 feeds `12V_IN`, F_IN feeds `12V_FUSED`, and Q_IN.5 is the upstream drain. Q_IN.1–3 are the downstream sources on `12V_PROTECTED`; this orientation permits forward startup through its body diode and then low-resistance channel conduction. R_QIN_G pulls its gate down; D_QIN_GS has its cathode at the source and anode at the gate. D_IN is a positive-rail TVS, cathode to `12V_PROTECTED`, anode to GND.

F1–F8 independently connect `12V_PROTECTED` to `12V_POD1`–`12V_POD8`. Every J1–J8 connector has:

- Pin 1: its own protected spoke supply.
- Pin 2: GND.
- Pin 3: corresponding positive audio input.
- Pin 4: corresponding negative audio input.

The selected 1812L035/60 reference specifies 0.35 A room-temperature hold, 0.70 A trip, and 1.700 Ω post-trip/reflow resistance maximum. These are not precision current-limiter specifications.

Independent arithmetic reproduces the conditional header floor:

`11.4 − 1.0 × 0.200 × 1.2 − 0.10 × 2.2 × 1.2 = 10.896 V`.

That calculation depends on the declared common/branch resistance allocations. Hot resistance, actual PFET gate drive, contact resistance, upstream source behavior, and fault selectivity remain unmeasured. The topology does not provide downstream reverse-source blocking or permit powered insertion.

### 2. Buck, reverse isolation, and held supply

D_BUCK_IN.2 is on `12V_PROTECTED`; its cathode, pin 1, supplies `12V_BUCK_IN`. U_BUCK VIN.3 and EN.2 and all three input capacitors are downstream of that diode. This correctly isolates the buck input-capacitor domain from a collapsing upstream trunk.

U_BUCK.1 senses `5V_BUCK`; SW.5 reaches L_BUCK and then `5V_BUCK`; C_BUCK_BST connects BST.6 to SW.5. The AP63205 fixed-5 V pin topology is correct. The selected 3.3 µH inductor differs from the 4.7 µH typical application but is not an intrinsic wiring defect at the declared local load. Ripple, startup, saturation, and installed stability require verification.

D_HOLD has its anode at `5V_BUCK` and cathode at `5V_LDO_FEED`. R_PRE provides a 22 Ω precharge path to `5V_LDO_HOLD`; Q_PRE parallels that path with source on FEED and drain on HOLD. Q_PRE_EN pulls its gate low when PWR_EN rises. C_HOLD1/2 provide held-domain reservoirs; C_LDO_IN supplies local ceramic bypass.

Q_PRE's body diode can return held charge toward FEED, but D_HOLD blocks continuation toward the buck. This is consistent with the intended isolation boundary, not a claim of zero leakage.

### 3. LT3041 pin, grade, set, sense, return, and thermal topology

U_LDO matches the selected LT3041ADE#TRPBF A-grade part:

| Pins | Actual connection | Manufacturer function |
|---|---|---|
| 1, 2, 3 | `5V_LDO_HOLD` | IN |
| 4 | NC | Unused VIOC |
| 5 | `LDO_EN` | EN/UV |
| 6 | NC | Unused PG |
| 7 | GND | Disable programmable current-limit function |
| 8 | `5V_LDO_HOLD` | PGFB tied to IN |
| 9 | `LDO_NR` | SET |
| 10, 11, 15 | GND | Ground and exposed pad |
| 12 | `3V3_ADC` | OUTS |
| 13, 14 | `3V3_ADC` | OUT |

R_LDO_SET is 33 kΩ to GND. The nominal result is `100 µA × 33 kΩ = 3.3 V`. Using the full-temperature 99–101 µA SET limits, ±2 mV offset, and a conservative ±0.35% resistor envelope gives approximately 3.254–3.347 V, within the authored 3.23–3.35 V envelope. This is an allocation calculation, not a measured rail.

C_LDO_NR4/5 total 2 nF. This does not inherit the regulator's published low-noise performance obtained with much larger SET capacitance.

C_LDO_OUT and C_OPA_BULK are two separate 47 µF output ceramics. The declared derating factor leaves about 16.18 µF each. ADI requires two effective ≥10 µF capacitors, each ESR <20 mΩ and ESL <2 nH. Native net equivalence alone cannot prove those requirements or Kelvin routing.

ADI explicitly supports output held above an input that is grounded, intermediate, or open. It also permits discharge through SET-related paths and up to 15 mA through overshoot recovery; that sink cannot be omitted.

At 0.23 A output, 5.15 V input, 3.23 V output, and a 25 mA ground-current allocation, calculated dissipation is approximately 0.570 W. Applying 37 °C/W gives approximately 106 °C junction at 85 °C ambient. The thermal resistance comes from a reference-board condition and is not acceptance of this PCB.

### 4. All eight complete analog channels

Every channel has the same verified functional sequence:

`J AUDIO± → 1 µF coupling → 100 kΩ bias → 10 kΩ input limiter → OPA2320 noninverting input`.

U_AFE1–8 pin 8 shares `3V3_ADC`; pin 4 is GND. Positive paths use input pin 3, feedback pin 2, and output pin 1. Negative paths use input pin 5, feedback pin 6, and output pin 7.

Each output reaches its FILTER net through 10 Ω. Its inverting input receives DC feedback through 300 Ω from that FILTER net and high-frequency feedback through 680 pF from the amplifier output. Thus feedback senses after the 10 Ω resistor; it is not an open-loop buffer or positive-feedback connection.

Each FILTER leg has two grounded 15 nF capacitors. This is 30 nF per leg and the same 15 nF differential equivalent as the vendor bridge, but it changes common-mode loading. No stability or distortion result is transferred from the vendor circuit.

U_ISO1–8 use S1.1/D1.2 for positive paths, S2.5/D2.6 for negative paths, both selects on AUDIO_EN, VDD.8 on `5V_LDO_HOLD`, and GND.4/EP.9 on GND. Every ADC-side leg has its own 10 kΩ pulldown and 1 nF capacitor.

| Channel | Bias bank | ADC negative pin | ADC positive pin |
|---|---|---:|---:|
| 1 | VMID1_EXT | 39 | 40 |
| 2 | VMID1_EXT | 41 | 42 |
| 3 | VMID1_EXT | 45 | 46 |
| 4 | VMID1_EXT | 47 | 48 |
| 5 | VMID2_EXT | 13 | 14 |
| 6 | VMID2_EXT | 15 | 16 |
| 7 | VMID2_EXT | 19 | 20 |
| 8 | VMID2_EXT | 21 | 22 |

Both passive bias banks are 1 kΩ/1 kΩ dividers with 10 µF +1 µF bypass. Their nominal Thevenin resistance is 500 Ω and nominal time constant 5.5 ms. They do not load the ADC's internal VMID outputs.

At 1.2 Vrms differential input, each balanced leg has 0.8485 V peak excursion. Around nominal 1.65 V bias this spans approximately 0.801–2.499 V, comfortably inside the normal shared rail. The nominal coupling high-pass corner is approximately 1.59 Hz.

OPA2320 input overdrive is explicitly current-limited by the 10 kΩ resistors; TI permits overdrive with current limited to 10 mA. Its rail-to-rail designation is not an ideal transient clamp guarantee.

The ADC presents approximately 3 kΩ differential input resistance typically, in addition to the 20 kΩ differential equivalent of the pulldowns. With a 0.3 Ω-per-switch allocation, their combined loading produces about 230 ppm differential attenuation after the feedback point. Exact unity gain and guaranteed ADC impedance are not claimed.

U_ESD1–8 have the correct TPD2E2U06 DRL pin map: IO1.3 and IO2.5 to audio, GND.4 to ground, pins 1/2 NC.

### 5. ADC supplies, references, and configuration

U_ADC VDD_A1.5, VDD_A2.9, and VDD_IO.31 share `3V3_ADC`. LDO_D_FILT.32 connects directly to VDD_D.33 and C_LDO_D; LDO_A_FILT.7 has its own capacitor. Ground pins 6, 8, 30, and 49 are common GND.

Internal VMID outputs 1/12 have separate local bypass banks. FILT1P.43 and FILT2P.18 receive the rail through individual 1 Ω resistors, with 470 µF/10 µF/1 µF banks to GND; FILT1N.44 and FILT2N.17 are grounded. Connections agree with the external-reference topology in Cirrus Figure 2-2.

The selected nominal bypass values exceed the relevant Cirrus minimum effective capacitances under the declared derating assumptions; installed capacitance remains a qualification item.

The actual straps decode as:

- CONFIG1.2: 4.7 kΩ down, secondary mode for 44.1/48 kHz.
- CONFIG2.3: direct pull-up through 0 Ω, minimum-slot TDM.
- CONFIG3.4: GND.
- CONFIG4.10: 4.7 kΩ up, normal channel order.
- CONFIG5.11: 100 kΩ down, linear-phase fast-rolloff filter with HPF enabled.

For this eight-channel converter, the selected 44.1/48 kHz TDM mode uses one output and eight slots at ≥256 fs BCLK. DOUT1.25 is connected; DOUT2–4 are intentionally NC. Hardware mode and unused control-pin terminations are consistent.

### 6. MCH clocks, data, and independent power

J10 connects MCH J1 pin 2 to TDM data, 9 to MCLK, 10 to BCLK, 11 to GND, and 12 to FSYNC. J11 uses MCH J3 pin 1 GND and pin 2 presence sense only. The module's 3.3 V output does not power the carrier rail.

U_CLK maps its three channels correctly, followed by individual 22 Ω damping resistors to U_ADC MCLK.34, BCLK.29, and FSYNC.24. All three incoming clock nets have 10 kΩ pulldowns. TI's 5 µA input-leakage maximum gives approximately 50 mV with nominal resistance when disconnected; additional module/cable leakage is an allocation.

The manual's 24.576/22.5792 MHz MCLK and 256 fs BCLK at 48/44.1 kHz match the ADC configuration. This is not approval for changing the firmware sample rate to 96 kHz without changing the configuration.

DOUT1 passes through U_TDM_SCH, then U_TDM, then R_TDM 33 Ω. R_TDM_PD defines the released raw-data state. The noninverting Schmitt stage accepts slow raw-data transitions; it does not leave an ordinary CMOS input floating.

J11 presence passes through 300 Ω/10 kΩ to U_OE, whose inversion correctly enables the active-low U_TDM OE only when presence is high. Ioff-capable devices support settled independent-power states. Neither Ioff specifications at VCC=0 nor a Schmitt presence threshold proves arbitrary intermediate-voltage safety at the external MCH receiver.

### 7. Reset and enable sequence

U_PWR monitors `5V_BUCK` through 30.9 kΩ/10 kΩ while powered from the held rail. Nominal falling/rising thresholds are approximately 4.7035/4.7321 V. PWR_EN bypasses precharge and, through the two-inverter RC chain, enables the LDO and removes the dump.

U_AUDIO monitors `3V3_ADC` through 17.4 kΩ/10 kΩ, with MR driven by PWR_EN. Nominal falling/rising thresholds are approximately 3.151/3.170 V. Its two CT capacitors delay audio reconnection.

The dump network has 50 kΩ equivalent resistance and 15 nF capacitance. PWR_EN falling eventually drives Q_DUMP on and LDO_EN low; AUDIO_EN is separately forced low by the supervisor path. The polarity is correct.

U_RST1 monitors the ADC rail and drives U_RST2 CLR. The monostable has A low and B high, so CLR rising triggers Q high. Q_RST1 then asserts ADC_RESET_N low until the pulse expires. Its default pull-up first permits RESET high. This implements the required high–wait–low–wait–high sequence.

TPS3839's specified 120 ms minimum release delay comfortably exceeds the initial 2 ms requirement. The 100 kΩ/220 nF monostable timing is deliberately long, but its achieved minimum pulse width remains a physical validation obligation; no typical timing coefficient has been promoted to a guarantee.

## Unresolved findings and qualification rows

No P0/P1 known electrical topology defect was found. The following remain open; “P2 qualification” denotes potentially consequential validation work, not a demonstrated schematic failure.

| ID | Severity | Exact subject | Evidence and unresolved requirement |
|---|---|---|---|
| Q1 | P2 qualification | U_LDO.12–14, C_LDO_OUT, C_OPA_BULK, SET.9, GND.10/11/15 | ADI requires effective capacitance, ESR/ESL, Kelvin sense/return, and thermal performance. Nominal components and common net names do not establish these. |
| Q2 | P2 qualification | U_ADC supply pins 5/9/31/33; Q_PRE/R_PRE; Q_DUMP/R_DUMP; FILT banks | Cirrus specifies 0.01–10 ms supply ramp up/down. Actual startup current, reservoir charging, reference tails, discharge waveform, and resistor/FET pulse stresses remain unmeasured. |
| Q3 | P2 qualification | U_AFE1–8 outputs; FILTER1–8 P/N; U_ISO1–8; ADC1–8 P/N | Shared supply removes an independent steady overdrive source but does not guarantee rail-relative transient tracking. The 50 pC switch-charge, 100 mV return-error, and 50 mV amplifier-overshoot values are engineering allocations. ADC limits remain −0.3 V to VDD_A+0.3 V. |
| Q4 | P2 qualification | All 16 OPA input limiters, VMID1/2_EXT, R_OPA_BLEED1/2 | At a 3.4 V rail barrier, the stated conservative source envelope gives about 12.98 mA gross positive injection versus 16.19 mA bleed at 210 Ω. This is conditional on retained-charge/leakage bounds; it is not measured silicon startup behavior. |
| Q5 | P2 qualification | All eight 30 nF-per-leg filters and passive bias banks | Differential equivalence does not prove common-mode stability, noise, distortion, matching, or crosstalk. The actual OPA2320/filter/ADC load must be measured. |
| Q6 | P2 qualification | J10/J11, U_CLK, U_OE, U_TDM_SCH, U_TDM | miniDSP does not supply complete loaded I/O and partial-power ratings in its manual. Verify actual levels, edge rates, setup/hold, current injection, split-cable states, and power transitions. Presence sensing is not a precision remote-rail supervisor. |
| Q7 | P2 qualification | U_RST1/U_RST2/Q_RST1 and U_PWR/U_AUDIO | Verify the ADC reset pulse, rail recovery, and supervisor/switch/dump timing over the intended range. Several falling delays and generated pulse characteristics are typical-only. |
| Q8 | P2 qualification | J9, F_IN, Q_IN, F1–F8, J1–J8 | The calculated delivery floor depends on hot path resistance and source behavior. Verify simultaneous load, startup, one-spoke fault selectivity, and recovery without resetting healthy spokes. PPTCs are not instantaneous current limiters. |
| Q9 | P2 qualification | U_ADC and shared 3V3/5V power tree | Cirrus consumption is published typically, not as a guaranteed full-corner maximum. Authored load/efficiency allocations must be confirmed; thermal arithmetic and nominal capacitor derating are not production guarantees. |

## Completion boundary

All commission topology blocks are covered; none was omitted for the deadline. No schematic-render verdict, realized-placement/copper verdict, DRC/fit qualification, procurement allocation, or release approval is supplied.

The packet and binding hashes were unchanged at completion. The schematic remains DO-NOT-ORDER.
