# Crow P1 native short diagnosis (read-only, 2026-09-23)

## Conclusion and source ownership

The seven J_JTAG `shorting_items` are real copper overlaps authored in **both** the exact KiCad footprint `projects/crow-usb-carrier-v1/03_src/lib/crow_usb_digital.pretty/Samtec_FTSH_105_01_L_DV_K.kicad_mod` and the TSX `FTSH2x5Land()` footprint in `projects/crow-usb-carrier-v1/03_tscircuit/src/crow_usb_digital.tsx`. They are neither an alias/net assignment failure nor a 90-degree generator rotation artifact. The board at `/tmp/crow-p1-floorplan-20260923/06_build/modular/p1_trial.kicad_pcb` loads J_JTAG at (228,50), rotation 90°, with the same 0.7 × 1.5 mm local rectangular pads as the library. Native pad centres 5/7/9 lie at (228,50.635), (226.73,50.635), (225.46,50.635) mm. Their 1.27 mm pitch and 1.50 mm copper extent along the pitch make each neighboring pair overlap **0.23 mm**. The reported 7-vs-9 GND/KEY_NC short and six other JTAG pairs follow directly.

The retained manufacturer source is `02_parts/FTSH-105-01-L-DV-K/Samtec_FTSH_footprint_revH.pdf`, SHA-256 `caa205b92560423f3b0aea9c69d6c38340d1b7f01b0655092994450e935edcb3`, Revision H (2019-08-27), sheet 1, Figure 1, for FTSH double vertical SMT. It specifies **1.27 mm contact pitch**, **0.74 mm land width along the pitch**, **2.79 mm land length transverse to the pitch**, and **6.86 mm total span across the two land rows**. Thus the transverse pad centre separation is 6.86 − 2.79 = **4.07 mm**. In the present footprint axes (contact rows vary in local Y), the drawing implies local pad size **2.79 × 0.74 mm**, column centres at **X = ±2.035 mm**, and row Y positions ±2.54, ±1.27, 0 mm. The 1.27 − 0.74 = **0.53 mm** along-row copper gap would remove these self-shorts. Preserve the present odd/even pin orientation, which matches the drawing's odd lower and even upper rows after the board's 90° rotation.

The smallest owning source repair is synchronized geometry in the TSX `FTSH2x5Land()` source **and** the exact KiCad library footprint, followed by normal regeneration and native footprint/pin/parity/DRC review. Pin numbers, signal assignments, and schematic/netlist electrical identity need no change for the pad-overlap repair. The part dossier's `KEY_NC` pin 7 is a separate project-owned electrical/keying claim. The retained Samtec Rev FX series drawing calls `-K` a keying option for FFSD and distinguishes it from an explicit omitted-position polarization option. It does not by itself prove that position 7 is absent, so do not remove or retarget pin 7 as a shortcut to clear the short.

## Other 32 native shorts

The DRC's 32 `shorting_items` are all local to a single footprint or its thermal vias:

| Class | Count | Direct cause in native board | Owning follow-up |
|---|---:|---|---|
| J_JTAG | 7 | 1.50 mm pad extent on 1.27 mm pitch, 0.23 mm overlap | Exact Samtec footprint and TSX land geometry above |
| U_FSYNC_FF1/FF2 | 10 | TI DCT SM8 pads are 1.20 mm tall on 0.65 mm pitch, 0.55 mm overlap | `TI_DCT0008A_SM8.kicad_mod` and `SM8_DCTLand()`; rederive manufacturer land dimensions |
| U_BCLK_INV, U_ADC_READY, U_ADC_PWR_BAD, U_ADC_CLOCK_OK, U_ADC_READY_BAD, U_ADC_DIGITAL_BAD | 12 | TI DCK SC70 pads are 1.00 mm tall on 0.65 mm pitch, 0.35 mm overlap | `TI_DCK0005A_SC70_5.kicad_mod` and `SC70_5Land()`; rederive manufacturer land dimensions |
| U_LDO | 3 | GND thermal vias overlap pads 6 (LDO_PGFB), 9/10 (N3V3_ADC) | `floorplan.yaml` thermal-via field / exact LDO geometry, with via clearance recheck |

The SC70 and SM8 candidate board pad positions/sizes exactly match their authored library/TSX footprint geometry at 0° rotation; this is a second source-geometry defect, not a rotation transform. No source was edited in this investigation. The P1 candidate remains diagnostic, not a DRC-clean board.
