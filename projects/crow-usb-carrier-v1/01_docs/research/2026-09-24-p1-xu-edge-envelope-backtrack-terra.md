# XU edge-envelope backtrack assessment

Read-only assessment from isolated board `ce589f8a4889854946ef9a1c234ed57de89bfbf220e60f72cd6d818734d8813e`. It is not a placement change or P1 result.

The data endpoint U_XU.107 is at (200.838,97.800). The three clock endpoints are U_XU.20/.22/.23 at (209.900,107.662), (210.700,107.662), and (211.100,107.662). They occupy different XU edges after the current 90-degree pose, so a shared local exit does not exist before considering obstacles.

The data-side exterior is bounded by the fixed local-ring bodies C_XU_VDD_104 (198.6,96.0), C_XU_VDD_105 (196.5,97.1), C_XU_VDD_106 (198.6,98.2), C_XU_VDDIO_109 (196.5,99.3), and the XU footprint itself. Moving 106 east to (200.7,101.2) created pad overlap with U_XU.115/.116 and a 1.850 x 1.010 mm U_XU courtyard overlap. Moving it south while retaining x=198.6 collided with C_XU_VDD_113; moving 109 south at x=196.5 collided with C_XU_VDDIO_121. These are hard geometry boundaries, not merely P-ADJ warnings.

The source does not expose an independent numeric P-ADJ ceiling for each XU capacitor in this file; its governing XU evidence instead requires each named VDD/VDDIO capacitor to remain local with a short direct ground return. Thus no unmeasured relocation outside the existing ring can be called legal merely because its courtyard clears. The two tested local moves did not open the U_XU.107 data pocket, and neither addressed the separate U_XU.20/.22/.23 clock pocket. This diagnostic does not exhaust every possible local topology.

The next constructive study should treat XU and its decoupler ring as one placement block: preserve the XU 90-degree orientation only if a new ring topology creates two independently measured edge windows, one at U_XU.107 and one at U_XU.20/.22/.23. If that cannot satisfy all owning-pin proximity/return measurements, study rotating or repositioning U_XU within `xmos_core` as one rigid XU-plus-decoupler block, then rederive USB, QSPI, JTAG and crystal escapes. This is a fresh P1 candidate, not permission to change the current anchors.
