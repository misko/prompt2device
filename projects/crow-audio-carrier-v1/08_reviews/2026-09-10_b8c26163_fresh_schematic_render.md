# Independent schematic readability witness

subject: crow-audio-carrier-v1  
source_commit: b8c26163c6a264af5c184a64d0cf64e4d4e4e115  
date: 2026-09-10  
reviewer: carrier_schematic_readability_20260910, independent fresh-context agent  
context-given: Frozen commission, subject packet, unedited 120 dpi Poppler renders, and permitted binding-hash method only  
independence: Independent of design author; no prior reviews, dispositions, journals, STATUS, or author-checker verdicts consulted  
review_stage: pre-route  
review_kind: schematic_render  
design_verdict: DEFECTIVE  
order_verdict: DO-NOT-ORDER  
completed_at: 2026-09-10T03:28:56Z  

commission_sha256: 7df8a217ddc8d72c260c18274b450c7ffa20626a81f34c999a62847aed329e39  
subject_packet_sha256: ed1ac9f2f8f5f432259885d3fd0e0aab47f67b64a0c01aa757561f9b984f9590  
circuit_json_sha256: 1207938f7076659ae9bba0305dba320c88b5f1d08222bde2ecdfdd4b3e1447a5  
schematic_pdf_sha256: a60ecc459b40f6f7d7480a33ec54ed65cbd52dd05bda819eb88440466d5a3ab0  
native_schematic_sha256: d546f64709c99f8f958c03e0d8c5e692c95a22f975dfb2fe71dec849549c27c3  
native_netlist_raw_sha256: c4fa53111717a9413978aea1ea0af0ad9ba519eb2940884ad57e8d614a081d66  
netlist_sha256: ea6b7755b478e43eacc403f4b69797f3a800d0e05c45ddd26e875cc0bfa42512  
parts_sha256: 999609a09ecdf1b80be4238fbe138fd772d08577b282df38a1ed588dd0e5998d  
design_rules_sha256: 672f0b9be3b3f9b6c2a9c9c1b1ea0e12ff4d91f061ede29ac36d6ac71965b8a4  

## Verdict and integrity

The schematic-render review is complete: all 19 supplied pages were visually inspected. The PDF omits the `AUDIO_EN` cross-page connection on all eight channel sheets. A separate wire/reference overlap occurs on page 3.

DEFECTIVE applies to the schematic presentation, not to an asserted electrical connectivity defect. The source/native pin-net comparison agrees; that agreement does not supply information missing from the PDF.

The commission, packet, four raw artifact hashes, and three owning binding hashes were independently calculated and matched both before and after review. The subject was not edited. No files were written or promoted.

## Findings

### SR-01 — P1: AUDIO_EN continuity omitted on all eight channel sheets

Pages 6–13 show each isolation switch’s `SEL2` pin 3 and `SEL1` pin 7 joined by a short local U-shaped wire, without an `AUDIO_EN` label or an onward connection. Consequently, the PDF presents these controls as an isolated local connection and does not show their relationship to the supervision block on page 4.

The adjacent `GND`/`EP` wiring is separate; this finding does **not** allege that the selector pins are grounded.

The native `AUDIO_EN` net contains:

- `U_AUDIO.6`, `R_AUDIO_PU.2`, and `R_AUDIO_PD.1`.
- `U_ISO1.3` and `.7` through `U_ISO8.3` and `.7`.

The frozen circuit JSON contains only one `AUDIO_EN` schematic net label: `schematic_net_label_395`, on `schematic_sheet_3` (PDF page 4). It contains no corresponding channel-sheet label or `AUDIO_EN` schematic text.

The affected channel traces share the source geometry `(5.5, -1.7) → (5.5, -1.9) → (5.7, -1.9) → (5.7, -1.7)`:

| PDF page | Reference | Trace identity | Unedited evidence |
|---|---|---|---|
| 6 | U_ISO1 | schematic_trace_331 | [page-06.png](/tmp/carrier-schematic-review-20260910.C5vUhS/render/page-06.png) |
| 7 | U_ISO2 | schematic_trace_365 | [page-07.png](/tmp/carrier-schematic-review-20260910.C5vUhS/render/page-07.png) |
| 8 | U_ISO3 | schematic_trace_399 | [page-08.png](/tmp/carrier-schematic-review-20260910.C5vUhS/render/page-08.png) |
| 9 | U_ISO4 | schematic_trace_433 | [page-09.png](/tmp/carrier-schematic-review-20260910.C5vUhS/render/page-09.png) |
| 10 | U_ISO5 | schematic_trace_467 | [page-10.png](/tmp/carrier-schematic-review-20260910.C5vUhS/render/page-10.png) |
| 11 | U_ISO6 | schematic_trace_501 | [page-11.png](/tmp/carrier-schematic-review-20260910.C5vUhS/render/page-11.png) |
| 12 | U_ISO7 | schematic_trace_535 | [page-12.png](/tmp/carrier-schematic-review-20260910.C5vUhS/render/page-12.png) |
| 13 | U_ISO8 | schematic_trace_569 | [page-13.png](/tmp/carrier-schematic-review-20260910.C5vUhS/render/page-13.png) |

Reproducible raster region: approximately `x=1099–1124, y=521–595`, measured from the upper-left corner of each 1500 × 1013 image.

Required correction: attach a clearly visible `AUDIO_EN` label to the joined selector net on every channel page and regenerate the PDF.

### SR-02 — P2: LDO_NR wire crosses the U_LDO reference

On page 3, the upper horizontal `LDO_NR` wire from `U_LDO.9` (`SET`) crosses the `U_LDO` reference text.

Evidence: [unedited page-03.png](/tmp/carrier-schematic-review-20260910.C5vUhS/render/page-03.png), approximately `x=1073–1115, y=160–174`; the wire is at approximately `y=165` in the 1500 × 1013 image.

Exact frozen source identities:

- `schematic_trace_611`, net `LDO_NR`, includes the horizontal segment `(10.395, 3.2) → (5, 3.2)`.
- `schematic_text_97`, text `U_LDO`, is left-anchored at `(6, 3.15)`, font size `0.18`.
- Native `LDO_NR` connects `U_LDO.9`, `R_LDO_SET.1`, `C_LDO_NR4.1`, and `C_LDO_NR5.1`.

The reference remains decipherable, but the wire intrudes into its lettering and fails the requested identifier-overlap check.

Required correction: move the reference or reroute the presentation wire to provide clear separation, then regenerate the PDF.

## Visual coverage

Every listed page was opened with `view_image`; repeated channel sheets were individually inspected, not inferred from channel 1. Pages 3 and 6 were additionally reopened at original image detail.

| Page | Components | Inspected content and notable result |
|---|---:|---|
| 1 | 6 | Input connector, fuse, reverse-polarity MOSFET, gate clamp and input TVS; terminal polarity and ground attachments readable. |
| 2 | 13 | Buck input isolation, bootstrap, switching/output paths, bypass and discharge branch; primary paths traceable. |
| 3 | 13 | Held supply, precharge switch, LT3041 set/sense/return and capacitors; SR-02. |
| 4 | 14 | Raw-rail and ADC-rail supervision, timing and enable outputs; `AUDIO_EN` source label visible. |
| 5 | 10 | Delayed enable, Schmitt stages and ADC discharge MOSFET; named control paths readable. |
| 6 | 27 | Channel 1 connector, fuse, ESD, coupling, bias, buffer/filter, isolation and ADC loading; SR-01. |
| 7 | 27 | Channel 2 complete signal/power presentation; SR-01. |
| 8 | 27 | Channel 3 complete signal/power presentation; SR-01. |
| 9 | 27 | Channel 4 complete signal/power presentation; SR-01. |
| 10 | 27 | Channel 5 complete signal/power presentation, including VMID2_EXT assignment; SR-01. |
| 11 | 27 | Channel 6 complete signal/power presentation; SR-01. |
| 12 | 27 | Channel 7 complete signal/power presentation; SR-01. |
| 13 | 27 | Channel 8 complete signal/power presentation; SR-01. |
| 14 | 12 | ADC analog pairs, supply/configuration pins, clocks/data, bypass and unused outputs; identities readable. |
| 15 | 8 | Independent passive external-bias dividers and bypass; VMID1_EXT/VMID2_EXT distinguished. |
| 16 | 12 | Reference filter banks and ADC VMID bypass; independent nets and capacitor polarity readable. |
| 17 | 9 | MCH connector, clock buffers, pulldowns and source termination; clock flow traceable. |
| 18 | 11 | TDM conditioning, presence sensing, output enable and connector NC pins; flow traceable. |
| 19 | 9 | Reset supervisor, monostable timing, reset MOSFET and pullup; timing-node identities distinguishable. |

Total: **19/19 pages, 333 represented components.** No visual page coverage remains missing.

## Enumerated checks

1. **Functional flow and primary wires:** Inspected on every page. Analog and power paths are traceable; the missing isolation-enable continuation is SR-01.
2. **Power/protection polarity:** Inspected labeled A/K and G/S/D terminals, polarized capacitors, and rail connections. This was a presentation check, not a rating calculation.
3. **Identities and values:** Inspected all pages for readable references, device identities and passive values. SR-02 records the identified reference overlap.
4. **Ground/power attachment geometry:** Inspected capacitor terminals, common-return buses, IC supply/return pins and nearby crossings. The isolation select-pin loop is distinct from its adjacent ground wiring.
5. **No-connect meaning:** Compared the 42 intentionally unconnected source ports with native unconnected nets. Coverage includes U_ESD1–8, U_LDO, U_DUMP, U_LDO_EN, U_ADC, J10, J11, U_TDM_SCH and U_OE. The rendered NC identities agree with those native meanings.
6. **Same-net labels and cross-page continuity:** Inspected shared rails, ADC pairs, bias/reference nets, clocks, data, reset and enables. Missing `AUDIO_EN` labels are SR-01. Plain wire text on page 2 (`3V3_ADC`), page 5 (`PWR_EN`), page 18 (`TDM_RAW`) and page 19 (`ADC_RESET_N`) supplies continuity there; those are not omissions.
7. **Native-netlist consistency:** An independent parse compared all 937 source component/pin memberships against the 937 native netlist nodes, covering 333 components. There were zero membership differences after explicitly accounting for the source’s `N` prefix on numeric-leading rail names, such as `N3V3_ADC` versus native/displayed `3V3_ADC`. All 42 unconnected ports agreed. This supplemental check does not cure SR-01’s missing rendered information.

## Unresolved rows and boundaries

| Row | Status | Remaining work |
|---|---|---|
| SR-01 | OPEN — P1 | Restore AUDIO_EN labels on pages 6–13; regenerate and independently inspect the resulting render. |
| SR-02 | OPEN — P2 | Separate U_LDO reference text from the LDO_NR wire; regenerate and inspect page 3. |
| Required review coverage | COMPLETE | No missing pages or unfinished readability checks. |

No full component-rating calculations, manufacturer-topology qualification, physical PCB placement/routing, copper/DRC, thermal/fit qualification, sourcing, procurement or release-readiness determination was performed. Neither this witness nor source/native membership agreement authorizes ordering.
