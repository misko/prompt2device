---
name: render-board
description: Render native PCB geometry from six cardinal directions and upper/lower 45-degree orbits, with connector close-ups and explicit model coverage. Use for local board inspection and connector-direction review; not fabrication or placement approval.
---

# Render a board, expose the evidence

Use an isolated output directory and the exact native board being reviewed.
Do not rotate footprints or move copper to make an attractive picture.

1. Identify board revision, population and connector references (including
   connectors on modules). Read existing mechanical evidence before reusing it.
2. Run `scripts/render_board.py` with the native `.kicad_pcb` and a board-owned
   inspection JSON. The helper uses KiCad for native outline/holes/footprints,
   and the existing vNext CadQuery/VTK runtime for PNGs. See
   [inputs](references/inputs.md) only when preparing that JSON.
3. Inspect top, bottom, all four edges, and eight azimuths at each of +45/-45
   elevation. Use labeled isolated close-ups when the full board hides pins or
   mouths. `gallery.html` and `overview.png` index the renders.
4. Verify actual numbered pads and locator holes against manufacturer facts,
   then transform the part's documented mouth direction into board coordinates.
   Compare it to the independently stated intended direction. A direction arrow
   or a cavity we drew is not independent proof. Check model coverage and every
   failed/unknown connector result, not just successful renders.
5. Report direction, registration and access separately. Local rendering cannot
   prove a vendor's zero-angle convention, finished-hole fit, insertion clearance,
   hidden contacts, thermal assembly acceptance or full production readiness.
   Keep existing holds open and return concrete mismatches to their owning stage.

The helper deliberately uses labeled drawing-derived inspection solids where
exact CAD is unavailable; non-reviewed components are visible footprint envelopes
with explicitly unknown height. It does not pretend these are manufacturer CAD.
For registered STEP/clearance acceptance use the PCB skill's
[mechanical procedure](../pcb-design/procedures/mechanical/3d-verification.md).
Keep board-specific dimensions and conclusions in the project, never this skill.

```sh
CAD_PYTHON scripts/render_board.py --board /absolute/board.kicad_pcb \
  --inspection /absolute/inspection.json --output /absolute/new-render-folder \
  --kicad-python /path/to/python-with-pcbnew
```

`CAD_PYTHON` means an interpreter with `vnext/tools/mechanical-requirements.txt`
and Pillow available; it is not a literal command. `--verify OUTPUT` checks
source/config hashes and output membership without rendering again. Diagnostics
never issue stage acceptance. Failures remain visible even when PNG generation
succeeds. No vendor actions are part of this skill.
