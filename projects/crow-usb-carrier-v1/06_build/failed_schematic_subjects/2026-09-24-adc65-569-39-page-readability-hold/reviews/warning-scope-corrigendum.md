# Corrigendum — Crow 39 render-warning scope audit

This corrigendum leaves `/tmp/crow-39-render-warning-scope-terra.md` unchanged.

The original audit's claim that the project renderer did not implement
`--sheet-text-scale`, and therefore that a renderer/driver mismatch existed,
was false. I inspected the authoritative project-worktree renderer:

`/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922/skills/kicad-pcb/scripts/render_schematic_pdf.mjs`

SHA-256: `6d9417ec834e9f49049988a86b1e3d7ba9523fb01e700aa985287dd9a268a8c9`.

Evidence in that exact script:

* lines 228--235 advertise `--sheet-text-scale <sheet>:<factor>:<pins|all>`;
* lines 250 and 260--268 parse it; lines 356--359 reject an unknown sheet;
* lines 458--485 scale `sch-pin-number` and `sch-pin-label` SVG text and emit
  an auditable count; and
* lines 566--572 apply that scale before baseline materialization.

The source-owned project driver invokes `--sheet-text-scale xmos_core:2.6:pins`
at `03_src/rebuild_all.sh:209--211`. The actual producer log, SHA-256
`248a3e357f4d86a5422ccd5f35cc7da2d1f174fcca10dfeccb52b821d6dbbf4d`,
records:

```
SCHEMATIC-RENDER sheet xmos_core: scaled 258 pins text item(s) by 2.6
SCHEMATIC-RENDER page 30/39: XMOS CORE (1 components, landscape)
```

at lines 1310--1311, followed by a 39-page renderer PASS for the bound
`28f678...` PDF. Thus the scale option was both implemented and applied to
the reviewed output.

The conclusion about no warning-derived PDF clipping/omission and the parts
digest defect is unaffected. XMOS normal-scale readability also remains a
real defect: the already-applied 2.6x pin-text intervention and the existing
40-mm U_XU width did not make the one-page, 129-pin perimeter normally
reviewable. The smallest credible next repair is consequently semantic
presentation content, not another scale-option repair or coordinate crop:
add source-owned, explicitly U_XU-linked functional pin-bank pages or a
pin-index appendix (power/ground; QSPI/debug; USB/reset/clock; audio/control;
NC), retaining every numbered pin/name/net exactly once. A fresh build,
all-129 tuple comparison, and independent normal-scale review remain required.
