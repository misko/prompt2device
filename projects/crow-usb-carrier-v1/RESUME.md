# Resume

<!-- pause-state:9fca6b57b9e65fe03e121c8b5c0b80c0a29b08462a3e57b333b4ecfc60d70378 -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: The frozen expanded board has no admitted P1/P2 integrated candidate. Its shared reset/JTAG screen is INCOMPLETE despite zero checker errors; USB 7628G full-width launches miss 0.150-mm foreign clearance at Type-C and XMOS, while the narrower 3313A source remains unadopted. The isolated C105 timing move improves local geometry but all 14 timing nets/54 pad duties remain INCOMPLETE. D18 private routing needs independent P1 and affected P2 first. Connector FULL, prototype-only TI ESD, production stack, release and order holds remain open.
3. Resume with: `Decide the 3313A research source/stack hypothesis from the pinned public sensitivity and exact rule packet; preserve D15 FAILED_RESEARCH. Then create one separately authorized, source-generated unrouted candidate on the frozen placement reference that integrates the reviewed shared-reset and C105 proposals, reopens source/native parity, and independently grades all P1 plus affected P2. Do not launch D18 private routing until those admissions and connector-neighbour assumptions are met.`

The authenticated checkpoint is `03_src/rules/critical_part_selection.yaml` at
`15288355fcc731ff8b1b0e35a1ae47b9faf66140223cfea0d31c91d99e9dc1ba`.
