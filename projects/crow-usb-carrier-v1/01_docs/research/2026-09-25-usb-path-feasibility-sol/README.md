# USB full-path feasibility screen — 2026-09-25

**Result: a continuous, legal USB path is not yet demonstrated.** This is one
read-only geometric hypothesis screen of the expanded locked 7628G placement,
not a route candidate, native routed DRC result, P1/P2/P3 admission, stack
selection, or connector qualification. Reproduce with
`/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-usb-path-feasibility-sol/measure.py`
from the repository root. It loads KiCad native pad boxes and stops on changed
input SHA-256. The input hashes are printed by the script: locked board
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`,
canonical `nets.yaml` `18033487a097b6d29abe3f9d8517879931cf80d278d8973adcf276010a5b7190`,
historical D15 DRU `ddb17c62f3beb2e0a03cf18acbb1148c36f60d516937c96660cfb44d146520a3`,
D15 project sidecar `2d0bf4d9c14fedee82e1ba22f06d05a4ba97e7b7fe39a66e086ec1c48b408c1a`,
and D15 board `ee34cf62a436fbebcd9afbdd0f046e5b9796e6a9ab60a8283d2e297a177b1db6`.
The D15 bytes are compared only as an unadopted rule hypothesis; that
experiment remains `FAILED_RESEARCH`.

## Exact native terminals and local clearance

The signal chain is `J_USB.A6/B6 (DP), A7/B7 (DN) → U_USB_ESD.1/.2 →
U_XU.60/.59`. The TI device is a **shunt**: its signal pads tap the continuous
DP/DN conductors; pad 3 is GND at `(217.0,35.575)` mm. The two signal pads
are 0.300-mm squares centred at `(216.65,36.425)` and `(217.35,36.425)` mm;
their 0.400-mm pad edge gap leaves local room to transition a pair, subject
to an actual route and return check.

At the Type-C receptacle, the four data pad centres at y=26.675 mm are,
in increasing x: `B6 DP 229.25`, `A7 DN 229.75`, `A6 DP 230.25`,
`B7 DN 230.75`. Each land is 0.300 mm wide in x, extends y=26.100–27.250,
and the adjacent unlike-net edge gap is 0.200 mm. For example, the `A8`
unconnected pad ends at x=228.900 and `B6 DP` starts at x=229.100;
`B6 DP`/`A7 DN` have the same gap. A centred, full-width
0.410-mm trace overlaps its land laterally by `(0.410−0.300)/2=0.055` mm,
leaving **0.145 mm** to the next unlike-net pad while the trace and land
overlap in y; this is 0.005 mm below the canonical 0.150-mm clearance.
At 0.180-mm width the pad contains the track, leaving the native 0.200-mm
pad-to-pad clearance. This is an endpoint launch lower bound, not a claim
that every conceivable neck or four-leaf topology is impossible.

At XU, pins 59 DN and 60 DP are centred `(216.1625,95.600)` and
`(216.1625,95.200)` mm. Their 0.250-mm-wide land boxes end at y=95.725
and begin at y=95.075 respectively; the native pad gap is 0.150 mm, also
the gap to foreign pads 58/61. A centred 0.410-mm parallel track pair would
have `0.400−0.410=−0.010` mm track-to-track edge gap. Each track also
overhangs its land toward a neighbouring foreign pad by 0.080 mm, leaving
only 0.070 mm of **pad-plus-track union** clearance to `61 N3V3X` from
`60 DP` (the `58`/`59` gap is the same). At 0.180-mm width the
tracks fit within their lands: their track-to-track gap is 0.220 mm and the
limiting union clearance remains the native 0.150-mm pad gap; track-only
clearance to the foreign pad is 0.185 mm. The prior local
0.150/0.250-mm stepped XU scratch launch is a separate failed-rule diagnostic;
it did not legalize a neck in the canonical 0.410-mm minimum-width contract.

## Whole-path constraints beyond these pads

The canonical 7628G source requires 0.410-mm width, 0.150-mm pair gap and
clearance, F.Cu over continuous In1.Cu, no USB vias, and at most 1 mm
DP/DN path spread across both reversible connector leaves and the ESD branch.
The locked board is unrouted. Its one saved GND zone is **unfilled F.Cu**;
there is no saved In1.Cu GND fill to inspect. The earlier linked-path coarse
screen reports two rough slots for two signals in `[229,28,231,29]` and three
for two in `[215.5,40,218.5,84]`. It does not prove the joins at either end,
continuous reference, trace spacing, skew, or clearance along the path.
The connector's alternating `P/N/P/N` leaves require an explicit native
four-leaf merge topology. This census alone cannot decide whether a no-via
F.Cu fan around pad tips can meet the rules; it must not be declared
topologically impossible from the alternating order alone.

The historical D15 3313A sidecar sets 0.180-mm USB width, 0.100-mm declared
pair gap and 0.150-mm general clearance. Its only 0.100-mm DP/DN clearance
rule applies when **both objects** are inside the F.Cu rectangle
`[215.3,95.0,217.1,95.8]` at XU. Thus the 0.100-mm figure has no effective
clearance authority over the ESD, connector, or intervening pair; a nominal
0.180/0.100-mm whole-path impedance calculation cannot be transferred to this
rule set. The historical D15 gate also failed independently and is not a
stack or board to route.

## Smallest next correction to evaluate

The least disruptive **next hypothesis** is the same-placement 3313A
0.180-mm pair, for which the measured endpoint pad envelopes accept the
width without an additional neck exception. Prepare one source-owned,
unadopted rule proposal extending the **DP/DN-only** 0.100-mm pair clearance
to the intended complete F.Cu pair domain, while retaining 0.150 mm to all
foreign copper. This would repair the D15 rule-domain mismatch; it would
not rehabilitate D15's failed gate or adopt 3313A as a production stack.
The 3313A stack and actual pad/ESD/connector transitions still need reviewed
fabrication and signal-integrity evidence, beyond the historical uniform-pair
nominal solve. An alternative 7628G investigation would instead need
source-owned, quantitatively bounded local neck exceptions at both XU and
Type-C, plus transition analysis; no neck width or length is selected here.

After the D18 P1/P2 and connector-neighbour prerequisites are met, evaluate
one native four-leaf merge and ESD-to-XU route with exact no-via, filled
In1.Cu return, DRC, skew and impedance checks. If that topology cannot clear
the locked placement, return to connector/ESD placement or a reviewed
layer/topology decision. No source, placement, route, rule or historical
receipt was changed by this measurement.
