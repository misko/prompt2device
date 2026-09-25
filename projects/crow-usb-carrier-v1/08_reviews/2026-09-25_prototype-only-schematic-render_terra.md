subject: Crow USB Carrier v1 prototype-only source/schematic bundle 20260925T044907Z-581549
date: 2026-09-25
reviewer: independent Terra, visual schematic-readability lens
context-given: exact private bundle and receipt
source_commit: dddf4f63e3a5a42aa01e1f0c27f32811c38027d5
board_sha256: not-applicable (private source/schematic bundle contains no board)
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER

# Prototype-only schematic render review

This is a visual/readability review of the private 45-page PDF at
`06_build/prototype_only/20260925T044907Z-581549/schematic.pdf`, not a
canonical pre-route witness or an electrical, placement, routing, release, or
order decision. The receipt is `PROTOTYPE_ONLY` and expressly limits its scope
to source/schematic evidence.

## Exact subject

The receipt binds source commit `dddf4f63e3a5a42aa01e1f0c27f32811c38027d5`.
I recomputed and matched all four recorded artifact hashes:

| Artifact | SHA-256 |
| --- | --- |
| `circuit.json` | `580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d` |
| `crow_carrier.kicad_sch` | `758e29b0d9606a6b8f123a2dca474ce62871a85e08fb2fb9024c5a7a3d04610d` |
| `crow_carrier.net` | `a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd` |
| `schematic.pdf` | `d2e54c1195a217b231fbc2ab058e051b01dc8e45b534c65d38006978af386eed` |

The PDF is a 45-page, 900 x 607.5 pt document. I opened normal-page 180 dpi
rasters of pages 4, 23, 30--31, 34--36, 39, and 40--45, with direct detailed
inspection of the USB, XMOS, and appendix pages requested for this review.

## Findings

Page 39, **USB FRONTEND**, is readable for a bounded USB prototype discussion.
`J_USB`, `U_USB_ESD = TPD2EUSB30ADRTR`, the `USB_DP`/`USB_DN` labels, GND,
CC pulls, VBUS shunt, and bleed resistor are visible without an observed
collision or clipping. Pages 34--35 are also readable at normal page scale;
the TDM translator and FSYNC-shaping identities, pins, and nets can be
followed. The widely spaced held-LDO, ADC, XMOS-decoupling, and ADC-clock
pages have generous whitespace, although their distributed blocks require
ordinary page scanning.

Pages 40--43 solve the XMOS overview's intentionally dense 129-terminal
symbol with a clear title/summary and readable pin tables for pins 1--78.
The summary visibly binds 129/129 source pins to the fresh native netlist.

**Blocking presentation defect:** pages **44** and **45**, intended to cover
U_XU pins 79--104 and 105--129, do not render as usable tables. Their headers
and rows are compressed into the upper portion of the landscape page; the
`Pin`, package-name, net/NC, and function columns overlap. For example, the
rows around pins 93--104 and 115--129 merge the package pin name into the net
or function text. Pin 127/128 QSPI rows and pin 129 EP/GND cannot be read
reliably at normal page scale or in the inspected 180 dpi raster. This is not
an acceptable substitute for the dense overview, because those appendix pages
are the supplied readable pin-level witness.

## Disposition

The PDF is useful as a **USB-FRONTEND-only visual discussion subject**, but is
**not suitable as a complete prototype schematic review subject** until the
page-44/45 pin-index pagination/layout defect is repaired and the private
bundle is regenerated. Reinspect all six index pages after that repair; do not
transfer any verdict from this private PDF to the canonical pre-route review.
This DEFECTIVE render result makes no claim of an electrical connection error.
