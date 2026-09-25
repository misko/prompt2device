# TI ADC analog local-port probe

**Research only; rejected as a complete 18-net P1 model.** This probe used
the TI diagnostic board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`
and an isolated copy of the schema-2 candidate. It did not edit canonical
source or board files, create an attempt, spend a P1 allowance, or accept P1.

## Compact model tested

The sixteen repeated AC-input failures are movable-pad bridge claims, so the
test replaced each with a `virtual_block_face` on its channel's south face at
y=84. Each retained the exact source/native pad and a typed `P2_REQUIRED`
pad-to-face obligation. It used short vertical local ports in y=84..85:

| Channels | Nets per port | Probe port x span mm | Local demand |
| --- | --- | --- | ---: |
| 1 | `ADC1N`, `ADC1P`, `VMID1_EXT` | 34.00..35.68 | 3 × 0.56 mm |
| 2–4 | each channel's N/P pair | 56.00..57.12; 78.00..79.12; 100.00..101.12 | 2 × 0.56 mm each |
| 5 | `ADC5N`, `ADC5P`, `VMID2_EXT` | 122.00..123.68 | 3 × 0.56 mm |
| 6 | `ADC6N`, `ADC6P` | 140.00..141.12 | 2 × 0.56 mm |
| 7 | `ADC7N`, `ADC7P` | 166.00..167.12 | 2 × 0.56 mm |
| 8 | `ADC8N`, `ADC8P` | 190.50..191.62 | 2 × 0.56 mm |

These are deliberately **local staging ports**. They do not form a nine-slot
trunk, reach an ADC pad, prove endpoint access, reserve a trace, establish a
return, or provide capacity credit for the complete analog allocation.

## Result

With all 18 witnesses converted, the checker reports:

```text
FAIL: C_ADC_AC7N1.2: virtual boundary enters audio_clock_tdm source region
```

The all-diagnostics output also names `C_ADC_AC7P1.2`, `C_ADC_AC8N1.2`, and
`C_ADC_AC8P1.2` for the same ownership conflict. Channel 6 clears when its
port is placed in the x=140.00..141.12 sliver; the next failure is channel 7.

Channel 7 has no exclusive north-face port: `audio_clock_tdm` occupies
x=145..190 through y=99.84, covering the whole channel-7 interval x=157..179.
The proposed channel-7 port also intersects courtyard-inclusive native boxes
for `Y_AUDIO`, `C_ADC_I2C_A`, and `C_ADC_CLOCK_OK`.

Channel 8 has no exclusive north-face port either. Its interval x=179..201 is
covered by `audio_clock_tdm` through x=190 and by `xmos_core` from x=190.
The x=190.50..191.62 alternative avoids a native body but enters the XU source
region; moving that XU boundary is not a harmless fix because the current XU
decoupler envelopes already cross x=190, x=191, and x=192.

## Conclusion and bounded next step

Current placement/ownership cannot express all sixteen AC pairs as exclusive
north-face local ports. A complete analog source model therefore requires a
P2-owned refloorplan of the channel-7/8, TDM, and XU neighborhood, with
nonoverlapping physical cells and fresh full-footprint checks. It must then
add exact local pad-to-face and return obligations before testing any staged
ports. The existing two nine-net rectangles remain invalid because they cut
through analog cells; no converted witness, local-port count, or empty
sub-band may be promoted to endpoint, capacity, routing, or P1 credit.
