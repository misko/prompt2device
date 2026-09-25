# Narrow acceptance rubric for a TPS26625 channel-8 six-member route trial

**Scope:** a fail-closed review rubric for the next isolated six-member
placement-and-route artifact. It does not adopt a pose, source rule, numeric
TI limit, P1 result, or P2 result.

## Authority boundary

The subject is `U_SPOKE8` (`TPS26625DRCR`) with `C_SPOKE_IN8`,
`C_SPOKE_OUT8`, `R_SPOKE_ILIM8`, `C_SPOKE_DVDT8`, and
`R_SPOKE_UVLO8`. The frozen TI netlist is SHA-256
`a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd`.
The retained TI TPS2662-family dossier, `SLVSDT4F` SHA-256
`ff038eaa557fb618f93c0b6276a5ae08d0d3d9fbff1dddf0c45974a89120aefa`,
section 12.1 says to place the IN/GND bypass closest to its terminals,
minimize its loop, keep ILIM/dVdT/UVLO support close to its pins and return
them by the shortest path to RTN, and place the PowerPAD on the RTN plane.

TI gives no millimetre maximum for those placement statements. Its numeric
layout-related requirement here is C(IN) at least 0.1 uF. The current source's
100 nF `C_SPOKE_IN8` satisfies that component-value requirement; it does not
by itself prove a local loop.

The current part dossier contains two **project-owned** 2.5-mm copper-gap
ceilings: `U_SPOKE8`↔`C_SPOKE_IN8` on `N12V_PROTECTED`, and
`U_SPOKE8`↔`R_SPOKE_ILIM8` on `SPOKE_ILIM8`. They implement TI's qualitative
guidance. Do not label either ceiling, or any extension to C(OUT), dVdT, UVLO,
GND, or RTN, as a TI limit.

## Required artifact and geometry gates

The candidate must be source-generated from hash-pinned floorplan, netlist,
pose overlay, library, generator, `.kicad_pro`, and `.kicad_dru` inputs. Its
receipt must show:

1. Exactly the intended six movable references change; all 569 footprint and
   native pad identities, plus all 27 fixed-reference poses/pads, remain
   invariant.
2. Each of the six remains owned by `analog_ch8`, has no full native
   body/courtyard collision, and has no foreign-source-region intersection.
3. Full-profile native DRC, generated POFV areas, zone refill, and V-PROCESS
   have no new issue identity. This is necessary evidence only; a clean delta
   does not prove loop locality.
4. The retained ADC8N trial link, if included, preserves its exact endpoint
   identities, complete full-envelope/foreign-region screen, and filled In1
   return-ribbon receipt. It cannot be used as evidence for the TPS26625
   support loops.

## Existing ceiling checks

Measure native effective F.Cu shape separation, not pad-center distance, for
the two source-owned project ceilings:

| Existing project check | Required result |
| --- | --- |
| `U_SPOKE8.1` to `C_SPOKE_IN8.1` on `N12V_PROTECTED` | <= 2.5 mm |
| `U_SPOKE8.7` to `R_SPOKE_ILIM8.1` on `SPOKE_ILIM8` | <= 2.5 mm |

The result must identify the actual direct route primitives, not merely report
that a globally shared net is connected somewhere on the board.

## Routed-loop receipt required before considering P2

Replace the rejected all-loop pad-gap proxy with an actual native copper
receipt for these exact loops:

| Loop | Exact anchors |
| --- | --- |
| Input bypass | `U_SPOKE8.1` → `C_SPOKE_IN8.1`; `C_SPOKE_IN8.2` → `U_SPOKE8.6` |
| Output bypass | `U_SPOKE8.10` → `C_SPOKE_OUT8.1`; `C_SPOKE_OUT8.2` → `U_SPOKE8.6` |
| ILIM/RTN | `U_SPOKE8.7` → `R_SPOKE_ILIM8.1`; `R_SPOKE_ILIM8.2` → `U_SPOKE8.5` and local PowerPAD.11 RTN copper |
| dVdT/RTN | `U_SPOKE8.8` → `C_SPOKE_DVDT8.1`; `C_SPOKE_DVDT8.2` → `U_SPOKE8.5` and local PowerPAD.11 RTN copper |
| UVLO | `U_SPOKE8.1` → `R_SPOKE_UVLO8.1` → `R_SPOKE_UVLO8.2` → `U_SPOKE8.2` |

For every row, the receipt must bind named copper primitives and layers to the
two endpoint pads, demonstrate native connectivity, record path length and a
reproducible closed centerline/polygonal loop-area calculation, and identify
any plane/via contribution. It must also prove that `U_SPOKE8.5` and
PowerPAD.11 share a local `SPOKE_RTN8` island, while `U_SPOKE8.6` is on
separate `GND` copper with no GND/RTN bridging primitive or zone contact.
OVP.3's deliberate tie to `SPOKE_RTN8` must remain explicit.

There is no accepted numeric loop-area or additional loop-length limit yet.
The receipt must report them; a later project decision based on current,
thermal, and transient analysis must set any pass/fail threshold. This avoids
turning TI's qualitative closest/shortest wording into an unverified number.

Before any P2 claim, the artifact must also discharge the separate channel-8
owner-cell/J8 mechanical condition, complete required ADC8N branches and
returns, and meet the applicable P2 endpoint/return obligations. As the
current corridor authority states for power, scalar capacity cannot replace
rail-current, return, and thermal evidence. Passing this six-member rubric is
therefore one bounded prerequisite, not P2 acceptance.
