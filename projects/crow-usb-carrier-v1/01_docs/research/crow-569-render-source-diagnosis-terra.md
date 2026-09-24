# Crow 569 schematic detail renderer — source diagnosis

**Scope.** Read-only diagnosis of the defective review packet
`/tmp/crow-569-schematic-review-render-terra-r1.md`, whose immutable SHA-256 is
`a0cac14bcdb959cfd19b38caa590bd54bb9051415c2e2679320d51fe0cbf81d9`.
No project file was edited, no PDF was regenerated, and no producer was run.

## Result

The defect is in the human-owned detail-page renderer, not in the circuit,
netlist, or PDF merger.  The currently enabled Crow driver requests fixed
rectangular grids at
`projects/crow-usb-carrier-v1/03_src/rebuild_all.sh:209-218`; the shared
renderer unconditionally emits all requested cells at
`skills/kicad-pcb/scripts/render_schematic_pdf.mjs:606-645`.

For a grid `g`, the code uses:

```
window = extent / (g - (g - 1) * 0.15)
stride = (extent - window) / (g - 1)
```

This gives 15% overlap and full *rectangular extent* coverage (for 3x3,
window = 0.37037 extent and stride = 0.31481 extent), but it never asks whether
a cell contains a symbol, text, wire, or a complete reviewable circuit region.
It then clones the full rendered SVG and changes only its `viewBox`
(`:619-625`), so every grid coordinate becomes a PDF page (`:626-643`).  There
is no empty-cell filter, no component/text bounding-box calculation, no
whole-symbol containment rule, no trace/label continuity metadata, and no
post-render page-content check.

That is sufficient to explain the frozen review's page 50: it is RESET
SUPERVISORS DETAIL 7/9 (R3C1), source sheet 25, whose crop contains only the
header.  The currently present 92-page PDF independently confirms that page 50
has no body text; adjacent pages 47--52 show only fragments.  The same blind
lattice mechanism accounts for the reported blank/sparse cells and edge cuts
on held-LDO, ADC, XMOS, TDM, FSYNC, and clock-control details.  It is not a
coordinate-transform or duplicate-`viewBox` fault: the root attributes are
replaced correctly in `:620-625`, and the old/new page-50 observation persists.

The current `totalPages` computation (`:503-504`) also counts every requested
cell before any content decision, making page numbering internally consistent
but reinforcing the wrong document contract: `grid * grid` pages are promised,
rather than one or more usable detail regions.

## Source ownership and electrical boundary

The repair owner is the shared renderer
`skills/kicad-pcb/scripts/render_schematic_pdf.mjs`, with the Crow opt-in
arguments in `projects/crow-usb-carrier-v1/03_src/rebuild_all.sh`.  The focused
test owner is `tests/t1_schematic_render.py` (present tile tests at `:72-110`).

The rendering path reads `circuit.json`, creates `canonicalDisplayCircuit` as
a shallow display copy (`render_schematic_pdf.mjs:297-345`), derives an SVG
(`:549-577`), and hashes the unchanged input (`:488-491`).  The Crow driver
renders the already-produced `$CJ` before native schematic/netlist conversion
(`rebuild_all.sh:205-234`).  Thus a renderer/driver/test-only repair can leave
the Circuit JSON bytes, native schematic, netlist, parts, and electrical source
unchanged.  Do not edit TSX electrical modules, rules, circuit JSON, KiCad
schematic, or generated PDFs for this repair.

## Prior claims and why they do not accept this output

The initial source audit
`projects/crow-usb-carrier-v1/08_reviews/2026-09-23_detail-tiles_terra_source.md:7-14`
correctly verified SVG serialization, overlap/end-to-end extent coverage,
numbering, option validation, and atomic publication.  It did **not** claim a
visual review or check tile content.  The existing fixture test likewise proves
only a five-page count, immutable input bytes, header captions, and that `U1`
and `U2` occur somewhere in the combined detail text
(`tests/t1_schematic_render.py:72-110`).  It cannot detect an empty third cell
or a component/label cut at a tile boundary.

The earlier independent 78-page review already identified the same limitation:
blank/sparse tiles were treated as inefficient only, while clipped/overprinted
references made the render DEFECTIVE
(`projects/crow-usb-carrier-v1/08_reviews/2026-09-23_schematic-detail-review_sol_source.md:20-42`).
The newer immutable 92-page review is stronger evidence: it inspected all 92
pages and finds a blank page 50 plus broad crop/continuity failures.  Therefore
the older source-audit statements and any later hash-bound SOUND/carryover claim
are not acceptance evidence for this 92-page PDF.  Keep the failed review
immutable; do not overwrite or repin it.

## Smallest safe repair

A change that merely reduces grid size, increases overlap, or omits cells with
no extracted text is insufficient.  It may hide page 50 while still bisecting
symbols/nets, and an SVG path-only region can be meaningful even without text.
There is no universal fixed `2x2`/`3x3` tiling parameter that can promise both
no empty pages and whole readable circuit regions for sparse, asymmetric sheets.

Replace the generic Crow `--detail-tiles sheet:grid` declarations with
**explicit, content-aware detail regions** owned by the renderer/driver.  The
smallest safe implementation is:

1. Add a detail-region option/data structure in
   `render_schematic_pdf.mjs` beside parsing at `:250-286`.  Each requested
   region is a named source-sheet view window; retain the current SVG-crop
   rendering approach, since it scales symbols, wires, label plates, and text
   together and does not alter Circuit JSON.
2. Before emitting a region in the loop at `:606-645`, validate it against the
   rendered schematic content: it must contain authored body material and each
   selected component's complete rendered bounding box plus a fixed padding.
   Derive bounds from the rendered SVG/component groups (not PDF text and not
   only `schematic_component.center/size`), so symbol pins, reference/value
   text, net-label plates, and graphical bodies share the coordinate system.
3. Build regions from component-connected local groups (component body plus its
   attached ports/text and incident trace/label material).  Merge overlapping
   padded groups.  A region may contain several groups, but must not cut a
   selected group.  If an inter-region net must cross a boundary, render a
   deterministic continuation annotation naming the other detail page and the
   net; otherwise merge the groups.  Reject a requested region with no body
   content or an unresolvable boundary before final PDF publication.
4. Update the Crow driver at `rebuild_all.sh:209-218` with the resulting
   region declarations for held LDO, ADC, reset supervisors, XMOS pin banks,
   TDM, FSYNC, and clock control.  For XMOS this naturally yields side/pin-bank
   views instead of a central symbol-interior tile.  Do not retain the old
   generic grid options as a fallback.

This is a presentation-only repair.  It is feasible in one focused renderer
change plus per-sheet region declarations; the nontrivial work is visual
selection/validation of the regions, not a new tscircuit or electrical design.
Do not estimate acceptance from syntax checks alone: it requires a newly
rendered candidate and a fresh full-PDF visual review.

## Focused validation after implementation

1. Extend `tests/t1_schematic_render.py` with asymmetric sparse fixtures that
   previously create a blank grid cell.  Assert that every emitted *detail body*
   has non-background schematic content, each fixture component's complete
   reference/value/body appears in at least one named detail, and no selected
   component is cut by a region.  Test a boundary-crossing net's continuation
   marker and fail-closed rejection of an empty/invalid region.
2. Preserve current checks: input Circuit JSON SHA is identical before/after;
   option parsing rejects duplicate/unknown/malformed regions; page count and
   each header's source-sheet/Circuit-JSON digest/overview link agree; a failed
   conversion or validation publishes no output.
3. Run only the focused static/unit checks first: `node --check` on the
   renderer, `bash -n` on the Crow driver, and the renderer test file.  Then,
   when authorized in the owning task, run one authoritative producer and
   compare the five electrical source-record classes plus regenerated native
   netlist against the approved baseline.  The presentation repair should show
   no electrical delta.
4. Rasterize and inspect every regenerated PDF page at normal page scale, with
   targeted high-resolution checks for each dense region.  Require zero blank
   detail pages, no cropped selected symbols/reference/value/net-label plates,
   and legible continuation handoffs before issuing a new hash-bound review.

Estimated engineering time: a few hours for the renderer/test/driver change and
one region-selection pass; validation/review time is dominated by the required
fresh producer and whole-document visual inspection.  The failed 92-page
review remains immutable throughout.
