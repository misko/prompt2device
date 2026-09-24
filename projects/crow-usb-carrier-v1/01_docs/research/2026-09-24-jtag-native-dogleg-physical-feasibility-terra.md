# Native JTAG dogleg physical-feasibility probe

**Disposition: geometry PASS, research only.** On the native QSPI-gap board
SHA-256 `fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`,
the four fixed `J_JTAG` signals can be represented by simultaneous F.Cu
Manhattan doglegs at 0.15-mm width and 0.15-mm clearance to foreign native
pads, front footprint bodies, front courtyards, existing F.Cu, and F.Cu rule
areas. Consequently, the earlier failure of four *rectangular reservations*
is a checker-representation failure; it is not a proof that the fixed
90-degree connector pose is physically unroutable.

The reproducer, [jtag_native_dogleg_probe_terra.py](jtag_native_dogleg_probe_terra.py),
pins the input hash and records its native-object screen in
[jtag_native_dogleg_probe_terra.json](jtag_native_dogleg_probe_terra.json).
It buffers each trace centreline by 0.075 mm and every screened obstacle by
0.15 mm; any strict-positive-area overlap fails. It also checks trace-to-trace
clearance across all four nets.

At the unchanged 90-degree pose, TMS exits east. TDI, TDO, and TCK traverse
the 1.28-mm inter-row opening at y=49.60, 49.90, and 50.20 mm respectively,
then use two exits to each side of the header before reaching the source-owned
strip `[221,65,226,84]` mm. The three 0.15-mm tracks at 0.15-mm clearance
consume 1.05 mm of that 1.28-mm raw opening. The exact coordinate witnesses
are in the JSON. This is a positive feasibility witness, not a preferred
production route.

The requested fixed-pose backtrack is also geometrically viable: rotate
`J_JTAG` 180 degrees at `(228,50)` mm (90 to 270 degrees) and expand the
source-owned JTAG strip to `[221,65,231,84]` mm. A virtual transformation of
the native pad geometry puts pads 2/4/6/8 on the south row at x extents
`225.09..225.83`, `226.36..227.10`, `227.63..228.37`, and `228.90..229.64`
mm. Four direct vertical traces from their lower pad edges to y=65 pass the
same native clearance screen and are mutually clear. It is a **P1-fixed pose
and source-region backtrack**; no PCB has been altered here.

The `J_JTAG` courtyard needs a stated escape semantic. Every source pad lies
inside its own courtyard, so a literal no-courtyard-crossing rule would make
any F.Cu escape impossible. This screen excludes that origin courtyard only;
it checks all foreign courtyards. It does not waive pad clearance: every other
pad of `J_JTAG`, including the keyed/ground/reset contacts, remains a foreign
copper obstacle.

Neither witness proves connector mating clearance, DRC closure, a filled
In1.Cu reference/return, impedance, source ownership, endpoint fanout,
simultaneous reset routing, P2 work, or P1 acceptance. It establishes only
that neither the current fixed geometry nor the rotated-plus-widened-region
candidate has an exact native F.Cu geometry blockage at the requested trace
class. Reproduce from the repository root with KiCad 10:

```sh
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/jtag_native_dogleg_probe_terra.py
```
