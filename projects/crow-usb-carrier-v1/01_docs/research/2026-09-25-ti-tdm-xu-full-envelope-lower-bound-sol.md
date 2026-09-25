# TI TDM→XU full-footprint corridor lower bound

This is a bounded, research-only obstruction witness on the exact TI board
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
It does not propose a legal placement, change the source or PCB, or earn P1
capacity. The probe binds the exact P1 requirements and floorplan, records
all 27 P1-fixed native poses, and excludes the ch7/ch8 analog regions
(`y=42..84` mm). Both tested lanes lie at y≥93.6 mm.

The first lane is `[182.475,94,199.825,100]` mm. The second expands its
north edge by 0.4 mm to y=93.6. With only body/pad rectangles, that second
lane appeared to fit four 0.45-mm slots (1.915 mm connected width). That
screen omitted complete footprint extents. With each non-endpoint's native
`GetBoundingBox(True, True)` as a keepout, **both lanes have zero connected
width**. `U_TDM_XLATE` and `U_XU` are exempted only as the intended terminal
footprints; their pad access remains unproved. The obstructing full envelopes
are `R_ADC_I2C_SCL_B_PU`, `C_XU_USB18`, `C_XU_VDD_104`, `_105`, `_106`,
`C_XU_VDDIO_109`, and `C_XU_VDD_113`. Their exact bboxes are in the JSON.

The probe exhaustively removes subsets of those seven *movable* obstacles as
an optimistic relaxation. For each lane, none of the 1 zero-part, 7 one-part,
or 21 two-part combinations reaches four slots. Exactly two of 35 three-part
combinations first reach the target:

| Relaxed obstacle set | Original lane | Expanded lane |
| --- | ---: | ---: |
| `C_XU_USB18`, `C_XU_VDD_104`, `R_ADC_I2C_SCL_B_PU` | 2.5384 mm / 5 slots | 2.9384 mm / 6 slots |
| `C_XU_VDD_104`, `C_XU_VDD_105`, `R_ADC_I2C_SCL_B_PU` | 2.60675 mm / 5 slots | 2.60675 mm / 5 slots |

Therefore **at least three non-endpoint footprints must change** for either
specified full-envelope rectangle while other poses remain fixed. Removal
does not demonstrate that those three parts can be relocated legally; their
complete envelopes, net/pad access, owner-cell occupancy, return plane, DRC,
and U_XU endpoint fanout still require an isolated regenerated board. A
different route band or a broader refloorplan is outside this lower bound.
The research result remains `INCOMPLETE` and `p1_accepted=false`.

Run:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-tdm-xu-full-envelope-lower-bound-sol.py /tmp/ti-tdm-xu-full-envelope.json
```
