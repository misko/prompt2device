# Independent logic-model source review

**Final revision:** `/tmp/crow-logic-models-20260923` follow-up
`fc5d941f57ca4caa8c141e86bc65933a22737f16`. The failed initial candidate
`363d16d3` remains visible in history.

## Verdict

**PASS for the bounded source-model repair.** The initial DCT binding is
explicitly rejected: generic `TSSOP-8_3x3mm_P0.65mm.step` had a 4.90-mm lead
span, 0.65 mm over TI DCT0008A's 4.25-mm maximum. The final revision removes
that asset and uses drawing-derived nominal `TI_DCT0008A_nominal.wrl`.

This is not a Crow-board generation, placement, P1, DRC, runtime, MODEL-REG,
full-model-coverage, or physical-qualification result.

## Invariance and intentional metadata exception

Initial changes to all four footprints were model clauses only. In the final
revision DCT's model path changes to the new WRL. `TI_DCU0008A_VSSOP8` also
changes its description from “0.65mm pitch” to “0.50mm pitch”, explicitly
requested by root. This is an intentional metadata scope addition, not a
model-only byte invariant; it is factually correct for its existing 0.5-mm pad
pitch and TI DCU drawing. Normalized comparison confirms pads, names,
copper/paste/mask, silk, fab and courtyard bytes otherwise remain unchanged.

## Dimension, pitch and orientation check

| Footprint / refs | Final model | Geometry (mm) | Retained primary-drawing comparison | Result |
|---|---|---:|---|---|
| `TI_DCK0005A_SC70_5` / 6 | public `SOT-353_SC-70-5.step` | 2.10 x 2.00 x 1.10 | TI 4214834/G DCK: plan 1.8..2.4 and 1.85..2.15, 1.1-mm max height, 0.65 pitch | PASS generic family geometry; five leads and pin-1/row convention agree. |
| `TI_DCT0008A_SM8` / 2 | `TI_DCT0008A_nominal.wrl` | lead X 4.10; body 3.00 x 3.00; body top 1.15; mark top 1.17 | TI 4220784/D DCT: overall X 3.95..4.25, body 2.9..3.1 square, height 1.0..1.3, 0.65 pitch | PASS: eight leads at 0.65 pitch and pin 1 upper-left; nominal dimensions are within retained limits. |
| `TI_DCU0008A_VSSOP8` / 1; `TI_TCA9406_DCU0008A_VSSOP8` / 1 | public `VSSOP-8_2.3x2mm_P0.5mm.step` | 3.10 x 2.00 x 0.85 | TI 4225266/A DCU: 3.0..3.2 overall, 2.2..2.4 body, 0.9 max height, 0.5 pitch | PASS generic nominal geometry; eight-lead rows and pin-1 orientation agree. |

The DCT replacement is source-authored nominal geometry, not TI CAD or a
maximum envelope. Its simplified lead boxes omit gull-wing curvature, tolerance
sweep, solder and mould detail; those limits are honestly documented. Comments
use footprint Y down, VRML inverts it once, and Z=0 is the seating plane.

## Public asset provenance

KiCad `10.0.4^{}` resolves to `0bc64e922178140eb6890377646efd45e15011bd`.
Fresh GitLab raw-byte checks match the final vendored assets and copied
CC-BY-SA 4.0-with-electronic-design-exception license:

* `SOT-353_SC-70-5.step`: `2860de5b7b085919ff6e952148353f928798588d9f544dc69430545aff2ba908`
* `VSSOP-8_2.3x2mm_P0.5mm.step`: `353552981eef35cb93635057d4aeb89aef22648c77af6fd095e328bfe6b834bd`
* `LICENSE.md`: `45d2bce75e5a4208f5afb01b8fb2c406e700371c4fe2b5f5cd5c443d46db4d8f`

The removed TSSOP hash is
`cf28a51742b2e31065e201d1b313207140cbfb49062efd938788f7a310d02738`.
New DCT WRL SHA-256 is
`0b3bb56858e676dbbd5a3756981aeb6b29f4159f749cf88bcf0be23e7f6915f8`.
Its TI SCES203Q p19 authority SHA-256 is
`19bc881b14bac1dd02c9a5c9a184d09b2482eab053fb5e7706897ab42c023bea`.

## Native fixture smoke

Corrected 0/90 fixture source SHA-256:
`4d58695d11c7ed3f2938619bb86c014a772654b0c1075674b50734abd6734a30`.
Top render SHA-256:
`16cd4f99bdef01c12e8dafeb54e449ce70c1f56c1ec2b845ba962b34e6c72ece`.
Eight instances load: four footprint types at 0 and 90 degrees. Independent
front-side native smoke rendering completed, showing all four body classes
above the board (SHA-256
`f4e29e175c3db92b29be3f8ebda224912748b94b175f1a17d53c62114953edda`).
This establishes native load/visibility and gross signed-side behavior only.

## Remaining action

Keep the DCT asset labeled nominal. Full-board identity/transform,
same-camera and signed-mounted-side registration are still owed on a later
generated candidate.
