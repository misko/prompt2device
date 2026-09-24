# P1 ADC analog boundary: isolated native screen

This is a placement diagnostic on the preserved 569-footprint isolated board
`01_docs/research/2026-09-24-p1-native-evidence-failure-evidence/candidate.kicad_pcb`,
SHA-256 `6d948f70f31c1b54dd75d53f5699c8b8fdc61ddf79d0451c3173190ea5b5ccfa`.
It does not change the canonical board, corridor source, or an active P1 attempt.
The source denominator in `03_src/rules/p1_corridor_requirements.yaml` is exact:
channels 1–4 plus VMID1 and channels 5–8 plus VMID2 each have 9 nets,
44 listed ref.pad endpoints on 37 footprints, and demand 9 F.Cu slots at
0.56 mm pitch (5.04 mm nominal width). All 88 listed ref.pad identifiers are
unique. These are branched networks; a scalar nine-slot trunk alone cannot
prove every branch or pad access.

Native KiCad coordinates in mm show why endpoint pockets cannot yet be frozen.
The channel capacitor/CM endpoint bodies for channels 1–8 sit at roughly
`x=26.225..199.775, y=56.175..70.825`; their P/N input cells are distributed
at 22 mm x pitch. `U_ADC_A` body is `[134.175,93.175,139.825,98.825]` with
analog pads 6–13 at y=97.25/97.90. `U_ADC_B` body is
`[134.175,105.175,139.825,110.825]` with analog pads 6–13 at
y=109.25/109.90. The VMID1 bank occupies x=121.395..129.255,
y=90.525..97.155, while VMID2 occupies x=111.245..121.005,
y=92.745..97.225. The VMID1 branch resistor pads run from
`R_B1N.2 (34.81,53.20)` to `R_B4P.2 (113.51,63.00)`;
VMID2 runs from `R_B5N.2 (122.81,53.20)` to
`R_B8P.2 (201.51,63.00)`. A single rectangular through-lane and pockets
for each 44-pad group would span these separate cells and cannot be claimed
from this placement. The channel-end pockets must include whole footprint
bodies, touch their lane, and remain outside the lane, as required by
`p1_corridor_capacity.py`; none has been authored or validated.

The checker also requires each pad's individual pocket to contain the
*entire* footprint body. All eight analog pads on one ADC therefore inherit
the same full-body pocket requirement, even if their escapes diverge. This
can reject a valid per-pad fanout as a structural false negative. Conversely,
the capacity calculation excludes an entire endpoint footprint from its
obstacles and can overstate free space around unrelated pads on that body.
Neither behavior licenses a smaller pocket or a passing capacity claim.

The following *negative probes* use `layer_obstacles` and
`connected_capacity` from `skills/kicad-pcb/scripts/p1_corridor_capacity.py`.
Each excludes only the 37 listed endpoint footprint refs of its own group,
so the measured foreign-body/pad bottleneck remains optimistic: no copper
clearance, courtyard, or pad-to-lane access was added. Coordinates are
`[x0,y0,x1,y1]`, F.Cu, horizontal, 0.56 mm raw slot pitch.

| Probe | Through box mm | Connected width mm | Raw slots / required | Finding |
| --- | --- | ---: | ---: | --- |
| VMID1-to-ADC-A neighborhood | `[114,89,140,99]` | 0.820 | 1 / 9 | ADC-A collar and nearby foreign parts squeeze the only connected path in this box. |
| VMID2-to-ADC-B neighborhood | `[111,92,140,106]` | 2.550 | 4 / 9 | ADC-A/B collars and reset/control parts obstruct a nine-slot common passage. |
| Broad channel 1–4 upper gap | `[26,71,140,93]` | 7.680 | 13 / 9 | Raw width alone is optimistic; the box has no validated 44 endpoint pockets or VMID/ADC access. |
| Broad channel 5–8 upper gap | `[114,71,140,105]` | 10.620 | 18 / 9 | Same endpoint failure; the box omits the eastward channel 6–8 cells and skirts the lower ADC-B pads. |

The negative VMID1 probe sees `C_ADC_A_AREG_100N/1U`,
`C_ADC_A_AVDD_100N/10U`, `C_ADC_A_DREG_100N/1U`, and the remaining ADC-A
collar as foreign bodies or pads. VMID2 also encounters ADC-B collar and
reset/control bodies. These are measured placement conflicts, not a proof that
all possible future shapes fail. Both broad boxes cross many channel and
support bodies; their high raw slot counts are not a route witness.

The native board has eight tiny F.Cu TMUX rule areas and one board-wide
In1.Cu GND zone, whose `IsFilled()` is false. No continuous filled GND
reference exists in this artifact under any proposed analog signal strip.
The capacity tool intentionally reports crow-p1 reference/pour continuity as
unmeasured even for a geometrically complete contract; the board-wide zone
also intersects all four probe boxes by its native bounding box. Do not
remove that zone to obtain a capacity result.

P1 analog boundary remains **INCOMPLETE**. Placement must first arrange the
ADC-A/ADC-B input collars, VMID banks, and channel handoffs into explicit
branch/lane topology. Then author exact touching, nonintersecting pockets for
all 88 ref.pad endpoints on an exact-hash board, independently bind the
capacity contract hash, and inspect native filled GND return and pour breaks.
No route, DRC, return continuity, or P1 acceptance is established here.
