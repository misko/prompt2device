# P1 analog bank: one isolated VMID placement change

One source-controlled floorplan hypothesis was tested in
`/tmp/crow-p1-analog-one-change-20260924`, with no canonical source/board or
active P1 attempt edit. The isolated `03_src/floorplan.yaml` copied the live
source and translated these eight `placement.post_anchors` by `(0,-12.00)` mm:
`C_VMID1_EXT_10U`, `C_VMID1_EXT_1U`, `R_VMID1_BOT`, `R_VMID1_TOP`,
`C_VMID2_EXT_10U`, `C_VMID2_EXT_1U`, `R_VMID2_BOT`, `R_VMID2_TOP`.
For example `C_VMID1_EXT_10U` changed from `[122.75,92.25,-90]` to
`[122.75,80.25,-90]`; `C_VMID2_EXT_10U` from `[120.00,95.50,-90]` to
`[120.00,83.50,-90]`. All eight rotations and intrabank relative poses
were retained. This is one coherent local bank allocation change, not a
proposed canonical placement. The netlist and all other source values were
identical for baseline and candidate.

The native generator produced two 569-footprint boards from those two exact
floorplans. Baseline board SHA-256 is
`4849d58d58c984401340e99cfbaf37e68345be34f87bcbd6bc33078ee2867285`;
candidate board SHA-256 is
`4af6297b504a61ffe0716121b5457596e9258eaa954c461995b363962febca2b`.
The generator reported zero inter-footprint pad overlaps/shorts and zero fixed
courtyard overlaps in the candidate. Native pose comparison found exactly
the eight named footprints changed; connector, power, XMOS, ADC, channel,
and collar poses were identical. Every source-listed analog ref.pad/net
identity remains present: 44/44 for channels 1–4 plus VMID1, and 44/44 for
channels 5–8 plus VMID2.

The table is a **negative/optimistic F.Cu rectangle screen**, using the
existing `p1_corridor_capacity.py` `layer_obstacles` and
`connected_capacity` functions with the 37 group endpoint footprints
excluded. Boxes are `[x0,y0,x1,y1]` mm. Each bank requires 9 raw slots at
0.56 mm pitch, or 5.04 mm. The rectangles are candidate graph edges, not
validated through-lanes: no whole-body endpoint pockets or pad access are
claimed.

| Graph edge / box | Axis | Bank 1 baseline → moved | Bank 2 baseline → moved |
| --- | --- | ---: | ---: |
| North shared trunk `[111,71,140,88]` | horizontal | 8.875 mm (15) → 3.870 mm (6) | 8.875 mm (15) → 3.495 mm (6) |
| South approach `[129,84,140,111]` | vertical | 1.375 mm (2) → 1.375 mm (2) | 1.540 mm (2) → 1.795 mm (3) |
| ADC-A collar `[129,89,140,99]` | horizontal | 0.820 mm (1) → 0.820 mm (1) | 0.370 mm (0) → 0.370 mm (0) |
| ADC-B collar `[129,101,140,111]` | horizontal | 0.375 mm (0) → 0.375 mm (0) | 1.815 mm (3) → 1.815 mm (3) |

The relocated banks occupy the north trunk and cut its raw capacity below
the nine-slot demand. At the ADC-A collar, the 0.820-mm bottleneck occurs
around x=131.75..132.46 and intersects the unchanged AREG/AVDD/DREG/IOVDD/
VREF capacitor collar. The ADC-B collar's 1.815-mm bottleneck occurs around
x=131.63..132.10 amid its own unchanged capacitor collar. A vertical south
approach also crosses the ADC-A/B collars. Thus the one local VMID translation
does not produce a nine-slot branching corridor; it moves the obstruction
upstream while leaving both ADC input approaches constricted.

The baseline and candidate each retain the board-wide In1.Cu GND zone, but
the native zone is unfilled. The corridor checker cannot independently prove
crow-p1 filled-reference continuity, and the zone's bounding box intersects
these rectangles. Do not remove the zone to make a capacity receipt green.

**Disposition: P1 analog boundary remains INCOMPLETE.** The tested local
VMID-bank move is insufficient. A constructive source candidate needs a
coordinated channel endpoint and ADC collar layout, with explicit per-channel
branches and VMID branches; ADC relocation may be necessary if the collar
cannot expose 5.04 mm without violating its local return/decoupling needs.
The one experiment does not prove every possible local arrangement fails.
Before claiming either bank, the full 44 whole-footprint endpoint pockets,
each touching a legal lane edge, must be validated on one hash-bound board,
followed by native filled-reference and copper/DRC evidence.
