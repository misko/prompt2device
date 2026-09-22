# Modular PCB work inside the existing lifecycle

Draft functional decomposition during architecture from requirements and
expected functions. After part selection and schematic generation, replace
provisional membership and interfaces with exact refs and observed connectivity
before placement begins. This is a procedure within `PCB-ARCHITECTURE`, `KICAD-SCHEMATIC`,
`KICAD-PLACEMENT`, and `KICAD-ROUTING`; it adds no lifecycle stage and grants no
gate reuse.

## Establish block ownership and interfaces

Derive blocks from the requirements, selected-part layout guidance, mechanical
constraints, and actual circuit connectivity. Schematic sheets are hints. Give
every electrical component exactly one block owner. Name board-level ownership
for shared planes, thermal copper, mechanical constraints, and other resources
that do not belong to one block.

Run `scripts/modular_design.py PLAN CIRCUIT --json REPORT`. Add
`--observations INDEX.json --evidence-root PROJECT` when reopening completed
child work. Its independent
`circuit.json` adapter extracts every source component and complete net endpoint
set, including `source_trace` connections. The authored plan has these exact
top-level fields:

| Field | Meaning |
|---|---|
| `schema`, `stage_id` | Schema 1 and the existing stage where this plan revision is drafted or validated; this does not relocate its P1–P5 children from placement |
| `blocks[]` | Stable `id`, sorted owned `refs`, and nonempty `responsibilities` |
| `interfaces[]` | One combined disposition per actual crossing net, with every `REF.pin` grouped by owning block, plus requirements |
| `shared_responsibilities[]` | Stable id, one block or `board_integration` owner, and requirements |
| `work_items[]` | P1–P5 child work inside `KICAD-PLACEMENT`, with blocks, dependencies, bounded attempts, backward repair targets, and output names |

An omitted or duplicate component owner fails. So does an omitted crossing,
invented net, unknown peer, or incomplete endpoint set. Ground and shared power
do not merge blocks, but their crossings still need a disposition. Mechanical
features absent from the electrical netlist are outside this census and remain
owned by floorplan and mechanical authorities; do not silently mix an authored
mechanical list into the observed electrical denominator.

## Schedule child work

Functional ownership does not require physical colocation. Place interface
terminations, protection, and bypass parts at the endpoints they serve, even
when other parts owned by that block sit elsewhere. Represent those attachments
in coupled placement/proof groups; do not use a block-center seed or a clean
courtyard check as evidence that its electrical placement is complete.

Use these scopes without forcing every block through a lockstep barrier:

1. `P1_FLOORPLAN` allocates fixed features, regions, and corridors.
2. `P2_BLOCK_PLACEMENT` places one block or a tightly coupled group.
3. `P3_CRITICAL_LOCAL_ROUTES` proves selected critical paths after their own P2 dependency.
4. `P4_JOINT_PROOF` grades coupled blocks and shared corridors together.
5. `P5_INTEGRATED_PLACEMENT_REVIEW` joins every declared P3/P4 proof before placement promotion.

A processing block may enter P3 while an independent connector block is still
in P2. Dependencies state the real ordering. P5 must transitively depend on all
P3 and P4 work. Backtrack targets point strictly backward; a failed attempt does
not reset when the worker or block name changes. After the bounded attempt limit,
use the recorded targets and the existing `D-BACK` procedure.

The optional observations index is a JSON list of
`{"attempt_path": "<project-relative TaskAttempt JSON>"}` rows. Each existing
schema-1 attempt's `task_id` equals the work item id and its subject must equal
`work_subject(plan, circuit)`. The checker reopens the runtime completion
manifest and hashes every file in the attempt's sibling `outputs/` directory.
A stale subject, missing or changed output, missing declaration, or unfinished
dependency cannot unlock a child. `WORK_RECORDED` means only that bounded work
and its runtime-validated outputs were recorded. Every work row reports
`engineering_acceptance: NOT_EVALUATED` because placement feasibility, coupled
geometry, routing, DRC, and review remain decisions of their existing gates.
A failed engineering prerequisite keeps dependent work undispatched, even if
delivery of its failure report passed. Do not execute a dependent task merely
to record that it is blocked, or infer admission from `WORK_RECORDED`.

## Backtrack and evidence boundaries

Classify a failure before retrying:

| Cause | First owner to reconsider |
|---|---|
| Local placement or escape | P2 block placement, then its floorplan allocation |
| Boundary corridor or coupled loop | P4 joint group, then P1 grouping/corridor |
| Package/pin-map limitation | sourcing/schematic authority and all dependent work |
| Board-wide congestion or return-path conflict | P1 floorplan/architecture |

Record exact violated constraints and evidence paths in the existing task and
findings mechanisms. An authored interface, a task `PASS`, or this checker's
coverage `PASS` does not establish geometric coexistence. Use the existing
placement receipt and independently reopened coupled-geometry witness for that
claim. Keep partial shared-net work diagnostic unless the route ownership
contract explicitly accepts the complete required scope.
