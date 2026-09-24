# Isolated XU-to-ESD F.Cu USB pair extension — 2026-09-24

**Disposition: local connected pair candidate, not an integrated USB route.** This follows the exact-board north escape in `2026-09-24-xu-usb-fcu-north-escape-sol.md`. The input remains the unseeded 569-footprint native board SHA-256 `60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17` and its parsed-equivalent source floorplan. Only scratch copper at `/tmp/crow-usb-fcu-north-sol-20260924/04_kicad/crow_carrier.kicad_pcb` was changed; the saved/refilled board SHA-256 is `a822e3ddb355113cb8708ffdd3e3990aacc9b53bf214355d88d04a7e5a3bb435`.

Starting with the twelve segments documented in the north escape, extend DP's vertical segment `(219.850,94.390) → (219.850,40.000)` and DN's `(220.410,94.950) → (220.410,39.440)`. Add these three 0.410-mm F.Cu segments:

| Net | Start → end |
|---|---|
| DP | (219.850,40.000) → (216.650,36.800) |
| DP | (216.650,36.800) → U_USB_ESD.1 (216.650,36.425) |
| DN | (220.410,39.440) → U_USB_ESD.2 (217.350,36.425) |

The staggered north-turn starts place the DN northwest diagonal northeast of DP, so the copper does not cross. This joins U_XU.60/.59 to the ESD's native DP/DN pads. The ESD pads are 0.300 × 0.300 mm and 0.700 mm apart; the 0.410-mm traces end at their centers. The central vertical pair has 0.560-mm center spacing, or nominal 0.150-mm copper gap. No via was introduced.

The exact-shape pass found **zero** foreign-pad/track collisions at 0.150-mm clearance, drilled holes at 0.250 mm, and **zero** pair collisions at the 0.145-mm native minimum gap. After refill, all **2,550** In1.Cu GND samples at at most 0.050-mm intervals along the fifteen copper segments were inside the GND fill. Native `kicad-cli pcb drc --severity-all --all-track-errors --refill-zones --save-board --schematic-parity --format json` reported exactly the baseline **170** violations (80 clearance, 64 hole-clearance, 10 library-footprint issues, eight via-diameter, eight annular-width), **499** unconnected items, and **zero** schematic-parity findings; there were no USB-specific DRC findings. The native DRC JSON SHA-256 is `6be363cb7e25eab36b323aa88c01f3f664351c7d252edc933f65067d0e931e90`.

The pad-edge-to-pad-center added-copper geometry is 62.7526 mm DP and 63.6679 mm DN, giving 0.9153-mm skew. This is below the declared 1.0-mm pair limit locally but leaves only 0.0847 mm for the connector-side path before compensating geometry would be required. The stepped U_XU neck and ESD-pad arrival have no solved impedance/taper model. GND samples do not establish a continuous return-current boundary or account for all via antipads and future copper. J_USB's A/B alias pads, connector-to-ESD route, and full pair length/impedance remain open; there is no P1/P3 or release claim.
