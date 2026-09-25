# TI outline-growth audio receiving-cell screen

**Research only.** The BRIEF calls 220 x 120 mm an initial, reversible
assumption rather than a maximum. This screen leaves the exact TI board,
canonical outline, all connector poses, and all 27 P1-fixed references
unchanged. It does not make an outline change or accept P1.

## Measured receiving area

The present outline is `[20,20,240,140]` mm. A downward-only extension to
`y2=156` mm creates an empty candidate cell `[145,140,190,156]`: an exact
board scan finds no current `GetBoundingBox(True, True)` footprint in that
rectangle. It can receive the three channel-7 portal blockers at their current
orientations with their full native envelopes:

| Ref | Candidate full bbox mm | Candidate origin mm |
| --- | --- | --- |
| `Y_AUDIO` | `[145.000,140.000,167.962,145.436]` | `(156.481,143.361)` |
| `C_ADC_I2C_A` | `[168.000,140.000,174.896,146.730]` | `(170.435,140.485)` |
| `C_ADC_CLOCK_OK` | `[168.000,146.730,174.896,155.797]` | `(172.461,153.789)` |

The rectangles only touch at their intended edges; none overlaps. Their
unrotated packing height is **15.797 mm**, so a 15-mm height extension is
insufficient for this exact locked-orientation arrangement and a 16-mm
extension is the smallest 0.01-mm-rounded candidate. The candidate board size
is therefore **220 x 136 mm**, extending only the existing south edge.

The nearby `U_ADC_I2C_XLATE` remains at `(169.1,95.3)` with full bbox
`[162.336494,93.575000,175.863506,98.761600]`; this receiving cell is 41.2384
mm below its south edge. It is a placement area, not a demonstrated short
local I2C route.

Adding 15 mm at the east edge alone is inadequate for the oscillator's
22.962-mm full width. A 30-mm east extension can contain it but does not
improve the channel-7 north face and moves the support cluster farther from
the ADC/TDM neighborhood. The downward 16-mm option is the smaller measured
receiving-area change.

## What it resolves, and what it does not

Moving these three P2 parts clears the measured channel-7 local rectangle
`[166,83.9,167.12,85]`; the current-cell packing witness no longer applies.
It does **not** itself make that rectangle exclusive: `audio_clock_tdm` still
owns x=145..190 above it. It also does not clear channel 8's audio/XU ownership
boundary or turn the `[188,94,190,99.84]` TDM/XU neck into a route. The neck
continues to have the five-slot full-bbox screen and its endpoint/return debt.

Consequently the larger-outline candidate is rejected as a P1 source model
unless a subsequent isolated floorplan does all of the following: moves or
partitions the complete 39-reference `audio_clock_tdm` owner without foreign
envelope overlap; creates typed nonoverlapping cells for the channel-7/8
portals and TDM/XU transition; retains exact TDM/XU endpoint and return debt;
and rechecks every full footprint against the new outline. The current
receiving-cell calculation establishes only that 16 mm of added south height
provides a nonoverlapping destination for the three immediate blockers.
