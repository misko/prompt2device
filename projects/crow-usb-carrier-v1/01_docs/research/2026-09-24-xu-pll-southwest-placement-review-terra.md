# XU PLL filter placement review: southwest isolated board

## Verdict and recommendation

The isolated southwest board's `C_PLL_100N` placement is **not defensible as
the required local PLL filter placement**. This is a qualitative XMOS finding,
not an invented capacitor-to-pin distance limit.

Use one source-owned **east-side PLL micro-cell**: place `FB_PLL` upstream on
`N0V9`, followed only by the filtered `PLL_0V9` node shared by
`C_PLL_100N.1`, `C_PLL_1U.1`, and `U_XU.41`; return both capacitor ground pads
directly and locally toward `U_XU.42`/the adjacent device ground. Keep this
three-part cell outside the bottom-side TDM exit fanout and south of the USB
launch pads on the right side of U_XU. The cell must be placed and routed as a
single topology review unit, rather than moving one capacitor independently.

This uses the right-side locality of `U_XU.41=PLL_AVDD` and
`U_XU.42=PLL_AGND`, while leaving the four TDM exits at pads 20/22/23/107 and
USB pads 59/60 outside the cell's allocation. It is a placement/topology
recommendation only; it is not a completed route, clearance margin, P1
allocation, or acceptance result.

## Exact isolated-board observation

Reviewed board:
`/tmp/crow-xu-southwest-sol/04_kicad/crow_carrier.kicad_pcb`.

| Item | Observed pad centre |
|---|---:|
| `U_XU.41` (`PLL_AVDD`) | `(216.1625, 103.0000)` |
| `U_XU.42` (`PLL_AGND`) | `(216.1625, 102.6000)` |
| `FB_PLL.1/.2` (`N0V9` / `PLL_0V9`) | `(209.915,89.200)` / `(210.885,89.200)` |
| `C_PLL_100N.1/.2` (`PLL_0V9` / GND) | `(198.120,103.600)` / `(199.080,103.600)` |
| `C_PLL_1U.1/.2` (`PLL_0V9` / GND) | `(218.000,108.880)` / `(218.000,107.920)` |

`C_PLL_100N.1` is about 18.05 mm centre-to-centre from `U_XU.41`; its present
position is on the opposite side of the package from the PLL pin and is not a
plausible reading of XMOS's "filter ... placed close to the PLL_AVDD pin"
guidance. `C_PLL_1U` is about 6.16 mm from pin 41, but no `PLL_0V9` copper or
ground-return path exists on the isolated board. Neither present capacitor
therefore closes the filter requirement.

## Source basis and required evidence

XMOS `XM-014532-PC v2.0.0`, retained at
`02_parts/XU316-1024-TQ128-C24/XM-014532-PC-v2.0.0.pdf`, says PLL_AVDD must be
separated from noisier supplies; recommends a low-pass filter (example 1 uF
MLCC plus 600-ohm-at-100-MHz, DCR-under-1-ohm ferrite); and Appendix I requires
the PLL filter capacitor close to PLL_AVDD. It does not state a millimetre
maximum, permitted via count, or ripple limit.

Before this recommendation can be admitted, an exact-hash saved native board
must show: the complete `N0V9 -> FB_PLL -> PLL_0V9 -> U_XU.41` copper graph;
both capacitor pad-2 returns to `U_XU.42`/device ground; no noisy-supply bypass
around the bead; filled continuous reference; foreign-copper/footprint and
courtyard review; and preserved USB/TDM escape geometry. First article must
measure PLL_AVDD relative to PLL_AGND across startup and credible activity,
against the XMOS 0.855--0.945 V operating range. These are the evidence needed
for a later review, not claims made by this placement note.
