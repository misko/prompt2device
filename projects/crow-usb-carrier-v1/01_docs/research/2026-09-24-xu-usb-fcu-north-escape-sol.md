# Isolated U_XU USB F.Cu north escape — 2026-09-24

**Disposition: local geometry candidate only.** The unseeded 569-footprint board is `/tmp/crow-presence-B5uZxt/project/04_kicad/crow_carrier.kicad_pcb`, SHA-256 `60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`. The canonical floorplan SHA-256 is `a882f87682484c37c5766a9e37c5a0d93b38a8e5a775fb1ab4425011da40a275`; its parsed YAML is equal to the scratch board's floorplan copy (`187840ff...`), which differs in explanatory text. No board, source, or route was promoted.

The isolated board at `/tmp/crow-usb-fcu-north-sol-20260924/04_kicad/crow_carrier.kicad_pcb` uses that exact unseeded board as its input. Its `.kicad_pro` and `.kicad_dru` are generated diagnostic rules with the `USB_HS` 0.410-mm width, 0.150-mm nominal gap/clearance, and the previous `usb_xu_launch_neck` F.Cu rule area that permits a 0.150-mm net-scoped neck only inside `[216.85,94.95,217.44,96.10]`. It has no new via. The native pad starts are U_XU.60 USB_DP `(216.1625,95.400)` and U_XU.59 USB_DN `(216.1625,95.800)`; both pads end at x=216.900. The following twelve straight segments were added in millimetres (start → end, width):

| Net | Start → end | Width |
|---|---|---:|
| DN | (216.900,95.800) → (217.325,95.800) | 0.150 |
| DN | (217.325,95.800) → (217.425,95.800) | 0.250 |
| DN | (217.425,95.800) → (219.560,95.800) | 0.410 |
| DN | (219.560,95.800) → (220.410,94.950) | 0.410 |
| DN | (220.410,94.950) → (220.410,87.100) | 0.410 |
| DP | (216.900,95.400) → (217.125,95.400) | 0.150 |
| DP | (217.125,95.400) → (217.125,95.240) | 0.150 |
| DP | (217.125,95.240) → (217.325,95.240) | 0.150 |
| DP | (217.325,95.240) → (217.425,95.240) | 0.250 |
| DP | (217.425,95.240) → (219.000,95.240) | 0.410 |
| DP | (219.000,95.240) → (219.850,94.390) | 0.410 |
| DP | (219.850,94.390) → (219.850,87.100) | 0.410 |

The two open ends `(219.850,87.100)` and `(220.410,87.100)` are inside the independently measured empty partial trunk `[215.420,38.550,223.400,87.100]`. The 0.560-mm vertical-run centre spacing leaves a nominal 0.150-mm copper gap at full width. The diagonals are parallel 45-degree turns; local routes are 10.7521 mm DP and 11.7121 mm DN, a **0.9600-mm local skew**. This spends almost the entire 1.0-mm declared pair budget before connector and ESD entry; remaining route geometry must correct it. The launch retains the stepped 0.150/0.250/0.410-mm neck from the prior diagnostic and is not an impedance-qualified taper.

An exact `GetEffectiveShape().Collide` pass over each candidate segment found **zero foreign pad/track collisions** at 0.150-mm clearance (drilled holes checked at 0.250 mm), and zero DP/DN segment collisions at the native minimum 0.145-mm pair gap. On the refilled candidate, all **466** In1.Cu GND centerline samples at no more than 0.050-mm separation were inside the filled GND zone. These samples are a local return screen, not an unbroken return-current or impedance proof. C_XU_VDD_54 remains a tight local neighbor, with GND pad 2 spanning x=218.830..219.450, y=96.180..96.740; C_XU_VDDIO_56 spans x=217.690..218.310 on its pads at y=92.040..93.560. The north turn goes east of both capacitors.

Native `kicad-cli pcb drc --severity-all --all-track-errors --refill-zones --save-board --schematic-parity --format json` gave the exact input board **170** violations (80 clearance, 64 hole-clearance, 10 library-footprint issues, eight via-diameter, eight annular-width), 499 unconnected, zero schematic-parity findings. The candidate gave the same 170 plus exactly two `track_dangling` warnings at the intentional open ends; 499 unconnected and zero schematic-parity findings remain. No USB clearance, width, short, or rule finding was introduced. The refilled candidate board SHA-256 is `7b51b8e17d4442f1c16661d555701a38236dfc6cbe4110762420e124a8a98b91`; baseline/candidate native JSON hashes are `c59c4ed682b375bf6720c068d5b1aaf2712ac594b5a6de355acc4250226ba45a` and `cc17859691278f05c8e14989c0fa70bc91750591408bf7f34e6fc2affe24f404`. The candidate `.kicad_pro`/`.kicad_dru` hashes are `2d33b77e71d3c2f225ef0eeeaf7082100c2cbde688174427fd23773397df6b83` and `f029d3f1918e558cd3f250c7589bd9ecec0ac5617a96d2fdaccc65ce4177bcba`.

This establishes a collision-checked local F.Cu path into the measured trunk boundary on this board hash. It does not connect U_USB_ESD, prove the rest of the trunk, account for return discontinuities at connector/ESD, qualify impedance, close all USB alias contacts, or satisfy P1/P3.
