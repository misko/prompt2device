# ADC8 cap additional south-shift screen

This read-only screen translates `C_ADC_AC8N1` from `(198.00,60.05)` to `(198.00,59.85)` on the immutable southwest-cap integrated board. It does not generate a board, source change, route, DRC result, return proof, or P1/P2 claim.

The translated checker full envelope is `[195.205,58.105,200.795,61.595]` mm. It has **no** intersection with any of the other 568 native full envelopes. Its `usb_vbus_sense` y=62 gap becomes 0.405 mm, versus 0.205 mm at y=60.05; its `analog_ch8` x=201 margin remains 0.205 mm.

The named support gaps remain positive: `C_A8P` 0.360 mm, `R_B8P` 0.480 mm, and `C_FILTER8N1` 0.580 mm. Thus the extra 0.20-mm south shift does not collide with those parts under `_physical_envelope`; it reduces the C_FILTER8N1 gap from 0.780 to 0.580 mm.

Pad-center locality has a mixed result. `C_ADC_AC8N1.1` to `U_ISO8.6` improves from 7.742254 to **7.560589 mm**, while `C_ADC_AC8N1.2` to `C_ADC_CM8N.1` worsens from 13.870865 to **13.964988 mm**. These are geometric observations, not qualified electrical limits.

The shift is therefore a viable later placement variable for making a southern route exit less constrained, but its netlist, pad clearance, source-region/cell ownership, full-profile DRC, filled In1 return, assembly, and complete ADC8N tree must be re-evaluated on a source-generated candidate. It provides no reason to promote the cap anchor independently.
