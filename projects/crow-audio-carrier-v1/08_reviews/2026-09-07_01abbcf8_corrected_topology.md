# Independent pre-route topology and ratings review

design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
review_kind: topology
review_stage: pre-route
reviewer: Codex independent subagent /root/carrier_topology_corrected
review_context: Fresh bounded review of frozen prototype source; no previous review files or design-session transcript read
review_date: 2026-09-07
review_started_utc: 2026-09-07 19:35:12 UTC
review_completed_utc: 2026-09-07 19:48:40 UTC
netlist_sha256: 01abbcf8345dafff98b76cd53b3c75b5c86661a4d0b2e2be642bc6d78fd5a265
parts_sha256: 82a2b2853eaa520252dc67e53371bf8559f161146c49a4068026e4e62ed00ebb
design_rules_sha256: 3c66fafe15df75ae062c19a6e92dc6e1f708689a88fcb3808b9d2453a62a6fc9
raw_netlist_sha256: bc93b5062c2698487fb44304009c4a7ceff26133ffb7fc5f435cae2022a3149a
circuit_json_sha256: 4abfd28e0ee7ed4149d78aa5d44850962704b794ec99f612ce5db27d374a5470
schematic_sha256: c93cd0fa0853acf7c11db50d220363b881fb839fa4ce92161b7b1624abf0e5b3

## Verdict and scope

The current source is DEFECTIVE: the ADC unused SPI chip-select termination contradicts the manufacturer requirement, and an authored audio-transient ratings proof uses unsupported limits. Neither finding depends on having a physical prototype. Correct source and re-gate before accepting this topology witness.

ADR-0007 permits prototype design before physical qualification. Absent bench measurements are not themselves used to reject this design. SOUND would not mean tested, production-ready, or authorized to order.

Reviewed: the exact native netlist, circuit.json, native schematic, BRIEF, ADRs 0001–0005 and 0007, electrical/rail/protection/spoke rules, pertinent route intent and first-article criteria, and primary datasheet material. The review procedure and KiCad owning skill/pin-review instructions were read independently. No design, rule, part, or build file was changed.

## Exact-subject and coverage evidence

- Native subject: 06_build/netlists/crow_audio_carrier_v1.net; 206 components, 601 component pins, 564 connected pins, 37 intentional unconnected pins and 134 named electrical nets.
- Independently reconstructed circuit.json source-port-to-net membership: 601/601 pins agree with the native netlist, including floats. Numeric-prefix net presentation was normalized, for example N12V_POD1 to 12V_POD1.
- Re-exported 04_kicad/crow_audio_carrier_v1.kicad_sch with kicad-cli directly to stdout. Its normalized electrical digest equals the frozen netlist digest above.
- Integrated pass: 8/8 receive channels, 2/2 buffered VMID domains, ADC supplies/reference/mode pins, 8/8 spoke branches, input protection, buck/LDO, reset, 3/3 incoming clocks, outgoing TDM and four settled independent-power states.
- Census: 24 ICs, 3 MOSFETs, 11 connectors, 9 PPTCs, 2 diodes, 83 capacitors, 72 resistors, one ferrite and one inductor. Connectivity coverage does not imply complete all-corner passive qualification.
- Parts digest includes 62 part.yaml dossiers. All 18 dossiers declaring a local primary PDF have matching actual/declared SHA-256 bytes. Hash verification proves identity, not every dossier assertion.

Normalized hashes were computed by importing the current skills/kicad-pcb/scripts/pre_route_review_check.py and calling netlist_digest and design_rules_digest. The parts hash uses that script's exact algorithm: sort PROJECT/02_parts/*/part.yaml; concatenate each project-relative POSIX path encoded as bytes, NUL, exact file bytes, NUL; SHA-256 the concatenation. Raw hashes separately bind the three exact artifacts.

## Blocking findings

### T1 — P0: unused U_ADC.38 SPI_CS is grounded instead of tied to VDD_IO

Actual U_ADC.38 connectivity is GND in the netlist, independently matched circuit.json, and schematic re-export.

Cirrus DS1314F1 section 1.3, Table 1-2, PDF page 6, places unused SPI_CS in the Connect to VDD_IO group together with RESET. SPI_SDO/I2C_SCL, SPI_SCK, SPI_SDI/I2C_SDA and unused CONFIG pins are the separate ground-termination group. I rendered and visually checked the merged table cells rather than relying only on flattened text. Pages 4–5 identify pin 38 as SPI_CS. This design selects hardware mode and does not use the SPI port. [Cirrus DS1314F1](https://statics.cirrus.com/pubs/proDatasheet/CS5308P_DS1314F1.pdf)

Required correction: tie SPI_CS to the actual VDD_IO rail, 3V3_ADC, in authoritative source and corresponding assertions; regenerate and re-review. No physical malfunction is asserted or needed to establish this violation of an explicit vendor termination requirement.

### R1 — P0: audio protection contract uses unsupported guaranteed limits

03_src/rules/protection_paths.yaml lines 43–50 sets clamp_max_V: 12.4, associates it with an 8/20-us waveform and 5.5-A peak, derives bounded_max_V: 13.64, and assigns U_ESD1–U_ESD8 recommended_max_V: 14 and absolute_max_V: 14.

Exact TI SLLSEG9C pages 3–4 instead show 12.4 V as TYPICAL at 5-A TLP, with 10-ns rise and 100-ns width. The 5.5-A 8/20-us peak-pulse rating is separate. Normal recommended VIO is 0–5.5 V; those tables publish neither a 14-V recommended operating voltage nor a 14-V absolute maximum voltage. Clamping above the working voltage is expected, but does not create such a voltage rating. [TI SLLSEG9C](https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf)

The dossier correctly calls its 1-A clamp observation typical; the unsupported promotion occurs in the machine-readable rule. Ten percent added to a typical value cannot make it a manufacturer maximum or transfer it between waveforms.

Required correction: replace or explicitly withdraw the unsupported transient-coordination claim through the owning source contract/schema. A declared unqualified prototype ESD selection is distinct from guaranteed surge survival. If the latter claim is retained, it needs valid waveform-specific authority and downstream analog-input coverage, not only clamp and coupling-capacitor bodies. This is a source-ratings defect, not a demand for pre-layout surge testing.

## Integrated observations

### Revised MCH networks

All six current resistors have the intended values/connections:

| References | Value | Connection |
|---|---:|---|
| R_MCH_MCLK_PD, R_MCH_BCLK_PD, R_MCH_FSYNC_PD | 10 kΩ each | Respective MCH input to GND |
| R_TDM_OE_PU | 10 kΩ | 3V3_ADC to TDM_OE_N |
| R_MCH_SENSE | 300 Ω | MCH_3V3_SENSE to TDM_SENSE_G |
| R_MCH_SENSE_PD | 10 kΩ | TDM_SENSE_G to GND |

Circuit.json identifies all five 10-kΩ parts as RC0402FR-0710KL/C60490 and the 300-Ω part as RC0402FR-07300RL/C138010. U_CLK inputs 1/3/6 and outputs 7/5/2 preserve MCLK/BCLK/FSYNC. U_TDM pins 1/2/3/4/5 are OE_N/A/GND/Y/VCC. Q_TDM_EN gate/source/drain reach sense/GND/OE_N.

TI SCES366L pp.4–5 and SCES223U pp.5–6 specify 0.8-V maximum VIL, 2.0-V minimum VIH at 3–3.6 V, ±5-µA input leakage and ±10-µA Ioff at VCC=0. Diodes DS30896 Rev.20-2 p.3 specifies ±10-µA gate leakage at its stated condition and is explicitly a 25°C table. It does not guarantee low-VDS on-resistance at 2.8-V gate drive.

check_clock_defaults.py ran without writing an output and reproduced all 8 arithmetic predicates: clock receiver-only low 0.0515 V, allocated low 0.2575 V, driver load 0.376134 mA, absent sense gate 0.206 V, present gate 2.901394 V, sense load 0.380324 mA, disabled OE 2.691 V and enabled OE current burden 0.376134 mA.

These calculations are valid UNDER ADR-0005's allocations. The ±3% resistance allowance, additional leakage, module-driver capability and low-drive transistor behavior are not manufacturer guarantees. Threshold voltage is not RDS(on). The source correctly distinguishes these engineering budgets. [TI clock buffer](https://www.ti.com/lit/ds/symlink/sn74lvc3g34.pdf), [TI data buffer](https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf), [Diodes MOSFET](https://www.diodes.com/assets/Datasheets/ds30896.pdf)

The miniDSP manual supports 3.3-V logic, J3.2 supply output, 24.576/12.288-MHz TDM clocks at 48 kHz, eight 32-bit slots and 24-bit input interpretation. J10 uses 2/9/10/11/12; J11 only 1/2. There is no carrier-to-MCH supply feed. Ioff and local bias support the four settled power-state topology cases subject to the declared allocations; split-cable behavior is not a glitch-free insertion guarantee. [miniDSP manual](https://www.minidsp.com/images/documents/MCHStreamer%20User%20Manual.pdf)

### ADC, analog and references

Except T1, the checked ADC functions/straps are consistent: 5/9/31 use 3V3_ADC; 33 VDD_D joins 32 LDO_D_FILT, not 3.3 V; grounds/paddle join GND. CONFIG1=4.7 kΩ down, CONFIG2=0 Ω up, CONFIG3=GND, CONFIG4=4.7 kΩ up, CONFIG5=100 kΩ down. DS1314F1 Tables 4-1–4-4 select secondary 44.1/48-kHz-family, minimum-slot TDM, default order and linear-phase fast-rolloff/HPF. DOUT1 is used; DOUT2–4 intentionally float.

ADC P/N pin pairs for channels 1–8 are 40/39, 42/41, 46/45, 48/47, 14/13, 16/15, 20/19 and 22/21. All eight paths preserve order/polarity.

Each receive cell has two 1-µF coupling capacitors and 100-kΩ buffered-VMID bias resistors. OPA1656 pins 3/5 take biased inputs, 2/6 are corresponding inverting nodes, 1/7 outputs. Each 300-Ω feedback resistor returns from the SAME ADC leg after its 10-Ω output resistor; 680-pF feedback returns to the raw output. Each 15-nF capacitor spans its own differential pair. This matches AN0556R1 Figure 2/Table 3: unity nominal gain, 1.59-Hz high-pass and approximately 640-kHz low-pass.

U_AFE9 closes each follower at the raw output before 100-Ω isolation and 4.7-µF polarized shunt; channels 1–4 use VMID1_BUF, 5–8 VMID2_BUF. AN0556R1 section 4.2/Figure 14 supports this buffered ADC_VMID source. The Cirrus July-2025 layout-guidelines PDF was independently retrieved from its official ZIP in memory; SHA a97e3cfbe311caf603bd56b7aeab189dd38727104168c26bb67dd24add07b62f. Sections 1.6–1.9 confirm the adopted effective minima. The declared 0.34425 derating factor leaves 1.618 µF from 4.7 µF, 0.1618 µF from 470 nF, 0.34425 µF from 1 µF and 3.4425 µF from 10 µF, above corresponding minima. These are engineering derating assumptions, not measured lot curves.

OPA1656 SBOS901C p.6 gives input common mode through V+−2.25 V. At 4.85-V supply, first-article VMID ceiling 1.70 V and balanced 1.2-Vrms differential input, the upper leg reaches 2.5485 V, leaving about 51.5 mV to 2.60 V. This narrow conditional budget does not permit the ADC's nominal 2-Vrms full scale at this carrier connector.

### Power and reset

J9 feeds F_IN then PFET drain; sources reach 12V_PROTECTED. The gate clamp cathode is on that source rail, anode on gate; R_QIN_G pulls gate down. D_IN cathode is on protected positive. DS37204 pp.1–2 supports the arrangement and −60-V/±20-V limits. This blocks reverse hookup, not energy from an independently powered downstream rail.

All eight PPTCs feed only their own headers. Independently reopened Littelfuse tables support 2920L260/33 R1max 0.075 Ω and 70/85°C hold 1.60/1.27 A; 1812L035/60 R1max 1.700 Ω, hold 0.20/0.16 A and 10-A fault rating. Adopted allocations give 11.4−1.2×1.0×0.200−1.2×0.10×2.200 = 10.896 V. This does not prove hot drop or fault selectivity. [Input PPTC](https://www.littelfuse.com/assetdocs/resettable-ptcs-2920l-datasheet?assetguid=f237e8c2-1ed9-4c13-a738-dbe0738b3d2c), [branch PPTC](https://www.littelfuse.com/assetdocs/resettable-ptcs-1812l-datasheet?assetguid=ca5c80cb-504e-4a8a-8e74-0107520a1717)

AP63205 fixed-output FB senses 5V_BUCK; EN joins VIN; bootstrap capacitance is BST-to-SW. The 3.3-µH XGL4020 is within the 2.2–10-µH application range, with 34-mΩ maximum DCR below the 100-mΩ recommendation. TPS7A2433 IN/EN use 5V_BUCK, OUT uses 3V3_ADC, fixed-variant pin 4 floats. Its output tolerance gives 3.25875–3.34125 V, inside ADC analog supply limits.

TPS3839K33 drives monostable CLR; SN74LVC1G123 A is low and B high, so CLR rising triggers Q and Q_RST1 pulls ADC_RESET_N low. Rext=100 kΩ to VCC and Cext=220 nF between 7/6 are correct. Supervisor minimum delay 120 ms exceeds the 2-ms pre-pulse wait. The approximately 22-ms RC pulse is not a guaranteed minimum; exact reset/brownout waveforms remain first-article work under ADR-0007.

## Unresolved engineering risks, not asserted physical failures

- OE slew needs a dedicated check. SCES223U requires 10 ns/V at 3.3 V. An illustrative 4-pF input-only model with 10-kΩ pull-up takes about 26 ns from 0.8 to 2.0 V; drain/board capacitance and slow sense transitions may worsen it. This is a typical-capacitance model, not a measured failure. DC bias does not establish transition compliance; a stronger driver/Schmitt-qualified strategy may be needed.
- Reconcile LDO thermal assumptions before claiming the full load/temperature envelope: power_tree.yaml permits 150 mA/400 mW, while its dossier derives 238 mW at 85°C using 167.8°C/W and TJ=125°C. At 5.15 V input and 3.25875 V output, 150 mA dissipates 283.7 mW and predicts 132.6°C under that model. Actual load, copper and ambient are not established by that calculation.
- The two 470-µF reference banks load 3V3_ADC through their feed resistors. Startup/dynamic capacitance must include them, not just C_LDO_OUT. ADC supply ramp (specified 0.01–10 ms), LDO stability and reference settling remain unmeasured.
- Firmware identity, cable continuity/orientation/fit, noise/THD/phase, hot all-eight delivery, one-fault/seven-healthy behavior and outdoor transients remain first-article/system obligations. No physical PASS is supplied.

## Limits and handoff

This bounded pass did not complete an exhaustive independent all-corner audit of every passive dossier, material curve or resistor pulse-energy condition. Package winding, lands, placement, render readability, routed return paths, realized timing, fabrication, assembly and sourcing are separate lenses and are not approved here.

Both blockers were reported promptly to the commissioning agent. Correct T1/R1, rerun affected gates and bind review to new hashes. This witness grants no exception for unreviewed corrections. DO-NOT-ORDER remains unconditional for this artifact.
