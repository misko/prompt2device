# Independent review: isolated XU PLL feed and pin-42 return

**Verdict: PASS as a stronger local topology probe; not PLL acceptance.**

Reviewed board: `/tmp/crow-xu-pll-feed-ground-sol/04_kicad/crow_carrier.kicad_pcb`,
SHA-256 `5b9e211a8d2a288730fd1be944c48f2221153419d225efcb5a36267985386dd9`.

`C_XU_VDD_45.1=N0V9` at `(218.0,101.08)` feeds `FB_PLL.1` through three
0.60-mm F.Cu segments. `FB_PLL.2` solely enters seven 0.20-mm `PLL_0V9`
tracks shared by U_XU.41, both capacitor pad 1s, and FB_PLL.2. No other
N0V9 or PLL_0V9 track is present, so the visible copper graph has no bead
bypass.

This board now demonstrates the needed distinction from EP129: `U_XU.42`
(`PLL_AGND`) at `(216.1625,102.6)` has its own 0.20-mm F.Cu segment to a GND
via at `(214.9,102.6)`. `C_PLL_100N.2` returns through a stub and via at
`(220.48,101.9)`; `C_PLL_1U.2` returns through a stub and via at
`(220.48,106.0)`. All three vias land on the filled In1.Cu GND zone. Pin 42
and both capacitor grounds therefore share a native plane node. The EP129 via
at `(208.5,103.1)` is separate supporting ground evidence and must not be
cited as the PLL_AGND connection.

The separate vias and plane do not yet demonstrate XMOS's qualitative
direct/short capacitor-return requirement: no plane-current corridor,
impedance/inductance model, or manufacturer maximum return length is shown.
Nor does DRC-clean diagnostic copper qualify mask openings, bodies, vias, or
assembly. XMOS XM-014532-PC v2.0.0 requires a clean locally filtered PLL_AVDD
supply and direct/short decoupler returns, but gives no numerical trace,
return-via, capacitor-distance, or ripple limit.

Before adoption, retain exact filled-plane/geometry extraction for the three
return vias, complete native clearance/mask/body review against the final
stack, and measure PLL_AVDD relative to **U_XU.42** through startup and load.
USB/TDM, full-board routing, and first-article release remain open.
