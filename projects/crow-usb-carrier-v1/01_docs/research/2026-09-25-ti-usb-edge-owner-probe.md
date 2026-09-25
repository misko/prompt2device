# TI board USB edge-owner split probe — 2026-09-25 UTC

**Research only.** The five copied inputs/results in
`2026-09-25-ti-usb-edge-owner-probe/` are an isolated SOL experiment against
the TI unrouted board, SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
They are not canonical source, a P1 attempt, or connector qualification. The
more detailed reproduction note is
`2026-09-25-ti-usb-edge-owner-split-probe-sol.md`.

The experiment gives fixed `J_USB` a distinct logical
`usb_edge_connector` owner, transfers its interface endpoints, and places a
pad-owner region at `[224.9,20,235.1,28]`. The seven support references stay
with `usb_frontend` in `[200,29,238.5,40]`. A disjoint corridor
`[229,28,231,29]` separates those regions. On the exact board, the checker
accepted that geometry, the six exact USB DP/DN affected endpoints, four
fixed connector-pad accesses, and two frontend ESD handoffs. The saved source
copies bind their interface and floorplan hashes without drift.

The full result is still **FAIL**. The first downstream USB rejection is
`U_XU.60: P2-movable owner requires virtual block-face witness`. The old XU
native-pad witness needs a virtual boundary and coherent frontend-to-XU
transition model. The checker also prevents giving the same data nets credit
both through the edge integration corridor and a second named reservation.
The global affected-endpoint denominator mismatch follows the early USB
allocation abort and must be reevaluated after the XU repair. No route,
capacity, return, impedance or P1 credit follows from this probe.

There is a separate physical-model boundary: J_USB's entire native
courtyard/body envelope is `[224.955,19.45,235.045,27.8]`, 0.55 mm beyond
the y=20 board edge when stroke is included. The logical pad-owner region
does not represent that whole physical envelope, so it cannot establish a
valid connector physical cell under present containment rules. The proposed
edge exception and actual connector registration remain unapproved; see
`2026-09-25-j-usb-edge-exception-coupon-proposal-terra.md`. Edge P-OUT,
connector FULL, filled return, P2 routing and the other 59-net allocations
remain separate gates.
