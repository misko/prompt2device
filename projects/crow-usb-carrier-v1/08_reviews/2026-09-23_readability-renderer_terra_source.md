# Bounded readability renderer audit

Scope: `skills/kicad-pcb/scripts/render_schematic_pdf.mjs` and `projects/crow-usb-carrier-v1/03_src/rebuild_all.sh` only. This is a code audit, not an engineering witness.

No actionable findings.

The `--sheet-text-scale` parser rejects malformed, duplicate, unknown-sheet, non-finite, non-positive, and over-4 factors. Scaling is applied to the parsed SVG before font-metric baseline materialization, so baseline offsets use the scaled font size. The renderer retains atomic final publication, while the rebuild script deletes the former PDF before its intentionally non-fatal renderer call; the existing freshness verification then fails if no newly rendered PDF exists. `node --check` and `bash -n` both passed.
