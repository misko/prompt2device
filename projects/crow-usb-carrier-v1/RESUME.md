# Resume

<!-- pause-state:66a8866441a930316ce77b5ece3f8e6b45f47b62597a480c2a6c9fc35dd2f659 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: The TI schematic prototype is sound for topology and source checks, but ordinary build/release remains held at PROTOTYPE_ONLY with XU316 transient unqualified. The isolated unrouted TI board has 499 opens; P1 geometry and connector edge/fit are unaccepted, and connector FULL has 19 physical unknowns.
3. Resume with: `Follow D18 on the existing expanded-locked placement reference: establish complete USB-path feasibility under actual package/stack/rules, then close independent P1 capacity and affected P2 gaps. Coarse INCOMPLETE is diagnostic, not admission. Current routing and ordinary P3/P5 remain blocked; do not regenerate D15 for a checker-only change, run D17, fabricate, or order.`

The authenticated checkpoint is `03_src/rules/critical_part_selection.yaml` at
`15288355fcc731ff8b1b0e35a1ae47b9faf66140223cfea0d31c91d99e9dc1ba`.
