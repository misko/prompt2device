# XMOS detail-page coverage audit

Scope: `/tmp/crow-detail-probe.pdf` pages 30–39 and the candidate Circuit JSON at `projects/crow-usb-carrier-v1/03_tscircuit/build/circuit.json`. Read-only output audit; this is not a canonical SOUND witness.

## Result

No coverage gap found.

- The candidate SHA-256 is `30377f6fdecb4e69cefb3a2b24b91fa9288607ec40db4fe2f4e6a123a22a1033`; every overview/detail header correctly carries the matching `30377f6fdecb4e69…` prefix.
- Actual PDF pages were raster-inspected: overview page 30 and XMOS detail pages 31–39 identify `XMOS CORE`, source sheet 30 / `schematic_sheet_29`, correct detail coordinate, and overview page 30. Page numbering is contiguous and consistently reports 48 total pages.
- The candidate declares 129 XMOS ports. Its 111 unique pin names and all 29 unique XMOS-sheet net/text labels are present in the nine detail pages. Visual inspection confirms readable, unclipped coverage of every perimeter side across the overlapping tiles; boundary-adjacent pin rows repeat in adjacent tiles (for example, top-row and left/right-edge rows at the R1/R2/R3 and C1/C2/C3 seams).
- Detail 5/9 (R2C2, page 35) contains no pins. This is expected for this large perimeter-pin symbol: its center is blank, while all pins are covered by the surrounding eight tiles. It is not a coverage omission.
- The 15% overlap is visually present at row/column seams. Cropped portions at an individual seam have complete readable counterparts in the adjacent tile.
- `pdffonts` reports embedded, subsetted Noto Sans TrueType/CID TrueType fonts. The raster pages show legible pin names, pin numbers, and net labels at the tile scale.

No PDF or candidate artifact was modified.
