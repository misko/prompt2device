---
schema: 1
kind: pcb-human-report
report_id: 2026-09-12-process-convergence-plan
title: Diagnose once, repair coherently, integrate once
subtitle: A focused PCB skill update to avoid serial validation loops
project: crow-audio-carrier-v1
date: 2026-09-12
status: DRAFT
evidence_status: INCOMPLETE
---

## Executive conclusion

**PROPOSED:** Extend the existing workflow in three small changes:

**Complete diagnosis → verified geometry evidence → one stable repair batch.**

The intended saving is fewer incomplete diagnoses, speculative checker changes and repeated downstream rebuild/review rounds. Keep the existing runtime, findings ledger and engineering gates. The earlier execution/qualification/ownership improvements are already implemented; this plan addresses the remaining diagnostic and integration gaps.

The short procedural guidance is already committed as **590a6e18**. The tooling and rollout below are proposals, not implemented capabilities or release acceptance. No speedup percentage is established.

## Question and scope

The user asked: “Can you please propose an elegant plan to update the process / skill to fix this for next time?”

Scope is the reusable PCB skill's behavior when native geometry and verification disagree. Apply the lessons to the current carrier/pod evidence as a canary, while retaining their separate board-release goal. This is not a new universal CAD parser, general autorouter, workflow framework or replacement gate battery.

## Evidence boundary

**MEASURED:** Independent model review completed and root closed delivery at 2026-09-13 00:14:53 UTC. It selects the unchanged first underside-registration candidate conditionally: exact eight-fuse native geometry is correct, actual-model inversion fails, and a separately reproduced synthetic visibility limitation also exists in the original checker. Documentation, an executable blind-spot fixture and normal integration remain owed. The rejected second method remains rejected; two method variants remain recorded.

**MEASURED:** Independent pod review completed and root closed delivery at 00:15:00 UTC. The local VIN/ground patch is SOUND, but complete seed acceptance remains FAIL. The complete census covers 12 seeded nets, 76 pads, 89 tracks and eight vias. It finds 20 additional same-net contacts confined to two nets, with one actual drill/land overlap. It also distinguishes two conservative bounding-box false positives and six deliberately unfinished downstream declarations.

**OWED:** Tool changes, their maintained regressions, independent forward evaluation and measured execution savings. Neither review accepts final routing or a release.

## Findings

| Observed problem | Evidence and implication |
|---|---|
| **MEASURED:** First-refusal reporting concealed later causes. | The complete pod review separates 20 contact pairs into a finite two-net problem. Another repair aimed only at U2.1/U2.2 would leave other contacts unresolved. |
| **MEASURED:** The synthetic model differed from its intended geometry. | Native export shows the nested-transform test body partly outside the declared side and partly inside the board. The real direct-coordinate fuse model is wholly outside the nominal stack. A greener pixel method was not the appropriate response. |
| **MEASURED:** A centre-point guard answers a narrower question than physical overlap. | The pod via centre clears U1.4 by about 0.100 mm, but its 0.300 mm drill overlaps the land by about 0.050 mm. The existing router guard also intentionally excludes pre-existing source vias. |
| **INFERRED:** Related source changes should settle before expensive renewal. | The current source batch includes route, ground and model-registration changes. Renewing dependent reviews between known pending corrections would produce signatures on soon-stale inputs. |

## Recommendations

### 1. Make one diagnostic run expose the complete repair scope

**PROPOSED owner:** Existing `critical_path_check.py`, its tests and the existing D-BACK procedure.

Add a bounded read-only diagnostic path that reports every declared critical path and all contact causes on the affected nets. Reuse the existing source readers and graph predicates; do not maintain a second weaker grading algorithm. Cache each net's diagnosis so multiple declarations do not repeatedly parse the same copper. An unsupported or malformed source must remain explicitly ungraded rather than yielding an apparently complete partial census.

Report exact net/ref/pad/object identities, coverage denominators and these distinct dispositions: demonstrated physical defect, unsupported representation, conservative screen, and downstream work not yet built. Use an independent native shape check when distinguishing real contact from a conservative screen. Unknown stays unknown. The ordinary acceptance command still fails when its required proof is missing; a diagnostic report never promotes a stage.

**Acceptance:** One run on the frozen pod identifies the complete retained contact set and all 22 declaration outcomes, without editing the board. A fixture containing multiple independent causes must report every cause in one run; removing the first cause must not reveal an omitted class. Missing geometry, malformed inputs and truncated reporting cannot pass. This is the first implementation priority.

### 2. Qualify what geometry tests actually prove

**PROPOSED owners:** Existing model-registration fixtures/native-export helpers and the via/seed geometry checks at their respective ownership boundaries.

For a new or changed CAD counterexample, establish the native-consumed geometry before attributing its verdict to the checker. Retain actual transforms, units, mounting face and body extent from an independent native export, with an asymmetric positive and deliberately wrong control. Compare the old checker, proposed checker and exact product model when deciding whether a result is a regression, an existing limitation or an invalid fixture. Reuse qualified fixtures; do not re-export every unchanged part on every repair.

For ordinary vias, distinguish centre membership, annulus contact and drill/land overlap. Add the centre-outside/drill-overlapping hostile case to the relevant maintained tests. Check ordinary source seed vias at source/prep admission as well as newly routed vias at the existing wave boundary; preserve explicitly reviewed filled/capped fields and their process authority. A router-delta guard must not silently claim coverage of source vias it intentionally excludes.

Pin a supported existing checker blind spot through the current G-VACUOUS docstring/test mechanism, without converting an existing required-fail control into a pass. Bind independent exact-product evidence when the missing property matters. A general finite-width routing graph or universal model-volume checker is outside this change unless a bounded canary demonstrates it is necessary.

**Acceptance:** The native fixture check detects the intended-versus-realized transform discrepancy; the real fuse inversion remains rejected. An ordinary via with its centre outside a land but drill overlapping is detected at its owning boundary, while a genuinely clear via passes. Intentionally governed source vias retain their explicit treatment. New bug regressions go RED against the prior implementation and GREEN after correction.

### 3. Integrate a stable repair batch through the existing workflow

**PROPOSED owners:** Existing lifecycle/execution references, checkpoint dependency inventory and project conductors.

Before a repair, freeze the complete affected finding set and choose one coherent source or representation hypothesis. Give one implementation owner the already-declared bounds. Prefer correcting the two complete pod source trees over commissioning a general graph adapter unless the bounded result shows source normalization is impractical. The experiment must distinguish those alternatives; a new agent name cannot reset exhausted work.

Before renewal, use existing dependency inventories to identify which source changes invalidate which checkpoints and reviews. Complete known related changes, then run one normal regeneration and the required current reviews on the stable result. This does not merge away mandatory schematic, placement, orientation or routing handoffs. A genuinely new source defect still invalidates downstream acceptance.

Use the existing TaskEnvelope/TaskAttempt output and closure path. Do not introduce another budget ledger or approval layer. Record useful progress as closed causes, accepted source and completed stage boundaries, separately from elapsed time, test counts and document counts.

**Acceptance:** A canary with two known related source changes receives one stable renewal rather than a review between those changes. All mandatory review boundaries still execute; old subject signatures cannot pass. A new material source change invalidates the right evidence. An exhausted campaign cannot resume by renaming it.

## Validation plan

**PROPOSED rollout:** Three reviewable changes in the order above. Land each with its owning tests, contracts and relevant template updates; do not widen a schema or gate silently. Keep diagnostic reporting non-authoritative. Promote any changed geometry predicate only after targeted regressions and the owning canary support it.

1. Use small independent synthetic fixtures to establish behavior. Preserve the current raw failure archives as forensic evidence, not golden board-byte expectations.
2. Replay the frozen pod and carrier in isolated scratch through the existing bounded runtime. Reuse one producer output for comparisons where possible.
3. Give one fresh evaluator the updated skill and a realistic frozen failure packet, without the expected diagnosis. It should find the full cause set, distinguish fixture validity from checker correctness, and choose the correct repair owner before editing.
4. Run relevant critical-path/model/via suites and the existing skill-authority, documentation and contract checks. Retain their real denominators and any declared blind spots.
5. Compare time to a complete diagnosis, missed causes found after the first repair, full regeneration/review rounds and owner transfers using TaskAttempt records. Require complete diagnosis with no lost defects or false acceptance; claim a time saving only if measured total effort improves.

**Stop condition:** If the canary still requires repeated source contortions merely to satisfy an endpoint model, stop that repair strategy and reassess the representation owner. If the update increases review churn or requires a parallel framework, reduce its scope. Existing safety, independence, timeout and release gates remain in force.

## Source register

- [Implemented execution, qualification and ownership changes](2026-09-10-workflow-improvements-implemented.md).
- [Current procedural lessons and limitations](../learnings/placement.md).
- [Guidance source and validation evidence](../journal/9d055c22f92ae5d6903ed51258e47d23ca7a8ad1609ef9e55d1b66323de31c12.tar.gz).
- [Independent native model-visibility reassessment](../journal/e9e8420334a455c9aaca081f8866a33ee19b96273c4d936bc709cdf0f1a0786e.tar.gz).
- [Independent complete pod contact census and source reassessment](../../../crow-mic-pod-v3/01_docs/journal/983cb94f44cdddfb496e7ecaeb3cb73d59acd2265b46e7784deedc310768d448.tar.gz).
- [Critical-path checker](../../../../skills/kicad-pcb/scripts/critical_path_check.py) and [maintained tests](../../../../tests/t1_critical_path_check.py).
- [Native registration checker](../../../../skills/jlcpcb-fab/scripts/native_model_registration.py) and [maintained model tests](../../../../tests/t1_model_registration.py).
- [Router-created via guard and its declared scope](../../../../skills/kicad-pcb/scripts/via_in_pad_guard.py).
- [Lifecycle and backtracking](../../../../skills/pcb-design/references/lifecycle-and-backtrack.md), [bounded execution](../../../../skills/pcb-design/references/execution-runtime.md), and [routing procedure](../../../../skills/kicad-pcb/references/routing-pipeline.md).
