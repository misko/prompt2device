# TI ADC timing transition probe — 2026-09-25 UTC

**Research only; not a P1 placement acceptance.** The saved variants in
`2026-09-25-ti-adc-transition-probe/` bind the TI unrouted board SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`,
canonical interface and P1 requirements hashes, and their own floorplan and
candidate hashes in each result. No canonical source or board changed.

Terra moved the ADC east face from x=145 to x=149 and the audio-clock west
face to x=153, leaving a 4-mm transition over y=92..99.5. All 14 ADC timing
and control boundary witnesses are typed virtual faces with explicit P2
pad-to-face obligations. On the first saved variant, ADC common and control
rough capacity are 8/3 and 8/4 slots, but the TDM neck is only 2/4 slots at
0.45-mm pitch. A second saved `tdm-widen/` variant moves the audio-clock east
face from x=189 to x=188 and reserves `[188,94,190,99.84]`; it measures 4/4
rough slots, zero fixed/movable/copper obstacles, no timing-witness diagnostic,
and the timing allocation becomes `INCOMPLETE` rather than `FAIL`.

The wide floorplan is **not yet a truthful physical-cell model**: its
`adc_reference = [75,85,149,134]` overlaps
`digital_power = [145,99.84,185,134]` in the 4-mm strip below y=99.84.
The current coarse checker does not reject that unrelated whole-region overlap
because the new ADC virtual faces and reservations all stop before y=99.84.
The proposal needs a connected, separately declared ADC east lobe limited to
y<99.84 (or an equivalent nonoverlapping placement redesign) before source
promotion. Even then, 4/4 is only a rough potential bound: native effective
rules, filled return, actual P2 access and routed DRC remain owed.

The saved `two-cell/` probe tried that lobe with an anchored main ADC cell.
The checker stopped before allocation evaluation at
`adc_reference: unassigned native footprint/pad C_LDO_NR5 enters physical
cell`. A full native-envelope ownership census of the current
`adc_reference = [75,85,145,134]` rectangle finds **23 quiet-power
footprints** inside it, including U_LDO and the hold capacitors. Thus making
the entire functional ADC region an exclusive physical cell would require
major placement changes and is not an implicit requirement of the block
plan: `modular_pcb_design.md` allows interleaved functional blocks. A
source-owned shared transition or a smaller exclusive island may express the
specific handoff without falsely claiming the whole ADC rectangle is
exclusive. That option still needs its own exact native and source test.
