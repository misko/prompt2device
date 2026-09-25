# TI board USB edge-owner split probe — 2026-09-25 UTC

**Research only.** The five copied inputs/results in
`2026-09-25-ti-usb-edge-owner-probe/` are an isolated SOL experiment against
the TI unrouted board, SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
They are not canonical source, a P1 attempt, or connector qualification.

The experiment gives fixed `J_USB` a distinct logical
`usb_edge_connector` owner, transfers its interface endpoints, and places a
pad-owner region at `[224.9,20,235.1,28]`. The seven support references stay
with `usb_frontend` in `[200,29,238.5,40]`. A proposed empty corridor
`[229.2,28,230.8,29]` separates those regions. On the exact board, the
checker found this corridor declaration geometrically possible: it did not
reject the region or fixed-footprint separation.

The full result is still **FAIL**. Only `J_USB.4` was changed to a typed fixed
access witness, so the USB allocation next rejects `J_USB.5` as a nonlocal
bridge. The experiment also intentionally leaves incomplete affected-endpoint
coverage and legacy USB DP/DN/VBUS reservations that overlap or double count
the new corridor. An `interfaces` hash drift in `coarse.json` is clerical to
this probe and must be corrected before interpreting a later full checker
result. No allocation has been accepted.

There is a separate physical-model boundary: J_USB's entire native
courtyard/body envelope is `[224.955,19.45,235.045,27.8]`, 0.55 mm beyond
the y=20 board edge when stroke is included. The logical pad-owner region
does not represent that whole physical envelope, so it cannot establish a
valid connector physical cell under present containment rules. The proposed
edge exception and actual connector registration remain unapproved; see
`2026-09-25-j-usb-edge-exception-coupon-proposal-terra.md`.

The next source-model iteration should convert all four connector DP/DN
fixed accesses, enumerate every affected corridor endpoint, and replace the
old overlapping USB reservations in one coherent packet. Only after exact
source/interface hashes, native geometry and independent review pass should
the changed modular ownership enter canonical source. Edge P-OUT, connector
FULL, filled return, P2 routing and the other 59-net allocations remain
separate gates.
