# USB4215 edge-registration coupon — measurement and lot record

**Status: UNMEASURED / INCOMPLETE.** This is a research coupon only. It does
not establish final-board mounting, connector FULL, P-OUT, release, order,
USB electrical operation, or ESD qualification.

## Bound source and coupon

| Item | Bound value |
|---|---|
| Connector | GCT USB4215-03-A |
| Manufacturer drawing | `../../../02_parts/USB4215-03-A/GCT_USB4215_A.pdf`, SHA-256 `1659ba00769b9b774a033fac72cb2f3bfc481a3272c53f34e87520f33635a9e1` |
| Footprint | `../../../03_src/lib/crow_usb_carrier_v1.pretty/GCT_USB4215_03_A.kicad_mod`, SHA-256 `956c6c04aa94ff5f4afa434db4715a93dc2d348fcbfb8495f9c5def98407c828` |
| Coupon PCB | `usb4215_edge_registration_coupon.kicad_pcb`, SHA-256 `5c6d66ae98d714c4478ba2fd585376287ca8fd5d7e4850afcff9ade9b9e8b998` |
| Coupon nominal outline | 30.0 x 20.0 mm; datum A is top Edge.Cuts y=0.000; datum B is x=15.000 |
| Connector pose | J_EDGE [15.000, 2.995, 180 degrees] |
| Current coupon process state | 2 copper layers, KiCad default 1.60 mm; no stackup/process match claimed |
| Exact TI comparison target | 4 copper layers, KiCad target 1.63 mm; not reproduced by this coupon |
| If a future build is admitted | Record fabricator finished-thickness target/tolerance and measured thickness; do not infer 1.63 mm |

The pose is the drawing-marker-flush hypothesis only: local front/mouth marker
+2.995 mm maps to board -Y at 180 degrees. **The generated coupon is currently
a two-copper-layer, 1.60-mm-default KiCad board, whereas the exact TI
 diagnostic board is four copper layers at a 1.63-mm KiCad target. It is
therefore nonqualifying for fabrication or process-matched registration until
an approved four-layer fabricator stackup and finished-thickness correspondence
is bound.** The vendor record does not provide
an installed mating-plane-to-PCB-edge tolerance, allowable edge setback, board
thickness tolerance, assembly method, or cable/enclosure clearance. Therefore
there are deliberately **no pass numerical limits** below until the build
house stackup/tolerance and intended mate are recorded.

## Lot/build traceability

| Field | Record |
|---|---|
| Coupon revision / PCB SHA | |
| Coupon quantity and lot IDs | |
| Fabricator, stackup, finished thickness target/tolerance | |
| Measured finished thickness at J_EDGE (three locations) | |
| Connector manufacturer lot/date code | |
| Assembly method, reflow profile, operator | |
| Measurement equipment and calibration ID | |
| Cable/plug MPN and lot used for mating trial | |
| Photos / microscope files / operator | |

## Measurements

Record three coupons minimum if fabricated. Measure before and after mating;
record the instrument uncertainty with each result.

| ID | Observable | Datum / method | Result | Limit | Disposition |
|---|---|---|---|---|---|
| M1 | Finished board thickness | near J_EDGE shell slots, three points | | build-specific | |
| M2 | Board-edge to drawing-marker registration | datum A to observed connector front/mouth feature; side view | | **UNSET** | |
| M3 | Shell-slot seating | shell/stake contact and lift at all four slots; microscope | | **UNSET** | |
| M4 | Edge damage | breakout, delamination, plating fracture at lower slots | | none permitted after criteria set | |
| M5 | Mating insertion/seating | named plug, fully seated state, interference/exposure photos | | **UNSET** | |
| M6 | Post-mating retention/visual | connector shift, shell deformation, board damage | | **UNSET** | |
| M7 | Courtyard projection | datum A to front F.CrtYd projection; nominal 0.505 mm | informational only | n/a | |

## Acceptance gate

A qualified reviewer must set M2–M6 limits from the named mating plug,
fabricator finished-thickness/edge/drill tolerances, and intended mechanical
envelope before fabrication evidence can be evaluated. Until then this record
remains INCOMPLETE. A passing coupon would address only the measured coupon
configuration; it would still require exact-final-board pose, neighbor,
assembly, routing, return, and connector-contract review.

## Current design-screen disposition

The coupon carries the manufacturer-native contact map to remove false fused-pad
shorts. Raw KiCad DRC reports zero geometric violations, but eight unconnected
items remain for GND, VBUS, USB_DP and USB_DN because this is intentionally a
mechanical-only article with no electrical topology. Adding arbitrary copper
or no-connect suppression solely to obtain a clean electrical DRC would create
unsupported electrical intent. No Gerber or drill export is authorized.

`generate_coupon.py` recreates the declared geometry but KiCad assigns fresh item UUIDs, so regenerated board bytes are not hash-stable. `verify_coupon.py` verifies the checked-in snapshot by default; `--rebuild` deliberately creates a new candidate that must receive a new hash and review binding before use.
