# Coordinator hardware review disposition

The XU316 hardware packet passed runtime delivery; that result is not parts or electrical acceptance. The retained report is a snapshot of the worker findings. Its source packet stays isolated pending the next hardware authoring task.

Coordinator reopened the pinned manufacturer datasheet, especially sections8,14 and15.7. The fixed1.8V bottom I/O domain and the830mA budgetary C24 core current are confirmed. Under section14, if the core is powered while VDDIOB18 is below its operating minimum, the other I/O domains default to1.8V mode: a3.3V domain must not exceed1.98V then. The implementation must address brownout and turn-off as well as startup; asserting reset alone does not remove this constraint.

The delivered hardware YAML is not adopted as live configuration: its3V3 regulator proposal disagrees with the report, and its flash entry still names a part that the report rejects as obsolete. The next source task must select a consistent active support BOM.

The candidate footprint description and report claim a4x4 thermal-via grid, but inspection found no drilled pads. Do not infer thermal connectivity from that text. Fabrication vias should be owned by the existing floorplan thermal_vias mechanism and checked against the actual board. The footprint references a standard KiCad body model; this is distinct from an exact manufacturer STEP or registered mating proof.

The generic escape-tier diagnostic alone does not select the manufacturing tier. Actual land geometry, escape routing, return planes and assembly capability must support that decision. The next task authors a complete draft digital hardware module and calculations, with no firmware or native board generation while commissioning remains open.
