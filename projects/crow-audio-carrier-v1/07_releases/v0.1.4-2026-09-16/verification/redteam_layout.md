design_verdict: SOUND
order_verdict: BLOCKED-SOURCING
release_classification: unchanged physical design remains SOUND; exact public stock clears configured surplus; allocation and first article remain owed
subject: crow-audio-carrier-v1 v0.1.4 exact release board
review_source: projects/crow-audio-carrier-v1/08_reviews/pre-route_layout.md



review_stage: pre-route
review_kind: layout
reviewer_identity: /root/carrier_final_delta_review
context: ASSEMBLY-POLICY PUBLIC-STOCK FIX-PASS; PHYSICAL SUBJECT UNCHANGED
date: 2026-09-16
independent_design_verdict: SOUND
independent_order_verdict: DO-NOT-ORDER
qualification: FIRST-ARTICLE-ONLY
board_sha256: 0776f364424282a7924266450f899ce69bf28cf95a602ca74d92b86fd91c164d
design_rules_sha256: f45a216fcc87beb74f390d97e97ecae9ef3a95c55fa445f2d727f5cac45cdd1f
prepared_board_sha256: 6440b4da5a8e0e2273526561ece7ef4c9e464498a484542413c59fddf08bccb3

Fresh bounded integrated LAYOUT judgment: SOUND for pre-route placement admission. The changed regions remain physically feasible with unchanged safety floors. Normal unfinished routing and exact later copper/ground/thermal grading remain owned by downstream stages. The supplied final diagnostic is not canonical acceptance, and its 0-open/2 historical supervisor-FPID mismatch statement is not substituted for current source/r0 observations.

2026-09-16 exact-board rebind: independent report SHA-256 a126202b3f11e89597b9b23295d69c33b4c60959f0ed64bfe031b8581118df8d accounts for the complete prepared-board delta as the corrected off-pad ADC3P via/link, a 0.02 mm ADC_RESET_N meeting-point move, and a width-preserving 3V3_ADC waypoint. It confirms no footprint or pad change and zero vias on all 13 governed no-via digital nets. LAYOUT remains SOUND; downstream route and final DRC gates retain ownership.

The complete actual native and source delta census is retained in native-census.json, complete-native-delta.json, deltas.json and the exact semantic source diffs. It compares all340 footprints, every pad field extracted, and every top-level native S-expression after UUID/whitespace normalization, including unchanged104 zones/keepouts, outline and board setup. Source and prepared component/pad identity/position/shape/layer extraction agrees exactly. No components are added or removed. There remain333 fitted components:306 SMD,27 THT, plus4 mounting holes and3 fiducials; all306 fitted SMD and all340 native footprints are front-side.

Actual placement/package deltas:

- U_AUDIO moves (33.0,61.1)→(33.299999,61.1)mm, rotation0. U_PWR stays (33.0,56.7), rotation0. Both adopt the separately reviewed supervisor derivative; all other electrical pads retain package-local positions and shapes.
- C_ADC_CM5N moves (94.25,77.35)→(94.45,77.35)mm, rotation-90 unchanged, with identical two pad/net identities. Its ADC5N proximity to U_ADC is freshly measured3.248877mm against4.0mm by the declared rotated pad bounding-box copper-gap metric.
- Seventeen pad-specific thermal angles are added: U_RST2.1/.4=45deg; C_ADC_CM1N.2=45; C_FILTER2N1.2=0; U_ISO4.4/.9=45; C_FILTER2N2.2=30; R_TDM_PD.2=45; C_FILTER8P1.2=60; C_PWR.2=45; U_ISO3.4/.9=45; C_FILTER5P1.2=45; R_ADC_PD1N.2=60; C_FILTER5P2.2=30; Q_PRE_EN.2=15; C_FILTER7N2.2=15. These change spoke orientation, not minimum spoke count, clearance or pad identity.
- Silk/reference presentation changes C_AUDIO,C_AUDIO_CT2,C_BUCK_IN,C_FILTER1P1,C_PWR,R_B1P,R_PWR_BOT,R_PWR_PU,U_AUDIO,U_PWR. C_AUDIO_CT2 becomes visible; R_PWR_BOT becomes hidden and replaces it in the23-reference locator/waiver census. R_PWR_PU/U_AUDIO lettering increases0.55→0.7mm. Two F.Fab reference labels follow their moved parts. Exact old/new positions/fonts/hide fields are retained in detail.log. Connector footprint serialization also reorders children with no native pad/placement change. Final assembly atlas/render acceptance remains separate; these changes do not confer a fresh atlas verdict.

Prepared r0 copper changes887→891 objects:25 old segments and3 vias removed;26 segments and6 vias added. Source native11 copper objects are unchanged. Complete coordinates, layers, widths and net names for every removed/added object are archived, not inferred from comments. Changed nets are 5V_LDO_HOLD (shorter supervisor supply landing), AUDIO_EN (via x34.2→34.4), PWR_EN (supervisor MR escape relocated to32.96,61.96), AUDIO_CT (reworked0.15mm timing tree), ADC5N (moved-capacitor fanout), ADC8P (escape via102.2,75.025→103.95,74.65), ADC3P (short local stub replacement), 5V_BUCK (1.2mm B.Cu trunk dogleg), CFG2 (added0.2mm B.Cu continuation), VMID2_EXT (new0.35mm F/B escape plus via), and GND (both supervisor0.3mm front returns and0.3/0.2mm vias). No digital seed geometry changes.

All13 digital seed-net copper censuses are unchanged; the10 populated nets contain110 F.Cu segments and zero vias. The remaining three TDM sections are absent from canonical r0, just as in the accepted baseline; their simultaneous routing feasibility is inherited from the prior independently accepted exact candidate witness. Both MCH_INPUT_SECTIONS and BUFFERED_DIGITAL_SECTIONS still explicitly require no_vias:true. Changed component placements are far from the TDM corridor, unchanged zone/keepout definitions preserve its obstacles, and the native region drawing was inspected. The deleted B.Cu digital reference projection was vacuous under these F.Cu-only requirements; the active F.Cu/In1.GND projection retains0.25mm track and0.50mm via-reference clearances. This is not permission to route digital signals on the back.

Fresh whole-board placement gates:333 assembled envelopes, zero body/courtyard-to-foreign-pad conflicts, zero warnings/failures; minimum pad-to-outline2.26mm at J1.9 versus0.15mm floor. Coarse capacity worst ratio15/263=0.06; this is only a congestion screen. All13 changed-reference adjacency roles pass, including C_AUDIO gap1.639916/2.5mm and both CT capacitors2.616414/3.0 and2.324999/3.0mm. Unchanged adjacency/physical-pin conclusions are inherited, not claimed rerun. Rotation-aware native plots inspect the supervisor, ADC south and clock/TDM regions; actual clearance judgment comes from native DRC.

Fresh scratch refill DRC with exact sidecars gives source5 starved thermals/499 opens and prepared76 violations/393 opens:38 dangling vias,24 dangling tracks,14 starved thermals. Zero shorts, copper clearances, drill clearances, edge, courtyard, track-width or library mismatch findings occur. No schematic-parity rerun is claimed. The five source thermals are C_FILTER4N1.2,C_FILTER7N1.2,U_ISO3.9,U_ISO4.9,C_FILTER2N1.2. Prepared adds C_ADC_CM3P.2,C_ADC_CM3N.2,C_FILTER4N2.2,C_ADC_CM7P.2,C_ADC_CM5N.2,C_ADC_CM1P.2,U_AFE4.4,U_CLK.4,J10.11. All require later exact filled-copper closure; J10.11 is the isolated-island case. The64 authored later ground stubs are source instructions, not already realized in r0. These preliminary findings are not intrinsic placement defects or a waiver of thermal limits.

Independently enumerated291 current drill features have minimum conservative edge gap0.500000mm (ADC3P/ADC4N); supervisor GND(31.79,60.7) to ADC_SENSE(32.45,60.45) gap0.505762mm. Thus the0.01mm local adjustment preserves the intermediate0.50mm criterion. Current prepared project explicitly sets hole-to-hole0.20mm from route_fab_overrides.txt; source project sets0.50mm. Neither is silently weakened in this review. The circle calculation conservatively uses maximum drill dimension for noncircular holes, and native DRC separately confirms the exact shapes.

Source semantic changes beyond placement are completely recorded but are downstream route implementation, not accepted realized copper: prep seeds227→230; CFG1/CFG2 move to timers; a bounded realized-width declaration is added to route wave1 and wave14 clearance strengthens0.20→0.25mm; exact additions24→29, chain edits28→103, six exact segment drops,31 via relocations,64 ground seeds,168 width edits, a0.3/0.2mm stitch-via tier, via janitor and explicit stub_scope:false; stitch passes22→34; via-current transfer census21→54 with per-barrel0.30A screening and only the genuinely parallel input pair summed at1A. The source itself labels the IPC capacity assumption as a retained screening basis, not an independently derived rating. These instructions require exact later geometry/current/DRC gates. No routed-board acceptance is borrowed from them.

Current connector human approval40e3171bc656b349 (machine9/9,human9/9) is retained as the supplied existing authority; connector geometry is unchanged and no new user approval is requested. First-article physical, loaded thermal and electrical holds remain at their documented first-article boundary. Order verdict remains DO-NOT-ORDER because this review does not own release/order authorization.

Evidence: actual scripts, raw logs, runtime receipts, complete census/deltas, guards, fresh DRC, current scratch board copies, primary page renders and independent native-region drawing are in evidence.tar.gz. Initial plotting attempt failed because matplotlib was unavailable; the retained failure was resolved using Pillow, without altering source. Native KiCad API warnings about unspecified via-layer width are preserved; widths were independently confirmed by exact native S-expression census, and no warning was treated as an engineering pass.

Per-reference PIN coverage trace (prior report/archive identifiers and pad rows are in per-ref-coverage.json):

U_AFE1: PASS — inherited accepted primary review; unchanged complete native identity.

U_AFE2: PASS — inherited accepted primary review; unchanged complete native identity.

U_AFE3: PASS — inherited accepted primary review; unchanged complete native identity.

U_AFE4: PASS — inherited accepted primary review; unchanged complete native identity.

U_AFE5: PASS — inherited accepted primary review; unchanged complete native identity.

U_AFE6: PASS — inherited accepted primary review; unchanged complete native identity.

U_AFE7: PASS — inherited accepted primary review; unchanged complete native identity.

U_AFE8: PASS — inherited accepted primary review; unchanged complete native identity.

U_CLK: PASS — inherited accepted primary review; unchanged complete native identity.

U_RST1: PASS — inherited accepted primary review; unchanged complete native identity.

U_RST2: PASS — inherited accepted primary review; unchanged complete native identity.

Q_DUMP: PASS — inherited accepted primary review; unchanged complete native identity.

Q_PRE_EN: PASS — inherited accepted primary review; unchanged complete native identity.

Q_RST1: PASS — inherited accepted primary review; unchanged complete native identity.

U_ADC: PASS — inherited accepted primary review; unchanged complete native identity.

U_LDO: PASS — inherited accepted primary review; unchanged complete native identity.

U_ESD1: PASS — inherited accepted primary review; unchanged complete native identity.

U_ESD2: PASS — inherited accepted primary review; unchanged complete native identity.

U_ESD3: PASS — inherited accepted primary review; unchanged complete native identity.

U_ESD4: PASS — inherited accepted primary review; unchanged complete native identity.

U_ESD5: PASS — inherited accepted primary review; unchanged complete native identity.

U_ESD6: PASS — inherited accepted primary review; unchanged complete native identity.

U_ESD7: PASS — inherited accepted primary review; unchanged complete native identity.

U_ESD8: PASS — inherited accepted primary review; unchanged complete native identity.

J10: PASS — inherited accepted primary review; unchanged complete native identity.

J11: PASS — inherited accepted primary review; unchanged complete native identity.

J9: PASS — inherited accepted primary review; unchanged complete native identity.

J1: PASS — inherited accepted primary review; unchanged complete native identity.

J2: PASS — inherited accepted primary review; unchanged complete native identity.

J3: PASS — inherited accepted primary review; unchanged complete native identity.

J4: PASS — inherited accepted primary review; unchanged complete native identity.

J5: PASS — inherited accepted primary review; unchanged complete native identity.

J6: PASS — inherited accepted primary review; unchanged complete native identity.

J7: PASS — inherited accepted primary review; unchanged complete native identity.

J8: PASS — inherited accepted primary review; unchanged complete native identity.

U_DUMP: PASS — inherited accepted primary review; unchanged complete native identity.

U_LDO_EN: PASS — inherited accepted primary review; unchanged complete native identity.

U_OE: PASS — inherited accepted primary review; unchanged complete native identity.

U_TDM: PASS — inherited accepted primary review; unchanged complete native identity.

U_TDM_SCH: PASS — inherited accepted primary review; unchanged complete native identity.

Q_IN: PASS — inherited accepted primary review; unchanged complete native identity.

Q_PRE: PASS — inherited accepted primary review; unchanged complete native identity.

C_FILT1_470U: PASS — inherited accepted primary review; unchanged complete native identity.

C_FILT2_470U: PASS — inherited accepted primary review; unchanged complete native identity.

C_HOLD1: PASS — inherited accepted primary review; unchanged complete native identity.

C_HOLD2: PASS — inherited accepted primary review; unchanged complete native identity.

D_BUCK_IN: PASS — inherited accepted primary review; unchanged complete native identity.

D_HOLD: PASS — inherited accepted primary review; unchanged complete native identity.

U_AUDIO: PASS — fresh TI primary figure and current native comparison.

U_BUCK: PASS — inherited accepted primary review; unchanged complete native identity.

U_PWR: PASS — fresh TI primary figure and current native comparison.

U_ISO1: PASS — inherited accepted primary review; unchanged complete native identity.

U_ISO2: PASS — inherited accepted primary review; unchanged complete native identity.

U_ISO3: PASS — inherited accepted primary review; unchanged complete native identity.

U_ISO4: PASS — inherited accepted primary review; unchanged complete native identity.

U_ISO5: PASS — inherited accepted primary review; unchanged complete native identity.

U_ISO6: PASS — inherited accepted primary review; unchanged complete native identity.

U_ISO7: PASS — inherited accepted primary review; unchanged complete native identity.

U_ISO8: PASS — inherited accepted primary review; unchanged complete native identity.

D_IN: PASS — inherited accepted primary review; unchanged complete native identity.

D_QIN_GS: PASS — inherited accepted primary review; unchanged complete native identity.


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


## v0.1.4 public-stock fix-pass

The exact board, schematic, fabrication payload, BOM, CPL, STEP and rendered connector subjects are byte-identical to v0.1.3. The changed assembly policy records exact LT3041ADE#TRPBF stock 1,965 against threshold 155 and exact TMUX2821DSGR stock 2,449 against threshold 190, with the configured 150-unit surplus applied by the machine checker. This closes the design-time public-stock shortages without changing a component identity. Authenticated JLC allocation or acquired exact-part consignment, uploader checks and first-article measurements remain owed; the order verdict is BLOCKED-SOURCING / DO-NOT-ORDER.
