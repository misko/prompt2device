# TI USB frontend-to-XMOS physical corridor probe — 2026-09-25 UTC

**Research only; no P1, routing or USB qualification credit.** The exact TI
unrouted board is SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
The five copied inputs/result files in
`2026-09-25-ti-usb-second-corridor-probe/` are individually bound by the
checker result hashes. They do not change canonical source or board.

The current planning cells leave a needlessly narrow USB passage: the
VBUS-sense refs' native envelopes end at x=213.96 while their region ends at
x=220; the fixed J_JTAG body begins at x=223.475 while the debug region
starts at x=221. In this isolated probe, VBUS-sense ends at x=215, debug
starts at x=222.5, and the dependent JTAG face is moved consistently. A
second DP/DN corridor occupies `[215.5,40,218.5,84]` on F.Cu, contacting the
USB frontend south face and XMOS north face without touching the latter's
east corner. Native scan finds no footprint envelope, pad, track or rule-area
inside that strip. A separate rough `connected_capacity` check measures
three 0.97-mm vertical slots with no native obstacle; this is **not** an
effective capacity or impedance measurement.

The source checker accepts the new corridor's region/face/native geometry and
its explicit `P2_REQUIRED` filled In1.Cu return *obligation*. It does not
evaluate a completed second USB allocation: the legacy VBUS witness is still
nonlocal, existing source corridors have endpoint-denominator noise after
the allocation aborts, and two top-level same-net USB reservations correctly
trigger duplicate-credit errors. The linked-path schema proposal must link
the edge corridor and this second corridor as ordered stages, counting DP/DN
once, before a complete source-level USB test is meaningful. P2 access,
filled-reference continuity, pair impedance, skew, native routed DRC and
connector P-OUT/FULL all remain unproved.
