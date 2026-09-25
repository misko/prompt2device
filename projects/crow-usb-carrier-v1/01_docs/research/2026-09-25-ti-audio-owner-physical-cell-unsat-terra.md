# TI audio owner physical-cell unsat witness

**Research only.** This audit uses the exact TI board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10` and
current 220 x 120 mm floorplan. It changes no board, source, outline, fixed
connector pose, or stock record; P1 remains unaccepted.

`audio_clock_tdm` owns 39 modular references but its current source rectangle
is `[145,72,190,99.84]`. Twenty-nine full native
`GetBoundingBox(True, True)` envelopes fit. The following ten do not:

| Ref | Full bbox mm | Foreign area entered |
| --- | --- | --- |
| `C_ADC_I2C_B` | `[162.209,89.315,168.191,101.362]` | `digital_power` below y=99.84 |
| `C_AUDIO_OSC` | `[168.594,89.015,174.806,100.062]` | `digital_power` below y=99.84 |
| `C_FSYNC_FF1` | `[165.409,90.815,171.591,102.862]` | `digital_power` |
| `C_XLATE_A` | `[156.938,90.615,166.935,100.520]` | `digital_power` |
| `R_ADC_CLOCK_OK_PD` | `[152.439,87.505,164.430,100.681]` | `digital_power` |
| `R_ADC_I2C_SCL_B_PU` | `[168.508,91.005,183.502,100.961]` | `digital_power` |
| `R_ADC_I2C_SDA_B_PU` | `[166.408,92.305,181.413,102.261]` | `digital_power` |
| `R_ADC_OK_BOT` | `[153.880,92.305,168.830,102.362]` | `digital_power` |
| `R_BCLK` | `[162.151,91.905,165.449,102.861]` | `digital_power` |
| `R_TDM_OE_PU` | `[169.083,92.305,173.917,101.261]` | `digital_power` |

This is a source-owner geometry unsat witness for a typed physical-cell
repartition **without footprint moves or foreign-region recuts**. The checker
requires every modular reference of an owner that adopts `physical_cells` to
be assigned exactly once, each full envelope to remain in its cell, and no
cell to overlap a foreign source region. The ten rows need a second audio cell
below y=99.84, but that space is already `digital_power` `[145,99.84,185,134]`.
Assigning only the 29 in-cell references fails the complete-owner denominator;
assigning any listed row to an audio cell there violates region exclusivity.

The three channel-7 blockers (`Y_AUDIO`, `C_ADC_I2C_A`,
`C_ADC_CLOCK_OK`) do fit the original audio rectangle, but the prior bounded
packing screen found no legal in-cell relocation for them. Channel 8 remains
split at the audio/XU boundary, and the `[188,94,190,99.84]` TDM/XU neck still
has its separate 2.538400-mm/five-slot full-bbox screen. Neither fact repairs
the ten-reference owner denominator.

Within the present outline, the first admissible next experiment must jointly
move or re-own these ten overflow references with `digital_power`, then test a
complete 39-reference audio cell partition and the channel-7/8 portals. A
south-outline extension can supply a receiving area, but it is outside this
current-outline witness. No partial physical-cell list, raw neck capacity, or
local portal earns endpoint, route, return, or P1 credit.
