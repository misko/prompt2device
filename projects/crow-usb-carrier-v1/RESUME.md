# Resume

<!-- pause-state:9896617e997ea678514d368a445b7d54876bbb90b9377739d201886f992c4215 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: Static USB endpoint screen: canonical 0.410-mm centered launches leave 0.145-mm Type-C and 0.070-mm XU foreign clearance against 0.150 required. Historical D15 0.180/0.100 pair clearance is XU-area-only. Full path, return, P1/P2, connector FULL and prototype-only ESD qualification remain open; 499 opens are inherited from the frozen unrouted board.
3. Resume with: `Prepare one unadopted same-placement 3313A USB pair-domain source proposal: 0.180-mm width, intended DP/DN-only 0.100-mm clearance, foreign clearance 0.150 mm unchanged. Review complete connector/ESD/XU domain and transition model before any new native experiment; retain D18 P1/P2 prerequisites. Do not replay D15/D17, adopt a stack, route, fabricate or order from this static screen. Use the new read-only pair-footprint command before full placement and review any scoped-rule INCOMPLETE; it grants no route or stage admission.`

The authenticated checkpoint is `03_src/rules/critical_part_selection.yaml` at
`15288355fcc731ff8b1b0e35a1ae47b9faf66140223cfea0d31c91d99e9dc1ba`.
