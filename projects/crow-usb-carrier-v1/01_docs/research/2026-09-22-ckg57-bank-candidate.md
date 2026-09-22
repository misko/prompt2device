# Conditional CKG57K 47 uF bank candidate

This source candidate replaces nine Murata 1210 positions with thirteen exact TDK `CKG57KX7R1E476M335JH` metal-frame capacitors. It adds one second output capacitor to each TPS62825 rail and one second LT3045 output capacitor. The exact LCSC identity is `C2171626`; observed stock was zero, so no JLC allocation is claimed. Fresh owning source grading for 65 parts passed through DigiKey and Mouser.

The conservative bank estimates are 33.558 uF for the TPSM63603 output, 19.572 uF for each doubled TPS62825 output, 9.786 uF for LT3045 input, and 19.572 uF for the doubled LT3045 output. TI explicitly permits added TPSM63603 output capacitance. TPS62825's tested 0.47-uH matrix contains nominal 47-uF and 100-uF columns, but the proposed 94-uF nominal pair is not treated as certification by proximity; startup, ramp and load-step stability remain required.

`C_OPA_BULK` remains a thirteenth physical source capacitor and an advisory downstream reservoir. The same proxy estimates 9.786 uF effective, but there is no independent regulator stability minimum to grade; analog load-step validation remains owed.

ADI permits larger LT3045 output capacitance but requires the complete COUT network to have ESR below 20 milliohm and ESL strictly below 2 nH. TDK's exact simple model gives 4.1 milliohm and 2.000 nH per part. An ideal symmetric pair is 2.05 milliohm and 1.000 nH, leaving less than 1.0 nH for shared interconnect. The placement contract therefore requires symmetric placement at OUT/GND, OUTS Kelvin sensing at the shared output node, extracted or measured assembled-network ESL below 2 nH, and hot/cold startup/load-step validation. This candidate does not claim those physical validations before placement.
