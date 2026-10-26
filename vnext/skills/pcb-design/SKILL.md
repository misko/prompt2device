---
name: pcb-design
description: Develop PCB designs from a brief through whole-system schematic drafts, independent review and acceptance. Supports bounded independent architecture exploration and evidence-led redesign. Manufacturing acceptance remains separate from drafting.
---

# PCB design — draft first, accept explicitly

This skill defines PCB deliverables and engineering acceptance. The sibling
[orchestrator](../workflow-orchestrator/SKILL.md) owns execution and recovery.
Use this local vNext package, not legacy conductors or inherited board choices.
Board topology, functions, quantities, supply limits and deployment environment
come from the current project's brief and reviewed design, never a previous
board or regression fixture. Load specialist procedures only when applicable.

## Choose the route

- New design or architecture exploration: read [whole-system drafting](workflow/stages/exploration.md).
  Start from the user's prompt and decisions. Produce a concrete candidate in
  the first bounded design pass; do not require accepted architecture or a
  locked BOM merely to draw it. Multiple independent drafts are optional unless
  requested. They converge on one repair baseline, not parallel endless repairs.
- Existing accepted project: preserve its binding and artifacts. Do not silently
  reinterpret an old receipt or continue a paused run. Explore alternatives in
  an isolated candidate directory, with explicit migration before adoption.
- Acceptance: use the existing [architecture](workflow/stages/architecture.md),
  [sourcing](workflow/stages/sourcing.md) and [schematic](workflow/stages/schematic.md)
  contracts. Draft existence, candidate selection and acceptance are distinct.
  After the schematic checkpoint is explicitly resumed, use
  [placement](workflow/stages/placement.md) for complete alternative placements,
  one refinement baseline and independent acceptance. After placement reflection,
  [routing](workflow/stages/routing.md) defines the next phase and its backtrack
  destinations; [mating clearance](workflow/stages/mating-clearance.md) defines
  the prerequisite applicability check. Their native-source build/verify and
  independent-review receipt adapter is a local pilot; explicitly adopt its
  [tooling](procedures/routing/tooling.md) before running that phase. It is not an
  autorouter, automatic scheduler or manufacturing approval.
  After routing reflection, [layout seal](workflow/stages/layout-seal.md) owns
  finishing, strict final checks and inherited engineering closure. Its local
  [adapter](procedures/layout-seal/tooling.md) preserves routed acceptance while
  reviewing cosmetic-only changes; engineering changes backtrack to their owner.
  After layout reflection, [fabrication](workflow/stages/fabrication.md),
  [assembly verification](workflow/stages/assembly-verify.md),
  [release review](workflow/stages/release-review.md) and
  [release seal](workflow/stages/release-seal.md) define the remaining contracts.
  Fabrication has an explicitly adopted local integration/review pilot through
  [staging tooling](procedures/fabrication/tooling.md); it does not authorize orders.
  Mating and assembly now require [registered 3D evidence](procedures/mechanical/3d-verification.md).
  The assembly [adapter](procedures/fabrication/assembly-tooling.md) requires
  explicit version2 adoption for new registered-3D admission. Historical
  envelope/contact receipts do not establish the upgraded route.
  Release review
  has a standalone archive/replay and independent admission
  [pilot](procedures/release/tooling.md); immutable release seal has an isolated
  local Git/source-provenance [pilot](procedures/release/seal-tooling.md).
  Component exports alone are not fabrication or assembly acceptance.
  RF and hierarchical acceptance remain unsupported locally. Existing accepted
  projects retain their exact upstream toolchain through explicit versioned
  adoption; do not refresh historical receipt identities silently.

## Design posture

Prefer the simplest understandable complete system, considering hardware,
firmware, sourcing and qualification together. Preserve requirements; expose
tradeoffs and assumptions rather than silently lowering capability. Use actual
manufacturer pin facts and reference schematics for critical circuits. Never
invent a verified pinout or count a functional placeholder as implemented.

Early screening focuses on architecture-defining parts and dangerous or
topology-changing interfaces. Draw the complete signal/power path while exposing
open questions. A known contradiction may be visible in an unaccepted draft,
but cannot be deferred as a test plan at acceptance. Physical qualification is
separate from design verification; ERC alone proves neither.

Keep common resistors and capacitors generic during schematic development:
specify value, tolerance, ratings, technology and package; choose exact stocked
MPNs together at the final BOM/sourcing check before schematic acceptance.
Check feasibility-critical electrical properties when the circuit needs them;
ordinary passive inventory must not interrupt drafting or repair. See
[passive timing](procedures/part-recheck.md#common-passives-design-now-source-at-the-end).

Use [part recheck](procedures/part-recheck.md) when supply evidence is due: JLCPCB first,
then a short Western fallback. An exact in-stock statement suffices when no
insufficient quantity is published. Ask the user if an adequate source cannot
readily be found, presenting ranked recommendations. Provisional parts may be
drawn under the exploration contract; they may not receive sourcing acceptance.

## Load detail only when needed

Use [power](procedures/commission/power-design.md),
[channel](procedures/commission/channel-design.md) or
[interface](procedures/commission/integration-design.md) guidance for a named
review finding. Their historical commissioning wrappers are not prerequisites
for the new exploration route. Retain technical safeguards and fact/assumption
distinctions. Avoid one research/review cycle per ordinary component.

Maintain one source of circuit truth. Export PDF, netlist and ERC from the actual
native schematic. Preserve original requirements, candidate revisions, findings
and failed approaches. Stop at the user's requested phase checkpoint.
