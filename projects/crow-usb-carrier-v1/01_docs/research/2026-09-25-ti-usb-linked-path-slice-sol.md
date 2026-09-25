# TI USB linked-path first slice — 2026-09-25 UTC

**Isolated source/checker experiment; no canonical Crow edit or P1 credit.**
The copied `2026-09-25-ti-usb-linked-path-slice-sol/` source, modular plan,
floorplan, contract and result bind the exact unrouted TI board SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
The copied contract SHA-256 is
`08c9762c0144c269cb956ac9a38a86692fc9e2826d3332f1b6504ec5cfb08af5`;
source SHA-256 is
`5ceb00e0dbc8bfb2e9477f5fc5eb3204d461e4385eb21b55693f3796fa99d3fa`;
result SHA-256 is
`2b961de40145be465106d57ba998de360328fecf797044eed7a5a6e6fcea5f0f`.

The opt-in `linked_paths` row accounts for `USB_DP` and `USB_DN` **once**
across ordered `usb_edge_connector → usb_frontend → xmos_core` ownership.
Its physical first stage reuses the native integration-corridor checks on
`[229,28,231,29]`, four exact J_USB pad accesses, all six stage affected
endpoints, exact P2 obligations and filled In1.Cu return debt. Its rough
capacity is two 0.97-mm slots against one declared slot, **not** route or SI
proof. The virtual second stage carries ESD-to-XU exact affected endpoints,
P2 obligations, an explicit ESD-pad join per net and filled-return debt. It
has `geometry: null` and `capacity_slots: null`; path status stays
`INCOMPLETE` regardless of the first stage's rough capacity.

The complete checker result has no global errors and reports the linked
subpath `INCOMPLETE`. The full `usb_device_pair` allocation remains
`INCOMPLETE` on the independent legacy `J_USB.2` VBUS witness (`witness bbox
is a nonlocal bridge across source region`). Other P1 allocation groups are
also unresolved; this is not a whole-board P1 result. A separate TI native
screen has identified a possible second physical strip near
`[215.5,40,218.5,84]` after VBUS/debug source-region recuts. It is a later
extension requiring exact stage-2 source/native and return validation; this
first slice does not claim that geometry or remove the virtual debt.

The generic checker adds the new path only when source and contract opt in;
legacy corridor records and default output remain unchanged. The linked
first slice accepts exactly one physical stage followed by one unresolved
virtual stage, rejects a second same-net top-level reservation, and rejects
missing endpoints, joins, native obstacles, geometry on the virtual stage,
and incomplete P2 or return duties. It cannot certify routing, impedance,
filled reference, connector mating, P-OUT, FULL, P2, or P1.
