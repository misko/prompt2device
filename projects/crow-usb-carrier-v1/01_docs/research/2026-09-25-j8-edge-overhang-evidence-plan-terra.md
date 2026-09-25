# J8-specific 0.045-mm edge-overhang evidence plan

## Scope and disposition

This is a bounded proposal for the fixed J8 only. It does not edit the physical-cell schema, board, outline, or connector contract, and it gives no P1/P2/FULL credit.

The source-selected pair is Würth Elektronik `615008160221` (through-hole RJ45 jack) and Telegärtner `100009141` S/FTP plug/cable. The board-frame mating axis is `-Y`. On the pinned integrated board SHA-256 `0b9d017706845ad4d77c2b579dd36f2e34c0ecf55a7b699ace4fca97465c5b93`, its outline starts at y=20.000 mm; J8's required checker envelope is `[198.875,19.955,216.268081,34.495]` mm. The exception sought is therefore only the rectangle x=`198.875..216.268081`, y=`19.955..20.000`: **0.045 mm**. The body reaches 0.025 mm past the edge; all 12 pads start at y=23.260 mm and are in-board.

## What the CAD and primary records may support now

The retained Würth drawing rev `001.003` (SHA-256 `6ed18749…1f0e048`), matching STEP rev1 (SHA-256 `f6906876…78510d7b`), and native fixed J8 pose support a **planning-model exception** only if it is all of the following:

- bound to that board hash, J8 reference, exact `615008160221` footprint/model, 0-degree pose, and the four native Edge.Cuts lines;
- limited to y=19.955..20.000 and that x span; all J8 pads, drills, and other `analog_ch8` members remain subject to ordinary containment;
- limited to the displayed full-envelope/body projection; it cannot be generalized to other connectors, other outlines, future J8 poses, or a generic out-of-outline allowance; and
- marked `planning_only`, with no route, return, capacity, acceptance, release, or FULL effect.

The drawing provides nominal/toleranced jack and recommended-hole geometry, and the STEP provides a nominal body. Neither establishes the manufactured board-edge registration, actual seating, spring deflection, mating-plane exposure, nor service clearance. The Telegärtner drawing `L00000A0149DP` (SHA-256 `9befcc16…fff7c9`) establishes the selected plug/cable identity and nominal 12.9 + 24 mm axial, 13.2 mm lateral, and 13.7 mm latch dimensions. Its nose projection is undimensioned; the contract's 41.9 x 14.2 x 14.7-mm mate envelope is intentionally conservative planning, not an installed measurement. CAD consequently cannot close connector FULL or justify a mechanical production exception.

## Exact physical evidence for a future mechanical exception

Use a hash-bound candidate or separately governed J8 article that copies the native J8 footprint, pose, Edge.Cuts relation, 4-layer stack, and finished-thickness target. Record exact jack and plug lots, article/candidate hash, operator/date, calibrated instrument ID and uncertainty, and raw photos or microscope images. Before fabrication, a qualified reviewer must define acceptance limits from the selected parts, fabricator edge/thickness tolerances, and intended enclosure; none are currently set.

| ID | Measure / observation | Datum and record |
| --- | --- | --- |
| E1 | Actual edge-to-J8 body and front/mouth projection | Board top Edge.Cuts as datum A; measure at left, center, and right of the J8 mouth before and after soldering. Record the signed projection and uncertainty. |
| E2 | Hole/pin/shell registration and seating | Inspect all eight contact pins (including GND on 2/6/8), chassis pins 9/10, and the two mechanical posts against the board edge. Record seating/lift, annular breakout, plating fracture, delamination, or edge damage. |
| E3 | Finished board/process stack | Measure thickness near J8 at three points; record fabricator, lot, edge-routing process, soldering process, and connector lot/date code. |
| E4 | Exact mate engagement | Fully mate `100009141`; photograph its reference/mating plane, latch state, exposure, and any contact with board edge, connector body, or intended enclosure. |
| E5 | Operated service/reaction | With the defined normal and bench populations, restrain the board at its governed mounting features; record insertion, latch release, withdrawal, grip access, neighbor disturbance, flex, rotation, and before/after joint inspection. |
| E6 | Cable exit | Record initial -Y exit, unobstructed start, first bend, strain relief, and interference using the exact cable. Do not infer a bend limit from its 6.2 +/- 0.2-mm OD. |

E1--E3 can establish an evidence-based J8 edge-registration/overhang decision for the tested construction only. E4--E6 remain necessary to establish realized connector behavior. The present spoke-RJ45 FULL predicate also covers J1--J8 and both simultaneous groups; a J8-only result cannot close that group-wide FULL gate.

## Existing coupons and records

`connector_fit_prototype.kicad_pcb` copies the connector-field pose and 220 x 120-mm edge loop, but its record explicitly has no mounting holes, accepted outline/process, enclosure, restraint, or physical observations. It is useful as a digital parity fixture only. The USB4215 edge-registration coupons are for a different connector and cannot evidence J8. Their unmeasured record is useful only as a template: bind the exact drawing/footprint/article, record raw lot and thickness data, retain three-point edge observations, and leave limits unset until authority exists.

The physical qualification plan and phase policy already require realized mating-plane/board-edge registration, populated service, reaction, and cable observations. A future J8 article must append its raw evidence to those governed records rather than turn a CAD exception into a passing FULL result.
