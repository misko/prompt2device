# Logic package models (KiCad 10.0.4)

These two **generic KiCad package** STEP models are unmodified public library
bytes, vendored so source footprints remain portable. They are **not TI CAD,
exact MPN registration, placement proof, or a substitute for MODEL-REG**. Each
file and `LICENSE.md` matches upstream commit
[`0bc64e922178140eb6890377646efd45e15011bd`](https://gitlab.com/kicad/libraries/kicad-packages3D/-/commit/0bc64e922178140eb6890377646efd45e15011bd)
(tag `10.0.4`) byte-for-byte by SHA-256. Original path root:
[`kicad-packages3D`](https://gitlab.com/kicad/libraries/kicad-packages3D); the
individual paths are in the table. `SHA256SUMS` records exact vendored bytes.
The copied upstream `LICENSE.md` is CC-BY-SA 4.0 with KiCad's electronic-design
exception; redistribution of these model files remains under that license.

| Native source footprint; fitted refs | Vendored upstream path | Manufacturer dimensional comparison |
|---|---|---|
| `TI_DCK0005A_SC70_5` / 6: `U_ADC_DIGITAL_BAD`, `U_ADC_PWR_BAD`, `U_ADC_READY_BAD`, `U_BCLK_INV` (`SN74LVC1G04DCKR`); `U_ADC_CLOCK_OK`, `U_ADC_READY` (`SN74LVC1G125DCKT`) | `Package_TO_SOT_SMD.3dshapes/SOT-353_SC-70-5.step` | Retained TI SCES214 and SCES223 DCK0005A package outline 4214834/G: SC70-5/SOT, 0.65-mm pitch, 1.1-mm maximum height, 1.8–2.4-mm package span and 1.85–2.15-mm body axis. Model has the matching five-lead SC70 family, pin1 upper left; source pad rows 1/2/3 left and 5/4 right agree. Source pad centres ±1.10 mm are 0.2625 mm farther outward than KiCad stock source land centres ±0.8375 mm, but its 0.95-mm-long lands still overlap model leads. Exact lead bends, body/lead tolerance, and maximum envelope are not asserted. |
| `TI_DCU0008A_VSSOP8` / 1: `U_ADC_OUT` (`SN74AUP3G34DCUR`); `TI_TCA9406_DCU0008A_VSSOP8` / 1: `U_ADC_I2C_XLATE` (`TCA9406DCUR`) | `Package_SO.3dshapes/VSSOP-8_2.3x2mm_P0.5mm.step` | Retained TI SCES766C and SCPS221G DCU0008A package outline 4225266/A: 8-lead VSSOP, 2.2–2.4 × 1.9–2.1-mm body, 3.0–3.2-mm overall span, 0.5-mm pitch, 0.9-mm maximum height. Generic KiCad 2.3×2-mm P0.5 model names exactly those nominal plan dimensions. Pins 1–4 left, 5–8 right; source lands at ±1.55 mm versus stock ±1.40 mm, with model-lead overlap. The `TI_DCU0008A_VSSOP8` source footprint's old description says “0.65mm pitch”; its pad coordinates actually have 0.5-mm pitch, which agrees with TI DCU and the model. Description repair is outside this model-only scope. |

The DCT package uses **source-authored drawing-derived nominal geometry**, not
the generic KiCad TSSOP model from the first candidate. Independent review
measured that failed generic model's overall X span at 4.90 mm, beyond TI's
4.25-mm maximum; its prior use remains visible in commit `363d16d3` but the
file is removed from this final bundle. `TI_DCT0008A_nominal.wrl` (SHA-256
`0b3bb56858e676dbbd5a3756981aeb6b29f4159f749cf88bcf0be23e7f6915f8`)
is a declarative VRML source file with per-shape millimetre dimensions. TI
SCES203Q retained `SN74LVC2G74-SCES203Q.pdf` (SHA-256
`19bc881b14bac1dd02c9a5c9a184d09b2482eab053fb5e7706897ab42c023bea`),
p.19, drawing 4220784/D, specifies body 2.9–3.1 × 2.9–3.1 mm, overall X
3.95–4.25 mm, 0.65-mm lead pitch, 0.15–0.30-mm lead width, and total height
1.0–1.3 mm. The model uses a 3.00×3.00-mm body from Z=0.10 to 1.15 mm,
eight 0.55×0.225×0.20-mm simple lead boxes at X=±1.775 mm and Y=±0.975/
±0.325 mm, giving **4.10-mm overall X**, 3.00-mm body Y, and 1.15-mm top.
Pin1 is upper left in footprint coordinates; a small top mark is illustrative.
The leads overlap the unchanged native land X ranges 1.35..2.45 mm. Curved
gull-wing form, alternate lead height, tolerances and mould details are not
represented. This is neither exact TI CAD nor a swept maximum envelope.

All source footprint changes add only zero-offset, unit-scale, zero-rotation
model clauses **except** the old `TI_DCU0008A_VSSOP8` description's inaccurate
“0.65mm pitch” text, corrected to the drawing and pad-coordinate value
“0.50mm pitch”. No pad, silk, fabrication, or courtyard text was changed. The
STEP/VRML files do not establish swept maximum-height clearance or PCB-mounted
registration. A fixture-only render at 0° and 90° checks visibility and gross
orientation; the full board model scene, same-camera registration, and final
coverage remain owed by the integration owner.

Initial fixture evidence (outside source tree, before DCT correction):
`/tmp/crow-logic-model-fixture-20260923/04_kicad/logic_models_fixture.kicad_pcb`
(SHA-256 `79582e2b9f4bdaef50e0aff3e08ee0e36737e6e31aa7233d20b76d203f18961a`)
and `logic_models_top.png` (SHA-256
`e7c96cd1cc8e6e95bbd170f9505182eb12b4eeae91eb6d3295abf39b004f5580`).
`kicad-cli pcb render` loaded all eight 0°/90° fixture instances; visual
inspection shows four bodies above the board in each row, pin-1 marks rotating
with each footprint, and no gross lead/body inversion. These files contain no
Crow board and are not P1 evidence.

Corrected fixture evidence:
`/tmp/crow-logic-model-fixture-20260923/04_kicad/logic_models_fixture_r2.kicad_pcb`
(SHA-256 `4d58695d11c7ed3f2938619bb86c014a772654b0c1075674b50734abd6734a30`)
and `logic_models_top_r2.png` (SHA-256
`16cd4f99bdef01c12e8dafeb54e449ce70c1f56c1ec2b845ba962b34e6c72ece`).
`kicad-cli pcb render` loaded all eight current models; visual inspection at
0°/90° shows the replacement DCT body above the board and pin1 on the same
rotated side as native pad1. This is a fixture check, not MODEL-REG.
