---
schema: 1
kind: pcb-human-report
report_id: 2026-09-25-process-consolidation-review
title: Crow process consolidation review
subtitle: Preserve the design and simplify the path from experiment to integrated board
project: crow-usb-carrier-v1
date: 2026-09-25
status: DRAFT
evidence_status: INCOMPLETE
---

## Executive conclusion

**PROPOSED:** Keep the existing Crow project, selected parts, schematic and useful placement work. Establish one reproducible integration candidate from current authored source; do not start a new electrical design or erase failed experiments. Refactor the execution seams and duplicated guidance before adding more checker models. This report proposes changes; it changes no gate or board authority.

**INFERRED:** The main inefficiency is fragmented execution and promotion. The skills already require one writer, bounded attempts, backtracking and separate evidence claims. Research repeatedly developed outside the formal work graph, while reusable code accumulated project-specific authority and integrated board acceptance did not advance.

## Question and scope

Review the architecture of pcb-design, kicad-pcb and jlcpcb-fab; their references, project conductors, modular graph, candidate transactions, findings/progress accounting and Crow-specific P1 extensions. Determine whether to restart and what minimal refactor would shorten feedback loops.

This is an architectural and execution-path review, not a line-by-line correctness audit of every validator. Inventory size does not itself establish waste. Existing electrical, native DRC, manufacturing, release and physical qualification checks are retained unless their owning policy is separately reviewed.

## Evidence boundary

**CITED:** Repository subject `96ceea1db0863257066401e699925f929af2bfa4`. Inventory excluding Python caches: pcb-design 101 files, kicad-pcb 162, jlcpcb-fab 52. Crow has 18 functional blocks, 59 crossing-net interfaces and 17 modular work items. Its research directory contains 1,215 files in the inspected workspace, including generated evidence; this is not a count of independent experiments.

**CITED:** STATUS records `prototype-layout-diagnostic`, ordinary release held by prototype-only USB ESD qualification, and an isolated board with 499 opens. The formal P1 item records 0/1 attempts and no engineering acceptance. The e07 Q_PRE board and d0 timing board are distinct research subjects; neither should silently supply the other's board-bound evidence.

**OWED:** The refactor has not been implemented or benchmarked. No time or token savings are measured. Previous eight-hour time buckets were chronological summaries inferred from commits, not measured task labor or agent-token accounting.

## Findings

| Area | Evidence and interpretation | Proposed disposition |
|---|---|---|
| Lifecycle composition | **CITED:** execution-graph.md explicitly says the 19-stage plan is disclosure-only and no production driver consumes it end to end. Shell conductors remain authoritative. | Keep conductors for now; extract only their duplicated common operations. Do not introduce another top-level engine. |
| Modular graph | **CITED:** modular_design.py validates ownership/interfaces and recorded TaskAttempts, and emits `engineering_acceptance: NOT_EVALUATED`. | Retain dependency and ownership logic. Link displayed progress to existing investigation and engineering receipts without converting task PASS into engineering PASS. |
| Completion seam | **CITED:** the coarse P1 checker grants no engineering PASS; the project conductors do not invoke the modular evaluator or P1 checker automatically. Separate review/admission is still required even when a research packet has no errors. | Make the next acceptance consumer explicit for each task. One existing runtime entry point should collect candidate diagnostics and identify the owning review/gate that can close the milestone; another diagnostic manifest alone cannot complete it. |
| Research budgeting | **CITED:** 20 findings exist; only the USB-XTAL finding currently carries an investigation record. Repeated later research is not accounted there as the same recurring decision. | Dispatch recurring experiments through existing pcb_flow investigation reservation/assessment. Do not add another ledger or retroactively invent executions. |
| Candidate authority | **CITED:** route_candidate_workspace and route_experiment_store already provide isolated grading, exact rule authority, terminal outcomes and accepted pointers. | Reuse their transaction mechanics for a separately typed placement candidate. Preserve route-only acceptance semantics; add only the missing placement integration seam. |
| Block geometry | **CITED:** functional ownership permits dispersed parts, but strict physical_cells require complete declared-owner coverage. This caused local handoff repairs to grow into whole-owner partition problems. | Separate functional block ownership, diagnostic planning bounds, selected proof geometry and final native physical checks. Require exclusive cells only where an actual claim depends on them. |
| P1 extensions | **CITED:** p1_corridor_capacity.py is 2,635 lines and embeds Crow project path, board hashes, connector refs and drawing identities. | Move project authority into independently reviewed project records. Keep generic geometry verification and reject stale/mismatched records. Do not accept a self-authored exception as approval. |
| Diagnostics | **CITED:** independent per-item diagnostics exist, but several cell/branch validators still stop at the first prerequisite failure. | Collect independent errors in one pass; mark dependent checks unevaluated. Preserve strict failure and avoid producing misleading cascades. |
| Status and guidance | **CITED:** STATUS derives from pause_state; critical-path prose and the root implementation proposal supply other instructions. The critical-path note contains both older measured-edge prerequisites and the newer P1-only nominal exception. | Keep findings/receipts as engineering authority, pause_state as the scope/pause record, and generate one concise status view. Archive stale proposal/history text without deleting evidence. |
| Qualification stages | **CITED:** ordinary conductors reject prototype_only and enforce connector FULL before placement approval/routing. | Keep those gates. Make the existing bounded prototype path usable for integrated development without claiming ordinary acceptance. Any future prototype fabrication path needs an explicit policy decision and separate tests. |
| Review granularity | **INFERRED:** many tiny producer/reviewer/report cycles amplified coordination work. | Review one integrated material change or acceptance milestone. Keep independent review for rules, exceptions and high-consequence changes. |

## Recommendations

**PROPOSED implementation order:**

1. **Clarify authority and operating instructions.** Edit pcb-design/SKILL.md, references/execution-graph.md, references/modular-design.md and the relevant kicad/fabrication reference boundaries. Keep one operational procedure; mark modular_pcb_design.md historical. Explain that a prototype hold restricts claims and permitted producers, while an explicit operator pause stops work. Neither can silently waive the other.
2. **Connect existing execution accounting.** Extend the existing pcb_flow/decision_progress dispatch seam and modular status projection so recurring research consumes the same finding's budget across workers and source revisions. Failed/aborted launches remain visible. Read-only audits and unrelated work should not require an experiment reservation.
3. **Provide one integration candidate path.** Reuse candidate workspace/store machinery with a placement-specific predicate and exact source/board/PRO/DRU/tool inputs. A coordinator selects one candidate; task outputs are source changes against it. Automatic comparisons detect changed pins, fixed poses, DRC identities and required connections before integration. A failed candidate cannot replace the accepted pointer.
4. **Separate project policy from reusable checking.** Move Crow edge authority out of Python constants into project-owned, independently bound evidence. Split P1 parsing, geometry and diagnostic reporting only where it makes this extraction/testability easier. Consolidate repeated endpoint representations around the existing modular interface authority; do not replace it with another master netlist.
5. **Resume Crow using that path.** Regenerate a candidate from current source and compare it against e07 before naming a baseline. Integrate compatible audio, power and edge changes through source recipes. Grade the full conflict set. Pick one coupled block with a clear completion criterion; produce an integrated improvement before any further broad process refactor.

No wholesale engine rewrite, new project, sourcing restart or general schema migration is recommended. Retain the locked initial stock snapshot, XMOS stock exception, and manual through-hole assembly decision. Preserve old reports and failures as history; remove them from the active instructions.

```text
candidate = reopen_current_integration_candidate(exact_sources_and_rules)
work = select_ready_block_or_coupled_group(existing_graph, existing_findings)
reserve_existing_investigation(work.decision_id)
trial = run_existing_bounded_producer(candidate, work.source_change)
result = grade_independent_checks_and_mark_dependent_unknowns(trial)
assess_existing_investigation(result)
if result.satisfies_declared_milestone:
    independently_review_material_change(trial, result)
    integrate_through_source_and_regrade_affected_requirements()
elif budget_exhausted_or_no_discriminating_next_test:
    backtrack_existing_decision_without_resetting_history()
render_status_from_existing_findings_tasks_and_receipts()
```

This pseudocode describes the proposed composition, not new API names or permission to bypass current gates.

## Validation plan

| Test | Required outcome |
|---|---|
| Current Crow failure corpus before/after refactor | Same genuine native failures; no missing endpoint, foreign occupancy, stale authority or rule violation becomes accepted. |
| d0 result offered to e07 candidate | Reject mismatched subject; explicitly recompute/review affected evidence. |
| Change unrelated label versus connector pose | Reuse only evidence whose declared semantic inputs are unchanged; changed connector geometry invalidates its relevant proof. Final review remains bound to final bytes. |
| Two non-improving runs, worker/source/report renamed | Same investigation history and budget remain; next local run requires reassessment. A review receipt does not reset this counter. |
| P1 task report versus engineering gate | Display task activity and native engineering verdict separately; neither is inferred from file existence or commit count. |
| Planning overlap versus actual cell/pad collision | Planning overlap remains diagnostic unless an exclusive allocation is claimed; real required geometry failures remain blocking. |
| Prototype-only integrated candidate | Allowed solely through the declared prototype producer; ordinary acceptance, release and order still reject. |
| Candidate failure, timeout, interrupted write | Preserve prior accepted candidate and canonical sources; retain classified failed attempt. |
| Small non-Crow board | Normal flow runs without Crow refs, paths, hashes or unused block machinery. |
| End-to-end Crow block trial | One source-generated board, one coherent result, exact endpoint denominator and measurable closure of the chosen block objective; no global regression. |

Record actual elapsed task/tool time, producer runs, repeated checker calls, independent reviews and resolved engineering objectives for the same trial before and after. Token totals require available usage telemetry and must not be inferred from commits. Run existing skill authority/documentation checks and affected runtime, modular, candidate and P1 tests. Only broaden refactoring if this vertical slice demonstrates benefit.

## Source register

- [PCB lifecycle skill](../../../../skills/pcb-design/SKILL.md), [execution graph](../../../../skills/pcb-design/references/execution-graph.md), [modular procedure](../../../../skills/pcb-design/references/modular-design.md), [backtracking/investigation protocol](../../../../skills/pcb-design/references/lifecycle-and-backtrack.md).
- [KiCad skill](../../../../skills/kicad-pcb/SKILL.md), [candidate contract](../../../../skills/kicad-pcb/references/route-candidate-contract.md), [fabrication skill](../../../../skills/jlcpcb-fab/SKILL.md), [root modular proposal](../../../../modular_pcb_design.md).
- [Modular evaluator](../../../../skills/pcb-design/scripts/modular_design.py), [P1 checker](../../../../skills/kicad-pcb/scripts/p1_corridor_capacity.py), [runtime](../../../../skills/kicad-pcb/scripts/pcb_flow.py), [decision progress](../../../../skills/pcb-design/scripts/decision_progress.py), [candidate store](../../../../skills/kicad-pcb/scripts/route_experiment_store.py).
- [Current status](../STATUS.md), [findings](../findings.yaml), [modular plan](../../03_src/modular_plan.json), [full conductor](../../03_src/rebuild_all.sh), [reuse conductor](../../03_src/rebuild_reuse.sh), [critical-path history](../research/2026-09-25-release-critical-path-pause.md).
