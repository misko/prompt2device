# Molex 43650-0400 primary-source fact record

Accessed: 2026-09-01
Authority status: manufacturer drawing retained and hash-verified; physical fit still owed

Primary drawing: [Molex 436501000 sales drawing, revision D8](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/436/43650/436501000_sd.pdf), released 2024-11-05.
The exact PDF is retained locally as `Molex_436501000_SD_revD8.pdf`, SHA-256
`b8942b95bc3fe4c02171de9e714d99b2688055e249ba1524e3c2a8c3cf78eaa3`.

Exact four-position facts used by this project:

- right-angle, single-row, through-hole Micro-Fit 3.0 header;
- 3.00 +/-0.05 mm contact pitch and 1.02 +/-0.05 mm signal holes;
- four-position table dimensions A = 15.65 mm, B = 9.00 mm, C = 4.70 mm;
- locating features use the drawing's 4.32 +/-0.08 mm relationship and the
  2.15 +/-0.05 mm offset represented by the exact project footprint;
- drawing general metric tolerances are +/-0.25 mm for two-place dimensions
  and +/-0.35 mm for one-place dimensions unless otherwise specified;
- mated length shown with the supported 43645 housing is 17.56 mm;
- the drawing calls out a 10.16 mm maximum from PCB edge to locating-peg
  centre to avoid mating interference; it is not measured from the signal-pin
  row. The pin row is 4.32 mm behind that peg centre and the mating face is
  another 4.60 mm toward the cable side.

The project-local footprint is checked against the pad/hole facts above. This
record does not establish installed seating, enclosure exposure, latch/key
detail, cable service, or physical fit.
