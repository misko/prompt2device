# Independent source review — courtyards and ADC/TMUX models

**Basis:** `crow-usb-carrier-v1-20260922` at `HEAD`
`6ffcdd24a0cd83d56bd126d7640301da218979e5`, reviewed 2026-09-23.

## Verdict

**PASS for the narrow source scope. No blocking source defect found.** This
review does not admit a canonical schematic or placement and makes no claim of
runtime PASS, MODEL-REG, full model coverage, P1, DRC, or physical qualification.

## Seven F.CrtYd repairs

For every edited footprint, deleting its one added `F.CrtYd` rectangle made the
file byte-identical to `HEAD`. Pads, pad names, copper/paste/mask, silk, fab
and other metadata are therefore unchanged.

| Footprint | Rectangle / span (mm) | Retained drawing basis | Result |
|---|---:|---|---|
| `Samtec_FTSH_105_01_L_DV_K` | `[-4,-4.5]..[4,4.5]` / 8.0 x 9.0 | Samtec Rev H p1: individual lands 2.79 x 0.74, full copper X span 6.86 (X +/-3.43); project exact FTSH envelope 7 x 8 | PASS: 0.5-mm body allowance and copper enclosed; not a service proof. |
| `TI_DMQ0006A_VSON6` | `[-1.25,-1.25]..[1.25,1.25]` / 2.5 x 2.5 | TI 4222645/E p32: 1.55 x 1.55 max body | PASS |
| `TI_RTW0024A_WQFN24_4x4_EP2.6` | `[-2.8,-2.8]..[2.8,2.8]` / 5.6 x 5.6 | TI 4222815/A p1: 4.1 x 4.1 max body; 0.5 pitch | PASS, including existing pin-one silk. |
| `TI_DCK0005A_SC70_5` | `[-1.85,-1.35]..[1.85,1.35]` / 3.7 x 2.7 | TI 4214834/G p34: 2.4 x 2.15 max plan | PASS |
| `TI_DCT0008A_SM8` | `[-2.7,-1.8]..[2.7,1.8]` / 5.4 x 3.6 | TI 4220784/D p19: 4.25 x 3.1 max plan | PASS; minimum body gap is 0.25 mm at courtyard-line centre. |
| `TI_DCU0008A_VSSOP8` | `[-2.25,-1.45]..[2.25,1.45]` / 4.5 x 2.9 | TI 4225266/A p23: 3.2 x 2.4 max plan | PASS |
| `TI_TCA9406_DCU0008A_VSSOP8` | `[-2.55,-1.7]..[2.55,1.7]` / 5.1 x 3.4 | TI 4225266/A p32: 3.2 x 2.4 max plan | PASS, including existing pin-one silk. |

Checked retained-PDF SHA-256: RTW
`45616d442aed7ce69f42ce26187526723e12082c905d51ad3ff7b2f014752765`; TMUX
`3af04d7ae37b0e43c71c1b663a2d055667d94d46b5dc87c9ca2de24ec2295028`; DMQ
`8a309f2a40486a380242d3f178eb4bda3ef4dca3deca647fa82f763d14866f63`; DCK
`ac04a53de979125799e57ea5a6dff4138fe53e0eceebe45c31f57523669887d5`; DCT
`19bc881b14bac1dd02c9a5c9a184d09b2482eab053fb5e7706897ab42c023bea`; DCU
`f188afa526b904201017529cf6c363974be3a1bf580a64e12485e40d5aefcf07`; TCA
`fdb80d682fbacd5ef18cbafc57e4d9375a295daa38da33721af6e055f8a7da61`; Samtec
`caa205b92560423f3b0aea9c69d6c38340d1b7f01b0655092994450e935edcb3`.

## ADC and TMUX WRML assets

`TI_RTW0024A_nominal.wrl` SHA-256
`30417f0355b2a9bd2e913770b322e176692cc4d9c6ba91e897ec6be5f4e713f2` has
24 external terminal boxes plus one 2.6 x 2.6-mm EP. It agrees with TI
4222815/A p1: 4 x 4 nominal body, 0.8 max height, 0.5-mm pitch, nominal
0.4 x 0.25 terminals and nominal 2.6 x 2.6 EP. Z runs 0..0.8 mm with the
0.025-mm standoff midpoint. Its `modelY=-footprintY` convention correctly
places pin 1 upper-left. The documentation honestly distinguishes nominal
body geometry from 4.1-mm maximum courtyard geometry and identifies unswept
terminal/EP tolerances and omitted solder/mould detail.

`TI_YBH0009_C02_envelope.wrl` SHA-256
`c766433c89a9460662cf18c5d8c29aa94d7487a18dcda90d13588cb108c30f37` has
nine balls in 3 x 3 row-major footprint order, A1/pad 1 at `(-0.4,-0.4)` and
0.4-mm pitch. Its VRML Y negates footprint Y exactly once. TI 4228717/C p32
supports its 1.627 x 1.627-mm max body, 0.4-mm max total height, 0.23..0.27-mm
ball-diameter range and 0.135..0.195-mm standoff: the selected 0.25-mm and
0.165-mm values are the stated midpoints. The body spans Z=0.165..0.4 mm.
Its explicitly simplified balls and non-guaranteed body thickness are honestly
documented.

Both files use KiCad VRML's 2.54-mm unit and Z=0 seating plane. Floorplan
bindings match exactly ten refs, once each: `U_ADC_A`, `U_ADC_B`, and
`U_ISO1` through `U_ISO8`; no other ref is matched by either override.

## Final fixture smoke

Final fixture hashes: `models.kicad_pcb`
`d53217f4253d59ff24bca32de78e8d4aafc33565d0c33bae5bf9b162ba4685fe`, `top.png`
`81f8812ea4bf549081dadb8f0a2c1bd9d921e7e0728e981b6da88b71ac792e79`, and
`side.png` `aa5d8b49cd7ccff52415b827f0dde56cead95012e6b8b90d250e929482fd72c6`.
It renders RTW and YBH at 0 and 90 degrees, and C1210; both native render logs
end `Successfully created 3D render image`. This is only native-load and
signed-side smoke evidence, not registration or board acceptance.

## Narrow C1210 addition

`C_1210_3225Metric.step` SHA-256
`f8510481c5044113cf49b0fa6dd54ddab9224508bd6808e1afab8ef0cefdefc9` uses
millimetre STEP units. Its 48 `VERTEX_POINT`s bound to 3.2 x 2.5 x 2.5 mm.
The exact Murata sheet p2, SHA-256
`fd44194fdabc476650301c34e6e10eeb64d0c7cba90253b20af2371a07fd5ea8`, gives
3.2 +/-0.3 x 2.5 +/-0.2 x 2.5 +/-0.2 mm, so it is a numerically correct
generic nominal model. `Murata_GRM32E_1210.kicad_mod` changes only by one
model clause; native loading reports two pads, one model, and zero offset,
unit scale and zero rotation. It covers the reported current 42 refs. It must
remain labeled generic nominal geometry, not exact Murata CAD, a maximum
envelope, registration proof, or physical qualification.

## Actionable follow-up

No source correction is required. The next native candidate must still run the
owed full P-CRT/placement-collision and model identity/transform/
signed-mounted-side registration gates. Do not promote this review or fixture
smoke into any of those results.
