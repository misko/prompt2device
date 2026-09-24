# P1 XMOS/clock shared-zone static probe

**Diagnostic only; REJECTED.** This is a read-only inspection of isolated board
`18e55f44d5c1a8f7a7dd050e12ca451f6e08932b8c79893a0ad74e3b18be861b`.
It does not edit `floorplan.yaml`, generate a board, create a task envelope,
spend an attempt, or accept P1.

## Candidate tested

The smallest rectangular shared-zone sketch that avoids the rejected y=112
cut was:

```yaml
xmos_core:         [185, 72, 232, 115]
xmos_clock_shared: [185, 115, 232, 133]
clock_flash_debug: [185, 133, 232, 136]
```

Using KiCad `GetBoundingBox(True, True)` (footprint graphics/courtyard-aware),
no footprint intersected the proposed horizontal boundaries y=115 or y=133
within x=185..232. The nearest clearance intervals were y=114.861..115.138
and y=132.862..136.000. This is only a boundary-intersection result; it is not
component placement, a corridor measurement, or a local-return result.

## Why the candidate is rejected

1. `xmos_core [185,72,232,115]` still positively overlaps the unchanged
   `audio_clock_tdm [140,72,190,112]` across x=185..190, y=72..112. A
   source-region exclusivity check therefore cannot admit this partition.
2. The current coarse checker supports a region name as a virtual witness
   `block` only when that block owns the exact endpoint in
   `modular_plan.json`. `xmos_clock_shared` owns none. Reassigning QSPI and
   crystal endpoints to it would change the modular ownership denominator and
   needs an explicit reviewed source model; adding a rectangle alone is not a
   schema-supported shared zone.
3. The shared rectangle contains the existing flash/crystal cluster. A source
   change would alter its placement region and require a fresh generated board
   plus P2 pad-access, XU-decoupling, return, and QSPI/crystal coexistence
   checks. The static gap does not establish any of those facts.

The 27 reviewed fixed refs remain untouched: `J1`..`J8`, `J_PWR`, `J_USB`,
`J_JTAG`, and `C_HOLD1`..`C_HOLD16`.

## Next source-governed step

Before a floorplan variant is authored, jointly partition `audio_clock_tdm`,
`xmos_core`, and `clock_flash_debug`, or add a reviewed shared-block ownership
model to both `modular_plan.json` and the coarse checker. The proposal must
provide non-overlapping source regions, explicit endpoint ownership, and
per-face P2 pad-to-face/return obligations. Only then may an isolated
floorplan variant be generated and checked for full-footprint intersections,
outline/rule-area conflict, raw demand, movable debt, and region exclusivity.
Its result remains `INCOMPLETE` and cannot promote P1.
