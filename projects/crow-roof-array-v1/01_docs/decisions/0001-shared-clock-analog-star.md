---
id: 0001
date: 2026-09-01
status: accepted
---
# 0001 — Central shared-clock conversion of balanced analog home runs

## Context
The array needs stable inter-channel delay for localization, but the project
does not authorize custom firmware. The archived central board depends on an
unwritten XU316 application, while independent digital pods would introduce
clock synchronization and outdoor digital-power complexity.

## Options
- **Balanced analog home runs into simultaneous central ADCs** — one physical
  star cable per pod; a single indoor clock controls every sample.
- **Digital ADC at every pod** — shorter analog path, but requires distributed
  clock recovery/synchronization, firmware and harder outdoor power integrity.
- **One USB audio interface per pod** — readily available, but independent USB
  clocks are not a localization-grade time base without resampling evidence.
- **Reuse the archived XU316 central board** — rejected as a baseline because
  its application firmware is absent and its cable power map conflicts with
  the archived pod.

## Decision
Adopt balanced analog home runs and central simultaneous conversion on one
shared clock, using an unchanged vendor USB-audio module at the host boundary.

## Consequences
The pod needs a low-noise balanced driver and local power filtering; cable
common-mode rejection and entry protection become first-order. The central
carrier needs one simultaneous multichannel ADC, explicit clock handling, and
a cross-board pin contract tested against both ends. Reversing this decision requires reopening
the firmware capability profile and synchronization validation plan.
