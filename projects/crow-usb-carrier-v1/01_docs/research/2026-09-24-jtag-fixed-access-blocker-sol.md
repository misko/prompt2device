# Four fixed JTAG access rectangles — FAIL

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

Every `J_JTAG` signal pad is in the north row, y=46.57–49.36 mm. The
checker permits a rectangle to contact any of its four sides. Contact at the
pad's bottom edge and extension to the strip at y=65 intersects its paired
south-row pad (y=50.64–53.43) on the same x interval. Contact at the **left**
edge can avoid that paired pad, so the earlier blanket paired-pad claim was
wrong. Testing that contact instead gives this exact result:

| Signal | Bottom-edge access hit | Left-edge access hit |
| --- | --- | --- |
| JTAG_TMS, `J_JTAG.2` | `J_JTAG.1` | `J_JTAG.3` (also other pads) |
| JTAG_TCK, `J_JTAG.4` | `J_JTAG.3` | `J_JTAG.5` (also other pads) |
| JTAG_TDO, `J_JTAG.6` | `J_JTAG.5` | `J_JTAG.7` (also `J_JTAG.8`) |
| JTAG_TDI, `J_JTAG.8` | `J_JTAG.7` | **No native pad/body hit** |

Top-edge access points away from the south strip; right-edge access cannot
reach its x≤226 interval. Therefore three of the four fixed pads are blocked
under the single-rectangle geometry contract, so the exact four-rectangle
set cannot pass. The `J_JTAG.8` left-edge rectangle
`[225.85,49.35,226.36,65]` mm is a valid **isolated coarse geometry**
candidate: its pad witness, positive debug-face intersection, source-region
containment and strip contact pass the checker predicates; it hits zero other
native pads, foreign body envelopes, existing copper, rule areas or named
reservations. Its raw bbox gap to `J_JTAG.9` is only 0.02 mm, so it does not
establish electrical clearance or routability.

The [JSON result](jtag_fixed_access_probe_sol.json) records all four contact
directions per pad and the exact candidate bboxes. The script exercises the
maintained checker’s exact fixed-pad witness, source corridor, source-face
and reservation contact checks, then uses its positive-area `intersects`
predicate against native pads, bodies, copper, rule areas and reservations.
Its whole-packet `evaluate_coarse` call remains `FAIL`: the pre-existing
`U_XU.38` reset witness is a nonlocal bridge. That earlier failure prevents
the whole-packet path from reaching the fixed-access obstacle loop; it does
not make the isolated `J_JTAG.8` candidate a whole-allocation result.

This result rules out the **set of four single rectangular fixed-access
reservations** through this south strip under the current checker. It does
not prove native PCB unroutability. A future source model would need explicit
segmented lanes or waypoints for at least the other three pads, with exact source ownership,
clearance, return and P2 access obligations. The existing 13-net service
allocation and P1 state remain `FAIL`/`INCOMPLETE`; no route, filled return,
effective capacity or P1 acceptance is claimed.

Reproduce from the repository root with KiCad 10 `pcbnew` and PyYAML:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/jtag_fixed_access_probe_sol.py
python3 -m unittest skills/kicad-pcb/scripts/tests/test_p1_coarse_capacity.py
```
