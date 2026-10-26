# Diagnose and repair schematic failure

Use after a failed producer, missing/stale gate, ERC/parity/semantic defect,
or independent review finding. Read the [stage contract](../../workflow/stages/schematic.md),
the sibling orchestrator recovery procedure, and repair owner references in
[existing-tools](../../bindings/existing-tools.md) completely. Reopen the
failed attempt and exact inputs; retain any previously accepted candidate.

Classify the primary cause before editing:

- Producer/adapter or render failure: inspect the pinned source and producer
  diagnostics. A zero exit with embedded errors, zero expected items, stale
  outputs or missing PDF is failure. Repair authored TSX or the justified
  adapter gap, then use the full source-changed conductor.
- Netlist/ERC/parity/label/closure failure: compare the intended function and
  exact exported subject; fix authoritative source, part facts or electrical
  rules with their owner. Rerun all affected mandatory checks. Do not silence
  a finding by changing a denominator, waiver or generated KiCad bytes.
- Readability/topology review failure: repair the source presentation or
  actual circuit as appropriate; regenerate both machine and human artifacts
  and obtain a new independent exact-subject review. Automated legibility
  checks do not replace the human PDF verdict.
- Wrong selected part, rating, pin fact, architecture interface or RF source
  premise: backtrack to sourcing, architecture or the RF owner. Preserve old
  receipts as history and invalidate dependent acceptance. A new worker or
  model does not reset the unresolved decision's attempt budget.

Record the diagnosis, changed source identities, affected dependents and
bounded next attempt in the existing findings/attempt records. If the same
decision has three non-improving iterations, use the baseline `D-BACK`
judgment; escalate with a bounded question and evidence when a genuine
reasoning gap remains. Do not weaken acceptance or start placement to work
around an incomplete schematic. After repair, follow [generate](generate.md)
and [review](review.md) for the new exact candidate.
