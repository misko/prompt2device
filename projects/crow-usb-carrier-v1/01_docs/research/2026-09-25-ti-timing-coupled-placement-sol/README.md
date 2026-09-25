# Isolated coupled TDM P2 placement probe — 2026-09-25

**A geometric candidate exists; P1 remains unproved.** `build_candidate.py` replays one coupled edit from the SHA-bound 15-part board, writes `candidate.kicad_pcb` (SHA-256 `53e6fb7809910946c36053e7ceeb77e7fc866456ff77775ed4c59b3e49278555`) and `result.json`, and rejects input drift, fixed-ref movement, new native courtyard/body intersections, new F.Cu pad-bbox intersections, new source-region envelope violations, worsened XU bypass pad-1-to-owning-pin distances, or a rough mouth below demand. No tracks were added, no copper was filled, and no canonical board/source was changed.

The original [three-mouth screen](../2026-09-25-ti-timing-mouth-screen-sol/README.md) was short at all exits. The new candidate moves C_ADC_I2C_B from `(172.8,95.0,0°)` to `(172.8,98.6,0°)` and shifts U_XU with all 25 nearby XU supply/USB capacitors north by 0.2 mm as a rigid group. Four capacitors then receive coupled local placement: C_XU_VDD_105 `(196.5,96.3,180°)`, C_XU_VDD_106 `(198.6,99.1,180°)`, C_XU_VDD_14 `(207.8,109.5,-90°)`, and C_XU_VDDIO_17 `(209.0,109.5,-90°)`. This moves 27 P2 refs. All 27 P1-fixed refs retain their native positions. Reference legends on these moved refs and adjacent U_ADC_I2C_XLATE are put on F.Fab; a final silk layout remains P2 work.

Moving U_XU with its local supply group is required by the xmos_core south face at y=110.5: the rotated 1.91-mm-tall C14/C17 courtyards need a 0.05-mm gap to the XU courtyard and fit with only 0.045 mm to the region edge. Keeping U_XU at its prior y=100.0 would make those two conditions contradictory. The new XU centre is `(208.5,99.8)`.

| Native full-envelope mouth (board mm) | Connected aperture | Rough 0.45-mm slots / demand |
| --- | ---: | ---: |
| Translator west `[172.5,94.2,174.305,96.8]` | 2.600 mm | 5 / 4 |
| XU west DATA `[197.5,97.1,199.805,98.5]` | 1.400 mm | 3 / 1 |
| XU south MCLK/BCLK/FSYNC `[209.5,108.5,212.5,109.7]` | 2.995 mm | 6 / 3 |

The candidate preserves or improves every moved numeric XU bypass owner distance. The decisive changes are C105 **4.8185→3.8898 mm**, C106 **2.8328→2.5882 mm**, C14 **1.8136→1.5861 mm**, and C17 **2.5162→1.5861 mm**. The other translated capacitors keep their offset to U_XU exactly. `result.json` records every move, owning region, distance, exact timing pad centre/bbox, aperture, and saved zone state. No new native courtyard/body or F.Cu pad-bbox overlaps were found.

Native KiCad DRC on the generated board reports **724 violations and 499 unconnected items**, versus **730 and 499** on the pinned baseline. Both have 224 clearance violations; the candidate has 19 silk-over-copper and 11 silk-overlap warnings versus baseline 21 and 15. This is a comparative screen, not a DRC pass. The saved In1.Cu GND zone is unfilled. The rough aperture counts do not prove effective per-net width/clearance, exact escape from the eight pads through their packages, a connected staged path between regions, or a continuous filled reference. Those checks are the next bounded work before any P1 corridor or route credit.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-timing-coupled-placement-sol/build_candidate.py
kicad-cli pcb drc -o /tmp/crow-timing-candidate-drc.txt projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-timing-coupled-placement-sol/candidate.kicad_pcb
kicad-cli pcb drc -o /tmp/crow-timing-baseline-drc.txt projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb
```
