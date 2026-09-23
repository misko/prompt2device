# Crow connector FULL evidence audit (read-only)

**Subject inspected:** `projects/crow-usb-carrier-v1` at repository HEAD
`8fb310f4878d7ab00bbe5749407285f47d4a5327`.

## Verdict

`06_build/verification/connector_assembly_contract.json` is
`INCOMPLETE`: 19 physical unknowns, four assemblies, 11 operated refs, and two
simultaneous-service groups.  `connector_assembly_source_gate.json` is `PASS`,
but only admits those exact 19 deferrals at source stage.  It is not FULL.

ADR 0011 preserves the predicate: base `PASS`, zero unknowns, all 19 targets,
on the exact board or separately governed coupon before P3, any route
preparation/import/routing, P5 promotion, release, or order.  Isolated P2 work
may proceed under its stated conditions; it neither closes nor weakens FULL.
P2 changes to connector-neighbor/service geometry reopen affected coupon/article
evidence.

## Exact target closure matrix

All observations below need the hash-bound candidate (or governed coupon with
the candidate footprint, thickness, outline/edge registration and mounting
process), selected connector lots, exact mates/cables, sample IDs, operator,
date, calibration/measurement identity, and raw records.  The group columns
mean every listed ref is operated with that group populated.

| Assembly / refs / groups | Exact open targets | Actual measurement/artifact that closes each | Digital preparation possible now |
|---|---|---|---|
| `spoke_rj45`: J1–J8; `normal_service`, `bench_service` | `interface` | For **each J1–J8**, measured realized orientation and mating plane versus the saved board/outline, with exact Telegartner `100009141` fully mated in intended enclosure state; dated photos/video showing full engagement, no collision/cross-mating/latch damage/loss of seating. | Freeze the candidate/hash and exact J1–J8/ref-to-lot/mate manifest; make the per-ref datum/photo log. Public Wurth drawing/STEP, Telegartner drawing, envelope and planned axis are already retained. |
| | `reaction` | Per required insertion, latch-release/withdrawal and cable-strain case: video/photos of restrained-board operation plus before/after seating, rotation, flex and solder-joint inspection. The Wurth shell/pins → PCB → adjacent board restraints must carry reaction; no damage, permanent movement or neighbor loading. | Prepare a load-case checklist, restraint diagram and before/after inspection sheet. |
| | `spoke_rj45_service` | Per-ref, per-group operation record from unmated target to mated target, with the declared neighbors connected: grip and latch access, interference, neighbor disturbance and result. | Populate a 8-ref × 2-group service matrix and a defined start/end-state checklist. |
| | `spoke_rj45_registration` | Raw, calibrated per-sample mating-plane-to-realized-board-edge measurements plus applicable PCB/seating/enclosure/print/tool-process contributors; derive a conservative exposure/setback allowance only from observed/cited stack. | Define datums, units, raw-data columns and candidate drawing overlay; do not enter estimates as observations. |
| `usb_device`: J_USB; `normal_service`, `bench_service` | `interface` | Measured realized orientation, mating plane/exposure/setback/service clearance; exact GCT `USB4215-03-A` and ASSMANN `A-USB31C-20A-100` fully engage with required neighbors populated, documented by photos/video and no collision/loss of seating. | Freeze ref/lot/cable identity and prepared datum/enclosure/photo record. Compare planned -Y service direction with the saved board; this is a pre-test check only. |
| | `reaction` | Video/photos and before/after inspection during insertion and withdrawal with PCB restrained at adjacent mounting features; reaction through shell stakes/SMT mounting → PCB, no flex/rotation/joint damage or neighbor loading. | Prepare operation/inspection record and restraint setup diagram. |
| | `usb_device_service` | One service record for each group: overmold grip access, full seating, interference and neighbor disturbance for the stated unmated-to-mated transition. | Pre-fill the 2-row group matrix and acceptance-observation fields. |
| | `cable` | Installed exact cable route record: actual exit, unobstructed straight segment, first controlled bend and radius, strain relief, and clearance to enclosure/neighbors with required neighbors populated. | Make a route-photo/measurement sheet using the retained exact cable drawing; no bend or clearance value is presently proven. |
| | `usb_device_registration` | Calibrated raw per-sample mating-plane-to-board-edge/process-stack measurements and a derived, evidence-based setback allowance. | Prepare the datum sketch and raw tolerance-stack worksheet. |
| `external_power`: J_PWR; `normal_service`, `bench_service` | `interface` | Measured orientation, mating plane/exposure/setback/service clearance and actual latch engagement of Molex `43650-0200` with `43645-0200 + 2x 43030-0038`, exact harness installed, neighbors populated; visual evidence of engagement and no collision/loss of seating. | Freeze header/housing/terminal/harness lot identities and make a latch/access/photo record. |
| | `reaction` | Video/photos and before/after seating/rotation/flex/joint inspection for latch engagement, latch release and withdrawal with adjacent-board restraint. Reaction is header → PCB → restraint, never wire/latch counter-hold. | Prepare restrained-operation, inspection and observation forms. |
| | `external_power_service` | Per-group start/end operation record, including latch access, grip, full seating, interference and neighbor disturbance. | Prepare 2-group service matrix and polarity/continuity record. |
| | `cable` | Installed `226206-1022` route record: exit, straight run, first bend/radius, strain relief, far-end support and clearance. Record A1–B1/A2–B2 continuity/polarity. | Prepare cable-ID/polarity and route-measurement sheets from the retained Molex extraction. |
| | `external_power_registration` | Calibrated raw sample measurements of mating-plane-to-realized-board-edge and all applicable assembly-process contributors, followed by a conservatively derived exposure/setback allowance. | Prepare datums and raw stack worksheet. |
| `debug_jtag`: J_JTAG; `bench_service` | `interface` | Measured realized orientation, polarized engagement, mating plane/exposure and service clearance of exact Samtec `FTSH-105-01-L-DV-K` with `FFSD-05-D-06.00-01-N`, bench group populated; photos/video of complete seating and no interference. | Freeze exact header/cable identity and create a polarized-engagement/datum record. |
| | `reaction` | Video/photos and before/after seating, rotation, flex and SMT-joint inspection for insertion/withdrawal while gripping the keyed socket body and restraining PCB. | Prepare restraint and inspection checklist. |
| | `debug_jtag_service` | Bench-group-populated service record for polarized mating/unmating: grip access, seating, interference and neighbor disturbance. | Pre-fill single-group record. |
| | `cable` | Installed exact cable-end route evidence: choose and record **one signed initial exit axis** (the contract supports +Y or -Y), then measure straight run, first controlled bend/radius, strain relief and populated-neighbor clearance. | Prepare signed-axis field, datum drawing and route-photo sheet. Existing ±Y alternatives are representation only, not an installed-route observation. |
| | `debug_jtag_registration` | Calibrated raw per-sample mating-plane-to-realized-board relationship/process-contributor measurements and evidence-based allowance. | Prepare datum and tolerance-stack worksheet. |

## Real external obligations

The gate needs physical access to an exact candidate/coupon, populated exact
hardware, selected mates and cables, a restraint fixture, an intended enclosure
state where applicable, and calibrated measurement/recording equipment. It
also needs an approved/cited sample-lot definition and numeric force,
deflection, cycle-count and any dimensional acceptance limits before such
numeric claims can be graded. The plan deliberately supplies none of these
limits. Public records/JLC search can support identity and preparation only;
they cannot supply installed observations.

No authenticated JLC account, supplier contact, purchase, order, or private
inventory is a prerequisite to documenting the plan. Hardware acquisition or
coupon/article fabrication is a later authorization, not something this audit
asserts occurred.

## Existing evidence checked; none overlooked as physical closure

Useful, already-present evidence is the exact identity/census/envelope record
in `03_src/rules/connector_assemblies.yaml`, the source-phase PASS receipt,
18 hash-bound public/source evidence files, the exact target-to-procedure map
in `connector_assembly_phases.yaml`, and the detailed physical plan
`01_docs/research/2026-09-22-connector-physical-qualification-plan.md`.
Those materially reduce preparation work but remain source/planning evidence.

No `03_src/connector_qualification_coupon.yaml`, connector-coupon package,
physical response record, FULL receipt, or
`connector_assembly_full_gate.json` exists. The in-tree TMUX4827 BGA coupon is
an escape-geometry diagnostic and covers no connector target. Static native
models/renders, model registration, planned axes, public drawings, source
stock evidence and manual-THT policy likewise do not close service, reaction,
installed routing or tolerance observations.

The immediately preceding P1/P2 audit already identified the same 19-target
set. ADR 0011 supersedes its old sequencing concern prospectively: bounded,
non-promoted P2 can now be prepared/executed under the ADR, but FULL stays
unchanged at the P2/P3/routing/promotion/release/order boundary.
