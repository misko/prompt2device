# Independent review: coupled TDM timing placement probe

**Decision: admit one bounded route/return experiment; do not promote P2 or
P1.**  `7afc7102` is a reproducible geometry improvement over the exact
15-footprint baseline, not a routing or local-placement proof.

## Replay and native invariants

Replaying `build_candidate.py` reproduces candidate SHA-256
`53e6fb7809910946c36053e7ceeb77e7fc866456ff77775ed4c59b3e49278555` from
baseline `d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`.
It moves exactly 27 P2 references: `C_ADC_I2C_B`, `U_XU`, 21 translated
nearby XU bypass/USB capacitors, and the four explicitly repositioned
capacitors `C_XU_VDD_105`, `C_XU_VDD_106`, `C_XU_VDD_14`, and
`C_XU_VDDIO_17`.  All 27 fixed refs retain pose.  The reference/pad census is
unchanged; independent comparison found no pad number, net, layer, shape,
size, or drill identity change.  The four rotated capacitors necessarily have
new relative pad coordinates, not new pad identities.

Checker `_physical_envelope` comparison finds three existing physical collision
pairs on each board, with no added or removed pair.  There are no new F.Cu
pad-bbox overlaps; all moved envelopes remain inside their assigned source
region.  This establishes only own-region containment, not an exclusive typed
physical-cell partition.

The checked XU owner-pad distances preserve or improve all 25 moved local
bypasses.  The four substantive improvements are C105 4.8185→3.8898 mm,
C106 2.8328→2.5882 mm, C14 1.8136→1.5861 mm, and C17 2.5162→1.5861 mm.

## Mouths and native DRC

The exact full-envelope connected apertures reproduce as follows:

| Mouth | Width | Rough slots/demand |
| --- | ---: | ---: |
| Translator west | 2.600 mm | 5/4 |
| XU west DATA | 1.400 mm | 3/1 |
| XU south MCLK/BCLK/FSYNC | 2.995 mm | 6/3 |

These are improvements over `5e1b3e82`’s 1.295 mm/2, 0 mm/0, and
0.545 mm/1 screens. They remain courtyard/body event-strip measurements at a
rough 0.45-mm pitch. They do not establish effective net-class clearance,
simultaneous escapes from the listed pads, a route between the regions, or
return continuity.

Independent KiCad DRC rerun is 730→724 violations with 499 unconnected items
on both boards. Clearance remains 224 and hole-clearance 28; silk-over-copper
falls 21→19 and silk-overlap 15→11. This is a delta, not a clean DRC result.
The In1.Cu GND zone remains unfilled.

## Important unmeasured XU relationships

Moving U_XU north by 0.2 mm preserves local USB-supply capacitor offsets:
`C_XU_USB18.1`→`U_XU.62` remains 18.1047 mm and
`C_XU_USB33.1`→`U_XU.61` remains 5.5158 mm. The USB ESD-to-XU centre distances
become 58.7770 mm (`USB_DP`) and 59.1869 mm (`USB_DN`), each 0.2000 mm shorter.
Neither result proves the required differential pair or ESD return.

The move worsens every sampled XMOS crystal interface by about 0.2 mm:
`R_XTAL_DRIVE.1`→`U_XU.34` 11.4434→11.6392 mm,
`R_XTAL_FB.1`→`U_XU.34` 9.6466→9.8457 mm,
`C_XTAL_OUT.1`→`U_XU.33` 10.8328→11.0322 mm,
`R_XTAL_FB.2`→`U_XU.33` 9.2003→9.4003 mm, and
`Y_XU.3`→`U_XU.33` 5.6627→5.8555 mm.  The source has qualitative local-crystal
requirements but no numeric ceiling that makes this a geometry rejection.
It is nevertheless a mandatory P3-local check before retaining the U_XU shift.

Finally, the probe moves reference legends for all 27 moved refs and
`U_ADC_I2C_XLATE` to F.Fab. That avoids an assembly-silk claim; it is not an
acceptable final assembly labeling result.

## Required next experiment

Use this exact board for one route-only experiment: prove each TDM endpoint’s
package escape, actual width/clearance and layer transition, the staged
translator-to-XU connection, and continuous filled In1.Cu return. In the same
review, prove the XMOS crystal loop and USB pair/ESD return were not degraded,
then restore a readable silk mapping. Reject the candidate if any of those
checks fails. Until then all mouth counts, DRC deltas, and bypass distances are
geometry screens with no capacity, P1, P2, or P3 acceptance.
