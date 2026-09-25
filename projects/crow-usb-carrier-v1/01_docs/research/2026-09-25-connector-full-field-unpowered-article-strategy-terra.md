# Minimum governed unpowered full-field connector article

**Research strategy only — no article design, fabrication payload, purchase, order,
or Connector FULL credit.** D11 allows Connector FULL evidence from a separately
governed coupon, but requires its passing receipt and exact coupon board to be
hash-bound and regradable before P3, P5, release, or order. D13/D14 do not
currently permit fabrication; a new narrow authority is therefore the first
required decision. It must authorize only one unpowered mechanical article and
must preserve D13's USB-ESD and DESIGN_CLEAN holds.

## Minimum physical subject

The smallest credible subject is **one full-outline mechanical field**, not a
small connector strip:

- exact frozen outline, edge routing, 11 connector footprints/poses, and six
  3.2-mm M3 mounting holes from the full-outline packet;
- a controlled four-layer construction with the same nominal finished thickness,
  copper/finish at connector lands, soldermask, board-edge treatment, drill
  process, and assembly profile as the board revision it represents;
- all eleven exact selected connectors installed by that assembly profile;
- every neighboring real body that can constrain a connector, finger, latch,
  mate, cable, fixture or fastener installed at its exact pose. A merely
  empty-board field can record connector mating but cannot close populated
  service/interference targets. A non-electrical dummy is acceptable only when
  its maximum assembled envelope, pose, attachment and process representation
  are separately controlled and it does not substitute for a connector joint;
- no power applied and no electrical functional claim. Routing is not needed
  for a mechanical observation, but omission of copper/inner-layer construction
  is not allowed because thickness, stiffness, pad process and solder-joint
  behavior are part of the subject.

The current full-outline geometry gives a provisional fixture datum only:
230 × 130 mm, coordinates `x=10..240`, `y=20..150`, target 1.63 mm, connector
field J1–J8/J_PWR/J_USB/J_JTAG, and holes H1 `(30,40)`, H2 `(130,40)`, H3
`(211.5,45)`, H4 `(18,82)`, H5 `(130,142)`, H6 `(230,130)` mm. These are not
finished-process dimensions. The former 3313A screen must not be used as the
article stack: D15 ended `FAILED_RESEARCH`, and its 1.58-mm special stack is
not accepted.

## Fixture and operation envelope

Use a flat, nonconductive or grounded-metal baseplate with six M3 clearance
locations matching the frozen hole pattern. Locate board XY with two designated
datum holes and support all six with equal-height standoffs; use shoulder
washers/insulators only if they are recorded. The drawing must specify:

1. baseplate datum, hole tolerances, standoff height/tolerance, screw, washer,
   nut/thread engagement, torque method and whether a clamp touches either board
   face;
2. keep-clear polygons on both faces: no standoff, washer, clamp, or fixture
   surface may touch a connector, mate, cable, solder joint, component body,
   pad, trace, or local flex area;
3. the load-cell or hand-operation direction, camera/dial-indicator locations,
   and the path `mate → connector → PCB → M3 restraint → baseplate`; and
4. separate configurations for the north RJ45 bank, J_USB/J_PWR, and lateral
   J_JTAG access. Do not react through an adjacent connector, cable, or a
   soldered joint.

The hardware list is therefore not yet a purchasable BOM: six M3 screws,
washers, spacers/standoffs, baseplate, locating pins, controlled-torque tool,
force gauge/load cell if force will be graded, deflection indicator, camera,
and dimensional metrology. Exact sizes/materials, torque, and support faces
remain owed by the fixture drawing and an engineering owner.

## What one article can close

There are 19 target families: 4 interface, 4 reaction, 4 service, 3 cable,
and 4 registration. The article can close all 19 only if its governing profile
also freezes exact mates/cables/lots, enclosure and far-end cable support,
fixture and approved acceptance limits, sample count, cycle count, measurement
method/calibration/uncertainty, and the exact physical board/process revision.

| Target group | Minimum observation | Additional condition for PASS |
| --- | --- | --- |
| 4 interface | exact mate fully engages; orientation, seating, mating plane and immediate populated-field interference recorded | approved interface/exposure/service-clearance limits and the intended enclosure state |
| 4 reaction | before/after seating, rotation, board deflection and joint inspection during insertion/withdrawal | approved force/deflection/cycle limits, calibrated measurements, and approved M3 restraint |
| 4 service | every target operated with each declared normal/bench simultaneous group populated | enclosure/service-access configuration and a repeatable pass/fail criterion |
| 3 cable | exact cable lot, exit, straight length, first bend, radius, strain relief, contact and far-end support recorded | approved installed-route limits and final enclosure/strain-relief hardware |
| 4 registration | raw board-edge/mating-plane/seating/process measurements per governed sample | approved one-sided tolerance allocation and measurement uncertainty |

Without enclosure, cable support, quantitative limits, or controlled process,
the same article can produce useful raw observations and failure photographs;
it closes **zero** FULL targets. With fixture and limits but no enclosure/cable
configuration, it can at most close reaction and some bench interface/service
items; the three cable targets and installed service predicates remain open.

## No-purchase preparatory work

1. Produce a governed-coupon decision draft that names one article count and
   revision hash, declares it unpowered, bars route/release/fabrication credit,
   and states exactly which of the 19 target receipts it may update. It must
   state re-test triggers: any connector pose, neighboring body, outline/edge,
   thickness/stack, finish, assembly process, mate/cable, enclosure, restraint,
   or service geometry change invalidates affected evidence.
2. Freeze a mechanical source package: outline/holes/connectors and all
   populated-neighbor bodies, exact 4L finished-stack/process requirements,
   board and component drawings, and a hashable population manifest. Resolve
   the finished board thickness and edge/drill/slot tolerance instead of using
   the current 1.63-mm KiCad target.
3. Draft the six-hole restraint drawing and a keep-clear audit against the
   full field. Select fixture datums and record why each remains clear of
   components and connector service paths.
4. Convert the existing 19-row matrix into sample-level forms: subject/lot
   IDs, configuration, mate/cable/enclosure identity, before/after images,
   raw dimensions, force/deflection instruments/calibration, result, deviation,
   and reviewer signature.
5. Obtain engineering-approved force, deflection, cycle, registration,
   exposure, service-clearance, cable-bend/straight-run and uncertainty limits.
   The present connector plan intentionally supplies none.
6. Freeze exact mates: Telegartner `100009141` for RJ45, the selected GCT USB
   cable, Molex `43645-0200` with `43030-0038` terminals/defined wire process,
   and Samtec `FFSD-05-D-06.00-01-N` for J_JTAG. Freeze their cable lengths,
   boots, strain relief and far-end supports, not only connector order numbers.

This is the shortest route to evidence that D11 can later regrade. It does not
make the present full-outline private board an authorized fabrication subject,
does not resolve D13, and does not make Connector FULL pass before the governed
physical observations and limits exist.

Sources: [D11](../decisions/0011-p1-floorplan-and-p2-placement-admission.md),
[connector plan](2026-09-22-connector-physical-qualification-plan.md), and
[full-outline measurement packet](2026-09-25-expanded-locked-full-outline-mechanical-article-terra/README.md).
