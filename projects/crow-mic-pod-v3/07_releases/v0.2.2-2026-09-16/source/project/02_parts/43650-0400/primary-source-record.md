# Molex 43650-0400 primary-source fact record

Accessed: 2026-09-03
Authority status: official manufacturer PDF retained and SHA-256 bound

Primary drawing: [Molex 436501000 sales drawing, revision D8](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/436/43650/436501000_sd.pdf), released 2024-11-05.

Exact four-position facts used by this project:

- right-angle, single-row, through-hole Micro-Fit 3.0 header;
- 3.00 +/-0.05 mm contact pitch and 1.02 +/-0.05 mm signal holes;
- four-position table dimensions A = 15.65 mm, B = 9.00 mm, C = 4.70 mm;
- locating features use the drawing's 4.32 +/-0.08 mm relationship and the
  2.15 +/-0.05 mm offset represented by the exact project footprint;
- drawing general metric tolerances are +/-0.25 mm for two-place dimensions
  and +/-0.35 mm for one-place dimensions unless otherwise specified;
- mated length shown with the supported 43645 housing is 17.56 mm;
- the drawing calls out a 10.16 mm maximum PCB-edge relationship to avoid
  mating interference.
- the drawing's component-side view and the project footprint are related by
  a 180-degree rotation, not a reflection: after aligning the peg/body axis,
  drawing circuit 1 lands on project pad 1.

The project-local footprint is checked against the pad/hole facts above. The
official one-page PDF is retained as `Molex_436501000_SD_revD8.pdf`, SHA-256
`b8942b95bc3fe4c02171de9e714d99b2688055e249ba1524e3c2a8c3cf78eaa3`.
This remains documentary authority, not physical fit evidence.
