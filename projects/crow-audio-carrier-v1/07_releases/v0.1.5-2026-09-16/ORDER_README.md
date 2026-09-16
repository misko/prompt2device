# Crow audio carrier v1 — v0.1.5 engineering release

**DESIGN: SOUND**

**PUBLIC SOURCING: CLEAR — exact public observations clear quantity plus the configured 150-unit surplus**

**ASSEMBLY FULFILLMENT: ORDER-TIME CHECK — confirm exact mappings, substitutions, fees and capability in the uploader**

**ORDER VERDICT: FIRST-ARTICLE-ONLY / DO-NOT-ORDER**

**QUALIFICATION: FIRST-ARTICLE-ONLY**

Do not upload or purchase this archive as an orderable turnkey assembly.
Current exact-part public evidence reports 1,965 LT3041ADE#TRPBF units through
ECIA TrustedParts' authorized channel and 2,449 TMUX2821DSGR units at DigiKey.
Those observations clear the configured thresholds of 155 and 190: the
five-board requirement plus 150 units per aggregated BOM line. They are not a
reservation or a claim about JLC assembly fulfillment. Because this project
has no authenticated JLCPCB order API, confirm exact mappings, substitutions,
fees and assembly capability manually in the eventual uploader session.

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
5. Before payment, confirm every exact part in JLCPCB's resolved table or
   acquire and admit the exact part through the consignment process.

## First power and prototype limits

Use a current-limited isolated 12 V source. Inspect polarity, shorts and rail
resistance before fitting sensitive or consigned parts. Bring up the protected
12 V path first, then 5V_BUCK, 5V_LDO_HOLD and 3V3_ADC while recording startup,
shutdown, current and temperature. Exercise reset and TDM clocks before fitting
all pod cables. Continue only under the project's first-article test plan.

This release does not claim production qualification, physical cable mating,
loaded copper temperature, analog performance, EMC, enclosure fit or outdoor
service. The remaining measured obligations are preserved in
`verification/deficiencies.md` and
`verification/first_article_test_plan.md` inside this archive.

## Public-sourcing classification successor

v0.1.5 keeps the v0.1.4 board, fabrication payload, STEP, schematic and
connector-view bytes unchanged. It recognizes exact surplus-backed public
observations as the configured release-time sourcing authority. No copper,
BOM, CPL, component identity, placement or routing changed. Uploader checks
remain order-time work; physical FIRST-ARTICLE-ONLY and DO-NOT-ORDER holds
remain in force.
