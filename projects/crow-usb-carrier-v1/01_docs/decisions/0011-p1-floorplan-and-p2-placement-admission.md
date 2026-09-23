---
id: 0011
date: 2026-09-23
status: accepted
---
# 0011 — Separate P1 floorplan proof from P2 local placement

## Context

Crow's modular plan calls P1 a floorplan task and P2 block placement. The three consumed native P1 attempts showed why that distinction matters: the first board (`637e266594a8b89dc8ce93ed9dc38f2661dc250c8f593fcc2cd2a03c3be44d51`) had real copper shorts; the second (`37b455203fcdae0c20880a94b17a4bcfb61103fa2b8b9df9ecf095c9c97aa519`) had residual native defects; the DLC/USB successor (`b2f59a1b2a8ef91dd1160d6b0074f6a045c4fa0e8d58611bdba98f076acd6fa5`) still had native silk/parity defects and a rough local placement. The source repair now makes all 311 placement budgets measurable, while actual local distances remain mostly unclosed. Those distances are the work of P2 and later integrated placement review, not evidence that every P1 connector/region/corridor allocation is wrong.

Crow's ordinary `03_src/rebuild_all.sh` step [3c] requires connector FULL immediately after board generation and before its placement-approval and routing steps. The base connector contract still has 19 physical unknown targets. The 2026-09-23 one-successor admission and reassessment barred P2 after the failed successor and held placement promotion on FULL. The generic modular procedure permits bounded P2 block work after a sound P1 floorplan, but neither task delivery nor a generated board constitutes acceptance. This decision is **prospective only**: it does not accept any consumed board, reset an attempt, or override step [3c].

## Options

- **Keep P1 and P2 coupled to connector FULL and every local-placement budget.** This preserves the strongest early stop, but makes the P1 floorplan task require the P2 local repositioning it is supposed to enable. A P1 coupon tested before P2 may also need requalification after neighboring parts move.
- **Separate P1 floorplan acceptance from P2 local placement, with a hard connector FULL bar before P3 or any routing and before integrated placement promotion.** This is the selected choice. It allows bounded isolated placement iterations and physical fit preparation while retaining every release and routing gate.
- **Use the unqualified-prototype adapter.** Not selected. Crow has no accepted project ADR admitting that path, and even if separately accepted it would be first-article-only/do-not-order rather than connector FULL or production release.
- **Waive, rename away, or weaken adjacency or physical connector targets.** Rejected. It would erase actual electrical/physical questions without solving the board.

## Decision

Define P1 engineering acceptance only for a fresh, hash-bound native candidate's fixed connector and hold-bank anchors, board outline and regions, service-facing axes, reserved corridors and capacity, source-to-native pin/net parity, no shorts or other P1-class native clearance/hole/library defects, and fitted-body/courtyard/model coverage. P1 must identify P2-owned local placements and their measured failures, not mark them passed. The seven P2 scopes may then run as **bounded, isolated, non-promoted** block-placement work on that accepted P1 floorplan even if connector FULL remains `INCOMPLETE`. P2 must close applicable `P-ADJ`/`P-ADJ-PAIR` budgets and regrade all altered clearance, geometry, connector-neighbor, and corridor evidence. P5 owns integrated whole-placement review; P1 proof is never P5 approval.

Keep all 19 connector targets, base `PASS` and zero unknowns as the FULL predicate. Require FULL on the exact relevant board or separately governed coupon **before any P3 critical-local-route proof, route preparation/import/other routing, P5 integrated placement promotion, release, or order**. Evidence from a P1 coupon must be reopened or repeated if P2 changes the connector-neighbor/service geometry it represents. The current canonical driver still hard-stops at [3c]; this decision authorizes only separately bounded isolated P1/P2 candidate work, with no accepted board pointer or claim that `rebuild_all.sh` can run past FULL. Any future wish to run P2 inside that driver requires an independently reviewed minimal order change placing the unchanged FULL gate after P2 and before P3/any routing and promotion. This ADR does **not** implement or authorize such a driver edit.

This decision supersedes the **prospective P2 sequencing implication only** of the 2026-09-23 one-successor admission and P1 reassessment. Their three failed board verdicts, consumed attempts, exact hashes, no-auto-retry rule, FULL physical obligations, and do-not-order status remain authoritative. Before any new P1 candidate, require an explicit fresh campaign reassessment, source/library and schematic acceptance, subject/hash freeze, and a newly bounded attempt; do not enlarge or reset old work-item allowances.

## Consequences

The current board `b2f59a1b…` remains defective and cannot be used as an accepted P1 base. A new native P1 proof may be attempted only under a separate bounded campaign decision. The accepted-CJ/schematic source, current part/library repair, connector axes, P1 native DRC/parity/model/hold-bank evidence, P2 local gaps, and physical connector targets all stay separately graded. Bounded P2 outputs are diagnostic until the owning engineering and connector gates pass; `WORK_RECORDED` supplies no geometry credit. Routing, full placement promotion and release remain blocked on connector FULL and the ordinary later gates. No lifecycle stage, waiver, release exception, or new gate implementation is created by this decision.
