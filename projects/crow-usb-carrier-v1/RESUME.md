# Resume

<!-- pause-state:21369c3a8de425ba304e976627b95cf46141eef91066f418dbb9b91ccd361408 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: The frozen-board reset candidate fails P1: three digital-power witnesses exceed the locality bound (10.2 versus 8.54 mm), and current source accounting rejects XU_RESET_N across its JTAG and reset-power corridors. USB edge ownership is checker-expressible but P1/P2 and route/return are incomplete. 3313A remains unadopted; connector FULL, prototype-only ESD, stack/order and release remain open.
3. Resume with: `Define and test a minimal branch-aware P1 representation for one shared five-terminal reset net over two physical corridors without double credit; retain the locality check and five-terminal/four-edge denominator. Then retry one source-backed reset/USB owner candidate on the frozen placement and regrade all P1 plus affected P2. Resolve timing-neighbour access and local GND return before any D18 private route experiment. Preserve D15 failed history and physical/release holds.`

The authenticated checkpoint is `03_src/rules/critical_part_selection.yaml` at
`15288355fcc731ff8b1b0e35a1ae47b9faf66140223cfea0d31c91d99e9dc1ba`.
