# Independent RF legacy compatibility review — 2026-09-22

Verdict: **ACCEPT**

Reviewed commit: `084a119b87a1e7e577716f9cdf85e1257712bfb2`

## Boundary review

- Ordinary early source admission for an enabled legacy intent contract with neither `rf.process` nor `rf.layout_constraints` returns `CONTRACT_ONLY`, `geometry_status: NOT_GRADED`, and honest 0/0 RF-net coverage.
- The same contract under `source --require-geometry` exits nonzero and states that geometry-required work cannot accept `CONTRACT_ONLY`. This preserves the placement replay immediately before `route_prep` in `pcb_flow.py` and `rebuild_all.sh`.
- Realized mode exits nonzero before publishing a bundle and states that source-only `CONTRACT_ONLY` cannot approve a board. An explicitly nonexistent `--board` cannot receive a green native RF result.
- `_validate_contract()` now reopens the exact contract through the owning `rf_contract_check.load_contract()` before `validate_enabled()`. Missing or empty rationale, empty port nets, malformed locked cross-sections, and incomplete adopted-module contracts fail.
- `rf.process: {}` cannot downgrade an adopted declaration into legacy handling; it fails for missing `rf-module-v1` profile.
- Legacy contracts that declare `layout_constraints` remain on the existing geometry inventory path. Adopted contracts remain subject to route-denominator, context, layout, placement-replay, and realized-board checks.
- The contract documentation now limits `CONTRACT_ONLY` to early source and states that geometry-required and realized modes are fail-closed.

## Independent checks

- `tests/t1_rf_module.py`: 14/14 pass, including six known-bad fixtures.
- `tests/t1_rf_contract.py`: 19/19 pass, including eleven known-bad fixtures.
- Actual Crow probes: ordinary source returns `PASS: CONTRACT_ONLY` with 0/0; `--require-geometry` exits 1; realized mode with `/tmp/definitely-no-board.kicad_pcb` exits 1.
- Additional negative probes: empty rationale exits 1; `process: {}` exits 1.
- `git diff --check 3c2423d3..084a119b` passes.

This compatibility result admits source intent only. It makes no native geometry, board, fence, DRC, signal-integrity, fabrication, or physical-performance claim.
