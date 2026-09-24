# Public XU316 USB-layout references

XMOS publishes a relevant board reference: the
[XK-AUDIO-316-MC-AB](https://www.xmos.com/xk-audio-316-mc-ab) names the exact
`XU316-1024-TQ128-C24`, includes high-speed USB, and links to the
[xcore.ai Multichannel Audio Platform Design Files v1V1](https://www.xmos.com/file/xcore_ai-multichannel-audio-platform-design-files)
(2022-11-22). XMOS also identifies the same device on its
[multichannel-board hardware page](https://www.xmos.com/documentation/XM-015142-UG/html/doc/rst/xk_audio_316_mc_ab/hw_316_mc.html).

The ZIP is a promising source of Altium/manufacturing evidence, but it was
**not inspected here**: direct public retrieval returned HTTP 406 in this
environment. Accordingly, no claim is made about its actual USB pad escape,
layer count, track dimensions, ESD order, or decoupler layout. Inspect the
download in an ordinary browser before using it as a geometry precedent.

XMOS's [XU316 product-series datasheet](https://www.xmos.com/documentation/XM-015129-PC/pdf/XU316-1024.pdf),
§14.1--14.2, specifies 90-ohm USB differential impedance, tightly matched
and coupled D+/D-, top-layer routing where possible, a continuous reference
below the lines, minimum vias, and no stubs. Its USB example table gives
0.120-mm width, 0.100-mm D+/D- gap, and 0.100-mm dielectric height. This is a
generic USB example in the product-series document; the adjacent
`(FB265, TQ128 only)` qualifier applies to the MIPI material, not USB.

Crow's selected JLC04161H-7628G section is materially different:
0.410-mm width, 0.150-mm gap, 0.5124-mm F.Cu-to-In1 height, and an archived
JLC calculation of 89.611 ohm. The thinner 0.100-mm example dielectric can
plausibly permit a narrower 90-ohm pair than Crow's 0.5124-mm geometry. That
is a field-geometry hypothesis only, not a reason to change Crow's stack or
copy XMOS numbers.

[TI SLLA414A §§4.2--4.3](https://www.ti.com/lit/an/slla414/slla414.pdf)
provides compatible general guidance: brief deviations occur naturally at a
package breakout; make them short and symmetric, then retain constant width
after the escape. This supports a bounded no-via diagnostic with matched
short necks followed by Crow's locked section. It does not prove the neck
impedance or USB compliance.

The current native board samples positive In1 GND fill. That does **not**
establish C54's decoupling return: its GND pad has no saved local F.Cu GND
track or GND via in the present diagnostic. The XMOS datasheet requires the
ground side of each decoupler to have a direct path back to device ground, so
native copper/return review remains required before accepting the C54 move.

