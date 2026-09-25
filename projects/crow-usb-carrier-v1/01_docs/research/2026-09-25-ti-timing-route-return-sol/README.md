# Bounded TDM route/return stop — 2026-09-25

**No timing route subset passes the native board rules.** This isolated experiment starts from the exact coupled-placement board SHA-256 `53e6fb7809910946c36053e7ceeb77e7fc866456ff77775ed4c59b3e49278555`. Its first required west-side DATA escape hits a concrete F.Cu clearance contradiction, so the experiment stops before claiming a staged four-net path or a continuous return.

`build_stop_fixture.py` adds only one 0.20-mm F.Cu track on TDM_DATA_1V8 from exact native U_XU.107 centre `(200.8375,97.6)` west to the measured courtyard mouth at `(199.805,97.6)`. It pins the input board, verifies pad net/layer/position, emits `data_west_stub.kicad_pcb` with deterministic SHA-256 `5a793498738c61c7e71ede55d8fe3efa6c6533bf08fe9efedec3545ab4288b93`, and runs native KiCad DRC on baseline and stub in one clean temporary project environment. `result.json` records the comparative DRC and exact new track items. The fixture preserves every footprint, pad identity, fixed ref, crystal spacing, and USB spacing from the coupled-placement board.

The board setup requires **0.20 mm minimum track width** and **0.20 mm copper clearance**. XU pads 107 and 108 are 0.40 mm apart on the edge, and the adjacent pad extends 0.125 mm toward the DATA centreline. The 0.20-mm track therefore leaves only `0.40 − 0.125 − 0.10 = 0.175 mm` to U_XU.108. Native DRC confirms a new `clearance` error with **actual 0.175 mm** on this exact stub. Baseline DRC has 724 violations; the stub has 726: one added clearance error and the expected dangling end on an intentionally isolated stub. The 499 unconnected items remain unchanged. A 0.15-mm exploratory trace was rejected by the 0.20-mm native minimum-width rule; it is not a lawful neckdown.

This is a rejection of the direct F.Cu west DATA mouth under the present native width/clearance rules, not a proof against every possible redesign or layer-transition technology. No legal route was established, so In1.Cu fill and continuous reference under actual paths cannot be credited. The saved In1.Cu GND zone remains unfilled. A next design iteration needs a source-backed escape rule or changed XU pin/package/placement approach before resuming route/return verification; the rule may not be silently waived for P1/P2.

Reproduce from repository root:

```sh
python3 projects/crow-usb-carrier-v1/01_docs/research/2026-09-25-ti-timing-route-return-sol/build_stop_fixture.py
```
