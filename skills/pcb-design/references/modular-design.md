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
5. Single-candidate operator workflow
6. Backtrack and evidence boundaries
7. Bounded integration research adapter

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

Before committing to those constraints, run the controlled-pair footprint/rule
screen described in [layout precedents](../../kicad-pcb/references/layout-precedents.md)
on a native interface fixture or existing board. Do not wait for all blocks to
be placed to discover an incompatible trace width or pair-clearance scope.
This early screen does not require a full-board placement receipt or routed
witness; it also grants neither P1 admission nor route authority.

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

Functional ownership, planning bounds and exclusive proof geometry are separate.
Do not opt a whole functional owner into `physical_cells` merely to make its
planning rectangle contain a remote endpoint. Use cells only when the intended
acceptance claim relies on exclusive space; then keep their full declared-owner
coverage and native occupancy checks. Existing strict cell failures cannot be
silenced by relabeling an exclusive allocation as a planning region.

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

## Evidence scheduling

Before launching work, name the engineering question, its existing acceptance
consumer, and which next action each possible result changes. Use the current
findings ledger and candidate record; do not create a second status registry.

| Evidence | Needed to proceed | Deferred work |
|---|---|---|
| Critical IC/interface feasibility | Before committing the stack and full placement: exact pads, escape envelope, generated width/clearance/via rules, reference-plane plan and applicable precedent | Realized route, SI and physical qualification |
| P1 engineering admission | Independent exact-subject review of anchors, outlines, ownership, usable corridor capacity, native parity/clearance and model coverage | P2 local distances and P3 realized copper/return |
| P2/P3 design work | Applicable engineering dependencies plus a bounded candidate/write scope; raw diagnostics never grant admission | Physical observations that require an article, when the project's explicit research authority permits deferral |
| Physical connector/ESD qualification | At its stated qualification/release boundary, with a reviewed article and measurement plan | Never replace observations with CAD, a nominal impedance result or a checker PASS |

The schema-2 P1 coarse screen deliberately emits only FAIL or INCOMPLETE and
`p1_accepted: false`. Review its concrete conflicts and capacity gaps; do not
turn its fixed status into a regeneration loop or mistake absence of conflicts
for engineering approval. An independent P1 review can carry explicit P2/P3
debt forward only after the actual P1 obligations are proved.

Before commissioning a separate mechanical coupon, compare its represented
connector/neighbor field and retest risk with a routed engineering article.
Include only omissions/dummies justified by service-envelope evidence; neither
an empty connector strip nor all-board population is an automatic requirement.
A combined article may serve connector and electrical qualification if its
sample count, nondestructive-before-destructive test order and failure criteria
are reviewed. Preparation, fabrication authorization and qualification are
separate decisions. Existing release/order gates remain binding.

A project may explicitly authorize bounded private design investigation before
physical FULL. That authorization must retain the real P1/P2 prerequisites,
freeze relevant mechanical assumptions, and specify nets, layers, mutable
objects, stop criteria and independent review. It does not remove `connector_full`
from ordinary P3/P5 dependencies, promote a prototype, or authorize fabrication.
It is not an ordinary P3 dispatch or route/promotion receipt. If the executable
path cannot enforce those bounds, keep dispatch blocked and state the missing
admission; prose alone is not an executable route permit.

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
Also name the milestone's acceptance consumer: an existing engineering gate or
independent review with explicit closure criteria. Coarse P1 `INCOMPLETE` and
modular `WORK_RECORDED` do not close that engineering milestone.
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

Use the single-candidate workflow below to evaluate and adopt an integrated
change. Changes to rules, exception authority or safety-critical claims still
need their own applicable independent review before use.

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

## Single-candidate operator workflow

The existing integration spec/input packet and its resulting research receipt
identify a candidate; the findings ledger owns outstanding work. `pause_state`
owns the resume checkpoint and generated status views. These are distinct
responsibilities, not competing copies of a board's acceptance status. Keep one
active candidate in the existing handoff; historical receipts remain immutable
evidence, not additional live revisions.

| Operator step | Existing mechanism | Required outcome |
|---|---|---|
| Prepare | Exact source/input packet and bounded producer | One board, its effective rules and its owning source; no mixed-revision inputs |
| Evaluate | Existing native/P1/modular checks composed in the candidate diagnostic | Full raw findings, grouped primary causes and explicit unevaluated checks |
| Repair | Source recipe plus existing decision-progress budget | Measurable improvement to the same engineering question; preserve the prior accepted state |
| Adopt | Owning project conductor and applicable independent reviews | Reopen the exact candidate bytes and satisfy the existing admission predicates |
| Release | Existing staging, review, seal and publication procedure | Self-contained archive and the separate release/order verdicts |

Keep intent and measurement separate. Owners, required net terminals, region
constraints, fixed refs, exceptions and return duties are source declarations.
Native pad bboxes, pad/net/layer census and placement poses are measurements.
Regenerate measurements after source changes; never enlarge an owner region,
invent a terminal or rewrite a reviewed hash to make the measurement pass.
Proposed measurements must remain visibly unreviewed until the owning review
accepts their exact subject.

Group known consequential findings under the primary failure while retaining
the raw checker result. For example, missing per-net witnesses can prevent an
allocation from accounting for otherwise valid branches. Do not create one
repair task per consequential error. Unknown errors retain their independent
visibility; grouping is not proof that they are harmless.

For checker-only corrections, keep board/source/sidecar identities fixed and
run only the affected checks with a separately reviewed checker digest. Record
the new result alongside the original result; preserve historical failed
receipts and consumed attempt budgets. A changed checker does not confer
previously absent P1, route or release authority. Regenerate only when relevant
source, geometry, effective rules or generator inputs change. Do not create a
new candidate merely to restate an already measured unchanged board.

Reuse evidence only when its declared input identities still match. A board
or placement change invalidates board-bound geometry, P1 and downstream
route/review evidence. It does not by itself reopen an unchanged initial-stock
selection decision. Changes to part identity, quantity, pin map or footprint
still follow selection admission. Missing dependency declarations mean the
evidence cannot be assumed reusable. Never refresh acceptance from producer
output hashes.

The diagnostic adapter does not promote boards. In particular, the experimental
`route_candidate_workspace.publish_accepted_bundle` remains disabled until its
authoritative regrade requirement is implemented. Use the existing project
conductor's admitted path; if that path refuses, expose the unresolved admission
instead of updating an accepted pointer. A `prototype_only` candidate retains
its scoped research restrictions throughout this workflow.

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

## Bounded integration research adapter

Run `python3 skills/pcb-design/scripts/integration_candidate.py PROJECT SPEC.json`
from the repository. This adapter composes existing investigation accounting,
TaskAttempt execution and the experiment store; it is not an ordinary board
producer or a new engineering acceptance gate.

The schema-1 spec names the existing finding's `decision_id`, a unique
`experiment_id`, an argv `command` invoking the pinned producer, `timeout_s`,
a fresh `output_root` beneath `06_build`, and `next_acceptance_consumer`.
Its `files` mapping supplies exact `{path, sha256}` records for `board`,
`netlist`, `circuit`, `floorplan`, `p1_source`, `p1_contract`, `interfaces`,
`aliases`, `modular_plan`, `pro`, `dru`, `route_config`, `producer`,
`p1_checker` and `modular_checker`; add `edge_authority` when applicable.
Data paths are project-relative; the three tool roles also accept `repo:` paths.
Expected authority hashes come from the caller's reviewed packet, not from
producer assertions. Hash identity alone does not establish independent review.

Selection eligibility, any existing pause record, source admission and the
existing investigation budget are checked before dispatch. Prototype-only
eligibility grants research scope only. It cannot authorize an ordinary
producer, release, fabrication or order. The adapter checks writer-scope changes
but is not a sandbox: use trusted producers and an isolated checkout when
physical protection from unintended writes is required.

The producer writes `candidate_inputs.json` under its output directory, with
observed `{path, sha256}` records for `board`, `p1_source` and `p1_contract`.
The board must be inside that directory. A changed board invalidates the old
P1 contract; the first receipt records this review debt. An independently
reviewed replay can add `expected_candidate`, mapping those same three roles
to their reviewed hashes. Baseline and candidate diagnostics remain separate.
This first slice keeps PRO/DRU, floorplan, interfaces and aliases pinned to the
input packet. Changing them requires preparing a new coherent input packet;
the adapter does not automatically integrate a placement source edit.

Before preparing that packet, inspect stale native-pad witnesses without
launching another producer:

```bash
python3 skills/pcb-design/scripts/integration_candidate.py diagnose-native-witnesses \
  PATH_TO_CANDIDATE.kicad_pcb PATH_TO_OLD_CONTRACT.json
```

This read-only diagnostic returns a proposed contract copy, exact observed
board identity, bbox differences and review debt. Only unresolved-branch
native-pad witnesses are regenerated; region faces, reservations, ownership,
aliases and safety intent require their owning source edits. Missing, duplicate
or wrong-net/layer native pads refuse a proposal. The output is a draft for
review, not an approved contract, and does not refresh the caller's expected
review hashes. Native DRC, routing, source admission and the other domain checks
still run through their existing owners.

P1 diagnostics also expose grouped missing per-net witnesses and attributable
branch-accounting consequences alongside the complete raw result. This changes
the repair queue, never the checker verdict. The Crow
`2026-09-25-ti-current-coupled-replay/diagnose_p1_rebind.py` pilot uses these
shared helpers instead of maintaining its own pad-repair loop.

Assess the reserved launch through the existing investigation protocol before
another producer run. Diagnostic receipts and task PASS never close engineering
milestones or promote the accepted candidate. Failure, timeout and missing
candidate output are retained as rejected attempts. The next named acceptance
consumer owns actual engineering review and the existing downstream gates.

`tests/test_integration_candidate.py` provides executable specs, failure controls
and a read-only Crow d0/e07 mismatch example. The current Crow example refuses
launch under its existing investigation budget; it is not a successful Crow
integration trial.
