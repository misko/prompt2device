commission: crow-audio-carrier-v1 exact current-board render and assembly-locator acceptance
subject: raw b4a8b2ab79ec9b8b03f7757a65a0e4054b1fdb143678618ac3b26b19c512e1f3; semantic 0eab8e10b5836744779dce26ca9f4500488fa5154bc757f653454ead113d4361
reviewer: Codex independent judgment agent /root/carrier_locator_render_review
completed_at: 2026-09-12T00:03:12Z
review_stage: pre-route
review_kind: render
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: 9aa1c2c821a31129176a8b519b9a211d78dfc011adb997a64470c03d0726891f
design_rules_sha256: 94251d1c7cb043c66d402d55b5cf89bac74f7ae0927b012556113ae56d7a2471
source_commit: f7fd347e
locator_manifest_sha256: 62359dcb06ffc184d47a929e9bc1c7233e845506ea222eefa22ea94540bc0928
locator_reviewed_refs: ["C_AUDIO_CT2","C_FILT1_10U","C_FILT2_10U","C_PWR_CT","C_VMID1_470N","C_VMID1_4U7","C_VMID2_470N","C_VMID2_4U7","R_ADC_BOT","R_ADC_PD1P","R_ADC_PD6N","R_ADC_TOP","R_AUDIO_PD","R_AUDIO_PU","R_DUMP_TIME1","R_DUMP_TIME2","R_FILT2P","R_IN6N","R_PRE_G","R_PWR_BOT","R_PWR_TOP","R_VMID1_BOT","R_VMID1_TOP","R_VMID2_TOP","R_X6N"]

# Independent current render and locator review

I inspected every one of the 25 supplied 2400 × 1600 locator atlas PNG pages at original resolution. Each page visibly names one and only one reviewed exception reference, value, MPN, LCSC identity, top-side rotation, native X/Y coordinates, numbered pads and pad nets. Each whole-board marker and enlarged target view identifies a unique physical body/pad pattern. Page order is 1 through 25 and matches the manifest list above. The pages are legible enough for assembly and service identification when used with the exact hash-bound release.

The independent exact structural check passed with 333/333 assembled native references, 995 assembled pads, 25/25 documented exception pages and 28/28 manifest members. That check re-opened the native board and compared every locator reference, value, side, rotation, position, Fab-body extent, numbered-pad geometry/net identity, BOM MPN/LCSC identity and CPL datum. It also compared the embedded HTML dataset and clickable reference set, verified PNG metadata identities, and decoded all 25 PDF page images to prove PDF-to-PNG image and ordering equality. The independently recomputed raw manifest digest matches the header. The shipped UI contains all 333 references; an executed state-transition check confirmed that a valid lookup selects the exact body and populates identity/pads, while a subsequent unknown lookup clears the old selection, identity, pad table, crosshair and URL hash.

## P4 and P5 disposition

The 25 references absent from F.SilkS are a dense, explicitly enumerated exception rather than an unidentified omission. For this DO-NOT-ORDER first-article prototype, the source-owned locator closes P4 at this review stage: it is owned by the Carrier board design owner, bound to the exact board/BOM/CPL/config/tool hashes, provides exact coordinates and side/rotation, gives body and numbered-pad/net context, carries operating instructions, and has complete visual and structural coverage. This acceptance is conditional on distributing this exact locator with assembly and service materials. It does not authorize production, a future board hash, or assembly without the locator.

I inspected the exact current native full-top image and current twin top/isometric views. CH1 through CH8 are all visible beside their own channel connector/component group; none is under an installed connector body. Their left-to-right and top/bottom ownership remains unambiguous, and the J10/J11 “DO NOT SWAP” operating legend and board-edge first-article/DO-NOT-ORDER instructions are visible. The previously blocking P5 caption condition is closed.

## Bodies, sides, connectors and polarity

The exact native full-top and portable twin agree on the complete populated placement: all 333 expected bodies are present on the component side, with no installed bottom-side bodies. Top, bottom, both isometrics, both edge views and the bare-top comparison show no floating, omitted or wrong-side body. Major connector egress is physically coherent: J1–J4 face north, J5–J8 face south, and J9 faces west. J10/J11 are top-entry headers. I also inspected the corrected Samtec front/right side views and overlay; the signed front-side proof measures a 0.830808 front fraction, 12/12 drilled centers for each header, and 0.021/0.000 mm center deltas. Existing P-ORIENT machine 9/9 and human 9/9 semantic approval remains applicable because connector identity and geometry are unchanged.

The current overlay remains honest partial optical measurement: 84/333 expected bodies measured, 249 below the 2 mm optical-resolution floor, zero resolvable-but-unmeasured and zero missing-model bodies. Native source/model receipts and the exact pin-transfer receipt support the unresolvable population; they do not turn the 249 small bodies into individual optical measurements. The existing physical-qualification split remains 20/42 qualified, with the same manual-placement, model-absence, catalog-CAD, terminal-metallurgy and process limits. The fuse and R_PWR_TOP source-selected models remain visually plausible while vendor pad comparison is unavailable.

Visible polarized capacitor marks and silk `+` marks remain coherent. Three existing uploader/order-preview holds remain open exactly as before: D_BUCK_IN uses a mount fallback after a best 0.57 mm fit exceeds the 0.5 mm limit; D_HOLD requires polarity check and is polarity-fit-blind; D_QIN_GS requires polarity check. These holds are preserved and prevent an order verdict.

## Scope and retained holds

This SOUND verdict covers exact-current rendered body presence, side, gross rotation, connector presentation, polarity markings, service captions, and the complete assembly-locator exception workflow. It transfers the already accepted full-pin judgments only through the exact 340-footprint/1002-pad equality receipt and does not re-grade them. LAYOUT-001 remains open and outside this visual review. Routing, clearances, signal integrity, thermal/pulse performance, harness qualification, terminal metallurgy, supplier process and release approval are not accepted here. The board remains DO-NOT-ORDER.
