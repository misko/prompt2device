# Source population component — not fabrication acceptance

Use only when preparing population evidence for the fabrication stage. This
component accounts for parts and their native coordinates, with optional explicit
vendor mapping. It is not an assembly planner, stock checker or stage receipt owner.

```
/usr/bin/python3 tools/fab_population.py build --project ABS --manifest REL --output NEW_REL
/usr/bin/python3 tools/fab_population.py verify --project ABS --manifest REL --output REL
```

Both commands rerun the current layout-seal acceptance and bind each board to
its accepted native output and schematic intent. A missing seal cannot be
bypassed by supplying an arbitrary board. The coordinator still owns phase-resume
authority. Internal functions exist
for isolated component tests, which never produce stage acceptance.

Manifest: version1, nonempty `boards` mapping. Each entry has `source`, `intent`,
positive integer `quantity` (number of this board to build), and `population`.
Every native reference occurs exactly once in population, with `mode` equal to
factory, consigned, manual, dnp or mechanical; nonempty `reason` and `evidence`
list of retained project-relative files. The reviewer owns the policy, not the
exporter. Manual/consigned treatment must retain actual instructions and
inspection requirements in that evidence. DNP requires engineering justification;
a syntactically complete policy does not make an exclusion acceptable.

Every physical intent part must have matching native value, footprint,
Manufacturer, MPN and Assembly fields. It cannot be called mechanical. Other
intent fields, including any supplier code, are retained and checked; native
DNP flags cannot contradict a populated policy. Native BOM/position exclusion
flags remain visible, not automatically translated into a population decision.
Factory population rejects either native exclusion flag; consigned population
requires native position inclusion. Manual placement may retain exclusions,
with explicit policy evidence. All-DNP policies retain complete reference coverage
and generate header-only demand/positions files, not a missing-board success.
Additional mechanical items currently support only unnamed, netless NPTH footprints;
other models need explicit implementation/review rather than inferred exclusion.

Outputs are `population.csv` (per-reference identity and disposition),
`demand.csv` (whole-system manufacturer/MPN quantities, excluding DNP/mechanical),
`positions.csv` (populated refs only), and a hashed source/evidence record.
Positions are **KiCad absolute footprint anchors, +Y down, native angles**—not
part centroids or vendor-ready CPL. No vendor rotation or supplier code is
invented. Final vendor identity mapping, quantity-aware stock checks, process
policy, standalone package replay and assembly review are still required.

Build refuses existing output and publishes only a complete component result.
Verify regenerates every byte and rejects stale, missing, extra or linked files.
Public exports also bind the exact layout receipt, input manifest and component
tool/manual identities; replay cannot silently renew that context.
Every output record is explicitly unaccepted and DO-NOT-ORDER. No operation here
issues `fabrication_staged`, uploads files, contacts a vendor or orders a board.

## Optional JLC assembly translation

The same manifest may include `assembly: {version: 1, boards: {...}}`. Every
board must occur, with `source_sha256` of its exact native PCB and `placements`
keyed by precisely its factory/consigned references. Manual, DNP and mechanical
references remain accounted in population.csv but never enter a machine CPL.
Empty factory/consigned sets produce header-only files, not omitted boards.

Each placement contains exact `manufacturer`, `mpn`, `footprint`, `supplier_code`,
`centroid_offset_mm: [dx,dy]`, `rotation_deg` and a nonempty `evidence` list of
retained project-relative files. A factory part requires a full C-number;
consigned parts may have an explicitly empty code. Native supplier-code fields,
when present, must agree, including malformed nonempty values in explicit
LCSC/JLCPCB code fields. The ambiguous `Supplier` field is treated as a code only
when it contains a full C-number. A code cannot identify different manufacturer/MPNs.
The files must support identity and centroid/orientation decisions; their presence
is not proof of truth or an independent approval. Do not fill a real mapping with
zero offsets/native angles merely to get an export. Actual manufacturer geometry
and vendor orientation evidence are still reviewed by assembly verification.

Offsets are in **native board axes (+Y down)** from the footprint anchor, bound
to this exact PCB, not reusable footprint-local offsets. Final vendor rotation
is explicit in [0,360), counterclockwise. No bottom-angle rule or mirroring is
inferred. CPL coordinates use the absolute origin, +X right/+Y up, matching the
native plot component's absolute Gerber/drill datum. A different plot datum needs
a coordinated implementation, not manual translation of only the CPL.

The exporter creates `BOARD-factory-bom.csv`, `BOARD-factory-cpl.csv` and separate
`BOARD-consigned-{bom,cpl}.csv`. Consigned files are a handling manifest, not proof
that a supplier accepted consignment. BOM rows group exact identity/value/package/
code; quantities and CPL describe **one board**, while demand.csv still accounts
for all board quantities and manual parts. Native positions.csv remains native.
The record binds mapping and retained evidence; verify regenerates all outputs.
Vendor matching/orientation preview, allocation, process confirmation and
independent assembly acceptance remain visible holds, not inferred passes.

Format authority checked 2026-10-06: [JLCPCB KiCad export guide](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)
and [CPL specification](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly).
