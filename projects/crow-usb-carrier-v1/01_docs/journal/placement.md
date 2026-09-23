# Placement journal

## 2026-09-23 15:08 — iterate 1
- did: Reopened accepted P1 r4 floorplan and measured a full 72-post-anchor isolated P2 input/quiet-power proposal. Preserved both terminal task attempts and one generated native board without promotion.
- result: A1 setup FAIL before board; A2 generated board `12224f54…` but delivery FAIL after skipped TMUX/native DRC. Exact P2 block layout 38/47 pass, nine fail; all 311 declared budgets reached. Supplemental untouched-board DRC 104/parity 0; prescribed-POFV derived board `75935c42…` DRC 0/parity 0, 499 unrouted. Independent Terra review DEFECTIVE/DO-NOT-ORDER.
- next: Retain research patch and nine measured gaps; graph records P1 WORK_RECORDED and P2 input-power BACKTRACK_REQUIRED 2/2, with P3/P5 blocked.

## 2026-09-23 15:08 — stuck
- did: Backtracked the exhausted P2 input/quiet-power work item after two task failures; did not retry, rewrite receipts, promote source or route.
- result: Plateau is nine numeric local gaps on the sole native P2 board, not a source net/pin mismatch. Cause is interacting dump-timing, precharge, LDO and supervisor placements; a separate in-memory 23-pose r2 proposal predicts 47/47 but has no native proof and tight margins.
- next: Independently review the unaccepted r2 source proposal, explicitly reassess a fresh bounded task/campaign, then regrade original 47 limits, all P1 invariants, TMUX POFV and native DRC/parity. Connector FULL 19 physical targets remains required before P3, any routing, P5 promotion, release and order.
