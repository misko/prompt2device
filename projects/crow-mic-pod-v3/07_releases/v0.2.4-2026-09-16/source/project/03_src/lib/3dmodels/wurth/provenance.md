# Wurth615008160221 manufacturer native model

Source: https://www.we-online.com/components/products/download/KiCad_WR-MJ%20%28rev26c%29.zip retrieved2026-09-12. WholezipSHA256 80e868f8f2d362198e4523cc6f424d292a46f637f4cf366a3231c2800d257914. Original exactnativefootprintSHA256 0a4a62dc8be59e02aa157d0ef910422ae381dc81ba7300d891fd8066ed0001c7. Original modelSHA256 3f902b89d4bd756b121be056782deff312efb127c9c48f2c798ebd6db0e59f49. Modelcopiedunchanged; no translation/rotation/scale applied. Footprint retains manufacturer hole/pin/body/courtyard/model authority and remaps S1/S2 to electrical pads9/10. Project-derived shield copper lands and board-safe silk are documented below; model path and library name are adapted. BlankNPTHremainunnumbered.

Native modelmathYisoppositetoKiCadPCB+Y-down. Mouthmodel+Y6.360054=>footprint-Y6.36. Originpad1. Barebody15x13.45x14.7mm; freeEMIfingers enlargeactual11-solid modelbox tox[-5.058081,12.218081],y[-7.09,6.360054],z[-3.254712,15.838181]. RootOCPmeasurement corroboratesmodelregistration, notmanufacturer tolerancelimits or physicalfit. Manufacturerdrawing001.003 governstolerances.

The separatelydownloadedgenericSTEP reportsoneunresolvedreference; it isretainedforensicandnotusedhere. Manufacturer KiCadmodel importswithoutthaterror. Initialsource-researchpin/tableerrors areexplicitlyrejected; see source-researcharchive168cb286ee392f49e1ec95ab9e66077b0069bb63ca653665095a3d7262204160. Assembly/latch/panelbondandtemperature testsremainowed.

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
