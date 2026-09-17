review_stage: pre-route
review_kind: layout
reviewer_identity: /root/carrier_cap_land_review
context: FRESH
date: 2026-09-16
source_commit: fd8c88b2accd3df10d8b1443e1e5968e1c4f0c3b
design_verdict: SOUND
order_verdict: FIRST-ARTICLE-ONLY
qualification: FIRST-ARTICLE-ONLY
board_sha256: c03db60ae47d6737e0bab2439bc410a127b8f15acfdde82925f77f96d62287df
design_rules_sha256: 790b9c21efc3a61c742237939eaa94759f3cbb4658e8c418a69781eb1f0d5417
floorplan_sha256: 0c2ea775da88bebc2c89f13dae7dde8411550d0e9cf0f0705208a97d889ab733
route_sha256: d1c24e76e29104d2f89bc740fdd42a606518e49e1ea9e3ac72adce039d4173d4
locator_manifest_sha256: ead3b85efb53b27a1486d5a3d80b53bf778c3afef7c4d373c2801434cdde45bd
twin_report_sha256: 226dd817c4c566d0a1a6dc096071bc3339e36dfc26970bfb1757c632ed912c27
twin_overlay_report_sha256: d3f573dc408fa6ebd4154ba12b6cfe36c04eeb8abd78df76238e0e98f11f451d
orientation_receipt_sha256: b0725e7f8695a38d0ee57ddf8782e4bc3d92b4f805360ca5f5ababec4f145349
orientation_subject_sha256: 155896eb43a7c2b04c684523d4d96309bd4d945670f11a1c7a1d52b01a7a70e8
orientation_approval_sha256: 7caf0d53c2909cb74ecea7cfaba51d5f87c09a84b514bafac37b5220a7a87570
2026-09-16 final sourcing rebind: the semantic rules digest changed only by adding exact dated public-stock plans for F_IN/C22870534 and U_ADC/C42457798. Placement, pin identities, models, connector geometry, routing constraints and every safety floor remain unchanged. Exact public observations clear the configured surplus; uploader fulfillment remains supervised.


# Fresh pre-route carrier layout review

## Verdict

**SOUND** for mechanical and electrical placement admission on the exact
track-free carrier board bound above. I independently inspected the native
board, current exact twin, top courtyard overlay, opposing oblique and edge
views, all 11 connector views, and every page of the 23-page assembly locator.
I also reran the placement-stage geometry, policy, pad-separation, model
coverage and native DRC screens. I found no placement defect that prevents
routing.

The order verdict remains **BLOCKED-SOURCING** because exact allocation and the
supplier uploader preview are separate release controls. The board remains
**FIRST-ARTICLE-ONLY**; installed cable strain relief, real connector mating,
loaded thermal behavior and measured electrical performance require the
documented first article.

## Population, mounting side and assembly access

The native board contains 340 footprints and all 340 are on the front side.
The fitted population is 333 parts: 306 top-side SMD parts and 27 through-hole
parts. Three additional front-side SMD footprints are fiducials and four
non-copper footprints are mounting holes. There is no bottom-side SMD or other
bottom-mounted body.

The 27 through-hole parts are J1-J11 plus the sixteen channel film capacitors
C_A1N/P through C_A8N/P. Their bodies are accessible from the top and all
solder tails remain accessible from the unpopulated bottom. J10 and J11 are
unobstructed top-entry headers. The four mounting holes are unobstructed in the
top, bottom and oblique views. This placement supports the declared workflow
in which J1-J11 and the film capacitors are installed after automated top-side
assembly.

## Mechanical clearance and routing feasibility

Fresh placement-routability grading accepts all 7/7 checks. Its physical
placement row covers all 333 assembled envelopes with zero failures and zero
warnings. The tightest pad-to-outline margin is 2.26 mm at J1.9 against the
0.15 mm floor. The closest reported courtyard pair is
C_HOLD1/C_FILT1_470U at at least 0.100 mm; there are zero close or overlapping
assembled-envelope pairs and zero envelope-to-foreign-pad findings. The coarse
capacity screen's worst cut is 15 demanded nets versus 263 track slots, ratio
0.06 against the 0.50 failure limit. Route ownership, class-layer eligibility
and all eight U_ESD shunt endpoint topologies also pass.

The independent pad-separation screen passes 1,009 copper pads across 340
footprints: 505,544 inter-footprint copper-pad pairs and 836,186
paste-to-foreign-copper pairs were graded at the 0.090 mm JLC four-layer
advanced floor. The placement policy audit passes 5/5. These checks establish
placement legality and credible escape capacity; they do not substitute for
the downstream exact routed-board DRC and return-path gates.

Fresh scratch native DRC with zone refill and schematic parity reports three
placement-stage findings, all classified as expected starved thermals on
C_FILTER4N1.2, C_FILTER7N1.2 and C_FILTER2N1.2. It reports 499 expected
unconnected items on this track-free board and zero schematic-parity finding.
The placement DRC classifier passes and assigns the three thermals and all
opens to routing. Final routing must close them; this review does not waive
them.

## Critical electrical placement

The eight channel cells retain a regular connector-to-ESD-to-AFE-to-filter
flow, with the large film capacitors between each RJ45 edge connector and its
active cell. The central ADC and its local common-mode, supply, reset and
configuration parts remain compact. The buck, input protection, supervisor,
hold and LDO parts form a coherent west-side power cell. The clock/TDM and
both service headers retain open launch space on the east side. No component
body occupies the authored digital or ADC-clock routing corridors.

The exact twin covers 333/333 expected fitted bodies. The top overlay passes:
all 340 courtyards are drawn, 83 render-resolvable bodies are measured, 250
smaller bodies are explicitly below the render resolution threshold, zero
resolvable bodies are unmeasured, and zero bodies lack a model. The measured
body/courtyard agreement and visual top, bottom, oblique and edge inspection
show no modeled collision or mounting-hole obstruction. Supplier-model
polarity limitations for D_HOLD and the separately named order-preview items
remain owned by the render and uploader gates.

## Via-in-pad process

The exact pre-route board has eleven vias, and every one is an intentional
GND thermal via inside an exposed pad: nine in U_ADC pad 49 and two in U_LDO
pad 15. Each is exactly 0.60 mm diameter with a 0.30 mm drill, and every via is
serialized with `capping yes` and `filling yes`. There are no other base-board
vias and no accidental via-in-pad site. The floorplan authority declares the
same two arrays and process. The route authority forbids unplanned new
via-in-pad geometry and later promotes the routed C_ADC_CM6P.2 return into the
same protected family, yielding the separately gated final count of twelve.
All ordinary routed 0.20 mm drills remain outside that process family.

Fabrication still requires explicit confirmation of epoxy fill and copper cap
for the final twelve 0.60/0.30 mm sites. Placement SOUND does not permit an
open, tent-only or unspecified treatment under U_ADC, U_LDO or C_ADC_CM6P.

## Connector and cable access

The current connector-orientation receipt is bound to this exact board and
passes all 9/9 declared edge connectors; the matching user approval binds the
same semantic subject. J1-J4 face north, J5-J8 face south, and J9 faces west,
with model/footprint axis alignment 1.0 for every connector. The RJ45 mouths,
top-side mounting, keying and outward cable approaches are visible and clear
in the top, opposing oblique, edge and dedicated inside/outside views. J9's
west-facing mating approach is clear. J10/J11 are vertical top-entry headers
and do not compete with an edge cable path.

The eight RJ45s are close enough to their adjacent film capacitors that final
real-plug boot clearance, latch handling, simultaneous cable seating and
strain relief must be checked on the first article. The rendered maximum-body
envelopes and current courtyard screen reveal no present collision, so this is
a retained physical qualification rather than a source placement defect.

## Assembly documentation

The current locator manifest binds this board, the current BOM and CPL, 333
assembly parts, 23 locator exceptions/pages and all 26 manifest members. I
inspected every locator page; each target has a whole-board context, an exact
highlighted local view and numbered/polarized pad cues where applicable. The
locator therefore closes access to dense or intentionally hidden references
without relying on crowded silkscreen.

No sourcing, routing, final DRC, fabrication-upload, supplier-rotation or
first-article acceptance is inferred from this layout verdict. Those gates
remain mandatory and no safety floor was weakened.
