# Channel-8 / USB boundary recut bound

**Research-only native-envelope map.**  The subject is the 15-footprint
candidate SHA-256 `d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`,
replayed from four-part SHA-256
`046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0`.
No board or canonical source was changed.  Envelopes below are checker
`_physical_envelope(fp)` (body/courtyard, excluding text), not a text-box
screen.

## Measured boundary occupants

Current source rectangles are `analog_ch8=[179,42,201,84]` and
`usb_vbus_sense=[195,62,215,82]` mm.  The candidate's cap is
`C_ADC_AC8N1=[195.405,58.505,200.995,61.995]`; its `ADC8N` pad is at
`(200.000,60.250)`.  Thus the current owner right edge and USB lower edge are
each 0.005 mm from the cap body.  This is only a zero-overlap result.

Five native channel-8 bodies occupy the present rectangle overlap
`[195,62,201,82]`:

| Ref | Native envelope (mm) |
| --- | --- |
| `C_A8N` | `[189.605,66.105,197.395,71.695]` |
| `C_FILTER8P1` | `[197.655,65.375,201.145,67.425]` |
| `R_IN8N` | `[194.525,71.985,196.475,73.015]` |
| `R_OUT8P` | `[197.825,69.885,199.775,70.915]` |
| `U_AFE8` | `[194.055,73.540,201.545,79.145]` |

No USB-owned body intersects the current analog rectangle.  The nearest USB
owner member is `R_VBUS_B=[205.825,70.185,207.775,71.215]`; the other USB
members are `R_VBUS_BE`, `R_VBUS_PU`, and `Q_VBUS`, still farther east.  The
open x interval between the channel-8 rightmost body (`U_AFE8.x2=201.545`)
and `R_VBUS_B.x1=205.825` is 4.280 mm.  This is a footprint map, not routed
capacity.

## Bounded simple recut

A *right-boundary-only* rectangular repartition can eliminate the cap's 5-µm
owner/foreign pinch without cutting one of the listed channel-8 or USB bodies:
set both `analog_ch8.x2` and `usb_vbus_sense.x1` to an x value in
`[201.695,205.675]` mm.  The interval applies an illustrative 0.150-mm
full-envelope separation from `U_AFE8` and `R_VBUS_B`; it is a geometry screen,
not a source rule for region edges.  The nearest choice, **x=201.695 mm**,
gives `C_ADC_AC8N1` 0.700 mm to the new right boundary and gives its east pad
1.695 mm to that boundary.  It also removes the cap's former y=62 USB
adjacency because the USB cell begins east of x=201.695.

This is the only compact boundary change supported by the map.  Moving only
the USB y=62 edge cannot help: the five channel-8 bodies above already inhabit
the overlap.  Moving only the analog x=201 edge also fails typed exclusivity:
it enlarges the overlap with USB rather than transferring it.

## Why this is not a useful typed mouth yet

The recut is a necessary geometric repair, not a P2 candidate.  It still does
not establish an exclusive physical-cell model: the full channel-8 population
also crosses other current region edges (`C_FILTER8P1` and `U_AFE8` to the
right; `R_IN8P` and `U_ESD8` to the left; `J8` below y=42), while the broader
source rectangles overlap other owners.  A full typed-cell checker cannot be
given just this one divider and truthfully declare all channel-8 members
contained exactly once.

Nor does the 1.695-mm pad-to-divider distance establish access or return.  No
trace leaves `C_ADC_AC8N1.2`, no via/layer transition is reserved, the moved
`U_ISO8` supply/`AUDIO_EN` pads have no route proof, and the GND reference zone
is unfilled.  The ADC7 portal remains a separate 0.255-mm `Y_AUDIO` geometry
condition.  Therefore **reject any claim that this recut creates a usable
access/return mouth**.  Its limited value is a precise next source experiment:
declare the x=201.695 divider in an isolated, complete physical-cell model and
first reject it unless every member is assigned once, every foreign cell is
disjoint, and named cap/ISO endpoint and return debts are supplied.  P1/P2
remain unaccepted.
