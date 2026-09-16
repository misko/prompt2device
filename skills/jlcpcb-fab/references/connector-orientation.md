# Connector orientation and mating-access review

Use this procedure for every edge-mounted connector and whenever its footprint,
native model, vendor/twin model, placement, board outline, or intended mating
edge changes. It closes `P-ORIENT` and `P-MATE-REG`; it does not replace
pin-map, native-model registration, courtyard/body clearance, enclosure, or
cable-service checks.

## Contents

1. One fact, one owner
2. Gate position and execution
3. Human evidence
4. Debug one reference

## One fact, one owner

Do not infer a connector mouth from a bounding-box centre, symmetric mounting
holes, reference text, pixels, or a model that merely fits its footprint.
Those channels can all be consistently backwards.

The sources are deliberately split by what they uniquely know:

- `03_src/floorplan.yaml` `asserts.edge_faces[]` owns the intended board edge
  (`x0`, `x1`, `y0`, or `y1`). Do not repeat the edge in another contract.
- The existing `03_src/rules/model_registration.yaml` group owns the exact
  model identity and an optional `orientation:` block. The block records the
  footprint-local mouth axis, model-local mouth/up axes, mounting side,
  mating-plane depth, allowed signed edge offset, and one keyed pad.
- A manufacturer drawing or exact manufacturer STEP owns those local axes and
  the mating-plane depth. Name that authority in the block.

Every realised `J*` reference is in the denominator. It must be orientation-
declared or listed in `orientation_exemptions` with a non-empty reason. Every
declared ref must have exactly one `edge_faces` row, and every `edge_faces` row
must be orientation-declared. Silence, an empty list, and 0/0 are not a pass.

The source board retains its approved native model. A fabrication twin may
substitute JLC's model because it is an independent representation, but the
substitution is never silent authority. `jlc_twin.py` automatically reads this
same contract and writes `connector_datum_receipt.json`
(`connector-datum-receipt-v1`). For every declared connector it binds both
model identities, the vendor transform, F.Fab and vendor body envelopes, the
access axis, and vendor support versus the authored mating plane. The allowed
delta defaults to the smaller of `fit_tolerance_mm` and 0.75 mm. Set
`representation_mating_tolerance_mm` only from manufacturer evidence.

Example extension to an existing model-registration group:

```yaml
orientation:
  authority: "Manufacturer drawing rev C and exact SHA-bound STEP"
  mount_side: front
  footprint_access_axis_local: [0, 1, 0]
  model_access_axis_local: [0, -1, 0]
  model_up_axis_local: [0, 0, 1]
  mating_plane_offset_mm: 8.20
  edge_offset_range_mm: [-0.20, 0.30]
  key_pad: "1"
  model_z_offset_range_mm: [-0.05, 0.05]
```

KiCad board coordinates use +X east/right and +Y south/down. Local axes are
unit vectors before footprint rotation and side mirroring. Footprint-local axes
use KiCad's Y-down convention; model-local axes use the exact native model's
Y-up convention. The gate applies KiCad's model matrix in renderer order:
nonuniform scale, negative stored X/Y/Z rotations, then the native-to-footprint
basis reflection (Y on F.Cu, X on B.Cu). A positive signed
edge offset means the mating plane projects beyond `Edge.Cuts`; a negative
value means it remains inboard. The allowed range comes from the connector
drawing plus the board/enclosure decision, not from the current placement.

## Gate position and execution

Run `connector_orientation_gate.py` after `P-MODEL-REG` and deterministic route
preparation, before placement review or route import. Use the script's `--help`
for exact syntax.

At fabrication-twin generation, `P-MATE-REG` runs automatically whenever this
contract exists. It compares the substituted body's support in the authored
access direction with the approved F.Fab physical datum. A pad-perfect,
correctly rotated model can therefore still fail when its shell or mouth is
recessed or advanced. `P-MATE-REG` cannot be discharged by generic
`MODEL-REG`, pad-fit, asymmetry, or render adjudication. Correct the derivative
model selection/transform or retain the approved native body, then regenerate.
Native retention is explicit per ref with `render_model_source: native`; the
receipt must bind the selected native SHA and still identify the rejected
catalog model. It never suppresses catalog pad or rotation checks.

The machine half checks, for every declared instance:

1. exact native-model SHA and exactly one model;
2. declared front/back mounting side and non-mirrored model scale;
3. model mouth versus footprint mouth, and model up versus board up;
4. transformed footprint mouth versus the single `edge_faces` authority;
5. the access ray leaves the closed board through that edge;
6. manufacturer mating-plane depth versus the measured `Edge.Cuts` distance;
7. one and only one keyed pad.

`P-ORIENT` consumes, but does not duplicate, the preceding `P-MODEL-REG`
mount-side result. Before directional views can be reviewed, the exact model
must already pass signed-Z side-profile evidence for its declared front/back
side. A connector whose mouth axis is correct but whose body is underneath the
PCB is a model-registration failure and cannot reach human orientation review.

A human cannot override a machine failure. Correct the owning source and
regenerate. The command prints render progress as `n/total`; a missing terminal
verdict or external timeout is a failure, never a review pause.

## Human evidence

The gate writes an exact-board review bundle under
`06_build/pre_route/orientation/`. Each image burns in the edge, true native camera side, board rotation,
orthographic projection, target references, renderer identity, and semantic
subject prefix so filenames cannot silently swap camera meaning.
Native views use high-quality rendering and fixed top, bottom, side, and camera
lights so a dark housing does not hide mouth, cavity, latch, or keying geometry.
The magenta box is selected from exact footprint geometry in the top view; it
is never inferred from an image difference. Side crops are projected from the
real connector coordinates through a calibrated board span and deliberately
draw no body box. Physical body bboxes remain exclusively `P-MODEL-REG`'s job.

The native scene resolves every declared model through the existing
`model_coverage_check` substitution table and passes that same table through
both native CLI variable overrides and its explicit environment. Missing
required model files or fitted footprints with no model refuse rendering.
The receipt binds every footprint's native serialized geometry, position,
side, attributes, model visibility/opacity, transforms and file hashes, plus
board drawings, setup/stackup and thickness. It also binds the renderer
configuration, command options and camera recipes. Routing segments and zone
fills are outside this orientation subject; setup changes are conservative
invalidation. The external resolver/reader and native executable identities
participate in tool identity.

Rendering uses a fresh isolated native configuration and the explicit empty
appearance preset, which enables every footprint class, including DNP. Native
per-model visibility and opacity remain as authored. The CLI's default board
stackup colors are retained and their source is bound; KiCad 10.0's explicit
boolean-value option is not used because it throws `bad_any_cast`. The receipt
is a declaration/resolution census, not a claim that every model is visible
through occluders or successfully parsed by the renderer. Inspect actual native
images. No source body is removed to produce an inside view.

Each unique orientation tuple requires:

- `top`: authored access arrow in board coordinates;
- `outside`: camera on the cable/mating side, where the mouth must be visible;
- `inside`: opposite camera, where the rear shell must be visible.

For opposing north/south rows, mandatory inside evidence uses the complete
native frame from `--side top --rotate 300,0,0` for the north rear and
`--side top --rotate 60,0,0` for the south rear. `--rotate` rotates the board;
it is not a camera-angle flag. These fixed elevated recipes separate opposing
rows in projection. Burned-in board coordinates and west-to-east tuple rank
identify the target. Oblique frames never use the cardinal board-strip crop
or an inferred model bbox. Lower rear portions can remain hidden by nearby
parts; camera selection is not an occlusion oracle. Reject human approval if
the required rear, mouth or keying cannot be judged. This machine blind spot
is maintained as a `VACUITY` fixture, with wrong-direction rejection as contrast.

Orthogonal profiles are included for a single-instance tuple. Their omission
for repeated edge rows is a recorded occlusion note, not a false geometry
failure. Repeated connectors
with the same exact model, transforms, side, rotation, edge, and orientation
contract share one visual representative; every physical reference remains in
the machine denominator and the approval subject.

Ask the user to confirm the visible mouth, mounting side, keying, and cable
approach. Do not write approval merely because the machine half passed or the
user previously said a different stage looked good. After explicit approval,
write `08_reviews/connector_orientation.yaml` through the gate's approval
option. Fresh approval is strict schema 1 and binds the semantic subject, complete
reference denominator, tool identity and every review-image hash. The gate
recomputes machine/scene/camera identity, then reopens the existing receipt
and verifies the closed receipt schema, full subject payload, current scene,
renderer, camera recipes, dimensions, complete instance measurements, failures
and deterministic notes before reusing a review bundle. Missing, extra,
duplicate, malformed or contradictory metadata refuse reuse; changing only a
subject digest never authenticates stale scene fields. Every expected review
image and native render/command/log is reopened against its exact key census
and SHA256. Each native command independently agrees with the current fixed
recipe, substitutions, renderer configuration, tool identity and subject.
The original `renders/rendered_board.kicad_pcb` bytes must agree with every
native command's producer hash and `rendered_board_sha256`. The separate
`observed_board.kicad_pcb` bytes verify the latest `observed_board_sha256`;
routing-only reuse updates that observation, retaining the original producer.
These are consistency checks, not cryptographic signatures or proof of human
judgment. Older bundles lacking this producer evidence require regeneration
and review through the ordinary invocation. Explicit approval refuses an absent, stale or tampered
bundle; first run without the approval option and review the newly generated
bundle. Approval and ordinary continuation never regenerate a verified bundle.
The receipt retains the original rendered-board hash if routing-only bytes
change while the semantic subject remains stable.

Existing schema 2 deliberately supports regenerated pixels for an unchanged
semantic subject and unchanged image-key census. It is not silently retired
or upgraded to strict pixel binding. New scene/camera semantics change the
subject and stale both schemas; no old approval approves this corrected scene.

Placement, model transform, model SHA, local-axis contract, intended edge,
board outline, keyed pad, checker identity, scene body geometry/visibility,
model dependency or camera changes make both approval schemas stale. Image
hash changes stale strict schema 1; schema 2 retains the compatibility behavior
described above. Image-key census changes stale both schemas. Routing-only byte churn does not change the semantic subject.

## Debug one reference

Use the first failing channel; do not repeatedly rerender the whole design:

1. **Model/footprint axis failure:** inspect the manufacturer drawing and exact
   STEP frame, then correct the authored local vector or model transform.
2. **Board-axis/edge failure:** correct the source placement rotation or the
   intended `edge_faces` declaration. Do not rotate only the render.
3. **Mating-plane failure:** reconcile the footprint origin and manufacturer
   mating-plane dimension, then change placement or the evidenced range.
4. **Top box looks wrong:** inspect the footprint geometry/board projection;
   never replace it with a colour threshold or unconstrained pixel bbox.
5. **Outside/inside crop is wrong:** inspect the board-strip calibration and
   fixed camera mapping. Do not substitute a populated-minus-hidden bbox;
   removing an overhanging model can change KiCad's auto-fit camera.
6. **Body is on the wrong side of the PCB:** return to `P-MODEL-REG`; inspect
   the exact STEP frame, model rotation and Z offset, then rerun the signed-Z
   coupon and its deliberately inverted known-bad. Do not repair this by
   changing camera labels or footprint placement.
7. **Native view passes but JLC twin is shifted:** inspect
   `connector_datum_receipt.json`. If `mating_support_delta_mm` exceeds the
   declared tolerance, this is a representation-substitution failure, not a
   board-placement correction. Do not move the footprint to make a wrong twin
   picture look flush.

Preserve the failed receipt and focused images as diagnostics. A corrected run
must produce a new subject and new explicit human decision.
