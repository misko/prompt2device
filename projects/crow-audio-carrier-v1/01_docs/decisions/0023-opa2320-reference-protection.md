---
id: '0023'
date: 2026-09-09
status: superseded by ADR0025
tags: [analog, protection, topology]
---
# ADR-0023 — OPA2320 on the existing rail with retained-reference protection

## Context

Historical decision. ADR0025 replaces this complete rail/reference arrangement
with eight shared-rail amplifiers and passive1k precision bias dividers. Its
current invariants own the retained amplifier/precision requirements and the
changed topology; the original decision below is preserved for provenance.

The OPA1656 upper common-mode restriction invalidated the prior full-range
linear shutdown model before the assumed isolation interval ended. Leaving a
model's valid domain is not itself hardware damage, and valid audio during
shutdown is not a new requirement. The source needed an amplifier/protection
choice with more credible headroom while preserving BRIEF G2/G3, A2/A5, T4
and D6: eight channels, 1.2 Vrms differential and eight 0.10 A spokes.

The independent fresh source-part review of commit4885a4a9 recommended
IMPLEMENT_WITH_EXPLICIT_SOURCE_OBLIGATIONS. It identified direct retained
VMID_EXT capacitor paths to U_AFE9 positive inputs and inadequately limited
VMID_BUF return paths. It did not grant source engineering or native approval.

## Options

- Keep OPA1656: retains the restrictive upper common-mode boundary. The prior
  divider-only study did not establish the full-range linear-load proof.
- OPA2320AIDR on existing5V_OPA: same D/SOIC-8 functions, rail-to-rail input
  range and lower unloaded current. Selected with local reference protection;
  supply overshoot, filter loading and startup/restart still require closure.
- OPA2320 on3V3_ADC: not selected. Input steering can energize the ADC/LDO
  output while LDO input is empty, reopening TPS7A92 reverse bias.
- Earlier-loss/interlock architecture: retained fallback only if the bounded
  post-correction state argument finds a concrete incompatibility. No new
  catalogue sweep or investigation-budget reset is authorized.

## Decision

Use nine exact TI OPA2320AIDR/C2863402 packages on existing5V_OPA. Add
R_VMID1_IN and R_VMID2_IN, each10k YAGEO RC0402FR-0710KL/C60490, between
VMIDn_EXT and newVMIDn_IN at U_AFE9+IN. Keep both10uF+1uF external-reference
capacitor banks on the divider side. Change R_VMID1_ISO/R_VMID2_ISO to1k
YAGEO RC0402FR-071KL/C106235; retain raw-output feedback and both4.7uF
Panasonic reservoirs. Retain all signal-path values and isolation ordering.

This supersedes ADR0004's amplifier identity and100ohm VMID isolators and
ADR0008's direct divider-to-input connection, not their other intent. The
external-divider selection, ADC-only VMID bypass, direct FILT-negative ground,
same-leg feedback, hardware ADC mode and locked signal/spoke envelope remain.
ADR0021/22 power-source corrections are not reverted.

Primary authority is TI SBOS513F p4(D/SOIC pinout), sections6.1/6.3/6.7,
7.3.2 and7.3.8, and p28(layout); exact captured SHA is in the new dossier.
The operating supply is1.8..5.5V, absolute supply6V, and specified common-mode
range extends0.1V beyond the rails under the stated conditions. Section6.1
note2 permits current-limited input overdrive of10mA or less. That is not a
separate output-backdrive rating. The AIDR part has no shutdown pin.
Exact resistor primary PDF and series derating authority are also vendored.
Public sourcing was checked before adoption; dated observations live only in
`../sourcing/parts-selection-2026-09-09.md`, not as reserved-stock authority.

## Consequences

The source checker's `reference_protection_screen()` reports current and
resistor-power arithmetic using the declared retained differential envelope
and resistance reserve. It does not establish that voltage envelope, an
output-pin overdrive rating, full settling, or an all-state protection proof.
Positive and hostile checks bind all nine identities, both new current
limiters, output isolator values and feedback location. The existing4.5V
scalar hold screen is retained as conservative engineering margin, not
mislabelled as OPA2320's minimum supply or a shutdown-audio requirement.
Legacy steady/shutdown current allocations are not reduced or relabelled as
vendor transient specifications.

**Prototype performance deviation:** Cirrus AN0556R1 p17 Table17 recommends
5nV/sqrtHz and-128dB THD+N. OPA2320's published typical7nV/sqrtHz at10kHz
and0.0005percent THD+N use different conditions and do not establish those
recommendations. No complete Cirrus performance-equivalence claim is made.
This does not relax the locked signal amplitude or existing first-article
acceptance requirements. Review both common-mode and differential feedback
loops with15nF differential and switched1nF/leg loads and the10k input
limiters; the simple TI unity-buffer capacitive-load example is insufficient.

Still owed before source engineering acceptance: correlated CT/NR/rail/
reference/filter states on cold startup, removal, brownout and rapid restart;
partial-VDD TMUX behavior and independent ADC voltage/current limits;
retained-node/output backdrive, reference leakage/loading/settling; finite-L
rail/feed current-duration and thermal argument; actual filter stability.
Native generation, exact schematic/pin/readability reviews, placement/routing
and release gates follow; actual copper/temperature and gain/phase/noise/THD/
recovery measurements retain their own later boundaries. This accepted
selection does not close CAR-F12 or credit choose_source_correction alone.
No release, order, firmware, pod change or publication is authorized here.
