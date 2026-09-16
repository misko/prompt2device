subject: crow-audio-carrier-v1 bdf66acdc7ce8454615ce53a0551eac781e60a91
date: 2026-09-07
reviewer: fresh-context agent, topology lens
context-given: exact-source-and-primary-documents, no prior reviews
source_commit: bdf66acdc7ce8454615ce53a0551eac781e60a91
review_stage: pre-route
review_kind: topology
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
netlist_sha256: fff1d88ea16195b5f57990597d69a35807ed10d82c34c37ef3af7f1b0d08f9d8
parts_sha256: 140bb54457a95637964e53542708692212d663c2af8dfceec483881565996206
design_rules_sha256: 51006cee26e05e4a3c6554be2ce8e776e99cb57528672e21c706925344ec0c55
schematic_pdf_sha256: d996da549d7881888721a2124562af078bb07a0b562e2037ff103c310ecaf993
review_started_at: 2026-09-07T22:41:53Z
review_completed_at: 2026-09-07T23:04:06Z
deadline_at: 2026-09-07T23:16:10Z

# Independent topology witness

The exact source has one blocking physical-pin identity defect: Q_IN omits manufacturer drain identities 6–8 without the required fused-land alias declaration. This is a demonstrated source-contract failure, not a claim that the common drain is electrically open.

I found no additional concrete electrical contradiction in the adopted laboratory-prototype scope. The held-power/isolation architecture has a coherent conditional engineering case, but its narrow startup and shutdown screens are not physical qualification or guaranteed all-corner performance. ADR0007 permits clearly identified first-article measurements to remain owed; it does not permit missing source identities.

## Authority, integrity and method

The canonical TaskEnvelope SHA-256 independently matched:

`ca86876b5a0f8a4e642f5e4b20f621a9b4b2d6a53101d189ae6e2d40deca5753`

`pipeline_execution.verify_input_packet` passed before review and after completed work: 4/4 packet items, no failures. Independent byte-length and SHA-256 checks passed for 367/367 census files before and after review. All required subject hashes above were independently reproduced using the prescribed normalization/digest functions and the checker’s exact 77-dossier aggregation.

Additional reproduced raw identities:

| Artifact | SHA-256 |
|---|---|
| Native netlist | `91fc31519a1cf9bd488460f7bdf837f6a459bd75bab83fc74e1533f6100c27dc` |
| Native schematic | `ab8aaed86a2b32e312582af20d041d8f2351c2ae9446ecdc42557f9fb6bfc13e` |
| Generated circuit.json | `e6b2d277a274be57009b3ae5bd3daaf1c2427ac4599ca5798c7eea3b1f6fb16d` |

I used the repository PCB lifecycle skills, selected schematic/review procedures, physical-pin protocol and project review contract. Their physical-identity requirement determines the blocking finding below.

I independently parsed the native S-expression netlist, inspected reference/pin/net mappings, reopened manufacturer electrical tables and selected figures, and wrote a separate temporary numerical analysis. The discharge calculation used the exact solution of a two-state linear network, not the author’s Euler implementation. Author test success was not treated as electrical proof.

No prior review, root source-correction report or another reviewer’s verdict was read. No repository/design artifact was changed. Analysis outputs were confined to `/tmp/carrier-topology-bdf-YRn4UH`. No conductor, routing, sub-delegation, purchase, external account or fabricated TaskAttempt/token telemetry was used.

## Measured coverage

The independently parsed population is 299 components, 205 nets and 868 pin-node entries, including intentional NC nets.

| Review area | Coverage |
|---|---|
| Native reference/pin/net census | 299/299 references; 205/205 nets; 868/868 entries |
| Repeated analog circuitry | 8/8 channels; 16/16 polarity legs; all feedback/filter/switch/bleed paths |
| ADC | 49/49 pin identities; all five configuration functions; both reference banks and internal-LDO supports |
| IC/FET/diode connectivity | 37/37 IC references, 5/5 FET references, 3/3 diode references |
| Connector electrical assignments | 11/11 headers, including eight spoke outputs and both MCH cables |
| Protection | One input chain and 8/8 branch-PPTC paths |
| Held-power design | Both supervisors, precharge/bypass, held reservoirs, delayed dump, LDO enable and 16 switch-control inputs |

This is schematic electrical/pin-function coverage, not a claim that every footprint dimension, pad winding, copper feature, connector fit or PDF presentation feature passed an independent layout/render review.

## Findings

### TOP-BDF-001 — P0: Q_IN drops physical drain identities before layout

The Diodes DMP6023LFG primary package figure shows three source positions, one gate position and four drain positions in PowerDI3333-8. The frozen dossier itself acknowledges “common drain land pins 5–8,” but its `pins` dictionary contains only identities 1–5 and has no `pin_aliases`.

The source likewise declares Q_IN schematic pins 1–5 only; its source-owned footprint gives the common drain land only `portHints=["5"]`. The native netlist contains Q_IN nodes 1, 2, 3, 4 and 5, with no 6, 7 or 8.

Evidence:

- Diodes DS37204 Rev.2-2, p.1, independently rendered and visually inspected: three S positions, G, four D positions and pin-1 marker.
- [DMP6023LFG dossier](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/DMP6023LFG-13/part.yaml:15).
- [Source-owned common-drain footprint](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx:172) and [Q_IN schematic definition](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_tscircuit/src/crow_audio_carrier_v1.tsx:373).
- [P-PINMAP policy](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/skills/kicad-pcb/references/design-policies.md:62) and [physical-pin protocol](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/skills/kicad-pcb/references/pin-review-protocol.md:32).

The policy explicitly requires all manufacturer identities in the dossier. A manufacturer-fused land may collapse artifact pads only through an explicit cited alias mapping with `fused: true`, a reason and evidence. Agreement among an incomplete dossier, schematic and netlist cannot establish completeness.

Required correction: preserve drain identities 5–8 and declare the supported fused-land mapping, then regenerate the affected producer artifacts and obtain a fresh exact-subject review. Merely stating that all drains are electrically common does not satisfy this gate.

Severity is P0 because this is a mandatory pre-layout source-identity requirement. I am not asserting a missing conducting drain connection, defective PFET orientation or a demonstrated physical power failure.

### TOP-BDF-002 — P2: LDO capacitor evidence describes the wrong voltage/dielectric

The two TPS7A92 capacitor-bank entries in `power_tree.yaml` describe a “16 V X5R” budget while naming GRM32ER71A476KE15L. Its frozen exact-part dossier specifies 47 µF, 10 V, X7R. The source uses that same MPN for C_LDO_IN and C_LDO_OUT.

Evidence: the TPS7A92 input/output entries in [power_tree.yaml](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_src/rules/power_tree.yaml) and [exact capacitor dossier](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/GRM32ER71A476KE15L/part.yaml).

Correct the evidence prose to describe the selected part and applicable derating assumptions. This documentary mismatch did not produce a demonstrated voltage-rating or capacitance failure: the selected nominal voltage is above the local rail, and the declared conservative 0.34425 factor leaves 16.18 µF from each 47 µF capacitor.

No additional P1 finding is asserted.

## Electrical assessment

### Analog paths and ADC references

All eight paths retain the complete AN0556 unity-gain differential filter before isolation: OPA output → 10 Ω → FILTER node; 300 Ω feedback terminates at that FILTER node; 680 pF feedback capacitors return to the OPA outputs; 15 nF bridges the two FILTER nodes. Neither feedback leg bypasses the TMUX. Opening isolation therefore leaves the OPA feedback loops closed.

Each connector signal has its intended ESD channel, 1 µF AC coupling and 100 kΩ bias return. Every ADC-side leg has its own 100 kΩ ground bleed and 1 nF C0G capacitor. The input high-pass corner is approximately 1.59 Hz. The two added 1 nF shunts contribute 0.5 nF differential capacitance when connected—3.3% of the original 15 nF—not evidence by itself of instability or qualified audio performance.

The two OPA1656 reference followers are driven by external 10 kΩ/10 kΩ dividers, not the ADC VMID outputs. ADC VMID1/2 are separately bypassed. FILT1N and FILT2N return directly to GND; only the positive FILT feeds contain the intended 1 Ω series resistors. Internal LDO_D_FILT feeds VDD_D, with local bypassing; the exposed ADC pad is grounded.

These arrangements match CS5308P DS1314F1 pin tables, Fig.2-2 and §4.5.6, and AN0556R1 Fig.2, which I inspected independently. OPA1656 SBOS901C specifies a 4.5 V minimum supply and an input common-mode upper limit of V+−2.25 V. The 1.2 Vrms differential operating target leaves modest, not generous, upper-input headroom on a low 5 V rail. Temperature, divider mismatch and achieved supply drop remain relevant to first-article testing.

### ADC mode, timing and MCH boundary

The native configuration is consistent with hardware-mode, secondary-clocked 44.1/48 kHz operation: CONFIG1 has 4.7 kΩ to ground; CONFIG2 is tied high for minimum-slot TDM; CONFIG3 is grounded; CONFIG4 has 4.7 kΩ pull-up; CONFIG5 has 100 kΩ pull-down. The unused control pins and DOUTs have the specified hardware-mode grounding/pull-up/NC treatment.

The MCH primary manual confirms J1 pin 2 as TDM input, 9 as MCLK, 10 as BCLK, 11 as GND and 12 as FSYNC; J3 pin 2 is 3.3 V and pin 1 ground. Its TDM8 mode provides 256 BCLK periods per frame and eight 32-bit slots. The independently inspected MCH timing figure and CS5308P noninverted TDM convention are compatible at topology level. Authorized firmware identity and actual setup/hold timing remain unmeasured. Sources: MCHStreamer User Manual §§2.4,2.5.4 and Table12; CS5308P DS1314F1 Tables4-1–4-4 and §4.7.

The three clock inputs have 10 kΩ pull-downs and the SN74LVC3G34 boundary buffer; the TDM output uses SN74LVC1G125, with enable derived from the MCH sense divider and Schmitt inverter. The selected TI buffers specify Ioff at VCC=0, but that is not a blanket transition/hot-plug guarantee. MCH 3.3 V is sensed rather than tied to the carrier supply.

The reset supervisor and monostable implement the intended delayed high–low–high ADC reset sequence. TPS3839K33 specifies a 120–350 ms release delay; the 100 kΩ/220 nF monostable is a roughly 22 ms timing design. The primary tables do not guarantee that exact R/C combination over every corner, so actual reset pulse width and rapid-restart behavior remain owed. Sources: TPS3839 SBVS193D and SN74LVC1G123 SCES586E.

### Input protection and spoke delivery

Q_IN’s electrical orientation is correct: drain toward J9/F_IN, sources toward the protected rail, gate pull-down, and gate-source zener cathode at the sources. D_IN is a shunt TVS after the reverse-hookup element. This is reverse-hookup protection, not downstream reverse-energy isolation or sustained-overvoltage cutoff.

The 2920L260/33 input part’s published resistance maximum is 0.075 Ω and its 85°C table hold current is 1.27 A. The selected 1812L035/60 branch part has 1.700 Ω published post-trip/reflow maximum and 0.16 A table hold current at 85°C, above the 0.10 A per-spoke target. These resistance values are not guaranteed hot, installed path resistances. The manufacturer’s temperature tables and fault-test conditions require application qualification. Sources: [Littelfuse 2920L primary](https://www.littelfuse.com/assetdocs/resettable-ptcs-2920l-datasheet?assetguid=f237e8c2-1ed9-4c13-a738-dbe0738b3d2c), [1812L primary](https://www.littelfuse.com/assetdocs/resettable-ptcs-1812l-datasheet?assetguid=ca5c80cb-504e-4a8a-8e74-0107520a1717).

SMBJ15A’s specified 24.4 V clamp at its rated pulse point is below the AP63205’s recommended 32 V maximum input and the selected 50 V input capacitors. This comparison does not prove installed transient clamping, fault selectivity or sustained overvoltage survival. Source: [Littelfuse SMBJ primary](https://www.littelfuse.com/assetdocs/tvs-diodes-smbj-series-datasheet?assetguid=ba555e99-a12d-4f72-a0b6-86b06c67171e), AP63205 DS41326 Rev.3-2.

### Held input, precharge and discharge

D_HOLD points from raw 5 V toward the held input. The 22 Ω precharge resistor is bypassed by Q_PRE only after U_PWR releases. Q_PRE’s body diode does not create a path around D_HOLD back into the raw rail.

U_AUDIO’s manual-reset input is PWR_EN, so a raw-power failure commands analog isolation before the delayed dump. The two Schmitt stages provide the intended valid-logic relationship between dump and LDO enable. This does not resolve their below-recommended-supply cold-start interval.

TPS7A92 pin assignments, feedback, grounded SS_CTRL, 47 nF NR network, local input/output bypasses, NC PG and grounded exposed pad match SBVS318B. TMUX supply, grounds/EP and both shared enable inputs match SCDS488. The five 470 µF reservoir/reference capacitors have positive pin 1 on their respective positive rails.

## Independent numerical screens

These are calculations, not measured results. Unless stated otherwise, they retain the adopted prototype allowances: precision-resistor ±0.3125% per resistor, supervisor/reference ±1%, specified sense-input bias; electrolytic high/low multipliers 1.716/0.504; ceramic startup-high 1.265 and hold-low 0.34425. The resistor allowance is not the manufacturer’s complete life/reflow limit.

| Screen | Independently calculated result |
|---|---|
| TPS7A92 output, 3.57 kΩ/1.15 kΩ | 3.2353–3.3320 V |
| Raw supervisor falling threshold | 4.6315–4.7761 V |
| ADC supervisor falling / nominal-hysteresis rising screens | 3.1054–3.1969 V / 3.1243–3.2164 V |
| ADC-related charge inventory | 1060.98 µF nominal; 1766.08 µF upper screen |
| Raw and held minimum reservoirs | 301.91 µF raw; 489.94 µF held, excluding small held bypasses conservatively |
| Held startup capacitance including 1.2 µF logic bypasses | 1674.01 µF upper screen |
| NR charging-time screen | 3.917–9.999 ms |
| LDO startup current using rounded 3.34 V endpoint | 1.660 A versus 2.3 A minimum current-limit specification |
| Buck ripple / LDO-start peak | 1.438 A peak-to-peak / 2.479 A versus 2.5 A minimum peak limit |
| Cold-start buck peak, assumed 4 ms / 3.5 ms ramp | 2.387 A / 2.581 A |
| Minimum precharge delay / residual deficit | 298.35 ms / approximately 1.83 mV |
| External VMID 99% settling upper screen / AUDIO delay minimum | 324 ms / 597 ms |
| All-eight-channel steady 5 V estimate | 267.3 mA, including 20.3 mA signal-dependent supply current |
| Upstream current using full 300 mA allocation | 0.9639 A including eight 0.10 A spokes |
| Carrier-header floor | 11.4−1.0×0.2×1.2−0.10×2.2×1.2 = 10.896 V |
| LDO dissipation / reference-board temperature estimate | 308.6 mW / 102.6°C at 85°C ambient |
| LDO dropout margin at adopted held-input floor | 4.10−3.34−0.40 = 0.36 V |
| Conditional raw/OPA floor during 320 µs isolation interval | 4.5105 V: only 10.5 mV above the OPA minimum |
| Distributed discharge, main / FILT 90–10% | 6.340 ms / 8.023 ms |
| FILT tails to 5% / 1% | 11.020 ms / 16.896 ms |
| Total dump / precharge stored-energy screens | 9.85 mJ / approximately 22.2 mJ |

Important qualifications:

- AP63205’s 4 ms soft start is typical, not a guaranteed minimum. The 3.5 ms counterexample exceeds the 2.5 A peak-limit screen. It demonstrates why actual startup is owed; it does not establish that the documented prototype necessarily starts at 3.5 ms.
- TPS7A92’s NR charging-current specification is at NR=0. Its final charging tail means the simple calculation is not a guaranteed complete supply-ramp time.
- The discharge solution uses 1.2 Ω total dump resistance and 2 Ω per FILT feed/ESR path, with no credit for ADC current. Cirrus does not define the rise/fall endpoints used here; 90–10% is only the declared screen.
- A strengthened reverse-current screen charging 20 mA diode leakage throughout the initial 1.5 ms delay as well as afterward leaves a minimum held-input-minus-output margin of approximately 227 mV. This remains conditional on the 4.10 V initial held floor, delay and component/load assumptions. B340A’s 0.5 V forward-drop maximum is specified at 25°C, not a universal hot/cold drop bound.
- The ADC supervisor’s low threshold can be below the ADC’s 3.13 V recommended minimum. Its output therefore is not an unconditional “ADC in specification” signal. The normal input-removal claim relies on raw supervision, and output-only droop requires explicit observation.
- The thermal estimate uses TI’s reference-board θJA, not achieved PCB thermal resistance. Startup pulse and repeated dump heating are not closed by average power.
- At the TMUX specified leakage test points, 0.1 µA through 101 kΩ gives 10.1 mV. Typical 5 pC charge injection into 0.95 nF gives 5.26 mV; 99% bleed settling is approximately 0.488 ms. None establishes worst-case partial-VDD leakage, feedthrough or audio pops.

Primary authorities for these calculations: TPS7A92 SBVS318B §§6–7; TPS3890 SLVSD65A electrical characteristics; AP63205 DS41326 Rev.3-2; TMUX28xx SCDS488; OPA1656 SBOS901C; B340A DS30891 Rev.19-2; Panasonic FK ABA0000C1181; Vishay 20043; Yageo RT V17; and CS5308P DS1314F1.

## Unresolved work and exclusions

The adopted POWER-COLD, START, FALL, LOOP, REVERSE, AUDIO, DRIFT and THERMAL obligations remain owed. They require simultaneous power/control/analog captures, actual capacitor and ESR behavior, rapid restart and partial-power testing, loaded audio measurements, pulse-temperature checks and achievable PCB thermal evidence. MCH firmware identity, reset/TDM timing and both independent-power states also remain unqualified.

Hot four-wire delivery on all eight outputs, source fault behavior, connector polarity/continuity/fit and the staged current-limited first-power procedure remain mandatory. No hot-plug, destructive local-short, downstream-backdrive, production-life or outdoor-deployment qualification is inferred.

The stale PCB, placement, routing, copper, DRC/ERC geometry, fabrication, sourcing allocation, order readiness and schematic readability are outside this witness. Receiving this review grants none of those permissions.

Correct TOP-BDF-001 and re-gate the resulting exact source. Record TOP-BDF-002. The documented measurements owed are not substituted for the demonstrated missing-identity correction.
