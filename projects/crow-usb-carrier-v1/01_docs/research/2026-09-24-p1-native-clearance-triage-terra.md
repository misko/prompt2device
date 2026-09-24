# Native-clearance triage for isolated coarse board — 2026-09-24

This triage reads the exact isolated board SHA-256 `18e55f44d5c1a8f7a7dd050e12ca451f6e08932b8c79893a0ad74e3b18be861b` and raw refilled DRC artifact `/tmp/crow-p1-native-preflight.InWK16/drc_refill.json`, previously recorded in [the native preflight note](2026-09-24-p1-native-preflight-coarse-sol.md). It is a diagnosis only. It does not alter the board or source, accept P1, or authorize a task.

The 245 DRC rows divide without ambiguity into 237 same-footprint pad-pair clearances and eight GND-via-to-pad clearances. There are no different-footprint body/pad rows and no row involving a ref in the current source-owned `p1_fixed_refs` set (the edge connectors and hold-bank capacitors). Thus there is **no measured fixed-P1 placement collision** in this DRC set. This does not make the fixed geometry acceptable: the saved-zone, outline, connector-mouth, and missing source-bound parity evidence from the preflight still bar P1.

| Ownership / corrective owner | Rows | Quantitative clusters | Classification |
| --- | ---: | --- | --- |
| Footprint/generator rule compatibility | 237 | `U_XU`: 121; `U_ISO1`–`U_ISO8`: 12 each / 96 total; `U_ESD1`–`U_ESD8`: 2 each / 16 total; `U_USB_CC_ESD` and `U_USB_VBUS_ESD`: 2 each / 4 total | Same-footprint pad pairs. Moving a component cannot change these pad-to-pad distances. 205 read 0.150 mm and 32 read 0.100 mm where the active rule requires 0.200 mm. |
| P2 local placement/copper | 8 | one each at `U_ISO1`–`U_ISO8`: a GND via is 0.100 mm from an ISO signal pad | Each ISO is a `placement.seeds` member in the exact cloned floorplan, so the offending via and local part entry are P2-owned, movable local geometry. |
| Fixed P1 unavoidable placement | 0 | none | No DRC row references the current 27 P1-fixed edge/hold refs. |

The largest individual clusters are native package pads, not board inter-part clearance: `U_XU` alone is 49.4% of the 245 rows, and the eight isolators are 39.2%. The eight via rows are 3.3%. This is consistent with the raw DRC examples: a 0.150-mm adjacent-pad gap inside `U_XU` or an isolator and a 0.100-mm GND via beside an ISO pad. It is not evidence for a blanket clearance relaxation.

The minimal safe sequence is:

1. Reconcile the actual 0.200-mm rule with the source footprints for `U_XU`, the ISO packages, and the ESD packages. Decide from fab/package authority whether a footprint correction or a narrowly evidenced rule/pad-class correction is required. Do not mute same-footprint DRC globally.
2. In the P2 local scope, relocate or remove each of the eight ISO-adjacent GND vias while preserving the later return-path proof obligation. Re-run native DRC on the regenerated saved board.
3. Refill and save the GND zone, then re-run the full DRC plus source-bound parity, model-registration, and connector-mouth gates on a complete candidate tree. The isolated copy’s zero schematic-parity row count is not sufficient because it lacks its matching source artifacts.

Even after those corrections, the result remains a new candidate requiring the separate P1 floorplan, connector FULL, and later P2/P3 gates.
