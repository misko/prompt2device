# TPSM63603 deterministic expanded-allocation construction

Status: **OUTPUT BANK FITS; COMPLETE CELL STILL BLOCKED BY VIN/PRECHARGE ALLOCATION**.

This was the single authorized deterministic construction after D-BACK. It expanded the VOUT pose-center band south into the verified-empty x 48–61, y 78–88 mm neighborhood and preserved the east dump cell. It was not another random search. The solve ended at its three-minute bound after 63,822 deterministic states.

## Measured improvement

All three output capacitors fit simultaneously under transformed F.CrtYd polygon collision with 0.25 mm clearance:

| Ref | Legal pose center (mm, degrees) |
|---|---:|
| `C_OUT1` | `(51.0, 92.0, 0)` |
| `C_OUT2` | `(56.0, 92.5, 90)` |
| `C_OUT3` | `(50.5, 87.0, 90)` |

This resolves the v1 `C_OUT1`/`C_IN2` allocation collision without moving the east dump cell or any unowned reference. It also demonstrates that the accepted southward VOUT allocation is useful; it does not establish routing or manufacturer-distance compliance.

The deepest joint partial additionally places:

| Ref | Legal pose center (mm, degrees) |
|---|---:|
| `C_IN1` | `(42.5, 96.5, 180)` |
| `C_IN2` | `(42.5, 100.0, 180)` |

The exact terminal JSON is `/tmp/crow-power-joint-cell-candidate-v3.json`. The frontier conflict census names `C_IN3` against `C_IN1` and `C_IN2`; `C_IN_HF` is not reached because the third bulk input capacitor cannot join that packing. The input center band is x 39–50, y 96–104.5 mm. Its upper edge is occupied by the invariant same-owner precharge cell `Q_PRE`, `Q_PRE_EN`, and `R_PRE_G`, while `U_BUCK` occupies its right/lower edge.

## Required upstream allocation change

The next source-owner decision is no longer an output-bank question. Preserve the three-cap VOUT allocation above and widen the VIN bank leftward/downward, or move the same-owner precharge cell as a group and revalidate its existing numeric rows. `Q_PRE`, `Q_PRE_EN`, and `R_PRE_G` cannot be moved implicitly: they are part of the previously accepted 47-row geometry. An admissible successor must explicitly allocate `C_IN1/2/3/C_IN_HF` with U_BUCK pins 3/4/18/19 and the PGND/EP-side current-return reservation, then re-run all 47 rows.

No full source patch is emitted because the deterministic construction stops at a five-part legal partial. The quiet/control pocket and `C_PWR_CT2` were not reached after the VIN frontier failed, so no claim is made about their final fit. The existing baseline 47/47 result remains valid only for baseline bytes; no revised 47-row receipt exists.

The full 89-ref scope remains open. In particular, `/tmp/crow-power-remaining26-obligations-terra.md` (SHA-256 `6143119c7db4f012b23736dc83494d1b2565137475e4efd60c37b902f63c057e`) still governs the hold-bank, LDO, timing, OPA, return, Kelvin, and thermal obligations. P3/FULL still owns actual VOUT/VIN loop copper, VCC/VLDO returns, FB Kelvin sense, AGND/PGND treatment, and thermal vias.

No board was saved or generated, no repository/source file was edited, and no routing or copper work occurred.
