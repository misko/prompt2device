# Modular PCB work inside the existing lifecycle

Draft functional decomposition during architecture from requirements and
expected functions. After part selection and schematic generation, replace
provisional membership and interfaces with exact refs and observed connectivity
before placement begins. This is a procedure within `PCB-ARCHITECTURE`, `KICAD-SCHEMATIC`,
`KICAD-PLACEMENT`, and `KICAD-ROUTING`; it adds no lifecycle stage and grants no
gate reuse.

## Contents

1. Establish block ownership and interfaces
2. Bind IC research before placement work
3. Schedule child work
4. Planning readiness and the native candidate loop
5. Backtrack and evidence boundaries

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
| `external_prerequisites[]` | Optional named physical evidence required by later child work; the current checker supports `connector_full` with a FULL phase receipt, binding receipt, and native board path |
| `work_items[]` | P1–P5 child work inside `KICAD-PLACEMENT`, with blocks, dependencies, bounded attempts, backward repair targets, output names, and any external prerequisite ids |

An omitted or duplicate component owner fails. So does an omitted crossing,
invented net, unknown peer, or incomplete endpoint set. Ground and shared power
do not merge blocks, but their crossings still need a disposition. Mechanical
features absent from the electrical netlist are outside this census and remain
owned by floorplan and mechanical authorities; do not silently mix an authored
mechanical list into the observed electrical denominator.

## Bind IC research before placement work

Before allocating P1 corridors, reconcile the source-derived selected-IC census
with `03_src/rules/ic_reference_research.yaml`. Dossier research may be reused
only for the same exact MPN/package; every instance records its own operating
mode, circuit, and stack/rule applicability. A `missing_evidence` packet is a
handoff to its research owner and keeps P1 incomplete. An independent semantic
review of the completed packet must pass before board generation. P1 uses
reviewed package/stack constraints; P3 owns native proof of each critical route.

## Schedule child work

Functional ownership does not require physical colocation. Place interface
terminations, protection, and bypass parts at the endpoints they serve, even
when other parts owned by that block sit elsewhere. Represent those attachments
in coupled placement/proof groups; do not use a block-center seed or a clean
courtyard check as evidence that its electrical placement is complete.

After the first native placement, census every footprint's full body/courtyard
envelope and pads against its functional owner and all planning regions before
building P1 corridors. Report owner escapes, foreign planning intersections,
and actual cross-owner native collisions separately; a rectangle overlap is
not a copper collision. Resolve native collisions and name any intentional
remote physical pockets or connector overhangs before treating a broad block
region as exclusive. Re-run the census after a coupled floorplan move.

For an isolated placement trial, generate its native board from the current
governed circuit/netlist and run the same post-generation transforms and
project-local `.kicad_pro`/`.kicad_dru` rules as the normal board rebuild before
comparing DRC issue identities. Preserve the exact input and rule hashes in the
trial receipt. A bare PCB checked without its process rule areas is only a
geometry probe; it cannot reject or admit a placement under the product's
native DRC. Compare named issues as well as totals, since equal counts can
hide a changed defect.

Use these scopes without forcing every block through a lockstep barrier:

1. `P1_FLOORPLAN` allocates fixed features, regions, coarse corridors, and boundary witnesses.
2. `P2_BLOCK_PLACEMENT` places one block or a tightly coupled group and closes its local endpoint placement and access to the P1 boundary.
3. `P3_CRITICAL_LOCAL_ROUTES` proves exact pad pockets, local escapes, filled reference and selected critical paths after their own P2 dependency.
4. `P4_JOINT_PROOF` grades coupled blocks and shared corridors together.
5. `P5_INTEGRATED_PLACEMENT_REVIEW` joins every declared P3/P4 proof before placement promotion.

Before counting a P3 route, sweep the *full copper width* of every segment
against the routed block's physical cell, foreign planning regions, and the
native body/courtyard envelopes of nearby components, including the route's
own launch and receive parts. Name the unavoidable pad-to-outside launch
separately; an unrestricted same-footprint body crossing is not an escape
proof. Record the smallest positive margins and check that they remain useful
after assembly/placement tolerances, as well as native pad/copper clearance,
filled-reference continuity and endpoint connectivity. Native DRC alone does
not reject a track under a component body or across a planning boundary.
When several local route variants trade one such conflict for another, return
to coupled support-part placement instead of tuning a trace in an unaccepted
floorplan.

For a board with a named coarse corridor contract, bind the source, interface,
footprint alias, floorplan, native board, and independently expected contract
hashes. Name at least one source-owned `REF.pin` boundary witness for each
covered net, verify its native pad alias and net, and give each reservation a
board-coordinate envelope, layer, and nonzero rough demand. A physical
`native_pad_face` witness belongs to an explicitly fixed P1 reference: its
small boundary bbox contains the actual pad on the reserved layer. A
P2-movable reference instead uses `virtual_block_face`: its small bbox lies on
the named face of its owning source region and touches the reservation outside
that region. Its pad identity and net are verified, but the pad need not be at
the face or on the reserved layer. Record an explicit `P2_REQUIRED`
pad-to-face obligation naming the pad, net, block, face, layer, and reservation;
P2 must prove the local path and any layer transition. The virtual face is an
allocation target, not a physical pad-access claim.
Check the outline, fixed features, native rule areas, and potential capacity
before spending P2 work. A movable part that occupies an envelope is relocation
debt, not free routing space. A raw slot count only screens a reservation; it
does not prove that all routes fit together. Record the required return-plane
allocation and whether filled-reference proof is still absent. Keep the full
cross-block endpoint list in the interface authority, while P2/P3 close every
local terminal, pad access, effective rule clearance, return, and DRC detail.
An edge connector's intentional body overhang needs its own mouth-to-outline
and assembly evidence; a generic on-board witness does not waive that datum.
Viable raw capacity remains `INCOMPLETE` until later evidence closes these
obligations; the coarse checker grants neither route nor engineering acceptance.

When a crossing net visits three ordered block owners, do not count each
inter-block span as a separate top-level route. The schema-2 coarse checker
supports an opt-in `linked_paths` series model with one reservation, exact
source-to-native pad coverage, one intermediate pad join per net, and either a
physical then unresolved stage or two physical stages. Each physical stage
must independently clear native obstacles and demand at least one rough slot
per signal net; each stage retains its own P2 pad-access and filled-return
obligations. The linked result remains `INCOMPLETE` and has no aggregated
capacity. A branched net, including fused connector contacts, needs an exact
`unresolved_multiterminal_branches` tree when its physical launch cannot yet
be proved and the checker can verify at least three owner-contained native
endpoints. Keep every native endpoint and P2/P3 obligation in that tree and
leave its geometry and capacity null. If an endpoint lies outside its declared
owner or a two-terminal crossing has no valid corridor, repair the source
ownership or handoff instead of inventing a branch. Neither model substitutes
for a later route, return-path, mechanical, or independent P1 review.

When placement changes trigger automatic reference-label movement, check that
affected visible labels still identify their own footprints in the assembly
view. Zero silkscreen DRC overlap does not establish that association. If the
placer falls back to a distant or ambiguously near-other-part label, revise
the placement or supply an explicit, checked assembly-label mapping before
calling the block placement ready.

If a narrow local opening is useful before its complete inter-block route can
be allocated, schema-2 `access_only_portals` can record the exact native pads,
their electrical owners, the transit owner and any named non-electrical
planning overlap. Keep its capacity null and its result `INCOMPLETE`; it
receives no reservation, route or P1 credit. Require local pad-to-port and
remote-route obligations plus filled-return debt. Check the portal against
native bodies, pads, copper, rule areas, foreign cells, and every same-layer
reservation or physical stage. Resolve any overlap in the source allocation
before treating the portal as a valid local access screen; a planning-region
overlap alone does not make that region an electrical owner.

For a shared power handoff, keep the net's complete source/native terminal
denominator separate from the small set of pads that physically enter the
port. Record local P2 connection debt for every terminal, entry-pad access,
current and thermal limits, and the filled return. A one-pad port declaration
cannot stand in for a many-terminal power tree; leave the handoff unallocated
until the source contract accounts for both sets.

When a modular plan declares `connector_full`, every P3 item and the P5 item
must name that external prerequisite unless it explicitly supplies `p3_scope`.
That optional closed mapping contains `affected_work_items` (P3 ids) and
`independent_work_items` (records with `id` and nonblank `rationale`). Together
they must partition every P3 item exactly once. Affected items must declare
`connector_full`; independent items must omit it. Review the independence
rationale against actual connector, mate, tool and service envelopes; a
different block name alone is not independence evidence. The declaration is
planning authority, not an independently verified physical claim. Legacy plans
without scope retain the blanket dependency. P5 always requires FULL.
Before dependent items are ready, the
checker reopens and regrades the FULL phase receipt, requires base PASS with
zero unknowns, and verifies a binding receipt against the current task subject
and exact receipt bytes. Its physical subject must be the planned native board
or a governed coupon with its qualification receipt and exact planned-board
binding. A recorded child attempt cannot replace this physical prerequisite.
The checker repeats this prerequisite check at P5.

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

## Planning readiness and the native candidate loop

Keep permission to investigate separate from engineering acceptance. P1
establishes exact source ownership, fixed mechanical constraints, applicable
rules, plausible reservations and explicit P2/P3 questions. It does not prove
pad access, simultaneous routing capacity or a filled return. Preserve a
coarse checker's FAIL/INCOMPLETE result; never relabel it PASS to dispatch work.
Classify its cause as a demonstrated planning conflict, a representation
limitation, or an unresolved realization obligation. Use one census of the
affected interfaces when a checker stops at its first refusal.

A bounded, isolated placement/routing experiment may investigate those
questions without promoting the candidate or entering canonical routing.
Use the existing task runtime and route-candidate transaction, exact prepared
rules and native quick/full checks. Name the source snapshot, required nets,
fixed refs, mutable group, decision question and deadline before launching.
Missing inputs or an unbounded mechanical uncertainty do not authorize an
experiment that depends on them. The ordinary P2/P3 dependency graph and
engineering promotion gates retain their authority.

For each coupled group: generate placement and critical copper from source,
grade connectivity and DRC by class, inspect the required filled reference,
then integrate the reviewed source recipe into one current candidate. One
owner writes that candidate. Keep failed experiments and prior accepted
artifacts separate. A quick result only guides the next experiment; full
applicable checks and independent review precede promotion. Logical blocks
need not be rectangular islands, and tightly coupled parts may share a
placement/proof group while retaining their exact modular owners.

For an investigation-only experiment, declare its bounded decision in the
existing findings ledger, then use the existing runner (example deadline):

```bash
python3 skills/kicad-pcb/scripts/pcb_flow.py run PROJECT --stage placement \
  --investigation FINDING_ID --budget-s 900 --timeout-s 900 -- \
  python3 SOURCE_RECIPE --output FRESH_CANDIDATE_DIRECTORY
```

The runner applies source admission before reserving an investigation attempt.
The recipe must refuse an existing output directory and bind the prepared
board and rule bytes. Assess the reserved launch in the same ledger before
another attempt; failed dispatch still consumes a reservation if one was made.
This command is bounded execution, not a TaskAttempt completion receipt or an
output sandbox. It cannot satisfy unmet modular dependencies. Use normal
task delivery for admitted P2/P3 work and full native grading for acceptance.

Use the existing findings investigation and D-BACK records across all attempts.
Count a resolved engineering decision or native proof as progress; a new
checker, report, source hash or worker does not reset the same question's
attempt budget. Report required connections, DRC classes, filled-return proof
and unresolved external dependencies on the current candidate. Add a checker
only when a named acceptance decision lacks an adequate existing check.

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
