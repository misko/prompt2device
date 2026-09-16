# JLC digital twin and model-registration procedure

Use this procedure before every order and whenever a 3D body, footprint,
rotation, or adjudication changes. The twin represents JLC's CAD mounted at
the CPL coordinates; it does not replace the board or datasheet authority.

## Contents

1. Inputs and bounded fetching
2. Pad correspondence
3. Mount and transform rules
4. Adjudications
5. Body and model coverage
6. Same-camera render registration
7. Debugging a disjoint overlay

Gate IDs owned here: `A-RENDER`, `MODEL-REG`, `MODEL-SELF`, `NO-BODY`,
`PAD-GEOM`, and `PAD-MISMATCH`. Connector representation closure is owned by
the routed connector procedure as `P-MATE-REG`.

## 1. Inputs and bounded fetching

Run `jlc_twin.py` with the exact board, staged BOM/CPL, assembly policy, and
adjudication register. Fetch JLC footprint/model data per LCSC into a reusable
cache. Classify transient fetch failures as `FETCH-FAILED`, distinct from
`NO-CAD`, and block until retried or independently proven absent.

When the real importer returns a generic failure without a footprint, retain
one bounded direct observation of the exact public component endpoint. Only
HTTP 200 with the exact application response `success: false`, integer
`code: 404`, and `message: Component not found` is affirmative absence.
Redirects, authorization errors, rate limits and unrecognized responses remain
blocking. Preserve URL, UTC observation time, transport status, raw body and
digest in the per-code cache's `catalog-response.json` and
`catalog-response.body`. A confirmed absence stops further retries for that
code in that run; an old observation is never a new fetch result. Successful
CAD takes precedence. This establishes no vendor pad comparison and does not
discharge mounted-body coverage. A native body still requires the separate
reviewed selection and physical evidence below.

Do not parallelize a rate-limited fetch burst. Retry with backoff and heartbeat
and retain already fetched codes. A partial twin cannot pass by shrinking its
denominator.

## 2. Pad correspondence

Fit JLC pads to board pads over quarter-turn rotations and mirror candidates.
Use physical pad numbers and report:

- whole-pattern residual and next-best margin;
- mirror result;
- per-pad multiplicity/alias state;
- pairwise pad-distance disagreement (`PAD-GEOM`);
- independent polarity/orientation channel for symmetric two-pad parts.

A mirrored best fit is critical. `PAD-GEOM` is rotation/translation invariant
and blocks until the footprint is reconciled with the manufacturer land
pattern. Naming differences should use an evidenced `pad_alias` so coverage is
restored rather than waived.

Use `mount_anchor` only when a one-to-many naming scheme makes full fitting
impossible and one unique physical datum plus angle is independently proven.
An anchor is not a model nudge.

## 3. Mount and transform rules

Use one named transform implementation for each frame conversion and pin it to
an external authority:

- board pads through pcbnew for footprint-local ↔ board coordinates;
- asymmetric rendered fixtures through `kicad-cli pcb render` for model frame;
- explicit tests at 0, 90, 180, and 270 degrees.

Mount around the unweighted common-pad centroid unless an evidenced unique-pad
anchor applies. Keep model-local and board-frame offsets distinct. Prefer
`board_dx`/`board_dy` in adjudications and verify the tool's local/board echo.
Apply model rotation and mount offset through the same canonical operator.

Treat the twin and its per-code CAD cache as a relocatable evidence bundle.
Rebind absolute paths embedded by the fetcher to the current cache when loading,
and persist bundle-local model references through `${KIPRJMOD}`. A temporary
atomic-staging directory must never survive in the promoted twin board. After a
producer or cache change, move/copy the bundle once and rerun mounted-body
coverage from its new location before accepting the evidence.

This also applies to explicitly declared manual-install bodies. Copy their
exact resolved source files into the twin's `native_models/` directory and
persist `${KIPRJMOD}` references while retaining scale, offset and rotation.
An absolute path into the author's project is provenance, not a portable
delivered model. An unresolved source body still fails `NO-BODY`.

Never validate a transform only at 0/180 degrees; sign errors are invisible
there and fail exactly at 90/270. Never treat an inverse mapping as suspect
because its formula resembles a previously wrong forward mapping—grade the
frames and authority, not text similarity.

## 4. Adjudications

Keep findings and mechanisms separate:

- `pad_alias`: numbering convention only;
- `mount_anchor`: independently proven unique datum;
- `model_rot_z`: model orientation correction, only with render/terminal
  evidence against JLC's own model orientation;
- `board_dx`/`board_dy`: measured board-frame body correction;
- `render_model_extension`: choose an explicitly evidenced sibling STEP/STP/
  WRL representation when the generated representation has a signed-Z or
  renderer defect; the requested sibling must exist or the twin fails;
- `render_model_source: native`: retain the source board's exact, hash-bound
  manufacturer body for the explicitly listed `refs` when the catalog body's
  mating datum fails `P-MATE-REG`. Vendor pad correspondence and rotation
  checks still run, the rejected vendor identity remains in the receipt, and
  the native file is copied into the relocatable twin bundle. This is not a
  wildcard waiver and requires a non-empty `refs` list;
- `plan_bbox_expand_mm`: symmetric, measured plan-envelope difference between
  that selected representation and the independently parsed WRL. This changes
  the expected envelope only; centre alignment and the ordinary A-RENDER
  tolerance remain active;
- explicit dispositions for `PAD-GEOM`, `MODEL-SELF`, `MODEL-REG`, polarity,
  and true missing CAD.

For successfully fetched catalog footprints with zero model clauses, an explicit
`native_representation` declaration may select a drawing-derived native body.
Bind the exact code/MPN, vendor-footprint/model SHA, primary PDF pages/revision,
source footprint, generator, provenance, reviewer/date and limitations. Require
an exact-ref `all_pad_centres` registration group with signed `mount_side`;
reject stale registration, changed inputs or a newly supplied vendor model.
Copy the complete accepted registration bundle and exact native file into the
twin; the generated receipt binds both board identities and the unchanged
model transform. A-RENDER reopens delivered evidence and uses independent
mounted-side Fab versus actual image differences. Missing fetch data never enables this
path, and every CPL body remains required. Run relocation and hostile-input
controls before accepting the generated evidence.

Account for a position delta by mechanism. A land-pattern shift cannot be
described as bbox asymmetry or fit residual. One waiver cannot discharge two
independent obligations. Preserve the raw failed fit in evidence.

Measure body-vs-pad shifts from populated-minus-bare image differences rather
than color thresholds. Exposed pads, leads, silk, and solder mask do not have a
stable universal color. Diff before/after renders to prove an applied nudge.
When changing model representation, additionally render the selected model in
isolation from both board sides: prove its signed mount side, measure the plan
envelope delta, and show that it no longer occludes a legitimate opposite-side
body. Never use an envelope expansion to compensate for a centre translation.
For explicit native retention, A-RENDER derives its expected plan position
from the independently authored mounted-side Fab physical envelope while the measured
position still comes only from populated-minus-bare pixels. Absence of that
Fab envelope is a failure; the selected body's SHA remains owned by the
connector datum receipt.

## 5. Body and model coverage

Generate six populated views, a navigable twin board, and same-camera bare
top/bottom views. Independently verify every CPL designator resolves to a
nonempty 3D file. Generate `missing_models.txt`; never hand-author it.

Plan-view registration and mount-side registration are separate obligations.
For each native-model registration coupon, render at least one orthogonal side
profile, locate the PCB plane from the authored coupon geometry, and measure
visible model-pixel occupancy on both signed sides of that plane. A front-mounted body
must have the declared minimum fraction above the board; a back-mounted body
must have it below. Leads crossing the plane are expected and therefore a
small opposite-side fraction is not itself a failure. The declared mounting
side and threshold are configuration, while the measured fractions and side
images are evidence. Include a known-bad fixture with an intentionally
inverted model: an XY-perfect body below the PCB must fail.

Report `bodies mounted: N/M`. `PAD-MISMATCH`, a fetch waiver, or a large number
of findings does not prove mounted-body coverage.

Run model-to-own-footprint (`MODEL-SELF`) and mounted-model-to-board
(`MODEL-REG`) checks. Both block when unadjudicated. `MODEL-REG` includes both
XY registration and signed mount-side occupancy; passing one cannot compensate
for failing the other. Bbox metrics are broad detectors rather than rotation
authority. For an asymmetric connector, a body center can legitimately differ
from the courtyard center. JLC's own footprint/model transform plus visibly
aligned leads/pins outranks a tempting 180-degree bbox improvement.

Registration still does not prove which side is the mating mouth. For an
edge-mounted connector, load `connector-orientation.md` and close `P-ORIENT`
independently; never promote a bbox or symmetric-hole fit into direction truth.
When the twin swaps in a vendor model, also require its automatic
`P-MATE-REG` receipt. This compares mating-side support along the independently
authored access axis, not bbox centres. Generic `MODEL-REG` adjudication cannot
waive it: a substituted rendering that disagrees with the approved connector
datum is diagnostic evidence, not a reason to move the physical footprint.

## 6. Same-camera render registration (`A-RENDER`)

Run `twin_overlay.py` after twin generation and before human render review.
Use populated and bare images from the exact same board, camera, projection,
crop, and resolution. Run each populated side; reject perspective views,
filename/side mismatches, dimension mismatches, and sides without usable
courtyards.

The overlay has three independent geometric concepts:

1. board footprint/courtyard expectation;
2. transformed 3D model expectation;
3. measured populated-minus-bare body pixels.

Render each box/shape separately and in a combined overlay with a legend,
coordinate frame, component ref, LCSC, rotation, expected/mounted/measured
centers, and deltas. Do not assume one box should always enclose another:
courtyard, pad pattern, model bbox, and visible-metal/body pixels describe
different physical extents. Their centers and relevant mating/contact regions
must agree within the declared criterion.

Read coverage as well as verdict. Name every unresolved component and reason.
A component expected to be measurable but not extracted is a failure, not an
omission.

## 7. Debugging a disjoint overlay

When a connector appears outside its pads or colored boxes are disjoint:

1. Pick one ref; do not debug the whole panel at once.
2. Reopen its footprint, pads, courtyard, CPL row, JLC model transform, and
   adjudication.
3. Render bare and populated views at high resolution with identical camera.
4. Draw pad/courtyard, transformed-model, and measured-diff geometry from their
   independent sources.
5. Print all coordinate-frame conversions and 0/90/180/270 fixture results.
6. Check that the mount uses common physical pad numbers or the declared anchor.
7. Check that expected geometry consumes the same final adjudication used to
   build the twin without deriving expectation from rendered pixels.
8. Inspect the signed side profile: body above/below the PCB, lead penetration,
   mounting side, and model Z offset are independent of top-view overlap.
9. Change one transform/nudge source, rerender, and measure the before/after
   centroid shift.

Do not fix a render by moving the real footprint unless independent PCB and
mechanical evidence says the footprint is wrong. A render/model failure and a
board placement failure are different dispositions.

## True catalog CAD absence

An explicit `native_representation.reason: vendor_cad_absent` selects a
reviewed native body when the exact public component endpoint supplies neither
footprint nor model. Require the dedicated independent absence and physical
pin/land reviews, exact response-body SHA, primary drawing, source footprint,
model, producer or verbatim import recipe and provenance. A newly captured
HTTP200/application404 observation must match the reviewed body and be no older
than24hours at twin production. New vendor CAD reopens the selection.

Write `catalog_comparison: unavailable`. No catalog residual, pad fit, or
rotation acceptance exists. Keep the raw NO-CAD finding and every CPL body in
the denominator. Signed native registration and actual same-camera extraction
remain mandatory. Copy all bound source authority files, registration outputs,
model and raw observation into the relocatable bundle. Offline overlay binds
the exact production-time observation; it does not claim a fresh network read.
An absent observation, changed review, changed model or missing native Fab
must fail. The uploader's exact-part assembly preview remains an order hold.

Extended SMD lands can place copper centers outside the package. An explicitly selected `all_smd_pad_overlap` registration datum tests positive-area intersection of every native effective copper polygon with the independently measured model plan envelope, while retaining Fab, courtyard and signed-side checks. It reports overlap counts, not center containment or solder qualification. Separate primary terminal/land and pin review is still required.

Native physical registration selects F.Fab/F.CrtYd for F.Cu footprints and B.Fab/B.CrtYd for B.Cu footprints. Opposite-side graphics cannot supply missing datums. A declared mount_side must agree with the native footprint; mixed-side groups are refused. Coupons preserve the native flip, normalize board rotation, and render populated and bare images from the actual mounted side. Bottom plan pixels are X-mirrored, with ordered inverse boxes used for native pad intersections. The registration tuple binds side, owned geometry, model transform, contract and tool bytes. Historical v1 native_top filenames remain stable bundle members; plan_camera and plan_projection in the report state their actual view.

Signed-side registration measures visible exterior pixels and does not prove
full model-volume exclusion from the board. The native engine declares this
G-VACUOUS limitation and binds a subject-first executable fixture: an inverted
1 mm nested-transform body falsely passes, while the height-only 3 mm contrast
fails the unchanged signed-side predicate. When full-volume exclusion matters,
require independent exact-model native geometry evidence in addition to the
registration receipt. Existing required-fail controls remain mandatory.


Native plan extraction also has a thin-feature sampling limitation. Two
3x3 erosions can delete actual exterior features before the surviving-pixel
union is measured, and restoring two pixels does not recover them. A PASS
therefore does not establish complete occupied extent at every coupon scale.
The bound G-VACUOUS fixture first requires a false PASS for an actual thin
exterior feature beyond courtyard, then requires FAIL for a thicker feature
at the same extent. Where this property matters, supplement ordinary
P-MODEL-REG with independent exact-model native full-extent/courtyard evidence
and original un-eroded images; an actual exterior feature outside courtyard
must fail or remain incomplete even if the eroded-pixel gate passes. Fab is a
union of geometric marks, so exterior-feature detail changes its bbox datum
and does not separately recognize a retained nominal-shell rectangle. Preserve
independent primary-drawing shell and attachment-datum evidence. Nominal CAD
containment is not a manufacturing-tolerance or physical-fit guarantee.
