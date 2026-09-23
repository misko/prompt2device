# Independent passive and clock source-model review

**Subject:** adopted commit `36330a351f5f697af1af58049429946948547df9` (same reviewed source tree as isolated commit `1002f5bc9e7bc8701de9a30f9b82da120cb20d76`), compared with base `723d2746`.

## Verdict

**PASS for the bounded source-model scope.** Four drawing-derived VRML assets serve exactly `L_U_CORE`, `L_U_1V8`, `L_U_3V3X`, `F_IN`, `Y_AUDIO`, and `Y_XU`. Each footprint diff adds one zero-offset, unit-scale, zero-rotation model clause. Removing it restores the parent footprint byte-for-byte: pads, pin identities, copper, paste/mask, silk, fab and courtyard geometry did not drift.

This is not a Crow PCB, placement, P1, DRC, MODEL-SELF/MODEL-REG, full coverage, runtime, assembly or release result.

| Exact part / refs | Model | Drawing-backed geometry check | Result |
|---|---|---|---|
| Coilcraft `XFL4015-471MEC` / three `L_U_*` | `Coilcraft_XFL4015_471MEC_max-envelope.wrl` | Doc 769-2 p2: 4.0 +/-0.3 plan and 1.60 max height. Model union 4.30 x 4.30 x 1.60 mm; 2.37-mm contact pitch and 0.82 x 3.25 contacts overlap native 0.98 x 3.4 lands. | PASS |
| Littelfuse `0451004.MRL` / `F_IN` | `Littelfuse_451_Nano2_2410_max-envelope.wrl` | 451/453 p4: 6.10 +/-0.20 x 2.69 +/-0.25 plan and stated 1.45 height. Model union 6.30 x 2.94 x 1.45 mm; end caps overlap both lands. Height is correctly stated as non-maximum. | PASS |
| SCTF `SX5M24.576M20F30TNN` / `Y_AUDIO` | `SCTF_SX5M_5032_max-envelope.wrl` | SCTF20215M027 B01 p4: 5.0 +/-0.1 x 3.2 +/-0.1 x 1.2 +/-0.15. Model envelope 5.10 x 3.30 x 1.35 mm; terminals follow the 2.54 x 2.30-mm land grid and overlap. | PASS |
| YXC `X322524MOB4SI` / `Y_XU` | `YXC_YSX321SL_3225_max-envelope.wrl` | YSX321SL p1: 3.20 +/-0.10 x 2.50 +/-0.10 x 0.70 +/-0.10. Model envelope 3.30 x 2.60 x 0.80 mm; terminals overlap the native 2.2 x 1.7-mm-pitch land grid. | PASS |

Primary-PDF SHA-256: Coilcraft `6535ab70d0ef65ba03d4b0800e206fc7867f26464e2d9dfd5dd931a2bcb0c7c1`; Littelfuse `e4f66814c90d70b283a5962080711f26554d974373a550958bda772dfdaf1bf9`; SCTF `c10be001568c12e27692d77260f88cd6cd55611b92835a34a2031d98da835804`; YXC `8448fb1ea37694ca77ad3d9579b5d10921746ccd8b3ff79349ef61322453340c`.

Model SHA-256: Coilcraft `9c6031cf0c1ae34a4bacc209c1afa8b60f5a5d0ac282c419abdadb6dfd2e6c39`; Littelfuse `186128e78c23909f184d9efa9fe207c4bd3bfd4622e812dcfd6d33479cb1f3bc`; SCTF `f9fddb51dffece51071c993cdde786c6d9f3cc5ffdcf2feba7064fa719432dcd`; YXC `d54038a6ec3e162ccf9219f137582013d850b5e6db5b1f09dc836aa148bafaf0`.

## Coordinate and native smoke review

All model clauses have zero offset/rotation and unit scale. Native `pcbnew.FootprintLoad` reports 2/4/4/2 pads and one model for Coilcraft/SCTF/YXC/Littelfuse. The fixture contains each type at 0 and 90 degrees; native top/front renders show all eight bodies above the front-side board. Fixture SHA-256: board `02c1c5fd1e2578209a8a7da06faf859c656ee1cecaed4bdde53f8368257ed1a1`; top `7f550329f95978628359f72b7ddbe110c4a27191d66640d26b45797321531dcc`; front `1bc023dd4667c1da12896829571ace31f52103470f34dfbc826966e5374346c9`.

SCTF and YXC numerical terminal placement and rotation are correct: model Y is the inverse of native footprint Y, placing each model pin 1 on the physical side of native pad 1. The adopted commit's exact WRL bytes contain no per-terminal “source Y down” phrase; their header accurately states “model Y is opposite footprint local Y.” The earlier claimed comment-label action was spurious and is withdrawn.

## Limits

The models are properly limited to project-authored rectangular envelope geometry, rather than vendor CAD. They omit terminal curves/chamfers, solder, actual markings, manufacturing distributions and mounted coplanarity. Later generated-board review must independently run full-board identity, transform, same-camera and signed-mounted-side registration checks.
