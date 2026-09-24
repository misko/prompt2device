# Schema-2 integration corridor probe

**Disposition: INCOMPLETE research.** The generic P1 coarse checker now has a
separate `integration_corridors` source declaration. It binds one empty,
non-overlapping `board_integration` floorplan region to two participant cells,
their positive-length shared handoff faces, one exact source demand and its
native ref.pad/net endpoints. A matching `integration_corridor` reservation
gets no rough slot count. It remains `INCOMPLETE` with explicit P2 pad-to-face
and GND filled-reference obligations, even when every geometry check succeeds.

The test fixture `CoarseCapacityTest.add_integration_corridor` uses six
`QSPI_*` nets, twelve native source pads and two adjacent virtual faces. It
demonstrates `INCOMPLETE`, and rejects missing return/endpoint declarations,
partial demand, corner contact, wrong ownership, native footprint intrusion,
duplicate reservation/net credit and an attempted `PASS` declaration. Run:

```sh
python3 -m unittest skills/kicad-pcb/scripts/tests/test_p1_coarse_capacity.py
```

The fixture is synthetic and **does not** assert a Crow P1 contract. Its shape
is based on the gap variant measured in `qspi_gap.json`: source floorplan
SHA-256 `cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925`,
generated board SHA-256
`fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.
That board has `board_integration_qspi [199.8,110.5,223.2,118.5]` mm between
`xmos_core` and `clock_flash_debug`; the measured x=200–205 mm face is 5.00 mm
wide against 2.70 mm raw demand. The checked-in canonical Crow source and P1
contract contain no corridor declaration. No native pad-to-face route,
effective capacity, filled return continuity, JTAG continuation or P1
acceptance follows from this geometry.
