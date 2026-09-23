# ADC/reference P2 source proposal — full 64-ref scope

## Status and boundary

This proposal supersedes no evidence.  The accepted board is SHA-256
`c3d906591a343aea8949687c05c0f5ff4372e982c5af70a04df4828b7409fd93`; the
source baseline is floorplan SHA-256
`744c0f2e6e8737969495b1febdf2f80a6406db21d63c066a238f5e4ffc51490f`.
The frozen 17-ref patch remains a **numeric-subset** placement proposal only:
its 16 engineering-dossier rows predict 16 PASS and zero residual.  It is not
ADC P2 closure.

The source contract must add twenty qualitative P2 observation/reservation
rows.  Each names a capacitor, its exact ADC/pin, its observed non-ground-pad
span, and a disposition `local_cell_required`; it must not impose an invented
manufacturer millimetre threshold.  TI SBAS992A section 11.1/page 116 is the
authority: decouplers close to their pins, VREF capacitors near pin 3, capacitor
ground direct to AVSS pin 4 with no via, and a central local ground/EP plane
area with thermal vias.  Section 8.3.4/page 30 requires at least 1 uF from
VREF to AVSS.

## 64-ref review ledger

| Class | Refs | Source/layout obligation | Present observation and disposition |
|---|---|---|---|
| Numeric reset/VMID cell | `C_RST1,C_RST2,C_RST_T,C_VMID1_EXT_10U,C_VMID1_EXT_1U,C_VMID2_EXT_10U,C_VMID2_EXT_1U,Q_RST1,R_RESET_GPD,R_RESET_PU,R_RST_T,R_VMID1_BOT,R_VMID1_TOP,R_VMID2_BOT,R_VMID2_TOP,U_RST1,U_RST2` | Four dossier owners retain the exact 16 numeric rows. | Frozen proposed poses: 16/16 predicted PASS; must be rerun on the saved candidate. |
| A bypass/reference collar | `C_ADC_A_AREG_100N,C_ADC_A_AREG_1U,C_ADC_A_AVDD_100N,C_ADC_A_AVDD_10U,C_ADC_A_DREG_100N,C_ADC_A_DREG_1U,C_ADC_A_IOVDD_100N,C_ADC_A_IOVDD_10U,C_ADC_A_VREF_100N,C_ADC_A_VREF_10U` | Exact per-pin local-cell reservations; VREF pad 2 reserves same-side direct corridor to `U_ADC_A.4`. | See measured table; ungraded diagnostic spans, all require replacement placement observation. |
| B bypass/reference collar | `C_ADC_B_AREG_100N,C_ADC_B_AREG_1U,C_ADC_B_AVDD_100N,C_ADC_B_AVDD_10U,C_ADC_B_DREG_100N,C_ADC_B_DREG_1U,C_ADC_B_IOVDD_100N,C_ADC_B_IOVDD_10U,C_ADC_B_VREF_100N,C_ADC_B_VREF_10U` | Same as A, with direct VREF pad-2 corridor to `U_ADC_B.4`. | See measured table; ungraded diagnostic spans, all require replacement placement observation. |
| ADC control passives | `C_ADC_DIGITAL_BAD,C_ADC_DIGITAL_OK,C_ADC_PWR_BAD,C_ADC_READY,C_ADC_READY_BAD,C_ADC_START_DELAY,R_ADC_1V8_OK_BOT,R_ADC_1V8_OK_TOP,R_ADC_3V3X_OK_BOT,R_ADC_3V3X_OK_TOP,R_ADC_DELAY_GATE_PD,R_ADC_DIGITAL_OK_PU,R_ADC_DIG_RST_PD,R_ADC_PWR_BAD_PD,R_ADC_READY_PD,R_ADC_START_DELAY` | Place by their supervisor/delay net functional cell; preserve exact named numeric constraints where a ref is in the 17-ref cell, otherwise no manufacturer distance limit asserted. | 16 refs; no silent placement pass or source numeric budget. Re-observe topology and clearance after local ADC-cell placement. |
| ADC control active parts | `Q_ADC_DELAY_DISCH,Q_ADC_DIG_RST,Q_ADC_PWR_RST,U_ADC_1V8_OK,U_ADC_3V3X_OK,U_ADC_DIGITAL_BAD,U_ADC_PWR_BAD,U_ADC_READY,U_ADC_READY_BAD` | Keep reset/startup control separate from VREF/AVSS return corridors and switching copper. | 9 refs; no numeric row is presently applicable. Must be assigned an explicit cell/corridor disposition. |
| ADC converters | `U_ADC_A,U_ADC_B` | Own each ten-cap collar, VREF-return reservation, AVSS/EP ground-area and thermal-via handoff. | 2 refs; P2 owns placement reservations, P3/FULL owns saved copper/return proof. |

## Qualitative P2 observation rows

| ADC / capacitor pair | Pin | accepted-board diagnostic span mm |
|---|---:|---:|
| A AREG 100 nF / 1 uF | 2 | 8.310 / 6.029 |
| A AVDD 100 nF / 10 uF | 1 or 19 | 4.894 / 4.401 |
| A DREG 100 nF / 1 uF | 24 | 6.140 / 13.259 |
| A IOVDD 100 nF / 10 uF | 1 | 9.741 / 12.745 |
| A VREF 100 nF / 10 uF | 3 | 8.543 / 9.695 |
| B AREG 100 nF / 1 uF | 2 | 10.708 / 8.793 |
| B AVDD 100 nF / 10 uF | 1 or 19 | 4.894 / 4.401 |
| B DREG 100 nF / 1 uF | 24 | 6.140 / 12.324 |
| B IOVDD 100 nF / 10 uF | 1 | 9.341 / 6.547 |
| B VREF 100 nF / 10 uF | 3 | 6.002 / 9.906 |

These are observations only, not a pass/fail budget.  All listed capacitors
have GND on pad 2.  The VREF 10-uF nominal values meet the 1-uF minimum, but
only a later saved copper review can prove their pad-2-to-pin-4 direct/no-via
connection.

## Concrete local-cell allocation for the next source pass

Keep each ADC and its ten capacitors as one placement cell.  Reserve five
pin-facing satellites per ADC: the AREG pair at pin 2, AVDD pair at the pin-1/
19 supply side, DREG pair at pin 24, IOVDD pair at pin 1, and VREF pair at pin
3.  The VREF pair needs a dedicated same-side corridor from each capacitor's
pad 2 to AVSS pin 4; no reset/control pad, via, or unrelated return may occupy
that corridor.  Reserve the central EP/ground area for the later thermal-via
and plane connection, without adding vias or copper in P2.

This is an allocation instruction, not evidence of fit.  The present source
seeds form two horizontal capacitor strips around `U_ADC_A/B`; the measured
4.401–13.259 mm spans show that the strips do not yet demonstrate close
per-pin placement.  A bounded source candidate must physically pack the two
five-satellite collars while retaining body/courtyard clearance and the frozen
power/hold anchors.  Failure to pack one collar must name its blocking body or
reserved corridor; board-area arithmetic alone is not an impossibility proof.

P3/FULL must reopen the saved board for VREF-cap ground to AVSS pin 4 without
a via, EP/local-ground/plane and thermal-via implementation, return-current
separation, DRC, and actual route escape.  No P3, routing, P5, release, or
ordering claim follows from this proposal.
