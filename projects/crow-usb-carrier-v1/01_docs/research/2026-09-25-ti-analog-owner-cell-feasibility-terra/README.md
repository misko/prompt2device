# Analog ch2/ch3/ch4 complete physical-cell feasibility — negative

**Research only; no canonical board or source edit and no P1/P2/P3 credit.**
`replay.py` is hash-bound to the reviewed Q_PRE-repair board
`e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef`, the
unified source/floorplan/modular plan, and records the checker digest in
`result.json`. Reproduce with `python3 replay.py` from this directory.

The probe asks the narrow question whether complete owner physical cells can
replace the broad `analog_ch2`, `analog_ch3`, and `analog_ch4` rectangles
without moving native parts. It removes only those three rectangles and creates
one complete rectangular occupied cell per owner: all 36 owner references are
included in each, patterns are rebound, and every other reviewed quiet-power
cell/region is retained. This is a deliberately maximal feasibility bound,
not an adopted decomposition.

The strict `_physical_cells` checker rejects the first candidate before any
neighbor-region recut: `analog_ch2_full: physical cell off board outline`.
The exact ch2 full-cell hull is `[46.725,19.955,84.268081,79.145]` mm, driven
by native J2's full envelope `[66.875,19.955,84.268081,34.495]` mm. The same
mechanical condition exists for J3 and J4: their full envelopes begin at
y=19.955 mm. A strict occupied physical cell may not extend beyond the board
outline, so this complete one-cell-per-owner partition is inadmissible.

This does **not** prove that every possible multi-cell partition is impossible.
It does prove that the proposed complete-owner-cell shortcut cannot avoid
separate edge-connector authority: a valid partition needs edge-compatible
connector cells/exception evidence plus a complete geometry treatment of all
36 references in each channel. The earlier AFE envelope conflicts with
neighbor channel regions remain unclosed. Do not use sparse pads/pockets or
this negative result as route, capacity, P2/P3/return, or P1 acceptance.
