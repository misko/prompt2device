# D14 — Private native geometry diagnostic under the TI prototype hold

**Decision (2026-09-25):** Allow a bounded, private, unrouted native PCB
diagnostic from the current TI prototype schematic/netlist. This extends D13's
schematic-only research scope solely to measure placement geometry with KiCad's
project rules. It creates no ordinary schematic or PCB checkpoint, P1/P2/P3
acceptance, connector FULL evidence, fabrication payload, release or order
authority. The selected ESD part remains `prototype_only` and its
`DESIGN_CLEAN` finding remains open.

The producer is `03_src/rebuild_prototype_board_diagnostic.py`. It requires the
existing `critical_part_selection_admission.py --require-prototype` result and
the hash-bound private TI circuit/netlist receipt. It snapshots current
`03_src`, parts and exact netlist to one fresh directory beneath
`06_build/prototype_board_diagnostic/`; it never writes `04_kicad`. The initial
KiCad `.kicad_pro` and `.kicad_dru` are pinned to the reviewed 2026-09-25 TI
diagnostic packet; the producer regenerates rules and TMUX POFV on the new
board, checks for unexpected retained DRU rules, runs pin/count parity, V-PROCESS
and native DRC, and records all input/output hashes. The seed is a declared
input authority because rule generation merges parts of it.

An output with 0 DRC violations may still have unrouted connections, unfilled
saved zones, incomplete P1 geometry and unknown connector fit. No board from
this producer may replace an accepted pointer or be used as fabrication input.
Independent review of the exact receipt is required before adopting it as a
baseline for a coupled placement decision. Ordinary conductors continue to
reject `prototype_only`. D13's electrical qualification and D12's locked
initial stock policy are unchanged.
