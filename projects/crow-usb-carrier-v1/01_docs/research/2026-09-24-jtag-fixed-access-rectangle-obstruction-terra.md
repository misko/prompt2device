# Fixed-JTAG access: rectangle obstruction

**Disposition: INCOMPLETE research.** This note examines the isolated
QSPI-gap board only.  It neither declares copper nor establishes a physical
route, P1 acceptance, DRC closure, return continuity, or release readiness.

## Pinned subject

- Parent source commit: `231342b0`.
- Pinned QSPI-gap board SHA-256:
  `fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.
- JTAG integration strip: `[221,65,226,84]` mm on `F.Cu`.
- `J_JTAG` remains P1-fixed at `(228,50,90)`.

The four signal pads are the upper row of the rotated 2x5 SMD header.  Their
native boxes are all at `y=46.57..49.36` mm.  The lower-row partner has the
same x extent and lies at `y=50.64..53.43` mm:

| Signal pad | Signal-pad x box (mm) | Lower-row obstructing pad |
| --- | --- | --- |
| `J_JTAG.2` / `JTAG_TMS` | `230.17..230.91` | `J_JTAG.1` |
| `J_JTAG.4` / `JTAG_TCK` | `228.90..229.64` | `J_JTAG.3` |
| `J_JTAG.6` / `JTAG_TDO` | `227.63..228.37` | `J_JTAG.5` |
| `J_JTAG.8` / `JTAG_TDI` | `226.36..227.10` | `J_JTAG.7` |

The header's `F.CrtYd` rectangle, including its native 0.05-mm stroke, spans
approximately `x=223.475..232.525`, `y=45.975..54.025` mm.  The companion
pads are the immediate copper obstruction; the courtyard is a separate
placement/body-clearance constraint that an access definition must state
explicitly for its origin footprint.

## Result: rectangle contract fails

For any one signal, an axis-aligned access rectangle that touches its source
pad and reaches the strip must include the signal pad's x interval and cross
from below `49.36` mm to at least `65` mm.  It therefore includes the paired
lower-row pad's identical x interval at `y=50.64..53.43` mm.  Each of the four
single-net rectangles consequently intersects a foreign pad before questions
of inter-net rectangle overlap arise.

This is a structural failure of a *single-bbox-per-net* access contract.  It
does not show that four physical tracks cannot be routed.  A dogleg can, in
principle, leave a signal pad sideways in the `1.28`-mm gap between the two
rows and use the `0.53`-mm raw inter-column gaps below.  At the declared
`0.15`-mm track and clearance class, one channel consumes `0.45` mm, leaving
only `0.08` mm raw lateral margin.  Simultaneous doglegs, endpoint-courtyard
treatment, all other native obstacles, effective clearances, and the In1.Cu
return remain unproven.

If the contract requires a path clear of the origin footprint's entire
courtyard with no explicit source-pad escape exception, it is internally
infeasible: every signal pad begins inside that courtyard.  That semantic
issue must be resolved before treating a courtyard intersection as physical
unroutability.

## Minimal next change candidates

The smallest contract-level repair is to represent each fixed-connector access
as an ordered polyline or channel sequence and test every segment against
native pads, bodies, courtyards, and the other reservations.  A bounding box
may remain a conservative envelope, but cannot serve as the access path.

If the project requires rectangular access reservations, a placement or region
change is required: rotate, move, or replace `J_JTAG`, or reposition the
integration region so each fixed pad has a direct clear face.  No particular
new coordinate is recommended here; every such candidate must be checked
against the connector's remaining pads, its full courtyard/body envelope,
neighboring source regions, and all four simultaneous routes.
