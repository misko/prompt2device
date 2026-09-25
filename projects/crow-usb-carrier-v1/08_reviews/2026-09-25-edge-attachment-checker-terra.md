# Independent review — edge-attachment physical-cell gate

Reviewed commit `b4fc652f` against the scope in
`01_docs/research/2026-09-25-ti-edge-connector-authority-sol/independent_review_terra.md`.

**PASS for the stated P1 physical-cell containment scope only.** The new path
runs inside `_physical_cells`; it requires the exact reviewed board SHA-256
`d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7`, a
single closed north-edge outline with the pinned outline digest, and one of the
explicit J_PWR/J1–J8 records. It independently hashes the selected footprint
library item and retained drawing, verifies the fixed pose and the maximum
0.045-mm F.CrtYd north projection, and permits only a one-reference physical
cell whose bbox is exactly the full native envelope. The normal inboard body,
pad, drill/slot and foreign-native/foreign-region checks remain active.

The actual cell path cannot use the declaration for J_USB, a non-north edge,
an unlisted connector, a missing cell, a multi-reference cell, a changed board,
outline, footprint, drawing or pose. The schema rejects extra status,
capacity, or connector-FULL fields. The exception is not passed to corridors,
reservations, capacity, routing, zones, DRC, connector FULL, release, or P1
acceptance logic. It therefore creates no P1/P2/P3, return, route, or
mechanical-release credit.

Focused test evidence:

- `python3 -m unittest skills.kicad-pcb.scripts.tests.test_p1_edge_attachment -v`: 3/3 pass.
- `python3 -m unittest discover -s skills/kicad-pcb/scripts/tests -p 'test_p1*.py' -q`: 171/171 pass.

The focused negatives cover J_USB, board/outline/footprint/drawing/pose hash
or identity drift, wrong edge, 0.046-mm declaration, nonfixed reference,
extra claims, offboard pads, oversized drill/slot, moved F.Fab shape, an extra
courtyard lobe, excess cell extent, absent cells and multi-reference cells.
The implementation also computes the actual courtyard projection, so an
actual footprint overhang change cannot be admitted merely by retaining the
0.045 declaration.

This is not an assembled-edge qualification. First-article finished-edge,
thickness, lot, solder-state and mating evidence remains required before any
connector mechanical conclusion or FULL status.
