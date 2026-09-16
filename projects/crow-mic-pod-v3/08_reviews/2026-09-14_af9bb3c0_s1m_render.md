review_stage: pre-route
review_kind: render
reviewer: rj45_pod_render_s1m1
context: FRESH
design_verdict: SOUND
order_verdict: DO-NOT-ORDER
board_sha256: af9bb3c0dcf5e9be20239d725d10dd4d4c1bf95cc0b7518badc3e27bd6523938
design_rules_sha256: 474e5d0a81baf576aefac32e9c60bce37704bb138961c16bf92573843b6409c4
prepared_board_sha256: fad0f345909d3169bd2e371896b6b0491c4c981f98725303b5aa3fad9c292a81
completed_at: 2026-09-14T03:43:58.646741+00:00

# Fresh independent pod pre-route render review

The exact 60 x 40 mm pod placement is visually and natively coherent for pre-route acceptance. I found no actionable render, placement-visibility, polarity, connector-access, or side-population defect.

## Coverage and measurements

- Reopened 468/468 frozen envelope inputs before and after review; every size and SHA-256 matched.
- Reopened the native board and deterministic prepared r0 with pcbnew. Both have the required exact hashes, 44 footprints, and matching placement. The population census is 31 fitted SMD on F.Cu, zero fitted SMD on B.Cu, one fitted THT J1, seven bare testpoints, four bare mounting holes, and the off-board MK1 two-wire landing. The 32 fitted bodies have 32 resolved model declarations.
- Opened both full-board approved-native images, all five current populated orientation renders, and all five J1 focused views at their frozen identities. All 12 required images were inspected individually. Labels remain readable at useful board scale: CROW POD V3; NOT ETHERNET / NOT POE; 12V, PROT, 5V, VREF and GND test labels; the J1 pin-use line; and MK1 WIRE LANDING + / -.
- Independently rendered top and bottom from a byte-identical board copy through the supplied render_board.py under the shared bounded runtime. Both runs resolved 32/32 models. The independent top render agrees with the approved top population and polarity; the independent bottom render agrees with approved_native_bottom.png and shows no fitted SMD body beneath the board. Render hashes differ because the supplied wrapper used its own exact renderer environment/color preset, while geometry and side population agree.
- Reopened the complete aggregate registration bundle and the J1/U2 receipts and imagery. J1 registers 12/12 attachment centres with 0.024 mm centre delta, no measured Fab/courtyard overrun, and 0.968 mounted-side pixel fraction. U2 registers 13/13 pad centres with zero centre delta and no courtyard overrun. These checks support view geometry; they are not manufacturing-fit proof.
- Independently compared J1 native pad centres to Wurth drawing 615008160221 revision 001.003. The board reproduces the 2.04 mm signal pitch, 4.00 mm stagger, 13.70 mm guide-hole spacing, 14.80 mm shell spacing and 3.05 mm shell-to-guide offset. The current model and all five focused views consistently put the RJ45 mouth toward the north board edge. The receipt measures a [0,-1,0] access axis, 0.5 mm mating-plane edge offset, and 1.0 footprint/model alignment. The exterior/cable view is unobstructed; the rear and two profiles show the latch/keying and through-board pins consistently.
- D1 at (39.5,35.6) mm shows its cathode band at the pad-1/VIN_PROTECTED end, consistent with the Vishay S1M source statement that the color band denotes cathode. D2's cathode stripe is visible. U1, U2 and U3 pin-1 marks are visible and agree with their footprint marks. Mounting holes H1-H4 at (24,24), (76,24), (24,56), and (76,56) mm are visually open from both faces.

## Findings

No findings.

## Limitations

This is a pre-route render/placement judgment. Expected unrouted opens were not treated as defects. Nominal CAD models and registration images do not establish housing tolerance, solderability, stencil outcome, enclosure/panel fit, cable bend clearance, or production process qualification. J1 remains a manually soldered first-article part, MK1 remains an off-board wired capsule, and all order-facing qualification remains owed. FIRST-ARTICLE-ONLY / DO-NOT-ORDER.
