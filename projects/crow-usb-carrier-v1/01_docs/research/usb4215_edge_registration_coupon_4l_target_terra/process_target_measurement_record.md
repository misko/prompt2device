# USB4215 four-layer registration coupon — process target and measurement record

**Status: PROCESS TARGET / UNMEASURED / INCOMPLETE.** This separate research
candidate is not a fabrication release. It does not establish final-board
mounting, connector FULL, P-OUT, release, order, USB electrical operation, or
ESD qualification. The existing two-layer snapshot under
`../usb4215_edge_registration_coupon_terra/` is immutable and remains a
separate, non-process-matched record.

## Bound candidate and authority

| Item | Bound value |
|---|---|
| Connector | GCT USB4215-03-A |
| Manufacturer drawing | `../../../02_parts/USB4215-03-A/GCT_USB4215_A.pdf`, SHA-256 `1659ba00769b9b774a033fac72cb2f3bfc481a3272c53f34e87520f33635a9e1` |
| Native footprint | `../../../03_src/lib/crow_usb_carrier_v1.pretty/GCT_USB4215_03_A.kicad_mod`, SHA-256 `956c6c04aa94ff5f4afa434db4715a93dc2d348fcbfb8495f9c5def98407c828` |
| Coupon generator | `generate_coupon.py`, SHA-256 `3163f6b1ddcc8c344a771656ee600150b1eb683da39bbfd61bf12a0ec88ae796` |
| Coupon PCB | `usb4215_edge_registration_coupon_4l_target.kicad_pcb`, SHA-256 `ef853f84f29b25ec995eed0c6bc561cc3d96b6846b4bc90324210c4bbfc417f6` |
| Coupon nominal outline | 30.0 x 20.0 mm; datum A is the routed top Edge.Cuts line `y=0.000`; datum B is centerline `x=15.000` |
| Connector pose | J_EDGE `[15.000, 2.995, 180 degrees]` |
| Coupon target in KiCad | 4 copper layers; 1.60 mm nominal board thickness |
| Local architecture target | `01_docs/ARCHITECTURE.md` / decision 0005: JLC04161H-7628G, nominal 1.6 mm, 1 oz outer and 0.5 oz inner copper |
| Exact TI diagnostic comparison | 4 copper layers, KiCad target 1.63 mm; this coupon is **not** a 1.63 mm match |
| Public fabricator capability checked | JLCPCB [Capabilities](https://jlcpcb.com/capabilities/Capabilities), accessed 2026-09-24: selectable 4-layer service and 1.60 mm board thickness; stated thickness tolerance at >=1 mm is +/-10% |

The JLC public capability record makes a **selectable nominal** four-copper,
1.60-mm coupon plausible. It does not bind a quote, actual stackup, material,
finished thickness, or production DFM acceptance. At the stated +/-10%, a
nominal 1.60-mm board may measure 1.44–1.76 mm. The exact-board KiCad setting
of 1.63 mm is only a design target and is not demonstrated equivalent to this
coupon or to a fabricator's finished stackup.

The same JLC record gives a multilayer plated-slot minimum of 0.35 mm and a
routed copper-to-edge minimum of 0.20 mm. The native connector uses 0.60-mm
shell slots and has nominally 1.0-mm shell copper-to-edge clearance, so these
are dimensional screens only. They are not an approved connector, edge, or
assembly exception. The 30 x 20 mm coupon also does not meet JLC's published
50 x 50 mm plus three 1.5-mm tooling-hole condition for its precision-routing
option; use only the regular routed-edge tolerance unless a future coupon is
redesigned and the order option is confirmed.

## Datum and measurement plan

The drawing-derived hypothesis places the local front/mouth marker at `+2.995`
mm from the footprint origin. At 180 degrees it maps to board `-Y`, flush with
datum A. Datum B controls lateral symmetry. It deliberately tests registration;
it does not assert that the marker is an approved GCT mating plane.

Fabricate at least three coupons only after the missing authorities below are
bound. For each coupon, record the actual fabrication lot, selected stackup,
and named mating plug before measuring.

| ID | Observable | Datum / method | Result | Limit | Disposition |
|---|---|---|---|---|---|
| M1 | Finished thickness | Three micrometer readings near, but not through, shell slots | | build-specific | |
| M2 | Edge registration | Datum A to observed front/mouth feature in a calibrated side view | | **UNSET** | |
| M3 | Lateral registration | Datum B to connector center / both shell-slot centerlines | | **UNSET** | |
| M4 | Shell seating | All four shell slots: stake contact, lift and solder wetting, microscope | | **UNSET** | |
| M5 | Edge integrity | Breakout, delamination, plating fracture around shell slots before/after mating | | **UNSET** | |
| M6 | Mating/seating | Named plug, fully seated state, insertion interference and exposure photos | | **UNSET** | |
| M7 | Post-mating retention | Connector shift, shell deformation and board damage | | **UNSET** | |
| M8 | Courtyard projection | Datum A to front F.CrtYd projection, nominal 0.505 mm | informational only | n/a |

### Required lot record

| Field | Record |
|---|---|
| Coupon PCB SHA / generator SHA | |
| Coupon quantity and fabricator lot IDs | |
| Ordered layer count, stackup, finished-thickness target/tolerance | |
| Actual thickness readings and instrument uncertainty | |
| Connector manufacturer lot/date code | |
| Assembly method, reflow profile and operator | |
| Measurement equipment and calibration ID | |
| Mating plug MPN, lot and cable/enclosure condition | |
| Photos / microscope files / operator | |

## DRC and deliberate limits

`verify_coupon.py` binds the four-copper/1.60-mm setting, connector pose and a
fresh KiCad DRC report. The committed result is zero DRC violations and eight
unconnected items. The generator assigns native connector functions to the
fused physical lands to avoid artificial shorts, but leaves the mechanical
article without electrical topology. Those opens include GND, VBUS, USB_DP and
USB_DN. Adding arbitrary copper or suppressions to make an electrical DRC pass
would add unsupported electrical intent.

`generate_coupon.py` recreates declared geometry, but KiCad assigns fresh item
UUIDs. A `verify_coupon.py --rebuild` run creates a new board candidate and
therefore requires a new board-hash binding and review before use.

## Missing authority and next evidence

The local GCT drawing and footprint do **not** provide an installed
mating-plane-to-board-edge tolerance, allowable board-edge setback, approved
finished-thickness range, shell-stake assembly method, named mating plug, or
cable/enclosure clearance. Consequently M2–M7 have no defensible acceptance
limits, and a fabricated coupon could provide observations only.

Before admitting fabrication or interpreting measurements, obtain:

1. GCT's controlled mechanical evidence or written confirmation defining the
   mating/edge datum, permitted edge relation and thickness range for
   USB4215-03-A.
2. A fabricator order/quote or controlled stackup confirmation tying a
   selectable 4-layer, nominal-1.60-mm build to the intended material and
   finished-thickness tolerance; do not infer it from KiCad or the generic JLC
   capability page.
3. The intended plug/cable and enclosure clearance limits, then a controlled
   lot measurement using the table above.

Until then this is a process-target candidate only: no Gerber/drill export,
order, FULL/P-OUT credit, or final-board exception is authorized.
