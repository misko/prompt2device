# Schematic-stage learnings

## Repeated protection finding requires an architecture backtrack

- what happened: CAR-F12 remained open after the implemented amplifier and
  reference corrections and the completed isolation-source comparison. The
  latest status turn changed no engineering state; passing source/tool tests
  did not close the protection argument.
- root cause: the successive local tasks retained the split-rail protection
  architecture while refining components and controls. Its full transition
  argument remained undecided; an unadopted proposal became too prescriptive
  an input to the next task.
- avoid next time: use the existing D-BACK boundary on a recurring finding,
  give a fresh architect the actual source and unchanged requirements, and
  allow an evidenced upstream arrangement change. Require a discriminating
  outcome, not another restatement of unresolved checklist rows. Missing
  individual maxima are not by themselves demonstrated part failures.
- candidate-canon: no — the existing D-BACK/decision-progress policy already
  prescribes this; this record documents applying it to the carrier.
