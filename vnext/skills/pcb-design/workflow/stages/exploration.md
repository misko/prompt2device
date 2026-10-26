# Whole-system schematic exploration

Input: raw description and chronological user decisions, with provenance.
Output: concrete UNACCEPTED schematic candidates and an independently reviewed
repair baseline, or an explicit no-selection finding. Not a stage pass.

This route permits native draft generation before architecture and sourcing
admission. It replaces the commission-only one-channel exception for newly
initialized exploration runs only. No acceptance threshold changes.

## Author contract

Read only the common brief and current redesign pointers, if any. Independent
authors must not see each other's work or old board selections before submission.
Use separate directories and no inherited conversation. Similar choices are
allowed: independence does not require artificial architectural differences.

Within one bounded pass, choose architecture and components and produce:

- Editable KiCad schematics for all board types and repeated required functions.
- PDFs, preliminary BOM and explicit inter-board cable/pin contract.
- Native netlists and all-severity ERC when export works; retain errors.
- A short design note: requirement coverage, assumptions, sources, calculations,
  firmware dependencies and prioritized unresolved issues.

Use available native KiCad tools or a reproducible generator. Existing
tools/native_schematic.py may be used within its flat-board scope; direct KiCad
authoring is allowed for drafts, including multi-sheet candidates. Record the
producer/version and source. Preserve partial output on tool failure. Unknown
pinouts and functional boxes are marked incomplete, never passed off as circuits.
Keep electrical pin types truthful; do not suppress checks to manufacture a pass.
Prefer readable functional grouping; label-connected pin boxes need later
readability review. Export successful artifacts even when other checks fail.

Screen critical part availability/lifecycle before deep investment. Record
provisional identities and failed lookups without indefinitely blocking drafting.
Exact quantity and footprint checks close before acceptance, and before spending
a repair pass on implementation that depends on that exact identity. Common
resistors/capacitors stay generic under [passive timing](../../procedures/part-recheck.md#common-passives-design-now-source-at-the-end);
batch exact sourcing belongs at the end, not in each schematic repair.
No purchasing or hardware tests.

## Independent comparison

Review actual artifacts, not author claims. Grade requirement coverage,
electrical/interface credibility, timing, power states, firmware feasibility,
sourcing/assembly and total remaining effort. Distinguish fatal contradictions,
repairable findings and permitted later physical qualification. ERC and
source-to-netlist equality are mechanical checks, not independent circuit proof.
Do not reward candidates for omitting requirements or admitting fewer risks.
Select a repair baseline only with a credible completion path; select none if
all are unsuitable. Borrowed circuits reopen affected interface review.

For each blocking finding name the requirement authority and classify it:
known contradiction; evidence required for design acceptance; permitted later
physical qualification; or missing user authority. A proposed reviewer preference
is not an inherited requirement. State the smallest check that could close the
finding and whether to repair the circuit or revisit its upstream choice.
In the existing exploration review schema, missing authority is an `uncertainty`
finding with its authority requirement named in the statement; no new enum or
ledger is needed.
Before prototype fabrication, close design/layout/DFM and sourcing checks and
define the measurement plan. Measurements needing a first article happen after
fabrication and before production/deployment qualification. Never require that
hardware to exist merely to accept a coherent prototype schematic, and never
defer a known electrical contradiction as a measurement plan.

Bind findings to stable problem IDs, evidence and affected candidates. Use
[exploration control](../../../workflow-orchestrator/references/exploration.md).
The coordinator journal is the single execution record; authors write only
their assigned candidate directories, reviewers only assigned review files.

## Acceptance boundary

Reuse the selected draft through repairs, not a separate production authoring
system. Before promotion explicitly adopt its source/output contract into the
existing admission route and satisfy architecture, sourcing, independent
electrical/readability, connectivity, ERC and harness review. Unsupported
acceptance capabilities (for example hierarchical sheets) need migration and
tests, not a false stage pass. Stop after accepted schematics for reflection.

Use a stable drawing notice such as `PROTOTYPE — NOT FOR FABRICATION` rather
than embedding mutable workflow state in circuit source. The current independent
receipt owns stage acceptance; a draft is always unaccepted regardless of its
title. Prototype schematic acceptance does not authorize fabrication.
