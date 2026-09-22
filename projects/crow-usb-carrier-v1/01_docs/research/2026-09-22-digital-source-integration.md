# Digital source integration and block interfaces — 2026-09-22

Electrical source checkpoint 18b7e415 integrates the independently reviewed power-state repair. This record documents source admission work, not native schematic, placement, routing or fabrication acceptance.

The circuit has 485 components, 85 selected MPN strings, 1615 ports and 1488 traces. Source expansion reports zero errors and 26 critical endpoint assertions pass. The authored block plan now assigns every component once and covers all 54 actual cross-block nets. Existing requirements are preserved. ADC_DIGITAL_BAD newly connects the ADC/reference reset clamp and audio-clock buffer disable; ADC_DIGITAL_OK stays internal to ADC/reference. Power, ground, VBUS and XU_RESET_N endpoint memberships include the added supervisors and defaults.

TypeScript passes. Early-design checks pass 4/4 gate families, including 8 capacitor banks; E-MARGIN passes 9 rails using the recorded conservative source resistance allocations. These checks do not prove native copper losses, hot thermal behavior or physical fault containment. The independent merged-source review and full schematic-page census are separate pending evidence.

JTAG envelopes are conservative containing boxes from retained Samtec primary drawings with explicit reference-dimension reserves. The board-normal local x axis is preserved: header 7×8×7mm; cable socket 5.5×11×5mm; grip cylinder diameter 12.1mm and axial length 5.5mm. The connector compiler now records 20/45 facts and 25 unknowns. Cable routing, finger clearance, simultaneous service and physical fit remain unqualified.

Current input hashes:

- `03_src/modular_plan.json`: `149adfa41fd95bcec78e3c0382e19c82846a302c0c7be375c3d1df5f1442dcb1`
- `03_src/rules/connector_assemblies.yaml`: `a0514bf7a19ed4aa3c7788e62f7eddf1103fa9d5dd9b3d47cdbb5d1be1633b06`
- `06_build/tmp/full-source/circuit.json`: `dd71d610bf56dcf1cc5b241f288efb43486b0a90fc82e8a713d2535eacbc9f83`
