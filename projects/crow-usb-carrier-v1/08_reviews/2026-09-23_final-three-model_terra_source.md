# Final three source models review — PASS

**Subject:** commit `79fee31d86037a96a4cea1087d8dd7d5430602d9` in
`/tmp/crow-passive-models-20260923`, compared with `1002f5bc`.
This is a source-model review only. It does not approve a Crow PCB producer,
placement, mating arrangement, clearance, or MODEL-REG.

**Disposition: PASS for the stated source-only scope.**

The three bindings use zero offset/rotation and unit scale references to
project-authored VRML. The declared source hashes agree with the retained
primary files and the reviewed assets:

| Part / footprint | Drawing SHA-256 | Model SHA-256 | Reviewed result |
|---|---|---|---|
| Molex 43650-0200 / J_PWR | `b8942b95bc3fe4c02171de9e714d99b2688055e249ba1524e3c2a8c3cf78eaa3` | `cecc9e5c231b1a6f654bcdd431f6ca67bb989a775b5579809cfc2bb14bb1e71b` | 9.65×9.90×4.37-mm housing plus 1.20-mm full-plan latch reserve; 3.30-mm below-board peg and 3.00-mm contact pitch are correctly represented as an envelope. The peg maps to the native 1.5,−4.32 datum and the connector mouth/mating direction is local −Y. |
| Samtec FTSH-105-01-L-DV-K / J_JTAG | `ef2961377445b9ad10762ea27519e7b59e5cbb5847dc0058d8e35c0d97c446a3` (series) and `caa205b92560423f3b0aea9c69d6c38340d1b7f01b0655092994450e935edcb3` (lands) | `61ace0bd681a9870865dae91deff43f2c8baa94616403fad523cdd09d80987e4` | Ten tails, ten 0.41-mm-square upright posts, 6.48-mm maximum insulator length, 3.43-mm reference width, and 0..6.10-mm simplified Z range are internally consistent with the cited drawing values and the existing 2.79×0.74-mm lands / 1.27-mm row pitch. Mating is +Z. |
| TI TPSM63603RDHR, RDH0030A / U_BUCK | `ffb05dbfc1fb35d79778fda2242d4880a0dfae146c28481afba8dff778b72dc6` | `95b041e1755b69ebae0a20a3f818d86d33656b46faa60487d5fb32dc44cb577f` | The maximum shell is exactly 4.10×6.10×1.90 mm, Z=0..1.90. Its pin-one marker maps to the footprint's pin-one corner (native −X,−Y). It properly makes no terminal or thermal-detail claim. |

All assets state that one VRML unit is 2.54 mm, model Y is opposite footprint
Y, and Z=0 is the PCB top. Applying that inversion puts the Molex peg at the
existing NPTH, the Molex tails at pads 1/2, the Samtec illustrative tails at
their corresponding 2×5 lands, and the TI orientation mark at pin one. The
Molex body plus latch is deliberately a conservative roof, not a shape claim;
its total model Z span includes the below-board peg. The Samtec key cutout and
the TI terminals are explicitly omitted. These limits are documented
honestly, and the research note correctly records that no supplier CAD was
obtained or imported. The models carry the repository MIT provenance and
cite, rather than copy, the drawings.

The three edited footprint files retain exactly **42 named pads**: Molex 2,
Samtec 10, and TI 30. Their pad, silk, courtyard, and all other functional
non-model S-expression bytes are unchanged from `1002f5bc`; only the model
clauses changed (the Molex URI was replaced, the other two were added). The
Samtec and TI edits leave one otherwise blank indentation-only line when a
model block is structurally removed; that is not a geometry or metadata
change. No `.kicad_pcb` or `.kicad_sch` file changed. `git diff --check`
is clean.

The retained fixture render log records successful native 3D loading for the
three source models at 0° and 90°. That is a smoke check only, and does not
demonstrate placement, mating direction in an installed assembly, exact CAD
parity, model-to-board registration, or clearance.
