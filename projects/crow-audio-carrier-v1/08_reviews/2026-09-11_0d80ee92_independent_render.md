# Independent current render / assembly-readability review

- subject: raw `f1a0cf347b9a6e374354987eae3efe920aeba23e5113fd1603871974fab242a9`; semantic `b253285c03fe36318da6bb5aacfb1a149f672ed0703646726129c42e4c156c80`
- source_commit: `7bfb3a9e` (generated PCB uncommitted checkpoint)
- reviewer: fresh independent judgment agent `current-render-review`
- context_given: frozen read-only project packet; no children; no routing or release acceptance
- completed_at: `2026-09-11T21:39:05.176821Z`
- review_stage: pre-route
- review_kind: render
- board_sha256: `0d80ee923dbbae34995fa892e5fc2224b489e5d4afc1a03dc2a7836c44a31058`
- design_rules_sha256: `072e13c96a25657108d8e7df0df4dd646433dfbbde696fbc8ae41513aae01b30`
- design_verdict: **DEFECTIVE**
- order_verdict: **DO-NOT-ORDER**

## Basis and coverage

I inspected all supplied complete manufacturing-twin views (top, bottom, two isometrics and both board edges), the native orientation overview and its front/back/left/right views, representative inside/outside connector views for J1, J5 and J9, and every supplied native-registration group/overlay for F1-F8, J1-J9, J10/J11, U_ISO1-U_ISO8 and R_PWR_TOP. I also viewed quadrant enlargements of the complete top image and independently re-opened the owning twin overlay against a byte-exact copied board.

The assembly denominator is **333 bodies**: BOM **51 data rows** (52 physical lines), CPL **300 data rows** (301 physical lines), plus **33 manual-placement bodies**. Final model-path coverage is **333/333**. The re-opened overlay reproduces **84/333 expected bodies optically measured**, **249 below the stated 2 mm resolvability floor**, **0 resolvable-but-unmeasured**, **0 without a model**, against **340 courtyards** at the stated **1 mm tolerance**. This is honest partial optical coverage; it is not 333 individual optical confirmations.

The raw connector-orientation overview was rendered without the model-directory defines and therefore is connector-local evidence, not a complete native-body census. A diagnostic wrapper run against a displaced copied board resolved only 284/333 because `$KIPRJMOD` context was absent. The same model-aware `render_board.py` run against the immutable exact source board resolved **333/333** and produced `native_full_top.png`; I viewed it and found all body classes populated, on the front side, and physically coherent with the twin. The complete twin bottom view shows no backside-installed bodies, consistently with the assembly data. I found no omitted or floating body in the resolvable views.

## Blocking findings

**P4 refdes legibility — blocking source defect.** The source reports **308/333 visible** reference designators and **25 hidden**, with a 0.7 mm minimum-height and 0.16 mm clearance regime. The exact hidden set is `C_AUDIO_CT2, C_FILT1_10U, C_FILT2_10U, C_PWR_CT, C_VMID1_470N, C_VMID1_4U7, C_VMID2_470N, C_VMID2_4U7, R_ADC_BOT, R_ADC_PD1P, R_ADC_PD6N, R_ADC_TOP, R_AUDIO_PD, R_AUDIO_PU, R_DUMP_TIME1, R_DUMP_TIME2, R_FILT2P, R_IN6N, R_PRE_G, R_PWR_BOT, R_PWR_TOP, R_VMID1_BOT, R_VMID1_TOP, R_VMID2_TOP, R_X6N`. Each affected footprint has its F.SilkS reference hidden and mechanically parked at offset **(+9.0,+9.0) mm** with 0.55 mm text; the F.Fab duplicate remains. `refdes_waiver.json` is generator output enumerating the condition and is not an evidence-backed project waiver. The existing W-FLOOR ceiling is 9 and cannot increase.

Source repair is required for the power/control group `C_AUDIO_CT2, C_PWR_CT, R_ADC_TOP, R_ADC_BOT, R_AUDIO_PU, R_AUDIO_PD, R_PRE_G, R_PWR_TOP, R_PWR_BOT, R_DUMP_TIME1, R_DUMP_TIME2`; these are distinct assembly/service functions and have no present documentation exception. Source repair is also required now for the central precision/filter group `C_FILT1_10U, C_FILT2_10U, C_VMID1_470N, C_VMID1_4U7, C_VMID2_470N, C_VMID2_4U7, R_FILT2P, R_VMID1_TOP, R_VMID1_BOT, R_VMID2_TOP, R_ADC_PD1P` and the channel-6 repeated-cell group `R_IN6N, R_X6N, R_ADC_PD6N`. A future documentation exception could be evaluated only for the latter dense/repeated groups if it supplies an exact board-hash locator map, coordinates, assembly/service workflow and owner; none exists in this packet. Measurements show real density rather than a blanket excuse: `C_PWR_CT` is 0.04 mm from `C_FILTER1P2`; `C_VMID1_470N` and `C_VMID2_470N` intersect the U_ADC envelope; the paired VMID parts have 0.29 mm separation; `R_IN6N` is 0.27 mm from U_AFE6; `R_PWR_TOP` is 0.27 mm from U_PWR. Repair must place readable F.SilkS references or supply an approved, hash-bound documented locator exception; no waiver is inferred here.

**P5 functional ownership — blocking source defect.** Seven channel captions `CH1, CH2, CH4, CH5, CH6, CH7, CH8` lie beneath their installed connector bodies and disappear in the populated native/twin views. Board-coordinate bounding-box measurement gives **2.999 mm² overlap for each caption** with its connector body envelope, equal to the full 2.350 × 1.276 mm caption box within rounding. CH3 has **0 mm² overlap** and is visibly placed in a clear strip. Move the seven captions into similarly visible strips while keeping each closest to its own connector. This blocks assembly/service comprehension even though connector reference designators and the J10/J11 “DO NOT SWAP” legend remain readable.

## Body, orientation, polarity and evidence limits

The complete native and twin views agree on major placement, side and connector egress. J1-J4 face the north edge, J5-J8 the south edge and J9 the west edge; their mouths are accessible. The existing exact-semantic user connector-orientation approval remains binding and is not re-requested. It does not qualify an installed harness.

Native registration evidence is visually and numerically credible for the supplied groups: F1-F8 center deltas 0.005-0.031 mm with 16/16 pad overlaps; J1-J8 0.031-0.051 mm and J9 0.009 mm; U_ISO1-U_ISO8 0.011-0.037 mm; R_PWR_TOP 0.004 mm; J10/J11 centers 0.021/0.000 mm with 12/12 drilled centers. Vendor pad-fit remains **UNAVAILABLE** for the eight fuses and R_PWR_TOP because catalog CAD is absent; exact native source-selected bodies are retained, but this does not prove terminal metallurgy or assembly process. The Samtec J10/J11 receipt grades mount side `not-graded` and supplies no orthogonal native side profile. Provide a signed-side native coupon/profile before order; this is evidence owed rather than an observed misplaced body.

Visible polarized capacitor markings and silk `+` marks are coherent in the full render. The overlay log still records `D_BUCK_IN` as mount-fallback (best pad fit 0.57 mm vs 0.5 mm), `D_HOLD` as polarity-check/polarity-fit-blind, and `D_QIN_GS` as polarity-check. Resolve these three exact-part transforms/polarity in the assembler uploader/order preview before order. The render does not close those part-specific facts.

## Scope

This verdict covers rendered body presence, registration evidence, side/orientation, labels and assembly/service readability. It makes no fresh full-pin, electrical, routing, terminal-metallurgy, manufacturing-process, or layout-corridor acceptance. `LAYOUT-001` remains OPEN outside this visual lens. Delivery completeness passes despite the engineering verdict being DEFECTIVE.
