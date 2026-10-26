# Adopt a source-owned flat KiCad draft

Use this optional producer adapter when a reviewed exploration draft already
has a reproducible local Python generator. Preserve that generator and drawing;
do not redraw the circuit to satisfy the built-in renderer's layout grammar.
This is not a direct-native-edit or hierarchical/RF acceptance route.

The project explicitly adopts schematic-contract version 2 with `producers`
listing `imported` (and `native` only if also used). Other fields remain
`manifest`, `expected`, `rf: false`. Version 1 still permits only the original
native builder. Upstream sourcing review must cover the chosen contract; neither
an imported artifact nor its provenance receipt can supply a missing prerequisite.

Each imported board in the existing assembly manifest names `producer: imported`,
`source` (import declaration), `membership` and `output`. Harness/instance schemas
and independent full-design expectations are unchanged, except imported component
membership additionally declares `physical`. A nonphysical schematic flag has
no footprint and must be excluded from both board and BOM in native export.
Do not mark real components virtual merely to avoid exact sourcing.

`tools/native_import.py` documents the small declaration and electrical-intent
schemas. Declare the trusted local Python entrypoint, every input, produced
intent/native paths, and project/library context. Compile intent from the same
circuit source that generates KiCad—not from its netlist or a second handwritten
drawing. Include complete pins, names/types, net/NC, values, footprints and custom
ordering fields. Production membership must come from reviewed architecture and
part evidence; a test projection of generated intent is not that evidence.

Run `python3 tools/native_import.py ROOT build DECLARATION OUTPUT` into a new,
empty output directory. Then run `verify` with `--membership MEMBERSHIP` and the
existing `tools/schematic_assembly.py ROOT MANIFEST EXPECTED`. Build replays the
producer in a temporary copy of its declared inputs, compares native/intent and
context bytes, and reexports native XML/PDF/all-severity ERC. Verification repeats
this and rejects stale sources/libraries/receipts, changed pin functions/types or
ordering fields, wrong PDFs, changed ERC report content (apart from timestamps),
ERC errors, missing membership and harness changes. Receipt and membership paths
must remain inside the project, including after resolving symlinks.
Only tool-generated provenance is written; no stage is promoted.

The replay executes trusted project Python with a 120-second subprocess timeout.
A temporary directory is not an OS security sandbox; review code before executing
an unfamiliar producer. Record external runtime dependencies. KiCad remains pinned
by the native toolchain. Nonempty project ERC customizations, hierarchy and unknown
producer/schema values fail closed; migrate these capabilities rather than waive
them. Native labels and page size are allowed when parity and actual readability
review support them; the built-in generator's wire-layout grammar is not imposed.

Final admission still uses `schematic_admission.py`, all six independent review
criteria and current upstream receipts. Review every producer input, compiled
intent, local library, native file, export, membership and harness on exact hashes.
Inspect actual PDFs and critical geometry; producer replay does not prove correct
engineering, datasheet interpretation, completeness or manufacturability. Tests
cover mechanical behavior and corruption controls, not a board acceptance verdict.
