review_stage: pre-route
review_kind: schematic_render
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
circuit_json_sha256: 1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448
schematic_pdf_sha256: 28f6786549db410174ecde50128091891eb8778c7d97f1d10f23ec65fd0829fd
netlist_sha256: 7ab8c90f46ff4f25a9af50f43659a6b304e3c15932875519fa916fd018b1d8cc
parts_sha256: f864f336da4593f411873bc5955bd8fe472b18168827fe6e44cc7787d52d311d
design_rules_sha256: 8211187b0a0bb0ab38799ade9459944f0226cdf0180a75bcfdb94ca385a1a0c1
helper_path: review/pre_route_review_check.py
helper_sha256: b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e
packet_manifest_sha256: 1cadb2895230a120e927cc0ebfc57783b31bd57b9e990276e085b0ed256a9e88

# Formal schematic-render review

## Scope and binding

This is a fresh, read-only review of the isolated packet rooted at
`/tmp/crow-39-formal-review-terra-vDNAHk`.  The reviewed subject identity is
raw `4841591b695cd4b64a8d5e8cda729f1e0de703cecfff580128369481583e6aeb`
and semantic `4841591b695cd4b64a8d5e8cda729f1e0de703cecfff580128369481583e6aeb`.

I recomputed every manifest entry: 839 of 839 path, size, and SHA-256 pairs
match `packet-manifest.json`, whose SHA-256 is the header value above. The
current circuit JSON, PDF, raw native netlist, and checkpoint also match their
bound identities: raw netlist SHA-256 is
`8a1ad62eeb9da4b9e8574269c07d613aaf3c956e09096ee4d2adc11595b9e502`; the
header's netlist value is the independent normalization produced by the copied
helper. The helper found 112 complete `02_parts/*/part.yaml` records for the
parts digest and used the semantic design-rules projection for its rules digest.

`pdfinfo` reports an unencrypted, 39-page PDF, 900 x 607.5 points, rotation
zero. The supplied checkpoint SHA-256 is
`29060df769ecf08cb8e8c968d7b6b9f49a8263bff0a367498e1009807d43eba8`.

## Review method and coverage

All 39/39 pages were independently raster-inspected at normal page-fit scale:
pages 1--6 power and control; 7--14 spoke protection; 15--24 analog/ADC/VMID;
25--31 reset, digital rails, XMOS, and decoupling; and 32--39 flash, audio,
TDM, clock, USB, and debug. Every page has its expected title and `Page n of
39` identity; none is blank. The mandatory dense set, pages 4, 23, 25, 30, 34,
35, and 36, was also inspected at high zoom. Pages 5, 24, 36, and 39 use the
portrait-fit content arrangement; the other page layouts are landscape-fit.

The visual pass found no duplicate or blank legacy 92-page detail tiles. Text
extraction confirms exactly one page identity per page. The historical 92-page
archive was reopened only as an immutable failed defect record; its DEFECTIVE
verdict is not used or carried forward here.

I checked labels, refdes/value rendering, visible net connections, and no-connect
intent across the complete set. The packet's native schematic has 146 explicit
`no_connect` markers; representative unconnected intent remains plainly named
on the rendered XMOS, FSYNC, JTAG, and USB pages (`*_NC`, `KEY_NC`, `NC1`,
`NC2`, and `UNUSED_NC`). Cross-page label continuity was specifically traced
through the power/spoke `N12V_PROTECTED` family and the ADC path
`ADC_BCLK_RAW`/`ADC_FSYNC_RAW` from page 23 through TDM translation (34),
FSYNC shaping (35), clock control (36), and the XMOS interface. Those names
are also present in the frozen native netlist. This is a rendering/document
continuity check only, not an electrical-connectivity acceptance.

## Findings

### RENDER-001 — containment diagnostics remain unresolved (DEFECT)

The reviewed `circuit.json` contains 152
`schematic_element_outside_sheet_warning` records. They identify components,
labels, and traces extending outside the drawing area on eight rendered sheets:

| PDF page | Sheet | Warning count | Components / labels / traces |
| --- | --- | ---: | --- |
| 1 | POWER INPUT | 5 | 2 / 2 / 1 |
| 4 | HELD LDO | 5 | 0 / 2 / 3 |
| 23 | ADC | 3 | 0 / 3 / 0 |
| 25 | RESET SUPERVISORS | 27 | 6 / 12 / 9 |
| 26 | RESET SEQUENCER | 2 | 0 / 2 / 0 |
| 30 | XMOS CORE | 74 | 1 / 43 / 30 |
| 31 | XMOS DECOUPLING | 3 | 0 / 3 / 0 |
| 36 | ADC CLOCK CONTROL | 33 | 7 / 18 / 8 |

These diagnostics cover precisely the sheet containment, net-label, and trace
integrity the render review must establish. Page 30 also puts the full 129-pin
XMOS perimeter at a density where individual pin and local-label text is not
normally readable at page-fit scale; high zoom makes it decipherable but does
not cure the normal-scale document-readability failure. The page-fit raster
does not establish a sound, contained, normally legible schematic for those
affected sheets. Therefore the render design verdict is **DEFECTIVE**.

The PDF had no blank pages or observed overlap artifact that would independently
explain the defect; the current, hash-bound source diagnostic is sufficient and
must be repaired/re-rendered before a new fresh render review.

## Receipt reopening

The project freeze receipt was reopened and hash-checked:
`06_build/crow-39-formal-freeze-receipt.json`, SHA-256
`6498e96a512ab6bee141f76b230fb5b92849f56096793f4554e54970e4313233`.
It binds this packet, its 839 files, the subject identities, the PDF, circuit,
raw netlist, checkpoint, and the historical archive boundary.

The separate r3 render probe receipts named by the allocated envelope were
reopened and hash-checked: attempt
`59f8155d0be213039c6ecfe6afac583f2bd4f3990f7c3d403d96057017dd1b02`,
probe `9c85667648311652fda3815aaf1ef94e9758f19ab83c1a53aa4d19e37a9c9532`,
and result `bcc7bb208f9765fc74f374783f7be27584af41396bded61814cdc2a237fbba47`.
They record the current manifest, nonce `crow-39-render-probe-r2-bd460ae1`,
and exact subject, with terminal task status PASS, no unresolved items, and
READ_ONLY scope showing no changed paths. This is a valid current READ_ONLY
terminal PASS probe receipt; it is not this review and supplies no design
verdict.

## Holds

This report grants no positive gate, PR-REVIEW pass, production, order,
release, native installation, source change, or design promotion. The physical,
sourcing/order, placement, routing, first-article, and release holds remain;
`order_verdict: DO-NOT-ORDER` applies regardless of the render finding. The
containment and normal-readability defect requires a corrected frozen subject
and a new independent render review.
