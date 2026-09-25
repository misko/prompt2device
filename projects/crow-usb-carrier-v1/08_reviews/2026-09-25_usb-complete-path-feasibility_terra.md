# Independent review: USB complete-path feasibility

**Subject.** The expanded-locked 7628G placement reference,
`06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb`, SHA-256
`fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16`;
canonical `03_src/rules/nets.yaml`, SHA-256
`18033487a097b6d29abe3f9d8517879931cf80d278d8973adcf276010a5b7190`;
the historical D15 private sidecars; and SOL's read-only measurement script,
SHA-256 `967b9c3efb9e7576991ba0ce228e739335e3650763eb9221cc23339fb71e0676`,
with report SHA-256
`c1d467cbba925f7bfab745b069794a02b40628b6452b689bd43daecad58e4e74`.
This is a read-only P1 feasibility review. It does not approve a rule, board,
route, connector, ESD selection, or a design stage.

## Verdict

The unchanged placement has a concrete **canonical-rule incompatibility**, not
a demonstrated complete-path failure. A same-placement USB route needs an
exact, source-owned pair-domain rule before a further diagnostic can be
meaningful. The pair must retain 0.150 mm clearance to every foreign object.
There is no evidence that a full connector/ESD/XU route, its return, or its
90-ohm behavior is feasible yet.

The smallest next hypothesis is the same-placement 3313A 0.180-mm pair:
endpoint pads accept that width without another neck exception. It needs a
reviewed source-owned, DP/DN-only pair domain spanning the complete physical
F.Cu pair, with 0.100 mm pair clearance and unchanged 0.150 mm foreign
clearance. It must explicitly cover the four Type-C leaves, both ESD data
pads, and `U_XU.59/.60`; the D15 XU-only exception cannot be extrapolated.
This is not a D15 replay or stack adoption and asserts no impedance. The
alternative 7628G path needs separately source-owned, quantitatively bounded
neck exceptions at both XU and Type-C, then transition analysis. Neither
option is admitted by this review.

## Reproduced native lower bounds

I ran SOL's hash-pinned read-only probe
`01_docs/research/2026-09-25-usb-path-feasibility-sol/measure.py` with KiCad
10.0.4. It reproduced the native pad boxes and the following static values.
They are pad/track-envelope lower bounds, not routes.

| Location | Canonical 0.410 mm track | 0.180 mm track | Consequence |
| --- | ---: | ---: | --- |
| `J_USB.B6` beside the 0.300 mm `A8` SBU pad | 0.145 mm foreign clearance | 0.200 mm pad/track-envelope clearance | 0.410 mm misses the 0.150 mm foreign rule by 0.005 mm. |
| `U_XU.60` beside `U_XU.61` (`N3V3X`) | 0.070 mm foreign clearance | 0.150 mm pad/track-envelope clearance | 0.410 mm misses the foreign rule by 0.080 mm. |
| `U_XU.59/.60` at 0.400 mm pitch | -0.010 mm pair copper gap | 0.220 mm pair copper gap | The canonical pair cannot emerge together at full width. |

The canonical source is exactly 0.410 mm width, 0.150 mm pair gap and 0.150
mm clearance. The historical D15 derivative is a different, failed-research
subject: its `USB_HS` class changes width/gap to 0.180/0.100 mm but retains
0.150 mm clearance. Its DRU gives 0.100 mm *clearance* only when both USB
tracks overlap `usb_pair_xu_launch`, the F.Cu rectangle
`[215.3, 95.0, 217.1, 95.8]`. That local exception cannot be read as a
0.100 mm connector or ESD corridor. Conversely, D15's 89.917-ohm 3313A
calculator output cannot be transferred to a 0.150 mm gap, the canonical
7628G stack, or this complete path.

## Complete-path obligations that remain open

The native net identity is sound: each data net has four terminals, with
`J_USB.A6/B6`, `U_USB_ESD.1`, `U_XU.60` on DP and
`J_USB.A7/B7`, `U_USB_ESD.2`, `U_XU.59` on DN. The reversible A/B leaves and
the ESD shunt leaves must remain in the route-length denominator; treating
the ESD as a series endpoint or omitting a Type-C leaf is insufficient.

Before a complete-path feasibility result can be accepted, the new exact
board/rule subject must show all of the following:

* Each of the three path identities in D8, F.Cu-only with no signal vias,
  no off-path copper, and at most 1 mm DP/DN spread per corresponding path.
* Continuous, filled In1.Cu ground below every pair segment and a reviewed
  connector/ESD ground-return path. The frozen board has no saved USB route
  and its saved GND zone is unfilled.
* A finite stack/mask/land/return model covering both XU and ESD transitions,
  pair-gap changes and connector branches. The XMOS material specifies a
  90-ohm, length-matched pair with a nearby unbroken reference, but supplies
  no transferable XU neck width, length or discontinuity limit.
* The exact TI DRT ESD part's connector-adjacent, low-inductance ground
  implementation and the still-open XU316 powered and rail-off transient
  finding. D13 keeps this selection `PROTOTYPE_ONLY`; component clamp and
  IEC ratings do not establish XU-pad survival or system ESD performance.
* Connector FULL and actual mating evidence. `J_USB`'s physical envelope
  extends 0.55 mm past the y=20 board edge, so logical pad access cannot
  substitute for the edge/mate decision.

The ordinary P1/P2/P3, connector FULL, D13 DESIGN_CLEAN, release and order
holds remain in force. The coarse P1 `INCOMPLETE` result and the D15
`FAILED_RESEARCH` screen do not change this verdict.
