subject: Crow USB Carrier v1 prototype-only source/schematic bundle 20260925T044907Z-581549
date: 2026-09-25
reviewer: independent Terra, direct high-resolution PDF raster recheck
context-given: exact private bundle and renderer-only candidate
source_commit: dddf4f63e3a5a42aa01e1f0c27f32811c38027d5
board_sha256: not-applicable (private source/schematic bundle contains no board)
design_verdict: SOUND
order_verdict: DO-NOT-ORDER

# Correction: XMOS appendix raster recheck

This dated recheck corrects the page-44/45 presentation finding in
`2026-09-25_prototype-only-schematic-render_terra.md`. That finding resulted
from the preview/downscaling path, not from the PDF's rendered page content.

I rendered the exact original private PDF and the renderer-only candidate with
`pdftocairo` at 300 dpi and inspected full pages 44 and 45 plus enlarged table
regions. Both PDFs show distinct table baselines and separated columns for
every row: page 44 covers pins 79--104 and page 45 covers pins 105--129,
including QSPI D0/D1 and EP/GND. No overprint or clipping is present in the
actual PDF raster.

The candidate is
`06_build/prototype_only/20260925T045900Z-581549-pin-index-layout/`.
Its circuit JSON, native schematic, and native netlist hashes exactly match
the original bundle: `580ac31…cb6d`, `758e29…4610`, and `a40b45…e9bd`.
The candidate PDF SHA-256 is
`c7a46f799696e7bae3399f26bc071df8cf09f9fc56a15c93f3cfbefe16ec627a`.

The render is readable as a prototype review subject. This correction concerns
only the prior visual claim. It is not a canonical pre-route witness and does
not alter the prototype-only selection, open ESD qualification finding,
electrical review, placement, routing, release, or order status.
