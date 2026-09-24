# Isolated ADC/TDM post-anchor probe

This is one source-controlled local placement test, not a P1 route, corridor allocation, or accepted placement. The canonical `floorplan.yaml`, PCB, requirements, and P1 dispatch were untouched. I copied the live source, parts, and netlist into `/tmp/crow-p1-adc-sol-20260924/` and added exactly these three `placement.post_anchors` to that copy:

```yaml
C_FSYNC_OR: [172.6, 100.9, 0]       # from (169.6,95.9)
C_XU_VDD_104: [198.6, 94.0, 0]   # from (198.6,96.0)
C_XU_VDD_106: [198.6, 103.2, 0]  # from (198.6,98.2)
```

The native generator placed 569 footprints with zero pad collisions and zero fixed courtyard overlaps. Comparing exact native poses with the baseline shows only those three moved; U_XU, U_USB_ESD, USB support, PLL, connectors, ADCs, and U_TDM_XLATE retained their poses. All 1,810 `(ref,pad) → net` identities match the baseline board generated from the same source netlist. The unfilled candidate board SHA-256 was `54f2ebfc94a849dd3224996c14b4b18dc7c21fa92737b84bdf79905741415f70`; after the native DRC zone refill/save it is `068e1c2f377420a3108329c3f53479f3b1b17bb5fcb4e1d99e1187b1e36b0939`.

The same `p1_corridor_capacity.py` F.Cu body/pad obstacle screen on the moved board gives:

| Screening rectangle `[x0,y0,x1,y1]` mm | Baseline | Moved board | Demand | Result |
|---|---:|---:|---:|---|
| ADC→TDM broad `[140.000,92.500,174.350,111.000]` | 1.030 mm / 2 slots | 1.105 mm / 2 slots | 3 × 0.45 mm | Still short by one raw slot. |
| TDM→XU narrow `[182.475,94.000,199.825,100.000]` | 1.515 mm / 3 slots | 2.615 mm / 5 slots | 4 × 0.45 mm | Raw width screen clears, but no legal four-net endpoint fanout or pocket proof. |

The ADC connected path drops from 2.420 mm to 1.105 mm at x≈162.890. Immediately before that point the free central opening is y=97.685..100.105 mm. `R_ADC_OK_BOT` begins at x=162.845 and occupies y=98.405..99.395, splitting that opening into 0.720 and 0.710 mm. The northern opening between `Y_AUDIO` (edge y=94.075) and `C_ADC_I2C_B` (edge y=95.415) is only 1.340 mm locally, 0.010 mm below the nominal 1.350 mm demand even before edge clearance; its connected approach is narrower. A future ADC geometry change must move or re-partition at least this x≈162.845 transition and prove a full 1.35-mm connected path through the remaining obstacles, while preserving both ADC branches and the dispersed R_BCLK, R_FSYNC, R_ADC_DATA_PD, and translator endpoints. Merely moving `C_FSYNC_OR` did not solve it.

The TDM narrow rectangle's minimum now occurs at x≈195.653: `C_XU_VDD_105` and `C_XU_VDDIO_109` leave y=94.000..96.615, 2.615 mm raw. It still ends at the west edge of U_XU, whereas AUDIO_MCLK/BCLK/FSYNC terminate on the south edge at y=107.662 and DATA terminates on the west edge at x=200.838. Thus the four exact pad/net pockets and shared fanout are unresolved. The two moved decouplers also need electrical proximity and return review; a raw opening cannot justify their new positions.

Full native `kicad-cli pcb drc --severity-all --refill-zones --all-track-errors --save-board --schematic-parity --format json` reports 269 clearance violations and 499 unconnected items. The baseline generated from the unmodified source has the same 269 violation identities and 499 unconnected items; this probe added zero DRC findings. KiCad reported that schematic parity could not run without a fully annotated schematic in the isolated copy, so the direct 1,810-pad source-board parity above is the supported parity claim. After refill the In1.Cu GND zone reports `IsFilled=true` with nine native filled polygons, but continuous reference beneath the proposed lanes has not been sampled or proven. `adc_timing_xmos_bundle` remains `INCOMPLETE` with null geometry.
