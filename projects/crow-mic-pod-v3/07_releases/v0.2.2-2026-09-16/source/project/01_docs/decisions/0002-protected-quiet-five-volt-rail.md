# ADR-0002 — use 12 V input protection and derive a quiet linear 5 V rail

Status: accepted for first article
Date: 2026-09-01

## Decision

Place a 100 mA-hold, 250 mA-trip-at-25 °C resettable fuse, low-leakage series
1N4007(M7)SMA reverse-polarity rectifier, SMBJ15A shunt TVS and 4.7 kΩ/1206
protected-node pull-down ahead of an adjustable TPS7A4901DGNR. Set the LDO
nominal output to 5.024 V with 324 kΩ / 100 kΩ,
add 10 nF feed-forward and NR/SS capacitors, and use local ceramic input/output
bulk plus HF bypass. Tie EN to protected input and leave DNC open.

## Why

The pod load is small enough that a linear regulator avoids a switching node
and its emissions. TPS7A4901 tolerates the selected TVS clamp and the full 12 V
input range. Local PTC and diode make a single failed/miswired pod less likely
to collapse the carrier trunk.

## Consequences and holds

The 1N4007 drop and PTC resistance reduce LDO dissipation slightly but consume
headroom; even their worst credible drop leaves ample margin above 5 V at the
10.5 V pod-header floor (the carrier-header floor is 10.8 V before the final
harness drop). SMBJ15A coordination covers only the cited component waveform,
not lightning or complete-enclosure surge immunity. First article must measure
rail regulation, noise, load response, reverse polarity and temperature. D1's
published 50 µA maximum reverse leakage at 125 °C times R14's +1% resistance
bounds the protected node to -0.23735 V, inside U2's -0.3 V absolute limit;
the hot reverse-hookup test remains mandatory.

## Enforced invariants

- Series chain: `12V_POD` -> F1 -> `12V_FUSED` -> D1 -> `VIN_PROTECTED`.
- D1 pad 1/cathode is `VIN_PROTECTED`; D2 pad 1/cathode is `VIN_PROTECTED`.
- U2 pin 7 DNC is unconnected; EN is `VIN_PROTECTED`; OUT is `5V_QUIET`.
- R1/R2 are 324 kΩ/100 kΩ and define the governed output window; signed
  feedback-current corners widen it to 4.79–5.23 V.
- R14 is 4.7 kΩ and must remain directly across VIN_PROTECTED/GND.
