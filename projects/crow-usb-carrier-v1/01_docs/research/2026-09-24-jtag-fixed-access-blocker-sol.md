# Fixed JTAG access rectangle probe — FAIL

**Research only. No P1 admission or source promotion.** The pinned QSPI-gap
native board is SHA-256 `fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.
`jtag_fixed_access_probe_sol.py` pins the board, QSPI-gap source packet,
modular interfaces and alias inventory, then builds a temporary variant. It
uses disjoint `usb_frontend [200,35,238.5,40]`, `debug_connector
[221,40,238,65]`, and `board_integration_jtag [221,65,226,84]` regions.
The maintained `_integration_corridors` validator accepts the exact four
`J_JTAG` and four `U_XU` JTAG endpoints, their two local faces and eight P2
pad-to-face obligations. The variant splits the source JTAG/reset demand to
declare these four JTAG nets exactly. Reset remains a separate incomplete net.

Every `J_JTAG` signal pad is in the north row, y=46.57–49.36 mm. Its paired
south-row pad has the **same x interval**, y=50.64–53.43 mm. A single
axis-aligned `fixed_connector_access` rectangle that touches the north-row
signal pad and reaches the integration strip at y=65 must include a positive
x interval from that signal pad. It necessarily intersects the paired pad on
the way south. This is a blocker under the maintained checker's native-pad
intersection rule, regardless of how the rectangle is narrowed horizontally:

| Signal | Exact fixed pad x interval (mm) | Forced paired obstacle |
| --- | --- | --- |
| JTAG_TMS | `J_JTAG.2`, 230.17–230.91 | `J_JTAG.1` |
| JTAG_TCK | `J_JTAG.4`, 228.90–229.64 | `J_JTAG.3` |
| JTAG_TDO | `J_JTAG.6`, 227.63–228.37 | `J_JTAG.5` |
| JTAG_TDI | `J_JTAG.8`, 226.36–227.10 | `J_JTAG.7` |

The [JSON result](jtag_fixed_access_probe_sol.json) records the exact pad,
access and obstacle bboxes. The script exercises the maintained checker’s
exact fixed-pad witness, source corridor and reservation contact checks, then
uses its positive-area `intersects` predicate against every native pad. Its
whole-packet `evaluate_coarse` call also remains `FAIL`: the pre-existing
`U_XU.38` reset witness is a nonlocal bridge. That earlier failure prevents
the whole-packet path from reaching the fixed-access obstacle loop; it does
not weaken the independent geometric impossibility above.

This result rules out **one rectangular fixed-access reservation per pad**
through this south strip under the current checker. It does not prove native
PCB unroutability. A future source model would need explicit segmented lanes
or waypoints that avoid the paired pads, with exact source ownership,
clearance, return and P2 access obligations. The existing 13-net service
allocation and P1 state remain `FAIL`/`INCOMPLETE`; no route, filled return,
effective capacity or P1 acceptance is claimed.

Reproduce from the repository root with KiCad 10 `pcbnew` and PyYAML:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/jtag_fixed_access_probe_sol.py
python3 -m unittest skills/kicad-pcb/scripts/tests/test_p1_coarse_capacity.py
```
