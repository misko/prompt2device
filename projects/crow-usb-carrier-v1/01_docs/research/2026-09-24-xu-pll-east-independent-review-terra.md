# Independent review: isolated east-side XU PLL placement

## Verdict

**PASS only as a bounded placement screen; do not admit it as a PLL-filter,
power-return, or route result.** The new position makes a local PLL cell
plausible, but fixed `C_XU_VDD_39` blocks the direct supply/return geometry
that must be demonstrated before the placement can be adopted.

Reviewed artifacts are SOL commit `3981656d` and
`/tmp/crow-xu-pll-local-sol/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`afd3d4b7ed92e8ff9d6a5055e224e2501ee2f014b87a77a82265a2bcb78fec4e`.

## Exact geometry and topology consequence

`U_XU.41=PLL_AVDD` is `(216.1625,103.0000)` and
`U_XU.42=PLL_AGND` is `(216.1625,102.6000)`. The candidate places
`C_PLL_100N.1/.2` at `(219.520,102.800)` / `(220.480,102.800)`,
`C_PLL_1U.1/.2` at `(219.520,105.000)` / `(220.480,105.000)`, and the
180-degree `FB_PLL.1/.2` at `(223.485,103.900)` / `(222.515,103.900)`.
The ferrite output faces the capacitors, which is the right filtered-node
ordering: `N0V9 -> FB_PLL -> PLL_0V9 -> {C_PLL_100N, C_PLL_1U, U_XU.41}`.

However, fixed `C_XU_VDD_39` sits between the XU and this cell:
its pads are `N0V9=(218.000,103.680)` and `GND=(218.000,102.720)`.
Its body/courtyard therefore occupies the direct eastward approach from pin
41 toward `C_PLL_100N.1`; its GND pad likewise lies beside the direct return
from `C_PLL_100N.2` toward pin 42. The reported 0.540-mm non-overlap is only
a placement fact. It says neither that a route around C39 fits with the needed
return topology nor that it is an assembly margin.

Direct native inspection finds zero `PLL_0V9` tracks and zero `N0V9` tracks.
There is consequently no present evidence of a ferrite-filtered supply, no
proof that the capacitors connect on the filtered side rather than bypass the
bead, and no direct capacitor-ground return to U_XU ground. The candidate is
not invalidated by its observed capacitor-to-pin spans; XMOS supplies no
millimetre maximum. It is open because its required topology is absent.

## Source basis and next evidence

XMOS XM-014532-PC v2.0.0 (retained
`02_parts/XU316-1024-TQ128-C24/XM-014532-PC-v2.0.0.pdf`, Sections 7.3/14 and
Appendix I) requires PLL_AVDD to be separated from noisier supplies, recommends
a low-pass filter, and requires its filter capacitor close to PLL_AVDD. It also
requires decoupler ground sides to have direct, short paths toward device
ground. The source publishes no distance, via-count, or ripple value that this
placement can satisfy by itself.

Before another placement decision, route a diagnostic exact-hash board around
the fixed C39 and prove all of the following: `FB_PLL.1` is the sole N0V9-side
entry; `FB_PLL.2`, both capacitor pad 1s, and U_XU.41 form one filtered node;
each capacitor pad 2 has an explicit, short return to U_XU.42/device ground;
no supply branch bypasses FB_PLL; the route and returns have continuous filled
reference and no prohibited clearance/courtyard finding; and USB pads 59/60
plus the four TDM exits retain their own measured geometry. Then conduct the
existing PLL first-article waveform check at U_XU.41 relative to .42. None of
these evidence items is present in this isolated board.
