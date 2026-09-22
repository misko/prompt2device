# Power and digital source disposition

These are source-stage reviews, not complete schematic or PCB acceptance.

## Power

The `power_repair` delivery passed the bounded runtime. TPSM63603V5RDHR is retained as a candidate for the 70 °C requirement, with the thermal/capacitance limits recorded in its packet. Independent component-source review rejected its proposed land: pad29 ground overlaps pad30 output, and other pad coordinates are wrong. Do not use the original candidate.

The review delivery itself passed. The coordinator then reopened TI example board layout page45 and corrected errors in the review's proposed replacement table: pads27/30 use 0.74 mm height; pads28/29 use 1.0 mm height; 4X(0.95) describes corner lands. Top/bottom row centers are ±2.85 mm from the 5.7 mm separation. A bounded `power_land_repair` task owns the actual source correction, including deliberate AGND/PGND attachment and corner geometry. Both earlier packets remain immutable.

## Digital

The initial `digital_source` delivery was INCOMPLETE because the coordinator rewrote its envelope after the initial snapshot; this is a coordinator delivery defect. Source review independently found clock-driver voltage incompatible with the ADC during quiet-rail brownout and two timing capacitor MPN/value mismatches.

The `digital_interface_repair` delivery passed. The repaired interface adds SN74AUP3G34 powered from the same quiet rail as ADC VDD_IO, so the output driver shares the receiving supply. The packet estimates 1.897 mA incremental load and retains 5.729 mA of the draft allocation; typical capacitance makes this a screening calculation, not a guaranteed measured current. Timing and native-board verification remain owed.

Before adoption, coordinator inspection found that the dossier footprint fields still include shorthand, prose, and absent native libraries. Native generator resolution requires actual library:name identities. The generic capacitor helper also gives non-default MPNs a default 100 nF JLC code. A bounded `digital_native_source` task now owns full reference/MPN/value/catalog identity and native component footprint closure. Passing TypeScript and footprinter syntax alone does not meet this requirement.

## Retained analog and USB

Direct expansion found unsupported analog footprint strings despite the earlier successful electrical topology comparison. `analog_footprint_repair` owns exact inline source lands with retained native component geometry and unchanged electrical identity.

The USB auxiliary ESD footprint string was replaced locally by explicit DRL lands. An isolated six-component USB fixture rendered under the pinned toolchain with 37 pads and zero reported error objects. Evidence is `06_build/tmp/usb-esd/component-render.json`; no native board, full-carrier schematic, routing, SI, mating or electrical acceptance is implied.
