# TI board exclusive-cell ownership census — 2026-09-25 UTC

**Pre-routing diagnostic only.** `skills/kicad-pcb/scripts/source_region_ownership.py`
checks only the six Crow `physical_cells` explicitly declared in
`03_src/rules/p1_corridor_requirements.yaml` as exclusive. It compares each
assigned native footprint body/courtyard envelope and every pad against its
cell, then reports every other native footprint or pad intersecting that cell.
Ordinary modular planning regions remain nonexclusive; their conflicts are
reported separately as observations and cannot fail this gate.

On the exact unrouted TI board, the hash-bound census returned **PASS** for
six exclusive cells: **zero owned-outside, zero foreign-inside, zero structural
errors**. It separately recorded **241 nonblocking planning observations**:
113 owned-outside and 128 foreign-inside. These are expected evidence that
functional block regions need not be footprint partitions; no rough region
was promoted to a physical cell. The ignored full JSON report is
`06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/source_region_ownership_census.json`,
SHA-256 `7acf8836542a1acd65a33f9cbd5855f2935502bccef5e216907ca18c57b8d89b`.

Bound inputs: board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`,
floorplan `0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868`,
modular plan `75c3a517cea50dd6b5745fae96b051d334debd48aac143becaca3d5fe3fc35dc`,
and P1 source `191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3`.
The CLI requires these four independently expected SHA-256 values and exits
nonzero on any exclusive-cell failure or hash drift. This result does not
establish connector edge fit, route capacity, P2, P1, P-OUT, or FULL.
