
## Retained primary-source provenance

# Würth 615008160221 source record

The manufacturer drawing is revision 001.003, dated 2025-07-09 and retrieved
2026-09-12. Its local PDF SHA-256 is
`6ed18749211d4e6cbffd99cd0b90461dfe4ec6d70f558ceceeb5901651f0e048`.
Source: https://www.we-online.com/components/products/datasheet/615008160221.pdf

The body is nominally 15 × 13.45 × 14.7 mm above the PCB, with ±0.15 mm
on those dimensions. The manufacturer KiCad WR-MJ library, revision 26c,
supplies the exact native footprint and STEP; provenance is recorded beside
the model. Include the free EMI fingers when evaluating the full geometry.
The STEP is nominal CAD, not a qualified manufacturing tolerance envelope.

There are eight signal drills of 0.8 mm, two unnumbered 3.18 mm locating
holes and two shield slots of 1 × 2 mm. Same-row pitch is 2.04 mm, stagger
is 1.02 mm and row spacing is 4 mm. Manufacturer shield pads S1/S2 are
renamed 9/10. Project-derived shield copper lands and board-safe silk are
documented below; hole geometry is unchanged. The circuit assignment belongs to
the synchronized spoke contract and TSX source.

Published 1.5 A and 20 mΩ maximum contact resistance apply to the jack,
not the Weidmuller cord. Manual soldering, bottom clamp assembly, system ESD,
wet entry, populated mating and installed tolerances require qualification.

## DC application basis — source review pending

The exact manufacturer's [Gigabit modular-jack product page](https://www.we-online.com/en/components/products/WR_MJ_MODULAR_JACKS_OVER)
lists 615008160221 in the range stated to be PoE++ compatible under
IEEE 802.3bt. This is application evidence separate from the exact datasheet's
150 VAC working rating. The latter remains explicitly AC and is never copied
into a DC maximum field. Retrieved 2026-09-12; raw page SHA-256:
`4103cebf3e1024dbd2aae87115e2f676627ae5b3e1cb6cfd1d4f6e0bd556fae4`.

Engineering inference for source review: PoE uses DC common-mode power on
these contacts, with a 57 V supply ceiling. A corroborating manufacturer
[PoE++ application page](https://www.we-online.com/en/components/products/WE-POE-PLUS-PLUS)
identifies 37–57 V DC input in that application. It is contextual voltage
information, not a rating transferred from a transformer to this jack.

For this power-off-mated, dry IP20, 13.2 V maximum normal spoke, adopt a
project insulation design ceiling of 28.5 V DC (57/2, a project 2x reserve).
The existing E-SURGE recommended/absolute comparison fields both use that
same deliberately lower project ceiling; neither asserts that the manufacturer
publishes a 28.5 V or 150 V DC absolute maximum. The 24.4 V component clamp
plus 10% coordination margin is 26.84 V, below 28.5 V by 1.66 V.
This is a bounded application assessment, not an AC-to-DC conversion, current
rating, surge waveform guarantee, PoE interoperability claim or hot-plug rating.
Physical first-article qualification and the upstream transient/source bounds
remain owed under the existing first-article-only restriction.

## Project-derived copper lands and board-safe silk — 2026-09-12

The drawing page 1 specifies holes, not the modified copper land. Its eight
0.8 mm signal drills, two 3.18 mm NPTH and two 2 x 1 mm shield slots, all
centres and orientations, remain unchanged. The WR-MJ rev26c signal pads,
F.Fab body, courtyard, mouth frame and unmodified STEP registration also
remain unchanged. Shell S1/S2 are electrical pads 9/10.

The project changes only the two shield copper ovals from 3 x 1.5 mm to
2.5 x 1.5 mm at their existing 270 degree orientation, around unchanged
2 x 1 mm oval slots. This is a project-derived land, not a manufacturer
recommendation. Equal 0.25 mm radius expansion of the slot gives a uniform
0.25 mm nominal annulus, preserving the previous minimum annulus while
reducing the long-end annulus from 0.50 to 0.25 mm. The nearest NPTH centre
is 0.55 mm across and 3.05 mm along the land axis. Capsule-to-circle gap
is sqrt(0.55^2 + (3.05 - (L-1.5)/2)^2) - 0.75 - 1.59 mm:
L=3 gives 0.024847 mm; L=2.5 gives 0.268639 mm. The latter has 0.018639 mm
nominal margin over the unchanged native 0.25 mm hole-to-copper floor.
These are nominal artwork distances, not a manufacturer tolerance guarantee.

At the locked local board edge y=-5.86 mm, the two forward side-silk lines
end at y=-5.50 mm (0.12 mm stroke), giving 0.30 mm ink-to-edge distance.
The outboard horizontal mouth line at y=-6.47 and marker at y=-6.945 are
omitted. Rear/side silk remains; F.Fab and courtyard keep the complete body
outline, and generated pin-1/pinmap identification remains available.
No connector anchor, mouth exposure, rule, exclusion or waiver changes.

Derived footprint SHA-256: `71ddc2085058b171a232326aec8adfe5d13ea40cf5c974b4aa9bfd0fea528ec0`.
Manufacturer original footprint SHA-256:
`0a4a62dc8be59e02aa157d0ef910422ae381dc81ba7300d891fd8066ed0001c7`.
Unchanged model SHA-256:
`3f902b89d4bd756b121be056782deff312efb127c9c48f2c798ebd6db0e59f49`.
Native local proof and independent source adoption are separate; full
integrated regeneration and placement/routing/assembly gates remain owed.

## Nominal free-state spring-finger Fab detail — 2026-09-13

Append-only derivation following the preceding shield-land/silk change.
Both exact-part footprints add circular F.Fab arcs and end lines from native
STEP shell sections at model z=4.14 and 10.62 mm, the midplanes of all four
lateral spring fingers. Exactly coincident end lines are represented once; upper/lower circular
projections are retained separately, including their submicrometre differences.
Arc start/mid/end coordinates are native circle samples rounded to 0.000001 mm;
footprint plan Y is minus model Y. The original 15 x 13.45 mm nominal-shell
rectangle, courtyard, pads/drills, silk and model transform remain unchanged.
This detail is MEASURED nominal/free-state CAD from unchanged manufacturer
STEP SHA-256 3f902b89d4bd756b121be056782deff312efb127c9c48f2c798ebd6db0e59f49.
Drawing rev001.003 page1 depicts these fingers but does not dimension their
free span. Its 15 +/-0.15, 13.45 +/-0.15 and 14.7 +/-0.15 mm leaders specify
main shell dimensions, not finger limits. Full nominal local occupied extent
is X[-5.058081,12.218081], Y[-6.360054,7.090000] mm. Right courtyard
centerline margin is only 0.001919 mm; no manufacturing containment guarantee.
The native Fab union now represents exterior tips and cannot independently
recognize the retained nominal shell. Exact-product shell/drill/native-extent
and raw-image evidence supplement ordinary registration, whose erosion can
omit thin features. Existing physical first-article obligations remain.

Candidate footprint SHA-256: `c8286c258474bde37022ef16730c7976e488d5fd7312699870ed54ee0dccc7d6`. Independent source acceptance,
full downstream regeneration and placement/orientation review remain owed.
