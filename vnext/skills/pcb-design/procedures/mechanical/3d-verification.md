# Registered 3D mechanical evidence

Use for mating and populated-assembly acceptance. Share one source-bound scene
between clearance checks, STEP export and rendered evidence; do not maintain an
independent cosmetic model that can disagree with the checked assembly.

## Geometry and registration

Retain model files and maker/revision evidence locally. Each mounted reference
maps to an exact model and population mode. Record whether it is manufacturer
CAD, a drawing-derived solid or a conservative envelope, its supported dimensions,
tolerances and omissions. A generic model or assumed height is provisional until
reviewed against the actual variant. Never render a missing body as absent from
the BOM. A conservative envelope can prove clearance, but cannot prove engagement
or cavity fit that it does not represent.

Use millimeters and an explicit right-handed board frame, with PCB top at Z=0.
Retain full board thickness, relevant holes/cutouts, underside protrusions and
mounted heights. Model-to-board registration uses independent numbered-contact,
hole and/or body landmarks sufficient to constrain the rigid transform. Reject
reflection, scaling, unsupported side conventions and degenerate registration.
Document any intended penetration/contact using named physical features, not a
blanket exemption for two entire components. Model libraries must be local in a
standalone release; ambient KiCad library paths cannot prove complete coverage.

Evaluate real solids for intersections and minimum separation. Use bounding boxes
only to accelerate checks, never as the final proof for curved/hollow geometry.
Assess applicable tolerance extremes, mating engagement and insertion/removal or
tool-access sweeps. Missing accessory geometry leaves that fit claim unresolved;
record exact scope instead of declaring all mechanical checks not applicable.
Known collision or inadequate seating returns to placement/mating through the
existing recovery loop; do not move verified copper to fit a bad derivative model.

For standard mating interfaces, distinguish source-supported compatibility from
external board/neighbor clearance. Independent review may use exact compatible
connector identities and conservative geometric bounds without reconstructing
private spring/contact/stop coordinates. Name the intended engagement features,
bind accessory/substitution limits, and test exterior sweeps on current solids;
a filled housing envelope cannot prove or refute fit inside an omitted cavity.
Missing material dimensions, incompatible variants and known collisions still
block acceptance. Physical contact/retention tests do not waive design gaps.

Apply the same distinction to standard board-mount interfaces: an exact maker
recommended hole/land pattern may establish mounting compatibility without
reconstructing private contact or compliant-peg geometry. Review deviations
explicitly; a larger hole may preserve insertion but change solder/retention.
Do not confuse nominal model registration tolerance with finished-hole fit.
For an omitted dimension, name each claim it could affect. It may be immaterial
to a demonstrated independent clearance bound, but not to an asserted enclosure
fit. Label illustrative geometry as such; it cannot supply a missing maximum.
An explicit external keepout/scope limit must be carried into assembly and release,
not used as a blanket board-collision exemption or a hidden deployment restriction.

## Outputs and review

Produce the populated board STEP and reopen it in the solid kernel: compare
nonzero solids, geometry, units, bounds, placement and population to the checked
scene. Require six labeled 3D views (top, bottom, two isometrics, two edge profiles)
and bare top/bottom views sharing the respective populated camera, projection,
crop and dimensions. Include critical mating closeups/sections when whole-board
views cannot show engagement, underside clearance or registration. Generate model
coverage, registration, collision/clearance and substitution/limitation reports;
hash-bind source, models, transforms, checks, commands and all exported artifacts.

Independent review checks the geometry against manufacturer facts and inspects
the actual outputs. Kernel success and attractive images are not fit acceptance.
Keep assembly design verification, vendor placement preview and physical
qualification distinct. Changed models/transforms/population invalidate affected
mechanical reviews and dependent release evidence, even without copper changes.

## Implementation status

`tools/mechanical_kernel.py` supplies tested solid operations, rigid registration,
STEP round-trip comparison and common-camera rendering. It is a component of the
upgraded adapter, not a stage acceptance command. Historical v1 receipts retain
their archived meaning. [Mating admission](mating-admission.md) now binds frozen
scene replay and independent feature/limitation judgments through the existing
owner. The version2 [assembly adapter](../fabrication/assembly-tooling.md) binds
its exact accepted package, complete model/board judgments and all limitations;
it does not inherit mating-only exclusions as assembly acceptance.

## Source-bound scene component

`tools/mechanical_scene.py` bridges the existing assembly manifest/population to
real solids. Run with the isolated runtime satisfying
`tools/mechanical-requirements.txt` and the project's KiCad Python/CLI runtime:

```
.venv-mechanical/bin/python -B tools/mechanical_scene.py build --project ABS --manifest REL --output NEW_ABS
.venv-mechanical/bin/python -B tools/mechanical_scene.py verify --project ABS --manifest REL --output ABS
```

The scene manifest has `version: 1`, `assembly_manifest`, `step_models` and
`unresolved` (explicit remaining claims). It reuses the assembly model keys,
exact staged native boards, every population disposition and maker evidence.
It does not create a second population list or call a historical receipt current.
Without an override a model is the existing drawing envelope, expressly not
proof of lead shape, engagement or hidden cavities.

For drawing envelopes distinguish molded-body dimensions from full occupied
package/termination dimensions. Check the maker's applicable maxima and axis
conventions; a body-only box is not a conservative envelope for protruding leads.
Either include those features conservatively or explicitly review their omitted
occupancy using source-supported geometry. Do not move valid copper to compensate
for a misread package drawing.

Each `step_models` override declares retained `path`, `evidence`, `limitations`,
`translation`, `rotation`, `local_landmarks`, `landmark_features`,
`expected_landmarks` and `tolerance_mm`. Use at least four noncoplanar witnesses.
Expected points are independently derived in the right-handed footprint frame
(native local X, negative local Y, Z above nominal board top). The transform is
extrinsic X/Y/Z rotation then translation; native footprint pose is applied once
afterward. A feature is `{kind: "surface"}` or
`{kind: "circle_center", radius_mm: R}`. Witnesses must match actual STEP faces
or circular-edge centers at 0.00001 mm CAD tolerance, separate from engineering
registration tolerance. Retaining the STEP itself is not independent evidence.
Feature correspondence still needs independent manufacturer/variant review;
geometric agreement does not prove that an omitted physical feature is harmless.

The raw `native-dielectric.step` is distinguished from `board.step`: the latter
extrudes the native top outline/holes to the declared nominal finished thickness,
with top Z=0. This is a nominal board envelope, not a measured laminate or detailed
copper/mask/finish surface. The populated STEP, checks and views share that scene.
Every body pair is counted; disjoint bounding boxes supply only a separation
lower bound, while touching/overlapping boxes enter the solid kernel. Access
volumes check their own component too; there are no whole-reference collision
waivers. Tolerance extremes and feature-specific intentional contacts must be
resolved before owning acceptance.

Build writes only a new output directory. Verify reconstructs from exact inputs,
checks complete artifact membership, reopened per-reference STEP geometry and
rendered pixels. Native export runs on disposable copies because KiCad may write
editor preferences beside its input. Detail views for retained STEP components
explicitly isolate the board and selected reference so foreground neighbors do
not conceal the interface; their visible-reference list and hidden-neighbor
label distinguish them from the complete-scene views and clearance checks.
Both report `accepted: false`; a clean nominal run remains
`INCOMPLETE`, never stage PASS. The component alone supplies neither owning-stage
admission, full mating sweeps nor engineering acceptance. Preserve failed outputs
and use the existing backtrack owner to resolve their causes.
