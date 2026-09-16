subject: crow-mic-pod-v3 current pre-route render
date: 2026-09-13
source_commit: abbae71edeab8d1addf9a8912d64c7c23c88ec7e
context-given: zero-context; exact current source/native board/r0/renders
source_report_sha256: b2208e539ce4a19bd1e825d51f2b716ff4f1384b5f4aa85a0ee6f56e6d53d76e
source_evidence_archive: 01_docs/journal/060f268c3ed0a8272759473e97527790b690fc4f1342c938982a2ba11d006bfd.tar.gz

review_stage: pre-route
review_kind: render
reviewer: /root/rj45_pod_render_approved — fresh independent Codex reviewer
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: a44b769b1a5ad5fa959b476bd30f91a64aeaba9ad64d7868fa4e60ffbb62ee48
design_rules_sha256: 02c4ed58432368b92e3019a06bf20c137dbf90765af16c96c458790e88d54a9f
prepared_board_sha256: 33b5148e76e630df8aa23a0013c89109579aa49dd0668b6df1f89d38cb7429b9

The current nominal PCB placement is SOUND in this independent pre-route render review. No unresolved render or nominal mounting-placement defect was found. This accepts the rendered physical placement only; it does not accept global routing, manufacturing fit, assembly process, electrical performance, an order, or outdoor deployment. FIRST-ARTICLE-ONLY / DO-NOT-ORDER remains in force. This is custom analog/DC over the exact factory Cat6A/RJ45 cord, not Ethernet or PoE. Mating and unmating require power off.

## Exact subject and actual methods

The envelope subject is raw d55e761ed1db7d56550ed36e8da49666c6fe5ce95071f828412388ba79c6ecb1 / semantic db44ae2506bbdae57e63ce7bd63d3dcdbc2ab4485e3cc6608002a88845dca975. All 499 envelope inputs were SHA-256/size verified before and after review. The design-rules digest was independently recomputed with the supplied semantic digest function; it is not the raw .kicad_dru file digest. The native board and prepared r0 were opened through pcbnew 10.0.4 without saving. The extracted complete footprint, pad, model, side, reference and courtyard records are identical between them.

I actually opened both approved_native_top.png and approved_native_bottom.png, all five current populated cardinal/top views, all five J1 orientation views, six current J1 registration images, and four current U2 registration images. I also produced and opened one additional full-scene bottom view with rotate=25,0,0 through the supplied render_board.py, on a byte-identical isolated project copy. No part was removed or hidden. Its model resolver reported 32/32 paths. In total, 23 rendered images and the rasterized manufacturer drawing page were viewed and retained; viewed-images.json binds every original file identity. Original full images are retained even where the viewing tool downscaled its display. All actual engineering scripts, raw stdout/stderr and runtime records are archived.

The same-board aggregate model_registration.md, stage receipt, aggregate bundle/index, both selected group reports, receipts, bundles and images were reopened. Forty-three group-output/orientation evidence hash links were independently verified. Current authority contains exactly J1 Wurth 615008160221 and U2 TI DGN0008G; the leftover MicroFit group and failed/historical views were not used as acceptance evidence. P-ORIENT user approval was not substituted for this judgment.

## Measured census and nominal physical fit

The outline is x=20..80, y=20..60 mm: 60 × 40 mm, 1.6 mm thick, two copper layers. There are 44 footprints: 32 modeled bodies (31 SMT parts plus manually fitted J1), seven bare probe pads TP1–TP7, one two-wire landing MK1, and four mounting holes. Modeled bodies occupy 31 top / 1 bottom; all footprints occupy 43 top / 1 bottom. U3 is the sole bottom body. There are 113 pad objects: 103 numbered electrical/probe lands, six NPTH objects, and four unnumbered paste-only U2 apertures. The 103 numbered lands comprise 84 SMT copper pads, 10 J1 electrical pads, two MK1 wire lands and seven test pads. These classes are not interchangeable assembly parts.

All 903 pairs of top-side footprint courtyard bounding boxes were compared; none overlap. There is no second bottom footprint courtyard to collide with U3. This conservative XY screen is supplemented by the real populated images; it is not an enclosure collision solver. The nearest J1 top-side courtyard neighbors are D1 at 0.610 mm and TP5 at 0.737494 mm, using pcbnew courtyard polygons. The Fab-outline aggregation includes connector EMI fingers and is not treated as a rectangular molded-housing dimension.

J1 native anchor is (45.500,25.860), front, 0°. Its mouth is at y=19.500, nominally 0.500 mm beyond the north edge y=20; outward access is board -Y. All outside/inside/profile views agree. The keyed/latch opening is visible facing outside; the rear contact structure faces the PCB interior. The two shell tabs, two guides and eight contacts correspond visibly to the footprint. The official Wurth drawing page 1 was inspected: native contact drill Ø0.8 mm, same-row pitch 2.04 mm, row separation 4.00 mm, stagger 1.02 mm, guide drill Ø3.18 mm at 13.70 mm spacing, shell slots 1 × 2 mm at 14.80 mm spacing, and board thickness 1.6 mm match its nominal pattern. Native signal rows are y=25.86/29.86; guides are (42.22,26.56)/(55.92,26.56); shell slots are (41.67,23.51)/(56.47,23.51). The manufacturer axial body dimension is 13.45 ±0.15 mm. It does not close the installed contact-to-mouth/enclosure tolerance stack.

The J1 group receipt reports 12/12 attachment centers, 0.024067 mm center delta and zero measured outward courtyard excursion. U2 reports 13/13 centers (including paste apertures), zero center delta, 0.903466 mm beyond the body Fab envelope from gull-wing leads, and zero outward courtyard excursion. I inspected their populated/bare/overlay images and found the described registration credible. The U2 lead rows visibly align with the pad rows. Registration proves neither solder quality nor manufactured fit.

U3 is at (49.070,27.860), bottom, native rotation 180° after the side transform. Its Fab body spans x=48.420..49.720, y=27.060..28.660. The added underside angle shows the eight J1 tails around, rather than through, its body. Analytic outer pad bounding boxes, derived from actual pad center/size/rotation, give a 0.675 mm minimum separation for U3.1–J1.5, U3.3–J1.6, U3.4–J1.4 and U3.5–J1.3. The U3 courtyard remains at least 0.405 mm from J1 land extents; the Fab body remains at least 0.550 mm away. These are conservative XY lower bounds, not solder-fillet tolerance claims. Earlier inscribed-polygon measurements are retained as raw diagnostics; corrected-physical-bounds.json supersedes their slightly optimistic circle extents. The TI DRL package drawing specifies 0.6 mm maximum height; the footprint pin-1 triangle and model dot agree in the underside view. Side views naturally obscure some bottom details; no absence claim relies on those occluded pixels.

H1/H2/H3/H4 are (24,24), (76,24), (24,56), (76,56), all Ø3.2 mm NPTH. Each hole rim is 2.4 mm from the nearest board edge. Their approximately 3.45 mm-radius footprint courtyard envelopes remain clear; the closest other courtyard to a mounting center is TP4 at 3.753751 mm from H3. The actual TP4 copper pad is 5.0 mm center-to-center from H3, leaving 2.65 mm hole-rim-to-pad clearance. All four holes are visible and accessible in the bare nominal board scene. Screws, washers, standoffs and the enclosure are not present, so their installed fit is not asserted.

## Labels, polarity and intentional absences

All 32 modeled-body reference labels are visible in the correct silk layer, at 0.6 mm height and minimum 0.12 mm stroke. The bottom U3 reference at (49.07,34.86) is separated from the pin field and unambiguous because U3 is the only bottom part. Functional captions have 0.45..0.65 mm height and minimum 0.1125 mm stroke, meeting the authored 0.45 mm floor. They are legible in the actual images; print-process fidelity at this small size remains an assembly/fabrication matter.

The unobscured J1 pin map reads 1/3/7:12V, 2/6/8:G, 5:+, 4:- and agrees with measured pad nets. The NOT ETHERNET / NOT POE warning is clear at (67,29). D1 cathode stripe corresponds to west pad 1 VIN_PROTECTED at (37.5,35.6); D2 stripe corresponds to north pad 1 VIN_PROTECTED at (27.3,35.85). U1/U2/U3 pin-1 cues are visible and agree with their local footprint orientation. F1 has a separate PTC legend. The probe labels correctly identify 12V, PROT, 5V, VREF, A+, A− and GND; TP5/TP6 are AUDIO_P/AUDIO_N. They are intentionally bare copper, not missing fitted bodies.

MK1 has no capsule model because it is an off-board capsule wire landing. Native pad 1 MIC_RAW is the square positive land at (73,45), pad 2 GND the circular land at (73,40), with Ø1.2 mm holes and 5.0 mm pitch. The plus mark, landing outline and MK1 WIRE LANDING + / − caption make that use clear. A dedicated power-off-mating instruction is not printed in the visible captions; that requirement remains in the governing interface/operating instructions. The render does not establish installed cable or capsule behavior.

## DRC and routing boundary

A fresh native DRC ran on the byte-identical scratch board with --severity-all --refill-zones --schematic-parity --exit-code-violations. It reports zero violations, 58 unconnected item findings and zero schematic-parity findings. Every one of the 58 exact raw finding/node pairs, coordinates and UUIDs is retained individually in drc-classification.json as EXPECTED_PRE_ROUTE_OPEN, next owner root/routing-layout owner. The five ignored native check categories are retained in that file. No generalized open count replaces the node rows. This is not a routed-clean claim. The native board contains zero tracks/vias; r0 contains 78 preparation tracks and eight vias, with identical placement. Those launches are not accepted as a global route by this render lens.

## Retained physical holds, distinct from placement defects

- HOLD / first article, J1 at (45.5,25.86), pads 1–10 and both guides: exact factory-cord seating, latch release/pull test, installed tolerances, solder seating and enclosure reaction/load path are unqualified. The selected nominal mate envelope and 67 mm bend-planning floor do not prove hand access or manufactured fit. Next owner: root / mechanical integration and first-article qualification.
- HOLD / first article, U3 at (49.07,27.86), pads 1–5 beside J1 tails: bottom-side paste/CPL, assembler DFM acceptance, manual jack soldering and actual solder-fillet clearance remain owed. Nominal physical separation is acceptable. Next owner: assembly/process owner.
- HOLD / first article, MK1.1 (73,45), MK1.2 (73,40): exact capsule enclosure mounting, wire strain relief, polarity, drainage and acoustic/environmental qualification remain owed. Next owner: mechanical and first-article owner.

There are zero unresolved nominal design-placement/render defects in this scope. Cable continuity/shield isolation, electrical qualification, UV/environmental obligations and all source order holds remain active. No source, checkpoint or live board was edited, no routing was performed, no physical limit was increased and no gate was bypassed.
