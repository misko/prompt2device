# Fresh independent carrier pre-route native render review

review_stage: pre-route
review_kind: render
reviewer: Codex GPT-6 independent reviewer /root/rj45_carrier_render_locator_toponly3
context: FRESH
completed_at: 2026-09-14T03:33:29.725622+00:00
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: 92a4e2fc0fecde845f2dfa0d9e2f5bfbd943372962fb449d699a98d957fc5633
design_rules_sha256: 7e0d0f0eae778e8332e9597a7345955b2b9423921d5decb980190d97e8721d4c
locator_manifest_sha256: 1dbd47a33fd57e5cd5af3c2ad52fe444e2479ad89fe5cfd7c67e4b6c4a2e91dd
locator_reviewed_refs: ["C_AUDIO_CT2","C_FILT1_10U","C_FILT2_10U","C_PWR_CT","C_VDDA2_10N","C_VMID1_470N","C_VMID1_4U7","C_VMID2_470N","C_VMID2_4U7","R_ADC_BOT","R_ADC_PD6N","R_ADC_TOP","R_AUDIO_PD","R_AUDIO_PU","R_DUMP_TIME2","R_FILT1P","R_IN6N","R_PRE_G","R_PWR_TOP","R_VMID1_BOT","R_VMID1_TOP","R_VMID2_BOT","R_X6N"]

## Judgment

The exact frozen carrier board is sound for the pre-route native-render gate. The complete native top, front, back, left, right, oblique, connector-detail, and corrected native bottom evidence show a coherent full-board assembly. J1-J8 expose their RJ45 mouths outward in two opposed edge rows; J9 exposes the keyed power inlet toward the west edge; J10 and J11 are upright top-entry headers. The views preserve the real occlusion between parts rather than hiding bodies.

The corrected bottom render is consistent with the board source and with an independently repeated exact bottom-render recipe. It contains only the expected through-board pads, pins, retention pegs, mounting holes, and nominal connector geometry visible beyond the edges. It does not show fitted SMD bodies under the board. In particular, F1-F8 and U_ESD1-U_ESD8 are all source-measured on F.Cu and their bodies are absent from the underside image. The repeated render has the same 1568x872 composition and only a mean absolute ray-sampling difference of 0.0204-0.0215 levels per RGB channel.

Source census: 340 total mounted footprints, all 340 on F.Cu and zero on B.Cu; 309 footprints consist entirely of SMD pads, all on F.Cu and zero on B.Cu. There are 333 model-bearing fitted component bodies. The exact seven model omissions are H1, H2, H3, H4, FID1, FID2, and FID3. Those omissions are nominal mechanical mounting-hole/fiducial features, not missing fitted component bodies. Four rectangular Edge.Cuts primitives form the board boundary; 21 NPTH instances comprise the four board mounting holes, sixteen RJ45 retention pegs, and the J9 mechanical hole.

The accepted model-registration aggregate and all six underlying registration groups were reopened with their plan, side, and overlay imagery. The exact-board aggregate is PASS; tuple-bound bodies agree with footprint Fab/courtyard and drilled-centre or SMD-pad datums within their stated tolerances. No unintended body-to-body or body-to-board interaction is visible. Connector pins and retention pegs crossing the PCB plane are intentional.

The complete locator HTML contains all 333 assembly parts, and its manifest binds the exact board, BOM, CPL, generator, template, and checker. Every one of the 23 locator PNG pages and all 23 rasterized PDF pages was inspected. Each page clearly identifies its exception reference in a whole-board map and an enlarged local view with a unique highlighted body and numbered pads. The HTML, JSON, PDF, and 23 PNG hashes all match the manifest.

## Findings

- none

## Limits and release posture

Pixel evidence cannot qualify production tolerances, connector mating force, enclosure clearance, or service access. Native Fab/render geometry remains nominal, and small bodies can be occluded in whole-board views; source coordinates, footprints, registration overlays, and dedicated connector views resolve the reviewed side/datum facts. Catalog component-body twin fidelity is a separate gate and was not inferred from the native 333/333 body census. The board remains unrouted. Factory Cat6A/RJ45 carries custom analog/DC rather than Ethernet or PoE and requires power-off mating. FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains mandatory.
