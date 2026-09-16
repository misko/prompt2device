# Architecture

## Signal and power flow

```text
RJ45 J1 pins 1/3/7 (+12V_POD)
  -> F1 0.10 A hold PTC
  -> D1 low-leakage Vishay S1M series reverse-polarity rectifier
  -> D2 SMBJ15A shunt TVS + R14 reverse-leakage pull-down + input bulk
  -> U2 TPS7A4901 adjustable LDO
  -> 5V_QUIET

5V_QUIET -> R3 3.9k / C7 100u filtered nominal 3 V capsule supply
          -> R4 2.2k -> AOM-5024L-HD-R -> AC coupling
          -> buffered 2.5 V VREF -> U1B inverting gain -9/11
          -> U1C polarity restore AUDIO+ --- 100 R -> J1 pin 5
          -> U1B low-Z PRE_OUT AUDIO- -------- 100 R -> J1 pin 4
                                             |       |
                                  U3 dual ESD clamp to GND

U1D is parked as a private VREF follower; it carries no signal and its output
is not paralleled with U1A or any other amplifier.
```

J1 pins 2/6/8 carry the spoke return. Shell pads 9/10 join the isolated
POD_SHIELD island, which remains separate from GND. The factory cord shield
is continuous to carrier CHASSIS; its panel bond requires qualification.

F1 (`0ZCJ0010FF2E`) is the downstream-board protection tier: 0.10 A hold and
0.25 A trip at 23 °C. The carrier's exact `1812L035/60MR` branch part is the
cable/pre-pod tier with a 0.70 A trip ceiling. This ordering is intentional,
but thermal PPTCs do not guarantee selectivity from those two numbers alone;
hot/time-current coordination, source foldback and one-fault/seven-healthy
operation remain first-article holds.

## Quiet rail

TPS7A4901 uses 324 kΩ over 100 kΩ around its nominal 1.185 V reference:

`VOUT = 1.185 V * (1 + 324k / 100k) = 5.024 V nominal`.

With reference, 1% divider and signed -100–0 nA feedback-current corners, the
governed envelope is conservatively declared 4.79–5.23 V. EN is tied to the
protected input. DNC is left open.
The input and output each receive local ceramic bulk and 100 nF HF bypass;
NR/SS receives 10 nF and the feedback top resistor receives 10 nF feed-forward.

This is a low-power linear stage, not a switching converter. At the board's
20 mA first-article current ceiling and 13.2 V input, conservative dissipation
is about 164 mW before diode/PTC loss. Temperature rise is still a measured
first-article obligation because copper area and enclosure ambient dominate it.
The powered pod and its component-level transient envelope are admitted only
from -30 to +70 °C, matching the exact capsule operating range. Roof solar
rise, enclosure temperature and condensation remain system/first-article
holds; operation outside that range is not claimed.

## Audio transfer

R3/C7 low-pass the quiet rail before R4 biases the microphone. At the PUI
datasheet's 0.5 mA observation, 3.9 kΩ drops 1.95 V and presents about 3.07 V
at the top of the 2.2 kΩ capsule load. That intentionally reproduces the
datasheet's characterized 3 V / 2.2 kΩ circuit instead of treating the
capsule's 2.2 kΩ output impedance as though its sensitivity were independent
of load. The nominal R3/C7 pole is 0.41 Hz; effective MLCC capacitance and
actual rail ripple remain measured holds.

The capsule signal is AC-coupled and biased to buffered VREF. U1B uses a
22 kΩ input resistor and 18 kΩ feedback resistor for inverting 9/11 gain while both inputs
stay near VREF, inside OPA1679's limited input common-mode range. U1C uses equal
10 kΩ resistors to restore polarity for AUDIO_P; the already low-impedance U1B
output drives AUDIO_N through R13 directly. U1D is a private VREF follower so
no signal-bearing input sees the large PRE_OUT swing. Differential gain is
therefore 18/11 V/V, approximately 1.636 V/V.

Using the capsule's nominal -24 dBV/Pa sensitivity, a 110 dB SPL sine is about
0.399 Vrms at the capsule and about 0.653 Vrms differential after gain. At the
capsule's +3 dB sensitivity corner the estimate is about 0.923 Vrms. Independent
1% gain-ratio corners give a conservative 1.686 V/V maximum and about 0.952
Vrms, retaining 2.0 dB to the frozen 1.2 Vrms pod-output ceiling. Clipping,
linearity and the capsule current/supply relationship remain bench holds.

The selected Weidmüller cord has no established pair-capacitance value in
the accepted source packet. Do not reuse the former Belden capacitance or RC
pole. Measure the complete cord's capacitance, gain, relative phase, noise
and stability with both 100 Ω output resistors and concurrent power loading.

## Ground and layout intent

- A continuous ground plane is the analog return; do not split it.
- J1, F1, D1, D2, R14, input bulk and U3 form the exposed boundary cluster.
- U2 input/output capacitors sit against their pins with short ground return.
- VREF divider, reservoir and U1A stay together; MIC_RAW/MIC_AC stay away from
  the connector power path and both audio outputs.
- AUDIO_P and AUDIO_N are routed together with symmetric series resistors and
  no deliberate length skew. They are ordinary audio nets, not controlled
  impedance.
- MK1 is a wire landing at the quiet end of the board, not a capsule footprint.

## References

Exact manufacturer documents and pin/rating extracts live in `02_parts/`.
The parent/child interface is frozen in `03_src/rules/spoke_interface.yaml`.


## Adopted factory RJ45 spoke — 2026-09-12

The adopted source uses Würth 615008160221 nonmagnetic shielded 8P8C
jacks and complete Weidmüller 8909650150 factory 15 m Cat6A S/FTP PUR cords.
Pins 1/3/7 carry +12 V, 2/6/8 return, 5 AUDIO+ and 4 AUDIO−. Shell pads
9/10 join carrier CHASSIS or pod POD_SHIELD; neither net connects to circuit
GND. The pod shield island is isolated from circuit ground, not disconnected
from the cord shield. These ports carry custom analog audio and power;
label them “POD AUDIO +12V / NOT ETHERNET OR POE” and mate with power off.
No field crimps, splices or pigtails belong to this spoke assembly.

Exact manufacturer STEP establishes a nominal complete plug end of
57.98 × 13.70 × 18.456687 mm and a 22.986 mm nominal grip diameter.
These are nominal CAD envelopes, not manufacturing or installed-service
limits. Cable OD is 6.1–6.5 mm; retain the 67 mm bend planning floor.
The three parallel power pairs give the conditional hot-loop screen
`290 Ω/km × 0.015 km / 3 × 1.25 + 0.300 Ω = 2.1125 Ω`, hence
10.58875 V at 0.10 A from 10.8 V. Contact allowance, finished-loop resistance,
power sharing, fault behavior, mating/service and environmental performance
remain measured obligations. UV is unestablished; PUR alone is not evidence.
The source adoption is recorded in the carrier schematic journal at
2026-09-12 20:08 UTC. Native review, routing and release are separate gates.
