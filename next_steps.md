# Crow next steps

Updated 2026-09-20. Working plan for carrier v0.1.8 and pod v0.2.7.

## Executive conclusion

**CITED:** Carrier v0.1.8 and pod v0.2.7 authorize five and ten supervised
first articles respectively, conditional on live assembly fulfillment and CAM
checks. The review disposition ledger records no remaining confirmed P0 from
the recent external reviews. Purchase authorization is not evidence of an
order, successful assembly, first power, or production qualification.

**PROPOSED:** Finish one coherent procedure/documentation correction while
preparing the two JLC orders. Close live order checks before payment. Prepare
the bench during fabrication, then qualify one carrier and one pod separately
before connecting the complete eight-pod array. Defer convenience/process work
that does not affect these gates.

## Question and scope

Collect outstanding tasks for ordering, receipt, controlled first power,
eight-channel audio qualification, and eventual roof deployment. This plan
consolidates active release instructions, latest external dispositions and
first-article procedures. Historical routing/placement issues are not reopened
solely because an old ledger still says open. Closure must link the later
exact-subject evidence when those ledgers are reconciled.

This is a proposed work order, not an amendment to released limits or permission
to skip a gate. Broader repository improvements remain in improvements.md;
only work relevant to these boards and the next review cycle is prioritized here.

## Evidence boundary

**CITED:** Baseline reviewed release source commit:
`49e977ce0b54bc8dcd0aeaa753043afd46b457de`; external-review publication commit:
`b8a996c2a61aebf63e02bf476e56d145fbc55568`.

- Carrier PCB SHA-256: `45ff675971600c279c1d1e34e1610a08426b144f8435349037919a2328987e26`.
- Pod PCB SHA-256: `2685281fdb8dac636e16334c2d4eca679300bfa5322a368ac2685b59f48e3dd1`.

**OWED:** Actual JLC resolved BOM, order-time stock/allocation, final placement
preview and CAM approval; physical measurements and signed acceptance results.
Archived public-stock numbers are dated observations, not current reservations.
External-model ORDER verdicts do not discharge those obligations. Visual models
cannot establish hidden joints, manufactured tolerances or physical polarity
from a render alone.

## Findings

All rows below are **OWED** unless explicitly described as **PROPOSED**.
Owners are roles for execution; no outside party has been contacted by this plan.

| ID | Task | Owner | Deadline / dependency | Evidence needed to close |
|---|---|---|---|---|
| P01 | Reconcile carrier power budget and first-power procedure | Engineering | Before any carrier energization | Itemized rail/input budgets with assumptions; separate startup versus steady limits and measurement points; reviewed source-foldback/inrush procedure; reconcile 120 mA abort and 200 mA supply setting without simply raising limits |
| P02 | Complete voltage-corner and audio acceptance specifications | Engineering + system owner | Before affected tests | Reviewed carrier card for 13.2 V, consistent probe ranges; numeric noise, THD+N, phase/gain matching, CMRR and crosstalk limits tied to system requirements; no invented pass thresholds |
| P03 | Reconcile current operator documents and evidence ledgers | Engineering | Alongside P01/P02 | Remove stale bottom-side ESD instructions and blanket no-order wording in mutable source; reconcile old pod candidate names and historical open rows with exact later closure; retain original dated reports verbatim |
| O01 | Prepare two exact JLC upload sets and quotations | Order operator + engineering | Before payment | Manifest-matched carrier v0.1.8 Gerbers/BOM/CPL, Standard PCBA quantity 5; pod v0.2.7 equivalents, Economic PCBA quantity 10; no mixed-version artifacts |
| O02 | Resolve exact parts and allocation | Order operator / JLC | Before payment | Every resolved BOM row matched; carrier CS5308P-DN package/code explicitly verified; LT3041 and TMUX2821 allocation or accepted exact-part consignment; no SMD DNP/substitution; refresh dated public observations if used for a new sourcing claim |
| O03 | Inspect actual assembly previews | Engineering + order operator | Before payment | Carrier 306 top-side placements, pod 31 top-side placements; carrier 26 flagged references plus Q_IN and other polarized devices; pod U1/U2 and D1/D2/U3; saved previews and explicit orientation outcomes |
| O04 | Confirm fabrication process and production files | Order operator / JLC CAM | Before payment | Carrier named four-layer stack, copper weights, thickness and finish; exactly 12 filled/capped 0.60/0.30 mm vias and 589 ordinary vias; all component holes untreated; pod ordinary two-layer/tented-via process; unchanged outline/copper/drills |
| O05 | Approve purchase and retain order receipt | User / order operator | After O01–O04 | Quote, selections, resolved BOM, preview, CAM evidence, order number and release hashes; payment is a separate explicit action |
| B01 | Acquire manual parts and integration hardware | Procurement | Before assembly/bench | Carrier 27 THT references per board (16 film capacitors, J1–J11); pod exact J1 and AOM-5024L-HD-R capsule; selected 15 m Weidmüller 8909650150 cords; MCHStreamer, two exact TCSD cables, authorized TDM8 image, Pi and isolated power source; record identities |
| B02 | Prepare fixtures, instruments and result templates | Bench owner + engineering | During fabrication | DMM, scope/probes, logic capture, audio/calibration fixtures, electronic loads and thermal measurement; calibrated IDs, grounding plan, serial/BOM records, structured first-article record and durable raw-data manifest |
| H01 | Inspect delivered PCBAs and finish THT assembly | Assembly / bench owner | Before first power | Literal population reconciliation, polarity/continuity/resistance checks, exposed-pad inspection method/results, photographed THT and capsule joints; no missing SMD hand-placement workaround |
| H02 | Bring up one carrier and one pod independently | Bench owner | After P01/P02/B02/H01 | First-article checker acceptance using reviewed limits; carrier rail/reset waveforms, startup/shutdown/brownout/restart; pod rails/bias/no-load current and approved protection tests |
| H03 | Establish digital and partial-power correctness | Bench owner + host integration | After controlled first power | MCLK/BCLK/FSYNC and TDM format/slot identity; all MCH/carrier independent-power states and back-power behavior; continuous 120 s eight-channel capture without framing discontinuity |
| H04 | Qualify analog and cable operation | Bench owner + system owner | After H02/H03 | 18/11 pod gain, acoustic polarity, 1.2 Vrms envelope, noise/THD/headroom/common mode, all-eight-channel impulse mapping, phase/crosstalk/CMRR and 15 m cable stability against P02 limits |
| H05 | Qualify loading, protection, copper and thermal behavior | Bench owner | Approved fixtures after H02 | Eight-spoke load/delivery, physical DCR/via temperature rise, one-fault/seven-healthy behavior, reverse recovery, hold/dump/interlock transients, hot/cold threshold drift and repeated startup; follow controlled procedures |
| H06 | Close fit and shield-bond evidence | Mechanical / bench owner | Before enclosure/deployment acceptance | Exact cord power/shield continuity, hot loop ≤2.2 Ω and delivery floor, individual parallel conductors, carrier CHASSIS bond and isolated pod shield, latch/boot/cable-bend fit with neighbors populated, measured manufactured tolerances |
| Q01 | Record sample coverage and decide the next hardware revision | Engineering + system owner | After bench work | Per-serial PASS/FAIL/BLOCKED matrix; retain all failures; propagate justified corrections to source and repeat affected gates; only fully covered articles may claim FIRST_ARTICLE_TESTED |
| Q02 | Qualify roof installation and production separately | Mechanical / system owner | Before outdoor deployment or production | Enclosure/acoustic port/windscreen/strain relief, condensation/drainage, UV/weather evidence, ESD/EMC and installation protection scope, thermal/environmental cycling; production acceptance criteria and manufacturing repeatability |
| D01 | Improve review reliability and reduce spend | Process owner | PROPOSED next process pass | Primary datasheet mode/trigger tables included in compact packets; explicit metric endpoints; preserve and hash exact submitted requests; reject length/error-only responses as reviews; bound retries and report all billed cost; no automatic conversion of conditional verdicts into acceptance |
| D02 | Keep convenience debt out of the order critical path | Process owner | PROPOSED next revision | Clear scoped-PASS wording, current deficiency index, improved locator/silkscreen convenience and evidence links; retain mandatory checks |

**CITED:** P01 combines CRW-ADV-002, CLAUDE-ADV-004 and historical TOP77-Q5;
these are one work item, not three independent failures. Refuted reset,
CONFIG-pin, capacitor-distance and pod-buffer allegations do not create PCB
revision tasks. Existing physical startup/audio obligations remain despite
those refutations.

## Recommendations

**PROPOSED — Stage 1: make the operator package coherent.** Execute P01–P03
as one bounded correction. Publish the reviewed procedure bound to the exact
hardware subjects. If the corrected plan is shipped inside a release, use a
new immutable successor with the applicable source/delta, review, rehearsal,
seal and publication gates. Do not modify existing archives or classify an
executable test-rule change as documentation-only without checking eligibility.
A plan document alone does not authorize new current or voltage limits.

**PROPOSED — Stage 2: close the purchasing evidence.** Run O01–O04 alongside
Stage 1. O05 follows only after actual vendor evidence is accepted. If a new
successor is selected for purchase, use its complete upload set and verify
whether manufacturing bytes stayed identical; never mix versions.

**PROPOSED — Stage 3: use fabrication time for bench readiness.** Complete
B01/B02 and P02 so arrival is followed by H01/H02 immediately. Start with one
carrier and one pod; expand to eight pods only after the independent bring-up
passes. Keep untouched spares for comparison and record the qualification
sample denominator explicitly.

**PROPOSED — Stage 4: qualify the system in increasing scope.** Complete
H03–H06, then Q01. Q02 is a separate deployment/production milestone. D01/D02
can be worked after the order without delaying fabrication unless a concrete
review-evidence defect affects an order decision.

**INFERRED planning estimates, not delivery promises:** P01–P03 and a focused
review are approximately one engineering day if no design defect emerges.
Upload preparation and preview inspection take roughly half a day of operator
work; JLC sourcing/CAM response time is external and has no verified ETA here.
Bench preparation is roughly one day if equipment and parts are on hand.
Initial independent power-up and digital bring-up may take one to two bench
days after arrival. Full cable/audio/fault/environmental qualification requires
a separate schedule based on facilities, failures and sample coverage.

## Validation plan

**PROPOSED:** Each row closes with its named artifact or physical record, not
with an unchecked narrative assertion. Audit corrected source/card consistency
and applicable gates before adopting P01/P02. Match resolved BOMs and preview
counts to exact release identities. Inspect CAM drill-family handling before
payment. Retain raw per-serial measurements and hash manifests for hardware
results; the existing first-article checkers must accept complete records.

**OWED:** Reconcile recent review conclusions with their actual evidence
scope. Source-generated geometry checks must be distinguished from direct
measurements of the sealed PCB; render review must not be credited as hidden
joint or live uploader approval. Any newly confirmed defect reopens the
owning source and affected gates, regardless of a model's verdict.

## Source register

- [Carrier order authority](projects/crow-audio-carrier-v1/07_releases/v0.1.8-2026-09-16/ORDER_README.md).
- [Carrier released deficiencies](projects/crow-audio-carrier-v1/07_releases/v0.1.8-2026-09-16/verification/deficiencies.md).
- [Pod order authority](projects/crow-mic-pod-v3/07_releases/v0.2.7-2026-09-16/ORDER_README.md).
- [Pod released deficiencies](projects/crow-mic-pod-v3/07_releases/v0.2.7-2026-09-16/verification/deficiencies.md).
- [Carrier active first-article plan](projects/crow-audio-carrier-v1/01_docs/FIRST_ARTICLE_TEST_PLAN.md).
- [Pod active first-article plan](projects/crow-mic-pod-v3/01_docs/FIRST_ARTICLE_TEST_PLAN.md).
- [System review dispositions](projects/crow-roof-array-v1/08_reviews/DISPOSITIONS.md).
- [Carrier historical dispositions](projects/crow-audio-carrier-v1/08_reviews/DISPOSITIONS.md).
- [Pod historical dispositions](projects/crow-mic-pod-v3/08_reviews/DISPOSITIONS.md).
- [Repository process backlog](improvements.md).


## Process improvements — current decision

Use the existing project driver and owning gates. Framework expansion is paused;
process work is not a prerequisite for ordering or ordinary board corrections.

**Explicitly authorized testing consumer (2026-09-20, implemented and validated):**
the checkpoint regression framework in `tests/checkpoints/` restores a bounded
board case with current skill context and independently grades a successful
repair. It reuses the existing runtime and stage graph. This does not reopen
production driver migration, automatic evidence reuse or unrelated bundle work.
Validation includes 16 deterministic framework tests and five case-control tests;
each of the three case families has initial-fail/valid-repair/invalid-shortcut
controls. Fresh Luna medium agents solved all three cases and independent grading
passed. The record in `tests/checkpoints/evidence/2026-09-20-validation.json`
distinguishes reference controls from agent solving and reduced fixtures from full
board replay. The nested CLI sandbox is unavailable on this host; the adapter now
detects that before spending tokens. External supervised runs remain supported,
with unmeasured usage explicitly unknown. Publication follows the normal reviewed
Git boundary; this framework is not a prerequisite for ordering Crow boards.

| Area | Current state | Next action |
|---|---|---|
| Geometry regressions | Retained: adjacent escapes, native rule scope, atomic via/stub rejection | Use applicable existing checks when a real geometry change needs them |
| Issue accounting | Available, opt-in: command ledger and offline provider imports | Use when attribution helps a concrete investigation; unknown usage stays unknown |
| Dependency graph | Diagnostic only; no automatic reuse permission | Consult when useful, then follow the actual driver and mandatory gates |
| Integration pilots | Completed, retained as regression coverage | No additional pilot solely to advance framework adoption |
| New bundle consumer, driver migration and automatic reuse | Deferred; no consumer code was implemented | Reopen only for a named production consumer and demonstrated missing capability |
| Live capture, descendant discovery and detailed time tracking | Deferred | Reopen if manual accounting demonstrably impedes real work |
| Review/deficiency workflow | Existing review gates and deficiency lists retained | Defer convenience debt; keep functional and manufacturing blockers explicit |
| Documentation/publication | Current roadmap here; history in Git and improvements.md | Publish the reviewed changes separately; no push performed in this pass |

**Next real work:** finish P03 operator-document reconciliation, then P01/P02
power-up and acceptance specifications. The first bounded P03 correction replaces
stale bottom-side ESD inspection wording in both mutable first-article plans:
carrier v0.1.8 and pod v0.2.7 order instructions require top-side SMD assembly.
This does not amend sealed releases or close the rest of P03.

For each real task, record the issue, changed source, owning check and outcome.
Use existing timing/usage tools only where useful; do not reconstruct missing
measurements. Compare repeated commands and retries before claiming savings.
Add infrastructure only when a named consumer and concrete failure demonstrate
a gap in the existing tools. One integration writer; inexpensive, bounded
subagents only for independent work that saves effort.
