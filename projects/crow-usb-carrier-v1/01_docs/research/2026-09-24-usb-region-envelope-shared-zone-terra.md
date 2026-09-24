# USB region-envelope correction and rectilinear rejection

**Research only; no source region, PCB, route, task, or P1 attempt changed.**
This replaces the prior historical-board measurement in this file. That
measurement used the rejected repaired-trial board and is retracted: it must
not be used for USB virtual faces or any placement conclusion.

## Exact subject and native measurements

I copied the current source, generated one isolated board with
`generate_board_generic.py`, and measured KiCad
`FOOTPRINT.GetBoundingBox(True, True)` on that generated board. The input
floorplan SHA-256 is
`a882f87682484c37c5766a9e37c5a0d93b38a8e5a775fb1ab4425011da40a275`; the
saved 569-footprint board SHA-256 is
`60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`.
This is the current Q_VBUS-only source subject, with Q_VBUS at
`[212.0,74.5,0]`; no historical-box translation is used.

| Region | Current rectangle `[x0,y0,x1,y1]` mm | Full native member-envelope `[x0,y0,x1,y1]` mm |
| --- | --- | --- |
| `usb_frontend` | `[200,35,236,70]` | `[209.803571,18.574900,242.991667,46.148571]` |
| `usb_vbus_sense` | `[195,62,220,82]` | `[204.270238,66.538400,215.410715,77.761600]` |
| `xmos_core` | `[185,72,232,128]` | `[187.222857,83.139313,229.886905,114.860688]` |
| `clock_flash_debug` | `[185,112,232,136]` | `[200.617684,115.138399,221.791667,132.861600]` |

The USB pair terminals are U_USB_ESD.1/2 at `(216.650,36.425)` /
`(217.350,36.425)` and U_XU.60/59 at `(216.1625,95.400)` /
`(216.1625,95.800)`. The presence terminals are Q_VBUS.3 at
`(212.9375,74.5)`, R_VBUS_PU.2 at `(208.010,72.000)`, and **U_XU.8 at
`(205.100,107.6625)`**. The corrected U_XU.8 coordinate is material: the
earlier `(200.8375,96.6)` value belongs to the wrong historical board.

## Tested joint rectilinear candidate — REJECTED

The requested candidate was evaluated without editing the source:

```yaml
usb_frontend:      [200, 35, 236, 62]
usb_vbus_sense:    [195, 62, 220, 82]
xmos_core:         [190, 82, 232, 115]
clock_flash_debug: [185,115, 232,136]
```

It would remove the direct positive-area overlaps among these four edited
rectangles, but it is not admissible. Its new or moved full-width boundaries
intersect these native full footprint boxes:

| Candidate boundary | Intersecting full native footprints |
| --- | --- |
| frontend south y=62, x=200..236 | `R_B8P [198.470238,61.038400,203.934286,65.018250]`; `C_ADC_AC8N1 [194.225000,61.275000,208.377144,66.248250]`; `C_FILTER8N1 [196.049049,57.839313,200.950952,62.428250]` |
| sense north y=62, x=195..220 | `C_A8P`, `U_SPOKE8`, plus the same R_B8P, C_ADC_AC8N1, and C_FILTER8N1 |
| XMOS north y=82, x=190..232 | `C_SPOKE_OUT8 [184.608572,72.795000,191.591429,82.361600]` |
| XMOS west x=190, y=82..115 | own `C_XU_VDD_105`, `C_XU_VDDIO_109`, and `C_XU_VDDIO_121`, plus `C_SPOKE_OUT8` |
| XMOS south y=115, x=190..232 | none |
| clock north y=115, x=185..232 | none |
| sense south y=82, x=195..220 | none |

No one of the exact 27 `p1_fixed_refs` crosses those tested boundary segments.
That does not rescue the candidate: its own-XMOS and foreign analog footprints
are full-body blockers. In particular, the west move from x=185 to x=190
cuts three `xmos_core` member envelopes, so the candidate cannot be described
as merely removing an ownership overlap.

## Remaining source-region conflicts

The candidate also leaves or reveals positive-area source overlaps outside the
four-cell relation. Those relevant to the USB side are `analog_ch8` with
`usb_frontend [200,42,201,62]`, `usb_vbus_sense [195,62,201,82]`, and
`xmos_core [190,82,201,84]`; and `debug_connector` with
`usb_frontend [218,35,236,62]` and `usb_vbus_sense [218,62,220,65]`.
It also retains the known ADC/audio, analog/audio, audio/digital-power,
hold-bank/quiet-power, and input-buck/quiet-power overlaps. Therefore the
candidate does not establish globally exclusive source cells.

## Disposition

Do not promote a rectangular or shared-zone model from this result. A later
source redesign must start with the exact current board and create a
footprint-clear staggered polygon or a schema-supported explicit shared zone.
It must name only faces that are clear on the exact board, preserve all 27
fixed refs, enumerate foreign occupants as obstacles, and then separately
prove short P2 pad-to-face geometry for USB_DP, USB_DN, and
VBUS_PRESENT_N. The present virtual pad-to-face gaps of roughly 7–27 mm are
not acceptable as those short obligations. No route, capacity, return, or
P1/P2 claim follows from this rejection.
