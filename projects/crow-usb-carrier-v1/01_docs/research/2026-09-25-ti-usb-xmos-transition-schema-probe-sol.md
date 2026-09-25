# TI USB/XMOS transition schema probe — 2026-09-25 UTC

**Research only; USB allocation still FAIL.** The tracked contracts and
results in `01_docs/research/2026-09-25-ti-usb-xmos-transition-probe/` use
the identical floorplan, modular plan and P1 requirements saved in
`01_docs/research/2026-09-25-ti-usb-edge-owner-probe/`, and the exact unrouted TI board
SHA-256 `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
They preserve the six `USB_DP`/`USB_DN` edge-corridor affected endpoints,
four exact fixed connector accesses, two ESD pad-to-face debts, and the
filled In1.Cu return obligation. They add both `U_XU.60/.59` as movable
virtual north-face witnesses with explicit P2 obligations. No board, canonical
source, P1 attempt, route, or connector qualification changed.

With the **single** existing edge reservation, `--diagnose-all` reports for
both XU witnesses: `block face does not contact assigned reservation`.
Their valid-form xmos face is at y=84, while the edge corridor is y=28–29.
The candidate contract SHA-256 is
`9f02078de0bcb530cd9a9212e69a6f0cf6d8fd94c0cd60c5d202f8057da9b0db`;
the result SHA-256 is
`467e4e13ffde0d145236bd9ab781652bc93c2e39ca09b843512a5ddfd40b8ea3`.

Adding a **second** same-net xmos trunk reservation at
`[215.3,40,217,84]` makes the checker report
`usb_edge_access: integration net double reservation credit in usb_device_pair`.
Its direct rectangle also enters the `usb_vbus_sense` source region for
both XU witnesses. That contract SHA-256 is
`2996abfd6fa9d23f952063b46effd4f30f9b35d8032716a5af57b67f04785164`;
the result SHA-256 is
`f03d60914c6c80aae31329824be52a88ee67c91e39abf67e96754b366e41c6fb`.
The normal allocation still stops on the unrelated legacy `J_USB.2` VBUS
witness; diagnostic mode exposes the independent data-net failures above.

The present source grammar has a two-participant rectangular integration
corridor and forbids any second reservation carrying the same signal net.
It cannot express the connector → protection → XU three-owner data path as
two disjoint, non-crediting hops while preserving both ESD and XU endpoint
debts. A source-model extension must explicitly link sequential physical
handoffs, distinguish allocation coverage from duplicate capacity credit,
and require exact affected endpoints and P2/filled-return obligations at
each hop. Any proposed second path must route around the current VBUS-sense
and debug owner regions, then pass native obstacle checks. This is a checker
contract limitation, not proof the PCB is physically unroutable. P1, P2,
P-OUT, connector FULL and the other allocation groups remain unresolved.
