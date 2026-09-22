# LT3045 via-process admission probe — 2026-09-22

Root built an isolated test fixture containing only the exact selected KiCad LT3045 ThermalVias footprint. This is a checker probe, not a generated or accepted project board; neither commissioning-held conductor was invoked.

The native footprint contains six plated0.20mm holes. Running the existing via_process_check.py against the proposed advanced-process assembly contract reports0/0 native vias and0/0 via-in-pad sites because the holes are footprint PTH pad objects, while the checker inventories PCB_VIA track objects. It correctly refuses acceptance with V-COVER zero-via/zero-protected findings. The candidate order remark also fails V-ORDER because it does not explicitly name the ordinary0.30mm drill family.

The proposed D-TIER/assembly patch remains unmerged. An adopted process must connect the actual source-owned hole representation to the owning fabrication census and order instructions. A declaration of fill/cap does not establish that the six footprint holes are counted or protected. Resolve through properly generated native protected vias or a justified exact PTH process census; preserve primary pad/thermal requirements and verify resulting geometry. Do not remove the coverage check or count nonexistent PCB_VIA objects.

Evidence:06_build/verification/lt-via-census-probe/probe.kicad_pcb and result.json. Native schematic, project PCB routing, production-process selection and physical qualification remain outstanding.
