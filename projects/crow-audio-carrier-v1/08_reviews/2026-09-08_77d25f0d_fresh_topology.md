# Frozen schematic topology witness

subject: crow-audio-carrier-v1 77d25f0dd1a44ca5139be80310e65417c17a2ec6  
date: 2026-09-07  
reviewer: fresh-context agent, topology lens  
context-given: exact-source-and-primary-documents, no prior reviews  
source_commit: 77d25f0dd1a44ca5139be80310e65417c17a2ec6  
review_stage: pre-route  
review_kind: topology  
design_verdict: SOUND  
order_verdict: DO-NOT-ORDER  
netlist_sha256: 32353f2259a5b903725e25bf54d192f9b2b5bc3a290e89d145a90e65400aba70  
parts_sha256: da40483f53767ef34e8d0b561eea11d36e6bc6c10162dcae50a9078cf5373e0d  
design_rules_sha256: 14603bc34e244ce702e97a3b14251090eeb88377107e26293fb6ace4d1d26fd9  
schematic_pdf_sha256: 9bd63701177f611b0822e30d6b8438e2c515522539007fa2502708e682ad7e89  
review_started_utc: 2026-09-07T23:55:19Z  
review_ended_utc: 2026-09-08T00:19:38Z  
final_integrity_check_utc: 2026-09-08T00:19:20.338974Z

## Verdict and scope

SOUND applies to this exact electrical source as the adopted, conditional laboratory-prototype candidate. I found no concrete topology contradiction requiring a DEFECTIVE verdict within that scope. It does not mean that startup, shutdown, partial-power behavior, analog performance, temperature performance, physical implementation or lifetime drift have been demonstrated.

[ADR0007](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/01_docs/decisions/0007-prototype-before-physical-qualification.md) permits a prototype before physical qualification; it does not waive known defects or authorize purchasing. [ADR0009](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/01_docs/decisions/0009-held-power-and-analog-isolation.md) explicitly makes the held-power candidate conditional on outstanding measurements. Those qualifications materially limit this verdict.

DO-NOT-ORDER remains mandatory. This witness approves neither the stale PCB nor layout, routing, fabrication outputs, an upload package, stock allocation or purchasing.

## Integrity, independence and coverage

The required PCB-design and KiCad skills, selected execution/review/schematic/pin-review procedures, project review contract, task and strict envelope were read. Review used authored requirements, protection/power rules, ADRs, first-article instructions, the generated native netlist and primary manufacturer documents. Earlier review verdicts and root SOURCE-CORRECTION reports were not consulted.

| Check | Measured result |
|---|---|
| Strict `TaskEnvelope` input verification | Before and after: 4/4 valid; no verification errors |
| Complete frozen census | Before and after: 368/368 files; independently re-enumerated set identical, including hashes and sizes |
| Source identity | No source delta from frozen commit; later commit changes are handoff material |
| Subject digests | Independently recomputed normalized netlist, parts aggregate, rules, PDF, native schematic and circuit JSON; all matched |
| Native population | 299 components, 205 nets, 868 emitted pin nodes, including 40 NC nodes |
| Population consistency | 299/299 manifest and first-power installed references matched the netlist set |
| Semiconductor coverage | 45 instances: 37 U, 5 Q, 3 D; 324 emitted semiconductor nodes, plus three physical fused-drain aliases on Q_IN |
| Repeated analog coverage | 8/8 channels; 272 independently evaluated connectivity/value assertions passed |
| ADC identities | All 49 package identities checked, including exposed pad, NCs and tied control pins |
| Other population | 128 capacitors, 104 resistors, 9 PPTCs, 11 connectors, 1 ferrite and 1 inductor |
| Parts digest population | 77 dossiers; includes unfitted alternatives/accessories, not 77 installed part types |

Additional independently verified identities:

- Raw netlist: `84bf1202fa7af5b77c3d52961f3cba81da3c6e688e202e6d7b4216e71440698b`
- Native schematic: `47e6adc0e2752fea46c1a60e5780a5f40ad8ff178353d82487b6a609366f8406`
- Circuit JSON: `a0a4818bdd30634dc727637be30465c239f467e5d3f4f7dd644580031845ee38`

The [native netlist](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/netlists/crow_audio_carrier_v1.net) was parsed independently for the graph checks. Passing author tests were not treated as proof. Calculations and PDF examination used temporary files under `/tmp`; no repository files were written. No builds, routing, delegation, accounts, vendor contact or ordering occurred.

## Electrical and physical-pin findings

### Eight analog paths and reference support

All eight paths have the intended four-wire spoke interface: protected branch power, ground, positive audio and negative audio. TPD2E2U06 signal pins 3/5 and ground pin 4 are connected correctly; unused pins 1/2 are NC. The adopted normal signal range fits the device’s working-voltage range. This is not proof of system-level cable-surge or ESD survival.

Each leg has 1 µF film AC coupling and a 100 kΩ bias return to its external buffered VMID domain. All eight OPA1656 filter pairs match the manufacturer application topology: 300 Ω feedback-path resistance, 680 pF local feedback, 10 Ω output isolation and 15 nF differential filtering.

All sixteen TMUX2821 poles are downstream of the completed filters. Opening a switch does not open the op-amp feedback loop. Pins 1/2 and 5/6 form the two signal paths, both select pins 3/7 use AUDIO_EN, pin 8 uses held power, and ground/exposed-pad connections are present. Every ADC-side leg has its own 100 kΩ bleed and 1 nF shunt. The powered-off/partial-power limits nevertheless require qualification at the actual signal and supply trajectories. [TI TMUX2821 datasheet](https://www.ti.com/lit/ds/symlink/tmux2821.pdf)

ADC positive/negative input pin pairs are:

| Channel | ADC P / N pins | Bias domain |
|---|---|---|
| 1 | 40 / 39 | VMID1_BUF |
| 2 | 42 / 41 | VMID1_BUF |
| 3 | 46 / 45 | VMID1_BUF |
| 4 | 48 / 47 | VMID1_BUF |
| 5 | 14 / 13 | VMID2_BUF |
| 6 | 16 / 15 | VMID2_BUF |
| 7 | 20 / 19 | VMID2_BUF |
| 8 | 22 / 21 | VMID2_BUF |

The ninth OPA1656 supplies two external VMID followers from bypassed 10 kΩ/10 kΩ dividers. Feedback returns from the raw follower outputs; 100 Ω output isolation precedes each 4.7 µF reservoir/bias bank. ADC VMID1/2 remain separately bypassed and do not supply these external bias loads.

Both FILT negative pins are directly grounded. Each positive FILT bank has its specified 1 Ω pulse-rated series resistor and 470 µF + 10 µF + 1 µF support. ADC internal-LDO, analog-supply, digital-supply and exposed-pad connections were checked against the physical pin figure. [Cirrus CS5308P DS1314F1, pinout, application circuits and supply guidance](https://statics.cirrus.com/pubs/proDatasheet/CS5308P_DS1314F1.pdf)

### ADC configuration, clocks and reset

Hardware straps select the intended secondary-clock operation, 44.1/48 kHz family, minimum TDM slot count, default channel order and linear fast filter with HPF enabled. DOUT1 carries the eight-channel stream; the unused DOUT/control pins are treated consistently. Eight 32-bit slots at 48 kHz require 12.288 MHz BCLK; 24.576 MHz MCLK is 512 Fs. [Cirrus CS5308P hardware-control tables](https://statics.cirrus.com/pubs/proDatasheet/CS5308P_DS1314F1.pdf)

The MCH boundary has clock inputs on J10 pins 9/10/12, carrier TDM output on pin 2, and ground on pin 11. J11 pin 2 is a sensed remote 3.3 V domain, not a remote supply feed. Clock-buffer input/output physical identities, 10 kΩ input pulls and 22 Ω output resistors were checked. The TDM buffer’s active-low enable comes from the remote-sense Schmitt inverter; its output has 33 Ω series resistance.

TPS3839 supervision and the SN74LVC1G123 pin connections implement the intended post-supply reset pulse: A low, B high, rising clear initiating Q, Q driving the reset pull-down MOSFET. The ADC therefore receives the intended initially high, asserted-low, then released-high sequence. The RC arithmetic is not a guaranteed pulse-width minimum; actual reset timing and MCH loaded logic/clock timing remain bench obligations.

### Input protection and held-power sequence

The input path is J9 → 2920L input PPTC → Q_IN → protected 12 V. Q_IN’s physical drain/source orientation and fused drain package identity are correct for reverse-input hookup protection. It is not an ideal bidirectional reverse-current blocker once enabled.

The SMBJ15A is connected cathode to protected 12 V and anode to ground. It provides transient clamping, not sustained-overvoltage regulation. The eight 1812L035 branch PPTCs are individually in series with spoke power. Their ratings are not precision current limits or proof of selective clearing. [Littelfuse input PPTC](https://www.littelfuse.com/assetdocs/resettable-ptcs-2920l-datasheet?assetguid=f237e8c2-1ed9-4c13-a738-dbe0738b3d2c), [branch PPTC](https://www.littelfuse.com/assetdocs/resettable-ptcs-1812l-datasheet?assetguid=ca5c80cb-504e-4a8a-8e74-0107520a1717), [SMBJ series](https://www.littelfuse.com/assetdocs/tvs-diodes-smbj-series-datasheet?assetguid=ba555e99-a12d-4f72-a0b6-86b06c67171e)

AP63205 VIN/EN, FB, SW, bootstrap and ground identities are correct. The bootstrap capacitor crosses BST–SW; the 3.3 µH inductor connects SW to the regulated output. The OPA supply is fed from raw 5 V through its ferrite, independently of held LDO power. [Diodes AP63205 datasheet](https://www.diodes.com/assets/Datasheets/AP63200-AP63201-AP63203-AP63205.pdf)

B340A feeds the held-input path in the intended direction. The 22 Ω precharge resistor is bypassed by AO3401A after PWR_EN. The two TPS3890 monitors use the intended raw-5 V and ADC-3.3 V dividers and cascaded manual-reset logic. The delayed dump logic, AO3400A drain/source identities and separate LDO-enable inverter implement “isolate first, disable/discharge afterward” while the logic supplies are valid.

TPS7A92 OUT/FB/ground/enable/NR/input/exposed-pad identities are correct; PG is NC and SS_CTRL is grounded. Avoidance of reverse LDO current depends on held-input energy and timely output discharge—it is not an unconditional reverse-current protection feature. [TI TPS3890](https://www.ti.com/lit/ds/symlink/tps3890.pdf), [TI TPS7A92](https://www.ti.com/lit/ds/symlink/tps7a92.pdf)

## Independent quantitative checks

These are calculations, not measurements. Divider bounds use the adopted prototype resistor allowance: 0.1% initial + 25 ppm/°C over 65°C + 0.05% prototype drift, with reference and pin-current bounds included. Capacitor inventories include the stated tolerance, temperature/endurance and solder assumptions.

| Check | Independent result and interpretation |
|---|---|
| LDO set point | 3.23497–3.33240 V |
| Raw-5 V monitor | Falling 4.63146–4.77613 V; upper rising threshold 4.81553 V, 34.47 mV below the adopted 4.85 V minimum |
| Audio monitor | Falling 3.10541–3.19692 V; upper rising threshold 3.22330 V, 11.67 mV below the calculated minimum LDO output |
| Upper capacitor inventories | Output charge: 1,766.080 µF; raw rail: 1,045.479 µF; held rail: 1,672.495 µF |
| Lower hold inventories | Raw rail: 301.909 µF; held rail: 489.940 µF |
| Precharge timing | Minimum modeled PWR delay 298.35 ms; worst modeled residual precharge error 1.82 mV |
| Bias settling | 99% VMID settling ≤323.61 ms versus minimum modeled audio-enable delay 596.70 ms |
| LDO startup screen | NR-current/capacitance calculation gives 3.917–9.999 ms full-scale equivalent; peak charging/current allocation 1.65634 A versus 2.3 A minimum current limit |
| Buck startup screen | Inductor ripple 1.43818 A peak-to-peak under the stated frequency/inductance assumptions; 4 ms raw ramp gives 2.38696 A peak, and LDO-bank startup gives 2.47543 A versus 2.5 A minimum limit |
| Startup sensitivity | A 3.5 ms raw ramp produces 2.58074 A in the same model: the apparent margin is not a guaranteed startup proof |
| Steady regulated load | 267.30 mA including ADC allocation, LDO ground current, all 18 OPA halves, modeled full-band audio loading, switches and controls; below 300 mA allocation |
| Input allocation | 0.8 A spokes + converted 5 V allocation at 85% efficiency + control allowance = 0.96387 A |
| Spoke voltage | Stated resistance/hot factors yield 11.160 V protected and 10.896 V at the loaded header: only 96 mV above 10.8 V |
| Hot PPTC hold rating | Input 1.27 A at 85°C versus 1 A allocation; branch 0.16 A versus 0.10 A allocation |
| LDO thermal screen | 0.3086 W; reference θJA 56.9°C/W gives 102.56°C junction at 85°C ambient. Actual implementation must achieve ≤129.62°C/W to stay below 125°C under this load model |
| OPA input common mode | Maximum modeled leg 2.54853 V versus 2.60 V high-end limit at 4.85 V supply: 51.47 mV margin |
| Effective local capacitors | LDO 47 µF part gives 16.18 µF under the adopted lower factors; ADC support capacitors also remain above their cited minimum effective capacitances |
| Isolation/hold screen | Assumed 100 µs detection budget + 220 µs switching endpoint leaves modeled OPA supply 4.51047 V: approximately 10.47 mV above 4.5 V |
| Held input at dump | With 1.5 ms shutdown budget, held-input minus maximum ADC output remains approximately 296 mV in the model |
| Discharge integration | Independently integrating both FILT banks gives main-rail 90–10% ≈6.385 ms and FILT ≈8.115 ms; FILT to 1% is ≈17.076 ms |
| Pulse energy | Upper precharge energy 22.18 mJ, initial resistor power 1.230 W; upper discharge energy 9.81 mJ |
| Switch logic fanout | Worst modeled AUDIO_EN high at 4.1 V held supply is ≈3.498 V after pull network and sixteen select-input loads |
| Reset screen | 100 kΩ × 220 nF = 22 ms nominal RC; low component corner × assumed timing factor 0.5 gives 9.801 ms, not a manufacturer-guaranteed minimum pulse |

The AP63205 4 ms soft-start value is typical. The oscillator assumption is not a guaranteed low-frequency corner. TPS7A92’s NR current specification at NR = 0 does not bound the complete ramp; the final approximately 3% uses the internal NR resistance. TPS3890’s detection timing and the TMUX test load likewise do not guarantee these complete system trajectories. Their limits were not silently promoted to guarantees. [AP63205](https://www.diodes.com/assets/Datasheets/AP63200-AP63201-AP63203-AP63205.pdf), [TPS7A92](https://www.ti.com/lit/ds/symlink/tps7a92.pdf), [TPS3890](https://www.ti.com/lit/ds/symlink/tps3890.pdf), [TMUX2821](https://www.ti.com/lit/ds/symlink/tmux2821.pdf)

## Findings and outstanding qualification

No P0 electrical source contradiction was identified. The following are qualification holds, not claims of completed tests or newly demonstrated source defects.

### P1 — Startup, shutdown and partial-power measurements remain essential

The 3.5 ms counterexample above defeats an unconditional claim that the buck cannot encounter current limit. The declared 4 ms candidate remains plausible but conditional. Likewise, the approximately 10 mV OPA shutdown margin is too dependent on assumed timing and effective capacitance to certify without traces.

The eight declared POWER-COLD, POWER-START, POWER-FALL, POWER-LOOP, POWER-REVERSE, POWER-AUDIO, POWER-DRIFT and POWER-THERMAL tests remain owed. Capture actual raw/held/input/output/FILT voltages, enable/dump states, analog pin excursions and current, including cold starts, slow input ramps, interrupted starts and rapid restart. Particular attention is required while the LDO can operate near 1.4 V but the Schmitt logic has not yet reached its specified operating supply.

The computed 90–10% fall times do not prove the entire manufacturer-required power trajectory. Neither the supervisor timing budget nor analog-switch turn-off at a different load is an observed maximum.

### P1 — Narrow threshold margins depend on prototype drift assumptions

The 0.05% prototype drift allowance is not the resistor manufacturer’s larger complete endurance/reflow allowance. The 11.67 mV audio release margin must not be represented as an all-life or all-process guarantee.

As-built, post-reflow thresholds across the adopted temperature range must establish that audio enable remains reachable at minimum regulated output, raw power-good remains reachable at minimum raw supply, and shutdown still occurs early enough. Failure of these inequalities would falsify the candidate and require source correction.

### P1 — Analog isolation and performance are not qualified by DC checks

A 100 nA leakage value at specified test points does not establish every partial-power trajectory. Typical charge injection is not a maximum, and off-capacitance is not a complete source-to-drain feedthrough bound.

Actual ADC-pin excursions, pops, settling, stability, channel interaction, noise and distortion require measurement with all eight channels active and the intended source/cable/loading conditions. The first-article plan must have signed numeric noise, THD and phase criteria before a functional pass can be claimed.

### P1 — Physical power protection and thermal performance remain open

The voltage budget has only 96 mV modeled header margin. Real hot resistances, connector/cable drops, B340A drop/leakage, MOSFET behavior, pulse-resistor capability and realized copper/thermal paths can consume the calculated margins.

The branch PPTC is not a 100 mA limiter; its published trip behavior does not establish that one fault leaves seven healthy spokes operating. Verify actual source foldback, branch clearing and hot operation. Reference-board thermal resistances and computed pulse energies are not measurements of the eventual PCB.

### P1 — First energization still requires the authored procedural reconciliation

The first-article instructions explicitly recognize that the original 0.20 A bench limit does not prove successful startup without foldback. The exact installed population, isolated supply transient capability and instrumented startup procedure must be reconciled before power is applied. This review does not authorize increasing a current limit during an unexplained failed run.

### P2 — Discharge model bookkeeping affects the reported number, not this verdict

Moving the local 10 µF + 1 µF ceramic capacitance into each physical FILT bank rather than the main rail changes the independent FILT 90–10% estimate from approximately 8.02 ms to 8.12 ms. Both remain below the modeled 10 ms target. This small modeling distinction should be preserved when comparing bench traces; it is not a demonstrated topology failure.

## Exclusions and disposition

Not established here: PCB/footprint geometry, copper routing, winding/layout suitability, actual thermal resistance, EMC, outdoor suitability, assembled ESD/surge survival, MCH firmware authorization, loaded clock timing, connector fit, manufacturing capability or physical measurements. The 19-page PDF was identity-bound; its readability is a separate lens.

Public availability is not allocated stock. No procurement or purchasing gate was cleared. No canonical TaskAttempt or token telemetry is claimed.

The frozen source is a coherent laboratory-prototype candidate with explicitly unclosed physical qualification. Final disposition: SOUND for that bounded topology scope; DO-NOT-ORDER.
