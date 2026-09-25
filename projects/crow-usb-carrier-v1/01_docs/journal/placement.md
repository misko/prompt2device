# Placement journal

## 2026-09-23 15:08 — iterate 1
- did: Reopened accepted P1 r4 floorplan and measured a full 72-post-anchor isolated P2 input/quiet-power proposal. Preserved both terminal task attempts and one generated native board without promotion.
- result: A1 setup FAIL before board; A2 generated board `12224f54…` but delivery FAIL after skipped TMUX/native DRC. Exact P2 block layout 38/47 pass, nine fail; all 311 declared budgets reached. Supplemental untouched-board DRC 104/parity 0; prescribed-POFV derived board `75935c42…` DRC 0/parity 0, 499 unrouted. Independent Terra review DEFECTIVE/DO-NOT-ORDER.
- next: Retain research patch and nine measured gaps; graph records P1 WORK_RECORDED and P2 input-power BACKTRACK_REQUIRED 2/2, with P3/P5 blocked.

## 2026-09-23 15:08 — stuck
- did: Backtracked the exhausted P2 input/quiet-power work item after two task failures; did not retry, rewrite receipts, promote source or route.
- result: Plateau is nine numeric local gaps on the sole native P2 board, not a source net/pin mismatch. Cause is interacting dump-timing, precharge, LDO and supervisor placements; a separate in-memory 23-pose r2 proposal predicts 47/47 but has no native proof and tight margins.
- next: Independently review the unaccepted r2 source proposal, explicitly reassess a fresh bounded task/campaign, then regrade original 47 limits, all P1 invariants, TMUX POFV and native DRC/parity. Connector FULL 19 physical targets remains required before P3, any routing, P5 promotion, release and order.

## 2026-09-25 — evidence scheduling and unchanged-board replay
- did: Implemented D18 workflow changes with SOL implementation and Terra independent review. Existing P1 CLI now supports `--check-only`; no additional scheduler or receipt schema was introduced. Checker fixes re-evaluate existing geometry, while historical failed research remains immutable.
- measured: SOL replayed expanded-locked Crow board `fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16` with exact expected input digests: exit 1, INCOMPLETE, five incomplete allocations, zero errors/diagnostics, no P1 acceptance. Board, inputs and historical receipt bytes were unchanged. Terra independently reviewed the implementation and D18.
- validation: 91 coarse checker tests, 19 modular workflow tests, 14 progressive disclosure tests and 15 documentation tests passed; skill authority and skill quick validation passed. These validate process behavior, not engineering admission or route feasibility.
- next: Use the same placement reference to establish complete USB-path feasibility under actual package/stack/rules, then close independent P1 capacity and affected P2 gaps. D18 narrowly revises the prospective private-design dependency on connector FULL; it does not admit current routing or ordinary P3/P5. Physical qualification, prototype-only transient findings and release/order holds remain open. No board was regenerated and no fabrication was authorized.

## 2026-09-25 — USB endpoint and complete-path rule screen
- did: SOL measured the frozen expanded-locked native pad geometry; Terra independently reproduced it. Root replayed `research/2026-09-25-usb-path-feasibility-sol/measure.py` successfully. The probe verifies five board/source/sidecar digests before and after reads.
- measured: A centered canonical 0.410-mm launch has only 0.145-mm foreign clearance at Type-C B6/A8 and 0.070 mm at XU60/61 against the 0.150-mm rule. The 0.180-mm hypothesis fits these static pad/track envelopes (0.200 and 0.150 mm). Historical D15 declares a 0.100-mm pair gap but only grants corresponding clearance inside its XU launch area. Complete connector/ESD/XU routing and continuous In1.Cu return remain unproved. These are local envelope calculations, not native routed DRC.
- next: Keep the placement fixed; prepare one unadopted 3313A whole-path USB pair-rule proposal retaining 0.150-mm foreign clearance. Resolve its exact pair domain and transition model before another native experiment. Preserve D18 P1/P2 prerequisites, D15 failed history and release/physical holds. Stop the present screen here rather than regenerate the unchanged conflict. No board, source rules, stock snapshot or historical receipt was changed.
- evidence: `01_docs/research/2026-09-25-usb-path-feasibility-sol/README.md`, its hash-pinned `measure.py`, and `08_reviews/2026-09-25_usb-complete-path-feasibility_terra.md`.
