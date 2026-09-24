# Segmented fixed access checker experiment

**Disposition: research only; P1 remains unaccepted.** The generic schema-2
checker now recognizes `fixed_connector_access_segmented`. A witness retains
the exact source/native pad, net, source block, fixed-ref status, layer,
source-owned integration corridor, and P2 obligation of the existing fixed
connector access witness. Its matching reservation names an ordered `segments`
list of at least two axis-aligned rectangles and a `bbox` equal to their exact
envelope. Each segment stays in the source region. The first shares a positive
edge with the physical pad boundary; each consecutive pair shares a positive
edge without area overlap; the last shares a positive edge with the corridor.
The chain must intersect the declared source face. All segments are checked
against native foreign bodies/courtyards, every other pad, existing copper,
native rule areas, and competing reservations. The envelope remains a
conservative overlap bound across named allocations.

Native synthetic tests exercise a dogleg around a pad inside its envelope,
disconnected/overlapping waypoints, missing corridor contact, changed
envelope, wrong source endpoint, a native obstacle on the chain, and a
competing reservation. The older single-rectangle form retains its checks.
Every accepted declaration reports `INCOMPLETE`, carries no `capacity_slots`,
and leaves `p1_accepted` false. The P2 filled-reference, effective trace width
and clearance, physical route, and simultaneous escapes remain unproved.

This is a **contract mechanism**, not a J_JTAG access proposal. The earlier
[rectangle obstruction study](2026-09-24-jtag-fixed-access-rectangle-obstruction-terra.md)
motivated it, but no Crow JTAG segments have been put in canonical source or
checked on a complete native Crow packet. A separate geometry idea is to
rotate the fixed header from 90° to 270° at the same center and widen the
integration strip to `[221,65,231,84]` mm; that may admit four rectangular
escapes, but the pose, native neighbors, return and connector service need a
separate study. No canonical JTAG pose or board changed here.
