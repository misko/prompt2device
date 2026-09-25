# Linked multi-hop P1 corridor contract proposal — 2026-09-25 UTC

**Design only.** No checker, canonical Crow source, board, P1 attempt, route,
connector FULL, or P-OUT status changes here. The exact TI board probe in
`2026-09-25-ti-usb-xmos-transition-schema-probe-sol.md` showed why a second
USB data reservation cannot simply be added: the current checker requires a
two-owner integration corridor, one reservation per witness, and rejects a
second reservation on either USB data net as duplicate credit. A single edge
reservation cannot contact the XU source face at y=84. The direct second
rectangle tested there also crossed `usb_vbus_sense`.

## Proposed opt-in source and contract shape

Add a separate `linked_paths` source list and one top-level
`kind: linked_path` reservation in the schema-2 allocation. Preserve existing
`integration_corridors` and their verdicts unchanged. Nested stages are
*not* independent top-level reservations or capacity credits. For Crow the
structural shape would be:

```yaml
linked_paths:
- id: usb_data_series
  allocation_id: usb_device_pair
  nets: [USB_DP, USB_DN]
  owner_order: [usb_edge_connector, usb_frontend, xmos_core]
  reservation_id: usb_data_series
  layer: F.Cu
  reference_layer: In1.Cu
  stages:
  - id: connector_to_esd
    kind: physical_corridor
    region_id: board_integration_usb_edge
    bbox: [229, 28, 231, 29]
    participants: [usb_edge_connector, usb_frontend]
    faces: [exact_connector_south_face, exact_frontend_north_face]
    affected: [J_USB.4, J_USB.12, J_USB.5, J_USB.13,
               U_USB_ESD.1, U_USB_ESD.2]
    fixed_accesses: [exact_A6_access, exact_B6_access,
                     exact_A7_access, exact_B7_access]
    p2_obligations: exact_pad_to_face_records
    return_obligation: continuous_filled_In1.Cu_P2_required
  - id: esd_to_xu
    kind: unresolved_virtual_span
    participants: [usb_frontend, xmos_core]
    affected: [U_USB_ESD.1, U_USB_ESD.2, U_XU.60, U_XU.59]
    geometry: null
    capacity_slots: null
    status: INCOMPLETE
    p2_obligations: exact_pad_to_virtual_boundary_records
    return_obligation: continuous_filled_In1.Cu_P2_required
  joins:
  - {from: connector_to_esd, to: esd_to_xu, owner: usb_frontend,
     net: USB_DP, source_pad: U_USB_ESD.1,
     kind: pad_anchored_virtual_interstage}
  - {from: connector_to_esd, to: esd_to_xu, owner: usb_frontend,
     net: USB_DN, source_pad: U_USB_ESD.2,
     kind: pad_anchored_virtual_interstage}
```

The names standing for faces/accesses/obligations above are placeholders for
full existing-schema records, **not** valid source syntax. A production
contract must bind their exact coordinates, native pad identities, layers,
source SHA-256s, and P2 duties. `unresolved_virtual_span` claims no empty
lane, connected copper, capacity, or physical route through the VBUS-sense
and debug regions. It remains an explicit P1/P2 blocker until replaced by
separately measured disjoint geometry and native return evidence.

## Fail-closed invariants

1. The path's terminal set is exactly the union of the authoritative modular
   interface endpoints for its nets and owner order, with each source/native
   pad/net/owner tuple present once. Native net, layer, aliases, modular ref
   ownership, and fixed/movable classifications must match. In Crow this
   means four connector data pads, two ESD pads, and two XU pads; the ESD pads
   may occur in two *stage obligations* only through the two explicit joins.
2. The stage graph is a linear ordered series for each net. Stage participants
   must be consecutive owners; no cycles, skipped owner, parallel competing
   stage, unjoined branch, or free-floating reservation is allowed. Type-C's
   two reversible connector pads per data net are terminal fan-in within the
   first owner, not parallel corridor capacity.
3. Every physical stage uses the current native outline, disjoint region,
   positive shared-edge faces, footprint/pad/copper/rule-area clearance,
   fixed-access, and P2 pad-to-face/filled-return checks. Consecutive
   physical stages either share a proven positive-edge boundary or have an
   explicit typed interstage join anchored to exact intermediate endpoints.
   A virtual stage or join must have **no bbox, segments, slots, or capacity**.
4. Exactly one top-level `linked_path` reservation accounts for these nets.
   Nested physical stages are measured independently, with no sum of slots or
   duplicated credit. A virtual stage has `capacity_slots: null`; the whole
   path stays `INCOMPLETE` and can never make P1 PASS. Any same-net top-level
   reservation outside the path, except a declared subordinate fixed-pad
   access, fails closed.
5. Every stage requires a separate exact P2 signal-access and filled-reference
   return obligation. The final result retains each stage's status and
   blockers; an aggregate result may use only a validated bottleneck, never
   add capacities. No source reservation proves routed continuity, impedance,
   SI, or connector qualification.

## Migration and tests

Implement this as a new validator and nested allocation result. Keep legacy
`boundary_witnesses`, `integration_corridors`, and their output byte-stable
unless a path explicitly opts in. Extract the existing physical-corridor
checks for reuse; do not merely whitelist same-net duplicates in the current
global loop. Add the Crow source copy as an isolated fixture only after the
new schema rejects all missing/extra endpoints and preserves the 59-net
coverage denominator. Canonical promotion requires independent source and
native review; this proposal supplies neither.

Positive fixture: a two-stage series with an exact intermediate pad-anchored
virtual join reports per-stage debts and overall `INCOMPLETE`, with no P1
credit. Negative fixtures must reject (a) a geometric gap without typed join,
(b) a fork or parallel same-net reservation that duplicates capacity,
(c) any omitted or misowned connector/ESD/XU endpoint, (d) a physical stage
or face crossing a foreign region or native obstacle, (e) geometry/capacity
fields on a virtual stage, and (f) missing per-stage filled return or P2
obligation. Existing legacy fixtures must retain their exact verdicts and
default output shape.
