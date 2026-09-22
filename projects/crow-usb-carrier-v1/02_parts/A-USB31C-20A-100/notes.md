# USB cable source candidate

Manufacturer drawing rev08 sheet1 specifies the Type-C body/boot axial extent 24 mm, grip length 17.6 mm, width 11 mm and thickness 6.5 mm. General tolerances are ±1 mm for integers and ±0.5 mm for one decimal. A 25 × 12 × 7 mm bounding box therefore includes these document tolerances. Plug projection is 6.65 ±0.15 mm. Cable OD is 3.8 mm; length is 1 m ±50 mm. These are cited dimensions, not measurements of a sample.

This dimensioned candidate replaces ACT AC7350 for source planning. No compatibility approval, lifetime, thermal rating or realized fit is inferred. Manufacturer bend-radius and operating-temperature evidence remain owed. The board should preserve straight access and a separately assessed service allowance beyond the plug body.

## External cable wiring (manufacturer ASS 7348 CA rev08)

This is a harness contact table, not a list of board footprint pads. The cable is not instantiated in the PCB source or CPL.

| USB-A contact | Cable connection |
|---|---|
| A1 | VBUS -> C A4/B4/A9/B9 |
| A2 | D- -> C A7 |
| A3 | D+ -> C A6 |
| A4 | GND -> C A1/B1/A12/B12 |
| SH | braid -> C shell |
