# Project status

<!-- pause-state:c31ae4ef9b55746f7319fa11c37986ac42faaf25b6cabb75d6297e76aad4c72b -->

- Phase: `placement`
- State: **PAUSED**
- Checkpoint: `06_build/checkpoints/schematic.json` (`2fb4dd626750`)
- Blocker: P1 floorplan and scoped P2 input/quiet-power board c3d90659 are independently accepted; graph P1/P2 work is recorded. Other blocks still exceed 3 keep-short and 227 adjacency budgets, and connector FULL has 19 physical targets unmeasured. The board remains 499 unrouted; P3, routing, P5 integrated promotion, release and order are blocked.
- Next command: `Census the remaining P2 blocks on the exact scoped board, prepare a bounded reviewed placement source candidate for their failed budgets, and obtain all 19 connector FULL physical measurements before P3 or any routing; preserve the old P2 2/2 failure history and scoped power acceptance.`

## Bound receipts

- `01_docs/research/2026-09-23-p2-input-power-r3-scoped-adoption.md` — `9ab8689c2853`
- `08_reviews/2026-09-23_p2-r3-budget-authority_terra.md` — `d070308a0fb1`
- `08_reviews/2026-09-23_p2-r3-native-power_terra.md` — `9a17469dd252`
- `08_reviews/2026-09-23_p2-r3-source-admission_terra.md` — `4b3bcecc65b6`

This file is generated from `01_docs/pause_state.json`; edit the manifest with
`pause_state.py record`, not this view.
