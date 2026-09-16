---
schema: 1
kind: pcb-human-report
report_id: 2026-09-01-design-math
title: Crow microphone pod v3 first-article design math
subtitle: Cable loss, quiet-rail corners, audio gain and explicit qualification limits
project: crow-mic-pod-v3
date: 2026-09-01
status: DRAFT
evidence_status: INCOMPLETE
---

## Executive conclusion

**INFERRED:** The selected 12 V cable and 18/11 V/V balanced-audio topology have
comfortable nominal DC-drop and ADC-level margins for a first article. They do
not yet prove long-cable noise/stability, capsule loading, headroom, polarity or
roof-environment performance, so the board remains DO NOT ORDER.

## Question and scope

This report asks whether the frozen 15 m electrical boundary is arithmetically
compatible with the selected cable, LDO and analog gain. It covers only values
derived from exact component documents and does not qualify an assembled pod,
harness, carrier or enclosure.

## Evidence boundary

**DATASHEET:** Belden 6541PA supplies conductor resistance and capacitance; TI
TPS7A49 supplies reference/output constraints; PUI AOM-5024L-HD-R supplies the
nominal sensitivity, tolerance and characterized 3 V / 2.2 kΩ circuit.
**OWED:** effective capacitance, capsule current/sensitivity under the selected
bias, output headroom, acoustic polarity, common mode and 4 m/15 m cable
measurements.

## Findings

### Input cable

Belden specifies 53.8 Ω/km maximum conductor DC resistance. At 15 m, a
two-conductor power loop is 30 m:

`Rloop = 53.8 Ω/km * 0.030 km = 1.614 Ω`.

At the 0.10 A maximum-continuous allocation, cable drop is 0.161 V. At the
expected first-article ceiling of 0.020 A it is about 32 mV. The frozen system
allows 2.2 Ω including contacts, preserving a 10.5 V pod minimum from the
10.8 V carrier-header minimum at 0.10 A.

### LDO setpoint and dissipation

Nominal: `1.185 * (1 + 324000 / 100000) = 5.0244 V`.

Using the datasheet's ±2.5% overall reference accuracy, independent 1%
resistor corners and signed `IFB=-100..0 nA` gives a calculated
4.7926–5.2295 V window, conservatively declared 4.79–5.23 V. At 13.2 V,
20 mA and 5.0 V output, `P ≈ (13.2 - 5.0) * 0.020 = 0.164 W`. Series
protection consumes part of the input loss, so this slightly overstates LDO
dissipation. The dossier's 300 mW board-specific ceiling is derived from TI's
DGN `RθJA = 63.4 °C/W`: even at a deliberately conservative 105 °C calculation
point—35 °C above the project's admitted +70 °C operating boundary—it predicts
a 19.02 °C rise and about 124.0 °C junction, just below the 125 °C recommended
junction ceiling. It is not presented as a TI fixed package-power rating;
actual enclosure temperature, copper and airflow remain a measured
first-article hold.

### Audio level

Capsule nominal sensitivity -24 dBV/Pa is 63.1 mVrms/Pa. A 110 dB SPL sine is
6.32 Pa rms (`20 µPa * 10^(110/20)`). **INFERRED:** capsule output is about
0.399 Vrms, giving about 0.653 Vrms after 18/11 V/V differential gain. At the +3 dB
sensitivity corner the estimate is 0.923 Vrms. Independent 1% corners on both
gain ratios produce a 1.686 V/V worst modeled differential ratio and 0.952
Vrms, 2.02 dB below the 1.2 Vrms pod limit. Bias/load behavior and distortion
make these planning estimates only.

### Capsule bias condition and rail filtering

The datasheet characterizes the capsule at a 3 V supply with 2.2 kΩ load and
reports 0.5 mA consumption under that condition. R3 = 3.9 kΩ therefore drops
1.95 V at the reported current, leaving 3.07 V from the 5.024 V nominal quiet
rail at the top of R4 = 2.2 kΩ. C7 = 100 µF makes R3/C7 a nominal 0.41 Hz
low-pass, about 43.3 dB down at 60 Hz using the -1% resistor corner. Even a
10 µF effective capacitor would give about 23.3 dB at 60 Hz before the
TPS7A49's own rejection. The design does not assert 10 µF as a guaranteed
MLCC floor; effective capacitance and residual microphone-rail ripple remain
first-article measurements.

### Differential polarity and exact gain

Let `x = MIC_AC - VREF` and `k = 18k/22k = 9/11`. The inverting preamp gives
`PRE_OUT = VREF - k*x`. The equal-resistor U1C stage gives
`OUTP_DRV = 2*VREF - PRE_OUT = VREF + k*x`; R13 is driven directly by
`PRE_OUT = VREF - k*x`. U1D is parked as a private VREF follower rather than
buffering the swinging negative leg. The equal 100 ohm output resistors do not
change the unloaded ratio, so:

`AUDIO_P - AUDIO_N = 2*k*x = (18/11)*x`.

This proves the schematic's positive algebraic polarity. It does not prove the
capsule's acoustic terminal polarity, which remains a physical qualification.

### OPA1679 headroom

At the modeled 0.952 Vrms worst-case differential output, independent gain
ratio corners put the larger complementary leg below 0.481 Vrms or 0.681 V
peak. Combining that with the independently conservative 2.35-2.65 V
common-mode envelope gives approximately 1.669-3.331 V. At the lowest
quiet-rail corner of 4.79 V, the upper output keeps 1.459 V to the positive
rail and the lower output keeps 1.669 V to ground. Both exceed the datasheet's
0.8 V guaranteed loaded-output boundary by more than 0.5 V.
Clipping remains a first-article measurement, but is no longer the nominal
corner on which contract compliance depends.

OPA1679 input common mode is `Vminus+0.5` through `Vplus-2`. Against a 4.79 V
rail, its upper boundary is 2.79 V; the 2.65 V maximum VREF declaration retains
0.14 V. U1B and U1C keep both signal inputs near virtual VREF, while U1D is a
fixed-VREF follower. No op-amp input is forced to track the swinging PRE_OUT
waveform against the common-mode limit.

### Current budget

OPA1679's full-temperature maximum quiescent current is 2.8 mA per channel, or
11.2 mA for four channels. Add the capsule's reported 0.5 mA at the 3 V/2.2 kΩ
condition, about 0.114 mA in
the VREF divider, about 0.012 mA in the LDO divider, about 2.55 mA in R14 at
the highest normal protected-node voltage, and a conservative
0.8 mA LDO ground-current allowance (the datasheet typical at 100 mA output):
the static planning total is about 15.18 mA. The 20 mA first-article ceiling
therefore retains roughly 4.8 mA for signal drive, leakage and uncertainty;
the 100 mA spoke allocation is a fault/delivery ceiling, not predicted load.

### Protection coordination

Normal 13.2 V stays 1.8 V below SMBJ15A's 15 V standoff. Its 24.4 V maximum
10/1000 us clamp, multiplied by the explicit 10% coordination margin, is
26.84 V. That remains 8.16 V below TPS7A4901's 35 V recommended maximum and at
least 13.16 V below the F1/50 V capacitor bounds; D1 is rated to 1000 V.
The public SMBJ figure is a component test at 24.6 A, not the admitted source:
this design is restricted to a prospective source current no greater than
F1's 10 A rating, and exact carrier/COTS proof remains an order hold. C2 is the exact
50 V `CC0402KRX7R9BB104`; the initially proposed 16 V bypass was rejected
because it could not survive the admitted clamp envelope. Input capacitance is
10.1 uF nominal versus the frozen 47 uF maximum.

For reverse hookup, D1's public 125 °C reverse-leakage maximum is 50 µA.
R14's +1% corner is 4.747 kΩ, so `50 µA * 4.747 kΩ = 0.23735 V`; the protected
node remains above U2's -0.3 V absolute minimum. This is an analytic bound,
not permission to skip the hot reverse-polarity first-article test.

### Cable capacitance

`90.2 pF/m * 15 m = 1.353 nF` conductor-to-conductor. Two 100 Ω series output
resistors make 200 Ω differential source resistance, for
`fc = 1 / (2*pi*200*1.353nF) ≈ 588 kHz`. This supports the topology but does
not qualify op-amp stability or EMC.

## Recommendations

**PROPOSED:** Keep the 18/11 V/V inverting-preamp topology, characterized capsule
load, matched 100 Ω output parts and the 15 m qualification fixture. Do not
increase gain until measured capsule sensitivity, distortion and carrier noise
establish that the extra level is useful and safe.

## Validation plan

- **OWED:** sweep 10.5–13.2 V and 0–20 mA while measuring rail regulation,
  ripple and temperature.
- **OWED:** measure gain, phase, common mode and clipping with a capsule
  simulator, then the exact capsule.
- **OWED:** repeat noise, CMRR, stability, ESD/EMC and polarity checks with
  exact 4 m and 15 m harnesses and the carrier receiver.

## Source register

- [Belden 6541PA technical data](https://catalog.belden.com/techdata/EN/6541PA_techdata.pdf)
- [TI TPS7A49 datasheet](https://www.ti.com/lit/ds/symlink/tps7a49.pdf)
- [PUI AOM-5024L-HD-R specification](https://puiaudio.com/file/specs-AOM-5024L-HD-R.pdf)
- [TI OPA1679 datasheet](https://www.ti.com/lit/ds/symlink/opa1679.pdf)
