# Complete 64-reference ADC P2 source proposal

The fuzz-0 source patch `p2_adc_reference_complete64_fuzz0.patch` has SHA-256
`bdc4bca454fc29068f95683108746f02c66922c505eeff882f5d37e2da08ecbd` and
produces floorplan SHA-256
`5f659a230905debe0dbb2dfc51651c60b3bd3ed8e75e202252ac45c2cbec3c2d`.
It applies byte-for-byte from source floorplan `744c0f2e...` with fuzz zero.

The proposal changes 62 movable references: the frozen 37-reference result and
all 25 remaining control-cell parts. `U_ADC_A` and `U_ADC_B` retain their accepted
positions. All 72 prior source anchors and every out-of-scope transform remain
unchanged.

The complete 64-reference exact courtyard scan has zero gaps below 0.25 mm. The
four VREF reservations retain their frozen poses and each still clears all 1,395
foreign non-GND effective F.Cu pad shapes at 0.20 mm width plus 0.15 mm
clearance. The numeric 17-reference poses are unchanged, retaining the predicted
16/16 numeric census.

`control25_functional_spans.json` records the actual composed pose and every
same-net pin-centre span inside each authored functional cell. These are
observations and dispositions, not invented manufacturer limits.

The source netlist connects the single `C_ADC_DIGITAL_OK` bypass to both
`U_ADC_1V8_OK` and `U_ADC_3V3X_OK`. The proposal places the two supervisors around
that capacitor. Closest observed supply/GND spans are 2.066/4.101 mm for
`U_ADC_1V8_OK` and 2.813/2.453 mm for `U_ADC_3V3X_OK`. Connectivity proves the
shared authored intent, but does not establish datasheet authority that one
capacitor satisfies two device-local bypass obligations. Independent review must
either accept that source electrical choice with device authority or require a
second bypass reference; layout proximity does not waive it.

No repository edit, native generation, saved-board mutation, routing, or
acceptance action was performed.
