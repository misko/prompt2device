# crow-audio-carrier-v1-connector-coupon physical connector coupon

This is a non-functional, connector-only qualification coupon. It is not the carrier PCB and must never be used as a product board.

## Bare-board order

- Copper layers: 4
- Finished thickness: 1.600 mm
- Surface finish: lead-free HASL
- Soldermask / silkscreen: green / white
- Population: hand solder exact connector lots after bare-board fabrication
- Upload the `*_gerbers.zip` archive for PCB fabrication only.
- Do not upload a PCBA BOM/CPL: the connector population is deliberately hand-installed so exact lot identity and seating can be photographed.

The coupon preserves the source carrier's complete outline, mounting holes, fiducials, connector anchors, footprint pad/hole geometry, layer count, and thickness. All signal pads are intentionally isolated.

Populate only the exact parts in `connector-population.csv`, gather the exact mates/cables in `qualification-hardware.csv`, then fill `physical-response.yaml`. Run the grade command recorded in `request.json`; an unfilled template is intentionally INCOMPLETE.
