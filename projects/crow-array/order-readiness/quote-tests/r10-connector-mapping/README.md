# Connector mapping measurements and diagnostic CPLs

The original measurement tools support a 180-degree catalog-to-native local
rotation for both connector types. Replaying the generated CPLs against the
retained catalog footprints aligns all ten native connector instances: maximum
RJ terminal error 0.014 mm, maximum locator-centre error 0.004 mm, and power-jack
terminal error below numerical precision. These are nominal CAD residuals,
not manufacturing tolerances or verification of the live JLC placement.

**These files assume JLC uses the retained catalog footprint origin directly.**
The active draft's interpretation remains unverified. Do not replace the r10
package, update the global rotation authority table, or approve manufacturing.
Native boards, Gerbers, BOMs and all non-connector CPL rows are unchanged.

## Measurement results

| Native reference | Native angle | Measured local correction | Diagnostic CPL angle | Diagnostic CPL XY in mm |
| --- | ---: | ---: | ---: | --- |
| Pod J1 | 0 | 180 | 180 | 10.556, −9.390 |
| Carrier J101–J108 | 0 | 180 | 180 | Existing X, −9.390 |
| Carrier power J1 | 180 | 180 | 0 | 185.650, −11.700 |

The power-jack correction composes with its native 180-degree orientation;
copying the RJ's absolute 180-degree value would be wrong under this mapping.
The pod file is byte-identical to the previously prepared test C. It is now
cross-checked with the original rotation measurement code, not a new candidate.

## What was recovered from the original procedure

`mapping.py` uses `jlc_rotation_measure.fit_by_number` for all four quarter-turns
and the original exporter's `placement_datum` for comparison. It reopens both
native boards, compares terminals to the retained manufacturer-derived inspection
facts, derives the raw catalog-origin translation, and then replays the actual
CSV coordinates using a separate transform with **no refitting or recentering**.
The locator holes are checked separately from the numbered-terminal fit.

The general legacy datum rule is not an exact origin oracle for every catalog
part. For C599441 its pad-centre bounding box includes the two unnumbered locator
holes, so the catalog datum is `(0, 1.270)` mm rather than `(0, 0)`. Applied to
native pod J1, it gives `(10.560, 8.120)` rather than the raw-origin registration
`(10.556, 9.390)`. The 0.004 mm X difference reflects catalog rounding. Neither
that generic rule nor the body-centre CPL establishes the live JLC insertion
point. C3096093's catalog pad bounding-box centre is `(0, 0)` and does not have
this particular discrepancy.

The exact maker drawings, inspection facts, catalog footprints, native boards,
source CPLs and measurement code are bound in [measurements.json](generated/measurements.json).
Mouth direction remains inherited from the manufacturer-bound native inspection;
this calculation does not inspect a live vendor 3D mouth. Catalog drill/land
sizes are not adopted as replacement native hole specifications.

## Files and controlled browser sequence

Start with the existing [POD J1 AB TEST NOT FOR ORDER draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=1f8dfa850b474dc9b4ac3860b26bbd59).
Use only this separate diagnostic draft. The reported disabled-tab observation
must be reconciled on the MacBook before an upload; if it remains disabled,
capture the state and stop without recreating the draft.

1. Confirm A restored, exact RJHSE-5080 / C599441 matching, 10 fabricated /
   8 assembled, and both review preferences set to Do not confirm automatically.
2. Obtain a usable 2D terminal overlay or underside view that distinguishes
   board holes from actual solder tails and pegs. The existing
   [read-only scene capture](../r10-pod-j1-origin/SCENE-CAPTURE.md) is an alternative
   if those features are hidden. Do not count socket spring contacts as tails.
3. Only when registration can be observed, compare the known
   [B rotation-only file](../r10-pod-j1-180/pod-cpl-J1-180-TEST-ONLY.csv) with
   [the measured raw-origin pod trial](generated/pod-ALL-CONNECTORS-RAW-ORIGIN-TEST-ONLY.csv).
   Their only difference is J1 Y. No toolbar rotations or dragging. Record
   file hashes, processed matching, identical-camera views, all eight numbered
   terminals, both peg centres, and the mouth relative to the board notch.
4. Reopen to confirm persistence, then restore
   [baseline A](../r10-pod-j1-180/pod-cpl-J1-000-BASELINE.csv), confirm restoration,
   and leave the diagnostic draft on HOLD. Return the observations for review.

If neither geometry nor usable physical-feature views are available, stop this
session. A second visual-only offset experiment adds no alignment evidence.
The preferred escalation is a source-bound JLC placement inquiry, requiring
fresh authorization to send; the fallback is to retain the order hold.

These carrier files are prepared for later separate diagnostics, not immediate
uploads to the original carrier draft:

- [J101-only trial](generated/carrier-J101-ONLY-RAW-ORIGIN-TEST-ONLY.csv): after pod review, establish one carrier instance independently.
- [Power J1-only trial](generated/carrier-J1-ONLY-RAW-ORIGIN-TEST-ONLY.csv): separate three-terminal and mouth-direction check; do not combine it with the RJ trial.
- [All-connector candidate](generated/carrier-ALL-CONNECTORS-RAW-ORIGIN-TEST-ONLY.csv): held until the individual mappings are resolved; every J101–J108 instance still needs final checking.

No purchases, reservations, substitutions, vendor messages or manufacturing
approvals. This does not qualify other components or the home-installed Pico.

## Reproduce and check

Run from the repository root with the KiCad-capable Python interpreter:

```sh
/usr/bin/python3 -B projects/crow-array/order-readiness/quote-tests/r10-connector-mapping/mapping.py verify
/usr/bin/python3 -B -m unittest discover -s projects/crow-array/order-readiness/quote-tests/r10-connector-mapping -p test_mapping.py
python3 projects/crow-array/order-readiness/r10_upload_check.py
```

`build` creates missing identical diagnostic outputs and refuses differing ones.
The ten tests cover all ten connectors, wrong rotation, wrong body datum, the
generic-datum counterexample, maker peg spacing, swapped pins, missing pegs,
native-engine 0/90/180/270 transforms, exact changed-row isolation, prior test C
equivalence, invalid side/nonfinite data, and duplicate/missing references.
The original skill's enforced per-code authority gate has not yet been added to
vNext; this project-level experiment supplies evidence for that later change,
not an assertion that the process gap is fixed.
