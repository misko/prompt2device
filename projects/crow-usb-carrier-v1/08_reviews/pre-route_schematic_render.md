review_stage: pre-route
review_kind: schematic_render
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
subject: crow-usb-carrier-v1 canonical 78-page tscircuit schematic
reviewer: GPT-6 fresh independent visual schematic-readability lens
context-given: immutable pinned input packet; prior author review was context, not acceptance evidence
source_commit: 3008bcf1c964ec38acdf61547a194489840e8770
subject_raw_sha256: aaeb92599a7e1adc819ff818939b9509ea18d70319957f895cb0df84ae2fd61d
subject_semantic_sha256: e4a55b45c8032cedfc11e89b685921f6dfe307f85bfdb098a12c7e8be2ab05c8
schematic_pdf_sha256: d772e63d540d031f734d5877bb3c32eecbb7d736a996bec461ba78d65450a767
circuit_json_sha256: 4bbd4ca2d358814edf6617c2a2781253f2c4af8d63b3e0147081d916da64e138
netlist_raw_sha256: a8047cefa0c437294dda86f9569798984a4f5d4821d87027b103d7ec53dffe97
netlist_sha256: 99d3f71062394d97db1e64bfc93ef6958886378d2c5fb4a2148bb318900c6f31
parts_sha256: e708f4b59642e1df45320def4cecc2990586a0c0f4fd71b46aa94a2ff7004c83
design_rules_sha256: e431f396ca42849da4f7a5dffa3b60383093cd3b9faceec885f510c47a14146e

# Fresh independent schematic render review — 2026-09-23

**Decision: DEFECTIVE for the schematic readability gate.** The canonical PDF is a coherent 39-overview/39-detail document, but the overview-plus-detail pair does not make every essential reference complete and legible. This is a visual presentation decision, not an electrical-topology, native-conversion, PCB-layout, firmware, vendor, or purchase decision. The separate topology review does not cure missing or obscured drawing text.

## Method and coverage

I verified the pinned PDF and Circuit JSON raw SHA-256 values above, then rendered and opened **all 78 PDF pages individually at full page resolution (120 dpi)**. I followed the overview/detail page mapping: held LDO 4–13, ADC 32–36, reset supervisors 38–47, XMOS 52–61, FSYNC 66–70, and ADC clock control 71–75. All other overviews were viewed individually. For ambiguous details I also opened the exact PDF at 240 dpi. I compared the 568 unique `source_component.name` references in the pinned Circuit JSON against raw PDF text extraction; **566/568 complete exact names occur in the PDF text, 2/568 do not**. Text occurrence is only a census: it cannot establish visual legibility, so findings below rest on the page images. I examined active-part labels, important pin/net labels, visible NC indications, support groups, continuity across detail tile boundaries, and apparent wire/text collisions. This review did not trace every net electrically.

## Findings

1. **P1 — blocking, complete component references are clipped in both ADC views.** Page 32 (ADC overview) cuts off `C_ADC_B_IOVDD_100N` and `C_ADC_B_VREF_100N` at its right edge. Page 36 (ADC detail 4/4) also ends these names as `C_ADC_B_IOVDD_1` and `C_ADC_B_VREF_10` at the right tile boundary. Neither full reference appears anywhere in the 78-page PDF, confirmed by exact-reference comparison with Circuit JSON. A reader cannot identify those two capacitors from the delivered drawing alone. Enlarge/repartition the right ADC-B area or adjust the component labels, regenerate, and inspect both pages at page scale.

2. **P1 — blocking, reset support reference is covered by an unrelated net label.** On page 43 (RESET SUPERVISORS detail 5/9), the `ADC_DIGITAL_BAD` label box is printed across the middle of `C_ADC_DIGITAL_OK`; the reference cannot be read cleanly even at 240 dpi. The page-38 overview renders the same dense region too small to rescue the detail. Pages 39–41 also have reference/value text over long wires around `U_RST1`, `U_ADC_1V8_OK`, `U_ADC_3V3X_OK`, and `U_ADC_DIGITAL_BAD`; page 47 has a vertical `N5V_LDO_HOLD` label/wire through the `U_ADC_PWR_BAD` identifier. Repose the support labels and wires so the active references and capacitor reference have clear whitespace. Detail page 45 contains no circuit content; it is merely a wasteful tile, not a separate missing-component claim.

3. **P1 — blocking, TDM translator pin identities crowd into adjacent text with no detail alternative.** Page 65 is the only TDM TRANSLATION view. At page fit, `U_TDM_XLATE` (`SN74AXC4T245PWR`) has vertically congested pin names: `1DIR`/`1OE_N` and `2DIR`/`2OE_N` visually run together, as do the `1A*`, `2A*`, `1B*`, and `2B*` entries near their pin numbers and net labels. At 240 dpi the symbols can be decoded with effort, but they still occupy near-touching text rows, so the critical 1.8 V-to-3.3 V signal mapping is not independently reviewable at normal page scale. Give this active part more symbol height or a dedicated detail view.

4. **P2 — repeated label/reference interference in passive detail panels.** On HELD LDO detail pages 9, 12, and 13, `N5V_LDO_HOLD` boxes overprint the `C_HOLD*` references (especially `C_HOLD3`–`C_HOLD8`). On ADC detail pages 35–36, supply/reference labels overprint long `C_ADC_A_*` and `C_ADC_B_*` decoupler names. These names are mostly recoverable from nearby text or the overviews, but the detail panels fail their purpose of resolving dense labels. Correct the label offsets when fixing the blocking ADC clipping.

5. **P2 — clock-control reference has a wire through it, but remains identifiable.** On page 75, a green power/decoupling wire crosses `U_ADC_CLOCK_OK` (`SN74LVC1G125DCKT`) and its value. At page scale the ref is still decipherable, and at 240 dpi the wire clearly continues to the decoupler rather than indicating a new connection through text. This particular crossing is not an independent blocker and does not establish an electrical short; moving the reference text would remove the ambiguity. The page-71 overview is too small to resolve it alone, so the detail panel is the relevant evidence.

## Other observed scope

The eight spoke-protection overviews (pages 16–23) and eight repeated analog-channel overviews (24–31) use consistent flow and retain their per-channel identities. The ADC A/B active-pin panels (33–34) show input pairs, SCL/SDA, BCLK/FSYNC, reset, supply, and explicit NC markings clearly. The XMOS overview (52) is too small for pin reading, but the four symbol sides across detail pages 53–61 expose the 129 source pins and the critical reset, clock, USB, QSPI, TDM and JTAG labels at useful size. Detail page 57 is blank symbol interior; that is inefficient pagination, not evidence that a pin is missing. FSYNC (66–70), ADC clock-control functional labels (71–75), USB logic (76), JTAG (77), and USB frontend (78) show their intended sections and named inter-sheet nets. These observations do not assert correct connectivity or component ratings.

**Boundary:** This was a read-only review of the pinned PDF/Circuit JSON and supporting source snapshot. No producer was run and no source was changed. On the current PDF, the exact missing ADC references, the reset overprint, and the undetailed TDM pin crowding prevent a SOUND readability verdict. A regenerated PDF needs a fresh whole-page visual check and renewed hash binding before schematic admission.
