# Pod J1 quote comparison at 0 and 180 degrees

**Diagnostic trial only. Neither file approves assembly or resolves the connector
hold.** The user authorized preparing and publishing this test; native boards and
the original r10 package are unchanged. No purchases, reservations, substitutions,
vendor messages, checkout or production/placement approvals.

Use this controlled upload comparison instead of repeatedly searching for a
saved-angle field. It supersedes that prerequisite in the previous MacBook
handoff **for this separate pod experiment only**. Uploaded angle is a known
input; JLC's effective model/production pose still requires physical verification.

## Files and verification

| Upload | File | J1 rotation |
| --- | --- | ---: |
| A baseline | [pod-cpl-J1-000-BASELINE.csv](pod-cpl-J1-000-BASELINE.csv) | 0° |
| B trial | [pod-cpl-J1-180-TEST-ONLY.csv](pod-cpl-J1-180-TEST-ONLY.csv) | 180° |

A is byte-identical to the original r10 pod CPL. B differs in **one field of
one row**: J1 Rotation `0.000000` → `180.000000`. All 29 references, row order,
XY, sides and every other rotation are preserved. J1 remains at CPL body centre
`10.556000mm, -8.373000mm`, Top. [manifest.json](manifest.json) binds the source,
both outputs, generator and native pod. This is not a new release or a permanent
vendor-rotation rule. Do not upload diagnostic KiCad models from other folders.

From the repository root, after safely pulling
`codex/crow-jlc-source-review-20261030` without discarding local work:

```sh
python3 projects/crow-array/order-readiness/r10_upload_check.py
python3 projects/crow-array/order-readiness/quote-tests/r10-pod-j1-180/test_cpl.py verify
python3 -B -m unittest discover -s projects/crow-array/order-readiness/quote-tests/r10-pod-j1-180 -p test_test_cpl.py
```

Use `test_cpl.py build` only to reproduce missing identical outputs; it refuses
to overwrite differing artifacts. No KiCad is required for these checks.

## MacBook comparison procedure

1. **Preserve the existing drafts.** The [current pod draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=71c384e886a94642a54e0c804cea3a97)
   and carrier draft are not test targets for this pass. Prefer a separate
   quote-only copy of the pod draft, clearly named `POD J1 AB TEST NOT FOR ORDER`.
   If duplication is unavailable, create a separate quote-only pod draft using
   the unchanged [pod Gerbers](../../quote-draft/r10-2c8p-outward-power/pod-gerbers.zip)
   and [reviewed grouped pod BOM](../../quote-draft/r9-merged-bom-candidates/pod-bom-merged-v2.csv).
   Use 10 fabricated / 8 assembled, four layers, JLC04161H-7628 and the existing
   finish/mechanical settings from the [r10 handoff](../../MACBOOK-R10-HANDOFF.md).
   Keep automatic production confirmation disabled. Record the new draft URL;
   stop if creating it requires an order, payment, reservation or new commitment.
2. **Load A explicitly.** Upload `pod-cpl-J1-000-BASELINE.csv` to the comparison
   draft even if duplication carried a CPL. Wait for processing and capture
   upload filename/completion plus the resulting preview. Confirm J1 is exact
   Amphenol RJHSE-5080 / C599441 and all 29 required factory references remain.
   Recheck matching/exclusions and quantities after any reset. Do not bypass
   shortages or substitute parts. Save selected top, underside/transparent and
   oblique PNGs, including board landmarks and J1 identity.
3. **Load B to the same comparison draft.** Change only the uploaded CPL to
   `pod-cpl-J1-180-TEST-ONLY.csv`. Do not also rotate using the toolbar. Wait for
   processing and save the same views at the same camera/zoom. Record the upload
   name, hash, completion, timestamp and draft identity. Capture any actual
   absolute fields if available, but their absence no longer blocks this trial.
   The toolbar's 90° is an increment, not the saved component angle.
4. **Compare physical geometry.** Check all eight model terminals and both
   locator pegs against the board holes, then check that the opening faces the
   connector edge. Use the sources below; do not mistake bare holes or markers
   for model pins. Establish top/bottom and any panel translation from known
   landmarks. Literal printed pin numbers are unnecessary when identities are
   established by the manufacturer's asymmetric pattern. An outward opening
   alone is insufficient; do not move XY to make a picture fit.
5. **Reopen and verify persistence.** Reload the comparison draft and recapture
   the B preview. This proves the observed appearance persists, not that an
   undisplayed numeric saved angle is known. If physical registration or upload
   ingestion is inconclusive, restore A by uploading its exact baseline file and
   verify its preview returns. If B clearly passes, it may remain in this
   separate **test draft on HOLD**, pending review. Do not propagate it to the
   original pod or carrier drafts and do not approve placement for manufacture.

If the model shows no meaningful change between A and B, report ingestion/cache
or representation uncertainty. Do not repeat cosmetic rotations. If pins align
but the mouth is wrong, report a model-registration conflict. If the mouth is
outward but terminals or pegs miss holes, B fails. Unclear evidence remains HOLD.

## Reference geometry

Native component-side coordinates are millimetres, X right and Y down. The
opening must face **native −Y**, away from the component area.

| Feature | Native position |
| --- | --- |
| Pin 1 | (7.000, 8.500) |
| Pin 8 | (14.112, 10.280) |
| Left and right locator holes | (4.210, 5.960), (16.910, 5.960) |
| Nominal mouth plane | Y = 0.880, facing −Y |

Pin n has X = 7 + (n−1)×1.016; odd pins have Y8.5 and even pins Y10.28.
The pegs lie toward the opening, ahead of the signal-tail rows. JLC view axes
may differ; do not infer a reflection or offset from screen direction alone.

- [Manufacturer drawing](../../r10-orientation-images/sources/rjhsex080.pdf)
  and [numbered-hole comparison](../../r10-orientation-images/numbered-holes.png).
- [Local fitted-model views](../../r10-orientation-images/pod-orientation.png),
  which are not a replay of the JLC draft.
- [Latest MacBook report and screenshots](../../r10-connector-session-20261101/REPORT.md)
  at source commit `c8b70522`. It confirms the increment-control interpretation
  and records no rotation trial. Preserve these as historical before evidence;
  capture a fresh A after the known baseline upload.

## Return for review

Save actual A/B/reopened/restored PNGs and a short report under a new session
folder in `projects/crow-array/order-readiness/`. Include draft URL, source Git
commit, exact input hashes, upload completion evidence, coordinate-frame mapping,
pin/peg observations, opening direction, other-reference coverage and final
saved/restored state. Mark saved numeric fields unknown unless actually observed.
Report every incidental reset or change. Do not publish account tokens, cookies,
signed private URLs or unredacted HAR files.

Rerun the two integrity checks above. Keep native files and r10 immutable.
Carrier J101–J108 and power J1 remain unresolved and are **not changed by this
pod-only test**. A verified pod result will inform a separately reviewed carrier
test; it is not blanket connector or manufacturing acceptance.
