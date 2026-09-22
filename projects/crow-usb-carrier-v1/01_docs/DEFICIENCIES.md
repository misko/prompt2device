# Release deficiencies

Release/revision under consideration: not yet selected.

Record small improvements here so they do not interrupt a working release.
Follow the pcb-design lifecycle procedure, section 8, for triage. This document
discloses dispositions; gates, review receipts, the brief, and any
`findings.yaml` ledger retain their authority.

## Fix before this release

No items recorded yet; this is not a gate-pass claim. Link current blockers
to their owning findings/receipts rather than duplicating gate state here.

## Deferred to a future release

No items recorded yet. Use stable IDs; one row per item is sufficient.

| ID | Affected revision/refs and issue | Impact; evidence it can wait; workaround if needed | Owner | Target revision or revisit trigger | Action and closure test | Status / closure evidence |
|---|---|---|---|---|---|---|

## Separate order / first-article / production holds

No items recorded yet; this is not an orderability or hardware-pass claim.
For each hold, link its authoritative record, name the boundary it blocks,
and state the evidence needed to close it. Do not classify these as minor.

## Release handoff

Before sealing, reconcile with current reviews and copy this document to the
staged release's `verification/DEFICIENCIES.md`. Include it in normal manifest
hashing; never add it retroactively to a sealed release. Revisit deferred IDs
at next-release planning and retain closure evidence.
