# Crow P1 relative-path failure owner reassessment

**Owner:** `placement-and-process`
**Decision:** prepare one distinct, independently admitted P1 replacement;
the failed campaign is terminal and consumed.

`p1_floorplan_569_after_launch_abort` spent its sole attempt in run
`p1_floorplan_569_after_launch_abort_r1`. The tracked primary receipt is
`01_docs/research/2026-09-24-p1-relative-path-failure-evidence/attempt.json`
(SHA-256 `c7e782d07766bf28ff3780603963e33cff4f8dca1b99f6e2b3663f3c73ee1700`),
with the ignored task-run path retained as supplemental provenance. It is
terminal `FAIL`, return code `1`, has no completion or outputs, and is missing
the candidate PCB, evidence archive, measurements, and result handback. Its
read-only writer scope passed with equal source hashes and `changed_paths: []`:
the project source was unchanged and no board exists.

The failure is a relative-path launch defect. The worker was invoked with
`projects/crow-usb-carrier-v1` despite a project-directory CWD, then attempted
to copy the nonexistent nested `projects/crow-usb-carrier-v1/02_parts` path.
It is not a source, schematic, library, floorplan, DRC, routing, or board
finding. It still consumes the bounded attempt and does not permit retry,
replacement-limit editing, or history reset.

The archive preserves the allocated envelope, runtime log, reviewed external
envelope, tool manifest, and formal review. The attempt's
`envelope_sha256` (`b91f803e87ce5c4f15710a5056555071b421ec2c884abda431574bd2042f8308`)
is the conductor canonical digest; it is distinct from the received allocated
envelope file SHA-256 (`a736d05a6471fb76c367be60484242a205c736c85f8c74535caaa150ff1f01fb`)
and from the reviewed external envelope SHA-256
(`43901bc23340bae467b460eb54df13372598a43cd05683c7069fa0693475f25d`).
The archive records those distinct facts without reclassification.

Retire `p1_floorplan_569_after_launch_abort` from future dispatch while
preserving all its evidence. The sole active P1 root becomes
`p1_floorplan_569_after_relative_path_abort`, with `max_attempts: 1` and
evidence target
`06_build/evidence/modular_work/p1_floorplan_569_after_relative_path_abort.json`.
This is a distinct future schema-2 campaign subject, not a retry: its envelope
must bind a clean frozen commit, accepted source/review packet, corrected
project-relative worker invocation, and a newly generated saved native board.

All seven P2 nodes depend on and backtrack to this sole root; the P4
power-return backtrack edge is also rebound. Scope remains P1 only: anchors,
outline/regions/corridors, native parity and P1 DRC, and body/courtyard/model
coverage. P2/P3, routing, promotion, release, and order remain barred.
Connector FULL remains base PASS, zero unknowns, and all 19 physical targets
before P3, routing, P5, release, or order, under ADR 0011.

Before dispatch, an independent reviewer must verify this archive, old-attempt
preservation, root singularity and reference rewrites, corrected relative-path
preflight, clean frozen source, and a fresh schema-2 envelope. Any failure of
the new one-run campaign is consumed and returns to `placement-and-process`.
