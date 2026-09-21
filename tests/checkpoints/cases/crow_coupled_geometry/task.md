# Repair the coupled MCH clock and ADC TDM neighborhood

Continue from this synthetic Crow-inspired routing checkpoint. The two routes
are each legal in isolation, but their current F.Cu polylines cross when they
are composed. The early `MCH_CLK` branch occupies the launch needed by the
later `ADC_TDM` terminal. This small coupon is not the historical Crow board
and does not prove that any larger placement is routable or impossible.

Edit only `03_src/route_geometry.yaml`. Co-design both complete trees so every
one of the three fixed pads on each net remains connected in a single combined
witness. Preserve the inherited seed segments. Both nets are frozen to F.Cu,
zero vias, 0.25 mm minimum width, and their exact current pad population. Do
not move or delete a pad, change `03_src/route.yaml`, relax
`03_src/rules/nets.yaml`, or treat an isolated-net result as success.

Regenerate the native prepared and witness boards from current source with:

```bash
/usr/bin/python3 build_native.py
```

Then use the trusted repository path in `.checkpoint_context/START.md` to run:

```bash
/usr/bin/python3 <trusted-repository>/skills/kicad-pcb/scripts/coupled_geometry_preflight.py grade . --prepared 06_build/coupled/prepared.kicad_pcb --witness 06_build/coupled/witness.kicad_pcb --workspace 06_build/coupled/gate/repair-1 --json 06_build/coupled/coupled-receipt.json
```

Use a fresh gate workspace. Record the source change and exact gate result in
`HANDOFF.md`. A passing receipt is only
a combined feasibility witness for this reduced neighborhood. It is not a
completed routing stage, full-board route, layout seal, or release claim.
