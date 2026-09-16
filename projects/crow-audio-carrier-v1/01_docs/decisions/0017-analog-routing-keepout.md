---
id: 0017
date: 2026-09-08
status: accepted
---
# 0017 — Keep switching exclusion clear of legitimate analog endpoints

## Context

The analog and quiet-reference waves select the User.3 routing mask. The
previous single rectangle included six channel-1 analog pads and two 5V_OPA
pads. ROOT measured the intersections using isolated native footprint copper,
not pad-centre approximations. The KRT parser treats closed User.3 rectangles
as routing obstacles; these are not merely annotations.

The buck remains AP63205WU-7. Its cached DS41326 Rev 3-2 layout guidance calls
for compact switching loops and separation of sensitive feedback. It does
not specify the numeric routing halo chosen here. This correction neither
changes the regulator circuit nor claims measured EMI performance.

## Options

- Keep the old mask: rejects legitimate endpoints before route search.
- Raise only its top edge: frees channel 1 but still traps the ferrite output
  and op-amp bulk-cap positive pad; the regression reproduces both hits.
- Remove the mask: frees the endpoints but loses the switching exclusion.
- Retain a central mask and split the lower region around the quiet-supply
  corridor: frees all affected pads while preserving switching exclusion.

## Decision

Adopt the three User.3 rectangles in `03_src/route.yaml prep.keepouts.rects`.
They leave the channel-1 endpoints above the switching exclusion and a lower
quiet-supply corridor between the two side rectangles. Preserve all other
route configuration, source copper, placement, stack and fabrication limits.

Use a 3 mm engineering halo around the complete native BUCK_SW/BUCK_BST pads
and existing source segments as a regression requirement. This is a chosen
layout constraint, not a manufacturer guarantee or derived noise limit.
The native bounding-box measurement of the adopted geometry is 3.3 mm at
its tightest item. The retained test recalculates this from actual shapes.

## Consequences

`test_analog_keepout_source.py` checks all 376 pads on the 103 nets selected
by the two affected waves, plus all seven hot-copper items. It rejects the
actual old mask, top-edge-only repair, blanket removal, and insufficient
switching halo. The existing thermal preservation test delegates only this
rectangle delta; all its other preservation assertions remain active.

The separate source launch diagnostic improves from 307 to 313 witnesses
over 320 analog pads. U_ADC pins 15, 16, 19, 22, 42, 45 and 46 still lack
a straight 1 mm witness with existing seed copper present. Those findings
remain open; individual witnesses do not establish simultaneous routing.
This diagnostic is not an owning P-LAND verdict or an impossibility proof.

Generated-board admission, exact schematic/placement reviews, completed
routing, matched analog paths, trace DCR, continuous filled returns, SI,
thermal performance and release checks remain required. No generated PCB,
review, checkpoint, sealed pod or release is modified by this decision.
All public-only, DO-NOT-ORDER, TOP77/0.20 A first-power and publication holds
remain in force. See `../SOURCE-CORRECTION-20260908-analog-keepout.md` for
the measured attempts and their limits.
