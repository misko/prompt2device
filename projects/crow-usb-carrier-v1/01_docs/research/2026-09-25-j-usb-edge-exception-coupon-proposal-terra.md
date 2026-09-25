# J_USB edge/courtyard exception and measurement proposal

**Status: proposal only.** It neither changes a source rule nor authorizes a
coupon, board, fabrication, P1 result, connector FULL result, routing, release,
or order.

## Exact diagnostic observation

Subject: ignored TI unrouted diagnostic board
`06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.

`J_USB` is `USB4215-03-A` using
`crow_usb_carrier_v1:GCT_USB4215_03_A` at `(230.000, 22.995, 180°)` on the
rectangular south edge `y=20.000`. Its F.CrtYd vertices are
`(225.005,19.500)`, `(234.995,19.500)`, `(234.995,27.750)`, and
`(225.005,27.750)` mm. Thus only the courtyard projects 0.500 mm outboard.
The strict P-OUT run reports that same 0.5-mm projection.

The footprint source has an F.Fab body rectangle ending nominally at local
`y=+2.995` and F.CrtYd ending at local `y=+3.500`. At the recorded 180° pose,
the nominal F.Fab front is the board edge (`y=20.000`); its 0.1-mm drawing
stroke has a `y=19.950` graphic bounding edge. No copper pad projects outboard:
the nearest shell-slot pad bounding box begins 1.000 mm inboard and signal-pad
boxes begin 6.100 mm inboard. The board's other P-OUT cases are not part of
this observation: J1–J8 and J_PWR are each at 0.00 mm inside a 0.15-mm generic
margin.

GCT drawing A, retained as `02_parts/USB4215-03-A/GCT_USB4215_A.pdf`
(SHA-256 `1659ba00769b9b774a033fac72cb2f3bfc481a3272c53f34e87520f33635a9e1),
supports the footprint's contact/shell layout and body dimensions. The part
notes expressly retain the board edge, shell-stake seating, mating datum and
installed orientation as owed. Therefore the outboard courtyard is a plausible,
authored edge-mount convention (its nominal 0.50-mm clearance beyond the body),
not yet an approved physical edge/mating authority.

## Why existing waiver forms are unsafe

`placement_gates.py` offers `out_ok`, which excludes a reference from *all*
P-OUT points, including its pads, and a whole-check `waive.P-OUT`. Neither is
safe here. Lowering `outline_margin` would also affect every footprint; adding
J1–J8/J_PWR to `out_ok` would hide their separate zero-margin cases. Do not use
any of those forms to record this USB-specific condition.

## Proposed narrow contract (not implemented)

Extend the placement-gate configuration and its generic checker with a typed
`outboard_courtyard_exceptions` list. A future single J_USB entry should be
accepted only when every field below matches the generated board:

```yaml
- id: j_usb_usb4215_south_courtyard
  ref: J_USB
  expected_value: USB4215-03-A
  expected_footprint: crow_usb_carrier_v1:GCT_USB4215_03_A
  expected_pose_mm_deg: [230.000, 22.995, 180.0]
  outline_segment: {axis: y, value_mm: 20.000, x_min_mm: 225.005, x_max_mm: 234.995}
  outboard_direction: negative_y
  allowed_layer: F.CrtYd
  max_outboard_mm: 0.500
  required_inside: {all_pads: true, nominal_fab_body: true}
  source_evidence:
    - 02_parts/USB4215-03-A/GCT_USB4215_A.pdf
    - 01_docs/research/2026-09-25-j-usb-edge-registration-measurement.md
```

The proposed checker behavior is deliberately narrow:

1. It first applies the ordinary P-OUT test to every pad and all non-exempt
   courtyard geometry.
2. It suppresses only F.CrtYd points that are within the named south-edge span
   and no more than 0.500 mm outboard. A 0.501-mm projection, a side/north-edge
   projection, changed pose/value/footprint, or a pad/body projection fails.
3. It reports the exception ID, exact maximum measured projection, board hash,
   and source-evidence hashes. It cannot waive P-BODYCLR, P-CAP, native DRC,
   connector FULL, or any other P-OUT reference.

The `nominal_fab_body` condition must use the manufacturer-derived body envelope
rather than F.Fab stroke width, since F.Fab is drawing artwork. If a reviewed
body-envelope representation cannot be made machine-checkable, leave this
exception unavailable rather than treating F.Fab graphics as a physical pass.

## Required future registration measurement

The referenced measurement record must bind the exact candidate/coupon board,
footprint/library hashes, `USB4215-03-A` lot, board thickness and finished edge
process. It must record, with calibrated method and raw data:

- actual finished edge versus the native `y=20.000` datum;
- shell-slot and contact locations versus the edge, and the receptacle body
  front/mouth direction versus the registered datum;
- seating/coplanarity and shell-stake mounting geometry;
- fully mated exact `A-USB31C-20A-100` plug exposure/engagement, with the
  assigned board `-Y` mating axis; and
- photos/drawings identifying sample, board hash, connector/cable lots and
  measurement coordinates.

A metrology sample can establish only the declared P-OUT edge-registration
exception after independent review. It does not close `usb_device.interface`,
`reaction`, `usb_device_service`, `cable`, or `usb_device_registration`; those
remain among connector FULL's 19 physical unknowns and need the existing
separately governed coupon/candidate procedure.

## Disposition

Do not adopt an exception until the exact-part edge registration and the typed,
fail-closed checker behavior are reviewed. Until then this diagnostic retains
its J_USB P-OUT failure alongside J1–J8/J_PWR, and receives no P1 credit.
