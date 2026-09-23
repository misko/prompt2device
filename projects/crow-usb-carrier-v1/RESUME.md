# Resume

<!-- pause-state:6c4609ef035f25820263ee1fc32724cde2e51a184e38452fe278efb0c3f634bd -->

Canonical state: `01_docs/pause_state.json`

1. Verify: `python3 skills/pcb-design/scripts/pause_state.py verify .`
2. Confirm blocker: Source silk/Description repairs and 311/311 layout-constraint coverage accepted; product candidate b2f59a1b remains rejected and its allowance consumed. Block-local distances and connector physical requirements remain open. P1/P2 admission authority is under read-only audit.
3. Resume with: `Resolve P1-to-P2 admission against owning gates, then explicitly admit the appropriate bounded block-placement work. Do not regenerate an exhausted candidate or waive physical/routing requirements.`

The authenticated checkpoint is `06_build/checkpoints/schematic.json` at
`2fb4dd626750114476150d550d88cf15c0d5a2deb5d8e971e1be67a2a7bde856`.
