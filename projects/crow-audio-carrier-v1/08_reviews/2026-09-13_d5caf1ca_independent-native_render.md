subject: crow-audio-carrier-v1 d5caf1ca native pre-route scene
date: 2026-09-13
reviewer: /root/rj45_carrier_render_approved
context-given: zero-context frozen native render packet
source_commit: 2623f978b7d444fff26d9dbf1e18a39c22a1b115
board_sha256: d5caf1ca050a466569325567cdc826d99f998ed58ce9a3e204e86d96a8bad9de
design_verdict: SOUND
order_verdict: DO-NOT-ORDER

review_stage: pre-route
review_kind: render
reviewer: /root/rj45_carrier_render_approved — fresh independent Codex reviewer
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: d5caf1ca050a466569325567cdc826d99f998ed58ce9a3e204e86d96a8bad9de
design_rules_sha256: ccf8a8adb3d10b89b0f9019af60279f512eb39ff330bbf45109fbe9e3e10c0b7
subject_raw_sha256: c7bcad8f75375807a48441385bf59c4aa466f797ea90275a0bec37632b9024e0
subject_semantic_sha256: 030f0b09d5c6a27e4528c2316365e08bb80b129890f65636e7a7441fb350ffc9
envelope_canonical_sha256: e4bd5ec2e9b1294e36fe79eb7c4c2562c6706ed617e8e41baf3dc2ebb9ecadf3

The current native carrier scene is SOUND for the commissioned pre-route render review. I found no demonstrated wrong mounted side, connector-facing error, nominal body collision, missing fitted native model, or undeclared hidden component reference. This verdict covers the complete native board scene, not catalog-twin A-RENDER fidelity, locator assembly acceptance, routing acceptance, ordering, or physical qualification. FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains in force. Factory Cat6A/RJ45 carries custom analog/DC; it is not Ethernet or PoE and mating is power-off.

I independently inspected the full top, full bottom, four cardinal and two elevated current native images; all eleven current annotated orientation views; and native top, registration-overlay and two side images for each of the six current registration groups. The existing user connector-orientation approval was not used as a substitute for this judgment. I requested no further approval and made no source, placement, model, or routing changes. No additional camera recipes were needed.

Identity and population evidence

The frozen envelope contains 692 inputs, all verified before review and after review. The semantic design-rule digest was recomputed by the frozen pre_route_review_check.design_rules_digest(project), rather than hashing one rules file. Native PCB bytes match the observed/rendered board identity. All 340 scene placement rows match the native positions and rotations; every one of 333 model instances matches its source filename, transform, show state and scene-recorded model content hash. Seven model-free items are exactly H1–H4 and FID1–FID3. The population includes zero DNP footprints; 317 modeled parts mount on top, 16 on bottom. The seven model-free fabrication features also reside on top. There are 32 distinct footprint/model combinations. The native board has 0 tracks, 11 thermal vias and 81 zones; these counts do not establish routing or DRC acceptance.

The same-board model_registration.md, accepted aggregate bundle/index/stage receipt and all six group reports, receipts and bundle outputs were reopened. All 88 group output files verify, and each group binds the exact current board. The groups cover J1–J8, J9, J10/J11, U_ISO1–U_ISO8, F1–F8 and R_PWR_TOP: 28 references total. The 11 annotated orientation image identities and 22 producer evidence files also verify. The native registration reports describe their own measurements; my separate whole-board judgment combines direct image inspection, native pcbnew enumeration, source placement/model data and broad-phase geometric checks.

Connector and board observations

| References | Native coordinates/orientation | Independent observation |
|---|---|---|
| J1–J4 | (36,25.86), (68,25.86), (100,25.86), (132,25.86) mm; 0 degrees; top | Four distinct mouths face north, with eight contacts, shell fingers and upper latch/key recess visible. Nominal mouth plane is 0.50 mm outside the north edge. |
| J5–J8 | (45,114.14), (77,114.14), (109,114.14), (141,114.14) mm; 180 degrees; top | Four distinct mouths face south with the same visible construction and 0.50 mm nominal mouth exposure. Rear shells remain physically occluded in places by the film capacitors in the populated oblique view. |
| J9 | (28,69) mm; 90 degrees; top | Two separate power cavities face west. Top boss/ramp, mouth and rear direction agree across outside, inside, top and profile views. Source mouth offset 8.92 mm gives 0.92 mm nominal edge overhang. |
| J10/J11 | (158,49), (158,80) mm; 90 degrees; top | Two separate vertical 2x6 headers with twelve posts each. They are unshrouded; no physical key is invented. Pin-1 pad datums and label identities are available; MCH TDM/MCH SENSE and DO NOT SWAP captions agree with their positions. Nominal modeled body ends at x=169 mm, 1 mm inside the east edge. |

The board outline is the source 150 x 100 mm rectangle, x=20..170 and y=20..120 mm, 1.6 mm thick. Native edge bounding box including its 0.10 mm stroke is [19.95,19.95,170.05,120.05] mm. Four open 3.2 mm mounting holes at (25,25), (165,25), (25,115), (165,115) are visible on both sides. Each drill has 3.4 mm nominal edge margin. The smallest hole-to-modeled-Fab gap is H1 to J1, 4.291919 mm; this does not qualify any selected screw-head or standoff envelope. All three top fiducials are visible.

Body, underside and polarity observations

All 141 explicit source anchors match the board. All 333 modeled footprints have mounted-side Fab shapes. A same-side screen of their Fab shape bounding boxes, including stroke widths, finds no overlap; its smallest gap is 0.5375 mm between C_LDO_NR5 at (68.8,73.3) and R_LDO_SET at (68.8,74.6). This is a broad-phase screen, not a BREP collision solver or manufacturing-tolerance sweep. F_IN's native maximum 7.98 x 5.44 mm body exceeds its standard Fab shell, so it was checked separately: its closest nominal envelope gap is 0.63 mm to D_IN. The visible board scene agrees with separated component bodies, including the four upright electrolytics, sixteen film capacitors, ADC, regulators, inductors, diodes and repeated channel circuits.

F1–F8 and U_ESD1–U_ESD8 are the exact sixteen underside parts. The full bottom scene shows eight fuse bodies and eight small ESD packages between the jack pin rows. Source side and coordinates were checked rather than inferred from their top-view absence. Each ESD Fab box has at least 0.50 mm to the nearest jack copper-pad bounding box. Each fuse Fab box has about 1.495 mm to the nearest locating-hole bounding box. These are conservative plan screens of nominal artwork and do not qualify solder fillets, protruding leads, soldering access, or an enclosure bottom.

C_HOLD1's positive pad is west; C_HOLD2 and C_FILT1_470U/C_FILT2_470U have positive pads east. Visible dark negative sectors oppose those pad-1/plus locations. D_BUCK_IN's cathode stripe and K mark are south; D_IN and D_HOLD stripes agree with their west pad-1 ends. Small IC pin-1 marks and lead layouts are coherent where visible. True manufacturer marking details on the derived models remain illustrative; occluded exposed pads and exact vendor legend printing are not established by these pixels.

The CROW AUDIO CARRIER / FIRST ARTICLE / DO NOT ORDER, POD AUDIO +12V / NOT ETHERNET OR POE, J9 isolated-input/no-hot-plug, channel and header captions are legible in the top evidence. Twenty-five component references are intentionally hidden and match refdes_waiver.json exactly: C_AUDIO_CT2, C_FILT1_10U, C_FILT2_10U, C_PWR_CT, C_VDDA2_10N, C_VMID1_470N, C_VMID1_4U7, C_VMID2_470N, C_VMID2_4U7, R_ADC_BOT, R_ADC_PD1P, R_ADC_PD6N, R_ADC_TOP, R_AUDIO_PD, R_AUDIO_PU, R_DUMP_TIME2, R_FILT1P, R_IN6N, R_PRE_G, R_PWR_BOT, R_PWR_TOP, R_VMID1_BOT, R_VMID1_TOP, R_VMID2_BOT, R_X6N. There are no undeclared hidden body references or unused waivers. H1–H4/FID1–FID3 also hide their fabrication-feature references. A declared visible field is not a guarantee of assembled-board readability beneath tall bodies; locator coverage remains a separate gate.

Findings and limits

- INFO NATIVE-01; J1–J8, the connector coordinates above; owner: mechanical/first-article qualification. Full free-state finger extent is X[-5.058081,12.218081], Y[-6.360054,7.090000] mm in the frozen exact-product source record. Thus the full nominal width is 17.276162 mm and adjacent 32 mm-pitch jacks retain 14.723838 mm between those enclosing extents. Ordinary registration erosion omits thin finger pixels; the Fab union cannot independently identify the retained shell rectangle. The right courtyard centerline margin is only 0.001919 mm. I therefore do not interpret the registration's zero-outward result as a manufacturing containment guarantee. These declared limits do not demonstrate a nominal whole-board collision. Installed finger deflection, panel bonding, plug/latch sweep and service access remain first-article holds.
- INFO NATIVE-02; J1–J11 and U_ESD1–U_ESD8; coordinates retained in native-measurements.json; owner: assembly/first-article qualification. Real rear-body and lead occlusion remains in the full scene. Native source and the registered coupon datums establish mounted sides and attachment correspondence, while wholly hidden contact interfaces, solder fillets and mating fit are unjudgeable from these images. Molex undimensioned cavity/latch details and omitted pegs, Samtec simplified posts, generic capacitor envelope and other source-declared nominal/maximum models retain their stated limitations. No new pre-route hardware prerequisite is imposed.
- INFO EVIDENCE-01; project/06_build/pre_route/orientation-supplement, whole board; owner: evidence publisher. Two supplied supplement images were opened and visibly depict the superseded Molex spoke population with missing ordinary models. They are rejected for this exact-board judgment. Their exact identities are recorded as rejected; no historical render verdict was adopted.
- OUT-OF-SCOPE HOLD; whole board; owner: root/catalog-twin reviewer. Native model registration 6/6 and this SOUND native review do not close catalog-twin A-RENDER, locator assembly checks, route review, release or first-article acceptance.

There are zero blocking native render findings. The evidence records which images were actually viewed; counts of declared models are not presented as automated pixel visibility counts. Full-board images are 2384 x 1568 pixels after the renderer's window crop and were displayed with application resizing; subpixel nominal distances come from source, not pixel measurement. No camera, model or part was removed to manufacture visibility.

Methods and delivery

Read-only measurements ran with /usr/bin/python3 -B and shared pipeline_runtime.run_stage, explicit scratch cwd, inherited environment with bytecode disabled, finite 90-second per-stage budgets and lossless combined stdout/stderr/runtime records. An initial JSON serialization attempt failed on pcbnew UTF8 and was corrected by converting that field to text; its raw failure and method version are retained. The first runner wrapper had a post-success return-code attribute error; the child evidence and completed runtime receipt remained intact and the wrapper was corrected. Neither changed source or supplied evidence. Packaging reopens all regular archive members and records size/hash; final preflight verifies the exact envelope, read-only scope and five-file delivery. A delivery PASS grades the complete honest handback, not orderability.
