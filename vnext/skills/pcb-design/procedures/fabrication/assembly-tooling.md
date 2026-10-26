# Source-bound assembly verification

Local pilot for flat non-RF staged boards. Read the assembly stage contract.
This checks a proposed assembled design, not performed physical assembly or
vendor orientation preview. Keep the staged package immutable; package-local
diagnostics must disable bytecode or run in a disposable copy and leave the full
file census unchanged. Unsupported geometry needs an explicit model extension,
not a fictitious clear render.

## Inputs and scope

New admission adopts `01_docs/assembly-contract.json`: version2, authority path
and SHA256, fabrication_receipt_sha256, and `mechanical` as described below.
Version1 remains an envelope component/historical-check route, not new admission.
Run upgraded commands in the mechanical runtime (the owner replays a frozen
producer with that runtime; missing dependencies fail, never skip checks):

```
/usr/bin/python3 -B tools/assembly_verify.py build --project ABS --manifest REL --output NEW_REL
/usr/bin/python3 -B tools/assembly_verify.py verify --project ABS --manifest REL --output REL
/usr/bin/python3 -B tools/assembly_verify.py issue --project ABS --review REL
/usr/bin/python3 -B tools/assembly_verify.py check --project ABS
```

Version1 manifest: `version`, `package` (accepted fabrication output), `models`,
`boards`, `instructions`, `handoff`. Evidence paths are project-relative retained
files. Model keys are arbitrary stable identifiers. Every model states exact
`manufacturer`, `mpn`, `footprint`, nonempty `evidence`, `basis` (what actual
maker dimensions support the model and any substitution/limitation), `polarity`
(explicit numbered-pad/mark/view convention, or explained nonpolar), `bodies`
and `contacts`. Models are dimensioned envelopes, not photorealistic proof.

Bodies use native footprint-local coordinates, mm, +X right/+Y down, at native
angle zero. A body is `{shape:"box", bounds:[left,top,right,bottom], z:[min,max]}`
or `{shape:"circle", center:[x,y], radius:R, z:[min,max]}`. Height z is from PCB
top surface; multiple volumes may represent an overhanging connector or module.
Use actual/toleranced maker bounds and explain conservative substitutions.
Contacts map each nonempty native pad number to
`{xy:[x,y], tolerance_mm:T}`. These are independently derived nominal lead/land
centers and justified registration allowance, not a copy of observed pad centers
passed off as maker facts. Every numbered native pad must correspond; duplicate
same-number pads must satisfy the declared contact envelope too. Contact fit,
hole/land size and solderability still need independent drawing review; center
agreement is not sufficient evidence for those judgments.

Each board has `source_sha256`, `references` (each populated electrical reference
to exactly one model key), and `access`. Access rows are
`{id,ref,bounds:[left,top,right,bottom],z:[min,max],evidence:[...]}` in native BOARD
coordinates. Declare applicable connector/mating/inspection volumes from retained
geometry; empty access needs an independent applicability disposition. Actual
plug/enclosure dimensions cannot be assumed from an unselected accessory.
All models must be used; DNP/mechanical parts remain visible in staged policy,
never silently counted as mounted bodies. No body substitution alters copper.

The pilot supports top-side bodies and cardinal footprint angles. A single closed
native line/arc outer contour, including edge recesses, is retained as a tessellated
2D overview; internal Edge.Cuts cutouts and multiple islands remain unsupported.
The envelope overhang list checks outer bounds only, not support above a recess.
Registered STEP checks and independent judgment own actual board/recess clearance.
It checks exact staged population/identity, contact registration, body
overlap in XY/Z and explicit access volumes, and emits common-datum bare/populated
SVGs plus a full per-reference geometry report. Both views retain every native
pad bound and drilled hole, including DNP, mechanical and unnumbered pads;
only actually populated references get bodies. Bodies are labeled as envelopes. Out-of-outline bodies
are reported for independent overhang/access judgment rather than automatically
accepted or clipped. These views do not certify an enclosure or physical hardware.

## Acceptance

Build/verify rerun the owning fabrication check and compare current adopted
receipt. Output is new/atomic. Verify recomputes all derivative bytes and full
membership, rejects symlinks, and binds the exact tool, stage and manual.
Evidence validity is an engineering judgment, not established by file existence.

Independent review uses exactly one JSON block: schema1, stage
`JLC-ASSEMBLY-VERIFY`, distinct author/reviewer, manifest/output, verdict PASS,
all verify `subjects`, and six `checks`: `population`, `geometry`, `polarity`,
`access`, `instructions`, `handoff`. Each has PASS, substantive rationale and
nonempty retained `evidence`. Review all model maker sources and generated views,
body/contact/land fit, substitutions, exclusions, datum/side/rotation and polarity.
The physical test/stock/vendor preview/process/order holds remain explicit.
Missing design evidence or a contradictory collision is not an order-day hold.
Root alone issues `assembly_verified`; receipt check repeats owning predicates.
Stop for assembly reflection before release review. Failures return to the model
owner first; actual placement/circuit defects backtrack to their upstream owner.

## Registered3D version2 admission

Contract `mechanical` has exactly `scene_manifest`, `scene_output`, `toolchain`,
`toolchain_files` (project-relative producer directory and exact file/hash inventory).
Use the [source-bound scene](../mechanical/3d-verification.md) with the same assembly
manifest and exact accepted fabrication package. Preserve the actual trusted
producer; hashes are not authorization to execute untrusted code. A fresh scene
may use a retained compatible producer without rewriting historical evidence.

The owner still produces/rechecks the envelope report, but also emits
`mechanical.json`: exact registered-scene coverage, exhaustive limitations,
artifact/input/producer hashes and actual frozen replay result. Replay reopens
solids and compares images. Require each populated reference, successful contacts,
body/board/access checks, per-reference STEP roundtrip, all six views and same-camera
bare views. Scene evidence remains INCOMPLETE/accepted:false; independent admission
is a different claim, not a modification of generated diagnostic status.

Keep the six ordinary review criteria. Add `mechanical` with exactly:

- `models`: every used model key maps `{verdict:"PASS",rationale,evidence:[...]}`.
  Judge exact maker/revision, supported body/lead occupancy and heights/tolerances,
  independent contact/land mapping, polarity and omissions. Cite all model sources
  and any retained STEP plus its independent registration sources. Model families
  may share reasoning, but do not omit exact identities.
- `boards`: every board key maps the same judgment shape. Judge all instances,
  poses/side/polarity, board-top/underside/contact datums, finite tolerances and
  applicable access/mating/inspection scope. Cite its actual complete STEP/view
  artifacts and scene report, not just a summary or attractive render.
- `limitations`: every ID in mechanical.json maps `{classification,rationale,
  evidence:[...]}`. Classify `design_resolved` or `physical_qualification` only.
  Earlier `outside_mating_scope` dispositions cannot excuse assembly review.
  Unknown design dimensions and contradictions cannot become physical test holds.

All new evidence joins exact review subjects. These judgments are independent
engineering work; schema completeness does not establish their truth. An omitted
body or failed nominal scene blocks before review. Firmware, actual inspection,
vendor preview, process/allocation and deployment remain distinct, visible holds.
