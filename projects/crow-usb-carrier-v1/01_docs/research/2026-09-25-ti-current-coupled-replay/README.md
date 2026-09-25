# Current-source coupled placement replay

**Research improvement; no P1/P2, route, return, release or order credit.**
This replays the previously reviewed 45-pose ADC7/8, analog/VMID and timing
union on the newly generated **current-source TI private board**, instead of
joining board-bound results from the older d0/e07 subjects. It is a replay of
an existing pose set, not another search iteration or reset of an investigation.

The baseline is the D14 private board SHA-256
`c5229350807edd85ce95eadd4ec8e4190941b0dd27edcf0a54a6defda145e6b8`.
The trial PCB SHA-256 is
`bdd5bccb2617d7bbe1de9cd27cda1a0e2f68467bedd169704473a010286a948b`.
Its private receipt, native DRC and source copy are under
`06_build/prototype_board_diagnostic/current-ti-coupled-replay-20260925/`.
Both boards used identical effective `.kicad_pro` and `.kicad_dru` bytes,
including the TMUX POFV rules. Their native DRC reports **0 violations,
499 unconnected items and 0 schematic parity issues**. Count parity and pin
map checks pass on the trial.

The [exact native comparison](comparison.json) confirms 45 expected footprint
pose changes, no other pose changes, all 27 P1-fixed poses unchanged and every
pad identity and relative geometry unchanged. No cross-owner native collision
is added. The ADC7 portal loses its two baseline Y_AUDIO obstacles. Outside
owner references improve **128 → 119**, and references entering a foreign
planning region improve **148 → 138**. Three rough timing openings change:

| Opening | Baseline slots | Trial slots |
| --- | ---: | ---: |
| Translator west | 5 | 5 |
| XMOS west data | 1 | 3 |
| XMOS south three | 0 | 6 |

These are aperture screens, not proven track capacity. The 499 opens mean the
signals remain unrouted. The saved GND zones lack filled-return evidence, the
timing group still has 0/28 references on F.Fab, the ADC8 support pocket
remains tight, and the combined P1 source branch model needs a fresh exact
board contract and independent review. USB ESD remains `prototype_only` and
connector FULL still has 19 physical unknowns.

Reproduce the current private baseline using
`03_src/rebuild_prototype_board_diagnostic.py`, then run `python3 replay.py`
from this directory once in a fresh private output root and
`/usr/bin/python3 analyze.py`. The replay refuses to overwrite existing
candidate output. KiCad assigns fresh POFV area UUIDs, so a fresh replay may
have a different PCB byte hash; bind the fresh exact output and compare native
geometry, rules and DRC before reusing this result. No canonical PCB or source
file was changed.
