Noncanonical native fixture for `CrowUsbPartialPortTest`.

`board.kicad_pcb` is the exact unseeded Crow USB carrier board measured on
2026-09-24 (SHA-256 `60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`).
The plan, floorplan, and P1 requirements are snapshots used to verify
block/ref ownership, logical-region overlap, and evaluator failure status
against that board. These files do not replace or edit the project's
canonical source.

The test admits only a Q_VBUS.3 partial transition into the body-clear area
between the `usb_vbus_sense` and `xmos_core` logical regions. The source pad
remains an exact `VBUS_PRESENT_N` endpoint. Pad access, filled return,
effective capacity, XU.8 access, routing, and P1 acceptance remain unproved.
