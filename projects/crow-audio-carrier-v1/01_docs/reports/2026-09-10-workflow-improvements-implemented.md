---
schema: 1
kind: pcb-human-report
report_id: 2026-09-10-workflow-improvements-implemented
title: Three PCB workflow improvements implemented
subtitle: Qualified tools, validated delivery and bounded ownership continuity
project: crow-audio-carrier-v1
date: 2026-09-10
status: REVIEWED
evidence_status: MIXED
---

## Executive conclusion

**MEASURED:** All three changes from the [implementation plan](2026-09-10-workflow-improvement-plan.md) are implemented in the existing runtime and flow interface. New skill work uses startup qualification and declared-output delivery. Routine subprocess repairs can retain their implementation owner within a predeclared allowance. Existing engineering gates, semantic handoffs and schema-1 readers remain authoritative.

**MEASURED:** An independent fresh evaluator qualified a scratch environment and recovered a real setup failure through the CLI. Its successful handback passed 1/1 delivery checks; its reopened chain passed 10/10 ownership/evidence assertions. The dense carrier canary preserved native domain failure while validating delivery. No product board was changed or release minted by this work.

## Question and scope

Implement the top three recommendations from the [twelve-hour retrospective](2026-09-10-twelve-hour-process-retrospective.md), following the approved dependency order. This is a generic skill/runtime change. It does not adjudicate the carrier's interrupted native-kernel review or complete placement/routing.

## Evidence boundary

**MEASURED:** Execution changes initially committed as 495ec717; startup qualification as 022af552. The final ownership and integration change contains the source/test bytes preserved in the [evidence manifest](../evidence/workflow-improvements-20260910/manifest.json). The archive retains exact final implementation files, test logs, three pre-fix RED controls, both carrier canaries and the independent evaluator's scratch evidence.

**MEASURED:** The evaluator ran freshly and completed its assigned workflow. Its report explicitly precedes the later initial-campaign guard and usability changes; those later changes are covered by focused regressions and an executable documentation example. Its direct host launch was not an agent-open/agent-close qualification probe. Native qualification correctly continues to report reviewer availability UNKNOWN until separately observed through that adapter.

**OWED:** No speedup percentage is established. Host event authenticity and causal classification remain coordinator responsibilities. Filesystem checks detect observed writes and reserve successors; they are not a sandbox or a tamper-proof ledger. Current carrier migration waits for its next recorded stable boundary.

## Findings

| Change | Measured resulting behavior |
|---|---|
| Execution/evidence | Schema-2 envelopes declare outputs and check IDs. Fresh directories, full combined logs, PID/exit/time receipts and exact handback validation precede successful delivery. Provider errors, unknown cleanup, missing output and deleted logs cannot pass. |
| Startup qualification | Complete-netclass serialization and explicit project reload; native clean/hostile DRC with the exact pad pair. Cache binds actual executables, imported modules, shared libraries, configuration and probe/runtime source. Repository audits run separately. |
| Ownership continuity | Same-owner task-repair preserves deadline, scope, hypothesis and cumulative limits. Initial campaign and predecessor claims prevent renamed/rebranched launches from restoring spend. Named investigations also reserve in the existing findings ledger. |
| Usability | Complete executable envelope example, explicit command separator in CLI help, documented evidence-name grammar and a duplicate-claim diagnostic naming the recorded successor. |

**MEASURED:** Three regressions were RED using an isolated copy of the actual pre-fix runtime: missing handback against cfa87025, initial-launch budget replay and deleted child log against 022af552. The same maintained tests are GREEN after correction. No gate-contract skip, denominator floor or domain check was relaxed.

**MEASURED:** The first carrier diagnostic was correctly rejected for an undeclared `.kicad_prl` write. The second commission explicitly allowed that scratch sidecar. One producer execution then yielded both the legacy process interpretation and new validated-delivery interpretation, both PASS, while its native domain result remained FAIL. The diagnostic copy contained 340 footprints, 1002 pads and 11 via items, with zero routed track segments. Its 210 warnings classify as 199 library-footprint issues and 11 dangling vias; 499 unconnected items and zero parity were retained. The copy lacked the original footprint-library context and did not run the canonical refill gate. These are canary observations, not a replacement board scoreboard. Live PCB/pro/rules/schematic bytes remained unchanged.

## Recommendations

**IMPLEMENTED:** For new work, follow the updated [runtime reference](../../../../skills/pcb-design/references/execution-runtime.md): `qualify`, `task-run`, and pre-admitted `task-repair`; use the host adapter for fresh agent delivery. Existing conductors retain compatibility. Roll back by selecting the prior dispatcher implementation, preserving failed evidence and maintaining the same engineering gates.

**OWED:** Resume the carrier's native-rule diagnosis from its preserved partial evidence before adopting any production repair. Keep the existing physical, review and order holds.

## Validation plan

**MEASURED:** Focused suites passed with the following denominators. Gate-contract retains one default slow-test skip; its existing blind spot and the disclosure suite's two blind spots are explicitly reproduced, not closed by this work.

| Suite | Passed | Known-bad fixtures |
|---|---:|---:|
| Runtime | 38/38 | 30 |
| Execution/schema and runnable example | 17/17 | 10 |
| Artifact transactions | 17/17 | 15 |
| Qualification | 6/6 | 5 |
| PCB flow | 41/41 | 17 |
| Decision progress | 17/17 | 14 |
| Gate contract | 37/37 | 24 |
| Skill disclosure | 14/14 | 2 |
| Documentation | 15/15 | 2 |
| Structure contracts | 17/17 | 13 |

**MEASURED:** Skill-authority check and skill-creator quick validation passed. No full board rebuild or release-gate pass is claimed. The archive was reopened member by member and all 141 sizes/digests matched.

## Source register

- [Final contract failure](../evidence/workflow-improvements-20260910/final-contract-failure.log) and [corrected contract audit](../evidence/workflow-improvements-20260910/final-contract-pass.log): the new evidence folder needed its own governing contract; no audit ceiling changed.
- [Evidence manifest](../evidence/workflow-improvements-20260910/manifest.json).
- [141-member evidence archive](../evidence/workflow-improvements-20260910/85090f9f83b413dddfaf96e6aa86177d9cdbf9c76486702dfcb7ea045a56d890.tar.gz).
- [Runtime authority and examples](../../../../skills/pcb-design/references/execution-runtime.md).
- [Lifecycle ownership rules](../../../../skills/pcb-design/references/lifecycle-and-backtrack.md).
- [Flow interface](../../../../skills/kicad-pcb/scripts/pcb_flow.py).
