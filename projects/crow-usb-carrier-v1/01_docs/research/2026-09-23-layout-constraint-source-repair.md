# Crow successor placement-constraint source repair — 2026-09-23

**Result:** The existing candidate board now reaches every declared dossier layout budget: `P-ADJ-UNREACHED PASS (311/311)` in `/tmp/crow-layout-audit-postrepair.md`, versus 55 unreached rules in the frozen pre-repair diagnostic. `P-ADJ` and `P-ADJ-PAIR` remain **FAIL** on measured copper gaps/spans; the source edit did not change any numerical ceiling, claim placement compliance, or waive a gate.

Scope was exactly ten `02_parts/*/part.yaml` files, inside their `layout.keep_short`, `layout.adjacency`, or `layout.notes` fields. YAML comparison against HEAD confirms every field outside `layout` is identical. This task made no changes to the circuit JSON, native board, schematic, footprints, audit code, accepted reviews, or waiver files. The concurrent uncommitted footprint edits and `03_tscircuit/dist/` in the shared root worktree belong to another agent and were not touched. No commit was made.

Inputs: `/tmp/crow-unreached-layout-constraints.json` (55 original rows); current board `/tmp/crow-p1-dlc-usb-successor-20260923/04_kicad/crow_carrier.kicad_pcb`; project dossiers at `/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/projects/crow-usb-carrier-v1/02_parts/`. The comparison ledger `/tmp/crow-layout-constraints-change-ledger.json` records exact old/new refs, nets, limits and rationale for all 79 per-item modifications. The board was only read by `pcbnew` and by `policy_audit.py --phase placement --skip-drc --release-candidate /tmp/crow-layout-audit-staging --output /tmp/crow-layout-audit-postrepair.md`; the candidate symlinks and audit output are under `/tmp`.

Changes by category:

| Category | Ledger rows | Reconciliation |
|---|---:|---|
| Shared-net correction | 43 | Verified both board footprints physically share each new net. Mostly canonical `N5V_LDO_HOLD`, `N5V_LDO_FEED`, `N12V_FUSED`, `N12V_PROTECTED`, and `N3V3_ADC`; eight TMUX output pulldowns use `ISO1..8P/N` rather than obsolete `ADC1..8P/N`. |
| `keep_short` net correction | 4 | LT3045 input/output and reset network use actual `N5V_LDO_HOLD`/`N3V3_ADC`; physical anchor pins, partners and span limits unchanged. |
| Split pairwise budgets | 26 | LT3045 `U_LDO` to each of two output capacitors at 3.5 mm; TPS26625 to each of eight local input capacitors and eight ILIM resistors at 2.5 mm; `U_DUMP` to each of eight parallel `C_DUMP_TIME1..8` on `DUMP_RC` at 3.5 mm. |
| Retarget series timing | 2 | Obsolete `U_DUMP`/`R_DUMP_TIME1` DUMP_RC pair replaced by `R_DUMP_TIME1` to each parallel `R_DUMP_TIME2/3` on actual intermediate `DUMP_RMID`, preserving the 4.5 mm ceiling. Existing `U_DUMP`/`R_DUMP_TIME2` DUMP_RC rule remains. `layout.notes` states the whole PWR_EN → R1 → DUMP_RMID → R2/R3 → DUMP_RC → eight capacitors path. |
| Parallel branch coverage | 1 | Added `U_DUMP`/`R_DUMP_TIME3` on shared `DUMP_RC` at the same 4.0 mm ceiling as the existing `R_DUMP_TIME2` branch; independent review found the missing parallel endpoint. |
| Retire obsolete refs | 3 | `U_OE/C_OE/R_MCH_SENSE/R_MCH_SENSE_PD` do not exist in the current circuit or on the board. Their old OE bypass/sense budgets cannot measure the current architecture. A dossier note identifies current OE owners `U_TDM_XLATE` pin 15, `Q_TDM_GATE`, and `R_TDM_OE_PU` on `TDM_OE_N`; no electrical or new numerical budget was invented. |

A static ledger assertion confirms every old/new numerical `max_mm` or `max_span_mm` is unchanged. The post-repair native policy audit reports `P-ADJ-UNREACHED PASS (311/311)` and deliberately still reports measured breaches, for example LT3045 `U_LDO.1`→`C_LDO_IN.1` 5.70 mm against 5.0 mm and Kelvin `U_LDO.9`→`C_LDO_OUT_1.1` 8.39 mm against 5.0 mm. These are true placement tasks for a future board campaign, not source-name defects. This is a read-only audit of the frozen candidate, not permission to regenerate it.
