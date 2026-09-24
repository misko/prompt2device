# XU service reservation representation after the rectangle probe

**Review only.** This recommends a future contract shape from source at
`e780b32b`; it does not edit the floorplan, requirements, checker, board, or
P1 state.  The rectangle probe remains `INCOMPLETE_RESEARCH`.

## Current constraint

The probe's disjoint cells are `xmos_core [190,84,232,114]` and
`clock_flash_debug [190,114,232,136]`.  Its QSPI diagnostic window crosses the
shared y=114 edge.  Its JTAG/reset window starts at y=84 and reaches only the
new XU north edge.

The present schema-2 checker cannot turn either movable-endpoint window into a
source-owned reservation.  A `virtual_block_face` must use an exterior
reservation, and `p1_corridor_capacity.py` rejects that reservation if it
intersects *any* source region.  Thus a QSPI window straddling the two cells is
correctly rejected; calling it a shared alias would evade the locality check.

## Smallest legitimate source model

Use one **named, non-overlapping `board_integration` corridor region**, not a
shared-zone alias, between the two service cells.  It must be a real third
source region with one bounded rectangle and a fixed net list; each adjacent
cell ends at its exterior face.  The touching y=114 rectangles cannot contain
that region, so the admitted source variant must leave a nonzero band enclosing
the selected reservation; this review does not select its geometry.  The
contract then has three distinct pieces:

| Piece | Owner | Scope |
| --- | --- | --- |
| XU handoff face | `xmos_core` | exact movable XU QSPI pad-to-face obligations |
| integration corridor | `board_integration` | the six QSPI nets and its declared F.Cu width/demand |
| flash handoff face | `clock_flash_debug` | exact movable flash/CS pad-to-face obligations |

The two handoffs touch opposite edges of that corridor but neither reservation
enters another cell.  The corridor has an explicit owner and is independently
checked against bodies, pads, courtyards, rule areas, outline, and overlapping
allocations.  Its only capacity credit is the six-net trunk; movable pad
escapes and return remain `P2_REQUIRED`.  This needs a small schema extension
for a named integration-corridor handoff (the existing virtual-face rule only
models exterior unowned space); do not weaken that rule or reinterpret a
diagnostic window as such a corridor.

Do not create a JTAG corridor from the y=84 face in this packet.  It is useful
only as a local XU ingress measurement.  A source-owned north path to fixed
`J_JTAG` necessarily crosses the current `usb_frontend [200,35,236,70]`
region before reaching the connector.  Without an independently owned,
non-overlapping handoff/corridor through that region and all JTAG/reset
terminals, its five-net reservation is incomplete regardless of the local
3.00-mm window.  The probe itself records this unproved continuation.

Consequently, the next source change, if separately admitted, should model the
QSPI-only integration corridor and retain JTAG as incomplete.  It must bind
the new floorplan, requirements, interfaces, aliases, board and checker hashes
and return an `INCOMPLETE` result until native P2 access and filled-reference
evidence exist.  It supplies no USB route, connector, P1, P2, or acceptance
claim.

Sources: `03_src/floorplan.yaml` (current regions),
`03_src/rules/p1_corridor_requirements.yaml` (QSPI/JTAG demands),
`01_docs/research/xu_service_variant/measurement.json` (the diagnostic
windows), and `skills/kicad-pcb/scripts/p1_corridor_capacity.py`
(`virtual_block_face` locality rule).
