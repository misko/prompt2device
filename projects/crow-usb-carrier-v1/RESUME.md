# Resume

<!-- pause-state:c0459bd22505a7aa59af86c16af37d54bbfab272aab129d01c80af5141d94de0 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: The exact-pair 3313A rule is tested but unadopted. Frozen-board P1 remains INCOMPLETE: JTAG accesses narrow below Default width, reset geometry is unfinished, and timing pad access/allocation is unproved. Affected P2, USB complete route/return, connector FULL, prototype-only ESD, stack/order and release remain open.
3. Resume with: `On the frozen expanded placement, resolve source-backed JTAG/reset and timing pad access; rerun independent P1 and affected P2 checks. Then review the unadopted 3313A USB four-leaf merge/ESD/XU transition and In1.Cu return before one bounded native route experiment. Preserve D15 failed history and D18 physical/release holds; do not regenerate D15 or order.`

The authenticated checkpoint is `03_src/rules/critical_part_selection.yaml` at
`15288355fcc731ff8b1b0e35a1ae47b9faf66140223cfea0d31c91d99e9dc1ba`.
