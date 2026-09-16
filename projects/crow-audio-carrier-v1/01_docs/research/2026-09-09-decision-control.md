# Decision-control adoption — 2026-09-09

The reusable process correction is implemented. It does not admit the circuit,
move an acceptance boundary or select a replacement part. Base: `6709d756`.
The existing findings ledger is the only authority for investigation state;
this note records adoption, not a second task queue.

## What changed

Recurring investigations now declare a requirement, relevant operating states,
the decision to make, finite milestones, and cumulative budgets. A read-only
guard checks evidence hashes and distinguishes continued bounded work, an
unassessed launch, and reassessment. Named `pcb_flow run --investigation`
commands reserve a slot before dispatch; another launch cannot silently consume
work while its predecessor is unassessed. The existing compact handoff derives
its decision view from the ledger and rejects stale history or tool identity.

This extends existing lifecycle/backtrack rules, not the engineering gates.
Routine boards need no investigation record. Source arguments belong before
source admission; actual copper checks belong at their layout boundaries;
physical qualification and order-time sourcing keep their existing boundaries.
No new universal simulator, stage, waiver, or vendor-information requirement
was introduced. The dispatch guard is opt-in, not an operating-system sandbox.

## Current carrier decision

`CAR-F12-power-sequencing-decision` records three historical assessments, each
with a distinct useful milestone: correcting the NR-settling premise, accounting
for signed input energy, and excluding the narrow divider-only proof correction.
These were not three failed experiments: the measured non-improving count is
zero. The enforced result is nevertheless `REASSESS` because the next decision
is limited by model uncertainty and requires architecture comparison. Invalid
linear-model predictions establish neither hardware failure nor safety. Valid
audio during undervoltage is not silently added to the brief.

The next bounded engineering work is to compare earlier input-loss detection/
isolation with an amplifier/supply arrangement across cold startup, normal audio,
input removal, brownout and rapid restart. Compare protection paths, stored
charge, credible margins, model limits and verification effort against the
unchanged brief. No candidate is selected here. Review that comparison under
the same finding/history before declaring the next discriminating experiment.
Do not reset the budget to evade reassessment or repeat threshold-only studies.

`CAR-F13-realized-power-transfer` keeps source current-duration budgets separate
from realized copper/return-path checks and first-article measurements. Old
review findings retain their closure obligations, while descriptions no longer
present obsolete pin censuses or already-corrected SPI_CS wiring as current.

```text
next_work(finding)
  -> reopen(requirement, evidence, whole_history)
  -> assess_progress(once_only_milestones, cumulative_spend, model_limits)
     -> carrier: REASSESS -> compare protection architectures
     -> permitted experiment: reserve slot -> bounded dispatch
        -> append actual result under reservation ID -> reassess progress
  -> derive compact handoff from the same ledger
  -> engineering review / native geometry / qualification gates stay unchanged
```

## Verification and limits

The new suite passes 14/14 tests, including 12 hostile/known-bad controls.
PCB flow passes 40/40; runtime 27/27; execution 16/16; disclosure 14/14;
documentation 15/15. These are process tests, not a new run of the carrier's
250 source tests. Full repository contracts still have inherited failures;
their exact baseline comparison is recorded in the companion outcome, without
ratchet inflation or acceptance-limit changes.
The targeted runner-integrity sweep separately fails on five unchanged older
suites that swallow failure exit codes. The new suite's failure propagation
and runner registration were checked directly and pass; this is not a claim
that the full repository suite is green.

Independent forward testing found duplicate-key history erasure, dispatches
not consuming budget, and a YAML merge-override compatibility regression. All
were corrected with actual failing cases and retested. The independent check
also exercised failed children, simultaneous processes, held-lock refusal,
matching/mismatched assessments, and read-only byte/mtime preservation.

Human assessment remains necessary: a hash does not prove an engineering claim,
nor does a milestone close a finding. Advisory locking protects cooperating
reservation writers, not arbitrary editors. Power-loss durability was not tested.
The implementation does not claim tamper-proof history or scientific verification.

All 503 protected source/native/pod inputs match the prior analog-load outcome.
The native board remains stale and unrouted; source engineering acceptance and
fresh exact-artifact reviews remain open. No circuit, acceptance limit, sealed
pod, release, account, upload, order or remote branch changed. Exact commands,
outputs and identities are retained once in
`01_docs/SOURCE-CORRECTION-20260909-decision-control-outcome.json`.
