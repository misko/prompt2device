subject: crow-audio-carrier-v1 current physical render and assembly locator
date: 2026-09-12
reviewer: Codex independent judgment agent /root/carrier_owned_render_review
context-given: FRESH isolated exact-current physical-render and locator packet
source_commit: b9d77ca73ac2b7eff4111e07bd8a8a0d6376d22e
board_sha256: ef72e6d2f5400b481f397532a58784644b82bc88d5fa527f4c46b7a3356c822b
design_rules_sha256: 53529b7c990d7a8313be7515483aaff9d5b92f2bf8f4b8b34c4153b39aac9b23
review_stage: pre-route
review_kind: render
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
completed_at: 2026-09-12T06:25:30Z
locator_manifest_sha256: 503e9326edf22ccd65e05d7aa23d50aba9fb261d81556937bc00100066fbcacd
locator_reviewed_refs: ["C_AUDIO_CT2","C_FILT1_10U","C_FILT2_10U","C_PWR_CT","C_VDDA2_10N","C_VMID1_470N","C_VMID1_4U7","C_VMID2_470N","C_VMID2_4U7","R_ADC_BOT","R_ADC_PD1P","R_ADC_PD6N","R_ADC_TOP","R_AUDIO_PD","R_AUDIO_PU","R_DUMP_TIME2","R_FILT1P","R_IN6N","R_PRE_G","R_PWR_BOT","R_PWR_TOP","R_VMID1_BOT","R_VMID1_TOP","R_VMID2_BOT","R_X6N"]

# Exact-current physical render and assembly-locator review

I find the exact current carrier board **SOUND for the pre-route visual and assembly-locator lens**. The order verdict remains **DO-NOT-ORDER**. This review does not admit routing, fabrication, assembly, or ordering.

I opened the current native full-top render, twin top and bottom, both isometric views, east/west edge views, the structural courtyard overlay, current front/back populated profiles, and the J9 top/outside/inside views. The 333 mounted bodies form a plausible, coherent population with no visible collisions or side errors; connector bodies face the expected access edges; the eight repeated channel blocks and CH1 through CH8 captions are consistent; J10/J11 are separately placed and the `J10=MCH J1 TDM  J11=MCH J3 SENSE  DO NOT SWAP` guidance is legible. J9's outside/cable direction agrees with the retained connector-orientation witness. The exact producer output binds all these current artifacts to board SHA-256 `ef72e6d2f5400b481f397532a58784644b82bc88d5fa527f4c46b7a3356c822b`.

I inspected every one of the 25 current 2400×1600 locator PNG pages at legible size. Each page has a unique whole-board marker and an enlarged target with body highlight and numbered pads; its reference/value, MPN/LCSC, top-side rotation, KiCad coordinates, pad-to-net list, board hash, operating instructions, and page/ref footer are readable and internally coherent. Page order and identities exactly match the machine-readable `locator_reviewed_refs` field above. The frozen exact checker independently compares those pages to the native board, grouped BOM, CPL, and exact source exceptions, and reports 333/333 assembled references, 995 assembled pads, 25/25 exceptions/pages, and 28 manifest members. It also proves that the 25-page PDF embeds the PNG pages in the same order. The HTML's actual shipped JavaScript passes a valid-to-unknown transition test: selection, details, pad table, crosshair, and URL hash all clear.

The two newly visible labels are acceptable in their exact native context. `R_DUMP_TIME1` is placed next to its vertically oriented resistor and remains distinct from `R_DUMP_TIME2`; `R_VMID2_TOP` appears beside the corresponding upper VMID2 divider part and remains distinguishable from `R_VMID2_BOT`. Both agree with the authored preferred offsets. The current locator/native identity set contains 333 assembled references, with 308 visible references and exactly 25 hidden references covered by the atlas; the 25-reference ceiling is retained.

The complete twin population is 333/333 bodies: 300/300 CPL bodies plus 33/33 declared manual-install bodies. Its structural overlay grades 84/333 bodies from pixels and reports PASS, with 249 bodies below the optical resolution floor, zero resolvable-but-unmeasured bodies, and zero missing bodies. Those 249 remain a model-resolution limit rather than a visual measurement. The retained connector-orientation evidence is current to this board and records PASS for J1 through J9; the existing 9 connector semantic approvals are unchanged.

The remaining limits are material. Three diode/model uploader and polarity-order holds remain (`D_BUCK_IN`, `D_HOLD`, and `D_QIN_GS`); no order-preview polarity approval is supplied here. Physical source qualification remains SOURCE PASS but FULL INCOMPLETE: 11 exact, 10 conservative, and 21 unknown evidence entries out of 42. Installed connector mating, cable fit/bend/strain relief, enclosure clearance, service operations, analog performance, and thermal/fault qualification remain open under ADR0007. `LAYOUT-001` routing is outside this visual scope and remains unaccepted.

Admission used canonical envelope SHA-256 `9ac7ebeb67840c4ed5b547c5665487c850a59ba4bd09f6a7a11d2e22a61ceb91`; the pretty-printed envelope file separately hashes to `bc5f6d34bb180e8439558dc597d592570c47b7392d8c8c92a8dd4b99563e36cc`. All 1,095 packet inputs matched their declared size and SHA-256 before and after review. Producer commands, runtime receipts, exact checker output, UI state-transition output, pixel-inspection coverage, and derived crops are preserved in the evidence archive.
