# Four-part local ADC7 margin variant

**Conditional P2 placement witness; no portal or routing acceptance.** This isolated variant starts from the exact [three-part candidate](../2026-09-25-ti-adc7-local-osc-probe-sol/README.md), SHA-256 `c9b758d69867b274f0592bd2eceb9a26d64a80dd2daafa8ab9516d23d5925502`. The [Y-only bound](../2026-09-25-ti-adc7-y-margin-bound-sol/README.md) showed that `C_ADC_I2C_B` blocked every downward Y move past y=87.20 mm. Here only `Y_AUDIO` and `C_ADC_I2C_B` move; the first candidate's `C_ADC_I2C_A=(168.0,97.6)` and `C_ADC_CLOCK_OK=(164.6,76.2)` stay fixed. The current **220 × 120 mm** outline, 27 P1-fixed poses, and all pad numbers/nets/layers stay unchanged.

| Ref | Prior origin mm | New origin mm | Related native pad-center gap, prior → new |
| --- | --- | --- | --- |
| `Y_AUDIO` | `(167.5,87.20)` | `(167.5,87.35)` | clock output→`U_TDM_XLATE.11` **15.736→15.643 mm**; VDD→`C_AUDIO_OSC.1` **6.067→5.982 mm** |
| `C_ADC_I2C_B` | `(165.2,89.8)` | `(172.8,95.0)` | VCCB bypass→`U_ADC_I2C_XLATE.7` **7.920→1.671 mm** |

The full checker `_physical_envelope` for `Y_AUDIO` becomes `[164.705,85.255,170.295,89.445]`, leaving **0.255 mm** to the ADC7 portal's y=85 southern edge. The cap's envelope is `[171.845,94.495,173.755,95.505]`. All four affected physical envelopes and native pads remain within `audio_clock_tdm=[145,72,190,99.84]`; both ADC7 and ADC8 portals have no physical or pad intersections. There are **zero new physical-envelope or pad overlap pairs**. The cap sits **0.150 mm** from `U_ADC_I2C_XLATE` and **0.195 mm** from `U_TDM_XLATE` courtyard envelopes, so endpoint access and route clearances still need native proof. The 0.255-mm portal gap exceeds an *illustrative* 0.25-mm screen mentioned in independent review; 0.25 mm is **not an admitted source requirement**.

Native `kicad-cli pcb drc --severity-all --refill-zones --format json` changes from **12 to 15 warnings**, all silkscreen. The three added `silk_overlap` findings are the moved `C_ADC_I2C_B` reference field against `C_U_CORE_OUT_1`, `C_CORE_OK`, and `R_1V8_FB_TOP` reference fields. There are **no new copper or other non-silk DRC findings**; unconnected items remain **499**. The prior twelve silk warnings and the text-inclusive `Y_AUDIO` ADC7 bbox intersection remain source-level label debt. Board-only label edits were not attempted because they would be lost at regeneration without source support and could obscure assembly references.

The exact isolated [candidate.kicad_pcb](candidate.kicad_pcb) has SHA-256 `046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0`. The [receipt](receipt.json) records all poses, geometry, pad distances, and the three new warning UUID pairs. Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-four-part-margin-sol/probe.py > projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-adc7-four-part-margin-sol/receipt.json
```

This remains an unrouted geometric and pad-proximity screen. The source must encode the four placements and readable labels, resolve the fifteen silkscreen warnings, and prove nearby pad access, cap return vias, actual channel-7 traces, filled In1.Cu reference, channel-8 ownership, and the complete timing bundle before any P2/P1 promotion. No canonical source/PCB or stock was edited.
