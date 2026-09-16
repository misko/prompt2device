subject: crow-audio-carrier-v1 isolated native CAD retention source projection
date: 2026-09-11
reviewer: carrier_cad_retention_review (fresh judgment)
context-given: frozen 96-item packet; envelope SHA256 7ec02266fa8982bc0c54d811bac45ce3f0bd6f08773065546a60ab71cc2db76b
source_commit: db86586129445c88b37d0a6a9ba52d6cec19d0b8 plus exact enumerated source diff
board_sha256: 0d80ee923dbbae34995fa892e5fc2224b489e5d4afc1a03dc2a7836c44a31058
design_verdict: DEFECTIVE
order_verdict: DO-NOT-ORDER
scope: Retention code and nine-ref image review; original defect retained and separately dispositioned.
original_report_sha256: c799efda219de0ad06aba15bf8ba17e02ce630bd6fa5902b47bab92f61383b4c

# Independent CAD-retention implementation and image review

Engineering verdict: **FAIL (one bounded A-RENDER expected-body defect).** Delivery/review completeness is PASS. The strict `vendor_cad_absent` selection, `all_smd_pad_overlap` registration mode, nine dedicated registrations, signed-side evidence, retained twin bodies, provenance relocation, and hostile-test coverage are otherwise defensible within their stated visual-only scope.

## Blocking implementation finding

`twin_overlay.py` lines 462-470 constructs the F.Fab body envelope by unioning every F.Fab graphical item without excluding footprint text. The supplied overview exposes the result: `R_PWR_TOP` is reported as **3.49 x 0.90 mm**, while its authored physical F.Fab rectangle and high-resolution registration are **1.60 x 0.80 mm**. The 3.49 mm width is text-contaminated expected geometry, not a conservative search envelope. Height 0.90 mm still leaves this specific part below the 2.0 mm overview floor, so its current `unresolvable` classification happens to remain unchanged; the implementation can misclassify or mismeasure another native retained body.

Bounded fix: exclude every footprint text/property item from the overlay's F.Fab physical-envelope census, preferably by sharing one explicit physical-Fab predicate with `native_model_registration.fab_bbox`. Add a regression that `R_PWR_TOP` resolves to exactly 1.60 x 0.80 mm even when visible F.Fab user/value text is present. Re-run the overlay after the fix.

## Code and provenance judgment

The new absence path is otherwise fail closed. Its closed schema requires exact LCSC/MPN/ref scope, native source, response-body hash, primary authority, native footprint/model/generator/provenance, independent absence and pin reviews, reviewer/date/limitations, and `catalog_comparison: unavailable`. A current observation must be zoned, within 24 hours at production, HTTP 200, exact endpoint identity, exact 60-byte application-404 shape, matching body size/hash and parsed object. A stale/future observation, changed source, changed delivered review/model/manifest, unsafe path, missing observation, incomplete ref scope, or later `*.kicad_mod` causes refusal. If catalog CAD reappears during production, the fetched footprint makes `vendor_cad_absent` fail rather than fabricate a vendor-pad fit.

Relocation is deliberately supported by the sealed twin: offline overlay verifies copied authority and registration artifacts relative to the twin bundle and binds the production-time observation through the receipt timestamp. Production still verifies original project source hashes before copying. The receipts contain all nine rows and all six authority categories. No vendor pad residual, rotation, or geometry PASS is invented for C3761431 or C861313.

The native-retention path keeps the full CPL body census. The supplied twin log reports **333/333 bodies mounted**, including F1-F8 and R_PWR_TOP, and the receipt demands exact equality between declared and retained native refs. `NO-BODY` remains a distinct terminal finding. This mounted count is evidence of model presence only; it is not release, routing, placement, purchasing, assembly-process, thermal, fault, or order-preview acceptance.

`all_smd_pad_overlap` uses each pad's KiCad effective copper polygon, including rounded/custom/rotated geometry, and requires positive plan-area intersection for every pad. Its cache tuple serializes copper outlines and holes. It retains independent body/Fab center tolerance, Fab outward excursion, courtyard containment, search-window contact, and front/back signed-side occupancy. The hostile tests cover tangency, rounded-corner bbox false positives, rotation, a detached pad, an inverted body, stale/relocated evidence, malformed/future/stale absence, and catalog-CAD reappearance. This overlap is intentionally weak registration evidence and does not prove terminal metallurgy, solderability, land adequacy, or assembly qualification.

## Nine-reference actual-image judgment

All nine original-resolution crops were viewed. F1-F8 each show the pink measured body aligned with the green 4.73 x 3.41 mm Fab envelope, contained by the orange courtyard, with positive overlap against both cyan effective copper pads. Their receipts grade 16/16 overlaps; center deltas range 0.005065..0.031362 mm; all Fab and courtyard excursions are 0. R_PWR_TOP shows the pink measured 1.60 x 0.80 mm body aligned with green Fab, inside orange courtyard, and overlapping both rounded pads; its receipt grades 2/2 overlaps, center delta 0.003931 mm, and zero Fab/courtyard excursion. Both front and right signed-side views were inspected for each group and visibly place the bodies above the front board plane.

The actual twin top image was also viewed. All eight fuse bodies are visible at their channel-local positions. R_PWR_TOP is present but below useful overview resolution. The overview census must be stated exactly: **A-RENDER measured 84/333 expected bodies; 249 are unresolvable, 0 resolvable-but-unmeasured, and 0 no-model.** It does not establish that all 333 were visually measured.

## Source evidence and remaining holds

The copied `native_authority` set matches the declarations byte-for-byte. The later fuse land/pin review closes the earlier historical source projection's objection by using the exact 1.78 x 3.15 mm lands, 5.23 mm pitch, maximum 4.73 x 3.41 x 1.80 mm body, all 16 pin/net identities, and local clearance census. The later Yageo pin/land review closes the historical missing-mounting-document objection with Mounting V10 and quantifies the retained rounded-pad relationship. Historical absence reports remain evidence of the earlier state and are not silently rewritten as current acceptance; their bounded fixes are closed by separately hashed later reviews and regenerated source evidence.

Release remains held pending the F.Fab text-filter fix and fresh canonical regeneration, followed by fresh registration/twin/overlay evidence. Thermal/fault qualification for the PPTCs, assembly-process qualification, whole-board placement/routing/DFM acceptance, stock/allocation/orderability, and exact-part uploader/order-preview inspection also remain open. The isolated input board is a source projection and is not itself proof that canonical regeneration has occurred.
