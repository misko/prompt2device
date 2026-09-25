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
including the TMUX POFV rules. Their native DRC reports **0 violations and
499 unconnected items**. The empty KiCad schematic-parity lists do not
establish a performed parity test. Separate count-parity and pin-map checks
pass on the trial.

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

A read-only scratch application of the older d0 unified P1 model to this
board, with its diagnostic regions and the current 45 poses, returned `FAIL`
(13 global errors and 10 item diagnostics). Its service/branch endpoint
witnesses and power handoffs do not transfer unchanged. The scratch contract's
expected hash was self-derived solely to inspect failures; it is not reviewed
P1 authority. The next source task is to regenerate complete endpoint and
boundary records from this exact board, then obtain independent review before
any formal P1 attempt.

The reproducible [native-pad rebind diagnostic](p1_rebind_comparison.json) now
isolates that first source defect. Of the old unresolved-branch witnesses,
only `U_XU.38` changed native bbox (its Y range moved by 0.20 mm). Rebinding
that bbox on the exact trial board changes XMOS service from `FAIL` to
`INCOMPLETE`, eliminates its one item diagnostic and four derivative global
errors, and leaves **nine global timing branch denominator errors and nine
power-boundary item diagnostics**. The timing errors arise because the timing
allocation still fails as a whole; its five primary source gaps are four
two-terminal crossings and `AUDIO_EN` owner containment. The power witnesses
remain eight nonlocal rectangles and one movable-owner witness with no virtual
block face. This repair changes only a private scratch contract, never the
canonical source or board, and grants no route or P1 credit. Reproduce with
`/usr/bin/python3 diagnose_p1_rebind.py` from this directory. The next
material board task is resolving the `AUDIO_EN` owner geometry and proving
timing access on this same board, followed by source-author review.

This diagnostic now calls the shared `integration_candidate.py` proposal and
finding grouper. The saved report retains all raw errors and item findings;
its repair view shows **five missing timing witnesses**, **nine consequential
branch errors**, and **nine independent power findings**. The proposal only
measures native geometry. It does not refresh a review hash or accept P1.

One [three-pose private trial](audio_en_three_pose.py) addresses that owner
geometry on the same current-source board. It moves `U_ISO1` to
`[27.05, 74.6, 0]`, `U_AUDIO` to `[28.7, 109.85, 0]`, and `R_AUDIO_PD` to
`[28.45, 106.1, 90]` (mm, degrees). The current exact saved PCB is
`0bd3ac8dd8c80177958c009a0644f0bc723bcee7ad7085c2fb76c09c5df958f5`.
Count and pin-map parity pass; native DRC remains **0 violations and 499 open**
under unchanged effective rules. KiCad schematic parity is not established by
that report. All **11/11 `AUDIO_EN`
native terminals** now lie inside their declared source-owner regions. A
native comparison confirms exactly these three of 569 footprint poses changed;
all 27 P1-fixed poses, 1,872 pad identities/local geometries, and the 14
existing board tracks remain unchanged. A
scratch exact unresolved-branch record for this net passes the checker’s
native endpoint, owner, blocker and P2/P3 obligation validation. Three quiet
power pads still intersect the overlapping `input_buck` planning region and
are explicitly listed as physical blockers. This candidate is neither routed
nor adopted as canonical source; it has no P1/P2 or release credit. The other
four timing nets lack two-terminal source records, and the nine old power
witness findings remain. Reproduce in a fresh private output directory with
`/usr/bin/python3 audio_en_three_pose.py`; the script refuses to overwrite an
existing candidate.

The same native pilot confirms `AUDIO_EN` has 11 exact terminals on both
private boards and improves source-owner containment from **8/11 to 11/11**.
The placement still needs integrated independent review and route/return
proof before any adoption.

A subsequent [six-hole mechanical-support trial](mounting_six_trial.py) tests
the missing restraint geometry on this same source candidate. It adds six
`MountingHole_3.2mm_M3` board-only footprints at `[30,40]`, `[130,40]`,
`[212,45]`, `[30,82]`, `[130,132]`, and `[230,130]` mm. The current private
PCB SHA-256 is `009ecf6383f07129653758fdc0855c793d8915e4ae5b0980278e7a5fa4fc47c7`.
Exactly H1–H6 are added; all previous 569 footprint poses and pad identities
are unchanged. The separate count/pin-map parity checks pass; native DRC
reports **0 violations and 499 open connections**. KiCad could not fetch a
fully annotated schematic netlist, so its schematic-parity test did not run;
the empty JSON parity list is not a parity pass. Hole centers are at least
8 mm from the rectangle outline. The smallest measured gap between a mounting footprint's
courtyard box and another component's courtyard box is only **1.513 mm**
(H5 to C_HOLD16); H2 is **2.007 mm** from J4/J5. These are screening
measurements, not screw-head, washer, standoff, connector-body, or fixture
clearance. The candidate has no tested restraint, enclosure fit, connector
FULL, P1 acceptance, fabrication authority, or release. A reviewed mechanical
specification must settle hardware envelopes, fixture load paths, service
access, and hole positions before any adoption. The script refuses to
overwrite its private output.

Reproduce the current private baseline using
`03_src/rebuild_prototype_board_diagnostic.py`, then run `python3 replay.py`
from this directory once in a fresh private output root and
`/usr/bin/python3 analyze.py`. The replay refuses to overwrite existing
candidate output. KiCad assigns fresh POFV area UUIDs, so a fresh replay may
have a different PCB byte hash; bind the fresh exact output and compare native
geometry, rules and DRC before reusing this result. No canonical PCB or source
file was changed.
