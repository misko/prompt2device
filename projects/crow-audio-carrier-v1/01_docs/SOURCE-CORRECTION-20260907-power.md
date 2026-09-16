# Power-source attempt — factual frozen outcome

Status: regenerated SOURCE CANDIDATE, not source acceptance, qualification,
review, route or release authority. DO-NOT-ORDER.

Author start observed 2026-09-07T21:36:55Z; engineering source frozen
2026-09-07T22:31:05Z, before absolute deadline 22:34:37Z. This outcome,
beacon and append-only journal are bookkeeping written immediately after
that declaration; no further engineering changes are authorized here.
No canonical TaskAttempt telemetry is asserted.

Worktree: circuits-worktrees/crow-roof-array-v1-20260901, branch
codex/crow-roof-array-board-dev-20260901; initial HEAD4a753d08.
Immutable task envelope and five files verified before work; exact canonical
envelope SHA and parent source are recorded in ADR-0009. Packet unmodified.
Initial pcb_flow validation passed architecture; final old flow handoff is
correctly STALE because the source changed. It was not relabeled current.

## Implemented source and authority

ADR-0009, exact part dossiers/primary PDFs, three TI primary-land footprints,
TSX, independent manifest, pin assertions, power/net/assembly/first-power rules
and hostile tests describe one 299-component candidate. TPS7A92 held input,
22 ohm precharge with delayed bypass, supervised delayed output dump and
eight complete-filter-path TMUX2821 switches replace the rejected branch.
The reference corrections, two 470 uF FILT reservoirs and pulse-rated feeds,
150 mA ADC/reference budget, 85 C ambient and hardware TDM/reset are preserved.
BLM21PG600SN1D is corrected to its exact 60 ohm catalog/primary identity.

Coordinator explicitly amended the internal local 5 V allocation from 0.25 A
to 0.30 A without changing the immutable packet or external boundaries.
All-channel steady screen 0.267299 A fits; full-allocation upstream screen
0.963872 A fits the unchanged 1.0 A trunk, eight 0.10 A spokes and 10.896 V
delivery calculation. No lowered load or ambient was used to pass.

The only shared edit was coordinator-authorized append of four exact verified
Yageo rows in lcsc_passives_ledger.yaml: C861380, C861192, C861313, C861167.
No existing ledger rows or shared checker implementation changed.

## Measured regeneration and checks

- Full rebuild r1 failed scratch PCB packing; project scratch spacing enlarged.
- Full rebuild r2 produced native source but failed 4 exact resistor identities.
  Exact public catalog descriptions supported the authorized ledger additions.
- Full rebuild r3 exited 2 at the preserved J-PCBA-PRELAYOUT stop, after
  E-CLOSURE 9/9, manufacturing selection 2/2, source census 299 across all four
  sources, E-INV 81/81, label parity 164/164, part pin maps 201/201,
  E-TOPO 10/10 rails and 2/2 converters, E-MARGIN nine rails.
- Exact logs: 06_build/power-source-full-rebuild-20260907.log,
  06_build/power-source-full-rebuild-20260907-r2.log and
  06_build/power-source-full-rebuild-20260907-r3.log.
- Final project unittest discovery: 51 passed. Shared tests/t1_bom_source.py:
  30 passed, 0 failed, 2 slow skipped; 15 known-bad fixtures rejected.
- Final project power-native checker: 25 power pin maps, 24 critical values
  and 16 conditional numerical checks pass; output at
  06_build/verification/power_source_20260907.json. No physical pass implied.
- Final build_provenance.py audit PASS for current source/artifacts.
  Calling the producer-only verify command a second time was inapplicable
  because its stamp is already phase=verified; audit is the after-build check.
- All six final r3 PDF pages viewed. Page-fit power/analog labels remain too
  small for comfortable review; source presentation remains OPEN.
- Existing PCB was not rebuilt, placed or routed; old ERC/DRC/reviews do not
  cover the 299-component candidate. No fresh board-grade result claimed.

The r3 generated prelayout request contains 51 exact codes. Coordinator
reports its separate public probe passed 51/51 at build quantity5 and zero
configured surplus; TMUX had60 observed versus40 needed. That is a dated
coordinator observation, NOT authenticated PCBA allocation or a sourcing pass
adopted by this source author.

IMPORTANT: final explanatory edits to ARCHITECTURE.md, DETAIL_DESIGN.md and
ADR-0009 occurred after r3 captured its 367-file prelayout-input checkpoint.
Verification correctly reports those three changed files. Preserve the
existing request/checkpoints; deliberately re-record final authority before
any later governed resume. No generated/source producer inputs changed
after r3, and M-FRESH remains current. This author did not resume any gate.

## Frozen subjects — SHA-256

- TSX: e066e7cdd044bf9ac72e753f35bcdb1c1003ba512a624b7ce2350f2e844dd15f
- circuit.json: e6b2d277a274be57009b3ae5bd3daaf1c2427ac4599ca5798c7eea3b1f6fb16d
- schematic.pdf: d996da549d7881888721a2124562af078bb07a0b562e2037ff103c310ecaf993
- native .net: 91fc31519a1cf9bd488460f7bdf837f6a459bd75bab83fc74e1533f6100c27dc
- native .kicad_sch: ab8aaed86a2b32e312582af20d041d8f2351c2ae9446ecdc42557f9fb6bfc13e
- unchanged .kicad_pcb: 0f6e2e608e72c986e2fc5d559e63df4ed23de8728e6428698eb3eba9ad7d15d1

## Unresolved rows

POWER-COLD: LDO operational 1.4 V versus logic recommended 1.65 V gap.
POWER-START: actual buck ramp/inrush, NR current through full ramp, restart.
POWER-FALL: actual supervisor detection, isolation/dump and OPA hold timing.
POWER-LOOP: full distributed capacitor/ESR-bank stability.
POWER-REVERSE: held input/output trajectory and hot reverse leakage.
POWER-AUDIO: partial-power/large-step feedthrough, switch distortion/pop.
POWER-DRIFT: prototype 0.05% allowance is not rated 0.5% plus0.05 ohm life drift.
POWER-THERMAL: achieved EP/copper thermal and repetitive pulse behavior at85 C.
PRESENTATION: dense power/analog pages need bounded source presentation work.
FIRST-POWER-PROCEDURE: reconcile conservative 0.20 A bench limit with the new
startup transient before any physical power; do not silently raise it in a run.

These are explicitly explained in ADR-0009, checker output and first-article
plan. Conditional modeled passes do not close them or prove all-life validity.
Uncommitted work is left for coordinator audit. No pod release or unrelated
primary-workspace edits; no push, purchase, vendor contact or sealing.
