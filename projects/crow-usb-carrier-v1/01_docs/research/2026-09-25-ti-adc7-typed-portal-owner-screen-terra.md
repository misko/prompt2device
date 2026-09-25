# TI ADC7 typed portal owner screen

**Research only.** Exact TI board:
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
This applies SOL’s pending physical candidate: `Y_AUDIO` `(167.5,87.2)`,
`C_ADC_I2C_A` `(168.0,97.6)`, and `C_ADC_CLOCK_OK` `(164.6,76.2)`.
No canonical source/board or P1 claim is made.

The physical portal `[166,83.9,167.12,85]` is clear under checker
`_physical_envelope` plus pads after that move. It cannot, however, be a
typed `analog_ch7` cell or a `virtual_block_face` under the current source
regions: `analog_ch7` ends at y=84 while `audio_clock_tdm=[145,72,190,99.84]`
owns the portal’s y=84..85 strip. A physical cell also cannot overlap that
foreign planning region. Thus an audio y1 recut to at least 85 is required
before the source can express an exclusive portal.

That recut is not a bookkeeping edit. After applying the three candidate
translations, it cuts 15 true audio physical envelopes, including
`C_ADC_CLOCK_OK` at `[163.645,75.695,165.555,76.705]`; the other affected
refs are `U_ADC_CLOCK_OK`, `R_ADC_I2C_SCL_A_PU`, `U_ADC_OUT`,
`C_FSYNC_INV`, `R_ADC_OK_PU`, `C_ADC_OK_CT`, `U_ADC_OK`, `C_FSYNC_OR`,
`U_FSYNC_FF2`, `R_BCLK_RAW_PD`, `R_ADC_OK_TOP`, `R_ADC_DATA_PD`,
`Q_TDM_GATE`, and `R_ADC_I2C_SDA_A_PU`. These are body/courtyard envelopes,
not text-only artifacts.

The moved oscillator and I2C-A capacitor no longer cross y=85
(`Y_AUDIO` becomes `[164.705,85.105,170.295,89.295]`; `C_ADC_I2C_A` becomes
`[167.045,97.095,168.955,98.105]`), but the clock-OK move deliberately places
its true envelope below the proposed recut. Therefore this candidate proves
physical portal clearance only. A valid typed source model must first rehome
or repartition all 15 envelopes, then bind exact `ADC7N/P` native endpoints
with P2 pad-access and filled-return obligations. It earns no capacity,
routing, or P1 credit.
