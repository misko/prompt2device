# TI ADC7/8 + TDM/XU joint refloorplan map

**Research only.** This map binds the TI diagnostic board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
It changes no canonical source or board, consumes no P1 attempt, preserves
the 27 fixed references, and does not accept P1.

## Coupled constraints

| Need | Exact current witness | Consequence |
| --- | --- | --- |
| Channel 7 local AC handoff | Proposed F.Cu portal `[166.00,83.90,167.12,85.00]` intersects `Y_AUDIO` `[156.019,82.559,178.981,87.995]`, `C_ADC_I2C_A` `[164.365,81.515,171.261,88.245]`, and `C_ADC_CLOCK_OK` `[163.739,82.841,170.635,91.908]`. | All three P2 parts must leave the portal. The bounded 0.05-mm search found zero legal origins for each inside the present `audio_clock_tdm` cell `[145,72,190,99.84]`; this requires a cell/placement redesign, not a port cut. |
| Channel 8 local AC handoff | `[190.50,83.90,191.62,85.00]` is body-clear but lies in `xmos_core`; channel 8 is otherwise covered by `audio_clock_tdm` to x=190. | A small, typed XU-west transition cell must own this portal, with full-envelope ownership for every XU decoupler assigned to it. A face relabel alone is invalid. |
| Four TDM-to-XU nets | The direct west band `[182.475,94,199.825,100]` has 1.515 mm: three 0.45-mm slots, not four. Its limiting x=197.7525 section is split by `C_XU_VDD_104`, `_106`, and `_113`. | This band cannot carry the claimed four-net demand at present. Moving those caps is one placement option, but grants no endpoint or return credit. |
| A raw alternate neck | The saved `tdm-widen` probe reported four rough 0.45-mm slots in `[188,94,190,99.84]` after setting `audio_clock_tdm` to `[153,72,188,99.84]`. | The exact full-envelope remeasurement below finds five slots, not an empty strip. No cap move was assumed. It remains `INCOMPLETE` because it is virtual and has not proved the complete 54-terminal timing bundle, physical-cell ownership, access, or return. |

The channel portals and the alternate timing strip do not geometrically
intersect. They nevertheless cannot be promoted independently: both demand
new ownership at the current audio/XU boundary, and the current checker has
no implicit shared-zone exception. A candidate must therefore make the
interfaces disjoint typed physical cells, or add explicitly supported shared
ownership semantics before using either interface.

## Exact full-envelope remeasurement of the alternate neck

On the exact board, I screened `[188.000,94.000,190.000,99.840]` on F.Cu
with `GetBoundingBox(True, True)` for every non-endpoint top-side footprint;
`U_TDM_XLATE` and `U_XU` were excluded only as the intended terminal
footprints. The connected horizontal bottleneck is **2.538400 mm**, or
**five 0.45-mm slots**. It therefore clears the four-slot geometric lower
bound, rather than the earlier four-slot body/pad estimate. The limiting
cross-section is x=189.290 mm; there both full envelopes cross the neck and
leave only the upper interval y=94.000..96.538400 mm:

| Full-envelope obstacle | Bbox mm |
| --- | --- |
| `C_XU_VDD_105` | `[188.579999,96.538400,198.934524,99.108250]` |
| `C_XU_VDDIO_109` | `[187.222857,98.738400,198.934524,101.308250]` |

This is a connected-capacity obstacle screen, not a claim that those five
traces can reach the endpoint pads or retain clearance after routing. In
particular, the excluded endpoint footprints, pad fanout, effective rules,
and filled-return continuity remain unproved.

## Smallest coupled redesign to measure

Keep all fixed references and the XU package fixed. Make a single isolated
placement copy with these bounded changes:

1. Repack `Y_AUDIO`, `C_ADC_I2C_A`, and `C_ADC_CLOCK_OK` into a newly sized
   audio/TDM cell, leaving the channel-7 portal clear. Their current cell is
   proven too full for an in-cell move, so the candidate must declare the
   receiving cell and test all of its native envelopes.
2. Split the former audio/XU interface into three nonoverlapping physical
   cells: the repacked audio/TDM cell, a TDM-to-XU transition containing the
   measured `[188,94,190,99.84]` neck, and an XU-west cell containing the
   channel-8 portal. Partition every modular reference of an owner across
   those cells; do not create an untyped empty gap or assign a component by
   origin only.
3. Retain the four named TDM pads (`U_TDM_XLATE.6/.4/.7/.5`) and their four
   XU pads as exact endpoints. The transition may record only four
   `P2_REQUIRED` pad-to-face and return obligations until a routed board and
   filled GND continuity prove them. The two channel portals likewise record
   only `ADC7N/P` and `ADC8N/P` local P2 obligations.

This is a source/placement scope, not a route claim. If the XU-west cell
cannot contain its complete assigned decoupler envelopes while preserving the
channel-8 portal, the bounded redesign is rejected; moving `C_XU_VDD_104`,
`_106`, and `_113` is then a separate larger alternative, not evidence for
the direct west band.

## Measurable gate for that isolated copy

Reject the copy unless all of the following are true:

* all 27 fixed references retain their current placement and every affected
  movable reference has a complete native body/pad envelope in exactly one
  declared physical cell;
* the two portal rectangles are free of foreign full footprints, are exclusive
  to their declared cells, and bind the four exact ADC N/P pads only;
* `[188,94,190,99.84]` retains at least four 0.45-mm connected F.Cu slots
  after all full-footprint obstacles are included (the exact current screen
  is 2.538400 mm/five slots), with exact TDM and XU endpoint witnesses for
  all four nets;
* all 54 members of `adc_timing_xmos_bundle` remain in the endpoint
  denominator, reservations do not overlap, and each local port and timing
  transition carries explicit pad-access and GND-return P2 debt.

Passing those geometric checks is still **not P1 acceptance**: no local
portal or raw slot count is capacity, routing, endpoint-completeness, or
return proof. The next action is to run this one isolated refloorplan copy
against native full envelopes and the schema-2 checker, preserving an
`INCOMPLETE`, `p1_accepted: false` result regardless of its screen outcome.
