# Power P2 qualitative source-backtrack — TPSM63603 cell

**Read-only in-memory proposal.** Baseline board is `crow_carrier.p2_input_power_source_backtrack_r1.kicad_pcb`, SHA-256 `c3d906591a343aea8949687c05c0f5ff4372e982c5af70a04df4828b7409fd93`; the active floorplan source identity is SHA-256 `744c0f2e6e8737969495b1febdf2f80a6406db21d63c066a238f5e4ffc51490f`. No board, source, attempt record, or prior audit was changed. Companion machine-readable pose input: `/tmp/crow-power-buck-p2-pose-hypothesis.json`.

## Result

This is a concrete **conditional P2 source pose** for the TPSM63603 cell. It improves the VCC, VLDO, FB, RT, and AGND satellite geography, but it is **not P2 accepted**: preserving all currently passed power rows and fixed islands leaves an exact pad-overlap allocation conflict between a proposed local output capacitor and `C_IN2`. The prior `47/47` numeric result remains valid for its rows; it must be described as numeric-only while this source backtrack is unresolved.

TI `TPSM63603` datasheet `02_parts/TPSM63603RDHR/TPSM63603_SLVSFS5A.pdf`, §7.3.11 (p.22) calls for a high-quality 1-uF VCC-to-AGND capacitor close to the device and permits a 0.1–1-uF VLDOIN ground capacitor for noise reduction. §§7.3.2–7.3.4 and §10 require local input/output capacitors, feedback taken at the regulation point, and layout minimizing noisy paths. These are qualitative placement/route obligations; no vendor distance has been invented here.

## Exact in-memory poses (mm, degrees)

`U_BUCK` `(47.500,97.500,0)` and `J_PWR` are retained anchors. The 13 satellites are:

| Ref | Proposed pose | Role |
|---|---:|---|
| C_VCC | 49.400, 93.000, 90 | VCC-to-AGND local capacitor |
| C_VLDO | 50.800, 93.000, 90 | VLDOIN-to-ground noise capacitor |
| R_BUCK_FB_TOP | 51.900, 93.100, 90 | regulation-point to FB leg |
| R_BUCK_FB_BOTTOM | 49.500, 91.300, 0 | FB-to-AGND leg |
| R_RT | 44.000, 90.700, 90 | quiet RT-to-AGND leg |
| R_AGND_JOIN | 44.000, 94.200, 90 | AGND-to-GND join |
| C_IN1 | 46.500, 92.100, 0 | input local bank (retained current valid pose) |
| C_IN2 | 54.000, 97.500, 0 | input bank (retained current valid pose) |
| C_IN3 | 41.000, 97.500, 0 | input bank (retained current valid pose) |
| C_IN_HF | 48.100, 102.500, 0 | input HF bank (retained current valid pose) |
| C_OUT1 | 52.600, 96.100, 90 | proposed nearest output capacitor |
| C_OUT2 | 41.000, 92.000, 0 | output bank (retained current valid pose) |
| C_OUT3 | 45.900, 88.100, 0 | output bank (retained current valid pose) |

The proposal intentionally does not move ADC/analog/other blocks, the 27 anchors, or 16 hold islands.

## Measured diagnostics (not limits)

Pad-centre spans to the exact functional U_BUCK pads in this pose: C_VCC pad 1 → U23 **1.651 mm**; C_VLDO pad 1 → U22 **2.580 mm**; FB-bottom pad 1 → U25 **3.896 mm**; RT pad 1 → U1 **4.232 mm**; AGND join pad 1 → U24 **3.501 mm**. Local bulk examples: C_IN1 VIN → U2 **3.692 mm**, C_OUT1 VOUT → U15 **3.598 mm**. These diagnose relative compactness only.

A front-pad AABB check finds 0.329 mm minimum against non-moved pads (`C_VCC.1` BUCK_VCC to U_BUCK.22 N5V_BUCK). It finds a **0.000 mm different-net moved-pair overlap**: `C_OUT1.1` (N5V_BUCK) with `C_IN2.1` (N12V_PROTECTED). This is a planning collision, not a fabricated clearance rule. The conditional pose must not be instantiated until it is removed and existing numeric rows are re-evaluated.

## Required P2 reservations; P3 proof

Reserve the following copper corridors now, without declaring them routed:

1. A short, wide local input loop from U2/U3/U4 and the nearby GND/EP side to the selected C_IN bank; keep it separate from AGND/FB/RT.
2. A local output loop from U7/U9–U15/U22/U30 to C_OUT1 and the output bank; do not pass that branch through the FB/AGND/RT corridor.
3. A quiet top/control corridor from U23 (VCC), U22 (VLDOIN), U25 (FB), U1 (RT), and U24/U27 (AGND) to their dedicated satellites. FB must leave the output regulation point and return to AGND without sharing the input/switch-current corridor.
4. Ground-return landing area beside the VCC/VLDO and control satellites; preserve a direct/short return option and do not consume it with the input/output high-current loops.

P3/FULL must prove the actual copper: input/output loop topology and width, VCC/VLDO ground returns, AGND handling, FB Kelvin/regulation-point sense, RT quietness, via transitions, and plane continuity. A positional reservation cannot prove these.

## Exact allocation decision needed

To realize C_OUT1 at `(52.600,96.100,90)` as the local output satellite, allocate a non-overlapping site for `C_IN2` or select another local C_OUT1 site and re-run the existing numeric ownership checks. `C_IN2` at `(54.000,97.500,0)` is in the conflict; it is a currently accepted power-row member, so moving it needs an upstream floorplan allocation plus numeric revalidation, not an implicit change. The other available approach is to retain C_IN2 and allocate an exclusive output-cap island below/right of U_BUCK, which would require moving/reserving the `C_PWR_CT2` neighborhood; that island is likewise fixed/owned. No ADC neighbor is implicated by either option.

## The remaining 26 qualitative refs

| Group | P2 placement/return reservation | P3/FULL routed proof |
|---|---|---|
| C_HOLD1…C_HOLD16 | Keep all 16 fixed hold islands and reserve their local bank-to-return corridors; do not reassign their area to buck loops. | Capacitor bank current sharing, hold-return paths, and via/plane continuity. |
| C_LDO_NR4, C_LDO_NR5, R_LDO_SET, R_LDO_PG_BOT_A/B | Preserve a quiet local NR/SET/PG pocket at the LDO; reserve direct ground-return room distinct from buck input/output loops. | LT3045 SET/OUTS/NR and EP return topology, Kelvin sense, and actual copper. |
| C_OPA_BULK, R_OPA_BLEED1/2 | Reserve downstream OPA bulk/bleed branch and its return; it is not a buck output capacitor substitute. | Downstream load/transient return route. |
| C_PWR_CT2, C_PWR_CT3 | Retain their fixed timing/supervision island and reserve its return corridor; do not place C_OUT1 into it. | Timing/supervisor return connectivity and noise isolation. |

Thus all 89 scoped power refs now have a disposition, but the qualitative classes are not all passed: this is a P2 placement/return reservation proposal with an identified allocation gate, followed by P3/FULL copper proof.
