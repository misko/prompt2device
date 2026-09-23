# Crow USB carrier P1 model-binding census (read-only, 2026-09-23)

Evidence: authored `projects/crow-usb-carrier-v1/03_src/floorplan.yaml` in `/home/mouse9911/gits/circuits-worktrees/crow-usb-carrier-v1-20260922`; native P1 trial `/tmp/crow-p1-repaired-trial-20260923/04_kicad/crow_carrier.kicad_pcb`; trial `06_build/modular/model_coverage.json`; exact part YAMLs and native footprint files under the project. I read native KiCad footprint IDs, model URIs, and footprint `Manufacturer Part Number` fields with pcbnew. No board or source files were changed.

## Finding

The native coverage report says **495/568 fitted footprints resolved, 73 missing** (63 with no model entry and 10 with an unresolvable URI). This checks file existence, **not whether the model represents the current MPN/package**. Ten of its 495 “resolved” footprints are false confidence: U_ADC_A/B resolve a 6×6-mm, 48-terminal Cirrus CS5308P QFN body while their fitted part is TI TLV320ADC6140IRTWT in RTW0024A 4×4-mm WQFN24; U_ISO1–8 resolve an 8-terminal, 2×2-mm TI DSG body while their fitted part is TMUX4827YBHR in YBH0009-C02 1.607-mm DSBGA9, 0.4-mm pitch. Both stale files are explicitly source derived geometry, not manufacturer CAD. The native ADC and ISO footprints have no own model entry: the floorplan overrides supply these wrong bodies.

## All authored floorplan overrides (36 native footprints)

| Refs / count | Native MPN; native footprint | Authored override and trial resolution | Identity judgment / smallest source repair |
|---|---|---|---|
| J1–J8 / 8 | 615008160221; `crow_usb_analog:Wurth_615008160221_RJ45` | `wurth/J_Wurth_WR-MJ_615008160221.step`; resolves | Same connector identifier; retain. This is a local Wurth-named STEP, without a separate manufacturer-registration claim in this audit. |
| C_A1N/P–C_A8N/P / 16 | `R82DC4100CK60J` (1-uF film capacitor); `Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm` | `kicad/C_Rect_L7.2mm_W5.0mm_P5.00mm.step`; resolves | Package-family match to native footprint; retain. This is a KiCad package model, not a manufacturer registered model for the KEMET part. |
| U_ADC_A/B / 2 | `TLV320ADC6140IRTWT`; `crow_usb_analog:TI_RTW0024A_WQFN24_4x4_EP2.6` | `derived/Cirrus_CS5308P_QFN48_nominal.wrl`; resolves | **Wrong device and package.** Replace the line at floorplan ~851 with `${KICAD10_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm.step` as an **existing generic package model**, then check orientation/height against TI RTW0024A before using for clearance. This exact KiCad model file exists locally; its 4×4, 24, 0.5, 2.6 dimensions match the exact TI package/footprint dossier. It is **not a TI registered exact-part CAD model**. Alternatively remove the stale override until a validated model is sourced, which correctly makes these two entries uncovered. Do not relabel the Cirrus file. |
| U_ISO1–U_ISO8 / 8 | `TMUX4827YBHR`; `crow_usb_analog:TI_YBH0009_C02_TMUX4827` | `derived/TI_DSG0008A_nominal.wrl`; resolves | **Wrong 8-terminal package for 9-ball BGA.** Delete the floorplan override line at ~861 (retain match/placement rule if needed); these then honestly have no model. No exact 1.607-mm YBH0009 3×3 P0.4 model was found in the project or installed KiCad 10 library. The installed `WLCSP-9_1.21x1.22mm_Layout3x3_P0.4mm.step` has matching ball grid but the wrong body size; the installed `BGA-9_1.6x1.6mm_Layout3x3_P0.5mm.step` has the wrong pitch. Neither is an exact replacement. A source-owned **dimension derived nominal** model could be made from retained TI SCDS457B p.32 drawing (body D/E 1.587–1.627 mm, height ≤0.4 mm; 3×3 0.4-mm pitch) with documented provenance, then bound explicitly; it must never be described as manufacturer CAD. |
| U_AUDIO, U_PWR / 2 | `TPS389001DSER`; `crow_usb_analog:TI_DSE0006A_Exact` | `derived/TI_DSE0006A_nominal.wrl`; resolves | Current device/package family matches. The same model is already in the source native footprint and appears on five other TPS389001DSER footprints. The two floorplan overrides are redundant but not stale. Keep for parity or delete only if normal footprint inheritance is verified. Model itself says source-derived, not manufacturer CAD. |

The native trial also has five other fitted TPS389001DSER references (`U_1V8_OK`, `U_ADC_1V8_OK`, `U_ADC_3V3X_OK`, `U_ADC_OK`, `U_XU_3V3_OK`) using `TI_DSE0006A_nominal.wrl` from the native footprint, not from the floorplan override. Thus the current board has seven DSE nominal model instances. The source `TI_DSE0006A_Exact.kicad_mod` has the model binding; the current ADC and YBH native footprint files do not.

## Native unresolved-model census by exact MPN and footprint

Each row names the native footprint and fitted board MPN field, not merely the electrical value. All 73 fitted-footprint failures are accounted for.

| Count | Exact MPN; native footprint | References | Failure |
|---:|---|---|---|
| 42 | `GRM32ER71A476KE15L`; `crow_usb_power_aux:Murata_GRM32E_1210` | `C_ADC_AC[1..8][N/P][1/2]` (32); `C_LDO_IN`, `C_LDO_OUT_1/2`, `C_OPA_BULK`, `C_OUT1/2/3`, `C_U_1V8_OUT_1`, `C_U_3V3X_OUT_1`, `C_U_CORE_OUT_1` (10) | No model entry |
| 8 | `RT0603BRD0744K2L`; `crow_usb_analog:Yageo_RT0603_NominalBody` | `R_SPOKE_ILIM1..8` | Broken project URI `kicad/R_0603_1608Metric.step` |
| 4 | `SN74LVC1G04DCKR`; `crow_usb_digital:TI_DCK0005A_SC70_5` | `U_ADC_DIGITAL_BAD`, `U_ADC_PWR_BAD`, `U_ADC_READY_BAD`, `U_BCLK_INV` | No model entry |
| 3 | `TPS62825DMQR`; `crow_usb_digital:TI_DMQ0006A_VSON6` | `U_1V8`, `U_3V3X`, `U_CORE` | No model entry |
| 3 | `XFL4015-471MEC`; `crow_usb_digital:Coilcraft_XFL4015_471MEC` | `L_U_1V8`, `L_U_3V3X`, `L_U_CORE` | No model entry |
| 2 | `SN74LVC1G125DCKT`; `crow_usb_digital:TI_DCK0005A_SC70_5` | `U_ADC_CLOCK_OK`, `U_ADC_READY` | No model entry |
| 2 | `SN74LVC2G74DCTR`; `crow_usb_digital:TI_DCT0008A_SM8` | `U_FSYNC_FF1/2` | No model entry |
| 1 | `0451004.MRL`; `crow_usb_power_aux:Littelfuse_451_Nano2_2410` | `F_IN` | No model entry |
| 1 | `43650-0200`; `crow_usb_power_aux:Molex_43650-0200` | `J_PWR` | Broken `${KICAD10_3DMODEL_DIR}/Connector_Molex.3dshapes/Molex_Micro-Fit_3.0_43650-0200_1x02_P3.00mm_Horizontal.step` URI: file absent from installed KiCad 10 library |
| 1 | `FTSH-105-01-L-DV-K`; `crow_usb_digital:Samtec_FTSH_105_01_L_DV_K` | `J_JTAG` | No model entry |
| 1 | `RT0603BRD0730K9L`; `crow_usb_analog:Yageo_RT0603_NominalBody` | `R_PWR_TOP` | Same broken project resistor URI |
| 1 | `SN74AUP3G34DCUR`; `crow_usb_digital:TI_DCU0008A_VSSOP8` | `U_ADC_OUT` | No model entry |
| 1 | `SX5M24.576M20F30TNN`; `crow_usb_digital:SCTF_SX5M_5032` | `Y_AUDIO` | No model entry |
| 1 | `TCA9406DCUR`; `crow_usb_digital:TI_TCA9406_DCU0008A_VSSOP8` | `U_ADC_I2C_XLATE` | No model entry |
| 1 | `TPSM63603RDHR`; `crow_usb_power:TPSM63603RDHR_RDH0030A` | `U_BUCK` | No model entry |
| 1 | `X322524MOB4SI`; `crow_usb_digital:YXC_YSX321SL_3225_4Pin` | `Y_XU` | No model entry |

`R_PWR_TOP` and `R_SPOKE_ILIM1..8` can be repaired with one source native footprint model URI replacement: `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0603_1608Metric.step`, which exists locally and is the same stock KiCad model used by other resolved 0603 resistors. This is a package model, not an exact manufacturer part body. `J_PWR` needs a vetted exact connector STEP or appropriately identified package substitute; simply pointing at a nonexistent stock KiCad path will never resolve. Other no-entry groups require source footprint model assignments or an explicit, documented decision that they remain uncovered; `model_coverage.json` alone cannot supply identity evidence.

## Repair acceptance

The smallest identity repair is one ADC line replacement and one ISO line deletion/replacement in source floorplan; then regenerate the native board and rerun coverage. Any checker should also compare current MPN/package against model provenance or an explicit reviewed mapping, since file-resolution success masks the ten stale bindings. If the ISO override is removed and ADC uses the installed generic QFN model, expected raw resolution is 487/568 before other repairs (495 + 0 − 8); if both stale overrides are removed it is 485/568. These are accounting projections, not a generated board result. The separate 16 missing same-side courtyard issue is unaffected.
