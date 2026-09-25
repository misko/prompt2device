# Independent review: quiet-power 13-cell replay and boundary probe

**Scope:** research-only review of SOL commits `6306bb84` and `505eb574`.
Neither packet supplies route, capacity, return, connected-tree, P1, or P2
acceptance.

## Reproduction

I extracted the checker and probe sources at their respective commits and ran
them in a temporary directory against the hash-bound Q_PRE board
`e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef`.
This avoided the then-uncommitted `branch_owner_pockets` checker work in the
shared tree. The `6306bb84` replay output is byte-identical to its committed
`result.json` (SHA-256
`1636d72b8587b5e98c59c6a1dac8670f3d951f03655205e3cf4a34e26d469f37`).
The `505eb574` boundary output is likewise byte-identical (SHA-256
`de4accd465de037e1b4c99162d4dc61c21d1d2af130735e333b71b854e6bded0`).

`_physical_cells` accepts the 13 occupied `quiet_power` cells. Its exact
69-reference partition is complete and unique: the 13 group counts are
6, 9, 1, 1, 1, 2, 2, 2, 10, 8, 10, 4, and 13 (sum 69). The replay also pins
the complete 569-reference modular-owner census. This admission exercises
the checker’s native full physical envelopes, every pad, foreign-footprint and
foreign-source-region exclusion, and pattern-to-cell consistency. The one
untagged quiet-power endpoint (`R_PWR_TOP.1`) has pad hull
`[74.775, 91.025, 75.575, 91.975]` mm and no foreign native envelope enters it;
there is no hidden source-region or stale-board success in this result.

The ten exact tagged endpoints are: `C_LDO_OUT_1.1`, `C_LDO_OUT_2.1`,
`C_OPA_BULK.1`, `R_ADC_TOP.1`, `R_DUMP.1`, `R_LDO_PG_TOP.1`,
`R_OPA_BLEED1.1`, `U_LDO.10`, `U_LDO.9` on `N3V3_ADC`, and `D_HOLD.2` on
`N5V_BUCK`. The full native terminal denominators remain 42 (`N1V8`), 27
(`N3V3X`), 68 (`N3V3_ADC`), and 34 (`N5V_BUCK`), with no terminal deletion or
capacity credit.

## Remaining blockers and boundary result

The baseline has the intended fail-closed outcomes: `N1V8` 42/42 and
`N3V3X` 27/27 admit only as unresolved, no-credit branch records;
`N3V3_ADC` rejects at `U_AFE2.8`, whose pad reaches x=69.25 mm beyond
`analog_ch2` x2=69.00; `N5V_BUCK` rejects at `U_BUCK.10`, whose pad reaches
y=100.70 mm beyond `input_buck` y2=100.50.

The independent replay of `505eb574` confirms the bounded result. Extending
only `analog_ch2` to x2=69.25 preserves physical-cell admission but immediately
stops at `U_AFE3.8` (x=91.25 beyond unchanged `analog_ch3` x2=91.00).
Extending `input_buck` to y2=100.70 as well is rejected before any branch
validation: it overlaps the `quiet_buck_edge` physical cell over
`[51.675, 100.525, 54.975, 100.700]` mm. This is a source-region/cell
contradiction, not a copper-short conclusion.

The next sound action is a coupled, full-member `input_buck` physical-cell
partition or a physical placement change, then a separately reviewed chain of
analog-channel region changes. It must retain the 569/69 census and all
171 terminals, and demonstrate native routing, filled-reference return, and
connected trees before any P2 or P1 consideration.
