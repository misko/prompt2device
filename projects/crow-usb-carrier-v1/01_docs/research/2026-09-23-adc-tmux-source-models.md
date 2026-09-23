# Drawing-derived ADC and TMUX source models

These two declarative VRML source files replace obsolete package overrides for
U_ADC_A/B and U_ISO1–8. They are independently authored from retained TI
mechanical dimensions, **not manufacturer CAD**, JLC registration evidence,
thermal models or physical qualification. They change no copper, pin identities
or electrical source. The literal VRML geometry, with adjacent millimetre
comments, is the source; it needs no external model-generation dependency.

## Dimensional authority and simplifications

| Model | Primary authority | Geometry represented | Limits |
|---|---|---|---|
| `TI_RTW0024A_nominal.wrl` | `02_parts/TLV320ADC6140IRTWT/RTW0024A-4222815A.pdf`, p.1, drawing4222815/A, SHA256 `45616d442aed7ce69f42ce26187526723e12082c905d51ad3ff7b2f014752765` | Nominal4×4 mm body; maximum0.8 mm height; nominal0.025 mm body standoff from0..0.05; 24 rectangular terminals at0.5 mm pitch, nominal0.4×0.25 mm ends and0.1 mm reference thickness; nominal2.6×2.6 mm exposed terminal25. | Body is not the maximum4.1 mm plan envelope. Terminal lengths0.3..0.5, widths0.2..0.3 and EP±0.1 tolerances are not swept. Rounded edges, solder and mould details omitted. Courtyard owner must use maximum dimensions, not this nominal body. |
| `TI_YBH0009_C02_envelope.wrl` | `02_parts/TMUX4827YBHR/TMUX4827_SCDS457B.pdf`, p.32, drawing4228717/C YBH0009-C02, SHA256 `3af04d7ae37b0e43c71c1b663a2d055667d94d46b5dc87c9ca2de24ec2295028` | Maximum1.627×1.627 mm body plan and0.4 mm total height. Nine0.25 mm XY-diameter flattened ellipsoids at0.4 mm pitch, nominal0.165 mm ball standoff (midpoint0.135..0.195), centred0.0825 mm above seating plane. Body starts at0.165 mm. | Balls are simplified ellipsoids, not measured solder shapes. Body thickness derived from the selected max-height/nominal-standoff combination, not a guaranteed die thickness. Ball0.23..0.27 and coplanarity tolerances not swept. No internal die/wire/thermal material properties. |

Frame: XY origin is package/footprint centre. Source comments use footprint Y
down; numeric VRML uses modelY=-footprintY once. One model unit is2.54 mm.
Z=0 is the seating plane; all geometry is above it. Floorplan attachments use
unit scale and zero model offset/rotation. ADC pin1 is upper-left in footprint
coordinates; pins1..6 down the left,7..12 along bottom,13..18 up right,19..24
along top. TMUX A1/pad1 is upper-left, then row-major1..9. Small top marks
identify those corners illustratively; their size is not a drawing dimension.

## Acceptance boundary

Source numeric comparison and native model loading are separate from mounted
board validation. No third P1 board has been generated. No full model-coverage
or MODEL-REG result is claimed from these files. The next accepted board must
reopen model identity/transform, same-camera render and signed mounted-side
registration, including90-degree cases. The exact ten-ref override inventory
must remain tied to current parts. Remaining model gaps are unchanged.
