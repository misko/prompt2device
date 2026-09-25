# TI analog boundary source-capacity audit — 2026-09-25 UTC

**Research only; no P1 or route credit.** Subject is the exact TI unrouted
diagnostic board SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`,
the current `03_src/floorplan.yaml`, and the 59-net coarse candidate.

The source demand for `adc_analog_boundary` is nine F.Cu slots at 0.56 mm
pitch (**5.04 mm**) for channels 1–4 plus VMID1, and the same nine-slot
demand for channels 5–8 plus VMID2. The diagnostic candidate reserves
`analog_1_4 = [25,71,112.75,85]` and
`analog_5_8 = [113.25,71,201,85]`. Both rectangles cut through source cells
`analog_ch1`–`analog_ch8`, which extend to y=84. Converting the eighteen
movable native-pad witnesses to virtual south faces does not legitimize those
reservations: `_virtual_region_clearance` checks the reservation against
source-cell interiors after all witnesses have been parsed.

Without moving source-cell boundaries, the band immediately south of the
analog cells is only y=84..85: **1.00 mm**, less than the declared 5.04 mm
single-layer transverse demand. For channels 5–8, `audio_clock_tdm =
[145,72,190,99.84]` also occupies this band, so even that 1.00-mm strip is
not a disjoint shared corridor across the full group. The ADC reference cell
begins at y=85 over x=75..145. The native board has U_AFE courtyard edges
near y=79.145 in several channels and clock/TDM footprints within y=79..85,
so simply moving the south cell face north to make 5.04 mm of room requires a
fresh placement/courtyard and ownership check.

This is a **source floorplan/capacity problem**, not an error that can be
cleared by renaming boundary witnesses. The next geometry proposal should
allocate the actual 18 nets across disjoint per-channel or staged corridors,
or deliberately refloorplan movable analog/clock/ADC blocks and remeasure
the full-width F.Cu demand. Any multilayer alternative must bind layers,
transitions, return/reference continuity and native capacity. The existing
two nine-net rectangles should not be promoted as P1 geometry.
