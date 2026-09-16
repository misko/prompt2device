# ADR-0003 — use an 18/11 V/V active-balanced audio topology at 2.5 V common mode

Status: accepted for first article
Date: 2026-09-01

## Decision

Use OPA1679IDR to buffer half-supply VREF, amplify the
AC-coupled microphone signal inverting by 9/11 with 22 kΩ input / 18 kΩ
feedback, and restore polarity through an equal-10 kΩ inverter for `AUDIO_P`.
The already low-impedance preamp output drives complementary `AUDIO_N`
directly through its 100 Ω source resistor. The fourth channel is parked as a
private VREF follower, with no paralleled output. This keeps every
signal-bearing input near VREF and avoids exceeding OPA1679's `(V+) - 2 V`
input common-mode limit. Each cable leg has 100 Ω source resistance. The pod
output is DC-coupled with 2.5 V nominal common mode; the carrier alone
owns the two 1 µF coupling capacitors into its 100 kΩ-to-VMID receivers.

## Why

Active-balanced drive reduces sensitivity to common-mode cable pickup while
keeping a simple, low-power four-wire node. Differential gain of 18/11 V/V maps the
nominal -24 dBV/Pa capsule to about 0.653 Vrms differential at 110 dB SPL and
about 0.923 Vrms at the capsule's +3 dB sensitivity corner. Even independent
1% gain-resistor corners remain below 0.96 Vrms, retaining at least 2.0 dB to
the frozen 1.2 Vrms pod-output ceiling and 6.4 dB to the ADC's 2.0 Vrms full
scale. The ADC still retains far more dynamic range than the 80 dB-SNR capsule.

## Consequences and holds

OPA1679's input common-mode/output-swing limits, actual capsule loading and
long-cable capacitive load still need bench proof. Simultaneous crows need not
be separated, but identity must remain
stable within a 120-second recording while the crow stays approximately still;
that algorithmic requirement is outside this analog PCB.

## Enforced invariants

- U1B input/feedback are 22 kΩ/18 kΩ (inverting 9/11 gain).
- U1C input/feedback resistors are equal 10 kΩ (polarity-restoring unity leg).
- R13 is driven directly from U1B `PRE_OUT`; no second signal buffer is used.
- U1D is a private VREF follower and its output is not paralleled or exported.
- AUDIO_P/AUDIO_N each have one 100 Ω series resistor and no series capacitor.
- U3 clamps only AUDIO_P/AUDIO_N; its NC pins remain unconnected.
