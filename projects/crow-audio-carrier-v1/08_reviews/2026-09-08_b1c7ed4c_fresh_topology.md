subject: crow-audio-carrier-v1 schematic admission before placement
date: 2026-09-08
reviewer: Fresh independent read-only topology reviewer /root/carrier_topology_b1c7ed4c
context-given: Assigned TASK.md, commission.json, task-envelope.json and their frozen input packet; native netlist, source, current requirements and accepted ADRs, captured manufacturer documents, and all 19 schematic page images. No prior conversations or 08_reviews conclusions consumed.
source_commit: b1c7ed4c6ac5dcb0b098e6ee053f42538c0c7b69
review_stage: pre-route
review_kind: topology
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
netlist_sha256: 83b1c3510e0b08d9d4f390fac59403374073615f7bfcc8f6361308b51ce84c73
parts_sha256: daac58b921bd754063c6a28a3a63dad592d216a453e2c9f5d2b2cbbac2404bd9
design_rules_sha256: e33aea9d2b4136aee98781dc592ba4df6c7f7fec99353af5f3703cc4d1c72036
schematic_pdf_sha256: e6f14936611a78ac863ed660cff45160e25ca4b8aa08f6e73c16aaef722e3c07
subject_raw_sha256: 590585a0886903645572f82767a2b45a59cf918347cbb33d2d89870f07534a68
subject_semantic_sha256: e0cb30a69ac09d6b76b8f51939580eb73714afadef408ad8fc61de6af012b6d4
commission_id: CARRIER-TOPOLOGY-20260908-B1C7ED4C
completed_at: 2026-09-08T16:02:53Z

## Verdict and scope

SOUND for schematic admission to placement of the explicitly unqualified laboratory prototype. I found no established electrical defect requiring a schematic correction within that scope.

This verdict does not certify realized PCB behavior, physical qualification, assembly allocation, procurement, outdoor installation, or production release. Several narrow-margin calculations are conditional engineering screens rather than manufacturer-guaranteed system bounds. Their explicit qualification obligations remain intact. DO-NOT-ORDER remains the separate order verdict.

Project root for the exact evidence paths below:

`/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1`

## Packet integrity and independent work

`pipeline_execution.verify_input_packet` passed before review and again after review: **460/460 files, zero mismatches**. The final verification and unchanged source HEAD were confirmed at 16:02:53 UTC.

I independently reopened the native netlist and established **302 components, 207 nets including no-connect representation, and 877 pin-node assignments**. Recomputed normalized netlist, parts and design-rule hashes match the identities above. The parts digest includes all 78 dossier files; all 59 distinct populated MPNs resolve to dossiers whose declared primary-document hashes matched their captured bytes.

Connections and values were established from the native netlist and TSX, not inferred from a machine PASS. Independent arithmetic included the fresh capacitor inventory, divider corners, charging-current screens, discharge model, steady-current allocation and complete clock-to-returned-data timing path. All 19 rendered schematic pages were viewed. No project files were edited and no producers, commits or uploads were run.

Primary circuit evidence is the [native netlist](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/06_build/netlists/crow_audio_carrier_v1.net), with the frozen TSX and 19-page schematic from the commissioned packet.

## Required checklist

checklist: adc_configuration_and_references PASS

Schematic pages 14–16 and native `U_ADC` pins implement hardware secondary-mode TDM8: CONFIG1 pin 2 uses 4.7 kΩ to ground, CONFIG2 pin 3 uses 0 Ω to VDDA, CONFIG3 pin 4 is grounded, CONFIG4 pin 10 uses 4.7 kΩ to VDDA, and CONFIG5 pin 11 uses 100 kΩ to ground. These select the 44.1/48 kHz family, minimum-slot TDM, normal ordering and linear-phase fast-rolloff filtering with HPF enabled. DOUT2–4, pins 26–28, are unused.

VDDA1/2 and VDDIO are local `3V3_ADC`; LDO_D_FILT pin 32 supplies VDDD pin 33. Ground and paddle connections are present. FILT1P pin 43 and FILT2P pin 18 each have their own 1 Ω positive feed and 470 µF/10 µF/1 µF bank. FILT1N pin 44 and FILT2N pin 17 return directly to ground.

The hardware-mode mid-impedance requirement is respected: U_AFE9 senses two external 10 kΩ/10 kΩ half-supply dividers, not the ADC’s VMID outputs. Each follower closes feedback before its 100 Ω output isolator and 4.7 µF reservoir. ADC VMID pins 1 and 12 retain local decoupling only.

Authority: [CS5308P DS1314F1](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CS5308P-DN/CS5308P_DS1314F1.pdf), pp. 13, 19–21 and §4.5.6; [Cirrus schematic/layout guidelines](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CS5308P-DN/CS530x_Schematic_Layout_Guidelines_202507.pdf), §§1.6–1.9.

checklist: component_identity_and_ratings PASS

The populated identities and their primary-document bindings are complete for this schematic review. Voltage-domain checks cover the 60 V input PFET, 12 V gate clamp, 50 V buck-input capacitors, 32 V recommended buck input limit, 10 V power reservoirs, 63 V nonpolar signal-coupling film capacitors, held-rail logic/switch limits, and local 3.3 V interface devices.

The exact XGL4020-332MEC is 3.3 µH ±20%, with 34 mΩ maximum DCR and a published 3.5 A point for 20% inductance reduction at 25 °C. The source’s additional inductance and temperature treatment remains an engineering screen, not a new manufacturer guarantee. Q_DUMP AO3400A has a published 48 mΩ maximum at VGS = 2.5 V, ID = 3 A; its pulse and thermal conditions still require realized-board assessment.

Passive tolerances, capacitor derating factors, resistor drift allowances and room-temperature versus temperature-qualified semiconductor limits were distinguished. In particular, the RT-series 0.05% prototype drift allowance is not represented as the manufacturer’s all-life maximum. Exact assembly allocation and realized footprint/thermal performance are excluded from this verdict.

Authority includes the exact dossiers under `02_parts`, [Coilcraft Document 1529](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/XGL4020-332MEC/XGL4020_Document1529-3.pdf), p. 1, and [AO3400A Rev. 3.1](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/AO3400A/AO3400A_Rev3.1.pdf), pp. 1–2.

checklist: eight_analog_signal_paths PASS

Every channel was traced independently from its connector through both complete analog legs to the ADC:

| Channel | Connector P/N | ADC P/N pins | Bias bank |
|---|---|---|---|
| 1 | J1.3 / J1.4 | 40 / 39 | VMID1_BUF |
| 2 | J2.3 / J2.4 | 42 / 41 | VMID1_BUF |
| 3 | J3.3 / J3.4 | 46 / 45 | VMID1_BUF |
| 4 | J4.3 / J4.4 | 48 / 47 | VMID1_BUF |
| 5 | J5.3 / J5.4 | 14 / 13 | VMID2_BUF |
| 6 | J6.3 / J6.4 | 16 / 15 | VMID2_BUF |
| 7 | J7.3 / J7.4 | 20 / 19 | VMID2_BUF |
| 8 | J8.3 / J8.4 | 22 / 21 | VMID2_BUF |

Each channel has its own branch fuse and two-line ESD array; each signal leg contains 1 µF series coupling, 100 kΩ bias, the correct OPA1656 noninverting input and same-leg feedback, 300 Ω/680 pF feedback elements and 10 Ω output isolation. The 15 nF differential capacitor precedes the TMUX2821. Both switch channels are controlled by AUDIO_EN; each ADC-side node has 100 kΩ and 1 nF to ground. No feedback path bypasses the analog isolation switch.

The base filter matches the noninverting unity-gain topology in [Cirrus AN0556R1](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/CS5308P-DN/CS530x_Input_Buffer_Filter_Circuits_AN0556R1.pdf), Fig. 2, p. 4. Its nominal high-pass corner is 1.59 Hz. The added switch and ADC-side capacitance are intentional departures whose loaded stability, distortion and switching transients remain qualification work.

The admitted 1.2 Vrms differential signal produces approximately 0.849 V peak per leg. A 1.70 V upper VMID screen gives approximately 2.549 V maximum amplifier input, below the OPA1656’s 2.60 V common-mode ceiling at the declared 4.85 V rail floor. This is narrow but positive within the stated envelope, not permission to use the ADC’s nominal 2 Vrms full scale as the carrier input rating. See [OPA1656 SBOS901C](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/OPA1656IDR/OPA1656_SBOS901C.pdf), electrical-characteristics tables.

checklist: mch_clock_and_tdm_interface PASS

Pages 17–18 implement the official MCHStreamer direction and pin mapping: J10.9 MCLK, J10.10 BCLK and J10.12 FSYNC enter U_CLK; J10.2 receives returned TDM; J10.11 is ground. J11.1/2 are ground and remote 3.3 V presence sense only. No remote 3.3 V connection powers the carrier.

U_CLK’s three inputs have 10 kΩ defaults and its outputs pass through 22 Ω resistors to ADC pins 34, 29 and 24. ADC DOUT1 pin 25 reaches the 10 kΩ-biased TDM_RAW node, noninverting U_TDM_SCH, U_TDM and its 33 Ω output resistor. The Schmitt stage handles slow release from Hi-Z without feeding that RC decay directly into U_TDM’s ordinary CMOS input.

The four settled power states and both split-cable states have the intended ownership: absent MCH sense disables the return output; local power absence is handled at the Ioff-capable interface boundary; absent clocks have defaults. Hot insertion and glitch-free brownout behavior are not claimed.

The 48 kHz, 24.576 MHz MCLK, 12.288 MHz BCLK, eight-slot contract agrees with the captured miniDSP manual. The complete conditional return-path screen was independently reproduced:

`0.45 / 12.288 MHz − (4.1 + 10 + 5.5 + 4.5 + 6 + 5) ns = 1.521094 ns`.

The terms include incoming buffering, ADC launch/enable, Schmitt conditioning, outgoing buffering, allocated interconnect delay and allocated remote setup. The 10 ns Cirrus limit has its stated 25 °C/load conditions; remote setup, duty cycle, cable load, hold and actual edge rates are not established manufacturer system guarantees. Doubling BCLK is not admitted by this screen.

Authority: captured `external_hardware/minidsp_mchstreamer/MCHStreamer_User_Manual.pdf`, pp. 9–14 and 24; DS1314F1 pp. 14 and 34–36; exact TI SCES366L/SCES223U and Nexperia 74LVC1G17 Rev. 16 documents; [ADR-0005, including its current amendment](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/01_docs/decisions/0005-mch-power-domain-boundary.md).

checklist: power_entry_protection PASS

J9.1 feeds F_IN, then Q_IN’s drain; Q_IN’s source supplies `12V_PROTECTED`. The gate pull-down and correctly oriented gate-source zener support static reverse-hookup blocking. The input TVS is cathode-to-protected-rail/anode-to-ground. This is neither downstream reverse-current blocking nor sustained-overvoltage cutoff.

The exact SMBJ15A row gives 15 V standoff and 24.4 V maximum clamp at 24.6 A for its specified pulse conditions. The declared 20% voltage screen gives 29.28 V, below the selected buck’s 32 V recommended input ceiling and the 33/50/60 V series-element/capacitor/PFET ratings. That arithmetic does not certify arbitrary source impedance, pulse repetition or lightning survival.

F_IN’s published 85 °C reference hold current is 1.27 A; each selected 1812L035/60 branch has 0.16 A at 85 °C, above the declared 1.0 A trunk and 0.10 A branch allocations. Independently calculated trunk current is approximately 0.964 A. The declared resistance allocations and 20% charge produce the stated 10.896 V carrier-header floor. Thermal PPTCs are not precision current limiters; the branch 0.15 s trip point applies at 8 A, and its 10 A fault rating still constrains the external source.

The sixteen normal-operation audio conductors stay below approximately 3.50 V, within the TPD2E2U06’s 0–5.5 V recommended range. Component ESD ratings are not asserted as connector-to-ADC board survival.

Authority: [protection_paths.yaml](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/03_src/rules/protection_paths.yaml); exact Littelfuse SMBJ datasheet p. 2, 2920L datasheet pp. 1–2 and 1812L datasheet pp. 2–3; TI TPD2E2U06 SLLSEG9C pp. 3–4.

checklist: regulators_and_capacitor_corners PASS

The AP63205 VIN/EN, FB-to-output, SW-to-inductor and BST capacitor connections are correct. Three 10 µF input capacitors and three 47 µF output capacitors provide the intended derated input/output banks. The TPS7A92 IN/OUT pairs, ground/paddle, feedback divider, EN and NR network are correctly connected; SS_CTRL is grounded.

Independent divider arithmetic under the declared prototype allowances gives:

- LDO output: 3.23497–3.33240 V.
- Raw-power falling threshold: 4.63146–4.77613 V.
- Audio-rail falling threshold: 3.10541–3.19692 V.
- Maximum screened audio rising threshold: 3.22330 V, below the screened minimum settled LDO output.

The fresh charge inventory is **1,061.08 µF**, including the added TDM bypass. The conservative high-capacitance model is 1,766.2062 µF; this is a charge inventory, not an LDO loop-stability equivalent. Independent screens give 3.9174–9.9986 ms NR-controlled full ramp, approximately 1.6564 A LDO charging peak and 2.4755 A corresponding buck peak. The 4 ms raw-buck startup screen is 2.3870 A; a 3.5 ms assumption gives 2.5807 A and fails the 2.5 A minimum peak-limit screen. AP63205’s 4 ms soft start is typical, not a guaranteed minimum.

The selected capacitor values clear the cited effective minima under the declared derating model: internal-LDO capacitors 1.618 µF versus 0.8 µF; VMID bulk/HF 1.618/0.1618 µF versus 1.0/0.1 µF; FILT support 3.4425/0.3443 µF versus 2.2/0.22 µF. The external LDO’s 47 µF output capacitor also clears its effective-capacitance requirement under the stated factors.

Independent all-channel steady-current screen is approximately 267.3 mA against the 300 mA local allocation. The reference-board LDO thermal calculation is only a placement input: actual exposed-pad soldering, thermal resistance, filtered-bank stability, pulse temperatures and startup behavior remain unmeasured.

Authority: [AP63205 DS41326 Rev. 3-2](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/AP63205WU-7/AP63205_DS41326_Rev3-2.pdf), electrical tables and application guidance; [TPS7A92 SBVS318B](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/02_parts/TPS7A9201DSKR/TPS7A92_SBVS318B.pdf), pp. 3–5; Cirrus guideline §§1.6–1.9; exact capacitor dossiers.

checklist: requirements_and_scope PASS

The current BRIEF, requirements, architecture, spoke contract and accepted ADRs describe one synchronous eight-channel carrier, off-board MCHStreamer/USB/Pi functions, an external isolated regulated 11.4–13.2 V source, eight 0.10 A spokes and the restricted balanced-audio envelope. The inspected schematic implements those architectural boundaries without a second sampling domain or an unintended carrier-to-MCH supply connection.

[ADR-0007](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/01_docs/decisions/0007-prototype-before-physical-qualification.md) explicitly separates prototype schematic/design admission from physical measurements on the later assembly. It does not excuse known design defects. ADR-0008’s external VMID/direct-reference-return decisions and ADR-0009’s held-power/isolation intent are present in the native circuit.

The exclusion of realized PCB, assembly allocation and physical qualification is respected. This review does not claim routing, thermal, connector, source-fault or outdoor qualification, and does not grant order authority.

checklist: sequencing_partial_power PASS

The held-energy topology has the correct causal controls and polarity. D_HOLD permits raw-to-held charging while blocking bulk discharge into a collapsing raw rail. R_PRE limits initial charging; Q_PRE bypasses it after U_PWR’s delayed release. U_AUDIO’s MR input follows PWR_EN, so power-fail assertion commands analog isolation before the delayed dump/LDO-disable path.

U_DUMP and U_LDO_EN implement complementary dump/enable control. Q_DUMP’s source is grounded and its drain reaches `3V3_ADC` through R_DUMP. The two FILT banks remain represented through their own feed resistors during discharge. Independently integrating the declared no-load-assisted discharge model gives approximately **6.339 ms main-rail and 8.022 ms FILT 90–10% fall times**, with approximately **0.296 V minimum held-input-over-output margin**. FILT reaches 5% at approximately 11.019 ms and 1% at 16.895 ms: these tails are not hidden inside the 90–10% result.

The raw-rail hold screen leaves OPA supply at approximately **4.5105 V** when isolation is expected, only about 10 mV above its 4.5 V minimum. The detector delay, actual switch load, dump timing and held-rail leakage assumptions therefore remain important qualification limits.

Reset page 19 implements Cirrus’s required high–low–high startup sequence: TPS3839 delays monostable release, CLR rising triggers SN74LVC1G123 with A low/B high, and Q_RST1 pulls the ADC reset node low before the 10 kΩ pull-up restores it. The topology is correct; the monostable pulse-width calculation is not substituted for a guaranteed minimum or an oscilloscope result.

TMUX2821 pin maps, low-select isolation and powered-off protection are consistent with the actual primary document. Undefined/unspecified behavior in partial-supply regions—particularly held logic around 1.4–1.65 V and TMUX supply between 0 and 1.8 V—is explicitly not certified. Neither destructive internal 5 V shorts nor externally back-driven pods are admitted by the present contract.

Authority: [ADR-0009](/home/mouse9911/gits/circuits-worktrees/crow-roof-array-v1-20260901/projects/crow-audio-carrier-v1/01_docs/decisions/0009-held-power-and-analog-isolation.md); TPS3890 SLVSD65A pp. 4–6; TMUX28xx SCDS488 pp. 3–7; Nexperia 74LVC1G14 Rev. 19 pp. 5–6; TPS3839 SBVS193D; SN74LVC1G123 SCES586E; DS1314F1 p. 21, Table 4-5.

## Findings and retained limits

No P0, P1 or P2 schematic-correction finding was established within the commissioned laboratory-prototype admission scope.

The especially narrow startup, shutdown and TDM margins above must remain explicit in the next-stage handoff. Measured leakage, edge rates, reset timing, complete rail ramps, rapid restart, loop stability, analog switching behavior, pulse/thermal behavior and connector/source-fault qualification remain open physical obligations. Their absence is not represented as a passed physical test, and this SOUND schematic verdict does not close them.
