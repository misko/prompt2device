# Repair the ADC source-launch branch

`geometry.json` is the only mutable source. It is a deliberately small,
synthetic reduction of the Crow carrier's ADC source-launch and branch-wall
constraint; it is not a copy of the historical board.

The initial F.Cu branch stops before an immutable vertical GND branch wall.
Extend or replace its polyline so `ADC_DOUT` connects the two fixed named pads
on F.Cu while going around that wall. The route must use no vias. Do not move
the pad endpoints: the grader checks their exact fixture coordinates
independently of board generation.

Run `python3 build_native.py` from the workspace to write
`native/adc_launch.kicad_pcb`, then run `kicad-cli pcb drc --severity-all
--output native/adc_launch.drc native/adc_launch.kicad_pcb` for an iteration result. `geometry.json` and
`HANDOFF.md` are the authored handoff inputs; the generated board and DRC
report under `native/` are also retained for review. The final grader checks
native pcbnew connectivity, invokes KiCad DRC, and rejects any via or non-F.Cu
route even if it connects the pads.
