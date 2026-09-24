# XMOS 90-degree support-block placement probe

The current `floorplan.yaml` anchors a reviewed rigid 90-degree rotation of
`U_XU` and its 28 direct power/PLL support footprints.  It uses ordinary
`placement.anchors`, so the complete block is present when the legalizer
places all remaining floating footprints.  The pre-existing 27 connector and
hold-bank anchors are unchanged.

An isolated generator-only probe produced a 569-footprint native board at
`/tmp/crow-p1-xu90-probe.YKwzFE/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`c4092002b20f351118ad9c27caf88626970b63dcbb30608278efa0e706f4036a`.
The generator reported no pad overlaps or fixed-courtyard overlaps. An
independent review then checked all 569 footprint courtyards and 1,807 copper
pads, including floating footprints, with no overlaps. It also verified the
29 new and 27 original anchors exactly.

This is a P1 placement-authoring checkpoint only. It is not a P1 acceptance,
native-DRC result, USB routing proof, connector qualification, release, or
order authorization. The transformed XMOS faces reopen USB, QSPI, JTAG,
crystal, and ADC-timing reservation work. The four named corridor allocations
remain incomplete until a fresh, hash-bound candidate demonstrates measured
capacity and reference allocation. Connector FULL remains incomplete on its
19 physical targets.

`U_USB_ESD` is also anchored at `[217.0, 36.0, 0]`. This is a collision-clean
connector-side starting point within `usb_frontend`, while retaining the fixed
JTAG connector pose. The corresponding isolated generator probe has SHA-256
`95d8878f8f6935cb6d0fa5904b8936b2a76afc7fca58a4efc60ab74402aa7afd` and
verified all 57 ordinary anchors, 135 post anchors, 569 courtyards, and 1,807
copper pads without an overlap. It does not demonstrate a short USB pair,
ESD return implementation, capacity reservation, or connector FULL.
