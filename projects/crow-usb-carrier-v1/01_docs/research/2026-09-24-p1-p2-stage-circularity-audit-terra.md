# P1/P2 circularity audit and safe stage-contract revision

## Finding

A real prospective circularity exists between the P1 source contract/checker
shape and the accepted P1/P2 boundary in ADR 0011.

ADR 0011 deliberately permits bounded P2 placement after a sound P1
floorplan. P1 is to establish fixed connector and hold-bank anchors, outline,
regions, service axes, reserved corridors/capacity, source-to-native parity,
and P1-class native defects. It must report P2 local failures without requiring
their closure. P2 then owns local adjacency and changed-neighborhood rechecks;
P3 owns critical local copper; P4 owns coupled geometry; P5 joins the
evidence before placement promotion.

The current P1 requirements instead require
`exact_ref_pad_net_pockets: required`. The schema-1 capacity checker makes
that an all-terminal route-adjacent predicate: each allocation's
`coverage_members` must equal the exact endpoint-pocket identities, its
pocket net set must equal all allocation coverage nets, and every covered net
requires at least two pockets. Each pocket must contain its full endpoint
footprint and touch the proposed lane. For Crow's multi-owner interfaces, that
forces stable local positions, local package escapes and connector-neighbor
geometry before P2 has placed the affected blocks. The proposed graph checker
has the same issue: it requires every source terminal to be reachable in the
declared graph. Those are P2/P3 facts, not coarse P1 facts.

Thus a future demand for all exact pockets, zero local blockers, or
all-terminal reachability as a P1 entrance condition would create:

```text
P1 exact pockets / local escape proof -> P2 local placement
P2 local placement                    -> accepted P1
```

The current plan's ordinary dependency graph is acyclic: one P1 item precedes
seven P2 items, P3 items depend on their relevant P2 items, P4 joins P3, and
P5 depends on all P4 items. The cycle is in the proposed P1 evidence
denominator, not in `modular_plan.json`'s `depends_on` edges.

There is also an enforcement gap for isolated work. ADR 0011 and
`03_src/rebuild_all.sh` [3c] require base CONNECTOR-FULL PASS with zero
unknowns before P3, any routing, P5 promotion, release, or order. The graph
does not encode that external receipt as a P3 prerequisite, so a manually
dispatched P3 task could otherwise be structurally ready after P2. The
ordinary driver remains safe because it stops at [3c]; the isolated modular
dispatcher needs the same hard admission check before a P3 task is issued.

## Recommended contract boundary

Keep the final gates unchanged. Split P1 evidence into coarse floorplan
admission and deferred local-route proof.

| Scope | Required proof | Explicitly not proved |
|---|---|---|
| P1 coarse floorplan | Hash-bound source/native parity; fixed connector, board-edge, hold-bank and mechanical anchors; region/keepout ownership; named corridor/reservation envelope; boundary witness pads at the source-cell faces; nonzero demand and no board-scale lane/outline/rule-area conflict; P1-class native DRC/library/model/courtyard checks. Signal reservations record the required GND reference *allocation* and whether native fill evidence is absent. | Every endpoint pad, local decoupler, package escape, local return, current/thermal copper, full filled-plane continuity, route legality, impedance, CONNECTOR-FULL. |
| P2 block placement | Full endpoint placement inside its owned cell; local P-ADJ/P-ADJ-PAIR and physical-clearance rechecks; connector-neighbor/service geometry affected by moves; exact transition from local cell to the P1 boundary witness. Changes that invalidate an envelope backtrack to P1. | Critical copper performance or a whole shared-net route. |
| P3 critical local routes | Exact pad pockets, local escape/neck geometry, native DRC and filled GND/return proof for selected critical paths; current/thermal/EMI and Kelvin claims only where their owning existing contract supplies a criterion. | Coupled coexistence outside the task's named neighborhood or full-board placement approval. |
| P4 joint proof | Actual coexisting shared-corridor/coupled-loop geometry, cross-block returns and complete endpoint-scoped proof where a shared net needs it. A boundary or return conflict can backtrack to P1; a local escape conflict backtracks to its P2 owner. | Whole-board promotion. |
| P5 / release | Join all P3/P4 evidence, rerun whole-placement and connector-neighbor checks, then ordinary release gates. | Nothing is waived. |

P1's contract should name one or more `boundary_witnesses` per net at each
cross-block cell face, rather than pretending the floorplan owns every local
terminal. A witness records `ref.pad`, net, owning block, and a source
reservation boundary/entry bbox. A P1 capacity screen can require that the
witness is on the correct native net/layer and that the envelope remains inside
the outline and outside a rule area; it should return `INCOMPLETE`, not a
route or acceptance result. A later P2/P3 record binds the complete
`modular_plan.json` endpoint set and connects each local endpoint to its
witness. This keeps the existing exact 59-net ownership union while avoiding
a false all-terminal P1 denominator.

For edge connectors, retain the separate named mouth/overhang registration
model. Do not relax ordinary footprint containment merely to make a USB
connector fit a generic endpoint pocket.

## Precise implementation proposal

No source change is made by this audit. A reviewed follow-up should change
these files together:

1. `projects/crow-usb-carrier-v1/03_src/rules/p1_corridor_requirements.yaml`:
   replace the global `exact_ref_pad_net_pockets: required` receipt term with
   `coarse_boundary_witnesses: required` and
   `exact_ref_pad_net_pockets: P3_required`. Add a per-allocation
   `coarse_geometry` object containing boundary witnesses, reservation bboxes,
   demand, and an explicit `local_endpoint_completion: P2_P3_REQUIRED`.
   Preserve every complete modular endpoint list as the authoritative
   denominator; do not delete it or mark a P1 coarse result accepted.

2. `skills/kicad-pcb/scripts/p1_corridor_capacity.py`: keep schema-1
   behavior as diagnostic history. Add a separately named schema-2 coarse P1
   profile that validates only its declared boundary witnesses and reservation
   bboxes. It must not reuse `coverage_members == endpoint_pockets` or
   all-terminal reachability for this profile. It must remain
   `routing_realized: false`, `p1_accepted: false`, and INCOMPLETE whenever
   filled-reference, effective geometry, or a required independent review is
   absent. Add red fixtures for a missing witness, wrong pad/net, off-outline
   envelope, rule-area overlap, and an attempted all-terminal/P2-local
   requirement.

3. `projects/crow-usb-carrier-v1/03_src/modular_plan.json` and
   `skills/pcb-design/scripts/modular_design.py`: add an explicit,
   hash-bound external prerequisite for each P3 item,
   `connector_full_receipt`, requiring the base FULL receipt to be PASS,
   zero unknowns, and bound to the relevant board or governed coupon. The
   dispatcher must reject P3 issuance without it. P4/P5 inherit the bar
   transitively; P5 should independently recheck it after connector-neighbor
   changes. Do not model CONNECTOR-FULL as a completed P1/P2 work item or
   accept `WORK_RECORDED` as a substitute.

4. `tests/t1_modular_design.py` plus a Crow-specific source test:
   prove P2 is ready after a coarse P1 result even with local P2 debt, prove
   P3 remains blocked without a valid exact-board FULL receipt, prove an
   invalidated P2 boundary witness targets P1 through D-BACK, and prove P5
   remains blocked on all P3/P4 and FULL evidence.

5. `projects/crow-usb-carrier-v1/01_docs/decisions/0011-p1-floorplan-and-p2-placement-admission.md`:
   append a narrowly scoped amendment that adopts the coarse-witness/P2-local
   split and the P3 dispatch enforcement. It must repeat that the current
   `rebuild_all.sh` [3c] ordering remains unchanged and that no existing
   P1/P2 attempt is reopened, reset, dispatched, or accepted.

The existing backtrack taxonomy already supports this result: a local escape
returns to P2, a boundary/coupled loop to P4 then P1, and board-wide congestion
or return conflict to P1. CONNECTOR-FULL prevents those isolated placement
results from turning into routing, P5 promotion, release, or order authority.

