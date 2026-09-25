# TI USB edge-owner source probe — 2026-09-25 UTC

**Research-only, FAIL.** The isolated files in `06_build/usb_edge_owner_split_probe_sol/`
split the fixed `J_USB` into a `usb_edge_connector` modular owner, transfer every
`J_USB.*` interface and source-allocation leaf from `usb_frontend`, and retain
the unchanged TI diagnostic board. The board SHA-256 is
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
The variant source/interface/floorplan/contract SHA-256 values are recorded
verbatim in its `result.json`; all input hash bindings match.

An edge source region `[224.9,20,235.1,28]`, support region
`[200,29,238.5,40]`, and disjoint integration corridor `[229,28,231,29]`
passed the checker's native corridor geometry screen. The corridor enumerates
all six exact `USB_DP`/`USB_DN` endpoints: `J_USB.A6/B6/A7/B7` and
`U_USB_ESD.1/.2`, with individual P2 pad-to-face and filled In1.Cu return
obligations. Four fixed-pad access witnesses use exact native pad bboxes and
separate `[pad-bottom, y=28]` access reservations. Legacy USB data reservations
were removed; the VBUS reservation was shifted east of the corridor to avoid
overlap. This grants no routing, capacity, impedance, return, or P1 credit.

The checker stops at the **first downstream USB witness**:
`U_XU.60: P2-movable owner requires virtual block-face witness`. The four
connector accesses and two `U_USB_ESD` handoffs precede it in the isolated
contract and passed witness validation. Because the USB allocation aborts at
`U_XU.60`, the final global `usb_edge_access: integration affected
endpoint/layer denominator mismatch` is consequential, not an independent
six-endpoint geometry verdict. The retained old XU witness is a native-pad
face; the complete source model still needs an XU virtual boundary and a
separately modeled frontend-to-XU handoff. The current checker also rejects
additional USB data reservations as double counting against the edge
integration corridor, so this is a source-schema/topology design question,
not a reason to omit XU endpoints from a full P1 contract.

The exact connector physical envelope is `[224.955,19.45,235.045,27.8]`:
its north end projects 0.55 mm past the board y=20 edge. The logical owner
region covers the tested pads, but a connector `physical_cell` cannot honestly
pass the present on-board full-envelope containment rule. Edge mating/P-OUT
and connector FULL remain separate open decisions. No canonical source, board,
P1 attempt, or acceptance status was changed.
