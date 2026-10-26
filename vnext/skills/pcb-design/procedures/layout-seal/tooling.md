# Layout seal — native finishing adapter

Use `/usr/bin/python3 tools/layout_seal.py` with `build`, `verify`, `issue`,
`check`. Options follow routing: `--project ABS`, `--manifest REL --output NEW_REL`
for build/verify; `--review REL` for issue. New outputs/receipts refuse overwrite.
The adapter is a finishing/replay verifier, not an automatic finisher or solver.

`01_docs/layout-seal-contract.json` version1 binds `authority`, its SHA256,
`routing_receipt_sha256`, and a nonempty `obligations` list. Each obligation has
unique `id`, `requirement` and project-relative `source` authority. Inspect the
accepted review to carry forward all obligations, not merely easy ones. Each
operation reruns the owning routing check; unsupported RF execution is not
implicitly admitted by a graph edge.

New acceptance uses contract version2. The manifest additionally requires
`schematics`, mapping every board key to its exact accepted native schematic.
The adapter resolves those paths from the upstream-checked schematic contract
and imported flat producer declarations; aliases or omitted boards fail closed.
Other producers require an explicit adapter extension. Version1 remains a
historical replay path, not new acceptance. Preserve old bindings before adoption.

Manifest version1: `boards` has exactly the accepted routing board keys. Each
entry contains native `source`, `project`, and `resources` (destination-relative
path → project-relative input). Resources support local `fp-lib-table` plus
`.pretty/*.kicad_mod` files. Library URIs must use `${KIPRJMOD}/...`, never global
configuration or external absolute paths. Every native footprint must have its
named module bound through that local table. Unnamed board-only NPTH mechanical
holes need no external lookup and remain protected by exact physical comparison.
Library files must use footprint-library syntax: a board-only root `at` field
is rejected even when KiCad accepts it during parsing and the current DRC passes.
See the [native format](https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html#footprint).
Optional `evidence` binds other files.
`closure` maps every contract obligation ID to `status` (`open`, `closed`,
`not_applicable`), `rationale`, and `evidence` paths. Closed/not-applicable claims
need evidence and independent disposition; the author flag alone is not proof.

The physical comparator ignores only specified non-copper text/graphic
presentation, preserving Reference/Value strings. It preserves all other native
authored tokens (without load/save auto-repair). Settings must exactly equal the
accepted routing settings; no custom rules or DRC exclusions. A rejected
engineering delta requires upstream reacceptance and explicit re-adoption,
never a changed digest in an old review. The pilot does not yet accept a changed
stack through a special migration path; surface this limitation explicitly.

Build copies resources into isolated board directories, enables all declared
DRC checks, refills zones, saves boards and exports F/B copper, silk and Fab SVGs.
The output is `OUTPUT/BOARD/native/BOARD.kicad_pcb` with corresponding settings,
DRC and layer views; `checks.json` records every board. Verify rebuilds from
source and compares native/settings/library/report/SVG outputs exactly, ignoring
only native top-level ordering and report/plot timestamps as in routing. Partial
build/replay success is not seal acceptance. No cosmetic DRC waivers are allowed.
Version2 copies the selected native schematic beside each board and actually runs
`--schematic-parity`; `drc-execution.json` binds the command and source hashes.
Replay compares these artifacts too. The command may return a report containing
findings; only strict zero-finding grading plus independent review permits issue.

Independent dated `08_reviews/*.md` has one JSON block: schema1,
stage `KICAD-LAYOUT-SEAL`, distinct `author`/`reviewer`, verdictPASS, manifest,
output, exact `subjects`, and `checks` for identity, physical, markings,
engineering, reproducibility. Each criterion has verdictPASS, rationale and
bound evidence. `obligations` independently dispositions every contract ID with
the same verdict/rationale/evidence fields, including non-applicability. Bind all
subjects returned by verify and substantive engineering/visual sources. Each
obligation review must cite all of its claimed closure evidence; the markings
review must cite both sides' SilkS/Fab views for every board. These checks bind
what was reviewed, not whether the engineering reasoning is correct.

Coordinator alone issues `06_build/checkpoints/layout_sealed.json` after strict
zero-finding DRC, closed obligations, exact replay and independent PASS. `check`
replays the full chain. The receipt binds tool, stage, manual and exact subjects.
Freeze those inputs; later process changes need explicit versioned adoption.

For progress, run `tools/workflow.py --project ABS`. Its table separates local
capability, STATUS-reported current stage and receipt presence. Add
`--verify-acceptance` to rerun supported owning checks; receipt presence alone
never counts as acceptance. This viewer does not dispatch or backtrack work.
