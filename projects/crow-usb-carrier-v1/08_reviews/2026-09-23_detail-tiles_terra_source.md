# Detail tiles renderer audit

Scope: uncommitted diff from `15e8f46e` for `skills/kicad-pcb/scripts/render_schematic_pdf.mjs` and `projects/crow-usb-carrier-v1/03_src/rebuild_all.sh` only. Read-only code audit; no producer or electrical-record review was run.

No remaining actionable findings.

An initial P1 was found and communicated during the audit: detail-page construction prepended a crop `viewBox` while retaining the source SVG `viewBox`, which would serialize duplicate attributes. The current diff fixes this by cloning the parsed SVG tree and assigning its root attributes, replacing the existing `viewBox`; it also explicitly sets `overflow="hidden"`.

Verified from the current code:

- Detail windows cover each source extent end-to-end in both dimensions, with the stated 15% adjacent overlap.
- Overview and tile numbering use the accumulated PDF list, and `totalPages` includes every requested grid tile. Detail captions identify the source sheet, hash, overview page, and tile coordinate.
- The parser accepts only unique existing sheet names and 2x2 or 3x3 grids. With no `--detail-tiles`, the page count, overview render path, and output behavior are unchanged.
- Rendering still publishes only through the existing temporary output path and rename after all pages merge; an individual tile conversion failure prevents publication.

`node --check` for the renderer and `bash -n` for the Crow driver both passed.
