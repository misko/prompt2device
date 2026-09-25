# TI audio owner physical-cell correction

**Correction and research only.** The prior claim that the current
`audio_clock_tdm` owner was physically unsatisfiable is retracted. It used
`GetBoundingBox(True, True)`, which includes movable reference/value text, not
the checker’s physical-cell geometry.

On exact board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`, all
39 audio-owner references have checker `_physical_envelope(fp)` geometry
(body plus courtyards, excluding text) and native pads inside
`audio_clock_tdm = [145,72,190,99.84]`. The ten apparent crossings below are
all **text-only**; none has a physical-envelope or pad crossing into
`digital_power`:

`C_ADC_I2C_B`, `C_AUDIO_OSC`, `C_FSYNC_FF1`, `C_XLATE_A`,
`R_ADC_CLOCK_OK_PD`, `R_ADC_I2C_SCL_B_PU`, `R_ADC_I2C_SDA_B_PU`,
`R_ADC_OK_BOT`, `R_BCLK`, and `R_TDM_OE_PU`.

For example, `C_ADC_I2C_B`'s full text-inclusive bbox reaches y=101.362 mm,
whereas its physical envelope is `[164.245,89.295,166.155,90.305]`; the
same distinction holds for every listed part. A complete typed physical-cell
partition of the existing audio owner is therefore not rejected by this
overflow observation.

This correction does not solve the actual blockers: the bounded channel-7
three-part placement search remains unsatisfied inside the audio cell;
channel 8 remains an audio/XU ownership conflict; and the TDM/XU neck remains
an incomplete five-slot full-bbox screen with endpoint and return debt. No
canonical source or board changed, and P1 remains unaccepted.
