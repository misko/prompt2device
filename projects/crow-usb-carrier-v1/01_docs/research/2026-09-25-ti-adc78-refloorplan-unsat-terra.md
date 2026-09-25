# TI ADC channel-7/8 bounded refloorplan search

**Research-only bounded unsat witness.** The subject is the exact TI
diagnostic board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
No canonical source, board, part, stock record, task envelope, or P1 attempt
was changed. This does not prove that a larger refloorplan is impossible.

## Search target

The desired channel-7 local AC port is the minimum two-slot vertical window
`[166.00,83.90,167.12,85.00]` on F.Cu. It would carry only `ADC7N` and
`ADC7P` from an `analog_ch7` south virtual face, with two explicit
`P2_REQUIRED` pad-to-face/return obligations. It would not reach U_ADC,
reserve an ADC route, prove a return, or earn complete-allocation capacity.

`audio_clock_tdm` currently owns `[145,72,190,99.84]`. The three direct
blockers, measured with KiCad `GetBoundingBox(True, True)`, are:

| Ref | Current origin mm | Full bbox mm |
| --- | --- | --- |
| `Y_AUDIO` | (167.500, 85.920) | [156.019, 82.559, 178.981, 87.995] |
| `C_ADC_I2C_A` | (166.800, 82.000) | [164.365, 81.515, 171.261, 88.245] |
| `C_ADC_CLOCK_OK` | (168.200, 89.900) | [163.739, 82.841, 170.635, 91.908] |

## Bounded result

I removed only those three movable audio references from the collision set,
then enumerated each reference's unrotated origin on a 0.05-mm grid over the
current audio cell. A candidate had to keep its complete native bbox inside
the cell, avoid the channel-7 port, and avoid every other native bbox touching
the cell (78 fixed-for-this-search occupants). The legal-origin counts were:

| Movable ref | Legal origins |
| --- | ---: |
| `Y_AUDIO` | 0 |
| `C_ADC_I2C_A` | 0 |
| `C_ADC_CLOCK_OK` | 0 |

Because none has an individual legal origin, no three-part co-placement exists
under this bounded model. The result is stronger than the initial direct-hit
observation, but remains a 0.05-mm-grid, unchanged-orientation, current-cell
witness rather than a global packing proof.

Channel 8 independently lacks an exclusive north-face interval: its
`analog_ch8` span x=179..201 is covered by `audio_clock_tdm` through x=190
and by `xmos_core` from x=190. The tempting channel-8 port
`[190.50,83.90,191.62,85.00]` avoids a native body but enters the XU source
region. Recutting that region is not a bookkeeping change: XU decoupler full
envelopes cross x=190, x=191, and x=192.

## Required next model

A new candidate must move or split the audio/TDM ownership cell together with
the affected channel-7/8 and XU decoupling placement, then regenerate an
isolated board. It must use explicit typed physical-cell ownership for any
split/shared transition, retain exact endpoint ownership, and bind P2
pad-to-face plus return debt. Reject it if any full envelope crosses a cell
boundary or local port, if foreign occupancy remains, or if it turns local
ports into ADC endpoint/capacity/routing credit. P1 remains unaccepted.
