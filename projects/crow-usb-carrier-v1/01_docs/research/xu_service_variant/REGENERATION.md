# Rectangle-only source regeneration

**INCOMPLETE research; no governed P1 run or acceptance.** The isolated trial at `/tmp/crow-xu-rect-regen-sol/project` copied the current Crow project inputs and changed only the two region rows in [floorplan_rectangles.patch](floorplan_rectangles.patch). It uses source commit `9c73181c432b51558003a8be7e496cc8c6757d5a` and the current netlist SHA-256 `e7ef7dbd752b9431ade0933ca77ee998963bfe3871c3caf65cddc56442f1371d`. The generator SHA-256 is `8a5fa1d48d80138458601a097ab6260565841510a498e44cb9c5773652215b3c` (native KiCad 10.0.4). The source floorplan changed from `a882f87682484c37c5766a9e37c5a0d93b38a8e5a775fb1ab4425011da40a275` to `01aa2aa9fa6b264510e568236a265fefb36494b275de081a99b62229c8be3de8`; [regeneration.json](regeneration.json) pins all other input and board hashes.

The generator completed: 569 footprints, 14 board-level vias/tracks, zero fixed courtyard overlaps, and a variant board SHA-256 of `c3b9d2885e1f475aad4744185eaa7258359a0d340e864e56418da5f61a0d3a6b`. Its exact-source baseline board is `60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17`. Native comparison covers every one of the 569 refdes poses and all 1,872 pads' ref/number/net/shape/size/layer identity. **Ten P2-movable footprints changed pose**: the eight `clock_flash_debug` parts (`C_FLASH`, `C_XTAL_IN`, `C_XTAL_OUT`, `R_QSPI_CS`, `R_XTAL_DRIVE`, `R_XTAL_FB`, `U_FLASH`, `Y_XU`) and `C_XU_USB18`/`C_XU_USB33`. The variant moved the clock group east/south and the two XU capacitors to new north-side sites. Pad identity, 27 P1-fixed poses, and all other footprint poses are unchanged; native positions of pads on the ten moved parts changed with them. All 37 assigned XU/clock footprint-plus-courtyard envelopes fit their new owner rectangles. The two rectangles have zero interior overlap with each other or any other source region, and the two earlier diagnostic windows hit no regenerated footprint envelope.

| Read-only check | Baseline | Rectangle variant | Interpretation |
| --- | --- | --- | --- |
| KiCad DRC `--severity-all --refill-zones --schematic-parity` | 225 clearance violations; 499 unconnected; 0 parity | same | Nonzero on both; no DRC acceptance. |
| `placement_gates.py --courtyard` | FAIL: 10 connector outline findings | same | J_USB courtyard extends 0.5 mm past outline; nine other connector courtyards have 0 mm margin. |
| `placement_routability_preflight.py grade` | `ACCEPTED` 8/8 local checks | same | This screen has no source-owned QSPI/JTAG corridor acceptance. |
| Zones/rule areas | one In1.Cu GND zone; zero native rule areas | same | Rule-area preservation cannot be tested from this board. |

The two touching rectangles and their cleared diagnostic face windows establish **geometry compatibility only**. They do not represent exclusive source-owned reservations. In the current schema-2 checker, `virtual_block_face` requires an exterior reservation and rejects overlap with either source region. A QSPI corridor would need a real non-overlapping `board_integration` region in a nonzero gap plus a handoff contract extension; the y=114 touching-edge variant has no such gap. The JTAG/reset path from its y=84 local face still crosses `usb_frontend` before fixed `J_JTAG`. Terra's schema recommendation is commit `c8db5559`. Both allocations and their P2 pad-to-face and filled-reference obligations remain incomplete. The ordinary preflight's `ACCEPTED` result is not a P1 verdict.

Reproduce in an isolated copy with the pinned current-source project and netlist, then run the compare. The paths below identify this exact trial:

```sh
cd /tmp/crow-xu-rect-regen-sol/project
/usr/bin/python3 /tmp/crow-xu-service-worktree/skills/kicad-pcb/scripts/generate_board_generic.py 03_src/floorplan.yaml -o 04_kicad/crow_carrier.kicad_pcb
cd /tmp/crow-xu-service-worktree
/usr/bin/python3 projects/crow-usb-carrier-v1/01_docs/research/xu_service_variant/compare_regenerated.py /tmp/crow-usb-regions-terra-HqnO4Z/project /tmp/crow-xu-rect-regen-sol/project > /tmp/crow-xu-regeneration.json
```

The compare script fails if any pinned source, netlist, generator, or board hash differs, and checks that the variant floorplan changed only the two region rows. The KiCad DRC and placement check commands above run read-only on both boards; their nonzero results are retained in this report. The generated board itself remains in the disposable copy and is not promoted.
