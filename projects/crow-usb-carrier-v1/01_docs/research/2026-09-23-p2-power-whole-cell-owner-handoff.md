# Power whole-cell source-owner D-BACK handoff

No further geometry attempt is authorized by this handoff. The v3 artifact is a **partial proof**, not proof of complete cell feasibility and not evidence of hardware impossibility.

## Frozen partial evidence

* Terminal JSON: `/tmp/crow-power-joint-cell-candidate-v3.json`, SHA-256 `b7bf07913e8c59abf81bd7ee22d32ea80de57cb32e542c61aba13c2fb7ad7b2a`.
* Terminal report: `/tmp/crow-power-dback-v3-terminal.md`, SHA-256 `1bc8bc393f7fe4dc1dcef2c8a0069380eb26d270f5e48b80ded464337ddc73b6`.
* Corrected v2 report: `/tmp/crow-power-dback-v2-terminal.md`, SHA-256 `8c1b785ea5fc2ac76a4f6a0402d9e8a69421d68377454103dde9b50644024732`.
* Accepted baseline constraint census: `/tmp/crow-p2-input-power-backtrack-r1-20260923/06_build/p2_input_power_source_backtrack_r1/constraint_census.json`, SHA-256 `cee0e10ef6e8b74644d9df7985997774e4be845252a70ab2a191ea1f3da3df58`.

V3 proves only that the south-widened allocation can simultaneously hold `C_OUT1 (51.0,92.0,0)`, `C_OUT2 (56.0,92.5,90)`, `C_OUT3 (50.5,87.0,90)`, `C_IN1 (42.5,96.5,180)`, and `C_IN2 (42.5,100.0,180)` under its courtyard predicate. It does not prove a complete VIN/control/precharge placement.

## Accepted numeric rows that bind the precharge group

All four are `P-ADJ-PAIR` copper-gap engineering ceilings from `02_parts/AO3401A/part.yaml`; they are not manufacturer maxima. AO3401A physical pins are pin 1 gate, pin 2 source, pin 3 drain.

| Row | Exact physical pads/net | Baseline | Budget |
|---|---|---:|---:|
| `AO3401A:adjacency:0` | `Q_PRE.2` source ↔ `D_HOLD.1`, `N5V_LDO_FEED` | 1.950 mm | 2.0 mm |
| `AO3401A:adjacency:1` | `Q_PRE.2` source ↔ `R_PRE.1`, `N5V_LDO_FEED` | 3.675 mm | 4.0 mm |
| `AO3401A:adjacency:2` | `Q_PRE.1` gate ↔ `R_PRE_G.1`, `PRE_GATE` | 1.780 mm | 2.5 mm |
| `AO3401A:adjacency:3` | `Q_PRE.1` gate ↔ `Q_PRE_EN.3`, `PRE_GATE` | 3.000 mm | 3.5 mm |

Thus a whole-cell source allocation must move `Q_PRE`, `Q_PRE_EN`, and `R_PRE_G` together with their numeric partners `D_HOLD` and `R_PRE`, or hold the partners fixed while proving all four rows still pass. Moving only the three initially named refs is insufficient because the two `N5V_LDO_FEED` rows bind `D_HOLD` and `R_PRE` to the same allocation decision.

## Next upstream allocation scope

The next source owner should allocate one coherent power cell containing the TPSM63603 VIN/VOUT/quiet-control satellites **and** the five-ref precharge neighborhood (`Q_PRE`, `Q_PRE_EN`, `R_PRE_G`, `D_HOLD`, `R_PRE`). Preserve `U_BUCK`, `J_PWR`, fixed 27, hold 16, east dump cell, and every unowned reference. Regrade the complete 6 P-ADJ + 41 P-ADJ-PAIR census, not only the four rows above, because moving the partners can affect other row ownership.

The remaining-26 qualitative ledger remains `/tmp/crow-power-remaining26-obligations-terra.md`, SHA-256 `6143119c7db4f012b23736dc83494d1b2565137475e4efd60c37b902f63c057e`. P3/FULL saved-copper obligations remain open. No source, board, graph, or attempt record was changed.
