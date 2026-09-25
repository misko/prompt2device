# TI audio critical-locality audit

**Research only.** Measurements use exact TI board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
They use native pad centres and checker physical envelopes, excluding
reference/value text. No route, return, P1 acceptance, source, or board change
is implied.

`ic_reference_research.yaml` binds three qualitative local-placement intents:
the SCTF oscillator requires `C_AUDIO_OSC` locally between `Y_AUDIO.4` VDD and
`Y_AUDIO.2` GND; TI TCA9406 guidance puts `C_ADC_I2C_A` at VCCA.3 and
`C_ADC_I2C_B` at VCCB.7 with short returns to pin 2; and the ADC clock buffer
requires local VCC/GND bypass and compact input/enable/output routing. The
sources give no numerical pad-distance ceiling, so the following are measured
gaps, not a pass/fail locality rule.

| Group | Same-net pad pair | Centre distance mm |
| --- | --- | ---: |
| oscillator bypass | `Y_AUDIO.1`–`C_AUDIO_OSC.1` N3V3X | 5.5502 |
| oscillator bypass | `Y_AUDIO.2`–`C_AUDIO_OSC.2` GND | 4.1872 |
| I2C A bypass | `C_ADC_I2C_A.1`–`U_ADC_I2C_XLATE.3` N1V8 | 13.6057 |
| I2C A return | `C_ADC_I2C_A.2`–`U_ADC_I2C_XLATE.2` GND | 13.0528 |
| I2C B bypass | `C_ADC_I2C_B.1`–`U_ADC_I2C_XLATE.7` N3V3_ADC | 7.9201 |
| I2C B return | `C_ADC_I2C_B.2`–`U_ADC_I2C_XLATE.2` GND | 5.5731 |
| clock-OK bypass | `C_ADC_CLOCK_OK.1`–`U_ADC_CLOCK_OK.5` N3V3_ADC | 12.9656 |
| clock-OK return | `C_ADC_CLOCK_OK.2`–`U_ADC_CLOCK_OK.3` GND | 13.0496 |

No source-supported numeric rule establishes that any current gap is formally
nonlocal. The I2C-A and clock-OK pairs are nevertheless not evidence of the
required “by/local/compact” geometry: both are about 13 mm before a route and
return are considered. The board is unrouted, so pad distance cannot prove a
short trace or return.

## Corrected relocation scope

The minimum move to clear the **physical** ADC7 portal is one reference:
`Y_AUDIO` from `(167.5,85.92)` to `(167.5,87.10)`. The exact-board candidate
uses checker `_physical_envelope`, clears the portal, creates no new physical
collision, and improves the oscillator/bypass pad distances. The apparent
`C_ADC_I2C_A` and `C_ADC_CLOCK_OK` portal hits were text-only
`GetBoundingBox(True, True)` overhangs; their physical envelopes do not block
the portal and their pad distances remain unchanged.

The seven-reference set is instead the minimum **qualitative-locality debt
closure scope** for a later refloorplan: `Y_AUDIO` with `C_AUDIO_OSC`; both
I2C capacitors with `U_ADC_I2C_XLATE`; and `C_ADC_CLOCK_OK` with
`U_ADC_CLOCK_OK`. The second I2C capacitor travels with the translator because
the TI guidance binds both supply sides. This remains a placement scope, not
permission to claim pads locally routed; native envelope, pad-access, return,
and routed verification remain required.
