# Corrigendum — Crow 569 schematic-render handback

This immutable corrigendum corrects one narrow factual error in the original
render handback; it does not modify, supersede, or weaken that report's P1
finding or its `DEFECTIVE` / `DO-NOT-ORDER` verdict.

Original report: `/tmp/crow-569-schematic-review-render-terra-r1.md`  
Original report SHA-256: `a0cac14bcdb959cfd19b38caa590bd54bb9051415c2e2679320d51fe0cbf81d9`

Reviewed frozen PDF: `/tmp/crow-569-schematic-review-packet-20260924-terra-r1/subject/03_tscircuit/build/schematic.pdf`  
PDF SHA-256: `6a6be131d497e0d2b66f53b97501251a4f37ec3a64b2d4743f9af793b512e54b`

## Corrected P2 component identity

The original P2 paragraph incorrectly called `C_ADC_DIGITAL_OK` the new
bypass capacitor and cited detail page 47. `C_ADC_DIGITAL_OK` is an existing
capacitor. The sole added 569 capacitor is `C_ADC_3V3X_OK_VDD` (100 nF), as
bound by the Circuit JSON delta.

The added capacitor is legibly named, valued, and shown on the reset
supervisors overview, page 43. Its generated detail occurrence is page 48
(`RESET SUPERVISORS — DETAIL 5/9`), where the reference and 100 nF value are
present but the tile still crops surrounding active material and adjoining
connections. Therefore the narrow changed-cap detailed-context finding
survives, with `C_ADC_3V3X_OK_VDD` / page 48 substituted for the mistaken
existing-capacitor / page-47 statement.

This correction makes no electrical-connectivity claim. P1 remains: the
detail-tile representation is cropped, contains blank/fragmentary tiles, and
lacks usable continuation conventions. That independent readability defect
continues to block acceptance.
