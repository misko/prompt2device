# P2 input/quiet-power full-cell A2: supplemental exact-board assessment

Status: **engineering FAIL / task-delivery FAIL; no P2 acceptance**. This assessment adds read-only checks of the one generated A2 board. It does not alter either original task receipt or claim a third attempt.

## Frozen execution history

- Accepted P1 base board SHA-256 `b7b1e7c8aa8b6bb5668b2c420271dba75ffc40fb0a170c8b0b103088c2d0dcea`. Source checkout HEAD `8fb310f4878d7ab00bbe5749407285f47d4a5327`; plan `c95f59ae4a562374c67464b8e2538716c63dd3f3ef991a39eb069020f6d603b8` and CJ `2b9a33b6473029138362253c48a28406138221e2dbf28907fb1a6f5a3dfd5410` unchanged.
- A1 task identity `(replacement_index=0, attempt_index=0)` is terminal FAIL, receipt SHA `4bde90026d02f2ab21215146283c98a9f89ae69670c4a0a2538430a0809128eb`. The command adapter stripped `P2_WORK`; wrapper failed before native generation. It counts against the plan's two-attempt task limit.
- A2 identity `(0,1)` is terminal FAIL, receipt SHA `c1f54aee84e66e53d36cd2c7bcca5a775dd274db17537ee9ee8ce4382d47bf49`. One native board was generated: original board SHA `12224f54c1da0bcfb30d0427167db1f0ec24e3f4569d09a19e2be249411312fc`. This second/final task attempt delivered exact 47-row measurements, but a shell tab-pattern defect skipped TMUX POFV and native DRC in the recorded task. `candidate-measured` correctly failed; the original check-status and task receipt remain unchanged. Two of two plan attempts are consumed. The withdrawn three-seed in-memory probe generated no board.
- Immutable copies of both receipts and original A2 measurement directory are under `/tmp/crow-p2-a2-immutable-archive-20260923`; the archive manifest lists SHA-256 for each file.

## Measured placement

`constraint_census.json` reports 5/6 `P-ADJ` and 33/41 `P-ADJ-PAIR`, **38/47 pass, nine fail**. All 311 declared placement budgets are reached/measurable; none is waived. Exact failures (actual/budget mm):

| Pad-to-pad relationship | Net | Actual / budget mm |
|---|---|---:|
| U_DUMP.2 to C_DUMP_TIME7.1 | DUMP_RC | 3.693 / 3.5 |
| U_DUMP.2 to C_DUMP_TIME8.1 | DUMP_RC | 3.908 / 3.5 |
| U_DUMP.2 to R_DUMP_TIME2.2 | DUMP_RC | 4.724 / 4.0 |
| U_DUMP.2 to R_DUMP_TIME3.2 | DUMP_RC | 4.880 / 4.0 |
| Q_DUMP.3 to R_DUMP.2 | ADC_DUMP | 2.325 / 2.0 |
| Q_PRE.1 to R_PRE_G.1 | PRE_GATE | 3.036 / 2.5 |
| Q_PRE.1 to Q_PRE_EN.3 | PRE_GATE | 5.534 / 3.5 |
| U_LDO.7 to R_LDO_SET.1 | LDO_NR | 5.368 / 5.0 |
| U_PWR.1 to R_PWR_BOT.1 | PWR_SENSE | 1.602 / 1.5 |

The unchanged P1 board has 6/47 passing owned rows, so this candidate improved the local placement but did not close P2. The A2 source added 72 `placement.post_anchors`; 42 owned references moved. All 479 unowned and 17 fixed owned references retain exact P1 transforms. Source count/pin/net parity, pad-separation, 568/568 model-file coverage, 27 fixed anchors, 16 holds, and region/corridor/capacity checks pass. Physical placement shows 0 body overlap/foreign-pad findings across 568 footprints, P-CAP 150/633 tracks (0.24 vs 0.5 fail threshold), and P-OUT 1.00 mm vs 0.15 mm minimum. Native route count remains 499 unrouted.

## Supplemental native check, separate from task receipt

The original board and `.kicad_pro`, `.kicad_dru`, `.kicad_sch` were copied byte-for-byte into a separate supplementary tree, and the original board SHA was rechecked after all work. The first supplementary TMUX run lacked the exact coupon in the sparse worktree and failed; the first DRC run lacked `fp-lib-table` and yielded 199 library-configuration warnings. Both diagnostic failures and logs are retained. Adding the **accepted, hash-checked** TMUX coupon/part/native footprint and generated footprint library table to the separate supplementary tree corrected only those missing copy dependencies.

With the complete library table, native DRC on a **byte-identical, untouched `12224f54…` board copy** reports **104 violations**: 56 clearance errors, 32 hole-clearance errors, eight via-diameter errors and eight annular-width errors; schematic parity is zero and 499 connections are unrouted. The original native candidate therefore does **not** have DRC clearance. The source board lacked its required TMUX POFV areas/rules because of the task runner's skipped step.

The TMUX POFV producer then passed and generated eight exact B2 rule areas/rules in a **separate derived board**, SHA `75935c42631f44ca7abc324e21601b7a9aa51503f621fba32ac868c9d897e405`. Its `.kicad_pro` hash remained `7f397b2a9f57ec8d4ec07b07920cfe0fe9173651642c17eba55a8f11c39c1ffd`; POFV appended reviewed rules to `.kicad_dru` hash `cf63c694cf349857cd13b6fe14c8044a38afd0ff6fa42ae4c6a1647c8509ddcd`. Independent `pcbnew` comparison of source and derived boards found all 568 footprint/pad signatures, 14 tracks/vias, 572 drawings and the one pre-existing non-rule zone identical; the only object-class count change was zero to eight named `tmux4827_b2_pofv_U_ISO1..8` rule areas. This supports equivalent placed copper/pad geometry under the prescribed profile, without equating the two board hashes.

Native `kicad-cli pcb drc --severity-all --refill-zones --schematic-parity --format json` on that separately derived POFV board, with the complete footprint table, reports **zero violations, zero schematic-parity findings, 499 unconnected items**. `placement_drc_check.py` passes. DRC JSON SHA `5e33e2a105022c8d805e33c11c588f7f885bcb69b88ccb23ef2c71b6a0562009`. This result attaches to derived board `75935c42…`, not untouched `12224f54…`; it is **not** a retroactive task PASS and does not erase its SKIPPED statuses.

## Next source step

Address nine residuals in the full input/quiet-power post-anchor source, preserving the exact source net/pin semantics, 27/16 fixed anchors/holds, every unowned transform, body/edge/forbid constraints, and 47 original numeric budgets. The failures cluster in dump timing (four), dump FET (one), precharge (two), LDO sense (one), and supervisor divider (one). An in-memory search can propose a correction, but no further native candidate is admitted under the consumed two-attempt `p2_input_power` work item. The owner must explicitly backtrack/reassess the failed work item and authorize any fresh, bounded source/board campaign; no old allowance or failed receipt may be reset. Physical connector FULL still has 19 unmeasured targets and blocks P3, all routing, P5 integrated promotion, release, and order. No accepted board pointer changes.
