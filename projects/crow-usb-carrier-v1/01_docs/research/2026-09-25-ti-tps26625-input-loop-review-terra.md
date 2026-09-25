# Independent review — TPS26625 input-bypass loop trial

**Subject:** SOL packet `9b5cf7be`,
`2026-09-25-ti-tps26625-input-loop-sol`. The packet establishes one bounded
native input-bypass connectivity witness. It remains research-only and cannot
support canonical, P1, or P2 promotion.

## Checks reproduced

Comparing the saved input-loop board with the pinned partial-return board finds
no footprint pose delta: all 569 footprints, all static native pad identities,
and the 27 fixed references match. The trial adds exactly one
`N12V_PROTECTED` F.Cu track, `(188.3,45.9)` to `(188.3,44.0)` mm, width
**1.20 mm** and length **1.90 mm**. That width matches the current source's
`INPUT_TRUNK` minimum-width assignment.

Direct native-shape inspection confirms that track contacts both
`U_SPOKE8.1` and `C_SPOKE_IN8.1`; native connectivity names exactly those
two supply endpoints. The U.1 land spans y=46.38–46.62 mm and the rounded
track endpoint reaches y=46.50 mm, leaving only **0.12 mm** of vertical
contact depth. The contact passes KiCad and the track clears PowerPAD.11 by
0.362121 mm and U.2 by 0.381774 mm, but that small edge overlap does not
prove production-current sharing, voltage drop, or thermal robustness.

The previously reviewed GND return still joins `C_SPOKE_IN8.2` to
`U_SPOKE8.6`; its vertices and the shared stitch lie in filled In1 GND outline
8. `GND` remains distinct from `SPOKE_RTN8`, whose local tracks remain
separate. I replayed the archived project/rules, generated POFV areas,
via-process check, refill, and native DRC in a temporary directory: before
and after are **199 violations / 499 opens**, with **+0/-0** violation
identities and no via-process failures.

## Area and disposition

The reported **15.410 mm²** shoelace figure is reproducible from the stated
pad-center polygon. It closes through an internal capacitor chord and an
internal device chord, so it is a **projected centerline closure area**, not a
measured current loop area, field solution, or accepted EMI limit. No source
or TI numeric area limit exists to compare it against.

This input loop is the only closed TPS26625 loop. OUT supply, ILIM signal,
dVdT signal, and UVLO signal tracks are still absent; their loops and loop
areas remain undefined. The PowerPAD/RTN network still lacks a qualified RTN
copper/thermal island. Therefore retain the existing project IN/ILIM 2.5-mm
placement ceilings and the current trial as a narrow native-connectivity
result. A later route packet must provide robust endpoint geometry plus the
remaining four signal legs, complete local RTN/PowerPAD thermal evidence,
per-loop routed path and area receipts, and the separate channel-8/J8/ADC8N
obligations before P2 can be considered.
