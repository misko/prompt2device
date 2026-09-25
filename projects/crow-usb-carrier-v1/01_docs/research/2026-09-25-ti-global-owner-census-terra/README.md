# Global functional-owner census — research only

`census.py` pins the exact 15-part board (`d0c065dc…a9fcf7`), unified
floorplan, modular plan, and checker in `receipt.json`.  It uses the checker’s
`_physical_envelope` (body plus courtyard, excluding reference/value text) and
native pad boxes.  Run `python3 census.py` from any directory to reproduce the
receipt.

The census finds 569 module references: 454 are fully inside their functional
owner’s primary rectangle and 115 are not.  A separate 139 references have
150 foreign planning-region incidences.  These are source-rectangle debts,
not automatically native collisions: the largest clusters are quiet-power
against input-buck (29) and adc-reference (23), audio-clock/TDM against
analog-ch7 (14), and xmos-core against xmos-core-east (10).

There is one cross-owner checker-envelope interaction: `C_IN3` (input-buck)
and `Q_PRE` (quiet-power).  It is a 0.020 mm corner overlap of their courtyard
envelopes; native bodies and pads do not overlap.  This distinction matters:
there are zero cross-owner body overlaps and zero cross-owner pad overlaps,
but current `_physical_cells` containment still makes a source-only exclusive
rectangle partition impossible.  Each cell has to contain its full assigned
envelope and exclude foreign native footprint/pad geometry.  Therefore the
first global-authority repair must either move/reassign one member of this
pair, or explicitly change and validate that checker rule.  Redrawing source
rectangles alone cannot solve it.

Fixed overhangs are fully enumerated in `fixed_ref_issues`.  In particular,
`J1`–`J8` lie below their analog primary rectangles (and `J8` also enters the
usb-frontend planning rectangle); `J_PWR` is outside input-buck; `J_USB`'s
envelope is outside usb-edge-connector while its pads remain contained.  The hold-bank capacitors
also create broad planning intersections.  Fixed connector placement thus
needs explicit connector-pocket/access authority rather than an attempt to
force every functional owner into one rectangle.

Prioritize the repair in this order:

1. Resolve the `C_IN3`/`Q_PRE` envelope conflict under an explicit checker
   policy before proposing exclusive physical cells.
2. Add typed multi-cell/pocket authority for fixed connectors and hold banks;
   retain their functional owners and do not grant branch or route credit.
3. Recut only the highest-count movable planning interfaces (quiet-power,
   audio/ADC7, xmos-core/east) and rerun this receipt.  A rectangle count is
   not evidence of electrical endpoint access, capacity, return continuity,
   P1, or P2 acceptance.
