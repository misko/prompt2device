# Remaining 26 input/quiet-power obligations

Bound board: `c3d906591a343aea8949687c05c0f5ff4372e982c5af70a04df4828b7409fd93`.
This ledger excludes the 15-ref TPSM buck cell and does not alter the valid
47/47 numeric P2 receipt. It records source reservations, never new mm limits.

| Refs / functional pins | P2 source reservation | P3 saved-copper/physical proof |
|---|---|---|
| C_HOLD1..C_HOLD16, held-rail storage bank | Fixed anchors are deliberate; retain bank ordering, polarity, hold-path access and clearance from switch/heat cells. No locality claim follows from bank anchoring. | Actual held-rail copper, current sharing, pulse/thermal rise and capacitor return topology. |
| C_LDO_NR4,C_LDO_NR5; U_LDO SET7 noise-reduction network | Reserve quiet SET/NR island beside U_LDO without sharing its return with load-current path. | SET/NR return association to the output-capacitor ground; leakage/noise and routed topology. |
| R_LDO_SET; U_LDO.7 SET | Keep resistor in the SET island; its ground reservation is the output-cap return, not arbitrary GND. | Kelvin SET ground connection and assembled noise/stability behavior. |
| R_LDO_PG_BOT_A,R_LDO_PG_BOT_B; U_LDO.6 PGFB / U_LDO.4 PG | Reserve threshold-divider/supervisor cell away from noisy switch/current return. | Actual PGFB/PG copper, startup behavior and ground-return separation. |
| C_OPA_BULK; downstream N5V_LDO_HOLD load | Reserve as downstream bulk, explicitly not LT3045 stability COUT. | Downstream load return, ripple/transient behavior and thermal current path. |
| C_PWR_CT2,C_PWR_CT3; held-power timing/control nets | Preserve designated timing-cell membership and keep away from switch/thermal corridors. | Actual timing-return and transient behavior. |
| R_OPA_BLEED1,R_OPA_BLEED2; discharge/load bleed path | Reserve together with the downstream hold/load discharge cell; do not imply current-loop or thermal proof. | Bleed-path copper, dissipation, pulse/thermal behavior and hold discharge measurement. |

LT3045 authority is `LT3045EDD-PBF/part.yaml`, pins IN1/2, PG4,
ILIM5, PGFB6, SET7, GND8/11, OUTS9, OUT10, EP11. Its source notes require
OUTS9 Kelvin sense at the shared output-cap/load node and direct SET return to
the output-cap ground. P2 can reserve those identities only. P3/FULL must
verify COUT/SET return, EP11/GND common thermal-via/plane realization, input/
output capacitor loop and assembled ESR/ESL; no such fact follows from a
footprint centre or the P-ADJ rows.

No diagnostic distance is included: the selected dossiers provide qualitative
return/thermal obligations here, not a manufacturer placement maximum.
