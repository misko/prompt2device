# Crow native land geometry repair (2026-09-23)

Commit: 1af0fe89. Isolated worktree: /tmp/crow-native-pad-alias-20260923. This repair changes authored TSX footprint geometry, exact KiCad footprint geometry, and two scoped dossier claims; it does not change the schematic, pin labels, component selection, source nets, or generated board/netlist in the repository.

## Manufacturer evidence and repair

| Package / exact source | Retained drawing and PDF page | Result |
|---|---|---|
| Samtec FTSH-105-01-L-DV-K, J_JTAG | `02_parts/FTSH-105-01-L-DV-K/Samtec_FTSH_footprint_revH.pdf`, Rev H sheet/PDF p1 Figure 1 | 1.27 mm contact pitch, 0.74 mm pad width along pitch, 2.79 mm transverse pad length, 6.86 mm total opposing-pad span => centres 4.07 mm apart. Native local pad centres X±2.035, Y±2.54/±1.27/0; copper 2.79×0.74. Samtec marks odd row below even row. TSX Y is upward, so its Y signs reflect native. Pin7 KEY_NC retained. |
| TI DCK0005A SC70-5, six active U_* refs | `02_parts/SN74LVC1G04DCKR/SN74LVC1G04-SCES214.pdf`, SCES214AF PDF p35 land-pattern example | 0.65 mm pitch, 0.95×0.40 lands, 2.20 mm opposing centre distance. TI labels pin1 **upper left** in board layout; native pin1 Y=-0.65, TSX pin1 Y=+0.65. Old native was mirrored and old pads overlapped by 0.35 mm. |
| TI DCT0008A SM8, U_FSYNC_FF1/2 | `02_parts/SN74LVC2G74DCTR/SN74LVC2G74-SCES203Q.pdf`, Rev Q PDF p20 land-pattern example | 0.65 mm pitch, 1.10×0.40 lands, 3.80 mm opposing centre distance. TI labels pin1 **upper left**; native pin1 Y=-0.975, TSX pin1 Y=+0.975. Old native was mirrored and old pads overlapped by 0.55 mm. |
| TI DMQ0006A VSON6, U_1V8/U_3V3X/U_CORE | `02_parts/TPS62825DMQR/TPS6282x-SLVSEF9I.pdf`, PDF p33 land-pattern example | Retained asymmetric 0.50 mm pitch, left 0.60×0.25, right 1.00×0.25 lands; corrected native pin1 to upper left, retaining selected pin IDs and asymmetric X geometry. TSX already had opposite Y-up sign. |
| TI DCU0008A VSSOP8, U_ADC_OUT | `02_parts/SN74AUP3G34DCUR/SN74AUP3G34-SCES766C.pdf`, PDF p24 land-pattern example | Corrected native and explicit TSX land to 0.50 mm pitch, 0.85×0.30 lands, 3.10 mm opposing centre distance and pin1 upper left in native. The prior dossier/footprint 0.65 mm pitch was wrong; the selected part and all 8 pins remain. |
| TI DSE0006A WSON6, **latent digital footprint only** | `02_parts/TPS389030DSER/TPS3890-SBVS228A.pdf`, PDF p25 land-pattern example | Corrected dormant `crow_usb_digital` native Y chirality and distinct pin1 0.80×0.25 land (other five 0.70×0.25). TSX source pin1 width/X now agrees. Seven current TPS3890 refs bind to already-correct `crow_usb_analog:TI_DSE0006A_Exact`; this digital library cleanup does not explain a current P1 short. |

The native P1 diagnostic had 32 shorting-item reports: 7 J_JTAG pad-pad, 10 DCT pad-pad, 12 DCK pad-pad, and 3 U_LDO signal-pad/GND-via. The edited lands address the first 29 by source geometry; the U_LDO vias are a separate floorplan owner. No pin7 deletion or electrical retargeting was used. The Samtec `-K` pin7 mechanical disposition remains an independent physical review question.

## Electrical and validation evidence

- Manufacturer-backed `t_crow_native_lands_from_drawings` and `t_crow_native_ti_chip_orientation` load all six edited native footprints, extract selected dimensions from retained PDF pages, check pad sets and signed pin1 orientation, assert TSX/native Y reflection, and reproduce prior overlong/mirrored bad cases. Both pass.
- The eight directly run generator tests, including prior alias/identity tests and `t_places`, pass. Both edited dossiers parse as YAML; `git diff --check` passes.
- One final bounded `tsci build --disable-pcb src/crow_carrier.tsx` passed (1 circuit). Its circuit JSON is at `/tmp/crow-native-pad-alias-20260923-check/final-circuit.json`; the accepted baseline copy is `baseline-circuit.json`. All **4,280 electrically significant source records** are exactly equal. All **4,572 schematic records** are exactly equal. The 1,636 unnamed-trace warnings retain their identifiers and only display generated trace object numbers differently; source metadata hash changes as expected. Electrical source class counts are unchanged.
- No full regenerated native board or DRC-clean claim is made. The older P1 diagnostic candidate and failed evidence remain untouched.

## U_LDO floorplan proposal (not edited here)

Selected `LT3045EDD#PBF` retained `LT3045_RevD.pdf` PDF p29 DD package drawing gives EP11 1.65×2.38 mm, with adjacent 0.50 mm pitch signal pads. The original six 0.50 mm GND vias at local X±0.575/Y±0.94 sit exactly on EP copper bounds; the P1 trial reported three via-to-pad shorts at pads 6, 9 and 10. A **trial** six-via field at local X±0.35/Y[-0.60,0,+0.60] leaves 0.225 mm horizontal and 0.34 mm vertical EP copper margin to the 0.50 mm via body. Its nearest outer signal copper has about 0.475 mm horizontal separation. The floorplan owner must check the exact new placement, all other pads/footprints, hole and mask rules, fab via process, EP solder/thermal behavior and DRC before adopting it.

Remaining physical review: the old footprint silk rectangles may need clearance adjustment after land growth, and the -K keyed mate/pin7 claim still needs independent exact-part review. No routing or fabrication status is implied.
