# USB launch EM-input inventory — 2026-09-24

**Research only; no pass claim.** This memo identifies inputs for an eventual
electromagnetic model of the XU316-to-ESD USB launch. It changes no canonical
PCB, route, rule, or acceptance state.

## Exact reviewed subject

The only routed object reviewed here is SOL scratch board SHA-256
`a822e3ddb355113cb8708ffdd3e3990aacc9b53bf214355d88d04a7e5a3bb435`, derived
from unseeded 569-footprint board
`60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`. It joins
`U_XU.60/.59` to `U_USB_ESD.1/.2`, has 15 F.Cu tracks and no USB via. The
checked scratch measurement is DP 62.752565 mm and DN 63.667873 mm (DN longer
by 0.915308 mm), with a 0.150000-mm minimum pair copper gap. Its six XU
launch tracks at 0.150 or 0.250 mm pass only a scratch DRU exception; they
fail the source `USB_HS_width` requirement of 0.410 mm.

This is a useful *model subject*, not an accepted launch: connector aliases
remain unconnected, native DRC has the baseline 170 unrelated violations and
499 unconnected items, and filled-plane samples establish only centerline
coverage by In1.Cu GND, not return-current continuity or impedance.

## Inputs present in public/check-in evidence

| Input | Evidence available now | Boundary |
|---|---|---|
| Nominal stack | JLC04161H-7628G, access id `c9cc086852034b99bdf5d61bf940f3cc`; L1-to-L2 h=0.5124 mm; nominal Dk=4.2366666667 | Starting values only; order confirmation remains required. |
| Copper and mask | 1-oz outer; JLC solver plated trace T=0.04064 mm; C1/C2/C3 mask=0.0254/0.01524/0.0254 mm, mask Dk=3.8 | Nominal calculator values, not as-built launch values. |
| Uniform pair | F.Cu 0.410-mm artwork width / 0.150-mm gap over In1.Cu | JLC `DiffEdgeCoupledCoatedMicrostrip1B` returned 89.6111388098 ohm for this uniform cross-section only. |
| Scratch copper | Exact board digest above; 15 F.Cu tracks, no vias; six 0.150/0.250-mm neck tracks; `0.150 -> 0.250 -> 0.410` progression | Extract every endpoint, width, gap, corner and pad overlap from exact bytes. The 0.525-mm x-envelope is not a qualified taper length. |
| Pin identities | XU316 USB_DP/DM pins 60/59; TPD2E2U06DRLR protected I/O pins 3/5 and GND pin 4 | Datasheets fix roles; current land patterns are needed for modeled pad geometry. |

## Inputs still required

| Missing input | Why it matters | Evidence needed |
|---|---|---|
| Finished trace profile | Final narrow width, sidewall, plating and CAM compensation set impedance and step behavior. | JLC order/CAM or controlled-impedance production data. |
| Pad/land/mask details | XU/ESD lands, mask openings, finish and trace-to-pad transitions create launch discontinuities. | Exact native lands plus checked manufacturing drawing. |
| Return environment | In1 edges/voids, antipads, nearby copper, stitching and ESD-ground vias affect differential and common mode. | Completed refilled board, all relevant layers. |
| Connector/full route | Scratch omits J_USB A6/B6 and A7/B7 aliases and connector-to-ESD copper. | Completed board and connector boundary model. |
| Electrical boundary models | S-parameters/eye require PHY, ESD, cable/fixture and port reference planes. | Manufacturer models or explicit conservative scope assumptions. |
| As-built result | Modeling alone cannot establish production impedance or HS margin. | JLC controlled-impedance order, coupon/differential TDR, assembled USB 2.0 HS eye. |

## Open-source solver path

[openEMS](https://www.openems.de/) is a feasible open-source FDTD route for a
future *comparative* 3-D launch model. Its official
[ports documentation](https://docs.openems.de/en/latest/concepts/ports.html)
supports S-parameter extraction with one active port at a time, but cautions
that lumped ports perform poorly for differential pairs. Use an appropriate
differential/mode port treatment and archive reference planes. Its
[model I/O documentation](https://docs.openems.de/en/latest/concepts/model_io.html)
describes Gerber/HyperLynx-to-CSXCAD PCB import, but labels import/automatic
meshing tooling experimental.

A minimum model must reproduce F.Cu/In1 and local surroundings from this exact
digest, stack/mask values, both pad launches, all three widths and transitions;
then archive mesh, boundaries, materials, ports, convergence and frequency
dependent differential S11/S21. It can compare the launch with the nominal
uniform pair. It cannot qualify fabrication or authorize the scoped exception.

## Route to qualification

Keep the source 0.410/0.150-mm rule in force. Review a bounded change only
after an exact segment/return model, JLC controlled-impedance stack and mask
confirmation, and first-article coupon/TDR plus applicable USB 2.0 HS eye
evidence exist.

## Primary public sources

* JLCPCB, [impedance calculator guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator) and [controlled-impedance stackups](https://jlcpcb.com/impedance), accessed 2026-09-24.
* XMOS, [XU316 product-series datasheet](https://www.xmos.com/documentation/XM-015129-PC/pdf/XU316-1024.pdf), accessed 2026-09-24.
* Texas Instruments, [TPD2E2U06 datasheet](https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf), accessed 2026-09-24.

