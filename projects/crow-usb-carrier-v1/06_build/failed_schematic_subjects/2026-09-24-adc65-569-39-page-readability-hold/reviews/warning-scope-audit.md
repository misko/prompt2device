# Crow 39 render-warning scope audit (Terra, read-only)

Date: 2026-09-23. This is an independent scope audit of the immutable formal render report, not a replacement verdict and not a producer/review retry.

## Bound inputs

* Formal report `06_build/task_runs/crow-39-schematic-render-review-terra-r4-418dac4413764abdac5c8c8ed203670e-a226bed7bc274c2c985c15f1fed5ceb9/outputs/review.md`: `92fdb26484883c910cc166e22cf0d4c91e8da4f92510e2e81fef8efcc639e95d`.
* Circuit JSON: `1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448`.
* PDF: `28f6786549db410174ecde50128091891eb8778c7d97f1d10f23ec65fd0829fd`; 39 pages, 900 x 607.5 pt, rotation zero.
* Packet manifest named by both formal reviews: `1cadb2895230a120e927cc0ebfc57783b31bd57b9e990276e085b0ed256a9e88`.
* Frozen-subject raw and semantic digest named by both: `4841591b695cd4b64a8d5e8cda729f1e0de703cecfff580128369481583e6aeb`.

## Scope of the 152 diagnostics

The count is correct and comprises 152 distinct elements, not 152 duplicate reports of one element.

| PDF page | sheet | components / labels / traces | total |
|---:|---|---:|---:|
| 1 | POWER INPUT | 2 / 2 / 1 | 5 |
| 4 | HELD LDO | 0 / 2 / 3 | 5 |
| 23 | ADC | 0 / 3 / 0 | 3 |
| 25 | RESET SUPERVISORS | 6 / 12 / 9 | 27 |
| 26 | RESET SEQUENCER | 0 / 2 / 0 | 2 |
| 30 | XMOS CORE | 1 / 43 / 30 | 74 |
| 31 | XMOS DECOUPLING | 0 / 3 / 0 | 3 |
| 36 | ADC CLOCK CONTROL | 7 / 18 / 8 | 33 |

`@tscircuit/core@0.0.2351` emits this diagnostic before PDF construction. Its `insertSchematicElementOutsideSheetWarnings` checks a fixed A4-derived rectangle (297 x 210 mm converted by `10.16 / 1.1`) minus a 5-mm inner margin, centered at `schematic_sheet.center`. It compares source component/label/trace bounds with that rectangle. It does not inspect the PDF page, a clipping path, SVG viewport, text legibility, or output raster.

The delivery renderer has a different contract. For each declared sheet it filters the exact Circuit JSON to that sheet and calls `convertCircuitJsonToSchematicSvg(pageCircuit, {width, height})`. The converter obtains `getSchematicBoundsFromCircuitJson(pageCircuit)` from components, ports, labels and every trace endpoint, applies padding, and maps the complete resulting bounds to the page SVG. The renderer embeds that fitted SVG below its header and converts it to PDF. Thus this warning and delivered-page containment test different coordinate spaces.

## Actual visible-page result

I rasterized the exact bound PDF at 200 dpi and inspected pages 1, 4, 23, 25, 26, 30, 31 and 36, including each page edge and every warning-bearing region. The retained montage is `/tmp/crow-warning-scope-terra-20260923/montage.png`, SHA-256 `38a1ddd18c3cd2a7435f187471f2578925024f35062ea555417b791ef7ba02db`.

No clipping, blank warning region, omitted warning-bearing element, or PDF edge cut was observed. The page-1 endpoints; page-4/23/25/26 label extremities; page-30 perimeter; page-31 left labels; and page-36 portrait extents are all inside their rendered pages. The all-element fitted-bounds path explains this result. This is strong evidence that the 152 warnings alone are not evidence of actual PDF clipping or omission. It does not prove electrical connectivity.

RENDER-001 therefore overstates what the warning type proves when it treats those source diagnostics alone as a failed PDF-containment finding. They may remain source-layout advisory debt, but require output evidence before being called visible clipping.

## Separate real risk: XMOS normal-scale readability

The warning false-positive conclusion does not cure page 30. The source puts all 129 U_XU pins round-robin around one `schWidth:40`, `schHeight:24` symbol. The exact PDF's Poppler XML reports XMOS body/pin label font classes at size 5 (with some body classes at 11); direct word boxes show the smallest label/number glyph extents. The prior read-only presentation investigation traced the pinned 0.15-mm pin font to about 2.7--3.3 pt PDF text and found top/bottom bank overlap when only enlarged 2.6x. The normal-view requirement explicitly rejects a document needing deep zoom.

The formal DEFECTIVE conclusion can therefore remain supportable on XMOS normal-scale readability, but not on inferred clipping from the containment warnings. The exact PDF font census also shows very small body text on pages 4, 25 and 36; this audit does not re-adjudicate those visual judgments.

## Smallest credible XMOS repair path (no coordinate crop)

1. Keep one electrical U_XU and all 129 exact numbered ports. In `03_tscircuit/src/z_schematic_presentation.tsx`, retain the presentation arrangement but give top/bottom banks sufficient horizontal pitch; the documented bounded starting geometry is about 40 mm wide.
2. Restore/implement the narrow `--sheet-text-scale xmos_core:<factor>:pins` renderer option already invoked by the project driver, applying a 2.4--2.6x pin-font scale only to emitted XMOS SVG text before baseline materialization. Current shared renderer source advertises only `--title` and `--net-aliases`, while `03_src/rebuild_all.sh` invokes that scale option; resolve this source/driver mismatch before claiming it repaired the frozen PDF.
3. If top/bottom banks still collide, replace the generic visual perimeter with source-owned functional pin-bank pages or a pin-index appendix: power/ground, QSPI/debug, USB/reset/clock, audio/control, and NC. Each must explicitly tie to U_XU and preserve each pin number/name/net exactly once. This is semantic presentation expansion, not a crop of generated coordinates or an electrical split of the physical part.

A candidate requires a new build, all-129 tuple comparison `(pin number, source-port name, connectivity key/net)`, no other population delta, and a fresh independent normal-page visual review. The owner is schematic presentation source plus shared PDF renderer/driver; do not edit generated PDF or Circuit JSON directly.

## Formal metadata defect: parts digest

The formal render report header says `parts_sha256: f864f336da4593f411873bc5955bd8fe472b18168827fe6e44cc7787d52d311d`. That is wrong for its named frozen packet.

I recomputed the owning helper's exact algorithm over all 112 sorted `02_parts/*/part.yaml` records: relative POSIX path + NUL + bytes + NUL. Result:

```
833913d1c3d68cec43ab53f34e63b48cbf0e38bd3ec5a5115abfbaa5e23c2a0e
```

This agrees with the independent formal topology report for the same manifest, circuit JSON and helper SHA-256 `b02a6d97feef2436ba71053e676d87e04c726b1ceec92cd92cf8a4b5d25c6b4e`. The helper compares `parts_sha256` exactly and separately requires a SOUND render verdict. Thus the immutable DEFECTIVE report could not be accepted as a render witness even if its design verdict were SOUND: its metadata fails the gate as written.

The exact origin of `f864...` cannot be proven after the reviewer packet copy was cleaned up. It is not the current/frozen 112-record helper digest or the straightforward path/terminator variants tested. The same packet's topology witness has `833913...`, supporting a render-review report emission/copy-paste or stale-input error rather than a part-dossier difference. Preserve the formal report; do not overwrite it.

## Next-owner backtrack

1. Treat `f864...` as a formal review-header defect and leave the failed report immutable.
2. Backtrack the source-owned XMOS/page-presentation defects above, including the renderer/driver scale-option mismatch. Do not use the 152 pre-render warnings as a clipping finding.
3. After a new frozen candidate exists, issue a fresh hash-bound render review that recomputes the 112-record digest and visually tests normal page-scale readability. Only that new witness can replace the failed one.
