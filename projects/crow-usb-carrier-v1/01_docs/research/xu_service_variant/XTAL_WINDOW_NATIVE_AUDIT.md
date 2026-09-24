# XMOS crystal window on the isolated QSPI-gap board — rejected

This research-only audit covers the seven exact `XTAL_IN`/`XTAL_OUT` pads on
the isolated QSPI-gap board. It does not change a canonical floorplan,
interface, route, P1 verdict, or acceptance state.

The board is `/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb`,
SHA-256 `fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.
The QSPI-gap floorplan is SHA-256
`cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925`; the
packet source variant is SHA-256
`9a13c0999d29f17280bb5d8ffb98a5e0d59afe3ee4511eb004e436bffc13ece4`.
The audit program records the checker hash in its result as well.

The exact native denominator is seven pads: `U_XU.34`, `R_XTAL_DRIVE.1`, and
`R_XTAL_FB.1` on `XTAL_IN`; `U_XU.33`, `C_XTAL_OUT.1`, `R_XTAL_FB.2`, and
`Y_XU.3` on `XTAL_OUT`. The packet's `crystal_clock_cell` window is
`[204, 118.5, 212, 132]` mm. Native pad bboxes show that it contains only the
two feedback-resistor pads and the output-capacitor pad. It excludes both XMOS
pins below the window, `R_XTAL_DRIVE.1` above it, and `Y_XU.3` to its east.

The source-local representation is rejected. The only two cross-owner
handoffs, `U_XU.34` and `U_XU.33`, use the packet's existing witnesses through
the local-window edge. The native corridor checker rejects both as “witness
bbox is a nonlocal bridge across source region”: their paths cross
`board_integration_qspi`, so treating them as clock-cell-local would violate
region ownership. This is separate from the packet's earlier JTAG rejection
and does not claim an allocation result for QSPI or P1.

The next action belongs to the floorplan/interface owner: place and declare an
oscillator cell whose owned endpoint handoff does not cross
`board_integration_qspi`, then provide native P2 pad-access and continuous
filled `In1.Cu` return evidence. Until then, the oscillator window is not a
valid local handoff or corridor and cannot support P1 acceptance.

Reproduce from `/tmp/crow-qspi-corridor-packet` with KiCad 10 `pcbnew` and
PyYAML:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/xtal_window_native_audit.py
```

The generated, hash-pinned result is
[`xtal_window_native_audit.json`](xtal_window_native_audit.json).
