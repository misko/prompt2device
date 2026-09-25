# P1 physical-cell checker review — 2026-09-24

Review scope was the optional schema-2 `physical_cells` extension in
`skills/kicad-pcb/scripts/p1_corridor_capacity.py`, against commit
`291ebf80`. No board, P1 source requirement, floorplan, modular-plan, route,
or acceptance state was changed.

The checker fails closed on native footprint body/courtyard and pad containment
in the named cell, rejects foreign native occupancy, requires exact-once
modular-ref assignment for each owner that adopts cells, rejects positive-area
cell/foreign-region overlap, and requires every transit cell to edge-connect
through its same-owner cell group. It retains the legacy path when the optional
source key is absent. Corridor faces and handoff witnesses require an
owner-matching cell ID when their modular owner uses cells, while endpoint
`block` remains the modular owner.

One attribution gap was found in `fixed_connector_access` and
`fixed_connector_access_segmented`: their P2 pad-to-corridor obligation did
not repeat the physical-cell identity. Commit `f351a9a2af1153f10dbe6027d1132a6c5f8f8516`
requires that field only for cell-scoped witnesses and adds a fixture that
accepts the complete INCOMPLETE debt record and rejects the same record with
the field removed. The focused P1 suites ran 94 tests successfully.

## G-ORPHAN governance finding

`03_src/rules/p1_corridor_requirements.yaml` has no
`### keys: 03_src/rules/p1_corridor_requirements.yaml` declaration in
`skills/pcb-design/templates/contracts`, or in the Crow USB carrier's rendered
rules contract. `schema_reader_audit.py --root .` consequently lists it as an
**UNGOVERNED** family. The file already has a broad schema: top-level P1
metadata; allocations, endpoint ownership and demands; power-boundary native
pad evidence; and optional source-owned transition/corridor/branch records.
Adding only `physical_cells` and `physical_cell_id` rows would turn every
pre-existing key in that file into a G-ORPHAN finding. This review deliberately
does not fabricate a partial declaration or claim governance for the new keys.

Before a physical-cell source record is admitted, add a complete family table
that attributes every observed key to its real reader (or a justified
`ADVISORY`/`OWED` state), raise the ratchet as required, and rerun G-ORPHAN.
The present P1 source remains INCOMPLETE and this note is not P1 evidence.
