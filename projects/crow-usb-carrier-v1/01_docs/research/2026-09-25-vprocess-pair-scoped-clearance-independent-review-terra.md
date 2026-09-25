# Independent review — 7aae2163 pair-scoped V-PROCESS guard

**Scope.** Read-only review of commit `7aae2163` (`via_process_check.py` and its targeted tests). No canonical source, board, or generated board was changed; this note grants no qualification or decision credit.

## Result: PASS for the checker change

The new `pair_scoped_dru_rules()` admission path remains constrained to an exact, source-backed pair exception. It requires the exact `nets_a`/`nets_b` schema, exactly one net on each side, a nonempty rationale, and rejects any pair containing a net present on the actual TMUX footprints. It requires exactly one named source rule area with `layers: [F.Cu]`, `deny: []`, and a finite rectangle; this is a **permissive** F.Cu rule area, as intended for the pair exception. It then requires exactly one native F.Cu rule area with the same name and bounds, whose relevant permissive flags are all false. The expected generated DRU rule is reconstructed and removed only by exact byte match. Any remaining foreign clearance constraint is still rejected.

This bounds the exception to an exact non-TMUX pair inside the declared F.Cu geometry. It does not change board electrical objects and does not turn the consumed D15 `FAILED_RESEARCH` result into a pass or grant D15/P1/release credit.

## Independent checks

- `python3 -m unittest skills.jlcpcb-fab.scripts.tests.test_via_pair_scoped_clearance`: **7/7 passed**. The tests cover exact output plus widened selector, TMUX-net, source/native area layer and bounds drift, and DRU selector tampering negative cases.
- Read-only `via_process_check.py` replays: **PASS** for both the D15 3313A candidate and frozen expanded-locked board; each reported `14 protected / 0 ordinary / 0 partial` and no V-PROCESS failures. No board generation was run.
- `python3 -m unittest skills.jlcpcb-fab.scripts.tests.test_assembly_locator`: **1 failure / 32 tests** in `test_freshness_composes_locator_failure`. The fixture exits first with `CRITICAL-SELECTION RELEASE HOLD: cannot locate project authority ...`, before its expected `A-LOCATOR FAIL`. Commit `7aae2163` changes neither `assembly_locator_check.py` nor its tests, so this is an existing fixture/order or environment failure, not a regression from this change.
