# Power contract candidate review — 2026-09-22

SOL delivery closed PASS; engineering acceptance remains open. Candidate is retained in `06_build/tmp/power-contract/power_tree.candidate.yaml`, not promoted over the live power contract yet.

The packet enumerates thirteen rails and five converters and correctly refuses eight spoke connector-plane margins. It also identifies the small input-PPTC hot-current margin. Those findings require circuit/delivery-budget work, not a waiver.

Coordinator found an additional inconsistent premise: the candidate declares TPSM efficiency 85%, while carrying a thermal obligation calculated at88%. At5V ×1.9A output, loss is 1.295455W at88% and 1.676471W at85%. With70°C ambient and125°C junction ceiling, the respective maximum thermal resistances are 42.456140°C/W and 32.807018°C/W. The 42.5°C/W screen therefore cannot accompany an85% worst-case power model. Neither efficiency nor thermal resistance is currently a guaranteed realized-board bound.

Before promotion: reconcile the efficiency/thermal premise; replace zero unknown capacitor deratings with defensible bounds or explicitly failing source evidence; move unconsumed engineering_debt prose into this research record; verify each active schema field against its owning reader; complete connector/copper/temperature IR allocations. No schema pass or footprint load proves these electrical margins.

## Current source adoption

The revised candidate replaces the battery-template power tree in the live
source. It is intentionally incomplete and has not crossed power admission.
See [power bounds adoption](2026-09-22-power-bounds-adoption.md) for the
consistent85%thermal premise and the withdrawn PPTC hard-limit claim.
