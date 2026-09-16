# Corrected-stage schematic review evidence

MEASURED: these are unmodified direct PDF raster crops retained from the fresh
review directory `/tmp/carrier-schematic-fresh-Rp4aU7/`, not edited design images.
They document remaining defects after the six-resistor and ADC-spacing changes.
The parent agent also opened the three crops on 2026-09-07 and confirmed the
visible collisions. They do not indicate native electrical shorts.

Exact source PDF: `03_tscircuit/build/schematic.pdf`

SHA-256: `dc23165096141171ee5a33ec711b4515613def66e9ed53d3204dbe29edab9470`

| Crop | PDF page | dpi | x, y, width, height (raster pixels) | Finding |
|---|---:|---:|---|---|
| p6-clocks-6.png | 6 | 300 | 175, 520, 1620, 460 | SR-1: boxed-label baseline and resistor-value collision |
| p1-fuse-1.png | 1 | 600 | 1710, 1140, 1030, 275 | SR-2: protected rail on F_IN border/output-label region |
| p1-fuses-top-1.png | 1 | 300 | 2530, 270, 710, 1140 | SR-3: F7 output and C_BUCK_IN3 label overprint |

Reproduce with `pdftoppm -f PAGE -l PAGE -png -r DPI -x X -y Y -W WIDTH
-H HEIGHT INPUT.pdf OUTPUT_PREFIX`, substituting a table row. The immutable
reviewer's complete verdict, coverage, exact native hashes and limits are in
`08_reviews/pre-route_schematic_render.md`. Both reports are DEFECTIVE and
DO-NOT-ORDER; no approval is inferred from retained evidence.
