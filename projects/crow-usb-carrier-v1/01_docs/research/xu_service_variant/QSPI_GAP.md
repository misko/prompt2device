# Source-declared QSPI gap probe

**INCOMPLETE research; no P1 capacity or acceptance.** In the isolated copy `/tmp/crow-xu-qspi-gap-sol/project`, the preceding rectangle variant (`03_src/floorplan.yaml` SHA-256 `01aa2aa9fa6b264510e568236a265fefb36494b275de081a99b62229c8be3de8`, board `c3b9d2885e1f475aad4744185eaa7258359a0d340e864e56418da5f61a0d3a6b`) was changed only by [floorplan_qspi_gap.patch](floorplan_qspi_gap.patch): `xmos_core [190,84,232,110.5]`, `clock_flash_debug [190,118.5,232,136]`, and a new, non-overlapping `board_integration_qspi [199.8,110.5,223.2,118.5]` mm. The floorplan SHA-256 is `cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925`. The same pinned netlist and KiCad 10.0.4 generator produced board SHA-256 `fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27`.

The three source rectangles fit the outline and have zero interior overlap with each other or foreign source regions. The generator accepted the new empty region and completed a 569-footprint board. All 37 assigned XU/clock footprint-plus-F.CrtYd envelopes remain in their respective owner cells. The corridor and its old diagnostic window `[200,111.9,205,117.9]` contain no native footprint envelope or pad. On the regenerated board, nearest assigned envelope clearance to the corridor is 0.615 mm on the XU side and 2.805 mm on the clock side. The selected QSPI south face x=200–205 at y=110.5 offers **5.00 mm raw vacant F.Cu span** against the declared 2.70 mm demand. This is geometric space only; no six-net pad escape, trace clearance, trunk capacity, or return continuity has been modeled.

Against the preceding rectangle board, all 569 footprint references and all 1,872 pad identities remain stable, and all 27 P1-fixed poses remain unchanged. Ten P2-movable footprints shift: the same eight clock/flash parts move south, while `C_XU_USB18` and `C_XU_USB33` move again. Their changed poses and pads are in [qspi_gap.json](qspi_gap.json). This relocation is **P2 debt**, not corridor credit. Native DRC remains 225 clearance violations, 499 unconnected items and zero schematic parity issues; strict courtyard placement gates retain the same ten connector-outline failures. Both boards have one In1.Cu GND zone and zero native rule areas, so preservation under a future rule area cannot be graded.

The new `placement.regions` row is **source-declared geometry only**. The generator does not emit it as a copper/rule-area reservation, and no P1 schema-2 allocation or handoff binds QSPI endpoints, F.Cu capacity, P2 pad-to-face obligations or filled-reference return to it. Terra's schema recommendation (`c8db5559`) calls for an explicit `board_integration` corridor and handoff contract extension; this probe supplies the gap geometry but does not implement that contract. JTAG/reset remains outside this probe and its north continuation still crosses `usb_frontend`. No governed P1 task was dispatched, no canonical floorplan was changed, and no route/placement was accepted.

Reproduce from the two pinned isolated copies:

```sh
cd /tmp/crow-xu-qspi-gap-sol/project
/usr/bin/python3 /tmp/crow-xu-service-worktree/skills/kicad-pcb/scripts/generate_board_generic.py 03_src/floorplan.yaml -o 04_kicad/crow_carrier.kicad_pcb
cd /tmp/crow-xu-service-worktree
python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/verify_qspi_gap.py
```

The verifier checks the committed JSON against both exact board/source hashes, the unchanged netlist and generator, every native pose/pad identity, fixed poses, region intersections, assigned courtyard envelopes and raw face width. To recreate the gap source from the canonical pinned source, apply `floorplan_rectangles.patch` first, then `floorplan_qspi_gap.patch` in an isolated copy.
