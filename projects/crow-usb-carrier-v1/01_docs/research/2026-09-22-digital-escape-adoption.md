# Selected digital escape calculations

Authority: source commit `124cc62128a07e5cfd18ae07d02ecff90975f0c9`, retained primary package/land drawings, exact selected footprints, `skills/kicad-pcb/scripts/escape_check.py`, and `skills/kicad-pcb/references/fab_tiers.yaml`.

The patch adds `escape` blocks to 13 selected digital/control/oscillator dossiers and repairs the unsupported style vocabulary in the existing TPD2EUSB30 block. This closes all 14 owned failures from the selected 85-part audit: 20 selected failures minus LT3045, TPS26625, the three TPS62825 variants, and TPSM63603 assigned to the independent power-package owner. `BC847B_215` and `IS25WP032D-JBLE` appeared only in the 92-dossier historical sweep and are excluded by the selected audit.

| Part | Primary/package geometry and exact-footprint cross-check | Checker inputs | Declared tier | Result |
|---|---|---|---|---|
| ASFL1-24.576MHZ-EC-T | Abracon ASFL1 p.2; 5.0 × 3.2 mm four-pad module; exact pad centers ±1.27 × ±1.10 mm | `module`, pitch 2.20 mm, worst side 2 | `jlc_2layer_default` | Unconditional |
| FA-238 24.0000MD30X-W5 | Epson Q22FA23801885 §4; exact pad centers ±1.20 × ±0.95 mm | `passive`, pitch 1.90 mm, worst side 2 | `jlc_2layer_default` | Unconditional |
| FTSH-105-01-L-DV-K | Samtec FTSH-DV Rev H; 1.27 mm 2×5 grid; exact footprint has five pads per column | `connector`, pitch 1.27 mm, worst side 5 | `jlc_2layer_default` | Unconditional |
| SN74AUP3G34DCUR | TI SCES766C DCU0008A; exact VSSOP footprint has four 0.65 mm-pitch leads per side | `leaded`, pitch 0.65 mm, worst side 4 | `jlc_2layer_default` | Unconditional |
| SN74AXC4T245PWR | TI SCES877 PW0016A; TSSOP-16 has eight 0.65 mm-pitch leads per side | `leaded`, pitch 0.65 mm, worst side 8 | `jlc_4layer_advanced` | Standard is conditional on `escape-corridor`; none is declared/proven, so unconditional advanced is required |
| SN74LVC1G04DCKR | TI SCES214AF DCK0005A; exact SC70 footprint has three leads on the worst side | `leaded`, pitch 0.65 mm, worst side 3 | `jlc_2layer_default` | Unconditional |
| SN74LVC1G125DCKT | TI SCES223 DCK0005A; exact SC70 footprint has three leads on the worst side | `leaded`, pitch 0.65 mm, worst side 3 | `jlc_2layer_default` | Unconditional; DCKT/DCKR tape quantity does not change DCK geometry |
| SN74LVC1G332DBVR | TI SCES489E DBV0006A; selected SOT-23-6 footprint has three 0.95 mm-pitch leads per side | `leaded`, pitch 0.95 mm, worst side 3 | `jlc_2layer_default` | Unconditional |
| SN74LVC2G74DCTR | TI SCES203Q DCT0008A; exact SM8 footprint has four 0.65 mm-pitch leads per side | `leaded`, pitch 0.65 mm, worst side 4 | `jlc_2layer_default` | Unconditional |
| TPD2EUSB30ADRTR | TI SLVSAC2G DRT page 27; existing dossier records 0.70 mm data pitch and three 0.30 mm lands | Existing block corrected from unsupported `sot` to checker-supported `leaded`; pitch 0.70 mm | `jlc_2layer_default` | Unconditional; no geometry or tier change |
| TPS3808G09DBVR | TI SBVS050N DBV0006A; selected SOT-23-6 footprint has three 0.95 mm-pitch leads per side | `leaded`, pitch 0.95 mm, worst side 3 | `jlc_2layer_default` | Unconditional |
| TPS389018DSER | TI SBVS228A DSE0006A; exact WSON footprint has three 0.50 mm-pitch bottom lands per side | `dfn`, pitch 0.50 mm, worst side 3 | `jlc_4layer_advanced` | Standard is conditional on `outward-only-local`; not proven, so unconditional advanced is required |
| TPS389030DSER | Same DSE0006A geometry as TPS389018 | `dfn`, pitch 0.50 mm, worst side 3 | `jlc_4layer_advanced` | Standard is conditional on `outward-only-local`; not proven, so unconditional advanced is required |
| XU316-1024-TQ128-C24 | XMOS XM-014532-PC TQ128; exact footprint has 32 leads per side at 0.40 mm pitch | `leaded`, pitch 0.40 mm, worst side 32 | `jlc_4layer_advanced` | Standard is conditional on `escape-corridor`; none is declared/proven, so unconditional advanced is required |

`escape_check.py 02_parts/*/part.yaml` reports `P-ESC PASS: 14/14 part.yaml graded, 0 problem(s)`. A semantic comparison after removing the root `escape` key confirms all device identity, electrical, pins, footprint, layout, and sourcing facts are byte-semantically unchanged. TPD2EUSB30 changes only `escape.style`; its existing pitch, tier, and checked provenance remain unchanged.

This is source feasibility admission only. It does not prove placed-board escape, routing, thermal-via implementation, connectivity, DRC, or manufacture at current vendor capability floors.

## Root adoption

Applied at661bdb90. Root semantic comparison confirms14/14 dossiers preserve every non-escape field. Owning selected-BOM escape check now has6problems across85dossiers, down from20. This closes14 malformed/missing records but does not close standard-process admission: four repaired digital parts declare unconditional advanced requirements, and LT3045 already declared advanced. The selected board remains jlc_4layer_standard pending genuine geometry/process resolution. Source TSX, nets, BOM identities and footprints are unchanged. Root evidence:06_build/verification/digital-escape-adoption.

The root declared-tier inventory finds eight selected MPNs above the board tier in total: LT3045EDD#PBF, TPS389018DSER, TPS389001DSER, TMUX2821DSGR, CS5308P-DNR, XU316-1024-TQ128-C24, SN74AXC4T245PWR and TPS389030DSER. Three of these pre-existing requirements were outside the malformed-record repair set. All eight must be resolved honestly before process admission.
