# Intended connector orientations

This authored placement contract defines intended connector frames for the future candidate. It is planning evidence consumed by the connector admission review, not an executable placement rule or proof of realized orientation. The existing floorplan must be implemented consistently with these directions, then independently checked against the saved native board.

Board coordinates: +X right, +Y back, +Z top. Local axial x follows mating direction, local lateral y follows the listed lateral direction, and local z is their cross product.

| Refs | Profile | Mating axis (board XYZ) | Lateral axis (board XYZ) |
|---|---|---|---|
| J1, J2, J3, J4, J5, J6, J7, J8 | spoke_rj45 | [0.0, -1.0, 0.0] | [1.0, 0.0, 0.0] |
| J_USB | usb_device | [0.0, -1.0, 0.0] | [1.0, 0.0, 0.0] |
| J_PWR | external_power | [0.0, -1.0, 0.0] | [1.0, 0.0, 0.0] |
| J_JTAG | debug_jtag | [0.0, 0.0, 1.0] | [1.0, 0.0, 0.0] |

All eleven orientations remain pending native placement. Do not infer connector rotation, edge location, exposure or service clearance from this document. Any orientation revision must update the connector assembly contract and this intent together, then recompile admission evidence.
