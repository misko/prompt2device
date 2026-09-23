# DLC/USB P1 successor measurements — 2026-09-23

**Engineering verdict: DEFECTIVE / DO-NOT-ORDER.** The one admitted successor is consumed. Runtime delivery passed; no placement acceptance, P2/P3 dispatch, routing or release seal follows.

Source admission commit: `55a16531`; accepted schematic commit: `106ace85`. Candidate SHA256: `b2f59a1b2a8ef91dd1160d6b0074f6a045c4fa0e8d58611bdba98f076acd6fa5`. Runtime: `06_build/task_runs/crow-p1-dlc-usb-successor-644f89c32ef540a7a7443b94d34bc120/attempt.json`, 72.895 seconds. Read-only native review: `08_reviews/2026-09-23_p1-successor_terra_native.md`.

| Measurement | Prior repaired P1 | New successor |
|---|---:|---:|
| Native DRC findings | 155 | 41 |
| Copper/hole/via/annular findings | 115 | 0 |
| Silkscreen findings | 40 | 41 |
| Native schematic parity findings | 45 | 8 |
| Unrouted connections | 499 | 499 |
| Footprints | 568 | 568 |
| Pads | 1866 | 1870 |
| Missing courtyards | 16 | 0 |
| Resolved model files | 495/568, including obsolete bindings | 568/568 |

Current native geometry reports all27 exact anchors, all16 hold capacitors inside their intended banks, no support/ADC courtyard intrusion into either bank, and zero shorts. Counts/pin-map, placement preflight, model-file coverage and pad-separation checks pass. Model registration returned N-A because no model_registration.yaml exists: file resolution is not registered mechanical acceptance. Connector FULL still has19 outstanding physical targets.

The41 violations are40 silk-over-copper and1 USB silk-edge: J_JTAG6; six logic packages5 each; F_IN4; J_USB1. All8 parity rows are U_SPOKE1–8 Description mismatches (PCB has the custom package description; schematic is blank). Preserve the source/library/generator ownership; never edit the generated board to hide these.

Full placement policy also fails:5/6 evaluated keep-short budgets and195/229 evaluated adjacency budgets exceed their limits. Another55/290 constraints are unreached. For example U_DUMP/C_DUMP_LOGIC requests old `5V_LDO_HOLD`, whereas the native net is `N5V_LDO_HOLD`. These constraints require individual source reconciliation; blanket renaming or dropping constraints is not authorized by this diagnosis. Physical local placement follows exact block constraints, not block-center seeds alone.

Review disposition: retain the independent DEFECTIVE verdict. Correct its classification prose: U_DUMP adjacency comes from placement_policy_audit.md, not a native DRC item;499 unrouted is expected at P1 and is later routing work. Silkscreen and Description defects first return to their source/library/generator owners, not direct generated-board cleanup. The runner emitted both drc_classification=1 and SKIPPED through its shell conditional; the checker ran and failed, and the second row cannot override that failure.

Evidence remains under `06_build/modular/dlc-usb-successor/` and isolated `/tmp/crow-p1-dlc-usb-successor-20260923/`. The graph observation validates568/568 components and59/59 interfaces and records delivered work only. Owning engineering gates still fail, so dependent tasks remain undispatched. Both prior rejected boards and the original max_attempts2 remain archived. No automatic further candidate is admitted.

Next owning work: repair footprint silkscreen and Description generation, reconcile55 unreached layout contracts against current exact nets/refs, then explicitly reassess the exhausted successor before another native candidate. P2 block placement must resolve measured adjacency before critical local routing. Public records/jlcsearch only; no firmware or orders.
