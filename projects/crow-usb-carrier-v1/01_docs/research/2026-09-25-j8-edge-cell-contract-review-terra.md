# Review: two-stage J8 edge-cell contract

SOL proposal `bc485c8c` correctly keeps the cell rectangle in-board, limits the exception to a sole fixed J8 member on the north edge, retains pad containment, and denies route, reservation, witness, endpoint, and return credit. Its source binding, native geometry binding, fixed-pose check, exterior-sliver limit, and negative controls are the right fail-closed shape.

One wording correction is necessary before treating it as an operative contract: an accepted `mechanical_receipt` must not be satisfied by **drawing-supported** overhang alone. The Würth drawing/STEP and exact CAD establish only a nominal, hash-bound planning condition. They do not establish finished board edge registration, seating, actual body/mouth projection, or mated behavior. “Measured or drawing-supported” would collapse those two evidence grades.

## Recommended two-stage representation

### Stage A — CAD-bound planning artifact

Keep this outside canonical `physical_cells` and outside any checker input that can return a P1/P2-positive result. It may name the exact board SHA, native outline digest, J8 pose/footprint/model hashes, the north-edge span x=`198.875..216.268081`, and the nominal maximum envelope projection `0.045` mm. Its only output is `PLANNING_ONLY`; it may support an isolated source-design discussion but cannot waive `_physical_cells` containment.

This stage may cite Würth `615008160221` drawing rev `001.003` and STEP rev1 plus the selected Telegärtner `100009141` drawing. It must say that the 0.045-mm envelope and 0.025-mm body projection are native-CAD observations, not measured mechanical limits. The current connector-fit prototype is likewise Stage A only.

### Stage B — measured, checker-consumable J8 attachment

Only after an accepted mechanical receipt may canonical source carry SOL's proposed `edge_attachment`. Require a receipt schema with `status: ACCEPTED`, exact hashes for board, outline, native J8 footprint/pose and part/mate identities, and a signed north-edge span/overhang measurement with uncertainty. It must include the raw E1--E3 evidence from [the evidence plan](2026-09-25-j8-edge-overhang-evidence-plan-terra.md): three-point actual body/mouth projection, pin/chassis/post registration and seating, and board thickness/process/lot traceability. The receipt must state a reviewed maximum that contains the measured projection plus the cited process allowance. A drawing, STEP file, plan, unmeasured coupon, prose assertion, or an artifact missing any hash fails.

The checker then permits only the named J8 full-envelope sliver up to that accepted maximum. It keeps the cell itself in-board; requires all pads, drills, and relevant mask features to remain in-board and in-cell; compares body and courtyard separately; verifies the exterior sliver is only on the named north span; and retains all ordinary owner, denominator, foreign-region, fixed-pose, and no-credit checks. Any geometry, outline, pose, footprint, receipt hash, edge/span, or maximum drift fails closed.

## Gate interpretation

Stage B makes only the **typed-cell geometry** eligible to report geometrically valid/`INCOMPLETE`; it is still not P1 or P2 acceptance. P1/P2 must never consume Stage A. They may consume Stage B only together with their separate endpoint, route, filled-reference, and regional-cell obligations.

Connector FULL remains a distinct, stronger gate. It needs E4--E6 and the existing group-wide J1--J8 observations: exact `100009141` mating, both simultaneous-service populations, restrained reaction/service, cable exit, and governed registration records. A successful Stage B receipt does not make FULL pass; a future FULL result does not waive the hash-bound typed-cell checks. Any gate that requires connector FULL must query the complete group receipt rather than infer it from `edge_attachment`.

This preserves SOL's useful future green control while preventing a nominal CAD datum from becoming mechanical authorization.
