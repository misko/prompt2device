# Crow prototype-only source/schematic producer

`03_src/rebuild_prototype_only.sh` is a bounded design-continuation producer
for a critical selection that the shared admission checker has classified as
`prototype_only`. It calls that checker with its explicit `--require-prototype`
exception, which rejects `PASS`, `NOT_APPLICABLE`, and incomplete selections,
then produces a private circuit JSON, KiCad schematic, native
netlist, readable schematic PDF, and hash receipt beneath
`06_build/prototype_only/<UTC-stamp>-<pid>/`.

The producer first creates a temporary copy of `03_tscircuit/src` and builds
there. It therefore does not overwrite the canonical generated circuit,
schematic, native KiCad directory, board, route material, release material, or
stock receipt. It uses the existing frozen local `node_modules` tree; it does
not install dependencies or query a supplier.

The generic critical-selection manifest is the only authority for this path.
Its `suitability.status: prototype_only` must be backed by separately named
decision owner and reviewer, hash-bound evidence, and one or more open
deferred findings that block at `DESIGN_CLEAN`. Findings tagged
`due_at_selection_findings` remain ordinary selection findings and must be
closed; they cannot be deferred by this producer.

This script deliberately has no call to the ordinary full/reuse conductors,
PCB generation, routing, layout acceptance, release sealing/publication,
fabrication export, or ordering. Its receipt states `PROTOTYPE_ONLY`, and is
not evidence of electrical qualification or release readiness. The separate
[TI USB ESD prototype test plan](2026-09-25-ti-usb-esd-prototype-test-plan.md)
defines the evidence still needed before ordinary selection or release may be
considered.

Run the focused regression with:

```bash
/usr/bin/python3 03_src/tests/test_rebuild_prototype_only.py
```
