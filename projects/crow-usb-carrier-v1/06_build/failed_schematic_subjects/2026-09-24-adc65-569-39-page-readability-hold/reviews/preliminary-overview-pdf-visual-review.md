---
review_kind: overview_only_pdf_visual
design_verdict: SOUND
scope: visual-render-only
candidate_status: noncanonical
pdf: /tmp/crow-569-overview-only-r2.pdf
pdf_sha256: 74c00fd8e8e227769cca3206de4e790fe0e49df15231f08fb9de72cc1e939179
pages: 39
---

# Independent visual review — Crow 569 overview-only candidate r2

## Bound subject and method

Reviewed only `/tmp/crow-569-overview-only-r2.pdf`, SHA-256
`74c00fd8e8e227769cca3206de4e790fe0e49df15231f08fb9de72cc1e939179`.
`pdfinfo` reports 39 pages, 900 x 607.5 pt pages, PDF 1.7, unencrypted.

Every page 1–39 was raster-reviewed at normal page scale (120 dpi). Pages 4,
23, 25, 30, 34, 35, and 36 received an additional 300-dpi inspection. “Legible
at zoom” below means that the zoom check, rather than ordinary whole-page
reading distance, established fine-label readability. This is a visual-render
review only: it makes no electrical-connectivity, source-authority, or release
claim.

## Verdict: SOUND

The candidate is visually sound as an **overview-only** schematic PDF. There
are no blank-body pages, cropped schematic boundaries, clipped labels, or
orphan detail tiles. Each page has the Crow USB Carrier v1 identity, a distinct
section heading, and its correct `Page N of 39` identity. Component references,
values, pin labels, and named nets render sharply; dense sheets are readable
at the stated 300-dpi check. Cross-sheet handoff is by repeated, descriptive
net labels (for example `ADC_BCLK`, `ADC_FSYNC`, `ADC_DOUT1`, `N3V3_ADC`, and
the named `*_NC` signals), which are comprehensible without a separate tile
map.

The prior 92-page PDF was defective because its generated detail-page tiles
were blank or edge-cropped and lacked continuation conventions. That specific
defect is absent here: this 39-page candidate deliberately contains the intact
overview sheets only, rather than presenting cropped detail pages as review
material. The corrigendum’s added capacitor is also visible on page 25 as
`C_ADC_3V3X_OK_VDD`, `100nF`, from `N3V3_ADC` to GND.

This is not a canonical acceptance: the authoritative producer and review gate
were not rerun for this candidate. The verdict applies solely to visual quality
of this exact PDF and does not remove other project holds or authorize ordering.

## Page-by-page normal-scale findings

| Page | Sheet | Finding |
|---:|---|---|
| 1 | Power input | Intact landscape sheet; input protection, net labels and capacitor values visible. |
| 2 | Power buck | Intact; regulator pins, feedback references and values visible. |
| 3 | Analog power aux | Intact sparse sheet; all three references/values visible. |
| 4 | Held LDO | Dense but intact; no clipped body; refs/nets/values legible at zoom. |
| 5 | Supervisors | Intact portrait sheet; two supervisor circuits and timing parts readable. |
| 6 | Dump | Intact; named nets and timing-bank values readable. |
| 7 | Spoke protection 1 | Intact; IC pin names, nets and values readable. |
| 8 | Spoke protection 2 | Same intact presentation as page 7. |
| 9 | Spoke protection 3 | Same intact presentation as page 7. |
| 10 | Spoke protection 4 | Same intact presentation as page 7. |
| 11 | Spoke protection 5 | Same intact presentation as page 7. |
| 12 | Spoke protection 6 | Same intact presentation as page 7. |
| 13 | Spoke protection 7 | Same intact presentation as page 7. |
| 14 | Spoke protection 8 | Same intact presentation as page 7. |
| 15 | Analog 1 | Intact; connector, amplifier, isolator, passive refs and nets readable. |
| 16 | Analog 2 | Intact; same readable structure as page 15. |
| 17 | Analog 3 | Intact; same readable structure as page 15. |
| 18 | Analog 4 | Intact; same readable structure as page 15. |
| 19 | Analog 5 | Intact; same readable structure as page 15. |
| 20 | Analog 6 | Intact; same readable structure as page 15. |
| 21 | Analog 7 | Intact; same readable structure as page 15. |
| 22 | Analog 8 | Intact; same readable structure as page 15. |
| 23 | ADC | Dense intact overview; dual ADC pin/net labels and bypass values legible at zoom. Explicit `GPIO1_NC` and `MICBIAS_NC` displays are visible. |
| 24 | VMID | Intact portrait sheet; divider/capacitor nets and values clear. |
| 25 | Reset supervisors | Dense intact overview; all named reset paths readable at zoom. Added `C_ADC_3V3X_OK_VDD` 100nF is visible and legible. |
| 26 | Reset sequencer | Intact; timing components, pin labels and reset nets readable. |
| 27 | Digital power 3V3X | Intact; regulator/monitor labels, nets and values readable. |
| 28 | Digital power 1V8 | Intact; regulator/monitor labels, nets and values readable. |
| 29 | Digital power core | Intact; regulator/monitor labels, nets and values readable. |
| 30 | XMOS core | Entire 128-pin symbol remains on one sheet, with no cropped body. Pin names, named net labels, and abundant `*_NC` pin display are legible at zoom. |
| 31 | XMOS decoupling | Intact; capacitor references, values and rail labels visible. |
| 32 | Flash clock | Intact; flash, crystal, reference and net labels readable. |
| 33 | Audio oscillator | Intact sparse sheet; oscillator and bypass labels/values clear. |
| 34 | TDM translation | Intact; translator pins, rails, cross-sheet signal labels and 100nF values legible at zoom. |
| 35 | FSYNC shaping | Intact; flip-flop/inverter/OR labels, named nets and bypass values legible at zoom. |
| 36 | ADC clock control | Dense portrait sheet, intact; I2C translator, clock safety logic, nets and values legible at zoom. |
| 37 | USB logic | Intact; FET, named VBUS nets and resistor values clear. |
| 38 | Debug | Intact; JTAG connector pins and `KEY_NC` display clear. |
| 39 | USB frontend | Intact portrait sheet; USB connector, ESD parts, CC nets and values readable. |

## Comparison to prior defective render

The earlier report and corrigendum identify a 92-page PDF whose overview sheets
were followed by defective crop tiles (including blank pages and symbols/nets
cut by page boundaries). This candidate has no corresponding detail tile range:
it ends at page 39 after the USB frontend overview. Its reviewed sheets retain
complete functional groups on a page. The prior P1 rendering defect therefore
does not recur. The corrigendum’s corrected component identity was used here:
the added part is `C_ADC_3V3X_OK_VDD`, not `C_ADC_DIGITAL_OK`.
