# Fixed J_USB access probe on the private TI board — 2026-09-25 UTC

**Outcome: current source cannot admit the handoff without a region/owner
redesign.** This is a USB-only research probe; no connector pose, canonical
source, P1 attempt, route, P-OUT, or connector FULL status changed.

The exact TI diagnostic board is SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
Its fixed J_USB is at `(230, 22.995, 180°)`; `J_USB.A6` on `USB_DP` has a
native copper bbox `[230.1, 26.1, 230.4, 27.25]` mm. The source owner
`usb_frontend` is `[200, 35, 238.5, 40]`, so the pad is 7.75 mm north of
that region. The full J_USB courtyard also projects 0.50 mm beyond the board
edge; this is a separate unresolved connector-mouth/FULL question.

`2026-09-25-ti-usb-fixed-access-probe-sol.json` (SHA-256
`aa7bca56ca0b3e09619808090d3d881c59bf958d0f789651b13888753f48d273`)
changes only the research candidate's `J_USB.4` witness to the exact native
pad bbox and `fixed_connector_access`, with an explicit access reservation.
The schema-2 checker returned nonzero `FAIL`, with the USB row reporting
`J_USB.4: undeclared fixed access corridor`; the retained evaluation JSON
is SHA-256
`fd3a04d5f0e1a7b34302e58a7e0dba6c13c32e171c499441b247c434df95576c`.
This is the expected fail-closed first check: current P1 source has QSPI,
XTAL and JTAG integration corridors, but no USB edge corridor.

To isolate the next schema condition without falsely authoring a full
corridor, I supplied a synthetic, matching USB corridor descriptor directly
to `_coarse_witness` in a read-only diagnostic. It then rejected the same
exact pad: `J_USB.4: fixed access pad boundary leaves source region`.
`fixed_connector_access` requires the physical pad and every access segment
inside its owning region. An access reservation alone cannot make the
connector local. Moreover, `integration_corridors` requires **two distinct
modular block owners** and disjoint source-cell geometry; it cannot join two
physical cells of the same current `usb_frontend` owner. A simple full-width
frontend expansion to contain A6 consumes the fixed J8 courtyard and leaves
the existing support/edge split unaccounted for.

The truthful next source model is a separate `usb_edge_connector` owner for
unchanged J_USB, with every connected Type-C leaf transferred in the modular
interface and TSX presentation, and the seven support refs retained under
`usb_frontend`. Then declare a board-contained edge region, a disjoint empty
connector-to-support integration corridor, exact A6/B6/A7/B7 fixed-pad
accesses, frontend movable handoffs and P2 pad-to-face/filled-return debts.
An unvalidated geometric lead is an edge cell near `[224.9, 20, 235.1, 28]`
and a narrow empty native strip near `[229.2, 28, 230.8, 33.1]`; current
supports above y=33.1 and the connector's off-board courtyard still need
separate source/physical disposition. These rectangles are **not** a validated
contract or an edge exception. If preserving one logical owner is preferred,
the generic corridor checker would instead need an explicit intra-owner
physical-cell participant mode; its present two-owner schema does not express
that handoff. Either design must keep P-OUT and connector FULL open until the
actual mating/courtyard evidence is reviewed.
