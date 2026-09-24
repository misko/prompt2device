# Shared-transition port checker review

**Reviewed commit:** `be69cd0c`  
**Verdict:** accepted as a schema-2 coarse screen only; it establishes no
capacity, route, P1, or connector-FULL result.

The checker binds every shared-port witness to its source and native pad, net,
modular footprint owner, port face/layer/bounding box, reservation identity,
and exact P2 pad-to-port obligation.  It requires every declared affected
endpoint on every declared copper layer to be consumed by a matching witness.
The real-board fixture is bound to unseeded Crow board SHA-256
`60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17` and
covers Q_VBUS.3 / `VBUS_PRESENT_N` only.

I independently probed a reassignment of `Q_VBUS` from `usb_vbus_sense` to
`xmos_core` while retaining the claimed endpoint owner.  It now fails with an
affected native footprint/block-owner mismatch, and the evaluator status is
`FAIL`, not `INCOMPLETE`.  The screen also rejects a reservation scope outside
the declared union zone, foreign source-region intersections, footprint/pad
intersections, and native rule areas anywhere in the declared zone.  Shared
reservations are reported `INCOMPLETE` without a capacity-slot result, and the
top-level result remains `routing_realized: false`, `p1_accepted: false`.

Validation: `python3 -m unittest
skills/kicad-pcb/scripts/tests/test_p1_coarse_capacity.py -q` — 33 passed.
