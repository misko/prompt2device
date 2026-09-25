# TI ADC timing: exact 14-net accounting boundary

**Research-only negative packet.** `build_trial.py` binds the exact unrouted
TI board SHA `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`
and the merged USB packet. The USB linked path and VBUS trees are retained
unchanged. No canonical source, board, checker, route, stock record, or P1
attempt is changed.

The source and `endpoint_ledger.json` retain **all 14 timing nets and 54/54
unique native F.Cu pad identities**, with source owner and exact alias
parity. The ledger assigns null capacity, P2 pad-to-tree and filled In1.Cu
return debt, and P3 connected-net debt to every unresolved net. The old
timing scalar reservations are removed so they cannot give duplicate or
unsupported capacity credit.

Nine nets with **35 terminals** fit the existing
`unresolved_multiterminal_branches` schema: `ADC_BCLK` (3), `ADC_FSYNC`
(3), `ADC_DOUT1` (4), `ADC_I2C_SCL` (4), `ADC_I2C_SDA` (4), `ADC_READY` (6),
`XU_I2C_SCL_1V8` (3), `XU_I2C_SDA_1V8` (3), and `ADC_DIGITAL_BAD` (5).
Each has one geometry-free branch reservation, an exact native-pad
representative, all endpoint P2 obligations, a P3 minimum tree-edge count,
and a filled-reference obligation. The branch validator accepts all nine.
Four branch pads also have source-region conflict inventory: `R_ADC_DATA_PD.1`,
`R_ADC_I2C_SCL_A_PU.1`, `R_ADC_I2C_SDA_A_PU.1`, and `U_ADC_CLOCK_OK.1`
enter `analog_ch7`. This is physical placement debt, not a corridor waiver.

Five nets with **19 terminals** cannot be encoded honestly by that schema:

| Nets | Terminals | Exact blocker |
| --- | ---: | --- |
| `AUDIO_MCLK_1V8`, `TDM_BCLK_1V8`, `TDM_DATA_1V8`, `TDM_FSYNC_1V8` | 2 each | The branch validator requires at least three exact terminals; each two-pad red trial fails `exact branch endpoint denominator mismatch`. |
| `AUDIO_EN` | 11 | `R_AUDIO_PD.1` and `U_AUDIO.6` lie west of `quiet_power` x=25; `U_ISO1.2` lies west of `analog_ch1` x=25; `U_ISO8.2` lies east of `analog_ch8` x=201. Its red trial fails `branch pad outside source owner region`. `R_AUDIO_PU.2` also enters `input_buck`. |

The full hash-bound `--diagnose-all` equivalent run reports **zero timing
item diagnostics and zero USB item diagnostics**, but the timing allocation
still **FAILS**: `missing per-net boundary witness` for those five nets.
Because allocation evaluation is all-or-nothing, the nine valid branch
representatives cannot be credited and nine global branch-denominator
errors result. This is a deliberate fail-closed outcome, not a P1 pass.
`p1_accepted=false`, timing capacity remains uncredited, and no route or GND return
has been proved.

The possible `[188,94,190,99.84]` lower neck has a separate raw five-slot
full-envelope measurement. It is omitted here because the owner-cell recut,
four distinct TDM/XU endpoint accesses, nonoverlap with other reservations,
and return proof are not yet source/native validated. Adding it alongside
the geometry-free debt without those checks would double-count the four nets.
The next source design must provide an honest two-terminal unresolved
crossing representation or a complete integration corridor, and correct the
four `AUDIO_EN` owner-region violations; the branch schema should not be
weakened merely to silence this negative result.

Reproduce from the repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc-timing-all14-accounting-sol/build_trial.py
```
