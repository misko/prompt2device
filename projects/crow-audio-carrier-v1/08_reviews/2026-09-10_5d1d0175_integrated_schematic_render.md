# Fresh integrated schematic readability witness

subject: crow-audio-carrier-v1
source_commit: 5d1d01757f4583fec61f795eb5803e98e2bf367f
date: 2026-09-10
completed_at: 2026-09-10T16:29:19Z
reviewer: Codex /root/carrier_native_fixed_readability
context-given: exact commission, immutable subject packet, supplied 19 page renders, repository method instructions, included source-intent documents
context_mode: FRESH
independence: independent visual and connectivity judgment; no prior independent reviews, dispositions, journals or STATUS consulted
review_stage: pre-route
review_kind: schematic_render
commission_sha256: be3861a15da06a27eae0c59c67e9da4b3d91b8fa6a5c1dd76777b7cb1fabc20a
subject_packet_sha256: 16623ca60af16237d2a24866e84c8291f3c89436ed286f9acd857595f6cb374c
netlist_sha256: 7190f3ba8b20280b81e39430fcbd5d5f06d182af30c5ac0ef87383dd98d19e29
parts_sha256: 2f76a9ca1a8b2e3cf948d3b43fbbbc6ad101f1fccd58de1d7ecd05c556b2f38d
design_rules_sha256: 672f0b9be3b3f9b6c2a9c9c1b1ea0e12ff4d91f061ede29ac36d6ac71965b8a4
circuit_json_sha256: 0e3836ba600c8b44c8929ca7c5053b9924054404073b183d5cff2e9e40a841a5
schematic_pdf_sha256: 9659f4b64ba5caef250a7647f4468f60336898d3909fbb5ce0ea270496359f39
native_schematic_sha256: 4c96d2ae398da1a9f83f8dd682ba9ea3ec788f6eea4cc94d1e2603d51bea69a9
raw_netlist_sha256: 986729171977ac50565978cd6f41470aa91251c99a6294d478eda5d07d760505
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER

The integrated readability lens fails on the native document defects below. The 19-page human PDF is readable and complete. This verdict concerns schematic presentation and its relationship to connectivity; it is not a full electrical-rating, PCB, sourcing, or release verdict.

## Method and independence

I visually inspected all supplied pages at their ordinary 120 dpi size, then examined dense analog, ADC, power and digital regions. Independently rerendering the exact PDF with Poppler produced pixel-identical images on all 19 pages. Text extraction supported reference lookup; it did not replace visual inspection.

I exported the untouched native schematic using KiCad 10.0.4 to PDF, SVG and XML netlist. I inspected its power, supervision, discharge, eight separate analog cells, ADC, both reference regions, clocks, TDM/presence and reset geometry. Native regions were inspected independently of PDF spacing. Private SVG viewports exposed additional detail and the reset geometry beyond the normal page; these change only the camera and do not repair the subject. The unedited exports remain available.

An independent union-find over circuit.json source ports/traces reconstructed 333 components, 937 pins and 178 connected nets. Every connected node set matches the fresh KiCad export; 42 additional singleton nets correspond to intentional floats. Native output contains 42 explicit no-connect flags. The source's leading-digit net-name escape (`N12V...`, `N3V3...`, etc.) explains 16 lexical name changes; it does not change connectivity. Direct TSX connection declarations and manufacturer pin descriptions were also read. KiCad printed an annotation warning; this review makes no clean-ERC claim.

For source intent I opened BRIEF and ARCHITECTURE. ARCHITECTURE contained embedded author progress/checker claims, which I incidentally saw and disclosed immediately to the coordinator. They were not used as acceptance evidence. All judgments here derive from my own current render, source, pin and net inspection. All 235 tar members matched the copied subject before and after review. The subject and live tree were never written. No OS-enforced read-only isolation is claimed.

## Findings

**R1 — P1, native page 1 / human PDF page 19: reset drawing is clipped.** The source declares paper `372.11 × 3137.53 mm`; both native exports use height `3048 mm` (PDF 8640 pt). `C_RST2` at `(100.330,3055.620)` and `R_RESET_GPD` at `(144.780,3055.620)` are outside the exported page. Their bodies, values and ground returns disappear. `C_RST1` at `(36.830,3042.920)` loses its value at y=3051.470 and part of its ground glyph. `Q_RST1` at `(176.530,3036.570)` intersects the drawing frame; its value lies at y=3048.930. A reader cannot follow the complete reset support circuit in an ordinary native export. The relevant nets are `3V3_ADC`, `RESET_PULSE_H`, `ADC_RESET_N` and `GND`. Reproduce by exporting the exact native schematic with `kicad-cli sch export pdf`; inspect the bottom edge. Correct the authored/native page arrangement and re-export the complete reset region.

**R2 — P2, native page 1 / PDF pages 3 and 16: electrolytic polarity is absent.** `C_HOLD1` `(127.000,394.970)`, `C_HOLD2` `(165.100,394.970)`, `C_FILT1_470U` `(72.390,2533.015)` and `C_FILT2_470U` `(72.390,2596.515)` render as plain rectangles with hidden pin numbers, unnamed pins and no polarity marks. The TSX explicitly marks these four EEEFK1A471P capacitors polarized; the human PDF correctly shows their positive terminals. Native pin 1 reaches `5V_LDO_HOLD`, `FILT1P` or `FILT2P`, and pin 2 reaches `GND`, so this is loss of visible polarity information. Emit recognizable polarized-capacitor geometry or explicit positive/negative terminal markings.

**R3 — P2, native page 1 / PDF page 6: a power flag occupies a capacitor body.** The GND `PWR_FLAG` anchored at `(300.990,876.935)` projects upward into `C_ADC_CM1N`, whose body spans x=295.275–306.705, y=869.315–876.935. Its diamond is visibly inside the yellow capacitor rectangle. This creates a composite symbol absent from the PDF and obscures the meaning of the ground attachment. Connectivity remains `C_ADC_CM1N.2 → GND`. Move the flag onto a clear external wire stub.

## Complete page coverage and checklist

| PDF page | Visually inspected content and result |
|---|---|
| 1 | J9 → F_IN → Q_IN → protected rail; TVS and gate-clamp polarity and grounds readable. |
| 2 | Input isolation diode, buck VIN/EN, bootstrap, switch/inductor, feedback, capacitors and rail bleed traceable. |
| 3 | D_HOLD, precharge/bypass, held capacitors and all LT3041 supply/control/ground pins readable; native R2. |
| 4 | Raw/ADC sense dividers, supervisor cascade, timing capacitors and enable pullups distinguishable. |
| 5 | Two Schmitt stages, delayed enable and Q_DUMP discharge path continuous. |
| 6 | Channel 1 complete P/N, bias, feedback, isolation and ADC shunts; native R3. |
| 7 | Channel 2 independently inspected, indexed labels and complete P/N paths. |
| 8 | Channel 3 independently inspected, indexed labels and complete P/N paths. |
| 9 | Channel 4 independently inspected, VMID1_EXT assignment and P/N paths. |
| 10 | Channel 5 independently inspected, VMID2_EXT assignment and P/N paths. |
| 11 | Channel 6 independently inspected, indexed labels and complete P/N paths. |
| 12 | Channel 7 independently inspected, indexed labels and complete P/N paths. |
| 13 | Channel 8 independently inspected, indexed labels and complete P/N paths. |
| 14 | All ADC input pairs, straps, reference pins, supplies, resets/clocks and DOUT NCs readable. |
| 15 | Two distinct passive external bias dividers and bypass banks readable. |
| 16 | Independent FILT and raw-VMID banks, positive electrolytic terminals and direct grounds readable; native R2. |
| 17 | J10 clocks, three buffer channels, 22 Ω output resistors and pulldowns traceable. |
| 18 | TDM return, J11 presence sense, Schmitt inversion and active-low output enable continuous. |
| 19 | Supervisor → monostable → reset NMOS and timing network complete in PDF; native R1. |

The functional flow is intelligible across the named page boundaries. Repeated ADCnP/N, VMID1/2_EXT, raw VMID1/2, supplies, enables and clock/TDM labels preserve distinct nets. Local decouplers and ground attachments are identifiable. Dense crossings in channel feedback and reset timing remain distinguishable on detail inspection. PDF identities and values are legible, with no observed text/body/plate collision. NC-labelled connector pins, ESD unused pins, LDO outputs and ADC DOUT2–4 have explicit native flags; the distinction between unused output and driven configuration input is maintained.

Primary-reference checks included Diodes DMP6023LFG DS37204 p.1 for source/drain/gate orientation; LT3041 Rev.A pp.7–8 for all 15 pin roles; Cirrus DS1314F1 pin descriptions and AN0556R1 p.4 Figure 2 for differential feedback; TI SCES366L and SCDS488 pin assignments; TI SCES586E p.3 and its clear-rising trigger description; and the miniDSP manual's TDM/power header information. For example, U_RST2 has A low, B high, CLR driven by POR_N, capacitor between pins 6/7 and resistor from pin 7 to supply. This supports the drawn sequence, without qualifying pulse width or transient behavior.

## Evidence locations and limits

Evidence root: `/tmp/carrier-fresh-render-witness.9Qqaj8/`.

- Unedited native exports: `native.pdf`, `svg/crow_audio_carrier_v1.svg`, `native.xml`.
- Unedited full render: `native-120dpi.png`; pixel-only reset/bottom crop: `native-presence.png` (x=0, y=13400, width=1758, height=1000).
- Detail evidence: `detail-hold-polarity.png`, `detail-afe1-flags.png`; viewport-only overflow inspection: `native-reset-overscan.png`.
- Integrity/connectivity records: `binding-before.json`, `tar-member-check-before.json`, `tar-member-check-after.json`, `independent-connectivity.json`, `pdf-render-confirmation.json`.

Native PDF SHA256: `7ea76267586a1ea579d006e94296a9f00c18dc332ba97fd910828093023c48f6`.
Native SVG SHA256: `9e2bb8874383f197cb647268128b55a53739a9478509572b3f084990c475d998`.

Physical layout, routing, fabrication, enclosure fit, sourcing/allocation, purchase authorization, first-article reset/TDM/analog/power-state measurements and outdoor qualification remain outside this lens and unclosed by it. Full rating calculations were excluded. DO-NOT-ORDER remains in force.
