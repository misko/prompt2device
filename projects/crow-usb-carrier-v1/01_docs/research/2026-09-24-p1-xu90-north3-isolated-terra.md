# Isolated 90-degree XU block +Y shift

Disposition: reject this as the next P1 source candidate; it increases USB
distance and leaves the TDM edge split unchanged.

The isolated copy at `/tmp/crow-p1-xu90-north3-terra` changed only U_XU and every C_XU_* anchor by +3.0 mm Y, retaining their 90-degree pose and rigid local geometry. `generate_board_generic.py` saved 569 footprints with zero inter-footprint pad overlaps and zero fixed-courtyard overlaps; the board is `/tmp/crow-p1-xu90-north3-terra/projects/crow-usb-carrier-v1/04_kicad/crow_carrier.kicad_pcb`.

The result preserves the USB-facing edge: U_XU.60/.59 move from y=95.400/95.800 to y=98.400/98.800 at x=216.162, while U_USB_ESD.1/.2 remain x=216.650/217.350, y=36.425. This **increases** centreline Y separation by 3.0 mm and has no connector-pocket, route, impedance, or reference-plane proof. TDM endpoint positions move by the same +3.0 mm and retain their separated-edge topology, so this shift alone does not establish the requested TDM corridor.

No native DRC, P-ADJ, filled-In1 return, or hash-bound capacity contract was run. This is an isolated collision-clean placement candidate only, not P1 acceptance or a canonical-source recommendation.
