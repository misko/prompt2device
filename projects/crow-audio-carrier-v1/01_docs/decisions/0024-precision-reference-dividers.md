---
id: '0024'
date: 2026-09-09
status: superseded by ADR0025
tags: [analog, topology]
---
# ADR-0024 — precision dividers for the retained reference acceptance window

## Context

Historical decision. ADR0025 replaces this complete rail/reference arrangement
with eight shared-rail amplifiers and passive1k precision bias dividers. Its
current invariants own the retained amplifier/precision requirements and the
changed topology; the original decision below is preserved for provenance.

The existing first-article VMID acceptance window remains binding. The prior
independent initial-tolerance divider corners already crossed its lower edge
at the admitted low ADC rail, before capacitor leakage and amplifier offset.
ADR0023's larger output isolator makes the leakage contribution more visible.
This is a source margin defect, not a measured hardware failure or a demand
for audio during power-off. The room-temperature arithmetic and its limits
are recorded in research/2026-09-09-reference-loading-and-model-authority.md.

## Options

- Retain the original equal1percent dividers: no new footprint work, but the
  known initial DC screen does not support the retained acceptance window.
- Reuse RT0603BRD0710KL/C95204: the board already uses this exact10k,
  0.1percent,25ppm/C,0603 YAGEO part in both supervisor dividers. Preserves
  nominal ratio and time constants while reducing independent initial spread.
- Change nominal divider ratio or alter the reference-buffer feedback:
  unnecessary for the demonstrated initial-tolerance issue, and would change
  nominal bias or introduce additional retained-charge feedback paths.

## Decision

Use RT0603BRD0710KL/C95204 for R_VMID1_TOP, R_VMID1_BOT, R_VMID2_TOP and
R_VMID2_BOT. Preserve each10k nominal value, separate bank topology, all
capacitors, the ADR0023 input/output limiters and raw-side follower feedback.
Use the0603 source footprint and verify its larger geometry against all
source-native-library parts. No placement rule or acceptance limit is relaxed.

This supersedes only ADR0008's external-divider resistor identity/tolerance;
its topology intent and ADR0023's current limiting remain. Primary authority
is YAGEO RT V17,2026-02-12 p2 ordering code and p4 geometry, already bound in
the existing dossier. Public exact-part sourcing was rechecked at the new
six-per-board total before adoption; this is not PCBA allocation.

## Consequences

Source population, pin census and connected nets do not change. The four
larger footprints require regenerated native geometry and fresh review before
routing. Exact identity, initial DC arithmetic and source geometry have
separate regressions; the arithmetic is not a new power-transient model or
closure of CAR-F12. No recurring-investigation milestone/budget is reset.

Panasonic's reference-capacitor leakage specification is conditional on its
room-temperature test. Installed leakage, temperature, reflow/endurance drift,
reference settling and audio performance remain explicit physical/source
obligations at their existing boundaries. Neither the precision part nor its
initial-tolerance calculation guarantees hot/lifetime production acceptance.
The source change preserves the full signal/spoke envelope and does not
authorize release, order, publication or a change to the microphone pod.
