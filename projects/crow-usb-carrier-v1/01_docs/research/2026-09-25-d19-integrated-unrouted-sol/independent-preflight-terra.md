# D19 independent preflight — PASS

**Signed review: Terra, 2026-09-25.** `D19_PREFLIGHT_PASS` for the exact
author packet SHA-256
`5b5972ac77e4ae3fb9b02e06d985b3d50f07d68b6487e3a0562757685ee7c1cb` at
`06_build/prototype_board_diagnostic/d19-integrated-source-preflight-r3-20260925/preflight.json`.

The packet binds the frozen expanded-board and sidecar inputs, complete source,
library and parts trees, matched `fp-lib-table`, KiCad CLI/pcbnew 10.0.4,
3313A pair-control receipt, generator/checker identities, source/P1
stack-and-anchor parity, and the fixed one-shot generation and post-generation
recipes. `generate_once.py --preflight-only` returned
`READY_FOR_INDEPENDENT_PREFLIGHT` with this digest and created neither a claim
nor candidate output.

This signature permits only the one hash-pinned, private, source-generated,
unrouted D19 candidate. D15 remains `FAILED_RESEARCH`; 3313A remains a
research hypothesis with no order or production-impedance claim. The result
must run the pinned post-generation checks, a new exact-board P1 contract, and
independent all-P1/affected-P2 review. It grants no P1/P2/P3/P5, connector
FULL, D18 route, fabrication, assembly, release, order, or spend credit.
