# Adjustable TPSM63603 5 V rail: bounded load closure

Research cut 2026-09-23. Source under review is isolated commit `5771d60b` at `/home/mouse9911/gits/circuits-worktrees/crow-stocked-power-candidate`; no source, contract, or PCB was edited for this review. **Verdict:** the candidate divider has no demonstrated DC incompatibility with the enumerated consumers and the declared 1.9 A operating allocation can cover them. It is **not yet a qualified 4.942–5.099 V power source**: TI does not guarantee that exact output range over the full 1.9 A/temperature conditions; thermal resistance on the selected 1 oz board, revised capacitor bias, and source startup/hold sequencing have not been established. These are bounded engineering tasks, not a firmware-authoring prerequisite. Preserve the candidate, but do not merge it as an accepted power contract or sealed release yet.

## Exact source load census

The tscircuit source generated at commit `5771d60b` had 495 source components matching its 495-reference manifest. Its `N5V_BUCK` source traces reach **21 references**:

| Role | Exact direct references | DC load treatment |
|---|---|---|
| Module and feedback | U_BUCK, R_BUCK_FB_TOP | Module output; top divider draw ≤5.099/50.2k = **0.102 mA**; bottom returns to BUCK_AGND. |
| Three converter VINs | U_3V3X, U_1V8, U_CORE | Output-envelope arithmetic below; 85% efficiency is the **declared engineering allocation**, not a TI guaranteed efficiency floor. |
| Digital rail monitors | U_1V8_OK, U_XU_3V3_OK | VDD/MR at 5 V. TI TPS3890 supply maximum 5.5 V, 6.5 µA each at 5.5 V across full-temperature table; ≤**0.013 mA** for both. SENSE pins watch 1V8/3V3X, not 5V_BUCK. |
| Analog threshold | R_PWR_TOP | 30.9k/10k divider draws ≤5.099/40.9k = **0.125 mA**; PWR_SENSE feeds U_PWR on the held rail. |
| Held analog branch | D_HOLD | B340A Schottky to `5V_LDO_FEED`, then `R_PRE` (22 Ω) in parallel with enabled `Q_PRE` to `5V_LDO_HOLD`. It is the sole substantial direct analog branch. |
| Storage/bypass, no continuous nominal load | C_OUT1–3, C_U_3V3X_IN_1/2, C_U_1V8_IN_1/2, C_U_CORE_IN_1/2, C_1V8_OK_VDD, C_XU_3V3_OK_VDD, C_VLDO | Charging and leakage still matter at startup; 141 µF module output bank plus 60 µF three-converter input bank nominal, before three small bypasses. |

Downstream source inspection of `5V_LDO_HOLD` reaches LT3045 `U_LDO` input, two 470 µF hold capacitors, C_LDO_IN, eight `U_ISO1..8` TMUX supplies and their local bypasses, `U_PWR`/`U_AUDIO` supervisors, `U_DUMP`/`U_LDO_EN` Schmitt logic, their pull-ups/dividers and capacitors. The LT3045 then supplies `3V3_ADC`, including the existing ADC, sixteen OPA channels, ADC-side supervisors/logic and reference networks. No XU316 pin or digital core supply is wired directly to 5V_BUCK; it is accounted for through the three TPS62825 outputs. USB VBUS is sensing only. This is a source census, not a routed-board or stale prose assumption.

## DC current and voltage at adverse corners

Candidate divider: 40.2k/10k 0.1% YAGEO, 25 ppm/°C each, TI nominal 1.0 V FB. Independent adverse resistor tolerance, opposite 100°C TCR drift, and TI ±1% VFB term give a **screen** of 4.94204–5.09872 V (nominal 5.020 V). The VFB accuracy condition in [TI SLVSFS5A §6.5](https://www.ti.com/lit/ds/symlink/tpsm63603.pdf) is VOUT=1 V, zero load, 200 kHz; load/line regulation numbers are typical. Thus 4.942–5.099 V is not a guaranteed all-load output limit without a separately justified margin and measurement.

At 4.94204 V input and each declared output/current upper allocation, using the power-tree's 85% efficiency screen:

| Branch | Calculation | 5 V input current |
|---|---:|---:|
| 3V3X | 3.333 V × 1.00 A /(0.85 × 4.94204 V) | **0.7934 A** |
| 1V8 | 1.818 V × 0.30 A /(0.85 × 4.94204 V) | **0.1298 A** |
| 0V9 | 0.920 V × 1.20 A /(0.85 × 4.94204 V) | **0.2628 A** |
| Digital total | | **1.1861 A** |
| 3V3_ADC LT3045 | 0.250 A output + deliberately adverse 0.025 A ground-current allowance from the 500 mA table | **0.2750 A** |
| Direct dividers/monitors | 0.102 + 0.125 + 0.013 mA, plus 3×10 µA TPS62825 no-load IQ if charged separately | **<0.001 A** |
| Held controls | 8×140 µA TMUX maximum =1.12 mA; two supervisors, two Schmitt supply currents and asserted pull-ups are under a few additional mA | **reserve 0.005 A** |
| Total screen | | **≤1.4671 A**, leaving **≥0.4329 A** against 1.9 A |

The 0.25 A quiet output allocation includes its downstream OPA/ADC/resistor loads; do not add the 16.5 mA OPA bleed or VCM divider again. The 25 mA LT3045 ground-current number is specified at 500 mA, not strictly proven monotonic at 250 mA, so it is an explicit conservative project allowance requiring measurement. The three TPS62825 10 µA maxima are no-load, non-switching values; a true 85% *total* conversion efficiency would already include them. Charging them again is harmless reserve. This calculation uses all specified rail upper current limits and therefore does not depend on a firmware image.

Hard voltage windows admit the screened endpoints: [TPS62825 SLVSEF9I](https://www.ti.com/lit/ds/symlink/tps62825.pdf) VIN 2.4–5.5 V; [TPS3890 SLVSD65A](https://www.ti.com/lit/ds/symlink/tps3890.pdf) VDD 1.5–5.5 V; 5V_BUCK-side CL21A106KOCLRNC input capacitors 16 V, CKG57K output bank 25 V. Held-rail [TMUX2821](https://www.ti.com/lit/ds/symlink/tmux2821.pdf) VDD 1.8–5.5 V and [74LVC1G14](https://assets.nexperia.com/documents/data-sheet/74LVC1G14.pdf) VCC 1.65–5.5 V see only a diode-lowered voltage. The 10 V hold capacitors also fit. The Schottky/Q_PRE path must keep LT3045 input at or above the current 4.10 V engineering floor: at 4.942 V buck minimum the **combined hot D_HOLD + Q_PRE drop budget is 0.842 V**. ADI Rev D guarantees at most 0.35 V LT3045 dropout at 300 mA, so 4.10 V input leaves ≥0.37 V over the 3.38 V analog output maximum plus dropout. The B340A 0.5 V maximum Vf is only specified at 3 A/25°C; AO3401A 85 mΩ maximum RDS(ON) at –2.5 V is also a 25°C datum. An all-hot drop bound or loaded measurement is needed before promoting this path.

`R_PWR_TOP`/`R_PWR_BOT` still sense the buck itself. Their nominal 1.15 V TPS389001 threshold occurs at 4.7035 V buck. Allowing ±1% supervisor threshold and opposite 0.1% divider errors gives approximately **4.649–4.758 V** buck trip, with at most ~3 mV extra buck uncertainty from the cited 100 nA SENSE leakage. Even the candidate's screened 4.942 V minimum is >0.18 V above the upper trip; no value change is indicated for R_PWR_TOP/BOT on the DC screen. It does not establish power-up/down timing.

## Thermal and startup gate

At the *allocated* 1.9 A, 5.09872 V, 85% efficiency and 70°C ambient, module loss is `5.09872×1.9×(1/0.85−1)=1.7096 W`; to stay under TI's 125°C junction ceiling the realized board needs **θJA ≤32.17°C/W**. This tightens the prior 5.0 V/1.9 A threshold 32.81°C/W. TI's cited 33.5°C/W measurement uses its four-layer **2 oz outer-copper** test board; the selected Crow board uses 1 oz and has no measured θJA. The estimated 1.467 A branch total would relax the threshold to roughly 41.6°C/W, but the contract reserves 1.9 A and transient/unspecified loads can consume margin. Do not silently replace the allocation with 1.467 A.

TI TPSM63603 soft-start time to 90% VREF is 3.5–7 ms; the module output capacitor bank's 3×47 µF and six 10 µF digital input capacitors are **201 µF nominal**, about **235 µF** at positive 20%/10% tolerances. A simple 235 µF×5.099 V/3.5 ms ramp is 0.343 A average charge current. The held 940 µF bank is behind 22 Ω until `Q_PRE` enables, so initial current is at most 5.099/22=0.232 A when treating Schottky drop as zero. Its nominal RC time constant is 20.68 ms, requiring about **103 ms for five time constants**. U_PWR's 1 µF CT and 0.9–1.35 µA charge current may delay Q_PRE sufficiently; at 1.17 V minimum CT threshold, effective C_CT must exceed about **0.119 µF** for a 103 ms delay at 1.35 µA. Exact C_CT DC-bias retention and MR/VDD/reset ordering must be checked. Three TPS62825 output banks hold another six 47 µF parts; a 1.25 ms **typical**, not bounded, regulator soft start adds approximately 0.16 A parent input charge average at +20% capacitors. These are charge estimates, not peak-switch-current bounds. The full simultaneous startup could exceed the remaining 0.433 A steady allocation, yet stay below TPSM's 3 A output headline; scope and sequence it under worst available load and hot/low VIN. TI's min 5.6 A high-side switch limit is a switch-current parameter, not a license to claim 5.6 A 5 V output.

## Minimum candidate-qualification work

1. Revise the **candidate** power-tree TPSM identity and parent voltage screen, propagate it to the three TPS62825 VIN rows and the LT3045 parent, and recalculate the PWR_SENSE/hold-drop, capacitor voltage-bias and thermal allocations. Keep the existing 1.9 A hardware envelope unless a reviewed requirement changes it. Add an explicit qualified all-load 5 V range; do not relabel the algebraic 4.942–5.099 V divider screen as a manufacturer guarantee.
2. Demonstrate the selected 1 oz copper/thermal-via realization meets θJA ≤32.17°C/W at 1.9 A and 70°C, or revise the power stage/board cooling to do so. Validate 5V_BUCK ripple, loaded setpoint, start-up, load step and thermal across 11.006–13.2 V protected input and temperature range. The still-unqualified output-cap bank and TPS62825 input-bank DC-bias conditions must be re-screened at 5.10 V, then measured.
3. Establish `D_HOLD+Q_PRE` hot drop ≤0.842 V at 0.275 A input allowance and verify ≥4.10 V held rail under 4.942 V buck minimum. Prove C_PWR_CT effective capacitance/delay, precharge completion before Q_PRE bypass, and quiet-rail/ADC reset/TMUX sequencing during normal start, brownout and rapid restart. This is the existing architecture's already-required physical gate, now with the new voltage extremes.
4. On the final board, verify the two new FB resistor lands and the preserved RDH0030A module geometry at the output-capacitor sense node and AGND join. Re-run source-to-native and supplier allocation gates; no generated native PCB or fab claim follows from the TSX census.

**No extra 6 V converter or firmware-specific current estimate is required to establish the DC architecture on the declared 1.9 A envelope.** The remaining barriers are the precise all-load voltage, hot precharge/hold, capacitor and 1 oz thermal evidence above. Primary local PDFs: TI SLVSFS5A, TI SLVSEF9I, TI SLVSD65A, ADI LT3045 Rev D, TI SCDS488 and the cited exact diode/FET dossiers in `projects/crow-usb-carrier-v1/02_parts` of the isolated worktree.
