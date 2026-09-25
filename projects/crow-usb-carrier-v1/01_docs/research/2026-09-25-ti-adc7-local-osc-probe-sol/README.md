# Local ADC7 physical-port placement candidate

**Conditional P2 placement witness, not a release or P1 pass.** On the exact TI unrouted board SHA-256 `8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`, this candidate keeps the existing `[20,20,240,140]` mm (220 × 120 mm) outline and all 27 fixed references. It uses the checker's `_physical_envelope` (native body plus courtyards, excluding movable reference/value text) and all pad bboxes for physical-cell and portal checks, following Terra's correction `9399b0f1`. This is a precise distinction from `GetBoundingBox(True, True)`, which still sees one **text-only** ADC7 intersection at `Y_AUDIO`.

| P2 ref | Baseline origin mm | Candidate origin mm | Related pad-center gap, baseline → candidate |
| --- | --- | --- | --- |
| `Y_AUDIO` | `(167.5,85.92)` | `(167.5,87.20)` | `Y_AUDIO.3`→`U_TDM_XLATE.11`: **16.566→15.736 mm**; `Y_AUDIO.4`→`C_AUDIO_OSC.1`: **6.876→6.067 mm** |
| `C_ADC_I2C_A` | `(166.8,82.0)` | `(168.0,97.6)` | `C_ADC_I2C_A.1`→`U_ADC_I2C_XLATE.3`: **13.606→2.050 mm** |
| `C_ADC_CLOCK_OK` | `(168.2,89.9)` | `(164.6,76.2)` | `C_ADC_CLOCK_OK.1`→`U_ADC_CLOCK_OK.5`: **12.966→1.250 mm** |

The loaded native copy [candidate.kicad_pcb](candidate.kicad_pcb) has SHA-256 `c9b758d69867b274f0592bd2eceb9a26d64a80dd2daafa8ab9516d23d5925502`. The [receipt](receipt.json) proves fixed poses and all pad-number/net/layer identities are unchanged, all three complete physical envelopes and pads remain in `audio_clock_tdm=[145,72,190,99.84]`, and there are **zero new physical-envelope overlap pairs** (3 baseline and 3 candidate). Both ADC7 `[166,83.9,167.12,85]` and ADC8 `[190.5,83.9,191.62,85]` are physically clear. `Y_AUDIO`'s physical box is `[164.705,85.105,170.295,89.295]`, leaving only **0.105 mm** between its north courtyard edge and the ADC7 portal south edge. This is a narrow geometry witness; no trace clearance, endpoint access, return, or tolerance is implied. The lower TDM/XU neck is physically unchanged; the known `C_XU_VDD_105` and `C_XU_VDDIO_109` hits are text-inclusive only in this screen.

Native `kicad-cli pcb drc --severity-all --refill-zones --format json` gives **0→12 violations**, all warnings: seven `silk_overlap` and five `silk_over_copper`; unconnected items stay **499→499**. The exact warning inventory and involved field/pad UUIDs are in the receipt. The new cap positions bring their original silkscreen references against neighboring labels (`R_3V3X_FB_BOTTOM`, `R_TDM_OE_PU`, `C_AUDIO_OSC`, `C_ADC_CM7N`, `R_ADC_PD7N`) and put the two stationary parent-IC reference fields against nearby cap silk or pads. These are **source-level text-placement debt**. No board-only label patches were made: regeneration would discard them, and moving references to F.Fab without an assembly-label plan would create ambiguity. The text-inclusive ADC7 hit at `Y_AUDIO` must likewise be resolved in the source/footprint text model if a downstream checker insists on that bbox definition.

Run from repository root to regenerate the exact isolated board and receipt:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-local-osc-probe-sol/build_probe.py > projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-local-osc-probe-sol/receipt.json
```

This placement improves **pad-center proximity**, but that alone does not certify local bypass current loops. The new cap ground-pad access, routed lengths, return via placement, `C_AUDIO_OSC`'s own bypass path, P1 channel-7/8 exact endpoints, 54-member timing-bundle allocation, and filled In1.Cu return remain open. Before source promotion, encode all three poses and label placements in a persistent source layer, rerender the native board, clear the twelve silk warnings without losing assembly readability, and independently review the resulting route/reference geometry. No canonical source/PCB was changed by this packet.
