# Crow P1 native-evidence terminal-failure archive

This compact tracked archive preserves verbatim the terminal task receipt,
schema-2 envelope, empty runtime log, and all four delivered outputs:
candidate board, evidence archive, measurements, and result. It intentionally
does not copy the large temporary source packet. `SHA256SUMS` authenticates
every archived file; this archive neither reclassifies nor retries the failed
one-attempt campaign.

Original task run:
`06_build/task_runs/p1_floorplan_569_after_relative_path_abort_r1-024bd8503d9f42368eeb7aa313712ed6/`.
The task is terminal `FAIL`, runtime return code `1`, and `result.json` marks
`candidate-measured: FAIL`; the read-only writer scope has equal before/after
hashes and `changed_paths: []`.

`candidate.kicad_pcb` and the evidence archive's candidate board are
SHA-256 `6d948f70f31c1b54dd75d53f5699c8b8fdc61ddf79d0451c3173190ea5b5ccfa`.
The retained placement receipt instead embeds board SHA-256
`979287bfbc2d2719d2cbd0bdf945a44084ab1e81b5e5ecabab4220e4b629b4c4`.
Its placement/capacity PASS is therefore non-creditable for the archived
candidate. The preserved board is forensic candidate-only: no acceptance,
repair, rerun, routing, promotion, release, or order follows from it.
