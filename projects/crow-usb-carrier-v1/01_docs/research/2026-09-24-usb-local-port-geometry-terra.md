# USB local-port geometry on the exact 569-footprint board

**Research only.** This records a bounded physical-port screen for a future
`board_integration` transition model.  It changes no canonical source, PCB,
route, task state, P1 state, or P3 state.

## Exact subject and measurement method

The subject is the current `03_src/floorplan.yaml`, SHA-256
`a882f87682484c37c5766a9e37c5a0d93b38a8e5a775fb1ab4425011da40a275`.
I regenerated it in an isolated copy with `generate_board_generic.py`; the
resulting 569-footprint board SHA-256 is exactly
`60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`.

All bodies below are KiCad `FOOTPRINT.GetBoundingBox(True, True)` full boxes,
and pad coordinates/sizes are native board values in millimetres.  The source
board has no signal track in this area; its only nearby existing copper item
is a GND via at `(202.7,58.4)`, outside the proposed trunk.  Thus the result
does not imply a cleared F.Cu or B.Cu routing lane after P2 routing begins.

| Item | Native pad centre / full footprint box |
| --- | --- |
| `U_USB_ESD.1` / `.2` | USB_DP `(216.650,36.425)` / USB_DN `(217.350,36.425)`; package `[209.803571,33.651750,224.196429,38.348250]` |
| `Q_VBUS.3` | VBUS_PRESENT_N `(212.9375,74.5000)`; package `[208.589286,71.038400,215.410715,77.748250]` |
| `R_VBUS_PU.2` | VBUS_PRESENT_N `(208.010,72.000)`; package `[204.851429,71.505000,210.148572,77.761600]` |
| `U_XU.60` / `.59` | USB_DP `(216.1625,95.4000)` / USB_DN `(216.1625,95.8000)`; package `[199.825000,88.019107,218.698250,110.101190]` |
| `U_XU.8` | VBUS_PRESENT_N `(205.1000,107.6625)`; same `U_XU` package |

## What is physically available now

There is one body-clear, fixed-reference-clear empty trunk:

```yaml
usb_pre_xu_transition_trunk:
  owner: board_integration
  status: P2_REQUIRED
  bbox_mm: [215.420, 38.550, 223.400, 87.100]
  layers: [F.Cu, B.Cu]
  semantics: obstacle-bounded transition workspace, not a routed lane or capacity claim
```

No full footprint intersects this open rectangle.  The east edge stops
0.075 mm before fixed `J_JTAG`'s full box at
`[223.475,38.307684,232.525,61.692315]`; the south edge stops 0.0384 mm
before `C_XU_VDD_68` begins at y=87.1384.  None of the exact 27
`p1_fixed_refs` intersects the trunk.  The apparent empty space is bounded
on its west and south by movable USB/XMOS support parts; it cannot be treated
as exclusive board capacity.

Two pad-adjacent, body-external P2 ports can enter this trunk:

```yaml
ports:
  - id: usb_esd_pair_south
    nets: [USB_DP, USB_DN]
    segment_mm: [216.500, 38.550, 217.500, 38.550]
    source_pads: [U_USB_ESD.1, U_USB_ESD.2]
    pad_center_to_port_mm: [2.125, 2.125]
    status: P2_REQUIRED
  - id: vbus_present_q_east
    nets: [VBUS_PRESENT_N]
    segment_mm: [215.420, 74.200, 215.420, 74.800]
    source_pads: [Q_VBUS.3]
    pad_center_to_port_mm: [2.4825]
    status: P2_REQUIRED
```

The distances are geometric pad-centre-to-segment minima, not trace lengths.
They deliberately start outside the full footprints: the ESD port is 0.20175
mm below its package box and the Q port is 0.009285 mm east of its package
box.  P2 must prove each actual package escape, width/clearance, local ground
return, and any F.Cu/B.Cu transition; this document does not infer a route
through a component body or courtyard.

## Why there is no complete USB transition-port proposal

The remaining two required local exits are physically blocked on the exact
board, so adding fictional XU ports would repeat the rejected long-distance
virtual-face error.

* `U_XU.60/.59` point east, but `C_XU_VDD_54`
  `[218.655000,93.378400,225.274287,99.374524]` and
  `C_XU_VDD_50` `[217.515000,94.865713,223.961600,101.134286]`
  cover the direct pair exit.  The north alternative is cut by
  `C_XU_VDD_68` `[210.365714,87.138399,216.634287,92.608250]`.
* `U_XU.8` points south.  Its first body-external south escape is blocked by
  `C_XU_VDD_11` `[198.615537,108.915000,208.434524,114.860688]`,
  `C_XU_VDDIO_10` `[199.908571,108.915000,207.091429,112.861600]`, and
  `C_XU_USB18` `[203.651428,110.315000,209.548572,114.261600]`.

The west side is additionally constrained by the analog-8 population
(`U_AFE8`, `R_IN8N`, `R_OUT8P`, `C_ADC_AC8N1`, and `C_FILTER8N1`), while the
upper-right continuation is bounded by the fixed JTAG connector.  These are
full-body observations, not a request to move any part.

Accordingly, the only sound shared-model proposal is the partial trunk plus
the two stated ports.  A future source-owned `board_integration` geometry may
adopt it only if it also declares the five XU-support footprints above as
P2-movable obstacles and adds new **measured, body-external** XU pair and
presence ports after a placement candidate.  It must bind all five terminal
groups—`U_USB_ESD.1/.2`, `Q_VBUS.3`, `R_VBUS_PU.2`, `U_XU.60/.59`, and
`U_XU.8`—rather than crediting the trunk as an endpoint.

This is insufficient for pair capacity, impedance, continuous reference,
VBUS current/thermal analysis, a complete all-terminal presence route, or
any P1/P3 conclusion.
