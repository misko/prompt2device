# Crow 569 overview-only driver source review (independent)

## Verdict: SOUND

This is a bounded, driver-only presentation repair.  Against base `f7c2afb`,
the sole tracked diff is `projects/crow-usb-carrier-v1/03_src/rebuild_all.sh`:
one line added and eight removed.  It removes exactly seven optional
`--detail-tiles` arguments from the existing `render_schematic_pdf.mjs`
invocation:

* `held_ldo:3`
* `adc:3`
* `reset_supervisors:3`
* `xmos_core:3`
* `fsync_shaping:2`
* `adc_clock_control:2`
* `tdm_translation:3`

The retained invocation is exactly:

```sh
node "$S/render_schematic_pdf.mjs" "$CJ" "$SCHPDF" \\
    --title "$SCHEMATIC_TITLE" "${NET_ALIAS_ARGS[@]}" \\
    --sheet-text-scale xmos_core:2.6:pins || true
```

Thus the title, conditional `--net-aliases` forwarding, and XMOS pin-only
2.6x text scaling are retained.  The pre-existing `|| true` remains attached
to the renderer command.  It is not newly introduced or broadened by this
patch.

## Invocation semantics and gate preservation

The renderer parses each `--detail-tiles <sheet>:<2|3>` into `detailTiles`.
It first emits exactly one overview page for every source sheet, then adds
`grid * grid` cropped detail pages only for entries in that map.  With no
entries, the calculated total is the source-sheet page count and the crop
loop is not entered.  The retained `--sheet-text-scale` is parsed separately
and applies only its requested sheet/mode; it is independent of details.

The current frozen Circuit JSON has 39 distinct `schematic_sheet` records,
569 `schematic_component` records, and 1,071 `schematic_net_label` records.
Therefore the expected output is 39 authored overview sheets, one per source
sheet.  This agrees with the alternatives review: the previous 92 pages were
39 overviews plus 53 requested detail tiles
(`9 + 9 + 9 + 9 + 4 + 4 + 9`).

The patch does not alter `rm -f` of the target PDF, `$CJ`, `$SCHPDF`, the
renderer implementation, conversion/netlist commands, or the immediately
following `build_provenance.py verify` call.  M-FRESH still requires the
render to exist and post-date the circuit artifact after this deliberate
best-effort renderer call.  Consequently renderer failure remains caught by
the named M-FRESH failure path; this patch creates no bypass.

## Independent checks

* `git diff --check f7c2afb` passed.  `git diff --name-only f7c2afb` names
  only the driver; no TSX, Circuit JSON, KiCad schematic, netlist, renderer,
  electrical rule, or producer source is in the tracked diff.
* `bash -n projects/crow-usb-carrier-v1/03_src/rebuild_all.sh` and
  `node --check skills/kicad-pcb/scripts/render_schematic_pdf.mjs` passed.
* I rendered the frozen Circuit JSON to `/tmp` using the retained arguments
  (title, aliases, and XMOS scaling; no detail flags).  The renderer exited
  zero and reported `39 page(s), 569 components, 18 explicit net alias(es),
  0` scaled two-port corrections, and maximum endpoint residual `0.00e+0`.
  `pdfinfo` reported 39 pages at 900 x 607.5 pt; extracted text had zero
  `DETAIL` occurrences.  This is a renderer execution check only, not a
  fresh producer run.
* The Circuit JSON SHA-256 was unchanged before and after that render:
  `1f01be73e0699cd62bc734aa189b25e9d66f1097b5ce6f52a8db30533ecc6448`.
* The retained driver SHA-256 is
  `2a337ff8086cdd8e57b64a2bd0b39fed35384d434c6eaf9c99fbdb1a06546a9f`.
* A source search excluding generated `06_build` and dependency directories
  found no active caller of this Crow driver.  The only hits are historical
  reviews, research patches/fixtures, and a stored prior hash; they do not
  invoke it.  No broader caller needs changing.
* Rehashed failed-review archive inputs remain
  `08e02b34065e71755b067c66accd12e6f42542581f846f7a508b4958092524a2`
  (`crow_carrier.kicad_sch`) and
  `6a6be131d497e0d2b66f53b97501251a4f37ec3a64b2d4743f9af793b512e54b`
  (`schematic.pdf`).

## Limits

This finding approves the source-level scope and renderer invocation
semantics only.  It does not accept the schematic, certify electrical
correctness, perform a native or producer run, establish M-FRESH runtime
receipt, or substitute for an authoritative render and page-by-page visual
review.  The untracked `03_tscircuit/dist/` directory was pre-existing in the
worktree status and was not inspected as a patch change or modified.
