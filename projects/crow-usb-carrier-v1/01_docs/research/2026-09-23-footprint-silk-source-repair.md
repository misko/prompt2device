# Crow footprint silk / Description repair

Scope is the five requested hand-edited footprint sources at repository HEAD
`93991eef745323f4e570ab85528e704de4a2b5fc`.  No generated Crow board,
schematic, project file, campaign receipt, or commit was created.

## Source edits

* `03_src/lib/crow_usb_digital.pretty/TI_DCK0005A_SC70_5.kicad_mod`
  replaces the pad-spanning 2 mm silk rectangle with a 0.14 mm diameter,
  filled pin-1 circle at local `(-1.55,-1.05)`.  It is adjacent to the
  existing pad-1 end of the SC70 footprint without touching copper.
* `03_src/lib/crow_usb_digital.pretty/Samtec_FTSH_105_01_L_DV_K.kicad_mod`
  replaces the central 2 mm silk rectangle with a filled pin-1 circle at
  local `(-3.60,3.45)`, beside pad 1.
* `03_src/lib/crow_usb_power_aux.pretty/Littelfuse_451_Nano2_2410.kicad_mod`
  removes the two full-width silk lines which crossed the end pads.  This is
  a non-polar fuse, so no pin-1 mark is applicable.
* `03_src/lib/crow_usb_carrier_v1.pretty/GCT_USB4215_03_A.kicad_mod`
  moves only the mouth silk line from local `y=2.995` to `y=2.60`.  At the
  saved board placement `(230,22.995,180)`, that line is at board `y=20.395`,
  0.395 mm inside the `y=20` edge.  The F.Fab outline and F.CrtYd remain at
  their original values.  This is silk clearance only; it does not close the
  outstanding physical USB fit/edge-overhang evidence.
* `03_src/lib/crow_usb_analog.pretty/TI_DRC0010J_VSON10.kicad_mod`
  clears only the outlier `Description` property.  Its `descr`, Datasheet,
  F.Fab, F.CrtYd, pads, and `${KICAD10_3DMODEL_DIR}` model are unchanged.

The source diff contains no pad statement, courtyard, F.Fab, model, anchor,
or electrical-metadata edit. `git diff --check` passes.  The resulting file
SHA-256 values are:

```
0ef2c5a7a660adc387c85b891be2ef2f0f84a6001dc86fcb617cefd6b001ff46  TI_DRC0010J_VSON10.kicad_mod
956c6c04aa94ff5f4afa434db4715a93dc2d348fcbfb8495f9c5def98407c828  GCT_USB4215_03_A.kicad_mod
b53ddc22486471db3b99a5c5e63c93731c169e05fdc93af7d6726062be38f6c6  Samtec_FTSH_105_01_L_DV_K.kicad_mod
cd1ff0fcef46acff65f2a5ec80db36bbbdeb2ed73cc5138785260c97b3205639  TI_DCK0005A_SC70_5.kicad_mod
4cd17365dc235412ea594e155e8c4f7413037da9c284844db9b1a24e80d3a366  Littelfuse_451_Nano2_2410.kicad_mod
```

## Disposable native coupon evidence

`/tmp/crow-footprint-silk-repair/make_and_verify_coupon.py` builds only
`/tmp/crow-footprint-silk-repair/coupon/silk_coupon.kicad_pcb`; it is not a
Crow candidate. It loads original snapshots and the five edited sources with
KiCad 10.0.4, compares every pad's number, shape, attribute, position, size,
drill, and layer set, then creates a coupon with six SC70 instances at 0°,
JTAG at the saved 90°, fuse at saved 0°, USB at saved 180° and `y=20` board
edge, and DRC0010J at 0°.

`timeout 60s kicad-cli pcb drc --severity-all --format json` completed with
exit 0. The structural comparison reports all five pad sets identical.
Native DRC has **0 silk-related violations**. Coupon-only reference fields
are hidden because reference placement is board-generated rather than
footprint-originated silk; the saved product board separately owns those
field poses. This makes the silk result limited to the repaired footprint
geometry.

The negative-control coupon is generated from the preserved original five
footprints with the identical 10-instance layout and DRC command. It reports
49 total findings: **41 silk-related** and the same eight non-silk USB
findings. Thus the checker detects the prior silk geometry and the repair
changes the fixture result from 41 to 0 silk findings. The denominator is
exactly 10 footprint instances (six SC70 + JTAG + fuse + USB + DRC0010J), not
the historical 18/41 campaign count or a property/metadata count. The rate
calculation is guarded: it is `null` if the instance count is zero; these
runs are `41 / 10 = 4.1` and `0 / 10 = 0.0`.

The repaired DRC JSON has eight non-silk findings: four `clearance` and four
`solder_mask_bridge` reports for intentionally overlapping, netless paired
USB contacts in the standalone fixture. They are not waived or treated as
passing product-board DRC.

Artifacts:

```
3a674b8aef1a8639126383c685527607f398f7eb9687e79ff3156c220dcdddc0  silk_coupon.kicad_pcb
179d591953c82146e7830649251d3aeff8427a56f21c30fc4012d787b22ec578  original_silk_coupon.kicad_pcb
9503741aadfa1c287449e484fd3eb203e1815772f2c151fa015af7afaeac8b92  pad_geometry.json
33dbd5dda2732e7a2004bf9cf8012208a2e7e77cd2bc2a7057681852674482f3  coupon_drc.json
baee33bcecb054b2a198514bd84c63dfa4759134e9bb31bd73a554c6ef6df4eb  coupon_drc_original.json
6af5e456fdd05aef4c0fbc1e4bf2112f6ea3b46a31be5303aa795b44b56e12ba  result.json
b505c078b1ac389963b0dbd9606e6392bc07566ee70bcd36769fd006e06b5a0f  result_original.json
```

This is bounded source repair evidence only. A subsequent canonical source
regeneration and independent review must establish product-board validity.
