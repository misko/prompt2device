# Modular PCB design: implementation plan

Status: proposed; no design, skill, gate or execution authority is changed by this document.

## Objective

Make functional decomposition a repeatable part of PCB design: discover useful
blocks, establish their interfaces, prove tightly coupled geometry together,
and integrate the complete board. The method must work across different board
types. Crow supplies regression evidence, not a template every board must fit.

Success means fewer unsuccessful routing attempts, smaller repair scopes and
clearer handoffs without weakening electrical, manufacturing or release checks.

## Design principles

1. **Derive structure from the design.** Use requirements, actual connectivity,
   part layout guidance and mechanical constraints. Schematic sheets suggest
   boundaries; they do not determine them.
2. **Assign one owner per component.** Integration groups may overlap in their
   checks, but never create competing component or routing ownership.
3. **Keep interfaces physical as well as electrical.** Include entry/exit
   regions, reference planes, current/thermal needs and routing restrictions.
4. **Solve coupled geometry together.** A feedback loop, constrained escape or
   shared corridor can require a joint placement task across functional blocks.
5. **Keep facts in their existing authorities.** Reference dossiers, electrical
   rules, floorplan and route configuration rather than copying their limits.
6. **Use the existing lifecycle.** Block work sits within architecture,
   placement and routing; it is not another release pipeline.
7. **Scale ceremony to risk.** A simple board may have a few coarse groups and
   no special local routing experiments.
8. **Acceptance has a scope.** Local success does not establish global
   routability, electrical performance or release readiness.

## Existing foundations and the missing seam

| Existing owner/tool | Retain and build on | Missing behavior to establish |
|---|---|---|
| `pcb-design` architecture and lifecycle | Fact locks, bounded work, backtracking, stage evidence | A consistent method for proposing and challenging decomposition |
| `kicad-pcb` placement | Proximity, functional cells, escapes, reservations, replica checks | Translate block intent into physical work scopes |
| Coupled-geometry checks | Independently graded combined copper witnesses | Select which neighborhoods need such proof and when |
| Route ownership/candidates | Unique routing authority and reproducible candidate transactions | Carry accepted local work into canonical routing without double ownership |
| Checkpoint framework | Saved context, bounded solver execution, independent graders | Diverse decomposition and integration regression cases |

Functional-cell shadow checks remain shadow until their existing promotion
requirements pass. A new block plan cannot promote them implicitly. Similarly,
checkpoint success grants no production gate reuse permission.

## Proposed design loop

```text
requirements + schematic + part facts + mechanical constraints
    -> propose blocks and interfaces
    -> challenge boundaries and identify coupled groups
    -> floorplan and rank unresolved physical risks
    -> prove hardest local/boundary geometry
    -> complete blocks and integrate
    -> whole-board verification

failed proof -> classify cause -> revise local geometry, grouping,
               floorplan, part selection or architecture -> recheck
```

### 1. Discover candidate blocks

The agent identifies functions, local feedback/reference/decoupling
relationships, repeated circuits and fixed mechanical features. Scripts derive
connectivity and check membership coverage. Power and ground connectivity must
not automatically merge the entire board into one block.

Output: a compact block map with component membership, boundary nets, source
references, physical assumptions and reasons for each boundary. Shared power,
ground references, thermal structures and mechanical restrictions remain
explicit board-level responsibilities.

Check the map independently against the current component census and observed
net/pad connectivity. Every component must have exactly one owner; every
cross-block connection must have an interface disposition naming its endpoints
and owning requirements. Give shared board-level responsibilities named owners
as well. Reject missing or duplicate membership and omitted crossings. A table
plus a connectivity extractor is sufficient initially; this does not require a
new block schema or promote an authored declaration into observed evidence.

Do not prescribe a universal list of block types. Regulation, processing,
conversion and communication are examples, not required categories.

### 2. Challenge boundaries

For each candidate boundary, ask:

- Does it cut through a feedback loop or critical current loop?
- Do the two sides compete for the same escape, layer or routing corridor?
- Can one side move without invalidating the other's assumptions?
- Are reference-plane, thermal or interference dependencies visible?
- Does separate management reduce the reasoning burden enough to be useful?

Keep a component's owner singular. Where several blocks constrain each other,
create a joint integration task rather than duplicating ownership. Record why
the group exists and what evidence would allow it to be split again.

### 3. Define minimal interfaces and floorplan

Use one short contract per useful block, initially as ordinary project source
annotations or a table referencing existing authorities:

| Item | Required meaning |
|---|---|
| Identity and membership | Stable name, component references, parent if useful |
| Electrical boundary | Actual boundary nets/pads and owning electrical requirements |
| Physical boundary | Preferred entry/exit regions, area/height envelope, allowed transforms |
| Local restrictions | Critical loops, proximity, assembly side and routing restrictions |
| Shared dependencies | Stackup, return paths, obstacles, thermal copper, neighboring interfaces |
| Completion scope | What local checks and boundary proofs establish acceptance |
| Open assumptions | What remains unresolved and who owns the decision |

Begin with regions, not unnecessarily fixed port coordinates. Refine positions
after floorplan evidence. Avoid treating every block as a sealed rectangle:
some layouts legitimately interleave supporting components or shared copper.

Place connectors, mounts and enclosure interfaces first. Allocate block space
and interconnection corridors together. Rank work by physical constraint,
uncertainty and consequence of failure, rather than schematic order.

### 4. Prove critical geometry before completing routine routing

Use exact footprints, rules, layer restrictions and surrounding obstacles.
Prove local loops and constrained boundary connections with actual geometry.
Reservation boxes alone do not prove routability.

A work item may finish with checked placement and critical paths rather than
all internal nets routed. Complete self-contained routing where useful; leave
flexible routes until interfaces settle. For repeated channels, prove a pilot
then check each instance's transformed surroundings and boundary connections.

Keep three scopes distinct:

| Scope | Claim |
|---|---|
| Block | Its declared local requirements pass under bound assumptions |
| Integration group | Named boundary routes coexist in the actual neighborhood |
| Whole board | All required connectivity, electrical, manufacturing and release checks pass |

These are evidence scopes within existing stages, not three new lifecycle gates.

### 5. Integrate through the existing route authority

Resolve the local-routing handoff before implementing reusable copper. The
current pipeline prepares a deterministic clean routing input and authenticates
route candidates. Local work must fit that model.

Prefer existing source-owned placement, deterministic local routing or accepted
candidate mechanisms. Every retained route needs unique ownership, exact
dependencies and a reproducible path into the final board. Never paste copper
into generated output or assign a complete net to multiple independent routers.

If existing mechanisms cannot represent a required local route, document the
specific gap and extend its owning contract with tests before adopting it.

Resolve partial-net acceptance explicitly in the phase-1 inventory. Current
candidate acceptance requires each declared required net to be connected, and
coupled-neighborhood declarations name whole nets. A locally connected branch
of a shared net is therefore not a whole-net acceptance. Choose and record one
of three treatments: retain it only as diagnostic geometry with no acceptance
claim; expand the integration task to prove the complete net; or implement and
test an endpoint-scoped extension in the owning contract before relying on it.
Omitting the net from required coverage cannot manufacture local acceptance.

### 6. Reconsider grouping when evidence demands it

On failure, record the violated constraint, causal geometry, attempted remedy
and next hypothesis. Classify the cause as local, boundary or board-wide.

Merge a placement task when repeated boundary conflicts show strong coupling;
split a task when independent regions can be solved separately. Preserve the
existing bounded plateau/backtrack policy. A new model, worker or group name
does not reset failed-attempt history.

## Implementation phases

| Phase | Work and deliverable | Exit condition | Suggested execution |
|---|---|---|---|
| 1. Authority inventory | Map proposed behavior to current source, gates and route ownership; resolve partial-net evidence and canonical replay handoffs | Each proposed fact/check has one owner; partial-net treatment is explicit; no duplicate lifecycle | Scripts and a bounded Sol-medium review |
| 2. Procedure pilot | Write a concise decomposition/boundary-review procedure; apply it read-only to a simple board and a constrained board | Useful work scopes emerge without board-specific rules or unnecessary ceremony | Sol medium for judgment; lower-cost worker for extraction |
| 3. Regression cases | Add small checkpoint cases for decomposition, local proof, integration and invalidation | Known-bad state fails, valid repair passes, shortcut fails | Deterministic graders first; bounded lower-cost agent trials |
| 4. Minimum integration | Connect procedure outputs to existing placement/coupled-geometry/route mechanisms | Local work regenerates and integrates without duplicate routing ownership | Bounded implementation tasks, one writer per live board |
| 5. Cross-board validation | Exercise different topology, density and assembly constraints | Results generalize; simple boards retain a short path; no gate weakening | Independent focused review and selected trials |
| 6. Promotion and simplification | Update owning skill references; remove any replaced duplicate instructions | Authority/documentation checks pass and execution behavior is evidenced | Mechanical checks plus final Sol-medium review |

Do not introduce a dedicated block schema during phase 1 merely because it
looks convenient. Add one only if pilots expose a named consumer that cannot
reliably use current source, and define its minimal fields from those examples.
Do not enable automatic selective gate reuse as a side effect of this work.

## Regression strategy

Keep the test framework independent of the board examples. Each case owns its
snapshot, history, objective, permitted edits and independent success criteria.
The existing runner owns restoration, current-skill context, execution bounds
and results. Graders inspect artifacts, not the solver's explanation.

| Case family | Deliberate failure | Required outcome |
|---|---|---|
| Simple sensor | Unnecessary fragmentation and invented prerequisites | Complete a small scope without extra lifecycle machinery |
| Decomposition coverage | A component has duplicate/no ownership, or an actual cross-block connection is omitted | Independent component/net/pad census rejects the omission; valid alternative partitions pass |
| Switching supply | Feedback/current loop split across independent tasks | Recognize coupling and produce compliant local geometry |
| Repeated channels | A copied layout collides with a different neighbor | Check each instance; repair without assuming pilot equivalence |
| Dense digital | Local passives block a constrained pin escape | Revise geometry and demonstrate the permitted route |
| Shared corridor | Two individually valid routes cannot coexist | Fail isolated acceptance; prove a joint solution |
| Partial shared net | A local branch is presented as acceptance of a multi-block net | Keep diagnostic scope explicit or prove all required endpoints through the owning contract; omitted coverage cannot pass |
| Canonical integration | Preparation drops accepted local copper, or a later router claims it again | Canonical regeneration preserves required connectivity, route ownership and applicable geometry constraints; both shortcuts fail |
| Analog measurement | Hidden reference/return dependency crosses a boundary | Expose the dependency and satisfy its owning constraints |
| Reuse invalidation | Changed package, obstacle or stack with old local evidence | Reject stale acceptance and identify affected scope |
| Assembly policy | A local optimization moves a component to a forbidden side | Reject without relaxing the board constraint |

Crow may supply the constrained escape and shared-corridor cases. Other boards
must supply materially different examples. Label reduced synthetic coupons
honestly; they are not full historical board replays.

Before a model trial, demonstrate deterministic RED, valid GREEN and invalid
shortcut RED. For new checker behavior, verify the counterexample exposes the
pre-fix weakness. Allow multiple valid decompositions and solutions: do not
grade exact coordinates, block names, or equality with a reference answer.

For canonical integration, produce local evidence, adopt its source-owned route
through the supported handoff, and regenerate through the canonical conductor.
Independently reopen the resulting board and verify required connectivity,
ownership, inherited-route requirements and applicable geometry checks. Test
both dropped local work and duplicate downstream routing ownership. A passing
coupon or candidate receipt alone does not satisfy this case; assert properties
rather than exact stochastic route bytes.

## Change scope and checkpoints

Checkpoint records should name exact inputs, completed work, boundary
assumptions, unresolved hypotheses and retired attempts with reconsideration
conditions. Use existing handoff and candidate mechanisms.

| Change | Minimum reconsideration |
|---|---|
| Component value | Owning electrical requirements and dependent layout assumptions |
| Footprint or pin map | Local geometry and all affected interfaces |
| Block translation/rotation | Boundary routing, obstacles, return paths and thermal/mechanical context |
| Shared clock or power topology | Relevant integration groups and downstream checks |
| Stackup or manufacturing floor | All dependent geometry and routing evidence |

This table guides diagnosis, not permission to skip gates. During development,
select focused checks through their existing supported interfaces. At final
acceptance, run every required whole-board and release gate.

## Cost and process evaluation

Use scripts for extraction, coverage, geometry grading and replay. Use agents
for boundary choices, physical tradeoffs and causal diagnosis. Begin with
bounded lower-cost trials; use Sol medium where architectural judgment is
needed. No higher-tier model is required by this plan.

Capture per work item: elapsed time, attempts, failure class, affected scope,
checks executed, rework after integration and provider-reported token usage
when available. Mark unavailable usage as unknown. Separate process/setup cost
from engineering solution cost and distinguish model latency from tool time.

Compare the same checkpoint problems and constraints before and after the
procedure. Look for fewer repeated failures and less integration rework without
reduced checking. Include a simple-board case to detect overhead regressions.
Set quantitative targets after observing a baseline rather than inventing
percentage improvements.

## Completion criteria

- A fresh agent can derive and explain a useful decomposition from current
  project artifacts without historical conversation context.
- Components and routing work have unambiguous owners; shared dependencies
  remain visible.
- Critical local and boundary failures are detected before extensive routing.
- Accepted work can be reproduced and integrated through current authorities.
- Known-bad, valid-repair and stale-evidence controls behave as intended across
  multiple board types.
- The simple-board path stays simple; no mandatory framework migration blocks
  ordinary design work.
- Applicable skill authority, documentation and focused test suites pass.
- No local result weakens final board, assembly, release or physical evidence
  requirements.

## Existing references

- [PCB lifecycle skill](skills/pcb-design/SKILL.md)
- [Placement and functional cells](skills/kicad-pcb/references/placement-and-proximity.md)
- [Route ownership](skills/kicad-pcb/references/route-ownership.md)
- [Route candidate contract](skills/kicad-pcb/references/route-candidate-contract.md)
- [Layout precedents](skills/kicad-pcb/references/layout-precedents.md)
- [Backtracking and handoffs](skills/pcb-design/references/lifecycle-and-backtrack.md)
- [Checkpoint regression framework](tests/checkpoints/README.md)
- [Prior PCB process test plan](update_and_test_pcb_design.md)
- [Crow carrier process replay](projects/crow-audio-carrier-v1/01_docs/reports/2026-09-21-modular-process-replay.md)
  — historical failure sequence and proposed pseudocode; not an executed replay.

Recommended first action after approval: run the phase-1 authority inventory
and two read-only decomposition pilots. Let their concrete results determine
the smallest necessary procedure and implementation changes.
