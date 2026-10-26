# Independently review the schematic candidate

Use only when the generated candidate and its owning gate evidence can be
reopened. Read the [stage contract](../../workflow/stages/schematic.md) and
review owner references in [existing-tools](../../bindings/existing-tools.md)
completely. Commission a fresh reviewer on the **exact** source, native
schematic/netlist, human PDF, selected parts/datasheet facts, requirements and
gate receipts—not the author's conversation or conclusion. The existing
review commission, timeout, verdict and adoption mechanism remains authority.

Independently derive the intended topology from the brief, architecture,
datasheet figures and part facts. Compare it to the exported netlist and
schematic: rails, power/protection path, pin functions, connector order,
polarity, ratings, NC handling, decoupling, interfaces and repeated channels.
Internal parity cannot prove that a symbol and footprint were not consistently
wrong together. Mark unsupported facts as questions; do not rationalize a
pin map from the candidate's own dossier. Apply the owning RF schematic and
high-speed digital criteria when selected.

Examine the exact PDF as a human document: visible primary paths, readable
values, legible connector direction, grouped pins, sheet boundaries and no
ambiguous overlap. The normal TSX render and KiCad machine schematic have
different audiences. Capture concrete findings with exact subject identity,
severity and repair destination. A reviewer timeout, missing checklist row,
stale subject or unadopted verdict remains unresolved.

Only the existing gate/review consumer may mark `schematic_reviewed`; this
procedure supplies its evidence. If a finding requires an edit, return to
[repair](repair.md) and review the regenerated exact subject. On acceptance,
persist the handoff and stop for the run's schematic reflection before any
placement task.
