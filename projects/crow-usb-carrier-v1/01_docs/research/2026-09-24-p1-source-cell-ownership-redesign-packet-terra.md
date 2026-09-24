# P1 source-cell ownership redesign packet

**Research only.** This packet does not edit the floorplan or a PCB, create a
coarse-contract receipt, dispatch a task, spend or reset an attempt, or accept
P1. `p1_accepted` remains false. It is the smallest source-governed input for
a future fresh, independently admitted one-attempt P1 candidate.

## Problem to resolve before contract promotion

The current schema-2 research candidate cannot become a canonical coarse
contract. Its physical witness boxes bridge source cells, and replacing those
with virtual witnesses fails while their reservations traverse other source
regions. The affected current regions are:

| Ownership conflict | Current regions | Consequence |
| --- | --- | --- |
| XU service / clock and flash | `xmos_core [185,72,232,128]`; `clock_flash_debug [185,112,232,136]` | 16-mm overlap. The proposed y=112 cut intersects full XU decoupler bounds and is rejected. |
| ADC / timing | `adc_reference [75,85,145,134]`; `audio_clock_tdm [140,72,190,112]` | 5-mm overlap. The proposed x=145 cut intersects ADC, IOVDD-decoupler, and channel-6 bounds and is rejected. |
| Analog / ADC interface | eight analog cells ending at y=84; ADC begins at y=85 | The 1-mm inter-cell gap measures 0/1 current raw F.Cu slots against the nine-net analog/VMID demand. |

The current raw screens also leave the ADC common strip at 2/3 slots, TDM west
at 3/4, and the seven-net control strip at 1/7. These are failures or
incomplete geometry, not permission to widen a witness across a source cell.

## Fixed authority retained

The redesign must retain the reviewed 27 `p1_fixed_refs` exactly: `J1` through
`J8`, `J_PWR`, `J_USB`, `J_JTAG`, and `C_HOLD1` through `C_HOLD16`. XU, USB,
ADC, clock/flash, PLL, local decoupling, and support components remain
P2-movable under a governed source revision; they cannot be silently promoted
to fixed obstacles or treated as free corridor area.

## Minimum source alternatives to evaluate

Choose one ownership model for each overlap; do not combine it with the
rejected straight cuts.

1. **Staggered disjoint cells.** Move one cell boundary around full component
   envelopes, leaving a non-overlapping inter-cell band wide enough for its
   declared signal demand. The source must name each resulting face and its
   reservation, while the P2 record retains pad-to-face/return obligations.
2. **Explicit shared zone.** Replace an overlap with one source-owned shared
   service zone, assigned a bounded net set and access owner. It must expose
   distinct exterior faces to adjacent cells; it cannot be an overlapping
   alias used to let a reservation cross unrelated cells.

Either alternative must separately allocate the distributed `AUDIO_EN` bus;
it cannot be folded into a nine-net analog strip without its own demand and
branch ownership.

## Reject the source candidate if any condition is true

- Any full native footprint body, pad, courtyard fallback, fixed connector,
  fixed hold bank, or native rule area intersects a proposed new boundary or
  reservation.
- A P2-movable witness lacks a short `virtual_block_face` on its own region
  face with the exact `P2_REQUIRED` pad-to-face obligation, or a fixed witness
  uses that virtual form.
- A reservation enters another source region, overlaps another allocation on
  the same layer, leaves the outline, or has raw capacity below its declared
  demand. Keep movable collisions as relocation debt, never capacity credit.
- The candidate omits P2 pad access, local supply/return, or a filled-reference
  follow-up; no raw-width result substitutes for those checks.

## Next measured step

Make a read-only source-floorplan variant for **one** alternative at a time,
then generate it only in a disposable isolated copy. Bind the floorplan,
netlist, requirements, interfaces, aliases, board, and tool digests. Measure
full-footprint/outline/rule-area intersections, each new face's region
exclusivity, per-reservation current and movable-debt slot counts, and the
explicit P2 pad-to-face/return obligation set. Reject the variant on any item
above; otherwise retain it as `INCOMPLETE` research for independent campaign
admission. Do not promote it to `p1_coarse_contract.json`, P1, P2, routing,
connector FULL, release, or order evidence.
