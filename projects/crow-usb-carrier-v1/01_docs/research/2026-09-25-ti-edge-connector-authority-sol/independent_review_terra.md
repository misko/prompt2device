# Independent review: fixed north-edge connector courtyard authority

Reviewed SOL commit `9fb29c4b` on the hash-bound 569-reference TI board
`d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`.
The native census reproduces byte-identically as receipt SHA-256
`ab382f88bd19b72a6793a8d0d4b159d47354b66a256cb50e5b474e06a1e492db`.
This is a source-geometry review only; it grants no route, P1, connector FULL,
P-OUT, release, mating, or service acceptance.

## Disposition

A narrowly typed **P1 physical-cell containment-only** exception is defensible
for the exact fixed north-edge references `J_PWR` and `J1` through `J8`.
Their F.CrtYd outer polygons project 0.045 mm north of the nominal outline
centerline at y=20.000 mm, while their F.Fab **shapes** start at y=20.450 mm
and pads start at y=23.260 mm (RJ45) or y=23.600 mm (J_PWR). The exception may
remove only that declared exterior courtyard sliver when testing the listed
reference's physical-cell outline containment. It must not change any other
physical, electrical, routing, or release rule.

`J_USB` is explicitly ineligible: its F.CrtYd begins at y=19.450 and its
F.Fab shape begins at y=19.950. That is a different physical-edge question.
`J_JTAG` is inboard and does not need an exception.

## Required fail-closed contract

The exception record must bind all of the following:

- exact board, footprint and manufacturer-drawing hashes; fixed native pose;
  reference identity; north-edge direction; outline centerline y=20.000 mm;
  and maximum exterior courtyard projection of 0.045 mm;
- one listed reference only in the affected physical cell, with no generic
  length tolerance or other-edge/direction fallback;
- all F.Fab shapes, pads, plated drills/slots, mounting/shell features and
  board-material bounds wholly inside the native outline; F.Fab text, silk and
  generic graphics must not be treated as material evidence;
- normal inboard courtyard/foreign-footprint exclusion, owner/ref denominator,
  floorplan-pattern, endpoint, P2, P3 and return obligations unchanged.

The exception must be callable only from physical-cell containment. It must
not relax board-outline checks for corridors, reservations, capacity, tracks,
zones, rule areas, DRC, mechanical gates, connector FULL, or release.

## Negative controls

Tests must reject an unlisted reference, any direction other than the declared
north edge, a projection of 0.046 mm or more, a changed board/footprint/drawing
hash or pose, a second exterior courtyard lobe, and any F.Fab shape, pad,
drill, slot, shell/mounting feature or material body beyond the outline. They
must also reject J_USB and any attempt to use the exception for a corridor,
reservation, route/capacity claim, or connector/release result.

First-article edge-registration evidence remains necessary before any
mechanical conclusion: record finished edge, thickness, process, part/board
lots, pre/post-solder left/center/right measurements and uncertainty. Such a
receipt is separate from this P1-only source containment exception.
