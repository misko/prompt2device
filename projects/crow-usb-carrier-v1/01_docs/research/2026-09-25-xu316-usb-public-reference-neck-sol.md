# XU316 TQ128 USB launch: public-reference screen

**Finding (2026-09-25): no transferable public neck geometry was established.**
XMOS publishes a TQ128 multichannel board and lists its design-files ZIP, but
the accessible official manual/datasheet pages do not state the USB 59/60
escape width, neck length or shape, local layer transitions/vias, or exact
reference-plane aperture. The official XMOS data support a *bounded model
scope*, not a numerical waiver of Crow's nominal pair rule. This is public
reference research only; no board or source change, route authorization, SI
acceptance, or stock recheck follows.

Crow's exact private XU footprint has `U_XU.59`/`.60` pad centres 0.400 mm
apart at `(216.1625,95.6)`/`(216.1625,95.2)` mm. Each pad is 0.250 mm wide
across the pitch, leaving 0.150 mm edge gap. A pair of parallel 0.410 mm
tracks cannot emerge at full width in that pitch interval: their nominal
edges would overlap by 0.010 mm before any clearance allowance. This is a
geometric inference from Crow's native pads, consistent with XMOS's published
TQ128 0.4-mm pitch and USB pins 59/60, not an XMOS escape recommendation.
The checked-in [`USB_HS` source rule](../../03_src/rules/nets.yaml) requires
F.Cu 0.410-mm width, 0.150-mm pair gap/clearance, and no vias; the
[`rf.yaml` nominal solver record](../../03_src/rules/rf.yaml) gives 89.611 ohm
only for masked 0.410/0.150 mm F.Cu over In1.Cu on JLC04161H-7628G.

The [prior six-track scratch disposition](2026-09-24-usb-xu-neck-public-disposition-terra.md)
measures 0.150/0.250-mm stepped launch sections within an x=216.900–217.425
mm (0.525-mm) local envelope before 0.410-mm width. Those six sections fail
the committed native width rule and passed only under a scratch rule area.
The 0.525 mm is an observed envelope, **not** an XMOS or JLC maximum length.
The separate open-ended pair had 0.16-mm local geometric skew; neither it nor
the later ESD-connected scratch path measures the final connector-to-PHY eye
or return loss. JLC's published multilayer trace/space capability establishes
that 0.150 mm is above its 0.09-mm bare-copper floor, not that a 0.150-mm
masked neck has 90-ohm differential impedance.

| Public primary record | Transferable fact | Missing for Crow |
|---|---|---|
| [XMOS XU316 TQ128 datasheet](https://www.xmos.com/documentation/XM-014532-PC/pdf/XU316-1024-TQ128.pdf) | Pins 59/60 are USB DM/DP; TQ128 is 0.4-mm pitch. XMOS calls for 90-ohm, length-matched USB routing, few high-speed vias, a nearby GND reference, and avoidance of plane splits. Its 0.12/0.10-mm cross-section is an example for its own stated dielectric height. | No pad-exit neck width/length/profile or permitted impedance discontinuity for Crow's JLC stack. |
| [XMOS TQ128 multichannel board manual](https://www.xmos.com/documentation/XM-014727-PC/html/doc/rst/index.html) and [official design-files listing](https://www.xmos.com/file/xcore_ai-multichannel-audio-platform-design-files) | Same XU316-1024-TQ128-C24 package and a working USB audio reference platform; XMOS lists 1V1 design files. | Manual schematics do not disclose measurable USB copper geometry. The listed design ZIP was not obtained/verified in this screen, so no Gerber/Altium width, length, plane, or via measurement is claimed. |
| [TI TPD2EUSB30A datasheet](https://www.ti.com/lit/ds/symlink/tpd2eusb30a.pdf) | ESD protection belongs close to the connector on straight protected traces. | Does not specify XU TQ128 escape or qualify Crow's stepped neck. |
| [JLCPCB capability table](https://jlcpcb.com/capabilities/Capab) and [Crow's exact solver evidence](2026-09-22-usb-impedance-evidence.md) | Published copper floor and nominal 0.410/0.150-mm pair solve. | No field solution for the pad, 0.150/0.250-mm steps, mask, ESD land, and local return together. |

A defensible bounded **engineering model proposal** would freeze the exact
Crow pad/land and mask geometry, both measured six-track transitions, the
selected JLC copper/stackup, ESD and connector lands, In1.Cu GND and its
voids, and any actual vias. It would evaluate mixed-mode reflection and
impedance versus frequency, pair skew, common-mode conversion, and then the
complete-path USB high-speed eye. The public XMOS material does not provide
a pass threshold for Crow's local neck, so it cannot itself admit an exception.
Any numerical bound must come from that exact simulation plus independent
fabrication and first-article measurements; until then retain the 0.410-mm
source rule and treat the six-track geometry as a failed scratch diagnostic.
