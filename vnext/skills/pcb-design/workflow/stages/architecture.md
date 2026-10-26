# PCB-ARCHITECTURE — local admission contract

For candidate creation before admission use [exploration](exploration.md).
This file governs acceptance, not permission to draw an unaccepted candidate.

Input role: accepted `commissioned_brief`. Output role: `architecture_locked`.
Use the local independently reviewed admission verifier below. A prerequisite
certificate is required; no historical owner is a fallback.

For bounded channel, power or integration work, use the existing task.py task
names with STATUS at architecture. The packet validates the current commission
receipt, binds its reviewed subjects, and loads this stage rather than commission.
Reuse the focused engineering procedures despite their historical commission/
directory; no new scheduler or relaxed evidence threshold is introduced. Name
the exact allowed source/report writes and one integration owner before dispatch.
Task completion is separate from architecture admission below.

Adopt the project's system architecture into ARCHITECTURE, DETAIL_DESIGN and
source rules, retaining exact requirement/decision provenance. Cover every
required board type and its interfaces, without assuming a multi-board topology.
Bind applicable power envelopes, simultaneous loads, regulation/thermal/
protection/off-state behavior; signal-path loading, bias, noise and stability;
clock/reset/data format; connector pinout/returns/shield/misplug boundaries;
and whole-system cost/assembly. Explicitly justify non-applicable concerns;
do not add an analog path, clock or external interface just to fill a checklist.
Module-first choices and justified bare-IC exceptions must be explicit.

Distinguish design assumptions from external equipment facts and physical
qualification. A prototype can have named later measurements; an unaddressed
known circuit contradiction cannot be called a test plan. Resolve applicability
for this stage; defer actual mating geometry only before it is consumed, never
claim placement readiness from an unresolved profile flag.

## System-first ordering

Work at two levels within this stage, not two new gates:
1. Define the whole system: all required functions, signal/power paths, interface
   ownership and envelopes, startup/off/fault states, architecture-defining
   component choices with credible availability, and major open assumptions.
2. Complete implementation: pin-level circuits, supporting components, exact
   identities and quantities, then whole-board consistency and acceptance.

Before routine exact-part research, identify the system-level decision it serves.
Resolve topology-changing uncertainties and missing required interfaces first.
Capacitance for hold-up or regulator stability, precision networks, protection,
and other details that determine feasibility belong in the first level.
Ordinary bypass/resistor identities remain generic requirements through schematic
development; select and qualify them together at the final BOM/sourcing check.
Use [passive timing](../../procedures/part-recheck.md#common-passives-design-now-source-at-the-end)
to distinguish deferred procurement from electrical properties needed now.

Maintain a short CURRENT closure table in the existing architecture document:
blocking condition, consequence for the next deliverable, next discriminating
action, owner/dependency, and evidence/status. Keep chronology in the journal.
Classify each item as needed for this stage, later permitted qualification, or
external decision; a known contradiction is never deferred as a measurement.
Do not require a complete BOM merely to decide the system architecture.

Batch routine selections and their verification around a stable circuit or
coherent cohort. Do not introduce one report/review cycle per commodity part
unless a distinct risk requires it. Review depth follows risk and shared
dependencies, not how finely an author split the work. Integration findings can
backtrack to system choices; preserve unrelated evidence and acceptance rules.

Live circuit references use project-relative paths and optional JSON pointers,
not embedded hashes of other live circuit files. Mutually dependent circuits
are normal; mutually embedded hashes cannot be frozen by repeated refreshes.
Bind the complete rules set in the existing external task/review subject map.
The admission route checks that snapshot; changed source invalidates its review,
not another source's text. Preserve historical evidence during migration.

Independent review grades the exact source using
[admission](../../procedures/commission/admission.md). Any power/interface
change reopens affected analyses and downstream part selection; unrelated
evidence is retained. No generated schematic, layout or order is authorized by
an architecture report or this file's existence.
