# Final routed-board render and physical review

subject: crow-mic-pod-v3 routed board at 08b79dbce2857341632c5224263db60adb4274e5
date: 2026-09-03
reviewer: Codex independent exact-board render/physical lens
context-given: full-tree; exact routed board, BOM/CPL, stored outputs, and fresh read-only renders
source_commit: 08b79dbce2857341632c5224263db60adb4274e5
board_sha256: a932200e0976418383fae0c131dfe2a5768c00ef261b611762ccd3507f05ca8f
bom_sha256: 905e78de505fa93aebf2c092371a62bedeb59b8cab9adc484108397f8089e49c
cpl_sha256: c310bc5e94e5689507a29849372d7103426253ad8b532c1729ace9c59eb3199e
design_rules_sha256: 0cbb7cab0be102a78062338cd69688b8d7de20728e9e3e40cd9907fa374ecf84
prelayout_inputs_sha256: a662d56e1e32d38b22960cb37facfa29dd2fda9a3374556b98c7d4ed7b681aaa
prelayout_checkpoint_sha256: 9016b9f58a7ba8bacb16237e8d6ebdb38e3feed12b3b6ec27cd2e7e9831c8a08
render_top_sha256: a8d9b46acb97e45960dba732a9103152b75368cca4a9b40fe3e90b401ad34ada
render_bottom_sha256: 1806ba93537afcff02e3f86792bc83e9b12379a62ceddda6935c73b1b488fd88
render_front_sha256: 34ae03f6a249c95f842b8fc2615731cdecc346304c295042b1515343e7a51d76
render_back_sha256: 00b66d68fa4e69e997f9ec348c4dce0b83b2520b440048dd7fe74cd0775563c7
pcb_layers_pdf_sha256: 74aac8aa656fc884fc2a328a9814ea75e9dc87a7b8c890d8060209defb37c1e7
assembly_pdf_sha256: 0fb3cd2bf0d6838bd2f4def008190f3a3f8a88b933e7eb29891e1e3a07c23389
model_coverage_sha256: aa8657aa91d86a45d6ed8d41f213a9cab8dff894e8f453d17c041a8b2cc2b732
native_drc_sha256: 52666334dc34f19355f0167dcea12fdf76e7da208ea153f9b49efd2cf9220d19
realized_route_receipt_sha256: db2a88eb683583363c2011528aeb6afe8d42389af42465a025a56ef02765a3dc
route_acceptance_receipt_sha256: c590e736ae947e60ef0f8fc0858f4c563bd2c73cc87cddf118bb9016f0d0c19d
design_verdict: SOUND
order_verdict: BLOCKED-SOURCING

## Scope and verdict

I independently inspected the exact routed board above. Evidence included the
four current final renders, both current vector PDFs, fresh high-resolution
top/bottom/front/back/left/right and perspective renders, model-stripped
top/bottom views, and fresh F.Cu/B.Cu route plots. I also reopened the exact
BOM and CPL and replayed the board-bound mechanical and copper checks.

The render/physical verdict is **SOUND**. No P0, P1 or P2 finding remains in
this lens. This is a design verdict only; the order verdict is
**BLOCKED-SOURCING**, and the board remains **DO-NOT-ORDER**.

The final layout seal and agent handoff are intentionally not bound here.
The governed flow includes every `08_reviews` file in its source census, so
those downstream receipts must be issued only after all independent reviews,
including this one, are committed. Treating a pre-review seal as final would
create a stale or self-referential evidence chain.

## Population, service geometry and markings

- All population is top-side. Model coverage resolves 32/32 fitted bodies:
  the 31 machine-placed SMT references plus the manually fitted J1 body. H1-
  H4, TP1-TP7 and the MK1 wire landing are correctly represented as bare board
  features rather than invented fitted components.
- The four 3.2 mm M3 mounting holes and all seven function-labeled probe pads
  remain unobstructed. J1 and MK1 retain clear solder access from below.
- J1 is top-mounted on the north edge and faces outward. Its square pad 1,
  `J1 1:12V 2:G 3:+ 4:-` legend and physical access direction agree.
- D1/D2 cathode bands, U1/U2/U3 pin-1 marks and MK1 square-pad / `+` polarity
  are mutually consistent in the board, models and silkscreen.
- `CROW POD V3`, `NOT ETHERNET / NOT POE`, `PTC`, the J1 map, all seven test-
  point functions and `MK1 WIRE LANDING + / -` remain readable after
  population. No fitted body is inverted, underside-mounted, visibly
  colliding, or obstructing a mounting/tool approach.

## Copper and exact assembly artifacts

Fresh native KiCad DRC reports zero violations, zero unconnected items and
zero schematic-parity findings without changing the board hash. The routed
board contains 255 segments and 57 identical 0.60/0.30 mm vias across F.Cu and
B.Cu. Fresh route plots show continuous, cleanly formed copper, intact ground
fills, no mounting-hole intrusion, no suspicious exposed spur and no visible
acute/sliver artifact. The exact realized-route audit passes all 22/22 local
path and connector-first ordering checks; the composed route-acceptance
receipt remains accepted.

The BOM contains 22 grouped rows covering 31 unique fitted SMT references.
The CPL contains exactly the same 31-reference set, all on the top side, with
zero measured placement-datum error. BOM source identity passes for every row,
including 16/16 encoded R/C value checks, and all 22 comments are legible.
J1, MK1 and TP1-TP7 are absent from machine placement by explicit assembly
policy: J1 is hand-soldered after PCBA, MK1 is an off-board capsule connected
at a two-wire landing, and TP1-TP7 are bare probe pads. Release order paperwork
must preserve that exact `not_assembled` decision.

## Explicit claim boundary and holds

The J1 model is a conservative drawing-derived body envelope, not exact
manufacturer latch or mating CAD. These renders therefore do not prove actual
mate/unmate force, latch access, cable bend/service clearance, crimp quality,
continuity or enclosure fit. The off-board microphone capsule, wire strain
relief, acoustic polarity, windscreen, drainage, condensation control and roof
environment are likewise absent from this board-level subject.

No authenticated JLCPCB PCBA allocation, resolved uploader preview, rotation
preview or economics receipt exists. The public catalog screen is not order
authority. Before any order, the operator must verify the exact BOM/CPL and
every polarity/rotation in JLC's resolved preview, preserve the manual J1/MK1
operations, and close the connector, cable, enclosure, electrical, acoustic,
environmental and first-article test holds. Nothing in this review claims
fabricated fit, assembled performance, environmental readiness, or production
readiness.
