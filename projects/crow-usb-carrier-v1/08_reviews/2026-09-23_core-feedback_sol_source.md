# Independent TPS62825 core-feedback source review

Date: 2026-09-23

Candidate: `e21d5902212767fb2460a22f5ca60d86eaf18ee3` in `/home/mouse9911/gits/circuits-worktrees/crow-core-feedback-fix`, based on the composed adjustable-rail and supervisor source stack.

## Verdict: ACCEPT as a source candidate

The change corrects the inherited TPS62825 core network in the direction required by TI SLVSEF9I section 8.2.2.2. The selected 100 kΩ lower resistor meets TI's stated maximum lower-resistor value, and the 120 pF feed-forward capacitor matches TI's value for a 100 kΩ lower resistor. The source connects 49.9 kΩ from 0V9 to `U_CORE_FB`, 100 kΩ from `U_CORE_FB` to GND, and 120 pF across the upper resistor. U_CORE pin 1 remains `CORE_EN`, pin 3 remains the feedback node, pin 5 remains the switch node, and the existing 1V8_OK -> CORE_EN -> CORE_OK/reset topology is unchanged.

The exact retained Yageo PDF has SHA-256 `7e7370fc65587b142979cccaa97cf240770c5d66c10f95e4eaead26eff5b2237` and identifies `RT0402BRD0749K9L` as 49.9 kΩ, 0.1%, ±25 ppm/°C, 0402/1005. Its dossier and source bind it to JLC code C852808. The retained 100 kΩ resistor and 120 pF C0G capacitor already have exact dossiers and codes C852472 and C106996.

I independently recomputed the feedback range using VFB 594--606 mV, opposing 0.35% total resistor corners, and ±50 nA FB leakage: 0.885852--0.913022 V, with 0.8994 V nominal. The unchanged declared 0.88--0.92 V rail envelope covers it and remains within the XU316 0.855--0.945 V operating range. Independent tool runs returned E-TOPO 13/13, E-MARGIN 12/12, TSX preflight 102/102, and schema-reader coverage 969/969 with zero orphan keys.

Aggregate public-stock arithmetic is internally consistent with the composed source: C852808 requires 155 including the project reserve against 32,721 observed; C852472 requires 185 for seven per board against 787,542; C106996 requires 165 for three per board against 681,219; C2650334 requires 165 for three regulators per board against 5,819. These observations do not establish allocation or PCBA acceptance.

The added component is present in the manifest, exact-parts CSV, integration selection, floorplan region, schematic presentation, and modular block/net ownership. The 507-component source/build census reported by the author is consistent with the one-component delta. Physical feedback-loop placement, ripple, overshoot, load-step stability, thermal behavior, EMI, and reset waveforms remain the stated downstream qualifications. The 10 mV release and 25 mV dynamic allocations are honestly labeled first-article targets rather than device guarantees. This review makes no native PCB or release claim.
