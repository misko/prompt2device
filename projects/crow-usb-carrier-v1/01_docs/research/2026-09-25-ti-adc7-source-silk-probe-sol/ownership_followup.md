# Bounded affected-label ownership follow-up

The existing generator already uses a general nearest-footprint-centroid
ownership check in `_place_owned`: each position must avoid pads, body boxes,
and prior silk and be nearer its own footprint centroid than any other.
If none of the four text poses × 84 stock offsets is owned, it deliberately
uses the smallest ownership deficit and emits `WARN silk ownership`. Thus the
11 affected-label failures in [`receipt.json`](receipt.json) are explicit
fallbacks, not an unimplemented ownership objective.

Two isolated source variants kept the four footprint anchors and all other
footprint poses unchanged. Both passed native DRC with zero violations, kept
all 13 relevant refdes visible on `F.SilkS`, and kept 499 unconnected items:

| Variant | Source change to baseline overlay | Ambiguous affected labels |
| --- | --- | ---: |
| Baseline `d35983ad` | `R_ADC_PD7N` exact priority | 11/13 |
| Constrained-first | Exact priority order below | 10/13 |
| Constrained-first + dense | Same priority; each of the 13 refs receives an 81-point 0.5 mm Cartesian grid from −2 to +2 mm in `preferred_offsets` (existing 84 offsets still follow) | 9/13 |

Priority order for the two variants:

```text
C_ADC_CM7N, C_ADC_CLOCK_OK, R_TDM_OE_PU, C_CORE_OK,
C_AUDIO_OSC, U_ADC_CLOCK_OK, C_U_CORE_OUT_1, R_1V8_FB_TOP,
U_ADC_I2C_XLATE, R_ADC_PD7N, C_ADC_I2C_B, C_ADC_I2C_A,
R_3V3X_FB_BOTTOM
```

The dense variant still degrades `C_ADC_CM7N`, `C_ADC_CLOCK_OK`,
`R_TDM_OE_PU`, `C_AUDIO_OSC`, `C_U_CORE_OUT_1`, `R_1V8_FB_TOP`,
`U_ADC_I2C_XLATE`, `R_ADC_PD7N`, and `C_ADC_I2C_B`. Its 4×165 sampled
poses per affected ref are a bounded negative screen, not a proof that no
continuous position exists. The source overlay and generated board in this
packet remain the baseline variant; experimental files were restored after
measurement.

As a separate metric check on the baseline generated board, measuring from
label center to the nearest point on each footprint body instead of its
centroid makes four of the 11 fallback labels appear owned (`R_ADC_PD7N`,
`U_ADC_CLOCK_OK`, `U_ADC_I2C_XLATE`, `C_U_CORE_OUT_1`). Seven remain closer
to a different body. For example, `C_ADC_CM7N` is 10.315 mm from its own
body but 1.505 mm from `R_IN7N`; `C_AUDIO_OSC` is 6.075 mm from its own
body but 0.775 mm from `Y_AUDIO`. Changing the metric alone therefore does
not prove assembly readability, and would conceal other failures.

A minimal safe source mechanism is an opt-in `ownership_required_refs` check
that fails generation if any named refdes takes the degraded or F.Fab-only
fallback. To satisfy that check, the board needs more near-owner silk space
through a local component/label floorplan change, shorter explicit assembly
labels with a documented mapping, or an explicit nearby pointer/leader system
whose ownership is checked against body geometry. The current poses do not
support promotion of the 13-label result as assembly-readable.
