---
id: "0014"
date: 2026-09-08
status: accepted
---
# 0014 — bounded peripheral power entries

Accepted as authored-source progress only. NOT ROUTE-READY; no generated-board
DRC, current/thermal qualification, layout seal, release or power-up claim.
ROOT is author and diagnostic operator, not an independent PCB reviewer.

## Evidence and decision

Start from clean commit `955769d11e12f5ea5c8b1155fdce0e7d76cfcb1a`. At
10:23:12Z, bind 1,131 tracked carrier subjects / 101,515,587 bytes before edits.
That committed tree is recoverable; ignored files are not claimed censused.

The first finite native entry scan found 66 witnesses among 84 connected F.Cu
power-copper groups across eight nets / 96 physical pads. Each witness is a
1 mm straight segment at 1.20 mm width / 0.25 mm clearance, starting inside
an actual pad or on existing same-net source copper. Forty-eight directions
and bounded pad/seed samples are offered. Native foreign pads, source copper,
vias, holes, keepouts and board edges are checked without distance culling.
A missing witness is a finite-search finding, not an impossibility proof.

Resolve sixteen peripheral findings with fifteen additional source banks and
38 straight primitives, using no new vias and no placement changes. All
57 previously adopted banks remain exact. Source totals become 72 banks,
189 primitives and 20 vias. Fourteen new whole-capsule width reservations
are added; all class floors, physical stack, fabrication rules and sixteen
existing scoped clearances remain unchanged. New copper clears the ordinary
0.25 mm requirement; no new clearance exception is introduced.

- Each U_ISO1-8 VDD8 reaches its own C_ISO 100 nF positive pad through
  0.30 mm copper, then a short 0.60 mm transition and explicit 1.20 mm entry.
  The small off-centre in-pad starts preserve clearance to SEL1/EP. Each
  repeated and rotated cell is screened against its own real surroundings.
- U_PWR VDD4 reaches C_PWR; a separate MR3 tied-high leaf reaches VDD4.
  U_AUDIO VDD4 reaches C_AUDIO around its adjacent timing/control pins.
  Shared supply-net identity does not interchange VDD4 and MR3 functions.
- C_DUMP_LOGIC gets a 0.60 mm cap-side feed and explicit 1.20 mm entry.
  This does not complete its remote connection to U_DUMP5 or its ground loop.
- U_CLK VCC8 reaches C_CLK using 0.35 mm local copper, with a separate
  1.20 mm entry. All existing clock-signal banks and their width bounds remain
  exact; no clock or power layer transfer is introduced.
- U_RST2 VCC8 reaches C_RST2 at 0.60 mm. Its distinct B2 high-trigger strap
  gets a 0.35 mm local exit and 1.20 mm entry; the two groups still need their
  generic rail connection. Timing pins6/7 and all logic identity stay exact.

The selected dossiers remain the authority: TMUX2821 SCDS488, TPS3890
SLVSD65A, SN74LVC3G34 SCES366L and SN74LVC1G123 SCES586E fix the exact pin
roles and local bypass intent. No part, value, net, package, manufacturer
reference copper or public-stock claim changes in this decision.

## Width and current accounting

| Subnominal source copper | Added length mm / items | Whole-net length mm / items |
|---|---:|---:|
| 5V_LDO_HOLD | 24.297221053 / 23 | 27.372221053 / 27 |
| 3V3_ADC | 5.782738500 / 4 | 24.054514705 / 24 |

HOLD's previous LDO subtotal3.075 mm/four items and 3V3's previous
18.271776206 mm/twenty items are preserved. SW remains0.9 mm/one item;
each FILT positive bank remains4.500392796 mm/three items. The power-wave
shared ceiling is27.372222 mm/27, rounded upward by less than1 nm. It does
not replace exact per-net tests or final per-net measurement on routed copper.

Per ISO narrowed branch:2.017283739 mm/two items. Other narrowed lengths
are MR3 1.2, PWR4 1.420563269, AUDIO4 3.151086443, DUMP cap2.387301431,
CLK8 2.162298992, RESET B2 1.8 and RESET VCC8 1.820439507 mm.

Preserve the1.20 mm F.Cu bulk and2.5 A transient bound. At nominal35 um copper,
rho85=2.1643958e-8 ohm-m, R=rho*L/(w*t), charging the entire2.5 A to each
narrowed leaf independently gives:

| Leaf | Resistance mOhm | Conditional loss mW |
|---|---:|---:|
| Each ISO | 3.336723 | 20.854518 |
| PWR MR3 | 2.473595 | 15.459970 |
| PWR VDD4 | 2.928249 | 18.301555 |
| AUDIO VDD4 | 6.495427 | 40.596418 |
| DUMP capacitor | 2.460507 | 15.378170 |
| CLK VCC8 | 3.820466 | 23.877913 |
| RESET B2 | 3.180337 | 19.877104 |
| RESET VCC8 | 1.876263 | 11.726642 |

These are conditional resistive estimates, not safe ampacity, temperature
rise, permissible fault duration, measured logic load, or equal-sharing
assumptions. Logic straps are not load-distribution trunks. Ground and thermal
paths, full rail routing and final current-cutset checks remain separate.

## Verification and remaining work

MEASURED10:42:48Z:148/148 project tests PASS. Live new-source screen:
43,476 comparisons, zero findings,15/15 contacts and whole-capsule extents
clear. The live entry scan covers all96 power pads,69/71 connected groups
with witnesses. Thirteen group merges explain the changed denominator;
no pin was dropped from coverage. Only ADC5/C_VDDA1_10N and
ADC9/C_VDDA2_10N still lack full-width local entries.

MEASURED10:43:17Z: existing ADC108,219, regulator49,215 and digital21,615
native comparisons clear;19/19 other full-width clock endpoints retained.
Rules8/8 and net references365/365 PASS. Exact-input source-shadow owns205
nets, including159 generic, five complete local, GND and40 intentional NC.
It is not a generated-board or routing-admission receipt.

Raw baseline, the first passing peripheral hypothesis, live source checks and
source-only plots are preserved under `06_build/tmp/power-landing-20260908`.
Tests reject runaway extents, illegal B.Cu power and the tempting but colliding
1.20 mm launch directly from the small dump bypass pad.

Next: investigate both west ADC bypass feeds together with their VMID-ground
and configuration geometry. Do not claim a finite negative proves F.Cu
impossible, substitute plane connectivity for the nearest GND_A return, or
silently relax fabrication/current constraints. ADC exposed-pad thermal and
common-plane return, complete FILT feeds, source admission, fresh generation/
independent reviews, routing and actual filled-board checks are still owed.
The TOP77/0.20 A first-power HOLD, sourcing/physical limits, and both-child
seals plus fresh exact-base/head P-PUBLISH condition for main remain intact.
