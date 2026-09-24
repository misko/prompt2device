# Crow P1 native-evidence failure owner reassessment

**Owner:** `placement-and-process`
**Decision:** preserve the terminal native attempt as consumed and prepare one
distinct, independently admitted P1 campaign.

`p1_floorplan_569_after_relative_path_abort` spent its sole attempt in
`p1_floorplan_569_after_relative_path_abort_r1`. Its primary durable evidence
is the tracked archive
`01_docs/research/2026-09-24-p1-native-evidence-failure-evidence/`; the
ignored task-run path is retained in that archive's README as supplemental
provenance. The immutable receipt is terminal `FAIL`, return code `1`, with a
failed `candidate-measured` delivery and no source/project change. Its envelope
retains `max_nonimproving_attempts: 1`, `replacement_limit: 0`, and no repair
allowance. This is consumed, non-retryable history; no old budget or record is
edited.

The delivered candidate board and evidence-board bytes are consistently
`6d948f70f31c1b54dd75d53f5699c8b8fdc61ddf79d0451c3173190ea5b5ccfa`, but
the placement routability receipt embeds
`979287bfbc2d2719d2cbd0bdf945a44084ab1e81b5e5ecabab4220e4b629b4c4`.
That mixed-SHA placement/capacity receipt is preserved but non-creditable. The
terminal result remains a failure even though its source counts, P1 geometry,
model coverage, pad separation, and native DRC observations are diagnostically
useful. The 499 unconnected items remain unrouted P1 evidence, not route
credit.

The worker also incorrectly converted `P-ADJ-PAIR` local placement debt into a
failed P1 delivery. Under ADR 0011 that debt remains explicitly P2-owned and
unwaived. Separately, the receipt declares zero corridors and zero net owners;
its route-ownership PASS is incomplete and provides no P1 corridor credit.
The corridor/ownership registry needs a separately owned source change and is
not changed by this reassessment.

Retire `p1_floorplan_569_after_relative_path_abort` from future dispatch. The
sole active P1 root is `p1_floorplan_569_after_native_evidence_abort`, with
`max_attempts: 1` and evidence target
`06_build/evidence/modular_work/p1_floorplan_569_after_native_evidence_abort.json`.
It is a distinct schema-2 subject, not a rerun. Before dispatch, its fresh
admission must bind a clean frozen packet and require: exact candidate board
hashes embedded in every checker receipt; mismatches or missing hashes to fail;
nonzero explicit corridor/ownership denominators; and P-ADJ/P-ADJ-PAIR reported
as P2 debt rather than a P1 delivery PASS or waiver.

All seven P2 dependencies/backtracks and the P4 power-return backtrack now
target the new root. Scope remains P1 only. Connector FULL stays base PASS,
zero unknowns, and all 19 physical targets before P3, routing, P5 promotion,
release, or order. No current board is accepted and no routing is authorized.
