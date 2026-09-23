# Murata C84494 capacitor bank — engineering candidate, review pending

This candidate replaces thirteen unstocked TDK CKG57KX7R1E476M335JH J-lead positions with ten Murata GRM32ER71A476KE15L 1210 ceramics per board. Direct JLC exact-code/MPN snapshot on 2026-09-23 showed 56,478 C84494 units, versus 50 needed for five boards. This is catalog stock, not reserved PCBA allocation. The revised copper footprint transcribes Fig. 3 of the exact June 2026 Murata reference sheet: 5.0 mm outer span, 2.2 mm inner gap, 2.9 mm pad height. Stencil, courtyard, placement, and assembly review remain open. The former TDK lands cannot be reused.

| Bank | Refs retained | Murata exact-base-part typical simple-model screen at -55 C | Conservative bound recorded in power_tree.yaml |
| --- | --- | --- | --- |
| TPSM63603 5 V | C_OUT1/2/3 | 14.7 uF each at both 5.05 V and 5.099 V | 3 × 47 × 0.31 × 0.90 × 0.875 = 34.42 uF >25 uF |
| TPS62825 3.3 V | C_U_3V3X_OUT_1 | 16.9 uF at 3.38 V | 47 × 0.35 × 0.90 × 0.875 = 12.95 uF >10 uF |
| TPS62825 1.8 V/core | C_U_1V8_OUT_1, C_U_CORE_OUT_1 | 18.4 uF at 1.818 V; 18.7 uF at 0.92 V | Each conservatively uses same 12.95 uF >10 uF |
| LT3045 input | C_LDO_IN | 14.7 uF at both 5.05 V and 5.099 V | 11.48 uF >4.7 uF |
| LT3045 output | C_LDO_OUT_1/2 | 16.9 uF each at 3.38 V | 25.91 uF >10 uF |
| OPA reservoir | C_OPA_BULK | 16.9 uF at 3.38 V | Advisory decoupling, no invented regulator minimum |

The Murata SimSurfing simple models are exact *base-part* small-signal typical values, not guaranteed lot limits. The -55 C values already include temperature and DC bias. The additional 10% tolerance and 12.5% lifecycle factors are project engineering reserves, not manufacturer guarantees. The 5.099 V run explicitly covers the possible TPSM63603RDHR replacement's worst-case output; the source power contract still names TPSM63603V5RDHR and its current ceiling. Approval-sheet or measured lot data and independent source review are owed before acceptance.

The three TPS62825 second capacitors were removed because TI SLVSEF9I Table 8-3 marks **0.47 uH + 47 uF nominal** for TPS62825, while 100 uF is blank in that row. The resulting LC nominal pair is still subject to replacement-inductor and full-distribution loop stability, startup, and load-step testing. The TPSM63603 141-uF nominal bank likewise needs startup/load-step verification beyond its 25-uF effective floor.

ADI LT3045 Rev. D requires an assembled output network with ESR <20 mΩ and ESL <2 nH. At 125 C and 3.38 V, Murata's typical model gives 0.657 nH and 2.13 mΩ per part; an ideal symmetric pair gives 0.3285 nH and 1.065 mΩ. **P3 quiet_power must prove shared pad, via, trace, ground-return and OUTS interconnect ESL <1.6715 nH**, with Kelvin OUTS at the shared output capacitor/load node and output-cap ground joined to SET-cap ground. The sum must remain strictly below 2 nH. These model coefficients are not maximums, and no physical extraction, assembled measurement, or first-article stability pass is claimed.

Primary references: [Murata exact reference sheet](https://pim.murata.com/asset/pim4/ceramicCapacitorSMD/GRM32ER71A476KE15-04CA-EN_PDF_CERAMICCAPACITORSMD?lastModifiedDatetime=20260730173643), [Murata SimSurfing](https://ds.murata.com/simsurfing/mlcc.html?oripartnumbers=%5B%22GRM32ER71A476KE15L%22%5D&partnumbers=%5B%22GRM32ER71A476KE15%22%5D), [ADI LT3045 Rev. D](https://www.analog.com/media/en/technical-documentation/data-sheets/lt3045.pdf), [TI TPS62825 SLVSEF9I](https://www.ti.com/lit/ds/symlink/tps62825.pdf), [TI TPSM63603 SLVSFS5A](https://www.ti.com/lit/ds/symlink/tpsm63603.pdf). Retained Murata model captures: `02_parts/GRM32ER71A476KE15L/models/` (the broader raw acquisition remains in `/tmp/crow-capbank-evidence-20260923/`); calculation dossier: `/tmp/crow-capbank-proof-20260923.md`. Original raw JLC snapshot: `/tmp/crow-jlc-adc-20260923/raw/C84494.json`.
