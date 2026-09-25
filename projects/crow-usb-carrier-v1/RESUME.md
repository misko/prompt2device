# Resume

<!-- pause-state:1896991cafd219f0816ac63bbf37b847ffcf89f22b496ef5018027db2c532206 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: The TI schematic prototype is sound for topology and source checks, but ordinary build/release remains held at PROTOTYPE_ONLY with XU316 transient unqualified. The isolated unrouted TI board has 499 opens; P1 geometry and connector edge/fit are unaccepted, and connector FULL has 19 physical unknowns.
3. Resume with: `Resolve the incomplete P1 source corridor/edge model on the isolated TI board, obtain independent P1 attempt admission, and qualify connector physical targets on a governed board or coupon before routing; do not promote the diagnostic board or order.`

The authenticated checkpoint is `03_src/rules/critical_part_selection.yaml` at
`15288355fcc731ff8b1b0e35a1ae47b9faf66140223cfea0d31c91d99e9dc1ba`.
