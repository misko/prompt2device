# Shared task interface

This is a semantic interface, not a new file format or execution service.
Map it to the domain's existing records. If a required fact has no storage or
enforcement owner, expose that gap rather than inventing a success.

| Object | Required meaning |
|---|---|
| Stage | Stable identity, required evidence, applicability, outputs, acceptance owner and dependencies |
| Task | Stage, bounded objective, exact inputs, selected instructions, allowed writes, output, verifier, deadline and stop boundary |
| Attempt | Stable identity, actual work/result, exact subjects, findings and budget charged |
| Progress checkpoint | Parent deliverable, newly settled attempts, domain-verified advancement versus prerequisites, exact evidence and any bounded recovery decision |
| Acceptance | Owning check/review on exact outputs; explicit coverage and applicability |
| Handoff | Accepted state, open findings, cumulative budget, resumable evidence and next action |

Paths, serialization, command syntax and lifecycle enums belong to the adapter.
The interface does not add fields to existing schemas or silently reinterpret
their status enums. Do not serialize this table as a second task ledger.

The adapter must identify the authoritative records and authorized promotion
consumer. A task completion message, elapsed time or empty finding list cannot
substitute for verification. Checks with no graded scope cannot prove acceptance.
Unavailable inputs require a blocker or an upstream task, not fabricated facts.

Decompose large work by output and interface. Child-task acceptance proves only
the child scope; the integration owner still runs domain-wide verification.
Independent review consumes the exact candidate and criteria, not an author's
claim of success. Never broaden write scope merely to repair an inconvenient
failure.

Bind historical evidence through immutable snapshots when later-stage work will
replace its live path; otherwise an upstream review can accidentally depend on
its downstream replacement. Keep actual current requirements and inputs live:
a snapshot must not conceal a change that requires causal re-acceptance.
