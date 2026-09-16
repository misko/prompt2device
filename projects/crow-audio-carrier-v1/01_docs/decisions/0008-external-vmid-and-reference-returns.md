---
id: "0008"
date: 2026-09-07
status: superseded-by-0023
---
# ADR-0008 — External hardware-mode VMID and direct reference returns

## Context

The locked CS5308P hardware/TDM8 architecture selects mid-impedance input
mode. DS1314F1 section 4.5.6 explicitly requires an external VMID source in
that mode, as Figure 2-2 shows. ADC_VMID1/2 are not the permitted input-buffer
reference in this mode. Figure 2-2 also grounds ADC_FILT1N/2N directly.
This corrects those portions of ADR-0004; its eight signal-path networks,
buffer-output isolation, coupling capacitors and audio contract remain intact.

## Options

- Reuse ADC_VMID1/2: rejected because the mode-specific manufacturer rule
  contradicts this topology, regardless of a generic buffer example.
- Change to high-impedance/software mode: rejected because it changes the
  locked hardware-only architecture and introduces forbidden firmware scope.
- Derive external VMID from VDD_A as Figure 2-2: selected, independently for
  the two existing follower halves and their four-channel bias banks.
- Keep one-ohm negative-return resistors: rejected; they insert ground
  impedance absent from the required connection and reference schematic.

## Decision

Each existing OPA1656 follower now senses its own external 10 kOhm/10 kOhm
divider from `3V3_ADC` to GND, using exact Yageo RC0402FR-0710KL parts.
`VMID1_EXT` and `VMID2_EXT` each receive 10 uF plus 1 uF ceramic bypass,
using the existing exact KEMET C0805C106K8RACTU/C0603C105K4RACTU identities.
This is conservative engineering margin under the existing capacitor
derating policy; Figure 2-2's nominal example is not a newly invented
minimum-capacitance specification. Larger bypass extends reference settling.
Feedback remains at the raw amplifier output before the 100 Ohm isolation
resistor and 4.7 uF buffered-node reservoir.

ADC_VMID1/2 keep only their existing local 4.7 uF/470 nF bypass networks.
They do not join the external references, even through another resistor.
ADC17/44 and all six FILT-bank negative terminals connect directly to GND;
R_FILT1N and R_FILT2N are removed. Both positive one-ohm feeds and both
470 uF reservoirs are retained. No reference-bulk reduction is authorized.
Both positive feeds are now exact Vishay CRCW12061R00FKEAHP (C844653),
1 Ohm / 1% / 1206 pulse-proof high-power parts, replacing the original
0402s. The dossier retains manufacturer document 20043 revision
17-Mar-2026, including its thermal-installation conditions. This increases
component capability without pretending the still-open regulator charging
pulse or board thermal conditions are qualified; no accepted pulse or
thermal bound is asserted by this topology decision.

## Consequences

Source adds eight external-divider/bypass components and removes two
ground-leg resistors. `check_analog_filter_topology.py` reopens the exact
DS1314F1 hash, checks both external dividers and both follower inputs,
requires ADC_VMID decoupler-only nodes, and rejects reintroduced resistive
ground returns. E-INV and pin-label survival independently bind key pins.

Divider DC/tolerance and settling equations belong to DETAIL_DESIGN.md;
they are component screens, not measured common-mode, noise or THD results.
The LDO thermal/bank/ramp/reverse-current source finding remains a separate
open architecture blocker until a coherent power design is adopted and
verified. This correction alone does not admit schematic review or routing.

Primary authority: local `02_parts/CS5308P-DN/CS5308P_DS1314F1.pdf`, SHA-256
`6ca42cc09ac47ebdacacaee435f05e3f9c34b83d5692e52a2d8a26533e810e57`,
Figure 2-2/p8 and section 4.5.6/p31; and E0 evaluation schematic p17,
SHA-256 `fce5684d95855422693ada480b59c165f95cf710b85b0e55a07cd6e26a3b3d28`.
