# Native test: 16 mm southern audio receiving cell

**Reject as an electrical placement.** This reproducible research packet tests Terra's `85d8bb18` exact `[145,140,190,156]` receiving-cell coordinates against the TI diagnostic board SHA-256 `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`. It alters an isolated temporary board only. Run from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-south-audio-cell-probe-sol/build_probe.py > projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-south-audio-cell-probe-sol/receipt.json
```

The copy extends only the existing south `Edge.Cuts` line and its two incident endpoints from y=140 to 156 mm, yielding **220 × 136 mm**. It moves `Y_AUDIO` to `(156.481,143.361)`, `C_ADC_I2C_A` to `(170.435,140.485)`, and `C_ADC_CLOCK_OK` to `(172.461,153.789)` at unchanged orientation. Reloaded KiCad `GetBoundingBox(True, True)` gives the complete respective envelopes `[145.000,140.000,167.962,145.436]`, `[168.000,140.000,174.896,146.730]`, and `[168.000,146.730,174.896,155.797]`. These are contained in the cell and create zero new full-envelope overlap pairs. All 27 fixed poses and every pad number/net/layer identity are unchanged. Channel-7 and channel-8 local ports are footprint-clear. The lower TDM/XU neck retains Terra's `C_XU_VDD_105` and `C_XU_VDDIO_109` full-envelope intersections. Native `kicad-cli pcb drc --severity-all --refill-zones --format json` reports **0→0 violations** and **499→499 unconnected items**. This is a DRC delta on an unrouted board, not route acceptance.

| Related native pad centers | Baseline mm | South-cell mm | Increase mm |
| --- | ---: | ---: | ---: |
| `Y_AUDIO.3` clock output → `U_TDM_XLATE.11` | 16.566 | 51.870 | +35.304 |
| `Y_AUDIO.4` supply → `C_AUDIO_OSC.1` bypass | 6.876 | 55.088 | +48.213 |
| `C_ADC_I2C_A.1` bypass → `U_ADC_I2C_XLATE.3` supply | 13.606 | 44.999 | +31.394 |
| `C_ADC_CLOCK_OK.1` bypass → `U_ADC_CLOCK_OK.5` supply | 12.966 | 76.745 | +63.779 |

The oscillator bypass and two IC bypasses are no longer local. Also, the source board's `In1.Cu` GND zone polygon ends at **y=140 mm**; this new cell at y=140..156 has no allocated reference plane. Refilled DRC cannot establish return continuity there. The geometric pass therefore does not justify an outline change or a source-cell acceptance.

**Best measured alternate for continued P2 work:** the prior [no-outline three-part native placement probe](../2026-09-25-ti-adc7-placement-probe-sol/README.md) keeps the related-pad distances to **26.205 / 35.742 / 17.190 / 12.596 mm** in the same row order, clears both local ports, and adds no full-envelope collision. It still fails full physical-cell ownership and oscillator bypass locality; it is a *less harmful geometric witness*, not a release candidate. Repack the existing audio/TDM and adjoining P2 cells while moving `C_AUDIO_OSC` with `Y_AUDIO` and keeping `C_ADC_I2C_A` and `C_ADC_CLOCK_OK` next to their parent IC supply/GND pins. Preserve the channel-8 port and four-net TDM neck obligations. A larger board should be reconsidered only with a whole-cluster placement and extended filled GND reference, not this three-part displacement.
