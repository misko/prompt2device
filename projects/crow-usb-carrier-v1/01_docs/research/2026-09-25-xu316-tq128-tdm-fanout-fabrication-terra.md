# XU316 TQ128 TDM fanout: fabrication evidence boundary

**Status: a separately scoped fabrication-geometry receipt is supportable;
electrical routing qualification is not.** This records public XMOS and JLCPCB
evidence only. It changes no Crow layout, rule, stackup, or routing claim.

XMOS's [XU316-1024-TQ128 datasheet v2.0.0](https://www.xmos.com/documentation/XM-014532-PC/html/rst/XU316-1024-TQ128.html)
identifies the package as a 128-pin TQFP at 0.4 mm pitch. In §14.2 it frames
the routing guidance around a four-layer signal/GND/power/signal board: top
layer routing closest to GND, a continuous reference plane, few vias, and
special treatment of high-speed clocks and differential pairs. Section 14.3
says the land pattern and stencil depend on the manufacturing process and
points to IPC-7351B plus the package mechanical drawing. XMOS does **not**
publish a 0.15 mm TQ128 escape-neck width, clearance, maximum neck length, or
an XU316 `U_XU.107` TDM fanout reference layout.

JLCPCB's current [manufacturing capabilities table](https://jlcpcb.com/capabilities/Capab)
lists minimum track width/spacing for multilayer boards as 0.09/0.09 mm at
1 oz copper, and 0.15/0.15 mm at 2 oz copper. It separately states a ±20%
track-width tolerance example and notes that the submitted design receives DFM
review. Thus a 0.15 mm F.Cu trace and 0.15 mm clearance can be screened as a
fabrication geometry under either stated multilayer case, provided the actual
board order fixes the copper weight and the feature is not altered by a
different mask/exposure or fabrication option. This is a process-capability
fact, not an impedance or signal-integrity result.

For `U_XU.107`, a short exact F.Cu neck can therefore be assessed as an
ordinary, non-USB fabrication feature without invoking USB high-speed
impedance or USB ESD qualification. A valid limited receipt must bind the
native pad, completed F.Cu neck polygon, 0.15 mm minimum width/clearance,
chosen four-layer stackup/copper option, solder-mask condition, and a
continuous named reference plane below it. It must explicitly remain separate
from the USB connector-to-protector-to-PHY path.

That receipt cannot establish a permissible TDM length, timing margin,
edge-rate/drive/load compatibility, crosstalk, return continuity through any
via or plane split, source termination, receiver setup/hold, EMC, or the
area available after all adjacent XU fanouts and decoupling are placed. The
two cited records provide no numeric bound for those items. No numerical
pad-limit or maximum-length inference is made here.
