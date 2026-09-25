# Isolated TI unrouted board diagnostic — 2026-09-25 UTC

**Research only; no P1/P2/P3, routing, connector FULL, release, fabrication, or
order claim.** I copied the project source, dossiers, local footprint library,
private TI prototype circuit/netlist/schematic, and KiCad project/rule sidecars
under ignored `06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/`.
The KiCad `.kicad_pro`/`.kicad_dru` starting sidecars came from the prior
isolated `xtal-r2` candidate; `generate_rules_generic.py` then regenerated
both from the copied current source, and the TMUX POFV producer emitted its
eight exact B2 rules. The generator wrote its footprint table beside the
diagnostic board. No canonical generated file or board was overwritten.

From the repository root, the corrected producer command was:

```sh
OUT=$(realpath projects/crow-usb-carrier-v1/06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project)
/usr/bin/python3 skills/kicad-pcb/scripts/generate_board_generic.py \
  "$OUT/03_src/floorplan.yaml" \
  --netlist "$OUT/06_build/netlists/crow_carrier.net" \
  -o "$OUT/04_kicad/crow_carrier.kicad_pcb"
/usr/bin/python3 skills/kicad-pcb/scripts/generate_rules_generic.py "$OUT"
/usr/bin/python3 skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py \
  "$OUT/04_kicad/crow_carrier.kicad_pcb" \
  --assembly "$OUT/03_src/rules/assembly.yaml"
```

The exact copied source/input SHA-256 values were floorplan
`0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868`,
P1 requirements `191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3`,
route `f49ca740665ce4cfdceb1c82701ddae548f140c8ee1735746040c523c96c8608`,
nets `18033487a097b6d29abe3f9d8517879931cf80d278d8973adcf276010a5b7190`,
RF `833a8c022648859e65ba3b727bffd14c868214936a9751f12c5a15ecd3ea376c`,
private TI netlist `a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd`,
and circuit JSON `580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d`.
The saved diagnostic board SHA-256 is
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`;
regenerated `.kicad_pro` is `7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094`
and `.kicad_dru` is `00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a`.

The generator placed 569 footprints, passed its two source asserts, and found
zero inter-footprint pad overlaps or fixed-courtyard overlaps. The board has
TI `U_USB_ESD` in `Package_TO_SOT_SMD:Texas_DRT-3` at `(217.0, 36.0, 0°)`;
pads 1/2/3 carry `USB_DP`/`USB_DN`/`GND`. `count_parity.py` passed all three
569-reference comparisons; `pin_map_check.py` passed 799 physical pin
identities across 79 multi-pin references. Native netlist-to-board parity
found zero discrepancies over 282 connected nets and 1,641 connected nodes,
with 146 corresponding no-connects.

Independent pcbnew and receipt inspection confirmed those counts, pose, pad
identities and hashes. The copied diagnostic project has no
`03_tscircuit/manifest.yaml`, so the count-parity result alone does not prove
generator intent; the explicitly bound private circuit/netlist hashes and
board receipt identify this research subject. The board has 11 `J*`
footprints including bench-only `J_JTAG`; the ten normal-service edge
connectors below are J1–J8, J_PWR and J_USB.

The native command `kicad-cli pcb drc --severity-all --refill-zones
--schematic-parity --format json` found **zero violations, 499 unconnected
items, and zero schematic-parity issues**. Its JSON SHA-256 is
`bdc3f199f7f0418ac980ffe80b89c83250ca0fb90c617a14bddbe475914c2a55`.
The saved board has no signal tracks: its 14 track-collection objects are
generator-emitted GND vias. Its nine saved zones are unfilled, so the DRC's
in-memory refill does not prove a hash-bound filled return on the saved board.

The stricter `placement_gates.py --courtyard` returned FAIL with ten P-OUT
findings: J1–J8 and J_PWR courtyards meet the outline at 0.00 mm rather than
the 0.15-mm generic margin, and J_USB projects 0.50 mm beyond it. It reported
zero close/overlapping courtyard pairs or foreign-pad findings over 569
envelopes. The diagnostic receipt SHA-256 is
`8c4d44543f028ffd50249ac3d57971391e6a1e67e76f4bbb6fa13a1e89f1034f`.
The fixed connector edge and mating exception is not approved. The source P1
contract remains `INCOMPLETE` with null signal-allocation geometry and
unproved power/corridor/filled-return capacity; connector FULL retains 19
physical unknowns. This board is a reproducible unrouted subject for those
repairs, not an admitted P1 candidate or a path around the prototype-only
critical-selection release hold.
