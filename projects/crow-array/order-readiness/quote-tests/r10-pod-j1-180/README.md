# Pod J1 quote comparison at 0 and 180 degrees

**Diagnostic trial only. Neither file approves assembly or resolves the connector
hold.** The user authorized preparing and publishing this test; native boards and
the original r10 package are unchanged. No purchases, reservations, substitutions,
vendor messages, checkout or production/placement approvals.

Use this controlled upload comparison instead of repeatedly searching for a
saved-angle field. It supersedes that prerequisite in the previous MacBook
handoff **for this separate pod experiment only**. Uploaded angle is a known
input; JLC's effective model/production pose still requires physical verification.

## MacBook handoff updated 2 November 2026

Run this test in the MacBook browser using local files from the shared repository.
Two further TinyFish attempts ended without a test draft, CPL upload or alignment
images. The first failed to create a separate draft; the second reported inability
to operate the file picker. They reported leaving existing drafts unchanged.
See the [assessment](browser-assessment.json) and retained
[first](browser-attempt-1.json) and [second](browser-attempt-2.json) reports.
These are automation limitations observed in those runs, not proof that JLC
prohibits new drafts or file uploads. Do not repeat the duplication search.

Create a fresh diagnostic draft using the exact files below. A separate copy is
also acceptable if immediately available. Uploading existing files to a new draft
does not change those files. Leave the original pod and carrier drafts untouched.
The target is a documented comparison, not an order or placement approval.

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
git status --short
git fetch origin codex/crow-jlc-source-review-20261030
```

Only in a clean checkout already on that branch, fast-forward with
`git merge --ff-only origin/codex/crow-jlc-source-review-20261030`.
If the checkout is dirty or on another branch, use an isolated worktree rather
than resetting or overwriting it. Record `git rev-parse HEAD`, then run:

```sh
python3 projects/crow-array/order-readiness/r10_upload_check.py
python3 projects/crow-array/order-readiness/quote-tests/r10-pod-j1-180/test_cpl.py verify
python3 -B -m unittest discover -s projects/crow-array/order-readiness/quote-tests/r10-pod-j1-180 -p test_test_cpl.py
```

Use `test_cpl.py build` only to reproduce missing identical outputs; it refuses
to overwrite differing artifacts. No KiCad is required for these checks.

## MacBook comparison procedure

1. **Preserve the existing drafts.** The [current pod draft](https://cart.jlcpcb.com/smt-order/?pcbFileNo=71c384e886a94642a54e0c804cea3a97)
   and carrier draft are not test targets for this pass. Create a fresh
   quote-only pod draft, clearly named `POD J1 AB TEST NOT FOR ORDER`, using
   the unchanged [pod Gerbers](../../quote-draft/r10-2c8p-outward-power/pod-gerbers.zip)
   and [reviewed grouped pod BOM](../../quote-draft/r9-merged-bom-candidates/pod-bom-merged-v2.csv).
   Use 10 fabricated / 8 assembled, four layers, JLC04161H-7628, ENIG,
   precision outline ±0.1 mm, top assembly and the remaining mechanical settings
   from the [r10 handoff](../../MACBOOK-R10-HANDOFF.md). Stackup and finish are
   separate selections. Record any rail or finished-edge uncertainty; it remains
   a manufacturing hold. Keep both production-file and placement-review options
   at **Do not confirm automatically**. Record the new draft URL;
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
| Pin 2 | (8.016, 10.280) |
| Pin 3 | (9.032, 8.500) |
| Pin 4 | (10.048, 10.280) |
| Pin 5 | (11.064, 8.500) |
| Pin 6 | (12.080, 10.280) |
| Pin 7 | (13.096, 8.500) |
| Pin 8 | (14.112, 10.280) |
| Left and right locator holes | (4.210, 5.960), (16.910, 5.960) |
| Nominal mouth plane | Y = 0.880, facing −Y |

Pin n has X = 7 + (n−1)×1.016; odd pins have Y8.5 and even pins Y10.28.
The pegs lie toward the opening, ahead of the signal-tail rows. JLC view axes
may differ; do not infer a reflection or offset from screen direction alone.
The underside view reverses apparent handedness relative to the top. Establish
pin 1 from the drawing and asymmetric tail pattern, not from leftmost position
on screen. Check the model's PCB solder tails, not the spring contacts inside
the socket. These coordinates are reference geometry, not permission to move XY.

For A and B, report each of pins 1–8 and both pegs as **aligned**, **misaligned**
or **not visible**, with its screenshot filename. Use an underside close-up for
tails and an oblique/transparent view for pegs if needed. If any feature is hidden,
the visual alignment verdict remains incomplete; do not fill it from the local
CAD render. Save originals alongside annotated copies identifying the witnesses.

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
folder in `projects/crow-array/order-readiness/`, for example
`r10-pod-ab-session-20261102/`. Use distinct names such as `A-top.png`,
`A-underside.png`, `A-oblique.png`, the equivalent `B-*` views and
`B-reopened.png` (or `A-restored.png`). Include draft URL, source Git
commit, exact input hashes, upload completion evidence, coordinate-frame mapping,
pin/peg observations, opening direction, other-reference coverage and final
saved/restored state. Mark saved numeric fields unknown unless actually observed.
Report every incidental reset or change. Do not publish account tokens, cookies,
signed private URLs or unredacted HAR files.

Return a short conclusion: **B visually aligned**, **B failed**, or
**inconclusive**, plus the final saved state and any remaining manufacturing
holds. Commit and push only the new session evidence and STATUS update to the
shared branch, then provide the commit and test-draft URL. Do not edit the
immutable test manifest to turn its original preparation status into approval.

Rerun the two integrity checks above. Keep native files and r10 immutable.
Carrier J101–J108 and power J1 remain unresolved and are **not changed by this
pod-only test**. A verified pod result will inform a separately reviewed carrier
test; it is not blanket connector or manufacturing acceptance.
