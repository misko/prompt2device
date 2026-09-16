---
id: "0013"
date: 2026-09-08
status: accepted
---
# 0013 — bounded ADC supply, reference and configuration exits

Accepted as **source geometry only**, not route admission, PCB DRC, layout seal
or physical qualification. Coordinates in floorplan.yaml/route.yaml and exact
source tests own the implementation. Generated boards/reviews remain stale.

## Evidence and decision

Starting source is commit `358f87bb3ca5a5fa7d089cce41b808258a2d0b8c`.
At 09:43:19Z the clean committed tree was bound over 969 tracked carrier files,
100,617,233 bytes. ROOT is the only writer; no producer, router, board import,
checkpoint rebinding, main push or sealed-release change is authorized here.

The [public Cirrus package](https://statics.cirrus.com/pubs/software/DC5302P_4P_4S_8P_8S-ADC_Schematic_Layout.zip)
was already known. Newly inspecting its E0 PCB PDF/PADS/IPC/Gerber/stack data
reached a stronger layout precedent than the previously retained schematic
and guidelines alone. The part dossier records exact identities and limits:
eight versus four layers, smaller reference vias, different copper EP land,
and an older CN/B0 part descriptor. Reconcile 49/49 ASCII/IPC pad coordinates
and four configuration drops; extract decisions, never vendor copper. Exact
CS5308P-DN datasheet/footprint authority remains unchanged.

Adopt two capacitor poses only:

- C_LDO_D: [102,69.8,0] to [102,67.9,0].
- C_VDDIO: [101.2,71.3,0] to [101.7,69.8,90].

This keeps VDDIO distribution on F.Cu with an explicit 1.20 mm entry rather
than the superseded, unadopted back-layer power hypothesis. LDO_D_FILT remains
the single three-pad net joining pins32/33 and C_LDO_D.1; no new VDD_D rail.
The two moved capacitors pass native body/courtyard/distinct-pad checks.
Their exact three pin spans are 2.725/2.526979/2.791577 mm (<=5); copper-bbox
gaps are 1.698897/1.518634 mm (<=2) and 2.042450 mm (<=2.5), respectively.
These are engineering proximity limits, not manufacturer numerical guarantees.

Reopen only ADC5/9 power elbows among the preceding 32 banks. The old upward
elbow fenced CFG2; moving its taper to the actual 10 nF positive pad opens the
configuration lane. The south pin9 knee is independently derived, not the pin5
mirror. Both retain 0.18/0.60 mm widths. Final 0.60 mm cap-side extensions are
0.05 mm, keeping ordinary 0.25 mm clearance to the unchanged ground traces.
All other 30 previous banks and every other pose are exact.

Add 25 banks. Total source becomes 57 banks, 151 straight primitives and 20
vias; this change grades 75 primitives (including six replacement west items)
and 12 new off-pad 0.50/0.20 mm vias. Seven precise width areas and nine
pin-pitch clearance areas are added; the global fabrication/class floors stay
unchanged. Entire narrow capsules, not mere area overlaps, must be contained.

VMID1/2 route outward around the staggered CFG1/2/4/5 exits and connect only
their own two bypass capacitors. CONFIG3 is intentionally grounded to EP;
that control strap is not a substitute for GND_A6/8 or GND_D30 return drops.
SPI_CS38 has a fixed high logic leaf and full-width F.Cu entry. RESET23 drops
before the common-mode capacitor row; generic F/B control continuation remains.
No power vias or digital clock vias are introduced.

LDO_D_FILT and VMID1/2 now have complete deterministic ownership: three actual
pads each, verified by native transitive contact without a fictional plane
edge. They are removed from explicit generic groups and added to the exclusion
list. Along with LDO_A_FILT and FSYNC_BUF there are five
complete local nets; 159 generic +5 deterministic +GND +40 NC =205 live nets.
Source-shadow compilation does not itself prove contact or physical routing.

FILT1P/2P reach their 1 uF and 10 uF ceramics. Each real five-pad net still
needs its resistor/reservoir feed, so both remain generic partial fanout.
Negative filter pins and GND_D30 get their own drops; ceramic ground groups
have separate drops. Three F.Cu paddle-gap barriers reserve against direct
pin-to-paddle bridges without splitting either inner ground plane. These
barriers and source contact graphs are not proof of final filled topology.

## Width, current and return limits

| Source subnominal copper | Length mm | Items |
|---|---:|---:|
| Reopened west ADC5/9 | 3.787761155 | 6 |
| Unchanged LDO OUT1/2 | 2.720060973 | 5 |
| Added ADC31/C_VDDIO/SPI_CS | 11.763954077 | 9 |
| Whole 3V3_ADC | 18.271776206 | 20 |
| Each FILT positive bank | 4.500392796 | 3 |
| Each CFG1/5 leaf | 3.154069475 | 3 |
| Each CFG2/4 leaf | 2.592772762 | 3 |

The power-wave ceiling is 18.271777 mm/20, control 3.154070 mm/3, rounded up.
These uniform output ceilings do not replace exact per-net source budgets,
whole-capsule extents, or final per-net remeasurement. HOLD3.075/4 and SW0.9/1
remain exact. The 1.20 mm bulk floor and 2.5 A transient design bound remain;
there is no equal-sharing assumption or lowered current to make a route fit.

Conditional resistance uses rho85=2.1643958e-8 ohm-m and nominal35 um copper,
R=rho*L/(w*t), with full2.5 A charged to each narrowed power branch separately.
Reopened ADC5/9 are 6.756896/6.015654 mOhm (42.2306/37.5978 mW); ADC31
10.273842 mOhm (64.2115 mW), C_VDDIO entry1.336053 mOhm (8.3503 mW), each
FILT9.870535 mOhm (61.6908 mW), and SPI_CS leaf25.688287 mOhm (160.5518 mW).
Those are conditional resistive estimates, **not** safe ampacity, temperature
rise or permissible fault duration. Configuration pins are ordinary static
logic leaves, not load-distribution trunks. No bench current, finished copper,
fault-duration, thermal-via/barrel or current-cutset result is invented.

## Verification and owed work

Source-native screen: 104,559 copper/hole/layer/keepout comparisons, zero
findings, 27/27 declared contacts, whole-capsule extents clear; separate moved
placement screen grades 6,987 comparisons including three adjacency/span rows.
The full project suite passes 141/141 at09:58:18Z. Existing regulator/digital
source screens remain clear (47,745/20,931 comparisons). Rules8/8 and net
references351/351 pass; shadow owns205 nets with159 generic. Tests include
lost LDO_D destination, runaway CFG extent, illegal power-layer change, exact
other-bank preservation and absence of fictional ground-plane graph edges.

Raw rejected candidates, first full-suite failures and fixes are retained in
`06_build/tmp/adc-source-20260908`. A 0.20 mm candidate screen initially missed
the older 0.25 mm widened-entry obligation; full-suite evidence caught it and
the two source extensions were shortened, not waived. Generic ownership
initially remained duplicated in an explicit group; both source lists were
corrected. Reference-parser encoding/spacing errors are preserved, not hidden.

Next: remaining source egress/current-return intent and exact-source admission,
then fresh generation and independent pin/placement/render reviews, bounded
routing, actual filled return/width/current/SI checks, and immutable release
verification. Source checks cannot be substituted for those later artifacts.
TOP77, first-power0.20 A HOLD, physical/service/sourcing limits and the
both-child-seals plus exact P-PUBLISH main-push condition all remain.

## 2026-09-08 — proximity-target evidence amendment

The three inequalities in the original placement paragraph are deliberately
chosen engineering proximity targets. They were not solved physical maxima,
manufacturer numerical requirements, or guarantees of electrical performance.
Their status is therefore **ESTIMATED**, not CITED. The original argument,
coordinates and limits above are unchanged. This amendment records the
distinction required by M-BOUND; it does not turn a chosen number into a
manufacturer-derived bound.

The executable evaluations below independently reconstruct the source's native
footprint geometry through the existing source tests and compare the named
metric with the candidate target as a dimensionless utilization. They do not
read the stale PCB or grade routed length, return copper, manufacturing
tolerances, or analog performance. The existing source test also checks body,
courtyard and pad clearance; later saved-board P-ADJ/P-ADJ-PAIR and independent
layout review remain mandatory. A utilization below one is compliance with an
engineering target, not proof that the target itself is physically sufficient.

No E-series component is being selected here. Each explicit set names the
single current placement-target option, not purchasable resistor/capacitor
values. The geometry comparison is runnable; a derivation establishing the
target as a sufficient physical maximum is not available, and remains
unclaimed.

<!-- bound: ADC_LOCAL_PIN_SPAN -->
```yaml
id: ADC_LOCAL_PIN_SPAN
claim: Maximum source pin-center span from C_LDO_D.1 to U_ADC.32/33 and C_VDDIO.1 to U_ADC.31
relation: "<="
value: 5
unit: mm
corner: nominal
grade: ESTIMATED
why_not_rerunnable: >-
  This is an engineering proximity target, not a solved manufacturer or
  physically qualified maximum. Source geometry can be remeasured, but no
  derivation from analog performance establishes this target as sufficient.
governs:
  evaluate: >-
    /usr/bin/python3 -B -c "import sys; sys.path.insert(0,'projects/crow-audio-carrier-v1/03_src/tests'); from test_adc_source import load_source,native_geometry,placement_screen; f=load_source()[0]; m=placement_screen(f,native_geometry(f)); print((max(m['pin_spans_mm'].values())) / float('{value}'))"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [5]
  series_why: >-
    Placement is continuous geometry, not a sourced E-series component.
    This explicit set contains only the currently adopted engineering target;
    it makes no claim about available component values or physical sufficiency.
chosen: 5
requires:
  - pcbnew
  - projects/crow-audio-carrier-v1/03_src/floorplan.yaml
  - projects/crow-audio-carrier-v1/06_build/netlists/crow_audio_carrier_v1.net
  - projects/crow-audio-carrier-v1/03_src/tests/test_adc_source.py
```

<!-- bound: ADC_LDO_D_COPPER_GAP -->
```yaml
id: ADC_LDO_D_COPPER_GAP
claim: Maximum source copper-bounding-box gap from C_LDO_D.1 to U_ADC.32/33
relation: "<="
value: 2
unit: mm
corner: nominal
grade: ESTIMATED
why_not_rerunnable: >-
  This is an engineering proximity target, not a solved manufacturer or
  physically qualified maximum. Source geometry can be remeasured, but no
  derivation from analog performance establishes this target as sufficient.
governs:
  evaluate: >-
    /usr/bin/python3 -B -c "import sys; sys.path.insert(0,'projects/crow-audio-carrier-v1/03_src/tests'); from test_adc_source import load_source,native_geometry,placement_screen; f=load_source()[0]; m=placement_screen(f,native_geometry(f)); print((max(v for k,v in m['copper_bbox_gaps_mm'].items() if k.startswith('C_LDO_D.1/'))) / float('{value}'))"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [2]
  series_why: >-
    Placement is continuous geometry, not a sourced E-series component.
    This explicit set contains only the currently adopted engineering target;
    it makes no claim about available component values or physical sufficiency.
chosen: 2
requires:
  - pcbnew
  - projects/crow-audio-carrier-v1/03_src/floorplan.yaml
  - projects/crow-audio-carrier-v1/06_build/netlists/crow_audio_carrier_v1.net
  - projects/crow-audio-carrier-v1/03_src/tests/test_adc_source.py
```

<!-- bound: ADC_VDDIO_COPPER_GAP -->
```yaml
id: ADC_VDDIO_COPPER_GAP
claim: Source copper-bounding-box gap from C_VDDIO.1 to U_ADC.31
relation: "<="
value: 2.5
unit: mm
corner: nominal
grade: ESTIMATED
why_not_rerunnable: >-
  This is an engineering proximity target, not a solved manufacturer or
  physically qualified maximum. Source geometry can be remeasured, but no
  derivation from analog performance establishes this target as sufficient.
governs:
  evaluate: >-
    /usr/bin/python3 -B -c "import sys; sys.path.insert(0,'projects/crow-audio-carrier-v1/03_src/tests'); from test_adc_source import load_source,native_geometry,placement_screen; f=load_source()[0]; m=placement_screen(f,native_geometry(f)); print((m['copper_bbox_gaps_mm']['C_VDDIO.1/U_ADC.31']) / float('{value}'))"
  budget: "<= 1"
  unit: utilization
standard_value:
  explicit: [2.5]
  series_why: >-
    Placement is continuous geometry, not a sourced E-series component.
    This explicit set contains only the currently adopted engineering target;
    it makes no claim about available component values or physical sufficiency.
chosen: 2.5
requires:
  - pcbnew
  - projects/crow-audio-carrier-v1/03_src/floorplan.yaml
  - projects/crow-audio-carrier-v1/06_build/netlists/crow_audio_carrier_v1.net
  - projects/crow-audio-carrier-v1/03_src/tests/test_adc_source.py
```


## 2026-09-13 filled-return correction and digital-cutout applicability

The completed native review found that all four ADC_VMID bypass ground pads
contacted broad F.Cu before their intended GND_A junctions. Retain every local
seed and component pose, adding bounded F.Cu pour reservations around each
whole cap-return/GND_A tree and via reservations with openings only around its
existing designated drop. VMID1 meets GND_A6 at(91.6,69.5); VMID2 meets GND_A8
at(89.8,71.5). Ground plane access is at those junctions. The separately
seeded GND_D30 drop and the nine paddle vias remain. Final filled-native graph
cuts must remove the owner pad and all layers of that designated barrel and
show no alternative general-plane access; shared GND names are insufficient.

July2025 CS530x guideline §3.7/Figure10 says GND_D should have its own plane
connection without directly connecting the paddle, and asks for a digital-side
ground cutout. Its next sentence reads: “The ground cutout should be deprecated
on all ground layers.” The word is deprecated, not duplicated. The finite
Figure10 drawing references the top layer of an eight-layer evaluation board;
it does not resolve this contradictory all-layer wording for our four-layer
board. Source decision: apply the unambiguous own-drop/no-direct-paddle intent
and retain the existing finite F.Cu paddle barrier, while preserving continuous
In1/In2 general ground references. Do not interpret the ambiguous word as an
instruction to duplicate a moat or split the package reference planes. This is
an explicit applicability decision, not a claim of literal all-layer cutout
conformance or manufacturer clarification. The document does not establish a
usable all-layer geometry; any stronger vendor-conformance claim needs Cirrus
clarification and subsequent source review. No new first-article prerequisite.

The two FILTP feed-after-bulk branches remain unrouted obligations: resistor
output must first reach its470uF reservoir side then the local ceramics/ADC.
Keep both reservoir poses and direct FILTN ground connections; no new resistor.

The12 exact one-spoke GND pads C_ADC_CM4P.2/C_ADC_CM4N.2, C_ISO1..8.2,
U_LDO_EN.3 and C_VDDA1_10N.2 receive the existing exact per-pad full-zone
connection treatment. These small top-side lands have no controlled Kelvin
or VMID-return function requiring thermal isolation; their direct local return
avoids starving a second spoke in the constrained fill. All other pad settings,
two-spoke thermal floor, clearance, copper and ampacity thresholds remain.
Native refill and quiet-cell topology must verify this intent. U_PWR.2 with
R_PWR_BOT.2 and U_AUDIO.2 ground opens remain declared route obligations.


Candidate refinement: native filled source showed the new VMID1 reservation
isolated C_VDDA1_10N.2. Move only the VMID1 return column fromx89.8 tox89.45
between its470nF pad andy69.17. The native filled result still isolates the supply-cap ground;
its two-cap bank nevertheless meets the unchanged GND_A6 drop. No component or drop
moves and no generic route is authored. Native thermal checks also report a
one-spoke remnant at each VMID470nF ground land despite zero actual filled
pad contact. Apply exact full-zone settings to these two lands: their return
is the reserved seed tree; the surrounding pour prohibition remains decisive.
This does not authorize direct general-plane contact and must pass the same
filled graph cuts. It preserves the global two-spoke thermal requirement.


## Proposed 2026-09-13 separate supply-ground plane connection

Fresh independent native analysis confirms that widening the VMID1 column did
not connect C_VDDA1_10N.2 to a broad plane. Add a distinct F.Cu0.30mm GND stub
from(90.52,68.5) through(90.0,68.0) to(90.0,67.5), terminating at one existing-
family0.50mm copper/0.20mm drill through-via. This supply return stays inside
its own island and does not touch the upstream VMID spine. Retain all six
VMID reservations, fourteen exact full-zone pad settings, designated GND_A6/8
and GND_D30 drops, nine paddle vias and LT3041 quiet-return topology.

Independent analytical margins are0.260001mm via/foreign copper,0.360001mm
stub/foreign copper,1.10mm drill spacing and0.009501mm full F-island disk
containment. These are exact nominal geometry results; no installed tolerance
or new native DRC acceptance is claimed. The small island margin requires
regrading after every surrounding-copper change. The same four VMID graph cuts,
three LT3041 cuts, five no-F-paddle shortcuts and supply closure must pass on
the assembled generated/prepared/refilled candidate. No rule floor is changed.
Previous two ADC candidates remain spent. This is one fixed reviewed upstream
source correction; no free geometry search or fourth top-only trial is granted.
