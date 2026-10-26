# Local project binding — research and upstream admission

The project remains outside the skill. `01_docs/BRIEF.md` owns the original
prompt, user decisions and assumptions; STATUS.md is the live view;
journal/commission.md is append-only history. Read project contracts before
writing. Research tasks never remove the hold or prior accepted evidence.
For upstream admission, explicitly bind the project to the
[admission route](../procedures/commission/admission.md) and its current local
verifier; preserve older frozen task snapshots. Only independent review plus
current receipts permits the coordinator to record the corresponding graph role.

## New project from raw inputs

When no project records exist, initialize an absent or empty absolute destination
using explicit source files (not a replay's expected answers or prior reports):

```sh
python3 tools/bootstrap.py --project /absolute/new-project --prompt /absolute/PROMPT.md --decisions /absolute/USER_DECISIONS.md --capability /absolute/capability-profile.json
```

The tool preserves exact bytes and SHA-256 provenance, creates the local contracts,
commission working status, active hold and initial journal. It refuses nonempty
destinations; do not use it to repair or overwrite an existing project. Decisions
must be chronological; explicitly record no decisions when none were supplied.
The coordinator or explicitly assigned intake author must read the preserved
sources and reconcile facts, superseding decisions, interpretations, assumptions,
authorization and stops in BRIEF.md before preparing an engineering task packet.
This is agent synthesis, not parser output: initialization does not extract
requirements or dispatch an engineering attempt.
Include `--input 01_docs/inputs/PROMPT.md --input 01_docs/inputs/USER_DECISIONS.md`
when building the first task packet so the raw source bytes are also hash-bound.

## Existing project tasks

`tools/task.py` opens and hashes local instructions and explicit project inputs.
Resolve the packet's instruction keys against its absolute `instruction_root`,
not the worker's current directory or another checkout.
`instructions` are required reading. `tool_bindings` records implementation
identity, not mandatory source-code reading. Load implementation only for the
command/schema needed or a demonstrated tool failure. Schematic packets select
only the adopted producer manuals; the stage owns their shared acceptance rules.
Dispatch/recovery instructions are loaded by the coordinator for those actions,
not copied into every author's mandatory reading. The orchestrator entrypoint
still supplies the retry ceiling and routes failures back to their owner.
It neither reads dependencies.json nor imports legacy tools. Historical
`tools/context.py` and `tools/checkpoints.py` are not the standalone execution
path. Do not run them to satisfy a missing local capability.

At STATUS architecture, the same bounded design task names require and revalidate
`06_build/checkpoints/commissioned_brief.json`; the packet binds the receipt,
independent review and all reviewed source subjects. It selects the architecture
contract and declares source/report output guidance, not permission to accept a
stage. Restrict actual writes in the coordinator dispatch. `schematic-draft`
remains commission-only. For an explicitly adopted non-RF flat-board source
contract, STATUS schematic permits `--task schematic-design`; it validates
parts_locked and binds the complete upstream chain. Sourcing's independent
assembly review must cover contracts.md, 01_docs/schematic-contract.json and
01_docs/capability-profile.json. The producing sourcing gate and consuming
schematic dispatch use the same predicate.
Prepare that declaration before sourcing review, not as unreviewed permission
afterward. Read the schematic stage for build/review/receipt steps. Other
stage/task routes through task.py remain unsupported. The separately adopted
[placement stage](../workflow/stages/placement.md) uses tools/placement.py and
its exact input manifest, not a fabricated schematic-design task packet.
Old frozen bindings do not inherit this route.

One author writes one dated report under `01_docs/reports/`; the coordinator
alone updates status and journal. Use the project's report contract and mark
incomplete evidence honestly. The reviewer gets the exact report bytes and
primary sources, rederives critical margins, and records findings against the
report hash in the journal. Any repair invalidates that review until rechecked.
Software arithmetic tests verify math, not physical assumptions or topology.

For a multi-task run, put a run ID and stable task IDs in that same journal.
Record actual dispatch/completion times, stage, actor, exact output and review
result. A backtrack records its causal finding, destination and affected
dependent evidence before the new attempt. Queued work is not dispatched work;
task completion is not stage promotion. Do not create a second progress ledger.

Keep STATUS's human-readable preamble short: current milestone, accepted evidence,
open blocking findings and next action. Put chronology in the journal, not this
live view. At an accepted user phase stop use `state: checkpoint`, not `blocked`;
task dispatch refuses this state until an authorized coordinator resume. A
checkpoint label is not an acceptance receipt and does not prove completion.

Bound each author/reviewer work segment to 10 minutes; its checkpoint returns
control to the orchestrator, not an automatic end to the design objective.
Before iteration, declare a finite total author/review budget and maximum
candidate attempts. Honor any explicit project limits. Without a task-specific
allowance, default to one initial attempt and one reviewed follow-on (local
repair or upstream alternative), at most 20 author minutes and 20 review minutes.
Every continuation consumes the same budget; only the coordinator may dispatch
it after the recovery decision. Exhaustion requires pause/reassessment, not an
automatic reset. These are procedural limits, not automatic cancellation.
Keep stable user-authorized policy in BRIEF.md: model/role preferences, scope,
explicit user budget/attempt ceilings, permitted recovery and phase stops.
Record each coordinator-selected task's finite author/review allowance, reserved
expert capacity, deadline, writes and cumulative spend in the existing journal
before dispatch. These operational entries do not require editing an unchanged
brief or renewing commissioning. Task packets bind the journal's exact bytes;
preserve the dispatch snapshot when appending subsequent events. Model names
belong to this project policy, not the generic orchestrator. Default limits above
apply when no explicit task allowance is provided.

This separation does not renew exhausted attempts, override a user ceiling or
hide a requirements change in the journal. Apply recovery reassessment first;
any changed requirement, equipment assumption, authority or stable policy belongs
in BRIEF and reopens affected acceptance. A review may explicitly bind execution
evidence when necessary; changing such a reviewed subject still invalidates its
receipt. Existing frozen projects require explicit reviewed instruction migration
before using this separation; do not rewrite their historical brief or budgets.
Prefer the user's selected worker model; escalate a named unresolved calculation,
requirement interpretation or evidence-sufficiency question, not merely missing
hardware data. Follow the orchestrator's recovery rule and independently review
the result. Preserve attempt results; later qualification is permitted only by
the owning domain contract, never by an expert's authority alone.

This slice does not port the project's legacy audit executables. Inspect the
applicable report/status/journal rules locally and state which checks were
manual; do not claim an unrun legacy audit passed. Unsupported gate commands
remain unrun. Before downstream promotion, migrate required verifiers and
their negative controls; do not weaken project contracts to bypass them.

Provenance: invariants extracted from the previously retained commission,
dispatch and project contracts (legacy baseline d94a96d84518dd29b2578f820311cbd89dfa1beb).
This is a scoped reimplementation, not a claim of full legacy policy parity.
