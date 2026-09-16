# Crow microphone pod v3 — v0.2.5

**FIRST-ARTICLE-ONLY — DO NOT ORDER.**

DESIGN: PASS — reviewed engineering candidate; physical first-article and order holds remain.
PUBLIC SOURCING: CLEAR — all 22 machine-BOM rows clear quantity plus the configured 150-unit surplus.
ASSEMBLY FULFILLMENT: ORDER-TIME CHECK — manually confirm mappings, substitutions, fees and capability in the uploader.
ORDER VERDICT: FIRST-ARTICLE-ONLY / DO-NOT-ORDER.

This daughter board accepts the governed 10.5–13.2 V spoke supply and returns one balanced analog microphone channel. J1 uses a straight-through Cat6 RJ45 patch cord with the Crow-specific power/audio assignment. **NOT ETHERNET. NOT POE. Never connect to network equipment.**

## Fabrication and assembly

Use `fab/crow_mic_pod_v3_gerbers.zip`, `fab/bom.csv`, and `fab/cpl.csv`. The board is two-layer, nominally 60 × 40 mm; confirm thickness, copper weight, mask and finish against the shipped native Board Setup before payment. BOM has 22 grouped exact-code rows; CPL has 31 top-side SMT placements. No bottom-side SMD assembly is required.

Build quantity is 10 under the current assembly contract. All 22 coded machine
BOM rows clear the build requirement plus the configured 150-unit public-stock
surplus. This clears configured release-time public sourcing; it does not claim
JLCPCB uploader fulfillment. J1, MK1 and TP1–TP7 are intentionally absent from machine BOM/CPL.
J1 is manually installed; MK1 is an off-board capsule wired to its landing;
test points are bare copper.

## Mandatory order-interface checks

1. Save JLCPCB's resolved BOM table and compare it with `verification/bom_echo_gate.txt` using the BOM echo checker. Every LCSC code and MPN must match; any substitution requires adjudication before payment.
2. Manually confirm the resolved exact-BOM allocation, quantity, fees and assembly capability in the uploader before payment.
3. Confirm all 31 CPL placements are on top and inspect pin 1/polarity for D1, D2, U1, U2 and U3 against the exact pin review and `fab/rotation_human_gate.txt`. Retain the uploader previews.
4. Confirm J1 and MK1 remain excluded from machine assembly. Do not substitute a generic jack or microphone.
5. Verify the selected fabrication process and dimensions against the shipped native project. Stop for any unresolved manufacturing, allocation, rotation or substitution row.

## Manual assembly and first power

Fit exact Würth 615008160221 J1 after PCBA. Inspect eight contacts, two shield tabs and both guides. Pins 1/3/7 carry `12V_POD`; pins 2/6/8 carry `GND`; pin 4 is `AUDIO_N`; pin 5 is `AUDIO_P`; tabs 9/10 are isolated `POD_SHIELD`. Prove end-to-end cord continuity 1–1 through 8–8 and shield continuity/isolation before connecting a powered carrier. Physical plug, boot, latch, service and enclosure fit remain unqualified.

Mount the exact AOM-5024L-HD-R capsule off board, strain-relieve its wires and verify polarity at MK1. Inspect U2's exposed pad and all polarized parts. Follow `verification/first_article_test_plan.md` with a current-limited isolated supply. Stop for wrong polarity, oscillation, abnormal heating/odor, current-limit operation, out-of-range rails or settled no-signal input current above 20 mA.

## Limits and deferred work

Digital twin includes all 32 physical bodies, including the manual RJ45. Image registration measures seven resolvable bodies; 25 small bodies remain below its image-resolution threshold. Bottom component overlay is inapplicable because there are no bottom component bodies. These are nominal representation checks, not proof of manufactured fit or solderability.

The prior D1 rationale mismatch is closed: the invariant text now names the
actual S1M rectifier. Rail/noise/gain/clipping, 4 m and 15 m cable behavior,
thermal, EMC/ESD, capsule mounting, condensation, drainage and rooftop
environmental tests remain first-article holds. This package does not authorize
ordering or claim tested/production-ready hardware.

## Public-sourcing classification successor

v0.2.5 keeps every v0.2.4 fabrication, STEP, schematic, PCB, BOM, CPL and
connector-view byte unchanged. It recognizes exact surplus-backed public
observations as the configured release-time sourcing authority. Uploader
fulfillment remains a manual order-time check; physical validation,
FIRST-ARTICLE-ONLY and DO-NOT-ORDER status remain in force.
