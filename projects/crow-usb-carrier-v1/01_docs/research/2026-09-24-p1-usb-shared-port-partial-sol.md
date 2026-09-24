# Partial USB shared-transition port check

The schema-2 coarse checker now accepts a source-owned `board_integration`
transition port only when its exact endpoint, participants, geometry, copper
layer, reservation scope, P2 pad access, and filled-reference return
obligations agree with the hash-bound native board, modular plan, and floorplan.
The ordinary virtual-region guard remains in force for every other witness.

On the exact unseeded board SHA-256
`60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`,
the only tested partial shared port is Q_VBUS.3 (`VBUS_PRESENT_N`) at
`[215.42, 74.2, 215.52, 74.8]` mm. Its bounded reservation is
`[215.52, 70, 217.5, 74.8]` mm on F.Cu. The local zone
`[215.42, 70, 217.5, 74.8]` mm crosses only the `usb_vbus_sense` and
`xmos_core` logical regions and contains no native full footprint envelope,
pad, or rule area. Moving the port's west edge to 215.32 mm correctly fails
against Q_VBUS's full envelope, which reaches 215.410715 mm.

This is one partial transition obligation. The ESD-to-XU path has no validated
XU endpoint port; pad access, filled return, effective capacity, routing, DRC,
and P1 acceptance remain **INCOMPLETE**. The fixture and generic checker do
not promote this research record into the canonical Crow P1 source.
