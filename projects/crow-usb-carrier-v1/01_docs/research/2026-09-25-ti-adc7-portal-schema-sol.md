# TI ADC7 local portal schema screen

**Research only, 2026-09-25.** No canonical source/PCB or P1 attempt changed.
The subject is SOL's isolated three-placement
[`candidate.kicad_pcb`](2026-09-25-ti-adc7-local-osc-probe-sol/candidate.kicad_pcb)
(SHA-256 `c9b758d69867b274f0592bd2eceb9a26d64a80dd2daafa8ab9516d23d5925502`),
Terra's [physical owner screen](2026-09-25-ti-adc7-typed-portal-owner-screen-terra.md),
and local portal `[166,83.9,167.12,85]` mm. The candidate's physical
envelope/pad scan reports that portal empty, but its native DRC has 12 new
silkscreen warnings; it is not an accepted placement.

The authoritative modular interface has **eight exact ADC7 terminals**:
`ADC7N`: `U_ADC_B.11` in `adc_reference`, and `C_ADC_AC7N1.2`,
`C_ADC_AC7N2.2`, `C_ADC_CM7N.1` in `analog_ch7`; `ADC7P`:
`U_ADC_B.10` in `adc_reference`, and `C_ADC_AC7P1.2`, `C_ADC_AC7P2.2`,
`C_ADC_CM7P.1` in `analog_ch7`. `audio_clock_tdm` owns none of these pads.

## Existing schema result

I invoked the current `_shared_ports` validator in memory on the isolated
candidate board, unchanged modular plan/floorplan, and a proposed single
F.Cu portal/zone/reservation of exactly `[166,83.9,167.12,85]`. The row
declared `analog_ch7` and `adc_reference` as participants, two local ADC7N/P
affected pads, exact `P2_REQUIRED` pad-to-port entries, and a
`continuous_filled_reference` GND return obligation. The result was
`adc7_portal: participant does not intersect zone`: `adc_reference` ends at
x=145; the portal starts at x=166. Adding `audio_clock_tdm` does not fix
the remote true owner, and would misstate audio as a signal participant.
Even if the participant check were bypassed, `audio_clock_tdm=[145,72,190,99.84]`
overlaps the portal and is not an electrical participant, so the current
foreign-region check rejects it. Enlarging the zone to reach x=145 is no
local portal and would encounter intervening region/physical checks.

An `analog_ch7` transit `physical_cell` also fails current invariants:
cells cannot overlap a foreign planning region, and the portal's y=84..85
strip lies in audio's region. Extending `analog_ch7` and recutting audio at
y=85 would cut 15 actual audio footprint envelopes after the three SOL
moves, as Terra measured. `virtual_block_face` requires its rectangle
inside the owner cell/region, so it cannot independently legalize the strip.
These are deliberate fail-closed rejections, not evidence that the physical
portal is blocked by a component.

## Minimal typed extension to consider

An **access-only ADC portal** should separate three roles: electrical net
owners `{analog_ch7, adc_reference}` from physical transit owner
`analog_ch7`, and a named *non-electrical planning overlap*
`audio_clock_tdm`. It should bind the exact eight source/native/net/owner
terminals above and reject any extra/duplicate native ADC7 pad. Only the
analog-side pad-to-local-port access may be attached to this portal;
`U_ADC_B.11/.10` remain remote `P2_REQUIRED` pad-to-route obligations,
not fictitious local portal participants. It should require the portal to
touch the analog cell by a positive edge, stay inside the board, and overlap
only explicitly listed planning regions. Any native body/courtyard/pad,
foreign copper or rule area in the portal must reject it regardless of
planning owner. The overlap exemption must not reassign a footprint or
electrical endpoint to audio. Require a named In1.Cu continuous filled-GND
return **obligation**, not a continuity pass. Exclude this type from rough
slot credit and force `INCOMPLETE`, `routing_realized: false`, and
`p1_accepted: false` until separate P2/P3 and native route review.

The existing `shared_transition_ports` and `physical_cells` cannot express
those distinct roles by data alone. A typed checker change with positive
and negative tests is required before promoting any isolated source record;
the candidate's 12 silkscreen warnings and all ordinary ADC/audio placement
checks remain independent blockers.
