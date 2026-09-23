---
review_stage: pre-route
review_kind: schematic_render
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
subject_raw_sha256: 39f7aa07c34cbe95b93448fa0116a927f48f6a6c70349e5a3caf4b7711319790
subject_semantic_sha256: d6ee9aa05a8cdcfda6e6ad2c421b822d4724cde4316fdc8a7180f8204be3c24d
circuit_json_sha256: f4097cb01771b00dcd459068f3655b7dcac93e42bce8242e4c4a6762a000c231
schematic_pdf_sha256: 5431a70e23f7b0bddbbaf4096b6c93bb3bb7a5a7dee5cb3a5c64a8930c3d7c7d
netlist_sha256: bd06331571ed870fdfbf3043fb1a8c89eaa5d7cff95bfd1a98494f31d01844e5
parts_sha256: e708f4b59642e1df45320def4cecc2990586a0c0f4fd71b46aa94a2ff7004c83
design_rules_sha256: 01cbdb3874b372c114280175932764c6bf8b7a168d69223f5ec90ec612590f4e
evidence: MEASURED
---

# Independent final schematic-render review

## Decision

**SOUND** for the reviewed 92-page PDF as a readable pre-route schematic render. This is a visual/readability verdict only. The retained procurement state is **DO-NOT-ORDER** because the topology witness still has conditional source, physical, and firmware evidence outstanding.

## Exact artifact and method

I independently opened every page of `03_tscircuit/build/schematic.pdf` at normal page scale (92 pages, 900 × 607.5 pt; rendered for inspection at 150 dpi). This was not a contact-sheet-only or text-census-only review. I also compared the PDF header binding on each page to the current circuit JSON hash above. The component source census is 568 references; all 568 distinct source references are present in PDF text and were covered by the normal-scale overview/detail inspection.

The 92 pages comprise 39 overview sheets and 53 detail panels. The header map is internally consistent: ADC overview 32/details 33–41; reset overview 43/details 44–52; XMOS overview 57/details 58–66; TDM overview 70/details 71–79; FSYNC overview 80/details 81–84; ADC-clock overview 85/details 86–89; USB logic 90, debug 91, and USB frontend 92. The remaining overview pages are 1–31, 42, and 53–69. Each detail header names its overview page and source sheet.

## Readability observations

- All 568 references are complete and legible collectively across their overview and detail panels. This includes the repaired ADC-B references `C_ADC_B_IOVDD_100N` (overview 32/detail 38) and `C_ADC_B_VREF_100N` (overview 32/detail 41).
- ADC pages 32–41 show both 25-pin converters, all required labels, passive support, and their panel continuity. Reset pages 43–52 make the reset and clock-qualification circuitry readable at detail scale.
- XMOS `U_XU` has 129 source ports. Overview 57 provides the whole perimeter; details 58–66 make all four sides, names, pin numbers, and explicit `_NC` marks readable. The empty center tile on page 62 is pagination whitespace, not omitted pins.
- `U_TDM_XLATE` has 16 ports. Its page-70 overview and pages 71–79 together show every port, labels, power/ground, and the arranged 16-pin perimeter. The blank interior detail tiles are expected tile space, not absent endpoints.
- Critical clock, FSYNC, USB, debug, power, analog, and crossed-tile net labels remain readable. No label collision made an endpoint, connection, or NC status ambiguous.

### P2 — compact but still readable labels

Page 44 places a vertical wire close to `U_ADC_1V8_OK`; its complete reference remains readable. Page 52 likewise keeps `C_ADC_PWR_BAD` complete and readable despite close neighboring graphics. These are nonblocking typography/spacing observations, not obscured text or a schematic defect.

## Limits

This review establishes render completeness and readability, not routing, thermal, source-fault, assembly, firmware, or purchase readiness. The separate topology bridge binds the current electrical carryover and its limits.

