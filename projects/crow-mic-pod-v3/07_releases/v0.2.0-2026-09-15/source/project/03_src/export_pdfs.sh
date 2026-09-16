#!/bin/bash
# Generate the exact human PDF set required by the release contract and
# rasterize every page for visual inspection. The schematic is copied from
# the governed tscircuit human render; KiCad's converted schematic is not a
# substitute for that reviewed artifact.
set -euo pipefail
cd "$(dirname "$0")/.."

BOARD=04_kicad/crow_mic_pod_v3.kicad_pcb
SCHEMATIC=03_tscircuit/build/schematic.pdf
OUT=06_build/pdf

test -f "$BOARD"
test -f "$SCHEMATIC"
mkdir -p "$OUT"
rm -f "$OUT"/*.pdf "$OUT"/*.png

cp -- "$SCHEMATIC" "$OUT/schematic.pdf"

kicad-cli pcb export pdf --mode-multipage \
    -l F.Cu,B.Cu,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask \
    --cl Edge.Cuts --include-border-title \
    -o "$OUT/pcb_layers.pdf" "$BOARD" >/dev/null

kicad-cli pcb export pdf --mode-multipage \
    -l F.Fab,F.Silkscreen,B.Fab,B.Silkscreen,Edge.Cuts \
    --sketch-pads-on-fab-layers --include-border-title --black-and-white \
    -o "$OUT/assembly.pdf" "$BOARD" >/dev/null

for pdf in "$OUT"/*.pdf; do
    pdftoppm -png -r 150 "$pdf" "${pdf%.pdf}" >/dev/null
done

printf '%s\n' "$OUT/assembly.pdf" "$OUT/pcb_layers.pdf" "$OUT/schematic.pdf"
