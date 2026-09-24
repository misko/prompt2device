# Crow P1 launch-abort owner reassessment

**Owner:** `placement-and-process`
**Decision:** positive replacement preparation; **admission status:** pending fresh
independent review.

## Consumed terminal attempt retained as history

The sole attempt of retired work item `p1_floorplan_r4_r3_plan_rebind` is
terminal, consumed, and non-retryable. Its primary durable record is the
verbatim tracked copy
`01_docs/research/2026-09-24-p1-launch-abort-evidence/attempt.json`
(SHA-256 `382f8798074233eef808f79fc868f155fa31972fde956c23cd6f645b6af99314`);
its original local runtime path remains supplemental provenance at
`06_build/task_runs/crow-45-569-p1-one-attempt-terra-a7b5e6b970ce440e862f123b2a2d214f/attempt.json`.
It records run `crow-45-569-p1-one-attempt-terra`, status `FAIL`, return code
`-15` (`SIGTERM`), no completion, zero outputs, and a read-only writer scope
whose before and after tree hashes are equal with `changed_paths: []`.

The bound schema-2 envelope's primary durable record is the verbatim tracked
copy `01_docs/research/2026-09-24-p1-launch-abort-evidence/envelope.json`
(file SHA-256 `01f5d608494cfd4c596c3fecbb422bc2bfa5199d225e994293d8edacc9c6b6d2`; the
original local runtime path remains supplemental provenance at
`06_build/task_runs/crow-45-569-p1-one-attempt-terra-a7b5e6b970ce440e862f123b2a2d214f/envelope.json`; the attempt's bound envelope digest is
`f004b21dce254ef29e7550b5e4f5805b9e95f50a33967e876971e78a00e42cd9`).
`01_docs/research/2026-09-24-p1-launch-abort-evidence/README.md` and
`SHA256SUMS` declare the copies historical and verify their byte identity.
There is no candidate PCB, measurement, evidence archive, or project change
from that attempt.  Those facts do not make the bounded attempt unspent.
Its envelope's `replacement_limit: 0` and `max_nonimproving_attempts: 1`
remain intact.  This decision neither edits that envelope nor changes prior
attempt history or allowance.

## Cause and replacement basis

The failure was a launch/preflight process defect: the worker was terminated
before it produced the required candidate handback, rather than returning a
board-level engineering result.  The empty log and output set do not identify a
source, library, schematic, floorplan, routing, or board defect.  They also do
not authorize a retry.  The process defect is therefore recorded as the cause
for a new governed campaign subject, while the terminal attempt remains
consumed.

ADR 0011 requires this fresh campaign reassessment, a separately bounded
attempt, accepted source/library and schematic inputs, and a hash freeze before
native work.  The pause state at commit `02f49262fbb8414ca23567e1a31b83c656c0e8de`
already directs preparation and independent admission of one fresh P1
source/native campaign.  This is the authority for this bounded replacement,
not an allowance reset.

## Replacement subject and graph decision

Retire the active graph identity `p1_floorplan_r4_r3_plan_rebind` from future
dispatch while retaining its task and attempt records above as history.  The
sole active P1 root is now `p1_floorplan_569_after_launch_abort`, with
`max_attempts: 1` and evidence target
`06_build/evidence/modular_work/p1_floorplan_569_after_launch_abort.json`.
It is a distinct campaign subject:
`crow-usb-carrier-v1/p1/569-after-launch-abort/v1`, not a continuation of the
old envelope or its native-board subject.

On admission, the scheduler must allocate a new schema-2 envelope whose
`task_id` is `p1_floorplan_569_after_launch_abort`, whose subject hashes bind
the clean replacement commit and accepted packet, and whose native-board
subject is a newly generated saved board at
`06_build/p1_floorplan_569_after_launch_abort/crow_carrier.kicad_pcb`.
That path is a declared future output, not an existing board.  The envelope
must have one attempt and no implicit replacement or repair allowance.  Any
termination, missing handback, or engineering failure consumes that one new
attempt and returns to `placement-and-process`.

All seven P2 items now depend on and backtrack to this sole P1 root.  The
remaining P4 backtrack reference is updated as well, so no active graph edge
names the retired root.  P3 remains downstream of P2 and blocked by connector
FULL.

## Scope and admission predicate

This owner decision permits only the P1 floorplan campaign: anchors, outline,
regions, service axes, reserved corridors/capacity, source-to-native parity,
P1-class native DRC, and body/courtyard/model coverage.  It does not admit P2,
P3, routing, promotion, release, or ordering.  Connector FULL remains base
`PASS`, zero unknowns, and all 19 physical targets before P3, routing, P5,
release, or order.

Before dispatch, an independent reviewer must verify this decision; the old
attempt preservation; exactly one P1 graph node; all rewritten P2 and other
graph references; and one frozen clean commit descended from `02f49262`.
That packet must bind the authenticated checkpoint
`06_build/checkpoints/schematic.json`
`917a45414c65cf43dbeef24704da01beda6b9711175cf9cec3af109ec027f4d6`, accepted
Circuit JSON, schematic, netlist, modular plan, floorplan, route/nets/
connector contracts, relevant parts/footprints/models, tool versions, and the
upstream source/library, canonical-schematic, E-FAULT, connector-composition,
and review receipts.  The untracked `03_tscircuit/dist/` directory is excluded
from that packet and must not be present in the clean-tree admission result.

The exact planned next admission is: independently review this replacement
record and the clean frozen commit, issue a PASS/SOUND receipt bound to the new
schema-2 envelope subject, then dispatch exactly one isolated native P1 run.
