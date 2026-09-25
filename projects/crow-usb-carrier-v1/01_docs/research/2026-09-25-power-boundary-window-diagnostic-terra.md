# Power-boundary P1 diagnostic review, 2026-09-25

Status: **INCOMPLETE**. This is a bounded source/witness diagnosis, not P1
acceptance or evidence of current, return, thermal, routing, fabrication, or
assembly adequacy.

## Exact native probe

The probed native board is
`06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/crow_carrier.kicad_pcb`,
SHA-256 `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
All ten recorded witness pads exist on `F.Cu` with their declared nets. The
fixed `J1.10` CHASSIS witness contains its native pad and is the one local
mechanical case. The remaining nine failures are not one common native-board
obstruction.

Seven boxes still contain the named native pad but were authored as long
source-to-reservation strips instead of local witness geometry:

| Net | Witness | Why the P1 checker rejects it |
| --- | --- | --- |
| GND | `C_ADC_3V3X_OK_VDD.2` | spans x=70..118.43 across the adc region |
| N12V_PROTECTED | `C_SPOKE_IN1.1` | extends from the pad to y=85 outside analog_ch1 |
| N1V8 | `R_ADC_1V8_OK_TOP.1` | spans x=114.66..199.825 across regions |
| N3V3X | `R_ADC_3V3X_OK_TOP.1` | spans x=121.66..199.825 across regions |
| N3V3_ADC | `C_ADC_3V3X_OK_VDD.1` | local rectangle but does not touch the declared adc face |
| N5V_LDO_HOLD | `C_ISO1.1` | extends from the pad to y=105 outside analog_ch1 |
| PWR_EN | `U_ADC_PWR_BAD.2` | local rectangle but does not touch the declared adc face |

The checker deliberately requires a local native-pad or virtual block-face
witness. It tests source-region/face locality before obstacle or rough-capacity
analysis, so a witness cannot also be a corridor from its part to a distant
reservation. These seven diagnostics demonstrate a witness-schema misuse; they
do not demonstrate occupied copper or insufficient physical corridor space.

Two boxes are additionally stale against current native geometry:

| Net | Witness | Recorded box | Native pad bounding box |
| --- | --- | --- | --- |
| N0V9 | `C_CORE_FF.1` | [160.22, 108.655, 199.825, 109.83] | [160.24, 116.59, 160.80, 117.21] |
| N5V_BUCK | `C_1V8_OK_VDD.1` | [70, 105.77, 164.22, 106.43] | [163.64, 113.19, 164.20, 113.81] |

Their failure is a genuine stale witness bbox, still not proof that a route is
blocked. The old aggregate packet had board SHA
`fbfb3bda...`; this probe uses the exact newer TI board above.

## Fail-closed repair proposal

Keep `power_boundary_windows` as source reservations with status
`INCOMPLETE`. Do not enlarge any witness to regain a pass. For each movable
power endpoint, replace the bridge strip with a small source-region-face
`virtual_block_face` witness that touches only its declared owner face and
carries the required P2 pad-to-face obligation. Give it a separate reservation
only when a declared integration corridor or shared transition port authorizes
that handoff. Update N0V9 and N5V_BUCK from a fresh native pad measurement;
do not infer their new boxes from component center coordinates. Keep CHASSIS as
the sole fixed native-pad witness and retain its explicit RJ45 pad evidence.

After source repair, rerun `p1_corridor_capacity.py --diagnose-all` against a
hash-bound TI board and require every power witness to be local, contain/alias
the exact pad where physical, and contact only its assigned reservation. The
result must remain `INCOMPLETE` until P2 proves local copper capacity, pad
access, filled-reference return, rail current, and thermal behavior.
