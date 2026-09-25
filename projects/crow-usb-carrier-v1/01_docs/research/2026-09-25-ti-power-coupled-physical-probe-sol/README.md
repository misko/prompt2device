# Coupled power owner study — stopped at structural conflicts

Run `python3 replay.py`. This is an in-memory study on the reviewed Q_PRE TI
board. It preserves all 569 modular owners and the four full power net terminal
counts of 42, 27, 68, and 34 (171 total). `result.json` records the board and
checker hashes. No board or canonical source was written.

**Analog channel boundary.** Full native U_AFE2 and U_AFE3 envelopes require
the ch2/ch3 boundary at x=69.545 mm and the ch3/ch4 boundary at x=91.545 mm
for rectangular, disjoint owner pockets. This is a source-only boundary recut,
but it does not preserve the neighboring native pad relationship: ch3's
`R_IN3P.1` and `U_ESD3.1/.2/.3`, and ch4's `R_IN4P.1` and
`U_ESD4.1/.2/.3`, cross the proposed left edges. The resistor pad on each
channel loses even its former partial intersection with its owner's region.
All eight pads already protruded across the old left edges; this proposal
makes that existing issue worse. The replay inventories all ch3/ch4 pads and
separately records the preexisting outside-region pads, so it does not label
them newly displaced. A valid next step needs a coupled neighboring member
cell/pocket recut or a physical move, with exact pad and footprint checks.

**Input buck cluster.** The smallest tested y-only clearance moves native
`C_PWR_CT2` from (53.2, 101.3) to (53.2, 102.43) mm. Its full envelope starts
at y=101.655 mm, just beyond the input cluster hull ending at y=101.645 mm;
native body collision is absent. With `quiet_buck_edge` recut to its moved
envelope, the existing 13 quiet-power cells still pass `_physical_cells` (19
cells including the six established cells). A 12-ref `input_buck_core`
rectangle [40.155, 84.205, 53.795, 101.645] has no other native footprint
or pad in it. Yet the actual `_physical_cells` call rejects adding only that
cell: `input_buck: physical cell ref denominator incomplete`. The remaining
eight owner refs are `C_IN3`, `C_OUT2`, `D_IN`, `D_QIN_GS`, `F_IN`, `J_PWR`,
`Q_IN`, and `R_QIN_G`. `J_PWR` is especially remote at y≈20–31 mm; a complete
occupied input-buck partition requires a further source/physical cell design.

This stops at the first complete-owner structural conflict. No unresolved
branch was replayed on this invalid partition, and no P1, P2, capacity,
return, or route credit is claimed.
