# Resume

<!-- pause-state:22f93e51e77f56ac1dfea5ed55bc45565a8419fe427c5d2749c5f5eb153c62f1 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: 3313A exact-pair clearance is tested but unadopted. Current source has incomplete P1 reset/USB ownership and timing bundle access/return; affected P2, connector FULL, prototype-only ESD, stack/order and release remain open. The 0.15-mm JTAG access geometry is a screened proposal, not a routed/native P1 pass.
3. Resume with: `On the frozen expanded placement, make one source-backed P1 candidate for the five-terminal reset tree and owned USB fixed-connector corridor, then test native pad access and the complete P1 denominator. Separately resolve timing-neighbour access and local GND return for affected P2. Keep 3313A source unadopted until full USB topology/return review; D18 allows no private route experiment before independent P1 and affected P2 admission. Preserve D15 failed history and physical/release holds.`

The authenticated checkpoint is `03_src/rules/critical_part_selection.yaml` at
`15288355fcc731ff8b1b0e35a1ae47b9faf66140223cfea0d31c91d99e9dc1ba`.
