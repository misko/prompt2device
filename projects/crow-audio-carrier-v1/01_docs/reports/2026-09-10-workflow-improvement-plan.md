---
schema: 1
kind: pcb-human-report
report_id: 2026-09-10-workflow-improvement-plan
title: A simpler execution path for the PCB skill
subtitle: Three small changes built on the existing runtime, qualification checks and ownership rules
project: crow-audio-carrier-v1
date: 2026-09-10
status: REVIEWED
evidence_status: INCOMPLETE
---

## Executive conclusion

**PROPOSED:** Implement the top three retrospective recommendations as three
reviewable changes sharing one execution path:

**Qualify the environment → run a bounded task → validate its handback →
repair locally or request independent judgment.**

Build in dependency order: execution and evidence first, startup qualification
second, ownership rules third. The user experiences a short startup check and
fewer interrupted repair tasks. The existing engineering gates retain authority.

The implementation should replace repeated coordination work, not introduce
another framework. Reuse TaskEnvelope, TaskAttempt, the bounded runtime,
artifact transactions and the existing findings ledger. Keep the skill entry
point short; put operational detail in its existing references.

## Question and scope

Implement recommendations1–3 from the [twelve-hour retrospective](2026-09-10-twelve-hour-process-retrospective.md): tool qualification, automated execution/evidence,
and continuity of implementation ownership through routine repairs.

This plan prepares changes; it does not implement them. The active board still
needs its native-rule diagnosis and all subsequent release gates. Process
qualification is not evidence that its design, placement or release passes.

## Evidence boundary

**MEASURED from source inspection:** The repository already has most primitives.
`pipeline_runtime.run_stage` owns process launch and termination;
`execute_attempt` handles subprocess envelopes and exact inputs;
`pipeline_execution` owns strict task/attempt schemas;
`pipeline_artifacts` provides staged output validation and promotion;
`pcb_flow` already exposes run, preflight, handoff and validation.

**INFERRED gap:** These primitives are not yet composed into one dependable
workflow for child evidence, agent completion, startup compatibility and
bounded same-owner repairs. In particular, execute_attempt currently accepts
subprocess envelopes only. Agent supervision needs an explicit host adapter;
a shell script cannot independently launch or monitor Codex reviewers.

## Findings

| Recommendation | Existing owner to extend | Missing behavior |
|---|---|---|
| Execution and evidence | pipeline_runtime, pipeline_execution, pipeline_artifacts; thin pcb_flow interface | Consistent task output allocation, child receipt closure, durable failure artifacts and validated agent handbacks |
| Startup qualification | pcb_flow preflight integration and maintained native fixtures | Version/config-bound compatibility receipt plus separately observed live reviewer availability |
| Ownership continuity | lifecycle-and-backtrack, execution-runtime, compute-tiers and existing investigation ledger | Explicit distinction between routine execution repair and a changed engineering hypothesis, with enforced limits |

## Recommendations

### Change 1 — Make every task produce a trustworthy result

**PROPOSED deliverable:** One composed execution path, exposed through the
existing pcb_flow interface. CLI spelling is finalized with its current parser;
this plan does not imply that a new command already exists.

- The runtime allocates a unique run directory below the existing governed
  build area. Producers receive explicit scratch/output paths and do not race
  the coordinator to create the same directory.
- Each child runs through the existing bounded launcher. Retain stdout,
  stderr, argv, cwd, actual PID/times/exit status, input identity and declared
  outputs. Capture a deliberate environment projection; do not log credentials.
- Child timeouts inherit the remaining parent deadline. Keep partial outputs
  after failure. If a logging/storage limit prevents complete capture, record
  the loss and refuse complete-evidence admission.
- Validate completion against declared outputs and relationships: files reopen,
  identities match, required checks have results, process cleanup is known,
  and incomplete rows are explicit. An exit-zero producer or an agent saying
  “done” is insufficient.
- Reuse the artifact manifest and TaskAttempt terminal vocabulary. Failed
  evidence may be archived as a completed failed attempt; it never becomes an
  accepted engineering bundle. Generate the compact handoff from these records.
- Add a narrow host adapter for agent state and delivery. A missing report,
  provider error or deadline produces an explicit unresolved terminal outcome.
  If host telemetry is unavailable, record UNKNOWN; do not infer completion
  from elapsed time or kill unverified PIDs after a resumed session.

**Acceptance:** Directory collision, missing executable, failed child,
exit-zero/missing output, stale input, early agent handback, timeout with
surviving descendants, output truncation and provider failure all retain the
available evidence and block false success. One terminal attempt is published;
late callbacks cannot overwrite it. Existing accepted artifacts remain intact.

Extend the current runtime/execution/artifact suites. Introduce a new test file
only for a genuinely new adapter boundary. Prove each changed behavior RED on
pre-fix code, then GREEN on the same test.

### Change 2 — Qualify the tools before spending board effort

**PROPOSED deliverable:** One startup qualification entry in pcb_flow, using
Change1 for all probe executions. Separate stable compatibility from live
availability in its output.

Stable checks cover the selected workflow's actual Python/KiCad executables,
required libraries/configuration, a tiny serialize/reload fixture with complete
netclass schema, and native positive/negative DRC with exact class/pad/finding
identities and nonzero denominators. Run the existing relevant repository
contract audits. Keep the fixture reusable and project-independent. This is a
small compatibility test, not a new general KiCad rule parser.

Cache only successful stable checks, keyed by the actual executable/library
identity, relevant configuration, probe source/fixture hashes and the checked
repository dependency closure. Changing any covered input invalidates the
receipt. Unrelated board edits should not require rerunning an unchanged API
probe; repository audits retain their own source-dependent freshness.

Check reviewer availability through the host adapter when independent review is
needed. A bounded fresh launch must acknowledge its subject and deliver a tiny
valid result. This demonstrates current availability, not future quota or
review quality. Do not reuse that probe as a supposedly fresh design review.
Do not cache availability as a promise that later launches will succeed.

Return actionable named failures, the last qualification receipt, and which
work can still proceed. Missing KiCad blocks native work; unavailable reviewers
block review admission, while independent authorized preparation can continue.

**Acceptance:** A missing/incompatible tool, class serialization fallback,
missing complete-track reporting, stale cached receipt and failed reviewer
launch are caught before dependent work. The clean fixture passes independently;
the hostile fixture fails for its intended physical finding. No board artifacts
are mutated during qualification.

### Change 3 — Keep the implementation owner until a real boundary

**PROPOSED deliverable:** A short revision to existing lifecycle rules, backed
by executable dispatch tests. Use the following decision table:

| Observed outcome | Next action |
|---|---|
| Known execution/setup defect, remedy inside declared scope | Same owner may correct it and execute a separately recorded attempt within the original task allowance |
| Failed engineering check, same hypothesis and measured improvement | Same owner continues within the existing investigation limits |
| Changed assumption, unsupported method, scope expansion or plateau | Stop local repair and invoke the existing fresh D-BACK judgment boundary |
| Accepted schematic, accepted placement/pilot before routing, or layout seal | Preserve the existing mandatory fresh stage handoff |
| Provider failure, exhausted deadline or completion cannot be verified | Preserve partial output and explicit unresolved state; no automatic replacement or budget reset |

One source transaction has one capable implementation owner; scripts handle
mechanical loops. Ownership continuity does not mean routing every cheap command
through a large reasoning model or retaining an exhausted context indefinitely.
Existing context-pressure handoffs and role ceilings still apply.

Predeclare the deadline, allowed edits and total execution allowance. Record
setup errors and engineering evaluations separately, while charging all elapsed
work and preserving every failed launch. Do not retroactively uncharge the
current campaign. Extend the existing attempt/investigation record only where
necessary; no parallel budget ledger. The coordinator assesses classification
from evidence rather than trusting an author's convenient label.

Because schema1 is closed, any new durable field requires an explicit schema
revision, reader compatibility tests and migration of mutable records. Never
rewrite sealed evidence to fit a new schema. Existing envelopes without the new
repair allowance keep today's stricter behavior.

**Acceptance:** An injected wrong-cwd or directory error can be corrected by the
same owner when admitted in advance. A changed clearance premise still requires
fresh judgment. Reclassifying an engineering failure as a setup error cannot
restore budget. An exhausted task and a stale handback cannot resume by renaming
the task or switching agents.

### Rollout

**PROPOSED:** Ship three dependency-ordered commits or PRs, each with its source,
focused tests, contracts and short documentation change. Keep new execution
behavior opt-in until the canary agrees with the current path.

Use one small clean project fixture and one dense carrier fixture in isolated
scratch trees. Execute a producer once and compare the old/new receipt
interpretations where possible; do not run duplicate live producers merely to
obtain a shadow comparison. A fresh independent evaluator then follows the
revised skill on a realistic task without being told the intended outcome.

Only after these tests pass should the new path become the default for new
work. Migrate the current carrier at a recorded stable boundary. Older evidence
stays readable and unchanged. A rollout failure restores the prior dispatch
path and preserves the failed run, rather than relaxing a domain check.

Update existing execution/lifecycle references, owning contracts and relevant
project templates in the same change. SKILL.md should contain only the short
workflow and routing links. Avoid another checklist or a second source of truth.

## Validation plan

**OWED before adoption:**

1. Change1's process and completion controls pass their deliberately broken
   cases; original runtime cleanup guarantees remain intact.
2. Change2 catches the previously observed setup/serialization/reporting errors
   and invalidates each independently changed qualification dependency.
3. Change3 retains all semantic handoff boundaries and cumulative limits while
   eliminating new-agent transfers for the admitted routine-error fixtures.
4. Run the relevant execution, runtime, artifact and pcb_flow tests, then the
   existing contract, skill-authority and documentation gates for changed homes.
5. Compare canary results: identical engineering findings, no accepted partial
   output, no lost available child evidence, and no handoff caused solely by
   the injected routine setup failures. Measure elapsed time and owner transfers;
   do not promise a speedup before this comparison.

Success is a shorter reliable path to the same engineering verdicts. Test
counts, new schemas and additional receipts are not the product outcome.

## Source register

- [Twelve-hour retrospective](2026-09-10-twelve-hour-process-retrospective.md).
- [Execution schemas](../../../../skills/pcb-design/scripts/pipeline_execution.py).
- [Bounded runtime](../../../../skills/pcb-design/scripts/pipeline_runtime.py).
- [Artifact transactions](../../../../skills/pcb-design/scripts/pipeline_artifacts.py).
- [Compatibility process adapter](../../../../skills/kicad-pcb/scripts/process_runner.py).
- [Existing flow entry point](../../../../skills/kicad-pcb/scripts/pcb_flow.py).
- [Runtime authority](../../../../skills/pcb-design/references/execution-runtime.md).
- [Lifecycle and backtracking](../../../../skills/pcb-design/references/lifecycle-and-backtrack.md).
- [Compute roles](../../../../skills/pcb-design/references/compute-tiers.md).
