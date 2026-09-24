# P1 corridor requirements source

The requirements file records all four P1 allocation coverage sets, their
owners, and only the slot arithmetic already supported by the corridor
diagnostic. The separate ten-net `power_boundary_windows` set owns CHASSIS,
GND, and the eight named power/control nets; it uses non-null source
reservation bboxes rather than scalar lanes. Those boxes are not copper,
current, thermal, return, or acceptance evidence. Every signal lane and pocket
remains null until measured on a fresh native board.

CHASSIS is deliberately outside `usb_device_pair`: native evidence must find
J1--J8 pads 9 and 10 on CHASSIS and preserve separation from GND. The four
physical J_USB.SH lands remain local GND features, not CHASSIS endpoints.

The USB no-via launch is limited endpoint evidence. It is not a
connector-to-ESD-to-XU corridor, return-plane, impedance, SI, decoupling,
routing, P1, P3, connector FULL, release, or order result.

A future separately admitted P1 measurement must instantiate the checker
contract with an exact board SHA, external expected contract SHA, exact
ref.pad/net pockets, connected geometry, and native outline/rule-area/pour
checks. The resulting receipt still does not replace ADR 0011 review or
connector FULL.
