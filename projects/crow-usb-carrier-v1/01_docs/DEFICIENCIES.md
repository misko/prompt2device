# Release deficiencies

Release/revision under consideration: not yet selected.

Record small improvements here so they do not interrupt a working release.
Follow the pcb-design lifecycle procedure, section 8, for triage. This document
discloses dispositions; gates, review receipts, the brief, and any
`findings.yaml` ledger retain their authority.

## Fix before this release

The authoritative open design controls are in [findings.yaml](findings.yaml):
capacitance, passive fault protection, power delivery, connector geometry, exact
parts/sourcing, and replacement of layout seed contracts. Native schematic review passed on 2026-09-23; placed/routed-board verification remains pending.
No design-clean or release claim is made.

## Deferred to a future release

The following nonblocking presentation observations are retained for next-release planning.

| ID | Affected revision/refs and issue | Impact; evidence it can wait; workaround if needed | Owner | Target revision or revisit trigger | Action and closure test | Status / closure evidence |
|---|---|---|---|---|---|---|
| CROW-P2-RENDER-01 | 92-page schematic, pages 44/52: graphics close to U_ADC_1V8_OK and C_ADC_PWR_BAD | Complete references remain legible; independent Terra review SOUND | Schematic presentation | Next presentation revision or new ambiguity | Improve spacing and independently recheck regenerated PDF | Deferred; 08_reviews/2026-09-23_schematic-r2_terra_source.md |
| CROW-P2-RENDER-02 | Sparse interior detail tiles on XMOS/TDM sheets | Overview/detail coverage complete; no omitted endpoints | Schematic presentation | Next renderer revision | Reduce blank tiles without reducing pin/label coverage | Deferred; same independent render review |

## Separate order / first-article / production holds

No items recorded yet; this is not an orderability or hardware-pass claim.
For each hold, link its authoritative record, name the boundary it blocks,
and state the evidence needed to close it. Do not classify these as minor.

## Release handoff

Before sealing, reconcile with current reviews and copy this document to the
staged release's `verification/DEFICIENCIES.md`. Include it in normal manifest
hashing; never add it retroactively to a sealed release. Revisit deferred IDs
at next-release planning and retain closure evidence.
