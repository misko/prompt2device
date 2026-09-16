design_verdict: SOUND
order_verdict: FIRST-ARTICLE-ONLY
release_classification: unchanged physical design remains SOUND; exact public stock clears configured surplus; allocation and first article remain owed
subject: crow-audio-carrier-v1 v0.1.5 exact release board
review_source: projects/crow-audio-carrier-v1/08_reviews/pre-route_pin.md

review_stage: pre-route
review_kind: pin
reviewer_identity: /root/public_sourcing_delta_review
context: PUBLIC-SOURCING CLASSIFICATION FIX-PASS; PHYSICAL SUBJECT UNCHANGED
date: 2026-09-16
independent_design_verdict: SOUND
independent_order_verdict: FIRST-ARTICLE-ONLY
qualification: FIRST-ARTICLE-ONLY
board_sha256: 0776f364424282a7924266450f899ce69bf28cf95a602ca74d92b86fd91c164d
design_rules_sha256: f45a216fcc87beb74f390d97e97ecae9ef3a95c55fa445f2d727f5cac45cdd1f
parts_sha256: 7e43d5d63f3021d88fa96b12d4f5bd80048868bad8f66fd53bc1f112743950fd

Fresh bounded fix-pass PIN judgment: SOUND for the commissioned 61 critical references. This is an independent reviewer of the delta, with 59 unchanged primary-document conclusions inherited explicitly from the accepted collection, not 59 newly researched parts. No purchase, fabrication, assembly qualification or completed-route acceptance is granted.

2026-09-16 exact-board rebind: independent report SHA-256 a126202b3f11e89597b9b23295d69c33b4c60959f0ed64bfe031b8581118df8d proves that the current source-board delta changes only the explicit solid GND zone connection of U_ISO3.9 and U_ISO4.9, while every footprint, pad identity, position, size, layer, and all 309 SMD mounting sides remain unchanged. PIN remains SOUND under the current routing policy.

841/841 envelope inputs independently passed SHA256 and size guards before and after review. Current hashes above were computed from bytes, with parts digest using sorted relative-path/NUL/content/NUL records and rules digest using the shared semantic policy projection. There are 89 part dossiers; 88 are byte-identical to the accepted baseline. TPS389001DSER alone changes package/footprint provenance; its MPN, manufacturer PDF and pin-function mapping remain identical. The exact per-reference credited prior reviewer/report/archive, complete local electrical pad identities, current native identity comparison and inheritance decision are in per-ref-coverage.json. The old native source and prepared hashes match the prior reports. All 61 refs are accounted for once: 59 inherited PASS, U_AUDIO and U_PWR fresh PASS.

Manufacturer witness: independently rendered and viewed TI SLVSD65A PDF pages 3,24,25,26, SHA256 ee79599730e7606ba9718d9820b411020e3dcd9ff7d44572f8ee63fead15b9d0, matching the selected dossier. Page 3 explicitly shows TOP VIEW: pin1 upper left, 1/2/3 descending left and 4/5/6 ascending right, CCW. Page24 package underside uses the opposite vertical orientation; converting that bottom projection to top agrees with page3. Both native parts mount F.Cu, rotation0, component-top x right/y down. No mirror is applied. Six distinct electrical terminals exist, no EP, no fused identities. Page25 land pattern has 0.5mm pitch, 1.2mm row separation, 0.8x0.25mm pin1 and five 0.7x0.25mm lands; page26 repeats those stencil apertures and R0.05 corners.

U_AUDIO and U_PWR — VERDICT: PASS. Fresh expected/observed function comparison:

| Pin | TI function | U_AUDIO net | U_PWR net |
|---|---|---|---|
| 1 | SENSE | ADC_SENSE | PWR_SENSE |
| 2 | GND | GND | GND |
| 3 | active-low MR | PWR_EN | 5V_LDO_HOLD |
| 4 | VDD | 5V_LDO_HOLD | 5V_LDO_HOLD |
| 5 | CT timing capacitor | AUDIO_CT | PWR_CT |
| 6 | open-drain RESET | AUDIO_EN | PWR_EN |

The two supervisors retain their prior accepted divider, pull-up, timing and cascade assignments; the table verifies every changed-footprint physical identity independently. Their electrical nets and numbered pad count did not change.

TI_DSE0006A_GNDToe018 is an engineered land derivative, not an exact manufacturer recommendation. Pin2 center moves from local x=-0.60 to -0.69mm and copper length from0.70 to0.88mm: inner edge stays -0.25mm, outer edge extends from -0.95 to -1.13mm. Its original0.70x0.25mm paste at x=-0.60 is retained as a separate unnumbered paste feature. Pins1/3 retain original copper/paste. Three separate mask-only openings are added: pin1 0.70x0.15mm, pins2/3 0.60x0.15mm. This gives the explicit page25 pads1–3 solder-mask-defined detail at least0.05mm copper overlap; the extra GND toe remains covered. Pins4–6 have +0.05mm NSMD mask expansion, matching the page25 maximum. The upper land-pattern graphic is less explicit about SMD versus NSMD than the labeled detail; I used the explicit lower detail and record this interpretation, not a fabricated manufacturer endorsement of the toe. Numbered pin identities remain six per package, with four extra non-electrical features per package. No pad or identity is collapsed. Fresh geometry/DRC establishes no introduced land overlap or drill violation. Assembly/process validation remains a first-article obligation, not a new prerequisite to prototype release.

The native whole-board census remains340 footprints and985 numbered pads; total pad features1050→1058 solely reflect those eight mask/paste features. All critical identity inheritance excludes these two altered footprints. Changes to pad thermal angles and silk do not change pin function/winding and are separately reviewed in the layout block.


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


## v0.1.5 public-stock fix-pass

The exact board, schematic, fabrication payload, BOM, CPL, STEP and rendered connector subjects are byte-identical to v0.1.3. The changed assembly policy records exact LT3041ADE#TRPBF stock 1,965 against threshold 155 and exact TMUX2821DSGR stock 2,449 against threshold 190, with the configured 150-unit surplus applied by the machine checker. This closes the design-time public-stock shortages without changing a component identity. Public sourcing is CLEAR. JLC uploader fulfillment remains a manual order-time check; first-article measurements remain owed and the qualification verdict is FIRST-ARTICLE-ONLY / DO-NOT-ORDER.

## Public-sourcing authority judgment

Exact public observations clear every coded and placed BOM line at the build quantity plus the configured 150-unit surplus. The team has no authenticated JLCPCB order API; uploader allocation, mappings, substitutions, fees and assembly acceptance are therefore manual order-time checks rather than release-time sourcing evidence. The physical subject is unchanged. Public sourcing is CLEAR; physical qualification remains FIRST-ARTICLE-ONLY / DO-NOT-ORDER.
