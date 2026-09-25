# Independent review — TPS26625 partial return-route trial

**Subject:** SOL packet `80d193b3`,
`2026-09-25-ti-tps26625-return-trial-sol`. This is a valid partial native
return witness, but it remains **research-only** and is not P2 evidence.

## Verified placement and rule result

The hash-pinned, source-generated trial retains 569 footprints, complete
native pad number/net/layer/shape/size parity, and all 27 fixed-reference
poses/pads. The six group poses are source-owned by `analog_ch8`; their
full-envelope collision and foreign-source-region censuses are empty. Relative
to the preceding whole-group board, the return trial updates four group poses
(`C_SPOKE_DVDT8`, `C_SPOKE_OUT8`, `R_SPOKE_ILIM8`, and `R_SPOKE_UVLO8`), while
the source receipt correctly identifies all six group references against the
earlier coupled baseline.

The two current project-owned effective-shape ceilings pass:

| Existing project check | Measured F.Cu pad-shape gap |
| --- | ---: |
| `U_SPOKE8.1` → `C_SPOKE_IN8.1` | 1.655273 mm |
| `U_SPOKE8.7` → `R_SPOKE_ILIM8.1` | 2.405089 mm |

Those are engineering ceilings, not numeric TI placement limits. TI's
closest/shortest-loop language remains qualitative.

## Actual native return evidence

Direct board inspection finds the following new 0.20-mm F.Cu copper:

* `C_SPOKE_IN8.2` reaches `U_SPOKE8.6` through the `(192.5,48.5)` join;
  stated path length is 7.400000 mm.
* `C_SPOKE_OUT8.2` reaches the same join through the `(195.55,48.5)` GND
  stitch; stated path length to the join is 4.850000 mm. The 0.60/0.30-mm
  via at that point and the two returns are in filled In1 GND outline 8.
* `R_SPOKE_ILIM8.2`, `C_SPOKE_DVDT8.2`, U.3, and U.5 have separate
  `SPOKE_RTN8` tracks to PowerPAD.11. Their reported path lengths are
  3.572487, 3.420000, 1.400000, and 1.814214 mm.

Native connectivity confirms both bypass-return pads on U.6's `GND` net and
both control-return pads on the U.3/U.5/PowerPAD.11 `SPOKE_RTN8` net. Those
nets remain distinct. There is one filled GND In1 zone and no `SPOKE_RTN8`
zone, so the result does **not** prove a local RTN thermal island or a
PowerPAD-on-RTN-plane implementation.

I replayed the archived full profile in a temporary directory. Baseline and
trial both return **199 violations / 499 unconnected**, **+0/-0** native issue
identities, and zero via-process failures. The retained ADC8N witness also
remains only a two-pad local link with its earlier 0.200001-mm USB-region and
0.205001-mm nearest-envelope margins.

## Remaining bounded debt

There are no added native tracks on `N12V_PROTECTED`, `N12V_POD8`,
`SPOKE_ILIM8`, `SPOKE_DVDT8`, or `SPOKE_UVLO8`. Thus the IN-supply, OUT-supply,
ILIM-signal, dVdT-signal, and UVLO legs remain unrouted. Each of the five
loops in the acceptance rubric is open, so a loop area is undefined, not zero.
The partial returns cannot be credited as a completed local bypass/control
network, high-current path, thermal island, or P2 return proof.

The next bounded packet must retain this GND/RTN distinction while supplying
all five named signal legs, named local copper primitives, reproducible
per-loop path lengths and polygonal areas, a local RTN island under
PowerPAD.11, and all normal full-profile/envelope/owner checks. It must still
discharge the separate J8/owner-cell and complete ADC8N route/return
obligations before any P2 decision.
