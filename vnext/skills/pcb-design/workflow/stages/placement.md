# KICAD-PLACEMENT — complete drafts, one refinement baseline

Requires accepted `schematic_reviewed`; produces `placement_reviewed`, never a
routed or manufacturing-ready board. The user must authorize leaving the
schematic checkpoint. Use the existing orchestrator and project journal.

## Inputs and exploration

Adopt a placement scope and input manifest: accepted schematic/part/footprint
identities, mechanical requirements and assumptions, layer-role intentions,
critical pin-specific placement obligations and their sources. Distinguish
manufacturer requirements from designer allocations. Unfixed dimensions may
be proposed; never invent enclosure fit or user approval. Ground-reference and
cross-block paths are whole-board obligations, not block-local preferences.

When alternative global arrangements could help, dispatch bounded independent
authors with identical inputs and isolated directories. Each returns every
board type with all actual footprints placed, native KiCad boards, readable
previews and one short rationale with open findings. Prefer concrete drafts
over a preliminary consensus/research loop. Do not force artificial diversity.

Functional blocks group components and local constraints; they do not change
electrical ownership or create a stage per component. Blocks may be translated
and rotated, but connector-side protection and load-side filtering may require
different physical regions. Keep exact membership, ports, constraints and
cross-block relationships visible. A repeated cell must be checked in every
actual instance; equivalent schematic structure does not prove equivalent space.

## Build, compare, refine

Use [placement tooling](../../procedures/placement/tooling.md). This first local
producer supports rectangular boards with explicit radiused edge recesses,
top-side footprints and quarter-turn
orientations. Unsupported geometry needs an explicit tool extension plus tests,
not an approximation presented as verified. Do not alter accepted circuit inputs.
Derived mechanical envelopes may refine conservative footprint drawings only
with retained evidence, unchanged pad geometry and independent review.
Explicit mechanical-hole repairs use the tooling's constrained `npth_revisions`
recipe and fresh review, retaining the accepted library and electrical source.
They reopen affected mating, routing, assembly and release evidence; they cannot
be promoted through cosmetic-only layout finishing.

Mechanical checks observe native placed geometry and nets, compare them to
accepted inputs, check body/courtyard clearance, edges, mounting keepouts,
declared connector access, pin-specific proximity and declared critical escape
reservations. They are not a proof of global routability, EMC or physical fit.
Any omitted necessary constraint remains an independent-review finding.

Compare actual candidates independently: hard violations first, then credible
completion effort, access, routing/return-path feasibility and mechanical cost.
Select one baseline or none. Refine the highest-impact finding on that baseline;
do not run several ongoing repair pipelines. Reassess after one unsuccessful
attempt and stop routine retries after at most two on the same causal problem.
New whole-board drafts need evidence-led redesign pointers and remaining budget.

## Acceptance and stop

Run fresh source/native/netlist/geometry checks, inspect actual previews and
independently review completeness, mechanical/access, electrical placement,
routing feasibility, reproducibility and applicability. A plan, clean bounding
boxes or author's own PASS cannot supply acceptance. Review the actual layers,
escapes, ground-return plan and all repeated instances, not only a pilot cell.

Before acceptance, demonstrate that critical blocks can be routed. The coordinator
declares which connections could force a placement change; the independent
reviewer checks that scope. Retain a native scratch trial on the exact placement
showing those connections, filled copper, returns and applicable electrical/thermal
evidence. This is bounded feasibility evidence, not complete-board routing or a
prerequisite routed-board receipt. Missing or failed trials block acceptance.
Use the version2 admission in [placement tooling](../../procedures/placement/tooling.md).

`tools/placement.py issue` binds the selected source, native boards, checks,
review, input manifests and upstream accepted toolchain. `check` replays them.
Only after both succeed may the coordinator record `placement_reviewed`.
Stop for the user's phase reflection before routing. Preserve all failed drafts.

Prior receipts remain interpreted by their exact archived toolchain when a
skill update changes broad instruction identities. The placement contract binds
that archive and current upstream subjects; this is explicit versioned adoption,
not silently refreshing old approvals. Source changes still fail upstream checks.
New admissions use version2; historical receipts retain their archived verifier
and do not gain the new critical-route claim automatically.
