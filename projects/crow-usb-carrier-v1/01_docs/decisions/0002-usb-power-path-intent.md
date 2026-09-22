---
id: 0002
date: 2026-09-22
status: accepted
---
# 0002 — USB data and independent carrier power intent

## Context
The new carrier connects directly to an independently powered Raspberry Pi. The retained Crow spokes require the separate carrier supply. USB VBUS must provide attachment sensing without becoming the carrier or spoke supply.

## Decision
Route USB D− to XU316 package pin 59 and D+ to pin 60, following the exact XU316 dossier pin table. Preserve both receptacle orientations through the USB front end. Sense VBUS through the 100 kΩ base resistor and grounded-emitter BC847B stage; its collector reports active-low presence to the 1.8 V domain. Do not connect USB VBUS to the input-power converter.

For external power, retain the fuse before the reverse-polarity P-channel device. Its drain faces the fused input and its sources face the protected output. The gate-to-source zener cathode faces the protected source node. The TPSM input pins consume this protected rail; its output feeds the internal 5 V bus. Keep its AGND join explicit through R_AGND_JOIN.

## Evidence and consequences
Pin identities and source implementation are recorded in the XU316, USB4105, BC847B, DMP6023LFG and TPSM63603V5 dossiers and the combined source check of 2026-09-22. This decision records intended topology; it does not accept the overall schematic or assert tested power-state behavior.

`03_src/rules/electrical_invariants.yaml` emits independently chosen endpoint assertions for these decisions. Native netlist execution, full VBUS isolation/path analysis, polarity review, USB signal integrity and power-state verification remain required. Endpoint assertions alone cannot prove the absence of every unwanted path.
