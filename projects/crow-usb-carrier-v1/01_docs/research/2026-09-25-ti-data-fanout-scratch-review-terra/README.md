# DATA fanout scratch-packet review — research only

This independently replays `b51007a1` and `cb5489df` without editing a
canonical board or source rule.  The available runtime is **KiCad CLI 10.0.4**,
not KiCad 9; therefore this is a replay of the packets' exact
`kicad-cli pcb drc --refill-zones --format json` arguments under 10.0.4, and
does not attest KiCad-9 behavior.

The 0.20-mm native stop reproduces on the pinned coupled-placement input SHA
`53e6fb…78555`: the U_XU.107 west stub is 1.0325 mm long and receives exactly
the reported F.Cu clearance failure to U_XU.108, 0.1750 mm actual versus the
0.2000-mm board rule.  It adds one clearance error and one dangling-track
warning: 724 to 726 violations, with 499 unconnected items unchanged.

The scoped 0.15-mm packet also reproduces its pinned output SHA
`d2aea4…76237`: U_XU.107 to `(199.805,97.6)` is 1.0325 mm, width 0.15 mm, and
its full rounded-stroke bounding rectangle `[199.73,97.525,200.9125,97.675]`
is strictly inside the declared `[199.7,97.49,200.95,97.71]` rule area.  The
packet's native filled-In1 polygon subtraction reports zero uncovered area;
the nearest existing GND via/PTH plane access remains 39.2442 mm away.  DRC
is 711 to 712 violations and 499 to 499 unconnected items; the sole new
local-track item is its deliberate dangling end, with no local track-width or
clearance item.

`review_controls.py` adds two temporary 0.15-mm tracks from `(198,97.6)` to
`(198.5,97.6)`, outside the exception: one on `TDM_DATA_1V8`, one on
`TDM_BCLK_1V8`.  Both receive exactly the default 0.20-mm track-width error,
so the packet's exception does not escape its named area.  This is a scope
control, not an electrical test.

The scratch neck remains **not electrically qualified**.  It lacks an XMOS
source-backed neck rule, local return transition, complete four-net route,
timing/skew analysis, crystal/USB interaction review, and route/return proof.
Neither scratch result earns P1 or P2 credit.
