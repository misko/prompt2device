# Fresh integrated schematic/native readability witness

subject: crow-audio-carrier-v1
source_commit: 74fd38dd3f6d35cf1f4fee7d0326d2ccdd9d4e38
date: 2026-09-10
reviewer: /root/carrier_complete_native_readability
agent-role: judgment
context_mode: FRESH
context-given: exact integrated-render commission, immutable source packet, nineteen provided 120dpi page renders, source commit and stated hashes; coordinator subsequently requested copies of my independently identified evidence.
independence: Independently inspected drawings, source pins/nets, native properties and primary references. No prior reviews, dispositions, journals, STATUS, or other agents' reasoning were consulted. ARCHITECTURE was not consulted; its embedded author progress/checker claims are expressly excluded from acceptance evidence. No machine verdict substitutes for this judgment.
review_stage: pre-route
review_kind: schematic_render
commission_sha256: 94ca0ad12aa9f4c945e3dc811776408d2e701f5c4442bcd343a1cadba71a3929
subject_packet_sha256: 29e5f80c288598593a4c38d254c3b27179b559e47866f99e7e557b8f8a677394
netlist_sha256: 7190f3ba8b20280b81e39430fcbd5d5f06d182af30c5ac0ef87383dd98d19e29
parts_sha256: 2f76a9ca1a8b2e3cf948d3b43fbbbc6ad101f1fccd58de1d7ecd05c556b2f38d
design_rules_sha256: 672f0b9be3b3f9b6c2a9c9c1b1ea0e12ff4d91f061ede29ac36d6ac71965b8a4
circuit_json_sha256: 6f8f629cc9932d3375969f6cf481b9a1429c201c2276cd97b6cb28cd99277d93
schematic_pdf_sha256: 84274c88878e0ac169ba089857d4dc8787be3e763c50fca7ff23ae407f7b2a0d
native_schematic_sha256: d1d0eecf7fb27c5dfbe8f5db5f431b8dcc344685db78df06409322dfd6f07b5d
raw_netlist_sha256: 299e616fdd8e9ae4f937d97f9bee85f542157e6a6ac2c0bfa8181c92b002893a
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
completed_at: 2026-09-10T17:05:07Z

## Judgment and method

The integrated presentation is defective because native component identity and inversion semantics are lost. This is a presentation verdict, not a finding that the compared electrical connections differ. The nineteen-page human PDF is readable within this lens; its better labeling does not cure the native representation.

All 235 tar members matched the copied subject before and after inspection; both verification outputs are identical. All commissioned raw/owning hashes were independently recalculated. Only the permitted digest methods were used from the named method source. Independent regeneration of all nineteen PDF pages at 120dpi produced pixels identical to the provided renders.

I exported the actual native schematic with KiCad 10.0.4 to netlist, SVG and PDF in private scratch. Its normalized netlist digest equals the commissioned owning digest. An independent graph reconstruction from circuit.json additionally found identical memberships for all 178 named nets, covering 895 connected component pins, plus 42 intentional single-pin unconnected nets: 937 source ports total. Exports printed an annotation warning; I did not convert that warning into an electrical verdict. Source and live tree remained untouched; all writes were private.

Evidence root: `/tmp/carrier-integrated-judgment.FgZbDW/`. Native evidence is the one-page `native.pdf`, SHA256 `33862b28fb36fa7b6b8e7d67d580a9fbc3194387c68b8322be17181c313140db`. Native coordinates below are millimetres in the actual schematic. `native-page-NN.png` are independent 120dpi regional renders, not alterations of the human PDF.

## Complete visual coverage

Every human page was inspected at ordinary viewing size; dense crossings received additional detail. Every corresponding native functional region was also visually inspected, including all eight repeated analog cells. Counts sum to all 333 component instances.

| Human PDF page | Components | Inspected content |
|---|---:|---|
| 1 | 6 | J9, fuse, reverse PFET, gate clamp, TVS |
| 2 | 13 | Buck, bootstrap, inductor, bypass, bleed |
| 3 | 13 | Precharge, held energy, LT3041 |
| 4 | 14 | Raw/ADC supervisors, audio enable |
| 5 | 10 | Delayed enable and discharge |
| 6 | 27 | Complete channel 1 |
| 7 | 27 | Complete channel 2 |
| 8 | 27 | Complete channel 3 |
| 9 | 27 | Complete channel 4 |
| 10 | 27 | Complete channel 5 |
| 11 | 27 | Complete channel 6 |
| 12 | 27 | Complete channel 7 |
| 13 | 27 | Complete channel 8 |
| 14 | 12 | ADC, configuration, supply/ground pins |
| 15 | 8 | Two passive external bias dividers |
| 16 | 12 | FILT banks and separate ADC VMID returns |
| 17 | 9 | MCH clocks, buffers, termination |
| 18 | 11 | Presence, Schmitt conditioning, TDM output |
| 19 | 9 | Supervisor/monostable/NMOS reset |

Unedited human evidence: `/tmp/carrier-complete-native-review-20260910.rdj0xya_/render/page-01.png` through `page-19.png`.

## Findings

**R1 — Major: native identities/critical value disappear.** Fifty-four of 333 nonpower native instances (54 of 67 generic chip instances) show supplier codes as Value and have no manufacturer-part-number instance property. For example, native page 1 Q_IN at (125.095,30.480) shows C780842, concealing DMP6023LFG-13; page 2 U_BUCK at (114.300,160.020) shows C2071056. L_BUCK at (165.100,160.020) shows C6937839, with neither XGL4020-332MEC nor 3.3 uH. Its nets are BUCK_SW/5V_BUCK. Reproduce in `native-page-01.png` and `native-page-02.png`, compared with human pages 1–2. Native ADC and connectors retain manufacturer identities, and the 146 capacitors/120 resistors retain numeric values; this finding does not allege that every instance is affected.

The complete affected set is F1–F8, U_ESD1–U_ESD8, U_AFE1–U_AFE8, U_ISO1–U_ISO8, Q_IN, D_QIN_GS, D_IN, D_BUCK_IN, U_BUCK, L_BUCK, U_LDO, D_HOLD, Q_PRE, Q_PRE_EN, U_PWR, U_AUDIO, U_DUMP, U_LDO_EN, Q_DUMP, U_CLK, U_TDM_SCH, U_TDM, U_OE, U_RST1, U_RST2 and Q_RST1. Exact page/coordinate/source-identity rows are in `native-opaque-identities.csv`, SHA256 `287ed5a7a63c1c1a899c66004112dbd7add12439beb90a727ee235a4d1c9d777`. Restore readable manufacturer identity and essential nominal values in native output.

**R2 — Major: native inverter behavior is invisible.** All three 74LVC1G14 instances use generic A_SCHMITT/Y blocks without an inversion mark or descriptive function: U_DUMP (113.030,665.480), U_LDO_EN (163.830,665.480), U_OE (160.020,2879.725). Inspect `native-page-05.png` and `native-page-18.png`; human counterparts are pages 5 and 18. The same generic shape represents the noninverting U_TDM_SCH at (147.320,2791.460). Nexperia independently identifies [74LVC1G14 as an inverter](https://www.nexperia.com/products/analog-logic-ics/logic/buffers-inverters-transceivers/inverters/serie/74lvc1g14) and [74LVC1G17 as a buffer](https://www.nexperia.com/products/analog-logic-ics/logic/buffers-inverters-transceivers/buffers/serie/74lvc1g17). Combined with R1's opaque values, the native drawing cannot communicate DUMP_RC→DUMP_GATE inversion, DUMP_GATE→LDO_EN inversion, or TDM_SENSE_G→TDM_OE_N inversion. This is a functional consequence within R1's affected population, not three additional missing components. Add explicit inversion/function semantics and retain the correct noninverting TDM conditioner.

## Checklist conclusions and boundaries

Primary paths were traced continuously from J9 through protection/buck/held LDO, and from each spoke through AC coupling, bias, amplifier feedback, filter, isolation and the correctly numbered ADC input. I checked actual OPA2320 and TMUX2821 pin tables. The source's passive external bias and two grounded filter capacitors per leg are visibly distinguishable from Cirrus AN0556 Figure 2; this review does not claim literal vendor-circuit equivalence or certify their performance.

Power polarity is traceable through named S/D/G and A/K pins; positive reservoir terminals, local bypass returns, ADC supply/ground attachment and separate VMID/FILT nets are clear. Human capacitor plates, values, component bodies and wire separation are readable. Suspected buck and supervisor crossings resolve to explicit bridges at detail, consistent with distinct native nets. Native passives use generic rectangles, but their units and reservoir polarity remain legible.

Cross-page ADC/TDM/reset continuity agrees with actual export. CS5308P DS1314F1 pin/configuration tables support the drawn input mapping, secondary TDM configuration and unused-output NC meaning. MiniDSP manual tables 3/12 support J10 clock/data pins and the intended 48kHz clock domain; J11 is presence-only. The reset wiring uses the SN74LVC1G123 CLR rising-edge trigger with A low/B high, Q driving the reset NMOS. Timing guarantees were not recalculated.

No full electrical-rating, physical PCB, thermal, sourcing, assembly or order acceptance is conferred. Exact COTS image/acquisition, cable fit, authenticated allocation, final fabrication checks, separate purchase authorization and first-article measurements remain required. DO-NOT-ORDER is unchanged. Coverage is complete for this commissioned lens; acceptance is withheld for R1/R2.
