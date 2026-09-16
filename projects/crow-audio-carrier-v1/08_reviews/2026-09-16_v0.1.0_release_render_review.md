design_verdict: SOUND
order_verdict: BLOCKED-SOURCING
release_classification: design verdict preserved from the independent review below; order verdict narrowed by exact shipped stock evidence dated 2026-09-16
subject: crow-audio-carrier-v1 v0.1.0 exact release board
review_source: projects/crow-audio-carrier-v1/08_reviews/pre-route_render.md

review_stage: pre-route
review_kind: render
reviewer_identity: /root/carrier_final_delta_review
reviewer: /root/carrier_final_delta_review
context: FRESH
date: 2026-09-16
completed_at: 2026-09-16T06:29:00+00:00
independent_design_verdict: SOUND
independent_order_verdict: DO-NOT-ORDER
board_sha256: 0776f364424282a7924266450f899ce69bf28cf95a602ca74d92b86fd91c164d
design_rules_sha256: f45a216fcc87beb74f390d97e97ecae9ef3a95c55fa445f2d727f5cac45cdd1f
locator_manifest_sha256: a0ad839da81520c03a107f2a24f14f096c9901b29dfe0887230a46a11cb34dfb
locator_reviewed_refs: ["C_FILT1_10U", "C_FILT2_10U", "C_PWR_CT", "C_VDDA2_10N", "C_VMID1_470N", "C_VMID1_4U7", "C_VMID2_470N", "C_VMID2_4U7", "R_ADC_BOT", "R_ADC_PD6N", "R_ADC_TOP", "R_AUDIO_PD", "R_AUDIO_PU", "R_DUMP_TIME2", "R_FILT1P", "R_IN6N", "R_PRE_G", "R_PWR_BOT", "R_PWR_TOP", "R_VMID1_BOT", "R_VMID1_TOP", "R_VMID2_BOT", "R_X6N"]

SOUND for the commissioned pre-route render and locator scope. No new source geometry defect observed. FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains; empty routing and diagnostic Gerbers are expected pre-route evidence, not fabrication release.

2026-09-16 exact-board rebind: independent report SHA-256 a126202b3f11e89597b9b23295d69c33b4c60959f0ed64bfe031b8581118df8d confirms unchanged component/model placement and all-front-side SMD population. The exact locator was regenerated twice from the current board with identical output; its JSON is identical after removing the board hash, and all 23 page-image differences are confined to the printed board-hash footer. RENDER remains SOUND. A transient live catalog fetch failure during an additional twin attempt adds no new geometry evidence and grants no sourcing or order acceptance.

All 333 native and twin fitted references have matching position, rotation and side. All 309 SMD-attributed footprints are on F.Cu (306 fitted plus three fiducials); 27 fitted THT bodies. The underside shows only board features and THT legs, with no fitted underside body. All 333 native model hash bindings verified.

The three full-frame obliques collectively expose both opposing RJ45 mouth rows. J1-J4 face the upper edge; J5-J8 face the lower edge; J9 faces left; J10/J11 are vertical top-entry with TDM/SENSE labels. Corner holes and board approaches are clear of modeled bodies. Existing nine-connector explicit user approval for subject 40e3171bc656b3496a0cd620e9bcd65e5246b618aae9147ea889a6c7e06b10bd remains valid and was not requested again. Real capacitor occlusion remains.

All 23 locator PNG pages were actually opened and usable. R_PWR_BOT is now page 18 at (30.000,56.700), 180 degrees, pad 1 PWR_SENSE on the right and pad 2 GND on the left; C_AUDIO_CT2 is no longer an omission page. Native targets are identified by numbered pads and local body context rather than nearby silk. The exact checker passed 333 references, 1051 pads and 23 pages. Native Fab bounding rectangles are locator context, not production body measurements.

Retry provenance: previous packet was diagnostic after provider failure. This new packet was independently reopened and all images reinspected; native/twin audit, locator and HTML checks rerun with new paths. Audit and packaging script methods reused, never their prior results.

Verified every one of 1054 envelope input sizes and SHA256 before and after review.

Fresh visual inspection of every image in image_bindings; no geometry changes, hidden-body tricks, new cameras or source adoption.

Independent pcbnew native/twin census, all mounting sides/coordinates/rotations, owning semantic rules digest and all 333 native model-instance hash bindings; installed KiCad libraries only outside frozen packet, never live project.

Shared runtime exact locator checker: 333 refs, 1051 pads, 23 pages, 26 manifest members; all PDF images decoded and compared; HTML data/SVG checked.

Shared runtime actual shipped HTML control function: 333/333 selections and 7/7 startup cases.

Read current TPS389001 dossier and engineered TI_DSE0006A_GNDToe018 source; freshly opened TI SLVSD65A PDF pages 24 and 25. Package 1.45..1.55 mm square, height <=0.8 mm, 0.5 mm pitch; left SMD/right NSMD mask detail and asymmetric pad 1 confirmed. Covered 0.18 mm ground toe is an authored engineering extension, not a TI verbatim recommendation. Current twin reports U_AUDIO/U_PWR fit 0.06 mm and model registration 0.02 mm.

Unchanged primary research reused explicitly from frozen prior independent report: Wurth p1, Molex p1, Samtec p1, US1B p4, B340A p6, TI DSG p30, Littelfuse p6, Yageo p4 and six native-registration groups. These pages were not falsely claimed freshly reopened here; current changed board/renders reviewed afresh.

R1 — coverage-limit — RETAINED

A-RENDER PASS measures 83/333 bodies, with 250 below 2.0 mm resolvability floor, zero resolvable unmeasured and zero missing models. Maximum listed center delta 0.555 mm at D_HOLD; limit 1.00 mm. Action: Retain explicit unresolvable census; do not claim 333 independent body measurements.

R2 — catalog-limitation — MOUNT-FALLBACK-RETAINED

Raw catalog numbered-pad fit 0.570 mm exceeds 0.5 mm. Declared common-centroid fallback and unchanged primary US1B land research support retaining source; catalog 5.14 mm pitch does not supersede native 4.00 mm pitch. Action: Retain fallback annotation and exact supplier preview check; do not import discrepant catalog lands.

R3 — order-hold — OPEN-ORDER-PREVIEW

POLARITY-CHECK and D_HOLD POLARITY-FIT-BLIND remain; symmetric body fitting cannot prove cathode orientation. Existing single-channel order-preview list remains owed. Action: Retain and perform all named final human supplier-preview orientation checks before ordering.

R4 — representation-limit — DECLARED-NATIVE-RETENTION

17 coded parts retain native representations (9 without independent catalog CAD and 8 without catalog body); 33 local/manual bodies retain native models. Action: Preserve nominal/max-envelope qualifications; native model registration is not independent catalog body confirmation.

R5 — first-article-hold — PHYSICAL-QUALIFICATION-OWED

Modeled mouths and board-level approaches are unobstructed, but plug/boot/latch access, tolerances, simultaneous seating and loaded service need physical qualification. Tall film capacitors cause real rear-view occlusion. Action: Retain physical first-article mating, continuity, pin-1 and service checks; not a new prototype-fabrication prerequisite. Factory Cat6A/RJ45 carries custom analog/DC only, not Ethernet/PoE; power off for mating.

R6 — method-limit — DISCLOSED

23 actual PNG pages visually inspected; PDF page images decoded and pixel-matched by exact checker; HTML geometry and 333 selection functions checked. No browser raster/layout session was performed. Action: Accept inspected PNG/PDF atlas for visual presentation; do not claim browser-specific layout review.

Exact locator visual acceptance:

| Page | Ref | X, Y mm | Rotation | Result |
|---:|---|---|---:|---|
| 1 | C_FILT1_10U | 96.750, 62.550 | 0.0 | PASS |
| 2 | C_FILT2_10U | 96.750, 77.450 | 0.0 | PASS |
| 3 | C_PWR_CT | 36.000, 55.300 | 0.0 | PASS |
| 4 | C_VDDA2_10N | 91.000, 71.500 | 180.0 | PASS |
| 5 | C_VMID1_470N | 90.600, 65.700 | 180.0 | PASS |
| 6 | C_VMID1_4U7 | 90.700, 63.900 | 180.0 | PASS |
| 7 | C_VMID2_470N | 90.600, 74.300 | 180.0 | PASS |
| 8 | C_VMID2_4U7 | 90.700, 76.100 | 180.0 | PASS |
| 9 | R_ADC_BOT | 30.900, 64.500 | 90.0 | PASS |
| 10 | R_ADC_PD6N | 69.750, 85.100 | 180.0 | PASS |
| 11 | R_ADC_TOP | 32.700, 64.500 | 90.0 | PASS |
| 12 | R_AUDIO_PD | 37.170, 59.650 | 90.0 | PASS |
| 13 | R_AUDIO_PU | 34.200, 63.400 | 90.0 | PASS |
| 14 | R_DUMP_TIME2 | 58.650, 78.200 | 0.0 | PASS |
| 15 | R_FILT1P | 88.000, 61.300 | 0.0 | PASS |
| 16 | R_IN6N | 67.550, 91.000 | 0.0 | PASS |
| 17 | R_PRE_G | 43.600, 61.000 | 0.0 | PASS |
| 18 | R_PWR_BOT | 30.000, 56.700 | 180.0 | PASS |
| 19 | R_PWR_TOP | 30.000, 54.900 | 180.0 | PASS |
| 20 | R_VMID1_BOT | 73.800, 74.600 | 90.0 | PASS |
| 21 | R_VMID1_TOP | 72.000, 74.600 | 90.0 | PASS |
| 22 | R_VMID2_BOT | 78.200, 75.700 | 90.0 | PASS |
| 23 | R_X6N | 65.900, 92.350 | 180.0 | PASS |


2026-09-16 final route-delta rebind: fresh independent Sol Medium integrated
review is SOUND on the exact current board, prepared route and accepted routed
board. The board/prepared hashes, all footprint/pad placement and connector
orientation subjects remain current; only the semantic rules digest changed.
The reviewed delta is confined to source-governed ADC3P restoration validation,
the ADC4P local notch/shared CM3 ground-via geometry and the fail-closed stitch
backstop. Exact native DRC is 0/0/0, analog paths pass 155/155, zero-via groups
retain zero realized vias, and all via/fabrication floors remain unchanged and
passing. This rebind grants no sourcing, ordering or first-article acceptance.

2026-09-16 CM6P redundant-spur rebind: fresh independent Sol Medium read-only review found this placement lens SOUND. The removed entry is under `stitch.seed_stubs`, after track-free preparation, so it cannot alter the exact pin, footprint, pad, placement, locator, model, or render subjects. The authoritative base-board SHA-256 remains `60aa7f6740255f9943eb92779b33f793a097e9b093923105a58141b3642623bf`; the prepared r0 SHA-256 remains `6440b4da5a8e0e2273526561ece7ef4c9e464498a484542413c59fddf08bccb3`. Fresh replay confirmed P-ROUTEBASE 340 footprints, 132 base/prepared vias, and 760 prepared segments; A-LOCATOR remains 333 refs, 1051 pads, 23 exceptions/pages, and 26 manifest members; P-ORIENT passes 9/9 machine and 9/9 human. FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains mandatory.

2026-09-16 CM6P Type VII final rebind: fresh independent Sol Medium read-only review found this lens SOUND. The exact route delta restores the short `C_ADC_CM6P.2` GND seed and adds `protect_via_in_pad` after exact-geometry restoration, promoting all 12 realized SMT-land barrels into the existing 0.60/0.30 mm epoxy-filled, copper-capped drill family. The assembly remark now names the U_ADC EP49 3x3 field, U_LDO EP15 pair, and CM6P.2 return; every 0.20 mm drill remains ordinary. This is a routed fabrication-process realization, not a schematic or track-free subject change. The native probe passes 601/601 vias, 12/12 via-in-pad sites, 12 protected/589 ordinary/0 partial, with zero non-library DRC or unconnected finding. FIRST-ARTICLE-ONLY / DO-NOT-ORDER and uploader confirmation remain mandatory.
