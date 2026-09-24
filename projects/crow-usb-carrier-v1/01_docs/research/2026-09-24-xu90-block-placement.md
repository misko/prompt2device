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
