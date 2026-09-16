# Crow audio carrier v1 — v0.1.1 engineering release

**DESIGN: SOUND**  
**SOURCING: BLOCKED-2 (C7452883, C53283916; measured 2026-09-16)**  
**ORDER VERDICT: BLOCKED-SOURCING / DO-NOT-ORDER**  
**QUALIFICATION: FIRST-ARTICLE-ONLY**

Do not upload or purchase this archive as an orderable turnkey assembly.
C7452883 (LT3041ADE#TRPBF) has catalog stock 0. C53283916
(TMUX2821DSGR) has catalog stock 16 while five boards require 40. Obtain fresh
exact-code JLCPCB allocation evidence or make a separately reviewed source
change before ordering.

## Fabrication selections

- Four copper layers, FR-4, 1.6 mm finished thickness, 1 oz copper.
- Use the advanced-prototype drill/clearance tier encoded in the board files.
- Epoxy fill and copper cap every 0.30 mm drill / 0.60 mm copper via: the 3x3
  U_ADC exposed-pad field, the two U_LDO exposed-pad vias, and the trapped
  C_ADC_CM6P pad-2 GND return. Keep every 0.20 mm drill via ordinary,
  unfilled and uncapped. Confirm these drill families in CAM before manufacture.
- Assemble the top side only. The CPL contains 300 top-side placements and no
  bottom-side SMD placements. Follow `verification/assembly.yaml` for the exact
  declared not-assembled set.
- The eight RJ45 connectors carry proprietary balanced analog and isolated DC
  over factory Cat6 patch cable. They are not Ethernet or PoE. Never connect
  them to network equipment and power down before mating.

## Assembly and upload checks

1. Upload `fab/crow_audio_carrier_v1_gerbers.zip`, then compare the interpreted
   stack, outline, drills and all four copper layers with the loose files.
2. Upload `fab/bom.csv` and `fab/cpl.csv`. Compare every resolved part against
   `verification/bom_echo_gate.txt`; redirects or substitutions are findings.
3. Confirm the single-channel rotation worklist in
   `verification/rotation_human_gate.txt` in JLCPCB's rendered placement view.
4. Confirm the 12 Type VII filled/capped sites and that no component lead hole
   or 0.20 mm via is selected for fill/cap.
5. Do not proceed while the two sourcing rows above remain blocked.

## First power and prototype limits

Use a current-limited isolated 12 V source. Inspect polarity, shorts and rail
resistance before fitting sensitive or consigned parts. Bring up the protected
12 V path first, then 5V_BUCK, 5V_LDO_HOLD and 3V3_ADC while recording startup,
shutdown, current and temperature. Exercise reset and TDM clocks before fitting
all pod cables. Continue only under the project's first-article test plan.

This release does not claim production qualification, physical cable mating,
loaded copper temperature, analog performance, EMC, enclosure fit or outdoor
service. The remaining measured obligations are listed in `01_docs/DEFICIENCIES.md`
and `01_docs/FIRST_ARTICLE_TEST_PLAN.md` in the source tree.

## Packaging correction

This docs-only successor removes a phantom MANIFEST entry for an ignored KiCad session file that was never committed in v0.1.0. All actual fab/, source/, and3d/ files are byte-identical to that predecessor. The board, assembly, oblique connector views and four exact-board reviews are unchanged. The old release is preserved; no absent session file was retro-filled. Existing sourcing and first-article holds remain in force.

## Publication transport successor

v0.1.2 binds the same fabrication, source, STEP, schematic, and connector-view
bytes to the clean publication source commit after GitHub rejected the earlier
aggregate development history. The oversized content-addressed review packets
are retained through Git LFS; no engineering or manufacturing payload changed.
All sourcing, physical-validation, FIRST-ARTICLE-ONLY, and DO-NOT-ORDER holds
remain in force.
