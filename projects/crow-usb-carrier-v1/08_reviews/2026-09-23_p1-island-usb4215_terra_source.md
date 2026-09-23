# USB4215 conditional island-anchor review

**Disposition: acceptable only as a conditional source proposal.** The reviewed
diff is SHA-256
`d5483fce45d4e98cd18357782c7dbe1b3dc0301e6fb75c5b0d8a486da5784575`;
`git apply --check` passes against the stated floorplan base
`62be425f350d8d0c9bd33834f99d3d1827e5f190480e4bb75ad95a70830e53af`.
The supporting report is SHA-256
`a5bd632966b93d4145b327848edb55b958dd2d5da82af8f50ac553732c7c57e4`.

The transform arithmetic is correct for the USB4215 source at commit
`3cd02b44940eb9aca8879d56f47796f7d4365cfa`. Its footprint hash matches the
reported `64d46bb6685897b550f76af541711d607a9b51b4ddc0c6421cab608ef9c6cb80`.
With a 180-degree placement, board y is `22.995 - local_y`. Therefore:

- local mouth/front marker y=+2.995 maps to y=20.000, the board top datum;
- F.Fab y=-3.505..+2.995 maps to y=20.000..26.500;
- F.CrtYd y=-4.760..+3.500 maps to y=19.495..27.755, a deliberate
  0.505 mm overhang;
- the nearest lower shell copper and drilled slot map to y=21.000 and
  y=21.200, respectively, giving nominal 1.000 mm copper-edge and 1.200 mm
  hole-edge distances.

Those nominal distances exceed the source 0.300 mm copper-edge floor. They do
not prove manufactured edge registration, plated-slot/process tolerance, shell
seating, mating-plane location, cable access, or assembly clearance. The
courtyard overhang is real and must remain a native placement/assembly finding,
not a waived clearance result.

The anchor at y=22.995 is outside all three capacitor-bank forbid rectangles
(y=113..137), so it does not weaken their floating-part reservation. The 16
hold and other connector anchors are otherwise unchanged.

This patch must not be applied alone to the current root: that would move the
old USB4105 footprint to a coordinate derived for USB4215. Adopt it atomically
with the reviewed USB4215 source/footprint, pin-alias mapping, parts and
connector-contract changes. It is not a P1 admission, board generation result,
or CONNECTOR-FULL/mating qualification. The marker itself is only a
drawing-derived mouth hypothesis; exact registration and physical service
evidence remain required.

