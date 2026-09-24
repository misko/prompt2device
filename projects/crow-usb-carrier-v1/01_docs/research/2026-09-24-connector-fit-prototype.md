# Connector fit prototype — nonqualifying

The adjacent `connector_fit_prototype.kicad_pcb` is a geometry screen extracted
from the pinned 569-footprint partial board fixture. It has only J1–J8, J_USB,
J_PWR, J_JTAG, and the fixture's four Edge.Cuts lines. The script copies each
native footprint instance, including its pads, rather than loading replacement
library footprints. It preserves their board-frame pose and the fixture's
1.63 mm nominal thickness. The companion JSON records the exact source SHA,
selected simultaneous group populations, and verified geometry parity.

Run `/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/connector_fit_prototype.py`
from the repository root to regenerate and check it. The script rejects source
SHA, population, connector pose, thickness, or outline drift. After saving, it
reloads the PCB and checks footprint identity, pose, all pad positions/sizes/
orientations/shapes/drills/layers, thickness, and Edge.Cuts geometry against
the source fixture.

This is **not a physical qualification coupon or fabrication package**. The
220 × 120 mm rectangle is an exploratory canvas, not a final accepted board
outline. The source defines no board restraint or mounting-hole coordinates.
It contains no proved hand, cable, bend, or enclosure clearance envelopes.
The recorded `normal_service` and `bench_service` populations are required
states to inspect, not clearance PASS results. It is not possible to preserve
nonexistent mounting or service geometry. No Gerbers, drill files, order, or
physical PASS are produced. The 19 physical FULL unknowns remain open pending
final board and restraint geometry, exact mates/cables/enclosure, and the
observations in the connector physical qualification plan.
