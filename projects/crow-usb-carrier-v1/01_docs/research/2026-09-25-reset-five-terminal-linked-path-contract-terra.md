# Five-terminal reset two-corridor P1 contract design — 2026-09-25

## Corrected finding

The existing `linked_paths` feature has the right **series topology**, but it
cannot express this reset case source-only on the frozen board. The earlier
source-only conclusion was incorrect and is retracted.

`J_JTAG.10` needs the two measured 0.15-mm access segments
`[221.175,47.89,225.09,48.04]` and `[221.175,48.04,221.325,65]` from the
reset scratch probe. Current linked-path records permit exactly one `bbox` for
each `source_pad` (`p1_corridor_capacity.py` lines 1274--1284), so that
segmented access cannot be represented. More decisively, the linked first
physical stage and its access area must not intersect *any* ordinary
reservation (lines 1263--1269 and 1328--1332). The existing four-net
`jtag_strip_trunk` occupies the only proposed first-stage strip. Replacing it
would discard the still-required ordinary JTAG capacity claim; retaining it
causes a mandatory overlap failure. There is no demonstrated non-overlapping
straight first-stage/access partition on this frozen placement.

The `U_XU.38` native pad is at `(216.162,104.0)`, whereas the current JTAG
strip's XU-side face is at y=84. A linked declaration could only carry an
unresolved P2 handoff across that separation; it does not establish native
pad access or a physical path to the JTAG strip.

This finding is bound to the frozen board
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`, current
checker `p1_corridor_capacity.py`
`fdbf97c70a105205423a7b4430f584344346a2250ddb63a0f71260e7cb284dd0`, and the
one-candidate reset failure summary
`c517898f46597110b6f296cd4de970b369c89af0db34c56674cf48a90b9524fb`.
It changes no source, board, route, or acceptance state.

## What the existing topology could describe

Declare one `linked_path` for `XU_RESET_N` in allocation
`xmos_service_escape`, ordered:

```text
debug_connector -> xmos_core -> digital_power
```

It would have exactly two F.Cu stages over In1.Cu reference:

1. `jtag_strip`: `J_JTAG.10` to `U_XU.38`, with segmented fixed connector
   access.
2. `reset_power_gap`: `U_XU.38` to the three digital-power terminals
   `R_XU_RST_PU.2`, `U_CORE_OK.1`, and `U_XU_3V3_OK.6`.

`U_XU.38` is the sole shared interstage endpoint. The five exact terminals
remain in the source denominator and the path declares four minimum tree
edges as a P3 obligation. The three digital-power terminals are distinct
terminal leaves of stage two; their physical fanout remains P2/P3 work.

Removing `XU_RESET_N` from its unresolved ordinary record is necessary, but
it does not solve the two frozen-board blockers above. Removing or replacing
the ordinary four-net `jtag_strip_trunk` is not an acceptable source-only
workaround because it removes its independently required capacity accounting.

For the digital-power side, use one deliberately local virtual face on its
east region edge, strictly smaller than one quarter of the local region span
and away from a corner. All three P2 pad-to-face obligations may name that
same face. It is a source face only: it does not assert that the three native
pads can reach it. The prior 10.2-mm face is invalid because it exceeds the
current 8.54-mm locality limit.

The existing feature fits the abstract series relation: three distinct owners,
two ordered stages, and one shared endpoint for each net at the middle owner.
It permits a physical second stage with multiple terminal endpoints at the
final owner. That topology is useful input to an extension; it is not an
admissible current-source representation.

## Narrow extension required before a proposal

Add a reviewed **shared physical-stage** capability to `linked_paths`, scoped
only to a named existing integration corridor. It must: (1) represent one
fixed endpoint as an ordered, contiguous segment list and validate every
segment against bodies, pads, copper, zones, and the source face; (2) bind the
linked first stage to exactly one named ordinary corridor with identical
participants, layer, reference, faces, and bbox; and (3) recompute that
corridor's capacity from the explicit union of its four ordinary JTAG nets and
the linked reset net, without treating reset as an ordinary reservation or
crediting it twice. The exception must reject any non-identical overlap,
unlisted net, second shared reservation, or missing affected/P2/return
denominator entry.

This is a checker change, not a source-only representation. It should retain
the second reset stage as `INCOMPLETE`, and preserve the y=84-to-y=104
`U_XU.38` handoff as explicit P2 debt. It gives no P1 or P2 credit until
native pad access, actual tree routing, and return are independently proved.

## Required invariants

- Exact endpoint set: `J_JTAG.10`, `U_XU.38`, `R_XU_RST_PU.2`,
  `U_CORE_OK.1`, `U_XU_3V3_OK.6`; all identify `XU_RESET_N` on F.Cu.
- Only `U_XU.38` occurs in both stages; every other endpoint occurs once.
- Owner order and the two stage participant pairs are exact. The first stage
  alone may carry the fixed JTAG access; the second has no fixed endpoint.
- A future shared first stage binds only to the exact named JTAG corridor;
  every other reservation and access shape remains disjoint. Its five-net
  capacity denominator is explicit and measured once.
- Each terminal retains `P2_REQUIRED` pad-to-face and continuous-filled-In1
  return obligations. The path remains `INCOMPLETE`, has no aggregate capacity
  credit, and retains a P3 connected-tree/skew/electrical obligation.

## Meaningful negative controls

1. Put `XU_RESET_N` in any ordinary witness or reservation as well as the
   linked path: reject competing credit.
2. Duplicate any non-junction endpoint across stages, or use a different XU
   pad as the junction: reject interstage multiplicity/terminal denominator.
3. Add a fourth owner, a third stage, a second shared XU endpoint, or another
   reset linked path: reject the bounded series schema.
4. Restore the 10.2-mm digital-power face or a face touching a region corner:
   reject locality.
5. Omit one digital-power terminal, alter its source/native/net/owner tuple,
   or omit its P2/return debt: reject exact endpoint or obligation parity.
6. Supply a single enclosing access rectangle in place of the two verified
   segments, or a segment that is discontinuous, misses the source face, or
   intersects a body/pad/copper/zone: reject it.
7. Allow shared-stage overlap with a non-identical corridor, omit any of the
   four JTAG or reset nets from the union capacity denominator, or bind a
   second shared reservation: reject it.
8. Mark a stage, capacity, return, P2, tree, or P1 result as passing: reject
   the no-credit boundary.

A genuine multi-junction or more-than-two-corridor reset topology would exceed
`linked_paths` and then requires a new reviewed branch-graph schema. This
contract design does not demonstrate a physical reset route, pad access,
filled return, P1, or P2 acceptance.
