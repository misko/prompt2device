# Independent review: SOL XU fanout probe — 2026-09-24

**Verdict: FAIL as an adoptable decoupler placement; PASS only for a narrow MCLK south-strip geometry screen.**

Read-only review of SOL's isolated board `/tmp/crow-xu-fanouts-sol/04_kicad/crow_carrier.kicad_pcb`, SHA-256 `6f7c77fbf9a815f1596b6dd5285526df8adfd027f62f110af1c82f52b7a6ff34`, and commit `5c240c95`. No canonical source or P1 attempt changed.

SOL moved `C_XU_VDDIO_17` from `[211.0,109.4,0]` to `[211.7,109.8,90]`. Its N1V8 pad 1 is `(211.700,110.280)` and XU pin 17 is `(208.700,107.6625)`: 3.9814 mm centre-to-centre, up from 2.5162 mm. Current P-ADJ does not grade this exact capacitor because no numeric `keep_short` or adjacency budget exists. That is unmeasured debt, not acceptance. XMOS guidance requires each VDDIO capacitor's ground side to have a direct, short return; this probe has no supply/return routing proof.

The 0.09-mm C_XU_VDD_106–C_XU_VDD_113 courtyard gap is also only a non-overlap result. Do not adopt the four coordinates from this probe.

For MCLK, I made a new temporary copy and added only a 0.15-mm F.Cu track from U_XU.23 `(211.100,107.6625)` to `(211.100,113.500)`. Native all-severity/refill/parity DRC added one dangling endpoint to SOL's three; it found no copper, hole, width, or courtyard DRC finding. The strip's right edge is `x=211.175`; C_XU_VDDIO_17's F.CrtYd starts at `x=211.215`, a **0.040-mm** lateral gap over `y=108.865..110.735`. Thus the MCLK strip is a narrow diagnostic feasibility only, not an assembly clearance, endpoint-pocket, route, SI, or return proof.

The next source step is not another coordinate move: add a source-owned C_XU_VDDIO_17-to-U_XU.17 local supply/ground-return constraint based on actual engineering evidence. The retained manufacturer source has no numeric ceiling, so none can be invented. Then choose a pose with a real MCLK clearance margin and rerun isolated proximity and return review before authoring floorplan coordinates.
