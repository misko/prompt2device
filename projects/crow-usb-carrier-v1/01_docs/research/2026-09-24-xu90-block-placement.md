# XMOS 90-degree support-block placement probe — rejected

Commit `f5d59d08` anchored a rigid 90-degree rotation of `U_XU` and its 28
direct power/PLL support footprints through ordinary `placement.anchors`.
That candidate was later withdrawn from `floorplan.yaml`: a per-pin audit found
all 23 VDD/VDDIO capacitor pad-1 to matching XMOS-pin distances were 5.351 to
22.409 mm, with 17 above 10 mm. The source does not declare a numeric
decoupling-distance limit, so this is a placement-defect screen rather than an
electrical failure calculation; it nevertheless invalidates calling the poses
a local support block. A future XMOS block must reconstruct each local
decoupling and return relationship before a new P1 candidate.

An isolated generator-only probe produced a 569-footprint native board at
`/tmp/crow-p1-xu90-probe.YKwzFE/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`c4092002b20f351118ad9c27caf88626970b63dcbb30608278efa0e706f4036a`.
The generator reported no pad overlaps or fixed-courtyard overlaps. An
independent review then checked all 569 footprint courtyards and 1,807 copper
pads, including floating footprints, with no overlaps. It also verified the
29 new and 27 original anchors exactly.

This historical probe is not a P1 acceptance, native-DRC result, USB routing
proof, connector qualification, release, or order authorization. The four
named corridor allocations remain incomplete until a fresh, hash-bound
candidate demonstrates measured capacity and reference allocation. Connector
FULL remains incomplete on its 19 physical targets.

`U_USB_ESD` is also anchored at `[217.0, 36.0, 0]`. This is a collision-clean
connector-side starting point within `usb_frontend`, while retaining the fixed
JTAG connector pose. The corresponding isolated generator probe has SHA-256
`95d8878f8f6935cb6d0fa5904b8936b2a76afc7fca58a4efc60ab74402aa7afd` and
verified all 57 ordinary anchors, 135 post anchors, 569 courtyards, and 1,807
copper pads without an overlap. It does not demonstrate a short USB pair,
ESD return implementation, capacity reservation, or connector FULL.

The current source also anchors the six USB-C service parts outside the former direct
pair lane: `U_USB_CC_ESD` at `[233.3, 30.2, 0]`, `U_USB_VBUS_ESD` at
`[236.7, 30.2, 0]`, `C_USB_VBUS` at `[236.7, 33.7, 0]`, `R_USB_CC1` at
`[231.5, 33.7, 0]`, `R_USB_CC2` at `[231.5, 36.4, 0]`, and
`R_USB_VBUS_BLEED` at `[236.7, 36.4, 0]`.  A now-rejected authoring probe
reserved the external portion of an intended pair lane with the native
`p1_usb_pair_through_lane` F.Cu rule area from `[216.1, 36.745]` to
`[217.4, 91.305]`, denying footprints and pours. The probe is
`/tmp/crow-p1-usb-reservation-probe.XsZUCv/04_kicad/crow_carrier.kicad_pcb`,
SHA-256 `e3841ad0f4a39fcbd72b6817a1d409273e6e76e16cded9018a296f2f6af66341`.
It has 63 exact ordinary anchors and no positive-area pad or courtyard
collisions. It was removed from current source after the required 1.37 mm
pair envelope could not reach the XMOS USB pads without crossing pads 61–64.
`C_XU_VDD_104` blocks the current exit, but its pad 1 is already 17.2388 mm
from `U_XU.104`; this checkpoint cannot claim that its present pose is local
decoupling. The service block remains; the pair needs a different, qualified
escape strategy and the whole XMOS decoupling map must be rechecked.
