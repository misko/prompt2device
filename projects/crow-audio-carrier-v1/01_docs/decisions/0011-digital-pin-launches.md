# ADR-0011 — bounded digital pin launches and exact FSYNC ownership

Date: 2026-09-08. Status: proposed source correction, pending root independent
adoption. NOT ROUTE-READY. No generated-board, DRC, SI, thermal, fabrication or
release acceptance. ADR0007/0009/0010 and all physical holds remain binding.

## Context and authority

All twelve literal ADC_CLOCK nets retain 27 native endpoints. The exact
SN74LVC3G34 DCU pinout is 1A=1,3Y=2,2A=3,GND=4,2Y=5,3A=6,1Y=7,VCC=8;
CS5308P FSYNC/DOUT1/BCLK/MCLK are physical pins24/25/29/34. Authorities are
the retained manufacturer SCES366L pp3/10, DS1314F1 pp4–5 and July2025
CS530x layout guidance pp10–12, plus their exact native library pad shapes.
These retain nearby bypassing, all three MCH pull-down branches, existing
source-series resistors and continuous common ground under digital copper.
The Cirrus50 ohm intent is not a solved impedance allocation.

Isolated source-native pad sampling at .36 mm/.25 mm finds eight shortfalls:
U_CLK.2/.3/.6/.7 and U_ADC.24/.25/.29/.34. The two ADC corner pads can launch
full .36 mm from an off-centre in-pad start at local .20 mm clearance; they
do not justify extra thin stubs. The other19 endpoints retain full .36/.25
native 1 mm launch witnesses even after all new and existing seeds are added.
Sampling and witnesses are local source diagnostics, not generated P-LAND.

## Decision

Add eight exact F.Cu-only seed banks, comprising18 straight primitives and no
digital vias. Preserve the previous nine west-ADC banks and all299 poses.
Six banks use .18 mm locally; two ADC corners stay .36 mm throughout.

| Pin / net | Authored subnominal length mm / primitive count | Complete owner? |
|---|---:|---|
| U_CLK.2 / FSYNC_BUF | 1.400000 / 1 | Yes, reaches R_FSYNC.1 |
| U_CLK.3 / MCH_BCLK | 1.430278 / 3 | No, partial launch |
| U_CLK.6 / MCH_FSYNC | 1.020000 / 1 | No, partial launch |
| U_CLK.7 / MCLK_BUF | 1.142443 / 2 | No, partial launch |
| U_ADC.29 / ADC_BCLK | .900000 / 1 | No, partial launch |
| U_ADC.34 / ADC_MCLK | .900000 / 1 | No, partial launch |
| U_ADC.24 / ADC_FSYNC | 0 / 0; full .36 mm | No, partial corner launch |
| U_ADC.25 / TDM_RAW | 0 / 0; full .36 mm | No, partial corner launch |

These are measured source lengths, not qualified SI/electrical length limits.
The exact point lists in route.yaml govern; every widened exit, except the
first two full-width corner items, is screened at ordinary .25 mm clearance.
The class remains twelve nets at .36 mm/.25 mm. FSYNC_BUF is excluded from the
generic wave and assigned only prep.seed_stubs; its one .18 mm item contacts
both native pads. The other seven banks remain partial; no generic branch or
source pull-down endpoint is removed. Totals become162 generic nets, two
complete deterministic nets, GND and40 intentional NCs, covering205 exactly.

Only four named F.Cu deny:[] rule areas gain .18 mm floors:
CLK_WEST_DIGITAL [144.1,58.4,145.8,60.1] on FSYNC_BUF/MCH_BCLK;
CLK_EAST_DIGITAL [148.2,58.3,149.65,59.65] on MCH_FSYNC/MCLK_BUF;
ADC_BCLK_LAUNCH [98.75,70.05,100.0,71.15] on ADC_BCLK;
ADC_MCLK_LAUNCH [98.75,68.05,100.0,69.15] on ADC_MCLK.
Those four and ADC_FSYNC_CORNER [97.85,72.9,98.85,73.7] on ADC_FSYNC and
ADC_DOUT1_CORNER [98.9,71.85,99.9,73.1] on TDM_RAW gain exact .20 mm
clearance exceptions. No corner width floor and no global fab change.

Rule-area item overlap is not pointwise containment. Source tests require the
entire round-ended narrow primitive within its exact eligible area, and the
two first full-width corner items within their clearance-only areas. The
existing clocks realized_width guard is explicitly configured with nominal
.36, minimum .18, maximum1.44 mm and three subnominal primitives per net.
This is an authored finite discontinuity allocation, not an impedance-derived
safe bound. Source tests additionally retain the exact per-net lengths/counts
above. FSYNC_BUF, excluded from the wave, requires a separate final same-bound
measurement: exactly one1.40 mm narrow item, not the wave allowance.

## Alternatives and consequences

The inherited CLK3 bulk entry at[144.8,59.35] and CLK6 entry at[149.2,59.25]
collide with CLK4 and CLK5 respectively at .36/.25. New H1 moved those entries
clear but its CLK7 extension to[149.95,58.4] collided with C_CLK.1. H2 retains
all other geometry and finishes horizontally at[149.95,58.55], giving .26 mm
nearest foreign-pad gap for that widened item. Both rejected hypotheses remain
in evidence and hostile native-shape regressions; neither is silently accepted.

The standard ownership preflight's O-DOUBLE family only grades many-pad power;
it does not reject a two-pad digital net in both a wave and deterministic plan.
Existing exact shadow authority compilation does reject that duplication.
The project regression exercises both facts. No shared checker is changed.

The wave output guard does not itself certify final post-stitch/import copper,
pointwise area containment, no router re-entry, or excluded FSYNC_BUF. Fresh
generated admission must inspect exact final topology and remeasure all local
width/extent bounds; no nominal command-line width substitutes for that work.
The unchanged0.36 mm stack hypothesis still requires field/return-path and
source/resistor/receiver endpoint SI review. No delay, skew or50 ohm PASS.

## Validation and retained limits

MEASURED final native source screen:18 primitives against868 pads,111 hole/
mounting-head shapes, existing/new seed copper, existing seed vias/holes,
relevant track keepout and edge:18357 checks, zero findings, all eight declared
pins reached. Other19 digital endpoints have separate full .36/.25 witnesses
against all final source copper. The own plated PTH drill is correctly not a
foreign obstacle to its own pad; all other holes remain screened.

MEASURED terminal project suite124/124 tests, source rules8/8 classes,334/334
net references and exact205-net shadow authority. These are SOURCE checks.
See [terminal source report](../SOURCE-CORRECTION-20260908-digital-launches.md)
for exact commands, logs, rejected attempts, authority hashes and inventory.

No Board constructor/load/save, producer, alternate PCB, routing/import,
checkpoint/review mutation, commit, account, vendor contact or publication.
Preserve1.20 mm bulk power/2.5 A bound,5.05 mm/eight-segment ADC exception,
three adopted capacitor poses, independent GND_A/VMID geometry and common
inner planes. Current/fault/thermal/ground/return/SI source obligations,
TOP77, first-power0.20 A HOLD, service/physical/sourcing/publication holds,
ADR0007 prototype limits and ADR0009 power-state obligations remain unresolved.
