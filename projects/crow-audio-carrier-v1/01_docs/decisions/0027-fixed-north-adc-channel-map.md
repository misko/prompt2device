---
id: 0027
date: 2026-09-12
status: accepted
---
# 0027 — fixed north pod-to-ADC association

The four north receive cells and connectors run left to right as pods1–4,
while the CS5308P north input pins run physically as channels4–1. Adopt a
fixed analog-wiring permutation to remove that endpoint-order reversal.
Keep the ADC, every connector, AFE, ISO, power/reference/filter/clock/reset
component and all south-channel electrical identities in place. This decision
changes the earlier identity association, not the selected ADC or hardware mode.

Authority: BRIEF G1 requires a deterministic association; A2/P delegates this
electrical implementation. Independent source-proposal review is SOUND under
that authority. No user-locked connector pin, audio polarity, current, COTS
image, firmware scope or clock domain changes.

Source authority is `03_src/adc_channel_map.json`, identity
`crow-carrier-channel-map-20260912`. ADCnP/N continues to mean logical pod n.
Physical CS5308P channel order and its hardware-default slots are unchanged.

| Pod / connector | Physical ADC channel | P / N pins | TDM slot (zero-based) |
|---|---:|---|---:|
| 1 / J1 | 4 | 48 / 47 | 3 |
| 2 / J2 | 3 | 46 / 45 | 2 |
| 3 / J3 | 2 | 42 / 41 | 1 |
| 4 / J4 | 1 | 40 / 39 | 0 |
| 5 / J5 | 5 | 14 / 13 | 4 |
| 6 / J6 | 6 | 16 / 15 | 5 |
| 7 / J7 | 7 | 20 / 19 | 6 |
| 8 / J8 | 8 | 22 / 21 | 7 |

The same JSON carries `capture_requirements`: map identity/digest, slot table,
serialized pod/cable identities, surveyed pod coordinates, stream epoch and
impulse evidence. The source checker validates their complete declaration and
emits the actual source SHA256. Capture status remains OWED. The existing
first_article.yaml is a first-power population/rail card; capture qualification
has this separate machine-checked source contract and the physical test plan.

Thus stream slots0–7 identify pods4,3,2,1,5,6,7,8. Capture metadata must bind
this map identifier and its source digest to the surveyed pod coordinates,
serialized cable/pod identities and stream epoch. No runtime reordering is
required. Physical slot/USB enumeration must still pass the eight-channel
impulse test; prospective source intent is not a measured capture result.

Exchange logical C_ADC_CM1↔4 and2↔3 references across the existing identical
1nF capacitor positions, including each P/N leg. Keep their existing physical
pad/ground arrangement and carry each physical adjacency ceiling with its
terminal pair. R_ADC_PD stays with its same ISO/logical pod. The eight north
U_ADC seed net assignments follow the new wiring; their dimensions and every
other seed remain identical. All north channels remain in VMID1_EXT and south
channels in VMID2_EXT. No matched-length or resistance ceiling is relaxed.

The original north association had six cross-channel bundle inversions;
this association has zero. The source test independently derives ordering
from physical pad coordinates and logical endpoints, with the former mapping
as a known-bad contrast. This removes the specific ordering reversal; it does
not prove a simultaneous legal route, matching, quiet returns or DRC.

Rejected alternative: the ten-capacitor local relocation proposal introduced
native courtyard/pad conflicts in root's independent source check, including
VMID capacitor overlaps and a conflict with C_LDO_D. Its claimed minimum
courtyard separation was not reproduced. Its original report and measurements
remain retained; no coordinates were adopted. ADC rotation would disturb both
analog banks and supply/reference/clock/reset geometry.

The exhausted LAYOUT-001 investigation retains all three spent attempts and
its history. No fourth probe, budget reset, source-emitted route or accepted
copper results from this decision. Source, native schematic, pin, render,
locator and layout gates must renew. Only a fresh exact-board review may
resolve the finding on the new association and admit ordinary routing.
Final routed connectivity, all declared paths, <=1mm P/N spread and filled
In1.Cu/In2.Cu continuity remain owed, as do first article and order readiness.


## Retained engineering target

The matching ceiling above is the existing ADR0019 engineering choice. It is
not a new derived phase/noise limit or evidence of a routed board. The typed
record below checks the published candidate against all 24 adopted source
ceilings. Realized path lengths remain graded by the saved-copper checker;
physical analog performance and assembly tolerances remain first-article work.

<!-- bound: RETAINED_ANALOG_PATH_SPREAD -->
```yaml
id: RETAINED_ANALOG_PATH_SPREAD
claim: Maximum allowed P/N path spread per post-buffer section and corresponding branch, retained from ADR0019 as source intent only
relation: "<="
value: 1.0
unit: mm
corner: nominal
grade: ESTIMATED
why_not_rerunnable: >-
  ADR0019 selects this engineering symmetry target without a derived physical
  phase/noise sufficiency bound. The source ceiling is executable; its adequacy
  for analog performance is not established by this declaration or regeneration.
governs:
  evaluate: >-
    /usr/bin/python3 -B -c "import yaml; from pathlib import Path; g=yaml.safe_load(Path('projects/crow-audio-carrier-v1/03_src/rules/nets.yaml').read_text())['length_match']; a=[v['max_spread_mm'] for k,v in g.items() if k.startswith('ANALOG_CH')]; assert len(a)==24 and set(a)=={1.0}; print(float('{value}')/min(a))"
  budget: "<= 1"
  unit: adopted_source_ceiling_utilization
standard_value:
  explicit: [1.0]
  series_why: >-
    A continuous PCB path constraint is not a sourced E-series component.
    This singleton is the unchanged adopted engineering target, with no claim
    of fabricated length accuracy or physical performance sufficiency.
chosen: 1.0
requires:
  - projects/crow-audio-carrier-v1/03_src/rules/nets.yaml
```
